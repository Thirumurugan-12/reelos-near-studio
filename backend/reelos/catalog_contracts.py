"""Bounded public contract for the 45 attributed starter recipes."""

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


@lru_cache
def catalog():
    return json.loads(Path(__file__).with_name("effect_catalog.json").read_text())


ALIASES = json.loads(Path(__file__).with_name("catalog_aliases.json").read_text())
LOOKS = {
    "glitter-spotlight": ("spotlight", "sparkle"),
    "editorial-cover": ("cover-star", "editorial"),
    "glass-bento": ("liquid-glass-graph", "bento"),
}
TEXT_LIST_FX = {
    "lineup",
    "the-bill",
    "todo",
    "shortcut-rain",
    "split-headline",
    "check-pills",
    "phone-fan",
    "headline-wall",
    "checklist",
    "apple-toggles",
    "led-sign",
    "over-the-shoulder-zoom",
    "messages",
}
NUMBERS = {
    "at": (0, 300),
    "x": (0.05, 0.95),
    "zoom": (1, 2),
    "push": (0, 2),
    "size": (0.08, 0.7),
    "count": (1, 1_000_000_000),
    "speed": (0.1, 5),
    "angle": (-45, 45),
    "y": (0.05, 0.95),
    "label_x": (0.05, 0.95),
    "ratio": (0.25, 0.85),
    "spin": (-90, 90),
    "height": (0.15, 0.55),
    "cell": (0.008, 0.1),
    "turns": (0.1, 5),
    "blur": (0, 0.03),
    "dark": (0, 0.8),
    "gap": (0.03, 1),
    "overlap": (-0.5, 0.5),
    "pick": (0, 8),
    "lines_y": (0.05, 0.95),
    "right_y": (0.05, 0.95),
}
COLORS = {"color", "accent", "bg"}
ENUMS = {
    "grade": {"moody", "bw", "warm", "cool", "pop"},
    "font": {"bold", "serif"},
    "pos": {"above", "below"},
}
LAYOUT_LOOKS = {
    "spotlight": {"sparkle"},
    "cover-star": {"editorial"},
    "liquid-glass-graph": {"bento"},
    "glass-widgets": {"simple"},
    "comment-box": {"bar"},
    "timeline": {"red"},
}
IDENTIFIER = Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]
# The schema advertises actual names, while validators also accept documented aliases.
FX_NAMES = Literal[tuple(r["id"] for r in catalog())]


