from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from face_gallery.services.embedder import DetectedFace


def _crop_face_bgr(img: np.ndarray, face: DetectedFace, padding: float = 0.15) -> np.ndarray:
    h, w = img.shape[:2]
    x, y, bw, bh = face.bbox_x, face.bbox_y, face.bbox_w, face.bbox_h
    pad_w = bw * padding
    pad_h = bh * padding
    x1 = max(0, int(x - pad_w))
    y1 = max(0, int(y - pad_h))
    x2 = min(w, int(x + bw + pad_w))
    y2 = min(h, int(y + bh + pad_h))
    return img[y1:y2, x1:x2]


def face_thumbnail_bytes(image_path: Path, face: DetectedFace, size: int = 160) -> bytes:
    img = cv2.imread(str(image_path))
    if img is None:
        return b""
    crop = _crop_face_bgr(img, face)
    if crop.size == 0:
        return b""
    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    pil.thumbnail((size, size), Image.Resampling.LANCZOS)
    buf = BytesIO()
    pil.save(buf, format="WEBP", quality=85)
    return buf.getvalue()


def photo_preview_bytes(image_path: Path, long_edge: int = 512) -> bytes:
    img = cv2.imread(str(image_path))
    if img is None:
        return b""
    h, w = img.shape[:2]
    m = max(h, w)
    if m > long_edge:
        scale = long_edge / m
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    buf = BytesIO()
    pil.save(buf, format="WEBP", quality=85)
    return buf.getvalue()


def embedding_to_blob(emb: np.ndarray) -> bytes:
    return np.asarray(emb, dtype=np.float32).tobytes()


def blob_to_embedding(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)
