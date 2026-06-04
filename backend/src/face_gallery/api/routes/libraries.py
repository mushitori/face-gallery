import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.api.library_mapping import row_to_library
from face_gallery.api.queries import LIBRARY_SELECT
from face_gallery.models.photo import LibraryCreate, LibraryOut
from face_gallery.services.queue_worker import library_has_active_job, notify_worker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/libraries", tags=["libraries"])


def _fetch_library(db: Session, where: str, params: dict) -> LibraryOut | None:
    row = db.execute(
        text(f"{LIBRARY_SELECT} WHERE {where}"),
        params,
    ).fetchone()
    return row_to_library(row) if row else None


@router.get("", response_model=list[LibraryOut])
def list_libraries(db: Session = Depends(get_db)) -> list[LibraryOut]:
    rows = db.execute(text(f"{LIBRARY_SELECT} ORDER BY l.id")).fetchall()
    return [row_to_library(r) for r in rows]


@router.post("", response_model=LibraryOut)
def create_library(body: LibraryCreate, db: Session = Depends(get_db)) -> LibraryOut:
    root = Path(body.root_path).resolve()
    if not root.is_dir():
        raise HTTPException(status_code=400, detail="root_path is not a directory")
    existing = _fetch_library(db, "l.root_path = :p", {"p": str(root)})
    if existing:
        logger.info(
            "create_library: existing library id=%s path=%s",
            existing.id,
            existing.root_path,
        )
        return existing
    db.execute(
        text("INSERT INTO libraries (root_path) VALUES (:p)"),
        {"p": str(root)},
    )
    db.commit()
    out = _fetch_library(db, "l.root_path = :p", {"p": str(root)})
    assert out
    logger.info("create_library: inserted id=%s path=%s", out.id, out.root_path)
    return out


@router.post("/{library_id}/scan")
def start_scan(
    library_id: int,
    force: bool = Query(
        default=False,
        description="Re-process every image (ignore unchanged mtime). Use after a failed partial scan.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    row = db.execute(
        text("SELECT root_path FROM libraries WHERE id = :id"),
        {"id": library_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Library not found")
    if library_has_active_job(db, library_id):
        raise HTTPException(
            status_code=409,
            detail="A scan is already queued or running for this library",
        )
    insert = db.execute(
        text(
            """
            INSERT INTO jobs (library_id, type, status, progress, message, force)
            VALUES (:lid, 'scan', 'queued', 0, 'Queued', :force)
            """
        ),
        {"lid": library_id, "force": 1 if force else 0},
    )
    job_id = int(insert.lastrowid or 0)
    db.commit()
    logger.info(
        "start_scan: library_id=%s job_id=%s force=%s root_path=%s",
        library_id,
        job_id,
        force,
        row[0],
    )
    if job_id <= 0:
        logger.error(
            "start_scan: invalid job_id=%s after INSERT (lastrowid=%s)",
            job_id,
            insert.lastrowid,
        )
        raise HTTPException(status_code=500, detail="Failed to create scan job")
    notify_worker()
    return {"job_id": job_id}
