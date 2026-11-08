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
    broll_art: str = "muse-image"
    near_contract_id: str = ""

    @classmethod
    def load(cls):
        root = Path(__file__).resolve().parents[2]
        load_dotenv(root / ".env")
        data_dir = Path(os.getenv("REELOS_DATA_DIR", "data"))
        return cls(
            data_dir=data_dir if data_dir.is_absolute() else root / data_dir,
            near_contract_id=os.getenv("REELOS_NEAR_CONTRACT_ID", "").strip(),
            api_key=os.getenv("MODEL_API_KEY", ""),
            muse_model=os.getenv("META_MUSE_MODEL", "muse-spark-1.3"),
            sam_model=os.getenv("META_SAM_MODEL", "sam-3.1"),
            budget_usd=min(150, max(0, float(os.getenv("REELOS_API_BUDGET_USD", "150")))),
            reserve_usd=max(0.1, float(os.getenv("REELOS_REQUEST_RESERVE_USD", "1"))),
            graphics_renderer=graphics_renderer(os.getenv("REELOS_GRAPHICS_RENDERER")),
            broll_art=broll_art(os.getenv("REELOS_BROLL_ART")),
        )


def graphics_renderer(value: str | None) -> str:
    value = (value or "hyperframes").strip().lower()
    if value not in {"hyperframes", "remotion"}:
        raise ValueError("REELOS_GRAPHICS_RENDERER must be 'hyperframes' or 'remotion'")
    return value


def broll_art(value: str | None) -> str:
    value = (value or "muse-image").strip().lower()
    if value not in {"muse-image", "template"}:
        raise ValueError("REELOS_BROLL_ART must be 'muse-image' or 'template'")
    return value
