import pytest
from pydantic import ValidationError

from reelos.catalog_contracts import CatalogParams, catalog
from reelos.timeline import EditPlan


def test_all_45_distinct_recipes_are_exposed():
    rows = catalog()
    assert len(rows) == 45 and len({r["id"] for r in rows}) == 45
    assert {"orbit", "pause-point", "match-cut", "messages", "place-in-grid"} <= {
        r["id"] for r in rows
    }


def test_aliases_and_named_look_are_canonicalized():
    assert CatalogParams(fx="follow").fx == "tap"
    p = CatalogParams(fx="glitter-spotlight", text="HELLO")
    assert p.fx == "spotlight" and p.options["look"] == "sparkle"


@pytest.mark.parametrize(
    "data",
    [
        {"fx": "arbitrary-code"},
        {"fx": "orbit", "options": {"images": "/etc/passwd"}},
        {"fx": "orbit", "options": {"count": 100000}},
        {"fx": "orbit", "options": {"zoom": 2.1}},
        {"fx": "lean-in", "options": {"zoom": float("nan")}},
        {"fx": "lean-in", "options": {"unknown": 3}},
        {"fx": "messages", "options": {"grade": "warm"}},
        {"fx": "orbit", "media_ids": ["../private"]},
    ],
)
def test_invalid_or_unsafe_options_are_rejected(data):
    with pytest.raises(ValidationError):
        CatalogParams(**data)


def test_catalog_placement_keeps_canonical_timeline():
    p = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 5,
            "effects": [
                {
                    "id": "orbit1",
                    "type": "catalog_effect",
                    "subject_id": "0",
                    "start": 1,
                    "end": 4,
                    "params": {"fx": "orbit", "options": {"count": 5}},
                }
            ],
        }
    )
    assert p.effects[0].params.fx == "orbit"
    assert p.storyboard()[0]["source_start"] == 1


def test_media_must_belong_to_the_project_and_not_be_style_references():
    from reelos.timeline import validate_assets

    p = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 5,
            "effects": [
                {
                    "id": "cards",
                    "type": "catalog_effect",
                    "subject_id": "0",
                    "start": 1,
                    "end": 4,
                    "params": {"fx": "orbit", "media_ids": ["b" * 32]},
                }
            ],
        }
    )
    with pytest.raises(ValueError, match="supporting"):
        validate_assets(p, {"a" * 32: {"duration": 5}})


@pytest.mark.parametrize(
    "field,value",
    [
        ("donut", "101%::share"),
        ("kpi", "NaN::total"),
        ("bars", "-1|2::bars"),
        ("bars", "::bars"),
        ("bars", "1|nope::bars"),
    ],
)
def test_invalid_bento_numbers_fail_before_render(field, value):
    options = {
        "from": "0",
        "to": "100",
        "donut": "50%::share",
        "kpi": "100::total",
        "bars": "3|2|1::bars",
    }
    options[field] = value
    with pytest.raises(ValidationError):
        CatalogParams(fx="glass-bento", options=options)
