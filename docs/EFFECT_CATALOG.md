# ReelOS complete effect catalog

ReelOS implements 45 recipes plus three named looks adapted from [Vibha Ramprakash’s claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects), pinned to `99c9a3393ee14d39bea155a05c73dc069f02f16f` (MIT, copyright 2026 Vibha Ramprakash). The original drawing functions, fonts, notices and YuNet model licence are retained in `backend/reelos/vendor/`. Upstream MediaPipe, CLI, private-code hook and arbitrary file loading are excluded.

## Use

Open **Effects** in the workspace. Search a treatment, play its illustrated preview, set text, timing, look and advanced controls, then **Apply and preview**. This creates an immutable child version. Upload optional supporting images/videos under Assets; choose their IDs in card-based recipes. Only project-owned assets are resolved. Style-reference clips are never copied into the edited content.

The API exposes `GET /api/effects`, per-effect `/preview` and `/poster`, and `POST /api/projects/{project}/effects`. The CLI exposes `effects`, `apply`, and `upload --role supporting`; see `skills/reelos-effects/SKILL.md`. Muse receives the same recipe catalogue and validated timeline schema for planning and partial revisions.

There are at most 48 timeline placements and three concurrent catalog effects, sharing one SAM subject when overlapping. SAM provides the foreground mask; local YuNet locates a face within that person, with a mask-head fallback. Motion is time-based and still-frame seeks match sequential rendering. Existing legacy plans and exports remain supported.

## Inventory and evidence

Every row has an actual renderer, a 3-second illustrated MP4/WebP preview, automated rendering checks, and three native 1080-wide still checks on authorised footage with cached real SAM masks. Local evidence: `data/catalog-evaluation/native-stills/verification.json` and contact sheets 1–8. Automated checks also compare independent seeks to sequential frames. The 48-window demonstration preserves all 167.9 seconds of source speech; it is a catalogue sampler using illustrative copy and numbers, not a Muse-directed creative edit.

| # | ID | Treatment | Supporting cards |
|---|---|---|---|
| 1 | `noise` | reels pile up behind your head, one every quarter second | Optional |
| 2 | `lineup` | numbered tiles fan out in an arc above your head | — |
| 3 | `locked-on` | corner brackets snap onto your face and the camera follows you | — |
| 4 | `orbit` | your reels circle your head: in front at the bottom, behind you at the top | Optional |
| 5 | `lean-in` | a fast punch-in on one word | — |
| 6 | `backdrop-word` | a giant word drops in behind you | — |
| 7 | `spotlight` | kill the lights, keep you lit | — |
| 8 | `the-bill` | prints every instruction like a ticket, into the wall above your head | — |
| 9 | `moody` | a moody colour grade: darker, softer, teal shadows | — |
| 10 | `swipe` | a before and after slider that sweeps across you | — |
| 11 | `todo` | a checklist card beside your head that ticks off as you talk | — |
| 12 | `comment-box` | an Instagram comments sheet above your head types your word, posts it, gets a heart and your reply | — |
| 13 | `tap` | a Follow button pops up and flips to Following | — |
| 14 | `pause-point` | freeze the frame and point at something with a hand-drawn arrow | — |
| 15 | `uninstall` | a glitchy uninstall bar that breaks the frame apart | — |
| 16 | `reel-frame` | your video shrinks into an Instagram reel card | — |
| 17 | `shortcut-rain` | keyboard keys rain down behind you | — |
| 18 | `reject-stamp` | a big red stamp slams onto the screen | — |
| 19 | `countdown-flip` | a 3, 2, 1 flip clock above your head | — |
| 20 | `rabbit-hole` | the frame tunnels into itself, spinning | — |
| 21 | `cover-star` | you become a magazine cover, with the title behind your head | — |
| 22 | `scribble` | marker doodles draw themselves around you | — |
| 23 | `glass-widgets` | frosted glass phone widgets and mini artifacts float around your head, with an Edited with ReelOS pill | — |
| 24 | `red-collage` | black and white you, a giant red word behind, kinetic type stacked beside you | — |
| 25 | `split-headline` | a clean headline card slides down and pushes you into the bottom of the frame | — |
| 26 | `pastel-word` | a soft lavender backdrop, a giant word behind you and a profile card that gets followed | — |
| 27 | `check-pills` | grid-paper room, your reels pinned behind you and blue pills that get clicked | Optional |
| 28 | `timeline` | a dark red cinematic grade with an editing timeline, a REC timecode and a glowing playhead | Optional |
| 29 | `headline-box` | a punch-in with a clean two-line headline, the second line in a white box | — |
| 30 | `profile-wall` | your profile grid fills the wall behind you while a counter ticks up | Optional |
| 31 | `tier-list` | a tier list drops in front of you and ReelOS flies into S tier | — |
| 32 | `broll-split` | split screen: b-roll on top with a price-tag sticker, you on the bottom | Optional |
| 33 | `phone-fan` | your reels fan out like a hand of phones in front of you, under a two-line headline | Optional |
| 34 | `dot-reveal` | your shot builds itself out of glowing dots, then snaps into the full picture | — |
| 35 | `headline-wall` | a wall of your own reel headlines piles up behind your head, then your total views pop in front | — |
| 36 | `checklist` | a ReelOS task list builds under your chin: each step spins, then ticks green | — |
| 37 | `liquid-glass-graph` | a liquid glass card floats under your chin while a graph climbs and the number counts up | — |
| 38 | `carousel-spin` | your reels spin around you in a 3D carousel, then slow to a stop | Optional |
| 39 | `match-cut` | news pages cut on one word, locked in place behind your head | — |
| 40 | `apple-toggles` | an iPhone settings card under your chin flips its switches on, one line at a time | — |
| 41 | `led-sign` | the lights drop and a glowing LED sign types itself out behind you | — |
| 42 | `slow-push` | a slow cinematic push-in from the wide shot to your face, the room melting out of focus | — |
| 43 | `over-the-shoulder-zoom` | the camera pushes into one top corner, a liquid glass graph pops beside your head, then the other corner with a second graph | — |
| 44 | `messages` | iMessage notifications pop in one after another, creamy glass with a soft glow, stacking up above the bottom of the frame | — |
| 45 | `place-in-grid` | you shrink into the centre tile of your 3x3 profile grid on frosted glass, then 8 of your reels pop in around you, one per frame, view counts on every tile | Optional |

