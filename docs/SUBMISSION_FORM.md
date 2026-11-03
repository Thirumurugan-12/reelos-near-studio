# Cerebral Valley submission fields (draft, not submitted)

Team: bluesense · Track: Indie Developer Track · Problem statement: Build for Your World

## Project Description

ReelOS is a creator video editor you direct in plain language. Upload a talking-head recording, say what the edit should feel like, and Muse Spark proposes a timed editing plan while SAM 3.1 tracks the person you choose. ReelOS validates that plan and renders a real 1080×1920 MP4 with subject-aware effects: titles behind the speaker, spotlight and contour, tracked labels, B-roll illustrations and a 45-recipe effect catalog. Ask for a change ("lower only the headline") and Muse revises just that part as a new version; every version can be compared, restored and downloaded.

New: multi-clip reels. Drop in several short clips from a trip or an event and one Muse request watches them all, picks the shots and writes visible-only captions. ReelOS snaps the cut to the music's beat, keeps camera times from metadata, converts iPhone HDR and slows very short clips, then renders with HyperFrames in a Calm, Energetic or Clean style. Restyling re-uses Muse's shots without another request.

It runs locally with Docker Compose (FastAPI + Next.js), with a CLI that drives the same engine. Limits: masks can need refinement around occlusions and there are no exact-word captions yet.

## Describe your use of Meta products to build the submitted project

Meta Model API is the brain of ReelOS. Muse Spark (muse-spark-1.3) writes every edit plan as validated JSON, applies targeted revisions, reads an optional style reference, and plans multi-clip reels by watching all the clips in one request. Muse Voice (muse-voice-transcribe-1.0) gives an approximate transcript so illustrations follow the topic. SAM 3.1 finds and tracks the selected person, and its masks (decoded with Meta's official @meta-sam/parser) drive text-behind-subject, spotlight and tracked labels. Clips and proxies go through the Meta Files API. Each paid call reserves a local budget allowance before dispatch and is never retried automatically.

## Why are Meta's models important to your solution?

The product only works because one model family both understands the footage and controls the edit. Muse Spark turns a creator's sentence plus the actual video into a structured plan we can validate and render, and revises one detail without disturbing the rest. SAM 3.1 gives pixel-accurate masks of the chosen person, which is what makes effects like titles behind the speaker look designed instead of pasted on. For multi-clip reels, Muse watching every clip at once is what lets ReelOS choose shots and write captions grounded in what is actually visible.

## Provide feedback from your experience using partner technologies

(Optional; Fireworks, Modal and Baseten were not used. Leave blank.)

## Survey questions

Your own answers; not drafted.
