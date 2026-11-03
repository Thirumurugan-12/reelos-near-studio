"""Generate the HyperFrames comparison edit (same brief/beats/copy as ReelOS main v22)."""
import json, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
COMP = ROOT / "compositions"
COMP.mkdir(exist_ok=True)
DUR = 167.9

INK = "#0E1630"
ACCENT = "#1D4ED8"
HERO = "#4C8DFF"
PAPER = "#F4F4F2"

# --- same beats and copy as ReelOS v22 ------------------------------------
TITLES = [  # id, host start, duration, line1, line2, entrance, cutout window start
    ("title-1", 0.0, 7.5, "MY GLASSES", "STORY", "word", 0.0),
    ("title-2", 62.0, 7.0, "ON STAGE", "BLURRY CROWD", "letter", 61.5),
    ("title-3", 111.0, 7.0, "EYE CHECK", "CONVERSATION", "line", 110.5),
    ("title-4", 160.0, 7.85, "COMMENT", "LASER", "ink", 159.5),
]
LABELS = [
    ("label-open", 0.5, 7.0, "a personal eye-story", None),
    ("label-close", 160.0, 7.85, "comment LASER for details", "LASER"),
]
CARDS = [
    ("card-1", 12.0, "glasses", "Power Glasses", "Childhood wish to wear glasses"),
    ("card-2", 46.0, "stage", "Dance And Karate", "Classical lessons then stage dance"),
    ("card-3", 72.0, "crowd", "Blurred Faces On Stage", "Crowd visible, faces not clear"),
    ("card-4", 110.0, "chart", "Eye Health Check", "Vision power and eye health review"),
    ("card-5", 145.0, "laser", "Laser Awareness", "Learn about the vision campaign"),
]
# Punch-in states as hard cuts, never inside a title window or over the creator's own
# photo inserts burned into the source (39.5-45.0 s and 75.5-81.0 s).
PUNCH = [
    (18.0, 1.12, 20), (27.0, 1.0, 0), (33.0, 1.15, 30), (39.0, 1.0, 0), (47.0, 1.12, 20),
    (52.6, 1.0, 0), (60.3, 1.0, 0), (82.0, 1.12, 20), (88.0, 1.0, 0),
    (95.0, 1.14, 30), (100.7, 1.0, 0), (105.4, 1.12, 20),
    (126.0, 1.12, 20), (138.3, 1.0, 0), (142.8, 1.14, 30), (152.4, 1.0, 0), (156.3, 1.12, 20),
]
# "Room for titles": the camera pushes out onto a navy ground while a title is up.
PUSH = [(0.0, 7.5), (61.5, 69.0), (110.5, 118.0), (159.5, None)]
PUSH_SCALE, PUSH_Y = 0.78, 300


def fit(text, width, cap, factor=0.80):
    return int(min(cap, width / (len(text) * factor)))


