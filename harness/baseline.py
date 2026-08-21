"""Freeze old-system outputs, lazily, one court at a time (disk is tight).

The freeze runs `_freeze_old.py` under the OLD repo's uv environment and
stores one JSON per court under baseline/. After a court is frozen, A/B
comparison never touches old code again.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import BASELINE_DIR, OLD_REPO  # noqa: E402

_FREEZER = Path(__file__).resolve().parent / "_freeze_old.py"


def baseline_path(court_id: str) -> Path:
    return BASELINE_DIR / f"{court_id}.json"


def freeze(court_id: str, force: bool = False) -> Path:
    out = baseline_path(court_id)
    if out.exists() and not force:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["uv", "run", "python", str(_FREEZER), court_id, str(out)],
        cwd=OLD_REPO, check=True,
    )
    return out


def load(court_id: str) -> dict:
    with open(baseline_path(court_id)) as f:
        return json.load(f)
