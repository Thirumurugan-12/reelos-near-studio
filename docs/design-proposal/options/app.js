const concepts = [
  {
    id: "01",
    name: "Canvas Pro",
    tag: "The balanced editor",
    desc: "Persistent canvas, compact tracks and a contextual inspector.",
    flow: "Preview → select moment → adjust",
    theme: "canvas",
  },
  {
    id: "02",
    name: "Paper Edit",
    tag: "An editorial workspace",
    desc: "Story outline, warm paper surfaces and bold serif typography.",
    flow: "Outline → arrange beats → finish",
    theme: "paper",
  },
  {
    id: "03",
    name: "Director",
    tag: "Conversation leads",
    desc: "A focused editing conversation beside an uninterrupted preview.",
    flow: "Describe → preview → refine",
    theme: "director",
  },
  {
    id: "04",
    name: "Pocket Studio",
    tag: "Designed for one hand",
    desc: "A portrait stage with thumb-friendly tools and bottom-sheet controls.",
    flow: "Watch → tap a tool → apply",
    theme: "pocket",
  },
  {
    id: "05",
    name: "Story Grid",
    tag: "See the whole story",
    desc: "Visual scene cards replace a dense timeline as the main workspace.",
    flow: "Review scenes → select → style",
    theme: "story",
  },
  {
    id: "06",
    name: "Script Cut",
    tag: "Edit from the story",
    desc: "A readable script beside the video, with effects attached to passages.",
    flow: "Read → select passage → treat",
    theme: "script",
  },
  {
    id: "07",
    name: "Motion Lab",
    tag: "A visible creative pipeline",
    desc: "A spatial workflow for source, tracking, treatment and output.",
    flow: "Connect stages → inspect → preview",
    theme: "lab",
  },
  {
    id: "08",
    name: "Lookbook",
    tag: "Choose with your eyes",
    desc: "A large visual treatment library paired with a live-sized preview.",
    flow: "Browse → compare looks → apply",
    theme: "lookbook",
  },
  {
    id: "09",
    name: "Cinema Focus",
    tag: "Only the moment matters",
    desc: "A cinematic full-height stage with floating tools and a quiet prompt.",
    flow: "Watch → direct → watch again",
    theme: "cinema",
  },
  {
    id: "10",
    name: "Review Room",
    tag: "Decisions over controls",
    desc: "Before/after comparison, change notes and a clear keep-or-revise decision.",
    flow: "Compare → keep or revise → export",
    theme: "review",
  },
];
const root = document.querySelector("#app"),
  params = new URLSearchParams(location.search),
  chosen = concepts.find((x) => x.id === params.get("id"));
const photo = (cls = "", original = false) =>
  `<div class="portrait ${cls}"><img src="../${original ? "original" : "footage"}.jpg" alt="${original ? "Original footage" : "Existing ReelOS edited footage"}"><span class="frame-badge">9:16</span></div>`;
const player = () =>
  `<div class="player"><button aria-label="Back five seconds">↶</button><button aria-label="Play example" data-action="preview">▶</button><span class="mono">00:22 <span class="muted">/ 02:48</span></span><button aria-label="Expand preview">⛶</button></div>`;
const title = (sub = "A different perspective") =>
  `<div class="brand">reel<span>os</span></div><span class="project-name">${sub}</span>`;
const tools = (active = "Edit") =>
  `<nav class="tools" aria-label="Editor tools">${["Edit", "Looks", "Media"].map((x, i) => `<button ${x === active ? 'class="selected"' : ""} data-select="tool"><span aria-hidden="true">${["◫", "✧", "▧"][i]}</span>${x}</button>`).join("")}</nav>`;
const timeline = (compact = false) =>
  `<section class="timeline ${compact ? "compact" : ""}" aria-label="Example timeline"><div class="row"><strong>Your edit</strong><span class="muted">Full video · 02:48</span></div><div class="ruler mono"><span>00:00</span><span>00:42</span><span>01:24</span><span>02:06</span><span>02:48</span></div><div class="filmstrip">${"<i></i>".repeat(12)}</div><div class="effect-track">${["Opening", "B-roll cards", "Spotlight", "Closing"].map((x) => `<button data-select="moment">${x}</button>`).join("")}</div><input type="range" aria-label="Example playhead" min="0" max="168" value="22"></section>`;
