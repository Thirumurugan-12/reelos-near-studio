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
