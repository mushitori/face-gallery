import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.models.photo import LibraryCreate, LibraryOut
from face_gallery.services.job_runner import start_scan_job_async

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=list[LibraryOut])
def list_libraries(db: Session = Depends(get_db)) -> list[LibraryOut]:
    rows = db.execute(
        text("SELECT id, root_path, last_scan_at FROM libraries ORDER BY id")
    ).fetchall()
    return [
        LibraryOut(id=r[0], root_path=r[1], last_scan_at=r[2]) for r in rows
    ]


@router.post("", response_model=LibraryOut)
def create_library(body: LibraryCreate, db: Session = Depends(get_db)) -> LibraryOut:
    root = Path(body.root_path).resolve()
    if not root.is_dir():
        raise HTTPException(status_code=400, detail="root_path is not a directory")
    existing = db.execute(
        text("SELECT id, root_path, last_scan_at FROM libraries WHERE root_path = :p"),
        {"p": str(root)},
    ).fetchone()
    if existing:
        out = LibraryOut(id=existing[0], root_path=existing[1], last_scan_at=existing[2])
        logger.info(
            "create_library: existing library id=%s path=%s",
            out.id,
            out.root_path,
        )
        return out
    db.execute(
        text("INSERT INTO libraries (root_path) VALUES (:p)"),
        {"p": str(root)},
    )
    db.commit()
    row = db.execute(
        text("SELECT id, root_path, last_scan_at FROM libraries WHERE root_path = :p"),
        {"p": str(root)},
    ).fetchone()
    assert row
    out = LibraryOut(id=row[0], root_path=row[1], last_scan_at=row[2])
    logger.info("create_library: inserted id=%s path=%s", out.id, out.root_path)
    return out


@router.post("/{library_id}/scan")
async def start_scan(
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
    insert = db.execute(
        text(
            """
            INSERT INTO jobs (library_id, type, status, progress, message)
            VALUES (:lid, 'scan', 'queued', 0, 'Queued')
            """
        ),
        {"lid": library_id},
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
    await start_scan_job_async(job_id, library_id, row[0], force=force)
    return {"job_id": job_id}
