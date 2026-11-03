"""Build the ReelOS live demo (HyperFrames) from real screen recordings.

Recordings: assets/single.mp4 and assets/multi.mp4 are unedited 1440x900 captures of the real
app making real Meta calls (data/recording/*.events.json logs every click and job stage).
Waiting time is shortened with labelled speed-ups and jump cuts; nothing is simulated.

Run: python3 build.py  (rewrites index.html and compositions/*.html)
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
COMP = ROOT / "compositions"
COMP.mkdir(exist_ok=True)

INK, LIME, BG, MUTED = "#F4F4F1", "#EAFF81", "#0B0F0D", "#9AA39D"
REC_W, REC_H = 1440, 900
FRAME_X, FRAME_Y, FRAME_W, FRAME_H = 520, 120, 1320, 825  # browser frame on screen
SCALE0 = FRAME_W / REC_W

# Each segment: source [a, b), playback rate, zoom (x, y, factor) in recording pixels or None,
# step number, headline, detail, badge (shown when time is shortened).
SINGLE = [
    (2.0, 13.4, 1.3, (1250, 300, 1.9), "01", "Say what you want.", "Describe the edit in plain language. Pick who to track.", None),
    (13.4, 20.0, 1.3, (1270, 620, 1.7), "02", "SAM 3.1 finds everyone.", "Five people detected in this clip. Choose the speaker.", None),
    (20.0, 38.4, 2, (380, 190, 1.55), "03", "Muse Spark plans the edit.", "A timed, validated plan: headline, spotlight, label, B-roll.", "2× · real run"),
    (38.4, 58.4, 10, None, "04", "Illustrate. Render.", "HyperFrames draws the B-roll; the compositor renders every frame.", "4 min → 4 s · real run"),
    (268.0, 287.8, 10, None, "04", "Illustrate. Render.", "HyperFrames draws the B-roll; the compositor renders every frame.", "4 min → 4 s · real run"),
    (292.6, 298.6, 1, (585, 250, 1.55), "05", "A real edit.", "Headline behind the speaker, spotlight, tracked label, B-roll.", None),
    (300.6, 309.8, 1.2, (1250, 560, 1.9), "06", "Change one thing.", "\"Lower only the headline a little.\"", None),
    (309.8, 335.2, 5, (380, 190, 1.55), "07", "Muse revises only that.", "A new version; every other field stays the same.", "5× · real run"),
    (340.1, 353.6, 1.8, None, "08", "Every version kept.", "Compare, restore, export 1080×1920.", None),
    ("paint.mp4", 9.6, 12.0, 1, (1250, 540, 1.7), "09", "Paint the B\u2011roll.", "Muse Image illustrates each B-roll card from Muse's own text.", None),
    ("paint.mp4", 12.0, 72.0, 10, (380, 190, 1.55), "09", "Paint the B\u2011roll.", "Muse Image illustrates each B-roll card from Muse's own text.", "Shortened · real run"),
    ("paintview.mp4", 2.4, 11.5, 1, (585, 420, 1.6), "09", "Paint the B\u2011roll.", "Muse Image illustrates each B-roll card from Muse's own text.", None),
]
MULTI = [
    (2.2, 6.0, 1.5, None, "01", "Drop in your clips.", "Four iPhone clips from one morning ride.", None),
    (6.0, 21.0, 4, (1270, 560, 1.6), "01", "Drop in your clips.", "Camera times and HDR detected on upload.", "4× · real run"),
    (21.0, 30.8, 1.5, (1250, 540, 1.7), "02", "Pick a style. Name it.", "Calm, Energetic or Clean. Energetic it is.", None),
    (30.8, 50.8, 10, None, "03", "Prepare every clip.", "HDR → SDR, upright, slow motion for a 0.8 s clip.", "Shortened · real run"),
    (100.0, 137.0, 10, None, "03", "Prepare every clip.", "HDR → SDR, upright, slow motion for a 0.8 s clip.", "Shortened · real run"),
    (137.0, 166.2, 4, (380, 190, 1.55), "04", "Muse watches all four clips.", "One request picks seven shots and writes the captions.", "4× · real run"),
    (166.2, 186.2, 10, None, "05", "HyperFrames renders on the beat.", "Cuts snap to the music; times come from the camera.", "Shortened · real run"),
    (242.5, 262.5, 10, None, "05", "HyperFrames renders on the beat.", "Cuts snap to the music; times come from the camera.", "Shortened · real run"),
    (267.4, 279.5, 1.3, (585, 330, 1.45), "06", "Seven shots. One reel.", "Captions describe only what is visible.", None),
    (279.5, 283.5, 1, (1250, 420, 1.7), "07", "Restyle in one click.", "Calm: same shots, no new Muse request.", None),
    (360.0, 375.4, 10, None, "07", "Restyle in one click.", "Calm: same shots, no new Muse request.", "Shortened · real run"),
    (380.3, 392.0, 1.8, None, "08", "Both styles kept.", "History holds every version.", None),
    ("carousel.mp4", 7.2, 12.4, 1, (1250, 600, 1.7), "09", "Turn it into a carousel.", "One click: Muse Image restyles frames from Muse's shots.", None),
    ("carousel.mp4", 12.4, 72.1, 10, (380, 190, 1.55), "09", "Turn it into a carousel.", "One click: Muse Image restyles frames from Muse's shots.", "Shortened · real run"),
    ("carousel.mp4", 91.9, 99.0, 1, (1250, 640, 1.8), "10", "Six slides, ready to post.", "ReelOS typesets the text; download the ZIP for Instagram.", None),
]


def zoom_xy(z):
    if not z:
        return 0.0, 0.0, 1.0
    px, py, f = z
    tx = FRAME_W / 2 - px * SCALE0 * f
    ty = FRAME_H / 2 - py * SCALE0 * f
    tx = min(0.0, max(FRAME_W - FRAME_W * f, tx))
    ty = min(0.0, max(FRAME_H - FRAME_H * f, ty))
    return round(tx, 1), round(ty, 1), f


def recording_scene(cid: str, src: str, segments: list, chapter: str) -> tuple[str, float]:
    videos, captions, tweens, badges = [], [], [], []
    t, last_head = 0.0, None
    groups = []  # consecutive segments sharing a headline become one caption block
    for i, segment in enumerate(segments):
        # A segment may name its own recording first: ("paint.mp4", a, b, ...).
        seg_src, segment = (segment[0], segment[1:]) if isinstance(segment[0], str) else (src, segment)
        a, b, rate, zoom, step, head, detail, badge = segment
        d = round((b - a) / rate, 3)
        videos.append(
            f'<video id="{cid}-v{i}" class="clip rec" src="assets/{seg_src}" data-start="{t:.3f}" '
            f'data-duration="{d:.3f}" data-media-start="{a:.3f}" data-playback-rate="{rate}" '
            f'data-track-index="{i % 2}" muted playsinline></video>'
        )
        x, y, f = zoom_xy(zoom)
        tweens.append(
            f'tl.to("#{cid}-cam", {{x: {x}, y: {y}, scale: {f}, duration: 0.6, '
            f'ease: "power2.inOut"}}, {max(0.0, t - 0.0):.3f});'
        )
        if badge:
            badges.append((t, d, badge))
        if head != last_head:
            groups.append([t, d, step, head, detail])
            last_head = head
        else:
            groups[-1][1] += d
        t = round(t + d, 3)
    total = t
    for j, (start, dur, step, head, detail) in enumerate(groups):
        captions.append(
            f'<div id="{cid}-cap{j}" class="clip cap" data-start="{start:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="3">'
            f'<div class="step">{step}</div><h2>{head}</h2><p>{detail}</p></div>'
        )
        tweens.append(
            f'tl.fromTo("#{cid}-cap{j} h2", {{opacity: 0, x: -24, filter: "blur(6px)"}}, '
            f'{{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out"}}, '
            f"{start + 0.05:.3f});"
        )
        tweens.append(
            f'tl.fromTo("#{cid}-cap{j} p", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, '
            f"{start + 0.25:.3f});"
        )
    for k, (start, dur, text) in enumerate(badges):
        captions.append(
            f'<div id="{cid}-badge{k}" class="clip badge" data-start="{start:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="4">{text}</div>'
        )
    html = f"""<template><style>
