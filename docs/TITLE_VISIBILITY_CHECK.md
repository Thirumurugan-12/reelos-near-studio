# Moving-subject title validation — 1 November 2026

The renderer previously checked behind-person title visibility at only the effect midpoint. Saved camera plans from reliability runs 3, 8 and 10 exposed the gap: the foreground person left about 44% of the title visible at the midpoint but only 33% at the three-quarter point. The existing rejection threshold was 40%, so these visually failed layouts completed rendering.

The renderer now checks the source-specific, framed SAM mask at one-quarter, midpoint and three-quarters of each behind-person title interval. It uses the existing held-layout alpha calculation and 40% threshold. A failed check retains the saved plan, does not replace a previous output, and offers the existing clear-space/framing recovery message. It does not change copy, timings, layout or subject selection automatically.

This is a detection improvement, not proof of universal readability: three samples can miss brief occlusions, 40% visibility does not establish word recognition, and the alpha calculation includes title decoration. Animated entrances/exits and semantic legibility still require actual output review. No paid retry or automatic model request is introduced.

## Verification

- Two regression tests reproduced the old failure first: a subject covers the title at one-quarter or three-quarters while leaving the midpoint clear. Both now reject the render and preserve the previous output bytes.
- Measurements use the actual saved plans and SAM tracks at 360px preview and 1080px export widths. All four readable loft plans retain at least 99% visibility at the sampled positions. The two framing-recovery children and two fresh framing-permitted drafts retain 100% sampled visibility.
- Six actual-footage replays at 360px completed: all three historically occluded camera plans are now rejected with the visibility recovery message; the readable loft plan, camera framing-recovery child and fresh framed main draft all render and decode completely. These reuse saved model results and are not fresh model attempts.
- The full backend suite passes 169 tests; Ruff and Compose configuration validation pass.
- Private measurements and replay results are retained in `data/title-visibility-audit/`. Replays operate on saved assets into temporary output files, without creating versions or changing project pointers.

The historical ten-attempt cohort remains seven pipeline exports and four visual passes. Rejecting a previously accepted bad layout does not turn an original failed attempt into a success or meet the broader 9/10 target.
