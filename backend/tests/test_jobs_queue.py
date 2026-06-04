import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from face_gallery.config import get_settings
from face_gallery.db.connection import get_engine, init_db
from face_gallery.main import create_app
from face_gallery.services.queue_worker import (
    library_has_active_job,
    reset_stuck_jobs_on_startup,
)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    lib_dir = tmp_path / "photos"
    lib_dir.mkdir()
    monkeypatch.setenv("FACE_GALLERY_DB_PATH", str(db_file))
    get_settings.cache_clear()
    init_db()
    yield lib_dir
    get_settings.cache_clear()


def _insert_library(lib_dir) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO libraries (root_path) VALUES (:p)"),
            {"p": str(lib_dir)},
        )
        row = conn.execute(text("SELECT id FROM libraries LIMIT 1")).fetchone()
    assert row
    return int(row[0])


def _insert_job(library_id: int, status: str) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO jobs (library_id, type, status, progress, message, force)
                VALUES (:lid, 'scan', :st, 0, 'test', 0)
                """
            ),
            {"lid": library_id, "st": status},
        )
        row = conn.execute(text("SELECT id FROM jobs ORDER BY id DESC LIMIT 1")).fetchone()
    assert row
    return int(row[0])


def test_reset_stuck_jobs_on_startup(test_db):
    lid = _insert_library(test_db)
    job_id = _insert_job(lid, "indexing")
    n = reset_stuck_jobs_on_startup()
    assert n == 1
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT status, message FROM jobs WHERE id = :id"),
            {"id": job_id},
        ).fetchone()
    assert row[0] == "queued"
    assert "Re-queued" in row[1]


def test_library_has_active_job(test_db):
    from face_gallery.db.connection import get_session

    lid = _insert_library(test_db)
    session = get_session()
    try:
        assert not library_has_active_job(session, lid)
        _insert_job(lid, "queued")
        assert library_has_active_job(session, lid)
    finally:
        session.close()


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_enqueue_scan_and_409_duplicate(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    with TestClient(create_app()) as client:
        r1 = client.post(f"/libraries/{lid}/scan")
        assert r1.status_code == 200
        assert r1.json()["job_id"] > 0
        r2 = client.post(f"/libraries/{lid}/scan")
        assert r2.status_code == 409


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_jobs_dashboard_buckets(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    _insert_job(lid, "queued")
    _insert_job(lid, "done")
    with TestClient(create_app()) as client:
        r = client.get("/jobs/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert data["active"] is None
        assert len(data["queue"]) == 1
        assert data["queue"][0]["status"] == "queued"
        assert data["queue"][0]["queue_position"] == 1
        assert len(data["history"]) == 1
        assert data["history"][0]["status"] == "done"


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_list_jobs_buckets(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    _insert_job(lid, "indexing")
    with TestClient(create_app()) as client:
        active = client.get("/jobs", params={"bucket": "active"})
        assert active.status_code == 200
        assert len(active.json()) == 1
        assert active.json()[0]["status"] == "indexing"
