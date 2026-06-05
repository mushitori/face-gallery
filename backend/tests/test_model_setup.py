from pathlib import Path
from unittest.mock import patch

import pytest

from face_gallery.config import Settings
from face_gallery.ml import model_setup


def _write_required_onnx(pack_dir: Path) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    for name in model_setup.REQUIRED_ONNX:
        (pack_dir / name).write_bytes(b"fake")


def test_is_model_pack_complete_when_all_present(tmp_path: Path) -> None:
    pack = tmp_path / "buffalo_l"
    _write_required_onnx(pack)
    assert model_setup.is_model_pack_complete(pack) is True


def test_is_model_pack_complete_when_missing_files(tmp_path: Path) -> None:
    pack = tmp_path / "buffalo_l"
    pack.mkdir()
    (pack / "det_10g.onnx").write_bytes(b"fake")
    assert model_setup.is_model_pack_complete(pack) is False


def test_is_model_pack_complete_when_dir_missing(tmp_path: Path) -> None:
    assert model_setup.is_model_pack_complete(tmp_path / "buffalo_l") is False


def test_resolve_model_root_app_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_data = tmp_path / "FaceGallery"
    pack = app_data / "models" / "buffalo_l"
    settings = Settings(app_data_dir=app_data, model_dir=pack)
    settings.resolve_paths()
    monkeypatch.setattr(model_setup, "get_settings", lambda: settings)
    assert model_setup.resolve_model_root(pack) == app_data


def test_resolve_model_root_repo_layout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    backend = tmp_path / "backend"
    pack = backend / "models" / "buffalo_l"
    settings = Settings(app_data_dir=tmp_path / "appdata", model_dir=pack)
    settings.resolve_paths()
    monkeypatch.setattr(model_setup, "get_settings", lambda: settings)
    assert model_setup.resolve_model_root(pack) == backend


def test_ensure_skips_download_when_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_data = tmp_path / "FaceGallery"
    pack = app_data / "models" / "buffalo_l"
    _write_required_onnx(pack)
    settings = Settings(app_data_dir=app_data, model_dir=pack)
    settings.resolve_paths()
    monkeypatch.setattr(model_setup, "get_settings", lambda: settings)

    with patch("insightface.utils.storage.download") as download_mock:
        with patch("face_gallery.ml.insightface_app.warmup") as warmup_mock:
            result = model_setup.ensure_models()

    assert result == pack.resolve()
    download_mock.assert_not_called()
    warmup_mock.assert_called_once()


def test_ensure_downloads_when_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_data = tmp_path / "FaceGallery"
    pack = app_data / "models" / "buffalo_l"
    pack.mkdir(parents=True)
    settings = Settings(app_data_dir=app_data, model_dir=pack)
    settings.resolve_paths()
    monkeypatch.setattr(model_setup, "get_settings", lambda: settings)

    def fake_download(sub_dir: str, name: str, force: bool = False, root: str = "") -> str:
        dest = Path(root) / sub_dir / name
        _write_required_onnx(dest)
        return str(dest)

    with patch("insightface.utils.storage.download", side_effect=fake_download):
        with patch("face_gallery.ml.insightface_app.reset_face_app_cache") as reset_mock:
            with patch("face_gallery.ml.insightface_app.warmup") as warmup_mock:
                result = model_setup.ensure_models()

    assert model_setup.is_model_pack_complete(result)
    reset_mock.assert_called_once()
    warmup_mock.assert_called_once()


def test_ensure_raises_when_still_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_data = tmp_path / "FaceGallery"
    pack = app_data / "models" / "buffalo_l"
    settings = Settings(app_data_dir=app_data, model_dir=pack)
    settings.resolve_paths()
    monkeypatch.setattr(model_setup, "get_settings", lambda: settings)

    def fake_download(sub_dir: str, name: str, force: bool = False, root: str = "") -> str:
        dest = Path(root) / sub_dir / name
        dest.mkdir(parents=True, exist_ok=True)
        return str(dest)

    with patch("insightface.utils.storage.download", side_effect=fake_download):
        with pytest.raises(RuntimeError, match="Face model pack incomplete"):
            model_setup.ensure_models()
