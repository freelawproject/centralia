"""Build ``output/notes.js`` from the per-court markdown notes.

Per-court review notes live as markdown files in ``output/notes/<court>.md`` —
the canonical, repo-tracked store (so they can be read before reprocessing a
court). The review viewer can't read the filesystem (it runs from file://), so
this collects the markdown into a single ``notes.js`` the viewer loads:

    window.NOTES = {"ariz": "# ariz ...", ...};

The viewer shows ``NOTES[court]`` as the starting text, lets you edit it (kept
in localStorage), and exports a ``notes.json`` you can hand back to merge into
the markdown files.

Run:  uv run python -m restatement.notes_build
"""

from __future__ import annotations

import json
from pathlib import Path

NOTES_DIR = Path("output/notes")
OUT = Path("output/notes.js")


def build() -> int:
    notes: dict[str, str] = {}
    if NOTES_DIR.is_dir():
        for md in sorted(NOTES_DIR.glob("*.md")):
            notes[md.stem] = md.read_text(encoding="utf-8")
    OUT.write_text(
        "window.NOTES = " + json.dumps(notes, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    return len(notes)


def merge(notes_json: str) -> int:
    """Merge an exported ``notes.json`` ({court: text}) back into the markdown
    files. Returns the number of courts written."""
    data = json.loads(Path(notes_json).read_text(encoding="utf-8"))
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    for court, text in data.items():
        (NOTES_DIR / f"{court}.md").write_text(text, encoding="utf-8")
    return len(data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        n = merge(sys.argv[1])
        print(f"merged {n} courts from {sys.argv[1]} into {NOTES_DIR}/")
    n = build()
    print(f"wrote {OUT} ({n} courts)")
