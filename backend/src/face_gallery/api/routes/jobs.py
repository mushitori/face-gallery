import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.api.job_mapping import attach_queue_positions, row_to_job
from face_gallery.api.queries import JOB_SELECT
from face_gallery.db.connection import commit_session
from face_gallery.models.job import JobOut, JobsDashboardOut
from face_gallery.services.queue_worker import library_has_active_job, notify_worker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

Bucket = Literal["active", "queue", "history"]

QUEUE_WHERE = "j.status IN ('queued', 'paused')"
HISTORY_WHERE = "j.status IN ('done', 'failed', 'cancelled')"
RETRYABLE_STATUSES = ("cancelled", "failed")


def _fetch_jobs(
    db: Session,
    where: str,
    params: dict | None = None,
    *,
    order: str,
    limit: int | None = None,
) -> list[JobOut]:
    params = params or {}
    limit_sql = f" LIMIT {int(limit)}" if limit is not None else ""
    rows = db.execute(
        text(f"{JOB_SELECT} WHERE {where} ORDER BY {order}{limit_sql}"),
        params,
    ).fetchall()
    return [row_to_job(r) for r in rows]


def _job_exists(db: Session, job_id: int) -> bool:
    row = db.execute(
        text("SELECT 1 FROM jobs WHERE id = :id"),
        {"id": job_id},
    ).fetchone()
    return row is not None


def _conditional_update(db: Session, job_id: int, sql: str, params: dict) -> int:
    result = db.execute(text(sql), {**params, "id": job_id})
    commit_session(db)
    return result.rowcount or 0


@router.get("/dashboard", response_model=JobsDashboardOut)
def jobs_dashboard(
    db: Session = Depends(get_db),
    history_limit: int = Query(default=50, ge=1, le=200),
) -> JobsDashboardOut:
    active_list = _fetch_jobs(
        db,
        "j.status IN ('indexing', 'clustering')",
        order="j.updated_at DESC",
        limit=1,
    )
    queue = _fetch_jobs(db, QUEUE_WHERE, order="j.created_at ASC, j.id ASC")
    attach_queue_positions(queue)
    history = _fetch_jobs(
        db,
        HISTORY_WHERE,
        order="j.created_at DESC, j.id DESC",
        limit=history_limit,
    )
    return JobsDashboardOut(
        active=active_list[0] if active_list else None,
        queue=queue,
        history=history,
    )


@router.get("", response_model=list[JobOut])
def list_jobs(
    bucket: Bucket = Query(...),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[JobOut]:
    if bucket == "active":
        jobs = _fetch_jobs(
            db,
            "j.status IN ('indexing', 'clustering')",
            order="j.updated_at DESC",
            limit=1,
        )
        return jobs
    if bucket == "queue":
        jobs = _fetch_jobs(db, QUEUE_WHERE, order="j.created_at ASC, j.id ASC")
        return attach_queue_positions(jobs)
    return _fetch_jobs(
        db,
        HISTORY_WHERE,
        order="j.created_at DESC, j.id DESC",
        limit=limit,
    )


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobOut:
    row = db.execute(
        text(f"{JOB_SELECT} WHERE j.id = :id"),
        {"id": job_id},
    ).fetchone()
    if not row:
        logger.warning("get_job: not found job_id=%s", job_id)
        raise HTTPException(status_code=404, detail="Job not found")
    job = row_to_job(row)
    if job.status == "queued":
        pos_row = db.execute(
            text(
                """
                SELECT COUNT(*) FROM jobs
                WHERE status = 'queued'
                  AND (created_at < :ca OR (created_at = :ca AND id <= :jid))
                """
            ),
            {"ca": job.created_at, "jid": job_id},
        ).scalar_one()
        job.queue_position = int(pos_row or 1)
    logger.debug(
        "get_job: job_id=%s status=%s progress=%s",
        job_id,
        job.status,
        job.progress,
    )
    return job


@router.post("/{job_id}/pause", status_code=204, response_class=Response)
def pause_job(job_id: int, db: Session = Depends(get_db)) -> Response:
    if not _job_exists(db, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    n = _conditional_update(
        db,
        job_id,
        """
        UPDATE jobs
        SET pause_requested = 1,
            message = 'Pause requested',
            updated_at = datetime('now')
        WHERE id = :id AND status = 'indexing'
        """,
        {},
    )
    if n == 0:
        raise HTTPException(
            status_code=409,
            detail="Job can only be paused while indexing",
        )
    return Response(status_code=204)


@router.post("/{job_id}/cancel", status_code=204, response_class=Response)
def cancel_job(job_id: int, db: Session = Depends(get_db)) -> Response:
    if not _job_exists(db, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    n = _conditional_update(
        db,
        job_id,
        """
        UPDATE jobs
        SET status = 'cancelled',
            message = 'Cancelled',
            pause_requested = 0,
            updated_at = datetime('now')
        WHERE id = :id AND status IN ('queued', 'paused')
        """,
        {},
    )
    if n == 0:
        raise HTTPException(
            status_code=409,
            detail="Job can only be cancelled while queued or paused",
        )
    return Response(status_code=204)


@router.post("/{job_id}/resume", status_code=204, response_class=Response)
def resume_job(job_id: int, db: Session = Depends(get_db)) -> Response:
    if not _job_exists(db, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    n = _conditional_update(
        db,
        job_id,
        """
        UPDATE jobs
        SET status = 'queued',
            message = 'Queued',
            pause_requested = 0,
            updated_at = datetime('now')
        WHERE id = :id AND status = 'paused'
        """,
        {},
    )
    if n == 0:
        raise HTTPException(status_code=409, detail="Job can only be resumed while paused")
    notify_worker()
    return Response(status_code=204)


@router.post("/{job_id}/retry", status_code=204, response_class=Response)
def retry_job(job_id: int, db: Session = Depends(get_db)) -> Response:
    row = db.execute(
        text("SELECT library_id, status FROM jobs WHERE id = :id"),
        {"id": job_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    if row[1] not in RETRYABLE_STATUSES:
        raise HTTPException(
            status_code=409,
            detail="Job can only be retried while cancelled or failed",
        )
    library_id = int(row[0])
    if library_has_active_job(db, library_id):
        raise HTTPException(
            status_code=409,
            detail="A scan is already queued or running for this library",
        )
    n = _conditional_update(
        db,
        job_id,
        """
        UPDATE jobs
        SET status = 'queued',
            progress = 0,
            message = 'Queued',
            pause_requested = 0,
            updated_at = datetime('now')
        WHERE id = :id AND status IN ('cancelled', 'failed')
        """,
        {},
    )
    if n == 0:
        raise HTTPException(
            status_code=409,
            detail="Job can only be retried while cancelled or failed",
        )
    notify_worker()
    return Response(status_code=204)
