# Complete-recording edit verification

30 October 2026. This supersedes the initial excerpt as the main user-supplied test. Earlier 18–19.5 second exports remain historical prototype results.

## Cause and behavior

The initial source asset was a 20-second derivative, and the timeline originally allowed only 30-second exports. That was insufficient for the requested full recording. Source uploads now accept up to five minutes / 200 MB, references up to 60 seconds / 200 MB. The web UI defaults to Full video; Short reel remains an explicit option. CLI callers use `draft --full-length`.

Full mode requires source_in=0 and source_out equal to the complete asset duration within one output frame. Both model-plan validation and manual-version validation enforce coverage. Effects can occur throughout the five-minute range. Full plans allow up to eight non-overlapping original Remotion inserts of at most five seconds each.

The real 127 MB upload also exposed Next's default 10 MB proxy buffer. The frontend now allows 210 MB and a 240-second proxy timeout; the complete source was uploaded through the frontend origin successfully.

## Actual source and plan

- Source: `testing_videos/VID_20261012_002734_182_bsl.mp4`, SHA-256 `f545a15ce3be8208c9dbf27aac93bfddc8d92af972ef337619461934d0f18dc5`.
- Original: 127,202,249 bytes, 1080 × 1920 HEVC/AAC, container duration 167.900417 seconds. Original remains untouched.
- Source asset: `6cf53766582d495ebfeeef1fe25107d4`, main project `25ec54f2c76e4b87b9357927edf8d6a9`.
- SAM: 1,678 analysis frames at 10 fps. Main speaker track 0 has a mask in every analysis frame. Its actual thumbnail was inspected before selection; background/photo tracks were excluded.
- Muse Voice transcribed the full recording. Approximate ASR supplies story meaning, not word-aligned subtitles.
- Muse full plan: `efc1808d1bee4a8093fd1831c1c7a677`; reviewed child: `673e9071da774bbcb3e00444dbb6d576`.
- Range: 0–167.9004 seconds. Continuous monochrome/dim background with red contour, five chapter headings, four tracked labels, and six three-second Remotion inserts at 12, 36, 68, 95, 125 and 148 seconds.
- Human/editorial review shortened four chapter titles and replaced a generic browser insert with a neutral illustrated consultation note. This is a reviewed model plan, not a claim that all final choices were automatic. No new medical efficacy claims were added.

The first full plan failed the insert-duration validator and was not rendered. A new request with explicit three-second insert limits succeeded. Source tracking and transcription were cached. Provider response JSON is now retained privately before plan validation to allow later repairs without repeating a paid request.

A manual-child bug initially omitted the parent's tracking reference. Same-source child versions now inherit tracking and observations; different-source children do not. A failing-then-passing regression test covers both cases.

The camera's video stream ends at 167.8 seconds, while audio/container lasts 167.900417. Full rendering holds the last camera frame for this short tail (three output frames here) to preserve speech. Padding is bounded to 0.25 seconds; unexpected longer decoder shortages still fail. Masks follow the same brief tail hold without filling internal missing frames.

## Verified preview

- Version `673e9071da774bbcb3e00444dbb6d576`, successful preview job `d3061bb5b9f24902b7880dc333501469`.
- Actual output: 167.900 seconds, 5,037 frames, 360 × 640, H.264/AAC, 24,419,763 bytes.
- Worker processing: 148.70 seconds with cached graphics; excludes queue waiting.
- Entire decoded audio correlation with source: 0.998843; final ten seconds: 0.999104. Re-encoding changes samples; these checks establish preserved timing/content rather than bit-identical audio.
- Fifteen representative composition frames inspected across opening, middle, all six illustrations, and ending. Embedded source photos remain; SAM contour quality is weaker around those photo occlusions.
- Browser playback reached currentTime=167.9 with ended=true and readyState 4. Original/Edit comparison loads the actual full original (167.900417 seconds) and full edited preview respectively.
- Mobile verification at 390 × 844: document and viewport both 390 × 844, no page overflow; full video readyState 4. Temporary viewport override reset afterward.
- Automated checks: 55 full-suite tests passed, including short audio-tail rendering, bounded final mask hold, same-source tracking inheritance, long-source upload and full-range validation. Ruff passed. Frontend production build and typecheck passed for the full-mode controls and proxy settings.

## Verified 1080p export

- Successful export job: `93c0a33653314e46b7806e6f9a957a8f`, same reviewed full version.
- Actual downloaded MP4: 135,543,396 bytes, 167.900 seconds, 5,037 frames, 1080 × 1920, 30 fps, H.264/AAC.
- Local ignored deliverable: `data/reelos-full-video-1080p.mp4`; preview: `data/reelos-full-video-preview.mp4`.
- Worker processing: 567.84 seconds (9 minutes 28 seconds), cached graphics; not a service latency guarantee.
- Entire export decoded with FFmpeg without errors. Whole-audio correlation with source: 0.998843; final ten seconds: 0.999104. Decoded audio duration difference is 0.000375 seconds.
- The actual 1080p frame at 135 seconds was inspected: heading and red subject treatment remain visible after two minutes.
- App reports Ready to play, selects the full version, shows 02:47, and exposes its Download MP4 link. Full preview playback already reached the ending.

The earlier 19.5-second export remains available as a prior version. Broader hackathon submission and user-feedback gates remain open; this verifies the complete-recording correction.
