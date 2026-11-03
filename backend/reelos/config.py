import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    data_dir: Path = Path("data")
    api_key: str = field(default="", repr=False)
    muse_model: str = "muse-spark-1.3"
    sam_model: str = "sam-3.1"
    budget_usd: float = 150
    reserve_usd: float = 1
    graphics_renderer: str = "hyperframes"

    @classmethod
    def load(cls):
        root = Path(__file__).resolve().parents[2]
        load_dotenv(root / ".env")
        data_dir = Path(os.getenv("REELOS_DATA_DIR", "data"))
        return cls(
            data_dir=data_dir if data_dir.is_absolute() else root / data_dir,
            api_key=os.getenv("MODEL_API_KEY", ""),
            muse_model=os.getenv("META_MUSE_MODEL", "muse-spark-1.3"),
            sam_model=os.getenv("META_SAM_MODEL", "sam-3.1"),
            budget_usd=min(150, max(0, float(os.getenv("REELOS_API_BUDGET_USD", "150")))),
            reserve_usd=max(0.1, float(os.getenv("REELOS_REQUEST_RESERVE_USD", "1"))),
            graphics_renderer=graphics_renderer(os.getenv("REELOS_GRAPHICS_RENDERER")),
        )


def graphics_renderer(value: str | None) -> str:
    value = (value or "hyperframes").strip().lower()
    if value not in {"hyperframes", "remotion"}:
        raise ValueError("REELOS_GRAPHICS_RENDERER must be 'hyperframes' or 'remotion'")
    return value
