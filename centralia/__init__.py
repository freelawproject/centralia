"""centralia — court PDF opinion extractor: PDF + court id -> typed Document.

    from centralia import read

    r = read("opinion.pdf", court_id="nmariana")   # path, bytes, or file object
    r["status"]      # valid | review | scanned | failed
    r["cluster"]     # the case: citation, docket, dates, panel, parties …
    r["opinions"]    # one entry per writing, each with its author and its html
    r["diagnostics"] # page facts and what went unplaced — reported, not judged
    r["html"]        # the document's text, no review furniture
    r["review_html"] # the reviewer's page: criteria box, Removed panel, tints
    r["casebody"]    # Harvard casebody XML

Lower-level, for callers that want the objects:

    from centralia import extract, render_html, render_opinion
    result = extract(pdf_path, court_id="mont")
    result.document   # typed Document
    result.trace      # per-decision evidence chains
    result.status
"""

from __future__ import annotations

import dataclasses as _dc
import os as _os
import tempfile as _tempfile
from typing import Any

from .dates import all_iso, to_iso
from .model import Criteria, Document, Meta, Opinion
from .pipeline import ExtractionResult, extract
from .render import (opinion_text, render_body, render_casebody, render_html,
                     render_opinion)

__all__ = [
    "read", "extract", "ExtractionResult",
    "Document", "Criteria", "Meta", "Opinion",
    "render_html", "render_body", "render_opinion", "render_casebody",
    "opinion_text", "to_iso", "all_iso", "__version__",
]

__version__ = "2.0.0a0"


def _as_path(src) -> tuple[str, bool]:
    """(path, is_temp). Bytes and file objects are spilled to a temp file.

    pdfplumber can read a stream, but the pipeline threads a PATH through for
    provenance (`Meta.source_path`) and for the stapled-document split, so
    normalising here keeps one code path in the engine instead of two.
    """
    if isinstance(src, (str, _os.PathLike)):
        return str(src), False
    data = src.read() if hasattr(src, "read") else src
    if isinstance(data, str):
        raise TypeError("read(): expected bytes or a binary file object, got str")
    fd, path = _tempfile.mkstemp(suffix=".pdf", prefix="centralia-")
    with _os.fdopen(fd, "wb") as fh:
        fh.write(data)
    return path, True


def _plain(value: Any) -> Any:
    """A JSON-safe copy: enums to their value, everything else as it stands."""
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if hasattr(value, "value") and type(value).__mro__[1].__name__ == "Enum":
        return value.value
    if _dc.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name))
                for f in _dc.fields(value)}
    return value


def _cluster(doc: Document) -> dict:
    """The case-level facts, named as an ingest names them.

    DATES COME BOTH WAYS: as the court printed them, and ISO where that can be
    read without guessing (`centralia.dates`). `date_argued`/`date_submitted`
    fall back to `submitted`, which is still the field 63 court files write —
    the split is a separate migration, and until it lands `submitted_kind`
    says only that the distinction is not yet known for this record.
    """
    c = doc.criteria
    argued = c.date_argued or None
    submitted = c.date_submitted or None
    if argued is None and submitted is None and c.submitted:
        submitted = c.submitted           # unsplit: see the note above
    return {
        "court_id": doc.meta.court_id,
        "court": c.court or doc.meta.court_label or None,
        "case_name": c.case_name,
        "case_name_short": c.short_case_name,
        "citation": c.citation,
        "docket_number": c.docket_number,
        "other_dockets": list(c.other_dockets),
        "date_filed": c.decision_date,
        "date_filed_iso": to_iso(c.decision_date),
        "date_argued": argued,
        "date_argued_iso": to_iso(argued),
        "date_submitted": submitted,
        "date_submitted_iso": to_iso(submitted),
        "date_reargued": c.date_reargued,
        "date_reargued_iso": to_iso(c.date_reargued),
        "submitted_split": bool(c.date_argued or c.date_submitted),
        "precedential_status": c.publication_status,
        "judges": c.judges,
        "panel": list(c.panel),
        "author": c.author,
        "attorneys": c.attorneys,
        "parties": list(c.parties),
        "caption": list(c.caption),
        "disposition": c.disposition,
        "history": c.history,
        "lower_court": c.lower_court,
        "lower_court_docket": list(c.lower_court_docket),
        "lower_court_judge": c.lower_court_judge,
        "title": c.title,
        "headmatter_style": c.headmatter_style,
        "n_pages": doc.meta.n_pages,
        "doc_type": _plain(doc.meta.doc_type),
    }


