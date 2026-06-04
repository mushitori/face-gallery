from __future__ import annotations

import logging
import threading

from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.db.connection import get_engine
from face_gallery.services.job_runner import run_queued_job

logger = logging.getLogger(__name__)

ACTIVE_JOB_STATUSES = ("queued", "indexing", "clustering")

_worker_thread: threading.Thread | None = None
_wake = threading.Event()
_shutdown = False
_thread_lock = threading.Lock()


def reset_stuck_jobs_on_startup() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE jobs
                SET status = 'queued',
                    message = 'Re-queued after restart',
                    updated_at = datetime('now')
                WHERE status IN ('indexing', 'clustering')
                """
            )
        )
        return result.rowcount or 0


def library_has_active_job(db: Session, library_id: int) -> bool:
    row = db.execute(
        text(
            """
            SELECT 1 FROM jobs
            WHERE library_id = :lid AND status IN ('queued', 'indexing', 'clustering')
            LIMIT 1
            """
        ),
        {"lid": library_id},
    ).fetchone()
    return row is not None


def notify_worker() -> None:
    _wake.set()


def _pick_next_job() -> tuple[int, int, str, bool] | None:
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                SELECT j.id, j.library_id, l.root_path, j.force
                FROM jobs j
                JOIN libraries l ON l.id = j.library_id
                WHERE j.status = 'queued'
                ORDER BY j.created_at ASC, j.id ASC
                LIMIT 1
                """
            )
        ).fetchone()
    if not row:
        return None
    return int(row[0]), int(row[1]), str(row[2]), bool(row[3])


def worker_loop() -> None:
    logger.info("queue_worker: loop started")
    while not _shutdown:
        _wake.wait(timeout=2.0)
        _wake.clear()
        while not _shutdown:
            job = _pick_next_job()
            if not job:
                break
            job_id, library_id, root_path, force = job
            logger.info(
                "queue_worker: running job_id=%s library_id=%s force=%s",
                job_id,
                library_id,
                force,
            )
            try:
                run_queued_job(job_id, library_id, root_path, force=force)
            except Exception:
                logger.exception("queue_worker: job_id=%s failed", job_id)


def start_queue_worker() -> None:
    global _worker_thread
    with _thread_lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            notify_worker()
            return
        _worker_thread = threading.Thread(
            target=worker_loop,
            daemon=True,
            name="scan-queue-worker",
        )
        _worker_thread.start()
    notify_worker()


def stop_queue_worker() -> None:
    global _shutdown
    _shutdown = True
    notify_worker()
