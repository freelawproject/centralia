"""Ground-truth loaders. Everything is read from the OLD repo in place.

Two truth sets exist today:
- footnote labels: 2,124 hand-verified entries keyed "court/stem" -> [labels]
  (old repo: output/notes/_footnotes_truth.json)
- headmatter criteria: one snapshot per printed FORMAT
  (this repo: tests/fixtures/criteria.json + tests/criteria_manifest.py,
  ported from the old repo; stems match as PREFIXES so renames don't break)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import CORPUS_ROOT, FOOTNOTE_TRUTH  # noqa: E402

FIXTURES = REPO_ROOT / "tests" / "fixtures"


def footnote_truth() -> dict[str, list[str]]:
    """'court/stem' -> expected footnote labels (whole document, in order)."""
    with open(FOOTNOTE_TRUTH) as f:
        return json.load(f)


def footnote_truth_for(court_id: str) -> dict[str, list[str]]:
    prefix = f"{court_id}/"
    return {k: v for k, v in footnote_truth().items() if k.startswith(prefix)}


def criteria_fixtures() -> dict[str, dict]:
    """'court/stem-prefix' -> expected criteria snapshot."""
    with open(FIXTURES / "criteria.json") as f:
        return json.load(f)


def criteria_manifest() -> dict[str, list[str]]:
    """court -> [stem prefixes]; one entry per printed format the court uses."""
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    from criteria_manifest import MANIFEST  # noqa: PLC0415
    return MANIFEST


def resolve_manifest_stem(court_id: str, prefix: str) -> Path | None:
    """A manifest stem is a prefix of a real corpus filename."""
    d = CORPUS_ROOT / court_id
    if not d.is_dir():
        return None
    hits = sorted(p for p in d.glob("*.pdf") if p.stem.startswith(prefix))
    return hits[0] if hits else None
