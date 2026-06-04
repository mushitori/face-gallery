from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.services.thumbnail import photo_preview_bytes

router = APIRouter(prefix="/thumbs", tags=["thumbs"])


@router.get("/face/{face_id}")
def face_thumb(face_id: int, db: Session = Depends(get_db)) -> Response:
    row = db.execute(
        text("SELECT face_thumbnail FROM faces WHERE id = :id"),
        {"id": face_id},
    ).fetchone()
    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="Face thumbnail not found")
    return Response(content=row[0], media_type="image/webp")


@router.get("/person/{person_id}")
def person_thumb(person_id: int, db: Session = Depends(get_db)) -> Response:
    row = db.execute(
        text(
            """
            SELECT COALESCE(p.face_thumbnail, f.face_thumbnail)
            FROM persons p
            LEFT JOIN faces f ON f.id = p.representative_face_id
            WHERE p.id = :id
            """
        ),
        {"id": person_id},
    ).fetchone()
    if not row or not row[0]:
        rep = db.execute(
            text("SELECT representative_face_id FROM persons WHERE id = :id"),
            {"id": person_id},
        ).fetchone()
        if rep and rep[0]:
            return face_thumb(rep[0], db)
        raise HTTPException(status_code=404, detail="Person thumbnail not found")
    return Response(content=row[0], media_type="image/webp")


@router.get("/photo/{photo_id}")
def photo_thumb(photo_id: int, db: Session = Depends(get_db)) -> Response:
    row = db.execute(
        text(
            """
            SELECT p.path, l.root_path FROM photos p
            JOIN libraries l ON l.id = p.library_id
            WHERE p.id = :id
            """
        ),
        {"id": photo_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Photo not found")
    full = Path(row[1]) / row[0]
    data = photo_preview_bytes(full)
    if not data:
        raise HTTPException(status_code=404, detail="Could not read image")
    return Response(content=data, media_type="image/webp")
