from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from face_gallery.config import get_settings

_lock = threading.Lock()
_app: Any | None = None


def _find_model_pack() -> Path:
    """Locate buffalo_l pack (directory containing *.onnx)."""
    settings = get_settings()
    repo_pack = Path(__file__).resolve().parents[3] / "models" / "buffalo_l"
    candidates = [
        settings.model_dir,
        settings.app_data_dir / "models" / "buffalo_l",
        settings.app_data_dir / "models" / "models" / "buffalo_l",
        repo_pack,
    ]
    for pack in candidates:
        if pack is None:
            continue
        p = Path(pack).resolve()
        if p.is_dir() and any(p.glob("*.onnx")):
            return p
    return Path(settings.model_dir).resolve()


def get_face_app() -> Any:
    global _app
    if _app is not None:
        return _app
    with _lock:
        if _app is not None:
            return _app
        from insightface.app import FaceAnalysis

        pack = _find_model_pack()
        name = pack.name
        settings = get_settings()
        # InsightFace resolves {root}/models/{name}/ — root must be app data (or repo root), not .../models
        if str(pack).startswith(str(settings.app_data_dir.resolve())):
            root = str(settings.app_data_dir)
        else:
            root = str(pack.parent.parent)
        app = FaceAnalysis(name=name, root=root, providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        _app = app
        return _app


def warmup() -> None:
    get_face_app()
