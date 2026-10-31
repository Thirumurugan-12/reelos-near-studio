# Dependency and media provenance

Updated 31 October 2026 against installed package metadata and the deployed Docker image. This inventory covers major direct components; locked dependency trees and their bundled notices remain the authoritative inventory for transitive components.

ReelOS application, validation, compositing and original illustration code is authored in this repository. The catalog reuses the 45 MIT-licensed Claude drawing recipes, fonts and YuNet model with retained attribution in `backend/reelos/vendor/`; the upstream tracker/CLI/private hook are excluded. The supplied Notion guide and marketplace video-editor agent informed the workflow. See [the catalog inventory](EFFECT_CATALOG.md). [Reference integration](EDITOR_REFERENCE_INTEGRATION.md).

| Component | Installed version | Declared licence / notice source | Use |
|---|---|---|---|
| Claude effects renderer | commit `99c9a33` | MIT, copyright 2026 Vibha Ramprakash; retained licence | All 45 recipes + 3 looks |
| OpenCV headless | 4.14.0.94 | Apache-2.0; package notices | Drawing, local face-anchor inference |
| YuNet | upstream `yunet.onnx` | MIT, copyright 2020 Shiqi Yu; retained licence | Face anchor inside SAM person |
| FastAPI | 0.162.0 | MIT; wheel `dist-info/licenses/LICENSE` | Backend API |
| Pydantic | 2.14.2 | MIT; wheel licence | Validated edit contracts |
| HTTPX | 0.28.1 | BSD-3-Clause; wheel `LICENSE.md` | Server-side API transport |
| NumPy | 2.5.4 | Composite BSD-3-Clause / 0BSD / MIT / Zlib / CC0 declaration; bundled notices | Frame processing |
| Pillow | 12.3.0 | MIT-CMU declaration plus bundled notices | Typography and compositing |
| `@meta-sam/parser` | 0.1.0 | SAM License, package `LICENSE`, updated 19 Nov 2025 | Official native mask decoding |
| `meta-sam-parser` | 0.1.0 | SAM License, wheel licence | Installed Python parser / reference compatibility |
| Next.js | 16.4.3 | MIT; package notice | Web workspace |
| React / React DOM | 19.2.4 | MIT; package notices | Interface and original Remotion components |
| Remotion renderer/bundler | 4.0.539 | Remotion licence; installed `LICENSE.md` | Original approved illustration templates |

The SAM parsers and Remotion have their own licence terms; they are not described as MIT dependencies. Original package licence files remain in the installed dependency trees. Remotion's installed licence permits qualifying individuals and small organizations and defines separate company terms; see [its official licensing page](https://www.remotion.dev/docs/license/pricing). The present deployment is an independent single-user hackathon build; do not assume another organization's eligibility.

Pillow's default font implementation identifies its embedded face as a limited-character version of Aileron Regular. The [font author's page](https://dotcolon.net/fonts/aileron/) describes Aileron as “No Rights Reserved.” Legacy render profiles may use system fonts supplied by the container; newer versions retain the recorded Pillow/Aileron profile.

FFmpeg, Python, Node and Debian runtime components are installed through the Dockerfiles. Their package notices remain in the corresponding installed packages and images. Consult actual package/build notices when distributing a binary image; no claim of an exhaustive redistribution audit is made here.

## Media

- Main recording and visual reference: supplied by the user for processing/demo. Originals remain outside Git. Generated results preserve source audio; source and reference assets are not silently published.
- Glasses, classroom, document and generic browser illustrations: original SVG/React artwork in `graphics/src/story-illustrations.tsx`; no copied reference screenshots, product logos, or downloaded stock illustrations.
- Independent stock recordings: [creators, original pages and Pexels licence record](EVALUATION_ASSETS.md). Neutral technical evaluation only; no implied endorsement.
- Design-reference captures under `docs/design-references/` are research material. They are not product UI assets or assets for automatic public redistribution.

Exact-word captions, music synchronization and arbitrary effects are not implemented merely because external references describe them. Model output is data for approved components, never downloaded executable effect code.

## Separate presentation project

The local showcase uses HyperFrames 0.8.220, GSAP 3.14.2 and Inter; its [specific provenance](../demo-showcase/THIRD_PARTY.md) and [review record](../demo-showcase/REVIEW.md) are separate from the production editing engine. Its original locally authored score is presentation material, not an implemented ReelOS music-sync feature.
