"""Render an ``ExtractedDocument`` as a self-contained, readable HTML page.

This is a review-oriented consumer of the extraction contract: it produces a
single styled HTML document meant to be opened and eyeballed against the
source PDF. When the document's ``source_path`` is available, the page is laid
out as two panes — the source PDF on the left, the extracted content on the
right — so the two can be compared side by side.

Paragraph/footnote text already carries inline markup
(``<em>``/``<strong>``/``<u>``/``<footnotemark>``/``<pagenumber>``) with its
literal text escaped; ``<em>``/``<strong>``/``<u>`` are valid HTML and pass
through, while footnote marks and page-number markers are rewritten into
review-friendly HTML. No regex — the inline rewrite is a plain string scan.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from ..models import ExtractedDocument, Footnote, Opinion


_CSS = """
  :root { --ink:#1a1a1a; --muted:#666; --rule:#ddd; --accent:#7a1f1f; }
  * { box-sizing: border-box; }
  body { font: 16px/1.6 Georgia, "Times New Roman", serif; color: var(--ink);
         margin: 0; }
  .review-cols { display: flex; height: 100vh; }
  .review-pane { flex: 1; min-width: 0; height: 100vh; overflow: auto; }
  .review-pane.pdf { background: #525659; border-right: 1px solid var(--rule); }
  .review-pane.pdf iframe { width: 100%; height: 100%; border: 0; }
  .review-pane.doc { padding: 2rem 2.5rem; }
  .doc-inner { max-width: 44rem; margin: 0 auto; }
  /* single-pane fallback when there is no PDF to show */
  body.single .review-pane.doc { padding: 2rem 1.25rem; }
  body.single .doc-inner { max-width: 46rem; }

  .fingerprint { border: 1px solid var(--rule); border-left: 4px solid var(--muted);
                 border-radius: .3rem; padding: .8rem 1rem; margin-bottom: 1.5rem;
                 background: #fafafa; }
  .fingerprint.fp-full-opinion { border-left-color: #2f5d3a; }
  .fingerprint.fp-no-opinion-decision { border-left-color: #6a4a1f; }
  .fingerprint.fp-per-curiam-opinion { border-left-color: #1f4e7a; }
  .fingerprint.fp-order, .fingerprint.fp-notice { border-left-color: var(--accent); }
  .fp-main { font-weight: bold; font-size: 1.15rem; }
  .fp-court { font-variant: small-caps; color: var(--muted); font-size: .9rem; }
  .fp-signals { margin-top: .5rem; display: flex; gap: .4rem; flex-wrap: wrap; }
  .fp-signals span { font-family: ui-monospace, monospace; font-size: .7rem;
             background: #ece9e3; color: #555; padding: .12rem .5rem;
             border-radius: .25rem; }
  details.dropped { margin-bottom: 1.5rem; border: 1px dashed #d8c4c4;
                    background: #fcf6f6; border-radius: .3rem; padding: .5rem .8rem; }
  details.dropped > summary { cursor: pointer; color: var(--accent);
                    font-size: .78rem; font-family: ui-monospace, monospace;
                    letter-spacing: .03em; }
  .dropline { font-family: ui-monospace, monospace; font-size: .76rem;
              color: #8a6a6a; line-height: 1.5; margin-top: .5rem;
              white-space: pre-wrap; word-break: break-word; }
  .block { margin-bottom: 2.5rem; }
  h2.sec { font-size: .8rem; text-transform: uppercase; letter-spacing: .1em;
           color: var(--muted); border-bottom: 2px solid var(--ink);
           padding-bottom: .3rem; margin: 0 0 1rem; }
  h2.sec .raw-tag, h2.sec .count { float: right; font-weight: normal;
           letter-spacing: .04em; text-transform: none; }
  h2.sec .raw-tag { color: var(--accent); }
  .headmatter .raw { background: #faf8f4; border: 1px solid var(--rule);
                     border-radius: .3rem; padding: .9rem 1.1rem; }
  .rawline { font-family: ui-monospace, monospace; font-size: .8rem;
             line-height: 1.5; color: #333; white-space: pre-wrap;
             word-break: break-word; }
  .rawline .centered { display: block; text-align: center; }  /* keep centering */
  .hmline { line-height: 1.45; color: #222; }
  hr.divider { border: 0; border-top: 1px solid #999; margin: .55rem auto;
               width: 40%; }
  .rawgap { height: .8rem; }
  .empty { color: var(--muted); font-style: italic; }
  .hm-fac { position: relative; font-family: "Times New Roman", Georgia, serif;
            color: var(--ink); margin: .25rem 0 .5rem; }
  .hm-fac .hm-line { position: absolute; white-space: nowrap; line-height: 1; }
  .hm-fac .hm-rule { position: absolute; }
  section.opinion { margin-top: 2rem; padding-top: 1.25rem;
                    border-top: 1px solid var(--rule); }
  section.opinion:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
  .author { font-variant: small-caps; font-weight: bold; font-size: 1.05rem;
            margin: .5rem 0 1rem; }
  .optype-badge { display: inline-block; font-family: ui-monospace, monospace;
            font-size: .72rem; font-weight: bold; text-transform: uppercase;
            letter-spacing: .06em; color: #fff; background: var(--muted);
            padding: .15rem .55rem; border-radius: .25rem; }
  .optype-badge.t-majority { background: #2f5d3a; }
  .optype-badge.t-dissent { background: #7a1f1f; }
  .optype-badge.t-concurrence { background: #1f4e7a; }
  .optype-badge.t-concurrence-in-result { background: #6a4a1f; }
  p { text-align: justify; margin: .85rem 0; }
  blockquote { margin: .85rem 0 .85rem 2rem; color: #333; }
  h3 { font-size: 1.05rem; margin: 1.4rem 0 .6rem; text-align: center; }
  sup.fn { color: var(--accent); font-weight: bold; padding: 0 .1em; }
  .pagenum { display: inline-block; font-family: ui-monospace, monospace;
             font-size: .62rem; color: #fff; background: var(--muted);
             border-radius: .2rem; padding: 0 .3rem; vertical-align: super;
             margin: 0 .15rem; }
  .footnotes { margin-top: 1.5rem; padding-top: .75rem;
               border-top: 1px solid var(--rule); font-size: .88rem;
               color: #333; }
  .footnote { margin: .5rem 0; }
  .footnote .label { color: var(--accent); font-weight: bold; margin-right: .4rem; }
  details.summary { margin-top: 2.5rem; font-size: .85rem; color: var(--muted); }
  details.summary pre { white-space: pre-wrap; font-family: ui-monospace, monospace;
                        font-size: .78rem; background: #faf8f4; padding: .75rem;
                        border-radius: .3rem; }
  .centered { display: block; text-align: center; }
  .warnings { background: #fff5f5; border: 1px solid #f0c0c0; color: #7a1f1f;
              padding: .6rem .9rem; border-radius: .3rem; margin-bottom: 1.5rem;
              font-size: .85rem; }
  .src { color: var(--muted); font-size: .78rem; margin-top: 3rem;
         border-top: 1px solid var(--rule); padding-top: .75rem;
         font-family: ui-monospace, monospace; word-break: break-all; }
  .nopdf { color: var(--muted); padding: 2rem; font-family: ui-monospace, monospace;
           font-size: .85rem; }
"""


def render_html(doc: ExtractedDocument, pdf_src: str | None = None) -> str:
    """Render the review page. ``pdf_src`` is the href used for the PDF pane —
    pass a path relative to where the HTML will be written so it resolves when
    served or previewed; if omitted, an absolute ``file://`` URI is used."""
    title = " ".join(doc.parties).strip() or doc.court_label or "Opinion"
    pdf_uri = pdf_src or _pdf_uri(doc.source_path)

    out = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(title)}</title>",
        f"<style>{_CSS}</style>",
        "</head>",
        f'<body class="{"" if pdf_uri else "single"}">',
        '<div class="review-cols">',
    ]

    if pdf_uri:
        out.append('<div class="review-pane pdf">')
        out.append(f'<iframe src="{escape(pdf_uri)}" title="source PDF"></iframe>')
        out.append("</div>")

    out.append('<div class="review-pane doc"><article class="doc-inner">')
    out.extend(_render_content(doc))
    out.append("</article></div>")

    out.append("</div></body></html>")
    return "\n".join(out)


def _pdf_uri(source_path: str | None) -> str | None:
    """Absolute ``file://`` URI for the source PDF, or None if unavailable."""
    if not source_path:
        return None
    try:
        return Path(source_path).resolve().as_uri()
    except (ValueError, OSError):
        return None


def _render_content(doc: ExtractedDocument) -> list:
    out = []
    if not doc.layout_ok:
        out.append(
            '<div class="warnings">⚠ unexpected layout — ' "review carefully</div>"
        )
    if doc.warnings:
        items = "".join(f"<li>{escape(w)}</li>" for w in doc.warnings)
        out.append(f'<div class="warnings"><ul>{items}</ul></div>')

    out.extend(_render_fingerprint(doc))
    out.extend(_render_dropped(doc))
    out.extend(_render_headmatter(doc))
    out.extend(_render_syllabus(doc))
    out.extend(_render_opinions(doc))
    out.extend(_render_trailer(doc))

    if doc.source_path:
        out.append(f'<div class="src">source: {escape(doc.source_path)}</div>')
    return out


_INDEX_CSS = """
  body { font: 15px/1.5 -apple-system, system-ui, sans-serif; color: #1a1a1a;
         max-width: 70rem; margin: 2rem auto; padding: 0 1.5rem; }
  h1 { font-size: 1.4rem; margin: 0 0 .25rem; }
  .sub { color: #666; margin-bottom: 1.5rem; }
  .legend { display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 2rem; }
  .legend a { text-decoration: none; font-size: .8rem; font-family: ui-monospace,
              monospace; background: #f0ece4; color: #333; padding: .2rem .6rem;
              border-radius: .25rem; }
  .legend a b { color: #7a1f1f; }
  h2.grp { font-size: 1.05rem; margin: 2rem 0 .5rem; padding-bottom: .3rem;
           border-bottom: 2px solid #1a1a1a; display: flex;
           justify-content: space-between; }
  h2.grp .n { color: #666; font-weight: normal; font-size: .9rem; }
  table { width: 100%; border-collapse: collapse; font-size: .9rem; }
  th { text-align: left; color: #888; font-weight: normal; font-size: .75rem;
       text-transform: uppercase; letter-spacing: .05em; padding: .3rem .5rem; }
  td { padding: .4rem .5rem; border-top: 1px solid #eee; vertical-align: top; }
  tr:hover td { background: #faf8f4; }
  td.name a { color: #1a4e7a; text-decoration: none; }
  td.name a:hover { text-decoration: underline; }
  td.types { font-family: ui-monospace, monospace; font-size: .78rem; color: #555; }
  td.pp { color: #888; white-space: nowrap; text-align: right; }
"""

# Display order for the fingerprint groups.
_FP_ORDER = [
    "Full opinion",
    "Per curiam opinion",
    "No-opinion decision",
    "Order",
    "Certificate of judgment",
    "Notice",
    "Unknown",
]


def render_index(court_id: str, court_label: str, entries: list) -> str:
    """An index page for a batch: cases grouped by fingerprint, each group a
    table. ``entries`` is a list of dicts with keys name/href/fingerprint/
    types/n_pages/doc_type."""
    groups = {}
    for e in entries:
        groups.setdefault(e["fingerprint"], []).append(e)
    ordered = [g for g in _FP_ORDER if g in groups] + [
        g for g in groups if g not in _FP_ORDER
    ]

    out = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(court_label)} — index</title>",
        f"<style>{_INDEX_CSS}</style></head><body>",
        f"<h1>{escape(court_label)}</h1>",
        f'<div class="sub">{len(entries)} document(s) · grouped by type</div>',
    ]

    out.append('<div class="legend">')
    for g in ordered:
        slug = g.lower().replace(" ", "-")
        out.append(f'<a href="#{slug}">{escape(g)} <b>{len(groups[g])}</b></a>')
    out.append("</div>")

    for g in ordered:
        rows = sorted(groups[g], key=lambda e: e["name"].lower())
        slug = g.lower().replace(" ", "-")
        out.append(
            f'<h2 class="grp" id="{slug}">{escape(g)}'
            f'<span class="n">{len(rows)}</span></h2>'
        )
        out.append(
            "<table><thead><tr><th>Case</th><th>Opinions</th>"
            "<th>doc_type</th><th>pp.</th></tr></thead><tbody>"
        )
        for e in rows:
            types = " · ".join(e["types"]) or "—"
            out.append(
                f'<tr><td class="name"><a href="{escape(e["href"])}">'
                f'{escape(e["name"])}</a></td>'
                f'<td class="types">{escape(types)}</td>'
                f'<td class="types">{escape(e["doc_type"])}</td>'
                f'<td class="pp">{e["n_pages"]}</td></tr>'
            )
        out.append("</tbody></table>")

    out.append("</body></html>")
    return "\n".join(out)


def fingerprint(doc: ExtractedDocument) -> str:
    return _fingerprint(doc)


def _fingerprint(doc: ExtractedDocument) -> str:
    """A human-facing characterization of the document, finer than doc_type:
    'Full opinion' vs 'No-opinion decision' vs 'Per curiam' vs order / etc."""
    if doc.doc_type == "certificate-of-judgment":
        return "Certificate of judgment"
    if doc.doc_type == "order":
        return "Order"
    if doc.doc_type == "notice":
        return "Notice"
    if doc.doc_type == "unknown":
        return "Unknown"
    # doc_type == opinion: look closer at the body.
    body = " ".join(b.text for op in doc.opinions for b in op.blocks).lower()
    if "no opinion" in body:
        return "No-opinion decision"
    per_curiam = doc.opinions and all(
        op.author.upper().startswith("PER CURIAM") for op in doc.opinions
    )
    if per_curiam:
        return "Per curiam opinion"
    return "Full opinion"


def _render_fingerprint(doc: ExtractedDocument) -> list:
    fp = _fingerprint(doc)
    n_fn = sum(len(op.footnotes) for op in doc.opinions)
    types = " · ".join(op.type for op in doc.opinions) or "—"
    signals = [
        f"type: {escape(doc.doc_type)}",
        f"{len(doc.opinions)} opinion(s): {escape(types)}",
        f"{n_fn} footnote(s)",
        f"{doc.n_pages} pp.",
    ]
    chips = "".join(f"<span>{s}</span>" for s in signals)
    slug = fp.lower().replace(" ", "-")
    return [
        f'<div class="fingerprint fp-{slug}">',
        f'<div class="fp-main">{escape(fp)}</div>',
        f'<div class="fp-court">{escape(doc.court_label)}</div>',
        f'<div class="fp-signals">{chips}</div>',
        "</div>",
    ]


def _render_dropped(doc: ExtractedDocument) -> list:
    """Collapsible block (closed by default) of content found and removed —
    publication notices, stamps, etc. — shown at the very top for review."""
    if not doc.dropped:
        return []
    out = [
        '<details class="dropped">',
        f"<summary>Removed before parsing — notices / stamps "
        f"({len(doc.dropped)})</summary>",
    ]
    for d in doc.dropped:
        out.append(f'<div class="dropline">{_inline_to_html(str(d))}</div>')
    out.append("</details>")
    return out


def _render_syllabus(doc: ExtractedDocument) -> list:
    """Official syllabus / case summary that precedes the opinion (Colorado's
    SUMMARY page, Connecticut's Syllabus) — its own block, not opinion body."""
    if not getattr(doc, "syllabus", None):
        return []
    out = [
        '<section class="block syllabus">',
        '<h2 class="sec">Syllabus '
        '<span class="raw-tag">not part of the opinion</span></h2>',
        '<div class="raw">',
    ]
    for line in doc.syllabus:
        out.append(f'<div class="rawline">{_inline_to_html(str(line))}</div>')
    out.append("</div></section>")
    return out


def _render_trailer(doc: ExtractedDocument) -> list:
    """Trailing matter after the last opinion (counsel names / addresses),
    grouped in its own box so it isn't mistaken for opinion body."""
    if not doc.trailer:
        return []
    out = [
        '<section class="block trailer">',
        '<h2 class="sec">Ending matter '
        '<span class="raw-tag">counsel / addresses</span></h2>',
        '<div class="raw">',
    ]
    for line in doc.trailer:
        out.append(f'<div class="rawline">{_inline_to_html(str(line))}</div>')
    out.append("</div></section>")
    return out


def _render_headmatter_facsimile(doc: ExtractedDocument) -> list:
    """Faithful headmatter: each line placed at its real x/y, at its real font
    size and weight, with the caption box drawn from the rule geometry. 1px per
    PDF point."""
    lines = doc.headmatter_lines
    box = doc.caption_box or {}
    xs = [l["x0"] for l in lines]
    if box.get("vx") is not None:
        xs.append(box["vx"])
    if box.get("hrules"):
        xs += [h[1] for h in box["hrules"]]
    min_x = min(xs)
    min_top = min(l["top"] for l in lines)
    bottom = max(l["top"] + l["size"] * 1.3 for l in lines)
    if box.get("vbottom"):
        bottom = max(bottom, box["vbottom"])
    height = bottom - min_top + 6

    out = [f'<div class="hm-fac" style="height:{height:.0f}px">']
    # caption-box rules
    if box.get("vx") is not None:
        out.append(
            f'<div class="hm-rule" style="left:{box["vx"] - min_x:.0f}px;'
            f'top:{box["vtop"] - min_top:.0f}px;'
            f'height:{box["vbottom"] - box["vtop"]:.0f}px;'
            'border-left:1px solid #b9b2a6"></div>'
        )
    for top, x0, x1 in box.get("hrules", []):
        out.append(
            f'<div class="hm-rule" style="left:{x0 - min_x:.0f}px;'
            f"top:{top - min_top:.0f}px;width:{x1 - x0:.0f}px;"
            'border-top:1px solid #b9b2a6"></div>'
        )
    for l in lines:
        weight = "bold" if l["bold"] else "normal"
        out.append(
            f'<div class="hm-line" style="left:{l["x0"] - min_x:.0f}px;'
            f'top:{l["top"] - min_top:.0f}px;font-size:{l["size"]:.1f}px;'
            f'font-weight:{weight}">{escape(l["text"])}</div>'
        )
    out.append("</div>")
    return out


def _render_headmatter(doc: ExtractedDocument) -> list:
    """Raw, unparsed pre-opinion content, verbatim and at the top. Structured
    caption parsing is deliberately deferred — this is the dump."""
    out = [
        '<section class="block headmatter">',
        '<h2 class="sec">Headmatter <span class="raw-tag">raw</span></h2>',
    ]
    if not doc.summary:
        out.append('<div class="empty">(none)</div>')
    else:
        out.append('<div class="raw">')
        for s in doc.summary:
            if isinstance(s, dict) and s.get("__caption__"):
                # A two-column caption box (left = parties, right = docket):
                # render the columns side by side as text, not as a raw dict.
                out.append(
                    '<div class="caption-cols" style="display:flex;'
                    'gap:1.4rem;align-items:stretch">'
                )
                out.append('<div style="flex:1;min-width:0">')
                for ln in s.get("left", []):
                    out.append(f'<div class="rawline">{_inline_to_html(str(ln))}</div>')
                # The drawn vertical rule between parties (left) and docket (right).
                out.append(
                    '</div><div style="border-left:1px solid #999"></div>'
                    '<div style="flex:1;min-width:0">'
                )
                for ln in s.get("right", []):
                    out.append(f'<div class="rawline">{_inline_to_html(str(ln))}</div>')
                out.append("</div></div>")
            elif isinstance(s, dict) and s.get("__hm__"):
                # A style-preserving headmatter line: relative font size,
                # alignment, and inline bold/italic kept from the PDF.
                al = {"C": "center", "L": "left", "R": "right"}.get(
                    s.get("align"), "left"
                )
                out.append(
                    f'<div class="hmline" style="text-align:{al};'
                    f'font-size:{s.get("rel", 1)}em">'
                    f'{_inline_to_html(str(s.get("html", "")))}</div>'
                )
            elif isinstance(s, dict):
                out.append(f'<div class="rawline">{escape(str(s))}</div>')
            elif str(s).strip() == "__DIVIDER__":
                out.append('<hr class="divider">')
            elif str(s).strip() == "":
                out.append('<div class="rawgap"></div>')  # section spacing
            else:
                out.append(f'<div class="rawline">{_inline_to_html(str(s))}</div>')
        out.append("</div>")
    if doc.headmatter_footnotes:
        out.append('<div class="footnotes">')
        for fn in doc.headmatter_footnotes:
            out.append(_render_footnote(fn))
        out.append("</div>")
    out.append("</section>")
    return out


def _render_opinions(doc: ExtractedDocument) -> list:
    out = ['<section class="block opinions">']
    if doc.opinions:
        types = " · ".join(op.type for op in doc.opinions)
        out.append(
            f'<h2 class="sec">Opinions '
            f'<span class="count">{len(doc.opinions)}: '
            f"{escape(types)}</span></h2>"
        )
    else:
        out.append('<h2 class="sec">Opinions <span class="count">none</span>' "</h2>")
    for op in doc.opinions:
        out.extend(_render_opinion(op))
    out.append("</section>")
    return out


def _render_opinion(op: Opinion) -> list:
    out = ['<section class="opinion">']
    out.append(
        f'<div class="optype-badge t-{escape(op.type)}">' f"{escape(op.type)}</div>"
    )
    out.append(f'<div class="author">{escape(op.author)}</div>')
    for b in op.blocks:
        if b.kind == "image":
            out.append(
                f'<img src="{escape(str(b.payload.get("src", "")))}" '
                f'alt="figure on page {b.page}">'
            )
        elif b.kind == "table":
            out.extend(_render_table(b.payload.get("rows") or []))
        elif b.kind == "heading":
            out.append(f"<h3>{_inline_to_html(b.text)}</h3>")
        elif b.kind == "blockquote":
            out.append(f"<blockquote>{_inline_to_html(b.text)}</blockquote>")
        else:
            out.append(f"<p>{_inline_to_html(b.text)}</p>")
    if op.footnotes:
        out.append('<div class="footnotes">')
        for fn in op.footnotes:
            out.append(_render_footnote(fn))
        out.append("</div>")
    out.append("</section>")
    return out


def _render_footnote(fn: Footnote) -> str:
    body = "".join(
        (
            f"<blockquote>{_inline_to_html(text)}</blockquote>"
            if tag == "blockquote"
            else f"<span>{_inline_to_html(text)}</span> "
        )
        for tag, text in fn.paragraphs
    )
    return (
        f'<div class="footnote">'
        f'<span class="label">{escape(fn.label)}</span>{body}</div>'
    )


def _render_table(rows: list) -> list:
    if not rows:
        return []
    out = ["<table>"]
    for ri, row in enumerate(rows):
        tag = "th" if ri == 0 else "td"
        cells = "".join(
            f"<{tag}>{escape((c or '').replace(chr(10), ' ').strip())}</{tag}>"
            for c in row
        )
        out.append(f"<tr>{cells}</tr>")
    out.append("</table>")
    return out


def _inline_to_html(text: str) -> str:
    """Rewrite the inline-markup string into review-friendly HTML.

    ``<em>``/``<strong>``/``<u>`` are already valid HTML and pass through.
    ``<footnotemark>N</footnotemark>`` -> superscript; ``<pagenumber
    value="N"/>`` -> a small page chip; ``<centered>`` -> a centered block.
    Plain string scanning, no regex."""
    text = (
        text.replace("<footnotemark>", '<sup class="fn">')
        .replace("</footnotemark>", "</sup>")
        .replace("<centered>", '<span class="centered">')
        .replace("</centered>", "</span>")
    )
    return _rewrite_pagenumbers(text)


def _rewrite_pagenumbers(text: str) -> str:
    marker = '<pagenumber value="'
    if marker not in text:
        return text
    out = []
    rest = text
    while True:
        i = rest.find(marker)
        if i == -1:
            out.append(rest)
            break
        out.append(rest[:i])
        rest = rest[i + len(marker) :]
        j = rest.find('"/>')
        if j == -1:  # malformed; emit the rest verbatim
            out.append(marker + rest)
            break
        out.append(f'<span class="pagenum">{rest[:j]}</span>')
        rest = rest[j + 3 :]
    return "".join(out)
