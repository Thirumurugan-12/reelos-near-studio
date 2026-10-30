import subprocess
import sys


def test_oversized_unbroken_title_finishes_with_a_clear_error():
    # Use a process timeout so a font-fitting regression cannot hang the test worker.
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
from reelos.media import text_layer
from reelos.timeline import TextStyle
try:
    text_layer((90, 160), TextStyle(text='W'*120), 1, 0, 3)
except ValueError as exc:
    print(str(exc))
else:
    raise AssertionError('Unrenderable text should be rejected')
""",
        ],
        capture_output=True,
        text=True,
        timeout=3,
    )
    assert result.returncode == 0, result.stderr
    assert "shorter" in result.stdout
