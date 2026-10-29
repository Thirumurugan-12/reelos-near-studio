import pytest
from pydantic import ValidationError

from reelos.timeline import EditPlan, validate_assets


def plan_data():
    return {
        "asset_id": "a" * 32,
        "source_in": 1,
        "source_out": 4,
        "effects": [{"id": "title", "type": "behind_subject_text", "start": 0,
                     "end": 2, "subject_id": "0", "params": {"text": "Hello"}}],
    }


def test_rejects_effect_outside_trimmed_output():
    data = plan_data()
    data["effects"][0]["end"] = 4
    with pytest.raises(ValidationError, match="effect.*outside"):
        EditPlan.model_validate(data)


@pytest.mark.parametrize("change", [
    {"source_out": 0}, {"source_in": float("nan")}, {"source_out": 40},
    {"asset_id": "../../secret"}, {"speed": 2},
])
def test_rejects_unsafe_or_unsupported_plan(change):
    with pytest.raises(ValidationError):
        EditPlan.model_validate(plan_data() | change)


def test_rejects_missing_asset_and_out_of_source_trim():
    plan = EditPlan.model_validate(plan_data())
    with pytest.raises(ValueError, match="asset"):
        validate_assets(plan, {})
    with pytest.raises(ValueError, match="duration"):
        validate_assets(plan, {plan.asset_id: {"duration": 2}})


def test_storyboard_is_derived_from_source_mapping():
    plan = EditPlan.model_validate(plan_data())
    beat = plan.storyboard()[0]
    assert beat["source_start"] == 1
    assert beat["source_end"] == 3
    assert beat["operation_id"] == "title"
