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