def _opinions(doc: Document) -> list[dict]:
    out = []
    for op in doc.opinions:
        pages = sorted({p for b in (*op.blocks, *op.signature)
                        for p in ([getattr(b, "prov", None).page]
                                  if getattr(b, "prov", None) else [])})
        out.append({
            "type": op.type,
            "author": op.author or None,          # as the page prints it
            "author_name": op.author_name or None,   # parsed
            "author_title": op.author_title or None,
            "pages": pages,
            "n_blocks": len(op.blocks),
            "html": render_opinion(op),
            "text": opinion_text(op),
            "footnotes": [{"label": f.label,
                           "text": opinion_text(Opinion(type="", blocks=f.blocks))}
                          for f in op.footnotes],
        })
    return out


def _diagnostics(doc: Document, status: str) -> dict:
    """Facts, not verdicts. Nothing here changes `status`; the caller decides
    (the user, 2026-08-21)."""
    mt = doc.meta
    removed: dict = {}
    for d in doc.dropped:
        removed[d.kind] = removed.get(d.kind, 0) + 1
    hm_rows = [i for i in doc.headmatter if hasattr(i, "role")]
    return {
        "status": status,
        "source_kind": mt.source_kind,
        "n_pages": mt.n_pages,
        "scan_pages": list(mt.scan_pages),
        "text_missing_pages": list(mt.text_missing_pages),
        "cid_pages": list(mt.cid_pages),
        "residual": [{"kind": r.kind, "page": r.prov.page, "text": r.text}
                     for r in doc.residual],
        "residual_content": sum(1 for r in doc.residual if r.kind == "content"),
        "removed_counts": removed,
        "opinion_count": len(doc.opinions),
        "unbylined_opinions": sum(1 for op in doc.opinions
                                  if not (op.author or op.author_name)),
        "footnote_count": sum(len(op.footnotes) for op in doc.opinions)
        + len(doc.headmatter_footnotes),
        "headmatter_rows": len(hm_rows),
        "headmatter_untinted": sum(1 for i in hm_rows if not i.role),
        "dates_unparsed": [k for k, v in (
            ("date_filed", doc.criteria.decision_date),
            ("date_submitted", doc.criteria.date_submitted
             or doc.criteria.submitted),
            ("date_argued", doc.criteria.date_argued),
        ) if v and not to_iso(v)],
        "warnings": list(doc.warnings),
    }


def read(src, court_id: str, *, include_document: bool = False) -> dict:
    """Read one PDF. ``src`` is a path, bytes, or a binary file object."""
    path, is_temp = _as_path(src)
    try:
        result = extract(path, court_id)
    finally:
        if is_temp:
            try:
                _os.unlink(path)
            except OSError:
                pass
    doc = result.document
    out = {
        "status": result.status,
        "court_id": court_id,
        "versions": dict(result.versions),
        "cluster": _cluster(doc),
        "opinions": _opinions(doc),
        "headmatter": [{"role": getattr(i, "role", "") or None,
                        "text": getattr(i, "text", ""),
                        "page": i.prov.page}
                       for i in doc.headmatter
                       if getattr(i, "text", "")],
        "sections": {name: [getattr(b, "text", "") for b in getattr(doc, name)]
                     for name in ("syllabus", "headnotes", "summary",
                                  "attorneys", "signature", "trailer")
                     if getattr(doc, name)},
        "removed": [{"kind": d.kind, "page": d.prov.page, "text": d.text}
                    for d in doc.dropped],
        "diagnostics": _diagnostics(doc, result.status),
        "html": render_body(doc),
        "review_html": render_html(doc),
        "casebody": render_casebody(doc),
        "warnings": list(doc.warnings),
    }
    if include_document:
        out["document"] = doc
    return out
