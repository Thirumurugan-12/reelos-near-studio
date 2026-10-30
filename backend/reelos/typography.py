"""Version-one editorial typography: fixed local fonts and seek-safe word choreography."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).with_name("fonts")


@lru_cache(maxsize=64)
def display_font(design: str, pixels: int):
    name = "GeistPixel-Square.ttf" if design == "pixel" else "Geist-Black.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), pixels)


def designed_text(size, style, elapsed: float, duration: float, badge: bool):
    # Quantize only to the composition's 30fps clock. Cache the long stationary hold.
    phase = min(round(max(0, elapsed) * 30), 40)
    exit_alpha = min(1.0, max(0.0, (duration - elapsed) / 0.22))
    layer = _plate(
        size,
        style.text,
        style.x,
        style.y,
        style.size,
        style.color,
        style.design,
        style.accent_color or "#F21F2B",
        phase,
        badge,
    )
    if exit_alpha >= 1:
        return layer
    layer = layer.copy()
    layer.putalpha(layer.getchannel("A").point(lambda a: round(a * exit_alpha)))
    return layer


@lru_cache(maxsize=16)
def _plate(size, text, x, y, scale, color, design, accent, phase, badge):
    width, height = size
    layer = Image.new("RGBA", size)
    draw = ImageDraw.Draw(layer)
    pixels = max(10, round(height * scale))
    max_width = width * (0.80 if badge else 0.84)
    # Explicit line breaks are editorial intent. Otherwise use balanced two-line titles.
    source_lines = text.splitlines() or [text]
    if not badge and len(source_lines) == 1 and len(text.split()) >= 3:
        words = text.split()
        split = max(1, len(words) // 2)
        source_lines = [" ".join(words[:split]), " ".join(words[split:])]
    while pixels > 5:
        face = display_font(design, pixels)
        if max(draw.textlength(line, font=face) for line in source_lines) <= max_width:
            break
        pixels -= 1
    if max(draw.textlength(line, font=face) for line in source_lines) > max_width:
        raise ValueError("Use shorter text or add spaces so the headline fits the frame.")
    line_height = pixels * 1.18
    block_height = line_height * len(source_lines)
    pad = height * 0.012
    center_y = min(height - block_height / 2 - pad * 2, max(block_height / 2 + pad * 2, height * y))
    center_x = min(width - max_width / 2 - pad, max(max_width / 2 + pad, width * x))
    rgb = tuple(bytes.fromhex(color[1:]))
    accent_rgb = tuple(bytes.fromhex(accent[1:]))
    clock = phase / 30
    word_index = 0
    for line_index, line in enumerate(source_lines):
        line_width = draw.textlength(line, font=face)
        cursor = center_x - line_width / 2
        top = center_y - block_height / 2 + line_index * line_height
        words = line.split()
        for word in words:
            # Limit total stagger even on long labels; all words settle by 1.3s.
            delay = min(word_index * 0.09, 0.65)
            progress = min(1.0, max(0.0, (clock - delay) / 0.4))
            eased = 1 - (1 - progress) ** 3
            alpha = round(255 * eased)
            shift = height * 0.035 * (1 - eased)
            length = draw.textlength(word, font=face)
            word_top = top + shift
            # The final headline line gets a red tab; labels get a charcoal pill.
            tab = not badge and line_index == len(source_lines) - 1
            if alpha:
                if badge or tab:
                    fill = (12, 15, 20, round(alpha * 0.94)) if badge else (*accent_rgb, alpha)
                    draw.rounded_rectangle(
                        (
                            cursor - pad * 0.5,
                            word_top - pad * 0.35,
                            cursor + length + pad * 0.5,
                            word_top + pixels + pad * 0.35,
                        ),
                        radius=pad * (0.7 if badge else 0.15),
                        fill=fill,
                    )
                bounds = draw.textbbox((0, 0), word, font=face)
                draw.text(
                    (cursor, word_top - bounds[1] + (pixels - bounds[3] + bounds[1]) / 2),
                    word,
                    font=face,
                    fill=(*rgb, alpha),
                    stroke_width=max(1, round(height * 0.001)),
                    stroke_fill=(0, 0, 0, alpha // 2),
                )
                if badge:
                    draw.rectangle(
                        (
                            cursor,
                            word_top + pixels + pad * 0.15,
                            cursor + length,
                            word_top + pixels + pad * 0.35,
                        ),
                        fill=(*accent_rgb, alpha),
                    )
            cursor += length + draw.textlength(" ", font=face)
            word_index += 1
    return layer
