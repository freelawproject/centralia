"""Regenerate the headmatter-criteria snapshot.

    uv run python tests/gen_criteria.py            # every court in the manifest
    uv run python tests/gen_criteria.py ca4 ca9    # just these

Run this ONLY when a change to the parse is intended, and read the diff before
committing it: the whole point of the snapshot is that an unintended change
shows up as a failing test rather than as output nobody looked at.
"""

from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Running this file puts tests/ at the head of sys.path, where tests/inspect.py
# shadows the standard library's `inspect` — which pdfminer imports, so the
# whole extractor fails to load. Take this directory back off the path.
_HERE = str(Path(__file__).resolve().parent)
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != _HERE]
sys.path.insert(0, str(ROOT))

from centralia.registry import get_extractor          # noqa: E402
from tests.criteria_manifest import MANIFEST          # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "criteria.json"


def resolve(court: str, stem: str):
    """The one PDF under assets/<court>/ whose name starts with ``stem``."""
    hits = sorted(glob.glob(str(ROOT / "assets" / court / f"{stem}*.pdf")))
    if not hits:
        return None
    return hits[0]


def build(courts) -> dict:
    out = {}
    for court in courts:
        for stem in MANIFEST[court]:
            path = resolve(court, stem)
            if path is None:
                print(f"  !! no asset for {court}/{stem}", file=sys.stderr)
                continue
            crit = get_extractor(court).extract(path).criteria
            out[f"{court}/{stem}"] = crit
            print(f"  {court}/{stem}: {len(crit)} fields")
    return out


def main() -> int:
    courts = sys.argv[1:] or list(MANIFEST)
    unknown = [c for c in courts if c not in MANIFEST]
    if unknown:
        print(f"not in the manifest: {', '.join(unknown)}", file=sys.stderr)
        return 2
    stored = {}
    if FIXTURE.exists():
        stored = json.loads(FIXTURE.read_text())
    stored.update(build(courts))
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(
        json.dumps(stored, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    )
    print(f"wrote {len(stored)} records -> {FIXTURE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
