from pydantic import BaseModel


class LibraryCreate(BaseModel):
    root_path: str


class LibraryOut(BaseModel):
    id: int
    root_path: str
    last_scan_at: str | None
    photo_count: int = 0
    person_count: int = 0
    cover_person_id: int | None = None


class PhotoOut(BaseModel):
    id: int
    library_id: int
    path: str
    face_count: int


class PhotoListResponse(BaseModel):
    items: list[PhotoOut]
    total: int
    page: int
    page_size: int
