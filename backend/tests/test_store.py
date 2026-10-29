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
