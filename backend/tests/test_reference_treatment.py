import numpy as np
from PIL import Image, ImageDraw

from reelos.media import composite
from reelos.timeline import EditPlan


def test_red_outline_and_black_background_protect_the_subject():
    frame = Image.new("RGB", (200, 300), (80, 140, 220))
    mask = Image.new("L", frame.size)
    ImageDraw.Draw(mask).rectangle((70, 70, 130, 250), fill=255)
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 1,
            "effects": [
                {
                    "id": "style",
                    "type": "subject_spotlight",
                    "start": 0,
                    "end": 1,
                    "subject_id": "0",
                    "params": {
                        "intensity": 1,
                        "background": "black",
                        "outline_width": 0.01,
                        "glow": 0.8,
                    },
                }
            ],
        }
    )
    result = composite(frame, plan, 0.5, {"0": mask})
    assert np.array_equal(result[150, 100], (80, 140, 220))
    assert max(result[10, 10]) == 0
    assert result[150, 68, 0] > 150 and result[150, 68, 0] > result[150, 68, 2] * 3


def test_monochrome_reference_treatment_keeps_foreground_in_color():
    frame = Image.new("RGB", (100, 200), (20, 150, 220))
    mask = Image.new("L", frame.size)
    ImageDraw.Draw(mask).rectangle((30, 50, 70, 150), fill=255)
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 1,
            "effects": [
                {
                    "id": "style",
                    "type": "subject_spotlight",
                    "start": 0,
                    "end": 1,
                    "subject_id": "0",
                    "params": {"intensity": 0, "background": "monochrome"},
                }
            ],
        }
    )
    result = composite(frame, plan, 0.5, {"0": mask})
    assert result[10, 10, 0] == result[10, 10, 1] == result[10, 10, 2]
    assert np.array_equal(result[100, 50], (20, 150, 220))
