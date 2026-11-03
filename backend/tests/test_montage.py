import json
from types import SimpleNamespace

import pytest

from reelos import montage as trip


def clip(i, duration, recorded=None, audio=True):
    return {
        "id": f"{i:032x}",
        "role": "clip",
        "duration": duration,
        "has_audio": audio,
        "recorded_at": recorded,
        "hdr": None,
    }


def test_apple_local_time_wins_and_orders_clips():
    assert trip.parse_time("2026-08-29T07:26:11+0530").hour == 7
    late = clip(1, 5, trip.parse_time("2026-08-29T07:54:55+0530").isoformat())
    early = clip(2, 5, trip.parse_time("2026-08-29T07:23:38+0530").isoformat())
    undated = clip(3, 5)
    assert [c["id"] for c in trip.ordered([undated, late, early])] == [
        early["id"],
        late["id"],
        undated["id"],
    ]
    assert trip.local_time(early) == "07:23"
    assert trip.date_lines(early) == ("29 AUG 2026", "29 · 08 · 2026")


def test_fit_plan_snaps_to_beats_clamps_and_slows_short_clips():
    long, short = clip(1, 17.6), clip(2, 0.78)
    proposal = trip.MontageProposal(
        shots=[
            trip.MontageShot(clip_id=long["id"], start=16.0, end=21.0, caption="into the mist"),
            trip.MontageShot(clip_id=short["id"], start=0, end=0.78, caption="<b>ride</b>"),
        ]
    )
    shots = trip.fit_plan(proposal, {c["id"]: c for c in (long, short)})
    first, second = shots
    beats = first["duration"] / trip.beat("calm")
    assert beats == pytest.approx(round(beats)) and first["duration"] == pytest.approx(4.8)
    assert first["media_start"] + first["duration"] <= long["duration"]
    assert first["caption"] == "INTO THE MIST"
    assert second["slow"] and second["duration"] == pytest.approx(1.8)
    assert second["caption"] == "BRIDE/B"  # markup characters are stripped, never rendered
    with pytest.raises(trip.PlanError):
        trip.fit_plan(
            trip.MontageProposal(shots=[trip.MontageShot(clip_id="f" * 32, start=0, end=3)] * 2),
            {long["id"]: long},
        )


def test_fit_plan_caps_total_length():
    clips = {c["id"]: c for c in (clip(i, 60) for i in range(1, 9))}
    proposal = trip.MontageProposal(
        shots=[trip.MontageShot(clip_id=id, start=0, end=9.6) for id in clips]
    )
    shots = trip.fit_plan(proposal, clips)
    assert sum(s["duration"] for s in shots) <= trip.MAX_TOTAL


def test_composition_keeps_all_words_out_of_html():
    a, b = clip(1, 10, "2026-08-29T07:23:38+05:30"), clip(2, 10, "2026-08-29T07:26:11+05:30")
    clips = {c["id"]: c for c in (a, b)}
    shots = [
        {"clip_id": a["id"], "media_start": 1, "duration": 4.8, "slow": False, "caption": "X"},
        {
            "clip_id": b["id"],
            "media_start": 0,
            "duration": 4.8,
            "slow": False,
            "caption": "<SCRIPT>ALERT(1)</SCRIPT>",
        },
    ]
    html = trip.composition(shots, clips)
    assert "@@" not in html and "SCRIPT>ALERT" not in html and "07:26" not in html
    assert 'data-duration="9.600"' in html
    values = trip.variables(shots, clips, "Nandi Hills")
    assert values["cap1"] == "<SCRIPT>ALERT(1)</SCRIPT>" and values["time1"] == "07:26"
    assert values["title"] == "Nandi Hills" and values["dateline"] == "29 AUG 2026"


