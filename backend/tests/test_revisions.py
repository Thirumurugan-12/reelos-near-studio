import pytest

from reelos.planner import Revision, apply_revision
from reelos.timeline import EditPlan


def base():
    return EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_in": 1,
            "source_out": 21,
            "effects": [
                {
                    "id": "title",
                    "type": "behind_subject_text",
                    "start": 0,
                    "end": 3,
                    "subject_id": "0",
                    "params": {"text": "Hello"},
                },
                {
                    "id": "light",
                    "type": "subject_spotlight",
                    "start": 3,
                    "end": 8,
                    "subject_id": "0",
                },
            ],
        }
    )


def test_revision_only_changes_requested_fields_and_keeps_parent():
    parent = base()
    original = parent.model_dump()
    patch = Revision.model_validate(
        {
            "summary": "Lowered the title",
            "changes": [
                {"effect_id": "title", "field": "y", "value": 0.35},
            ],
        }
    )
    child = apply_revision(parent, patch)
    assert parent.model_dump() == original
    assert child.effects[0].params.y == 0.35
    changed = child.model_dump()
    changed["effects"][0]["params"]["y"] = original["effects"][0]["params"]["y"]
    assert changed == original


def test_graphic_copy_revision_preserves_template_timing_and_other_effects():
    parent = base()
    data = parent.model_dump()
    data["effects"].append(
        {
            "id": "illustration",
            "type": "graphic_insert",
            "start": 9,
            "end": 12,
            "subject_id": "0",
            "params": {"template": "glasses", "title": "My story", "body": "A pair of glasses."},
        }
    )
    parent = EditPlan.model_validate(data)
    expected = parent.model_dump()
    expected["effects"][2]["params"]["title"] = "Seeing clearly"
    child = apply_revision(
        parent,
        Revision(
            summary="Change insert heading",
            changes=[
                {
                    "effect_id": "illustration",
                    "field": "title",
                    "value": "Seeing clearly",
                }
            ],
        ),
    )
    assert child.model_dump() == expected
    assert parent.effects[2].params.title == "My story"


@pytest.mark.parametrize(
    "change",
    [
        {"effect_id": "missing", "field": "y", "value": 0.35},
        {"effect_id": "light", "field": "y", "value": 0.35},
        {"effect_id": "title", "field": "end", "value": 99},
        {"effect_id": "title", "field": "y", "value": -2},
    ],
)
def test_invalid_revision_fails_without_mutating_parent(change):
    parent = base()
    original = parent.model_dump()
    with pytest.raises(ValueError):
        apply_revision(parent, Revision(summary="change", changes=[change]))
    assert parent.model_dump() == original


def test_catalog_option_patch_preserves_other_options_and_parent():
    parent = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 5,
            "effects": [
                {
                    "id": "orbit",
                    "type": "catalog_effect",
                    "subject_id": "0",
                    "start": 1,
                    "end": 4,
                    "params": {
                        "fx": "orbit",
                        "text": "Story",
                        "options": {"count": 6, "speed": 1.2},
                    },
                }
            ],
        }
    )
    original = parent.model_dump()
    child = apply_revision(
        parent,
        Revision(
            summary="Slow orbit",
            changes=[{"effect_id": "orbit", "field": "options", "value": {"speed": 0.5}}],
        ),
    )
    expected = parent.model_dump()
    expected["effects"][0]["params"]["options"]["speed"] = 0.5
    assert child.model_dump() == expected and parent.model_dump() == original
