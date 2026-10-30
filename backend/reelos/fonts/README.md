# Frozen display fonts

Unmodified upstream fonts from https://github.com/vercel/geist-font, retrieved 2026-10-30.
Both accompanying upstream SIL Open Font License 1.1 notices are retained.

| File | Git blob | SHA-256 |
| --- | --- | --- |
| Geist-Black.ttf | d0098e7c23a30ca1f652a213154537989caeb27d | 558a58b06cd4cbc57117fae2f905648f0d7c88d89bbdb497d64d5317b1b19a36 |
| GeistPixel-Square.ttf | 8ad54b9edd494702a4c4b72a0630de6ac67afdd8 | c1fbf7316997c1749857708998958e8ca0343416b3f8d2c7156d634a9520e997 |

Renderer loads these files directly, without a platform font fallback. They are packaged
inside the backend wheel/image so preview and export use the same glyphs.