The three extra looks are `glitter-spotlight` (spotlight/sparkle), `editorial-cover` (cover-star/editorial), and `glass-bento` (liquid-glass-graph/bento). They are style variants, not three additional independent recipes. Both aliases and canonical names are accepted.

## Practical limits

- Supporting video assets currently supply poster cards, not synchronized moving B-roll. Without assets, card recipes sample nine stills from the source. Generated Remotion inserts remain available through the existing graphic-insert family.
- Text timing is intentional scene timing, not exact word-aligned captioning. Pause Point freezes the picture while original speech continues.
- Gallery and sampler figures are illustrative. Graphs require explicit creator-supplied values; no inferred engagement or invented statistics. Bento also requires donut, KPI and bars inputs.
- This is a reusable starter library. Composition still needs editorial judgment: close-up faces, long copy, extreme settings and overlapping treatments need preview review. A style reference does not promise an identical edit.
- Muse receives supporting asset names/IDs/kinds, not a visual analysis of every supporting image. Select an asset explicitly when its content matters.
- The service uses local reservation accounting; this is not Meta’s confirmed billing balance. No paid model calls are needed to apply a catalog effect to an already tracked version.

## Reproduce

From `backend/`, run `uv run pytest -q` and `uv run ruff check reelos tests scripts`. Generate previews with `uv run python scripts/render_catalog_previews.py --force`. `scripts/check_catalog_source.py` accepts authorised source/track paths and `--render --width 360` or `1080` for the complete sampler. These local scripts never make paid provider requests.

## Completed verification — 31 October 2026

- 160 backend tests passed; Ruff passed; frontend TypeScript check and production Compose builds passed.
- All 48 public preview videos fully decoded (3 seconds each); 49 aliases validated.
- All 48 treatments inspected at three times at native 1080-wide resolution on real footage. The full 1080×1920 export also fully decoded: 5,037 frames, 167.9 seconds, H.264/AAC. Original speech is AAC re-encoded; decoded mono audio correlation with the source is 0.99885, not byte-identical passthrough.
- Live browser: search, sparkle look preview and apply, two-image upload, supporting-card selection and Orbit apply completed. Immutable versions v3/v4 in the demonstration project retain these checks.
- Mobile 390×844: document dimensions equal viewport for preview and Effects; task panels scroll internally. Desktop: preview aligned above the bounded long timeline and direction panels.
- The separate app project **Complete effects catalog · demonstration**, project `d2ce7b1de35f4b748fc4f7f85de701c6`, v1, contains the full sampler and 1080p download. Main source project v22 remains selected and unchanged. Example statistics/copy are illustrative.
- No paid provider calls were used for this implementation/evaluation. Muse catalogue plumbing is covered by the schema and a fixture-backed plan/revision integration test; this verification does not claim a fresh paid Muse creative plan was generated.
