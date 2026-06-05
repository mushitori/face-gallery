from unittest.mock import patch

from fastapi.testclient import TestClient

from face_gallery.db.connection import init_db
from face_gallery.main import create_app


def test_health():
    init_db()
    with patch("face_gallery.main.ensure_models"):
        client = TestClient(create_app())
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "models": "ready"}
