import os
import shutil
import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import Field, model_validator

from reelos.config import Settings
from reelos.media import inspect_media, make_proxy
from reelos.service import Editor
from reelos.store import new_id
from reelos.timeline import Contract, EditPlan, Identifier


class ProjectInput(Contract):
    name: str = Field(default="Untitled reel", min_length=1, max_length=100)


class VersionInput(Contract):
    plan: EditPlan
    parent_id: Identifier | None = None


class JobInput(Contract):
    action: Literal["draft", "revise", "render"]
    asset_id: Identifier | None = None
    version_id: Identifier | None = None
    reference_id: Identifier | None = None
    instruction: str = Field(default="Create a clear, engaging creator explainer.", max_length=2000)
    subject_prompt: str = Field(default="person", min_length=1, max_length=120)
    subject_id: str | None = Field(default=None, pattern=r"^[0-9]{1,8}$")
    review_storyboard: bool = False
    quality: Literal["preview", "export"] = "preview"

    @model_validator(mode="after")
    def references(self):
        if self.action == "draft" and not self.asset_id:
            raise ValueError("Source footage is required.")
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
            "note": "Local reservations are conservative allowances, not confirmed Meta billing.",
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
            "versions": editor.store.list("version", project_id),
            "jobs": editor.store.list("job", project_id),
        }

    @app.post("/api/projects/{project_id}/assets", status_code=201)
    def asset_upload(
        project_id: Identifier,
        file: UploadFile = File(),
        role: Literal["source", "reference"] = Form("source"),
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
            metadata = inspect_media(source)
            if metadata["duration"] > (30 if role == "reference" else 60):
                raise ValueError("Use a source up to 60 seconds or reference up to 30 seconds.")
            make_proxy(source, directory / "proxy.mp4")
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
        editor.store.get("asset", asset_id, project_id)
        return FileResponse(editor.asset_dir(asset_id) / "source.mp4", media_type="video/mp4")

    @app.post("/api/projects/{project_id}/versions", status_code=201)
    def version_create(project_id: Identifier, data: VersionInput):
        editor.store.get("project", project_id)
        return editor.version(project_id, data.plan, data.parent_id)

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
        return editor.queue(project_id, data.model_dump())

    @app.get("/api/projects/{project_id}/jobs/{job_id}")
    def job_get(project_id: Identifier, job_id: Identifier):
        return editor.store.get("job", job_id, project_id)

    return app
