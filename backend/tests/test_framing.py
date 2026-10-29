import numpy as np
from PIL import Image, ImageDraw

from reelos.media import frame_subject
from reelos.timeline import EditPlan


def test_framing_transforms_video_and_mask_together_and_creates_headroom():
    plan = EditPlan.model_validate(
        {"asset_id": "a" * 32, "source_out": 1, "framing": {"scale": 0.8, "offset_y": 0.2}}
    )
    video = Image.new("RGB", (100, 200), "red")
    mask = Image.new("L", video.size)
    ImageDraw.Draw(mask).rectangle((20, 20, 79, 179), fill=255)
    canvas, masks = frame_subject(video, {"0": mask}, plan.framing)
    assert masks["0"].point(lambda p: 255 if p >= 128 else 0).getbbox() == (26, 56, 74, 184)
    assert canvas.getpixel((50, 10))[0] < 180
    assert canvas.getpixel((50, 70))[0] == 255
    assert np.asarray(masks["0"])[:40].sum() == 0


def test_default_framing_keeps_pixels_unchanged():
    plan = EditPlan(asset_id="a" * 32, source_out=1)
    frame = Image.new("RGB", (90, 160), "red")
    canvas, _ = frame_subject(frame, {}, plan.framing)
    assert np.array_equal(frame, canvas)


def test_unreadable_headline_is_detected_instead_of_accepted():
    from reelos.media import headline_visibility
    from reelos.timeline import Headline

    effect = Headline(
        id="title",
        type="behind_subject_text",
        start=0,
        end=3,
        subject_id="0",
        params={"text": "YOUR STORY", "y": 0.1},
    )
    assert headline_visibility((180, 320), effect, Image.new("L", (180, 320), 255)) == 0
    assert headline_visibility((180, 320), effect, Image.new("L", (180, 320), 0)) == 1


def test_short_headline_stays_one_line_in_preview_and_export():
    from reelos.media import text_layer
    from reelos.timeline import TextStyle

    style = TextStyle(text="YOUR STORY", y=0.09, size=0.085)
    for width, height in [(360, 640), (1080, 1920)]:
        bounds = text_layer((width, height), style, 2, 0, 6).getbbox()
        assert bounds is not None
        assert bounds[3] - bounds[1] < height * 0.1
        assert bounds[2] - bounds[0] <= width * 0.9
