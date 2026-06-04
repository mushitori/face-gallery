from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FACE_GALLERY_", env_file=".env")

    api_host: str = "127.0.0.1"
    api_port: int = 28765

    app_name: str = "FaceGallery"
    app_data_dir: Path | None = None
    db_path: Path | None = None
    thumb_cache_dir: Path | None = None
    model_dir: Path | None = None

    scan_resize_long_edge: int = 1024
    scan_batch_size: int = 16
    dbscan_eps: float = 0.45
    dbscan_min_samples: int = 2
    embedding_version: str = "buffalo_l_v1"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "tauri://localhost",
        "http://tauri.localhost",
    ]

    def resolve_paths(self) -> None:
        base = self.app_data_dir
        if base is None:
            base = Path.home() / "AppData" / "Local" / self.app_name
        self.app_data_dir = Path(base)
        if self.db_path is None:
            self.db_path = self.app_data_dir / "gallery.db"
        if self.thumb_cache_dir is None:
            self.thumb_cache_dir = self.app_data_dir / "thumbs"
        if self.model_dir is None:
            repo_models = Path(__file__).resolve().parents[3] / "models" / "buffalo_l"
            if repo_models.exists():
                self.model_dir = repo_models
            else:
                self.model_dir = self.app_data_dir / "models" / "buffalo_l"

        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.resolve_paths()
    return s
