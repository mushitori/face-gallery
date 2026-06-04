from pydantic import BaseModel


class JobOut(BaseModel):
    id: int
    library_id: int
    type: str
    status: str
    progress: float
    message: str | None = None
    force: bool = False
    created_at: str | None = None
    updated_at: str | None = None
    library_root_path: str | None = None
    queue_position: int | None = None


class JobsDashboardOut(BaseModel):
    active: JobOut | None = None
    queue: list[JobOut] = []
    history: list[JobOut] = []
