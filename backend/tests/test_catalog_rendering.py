import numpy as np
import pytest

from reelos.catalog_contracts import catalog
from reelos.catalog_renderer import CatalogRenderer
from reelos.catalog_samples import illustrated_cards, illustrated_source, sample_params
from reelos.timeline import EditPlan


@pytest.mark.parametrize(
    "name", [r["id"] for r in catalog()] + ["glitter-spotlight", "editorial-cover", "glass-bento"]
)
def test_every_recipe_actually_draws_and_is_seek_deterministic(name):
    image, mask = illustrated_source()
    params = sample_params(name)
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 3,
            "effects": [
                {
                    "id": "fx",
                    "type": "catalog_effect",
                    "subject_id": "0",
                    "start": 0,
                    "end": 3,
                    "params": params.model_dump(),
                }
            ],
        }
    )
    a = CatalogRenderer(
        plan, cards={"fx": illustrated_cards()}, starts={"fx": (image, mask, (180.0, 200.0, 110.0))}
    )
    a.detector = None
    first = np.asarray(a.apply(image.copy(), 1.5, {"0": mask}))
    assert first.shape == (640, 360, 3) and first.dtype == np.uint8
    assert not np.array_equal(first, np.asarray(image)), name
    b = CatalogRenderer(
        plan, cards={"fx": illustrated_cards()}, starts={"fx": (image, mask, (180.0, 200.0, 110.0))}
    )
    b.detector = None
    b.apply(image.copy(), 0, {"0": mask})
    second = np.asarray(b.apply(image.copy(), 1.5, {"0": mask}))
    assert np.array_equal(first, second), f"{name} depends on frame visitation order"


def test_zero_value_bento_is_a_valid_flat_chart():
    image, mask = illustrated_source()
    params = sample_params("glass-bento").model_copy(deep=True)
    params.options.update(
        {"to": "0", "donut": "0%::Share", "kpi": "0::Value", "bars": "0|0|0::Bars"}
    )
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 3,
            "effects": [
                {
                    "id": "flat",
                    "type": "catalog_effect",
                    "subject_id": "0",
                    "start": 0,
                    "end": 3,
                    "params": params.model_dump(),
                }
            ],
        }
    )
    renderer = CatalogRenderer(plan, cards={"flat": illustrated_cards()})
    renderer.detector = None
    assert renderer.apply(image, 1.5, {"0": mask}).size == image.size
