# ReelOS NEAR demo — revised edit

Final sample: `data/near-demo/reelos-test-footage-broll-v2-1080p.mp4` (ignored).
20 seconds, 1080×1920/30fps, H.264 + original AAC voice. Fresh app render took
53.3007s. New version `1949fa52463a446ebf6f146e1b0add03`, job
`7419bee4a57b4f7d80ad236c3e092167`, project
`25ec54f2c76e4b87b9357927edf8d6a9`.
SHA-256: `bd76a5276856a7306cc4703d0f9c61d31d6ddb4f00ab878b87f70f83772cb0ca`.

The 18s initial edit was rejected visually and is retained only as history. The
revision uses a new directed timeline with cached subject tracking, two actual
moving stock cutaways, native presenter framing, restrained camera emphasis and
readable story headings. No new model calls; the local API budget stayed zero.

Updated walkthrough: 54s, 1920×1080/30fps. Editable sources in
`videos/reelos-near-demo/`; see BRIEF, SPEC and REVIEW for verification. Captures
show the actual revised editor and the deployed NEAR testnet pricing. No customer
funding, provider delivery signature or client approval is claimed. No artifact
or footage has been published. Previous source files and edit versions are intact.

## Requested quality revision

The first sample was not accepted visually. Replace it with a native full-frame
presenter edit, actual moving B-roll of eyewear, restrained camera moves and
short editorial text beats. Preserve the original voice and previous versions.
Supporting footage sources (checked 9 November 2026):

- Kaboompics, [eyeglasses on display](https://www.pexels.com/video/variety-of-eyeglasses-on-display-5241104/).
- Tima Miroshnichenko, [glasses on a desk](https://www.pexels.com/video/close-up-view-of-an-eyeglasses-above-the-table-6615433/).
- Both are covered by the [Pexels License](https://www.pexels.com/license/).

These object-only clips are illustrative cutaways, not the creator's own shop or
personal property. Original files and derivatives remain ignored private assets.

ReelOS now accepts a bounded `footage_insert` timeline effect containing a
project-scoped supporting-video asset ID and source offset. It decodes actual
moving frames and preserves audio from the main recording. Missing/reference/
image/out-of-range assets are rejected, decoder processes are closed, and a
failed render cannot replace a previous export. Integration tests verify moving
picture changes, presenter restoration and source 440 Hz audio rather than the
support clip's 880 Hz audio.

Final walkthrough: `data/near-demo/reelos-near-working-demo-v2.mp4`, 54s / 1920×1080/30fps.
SHA-256: `142d0570fe38e57713abbbb0788108c046505473f7ba6b981631a6e4c1948af7`.
