from types import SimpleNamespace

import pytest

from reelos.config import Settings
from reelos.service import Editor


def setup_editor(tmp_path):
    editor = Editor(Settings(data_dir=tmp_path))
    asset = editor.store.put(
        "asset", "a" * 32, {"project_id": "b" * 32, "provider_file": "file-old"}
    )
    directory = editor.asset_dir(asset["id"])
    directory.mkdir(parents=True)
    (directory / "proxy.mp4").write_bytes(b"proxy fixture")
    return editor, asset


def test_cached_upload_is_refreshed_when_unavailable_to_current_key(tmp_path):
    editor, asset = setup_editor(tmp_path)
    uploaded = []
    editor.meta = SimpleNamespace(
        file_available=lambda id: False, upload=lambda path: uploaded.append(path) or "file-new"
    )
    try:
        assert editor.provider_file(asset) == "file-new"
        assert uploaded == [editor.asset_dir(asset["id"]) / "proxy.mp4"]
        assert editor.store.get("asset", asset["id"])["provider_file"] == "file-new"
    finally:
        editor.worker.shutdown()


def test_visible_cached_upload_is_reused(tmp_path):
    editor, asset = setup_editor(tmp_path)

    def unexpected_upload(path):
        raise AssertionError("Visible file should not be uploaded again")

    editor.meta = SimpleNamespace(file_available=lambda id: True, upload=unexpected_upload)
    try:
        assert editor.provider_file(asset) == "file-old"
    finally:
        editor.worker.shutdown()


def test_failed_refresh_preserves_existing_asset_record(tmp_path):
    editor, asset = setup_editor(tmp_path)

    def failed_upload(path):
        raise ValueError("Upload unavailable")

    editor.meta = SimpleNamespace(file_available=lambda id: False, upload=failed_upload)
    try:
        with pytest.raises(ValueError, match="Upload unavailable"):
            editor.provider_file(asset)
        assert editor.store.get("asset", asset["id"])["provider_file"] == "file-old"
    finally:
        editor.worker.shutdown()
