# HyperFrames comparison edit — review

Purpose: edit the same source as ReelOS main v22 (`testing_videos/VID_20261012_002734_182_bsl.mp4`,
167.9 s, 1080×1920) in HyperFrames, so the two outputs can be compared side by side.

## Brief kept identical to ReelOS v22

- Full length 0–167.9 s, source audio kept, portrait 1080×1920 at 30 fps.
- Same four behind-the-speaker titles at the same times: MY GLASSES / STORY (0–7.5 s),
  ON STAGE / BLURRY CROWD (62–69 s), EYE CHECK / CONVERSATION (111–118 s), COMMENT / LASER (160 s–end).
- Same two labels: "a personal eye-story" (0.5–7.5 s), "comment LASER for details" (160 s–end).
- Same five B-roll cards and copy: Power Glasses 12 s, Dance And Karate (moved, see below),
  Blurred Faces On Stage 72 s, Eye Health Check 110 s, Laser Awareness 145 s.

## How each element was built here

- Text behind the speaker: local `npx hyperframes remove-background` (CoreML, free) mattes for the four
  title windows only (`assets/cut/t*-cutout.webm`). The order is plate, then title, then matte.
- Room for titles: the speaker's head fills the top of the frame, so a title behind the head was ~90% hidden on the first pass.
  In each title window the camera pushes out to 0.78 scale, 300 px down, onto a navy ground (0.6 s `power2.inOut`).
  This matches the problem ReelOS solved with its "Room for titles" framing (0.82 / 0.16).
- Punch-ins (1.12–1.15) are hard cuts placed on detected speech pauses. None land inside a title window.
- Cards: dark glass, with inline SVG illustrations that draw on (glasses, stage figure, crowd that goes out of focus,
  eye chart, eye with a laser sweep). No stock or generated imagery.
- Sound: source dialogue at unity. Bundled offline whoosh (card entries, 0.35) and soft bass hit (title landings, 0.25).
  No music, because ReelOS v22 has none and the piece is speech-led.

## Deliberate differences from ReelOS

- Card 2 moved from 40 s to 46 s. The source already contains the creator's own photo inserts (karate photo
  39.5–41 s, stage photos 42–45 s and 75.5–81 s). The ReelOS card at 40 s covers them; this edit keeps them clear.
  Punch-ins also avoid those windows so the photos are not cropped.
- No continuous subject spotlight or outline (ReelOS applies one for the full 167.9 s via SAM). A full-length local
  matte would take roughly 40 min of CPU time and wasn't needed for this comparison.
- No captions in either edit. The speech is Tamil/Telugu, and the local transcriber defaults to English translation.

## What was measured vs looked at

- `hyperframes check`: passes with 0 errors and 0 warnings after fixes (pill centring transform conflict, 26 px kicker under
  the 28 px floor, decorative eye-chart text marked `data-layout-ignore`, empty GSAP targets).
- Looked at: review sheets (beats, phone width), title windows, insert windows.
- Not heard: the mix was not listened to. Lip-sync was not reviewed by a person.

## Weakest shot / next steps

- Long second lines (BLURRY CROWD, CONVERSATION) fit at ~100 px and mostly sit above the head, so the
  behind-subject effect is subtle there. STORY and LASER read as intended (about 30–50% covered).
- The matte edges are the model's; flicker on hands was not inspected frame by frame.

Regenerate the compositions with `python3 build_compositions.py .` (it overwrites `index.html` and `compositions/`).
