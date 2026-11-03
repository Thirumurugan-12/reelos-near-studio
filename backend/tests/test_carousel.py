import io
import subprocess
import zipfile

from PIL import Image

from reelos import carousel, montage
from reelos.pricing import estimate_cost


def png(color, size=(512, 640)):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


def shot(clip_id, caption, start=0.5, duration=2.4):
    return {
        "clip_id": clip_id,
        "media_start": start,
        "duration": duration,
        "slow": False,
        "caption": caption,
    }


def test_pick_shots_spreads_across_the_reel():
    shots = [shot(f"{i:032x}", str(i)) for i in range(7)]
    picked = carousel.pick_shots(shots)
    assert [s["caption"] for s in picked] == ["0", "2", "3", "4", "6"]
    assert carousel.pick_shots(shots[:3]) == shots[:3]


def test_slides_are_4_by_5_and_typeset_locally():
    cover = carousel.compose_cover(png("navy"), "Nandi Hills", "29 AUG 2026", 4)
    slide = carousel.compose_slide(png("green"), "INTO THE MIST", "07:23", 2, 4)
    assert cover.size == slide.size == (1080, 1350)
    # The lime date tag is drawn by ReelOS, not by the image model.
    assert any(px == (234, 255, 129) for px in cover.getdata())


def test_make_builds_slides_and_zip_from_real_frames(tmp_path):
    clips, dirs = {}, {}
    for i in range(3):
        cid = f"{i + 1:032x}"
        d = tmp_path / cid
        d.mkdir()
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"color=c=0x{i * 40 + 30:02x}5060:s=320x568:d=4",
                "-pix_fmt",
                "yuv420p",
                str(d / "source.mp4"),
            ],
            check=True,
        )
        clips[cid] = {
            "id": cid,
            "duration": 4.0,
            "has_audio": False,
            "hdr": None,
            "recorded_at": "2026-08-29T07:2%d:00+05:30" % i,
        }
        dirs[cid] = d
    shots = [shot(cid, f"CAPTION {n}") for n, cid in enumerate(clips)]
    version = {
        "kind": "montage",
        "montage": {"title": "Nandi Hills", "style": "calm", "show_times": True, "shots": shots},
    }
    calls = []

    class Fake:
        def images(self, prompt, size, references):
            calls.append((prompt, size, len(references)))
            assert all(r.startswith("data:image/jpeg;base64,") for r in references)
            return [png("gray")]

    record = carousel.make(Fake(), version, clips, dirs, tmp_path / "out")
    assert record["slides"] == ["slide-01.png", "slide-02.png", "slide-03.png", "slide-04.png"]
    assert len(calls) == 4 and calls[0][2] == 3 and all(c[1] == "1024x1280" for c in calls)
    assert all("Do not add people" in c[0] for c in calls)
    with zipfile.ZipFile(tmp_path / "out" / "carousel.zip") as archive:
        assert sorted(archive.namelist()) == record["slides"]
    assert not (tmp_path / "out.partial").exists()
    assert montage.stored(version)["title"] == "Nandi Hills"


def test_muse_image_cost_is_per_generated_image():
    assert estimate_cost("muse-image-1.0", {"images_generated": 6, "input_tokens": 9}) == 0.06
    assert estimate_cost("muse-image-1.0", {}) is None


def test_paint_broll_job_needs_a_version():
    import pytest
    from pydantic import ValidationError

    from reelos.api import JobInput

    with pytest.raises(ValidationError):
        JobInput(action="paint_broll")
    assert JobInput(action="paint_broll", version_id="a" * 32).action == "paint_broll"
