import pytest
from pydantic import ValidationError

from reelos.timeline import EditPlan, validate_assets


def plan_data():
    return {
        "asset_id": "a" * 32,
        "source_in": 1,
        "source_out": 4,
        "effects": [
            {
                "id": "title",
                "type": "behind_subject_text",
                "start": 0,
                "end": 2,
                "subject_id": "0",
                "params": {"text": "Hello"},
            }
        ],
    }


def test_rejects_effect_outside_trimmed_output():
    data = plan_data()
    data["effects"][0]["end"] = 4
    with pytest.raises(ValidationError, match="effect.*outside"):
        EditPlan.model_validate(data)


@pytest.mark.parametrize(
    "change",
    [
        {"source_out": 0},
        {"source_in": float("nan")},
        {"source_out": 40},
        {"asset_id": "../../secret"},
        {"speed": 2},
    ],
)
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


def test_full_video_plan_keeps_late_effects_without_relaxing_reel_limit():
    data = plan_data() | {"output_mode": "full", "source_in": 0, "source_out": 167.9}
    data["effects"][0].update(start=120, end=125)
    plan = EditPlan.model_validate(data)
    assert plan.duration == 167.9
    assert plan.storyboard()[0]["source_end"] == 125
    with pytest.raises(ValidationError):
        EditPlan.model_validate(data | {"output_mode": "reel"})
    with pytest.raises(ValidationError):
        EditPlan.model_validate(data | {"source_out": 301})


def test_full_video_scope_rejects_a_short_plan_or_shifted_source():
    from reelos.planner import validate_output_scope

    plan = EditPlan(asset_id="a" * 32, output_mode="full", source_out=167.9)
    validate_output_scope(plan, 167.900417, "full")
    with pytest.raises(ValueError, match="entire source"):
        validate_output_scope(plan.model_copy(update={"source_out": 19.5}), 167.9, "full")
    with pytest.raises(ValueError, match="entire source"):
        validate_output_scope(plan.model_copy(update={"source_in": 10}), 167.9, "full")
