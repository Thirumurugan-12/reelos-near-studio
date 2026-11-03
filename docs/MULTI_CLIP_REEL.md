# Multi-clip reel

Several short clips (a trip, an event, a day out, a product) become one portrait reel.
Added 3 November 2026 as "Trip reel"; renamed and given styles the same day.

## Flow

1. **Media → Multi-clip reel → Add clips** (multi-select MP4/MOV, each up to 2 minutes).
   Upload stores duration, HDR transfer and recording time, preferring Apple's local-time
   tag (`com.apple.quicktime.creationdate`) over UTC `creation_time`.
2. **Continue to direction → Multi-clip reel.** Clips in recording order with local time and
   length; clips under 1.5 s are marked slow-mo. Pick a **style**, choose whether to **show
   recording times and date**, add an optional title (≤24 characters) and a feeling.
3. **Make reel** queues one `montage` job:
   - *Preparing your clips*: each clip converted once and cached: HLG/PQ tone-mapped to SDR
     (`zscale` + `tonemap=hable`), upright 1080×1920, 30 fps, 1 s keyframes; clips under
     1.5 s become motion-interpolated 0.4× slow motion.
   - *Muse is watching your clips*: 360p proxies uploaded to Meta Files (free).
   - *Muse is planning your reel*: **one** Muse Spark response with every clip attached and a
     neutral prompt (any kind of footage) plus the style's pacing. It returns shots, visible-
     only captions, a title if none was given and a summary. No retries; a schema-invalid
     answer falls back to a labelled rule-based plan, provider errors fail the job.
   - ReelOS clamps shots into their clips, snaps them to the style's beat grid, caps the reel
     at 45 s. Times and dates on screen come only from clip metadata.
   - *HyperFrames is rendering your reel*: `graphics/montage/template.html` is filled with
     numbers and a style keyword only; every word travels as a HyperFrames variable bound
     with `textContent`.
4. **Change style** on a finished reel queues a `restyle` job: the same Muse shots and captions
   are re-timed for the new style's grid (`montage.refit`) and re-rendered as a child version.
   **No new Muse request.** History keeps every style.

## Styles

| | Calm | Energetic | Clean |
|---|---|---|---|
| Music (first-party, `reelos/music.py`) | 100 BPM bed, 0.6 s beats | 120 BPM drive, 0.5 s beats | 100 BPM bed, quieter |
| Shot length | 1.2–9.6 s | 1.0–4.0 s | 1.2–7.2 s |
| Transitions | mist flashes, whip into slow-mo | alternating vertical/horizontal whips with a white flash, punch-in | hard cuts |
| Type | serif title, glass time chips | bold uppercase, lime date tag, big centred captions | sans title top-left, lower-left captions |
| Ending | mist rises, serif title | black card | fade to black |
| Times by default | on | off | on |

## Measured (3 November 2026, Docker on the development Mac)

- Four real iPhone clips (43 s, three HLG HDR, one 0.78 s), Calm, Muse-planned: job 134 s
  after clip preparation; 4 shots, 23.4 s, 1080×1920, decodes cleanly. One local allowance
  reserved ($75 → $76 of the $80 cap the user approved).
- Restyled locally from the same shots: Energetic 13.5 s (render 54 s), Clean 23.4 s
  (77 s). The original Calm track port is sample-identical to `demo-showcase/compose_audio.py`.
- The energetic track was measured (regular rhythm, −17.5 LUFS, no clipping), not listened to.

## Limits

No manual trimming, reordering or caption editing yet; one track per style; no beat detection
on user music; captions are model output describing visible content only. Place names appear
only if the creator types them. Text revisions are not supported for reels; change the style
or make a new reel.
