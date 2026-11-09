"""Stream actual supporting-video cutaways; the main recording keeps its audio."""

import math
import subprocess

from PIL import Image


class FootageTrack:
    def __init__(self, source, source_in, duration, width, fps):
        self.source = source
        self.source_in = source_in
        self.duration = duration
        self.size = (width, width * 16 // 9)
        self.fps = fps

    def __enter__(self):
        from reelos.media import portrait_filter

        if not self.source.is_file():
            raise ValueError("Supporting cutaway video is unavailable.")
        self.decoder = subprocess.Popen(
            [
                "ffmpeg",
                "-v",
                "error",
                "-ss",
                str(self.source_in),
                "-i",
                str(self.source),
                "-an",
                "-vf",
                portrait_filter(self.size[0], self.fps),
                "-frames:v",
                str(math.ceil(self.duration * self.fps)),
                "-pix_fmt",
                "rgb24",
                "-f",
                "rawvideo",
                "pipe:1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return self

    def frame(self):
        expected = self.size[0] * self.size[1] * 3
        raw = self.decoder.stdout.read(expected)
        if len(raw) != expected:
            raise ValueError("Supporting cutaway video ended before its requested interval.")
        return Image.frombytes("RGB", self.size, raw)

    def __exit__(self, *_):
        if self.decoder.poll() is None:
            self.decoder.kill()
        self.decoder.wait(timeout=30)
        self.decoder.stdout.close()


def prepare_footage(plan, asset_root, width, stack):
    effects = [e for e in plan.effects if e.type == "footage_insert"]
    if effects and asset_root is None:
        raise ValueError("Supporting cutaways require the project media store.")
    return {
        effect.id: stack.enter_context(
            FootageTrack(
                asset_root / "assets" / effect.params.asset_id / "source.mp4",
                effect.params.source_in,
                effect.end - effect.start,
                width,
                plan.fps,
            )
        )
        for effect in effects
    }
