import json
import logging
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from reelos import montage
from reelos.config import Settings
from reelos.graphics import prepare_graphics
from reelos.media import MaskTrack, render
from reelos.meta import MetaClient, output_text
from reelos.planner import create_plan, revise_plan
from reelos.segmentation import save_masks
from reelos.store import Store, new_id
from reelos.timeline import EditPlan, validate_assets

log = logging.getLogger("reelos.jobs")


class Editor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.store = Store(settings.data_dir)
        self.meta = MetaClient(settings, self.store)
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="reelos")
        # Provider outcome can be unknown after a crash. Never silently repeat paid jobs.
        for job in self.store.list("job"):
            if job["status"] in {"queued", "running"}:
                self.store.put(
                    "job",
                    job["id"],
                    job
                    | {
                        "status": "failed",
                        "error": "Server restarted. Review and retry this job.",
                    },
                )

    def asset_dir(self, id: str) -> Path:
        return self.store.root / "assets" / id

    def version_dir(self, id: str) -> Path:
        return self.store.root / "versions" / id

    def provider_file(self, asset: dict) -> str:
        if not asset.get("provider_file") or not self.meta.file_available(asset["provider_file"]):
            asset["provider_file"] = self.meta.upload(self.asset_dir(asset["id"]) / "proxy.mp4")
            self.store.put("asset", asset["id"], asset)
        return asset["provider_file"]

    def source_speech(self, asset: dict) -> dict | None:
        if not asset.get("has_audio"):
            return None
        if not asset.get("speech"):
            with tempfile.TemporaryDirectory() as temp:
                wav = Path(temp) / "source.wav"
                subprocess.run(
                    [
                        "ffmpeg",
                        "-v",
                        "error",
                        "-i",
                        str(self.asset_dir(asset["id"]) / "source.mp4"),
                        "-ac",
                        "1",
                        "-ar",
                        "24000",
                        "-c:a",
                        "pcm_s16le",
                        str(wav),
                    ],
                    capture_output=True,
                    check=True,
                    timeout=60,
                )
                asset["speech"] = self.meta.transcribe(wav)
            self.store.put("asset", asset["id"], asset)
        return asset["speech"]

    def segment(self, asset: dict, prompt: str, stage=None) -> tuple[dict, str]:
        import hashlib

        key = hashlib.sha256((self.settings.sam_model + "|" + prompt).encode()).hexdigest()[:32]
        directory = self.asset_dir(asset["id"]) / "tracks" / key
        manifest = directory / "manifest.json"
        if manifest.exists():
            return json.loads(manifest.read_text()), key
        directory.mkdir(parents=True, exist_ok=True)
        cached = directory / "response.json"
        if cached.exists():
            data = json.loads(cached.read_text())
        else:
            data = self.meta.response(
                self.settings.sam_model,
                [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_video", "file_id": self.provider_file(asset)},
                ],
                metadata={"mask_encoding": "one_bit"},
                request_timeout=600 if asset["duration"] > 60 else 180,
            )
            cached.write_text(json.dumps(data))
        if stage:
            stage("Decoding SAM subject masks")
        result = save_masks(output_text(data), directory, 360, 640, 10)
        return result, key

    def version(
        self,
        project_id: str,
        plan: EditPlan,
        parent: str | None = None,
        summary: str = "Manual edit",
        track_key: str | None = None,
        observations: list | None = None,
    ) -> dict:
        assets = {a["id"]: a for a in self.store.list("asset", project_id)}
        validate_assets(plan, assets)
        profile = {"font": "aileron", "pillow": "12.3.0", "version": "1"}
        if parent:
            previous = self.store.get("version", parent, project_id)
            profile = previous.get("render_profile", {"font": "system", "version": "legacy"})
            if previous["plan"]["asset_id"] == plan.asset_id:
                if track_key is None:
                    track_key = previous.get("track_key")
                if observations is None:
                    observations = previous.get("observations", [])
        return self.store.put(
            "version",
            new_id(),
            {
                "project_id": project_id,
                "parent_id": parent,
                "created_at": time.time(),
                "plan": plan.model_dump(),
                "summary": summary,
                "track_key": track_key,
                "render_profile": profile,
                "storyboard": plan.storyboard(),
                "observations": observations or [],
                "has_preview": False,
                "has_export": False,
            },
        )

    def montage_clips(self, project_id: str, clip_ids: list[str]) -> list[dict]:
        clips = [self.store.get("asset", id, project_id) for id in clip_ids]
        if len(clips) < 2 or any(c["role"] != "clip" for c in clips):
            raise ValueError("Choose at least two clips for a multi-clip reel.")
        return clips

    def montage_version(self, pid, shots, clips, plan: dict, summary: str, parent=None):
        record = montage.version_record(
            shots,
            {c["id"]: c for c in clips},
            plan["title"],
            summary,
            plan["style"],
            plan["show_times"],
            plan.get("source"),
        )
        return self.store.put(
            "version",
            new_id(),
            record
            | {
                "project_id": pid,
                "parent_id": parent,
                "created_at": time.time(),
                "track_key": None,
                "clip_ids": [c["id"] for c in clips],
                "has_preview": False,
                "has_export": False,
            },
        )

    def make_montage(self, pid: str, req: dict, stage) -> dict:
        clips = self.montage_clips(pid, req["clip_ids"])
        style, by_id = req.get("style", "calm"), {c["id"]: c for c in clips}
        stage("Preparing your clips")
        for clip in clips:
            montage.normalized_clip(clip, self.asset_dir(clip["id"]), montage.is_slow(clip))
        title = req.get("title", "").strip()
        stage("Muse is watching your clips")
        files = {c["id"]: self.provider_file(c) for c in clips}
        stage("Muse is planning your reel")
        try:
            proposal = montage.muse_proposal(
                self.meta, clips, files, title, req["instruction"], style
            )
            summary = proposal.summary or "Muse-planned multi-clip reel"
            shots = montage.fit_plan(proposal, by_id, style)
        except montage.PlanError:
            # Muse answered but the plan was unusable: never re-ask (no paid retries).
            proposal = montage.rule_proposal(clips, style)
            summary = "Clips in recording order (Muse's plan could not be used)"
            shots = montage.fit_plan(proposal, by_id, style)
        plan = {
            "title": title or proposal.title,
            "style": style,
            "show_times": req.get("show_times", True),
            # Muse's own windows, kept so every later restyle starts from them.
            "source": [shot.model_dump() for shot in proposal.shots],
        }
        return self.montage_version(pid, shots, clips, plan, summary)

    def restyle(self, pid: str, req: dict, stage) -> dict:
        parent = self.store.get("version", req["version_id"], pid)
        if parent.get("kind") not in {"montage", "trip"}:
            raise ValueError("Only multi-clip reels can change style.")
        clips = [self.store.get("asset", id, pid) for id in parent["clip_ids"]]
        old, style = montage.stored(parent), req.get("style", "calm")
        stage("Re-timing your shots for the new style")
        shots = montage.refit(old["source"], {c["id"]: c for c in clips}, style)
        plan = {
            "title": old["title"],
            "style": style,
            "show_times": req.get("show_times", True),
            "source": old["source"],
        }
        summary = f"{style.capitalize()} style · same shots, no new Muse request"
        return self.montage_version(pid, shots, clips, plan, summary, parent=parent["id"])

    def render_montage(self, version: dict, stage) -> None:
        pid, plan = version["project_id"], montage.stored(version)
        clips = [self.store.get("asset", id, pid) for id in version["clip_ids"]]
        export = self.version_dir(version["id"]) / "export.mp4"
        if not export.exists():
            stage("HyperFrames is rendering your reel")
            montage.render_reel(
                plan["shots"],
                {c["id"]: c for c in clips},
                {c["id"]: self.asset_dir(c["id"]) for c in clips},
                plan["title"],
                self.store.root,
                export,
                plan["style"],
                plan["show_times"],
            )
        preview = export.with_name("preview.mp4")
        if not preview.exists():
            preview.hardlink_to(export)
        version.update(has_preview=True, has_export=True)

    def queue(self, project_id: str, request: dict) -> dict:
        if any(j["status"] in {"queued", "running"} for j in self.store.list("job", project_id)):
            raise ValueError("This project already has a job running.")
        job = self.store.put(
            "job",
            new_id(),
            {
                "project_id": project_id,
                "request": request,
                "status": "queued",
                "stage": "Waiting to start",
                "progress": None,
                "created_at": time.time(),
            },
        )
        self.worker.submit(self.run, job)
        return job

    def run(self, job: dict):
        id, pid, req = job["id"], job["project_id"], job["request"]
        started = time.monotonic()

        def stage(name, progress=None):
            job.update(status="running", stage=name, progress=progress)
            self.store.put("job", id, job)

        try:
            stage("Preparing edit")
            version = None
            if req["action"] == "draft":
                asset = self.store.get("asset", req["asset_id"], pid)
                if asset["role"] != "source":
                    raise ValueError("Choose source footage for this edit.")
                stage("Tracking the selected subject with SAM")
                manifest, track_key = self.segment(asset, req["subject_prompt"], stage)
                subject = req.get("subject_id")
                if not subject and len(manifest["subjects"]) > 1:
                    job.update(
                        status="needs_subject",
                        stage="Choose your subject",
                        result={"subjects": manifest["subjects"], "track_key": track_key},
                    )
                    self.store.put("job", id, job)
                    return
                subject = subject or manifest["subjects"][0]
                if subject not in manifest["subjects"]:
                    raise ValueError("Selected subject is not in this track.")
                reference_file = None
                reference_duration = None
                if req.get("reference_id"):
                    reference = self.store.get("asset", req["reference_id"], pid)
                    if reference["role"] != "reference":
                        raise ValueError("Choose a reference video for style analysis.")
                    reference_file = self.provider_file(reference)
                    reference_duration = reference["duration"]
                stage("Muse is planning the edit")
                speech = self.source_speech(asset)
                plan, observations = create_plan(
                    self.meta,
                    asset,
                    self.provider_file(asset),
                    subject,
                    req["instruction"],
                    reference_file,
                    speech,
                    req.get("output_mode", "reel"),
                    reference_duration=reference_duration,
                    supporting_assets=[
                        {k: a.get(k) for k in ("id", "name", "kind", "duration")}
                        for a in self.store.list("asset", pid)
                        if a["role"] == "supporting"
                    ],
                )
                version = self.version(
                    pid,
                    plan,
                    summary="Reference-inspired edit"
                    if req.get("reference_id")
                    else "First Meta-directed edit",
                    track_key=track_key,
                    observations=observations,
                )
                job["version_id"] = version["id"]
                if req.get("review_storyboard"):
                    job.update(
                        status="completed",
                        stage="Storyboard ready",
                        elapsed=time.monotonic() - started,
                    )
                    self.store.put("job", id, job)
                    return
            elif req["action"] == "montage":
                version = self.make_montage(pid, req, stage)
                job["version_id"] = version["id"]
            elif req["action"] == "restyle":
                version = self.restyle(pid, req, stage)
                job["version_id"] = version["id"]
            elif req["action"] == "revise":
                parent = self.store.get("version", req["version_id"], pid)
                if parent.get("kind") in {"montage", "trip"}:
                    raise ValueError(
                        "Multi-clip reels can't be revised with text yet. Change the style "
                        "or make a new reel."
                    )
                stage("Muse is applying your direction")
                plan, summary = revise_plan(
                    self.meta,
                    EditPlan.model_validate(parent["plan"]),
                    req["instruction"],
                    supporting_assets=[
                        {k: a.get(k) for k in ("id", "name", "kind", "duration")}
                        for a in self.store.list("asset", pid)
                        if a["role"] == "supporting"
                    ],
                )
                version = self.version(
                    pid, plan, parent["id"], summary, parent["track_key"], parent["observations"]
                )
                job["version_id"] = version["id"]
            else:
                version = self.store.get("version", req["version_id"], pid)
                job["version_id"] = version["id"]
            quality = req.get("quality", "preview")
            if version.get("kind") in {"montage", "trip"}:
                self.render_montage(version, stage)
                target = None
            else:
                plan = EditPlan.model_validate(version["plan"])
                asset = self.store.get("asset", plan.asset_id, pid)
                target = self.version_dir(version["id"]) / f"{quality}.mp4"
            if target is not None and not target.exists():
                if any(e.type == "graphic_insert" for e in plan.effects):
                    stage("Illustrating the story")
                graphics = prepare_graphics(
                    plan, self.store.root, renderer=self.settings.graphics_renderer
                )
                track = None
                if version.get("track_key"):
                    track = MaskTrack(self.asset_dir(asset["id"]) / "tracks" / version["track_key"])
                stage("Rendering your " + quality)
                render(
                    self.asset_dir(asset["id"]) / "source.mp4",
                    plan,
                    target,
                    width=360 if quality == "preview" else 1080,
                    track=track,
                    progress=lambda p: stage("Rendering your " + quality, p),
                    font_family=version.get("render_profile", {}).get("font", "system"),
                    graphics=graphics,
                    asset_root=self.store.root,
                )
            if version.get("kind") not in {"montage", "trip"}:
                version["has_" + quality] = True
            self.store.put("version", version["id"], version)
            project = self.store.get("project", pid)
            project["current_version_id"] = version["id"]
            self.store.put("project", pid, project)
            job.update(
                status="completed",
                progress=1,
                stage="Ready to play",
                elapsed=time.monotonic() - started,
            )
        except Exception as exc:
            if not isinstance(exc, ValueError):
                log.exception("Job %s failed unexpectedly", id)
            message = (
                str(exc)[:400]
                if isinstance(exc, ValueError)
                else ("This operation could not finish. Your previous edit is preserved.")
            )
            job.update(
                status="failed",
                error=message,
                stage="Needs attention",
                elapsed=time.monotonic() - started,
            )
        self.store.put("job", id, job)
