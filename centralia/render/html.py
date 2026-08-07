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

from ..models import Block, ExtractedDocument, Footnote, Opinion


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

  .fingerprint { border: 1px solid var(--rule); border-left: 10px solid var(--muted);
                 border-radius: .3rem; padding: .8rem 1rem; margin-bottom: 1.5rem;
                 background: #fafafa; }
  .fingerprint.fp-full-opinion { border-left-color: #2f5d3a; }
  .fingerprint.fp-no-opinion-decision { border-left-color: #6a4a1f; }
  .fingerprint.fp-per-curiam-opinion { border-left-color: #1f4e7a; }
  .fingerprint.fp-order, .fingerprint.fp-notice { border-left-color: var(--accent); }
  .fingerprint.fp-attorney-filing { border-left-color: #8a1f1f; }
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
  /* Unplaced CONTENT is a to-do, not furniture: it gets its own loud box,
     open by default, so it can never hide behind a 'notices / stamps' count. */
  details.unplaced { border-style: solid; border-color: #b45309;
                    background: #fdf6ec; }
  details.unplaced > summary { color: #92400e; font-weight: 600; }
  details.unplaced .dropline { color: #7c3f12; }
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
  .headmatter .raw, .syllabus .raw, .headnotes .raw, .attorneys .raw { background: #faf8f4;
                     border: 1px solid var(--rule);
                     border-radius: .3rem; padding: .9rem 1.1rem; }
  .rawline { font-family: ui-monospace, monospace; font-size: .8rem;
             line-height: 1.5; color: #333; white-space: pre-wrap;
             word-break: break-word; }
  .rawline .centered { display: block; text-align: center; }  /* keep centering */
  .rawline .flushright { display: block; text-align: right; }  /* keep right margin */
  .hmline { line-height: 1.45; color: #222; }
  details.crit > summary { cursor: pointer; }
  details.crit .crit-body { background: #faf8f4; border: 1px solid var(--rule);
             border-radius: .3rem; padding: .7rem 1rem; margin-top: .5rem; }
  .crit-row { display: flex; gap: .8rem; align-items: baseline;
              padding: .12rem 0; font-size: .82rem; }
  .crit-k { flex: 0 0 9rem; font-family: ui-monospace, monospace;
            color: #7a1f1f; text-align: right; }
  .crit-v { flex: 1; min-width: 0; color: #222; word-break: break-word; }
  .crit-case { margin: .55rem 0 .2rem; font-size: .82rem; color: #555; }
  .crit-block { white-space: normal; line-height: 1.45; }
  .hm-logo { display: block; margin: 0 auto .9rem; max-height: 90px;
             width: auto; }
  hr.divider { border: 0; border-top: 1px solid #999; margin: .55rem auto;
               width: 40%; }
  .rawgap { height: .8rem; }
  /* BAP headmatter uses several small, source-faithful vertical gaps.  Keep
     them visible, but avoid turning the caption into a long stack of blank
     space in the review view. */
  .headmatter.court-bap6 .rawgap { height: .35rem; }
  .headmatter.court-bap6 .hmline { line-height: 1.05; }
  .headmatter.court-bap6 .caption-cols .rawline { line-height: 1.05; }
  .empty { color: var(--muted); font-style: italic; }
  .hm-fac { position: relative; font-family: "Times New Roman", Georgia, serif;
            color: var(--ink); margin: .25rem 0 .5rem; }
  .hm-fac .hm-line { position: absolute; white-space: nowrap; line-height: 1; }
  .hm-fac .hm-rule { position: absolute; }
  /* Each opinion runs behind a colour-keyed rail down its left edge, so a
     document carrying more than one writing reads as separate opinions at a
     glance — where the majority ends and the dissent begins is visible without
     reading. The badge takes its colour from the SAME variable, so the label
     and the rail can never disagree. */
  section.opinion { --op-accent: var(--muted);
                    margin-top: 2rem; padding: 1.25rem 0 .5rem 1.1rem;
                    border-top: 1px solid var(--rule);
                    border-left: 4px solid var(--op-accent); }
  section.opinion:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
  section.opinion.t-majority { --op-accent: #2f5d3a; }
  section.opinion.t-dissent { --op-accent: #7a1f1f; }
  section.opinion.t-concurrence { --op-accent: #1f4e7a; }
  section.opinion.t-concurrence-in-result { --op-accent: #6a4a1f; }
  section.opinion.t-concurring-in-part-and-dissenting-in-part
                                          { --op-accent: #6b3f8a; }
  section.opinion.t-order { --op-accent: #55606b; }
  .opinion-caption { margin: .8rem 0 1.1rem; padding: .7rem 1rem;
    border-top: 1px solid #bbb; border-bottom: 1px solid #bbb; }
  .opinion-caption p, .opinion-caption blockquote { margin: .35rem 0; }
  .opinion-caption h3 { margin: .25rem 0 .7rem; }
  .opinion-signature { margin: 1rem 0; text-align: center; }
  .opinion-signature img { max-width: 100%; max-height: 90pt; }
  .author { font-variant: small-caps; font-weight: bold; font-size: 1.05rem;
            margin: .5rem 0 1rem; }
  .optype-badge { display: inline-block; font-family: ui-monospace, monospace;
            font-size: .72rem; font-weight: bold; text-transform: uppercase;
            letter-spacing: .06em; color: #fff; background: var(--op-accent);
            padding: .15rem .55rem; border-radius: .25rem; }
  p { text-align: justify; margin: .85rem 0; }
  blockquote { margin: .85rem 0 .85rem 2rem; color: #333; }
  section.opinion table { width: 100%; margin: 1rem 0;
                          border-collapse: collapse; border: 2px solid #555; }
  section.opinion table th, section.opinion table td {
    border: 1px solid #777; padding: .45rem .55rem; vertical-align: top;
  }
  section.opinion table th { background: #eee; text-align: left; }
  .trailer table { width: 100%; margin: 1rem 0; border-collapse: collapse;
                   border: 2px solid #555; }
  .trailer table td, .trailer table th { border: 1px solid #777;
                                        padding: .45rem .55rem; vertical-align: top; }
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
  .flushright { display: block; text-align: right; }
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
    if doc.non_digital:
        # Two different faults land here: a raster scan, and a born-digital PDF
        # whose font ships no character map. Name the one that actually applies
        # — 'scanned image' on a CID-broken file sends review down the wrong path.
        if getattr(doc, "cid_glyphs", 0):
            out.append(
                '<div class="warnings">🔤 unreadable text layer — '
                f"{doc.cid_glyphs} unmapped <code>(cid:N)</code> glyphs. The "
                "PDF's font declares glyphs but no character mapping, so the "
                "text extracts as glyph ids rather than characters. Not "
                "processed: the page geometry is intact, so this would "
                "otherwise parse into an opinion made of noise.</div>"
            )
        else:
            out.append(
                '<div class="warnings">🖼 non-born-digital document '
                "(scanned image + OCR text layer) — not processed. The engine "
                "relies on authored page geometry, which an OCR’d scan does not "
                "provide.</div>"
            )
        return out
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
    out.extend(_render_criteria(doc))
    out.extend(_render_headnotes(doc))
    out.extend(_render_syllabus(doc))
    out.extend(_render_attorneys(doc))
    out.extend(_render_opinions(doc))
    out.extend(_render_signature(doc))
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
  .opinion table { margin: 1rem 0; border: 1px solid #999; }
  .opinion table th, .opinion table td { border: 1px solid #bbb; }
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
    if doc.doc_type == "filing":
        return "Attorney filing"
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


def _caption_style(doc: ExtractedDocument):
    """Best-effort caption style name from the /captions catalog, derived
    from the structural signals extraction already found (rail glyph, drawn
    rules, corner close, divider rows). Exact names only where the signal is
    decisive; a descriptive label otherwise; None when there is no caption."""
    cap = next(
        (s for s in doc.summary if isinstance(s, dict) and s.get("__caption__")),
        None,
    )
    summary_text = [str(s) for s in doc.summary if not isinstance(s, dict)]
    has_divider = any(s == "__DIVIDER__" for s in summary_text)
    star_rows = any(
        isinstance(s, dict)
        and s.get("__hm__")
        and set(str(s.get("html", "")).replace("<", "").replace(">", "")) <= set("* ")
        for s in doc.summary
    )
    fp = (doc.caption_box or {}).get("fp_style")
    if fp:
        return fp
    if cap is None:
        if has_divider:
            return "one-column, ruled"
        return None
    rail = cap.get("rail", "__legacy__")
    if cap.get("boxes"):
        return "The Double Box"
    if rail == "|" or (rail == "__legacy__" and (doc.caption_box or {}).get("vx")):
        return "Old Faithful" if cap.get("corner") else "Old Faithful (open)"
    names = {
        ")": "The Banded Bracket" if has_divider else "The Parenthetical Box",
        "§": "The Section-Sign Rail",
        ":": "The Colon Rail",
        "]": "The Square-Bracket Rail",
        "*": "The Asterisk Rail",
        "}": "The Gathering Brace",
    }
    if isinstance(rail, str) and rail in names:
        return names[rail]
    if rail is None:
        if star_rows:
            return "The Starbreak"
        if has_divider:
            return "The Rule Sandwich"
        return "two-column (whitespace)"
    return None


def _render_fingerprint(doc: ExtractedDocument) -> list:
    fp = _fingerprint(doc)
    n_fn = sum(len(op.footnotes) for op in doc.opinions) + len(
        doc.headmatter_footnotes
    )
    types = " · ".join(op.type for op in doc.opinions) or "—"
    signals = [
        f"type: {escape(doc.doc_type)}",
        f"{len(doc.opinions)} opinion(s): {escape(types)}",
        f"{n_fn} footnote(s)",
        f"{doc.n_pages} pp.",
    ]
    cap_style = _caption_style(doc)
    if cap_style:
        signals.append(f"caption: {escape(cap_style)}")
    style_label = (doc.caption_box or {}).get("style_label")
    if style_label:
        signals.append(escape(str(style_label)))
    if getattr(doc, "cid_glyphs", 0):
        signals.append(f"⚠ {doc.cid_glyphs} unmapped glyph(s) (cid:)")
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
    residual = getattr(doc, "residual", None) or []
    if not doc.dropped and not residual:
        return []

    # Three DIFFERENT things, so three boxes with their own counts. Lumping
    # them under one 'notices / stamps (41)' total hid the only line that
    # actually needs work behind forty that don't.
    def _kind(r):
        return r.get("kind") if isinstance(r, dict) else None

    content = [r for r in residual if _kind(r) != "furniture"]
    furniture = [r for r in residual if _kind(r) == "furniture"]
    out: list = []

    def _box(label, cls="dropped", open_=False):
        out.append(f'<details class="{cls}"{" open" if open_ else ""}>')
        out.append(f"<summary>{label}</summary>")

    if content:
        # Unplaced CONTENT is the review to-do: real text the parse could not
        # place. Opened by default and styled apart from the junk.
        _box(
            f"Unplaced content — needs a home ({len(content)})",
            cls="dropped unplaced",
            open_=True,
        )
        for r in content:
            txt = r.get("text", "") if isinstance(r, dict) else str(r)
            pg = r.get("page") if isinstance(r, dict) else None
            tag = f'<span class="droppg">p{pg}</span> ' if pg else ""
            out.append(f'<div class="dropline">{tag}{_inline_to_html(str(txt))}</div>')
        out.append("</details>")

    if furniture:
        # Identified junk the sweep caught rather than the parse — a rail glyph,
        # a folio, a running head. Confirm the call, then it can be dropped.
        _box(f"Unplaced furniture — confirm &amp; drop ({len(furniture)})")
        for r in furniture:
            txt = r.get("text", "") if isinstance(r, dict) else str(r)
            pg = r.get("page") if isinstance(r, dict) else None
            tag = f'<span class="droppg">p{pg}</span> ' if pg else ""
            out.append(f'<div class="dropline">{tag}{_inline_to_html(str(txt))}</div>')
        out.append("</details>")

    if doc.dropped:
        # Deliberately removed by the extractor — a publication notice, a seal,
        # an e-filing stamp. Nothing to do; shown so it is never silent.
        _box(f"Removed before parsing — notices / stamps ({len(doc.dropped)})")
        for d in doc.dropped:
            out.append(f'<div class="dropline">{_inline_to_html(str(d))}</div>')
        out.append("</details>")
    return out


def _render_headnotes(doc: ExtractedDocument) -> list:
    """Reporter headnotes preceding the opinion (Maryland) — bold topical
    headings and their summary prose, their own section, not opinion body."""
    if not getattr(doc, "headnotes", None):
        return []
    out = [
        '<section class="block headnotes">',
        '<h2 class="sec">Headnotes '
        '<span class="raw-tag">not part of the opinion</span></h2>',
        '<div class="raw">',
    ]
    for line in doc.headnotes:
        if isinstance(line, dict) and line.get("__hm__"):
            al = {"C": "center", "L": "left", "R": "right"}.get(
                line.get("align"), "left"
            )
            ind = line.get("ind")
            pad = f"padding-left:{ind}pt;" if ind else ""
            # A first-line indent on a wrapped row (a counsel entry) indents
            # only its opening line, unlike the whole-row shift of ``ind``.
            tind = line.get("tind")
            if tind:
                pad += f"text-indent:{tind}pt;"
            out.append(
                f'<div class="hmline" style="{pad}text-align:{al};'
                f'font-size:{line.get("rel", 1)}em">'
                f'{_inline_to_html(str(line.get("html", "")))}</div>'
            )
        elif str(line).strip() == "":
            out.append('<div class="rawgap"></div>')
        else:
            out.append(f'<div class="rawline">{_inline_to_html(str(line))}</div>')
    out.append("</div></section>")
    return out


def _render_attorneys(doc: ExtractedDocument) -> list:
    """The COUNSEL block — who argued and who was on the brief.

    Its own section rather than a run of headmatter rows: the reporter prints
    it under its own heading, and leaving it in the caption made a page of
    counsel read as though it were part of the case caption."""
    text = getattr(doc, "attorneys", None)
    if not text:
        return []
    # The criteria panel already lists counsel when the headmatter parse found
    # it, and ``attorneys`` is mirrored from that same text — render it once,
    # in the parsed area, rather than twice under two headings.
    if (getattr(doc, "criteria", None) or {}).get("counsel"):
        return []
    out = [
        '<section class="block attorneys">',
        '<h2 class="sec">Counsel</h2>',
        '<div class="raw">',
    ]
    for line in str(text).split("\n"):
        if not line.strip():
            out.append('<div class="rawgap"></div>')
        else:
            out.append(f'<div class="rawline">{_inline_to_html(line)}</div>')
    out.append("</div></section>")
    return out


def _render_criteria(doc: ExtractedDocument) -> list:
    """The structured headmatter criteria, collapsed.

    Rendered — not merely stored — for two reasons. The reviewer needs to see
    what the dissection actually pulled out in order to trust it, and a row the
    court lifts OUT of the headmatter (CA11's 'FOR PUBLICATION') has no other
    home on the page; the audit only excuses text the reader can reach."""
    crit = getattr(doc, "criteria", None)
    if not crit:
        return []

    def row(label, value):
        return (
            f'<div class="crit-row"><span class="crit-k">{escape(str(label))}</span>'
            f'<span class="crit-v">{_inline_to_html(str(value))}</span></div>'
        )

    cases = crit.get("cases") or []
    n = len(cases)
    label = "Parsed criteria" + (f" · {n} cases heard together" if n > 1 else "")
    out = [
        '<section class="block criteria">',
        f'<details class="crit" open><summary class="sec">{escape(label)}'
        ' <span class="raw-tag">parsed</span></summary>',
        '<div class="crit-body">',
    ]
    def block_row(label, value):
        """A row whose value keeps its own line structure (caption, counsel)."""
        body = "<br>".join(
            _inline_to_html(line) if line.strip() else ""
            for line in str(value).split("\n")
        )
        return (
            f'<div class="crit-row"><span class="crit-k">{escape(str(label))}</span>'
            f'<span class="crit-v crit-block">{body}</span></div>'
        )

    for key in ("headmatter_style", "publication", "title", "court",
                "short_case_name", "term", "date_filed",
                "date_argued", "date_argued_and_submitted", "date_submitted",
                "date_decided", "date_decided_and_filed", "date_reargued",
                "date_amended", "summary", "panel_line", "disposition"):
        if crit.get(key):
            out.append(row(key.replace("_", " "), crit[key]))
    if crit.get("panel"):
        out.append(row("panel", " · ".join(crit["panel"])))
    for i, case in enumerate(cases, 1):
        head = f"case {i}" if n > 1 else "case"
        out.append(f'<div class="crit-case"><b>{escape(head)}</b></div>')
        for key in ("docket", "case_name", "prior_history",
                    "lower_court", "lower_docket", "lower_judge"):
            if case.get(key):
                out.append(row(key.replace("_", " "), case[key]))
        # The CAPTION keeps its own line structure — the party rows, their status
        # labels, the hinge, and the blank line where the page separates one
        # consolidated case's parties from the next. Flattened into one row it
        # reads as a run-on list.
        if case.get("caption_text"):
            out.append(block_row("caption", case["caption_text"]))
    if crit.get("counsel"):
        # ONE BLOCK, spacing intact — the empty rows are what separate one
        # side's appearance from the other's. Listed line by line under a
        # repeated label the entries ran together.
        body = "<br>".join(
            _inline_to_html(line) if line.strip() else ""
            for line in str(crit["counsel"]).split("\n")
        )
        out.append(
            '<div class="crit-row"><span class="crit-k">counsel</span>'
            f'<span class="crit-v crit-block">{body}</span></div>'
        )
    out.append("</div></details></section>")
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
        if isinstance(line, dict) and line.get("__hm__"):
            # A styled syllabus paragraph (SCOTUS): real flowing text with
            # inline bold/italic, same row treatment as styled headmatter.
            al = {"C": "center", "L": "left", "R": "right"}.get(
                line.get("align"), "left"
            )
            out.append(
                f'<div class="hmline" style="text-align:{al};'
                f'font-size:{line.get("rel", 1)}em">'
                f'{_inline_to_html(str(line.get("html", "")))}</div>'
            )
        elif str(line).strip() == "":
            out.append('<div class="rawgap"></div>')
        else:
            out.append(f'<div class="rawline">{_inline_to_html(str(line))}</div>')
    out.append("</div></section>")
    return out


def _caption_cell_lines(entries) -> list:
    """Caption cell lines, faithful to the page: inline bold/italic kept,
    per-line indents preserved (a role line indented under its party), and
    blank spacer rows where the caption is double-spaced. Plain strings
    (older stored summaries) still render as before."""
    out = []
    for ln in entries:
        if isinstance(ln, dict) and ln.get("__shelf__"):
            # a DRAWN caption rule at its true side — the shelf under a party
            # column, or the full rule between stacked consolidated captions
            out.append(
                '<div style="border-bottom:1px solid #999;'
                'height:.3rem;margin-bottom:.3rem"></div>'
            )
            continue
        if isinstance(ln, dict):
            ind = ln.get("ind") or 0
            style = (
                f' style="padding-left:{min(round(ind * 0.9), 160)}px"'
                if ind > 14
                else ""
            )
            out.append(
                f'<div class="rawline"{style}>'
                f'{_inline_to_html(str(ln.get("h", "")))}</div>'
            )
        elif str(ln).strip() == "":
            out.append('<div style="height:.55rem"></div>')
        else:
            out.append(
                f'<div class="rawline">{_inline_to_html(str(ln))}</div>'
            )
    return out


def _render_signature(doc: ExtractedDocument) -> list:
    """The signature block lifted off the end of the last opinion — the
    '/s/' conformed signature or signature rule, the printed name, and the
    signer's title — in its own box so it isn't read as opinion body."""
    if not doc.signature:
        return []
    out = [
        '<section class="block signature">',
        '<h2 class="sec">Signature</h2>',
        '<div class="raw">',
    ]
    for line in doc.signature:
        if isinstance(line, dict) and line.get("__image__"):
            h = line.get("height") or 54
            out.append(
                f'<img src="{escape(str(line.get("src", "")))}" '
                f'alt="signature" style="display:block;max-height:{round(h)}px">'
            )
        else:
            out.append(
                f'<div class="rawline">{_inline_to_html(str(line))}</div>'
            )
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
        if isinstance(line, dict) and line.get("__table__"):
            out.extend(_render_table(line.get("rows") or []))
        elif isinstance(line, Block):
            if line.kind == "image":
                w = line.payload.get("width")
                size = (
                    f' style="width:{round(w)}pt;max-width:100%;height:auto"'
                    if w
                    else ""
                )
                out.append(
                    f'<img src="{escape(str(line.payload.get("src", "")))}" '
                    f'alt="figure on page {line.page}"{size}>'
                )
            else:
                out.append(
                    f'<div class="rawline">{_inline_to_html(line.text)}</div>'
                )
        else:
            out.append(f'<div class="rawline">{_inline_to_html(str(line))}</div>')
    out.append("</div></section>")
    return out


def _stack_headmatter_pages(lines: list) -> list:
    """Headmatter that spans pages carries each line's own page-local y, so
    absolute positioning would overlay page 2's top on page 1's top. Shift
    every page after the first to start just below the previous page's last
    line, preserving page-local geometry. Page-1 coordinates are untouched, so
    the caption-box rules (page-1 geometry) stay aligned."""
    pages = sorted({l.get("page", 1) for l in lines})
    if len(pages) <= 1:
        return lines
    out, cursor = [], None
    for pno in pages:
        pls = [l for l in lines if l.get("page", 1) == pno]
        top0 = min(l["top"] for l in pls)
        off = 0.0 if cursor is None else cursor - top0
        out += [{**l, "top": l["top"] + off} for l in pls]
        cursor = max(l["top"] + off + l["size"] * 1.3 for l in pls) + 14
    return out


def _render_headmatter_facsimile(doc: ExtractedDocument) -> list:
    """Faithful headmatter: each line placed at its real x/y, at its real font
    size and weight, with the caption box drawn from the rule geometry. 1px per
    PDF point."""
    lines = _stack_headmatter_pages(doc.headmatter_lines)

    # PDF fonts are often embedded and unavailable to the browser. A fallback
    # font can therefore be a little wider than the source font and make two
    # same-row caption lines touch even though their measured PDF x positions
    # do not. Preserve the source geometry by default, but make the smallest
    # rightward adjustment needed to prevent a visual collision.
    def approx_width(line):
        size = float(line.get("size") or 10)
        text = str(line.get("text") or "")
        width = 0.0
        for ch in text:
            if ch in " ilI.,'":
                factor = 0.27
            elif ch in "MW@%":
                factor = 0.82
            else:
                factor = 0.52
            width += factor * size
        return width

    adjusted = []
    for line in lines:
        item = dict(line)
        for prior in adjusted:
            if prior.get("page", 1) != item.get("page", 1):
                continue
            prior_top = float(prior.get("top") or 0)
            item_top = float(item.get("top") or 0)
            prior_size = float(prior.get("size") or 10)
            item_size = float(item.get("size") or 10)
            if abs(prior_top - item_top) > max(prior_size, item_size) * 0.9:
                continue
            prior_x = float(prior.get("x0") or 0)
            item_x = float(item.get("x0") or 0)
            if item_x <= prior_x:
                needed = item_x + approx_width(item) + 10
                if prior_x < needed:
                    prior["x0"] = needed
                continue
            needed = prior_x + approx_width(prior) + 10
            if item_x < needed:
                item["x0"] = needed
        adjusted.append(item)
    lines = adjusted
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
    court_class = " court-bap6" if doc.court_id == "bap6" else ""
    # When the headmatter has been DISSECTED, the parsed panel above is the
    # useful view and this raw dump is the backup — so collapse it. Where no
    # criteria were parsed the dump is all there is, and it stays open.
    parsed = bool(getattr(doc, "criteria", None))
    if parsed:
        out = [
            f'<section class="block headmatter{court_class}">',
            '<details class="crit"><summary class="sec">Headmatter'
            ' <span class="raw-tag">raw</span></summary>',
        ]
    else:
        out = [
            f'<section class="block headmatter{court_class}">',
            '<h2 class="sec">Headmatter <span class="raw-tag">raw</span></h2>',
        ]
    if (
        doc.summary
        and isinstance(doc.summary[0], dict)
        and doc.summary[0].get("__facsimile__")
        and doc.headmatter_lines
    ):
        # Style/whitespace-preserving facsimile (exact x/y, size, weight);
        # the plain rows behind the sentinel exist for the audit and DB.
        out.append('<div class="raw">')
        out.extend(_render_headmatter_facsimile(doc))
        out.append("</div>")
    elif not doc.summary:
        out.append('<div class="empty">(none)</div>')
    else:
        out.append('<div class="raw">')
        for s in doc.summary:
            if isinstance(s, dict) and s.get("__image__"):
                # The court seal / logo, placed above the caption.
                out.append(
                    f'<img class="hm-logo" src="{escape(str(s.get("src", "")))}" '
                    'alt="court seal">'
                )
            elif isinstance(s, dict) and s.get("__caption__"):
                # A two-column caption box (left = parties, right = docket).
                # The divider mirrors the SOURCE: a stacked rail-glyph column
                # (')' / '§' / ':') where the PDF uses glyphs, nothing where
                # the columns are separated by whitespace alone, and the
                # legacy drawn rule only when the producer didn't say.
                out.append(
                    '<div class="caption-cols" style="display:flex;'
                    'gap:1.4rem;align-items:stretch">'
                )
                # 'Old Faithful' close: the half-rule under the parties that
                # runs into the vertical renders as the left column's bottom
                # border, meeting the divider at the corner.
                shape = s.get("shape")
                lstyle = "flex:1;min-width:0"
                if s.get("boxes") or shape == "double-box":
                    lstyle += ";border:1px solid #999;padding:.4rem .6rem"
                elif shape == "i-beam":
                    lstyle += (";border-top:1px solid #999"
                               ";border-bottom:1px solid #999")
                elif shape == "backwards-c":
                    lstyle += (";border-top:1px solid #999"
                               ";border-bottom:1px solid #999")
                elif shape == "upside-down-t":
                    lstyle += ";border-bottom:1px solid #999"
                elif s.get("corner") or shape == "old-faithful":
                    lstyle += ";border-bottom:1px solid #999"
                out.append(f'<div style="{lstyle}">')
                out.extend(_caption_cell_lines(s.get("left", [])))
                rail = s.get("rail", "__legacy__")
                shape = s.get("shape")
                if s.get("boxes") or shape == "double-box":
                    mid_div = '<div style="flex:none;width:.2rem"></div>'
                elif shape == "twin-rail":
                    mid_div = '<div style="border-left:3px double #999"></div>'
                elif shape in ("i-beam", "backwards-c", "upside-down-t",
                               "old-faithful"):
                    mid_div = '<div style="border-left:1px solid #999"></div>'
                elif rail == "__legacy__" or rail == "|":
                    # '|' = the PDF draws a real vertical rule here.
                    mid_div = '<div style="border-left:1px solid #999"></div>'
                elif rail:
                    # draw exactly one rail glyph per SOURCE row that bore it
                    # (the PDF draws a ')' per caption row); never one-per-cell,
                    # which invents glyphs for banner / blank rows. Falls back
                    # to the non-blank cell count for older stored summaries.
                    n = s.get("rail_rows")
                    if not n:
                        n = max(
                            sum(1 for x in s.get("left", []) if str(x).strip()),
                            sum(1 for x in s.get("right", []) if str(x).strip()),
                            1,
                        )
                    glyphs = "<br>".join([escape(str(rail))] * n)
                    mid_div = (
                        '<div class="rawline" style="color:#8a8374;'
                        f'text-align:center;flex:none">{glyphs}</div>'
                    )
                else:
                    mid_div = '<div style="flex:none;width:.2rem"></div>'
                rstyle = "flex:1;min-width:0"
                shape = s.get("shape")
                if s.get("boxes") or shape == "double-box":
                    rstyle += ";border:1px solid #999;padding:.4rem .6rem"
                elif shape == "i-beam":
                    rstyle += (";border-top:1px solid #999"
                               ";border-bottom:1px solid #999")
                elif shape == "upside-down-t":
                    rstyle += ";border-bottom:1px solid #999"
                elif shape == "status-flush":
                    # status labels are pinned against the right margin
                    rstyle += ";text-align:right"
                out.append(f"</div>{mid_div}" f'<div style="{rstyle}">')
                out.extend(_caption_cell_lines(s.get("right", [])))
                out.append("</div></div>")
            elif isinstance(s, dict) and s.get("__hmrow__"):
                # A three-zone flush-right row: party at the left margin,
                # status label pinned right, docket centered between them.
                # Equal 1fr side tracks keep the center cell truly centered.
                out.append(
                    '<div class="hmline" style="display:grid;'
                    'grid-template-columns:1fr auto 1fr;column-gap:.6rem">'
                    f'<div>{_inline_to_html(str(s.get("l", "")))}</div>'
                    '<div style="text-align:center">'
                    f'{_inline_to_html(str(s.get("c", "")))}</div>'
                    '<div style="text-align:right">'
                    f'{_inline_to_html(str(s.get("r", "")))}</div>'
                    "</div>"
                )
            elif isinstance(s, dict) and s.get("__hm__"):
                # A style-preserving headmatter line: relative font size,
                # alignment, and inline bold/italic kept from the PDF.
                al = {"C": "center", "L": "left", "R": "right"}.get(
                    s.get("align"), "left"
                )
                # 'ind' is the row's offset from the caption block's own left
                # edge, in PDF points — the same unit as CSS pt — so a role
                # line stays under its party and a docket number stays out to
                # the right, exactly as printed.
                ind = s.get("ind")
                pad = f"padding-left:{ind}pt;" if ind else ""
                zones = s.get("zones")
                if zones and len(zones) > 1:
                    # The row holds separate COLUMNS on one baseline (a party at
                    # the left margin, its status flush right). Lay them out so
                    # each keeps the side it was printed on instead of
                    # collapsing the gap between them to a single space.
                    cells = "".join(
                        '<div style="text-align:{}">{}</div>'.format(
                            "right" if z.get("align") == "r" else "left",
                            _inline_to_html(str(z.get("h", ""))),
                        )
                        for z in zones
                    )
                    out.append(
                        f'<div class="hmline" style="{pad}display:flex;'
                        f'justify-content:space-between;column-gap:1rem;'
                        f'font-size:{s.get("rel", 1)}em">{cells}</div>'
                    )
                else:
                    out.append(
                        f'<div class="hmline" style="{pad}text-align:{al};'
                        f'font-size:{s.get("rel", 1)}em">'
                        f'{_inline_to_html(str(s.get("html", "")))}</div>'
                    )
            elif isinstance(s, dict):
                out.append(f'<div class="rawline">{escape(str(s))}</div>')
            elif str(s).strip() == "__RULE__":
                # a DRAWN full-width rule at its position
                out.append('<hr style="border:0;border-top:1px solid #999;margin:.55rem 0">')
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
    if parsed:
        out.append("</details>")
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


def _quote_style(payload) -> str:
    """Inline a block quote's own measure — the page's proportions, not points.

    ``inset_left_pct`` / ``inset_right_pct`` are fractions of the opinion's
    body measure, so the quote keeps the same relative width whatever the
    review column's width happens to be; absolute points overshot badly for a
    quote inset a full inch on a 6.5in page. Falls back to the legacy absolute
    ``indent`` when the fractions are absent.
    """
    if not payload:
        return ""
    left = payload.get("inset_left_pct")
    if left is not None:
        right = payload.get("inset_right_pct") or 0
        return f' style="margin-left:{left}%;margin-right:{right}%"'
    extra = payload.get("indent", 0)
    return f' style="margin-left:calc(2rem + {extra}pt)"' if extra else ""


def _render_opinion(op: Opinion) -> list:
    # The type rides on the SECTION, not just the badge — it keys the rail
    # colour for the whole writing, footnotes included.
    out = [f'<section class="opinion t-{escape(op.type)}">']
    out.append(
        f'<div class="optype-badge t-{escape(op.type)}">' f"{escape(op.type)}</div>"
    )
    visible_byline = False
    if getattr(op, "caption", None):
        out.append('<div class="opinion-caption">')
        for b in op.caption:
            role = (b.payload or {}).get("role")
            visible_byline = visible_byline or role in ("byline", "announcement")
            if b.kind == "heading":
                out.append(f"<h3>{_inline_to_html(b.text)}</h3>")
            elif b.kind == "blockquote":
                out.append(
                    f"<blockquote{_quote_style(b.payload)}>"
                    f"{_inline_to_html(b.text)}</blockquote>"
                )
            elif b.kind == "image":
                out.append(
                    f'<img src="{escape(str(b.payload.get("src", "")))}" '
                    f'alt="caption figure on page {b.page}">'
                )
            else:
                out.append(f"<p>{_inline_to_html(b.text)}</p>")
        out.append("</div>")
    if not visible_byline:
        out.append(f'<div class="author">{escape(op.author)}</div>')
    list_tag = None
    for b in op.blocks:
        if b.kind in ("list-item", "ordered-list-item"):
            wanted_tag = "ol" if b.kind == "ordered-list-item" else "ul"
            if list_tag != wanted_tag:
                if list_tag is not None:
                    out.append(f"</{list_tag}>")
                out.append(f"<{wanted_tag}>")
                list_tag = wanted_tag
            text = b.text
            if b.kind == "ordered-list-item":
                _marker, _separator, text = text.lstrip().partition(" ")
                text = text.lstrip()
            out.append(f"<li>{_inline_to_html(text)}</li>")
            continue
        if list_tag is not None:
            out.append(f"</{list_tag}>")
            list_tag = None
        if b.kind == "image":
            # Render at the figure's true size on the page — the payload
            # carries the PDF-point box, and CSS pt maps 1:1 to it (the PNG
            # itself is rasterized at 150dpi and would display ~2x too big).
            w = b.payload.get("width")
            size = (
                f' style="width:{round(w)}pt;max-width:100%;height:auto"'
                if w
                else ""
            )
            out.append(
                f'<img src="{escape(str(b.payload.get("src", "")))}" '
                f'alt="figure on page {b.page}"{size}>'
            )
        elif b.kind == "table":
            out.extend(
                _render_table(
                    b.payload.get("rows") or [],
                    has_header=b.payload.get("has_header", True),
                    continued=b.payload.get("continuation", False),
                )
            )
        elif b.kind == "p" and b.payload.get("first_line_indent"):
            indent = float(b.payload["first_line_indent"])
            out.append(
                f'<p style="text-indent:{indent:.1f}pt">'
                f'{_inline_to_html(b.text)}</p>'
            )
        elif b.kind == "heading":
            out.append(f"<h3>{_inline_to_html(b.text)}</h3>")
        elif b.kind == "rule":
            # a rule DRAWN on the page at this point in the flow (wvnd's
            # full-width line under the document-type title)
            out.append('<hr class="divider">')
        elif b.kind == "blockquote":
            out.append(
                f"<blockquote{_quote_style(b.payload)}>"
                f"{_inline_to_html(b.text)}</blockquote>"
            )
        else:
            out.append(f"<p>{_inline_to_html(b.text)}</p>")
    if list_tag is not None:
        out.append(f"</{list_tag}>")
    if getattr(op, "signature", None):
        out.append('<div class="opinion-signature">')
        for item in op.signature:
            if isinstance(item, dict) and item.get("__image__"):
                out.append(
                    f'<img src="{escape(str(item.get("src", "")))}" '
                    'alt="opinion signature">'
                )
            else:
                out.append(f"<div>{_inline_to_html(str(item))}</div>")
        out.append("</div>")
    if op.footnotes:
        out.append('<div class="footnotes">')
        for fn in op.footnotes:
            out.append(_render_footnote(fn))
        out.append("</div>")
    out.append("</section>")
    return out


def _render_footnote(fn: Footnote) -> str:
    def piece(tag, text):
        if tag == "table":
            # Already-escaped markup built by the extractor: a table printed
            # inside the footnote itself, emitted verbatim.
            return str(text)
        if tag == "blockquote":
            return f"<blockquote>{_inline_to_html(text)}</blockquote>"
        return f"<span>{_inline_to_html(text)}</span> "

    body = "".join(piece(tag, text) for tag, text in fn.paragraphs)
    return (
        f'<div class="footnote">'
        f'<span class="label">{escape(fn.label)}</span>{body}</div>'
    )


def _render_table(rows: list, has_header=True, continued=False) -> list:
    if not rows:
        return []
    out = ['<table class="continued">' if continued else "<table>"]
    for ri, row in enumerate(rows):
        tag = "th" if has_header and ri == 0 else "td"
        # Keep the cell's internal line breaks — a multi-line citation cell
        # ('State v. Clark,\n2022 ND 85\n999 N.W.2d 632') reads as the PDF
        # stacks it, not as one run-on line.
        cells = "".join(
            f"<{tag}>{escape((c or '').strip()).replace(chr(10), '<br>')}</{tag}>"
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
        .replace("<flushright>", '<span class="flushright">')
        .replace("</flushright>", "</span>")
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
