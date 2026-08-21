"""Harvard casebody XML — the machine-readable projection.

Iterates the same SECTION_SPEC as the review HTML, so it cannot drift the way
the old casebody.py did (six sections behind the model, updated by nobody).
Criteria scalars map to their casebody elements. Compatibility target is
SEMANTIC (normalized diffs), not byte-for-byte.
"""

from __future__ import annotations

from html import escape

from .. import model as m
from ..sections import SECTIONS


def _markup_ok(s: str) -> str:
    """Model markup is already escaped + known-tag XML; pass through."""
    return s or ""


def _blocks_xml(blocks: list, out: list) -> None:
    for b in blocks:
        match b:
            case m.Paragraph() | m.ListItem():
                out.append(f"<p>{_markup_ok(b.text)}</p>")
            case m.Heading():
                out.append(f"<p><strong>{_markup_ok(b.text)}</strong></p>")
            case m.Blockquote():
                out.append(f"<blockquote>{_markup_ok(b.text)}</blockquote>")
            case m.TableBlock():
                rows = "".join(
                    "<tr>" + "".join(f"<td>{_markup_ok(c)}</td>" for c in row) + "</tr>"
                    for row in b.rows)
                out.append(f"<p><table>{rows}</table></p>")
            case m.ImageBlock():
                pass  # casebody carries no images
            case _:
                raise TypeError(f"_blocks_xml: {type(b)!r}")


def _hm_xml(items: list, el: str, out: list) -> None:
    for item in items:
        match item:
            case m.HmLine():
                if item.text:
                    out.append(f"<{el}>{_markup_ok(item.text)}</{el}>")
            case m.CaptionBlock():
                for row in item.left + item.right:
                    if row.text:
                        out.append(f"<{el}>{_markup_ok(row.text)}</{el}>")
            case m.Rule() | m.Divider() | m.Gap() | m.ImageBlock():
                pass
            case _:
                raise TypeError(f"_hm_xml: {type(item)!r}")


def _footnotes_xml(fns: list, out: list) -> None:
    for fn in fns:
        out.append(f'<footnote label="{escape(fn.label, quote=True)}">')
        _blocks_xml(fn.blocks, out)
        out.append("</footnote>")


def render_casebody(doc: m.Document) -> str:
    out: list[str] = []
    c = doc.criteria
    # THE SOURCE FLAG RIDES ON THE ROOT, and only when there is something to
    # say. A scan's OCR text is indistinguishable from a court's own type once
    # it is in this XML, so anything ingesting the projection needs to be able
    # to refuse it without re-opening the PDF. Absent on born-digital paper,
    # so ordinary output is unchanged byte for byte.
    _src = (f' source="{escape(doc.meta.source_kind, quote=True)}"'
            if doc.meta.source_kind else "")
    out.append(f'<casebody firstpage="1" lastpage="{doc.meta.n_pages}"{_src} '
               f'xmlns="http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Case_Body:v1">')
    for p in c.parties:
        out.append(f"<parties>{escape(p)}</parties>")
    if c.docket_number:
        out.append(f"<docketnumber>{escape(c.docket_number)}</docketnumber>")
    for d in c.other_dockets:
        out.append(f"<docketnumber>{escape(d)}</docketnumber>")
    for d in c.lower_court_docket:
        out.append(f'<docketnumber type="lower">{escape(d)}</docketnumber>')
    if doc.meta.court_label:
        out.append(f"<court>{escape(doc.meta.court_label)}</court>")
    if c.decision_date:
        out.append(f"<decisiondate>{escape(c.decision_date)}</decisiondate>")
    if c.lower_court:
        out.append(f"<otherdate>{escape(c.lower_court)}</otherdate>")
    if c.history:
        out.append(f"<history>{escape(c.history)}</history>")
    if c.disposition:
        out.append(f"<disposition>{escape(c.disposition)}</disposition>")
    if c.attorneys:
        out.append(f"<attorneys>{escape(c.attorneys)}</attorneys>")
    if c.judges:
        out.append(f"<judges>{escape(c.judges)}</judges>")

    for spec in SECTIONS:
        if spec.casebody is None:
            continue
        value = getattr(doc, spec.attr)
        if not value:
            continue
        if spec.html == "hm":
            _hm_xml(value, "summary", out)
        elif spec.html == "flow":
            wrap = spec.casebody
            out.append(f"<{wrap}>")
            _blocks_xml(value, out)
            out.append(f"</{wrap}>")
        elif spec.html == "footnotes":
            _footnotes_xml(value, out)
        elif spec.html == "opinions":
            for op in value:
                out.append(f'<opinion type="{escape(op.type, quote=True)}">')
                if op.author:
                    out.append(f"<author>{_markup_ok(op.author)}</author>")
                _blocks_xml(op.blocks, out)
                _footnotes_xml(op.footnotes, out)
                out.append("</opinion>")
    out.append("</casebody>")
    return "\n".join(out)
