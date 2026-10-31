import json
from types import SimpleNamespace

from reelos.planner import create_plan, revise_plan


def test_muse_contract_exposes_all_recipes_and_revises_only_selected_option():
    prompts = []
    plan_data = {
        "asset_id": "a" * 32,
        "source_out": 20,
        "effects": [
            {
                "id": "cards",
                "type": "catalog_effect",
                "subject_id": "0",
                "start": 1,
                "end": 4,
                "params": {
                    "fx": "orbit",
                    "options": {"count": 5, "size": 0.2},
                    "media_ids": ["b" * 32],
                },
            }
        ],
    }
    replies = [
        {"plan": plan_data, "observations": []},
        {
            "summary": "Slower orbit",
            "changes": [
                {"effect_id": "cards", "field": "options", "value": {"speed": 0.5}},
            ],
        },
    ]

    def response(model, content, **kwargs):
        prompts.append(json.loads(content[0]["text"]))
        return {
            "output": [{"content": [{"type": "output_text", "text": json.dumps(replies.pop(0))}]}]
        }

    client = SimpleNamespace(settings=SimpleNamespace(muse_model="fixture"), response=response)
    assets = [{"id": "b" * 32, "name": "Story illustration", "kind": "image", "duration": 0}]
    plan, _ = create_plan(
        client,
        {"id": "a" * 32, "duration": 20},
        "file",
        "0",
        "Orbit my illustration",
        supporting_assets=assets,
    )
    child, _ = revise_plan(client, plan, "Slower orbit", supporting_assets=assets)
    for prompt in prompts:
        assert len(prompt["effect_catalog"]) == 45
        assert prompt["supporting_assets"] == assets
        assert all("images" not in row["options"] for row in prompt["effect_catalog"])
    assert child.effects[0].params.options == {"count": 5, "size": 0.2, "speed": 0.5}
    assert child.effects[0].params.media_ids == ["b" * 32]
    assert plan.effects[0].params.options == {"count": 5, "size": 0.2}
