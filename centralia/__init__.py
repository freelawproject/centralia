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
import enum as _enum
import os as _os
import tempfile as _tempfile
from typing import Any

from .courts import PROFILES
from .dates import all_iso, to_iso
from .model import Criteria, Document, Meta, Opinion
from .pipeline import ExtractionResult, extract
from .released import HELD_BACK, RELEASED
from .render import (opinion_text, render_body, render_casebody,
                     render_headmatter, render_html, render_opinion)
from .render.facsimile import render_hm_items

__all__ = [
    "read", "extract", "ExtractionResult", "released_courts",
    "UnknownCourt", "CourtNotReleased",
    "Document", "Criteria", "Meta", "Opinion",
    "render_html", "render_body", "render_opinion", "render_casebody",
    "render_headmatter", "opinion_text", "to_iso", "all_iso", "__version__",
]

__version__ = "0.0.2"


class UnknownCourt(KeyError):
    """No such court id. Raised rather than falling back, because an
    unregistered id silently gets core's GENERIC reader — the record still
    extracts and still says `status: valid`, it is just read worse. A typo
    should not look like a thin court."""


class CourtNotReleased(RuntimeError):
    """The court is still being worked on. See `centralia/released.py`."""


def released_courts() -> frozenset[str]:
    """The court ids the public API will read. See `centralia/released.py`."""
    return RELEASED


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
    # isinstance, NOT a walk of __mro__: DocType is a StrEnum, so its second
    # base is StrEnum and a name check for "Enum" missed it entirely. And
    # because a StrEnum IS a str, json.dumps serialised it happily — so the
    # payload looked fine while the Python value handed to a caller was still
    # an enum (the user, 2026-08-21). The JSON test could not see that; the
    # type test below can.
    if isinstance(value, _enum.Enum):
        return value.value
    if _dc.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name))
                for f in _dc.fields(value)}
    return value


def _bare(text: str) -> str:
    """A row's words without the model's inline markup. `HmLine.text` carries
    the <strong>/<em>/<u> vocabulary, which a consumer reading a FIELD does not
    want — 'ALABAMA COURT OF CIVIL APPEALS' is the value, not
    '<strong>ALABAMA COURT OF CIVIL APPEALS</strong>'."""
    import re as _re
    from html import unescape as _un
    return _un(_re.sub(r"<[^>]+>", "", text or "")).strip()


def _blocks_text(blocks) -> str:
    """Plain text for a run of blocks — a footnote's body, a section's prose."""
    import re as _re
    from html import unescape as _un
    out = []
    for b in blocks:
        t = getattr(b, "text", "") or ""
        if not t and getattr(b, "rows", None):
            t = " ".join(" ".join(r) for r in b.rows)
        if t:
            out.append(_un(_re.sub(r"<[^>]+>", "", t)))
    return "\n\n".join(out)


_PRECIS_ROLES = ("syllabus", "summary", "headnotes")


def _precis(doc: Document) -> dict:
    """syllabus / summary / headnotes as text, FROM BOTH PLACES THEY LIVE.

    The same thing arrives two ways depending on how a court reader emitted
    it, and a consumer should not have to know which court does which:

      * as flow Blocks on `doc.syllabus` / `.summary` / `.headnotes` —
        orctapp's disposition summary, ca9's staff summary
      * as headmatter ROWS carrying that role — nebctapp sets 100 syllabus
        rows on its cover, bia one summary row, and `sections` was empty for
        both while the text sat in `headmatter.by_role` (the user, 2026-08-21)

    Merged here, flow first then rows, because that is the order the page
    prints them in. The rows stay in `headmatter` too — this is a derived
    view, not a second home.
    """
    out: dict = {}
    for role in _PRECIS_ROLES:
        parts = [_bare(getattr(b, "text", ""))
                 for b in getattr(doc, role, ()) or ()]
        parts += [_bare(getattr(i, "text", ""))
                  for i in doc.headmatter
                  if getattr(i, "role", "") == role
                  and getattr(i, "text", "")]
        out[role] = "\n".join(p for p in parts if p) or None
    return out


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
        **_precis(doc),
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
        # THE CASES THIS RECORD DECIDES, where it decides more than one —
        # each with its own number and its own parties. Empty for the
        # ordinary record: `docket_number` and `case_name` already name it.
        "cases": [{"docket_number": k.docket_number,
                   "case_name": k.case_name,
                   "parties": list(k.parties),
                   "caption": list(k.caption),
                   "lower_court": k.lower_court or None,
                   "lower_court_docket": k.lower_court_docket or None,
                   "lower_court_judge": k.lower_court_judge or None,
                   "prior_history": k.prior_history or None,
                   "page": k.prov.page}
                  for k in (c.cases or ())],
        "caption": list(c.caption),
        "disposition": c.disposition,
        "history": c.history,
        "lower_court": c.lower_court,
        "lower_court_docket": list(c.lower_court_docket),
        "lower_court_judge": c.lower_court_judge,
        "title": c.title,
        # PREVIOUSLY DROPPED. `Criteria` carries 27 fields and this dict named
        # 25 of them; `panel_line` (the roster exactly as printed) and `motion`
        # fell through in silence — the same way the headmatter did. The test
        # `test_every_criteria_field_is_exposed` now makes that impossible.
        "panel_line": c.panel_line,
        "motion": c.motion,
        "headmatter_style": c.headmatter_style,
        "n_pages": doc.meta.n_pages,
        "doc_type": _plain(doc.meta.doc_type),
    }


