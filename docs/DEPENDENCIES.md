# Dependency and media provenance

Inspected 30 October 2026 against installed package metadata and the deployed Docker image. This inventory covers major direct components; locked dependency trees and their bundled notices remain the authoritative inventory for transitive components.

ReelOS application, validation, compositing and original illustration code is authored in this repository. The Claude effects skill, supplied Notion guide and marketplace video-editor agent informed the workflow and supported catalog; their renderer/agent source was not copied. [Reference integration](EDITOR_REFERENCE_INTEGRATION.md).

| Component | Installed version | Declared licence / notice source | Use |
|---|---|---|---|
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
