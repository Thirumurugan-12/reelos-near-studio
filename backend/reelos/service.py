import json
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from reelos.config import Settings
from reelos.graphics import prepare_graphics
from reelos.media import MaskTrack, render
from reelos.meta import MetaClient, output_text
from reelos.planner import create_plan, revise_plan
from reelos.segmentation import save_masks
from reelos.store import Store, new_id
from reelos.timeline import EditPlan, validate_assets


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
        if not asset.get("provider_file"):
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
            elif req["action"] == "revise":
                parent = self.store.get("version", req["version_id"], pid)
                stage("Muse is applying your direction")
                plan, summary = revise_plan(
                    self.meta, EditPlan.model_validate(parent["plan"]), req["instruction"]
                )
                version = self.version(
                    pid, plan, parent["id"], summary, parent["track_key"], parent["observations"]
                )
                job["version_id"] = version["id"]
            else:
                version = self.store.get("version", req["version_id"], pid)
                job["version_id"] = version["id"]
            plan = EditPlan.model_validate(version["plan"])
            asset = self.store.get("asset", plan.asset_id, pid)
            quality = req.get("quality", "preview")
            target = self.version_dir(version["id"]) / f"{quality}.mp4"
            if not target.exists():
                if any(e.type == "graphic_insert" for e in plan.effects):
                    stage("Remotion is illustrating the story")
                graphics = prepare_graphics(plan, self.store.root)
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
                )
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
