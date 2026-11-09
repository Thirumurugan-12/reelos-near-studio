# Revised demo review

The first 18-second sample was rejected by the user. The replacement is a new
20-second native-frame edit with two moving eyewear B-roll cutaways, two readable
story headings, one restrained camera push and one short keyword label. Removed
the generic Speaker badge and blurred framing. Her original voice is continuous.
The B-roll is neutral illustrative stock, not the creator's own shop/property.

Measured: 20s, 1080×1920/30fps, H.264/AAC, full decode, 53.3007s worker time,
preview readyState 4, unchanged model usage. New project-scoped footage_insert
renders real moving frames. Integration tests verify main audio preservation,
return to the presenter, rejection of invalid assets and atomic export recovery.
254 backend tests, TypeScript and frontend production build pass.

Reviewed actual encoded sample frames and nine full walkthrough snapshots spanning
all six edit beats plus the three evidence scenes. Actual editor screenshot shows
the selected B-roll moment and the six-moment timeline. The preview loads at 54s.
HyperFrames checks have zero errors. One retained warning: six sequential caption
annotations share one track, keeping the six short beats together for readability.
No runtime, layout, contrast, audio or type-floor findings remain.

Source peaks reach 0 dBFS; the walkthrough voice uses 0.75 gain with a quiet local
music bed. Sound has been measured, not judged through human listening. Output
claims trace to actual render/RPC evidence. No new model inference, customer
funding, provider delivery or client approval is claimed. Testnet upgrade key
remains. Nothing has been published.

Weakest shot: full application screenshots are small on a phone. Large sidebars
carry the important statements; longer control-by-control zooms are outside this
short walkthrough. Human review of pacing and sound remains the next quality gate.

Delivery verification: 54s / 1620 frames at 1920×1080/30fps, H.264/AAC; full
FFmpeg decode passed. Encoded frames at 4.5s and 38s match the preview and show
actual B-roll plus unchanged NEAR pricing. Final audio peak remains below 0 dBFS.

Final capture correction: the narrow browser layout put payment below the fold,
so the old whole-page viewport image omitted it. Replaced that shot with a direct
631×784 browser crop of the actual live payment summary. The film now shows the
full 0.1/0.02/0.12 breakdown and pending wallet connection at a readable size.
