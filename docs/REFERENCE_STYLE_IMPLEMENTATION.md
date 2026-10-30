# Reference-inspired editing and Remotion inserts

Implemented 30 October 2026 after the creator supplied a 54.08-second landscape example in `reference_video/` and explicitly requested Remotion-generated graphics.

## Actual visual target

The reference uses red/black contrast, glowing subject contours, large typography behind the speaker, and short illustration/interface cutaways. Representative frames at 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, and 53 seconds were inspected. The code adapts those visual ideas; it does not copy the example's Claude branding, screenshots, logos, or illustrations.

Reference proxies now preserve landscape framing rather than center-cropping it to portrait. Source proxies retain the portrait geometry required by SAM. Both input roles accept up to 60 seconds and 200 MB.

## Source understanding

Muse Spark reported that it could not access speech from the source video. A separate real `muse-voice-transcribe-1.0` call returned an approximate Tamil transcript about wanting glasses and later struggling to see the classroom board, even from the first bench. The opening ASR text contains uncertain mixed-script tokens. The transcript is used for topic selection only. Editorial English graphics are not presented as quotations, translations with guaranteed accuracy, or word-aligned captions.

The source transcript and SAM masks are cached per asset. Source speech remains beneath the graphic cutaways without retiming or replacement.

## Shared engine additions

- `subject_spotlight` supports original, monochrome, or black backgrounds, plus a configurable colored contour and glow. Defaults preserve prior plans' behavior.
- `graphic_insert` selects one of four original Remotion templates: glasses, classroom, document stack, or a generic illustrated editor window. The latter is an illustration rather than a screenshot of a real product.
- Templates receive validated text, color, duration and enum props. Muse cannot supply executable React, shell commands or external URLs.
- At most two non-overlapping inserts, each up to five seconds, are accepted. PNG sequences are cached by renderer/template version, props and duration and reused for preview and export.
- Graphic copy, template, accent and subject treatment fields can be revised through constrained patches. Other settings remain protected by whole-plan validation.
- Docker includes the graphics code, locked dependencies, a prebuilt composition bundle and Chrome Headless Shell. The API and CLI use the same rendering path.

## Measured output

The real Muse-directed version `be8abd1a832b482eb7e7692575552996` uses source seconds 0–19.5 from the existing 20-second derivative:

| Output time | Treatment |
|---|---|
| 0–19.5s | SAM foreground on black with red contour and glow |
| 0–2.7s | Red THE LOOK headline behind the speaker |
| 3–5.6s | Original animated Remotion glasses illustration |
| 7–10s | Red THEN, REALITY headline behind the speaker |
| 11–13.5s | Tracked MY STORY label |
| 16.5–19.3s | Original Remotion classroom board illustration with increasing blur |

Planning, graphics generation and preview completed in 40.98 seconds using existing masks and transcript. The 1080p export completed in 64.39 seconds with cached graphics. FFprobe confirmed 1080 × 1920, 30 fps, H.264/AAC, 19.5 seconds; the downloaded file was 13,590,059 bytes. Source/export audio correlation at matching sample positions was 0.999197. Representative edited frames at 1.5, 4.3, 8.5, 12, 15 and 18.2 seconds were visually inspected, and browser playback reached the end.

This is a guided reference adaptation on one recording. The model's timestamped reference observations are approximate and require visual review. It is not evidence of arbitrary reference reconstruction or robustness across three independent recordings.

## Dependencies and provenance

Remotion is pinned to 4.0.539. Composition and SVG illustration code is original ReelOS code. A transitive Zod override pins 4.6.7 to resolve the audit finding in its upstream dependency tree; the graphics dependency audit then reported zero vulnerabilities. Remotion's [licensing page](https://www.remotion.dev/docs/license/pricing) describes the free tier for individuals and companies of up to three people and separate terms for larger organizations. This is an independent single-user hackathon build.

Implementation references: [Remotion SSR](https://www.remotion.dev/docs/ssr-node), [frame rendering](https://www.remotion.dev/docs/renderer/render-frames), [Docker runtime](https://www.remotion.dev/docs/docker), [Meta speech transcription](https://dev.meta.ai/docs/speech-to-text), and [Meta pricing](https://dev.meta.ai/docs/pricing-rate-limits).

At the 19-attempt checkpoint, known-usage estimates totaled $0.262862, two requests remained unpriced, and $19 was conservatively reserved against the configured $50 cap. The earlier paired analysis disconnected without a response and was not silently retried. Reservations and known-usage estimates are separate from confirmed account billing.

## Finishing pass

The initial cut briefly returned to the speaker after the final illustration. Motion sampling also exposed a source-camera crop as the speaker leaned beyond its edge. Manual child versions preserved the model plan and corrected the classroom interval to 14.5–19.5 seconds, covering that source limitation and finishing on the illustration. Final version: `6f45a4247574489bbcac3d432681e93f` (preview 26.91 seconds with the new cached sequence). Earlier artifacts remain intact. The reference interpretation and illustration wording remain the original Muse plan; the timing correction is an editorial QA change, not a new inferred model result.