def test_muse_plans_with_one_call_and_bad_answers_never_retry():
    clips = [clip(1, 10), clip(2, 8)]
    files = {c["id"]: f"file-{i}" for i, c in enumerate(clips)}
    calls = []

    class Fake:
        settings = SimpleNamespace(muse_model="muse-spark-1.3")

        def __init__(self, text):
            self.text = text

        def response(self, model, content, **kwargs):
            calls.append(content)
            return {"output": [{"content": [{"type": "output_text", "text": self.text}]}]}

    good = json.dumps(
        {
            "title": "Morning mist",
            "shots": [
                {"clip_id": clips[0]["id"], "start": 1, "end": 5, "caption": "INTO THE MIST"},
                {"clip_id": clips[1]["id"], "start": 0, "end": 4, "caption": "VALLEY VIEW"},
            ],
            "summary": "Mist first, then the view.",
        }
    )
    proposal = trip.muse_proposal(Fake(good), clips, files, "", "calm", "calm")
    assert len(calls) == 1 and proposal.title == "Morning mist"
    assert [p["file_id"] for p in calls[0] if p["type"] == "input_file"] == ["file-0", "file-1"]
    with pytest.raises(trip.PlanError):
        trip.muse_proposal(Fake("not json"), clips, files, "", "calm", "calm")
    assert len(calls) == 2  # one call per attempt, no hidden retry


def test_version_record_reads_like_an_edit_for_history_and_timeline():
    a, b = clip(1, 10, "2026-08-29T07:23:38+05:30"), clip(2, 10)
    shots = [
        {"clip_id": a["id"], "media_start": 0, "duration": 4.8, "slow": False, "caption": "MIST"},
        {"clip_id": b["id"], "media_start": 0, "duration": 1.8, "slow": True, "caption": ""},
    ]
    record = trip.version_record(shots, {a["id"]: a, b["id"]: b}, "Trip", "summary")
    assert record["kind"] == "montage" and record["plan"]["source_out"] == pytest.approx(6.6)
    assert [e["type"] for e in record["plan"]["effects"]] == ["montage_shot", "montage_shot"]
    assert record["plan"]["effects"][0]["params"]["text"] == "07:23 · MIST"
    assert record["plan"]["effects"][1]["params"]["text"] == "SHOT 2"


def test_rule_proposal_uses_every_clip_in_recording_order():
    clips = [clip(1, 20, "2026-08-29T08:00:00+05:30"), clip(2, 0.7, "2026-08-29T07:00:00+05:30")]
    proposal = trip.rule_proposal(clips)
    assert [s.clip_id for s in proposal.shots] == [clips[1]["id"], clips[0]["id"]]


def test_montage_job_input_needs_two_distinct_clips():
    from pydantic import ValidationError

    from reelos.api import JobInput

    with pytest.raises(ValidationError, match="at least two clips"):
        JobInput(action="montage", clip_ids=["a" * 32, "a" * 32])
    job = JobInput(action="montage", clip_ids=["a" * 32, "b" * 32], title="Nandi Hills")
    assert job.title == "Nandi Hills"


def test_normalize_filter_tonemaps_hdr_and_interpolates_short_clips(monkeypatch):
    monkeypatch.setattr(trip, "has_zscale", lambda: True)
    hlg = trip.normalize_filter("arib-std-b67", slow=True)
    assert "tin=arib-std-b67" in hlg and "tonemap=hable" in hlg and "minterpolate" in hlg
    sdr = trip.normalize_filter(None, slow=False)
    assert "zscale" not in sdr and sdr.endswith("fps=30,format=yuv420p")


def test_styles_use_their_own_beat_grid_and_shot_lengths():
    long = clip(1, 30)
    proposal = trip.MontageProposal(
        shots=[trip.MontageShot(clip_id=long["id"], start=0, end=7.0, caption="A")] * 2
    )
    calm = trip.fit_plan(proposal, {long["id"]: long}, "calm")
    energetic = trip.fit_plan(proposal, {long["id"]: long}, "energetic")
    assert calm[0]["duration"] == pytest.approx(7.2)  # 12 beats of 0.6 s
    assert energetic[0]["duration"] == pytest.approx(4.0)  # capped at 8 beats of 0.5 s
    assert trip.beat("energetic") == 0.5 and trip.beat("clean") == 0.6


