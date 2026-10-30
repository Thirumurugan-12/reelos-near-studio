# Reproducible ReelOS demo

This is a rehearsal runbook, not a claim that the submission is complete. Two additional independent rights-cleared source recordings and broader evaluation remain outstanding. The official event details currently redirect to sign-in; confirm the portal's required video length, access format, deadline and declarations in the participant account before submission. Nothing has been submitted externally.

## Start and check

1. Configure `MODEL_API_KEY` server-side in the root `.env`. Keep the current local budget cap unless the builder changes it.
2. Run `docker compose up --build -d`, then `docker compose ps`.
3. Open [the local workspace](http://127.0.0.1:3000). CLI checks use the same instance:

```sh
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 health
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 usage
```

Use one source and optional style reference, each no longer than 60 seconds. The existing long source was preserved; the tested source is a 20-second derivative of its seconds 10–30. Sources, references, outputs, masks and transcripts stay outside Git in the Compose data volume.

## Main sequence

| Moment | Action | Evidence to show |
|---|---|---|
| Problem | Show raw footage with Original selected | An ordinary talking-head recording and its creator task |
| Intent | Add the style reference and describe the desired treatment | Red/black palette, contour, typography and illustration direction |
| Subject | Create a draft; select the highlighted speaker if SAM finds several tracks | Actual source thumbnails, including background photo detections |
| Plan | Show Storyboard/Edit overview | Supported timed operations and explanations |
| Result | Play Edit at normal speed | SAM foreground separation, text behind the real subject, original Remotion graphics and preserved speech |
| Control | Request one clear revision | A new immutable version and a visibly targeted change |
| Recovery | Select an earlier version and Restore | Earlier preview/export remains playable |
| Output | Export and download | Actual H.264/AAC 1080 × 1920 MP4 |

Suggested prompt for the provided source/reference: “Adapt this reference's red/black palette, glowing speaker outline, bold typography and illustration cutaways to my story. Use original graphics relevant to the source, preserve my speech, and make a short portrait edit.” Automatic interpretations still require review; the measured main example used explicit timing and styling instructions to direct the result.

Useful revision prompts are “Move only the headline lower to y=0.11,” “Soften only the spotlight to 0.35,” or “End only the opening headline at four seconds.” For an illustration, specify its operation ID and the title change. Explain that faster opening effects do not speed up the voice.

## Measured example and backup

In the existing local project `25ec54f2c76e4b87b9357927edf8d6a9`, final version `6f45a4247574489bbcac3d432681e93f` contains the 19.5-second reference-inspired result. The initial reference adaptation took 40.98 seconds for preview and 64.39 seconds for export on this development machine with cached masks/transcript. The final QA child exported in 62.64 seconds. These are individual runs, not guarantees or cold-run statistics. Keep any edited waiting period visibly labelled with its real elapsed time.

If a provider call fails during rehearsal, show the previously generated export and say it is previously generated. Inspect the same job before retrying; unknown paid outcomes retain their budget allowance. Never present a saved result as a fresh live generation.

The original source, reference, plan, preview, export and request ledger provide the local evidence trail. See [evaluation](EVALUATION.md) and [reference implementation](REFERENCE_STYLE_IMPLEMENTATION.md) for current limits, exact output metadata, dependency provenance and usage estimates. Do not claim arbitrary style reconstruction, word-aligned captions, music synchronization, creator time savings or three-recording reliability from this single tested recording.
