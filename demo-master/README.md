# ReelOS extended master

A local **193.4-second** (3:13.4) landscape master, extended from the PID's approximate three-minute target to include every catalog treatment at normal speed. The separate recording demo is 101.4 seconds. Portal delivery limits remain unverified.

The editable HTML uses real source/results, actual Canvas Pro captures, the actual SAM thumbnail, real parent/revised previews, original Remotion illustrations, the full 45-recipe/3-look gallery and the recorded reliability limitations. It is a composed walkthrough of saved results, not a live generation recording. Existing 75-second exports are preserved.

## Preview and render

With private local assets and Node 22+/FFmpeg available:

```sh
cd demo-master
npm run check
npx --yes hyperframes@0.8.220 snapshot --review
npx --yes hyperframes@0.8.220 preview --background --port 3020 --no-open
HYPERFRAMES_NO_TELEMETRY=1 npm run render -- --quality delivery --output ../data/reelos-hackathon-master-all-effects.mp4
```

Open `http://127.0.0.1:3020/#project/demo-master` while the managed preview runs. Keep editing there or through the HyperFrames desktop app's Edit with Framey action. No publishing command is authorized.

## Private assets

`prepare_assets.py` derives/copies previously verified artifacts without model calls. Gallery intervals, exact source identity and all labels are frozen in EFFECT_GALLERY.json. Rebuild the private gallery files from the verified full sampler with:

```sh
python3 ../demo-showcase/prepare_effect_gallery.py --target .
```

These asset commands intentionally leave the editable HTML unchanged. The clip manifest requires the exact verified sampler; do not silently substitute another person's footage. A fresh clone excludes all private source media, captures, score WAV, proxy cache and outputs. See ASSET_LEDGER.json and the repository's media-provenance docs to rebuild with authorized media.

The background uses the earlier original instrumental recording in finite overlapping segments with a final fade, rather than new synthesized music. Gallery tiles are muted to avoid four overlapping speech tracks; the full sequential portrait sampler retains source speech. The first scene demonstrates original voice. This soundtrack belongs to the presentation, not a ReelOS music-sync feature. Listening review remains human work.
