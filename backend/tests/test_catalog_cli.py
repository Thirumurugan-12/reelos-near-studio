import json
import sys
from unittest.mock import patch

import httpx

from reelos.cli import main


def test_cli_applies_parameters_and_supporting_media(tmp_path, capsys):
    options = tmp_path / "options.json"
    options.write_text(json.dumps({"count": 5, "size": 0.2}))
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"job_id": "job"})

    client = httpx.Client(base_url="http://localhost/api/", transport=httpx.MockTransport(handle))
    with (
        patch("reelos.cli.httpx.Client", return_value=client),
        patch.object(
            sys,
            "argv",
            [
                "reelos",
                "apply",
                "project",
                "version",
                "orbit",
                "--start",
                "1",
                "--end",
                "4",
                "--text",
                "Story",
                "--options-file",
                str(options),
                "--media",
                "a" * 32,
            ],
        ),
    ):
        main()
    body = json.loads(requests[0].content)
    assert requests[0].url.path == "/api/projects/project/effects"
    assert body == {
        "version_id": "version",
        "start": 1,
        "end": 4,
        "params": {
            "fx": "orbit",
            "text": "Story",
            "options": {"count": 5, "size": 0.2},
            "media_ids": ["a" * 32],
        },
    }
    assert json.loads(capsys.readouterr().out)["job_id"] == "job"


def test_cli_framing_uses_the_shared_version_operation(capsys):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(202, json={"id": "queued", "version_id": "child"})

    client = httpx.Client(base_url="http://localhost/api/", transport=httpx.MockTransport(handle))
    with (
        patch("reelos.cli.httpx.Client", return_value=client),
        patch.object(
            sys,
            "argv",
            ["reelos", "frame", "project", "version", "--scale", ".82", "--offset-y", ".16"],
        ),
    ):
        main()
    assert len(requests) == 1
    assert requests[0].url.path == "/api/projects/project/versions/version/framing"
    assert json.loads(requests[0].content) == {"scale": 0.82, "offset_y": 0.16}
    assert json.loads(capsys.readouterr().out)["version_id"] == "child"