def title_scene(cid, dur, l1, l2, entrance):
    s1 = fit(l1, 940, 150)
    s2 = fit(l2, 980, 230)
    words1 = "".join(f'<span class="w">{w}</span> ' for w in l1.split())
    if entrance == "letter":
        line2 = "".join(f'<span class="w">{c if c != " " else "&nbsp;"}</span>' for c in l2)
    else:
        line2 = "".join(f'<span class="w">{w}</span> ' for w in l2.split())
    out_at = dur - 0.35
    if entrance == "word":
        intro = f"""tl.fromTo(q(".w"), {{opacity: 0, filter: "blur(6px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.13, stagger: 0.067, ease: "power2.out"}}, 0.05);"""
    elif entrance == "letter":
        intro = f"""tl.fromTo(q(".l1 .w"), {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.18, stagger: 0.08, ease: "power3.out"}}, 0.05);
    tl.fromTo(q(".l2 .w"), {{opacity: 0.3, filter: "blur(3px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.12, stagger: 0.035, ease: "power2.out"}}, 0.25);
    tl.fromTo(q(".l2 .w"), {{opacity: 0}}, {{opacity: 0.3, duration: 0.01}}, 0.0);"""
    elif entrance == "line":
        intro = f"""tl.fromTo(q(".l1"), {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out"}}, 0.05);
    tl.fromTo(q(".l2"), {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out"}}, 0.2);"""
    else:  # ink: grey to ink per word
        intro = f"""tl.fromTo(q(".l1 .w"), {{opacity: 0}}, {{opacity: 1, duration: 0.08}}, 0.0);
    tl.fromTo(q(".l1 .w"), {{color: "#B9BDC6"}}, {{color: "{PAPER}", duration: 0.25, stagger: 0.09, ease: "power1.out"}}, 0.05);
    tl.fromTo(q(".l2"), {{opacity: 0, filter: "blur(10px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "expo.out"}}, 0.3);"""
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #{cid}-block {{ position: absolute; left: 0; right: 0; top: 176px; text-align: center; font-family: "Archivo Black", sans-serif; text-transform: uppercase; }}
    #{cid}-block .l1 {{ font-size: {s1}px; line-height: 0.95; letter-spacing: -0.02em; color: {PAPER}; }}
    #{cid}-block .l2 {{ font-size: {s2}px; line-height: 0.92; letter-spacing: -0.03em; color: {HERO}; margin-top: 4px; }}
    #{cid}-block .w {{ display: inline-block; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-block" class="clip" data-start="0" data-duration="{dur}" data-layout-allow-overlap>
      <div class="l1">{words1.strip()}</div>
      <div class="l2">{line2.strip()}</div>
    </div>
  </div>
  <script>
    const q = (s) => document.querySelectorAll("#{cid}-block " + s);
    const tl = gsap.timeline({{ paused: true }});
    {intro}
    tl.to("#{cid}-block", {{ opacity: 0, filter: "blur(8px)", duration: 0.22, ease: "power2.in" }}, {out_at:.2f});
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def label_scene(cid, dur, text, accent_word):
    parts = []
    for w in text.split():
        cls = "w acc" if w == accent_word else "w"
        parts.append(f'<span class="{cls}">{w}</span>')
    arrow = ""
    if accent_word:
        arrow = f'<svg id="{cid}-arrow" class="arrow" viewBox="0 0 24 24" width="40" height="40"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="{PAPER}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #{cid}-row {{ position: absolute; left: 0; right: 0; top: 1188px; display: flex; justify-content: center; }}
    #{cid}-pill {{ display: flex; align-items: center; gap: 18px;
      padding: 22px 34px; border-radius: 999px; background: rgba(14, 22, 48, 0.82); backdrop-filter: blur(18px);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 46px; color: {PAPER}; white-space: nowrap; letter-spacing: -0.01em; }}
    #{cid}-pill .dot {{ width: 16px; height: 16px; border-radius: 50%; background: {ACCENT}; box-shadow: 0 0 0 6px rgba(29, 78, 216, 0.28); }}
    #{cid}-pill .w {{ display: inline-block; margin-right: 0.26em; }}
    #{cid}-pill .w:last-of-type {{ margin-right: 0; }}
    #{cid}-pill .acc {{ background: {ACCENT}; padding: 0 0.22em; border-radius: 8px; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-wrap" class="clip" data-start="0" data-duration="{dur}">
      <div id="{cid}-row"><div id="{cid}-pill"><span class="dot"></span><span class="txt">{''.join(parts)}</span>{arrow}</div></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#{cid}-pill", {{ opacity: 0, y: 30, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, 0.6);
    tl.fromTo("#{cid}-pill .w", {{ color: "#8A93AB" }}, {{ color: "{PAPER}", duration: 0.2, stagger: 0.08, ease: "power1.out" }}, 0.8);
    {f'tl.fromTo("#{cid}-arrow", {{ x: -12, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, 1.3);' if accent_word else ''}
    tl.to("#{cid}-pill", {{ opacity: 0, y: 16, filter: "blur(6px)", duration: 0.25, ease: "power2.in" }}, {dur - 0.4:.2f});
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


