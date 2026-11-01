# Reproducible ReelOS demo

This is a rehearsal runbook, not a claim that the submission is complete. Three independent footage sets and three fresh-project workflow rehearsals are now documented; the local [75-second demo MP4](DEMO_ARTIFACT.md) is verified. Creator feedback, human listening review and current portal checks remain outstanding. The official event details currently redirect to sign-in; confirm the portal's required video length, access format, deadline and declarations in the participant account before submission. Nothing has been submitted externally.

## Start and check

1. Configure `MODEL_API_KEY` server-side in the root `.env`. Keep the current local budget cap unless the builder changes it.
2. Run `docker compose up --build -d`, then `docker compose ps`.
3. Open [the local workspace](http://127.0.0.1:3000). CLI checks use the same instance:

```sh
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 health
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 usage
```

Use one source up to five minutes and an optional style reference up to 60 seconds, each up to 200 MB. Select Full video to preserve the whole recording. Earlier prototype evidence used a 20-second derivative of source seconds 10–30; it does not demonstrate full-video completion. Sources, references, outputs, masks and transcripts stay outside Git in the Compose data volume.

## Main sequence

| Moment | Action | Evidence to show |
|---|---|---|
| Problem | Show raw footage with Original selected | An ordinary talking-head recording and its creator task |
| Intent | Add the style reference and describe the desired treatment | Red/black palette, contour, typography and illustration direction |
| Subject | Create a draft; select the highlighted speaker if SAM finds several tracks | Actual source thumbnails, including background photo detections |
| Plan | Open Edit, then expand Edit decisions; select a timeline moment for details | Supported timed operations and explanations |
| Result | Play Edit at normal speed | SAM foreground separation, text behind the real subject, original Remotion graphics and preserved speech |
| Control | Request one clear revision | A new immutable version and a visibly targeted change |
| Recovery | Open header Version history, select an earlier version, then Restore selected version | Earlier preview/export remains playable |
| Output | Export and download | Actual H.264/AAC 1080 × 1920 MP4 |

Suggested prompt for the provided source/reference: “Adapt this reference's red/black palette, glowing speaker outline, bold typography and illustration cutaways to my story. Use original graphics relevant to the source, preserve my speech, and edit the complete recording without trimming.” Automatic interpretations still require review; the measured main example used explicit timing and styling instructions to direct the result.

Useful revision prompts are “Move only the headline lower to y=0.11,” “Soften only the spotlight to 0.35,” or “End only the opening headline at four seconds.” For an illustration, specify its operation ID and the title change. Explain that faster opening effects do not speed up the voice.

## Measured example and backup

As of 1 November, the main project `25ec54f2c76e4b87b9357927edf8d6a9` selects `7d7cc51f54a3460fb7cc8b59597490fc` (v22), “Muse source-only · reviewed copy”: a 167.9-second edit with 12 operations, completed preview and export. This is the source-only treatment with reviewed copy; see [its provenance and limits](NO_REFERENCE_EDIT.md). The earlier reference-directed full version `673e9071da774bbcb3e00444dbb6d576` remains in history. Its measured preview/export times were 148.70 / 567.84 seconds with cached graphics; those timings do not describe v22. [Earlier full-recording evidence](FULL_VIDEO_VERIFICATION.md).

The earlier 19.5-second reference cut `6f45a4247574489bbcac3d432681e93f` remains a clearly labelled short backup. Do not show it as the complete source. [Three fresh 20-second excerpt rehearsals](REHEARSALS.md) passed planning, precise revision, restore and 1080p export; [three independent footage sets](THREE_SET_EVALUATION.md) passed functional checks with documented quality limits. These are measured individual runs, not guarantees.

If a provider call fails during rehearsal, show the previously generated export and say it is previously generated. Inspect the same job before retrying; unknown paid outcomes retain their budget allowance. Never present a saved result as a fresh live generation.

The original source, reference, plan, preview, export and request ledger provide the local evidence trail. See [evaluation](EVALUATION.md) and [reference implementation](REFERENCE_STYLE_IMPLEMENTATION.md) for current limits, exact output metadata, dependency provenance and usage estimates. Do not claim arbitrary style reconstruction, word-aligned captions, music synchronization, creator time savings or general reliability from these limited tests.

## Current interface and remaining preparation

The live app now uses [Canvas Pro](CANVAS_PRO.md): Edit, Looks and Media tools, a compact timeline, mobile control sheets and header history/export. The 30 October composed walkthrough contains real captures of the earlier interface; refresh those captures and re-render before treating it as a current-interface presentation. Do not relabel historical captures as current. [Completion audit](COMPLETION_AUDIT.md).
