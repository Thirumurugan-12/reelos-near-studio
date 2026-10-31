"""Catalog discovery and explicit, model-free application to immutable edit versions."""

from pathlib import Path

from fastapi.responses import FileResponse
from pydantic import Field

from reelos.catalog_contracts import (
    ALIASES,
    ENUMS,
    LAYOUT_LOOKS,
    LOOKS,
    NUMBERS,
    TEXT_LIST_FX,
    CatalogParams,
    catalog,
)
from reelos.catalog_samples import sample_params
from reelos.store import new_id
from reelos.timeline import Contract, EditPlan, Identifier, Seconds

PREVIEWS = Path(__file__).with_name("catalog_previews")


class ApplyEffect(Contract):
    version_id: Identifier
    params: CatalogParams
    start: Seconds
    end: Seconds
    subject_id: str | None = Field(default=None, pattern=r"^[0-9]{1,8}$")


def mount_catalog(app, editor):
    @app.get("/api/effects")
    def effects():
        rows = []
        for row in catalog():
            name = row["id"]
            rows.append(
                row
                | {
                    "options": [k for k in row["options"] if k not in {"images", "text"}],
                    "numeric_options": {
                        k: list(v) for k, v in NUMBERS.items() if k in row["options"]
                    },
                    "preview_url": f"/api/effects/{name}/preview",
                    "poster_url": f"/api/effects/{name}/poster",
                    "preview_ready": (PREVIEWS / f"{name}.mp4").exists(),
                    "multiline_text": name in TEXT_LIST_FX,
                    "accepts_text": "text" in row["options"],
                    "enum_options": {
                        k: sorted(LAYOUT_LOOKS.get(name, set()) if k == "look" else ENUMS[k])
                        for k in row["options"]
                        if k in ENUMS or k == "look"
                    },
                    "example": sample_params(name).model_dump(),
                    "looks": [k for k, (fx, _) in LOOKS.items() if fx == name],
                    "requires_values": name in {"liquid-glass-graph", "over-the-shoulder-zoom"},
                }
            )
        return {
            "effects": rows,
            "named_looks": list(LOOKS),
            "aliases": ALIASES,
            "preview_note": (
                "Illustrated previews use example text and data. "
                "Exports use your supplied text, values and media."
            ),
        }

    def artifact(name, suffix):
        name = "glitter-spotlight" if name == "glitter" else ALIASES.get(name, name)
        if name not in {r["id"] for r in catalog()} | set(LOOKS):
            raise KeyError("Effect not found")
        path = PREVIEWS / (name + suffix)
        if not path.is_file():
            raise KeyError("Preview is not prepared")
        return FileResponse(path, media_type="video/mp4" if suffix == ".mp4" else "image/webp")

    @app.get("/api/effects/{name}/preview")
    def preview(name: str):
        return artifact(name, ".mp4")

    @app.get("/api/effects/{name}/poster")
    def poster(name: str):
        return artifact(name, ".webp")

    @app.post("/api/projects/{project_id}/effects", status_code=202)
    def apply_effect(project_id: Identifier, data: ApplyEffect):
        parent = editor.store.get("version", data.version_id, project_id)
        if not parent.get("track_key"):
            raise ValueError("Create a subject-tracked edit before applying an effect.")
        if any(j["status"] in {"queued", "running"} for j in editor.store.list("job", project_id)):
            raise ValueError("Wait for this project’s current job before applying another effect.")
        subject = data.subject_id or next((e["subject_id"] for e in parent["plan"]["effects"]), "0")
        plan = EditPlan.model_validate(
            parent["plan"]
            | {
                "effects": parent["plan"]["effects"]
                + [
                    {
                        "id": "fx_" + new_id()[:12],
                        "type": "catalog_effect",
                        "start": data.start,
                        "end": data.end,
                        "subject_id": subject,
                        "reason": "Explicitly selected from the effect catalog.",
                        "params": data.params.model_dump(),
                    }
                ]
            }
        )
        label = next(r["label"] for r in catalog() if r["id"] == data.params.fx)
        version = editor.version(
            project_id, plan, parent=parent["id"], summary=f"{label} · {data.start:g}–{data.end:g}s"
        )
        job = editor.queue(
            project_id, {"action": "render", "version_id": version["id"], "quality": "preview"}
        )
        return job | {"version_id": version["id"]}
