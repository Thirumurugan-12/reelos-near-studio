import pytest
from PIL import Image

from reelos.segmentation import save_masks


def test_empty_segmentation_is_not_a_successful_person_track(tmp_path):
    with pytest.raises(ValueError, match="No subjects"):
        save_masks("", tmp_path, width=360, height=640, fps=10)


def test_official_image_smoke_has_valid_geometry(tmp_path):
    # Real 2026-10-29 SAM response to our generated red square. No paid call in tests.
    text = (
        "<0f>0<|box;x1=32;y1=32;x2=96;y2=96;w=128;h=128|>"
        "<|mask;x=0;y=0;data=65,65,!!!!!(y:U@EM#s|>\n"
    )
    manifest = save_masks(text, tmp_path, 128, 128, 10)
    subject = manifest["subjects"][0]
    image = Image.open(tmp_path / subject / "000000.png")
    assert image.getpixel((64, 64)) > 200
    assert image.getpixel((0, 0)) == 0
