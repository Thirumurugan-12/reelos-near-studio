"""Rebuild metadata from the pinned vendor renderer without executing it."""

import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "reelos"
t = ast.parse((root / "vendor/claude_effects.py").read_text())
funcs = {n.name: n for n in t.body if isinstance(n, ast.FunctionDef)}


def keys(name, seen=None):
    seen = set() if seen is None else seen
    if name in seen:
        return set()
    seen.add(name)
    out = set()
    aliases = {
        n.id
        for a in ast.walk(funcs[name])
        if isinstance(a, ast.Assign) and isinstance(a.value, ast.Attribute) and a.value.attr == "o"
        for n in a.targets
        if isinstance(n, ast.Name)
    }

    def opts(n):
        return (isinstance(n, ast.Attribute) and n.attr == "o") or (
            isinstance(n, ast.Name) and n.id in aliases
        )

    for n in ast.walk(funcs[name]):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get"
            and opts(n.func.value)
            and n.args
            and isinstance(n.args[0], ast.Constant)
        ):
            out.add(n.args[0].value)
        if isinstance(n, ast.Subscript) and opts(n.value) and isinstance(n.slice, ast.Constant):
            out.add(n.slice.value)
        if isinstance(n, ast.Name) and n.id in funcs:
            out |= keys(n.id, seen)
    return out


rows = []
for n in funcs.values():
    for d in n.decorator_list:
        if isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "effect":
            name, desc = [a.value for a in d.args]
            rows.append(
                dict(
                    id=name,
                    label=name.replace("-", " ").title(),
                    description=desc.replace("Claude", "ReelOS"),
                    options=sorted(keys(n.name)),
                    uses_media=name
                    in {
                        "noise",
                        "orbit",
                        "carousel-spin",
                        "place-in-grid",
                        "check-pills",
                        "profile-wall",
                        "phone-fan",
                        "broll-split",
                        "timeline",
                    },
                )
            )
assert len(rows) == 45
order = json.loads((root / "catalog_order.json").read_text())
rows.sort(key=lambda row: order.index(row["id"]))
(root / "effect_catalog.json").write_text(json.dumps(rows, indent=2) + "\n")
