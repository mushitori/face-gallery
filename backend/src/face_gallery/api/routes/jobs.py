from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.models.job import JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobOut:
    row = db.execute(
        text(
            "SELECT id, library_id, type, status, progress, message FROM jobs WHERE id = :id"
        ),
        {"id": job_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut(
        id=row[0],
        library_id=row[1],
        type=row[2],
        status=row[3],
        progress=float(row[4]),
        message=row[5],
    )