#root{{position:absolute;inset:0;overflow:hidden;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.chapter{{position:absolute;left:80px;top:72px;font-family:"Space Mono",monospace;font-weight:700;font-size:26px;letter-spacing:.12em;color:{LIME}}}
.frame{{position:absolute;left:{FRAME_X}px;top:{FRAME_Y}px;width:{FRAME_W}px;height:{FRAME_H + 34}px;border-radius:18px;background:#1b1e21;box-shadow:0 30px 90px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08);overflow:hidden}}
.bar{{position:absolute;left:0;right:0;top:0;height:34px;display:flex;align-items:center;gap:8px;padding:0 16px;background:#141618}}
.bar i{{width:11px;height:11px;border-radius:50%;background:#3a3f44}}
.bar span{{margin-left:14px;font-family:"Space Mono",monospace;font-size:14px;color:{MUTED}}}
.screen{{position:absolute;left:0;top:34px;width:{FRAME_W}px;height:{FRAME_H}px;overflow:hidden;background:#111}}
#{cid}-cam{{position:absolute;left:0;top:0;width:{FRAME_W}px;height:{FRAME_H}px;transform-origin:0 0}}
.rec{{position:absolute;left:0;top:0;width:{FRAME_W}px;height:{FRAME_H}px;object-fit:fill}}
.cap{{position:absolute;left:80px;top:260px;width:390px;right:auto;bottom:auto;height:auto}}
.cap .step{{font-family:"Space Mono",monospace;font-weight:700;font-size:28px;color:{LIME}}}
.cap h2{{margin:14px 0 0;font-family:"Archivo Black",sans-serif;font-weight:400;font-size:52px;line-height:1.02;letter-spacing:-.02em}}
.cap p{{margin:22px 0 0;font-size:28px;line-height:1.35;color:#C9CEC9}}
.badge{{position:absolute;left:80px;top:860px;right:auto;bottom:auto;width:auto;height:auto;padding:12px 18px;border-radius:999px;background:rgba(234,255,129,.12);border:1px solid rgba(234,255,129,.5);color:{LIME};font-family:"Space Mono",monospace;font-weight:700;font-size:24px;letter-spacing:.06em;white-space:nowrap}}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
<div class="chapter">{chapter}</div>
<div class="frame"><div class="bar"><i></i><i></i><i></i><span>127.0.0.1:3000 · ReelOS (local)</span></div>
<div class="screen"><div id="{cid}-cam">
{chr(10).join(videos)}
</div></div></div>
{chr(10).join(captions)}
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.set("#{cid}-cam", {{x:0, y:0, scale:1}}, 0);
{chr(10).join(tweens)}
tl.set({{}}, {{}}, {total:.3f});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, total


PHONE = (
    '<div class="phone" style="left:{x}px"><div class="label">{label}</div>'
    '<video id="{id}" class="clip" src="assets/{src}" data-start="{start}" data-duration="{dur}" '
    'data-media-start="{ms}" data-track-index="{track}" muted playsinline></video>'
    '<div class="note">{note}</div></div>'
)
PHONE_CSS = f""".phone{{position:absolute;top:150px;width:370px}}
.phone video{{position:relative;display:block;width:370px;height:658px;object-fit:cover;border-radius:28px;background:#111;box-shadow:0 24px 70px rgba(0,0,0,.6),0 0 0 6px #1b1e21}}
.phone .label{{font-family:"Archivo Black",sans-serif;font-size:34px;margin-bottom:18px;color:{INK}}}
.phone .note{{margin-top:20px;font-size:24px;line-height:1.35;color:#C9CEC9}}"""


def showcase(cid, heading, sub, phones, dur, chapter):
    blocks = []
    for i, (label, src, note, ms) in enumerate(phones):
        x = 760 + i * 400 if len(phones) == 3 else 900 + i * 440
        blocks.append(
            PHONE.format(
                x=x, label=label, id=f"{cid}-p{i}", src=src, start=0, dur=dur, ms=ms,
                track=i, note=note,
            )
        )
    html = f"""<template><style>
#root{{position:absolute;inset:0;overflow:hidden;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.chapter{{position:absolute;left:80px;top:72px;font-family:"Space Mono",monospace;font-weight:700;font-size:26px;letter-spacing:.12em;color:{LIME}}}
.head{{position:absolute;left:80px;top:260px;width:600px}}
.head h2{{margin:0;font-family:"Archivo Black",sans-serif;font-weight:400;font-size:76px;line-height:1;letter-spacing:-.02em}}
.head p{{margin:26px 0 0;font-size:30px;line-height:1.35;color:#C9CEC9}}
{PHONE_CSS}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
<div class="chapter">{chapter}</div>
<div id="{cid}-head" class="clip head" data-start="0" data-duration="{dur}" data-track-index="5"><h2>{heading}</h2><p>{sub}</p></div>
{chr(10).join(blocks)}
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#{cid}-head h2", {{opacity:0, y:30, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:0.45, ease:"expo.out"}}, 0.1);
tl.fromTo("#root .phone", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:0.55, stagger:0.12, ease:"expo.out"}}, 0.2);
tl.set({{}}, {{}}, {dur});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, dur


def carousel_scene(dur=7.0):
    cid = "carousel"
    slides = [f"assets/slides/slide-{i:02d}.png" for i in range(1, 7)]
    imgs = "".join(f'<img src="{src}" alt="" />' for src in slides)
    dots = "".join(f'<i id="car-dot{i}"></i>' for i in range(len(slides)))
    step = (dur - 1.2) / (len(slides) - 1)
    swipes = "\n".join(
        f'tl.to("#car-strip", {{x: {-420 * i}, duration: 0.45, ease: "power3.inOut"}}, {0.9 + step * (i - 1):.2f});'
        f'tl.set("#car-dot{i}", {{backgroundColor: "{LIME}"}}, {1.1 + step * (i - 1):.2f});'
        f'tl.set("#car-dot{i - 1}", {{backgroundColor: "#3a3f44"}}, {1.1 + step * (i - 1):.2f});'
        for i in range(1, len(slides))
    )
    html = f"""<template><style>
#root{{position:absolute;inset:0;overflow:hidden;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.chapter{{position:absolute;left:80px;top:72px;font-family:"Space Mono",monospace;font-weight:700;font-size:26px;letter-spacing:.12em;color:{LIME}}}
.head{{position:absolute;left:80px;top:250px;width:640px;right:auto;bottom:auto;height:auto}}
.head h2{{margin:0;font-family:"Archivo Black",sans-serif;font-weight:400;font-size:76px;line-height:1;letter-spacing:-.02em}}
.head p{{margin:26px 0 0;font-size:30px;line-height:1.35;color:#C9CEC9}}
.head b{{color:{LIME};font-weight:700}}
.phone{{position:absolute;left:1000px;top:110px;width:460px;height:860px;border-radius:52px;background:#1b1e21;box-shadow:0 30px 90px rgba(0,0,0,.6),0 0 0 2px #2a2f33}}
.phone .bar{{position:absolute;left:20px;right:20px;top:34px;height:56px;display:flex;align-items:center;gap:12px;font-weight:700;font-size:22px}}
.phone .bar span{{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,{LIME},#5fb3a1)}}
.view{{position:absolute;left:20px;top:100px;width:420px;height:525px;overflow:hidden;border-radius:6px}}
#car-strip{{position:absolute;left:0;top:0;height:525px;display:flex}}
#car-strip img{{width:420px;height:525px;object-fit:cover;flex:none}}
.dots{{position:absolute;left:0;right:0;top:648px;display:flex;justify-content:center;gap:9px}}
.dots i{{width:9px;height:9px;border-radius:50%;background:#3a3f44}}
#car-dot0{{background:{LIME}}}
.cap{{position:absolute;left:20px;right:20px;top:690px;font-size:21px;line-height:1.4;color:#C9CEC9}}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
<div class="chapter">02 · MANY CLIPS · RESULT</div>
<div id="car-head" class="clip head" data-start="0" data-duration="{dur}" data-track-index="0"><h2>Swipe-ready<br>carousel.</h2><p><b>Muse Image</b> restyles real frames from Muse's shots. ReelOS typesets your title, captions and camera times.</p></div>
<div id="car-phone" class="clip phone" data-start="0" data-duration="{dur}" data-track-index="1">
<div class="bar"><span></span>bluesense</div>
<div class="view"><div id="car-strip">{imgs}</div></div>
<div class="dots">{dots}</div>
<div class="cap"><b>bluesense</b> Nandi Hills, 29 Aug · six slides from one morning ride</div>
</div>
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#car-head h2", {{opacity:0, y:30, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:0.45, ease:"expo.out"}}, 0.1);
tl.fromTo("#car-phone", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:0.55, ease:"expo.out"}}, 0.15);
tl.set("#car-strip", {{x:0}}, 0);
{swipes}
tl.set({{}}, {{}}, {dur});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, dur


def card(cid, num, line, dur=2.5):
    html = f"""<template><style>
#root{{position:absolute;inset:0;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.num{{position:absolute;left:160px;top:330px;font-family:"Archivo Black",sans-serif;font-size:240px;line-height:1;color:{LIME}}}
.line{{position:absolute;left:170px;top:610px;width:1500px;font-family:"Archivo Black",sans-serif;font-size:84px;line-height:1.05;letter-spacing:-.02em}}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
<div id="{cid}-num" class="clip num" data-start="0" data-duration="{dur}" data-track-index="0">{num}</div>
<div id="{cid}-line" class="clip line" data-start="0" data-duration="{dur}" data-track-index="1">{line}</div>
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#{cid}-num", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.5, ease:"expo.out"}}, 0.05);
tl.fromTo("#{cid}-line", {{opacity:0, y:30, filter:"blur(10px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:0.45, ease:"expo.out"}}, 0.25);
tl.to(["#{cid}-num", "#{cid}-line"], {{opacity:0, duration:0.2, ease:"power2.in"}}, {dur - 0.25});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, dur


def hook(dur=5.5):
    cid = "hook"
    phones = [
        ("single-draft.mp4", 0.0, 700),
        ("reel-energetic.mp4", 1.0, 1110),
        ("reel-calm.mp4", 6.0, 1520),
    ]
    vids = "\n".join(
        f'<video id="hook-v{i}" class="clip hp" src="assets/{s}" data-start="0" data-duration="{dur}" '
        f'data-media-start="{ms}" data-track-index="{i}" muted playsinline style="left:{x}px"></video>'
        for i, (s, ms, x) in enumerate(phones)
    )
    html = f"""<template><style>
#root{{position:absolute;inset:0;overflow:hidden;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.hp{{position:absolute;top:150px;width:370px;height:658px;object-fit:cover;border-radius:28px;box-shadow:0 24px 70px rgba(0,0,0,.6),0 0 0 6px #1b1e21}}
.words{{position:absolute;left:80px;top:300px;width:600px;font-family:"Archivo Black",sans-serif;font-size:104px;line-height:.98;letter-spacing:-.03em}}
.words .w{{display:inline-block}}
.words .accent{{color:{LIME}}}
.sub{{position:absolute;left:84px;top:720px;width:560px;font-size:30px;line-height:1.35;color:#C9CEC9}}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
{vids}
<div id="hook-words" class="clip words" data-start="0" data-duration="{dur}" data-track-index="4"><span class="w">Edit</span> <span class="w">your</span> <span class="w">video</span> <span class="w accent">by</span> <span class="w accent">talking.</span></div>
<div id="hook-sub" class="clip sub" data-start="0" data-duration="{dur}" data-track-index="5">Real outputs from ReelOS: one recording, and four phone clips.</div>
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#hook-words .w", {{opacity:0.25, y:24, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:0.3, stagger:0.11, ease:"expo.out"}}, 0);
tl.fromTo("#hook-sub", {{opacity:0}}, {{opacity:1, duration:0.4}}, 0.9);
tl.fromTo(".hp", {{opacity:0, y:80, rotation:3}}, {{opacity:1, y:0, rotation:0, duration:0.6, stagger:0.15, ease:"expo.out"}}, 0.2);
tl.to(["#hook-words", "#hook-sub", ".hp"], {{opacity:0, duration:0.25, ease:"power2.in"}}, {dur - 0.3});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, dur


def title(dur=2.4):
    cid = "title"
    html = f"""<template><style>
#root{{position:absolute;inset:0;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.name{{position:absolute;left:0;right:0;top:330px;text-align:center;font-family:"Archivo Black",sans-serif;font-size:220px;letter-spacing:-.04em}}
.name span{{color:{LIME}}}
.roles{{position:absolute;left:0;right:0;top:640px;text-align:center;font-family:"Space Mono",monospace;font-weight:700;font-size:30px;letter-spacing:.08em;color:#C9CEC9}}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
<div id="title-name" class="clip name" data-start="0" data-duration="{dur}" data-track-index="0">reel<span>os</span></div>
<div id="title-roles" class="clip roles" data-start="0" data-duration="{dur}" data-track-index="1">MUSE SPARK PLANS · SAM 3.1 TRACKS · MUSE IMAGE PAINTS</div>
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#title-name", {{opacity:0, scale:1.12, filter:"blur(14px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:0.5, ease:"expo.out"}}, 0.05);
tl.fromTo("#title-roles", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.4, ease:"expo.out"}}, 0.45);
tl.to(["#title-name", "#title-roles"], {{opacity:0, duration:0.22, ease:"power2.in"}}, {dur - 0.3});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, dur


def outro(dur=7.5):
    cid = "outro"
    rows = [
        ("Muse Spark", "edit plans, targeted revisions, multi-clip shot plans"),
        ("Muse Voice", "approximate transcript for topic-aware B-roll"),
        ("SAM 3.1", "finds and tracks the chosen speaker"),
        ("Muse Image", "painted B-roll and Instagram carousels from your frames"),
        ("HyperFrames", "B-roll cards and multi-clip reels, rendered in Docker"),
    ]
    items = "".join(f"<div class='row'><b>{a}</b><span>{b}</span></div>" for a, b in rows)
    html = f"""<template><style>
#root{{position:absolute;inset:0;background:{BG};font-family:Inter,sans-serif;color:{INK}}}
.head{{position:absolute;left:80px;top:150px;font-family:"Archivo Black",sans-serif;font-size:88px;line-height:1;letter-spacing:-.02em}}
.head span{{color:{LIME}}}
.rows{{position:absolute;left:84px;top:330px;width:1500px}}
.row{{display:flex;gap:28px;align-items:baseline;padding:20px 0;border-bottom:1px solid #2a2f33}}
.row b{{width:300px;font-family:"Space Mono",monospace;font-size:32px;color:{LIME}}}
.row span{{font-size:34px;color:#DADFD9}}
.repo{{position:absolute;left:84px;top:860px;font-family:"Space Mono",monospace;font-weight:700;font-size:34px;color:{INK}}}
.repo small{{display:block;margin-top:12px;font-family:Inter,sans-serif;font-weight:400;font-size:26px;color:{MUTED}}}
</style><div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
<div id="outro-head" class="clip head" data-start="0" data-duration="{dur}" data-track-index="0">Meta models <span>inside.</span></div>
<div id="outro-rows" class="clip rows" data-start="0" data-duration="{dur}" data-track-index="1">{items}</div>
<div id="outro-repo" class="clip repo" data-start="0" data-duration="{dur}" data-track-index="2">github.com/Thirumurugan-12/reelos<small>Runs locally with Docker Compose · every clip above is a real run</small></div>
</div><script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#outro-head", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:0.45, ease:"expo.out"}}, 0.05);
tl.fromTo("#outro-rows .row", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, stagger:0.15, ease:"expo.out"}}, 0.4);
tl.fromTo("#outro-repo", {{opacity:0}}, {{opacity:1, duration:0.4}}, 1.4);
tl.set({{}}, {{}}, {dur});
window.__timelines["{cid}"] = tl;
</script></template>
"""
    (COMP / f"{cid}.html").write_text(html)
    return cid, dur


scenes = [
    hook(),
    title(),
    card("ch1", "01", "One video, directed in plain language."),
    recording_scene("single", "single.mp4", SINGLE, "01 · ONE VIDEO · REAL RUN"),
    showcase(
        "single-result", "Same voice.<br>New edit.", "Original, Muse's first edit, and the one-line revision.",
        [("Original", "single-source.mp4", "Your recording", 1.0),
         ("First edit", "single-draft.mp4", "Headline, spotlight, B-roll", 1.0),
         ("Revised", "single-revised.mp4", "\"Lower only the headline\"", 1.0)],
        5.5, "01 · ONE VIDEO · RESULT",
    ),
    card("ch2", "02", "Many clips. One reel."),
    recording_scene("multi", "multi.mp4", MULTI, "02 · MANY CLIPS · REAL RUN"),
    showcase(
        "multi-result", "Two styles.<br>One plan.", "Energetic and Calm from the same Muse shot plan.",
        [("Energetic", "reel-energetic.mp4", "7 shots, whips, bold captions", 0.0),
         ("Calm", "reel-calm.mp4", "Mist dissolves, camera times", 0.0)],
        5.5, "02 · MANY CLIPS · RESULT",
    ),
    carousel_scene(6.5),
    outro(),
]

t, hosts = 0.0, []
for cid, dur in scenes:
    hosts.append(
        f'<div id="{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
        f'data-start="{t:.3f}" data-duration="{dur:.3f}" data-track-index="1" data-track-kind="graphics" '
        f'data-width="1920" data-height="1080"></div>'
    )
    t = round(t + dur, 3)
total = t
index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<script src="assets/gsap.min.js"></script>
<style>*{{box-sizing:border-box}}html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:{BG}}}.clip{{position:absolute;inset:0}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
<audio id="music" class="clip" src="assets/music.wav" data-start="0" data-duration="{total:.3f}" data-media-start="0" data-track-index="9" data-timeline-role="music" data-volume="0.4" data-fade-in="0.5" data-fade-out="3"></audio>
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines.main=gsap.timeline({{paused:true}});</script></body></html>
"""
(ROOT / "index.html").write_text(index)
print(json.dumps({"total": total, "scenes": scenes}))
