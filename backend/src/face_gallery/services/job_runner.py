from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from face_gallery.db.connection import commit_session, get_engine, get_session
from face_gallery.db.retry import run_with_retry
from face_gallery.services.clusterer import cluster_library_faces
from face_gallery.services.indexer import index_library
from face_gallery.ml.insightface_app import warmup

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

    def _write() -> None:
        with engine.begin() as conn:
            conn.execute(
                _UPDATE_SQL,
                {"st": status, "pr": progress, "msg": msg, "jid": job_id},
            )

    run_with_retry(_write)


def _clear_library_clusters(session, library_id: int) -> None:
    session.execute(
        text(
            "DELETE FROM photo_persons WHERE person_id IN "
            "(SELECT id FROM persons WHERE library_id = :lid)"
        ),
        {"lid": library_id},
    )
    session.execute(text("DELETE FROM persons WHERE library_id = :lid"), {"lid": library_id})
    session.execute(
        text(
            "UPDATE faces SET person_id = NULL WHERE photo_id IN "
            "(SELECT id FROM photos WHERE library_id = :lid)"
        ),
        {"lid": library_id},
    )
    commit_session(session)


def _run_scan(job_id: int, library_id: int, root_path: str, *, force: bool = False) -> None:
    try:
        _update_job(job_id, "indexing", 0.02, "Loading face models…")
        warmup()

        def on_progress(p: float, msg: str) -> None:
            _update_job(job_id, "indexing", min(0.85, p), msg)

        session = get_session()
        try:
            if force:
                _update_job(job_id, "indexing", 0.04, "Clearing old person clusters…")
                _clear_library_clusters(session, library_id)
            _update_job(job_id, "indexing", 0.05, "Scanning images…")
            total, _faces_new, skipped, indexed = index_library(
                session,
                library_id,
                Path(root_path),
                on_progress=on_progress,
                force=force,
            )
        finally:
            session.close()

        _update_job(job_id, "clustering", 0.9, "Clustering faces…")
        session = get_session()
        try:
            n = cluster_library_faces(session, library_id)
            face_total = session.execute(
                text(
                    """
                    SELECT COUNT(*) FROM faces f
                    JOIN photos p ON p.id = f.photo_id
                    WHERE p.library_id = :lid
                    """
                ),
                {"lid": library_id},
            ).scalar_one()
        finally:
            session.close()

        summary = (
            f"Complete. {n} persons from {face_total} faces "
            f"({indexed} photos indexed, {skipped} skipped, {total} total)."
        )
        _update_job(job_id, "done", 1.0, summary)
    except Exception as exc:  # noqa: BLE001
        err = f"{type(exc).__name__}: {exc}" if str(exc) else f"{type(exc).__name__}"
        try:
            _update_job(job_id, "failed", 0.0, err[:500])
        except Exception:
            pass


def run_queued_job(
    job_id: int, library_id: int, root_path: str, *, force: bool = False
) -> None:
    """Run one scan job synchronously (queue worker only)."""
    _run_scan(job_id, library_id, root_path, force=force)
