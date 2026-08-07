"""The headmatter criteria each circuit reads, locked to a stored snapshot.

WHY THIS EXISTS. The criteria walk is shared between circuits, so a rule added
for one court silently moves another: tightening CA5's roster split dropped
CA3's panel from 49 files to 46, and it was two courts later before anyone
noticed. Field counts do not catch that — the count stayed plausible while the
content changed. Comparing the parse field by field does.

Each record is one FORMAT the court actually prints (see criteria_manifest.py),
not a random sample. A failure here means the parse changed; it does not by
itself mean the parse got worse. Read the diff:

  * intended improvement -> `uv run python tests/gen_criteria.py <court>`,
    then read what moved before committing it.
  * anything else -> a regression, in the court named by the failure.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import pytest

from centralia.registry import get_extractor
from tests.criteria_manifest import MANIFEST

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).parent / "fixtures" / "criteria.json"

CASES = [(court, stem) for court, stems in MANIFEST.items() for stem in stems]


def _asset(court: str, stem: str):
    hits = sorted(glob.glob(str(ROOT / "assets" / court / f"{stem}*.pdf")))
    return hits[0] if hits else None


@pytest.fixture(scope="session")
def snapshot() -> dict:
    if not FIXTURE.exists():
        pytest.skip(
            "no criteria snapshot; run: uv run python tests/gen_criteria.py"
        )
    return json.loads(FIXTURE.read_text())


@pytest.mark.parametrize(
    "court,stem", CASES, ids=[f"{c}/{s}" for c, s in CASES]
)
def test_criteria_unchanged(court, stem, snapshot):
    key = f"{court}/{stem}"
    if key not in snapshot:
        pytest.skip(f"{key} not in the snapshot")
    path = _asset(court, stem)
    if path is None:
        pytest.skip(f"no asset for {key}")

    actual = get_extractor(court).extract(path).criteria
    expected = snapshot[key]
    # Compare through JSON so tuples/lists and the stored form agree.
    actual = json.loads(json.dumps(actual, default=str, ensure_ascii=False))

    if actual == expected:
        return

    # Name the fields that moved rather than dumping two whole dicts — the
    # useful question is always "which field, and what did it become".
    lines = [f"{key}: parsed criteria differ from the snapshot"]
    for field in sorted(set(expected) | set(actual)):
        was, now = expected.get(field), actual.get(field)
        if was == now:
            continue
        lines.append(f"  {field}:")
        lines.append(f"    snapshot: {json.dumps(was, ensure_ascii=False)[:400]}")
        lines.append(f"    now:      {json.dumps(now, ensure_ascii=False)[:400]}")
    lines.append("")
    lines.append(
        "  If this change is intended: "
        f"uv run python tests/gen_criteria.py {court}"
    )
    pytest.fail("\n".join(lines), pytrace=False)


def test_manifest_assets_exist():
    """Every stem in the manifest resolves to exactly one PDF.

    A stem that stops matching (a renamed or removed asset) would otherwise
    turn into a silent skip, and the format it stood for would go uncovered
    without anything failing."""
    missing = [f"{c}/{s}" for c, s in CASES if _asset(c, s) is None]
    assert not missing, "manifest stems with no asset: " + ", ".join(missing)
