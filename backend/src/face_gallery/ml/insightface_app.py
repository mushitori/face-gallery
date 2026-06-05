from __future__ import annotations

import threading
from typing import Any

from face_gallery.ml.model_setup import find_model_pack, resolve_model_root

_lock = threading.Lock()
_app: Any | None = None


def reset_face_app_cache() -> None:
    global _app
    with _lock:
        _app = None


def get_face_app() -> Any:
    global _app
    if _app is not None:
        return _app
    with _lock:
        if _app is not None:
            return _app
        from insightface.app import FaceAnalysis

        pack = find_model_pack()
        root = resolve_model_root(pack)
        app = FaceAnalysis(
            name=pack.name,
            root=str(root),
            providers=["CPUExecutionProvider"],
        )
        app.prepare(ctx_id=-1, det_size=(640, 640))
        _app = app
        return _app


def warmup() -> None:
    get_face_app()
