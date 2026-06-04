import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.api.job_mapping import attach_queue_positions, row_to_job
from face_gallery.api.queries import JOB_SELECT
from face_gallery.models.job import JobOut, JobsDashboardOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

Bucket = Literal["active", "queue", "history"]


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
    queue = _fetch_jobs(db, "j.status = 'queued'", order="j.created_at ASC, j.id ASC")
    attach_queue_positions(queue)
    history = _fetch_jobs(
        db,
        "j.status IN ('done', 'failed')",
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
        jobs = _fetch_jobs(db, "j.status = 'queued'", order="j.created_at ASC, j.id ASC")
        return attach_queue_positions(jobs)
    return _fetch_jobs(
        db,
        "j.status IN ('done', 'failed')",
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
