from __future__ import annotations

import logging
from pathlib import Path

from face_gallery.config import get_settings

logger = logging.getLogger(__name__)

MODEL_PACK_NAME = "buffalo_l"
DOWNLOAD_URL = (
    "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
)
REQUIRED_ONNX = ("det_10g.onnx", "w600k_r50.onnx")


def repo_model_pack() -> Path:
    return Path(__file__).resolve().parents[3] / "models" / MODEL_PACK_NAME


def resolve_model_root(pack_dir: Path) -> Path:
    settings = get_settings()
    pack_resolved = pack_dir.resolve()
    app_data = settings.app_data_dir.resolve()
    if str(pack_resolved).startswith(str(app_data)):
        return app_data
    return pack_resolved.parent.parent


def is_model_pack_complete(pack_dir: Path) -> bool:
    if not pack_dir.is_dir():
        return False
    return all((pack_dir / name).is_file() for name in REQUIRED_ONNX)


def find_model_pack() -> Path:
    """Locate buffalo_l pack directory; prefer dirs with required models."""
    settings = get_settings()
    candidates = [
        settings.model_dir,
        settings.app_data_dir / "models" / MODEL_PACK_NAME,
        settings.app_data_dir / "models" / "models" / MODEL_PACK_NAME,
        repo_model_pack(),
    ]
    for pack in candidates:
        if pack is None:
            continue
        p = Path(pack).resolve()
        if is_model_pack_complete(p):
            return p
    if settings.model_dir is not None:
        return Path(settings.model_dir).resolve()
    return settings.app_data_dir / "models" / MODEL_PACK_NAME


def ensure_models() -> Path:
    settings = get_settings()
    pack_dir = find_model_pack()

    if is_model_pack_complete(pack_dir):
        logger.info("Face models ready at %s", pack_dir)
        settings.model_dir = pack_dir
        from face_gallery.ml.insightface_app import warmup

        warmup()
        return pack_dir

    target = Path(settings.model_dir).resolve() if settings.model_dir else pack_dir
    root = resolve_model_root(target)
    dest = root / "models" / MODEL_PACK_NAME
    logger.info("Downloading InsightFace %s to %s …", MODEL_PACK_NAME, dest)

    from insightface.utils.storage import download

    download("models", MODEL_PACK_NAME, force=True, root=str(root))

    if not is_model_pack_complete(dest):
        missing = [name for name in REQUIRED_ONNX if not (dest / name).is_file()]
        raise RuntimeError(
            f"Face model pack incomplete at {dest}. "
            f"Missing: {', '.join(missing)}. "
            f"Manual download: {DOWNLOAD_URL}"
        )

    settings.model_dir = dest
    logger.info("Face models installed at %s", dest)

    from face_gallery.ml.insightface_app import reset_face_app_cache, warmup

    reset_face_app_cache()
    warmup()
    return dest
