from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.config import get_settings
from face_gallery.services.embedder import detect_faces
from face_gallery.services.thumbnail import embedding_to_blob, face_thumbnail_bytes

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
PROGRESS_INTERVAL_SEC = 0.75
PROGRESS_EVERY_N_SKIPS = 25


def iter_image_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(p)
    return files


def _rel_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _should_report_progress(
    idx: int,
    total: int,
    last_ts: float,
    *,
    force: bool = False,
) -> bool:
    if force or idx == 0 or idx >= total - 1:
        return True
    if idx % PROGRESS_EVERY_N_SKIPS == 0:
        return True
    return (time.monotonic() - last_ts) >= PROGRESS_INTERVAL_SEC


def index_library(
    session: Session,
    library_id: int,
    root_path: Path,
    on_progress: Callable[[float, str], None] | None = None,
) -> tuple[int, int]:
    settings = get_settings()
    root_path = root_path.resolve()
    files = iter_image_files(root_path)
    total = len(files)
    processed_faces = 0
    last_progress_ts = 0.0

    for idx, file_path in enumerate(files):
        rel = _rel_path(root_path, file_path)
        stat = file_path.stat()
        row = session.execute(
            text(
                "SELECT id, mtime, size FROM photos WHERE library_id = :lid AND path = :path"
            ),
            {"lid": library_id, "path": rel},
        ).fetchone()

        if row and row[1] == stat.st_mtime and row[2] == stat.st_size:
            session.commit()
            if on_progress and total and _should_report_progress(
                idx, total, last_progress_ts
            ):
                on_progress((idx + 1) / total * 0.85, f"Skipped {rel}")
                last_progress_ts = time.monotonic()
            continue

        if row:
            photo_id = row[0]
            session.execute(text("DELETE FROM faces WHERE photo_id = :pid"), {"pid": photo_id})
            session.execute(
                text(
                    """
                    UPDATE photos SET mtime = :m, size = :s, processed_at = datetime('now')
                    WHERE id = :id
                    """
                ),
                {"m": stat.st_mtime, "s": stat.st_size, "id": photo_id},
            )
        else:
            session.execute(
                text(
                    """
                    INSERT INTO photos (library_id, path, mtime, size)
                    VALUES (:lid, :path, :m, :s)
                    """
                ),
                {"lid": library_id, "path": rel, "m": stat.st_mtime, "s": stat.st_size},
            )
            photo_id = session.execute(text("SELECT last_insert_rowid()")).scalar_one()

        try:
            faces, w, h = detect_faces(file_path)
        except Exception as exc:  # noqa: BLE001
            session.execute(
                text(
                    "UPDATE photos SET face_count = 0, width = 0, height = 0 WHERE id = :id"
                ),
                {"id": photo_id},
            )
            session.commit()
            if on_progress and total:
                on_progress((idx + 1) / total * 0.85, f"Error {rel}: {exc}")
                last_progress_ts = time.monotonic()
            continue

        for fi, face in enumerate(faces):
            thumb = face_thumbnail_bytes(file_path, face)
            session.execute(
                text(
                    """
                    INSERT INTO faces (
                        photo_id, face_index, bbox_x, bbox_y, bbox_w, bbox_h,
                        det_score, embedding, face_thumbnail
                    ) VALUES (
                        :pid, :fi, :bx, :by, :bw, :bh, :ds, :emb, :thumb
                    )
                    """
                ),
                {
                    "pid": photo_id,
                    "fi": fi,
                    "bx": face.bbox_x,
                    "by": face.bbox_y,
                    "bw": face.bbox_w,
                    "bh": face.bbox_h,
                    "ds": face.det_score,
                    "emb": embedding_to_blob(face.embedding),
                    "thumb": thumb,
                },
            )
            processed_faces += 1

        session.execute(
            text(
                """
                UPDATE photos SET face_count = :fc, width = :w, height = :h,
                processed_at = datetime('now') WHERE id = :id
                """
            ),
            {"fc": len(faces), "w": w, "h": h, "id": photo_id},
        )
        session.commit()

        if on_progress and total and _should_report_progress(
            idx, total, last_progress_ts, force=True
        ):
            on_progress((idx + 1) / total * 0.85, f"Indexed {rel} ({len(faces)} faces)")
            last_progress_ts = time.monotonic()

    session.execute(
        text("UPDATE libraries SET last_scan_at = datetime('now') WHERE id = :lid"),
        {"lid": library_id},
    )
    session.commit()
    return total, processed_faces
