import pytest

from reelos.store import Store


def test_budget_reservation_is_durable_and_fails_closed(tmp_path):
    store = Store(tmp_path)
    call = store.reserve("muse", 1, 1.5)
    assert Store(tmp_path).budget()["reserved_usd"] == 1
    with pytest.raises(ValueError, match="budget"):
        store.reserve("sam", 1, 1.5)
    store.finish_call(call, "completed", {"input_tokens": 3}, 0.4)
    # Reservations stay charged until actual spend is reconciled; success isn't free.
    assert store.budget()["reserved_usd"] == 1


def test_records_survive_reopen_and_enforce_project_scope(tmp_path):
    store = Store(tmp_path)
    store.put("asset", "a", {"project_id": "p1", "duration": 20})
    assert Store(tmp_path).get("asset", "a")["duration"] == 20
    with pytest.raises(KeyError):
        store.get("asset", "a", project_id="p2")


def test_usage_estimates_keep_unpriced_calls_and_reservations_separate(tmp_path):
    store = Store(tmp_path)
    known = store.reserve("muse-spark-1.3", 1, 5)
    store.finish_call(known, "incomplete", {"input_tokens": 1000, "output_tokens": 200}, 0.4)
    unknown = store.reserve("sam-3.1", 1, 5)
    store.finish_call(unknown, "failed_or_unknown", {}, 2)
    report = Store(tmp_path).budget()
    assert report["estimated_known_usd"] == pytest.approx(0.0021)
    assert report["unpriced_calls"] == 1
    assert report["reserved_usd"] == 2
    assert report["calls"][0]["estimated_usd"] is None