ICONS = {
    "glasses": """<g fill="none" stroke="#F4F4F2" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
        <rect class="draw" x="18" y="92" width="92" height="70" rx="22"/>
        <rect class="draw" x="130" y="92" width="92" height="70" rx="22"/>
        <path class="draw" d="M110 112 q10 -12 20 0"/>
        <path class="draw" d="M18 104 L6 88"/><path class="draw" d="M222 104 L234 88"/>
      </g>
      <g class="pop"><path d="M38 106 l22 -10" stroke="#93B4FF" stroke-width="7" stroke-linecap="round"/><path d="M150 106 l22 -10" stroke="#93B4FF" stroke-width="7" stroke-linecap="round"/></g>""",
    "stage": """<g class="pop" opacity="0.9"><path d="M120 18 L52 210 L188 210 Z" fill="url(#beam)"/></g>
      <g fill="none" stroke="#F4F4F2" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
        <path class="draw" d="M20 214 H220"/>
        <circle class="draw" cx="120" cy="92" r="16"/>
        <path class="draw" d="M120 108 V160 M120 160 L96 204 M120 160 L146 200 M120 124 L84 104 M120 124 L160 98"/>
      </g>""",
    "crowd": """<g class="blurme" fill="#C9D3EA">
        <circle cx="46" cy="120" r="24"/><circle cx="104" cy="112" r="26"/><circle cx="164" cy="120" r="24"/><circle cx="214" cy="126" r="18"/>
        <path d="M14 214 q32 -64 64 0 Z"/><path d="M68 214 q36 -72 72 0 Z"/><path d="M132 214 q32 -64 64 0 Z"/><path d="M190 214 q24 -50 48 0 Z"/>
      </g>
      <g fill="none" stroke="#F4F4F2" stroke-width="6" stroke-linecap="round"><path class="draw" d="M14 30 H226"/></g>""",
    "chart": """<g font-family="Archivo Black, sans-serif" fill="#F4F4F2" text-anchor="middle" data-layout-ignore>
        <text class="row" x="120" y="74" font-size="64">E</text>
        <text class="row" x="120" y="124" font-size="40">F P</text>
        <text class="row" x="120" y="162" font-size="28">T O Z</text>
        <text class="row" x="120" y="192" font-size="20">L P E D</text>
        <text class="row" x="120" y="214" font-size="14">P E C F D</text>
      </g>
      <g fill="none" stroke="#93B4FF" stroke-width="5"><rect class="draw" x="40" y="8" width="160" height="220" rx="14"/></g>""",
    "laser": """<g fill="none" stroke="#F4F4F2" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
        <path class="draw" d="M14 120 Q120 30 226 120 Q120 210 14 120 Z"/>
        <circle class="draw" cx="120" cy="120" r="34"/>
      </g>
      <circle class="pop" cx="120" cy="120" r="14" fill="#F4F4F2"/>
      <rect class="sweep" x="2" y="117" width="236" height="6" rx="3" fill="#FF3B5C"/>""",
}


def card_scene(cid, icon, title, body):
    dur = 3.0
    extra = ""
    pop_js = (f'tl.fromTo("#{cid}-card .pop", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.4)" }}, 0.9);' if 'class="pop"' in ICONS[icon] else "")
    if icon == "crowd":
        extra = f'tl.fromTo("#{cid} .blurme", {{ filter: "blur(0px)" }}, {{ filter: "blur(7px)", duration: 1.0, ease: "power2.inOut" }}, 1.0);'
    elif icon == "chart":
        extra = f'tl.fromTo("#{cid}-card .row", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, stagger: 0.12, ease: "power1.out" }}, 0.55);'
    elif icon == "laser":
        extra = f'tl.fromTo("#{cid}-card .sweep", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.6, ease: "power2.inOut" }}, 1.1);'
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #{cid}-card {{ position: absolute; left: 48px; top: 1010px; width: 984px; height: 300px; border-radius: 36px;
      background: rgba(15, 16, 22, 0.80); backdrop-filter: blur(22px); border: 1.5px solid rgba(255, 255, 255, 0.12);
      display: flex; align-items: center; gap: 34px; padding: 30px 40px 30px 30px; transform-origin: 50% 100%; }}
    #{cid}-card .art {{ width: 240px; height: 240px; flex: none; border-radius: 26px; background: linear-gradient(160deg, #1D4ED8 0%, #0E1630 100%); overflow: hidden; }}
    #{cid}-card .copy {{ display: flex; flex-direction: column; gap: 14px; min-width: 0; }}
    #{cid}-card .kicker {{ font-family: "Space Mono", monospace; font-size: 28px; letter-spacing: 0.12em; color: #93B4FF; text-transform: uppercase; }}
    #{cid}-card h2 {{ font-family: "Archivo Black", sans-serif; font-weight: 400; font-size: 58px; line-height: 1.0; letter-spacing: -0.02em; color: {PAPER}; }}
    #{cid}-card p {{ font-family: "Inter", sans-serif; font-weight: 400; font-size: 34px; line-height: 1.25; color: rgba(244, 244, 242, 0.78); }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}" class="clip" data-start="0" data-duration="{dur}">
      <div id="{cid}-card">
        <div class="art">
          <svg viewBox="0 0 240 240" width="240" height="240">
            <defs><linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF7C2" stop-opacity="0.9"/><stop offset="1" stop-color="#FFF7C2" stop-opacity="0.05"/></linearGradient></defs>
            {ICONS[icon]}
          </svg>
        </div>
        <div class="copy">
          <div class="kicker">B-roll</div>
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#{cid}-card", {{ opacity: 0, y: 60, scale: 0.94, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }}, 0);
    tl.fromTo("#{cid}-card .copy > *", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.16, stagger: 0.08, ease: "power2.out" }}, 0.2);
    document.querySelectorAll("#{cid}-card .draw").forEach((el) => {{
      const len = el.getTotalLength ? Math.ceil(el.getTotalLength()) : 600;
      tl.fromTo(el, {{ strokeDasharray: len, strokeDashoffset: len }}, {{ strokeDashoffset: 0, duration: 0.8, ease: "power2.out" }}, 0.35);
    }});
    {pop_js}
    {extra}
    tl.to("#{cid}-card", {{ opacity: 0, y: 30, filter: "blur(8px)", duration: 0.3, ease: "power3.in" }}, 2.62);
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


