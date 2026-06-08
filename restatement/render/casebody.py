"""Render an ``ExtractedDocument`` as Harvard Caselaw casebody XML.

This is one consumer of the extraction contract; the same model can feed an
HTML or JSON renderer. Paragraph/footnote text in the model already carries
inline markup (``<em>``/``<strong>``/``<u>``/``<footnotemark>``/
``<pagenumber>``) with its literal text escaped, so block text is emitted
verbatim; only plain scalar fields are escaped here.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from ..models import ExtractedDocument, Footnote, Opinion


CASEBODY_NS = "http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Case_Body:v1"


def render_casebody(doc: ExtractedDocument) -> str:
    attrs = f'firstpage="1" lastpage="{doc.n_pages}" xmlns="{CASEBODY_NS}"'
    if not doc.layout_ok:
        attrs += ' status="unexpected-layout"'
    out = [f"<casebody {attrs}>"]
    out.extend(_render_headmatter(doc))

    if doc.headmatter_footnotes:
        out.append("  <headmatter-footnotes>")
        for fn in doc.headmatter_footnotes:
            out.append(_render_footnote(fn))
        out.append("  </headmatter-footnotes>")

    for op in doc.opinions:
        out.extend(_render_opinion(op))
    out.append("</casebody>")
    return "\n".join(out)


def _render_headmatter(doc: ExtractedDocument) -> list:
    out = []
    if doc.decision_date:
        out.append(f"  <decisiondate>{escape(doc.decision_date)}</decisiondate>")
    if doc.court_label:
        out.append(f"  <court>{escape(doc.court_label)}</court>")
    if doc.docket_number:
        out.append(f"  <docketnumber>{escape(doc.docket_number)}</docketnumber>")
    if doc.other_docket:
        out.append(f"  <otherdocket>{escape(doc.other_docket)}</otherdocket>")
    for p in doc.parties:
        out.append(f"  <parties>{escape(p)}</parties>")
    if doc.motion:
        out.append(f"  <p>{escape(doc.motion)}</p>")
    if doc.parent_case:
        out.append(f"  <history>{escape(doc.parent_case)}</history>")
    if doc.lower_court:
        out.append(f"  <history>{escape(doc.lower_court)}</history>")
    if doc.history:
        out.append(f"  <history>{escape(doc.history)}</history>")
    if doc.attorneys:
        out.append(f"  <attorneys>{escape(doc.attorneys)}</attorneys>")
    if doc.judges:
        out.append(f"  <judges>{escape(doc.judges)}</judges>")
    if doc.disposition:
        out.append(f"  <disposition>{escape(doc.disposition)}</disposition>")
    for s in doc.summary:
        if isinstance(s, dict) and s.get("__caption__"):
            out.append("  <caption-columns>")
            out.append("    <col-left>")
            for ln in s.get("left", []):
                out.append(f"      <line>{ln}</line>")
            out.append("    </col-left>")
            out.append("    <col-right>")
            for ln in s.get("right", []):
                out.append(f"      <line>{ln}</line>")
            out.append("    </col-right>")
            out.append("  </caption-columns>")
        else:
            out.append(f"  <summary>{s}</summary>")
    if doc.submitted:
        out.append(f"  <otherdate>Submitted {escape(doc.submitted)}</otherdate>")
    return out


def _render_opinion(op: Opinion) -> list:
    out = [
        f'  <opinion type="{op.type}">',
        f"    <author>{escape(op.author)}</author>",
    ]
    for b in op.blocks:
        if b.kind == "image":
            out.append(
                f'    <image src="{b.payload["src"]}" '
                f'width="{b.payload["width"]:.0f}" '
                f'height="{b.payload["height"]:.0f}" page="{b.page}"/>'
            )
        elif b.kind == "table":
            out.extend(_render_table(b.payload.get("rows") or [], b.page))
        else:
            out.append(f"    <{b.kind}>{b.text}</{b.kind}>")
    if op.footnotes:
        out.append("    <footnotes>")
        for fn in op.footnotes:
            out.append(_render_footnote(fn))
        out.append("    </footnotes>")
    out.append("  </opinion>")
    return out


def _render_footnote(fn: Footnote) -> str:
    inner = "".join(f"<{tag}>{text}</{tag}>" for tag, text in fn.paragraphs)
    return f'      <footnote label="{escape(fn.label)}">{inner}</footnote>'


def _render_table(rows: list, page_no) -> list:
    if not rows:
        return []
    out = [f'    <table page="{page_no}">']
    for ri, row in enumerate(rows):
        tag = "th" if ri == 0 else "td"
        out.append("      <tr>")
        for cell in row:
            cell_text = (cell or "").replace("\n", " ").strip()
            out.append(f"        <{tag}>{escape(cell_text)}</{tag}>")
        out.append("      </tr>")
    out.append("    </table>")
    return out
