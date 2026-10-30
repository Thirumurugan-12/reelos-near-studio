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


def test_broll_keeps_presenter_visible_and_only_overlays_lower_frame(tmp_path):
    Image.new("RGB", (360, 640), "red").save(tmp_path / "0.png")
    (tmp_path / "manifest.json").write_text(json.dumps({"fps": 30, "frames": ["0.png"]}))
    track = GraphicTrack(tmp_path)
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 3,
            "effects": [
                {
                    "id": "broll",
                    "type": "graphic_insert",
                    "start": 0,
                    "end": 3,
                    "subject_id": "0",
                    "params": {
                        "template": "glasses",
                        "title": "My glasses story",
                        "body": "A childhood memory.",
                        "presentation": "broll",
                    },
                }
            ],
        }
    )
    source = Image.new("RGB", (360, 640), "blue")
    result = composite(source, plan, 1, {}, graphics={"broll": track})
    assert np.array_equal(result[:380], np.asarray(source)[:380])
    assert np.array_equal(result[:, 0], np.asarray(source)[:, 0])
    assert not np.array_equal(result[450:580, 40:320], np.asarray(source)[450:580, 40:320])
    start = composite(source, plan, 0, {}, graphics={"broll": track})
    assert np.array_equal(start, np.asarray(source))


def test_legacy_graphic_style_serialization_stays_unchanged():
    from reelos.timeline import GraphicStyle

    assert (
        "presentation"
        not in GraphicStyle(template="glasses", title="Story", body="Glasses.").model_dump()
    )


def test_broll_reuses_the_existing_remotion_frames(tmp_path, monkeypatch):
    from pathlib import Path

    from reelos.graphics import prepare_graphics

    requests = []

    def fake_render(command, **kwargs):
        batch = json.loads(Path(command[-1]).read_text())
        requests.extend(batch)
        for request in batch:
            directory = Path(request["outputDir"])
            directory.mkdir(parents=True)
            Image.new("RGB", (90, 160), "red").save(directory / "0.png")
            (directory / "manifest.json").write_text(json.dumps({"fps": 30, "frames": ["0.png"]}))

    monkeypatch.setattr("reelos.graphics.subprocess.run", fake_render)
    data = {
        "asset_id": "a" * 32,
        "source_out": 3,
        "effects": [
            {
                "id": "g",
                "type": "graphic_insert",
                "start": 0,
                "end": 3,
                "subject_id": "0",
                "params": {"template": "glasses", "title": "Glasses", "body": "A memory."},
            }
        ],
    }
    legacy = prepare_graphics(EditPlan.model_validate(data), tmp_path)
    data["effects"][0]["params"]["presentation"] = "broll"
    overlay = prepare_graphics(EditPlan.model_validate(data), tmp_path)
    assert len(requests) == 1
    assert legacy["g"].directory == overlay["g"].directory
    assert "presentation" not in requests[0]["props"]


def test_presentation_revision_is_targeted_and_preserves_parent():
    from reelos.planner import Revision, apply_revision

    parent = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 3,
            "effects": [
                {
                    "id": "g",
                    "type": "graphic_insert",
                    "start": 0,
                    "end": 3,
                    "subject_id": "0",
                    "params": {"template": "glasses", "title": "Glasses", "body": "A memory."},
                }
            ],
        }
    )
    original = parent.model_dump()
    child = apply_revision(
        parent,
        Revision(
            summary="B-roll overlay",
            changes=[{"effect_id": "g", "field": "presentation", "value": "broll"}],
        ),
    )
    expected = parent.model_dump()
    expected["effects"][0]["params"]["presentation"] = "broll"
    assert child.model_dump() == expected
    assert parent.model_dump() == original
