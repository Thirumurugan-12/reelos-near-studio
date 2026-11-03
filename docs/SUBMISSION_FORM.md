# Cerebral Valley submission fields (draft, not submitted)

Team: bluesense · Track: Indie Developer Track · Problem statement: Build for Your World

## Project Description

ReelOS is an AI video editor that works like a creative agent you direct in plain language. You give it a goal ("bold and confident, headline behind me, spotlight on me") and it carries out the multi-step job: Muse Spark watches the footage and decides the edit as a structured plan (which effects, when, where and with what text); ReelOS calls SAM 3.1 to find and track the person, checks every decision against a strict schema, and drives the renderers to produce a real 1080×1920 MP4. When SAM sees several people, it stops and asks you which one. Ask for a change ("lower only the headline") and Muse revises just that decision as a new version; every version can be compared, restored and downloaded. Muse Image then paints a custom illustration for every B-roll card Muse planned.

The same loop handles many clips at once: one Muse request watches every clip, picks the shots and their order, and writes captions grounded in what is visible. ReelOS converts iPhone HDR, slows very short clips, snaps the cut to the music's beat, keeps camera times from metadata and renders with HyperFrames in a Calm, Energetic or Clean style. Restyling re-uses Muse's plan without another call. One more click turns the reel into a swipe-ready Instagram carousel: Muse Image restyles real frames from Muse's chosen shots, and ReelOS typesets the title, captions and camera times on top.

## Describe your use of Meta products to build the submitted project

Meta Model API is the brain of ReelOS. Muse Spark (muse-spark-1.3) writes every edit plan as validated JSON, applies targeted revisions, reads an optional style reference, and plans multi-clip reels by watching all the clips in one request. Muse Voice (muse-voice-transcribe-1.0) gives an approximate transcript so illustrations follow the topic. SAM 3.1 finds and tracks the selected person, and its masks (decoded with Meta's official @meta-sam/parser) drive text-behind-subject, spotlight and tracked labels. Muse Image (muse-image-1.0) paints each B-roll card from Muse's own insert text and, in edit mode, restyles real frames from the reel into 4:5 Instagram carousel slides. Clips and proxies go through the Meta Files API. Each paid call reserves a local budget allowance before dispatch and is never retried automatically.

## Why are Meta's models important to your solution?

The product only works because one model family both understands the footage and controls the edit. Muse Spark turns a creator's sentence plus the actual video into a structured plan we can validate and render, and revises one detail without disturbing the rest. SAM 3.1 gives pixel-accurate masks of the chosen person, which is what makes effects like titles behind the speaker look designed instead of pasted on. For multi-clip reels, Muse watching every clip at once is what lets ReelOS choose shots and write captions grounded in what is actually visible, and Muse Image turns those same shots into designed carousel slides and B-roll art that keep the creator's real scenes.

## Provide feedback from your experience using partner technologies

(Optional; Fireworks, Modal and Baseten were not used. Leave blank.)

## Survey questions

Your own answers; not drafted.
