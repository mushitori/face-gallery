from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.api.deps import get_db
from face_gallery.models.person import PersonListResponse, PersonOut
from face_gallery.models.photo import PhotoListResponse, PhotoOut

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("", response_model=PersonListResponse)
def list_persons(
    library_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PersonListResponse:
    if library_id is not None:
        rows = db.execute(
            text(
                """
                SELECT p.id, p.library_id, p.display_name, p.face_count, p.representative_face_id,
                       (SELECT COUNT(*) FROM photo_persons pp WHERE pp.person_id = p.id) AS photo_count
                FROM persons p
                WHERE p.library_id = :lid
                ORDER BY photo_count DESC, p.id
                """
            ),
            {"lid": library_id},
        ).fetchall()
    else:
        rows = db.execute(
            text(
                """
                SELECT p.id, p.library_id, p.display_name, p.face_count, p.representative_face_id,
                       (SELECT COUNT(*) FROM photo_persons pp WHERE pp.person_id = p.id) AS photo_count
                FROM persons p
                ORDER BY photo_count DESC, p.id
                """
            )
        ).fetchall()
    items = [
        PersonOut(
            id=r[0],
            library_id=r[1],
            display_name=r[2],
            face_count=r[3],
            photo_count=r[5],
            representative_face_id=r[4],
        )
        for r in rows
    ]
    return PersonListResponse(items=items, library_id=library_id)


@router.get("/{person_id}/photos", response_model=PhotoListResponse)
def person_photos(
    person_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=60, ge=1, le=200),
    db: Session = Depends(get_db),
) -> PhotoListResponse:
    total = db.execute(
        text("SELECT COUNT(*) FROM photo_persons WHERE person_id = :pid"),
        {"pid": person_id},
    ).scalar_one()
    offset = (page - 1) * page_size
    rows = db.execute(
        text(
            """
            SELECT ph.id, ph.library_id, ph.path, ph.face_count
            FROM photos ph
            JOIN photo_persons pp ON pp.photo_id = ph.id
            WHERE pp.person_id = :pid
            ORDER BY ph.path
            LIMIT :lim OFFSET :off
            """
        ),
        {"pid": person_id, "lim": page_size, "off": offset},
    ).fetchall()
    items = [
        PhotoOut(id=r[0], library_id=r[1], path=r[2], face_count=r[3]) for r in rows
    ]
    return PhotoListResponse(items=items, total=total, page=page, page_size=page_size)
