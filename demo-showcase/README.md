# ReelOS hackathon walkthrough

A local 101.4-second, 1920 × 1080 / 30 fps composed walkthrough of real ReelOS outputs and captured UI. This is not a live model-generation recording. Saved results are labelled as previously generated throughout; no product controls or model responses were invented.

The existing video-editing app still uses its shared Python/FFmpeg engine and original Remotion illustration templates. This separate presentation uses HyperFrames 0.8.220 to assemble the demonstration. The original deterministic score in `compose_audio.py` belongs to this showcase; it does not imply that ReelOS implements music synchronization.

## Result and preview

- Verified MP4 in this workspace: `../data/reelos-hackathon-demo-all-effects.mp4` (media stays outside Git).
- Editable local preview: `http://127.0.0.1:3017/#project/demo-showcase` while the managed preview is running.
- Review notes and deliberate limits: `REVIEW.md`.
- Shot/source evidence: `STORYBOARD.md`, `SPEC.md`, and `ASSET_LEDGER.json`.

## Re-render the frozen local project

With Node 22+, FFmpeg and the private local assets present:

```sh
cd demo-showcase
npm run check
npx hyperframes snapshot --review
npx hyperframes preview --background --port 3017 --no-open
HYPERFRAMES_NO_TELEMETRY=1 npm run render -- --quality delivery --output ../data/reelos-hackathon-demo-all-effects.mp4
```

Review the snapshots before rendering. CLI scripts pin 0.8.220. No paid Meta or media-generation calls are required to re-render the frozen composition. The preview binds to 127.0.0.1. Do not publish private media or the project automatically.

## Rebuild assets on this development machine

`prepare_assets.py` derives clips from the verified source/output files and downloads existing local-service previews and the real SAM thumbnail. It requires the known local project IDs and Compose data described by the evidence docs. It never calls a model. `compose_audio.py` creates an original instrumental bed locally using NumPy.

```sh
uv --directory backend run python /absolute/path/to/demo-showcase/prepare_assets.py
uv --directory backend run python /absolute/path/to/demo-showcase/compose_audio.py
```

The editable HTML files are the delivered source; they render directly without a source generator. Preserve human edits made in the preview. UI captures are real screenshots obtained separately with browser controls, not reconstructed dashboards. Required capture names are listed in the asset ledger. Save current workspace, assets, restored baseline and retained-revision screens before rebuilding their detail crops. Keep the actual value labels and states intact.

Raw footage, source audio, captures, rendered movies, history and media cache are ignored by Git. A fresh clone therefore does not include private media. To reproduce with other footage, create actual ReelOS edits first and replace the explicit source paths/IDs and evidence labels. Never substitute stock mockups or simulated model outputs.

## Presentation status

The local walkthrough can be reviewed now. Its 101.4-second length is a preparation choice; current official portal duration, hosting/access requirements and the final creator-feedback gate remain unverified. Nothing has been published or submitted externally. The two alternative directions in `STORYLINES.md` were considered but not produced.

## Canvas Pro capture refresh

The 1 November review artifact uses actual captures named `canvas-workspace.png`, `canvas-media.png`, `canvas-history-baseline.png` and `canvas-history-revision.png`. Capture dimensions/crop descriptions and hashes are in ASSET_LEDGER.json. Source is the restored rehearsal-3 project, not a mockup. Media/history are direct screenshot crops; text and states are not altered. Older captures and the October MP4 remain historical material. The asset preparation script preserves the new capture metadata when rebuilding derived media.

## Complete effects recording

The user requested every treatment on the supplied video. The recording now includes all 45 recipes and 3 extra looks, labelled in four normal-speed panels from 20.0–58.4 seconds. EFFECT_GALLERY.json freezes source identity and all 48 intervals. Run `python3 prepare_effect_gallery.py` to rebuild missing private tiles from the verified full sampler; it leaves HTML unchanged. Read [the recording chapter map and verification](../docs/EFFECT_DEMO.md). Prior 75-second MP4s remain historical artifacts. The source assets include an additional finite original-score tail for the 101.4-second recording.
