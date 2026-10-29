"""Canonical, deliberately constrained editing contract shared by API and CLI."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]
Seconds = Annotated[float, Field(ge=0, le=60, allow_inf_nan=False)]
Unit = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class TextStyle(Contract):
    text: str = Field(min_length=1, max_length=120)
    x: Unit = 0.5
    y: Unit = 0.23
    size: float = Field(default=0.075, ge=0.025, le=0.15)
    color: str = Field(default="#F4F4F2", pattern=r"^#[0-9a-fA-F]{6}$")


class SpotlightStyle(Contract):
    intensity: Unit = 0.45


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


Effect = Annotated[Headline | Spotlight | Label, Field(discriminator="type")]


class EditPlan(Contract):
    schema_version: Literal["1.0"] = "1.0"
    asset_id: Identifier
    source_in: Seconds = 0
    source_out: Seconds
    fps: Literal[30] = 30
    effects: list[Effect] = Field(default_factory=list, max_length=12)

    @property
    def duration(self) -> float:
        return self.source_out - self.source_in

    @model_validator(mode="after")
    def valid_timeline(self):
        if not 0.2 <= self.duration <= 30:
            raise ValueError("output duration must be between 0.2 and 30 seconds")
        if len({e.id for e in self.effects}) != len(self.effects):
            raise ValueError("effect IDs must be unique")
        for effect in self.effects:
            if not 0 <= effect.start < effect.end <= self.duration:
                raise ValueError(f"effect {effect.id} outside output duration")
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
