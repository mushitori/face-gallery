from __future__ import annotations

import threading
from typing import Any

from face_gallery.config import get_settings

_lock = threading.Lock()
_app: Any | None = None


def get_face_app() -> Any:
    global _app
    if _app is not None:
        return _app
    with _lock:
        if _app is not None:
            return _app
        from insightface.app import FaceAnalysis

        settings = get_settings()
        # InsightFace resolves models at {root}/models/{name}/
        model_pack = settings.model_dir
        name = model_pack.name
        root = str(model_pack.parent.parent)
        app = FaceAnalysis(name=name, root=root, providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        _app = app
        return _app


def warmup() -> None:
    get_face_app()
