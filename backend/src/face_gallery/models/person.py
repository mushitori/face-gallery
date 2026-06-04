from pydantic import BaseModel


class PersonOut(BaseModel):
    id: int
    library_id: int
    display_name: str | None
    face_count: int
    photo_count: int
    representative_face_id: int | None


class PersonListResponse(BaseModel):
    items: list[PersonOut]
    library_id: int | None = None
