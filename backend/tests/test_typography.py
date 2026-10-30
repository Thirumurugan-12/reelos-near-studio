import numpy as np
import pytest
from PIL import Image

from reelos.media import composite, text_layer
from reelos.timeline import EditPlan, TextStyle


def test_legacy_styles_keep_their_serialized_contract():
    assert TextStyle(text="OLD").model_dump() == {
        "text": "OLD",
        "x": 0.5,
        "y": 0.23,
        "size": 0.075,
        "color": "#F4F4F2",
    }


@pytest.mark.parametrize("design", ["editorial", "pixel"])
def test_designed_titles_reveal_words_deterministically_and_hold(design):
    style = TextStyle(text="MY GLASSES\nSTORY", design=design, size=0.12)
    frames = [np.asarray(text_layer((360, 640), style, t, 0, 5)) for t in [0, 0.12, 0.4, 1, 2, 5]]
    assert frames[0][:, :, 3].sum() == 0
    assert 0 < frames[1][:, :, 3].sum() < frames[3][:, :, 3].sum()
    assert not np.array_equal(frames[1], frames[2])
    assert np.array_equal(frames[3], frames[4])
    assert frames[5][:, :, 3].sum() == 0
    # A colored accent panel and readable off-white glyphs are actually rendered.
    held = frames[3]
    assert ((held[:, :, 0] > 150) & (held[:, :, 1] < 80)).sum() > 100
    assert (held[:, :, :3].min(axis=2) > 220).sum() > 100


def test_new_design_preserves_real_foreground_occlusion():
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 2,
            "effects": [
                {
                    "id": "h",
                    "type": "behind_subject_text",
                    "start": 0,
                    "end": 2,
                    "subject_id": "0",
                    "params": {"text": "MY STORY", "design": "editorial"},
                }
            ],
        }
    )
    frame = Image.new("RGB", (180, 320), "blue")
    full = Image.new("L", frame.size, 255)
    assert np.array_equal(composite(frame, plan, 1, {"0": full}), np.asarray(frame))


def test_designed_label_fits_preview_and_export():
    style = TextStyle(text="Talking about childhood", design="editorial", y=0.88, size=0.04)
    for size in [(360, 640), (1080, 1920)]:
        layer = text_layer(size, style, 1, 0, 5, badge=True)
        box = layer.getbbox()
        assert box and box[0] > 0 and box[2] < size[0] and box[3] < size[1]


def test_design_revision_changes_only_the_selected_title():
    from reelos.planner import Revision, apply_revision

    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 2,
            "effects": [
                {
                    "id": "h",
                    "type": "behind_subject_text",
                    "start": 0,
                    "end": 2,
                    "subject_id": "0",
                    "params": {"text": "MY STORY"},
                }
            ],
        }
    )
    original = plan.model_dump()
    revised = apply_revision(
        plan,
        Revision(
            summary="Pixel title", changes=[{"effect_id": "h", "field": "design", "value": "pixel"}]
        ),
    )
    expected = plan.model_dump()
    expected["effects"][0]["params"]["design"] = "pixel"
    assert revised.model_dump() == expected
    assert plan.model_dump() == original
