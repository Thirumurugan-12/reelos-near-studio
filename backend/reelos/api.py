import os
import shutil
import time
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, Path, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import Field, model_validator

from reelos.config import Settings
from reelos.media import inspect_media, make_proxy
from reelos.montage import clip_metadata
from reelos.segmentation import subject_thumbnail
from reelos.service import Editor
from reelos.store import new_id
from reelos.timeline import Contract, EditPlan, Framing, Identifier


class ProjectInput(Contract):
    name: str = Field(default="Untitled reel", min_length=1, max_length=100)


class VersionInput(Contract):
    plan: EditPlan
    parent_id: Identifier | None = None


class JobInput(Contract):
    action: Literal["draft", "revise", "render", "montage", "restyle", "carousel", "paint_broll"]
    asset_id: Identifier | None = None
    clip_ids: list[Identifier] = Field(default_factory=list, max_length=12)
    title: str = Field(default="", max_length=24)
    style: Literal["calm", "energetic", "clean"] = "calm"
    show_times: bool = True
    version_id: Identifier | None = None
    reference_id: Identifier | None = None
    instruction: str = Field(default="Create a clear, engaging creator explainer.", max_length=2000)
    subject_prompt: str = Field(default="person", min_length=1, max_length=120)
    subject_id: str | None = Field(default=None, pattern=r"^[0-9]{1,8}$")
    review_storyboard: bool = False
    quality: Literal["preview", "export"] = "preview"
    output_mode: Literal["reel", "full"] = "reel"

    @model_validator(mode="after")
    def references(self):
        if self.action == "draft" and not self.asset_id:
            raise ValueError("Source footage is required.")
        if self.action == "montage":
            if len(set(self.clip_ids)) < 2:
                raise ValueError("Choose at least two clips for a multi-clip reel.")
            return self
        if self.action != "draft" and not self.version_id:
            raise ValueError("An edit version is required.")
        return self


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.load()
    editor = Editor(settings)

    @asynccontextmanager
    async def lifespan(app):
        yield
        editor.worker.shutdown(wait=True)

    app = FastAPI(title="ReelOS", version="0.1.0", lifespan=lifespan)
    app.state.editor = editor
    from reelos.catalog_api import mount_catalog

    mount_catalog(app, editor)
    from reelos.near_api import mount_near

    mount_near(app, settings)

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        origin = request.headers.get("origin")
        allowed = os.getenv("REELOS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        if origin and origin not in allowed.split(","):
            return JSONResponse(
                {"error": {"code": "ORIGIN", "message": "Origin not allowed."}}, 403
            )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({"error": {"code": "NOT_FOUND", "message": "Resource not found."}}, 404)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({"error": {"code": "INVALID_INPUT", "message": str(exc)[:400]}}, 422)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        return JSONResponse(
            {
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Check the required fields and supported values.",
                }
            },
            422,
        )

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "meta_configured": bool(settings.api_key),
            "mode": "controlled_single_user",
            "budget_limit_usd": settings.budget_usd,
        }

    @app.get("/api/usage")
    def usage():
        return editor.store.budget() | {
            "limit_usd": settings.budget_usd,
            "note": "Estimates cover reported usage only; unpriced calls may add cost. "
            "Reservations remain conservative allowances. Neither is confirmed Meta billing.",
        }

    @app.get("/api/projects")
    def projects():
        return editor.store.list("project")

    @app.post("/api/projects", status_code=201)
    def project_create(data: ProjectInput):
        return editor.store.put(
            "project",
            new_id(),
            {
                "name": data.name,
                "created_at": time.time(),
                "current_version_id": None,
            },
        )

    @app.get("/api/projects/{project_id}")
    def project_get(project_id: Identifier):
        return editor.store.get("project", project_id) | {
            "assets": editor.store.list("asset", project_id),
            "versions": sorted(
                editor.store.list("version", project_id),
                key=lambda version: (version.get("created_at", 0), version["id"]),
                reverse=True,
            ),
            "jobs": editor.store.list("job", project_id),
        }

    @app.post("/api/projects/{project_id}/assets", status_code=201)
    def asset_upload(
        project_id: Identifier,
        file: UploadFile = File(),
        role: Literal["source", "reference", "supporting", "clip"] = Form("source"),
    ):
        editor.store.get("project", project_id)
        id = new_id()
        directory = editor.asset_dir(id)
        directory.mkdir(parents=True)
        try:
            size = 0
            source = directory / "source.mp4"
            with source.open("wb") as target:
                while chunk := file.file.read(1024 * 1024):
                    size += len(chunk)
                    if size > 200 * 1024 * 1024:
                        raise ValueError("Video exceeds the 200 MB upload limit.")
                    target.write(chunk)
            metadata = None
            if role == "supporting":
                try:
                    with Image.open(source) as image:
                        if image.format not in {"PNG", "JPEG", "WEBP"}:
                            raise ValueError("Use a PNG, JPEG or WebP supporting image.")
                        if image.width * image.height > 25_000_000:
                            raise ValueError("Supporting images must be at most 25 megapixels.")
                        image.load()
                        normalized = ImageOps.exif_transpose(image).convert("RGB")
                        normalized.thumbnail((2048, 2048))
                        normalized.save(directory / "source.png")
                        metadata = {
                            "kind": "image",
                            "duration": 0,
                            "width": normalized.width,
                            "height": normalized.height,
                            "has_audio": False,
                        }
                    source.rename(directory / "original.upload")
                except UnidentifiedImageError:
                    pass  # Supporting videos use the same inspected media path below.
                except (OSError, Image.DecompressionBombError) as exc:
                    raise ValueError("Cannot decode this supporting image.") from exc
            metadata = metadata or inspect_media(source)
            if metadata["duration"] > {"reference": 60, "clip": 120}.get(role, 300):
                raise ValueError(
                    "Use source footage up to five minutes, reel clips up to two minutes "
                    "or a reference up to one minute."
                )
            if role == "clip":
                metadata |= clip_metadata(source)
            if metadata.get("kind") != "image":
                make_proxy(source, directory / "proxy.mp4", portrait=role in {"source", "clip"})
            return editor.store.put(
                "asset",
                id,
                metadata
                | {
                    "project_id": project_id,
                    "role": role,
                    "size": size,
                    "name": (file.filename or "clip.mp4").replace("\\", "/").split("/")[-1][:150],
                },
            )
        except Exception:
            shutil.rmtree(directory)
            raise

    @app.get("/api/projects/{project_id}/assets/{asset_id}/source")
    def asset_source(project_id: Identifier, asset_id: Identifier):
        asset = editor.store.get("asset", asset_id, project_id)
        if asset.get("kind") == "image":
            return FileResponse(editor.asset_dir(asset_id) / "source.png", media_type="image/png")
        return FileResponse(editor.asset_dir(asset_id) / "source.mp4", media_type="video/mp4")

    @app.post("/api/projects/{project_id}/versions", status_code=201)
    def version_create(project_id: Identifier, data: VersionInput):
        editor.store.get("project", project_id)
        return editor.version(project_id, data.plan, data.parent_id)

    @app.post("/api/projects/{project_id}/versions/{version_id}/framing", status_code=202)
    def reframe(project_id: Identifier, version_id: Identifier, data: Framing):
        parent = editor.store.get("version", version_id, project_id)
        if any(j["status"] in {"queued", "running"} for j in editor.store.list("job", project_id)):
            raise ValueError("Wait for this project’s current job before changing framing.")
        plan = EditPlan.model_validate(parent["plan"] | {"framing": data.model_dump()})
        version = editor.version(project_id, plan, parent=version_id, summary="Reframed speaker")
        job = editor.queue(
            project_id, {"action": "render", "version_id": version["id"], "quality": "preview"}
        )
        return job | {"version_id": version["id"]}

    @app.post("/api/projects/{project_id}/versions/{version_id}/restore")
    def restore(project_id: Identifier, version_id: Identifier):
        version = editor.store.get("version", version_id, project_id)
        if not version["has_preview"]:
            raise ValueError("Render this version's preview before restoring it.")
        project = editor.store.get("project", project_id)
        return editor.store.put("project", project_id, project | {"current_version_id": version_id})

    @app.get("/api/projects/{project_id}/versions/{version_id}/{kind}")
    def version_file(
        project_id: Identifier, version_id: Identifier, kind: Literal["preview", "export", "plan"]
    ):
        version = editor.store.get("version", version_id, project_id)
        if kind == "plan":
            return JSONResponse(
                version["plan"],
                headers={
                    "Content-Disposition": 'attachment; filename="reelos-plan.json"',
                },
            )
        target = editor.version_dir(version_id) / f"{kind}.mp4"
        if not target.exists():
            raise KeyError("Render not ready")
        return FileResponse(
            target, media_type="video/mp4", filename="reelos.mp4" if kind == "export" else None
        )

    @app.get("/api/projects/{project_id}/versions/{version_id}/carousel/{name}")
    def carousel_file(
        project_id: Identifier,
        version_id: Identifier,
        name: Annotated[str, Path(pattern=r"^(slide-\d{2}\.png|carousel\.zip)$")],
    ):
        version = editor.store.get("version", version_id, project_id)
        if not version.get("carousel"):
            raise KeyError("Carousel not ready")
        target = editor.version_dir(version_id) / "carousel" / name
        if not target.exists():
            raise KeyError("Carousel file not found")
        if name.endswith(".zip"):
            return FileResponse(
                target, media_type="application/zip", filename="reelos-carousel.zip"
            )
        return FileResponse(target, media_type="image/png")

    @app.post("/api/projects/{project_id}/jobs", status_code=202)
    def job_create(project_id: Identifier, data: JobInput):
        editor.store.get("project", project_id)
        # Fail early on cross-project references before dispatching work.
        for key, kind in [
            ("asset_id", "asset"),
            ("reference_id", "asset"),
            ("version_id", "version"),
        ]:
            value = getattr(data, key)
            if value:
                editor.store.get(kind, value, project_id)
        for clip_id in data.clip_ids:
            editor.store.get("asset", clip_id, project_id)
        return editor.queue(project_id, data.model_dump())

    @app.get("/api/projects/{project_id}/jobs/{job_id}")
    def job_get(project_id: Identifier, job_id: Identifier):
        return editor.store.get("job", job_id, project_id)

    @app.get("/api/projects/{project_id}/jobs/{job_id}/subjects/{subject_id}/thumbnail")
    def subject_preview(project_id: Identifier, job_id: Identifier, subject_id: str):
        job = editor.store.get("job", job_id, project_id)
        if subject_id not in job.get("result", {}).get("subjects", []):
            raise KeyError("Subject not found")
        asset = editor.store.get("asset", job["request"]["asset_id"], project_id)
        directory = editor.asset_dir(asset["id"])
        return Response(
            subject_thumbnail(
                directory / "proxy.mp4",
                directory / "tracks" / job["result"]["track_key"],
                subject_id,
            ),
            media_type="image/png",
        )

    return app
