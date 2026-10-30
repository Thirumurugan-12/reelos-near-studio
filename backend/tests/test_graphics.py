import json

import numpy as np
import pytest
from PIL import Image

from reelos.graphics import GraphicTrack
from reelos.media import composite
from reelos.timeline import EditPlan


def test_graphic_insert_uses_its_own_time_and_leaves_other_frames_intact(tmp_path):
    for i, color in enumerate(["red", "green"]):
        Image.new("RGB", (90, 160), color).save(tmp_path / f"{i}.png")
    (tmp_path / "manifest.json").write_text(json.dumps({"fps": 30, "frames": ["0.png", "1.png"]}))
    track = GraphicTrack(tmp_path)
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 2,
            "effects": [
                {
                    "id": "insert",
                    "type": "graphic_insert",
                    "start": 1,
                    "end": 1.5,
                    "subject_id": "0",
                    "params": {
                        "template": "browser_demo",
                        "title": "Clear ideas",
                        "body": "Say what matters.",
                    },
                }
            ],
        }
    )
    source = Image.new("RGB", (90, 160), "blue")
    frames = {"insert": track}
    assert np.array_equal(composite(source, plan, 0.5, {}, graphics=frames)[0, 0], (0, 0, 255))
    assert np.array_equal(composite(source, plan, 1, {}, graphics=frames)[0, 0], (255, 0, 0))
    assert np.array_equal(composite(source, plan, 1.04, {}, graphics=frames)[0, 0], (0, 128, 0))
    assert np.array_equal(composite(source, plan, 1.6, {}, graphics=frames)[0, 0], (0, 0, 255))


def test_oversized_or_overlapping_graphic_work_is_rejected_before_rendering():
    def insert(id, start, end):
        return {
            "id": id,
            "type": "graphic_insert",
            "subject_id": "0",
            "start": start,
            "end": end,
            "params": {"template": "glasses", "title": "A story", "body": "A pair of glasses."},
        }

    for effects in [
        [insert("long", 0, 6)],
        [insert("a", 0, 2), insert("b", 1, 3)],
        [insert("a", 0, 1), insert("b", 2, 3), insert("c", 4, 5)],
    ]:
        with pytest.raises(ValueError, match="[Gg]raphic"):
            EditPlan.model_validate({"asset_id": "a" * 32, "source_out": 10, "effects": effects})
