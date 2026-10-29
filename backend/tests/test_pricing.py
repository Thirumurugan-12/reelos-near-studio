import pytest

from reelos.pricing import estimate_cost


def test_spark_cache_and_reasoning_are_not_double_counted():
    usage = {
        "input_tokens": 1000000,
        "output_tokens": 100000,
        "input_tokens_details": {"cached_tokens": 200000},
        "output_tokens_details": {"reasoning_tokens": 50000},
    }
    assert estimate_cost("muse-spark-1.3", usage) == pytest.approx(1.455)


def test_sam_images_and_billed_video_frames():
    assert estimate_cost("sam-3.1", {"video_frames_processed": 200}) == 0.04
    assert estimate_cost("sam-3.1", {"images_processed": 1}) == 0.0025
    assert estimate_cost("sam-3.1", {"video_frames_processed": 12}) == 0.01


@pytest.mark.parametrize(
    "model,usage",
    [
        ("muse-spark-1.3", {}),
        ("sam-3.1", {}),
        ("other", {"input_tokens": 4, "output_tokens": 2}),
        ("muse-spark-1.3", {"input_tokens": -1, "output_tokens": 5}),
    ],
)
def test_missing_unknown_or_invalid_usage_is_unpriced_not_free(model, usage):
    assert estimate_cost(model, usage) is None
