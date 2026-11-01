# ReelOS submission draft

Local preparation only. Nothing has been submitted or published. Required portal fields, video duration, access expectations and official deadline still need verification in the participant account. A 1 November browser check of the event details redirected to participant sign-in; the earlier user-pasted rules summary is background, not current official verification.

## Title

ReelOS — direct your video through conversation

## One sentence

ReelOS turns a talking-head recording and a visual reference into a rendered video with subject-aware graphics, then lets the creator revise specific details in plain language.

## Product description

Creators can describe the video they want without manually managing masks and layers. ReelOS accepts a source recording and an optional visual reference, uses Meta models to propose a timed editing plan, validates it, and renders an actual MP4.

SAM 3.1 tracks the selected person. Muse Spark maps creative instructions and supported reference styling into the editing contract. Muse Voice supplies an approximate transcript so original Remotion illustrations can follow the source topic. The renderer supports text behind the speaker, subject spotlight and contour, tracked labels, and approved illustration cutaways while preserving the original audio. A catalog adapts 45 MIT-licensed upstream effect recipes with three additional named looks; reused code and notices are disclosed. Illustrative cards and figures are template graphics, not factual screenshots or automatically sourced evidence.

A conversational revision changes an existing plan and creates a separate version. Creators can compare the original with the edit, recover prior versions, and download a 1080p export. The web workspace and CLI use the same service and rendering engine. Docker Compose runs the frontend and backend from one repository; provider credentials remain server-side.

Full video preserves complete recordings up to five minutes. An explicitly selected short-reel mode supports the initial hackathon workflow. Current limitations include approximate segmentation around occlusions, no word-aligned captions, no music synchronization, no arbitrary transitions, and a controlled single-user deployment rather than public multi-user hosting.

## Evidence to attach or demonstrate

- [Complete-effects recording and extended master](EFFECT_DEMO.md): 101.4 seconds and 193.4 seconds, composed from actual captures and real outputs. Both include all 45 recipes plus three named looks on the supplied footage. [Delivery index](DELIVERY.md); portal format remains unconfirmed.

- Complete main recording: 167.9 s / 1080 × 1920 H.264/AAC. [Verification](FULL_VIDEO_VERIFICATION.md).
- Three independent footage sets with real Meta execution and playable exports. [Results, licences and quality limitations](THREE_SET_EVALUATION.md).
- Nine targeted revision trials: all changed only the requested field in the complete plan; previous versions remained available.
- [Three fresh-project workflow rehearsals](REHEARSALS.md): planning, exact revision, restore and 1080p export passed; these used labelled 20-second excerpts, not the full recording.
- The fixed ten-attempt cohort produced seven decodable exports and four sampled visual passes; the 9/10 target was not met. Two separately registered framing-permitted drafts passed without manual layout repair. These are bounded results, not general reliability or creator-usefulness claims. [Original cohort](RELIABILITY_RESULTS.md), [separate follow-up](LAYOUT_FOLLOWUP_RESULTS.md).
- Setup: root README and Docker Compose. The current working service is local-only; no public hosted link has been prepared.
- Component provenance: [dependency and media inventory](DEPENDENCIES.md), retained package licence files, and the reference implementation documentation.

## Claims to avoid

Do not claim automatic reconstruction of arbitrary references, perfect masks, verified creator time savings, general multilingual accuracy, music editing, full nonlinear-editor functionality, or a public deployment. The measured full reference adaptation received editorial review. Stock subjects are technical evaluation footage, not endorsers or customers.

## Final owner checklist

- Confirm the current official rules, track, eligibility, original-work declaration and credit terms in the participant account.
- Confirm required video duration, file size, repository visibility, hosting/access and submission fields.
- Review the final recorded demo, description, provenance and media permissions for external publication.
- Verify every submitted link from another browser/account and check that credentials and private source files are absent.
- Human authorization is required before external project submission. No submission action is part of this draft.