const lookCards = (count = 3) =>
  `<div class="look-cards">${[
    "editorial-cover",
    "glass-bento",
    "glitter-spotlight",
    "orbit",
    "messages",
    "red-collage",
  ]
    .slice(0, count)
    .map(
      (x, i) =>
        `<button data-select="look" class="${i === 0 ? "selected" : ""}"><img src="http://127.0.0.1:3000/api/effects/${x}/poster" alt="${["Editorial", "Glass", "Spotlight", "Orbit", "Messages", "Collage"][i]} effect preview"><span>${["Editorial", "Glass", "Spotlight", "Orbit", "Messages", "Collage"][i]}</span></button>`,
    )
    .join("")}</div>`;
const brief = (button = "Generate preview") =>
  `<label for="direction">Your direction</label><textarea id="direction">Keep me visible. Add animated titles and B-roll cards that support the story.</textarea><div class="tags"><button data-action="brief">Stronger opening</button><button data-action="brief">Fewer effects</button></div><button class="primary full" data-action="brief">${button} ↗</button>`;
const scene = (n, label, t, cls = "") =>
  `<button class="scene ${cls}" data-select="scene"><span class="scene-image"><img src="../footage.jpg" alt="Example scene ${n}"><small>${t}</small><b>${String(n).padStart(2, "0")}</b></span><strong>${label}</strong><span class="muted">${["Title + gentle push", "B-roll card", "Subject spotlight", "Closing title"][(n - 1) % 4]}</span></button>`;
