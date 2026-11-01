# Three independent footage sets

Verified 30 October 2026 against the running Compose service, downloaded MP4s and real browser playback. This is a functional evaluation, not a claim of broad visual reliability or creator preference.

| Set | Rights/provenance | Verified output | Evidence and limits |
|---|---|---|---|
| Main speaker | User-supplied and authorized for processing/demo | Original short test 18 s; reference cut 19.5 s; complete recording 167.9 s, H.264/AAC 1080 × 1920 | Real Muse, Muse Voice and SAM; all three subject effects; reference-directed original Remotion inserts; preserved source speech. [Full-recording evidence](FULL_VIDEO_VERIFICATION.md) |
| Loft presenter | MART PRODUCTION, Pexels 7261921; [source and licence record](EVALUATION_ASSETS.md) | 18 s, 540 frames, 1080 × 1920 H.264, 4,226,486 bytes | Clear speaker, glasses and curly hair; visible headline, spotlight and tracked label. Silent source; does not independently test speech processing |
| Camera occlusion | Anna Shvets, Pexels 6617465; [source and licence record](EVALUATION_ASSETS.md) | 16 s, 480 frames, 1080 × 1920 H.264, 4,059,246 bytes | Difficult focus/occlusion case. SAM distinguishes the actual blurred person (0) from the person on the camera LCD (1). The selected actual person remains tracked, but its hard silhouette produces a conspicuous spotlight boundary. Functional pass; visual-quality limitation, not a polished demo recommendation. Silent source |

The downloaded stock exports match the running service byte-for-byte by SHA-256 and both decode completely with FFmpeg without errors. HTTP download returns 200. Browser playback reaches ended=true at 18 and 16 seconds, readyState 4. Ten actual export frames per stock set were inspected, including effect boundaries and late frames. Headline and label placement remain readable. The camera-case spotlight boundary is explicitly retained as a known limitation.

The local evidence ledger is `data/evaluation-media/verified-results.json`; screenshots and ten-frame contact sheets are in that ignored directory. These files and raw stock media are not included in Git.

## Targeted revisions: 9 of 9 exact plan matches

Each intent was sent to real Muse. Current durable parent/child plans were re-read and compared as complete objects, not inferred from summaries. Each child has its own playable preview; unrelated fields are unchanged.

| Set | Headline position | Spotlight intensity | Opening end | Worker processing seconds |
|---|---|---|---|---|
| Main speaker | 0.09 → 0.11 | 0.60 → 0.35 | 6 → 4 s | 8.00 / 8.24 / 8.85 |
| Loft | 0.09 → 0.11 | 0.55 → 0.30 | 6 → 4 s | 6.86 / 7.95 / 7.73 |
| Camera occlusion | 0.09 → 0.11 | 0.55 → 0.30 | 5 → 3 s | 7.08 / 6.75 / 7.10 |

Worker times exclude queue waiting. For the camera set, separate observed client dispatch-to-terminal times were 8.09 / 7.07 / 8.08 seconds, including polling delay. These are individual observations, not percentiles or service guarantees.

Projects and baseline versions:

- Loft: `4eedb7d83d46457780390b88b2a9e635`, baseline `439424f0ac624546906b727eae6a5eda`.
- Camera occlusion: `4f12f1da97144a8384fd7595902e6ccf`, baseline `f393ba0c2dcf4ce5bc2b8a05988d1e86`.
- Main original revision chain starts at `47d81f08e2584bd29ac0dd8d5486e713`; verified children `5ca75743c0554a25a2132394e254c5ca`, `95e9fde2dc514e82a00b4344fd35e76c`, `da87b07b7e9d4a39b5e50cdcca2c5556`.

Both stock projects have their baseline restored as the durable current version while retaining all three child versions. The main project retains all 17 versions and selects the newer full-length result, preserving the earlier browser-verified restore history.

## Remaining gates

Follow-up evidence now includes [three fresh-project rehearsals](REHEARSALS.md) and a [verified local demo MP4](DEMO_ARTIFACT.md). Creator task feedback, current official portal requirements and human presentation review remain open. Three playable inputs and nine precise revisions do not prove the PID's 9/10 end-to-end reliability target or its 2/3 creator usefulness target.

## Subsequent reliability batch

The separate [1 November fixed ten-attempt test](RELIABILITY_RESULTS.md) produced seven exports and four sampled visual passes. Two main-source attempts failed, and camera titles were obscured in three exports. The 9/10 target was not met; the earlier successes above must not be presented as overriding these failures.
