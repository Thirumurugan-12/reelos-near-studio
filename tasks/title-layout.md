# Title-layout recovery

1. Add a validated framing operation to the existing API and CLI. It creates an immutable child, inherits tracking/profile, preserves all non-framing plan fields, rejects out-of-project parents and active jobs, and queues the shared renderer. Verify with API/CLI regression tests before implementation.
2. Expose Room for titles (scale .82, offset .16) and Original framing (1, 0) in Edit controls. Use the same operation, disable while busy/current, retain normal error/history behavior. Verify type/build and actual desktop/mobile controls.
3. Apply the operation to the saved failed main version and the occluded camera version, render real preview/export with cached SAM, inspect the actual frames and decode outputs. Preserve the failed cohort score and existing main/demo current versions. Use no paid model calls.

Acceptance: title readable in reviewed recovery outputs, no mutation of parents/non-framing fields, API/CLI/web share rendering, and no claims of automatic layout adaptation or a changed reliability score.
