import shutil
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
    # 1 = keep every face as at least its own person (no one-off faces dropped as noise)
    dbscan_min_samples: int = 1
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
        canonical = self.app_data_dir / "models" / "buffalo_l"
        legacy = self.app_data_dir / "models" / "models" / "buffalo_l"
        if self.model_dir is None:
            repo_models = Path(__file__).resolve().parents[3] / "models" / "buffalo_l"
            if repo_models.exists() and any(repo_models.glob("*.onnx")):
                self.model_dir = repo_models
            else:
                self.model_dir = canonical

        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_cache_dir.mkdir(parents=True, exist_ok=True)
        (self.app_data_dir / "models").mkdir(parents=True, exist_ok=True)

        # Earlier builds used root=.../models, so InsightFace downloaded to models/models/buffalo_l
        if legacy.is_dir() and any(legacy.glob("*.onnx")) and not any(canonical.glob("*.onnx")):
            canonical.mkdir(parents=True, exist_ok=True)
            for onnx in legacy.glob("*.onnx"):
                shutil.move(str(onnx), str(canonical / onnx.name))
            self.model_dir = canonical
        elif canonical.is_dir() and any(canonical.glob("*.onnx")):
            self.model_dir = canonical


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.resolve_paths()
    return s
