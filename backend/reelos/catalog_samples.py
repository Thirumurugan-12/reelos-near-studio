"""Explicitly fictional preview inputs; never supplied to Muse as source facts."""

from PIL import Image, ImageDraw

from reelos.catalog_contracts import CatalogParams

TEXT = {
    "lineup": "IDEA|STORY|EDIT|SHARE",
    "locked-on": "SUBJECT",
    "backdrop-word": "STORY",
    "spotlight": "FOCUS",
    "the-bill": "Choose a story|Build a scene|Refine the edit",
    "todo": "Find the story|Add clarity|Share it",
    "comment-box": "STORY",
    "pause-point": "LOOK HERE",
    "uninstall": "REMOVE DISTRACTIONS",
    "reel-frame": "@creator",
    "shortcut-rain": "CMD|SHIFT|C|V",
    "reject-stamp": "REVIEWED",
    "cover-star": "CREATOR",
    "scribble": "YOUR STORY",
    "glass-widgets": "100",
    "red-collage": "STORY",
    "split-headline": "YOUR STORY|MADE CLEAR",
    "pastel-word": "STORY",
    "check-pills": "PLAN|EDIT|SHARE",
    "timeline": "YOUR STORY",
    "headline-box": "ONE IDEA|CLEARLY TOLD",
    "broll-split": "YOUR STORY",
    "phone-fan": "YOUR CLIPS|ONE STORY",
    "headline-wall": "Your opening::demo|Your story::demo|Your closing::demo",
    "checklist": "Choose::story|Create::edit|Share::result",
    "liquid-glass-graph": "Example progress",
    "match-cut": "STORY",
    "apple-toggles": "Clear story|Readable text|Good pacing",
    "led-sign": "YOUR STORY|IN FOCUS",
    "over-the-shoulder-zoom": "First example|Second example",
    "messages": "Your first idea|Another thought|A clear ending",
}
OPTIONS = {
    "countdown-flip": {"from": "3"},
    "cover-star": {"lines": "One clear idea|Your own voice", "issue": "DEMO ISSUE"},
    "red-collage": {"lines": "One idea|A clear voice|A better edit", "tag": "STORY NOTES"},
    "split-headline": {"hl": "CLEAR", "pill": "CREATOR NOTES"},
    "timeline": {"sub": "DEMONSTRATION", "tc": "00:00:00"},
    "profile-wall": {"count": 9, "label": "Example clips"},
    "tier-list": {
        "title": "Demo ranking",
        "item": "Your pick",
        "others": "Option A|Option B|Option C",
    },
    "headline-wall": {"total": "3", "label": "Story beats"},
    "checklist": {"title": "EDITING CHECKLIST"},
    "liquid-glass-graph": {"from": "0", "to": "100"},
    "over-the-shoulder-zoom": {"to": "100|200"},
    "messages": {"title": "Example messages"},
    "comment-box": {"handle": "@creator", "reply": "An illustrated reply", "chip": "Demo"},
}


def sample_params(name):
    if name == "glass-bento":
        return CatalogParams(
            fx=name,
            text="Example progress",
            options={
                "from": "0",
                "to": "100",
                "donut": "50%::Demo share",
                "kpi": "100::Demo metric",
                "bars": "3|2|1::Demo bars",
            },
        )
    return CatalogParams(fx=name, text=TEXT.get(name, "YOUR STORY"), options=OPTIONS.get(name, {}))


def illustrated_source(size=(360, 640)):
    w, h = size
    im = Image.new("RGB", size, "#d5cfc4")
    draw = ImageDraw.Draw(im)
    for x in range(0, w, max(1, w // 12)):
        draw.line((x, 0, x, h), fill="#bcb8b1", width=max(1, w // 180))
    mask = Image.new("L", size)
    md = ImageDraw.Draw(mask)
    body = [
        (w * 0.2, h),
        (w * 0.22, h * 0.51),
        (w * 0.38, h * 0.43),
        (w * 0.62, h * 0.43),
        (w * 0.78, h * 0.51),
        (w * 0.8, h),
    ]
    head = (w * 0.34, h * 0.17, w * 0.66, h * 0.45)
    draw.polygon(body, fill="#335e69")
    md.polygon(body, fill=255)
    draw.ellipse(head, fill="#bb886d")
    md.ellipse(head, fill=255)
    draw.arc(
        (w * 0.32, h * 0.15, w * 0.68, h * 0.44), 180, 360, fill="#26272a", width=max(2, w // 25)
    )
    for x in [0.43, 0.57]:
        draw.ellipse((w * (x - 0.014), h * 0.29, w * (x + 0.014), h * 0.305), fill="#191f23")
    draw.arc(
        (w * 0.44, h * 0.32, w * 0.56, h * 0.38), 0, 160, fill="#643c34", width=max(1, w // 150)
    )
    return im, mask


def illustrated_cards():
    cards = []
    for i, col in enumerate(
        [
            "#164e63",
            "#4c1d95",
            "#115e59",
            "#7f1d1d",
            "#78350f",
            "#1e3a8a",
            "#831843",
            "#365314",
            "#44403c",
        ]
    ):
        im = Image.new("RGB", (180, 320), col)
        d = ImageDraw.Draw(im)
        d.rectangle((15, 30, 165, 240), outline="#f4eee0", width=3)
        d.text((45, 260), f"Clip {i + 1}", fill="white")
        cards.append(im)
    return cards