def _opinions(doc: Document) -> list[dict]:
    """One entry per writing, IN THE ORDER THE DOCUMENT PRINTS THEM.

    `order` is that position, 1-based — the sequence a court's papers were
    filed in and the sequence an ingest has to preserve, since a dissent means
    nothing without the opinion it dissents from. The list is already ordered;
    the field makes it survive a caller that sorts, filters or round-trips
    through a store that does not preserve sequence.

    NOTE ON THE NAME: `order` here is a POSITION, while `type` may itself be
    the string "order" (this court files its order as a separate paper). They
    are different things sharing a word — say so if you would rather have
    `ordering_key`, which is what CourtListener calls the same field.
    """
    out = []
    for n, op in enumerate(doc.opinions, start=1):
        pages = sorted({p for b in (*op.blocks, *op.signature)
                        for p in ([getattr(b, "prov", None).page]
                                  if getattr(b, "prov", None) else [])})
        out.append({
            "order": n,
            "type": op.type,
            "author": op.author or None,          # as the page prints it
            "author_name": op.author_name or None,   # parsed
            "author_title": op.author_title or None,
            "pages": pages,
            "n_blocks": len(op.blocks),
            "html": render_opinion(op),
            "text": opinion_text(op),
            "footnotes": [{"label": f.label, "text": _blocks_text(f.blocks)}
                          for f in op.footnotes],
        })
    return out


def _hm_block(items, html: str) -> dict:
    """A ROLE-BEARING BLOCK, as its own section: the rows the court printed,
    grouped by the role each was read as, plus the block's own HTML.

    Two of the document's sections are shaped this way, not as flowing prose —
    `headmatter` (the cover) and `endmatter` (the appearances). `sections.py`
    gives them both the 'hm' style, and flattening them to a list of strings
    threw away the roles, which are the product of a court port.
    """
    rows = [{"role": getattr(i, "role", "") or None,
             "text": _bare(getattr(i, "text", "")),
             "html": getattr(i, "text", ""),
             "page": i.prov.page}
            for i in items if getattr(i, "text", "")]
    by_role: dict = {}
    for row in rows:
        by_role.setdefault(row["role"] or "untinted", []).append(row["text"])
    return {
        "rows": rows,
        "by_role": by_role,
        "html": html,
        "text": "\n".join(r["text"] for r in rows),
        "untinted": sum(1 for r in rows if not r["role"]),
    }


def _headmatter(doc: Document) -> dict:
    """The cover, with the notes it carries."""
    out = _hm_block(doc.headmatter, render_headmatter(doc))
    out["footnotes"] = [{"label": f.label, "text": _blocks_text(f.blocks)}
                        for f in doc.headmatter_footnotes]
    return out


def _placed_row(rec) -> dict:
    """One removed or unclaimed row, with its position. ``bbox`` is
    (x0, top, x1, bottom) in PDF points over the row's own source lines, and
    ``line_ids`` are stable within this extraction — the two together are what
    make the decision checkable against the page."""
    out = {"kind": rec.kind, "page": rec.prov.page, "text": rec.text,
           "line_ids": list(rec.prov.line_ids)}
    if rec.bbox:
        out["bbox"] = [round(v, 2) for v in rec.bbox]
    return out


