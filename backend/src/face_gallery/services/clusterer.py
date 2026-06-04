from __future__ import annotations

import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy import text
from sqlalchemy.orm import Session

from face_gallery.config import get_settings
from face_gallery.services.thumbnail import blob_to_embedding


def cluster_library_faces(session: Session, library_id: int) -> int:
    settings = get_settings()
    rows = session.execute(
        text(
            """
            SELECT f.id, f.embedding, f.det_score
            FROM faces f
            JOIN photos p ON p.id = f.photo_id
            WHERE p.library_id = :lid AND f.embedding IS NOT NULL
            """
        ),
        {"lid": library_id},
    ).fetchall()
    if not rows:
        session.execute(
            text("DELETE FROM persons WHERE library_id = :lid"),
            {"lid": library_id},
        )
        session.commit()
        return 0

    ids = [r[0] for r in rows]
    embs = np.stack([blob_to_embedding(r[1]) for r in rows])
    scores = np.array([r[2] for r in rows], dtype=np.float32)

    clustering = DBSCAN(
        eps=settings.dbscan_eps,
        min_samples=settings.dbscan_min_samples,
        metric="cosine",
        n_jobs=-1,
    )
    labels = clustering.fit_predict(embs)

    session.execute(
        text("DELETE FROM photo_persons WHERE person_id IN (SELECT id FROM persons WHERE library_id = :lid)"),
        {"lid": library_id},
    )
    session.execute(text("DELETE FROM persons WHERE library_id = :lid"), {"lid": library_id})
    session.execute(
        text(
            "UPDATE faces SET person_id = NULL WHERE photo_id IN (SELECT id FROM photos WHERE library_id = :lid)"
        ),
        {"lid": library_id},
    )
    session.commit()

    unique_labels = sorted({int(l) for l in labels if int(l) >= 0})
    person_count = 0
    for label in unique_labels:
        mask = labels == label
        cluster_ids = [ids[i] for i in range(len(ids)) if mask[i]]
        cluster_embs = embs[mask]
        centroid = cluster_embs.mean(axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm

        dists = np.linalg.norm(cluster_embs - centroid, axis=1)
        best_idx = int(np.argmin(dists + (1.0 - scores[mask]) * 0.01))
        rep_face_id = cluster_ids[best_idx]

        centroid_blob = centroid.astype(np.float32).tobytes()
        session.execute(
            text(
                """
                INSERT INTO persons (library_id, face_count, centroid, representative_face_id)
                VALUES (:lid, :fc, :centroid, :rep)
                """
            ),
            {"lid": library_id, "fc": len(cluster_ids), "centroid": centroid_blob, "rep": rep_face_id},
        )
        person_id = session.execute(text("SELECT last_insert_rowid()")).scalar_one()
        person_count += 1

        for fid in cluster_ids:
            session.execute(
                text("UPDATE faces SET person_id = :pid WHERE id = :fid"),
                {"pid": person_id, "fid": fid},
            )

        session.execute(
            text(
                """
                UPDATE persons SET face_thumbnail = (
                    SELECT face_thumbnail FROM faces WHERE id = representative_face_id
                ) WHERE id = :pid
                """
            ),
            {"pid": person_id},
        )

    session.execute(
        text(
            """
            INSERT OR IGNORE INTO photo_persons (photo_id, person_id)
            SELECT DISTINCT f.photo_id, f.person_id
            FROM faces f
            JOIN photos p ON p.id = f.photo_id
            WHERE p.library_id = :lid AND f.person_id IS NOT NULL
            """
        ),
        {"lid": library_id},
    )
    session.commit()
    return person_count
