from __future__ import annotations

import asyncio
import threading
import time
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from face_gallery.db.connection import get_engine, get_session
from face_gallery.services.clusterer import cluster_library_faces
from face_gallery.services.indexer import index_library
from face_gallery.ml.insightface_app import warmup

_active_jobs: dict[int, threading.Thread] = {}
_active_libraries: set[int] = set()
_lock = threading.Lock()

_UPDATE_SQL = text(
    """
    UPDATE jobs SET status = :st, progress = :pr, message = :msg,
    updated_at = datetime('now') WHERE id = :jid
    """
)


def _update_job(job_id: int, status: str, progress: float, message: str | None) -> None:
    """Separate connection so scan session does not block progress writes."""
    engine = get_engine()
    msg = message[:500] if message else message
    for attempt in range(8):
        try:
            with engine.begin() as conn:
                conn.execute(
                    _UPDATE_SQL,
                    {"st": status, "pr": progress, "msg": msg, "jid": job_id},
                )
            return
        except OperationalError:
            if attempt == 7:
                raise
            time.sleep(0.05 * (attempt + 1))


def _run_scan(job_id: int, library_id: int, root_path: str) -> None:
    try:
        _update_job(job_id, "indexing", 0.02, "Loading face models…")
        warmup()

        def on_progress(p: float, msg: str) -> None:
            _update_job(job_id, "indexing", min(0.85, p), msg)

        session = get_session()
        try:
            _update_job(job_id, "indexing", 0.05, "Scanning images…")
            index_library(session, library_id, Path(root_path), on_progress=on_progress)
        finally:
            session.close()

        _update_job(job_id, "clustering", 0.9, "Clustering faces…")
        session = get_session()
        try:
            n = cluster_library_faces(session, library_id)
        finally:
            session.close()

        _update_job(job_id, "done", 1.0, f"Complete. {n} persons found.")
    except Exception as exc:  # noqa: BLE001
        try:
            _update_job(job_id, "failed", 0.0, str(exc)[:500])
        except Exception:
            pass
    finally:
        with _lock:
            _active_jobs.pop(job_id, None)
            _active_libraries.discard(library_id)


def start_scan_job(job_id: int, library_id: int, root_path: str) -> None:
    with _lock:
        if library_id in _active_libraries:
            _update_job(job_id, "failed", 0.0, "A scan is already running for this library.")
            _active_jobs.pop(job_id, None)
            return
        if job_id in _active_jobs:
            return
        _active_libraries.add(library_id)
        t = threading.Thread(
            target=_run_scan,
            args=(job_id, library_id, root_path),
            daemon=True,
            name=f"scan-job-{job_id}",
        )
        _active_jobs[job_id] = t
        t.start()


async def start_scan_job_async(job_id: int, library_id: int, root_path: str) -> None:
    await asyncio.to_thread(start_scan_job, job_id, library_id, root_path)