class CatalogParams(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    fx: FX_NAMES
    text: str = Field(default="", max_length=480)
    options: dict[str, str | float] = Field(default_factory=dict, max_length=40)
    media_ids: list[IDENTIFIER] = Field(default_factory=list, max_length=9)

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, data):
        if not isinstance(data, dict):
            return data
        data = dict(data)
        name = str(data.get("fx", "")).lower().lstrip("/")
        if name == "glitter":
            name = "glitter-spotlight"
        if name in LOOKS:
            name, look = LOOKS[name]
            data["options"] = dict(data.get("options") or {}) | {"look": look}
        data["fx"] = ALIASES.get(name, name)
        if isinstance(data.get("text"), str):
            data["text"] = (
                data["text"].replace("\n", "|")
                if data["fx"] in TEXT_LIST_FX
                else " ".join(data["text"].splitlines())
            )
        if any(type(v) is bool for v in (data.get("options") or {}).values()):
            raise ValueError("Effect options require numbers or text, not booleans.")
        return data

    @model_validator(mode="after")
    def valid_options(self):
        recipe = next(r for r in catalog() if r["id"] == self.fx)
        allowed = set(recipe["options"]) - {"images", "text"}
        for key, value in self.options.items():
            if key not in allowed:
                raise ValueError(f"{self.fx} does not support option {key}.")
            if key in NUMBERS:
                lo, hi = NUMBERS[key]
                try:
                    n = float(value)
                except (ValueError, TypeError):
                    raise ValueError(f"{key} must be numeric.") from None
                if not math.isfinite(n) or not lo <= n <= hi:
                    raise ValueError(f"{key} must be between {lo} and {hi}.")
                if key == "count" and self.fx != "profile-wall" and n > 32:
                    raise ValueError("Use at most 32 particles/cards.")
                if key in {"count", "pick"} and n != int(n):
                    raise ValueError(f"{key} must be an integer.")
                self.options[key] = n
            elif key in COLORS:
                if not re.fullmatch(r"#[a-fA-F0-9]{6}", str(value)):
                    raise ValueError("Use a six-digit hex color.")
            elif key in ENUMS and value not in ENUMS[key]:
                raise ValueError(f"Unsupported {key}.")
            elif key == "look" and value not in LAYOUT_LOOKS.get(self.fx, set()):
                raise ValueError("Unsupported named look.")
            elif not isinstance(value, str) or len(value) > 480:
                raise ValueError("Use bounded text options.")
            if isinstance(value, str) and (
                len(value.split("|")) > 12 or any(len(x) > 140 for x in value.split("|"))
            ):
                raise ValueError("Use at most 12 short items per text option.")
        if any(len(x) > 140 for x in self.text.split("|")) or len(self.text.split("|")) > 12:
            raise ValueError("Use at most 12 short text items.")
        for key in ("ticks",):
            if key in self.options:
                try:
                    values = [float(x) for x in str(self.options[key]).split("|")]
                except ValueError:
                    raise ValueError("Ticks must be numeric seconds joined with |.") from None
                if any(not math.isfinite(x) or not 0 <= x <= 300 for x in values):
                    raise ValueError("Invalid tick time.")
        if self.fx == "countdown-flip" and "from" in self.options:
            try:
                n = float(self.options["from"])
            except ValueError:
                raise ValueError("Countdown from must be an integer.") from None
            if not n.is_integer() or not 1 <= n <= 60:
                raise ValueError("Countdown from must be between 1 and 60.")
        if self.fx in {"liquid-glass-graph", "over-the-shoulder-zoom"}:
            if "to" not in self.options:
                raise ValueError(
                    "Graph effects require an explicit to value; never invent metrics."
                )
            for part in str(self.options["to"]).split("|"):
                if not re.fullmatch(r"-?\d+(?:\.\d+)?[KMB%]?", part, re.I):
                    raise ValueError("Use numeric graph values.")
            if self.fx == "over-the-shoulder-zoom" and len(str(self.options["to"]).split("|")) != 2:
                raise ValueError("Shoulder zoom requires two values joined with |.")
        if self.fx in {"liquid-glass-graph", "over-the-shoulder-zoom"}:
            for field in ("from", "to"):
                if field not in self.options:
                    continue
                for part in str(self.options[field]).split("|"):
                    if not re.fullmatch(r"-?\d+(?:\.\d+)?[KMB%]?", part, re.I):
                        raise ValueError("Use numeric graph values.")
                    n = float(part.rstrip("KkMmBb%"))
                    if not math.isfinite(n) or abs(n) > 1e12:
                        raise ValueError("Graph values are too large.")
                    if part.endswith("%") and not 0 <= n <= 100:
                        raise ValueError("Percentages must be between 0 and 100.")
        if self.options.get("look") == "bento" and any(
            k not in self.options for k in ("donut", "kpi", "bars")
        ):
            raise ValueError("Bento graphs require explicit donut, kpi and bars data.")
        if self.options.get("look") == "bento":
            for field in ("donut", "kpi", "bars"):
                raw = str(self.options[field]).split("::")[0]
                values = raw.split("|") if field == "bars" else [raw]
                for value in values:
                    if not re.fullmatch(r"-?\d+(?:\.\d+)?[KMB%]?", value, re.I):
                        raise ValueError("Use numeric bento values followed by ::label.")
                    n = float(value.rstrip("KkMmBb%"))
                    if not math.isfinite(n) or abs(n) > 1e12 or (field == "bars" and n < 0):
                        raise ValueError("Invalid bento chart value.")
                    if field == "donut" and (not value.endswith("%") or not 0 <= n <= 100):
                        raise ValueError("Donut values must be percentages between 0 and 100.")
        if self.fx == "over-the-shoulder-zoom" and self.text and len(self.text.split("|")) != 2:
            raise ValueError("Provide two shoulder-zoom labels separated by |.")
        if self.media_ids and not recipe.get("uses_media"):
            raise ValueError("This recipe does not use supporting media cards.")
        if len(set(self.media_ids)) != len(self.media_ids):
            raise ValueError("Do not repeat media asset IDs.")
        return self
