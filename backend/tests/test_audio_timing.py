import numpy as np
import pytest

from scripts.check_audio_timing import window_delay


@pytest.mark.parametrize("delay", [-1000, 0, 640])
def test_recovers_known_delay_without_confusing_source_trim(delay):
    rate = 8000
    source = np.random.default_rng(317).normal(size=rate * 5)
    # The output starts one second into the source, then shifts by the tested delay.
    output = np.roll(source[rate:], delay)
    result = window_delay(source, output, rate, 1, 1, source_in=1)
    assert result["lag_ms"] == pytest.approx(delay / rate * 1000, abs=0.13)
    assert result["correlation"] == pytest.approx(1, abs=1e-10)


def test_silence_is_inconclusive_instead_of_proving_alignment():
    with pytest.raises(ValueError, match="silence"):
        window_delay(np.zeros(32000), np.zeros(32000), 8000, 1, 1)


def test_unrelated_audio_does_not_look_like_a_good_match():
    rng = np.random.default_rng(721)
    result = window_delay(rng.normal(size=32000), rng.normal(size=32000), 8000, 1, 1)
    assert abs(result["correlation"]) < 0.1


def test_out_of_bounds_window_is_not_silently_shortened():
    with pytest.raises(ValueError, match="outside"):
        window_delay(np.ones(8000), np.ones(8000), 8000, 0, 1)
