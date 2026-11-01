# Local delivery index — 1 November 2026

These are prepared local artifacts, not a submitted entry. Current portal duration/file limits, track, team declarations and repository/hosting access still require the participant account. The official event details redirected to sign-in during the latest browser check. Choose or shorten a cut only after those requirements are known.

## Current media

All three files have H.264 video at 30 fps and AAC audio. Full-file decode and encoded-frame review are recorded in [the effects demonstration report](EFFECT_DEMO.md). Metadata and hashes were rechecked for this index.

| Purpose | Local artifact | Duration / geometry | Bytes |
|---|---|---|---:|
| Recording with every treatment | `data/reelos-hackathon-demo-all-effects.mp4` | 101.4 s / 1920×1080 / 3,042 frames | 83,346,888 |
| Extended product master | `data/reelos-hackathon-master-all-effects.mp4` | 193.4 s / 1920×1080 / 5,802 frames | 109,038,618 |
| Full-size sequential effect inspection | `data/catalog-evaluation/full-render/catalog-1080.mp4` | 167.9 s / 1080×1920 / 5,037 frames | 156,173,484 |

The gallery includes all 45 recipes and three extra looks on the identical authorized source. In the recording it runs from 20.0–58.4 seconds; in the master, 55.0–93.4 seconds. Four tiles play simultaneously at normal speed. The sequential portrait file shows the treatments individually and retains the source speech. Earlier 75-second demo exports remain historical alternatives.

SHA-256, in table order:

```text
5a1813b0393641ba18ab6760f34cdab8edab9b0cbc1ef22760c382245ac62f5d
356d71a9aeb43342f6176681d6db07c5c2d8d1f62236e4893b9637c0ce2a44fa
6a8f4eb69e9caeb9a0ecbb589504794c901f764d0dbafe44a58d7ba665d9a99e
```

## Reproduce locally

Run the product with the root README's Docker Compose instructions and a server-side key. The CLI and browser use the same service; don't run paid work against a separate copy of the budget ledger. The main project remains at v22 and the catalog at v1.

The editable presentation projects are `demo-showcase/` and `demo-master/`. They use saved, labelled results and actual interface captures. Their preview/check/render commands are in their READMEs. Private source footage, captures, music and derived clips are deliberately absent from Git: a fresh clone can run the product with authorized uploads but cannot recreate this exact private demonstration without its recorded dependencies.

With the existing private assets available, run from the repository root:

```sh
# Verify/rebuild all 48 recording-gallery clips from the frozen sampler.
python3 demo-showcase/prepare_effect_gallery.py
# Rebuild the master dependencies, including the full gallery and its ledger.
python3 demo-master/prepare_assets.py
```

Gallery verification requires both valid 432×768 / 96-frame media and the exact frozen clip SHA-256. A same-size replacement is rejected and preserved for inspection. A different encoder version may produce different bytes even from the correct source; do not silently update the manifest to make that pass. Review the new encoded footage before intentionally recording new hashes. These helpers make no model requests and leave editable composition HTML unchanged.

The local master rebuild retained all 70 ledger entries, including 48 gallery clips. Both projects' ledgers were compared against every actual asset: 75 recording assets and 70 master assets matched, with no changed media hashes. Two provenance regressions and the full 171-test backend suite pass. This verifies the local rebuild; it does not imply all private inputs are distributed with the repository.

## Submission evidence and remaining decisions

- [Description draft](SUBMISSION_DRAFT.md): problem, intended users, actual Meta contributions, reuse and limitations.
- [Three footage sets](THREE_SET_EVALUATION.md), [nine targeted revisions and rehearsals](REHEARSALS.md), [original reliability cohort](RELIABILITY_RESULTS.md), and [separate framing follow-up](LAYOUT_FOLLOWUP_RESULTS.md).
- [Setup and commands](../README.md), [architecture and canonical plan](REELOS_PID.md), [dependencies/media provenance](DEPENDENCIES.md), and retained upstream notices in `backend/reelos/vendor/`.
- [Audio alignment results and reproducible checker](AUDIO_TIMING_RESULTS.md): current main, catalog and fresh framed output pass designated beginning/middle/end source-audio checks; human listening/lip-sync review is separate.
- [Completion audit](COMPLETION_AUDIT.md): the 9/10 reliability target, creator usefulness/time savings, human listening review and portal acceptance are still unproven. The recorded cohort remains seven pipeline exports and four visual passes. No failed run was replaced.

The local cap remains fully reserved at $75; the known estimate is $1.87104170 plus seven unpriced calls. These are local accounting figures, not confirmed Meta billing or remaining credit balance. This preparation used no paid requests. External publication or submission needs the user's authorization after reviewing the concrete artifacts and actual portal requirements.
