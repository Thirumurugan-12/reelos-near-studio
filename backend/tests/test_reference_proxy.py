import subprocess

from reelos.media import inspect_media, make_proxy


def test_landscape_reference_keeps_its_full_composition(tmp_path):
    source = tmp_path / "landscape.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=s=1280x720:r=10:d=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(source),
        ],
        check=True,
    )
    reference = tmp_path / "reference.mp4"
    make_proxy(source, reference, portrait=False)
    meta = inspect_media(reference)
    assert (meta["width"], meta["height"]) == (640, 360)