const layouts = {
  canvas: () =>
    `<header>${title()}<div class="header-actions"><button>Version 03 ⌄</button><button class="primary">Export ↗</button></div></header><div class="canvas-layout">${tools()}<main class="canvas-center"><div class="stage"><div class="stage-caption">PREVIEW <span>Original / <b>Edit</b></span></div>${photo()}${player()}</div>${timeline()}</main><aside><h1>Make it yours.</h1><p class="muted">A few good choices. Your own story.</p><h2>Overall feel</h2>${lookCards()}<div class="inspector-form">${brief()}</div></aside></div>`,
  paper: () =>
    `<header>${title("The story, before the spectacle.")}<div class="header-actions"><button>History</button><button class="primary">Publish edit ↗</button></div></header><main class="paper-layout"><section class="outline"><span class="eyebrow">THE OUTLINE</span><h1>A different<br> <em>perspective.</em></h1><p class="muted">One recording. Four moments worth keeping.</p><ol>${["The opening thought", "The story unfolds", "A turning point", "The takeaway"].map((s, i) => `<li><button data-select="beat" class="${i === 2 ? "selected" : ""}"><span>0${i + 1}</span>${s}<small>${["00:00", "00:34", "01:12", "02:16"][i]}</small></button></li>`).join("")}</ol><button class="border" data-action="brief">＋ Rewrite the direction</button></section><section class="paper-video"><div class="row"><span class="eyebrow">03 / A TURNING POINT</span><span class="muted">02:48 total</span></div>${photo()}${player()}</section><section class="paper-note"><span class="eyebrow">EDITOR’S DESK</span><h2>Let the story<br>do the work.</h2><p>Add a title at the turning point, then give the speaker room.</p><div class="paper-swatch">Aa<span>Editorial / warm ivory</span></div><button class="primary full" data-action="brief">Refine this moment ↗</button><span class="small muted">Example editorial plan</span></section></main>`,
  director: () =>
    `<header>${title()}<div class="header-actions"><span class="muted">Draft 03</span><button class="primary">Export</button></div></header><main class="director-layout"><section class="conversation"><div class="row"><h1>Your director.</h1><span class="pill">Example conversation</span></div><p class="muted">A clearer story starts with a conversation.</p><div class="messages"><article class="user-message">Make this feel like a polished creator reel. Keep the full recording.</article><article class="assistant-message"><span class="avatar">r.</span><div><strong>Here’s the direction.</strong><p>Bold opening. Supporting cards in the middle. A quieter ending.</p><div class="edit-summary"><span>↗ Animated titles</span><span>▧ B-roll cards</span><span>◉ Speaker stays visible</span></div></div></article><article class="user-message">Less full-screen graphics. More of me.</article><article class="assistant-message"><span class="avatar">r.</span><div><strong>Keep the speaker in the scene.</strong><p>Use smaller cards alongside the footage.</p><button class="border" data-action="preview">View example ↗</button></div></article></div><div class="composer"><label for="chat">What would you change?</label><div class="compose-line"><input id="chat" placeholder="Make the opening stronger…"><button class="primary" data-action="brief" aria-label="Send example direction">↑</button></div><span class="small muted">Design concept · messages are illustrative</span></div></section><section class="director-preview"><div class="stage-caption">THE CURRENT CUT <span>Compare ⌄</span></div>${photo()}${player()}${timeline(true)}</section></main>`,
  pocket: () =>
    `<header>${title("Pocket Studio")}<div class="header-actions"><button class="primary">Export ↑</button></div></header><main class="pocket-layout"><section class="pocket-guidance"><span class="eyebrow">MADE FOR THE MOMENT</span><h1>Watch.<br>Tap.<br><em>Make it yours.</em></h1><p class="muted">A portrait workspace with the tools within reach.</p><div class="task-card"><span>NOW EDITING</span><strong>Spotlight</strong><p>A little more focus on the speaker.</p><button data-action="brief" class="border">Adjust this effect →</button></div></section><section class="phone-stage"><div class="phone-top"><span>03 / YOUR EDIT</span><span>9:16</span></div>${photo()}${player()}<div class="mini-strip">${"<i></i>".repeat(7)}</div><nav class="pocket-dock">${["✎ Edit", "✧ Looks", "▧ Media", "↶ Undo"].map((x) => `<button data-action="sheet">${x}</button>`).join("")}</nav></section><section class="pocket-side"><h2>Pick the feeling.</h2>${lookCards()}<div class="preset-card"><span class="muted">Selected moment</span><h2>A subtle spotlight</h2><label for="pocket-intensity">Intensity</label><input id="pocket-intensity" type="range" value="65"><button class="primary full" data-action="brief">Apply to moment</button></div></section></main>`,
  story: () =>
    `<header>${title("The whole story")}<div class="header-actions"><button>Story order ⌄</button><button class="primary">Preview story ↗</button></div></header><main class="story-layout"><section class="story-board"><div class="board-heading"><div><span class="eyebrow">YOUR STORYBOARD</span><h1>Every moment has a job.</h1></div><span class="pill">6 example scenes</span></div><div class="scene-grid">${["Hook the viewer", "Set the scene", "Build the story", "The turning point", "Make it clear", "Leave a takeaway"].map((s, i) => scene(i + 1, s, ["00:00–00:18", "00:18–00:42", "00:42–01:12", "01:12–01:38", "01:38–02:16", "02:16–02:48"][i], i === 3 ? "selected" : "")).join("")}</div></section><aside class="scene-detail"><span class="eyebrow">SELECTED SCENE / 04</span><h2>The turning point</h2>${photo()}<p class="muted">A title to mark the change. The speaker stays in view.</p><button class="primary full" data-action="brief">Style this scene →</button><span class="small muted">Illustrative scene grouping</span></aside></main>`,
  script: () =>
    `<header>${title("Story-led editing")}<div class="header-actions"><button>Versions</button><button class="primary">Export</button></div></header><main class="script-layout"><section class="script-page"><div class="row"><h1>The story is the starting point.</h1><span class="pill">Example script</span></div><p class="muted">Select a passage. Give that moment a visual treatment.</p><div class="script-copy"><button class="script-paragraph" data-select="passage"><time>00:00</time><span>I wanted glasses when I was younger. I liked the way they looked.</span></button><button class="script-paragraph" data-select="passage"><time>00:34</time><span>Then I started noticing that things in the distance were difficult to see.</span></button><button class="script-paragraph selected" data-select="passage"><time>01:12</time><span>That was when I understood how much clear vision mattered.<small>✧ Emphasis title · 3 seconds</small></span></button><button class="script-paragraph" data-select="passage"><time>02:16</time><span>Now I want to share the story and help people ask the right questions.</span></button></div><p class="small muted">Illustrative English paraphrase, not a word-aligned transcript.</p><div class="inline-toolbar"><button data-action="brief">＋ Title</button><button data-action="brief">▧ B-roll</button><button data-action="brief">✧ Emphasis</button></div></section><section class="script-preview"><div class="stage-caption">SELECTED MOMENT <span>01:12–01:15</span></div>${photo()}${player()}<button class="primary" data-action="brief">Preview this passage →</button></section></main>`,
  lab: () =>
    `<header>${title("Motion Lab")}<div class="header-actions"><span class="pill">Advanced concept</span><button class="primary">Run preview ↗</button></div></header><main class="lab-layout"><div class="lab-heading"><h1>Your edit, connected.</h1><p class="muted">See the pipeline. Tune the treatment.</p></div><section class="node source-node"><span class="node-type">01 / INPUT</span><h2>Source footage</h2><img src="../original.jpg" alt="Source recording"><span class="small muted">02:48 · 1080 × 1920</span><button class="border" data-action="brief">Change source</button></section><section class="node mask-node"><span class="node-type">02 / SUBJECT</span><h2>Keep the speaker</h2><div class="mask-illustration">◎</div><p class="small muted">SAM subject mask</p><span class="pill">Person 01 selected</span></section><section class="node style-node"><span class="node-type">03 / TREATMENT</span><h2>Spotlight + title</h2><label for="node-title">Title</label><input id="node-title" value="A different perspective"><label for="node-strength">Strength</label><input id="node-strength" type="range" value="65"><button data-action="brief" class="primary">Inspect treatment →</button></section><section class="node output-node"><span class="node-type">04 / OUTPUT</span><h2>The current result</h2>${photo()}${player()}</section><div class="lab-footer"><span>Source → subject → treatment → result</span><span class="muted">Concept pipeline, not a running graph</span></div></main>`,
  lookbook: () =>
    `<header>${title("Find your visual language")}<div class="header-actions"><button>Saved looks ♡</button><button class="primary">Use this look ↗</button></div></header><main class="lookbook-layout"><section class="look-library"><div class="library-heading"><span class="eyebrow">THE LOOKBOOK</span><h1>Less guessing.<br> More seeing.</h1><p class="muted">Choose a treatment by what it does to your footage.</p><div class="filter-tabs">${["All looks", "Type", "Cards", "Light"].map((x, i) => `<button data-select="filter" class="${i === 0 ? "selected" : ""}">${x}</button>`).join("")}</div></div>${lookCards(6)}<p class="small muted">Preview examples from the existing ReelOS effect library.</p></section><section class="lookbook-preview"><div class="row"><span class="eyebrow">ON YOUR FOOTAGE</span><button class="border" data-action="preview">Original / Edit</button></div>${photo()}${player()}<div class="row selected-look"><div><span class="small muted">EXAMPLE TREATMENT</span><h2>Spotlight</h2></div><button class="primary" data-action="brief">Make it mine →</button></div></section></main>`,
  cinema: () =>
    `<header>${title("Focus mode")}<div class="header-actions"><button>History</button><button class="primary">Export ↗</button></div></header><main class="cinema-layout"><div class="cinema-label"><span class="eyebrow">THE CURRENT CUT</span><h1>A different<br>perspective.</h1><span class="muted">Full recording / 02:48</span></div><section class="cinema-frame">${photo()}<div class="cinema-play">${player()}</div></section><nav class="floating-tools" aria-label="Focus tools"><button data-action="sheet" aria-label="Edit title">Aa</button><button data-action="sheet" aria-label="Choose a look">✧</button><button data-action="sheet" aria-label="Add supporting media">▧</button><button data-action="sheet" aria-label="View history">↶</button></nav><div class="cinema-composer"><label for="focus-direction">DIRECT THE NEXT PASS</label><div class="compose-line"><input id="focus-direction" placeholder="A stronger opening. More of me. Less clutter."><button class="primary" data-action="brief" aria-label="Apply example direction">↑</button></div></div></main>`,
  review: () =>
    `<header>${title("Review Room")}<div class="header-actions"><button>Version 03 ⌄</button><button class="primary">Keep & export ↗</button></div></header><main class="review-layout"><section class="comparison"><div class="review-heading"><div><span class="eyebrow">SIDE BY SIDE</span><h1>Is this the cut?</h1></div><span class="pill">Same moment · 00:22</span></div><div class="compare-pair"><div><span class="compare-label">ORIGINAL</span>${photo("", true)}</div><div><span class="compare-label">EDIT / V03</span>${photo()}</div></div>${player()}<div class="review-decision"><button class="border" data-action="brief">One more change</button><button class="primary" data-action="preview">Keep this direction ✓</button></div></section><aside class="change-notes"><span class="eyebrow">WHAT CHANGED</span><h2>A clearer visual story.</h2><ol><li><b>01</b><div><strong>Designed titles</strong><p>Give the opening and closing a visual identity.</p></div></li><li><b>02</b><div><strong>Speaker stays visible</strong><p>Supporting cards sit alongside the footage.</p></div></li><li><b>03</b><div><strong>Original speech</strong><p>Keep the complete recording and its voice.</p></div></li></ol><div class="review-note"><label for="review-note">What would you change?</label><textarea id="review-note" placeholder="The opening is good. Soften the middle…"></textarea><button class="primary full" data-action="brief">Revise this version →</button></div><span class="small muted">Illustrative review notes</span></aside></main>`,
};
if (!chosen) {
  document.body.className = params.has("board") ? "gallery board" : "gallery";
  root.innerHTML = `<header class="gallery-header"><a class="brand" href="../">reel<span>os</span></a><span class="muted">DESIGN EXPLORATIONS / 10 DIRECTIONS</span><a class="button" href="?board=1">Compact comparison ↗</a></header><main class="gallery-main"><div class="gallery-intro"><div><span class="eyebrow">A BETTER WAY TO MAKE THE CUT.</span><h1>Ten ways ReelOS could feel.</h1><p>Different layouts. Different editing habits. The same story at the center.</p></div><span class="gallery-note">Interactive design concepts<br>Live editor stays unchanged.</span></div><div class="concept-grid">${concepts.map((c) => `<article class="concept-card"><a class="preview-link" href="?id=${c.id}" aria-label="Open ${c.name}"><div class="mini-frame"><iframe src="?id=${c.id}&embed=1" title="${c.name} layout preview" tabindex="-1" loading="lazy"></iframe></div><span class="open-preview">Explore ${c.id} ↗</span></a><div class="concept-caption"><span class="concept-number">${c.id}</span><div><h2><a href="?id=${c.id}">${c.name}</a></h2><p>${c.desc}</p><span class="small muted">${c.flow}</span></div></div></article>`).join("")}</div><footer class="gallery-footer">Original ReelOS design explorations · inspired by the previously reviewed design galleries · no generation or uploads in this prototype.</footer></main>`;
  const ro = new ResizeObserver((entries) =>
    entries.forEach(({ target, contentRect }) => {
      target.querySelector("iframe").style.transform =
        `scale(${contentRect.width / 1200})`;
    }),
  );
  document.querySelectorAll(".mini-frame").forEach((x) => ro.observe(x));
} else {
  document.title = `ReelOS · ${chosen.id} ${chosen.name}`;
  document.body.className = `design ${chosen.theme} ${params.has("embed") ? "embedded" : ""}`;
  root.innerHTML = `<div class="concept-bar"><a href="./">← All 10 designs</a><span>${chosen.id} / ${chosen.name} <span class="bar-tag">· ${chosen.tag}</span></span><button data-action="about">Concept only ⓘ</button></div><div class="editor">${layouts[chosen.theme]()}</div>`;
}
const dialog = document.querySelector("#brief-dialog"),
  toast = document.querySelector("#toast");
let toastTimer, priorFocus;
function showToast(text) {
  clearTimeout(toastTimer);
  toast.textContent = text;
  toast.classList.add("visible");
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3500);
}
document.addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b || b.closest("dialog")) return;
  if (b.dataset.select) {
    const group = b.dataset.select;
    document.querySelectorAll(`[data-select="${group}"]`).forEach((x) => {
      x.classList.toggle("selected", x === b);
      x.setAttribute("aria-pressed", String(x === b));
    });
    showToast("Selection updated in this design concept.");
    return;
  }
  if (b.dataset.action === "brief" || b.dataset.action === "sheet") {
    priorFocus = b;
    dialog.showModal();
    return;
  }
  showToast("Design exploration only — your live project is unchanged.");
});
document.querySelector(".close").onclick = () => dialog.close();
document.querySelector("#save-brief").onclick = () => {
  dialog.close();
  showToast("Example brief saved locally in this concept. No render started.");
};
dialog.onclose = () => priorFocus?.focus();
