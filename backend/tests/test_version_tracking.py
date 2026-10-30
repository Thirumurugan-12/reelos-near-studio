from reelos.config import Settings
from reelos.service import Editor
from reelos.timeline import EditPlan


def test_manual_child_keeps_tracking_only_for_the_same_source(tmp_path):
    editor = Editor(Settings(data_dir=tmp_path))
    pid, aid, other = "a" * 32, "b" * 32, "c" * 32
    for asset in (aid, other):
        editor.store.put("asset", asset, {"project_id": pid, "duration": 65})
    plan = EditPlan(asset_id=aid, source_out=65, output_mode="full")
    parent = editor.version(
        pid, plan, track_key="real-source-track", observations=[{"text": "Source evidence"}]
    )
    child = editor.version(pid, plan, parent=parent["id"])
    assert child["track_key"] == parent["track_key"]
    assert child["observations"] == parent["observations"]
    different_source = editor.version(
        pid, plan.model_copy(update={"asset_id": other}), parent=parent["id"]
    )
    assert different_source["track_key"] is None
    assert different_source["observations"] == []
