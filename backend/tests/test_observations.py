import json
from types import SimpleNamespace

import pytest

from reelos.planner import create_plan


def planned(observations, reference_duration=None):
    output = {
        "plan": {"asset_id": "a" * 32, "source_in": 0, "source_out": 20},
        "observations": observations,
    }
    client = SimpleNamespace(
        settings=SimpleNamespace(muse_model="fixture"),
        response=lambda *args, **kwargs: {
            "output": [{"content": [{"type": "output_text", "text": json.dumps(output)}]}]
        },
    )
    return create_plan(
        client,
        {"id": "a" * 32, "duration": 20},
        "file-source",
        "0",
        "A test edit",
        reference_duration=reference_duration,
    )


def test_observation_ranges_are_grounded_in_the_correct_media():
    _, observations = planned(
        [
            {"text": "Source gesture", "origin": "footage", "source_start": 2, "source_end": 4},
            {"text": "Reference color", "origin": "reference", "source_start": 1, "source_end": 5},
        ],
        reference_duration=5,
    )
    assert [o["timing"] for o in observations] == ["approximate", "approximate"]
    assert observations[0]["source_start"] == 2
    assert observations[1]["source_end"] == 5


@pytest.mark.parametrize(
    "origin,start,end",
    [
        ("footage", -1, 2),
        ("footage", 1, 21),
        ("footage", 3, 2),
        ("footage", 1, float("nan")),
        ("footage", True, 2),
        ("footage", "1", 2),
        ("reference", 1, 6),
        ("invented", 1, 2),
        ([], 1, 2),
        ({}, 1, 2),
    ],
)
def test_unusable_observation_timing_does_not_discard_a_valid_plan(origin, start, end):
    plan, observations = planned(
        [
            {
                "text": "Model interpretation",
                "origin": origin,
                "source_start": start,
                "source_end": end,
            }
        ],
        reference_duration=5,
    )
    assert plan.duration == 20
    assert observations[0]["timing"] == "unverified"
    assert observations[0]["source_start"] is None
    assert observations[0]["source_end"] is None
    assert observations[0]["origin"] in {"footage", "reference", "unknown"}


@pytest.mark.parametrize("payload", [[], None, "malformed", [{"text": 4}], [{"text": "   "}]])
def test_missing_analysis_is_explicitly_marked_without_inventing_evidence(payload):
    plan, observations = planned(payload)
    assert plan.duration == 20
    assert len(observations) == 1
    assert observations[0]["origin"] == "unknown"
    assert observations[0]["timing"] == "unverified"


def test_reference_observation_without_a_reference_is_not_attributed_as_evidence():
    _, observations = planned(
        [
            {
                "text": "Unverifiable reference claim",
                "origin": "reference",
                "source_start": 0,
                "source_end": 2,
            }
        ]
    )
    assert observations[0]["origin"] == "unknown"
    assert observations[0]["timing"] == "unverified"
