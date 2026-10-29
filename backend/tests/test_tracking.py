import json

import pytest
from PIL import Image, ImageDraw

from reelos.media import MaskTrack


def test_tracking_uses_source_time_and_does_not_fill_missing_frames(tmp_path):
    (tmp_path / "0").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"fps": 10, "subjects": ["0"]}))
    for index, left in [(0, 10), (1, 30)]:
        im = Image.new("L", (100, 100))
        ImageDraw.Draw(im).rectangle((left, 20, left + 19, 79), fill=255)
        im.save(tmp_path / "0" / f"{index:06d}.png")
    track = MaskTrack(tmp_path)
    frame = track.at(0.15, (100, 100))["0"]
    assert frame.getbbox() == (30, 20, 50, 80)
    assert frame.info["label_motion"][0] == pytest.approx(0.1)
    assert track.at(0.25, (100, 100)) == {}


def test_font_is_available_without_platform_specific_font_files(monkeypatch):
    from pathlib import Path

    from reelos.media import font

    assert font(32).getname()[0] == "Aileron"
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    face = font(32)
    assert face.getname()[0] == "Aileron"
