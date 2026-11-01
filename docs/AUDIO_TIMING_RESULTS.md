# Source/output audio alignment — 1 November 2026

Beginning, middle and end audio windows in the current main v22 export, the complete catalog sampler and the fresh framing-permitted main draft all match the source with **0.000 ms measured lag** at 24 kHz (one sample is approximately 0.0417 ms). All nine checks exceed 0.998 correlation. The historical full-length export also passes its three windows. This is evidence of preserved decoded audio timing/content at the designated checks, not human listening or visual lip-sync review.

## Method and calibration

`backend/scripts/check_audio_timing.py` is a read-only, local checker. It decodes source and output audio to mono float PCM with FFmpeg, then calculates normalized cross-correlation over equal five-second windows, searching ±500 ms around the expected source/output mapping. Positive lag means the exported audio is later. Each check requires absolute lag ≤100 ms, absolute correlation ≥0.9, and a peak away from the search boundary. It reports the signed correlation, exact window positions, file hashes and stream start timestamps.

Both files must contain audio and video with matching stream start timestamps; all measured files start both streams at zero. A nonzero source trim is supplied with `--source-in`. Silence, non-finite data and out-of-bounds windows are inconclusive errors, not passing alignment. The final short-output window starts at 14.4 seconds so its full ±500 ms search remains inside the actual decoded AAC range; the nominal 20-second container alone does not establish valid PCM coverage.

Six regression cases calibrate −125 ms, 0 ms and +80 ms shifts with a one-second source trim, reject silence/out-of-bounds windows, and verify unrelated audio has low correlation. Known shifts are recovered within one 8 kHz calibration sample. The full backend suite passes **177 tests**; Ruff passes. Tests and measurements make no model requests.

## Actual results

Every row is a five-second window. Times are output seconds; all measured plans use source_in=0.

| Export | Window starts | Measured lag, each | Correlation, in window order |
|---|---|---|---|
| Current main v22, 167.9 s | 0.5 / 81 / 162 | 0.000 ms | 0.998445 / 0.998940 / 0.999023 |
| Complete catalog sampler, 167.9 s | 0.5 / 81 / 162 | 0.000 ms | 0.998594 / 0.998905 / 0.998996 |
| Fresh framed main draft, 20 s | 0.5 / 7.5 / 14.4 | 0.000 ms | 0.999190 / 0.999703 / 0.998318 |
| Historical full-length export, 167.9 s | 0.5 / 81 / 162 | 0.000 ms | 0.998445 / 0.998940 / 0.999023 |

The current v22 file was copied read-only from its actual Compose version directory and matched its server-side SHA-256:

```text
main v22:   daeb07559492114f86ccba9c439a062c2eceda39f93803410e53a32a294a1146
catalog:    6a8f4eb69e9caeb9a0ecbb589504794c901f764d0dbafe44a58d7ba665d9a99e
fresh main: 1f602b88d90783b063b5f9f4a40799002bbbce1102ec1e2a83dcbd67594dfa60
historical: a6ac51db9db9927ef54acd3893a45c6c256942e5884b24df891c220338a4f70b
```

The selected main v22 differs from the historical export as a file; identical audio correlations do not establish identical video. Private JSON reports, source/output hashes and the read-only current export copy remain under ignored `data/audio-timing/`.

## Reproduce

From the repository root, using existing private authorized media:

```sh
uv --directory backend run python scripts/check_audio_timing.py \
  ../testing_videos/VID_20261012_002734_182_bsl.mp4 \
  ../data/audio-timing/current-main-v22.mp4 --at .5 81 162
uv --directory backend run python scripts/check_audio_timing.py \
  ../data/demo-inputs/new-raw-20s.mp4 \
  ../data/layout-followup/run-01-export.mp4 --at .5 7.5 14.4
```

The utility does not fetch or render outputs. Supply the actual export and the corresponding source/trim. High correlation cannot establish frame continuity, the original recording's own lip sync, perceptual audio quality, loudness, or exact-word captions. Human listening/presentation review remains open. This adds measured timing evidence without changing the original failed reliability cohort, raising the local cap, or spending credits.
