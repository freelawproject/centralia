"""Freeze the OLD system's output for one court. RUNS UNDER THE OLD REPO'S ENV.

Usage (from the old repo's directory, so `uv run` resolves its lockfile):

    uv run python /Users/Palin/Code/rewrite/harness/_freeze_old.py <court> <out.json>

This script must stay standalone: it imports the OLD `centralia` package (cwd
is the old repo), never the new one. It stores RAW section text — the new
repo's `audit.norm` is applied at compare time, so normalization changes never
require a re-freeze.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, ".")

from centralia.registry import get_extractor  # old repo's registry

_PARA_TAGS = {"p", "blockquote", "table"}


def harvest(x):
    """Yield every text string from the old model's heterogeneous shapes:
    plain strings, Blocks, sentinel dicts, caption columns, (tag, text)
    footnote paragraphs, nested lists."""
    if x is None:
        return
    if isinstance(x, str):
        if x and x not in ("__DIVIDER__", "__RULE__"):
            yield x
        return
    if isinstance(x, tuple) and len(x) == 2 and x[0] in _PARA_TAGS:
        yield from harvest(x[1])
        return
    if isinstance(x, (list, tuple)):
        for item in x:
            yield from harvest(item)
        return
    if isinstance(x, dict):
        for key in ("html", "h", "l", "c", "r", "text"):
            v = x.get(key)
            if isinstance(v, str) and v:
                yield v
        for key in ("left", "right", "rows"):
            if x.get(key):
                yield from harvest(x[key])
        return
    # dataclass-ish: Block has .text/.payload; Footnote has .label/.paragraphs
    text = getattr(x, "text", None)
    if isinstance(text, str):
        if text:
            yield text
        payload = getattr(x, "payload", None) or {}
        yield from harvest(payload.get("rows"))
        return
    paragraphs = getattr(x, "paragraphs", None)
    if paragraphs is not None:
        yield from harvest(paragraphs)
        return


def crit_texts(d):
    if isinstance(d, dict):
        for v in d.values():
            yield from crit_texts(v)
    elif isinstance(d, (list, tuple)):
        for v in d:
            yield from crit_texts(v)
    elif isinstance(d, str) and d:
        yield d


def freeze_doc(doc):
    ops = []
    for op in doc.opinions:
        blocks_text = list(harvest(op.blocks))
        ops.append({
            "type": op.type,
            "author": op.author,
            "words": sum(len(t.split()) for t in blocks_text),
            "blocks_text": blocks_text,
            "footnote_labels": [fn.label for fn in op.footnotes],
            "footnotes_text": list(harvest([fn.paragraphs for fn in op.footnotes])),
            "caption_text": list(harvest(op.caption)),
            "signature_text": list(harvest(op.signature)),
        })
    return {
        "doc_type": doc.doc_type,
        "n_pages": doc.n_pages,
        "non_digital": bool(getattr(doc, "non_digital", False)),
        "sections": {
            "headmatter": list(harvest(doc.summary)),
            "headnotes": list(harvest(doc.headnotes)),
            "syllabus": list(harvest(doc.syllabus)),
            "attorneys": list(harvest(doc.attorneys)),
            "trailer": list(harvest(doc.trailer)),
            "signature": list(harvest(doc.signature)),
            "dropped": list(harvest(doc.dropped)),
            "criteria": list(crit_texts(doc.criteria)),
        },
        "headmatter_footnote_labels": [fn.label for fn in doc.headmatter_footnotes],
        "headmatter_footnotes_text": list(
            harvest([fn.paragraphs for fn in doc.headmatter_footnotes])
        ),
        "opinions": ops,
        "residual": [
            {"page": r.get("page"), "kind": r.get("kind"), "text": r.get("text")}
            for r in (doc.residual or [])
            if isinstance(r, dict)
        ],
        "warnings": list(doc.warnings or []),
    }


def main() -> int:
    court, out_path = sys.argv[1], Path(sys.argv[2])
    extractor = get_extractor(court)
    pdfs = sorted(Path("assets", court).glob("*.pdf"))
    records, errors = {}, {}
    for pdf in pdfs:
        try:
            records[pdf.stem] = freeze_doc(extractor.extract(str(pdf)))
        except Exception:  # noqa: BLE001 — a crash is data here, not a stop
            errors[pdf.stem] = traceback.format_exc(limit=3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({"court": court, "files": records, "errors": errors}, f)
    print(f"{court}: froze {len(records)} files, {len(errors)} errors -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
