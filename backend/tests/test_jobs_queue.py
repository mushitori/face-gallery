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


def _insert_job(
    library_id: int,
    status: str,
    *,
    progress: float = 0,
    message: str = "test",
) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO jobs (library_id, type, status, progress, message, force)
                VALUES (:lid, 'scan', :st, :pr, :msg, 0)
                """
            ),
            {"lid": library_id, "st": status, "pr": progress, "msg": message},
        )
        row = conn.execute(text("SELECT id FROM jobs ORDER BY id DESC LIMIT 1")).fetchone()
    assert row
    return int(row[0])


def test_library_has_active_job_includes_paused(test_db):
    from face_gallery.db.connection import get_session

    lid = _insert_library(test_db)
    session = get_session()
    try:
        _insert_job(lid, "paused", progress=0.42)
        assert library_has_active_job(session, lid)
    finally:
        session.close()


def test_pick_next_job_skips_paused(test_db):
    from face_gallery.services.queue_worker import _pick_next_job

    lid = _insert_library(test_db)
    _insert_job(lid, "paused", progress=0.5, message="Processed 50%")
    assert _pick_next_job() is None


def test_pick_next_job_picks_queued_not_paused(test_db):
    from face_gallery.services.queue_worker import _pick_next_job

    lid = _insert_library(test_db)
    _insert_job(lid, "paused")
    queued_id = _insert_job(lid, "queued")
    picked = _pick_next_job()
    assert picked is not None
    assert picked[0] == queued_id


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_jobs_dashboard_includes_paused_and_cancelled(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    _insert_job(lid, "queued")
    _insert_job(lid, "paused", progress=0.42, message="Processed 42%")
    _insert_job(lid, "cancelled", message="Cancelled")
    with TestClient(create_app()) as client:
        r = client.get("/jobs/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert len(data["queue"]) == 2
        statuses = {j["status"] for j in data["queue"]}
        assert statuses == {"queued", "paused"}
        paused = next(j for j in data["queue"] if j["status"] == "paused")
        assert paused["queue_position"] is None
        queued = next(j for j in data["queue"] if j["status"] == "queued")
        assert queued["queue_position"] == 1
        assert any(j["status"] == "cancelled" for j in data["history"])


@patch("face_gallery.main.reset_stuck_jobs_on_startup", return_value=0)
@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_pause_job_only_while_indexing(_mock_start, _mock_stop, _mock_reset, test_db):
    lid = _insert_library(test_db)
    queued_id = _insert_job(lid, "queued")
    indexing_id = _insert_job(lid, "indexing")
    clustering_id = _insert_job(lid, "clustering")
    with TestClient(create_app()) as client:
        assert client.post(f"/jobs/{queued_id}/pause").status_code == 409
        assert client.post(f"/jobs/{clustering_id}/pause").status_code == 409
        assert client.post(f"/jobs/{indexing_id}/pause").status_code == 204
        engine = get_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT pause_requested FROM jobs WHERE id = :id"),
                {"id": indexing_id},
            ).fetchone()
        assert row[0] == 1


@patch("face_gallery.main.reset_stuck_jobs_on_startup", return_value=0)
@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_cancel_job_queued_and_paused(_mock_start, _mock_stop, _mock_reset, test_db):
    lid = _insert_library(test_db)
    queued_id = _insert_job(lid, "queued")
    paused_id = _insert_job(lid, "paused")
    indexing_id = _insert_job(lid, "indexing")
    with TestClient(create_app()) as client:
        assert client.post(f"/jobs/{queued_id}/cancel").status_code == 204
        assert client.post(f"/jobs/{paused_id}/cancel").status_code == 204
        assert client.post(f"/jobs/{indexing_id}/cancel").status_code == 409


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_resume_job(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    paused_id = _insert_job(lid, "paused", progress=0.42, message="Processed 42%")
    with TestClient(create_app()) as client:
        with patch("face_gallery.api.routes.jobs.notify_worker") as notify:
            r = client.post(f"/jobs/{paused_id}/resume")
            assert r.status_code == 204
            notify.assert_called_once()
        engine = get_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT status, progress, message FROM jobs WHERE id = :id"),
                {"id": paused_id},
            ).fetchone()
        assert row[0] == "queued"
        assert row[1] == pytest.approx(0.42)
        assert row[2] == "Queued"


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_retry_cancelled_job(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    cancelled_id = _insert_job(lid, "cancelled", message="Cancelled")
    with TestClient(create_app()) as client:
        with patch("face_gallery.api.routes.jobs.notify_worker") as notify:
            r = client.post(f"/jobs/{cancelled_id}/retry")
            assert r.status_code == 204
            notify.assert_called_once()
        engine = get_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT status, progress, message FROM jobs WHERE id = :id"),
                {"id": cancelled_id},
            ).fetchone()
        assert row[0] == "queued"
        assert row[1] == 0
        assert row[2] == "Queued"


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_retry_failed_job(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    failed_id = _insert_job(lid, "failed", message="RuntimeError: test")
    with TestClient(create_app()) as client:
        with patch("face_gallery.api.routes.jobs.notify_worker") as notify:
            r = client.post(f"/jobs/{failed_id}/retry")
            assert r.status_code == 204
            notify.assert_called_once()
        engine = get_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT status, progress, message FROM jobs WHERE id = :id"),
                {"id": failed_id},
            ).fetchone()
        assert row[0] == "queued"
        assert row[1] == 0
        assert row[2] == "Queued"


@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_retry_cancelled_409_when_library_busy(_mock_start, _mock_stop, test_db):
    lid = _insert_library(test_db)
    _insert_job(lid, "queued")
    cancelled_id = _insert_job(lid, "cancelled")
    with TestClient(create_app()) as client:
        assert client.post(f"/jobs/{cancelled_id}/retry").status_code == 409


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


@patch("face_gallery.main.reset_stuck_jobs_on_startup", return_value=0)
@patch("face_gallery.main.stop_queue_worker")
@patch("face_gallery.main.start_queue_worker")
def test_list_jobs_buckets(_mock_start, _mock_stop, _mock_reset, test_db):
    lid = _insert_library(test_db)
    _insert_job(lid, "indexing")
    with TestClient(create_app()) as client:
        active = client.get("/jobs", params={"bucket": "active"})
        assert active.status_code == 200
        assert len(active.json()) == 1
        assert active.json()[0]["status"] == "indexing"