def test_restyle_refit_keeps_moments_and_captions_without_a_model():
    long, short = clip(1, 20), clip(2, 0.78)
    clips = {c["id"]: c for c in (long, short)}
    calm = [
        {
            "clip_id": long["id"],
            "media_start": 3.0,
            "duration": 7.2,
            "slow": False,
            "caption": "INTO THE MIST",
        },
        {
            "clip_id": short["id"],
            "media_start": 0.0,
            "duration": 1.8,
            "slow": True,
            "caption": "CURVING AHEAD",
        },
    ]
    energetic = trip.refit(trip.source_from_shots(calm), clips, "energetic")
    assert [s["caption"] for s in energetic] == ["INTO THE MIST", "CURVING AHEAD"]
    assert energetic[0]["media_start"] == pytest.approx(3.0)
    assert energetic[0]["duration"] == pytest.approx(4.0) and energetic[1]["slow"]


def test_each_style_renders_its_own_look_and_hides_times_when_asked():
    a, b = clip(1, 10, "2026-08-29T07:23:38+05:30"), clip(2, 10, "2026-08-29T07:26:11+05:30")
    clips = {c["id"]: c for c in (a, b)}
    shots = [
        {"clip_id": a["id"], "media_start": 1, "duration": 4.0, "slow": False, "caption": "X"},
        {"clip_id": b["id"], "media_start": 1, "duration": 4.0, "slow": False, "caption": "Y"},
    ]
    energetic = trip.composition(shots, clips, "energetic")
    clean = trip.composition(shots, clips, "clean")
    calm = trip.composition(shots, clips, "calm")
    assert 'data-style="energetic"' in energetic and 'T("#flash"' in energetic
    assert 'T("#shot-0", {y: 0}' in energetic  # whips alternate y, x, y...
    assert 'T("#flash"' not in clean and 'T("#shot-' not in clean  # hard cuts only
    assert 'data-style="calm"' in calm and 'T("#veil", {opacity: 0}, {opacity: 0.85' in calm
    hidden = trip.variables(shots, clips, "Reel", show_times=False)
    assert hidden["time1"] == "" and hidden["dateline"] == "" and hidden["cap1"] == "Y"


def test_versions_saved_before_styles_still_load():
    shot = {
        "clip_id": "a" * 32,
        "media_start": 4.5,
        "duration": 1.8,
        "slow": True,
        "caption": "RIDE",
    }
    legacy = {"kind": "trip", "trip": {"title": "Nandi Hills", "shots": [shot]}}
    plan = trip.stored(legacy)
    assert (plan["title"], plan["style"], plan["show_times"]) == ("Nandi Hills", "calm", True)
    assert plan["source"] == [
        {"clip_id": "a" * 32, "start": 1.8, "end": pytest.approx(2.52), "caption": "RIDE"}
    ]


def test_restyle_job_input_carries_style():
    from reelos.api import JobInput

    job = JobInput(action="restyle", version_id="a" * 32, style="energetic", show_times=False)
    assert job.style == "energetic" and job.show_times is False


def test_restyle_chain_starts_from_muse_windows_not_the_previous_style():
    long = clip(1, 30)
    clips = {long["id"]: long}
    source = [
        {"clip_id": long["id"], "start": 2.0, "end": 9.2, "caption": "A"},
        {"clip_id": long["id"], "start": 12.0, "end": 19.2, "caption": "B"},
    ]
    energetic = trip.refit(source, clips, "energetic")
    record = trip.version_record(energetic, clips, "T", "s", "energetic", False, source)
    clean = trip.refit(trip.stored(record)["source"], clips, "clean")
    assert [s["duration"] for s in energetic] == [4.0, 4.0]
    assert [s["duration"] for s in clean] == [7.2, 7.2]  # not shrunk by the energetic pass
