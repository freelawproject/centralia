"""Per-document expectation marks — lightweight, unit-test-style assertions
about what a PDF *should* extract to, checked against what it actually did.

For each document we compute an extraction **profile** (doc_type, # opinions,
# syllabus rows, # headmatter rows, # dropped/notice, # footnotes, # pages) from
the DB, and store an **expected** mark (the same fields, whichever the reviewer
fills in) plus a free-text note. ``compare`` lines them up so the UI can show a
✓/✗ per field. Marks live in output/notes/_docmarks.json keyed by 'court/stem',
so both the web UI and the CLI (manage.py markdoc) write the same store.
"""

from __future__ import annotations

import json

from django.conf import settings

from .models import Document, Footnote

_PATH = settings.BASE_DIR / "output" / "notes" / "_docmarks.json"

# Fields a reviewer can assert; each compared int-first, then string.
FIELDS = ("doc_type", "opinions", "syllabus", "headmatter", "dropped", "footnotes", "pages")


def _key(court_id: str, stem: str) -> str:
    return f"{court_id}/{stem}"


def load() -> dict:
    if _PATH.exists():
        try:
            return json.loads(_PATH.read_text())
        except Exception:
            return {}
    return {}


def save(store: dict) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(store, indent=1, sort_keys=True))


def get_mark(court_id: str, stem: str) -> dict:
    return load().get(_key(court_id, stem), {})


def set_mark(court_id, stem, expected: dict, note: str = "", by: str = "user") -> None:
    store = load()
    clean = {k: v for k, v in (expected or {}).items() if str(v).strip() != ""}
    entry = {"by": by}
    if clean:
        entry["expected"] = clean
    if (note or "").strip():
        entry["note"] = note.strip()
    if len(entry) == 1:  # only 'by' — nothing to keep
        store.pop(_key(court_id, stem), None)
    else:
        store[_key(court_id, stem)] = entry
    save(store)


def profile(doc: Document) -> dict:
    """The actual extraction profile of a Document."""
    ops = list(doc.opinions.all())
    return {
        "doc_type": doc.doc_type,
        "opinions": len(ops),
        "syllabus": len(doc.syllabus or []),
        "headmatter": len(doc.summary or []),
        "dropped": len(doc.dropped or []),
        "footnotes": Footnote.objects.filter(document=doc).count(),
        "pages": doc.n_pages,
        "authors": [f"{o.type}: {o.author}" for o in ops],
    }


def compare(expected: dict, actual: dict) -> list:
    """[(field, expected, actual, ok)] for every asserted field."""
    rows = []
    for f in FIELDS:
        if f not in (expected or {}) or str(expected[f]).strip() == "":
            continue
        exp, act = expected[f], actual.get(f)
        try:
            ok = int(exp) == int(act)
        except (TypeError, ValueError):
            ok = str(exp).strip().lower() == str(act).strip().lower()
        rows.append((f, exp, act, ok))
    return rows