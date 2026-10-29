# Editing references applied to ReelOS

Updated 29 October 2026, following the user's observation that the initial effects were barely visible.

## References

- [Jeremy Longshore's video-editor agent](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/plugins/packages/creator-studio-pack/plugins/video-production/video-editor-ai/agents/video-editor.md): describes footage analysis, editing opportunities, post-production, and final checks. Its sample scripts and platform recommendations are reference material, not independently verified APIs or universal editing rules.
- [Vibha Ramprakash's Claude effects skill](https://github.com/Vibha-Ramprakash/claude-video-effects/blob/main/SKILL.md): provides concrete effect recipes, a structured plan, and representative-frame inspection before export. The inspected current guide lists 45 effects; our baseline is not a claim to implement the whole catalog.
- The user-pasted Notion guide contributes explicit styling, layer order, and timed visual recipes.

## Product correction

A valid MP4 with a valid timeline is not sufficient. The edit must visibly serve the intended treatment. The first title was placed where a close-up subject occluded most of it, so the result failed that practical expectation despite passing structural checks.

The response is a supported framed composition that creates headroom for typography, transforms SAM masks with the footage, and keeps labels readable through a contrasting background. A numerical headline-visibility check rejects near-total occlusion at a representative effect midpoint. Manual playback and additional sampled frames remain necessary; the metric alone does not prove readability or artistic quality.

## Workflow to retain

1. Inspect actual footage and identify a concrete edit opportunity.
2. Let Muse select supported treatments and produce the executable plan.
3. Check that the requested treatment is visible and masks align after any framing transform.
4. Render and inspect effect boundaries, midpoints, and moving-subject frames.
5. Compare original and edit, explain actual changes, and preserve versions.

Silence removal, filler-word deletion, exact-word captions, music, and multi-platform exports remain separate capabilities requiring their own implementation and timing evidence. We will not claim those features merely because the reference agent describes them. We are not switching to DaVinci Resolve or installing the referenced marketplace as part of this review.
