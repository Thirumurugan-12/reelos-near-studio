"""Canonical, deliberately constrained editing contract shared by API and CLI."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]
Seconds = Annotated[float, Field(ge=0, le=300, allow_inf_nan=False)]
Unit = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Framing(Contract):
    scale: float = Field(default=1, ge=0.65, le=1)
    offset_y: float = Field(default=0, ge=0, le=0.35)

    @model_validator(mode="after")
    def fits_canvas(self):
        if self.scale + self.offset_y > 1.001:
            raise ValueError("framed footage must fit within the output canvas")
        return self


class TextStyle(Contract):
    text: str = Field(min_length=1, max_length=120)
    x: Unit = 0.5
    y: Unit = 0.23
    size: float = Field(default=0.075, ge=0.025, le=0.15)
    color: str = Field(default="#F4F4F2", pattern=r"^#[0-9a-fA-F]{6}$")


class SpotlightStyle(Contract):
    intensity: Unit = 0.45
    background: Literal["original", "monochrome", "black"] = "original"
    outline_color: str = Field(default="#F21F2B", pattern=r"^#[0-9a-fA-F]{6}$")
    outline_width: float = Field(default=0, ge=0, le=0.02)
    glow: Unit = 0


class EffectBase(Contract):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,50}$")
    start: Seconds
    end: Seconds
    subject_id: str = Field(pattern=r"^[0-9]{1,8}$")
    reason: str = Field(default="", max_length=300)


class Headline(EffectBase):
    type: Literal["behind_subject_text"]
    params: TextStyle


class Spotlight(EffectBase):
    type: Literal["subject_spotlight"]
    params: SpotlightStyle = Field(default_factory=SpotlightStyle)


class Label(EffectBase):
    type: Literal["tracked_label"]
    params: TextStyle


class GraphicStyle(Contract):
    template: Literal["document_stack", "browser_demo", "glasses", "classroom"]
    title: str = Field(min_length=1, max_length=36)
    body: str = Field(min_length=1, max_length=120)
    accent: str = Field(default="#F21F2B", pattern=r"^#[0-9a-fA-F]{6}$")


class GraphicInsert(EffectBase):
    type: Literal["graphic_insert"]
    params: GraphicStyle


Effect = Annotated[Headline | Spotlight | Label | GraphicInsert, Field(discriminator="type")]


class EditPlan(Contract):
    schema_version: Literal["1.0"] = "1.0"
    asset_id: Identifier
    source_in: Seconds = 0
    source_out: Seconds
    fps: Literal[30] = 30
    output_mode: Literal["reel", "full"] = "reel"
    framing: Framing = Field(default_factory=Framing)
    effects: list[Effect] = Field(default_factory=list, max_length=48)

    @property
    def duration(self) -> float:
        return self.source_out - self.source_in

    @model_validator(mode="after")
    def valid_timeline(self):
        limit = 300 if self.output_mode == "full" else 30
        if not 0.2 <= self.duration <= limit:
            raise ValueError(f"output duration must be between 0.2 and {limit} seconds")
        if self.output_mode == "reel" and len(self.effects) > 12:
            raise ValueError("Use at most twelve effects in a short reel.")
        if len({e.id for e in self.effects}) != len(self.effects):
            raise ValueError("effect IDs must be unique")
        for effect in self.effects:
            if not 0 <= effect.start < effect.end <= self.duration:
                raise ValueError(f"effect {effect.id} outside output duration")
        inserts = sorted(
            (e for e in self.effects if e.type == "graphic_insert"), key=lambda e: e.start
        )
        insert_limit = 8 if self.output_mode == "full" else 2
        if len(inserts) > insert_limit or any(e.end - e.start > 5 for e in inserts):
            raise ValueError(
                f"Use at most {insert_limit} graphic inserts, up to five seconds each."
            )
        if any(b.start < a.end for a, b in zip(inserts, inserts[1:])):
            raise ValueError("Graphic inserts must not overlap.")
        return self

    def storyboard(self) -> list[dict]:
        return [
            {
                "operation_id": e.id,
                "type": e.type,
                "start": e.start,
                "end": e.end,
                "source_start": self.source_in + e.start,
                "source_end": self.source_in + e.end,
                "reason": e.reason,
                "text": getattr(e.params, "text", None),
            }
            for e in sorted(self.effects, key=lambda e: e.start)
        ]


def validate_assets(plan: EditPlan, assets: dict) -> None:
    if plan.asset_id not in assets:
        raise ValueError("source asset not found")
    if plan.source_out > assets[plan.asset_id]["duration"] + 0.001:
        raise ValueError("source interval exceeds asset duration")
    if plan.output_mode == "full" and (
        plan.source_in != 0
        or abs(plan.source_out - assets[plan.asset_id]["duration"]) > 1 / plan.fps
    ):
        raise ValueError("Full-video mode must preserve the entire source.")