for cid, start, dur, l1, l2, ent, _ in TITLES:
    (COMP / f"{cid}.html").write_text(title_scene(cid, dur, l1, l2, ent))
for cid, start, dur, text, acc in LABELS:
    (COMP / f"{cid}.html").write_text(label_scene(cid, dur, text, acc))
for cid, start, icon, title, body in CARDS:
    (COMP / f"{cid}.html").write_text(card_scene(cid, icon, title, body))

# --- root -------------------------------------------------------------------
hosts = []
z = 10
for cid, start, dur, *_ in TITLES:
    hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{start}" data-duration="{dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:2"></div>')
mattes = []
for i, (cid, start, dur, *_rest) in enumerate(TITLES, 1):
    w0 = _rest[-1]
    mdur = round(start + dur - w0, 3)
    mattes.append(f'        <video id="matte-{i}" class="clip" src="assets/cut/t{i}-cutout.webm" data-start="{w0}" data-media-start="0" data-duration="{mdur}" data-track-index="3" muted playsinline data-layout-allow-occlusion></video>')
for cid, start, dur, *_ in LABELS:
    hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{start}" data-duration="{dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:4"></div>')
for cid, start, *_ in CARDS:
    hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{start}" data-duration="3" data-track-index="5" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:5"></div>')
sfx = []
for i, (cid, start, *_r) in enumerate(CARDS, 1):
    sfx.append(f'      <audio id="sfx-card-{i}" class="clip" src="assets/sfx/whoosh.mp3" data-start="{start}" data-duration="0.6" data-track-index="7" data-volume="0.35"></audio>')
for i, (cid, start, *_r) in enumerate(TITLES, 1):
    sfx.append(f'      <audio id="sfx-title-{i}" class="clip" src="assets/sfx/impact.mp3" data-start="{start + 0.05:.2f}" data-duration="2.1" data-track-index="8" data-volume="0.25"></audio>')

punch_js = "\n".join(
    f'      tl.set(cams, {{ scale: {s}, y: {y} }}, {t});' for t, s, y in PUNCH
)

push = []
def before(t):
    st = (1.0, 0)
    for pt, sc, y in PUNCH:
        if pt < t: st = (sc, y)
    return st
for a, b in PUSH:
    if a == 0:
        push.append(f'      tl.set(cams, {{ scale: {PUSH_SCALE}, y: {PUSH_Y} }}, 0); tl.set("#plate", {{ borderRadius: 44 }}, 0);')
    else:
        sc, y = before(a)
        push.append(f'      tl.fromTo(cams, {{ scale: {sc}, y: {y} }}, {{ scale: {PUSH_SCALE}, y: {PUSH_Y}, duration: 0.6, ease: "power2.inOut", immediateRender: false }}, {a}); tl.fromTo("#plate", {{ borderRadius: 0 }}, {{ borderRadius: 44, duration: 0.6, ease: "power2.inOut", immediateRender: false }}, {a});')
    if b is not None:
        push.append(f'      tl.fromTo(cams, {{ scale: {PUSH_SCALE}, y: {PUSH_Y} }}, {{ scale: 1, y: 0, duration: 0.6, ease: "power2.inOut", immediateRender: false }}, {b}); tl.fromTo("#plate", {{ borderRadius: 44 }}, {{ borderRadius: 0, duration: 0.6, ease: "power2.inOut", immediateRender: false }}, {b});')
push_js = "\n".join(push)

index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      #ground {{ position: absolute; inset: 0; z-index: 0; background: radial-gradient(120% 70% at 50% 18%, #1B2A5C 0%, #0E1630 55%, #070B18 100%); }}
      .cam {{ position: absolute; inset: 0; transform-origin: 540px 560px; }}
      #plate {{ overflow: hidden; }}
      .cam video {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #plate {{ z-index: 1; }}
      #matte {{ z-index: 3; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="ground"></div>
      <div id="plate" class="cam">
        <video id="src" class="clip" src="assets/source.mp4" data-start="0" data-media-start="0" data-duration="{DUR}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
      </div>
{chr(10).join(hosts[:len(TITLES)])}
      <div id="matte" class="cam">
{chr(10).join(mattes)}
      </div>
{chr(10).join(hosts[len(TITLES):])}
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const cams = ["#plate", "#matte"];
{punch_js}
{push_js}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index)
print("written", len(list(COMP.glob('*.html'))), "scenes")
