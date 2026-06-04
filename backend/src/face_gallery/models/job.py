from pydantic import BaseModel


class JobOut(BaseModel):
    id: int
    library_id: int
    type: str
    status: str
    progress: float
    message: str | None = None