def _redaction_runs(doc: Document) -> int:
    """How many blacked-out spans the record carries — one per run of block
    glyphs, not one per glyph: a bar the width of a name is one redaction."""
    import re as _re
    parts = [getattr(i, "text", "") or "" for i in doc.headmatter]
    for op in doc.opinions:
        parts += [getattr(b, "text", "") or ""
                  for b in (*op.blocks, *op.signature)]
        parts += [getattr(b, "text", "") or ""
                  for fn in op.footnotes for b in fn.blocks]
    return sum(len(_re.findall(r"\u2588+", t)) for t in parts)


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
        "rollout": "released" if doc.meta.court_id in RELEASED else "pending",
        "source_kind": mt.source_kind,
        "n_pages": mt.n_pages,
        "scan_pages": list(mt.scan_pages),
        "text_missing_pages": list(mt.text_missing_pages),
        "cid_pages": list(mt.cid_pages),
        "residual": [_placed_row(r) for r in doc.residual],
        "residual_content": sum(1 for r in doc.residual if r.kind == "content"),
        "removed_counts": removed,
        "opinion_count": len(doc.opinions),
        "unbylined_opinions": sum(1 for op in doc.opinions
                                  if not (op.author or op.author_name)),
        "footnote_count": sum(len(op.footnotes) for op in doc.opinions)
        + len(doc.headmatter_footnotes),
        # BLACKED-OUT SPANS ARE A FACT ABOUT THE TEXT. A redacted printing
        # reads as ordinary prose with words missing, and a consumer cannot
        # tell that from prose we failed to extract — so the count is
        # reported. `pdfio.quirks` reads a redaction back into its line as
        # FULL BLOCK glyphs, whether the page drew it as a filled rect or
        # (akd/62768.505.0) as one very wide dash, so counting the runs
        # counts the redactions.
        "redactions": _redaction_runs(doc),
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


def read(src, court_id: str, *,
         include_document: bool = False,
         allow_pending: bool = False) -> dict:
    """Read one PDF. ``src`` is a path, bytes, or a binary file object.

    THE COURT ID IS CHECKED, and both ways of getting it wrong now fail loudly
    instead of quietly reading worse:

      * an id no court declares raises `UnknownCourt` — it would otherwise get
        core's generic reader, and the record comes back valid but thin (the
        user hit this with 'ala' for an 'alacivapp' record: no case name, no
        filing date, no parties, and all 16 headmatter rows unclaimed).
      * a court still being worked on raises `CourtNotReleased`. Pass
        `allow_pending=True` to read it anyway; `diagnostics['rollout']` then
        says which you got, so a consumer that overrode still knows.

    Nothing else is gated: `harness.cli extract`, `render`, the guard and the
    viewer all read every court, released or not.
    """
    if court_id not in PROFILES:
        raise UnknownCourt(
            f"{court_id!r} is not a registered court id; "
            f"{len(PROFILES)} are. Did you mean a sibling court?")
    if court_id not in RELEASED and not allow_pending:
        n, seen, bad = HELD_BACK.get(court_id, (0, 0, 0))
        raise CourtNotReleased(
            f"{court_id!r} is not released yet ({seen}/{n} records reviewed, "
            f"{bad} marked bad). Pass allow_pending=True to read it anyway.")
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
        "headmatter": _headmatter(doc),
        # THE SIBLING SECTIONS, words and markup both. `attorneys` is the
        # appearances block — the counsel the page prints, which `cluster`
        # carries only as the court's own one-line summary.
        # ENDMATTER IS THE APPEARANCES, and it is role-bearing rows like the
        # cover — not prose. `sections.py` names it 'endmatter' over
        # `doc.attorneys`; flattened in with the flowing sections its roles
        # were lost (the user, 2026-08-21: 'also endmatter is a thing').
        "endmatter": _hm_block(doc.attorneys,
                               render_hm_items(doc.attorneys)),
        # The sections that really are flowing prose.
        "sections": {name: {"text": [_bare(getattr(b, "text", ""))
                                     for b in getattr(doc, name)],
                            "html": [getattr(b, "text", "")
                                     for b in getattr(doc, name)]}
                     for name in ("syllabus", "headnotes", "summary",
                                  "signature", "trailer")
                     if getattr(doc, name)},
        # AUDITABLE, not merely reported. Each removal says what it was,
        # what it said, and WHERE IT STOOD — page, box and the source line
        # ids — so a reader can put it back on the sheet and check the call
        # (the user, 2026-08-22: 'i want to be able to sorta let someone
        # audit it').
        "removed": [_placed_row(d) for d in doc.dropped],
        "diagnostics": _diagnostics(doc, result.status),
        "html": render_body(doc),
        "review_html": render_html(doc),
        "casebody": render_casebody(doc),
        "warnings": list(doc.warnings),
    }
    if include_document:
        out["document"] = doc
    return out
