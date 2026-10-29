"""Local estimates from reported usage, separate from conservative reservations."""

PRICING_AS_OF = "2026-10-29"
PRICING_SOURCE = "https://dev.meta.ai/docs/pricing-rate-limits"


def estimate_cost(model: str, usage: dict) -> float | None:
    def count(key, data=usage):
        if not isinstance(data, dict):
            return None
        value = data.get(key)
        return value if type(value) is int and value >= 0 else None

    if model in {"muse-spark-1.1", "muse-spark-1.2", "muse-spark-1.3"}:
        inputs, outputs = count("input_tokens"), count("output_tokens")
        details = usage.get("input_tokens_details", {})
        cached = count("cached_tokens", details)
        if inputs is None or outputs is None:
            return None
        if not isinstance(details, dict) or ("cached_tokens" in details and cached is None):
            return None
        cached = cached or 0
        if cached > inputs:
            return None
        # Reported output_tokens already includes reasoning tokens.
        return ((inputs - cached) * 1.25 + cached * 0.15 + outputs * 4.25) / 1_000_000
    if model == "sam-3.1":
        images, frames = count("images_processed"), count("video_frames_processed")
        if any(
            k in usage and count(k) is None for k in ("images_processed", "video_frames_processed")
        ):
            return None
        if images is None and frames is None:
            return None
        billed_frames = max(50, frames) if frames else 0
        return (images or 0) * 2.5 / 1000 + billed_frames * 0.2 / 1000
    return None
