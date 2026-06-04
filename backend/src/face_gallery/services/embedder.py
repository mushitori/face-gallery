from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from face_gallery.config import get_settings
from face_gallery.ml.insightface_app import get_face_app


@dataclass
class DetectedFace:
    bbox_x: float
    bbox_y: float
    bbox_w: float
    bbox_h: float
    det_score: float
    embedding: np.ndarray


def _resize_long_edge(img: np.ndarray, long_edge: int) -> np.ndarray:
    h, w = img.shape[:2]
    m = max(h, w)
    if m <= long_edge:
        return img
    scale = long_edge / m
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)


def _scalar_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    arr = np.asarray(value, dtype=np.float64).reshape(-1)
    return float(arr[0]) if arr.size else default


def _get_embedding(face: object) -> np.ndarray | None:
    emb = getattr(face, "normed_embedding", None)
    if emb is None:
        emb = getattr(face, "embedding", None)
    if emb is None:
        return None
    emb = np.asarray(emb, dtype=np.float32).reshape(-1)
    if emb.size == 0:
        return None
    norm = float(np.linalg.norm(emb))
    if norm > 0:
        emb = emb / norm
    return emb


def detect_faces(image_path: Path) -> tuple[list[DetectedFace], int, int]:
    settings = get_settings()
    img = cv2.imread(str(image_path))
    if img is None:
        return [], 0, 0
    h0, w0 = img.shape[:2]
    img = _resize_long_edge(img, settings.scan_resize_long_edge)
    faces = get_face_app().get(img)
    out: list[DetectedFace] = []
    for f in faces:
        emb = _get_embedding(f)
        if emb is None:
            continue
        bbox = np.asarray(f.bbox, dtype=np.float64).reshape(-1)
        if bbox.size < 4:
            continue
        x1, y1, x2, y2 = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        out.append(
            DetectedFace(
                bbox_x=x1,
                bbox_y=y1,
                bbox_w=x2 - x1,
                bbox_h=y2 - y1,
                det_score=_scalar_float(getattr(f, "det_score", 0.0)),
                embedding=emb,
            )
        )
    return out, w0, h0
