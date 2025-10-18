import subprocess
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> List[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [REPO_ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]


def test_tracked_text_files_use_lf_endings() -> None:
    offenders: List[str] = []

    for path in _tracked_files():
        if not path.exists():
            continue

        data = path.read_bytes()
        if b"\0" in data:
            continue  # binary file

        if b"\r\n" in data:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, f"Files with CRLF line endings: {offenders}"
