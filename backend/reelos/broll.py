"""Compact supporting visuals over live footage; deterministic, audio-neutral composition."""

from PIL import Image, ImageDraw, ImageOps

from reelos.typography import display_font


def _wrap(draw, text, face, width):
    lines, line = [], ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if line and draw.textlength(candidate, font=face) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    return lines + [line]


def broll_layer(asset, style, elapsed, duration):
    width, height = asset.size
    result = Image.new("RGBA", asset.size)
    enter = min(1.0, max(0.0, elapsed / 0.42))
    eased = 1 - (1 - enter) ** 3
    opacity = min(eased, max(0.0, min(1.0, (duration - elapsed) / 0.22)))
    if opacity <= 0:
        return result
    card_width, card_height = round(width * 0.88), round(height * 0.29)
    card = Image.new("RGBA", (card_width, card_height), "#101317")
    draw = ImageDraw.Draw(card)
    pad = max(5, round(width * 0.035))
    accent = style.accent
    draw.rectangle((0, 0, card_width, max(2, round(height * 0.003))), fill=accent)
    # Reuse the central illustration from the approved Remotion scene. Its full-screen
    # heading/footer stay outside this crop; the card redraws copy at readable sizes.
    illustration = asset.crop(
        (round(width * 0.045), round(height * 0.28), round(width * 0.955), round(height * 0.65))
    )
    art_size = (round(card_width * 0.42), card_height - pad * 2)
    illustration = ImageOps.contain(illustration, art_size, Image.Resampling.LANCZOS)
    card.paste(illustration, (pad, (card_height - illustration.height) // 2))
    left = round(card_width * 0.49)
    available = card_width - left - pad
    face = display_font("editorial", max(10, round(height * 0.032)))
    body_face = display_font("editorial", max(8, round(height * 0.017)))
    title = _wrap(draw, style.title.upper(), face, available)
    body = _wrap(draw, style.body, body_face, available)
    # Fit long copy without clipping or silently dropping words.
    while (
        len(title) * face.size * 1.16 + len(body) * body_face.size * 1.4 + pad * 3 > card_height
        or any(draw.textlength(line, font=face) > available for line in title)
        or any(draw.textlength(line, font=body_face) > available for line in body)
    ):
        if face.size <= 5 or body_face.size <= 5:
            raise ValueError("Use shorter B-roll text so the supporting card stays readable.")
        face = display_font("editorial", face.size - 1)
        body_face = display_font("editorial", body_face.size - 1)
        title = _wrap(draw, style.title.upper(), face, available)
        body = _wrap(draw, style.body, body_face, available)
    top = pad
    for line in title:
        draw.text((left, top), line, font=face, fill="#F4F4F2", anchor="lt")
        top += round(face.size * 1.16)
    top += pad * 0.6
    for line in body:
        draw.text((left, top), line, font=body_face, fill="#BCBFC7", anchor="lt")
        top += round(body_face.size * 1.4)
    mask = Image.new("L", card.size)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, card_width, card_height), radius=width * 0.025, fill=round(opacity * 255)
    )
    card.putalpha(mask)
    position = ((width - card_width) // 2, round(height * 0.65 + (1 - eased) * height * 0.035))
    result.alpha_composite(card, position)
    return result
