"""The review HTML page — the surface the user actually eyeballs.

Iterates SECTION_SPEC; dispatch is typed (see facsimile.render_hm_items and
_render_blocks). A section that is empty renders nothing. The Removed box and
the residual worklist render up top, because that is the reviewer's first
question: what did the extractor do with everything?
"""

from __future__ import annotations

import re

from html import escape

from .. import model as m
from ..sections import SECTIONS
from .facsimile import render_hm_items
from .inline import inline_to_html

_CSS = """
/* A HIGHLIGHTER'S FILL, reproduced. The page painted a colour behind these
   glyphs; `<mark>` says so, and the review sheet must not let a UA default
   wash it out. Kept legible against the dark review background. */
mark{background:#ffe95c;color:#111;padding:0 .05em;border-radius:2px}

:root { --ink:#1a1a1a; --mut:#777; --line:#ddd; --accent:#6b4b9a; --bad:#b3372f; }
* { box-sizing:border-box }
/* The measure FOLLOWS THE PANE. A flat 820px squeezed the document when the
   review viewer showed the PDF beside it, and then refused to use the room
   when the PDF was closed. It now grows to 1180px when there is space and
   falls back to 94vw when there is not — and the left gutter that the
   headmatter's margin labels live in (left:-96px) grows with it, so those
   labels stop being clipped in the narrow split view. */
body { font:15px/1.5 Georgia,'Times New Roman',serif; color:var(--ink);
       max-width:min(1180px, 94vw); margin:1.5em auto 6em;
       padding:0 1.5em 0 clamp(1.5em, 8vw, 6.5em); background:#fdfdfc }
h1 { font-size:1.15em; margin:.2em 0 }
.meta { color:var(--mut); font:12px system-ui,sans-serif; margin-bottom:1.2em }
.chip { display:inline-block; font:600 11px system-ui,sans-serif; color:#fff;
        background:var(--accent); border-radius:9px; padding:1px 9px; margin-right:.4em }
.chip.warn { background:var(--bad) }
.chip.kind { background:#8a8a8a }
/* THE SOURCE BANNER. A scan's OCR text reads like any other text — that is
   exactly the danger, so the page says so before it says anything else. The
   warning chip alone was a tooltip on a glyph; this is unmissable and its
   colour is the one the sheet already reserves for a defect. */
.srcbanner { border:1px solid var(--bad); border-left-width:6px; border-radius:4px;
             background:#fdf3f2; color:#7a2620; padding:.6em .9em; margin:0 0 1.1em;
             font:13px/1.45 system-ui,sans-serif }
.srcbanner b { font:700 13px system-ui,sans-serif; letter-spacing:.02em }
.srcbanner code { font:12px ui-monospace,Menlo,monospace; background:#fff;
                  border:1px solid #e6cfcd; border-radius:3px; padding:0 4px }
section { margin:1.4em 0 }
section > h2 { font:600 12px system-ui,sans-serif; text-transform:uppercase;
               letter-spacing:.08em; color:var(--mut); border-bottom:1px solid var(--line);
               padding-bottom:2px }
.box { border:1px solid var(--line); border-radius:6px; padding:.7em 1em;
       font-size:.92em; background:#f7f6f4 }
.box.removed div { color:var(--mut) }
/* ONE GROUP PER CASE inside the criteria box: the heading names the case,
   the rows under it are that case's own. */
.caseline { margin:.55em 0 .1em; color:#555; font:12px system-ui,sans-serif }
.caserow { padding-left:1.1em }
.box.residual .content { color:var(--bad) }
details { margin:.8em 0 }
details > summary { font:600 12px system-ui,sans-serif; text-transform:uppercase;
  letter-spacing:.08em; color:var(--mut); cursor:pointer; user-select:none }
.hmrow { min-height:1.2em; white-space:pre-wrap; margin:.24em 0 }
.hmrow.ac { text-align:center } .hmrow.ar { text-align:right }
.hmrow.rel { transform:translateX(var(--rel)) }
/* How the headmatter was READ, shown in place — the block renders whole and
   the tints say which rows a court reader identified as what. */
.hmrow[data-role] { border-left:3px solid transparent; padding-left:6px }
/* COURT: the court naming itself — its name, its division, its seat, the
   term it sits in. Called `banner` until 2026-08-19, which conflated it with
   the publication flag printed in the same band (the user's call: a banner
   that names the court IS the court). */
.hmrow[data-role="court"]   { background:#eef4ff; border-left-color:#8ab }
.hmrow[data-role="banner"]  { background:#eef4ff; border-left-color:#8ab }
.hmrow[data-role="title"]   { background:#eef4ff; border-left-color:#8ab }
/* PUBLICATION: 'PUBLISHED' / 'NOT FOR PUBLICATION' / 'NOT PRECEDENTIAL' —
   ~500 rows that were tinted as if they named the court. */
.hmrow[data-role="publication"] { background:#f7f0ff; border-left-color:#b9a6de }
/* CITATION: the court's own public-domain cite ('Slip Opinion No.
   2026-Ohio-2065', '2026 IL 130930') — read as a banner it looked like the
   court naming itself, and as a docket it displaced the real one. */
.hmrow[data-role="citation"] { background:#eef7f4; border-left-color:#8bb3a5 }
/* HEADNOTES: the Reporter of Decisions' SUBJECT list, not a summary of the
   case — 'Pretrial Detention. Robbery. Dangerous Weapon.' (mass);
   'Attorneys—Misconduct—…—Public reprimand.' (ohio). The user's call,
   2026-08-19: these are headnotes, and a précis is a different thing. */
.hmrow[data-role="headnotes"] { background:#f6f6f2; border-left-color:#c2c0a8 }
/* A SYLLABUS IS NOT HEADNOTES. Kansas (and wva) print numbered points of
   law BY THE COURT in the headmatter; headnotes are the reporter's subject
   list. Same band of the page, different authorship, so a different tint. */
.hmrow[data-role="syllabus"] { background:#f2f4f6; border-left-color:#a8b6c2 }
/* AUTHOR: who the caption says wrote it, where the court ANNOUNCES the
   author instead of signing the writing ('OPINION BY' over 'JUSTICE WESLEY
   G. RUSSELL, JR.' — va). Distinct from `panel`: va prints a real roster
   row ('PRESENT: Powell, Kelsey, …') in the same block, and one label for
   both made two different things look alike. */
.hmrow[data-role="author"] { background:#eefaf2; border-left-color:#7bbf95 }
.hmrow[data-role="docket"]  { background:#f3f0ff; border-left-color:#a9b }
.hmrow[data-role="date"]    { background:#f3f0ff; border-left-color:#a9b }
.hmrow[data-role="panel"]   { background:#eefaf2; border-left-color:#8c9 }
.hmrow[data-role="caption"] { background:#fff8e8; border-left-color:#dc9 }
.hmrow[data-role="counsel"] { background:#fdeef4; border-left-color:#d9b }
.hmrow[data-role="summary"] { background:#f6f6f6; border-left-color:#bbb }
.hmrow[data-role="lower-court"] { background:#eef9fb; border-left-color:#7bb }
.hmrow.role-start[data-role="lower-court"]::before { content:"lower court" }
/* CASE INFO: apparatus the caption carries that is none of the named parts.
   A bankruptcy caption's 'Chapter 7' row is the case's identity, not its
   docket, and tinting it as a docket said the reader had found a number. */
.hmrow[data-role="case-info"] { background:#f4f2ee; border-left-color:#c9ba9a }
/* DISPOSITION: what the court DID, stated in the headmatter ('WRIT GRANTED',
   'AFFIRMED') — wva fences it as a band of its own. */
.hmrow[data-role="disposition"] { background:#f0f7ee; border-left-color:#9c8 }
.hmrow.role-start[data-role="case-info"]::before { content:"case info" }
/* …and a rule down the WHOLE block, so a recognized headmatter reads as one
   thing and the opinion below it plainly starts somewhere else. */
section.sec-headmatter, section.sec-endmatter {
  border-left:2px solid #d8d8d8; padding-left:10px; margin-left:2px }
/* THE COURT'S SEAL stands at the head of the block, centred, as the page
   sets it — not inside the opinion, which is not where it belongs. */
img.hm-img { display:block; margin:.2em auto .6em; max-width:180px; height:auto }
.hm-legend { font:11px system-ui,sans-serif; color:#888; margin:.2em 0 .6em }
.hm-legend b { font-weight:600; padding:1px 6px; margin-right:4px;
               border-radius:3px; border-left:3px solid transparent }
/* the margin label — named where each run of one role begins */
section.sec-headmatter, section.sec-endmatter {
  padding-left:136px; padding-right:136px }
.hmrow.role-start { position:relative }
/* THE MARGIN LABEL sits in the gutter, and the gutter has to fit the longest
   name in the vocabulary. At 78px 'lower court' wrapped to two lines and
   collided with the row beneath it, and 'headnotes' overran into the row's
   own first word. The vocabulary grew on 2026-08-19 (publication, citation,
   headnotes, disposition, case info, author), so the gutter grew with it and
   the label is kept to ONE line — a label that wraps is a label in the way. */
.hmrow.role-start::before {
  content:attr(data-role); position:absolute; left:-136px; width:118px;
  text-align:right; font:10px/1.7 system-ui,sans-serif; color:#9a9a9a;
  text-transform:uppercase; letter-spacing:.04em; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; pointer-events:none }
/* A caption's RIGHT column is a second stack of rows, and its label belongs
   in the margin beside IT — named in the left gutter it lands on top of the
   left column's own text. The block keeps a gutter on both sides. */
.cap-right .hmrow.role-start::before {
  left:auto; right:-136px; text-align:left }
.caption { display:grid; grid-template-columns:1fr auto 1fr; gap:0 10px; margin:.6em 0 }
.rail.drawn { border-left:1.5px solid var(--ink) }
.rail.glyphs { display:flex; flex-direction:column; justify-content:space-between;
               font-family:inherit }
.rail.open { width:14px }
.pgbreak { font:600 10px system-ui,sans-serif; color:#999; text-align:center;
           border-top:1px dashed #ccc; margin:.9em 0 .5em; padding-top:2px }
[data-pg] { cursor:default }
.rule { border-bottom:1.5px solid var(--ink); margin:.45em 0 }
.rule.span-left { margin-right:50% } .rule.span-right { margin-left:50% }
.rule.span-center { width:44px; margin:.55em auto }
p.sig-right { margin-left:48% }
/* A SIGNATURE THAT IS A PICTURE: an ECF order is signed with a stamp, and
   kyed's judge's name exists only as pixels. Sized to the page's own scale
   rather than the measure, so it reads as a signature and not a figure. */
.sig img { display:block; max-width:320px; height:auto; margin:.4em 0 }
.typedrule { border-bottom:1.5px dashed var(--ink); margin:.45em 0 }
.divider { height:.6em }
p { margin:.55em 0; text-indent:1.6em }
p.noindent { text-indent:0 }
blockquote { margin:.7em 2.2em; font-size:.95em }
h3.bhead { font-size:1em; text-align:center; margin:1em 0 .4em }
table.tb { border-collapse:collapse; margin:.6em 0; max-width:100% } .tb td,.tb th { border:1px solid var(--line); padding:2px 8px; vertical-align:top; text-align:left } .tb td:empty,.tb th:empty { height:1em }
.opinion { border-top:2px solid var(--accent); margin-top:1.6em; padding-top:.5em }
.byline { font-weight:bold; margin:.4em 0 }
.fns { border-top:1px solid var(--line); margin-top:1em; padding-top:.4em; font-size:.88em }
.fn { display:flex; gap:.6em; margin:.35em 0 }
.fn .lbl { font-weight:bold; min-width:1.4em; text-align:right }
.fn p { text-indent:0; margin:.2em 0 }
sup.fnmark { color:var(--accent); font-weight:bold }
span.pg { font:600 10px system-ui,sans-serif; color:#fff; background:#b8b2c8;
          border-radius:8px; padding:0 6px; margin:0 3px; vertical-align:2px }
span.fr { display:block; text-align:right }
span.ctr { display:block; text-align:center }
.sig { margin:1em 0 0 45% }
"""


def _render_blocks(blocks: list, plain_paras: bool = False) -> str:
    """Every block carries data-pg (its source page) so the viewer can sync
    the original-PDF pane to the reader's position; a small chip marks each
    page transition."""
    out = []
    last_pg = None
    for b in blocks:
        pg = getattr(getattr(b, "prov", None), "page", None)
        attr = f' data-pg="{pg}"' if pg else ""
        if pg and last_pg is not None and pg != last_pg:
            out.append(f'<div class="pgbreak" data-pg="{pg}">p. {pg}</div>')
        if pg:
            last_pg = pg
        match b:
            case m.Paragraph():
                names = []
                if b.continuation or plain_paras:
                    names.append("noindent")
                if getattr(b, "align", "") == "right":
                    names.append("sig-right")
                if getattr(b, "role", "") == "disposition":
                    names.append("disposition")
                cls = f' class="{" ".join(names)}"' if names else ""
                out.append(f"<p{cls}{attr}>{inline_to_html(b.text)}</p>")
            case m.Blockquote():
                out.append(f"<blockquote{attr}>{inline_to_html(b.text)}</blockquote>")
            case m.Heading():
                out.append(f'<h3 class="bhead"{attr}>{inline_to_html(b.text)}</h3>')
            case m.ListItem():
                tag = "ol" if b.ordered else "ul"
                out.append(f"<{tag}{attr}><li>{inline_to_html(b.text)}</li></{tag}>")
            case m.TableBlock():
                rows = []
                for i, row in enumerate(b.rows):
                    tag = "th" if (b.has_header and i == 0) else "td"
                    cells = "".join(f"<{tag}>{inline_to_html(c)}</{tag}>" for c in row)
                    rows.append(f"<tr>{cells}</tr>")
                out.append(f'<table class="tb"{attr}>{"".join(rows)}</table>')
            case m.ImageBlock():
                out.append(f'<img src="{b.src}" alt="{escape(b.role)}"{attr}>')
            case _:
                raise TypeError(f"_render_blocks: {type(b)!r}")
    return "".join(out)


def _render_endmatter(blocks: list) -> str:
    """A roster the court prints BELOW its writings, shown the way the
    headmatter is shown.

    It is the same thing the headmatter's counsel block is — the court just
    set it after the opinions — so it reads as tagged rows, not as body
    prose. A centred short row inside a roster is an appearance, never a
    section heading: rendering it as one turned '[Argued]' and a firm's
    name into headings of the document."""
    out = []
    last_pg = None
    for b in blocks:
        pg = getattr(getattr(b, "prov", None), "page", None)
        if pg and last_pg is not None and pg != last_pg:
            out.append(f'<div class="pgbreak" data-pg="{pg}">p. {pg}</div>')
        if pg:
            last_pg = pg
        text = getattr(b, "text", None)
        if text is None:
            out.append(_render_blocks([b]))
            continue
        attr = f' data-pg="{pg}"' if pg else ""
        out.append(f'<div class="hmrow al" data-role="counsel"{attr}>'
                   f"{inline_to_html(text)}</div>")
    return "".join(out)


def _render_footnotes(fns: list) -> str:
    if not fns:
        return ""
    rows = []
    for fn in fns:
        rows.append(f'<div class="fn"><span class="lbl">{escape(fn.label)}</span>'
                    f"<div>{_render_blocks(fn.blocks, plain_paras=True)}</div></div>")
    return f'<div class="fns">{"".join(rows)}</div>'


_TAG = re.compile(r"<[^>]+>")


def _hm_signature(doc: m.Document) -> str:
    """The headmatter's own author rows, whitespace removed — what the page
    prints as its ANNOUNCEMENT of who wrote the opinion."""
    out = []
    for item in doc.headmatter:
        if getattr(item, "role", "") == "author":
            out.append(_TAG.sub("", getattr(item, "text", "") or ""))
    return "".join("".join(t.split()) for t in out)


def _render_opinion(op: m.Opinion, hm_sig: str = "") -> str:
    parts = [f'<div class="opinion"><span class="chip">{escape(op.type)}</span>']
    if op.caption:
        parts.append(render_hm_items(op.caption))
    # AN ANNOUNCEMENT IS NOT THE WRITING'S BYLINE. Where the court announces
    # its author in the HEADMATTER ('MATTHEW J. WILSON, J., delivered the
    # opinion of the court, in which …' — the Tennessee courts, va, tenn),
    # the row is already rendered where the page prints it, and drawing it
    # again at the head of the writing prints the same sentence twice and
    # reads as though the opinion began with it (the user, 2026-08-21: 'this
    # is not part of the opinion its the headmatter'). The author stays on
    # the object for every consumer of it; only the duplicate line goes.
    _same = op.author and hm_sig and "".join(
        _TAG.sub("", op.author).split()) in hm_sig
    if op.author and not _same:
        parts.append(f'<div class="byline">{inline_to_html(op.author)}</div>')
    parts.append(_render_blocks(op.blocks))
    if op.signature:
        # Stacked '/s/ Name' lines keep their breaks — the page sets one
        # signer per line ('/s/ Ackerman /s/ Borrello' joined is wrong).
        sig_html = _render_blocks(op.signature, True).replace(
            " /s/ ", "<br>/s/ ")
        parts.append(f'<div class="sig">{sig_html}</div>')
    parts.append(_render_footnotes(op.footnotes))
    parts.append("</div>")
    return "".join(parts)


def render_opinion(op: m.Opinion) -> str:
    """One writing's own HTML — its byline, blocks, signature and footnotes.

    Public because a consumer ingesting sub-opinions needs each writing
    addressable on its own; `render_html` emits the whole review page and
    `render_casebody` buries the same content inside its XML.
    """
    return _render_opinion(op)


def opinion_text(op: m.Opinion) -> str:
    """The same writing as plain text, for search and diffing. Markup is the
    model's own vocabulary, so it is stripped rather than escaped away."""
    import re as _re
    from html import unescape as _un
    out = []
    for b in (*op.blocks, *op.signature):
        t = getattr(b, "text", "") or ""
        if not t and getattr(b, "rows", None):
            t = " ".join(" ".join(r) for r in b.rows)
        if t:
            out.append(_un(_re.sub(r"<[^>]+>", "", t)))
    for fn in op.footnotes:
        body = " ".join(_un(_re.sub(r"<[^>]+>", "", getattr(x, "text", "") or ""))
                        for x in fn.blocks)
        if body:
            out.append(f"[{fn.label}] {body}")
    return "\n\n".join(out)


def render_headmatter(doc: m.Document) -> str:
    """The cover as the page sets it: the caption block, the rows, the rules.

    Public because the headmatter is a part of the document in its own right,
    not review furniture — `render_body` used to skip it (its section style is
    'hm', which that function did not handle) and the whole cover, plus the
    attorneys block, silently vanished from the body render.
    """
    return render_hm_items(doc.headmatter)


def render_body(doc: m.Document) -> str:
    """The document's TEXT, without the review furniture — no criteria box, no
    Removed panel, no role tints, no legend. This is what an ingest wants;
    `render_html` is what a reviewer wants.

    EVERY SECTION IS ACCOUNTED FOR, and the 'hm' ones are included rather than
    dropped: an unhandled style used to fall through the loop in silence, so
    the cover and the appearances were lost from the body with nothing saying
    so. An unknown style now raises.
    """
    parts = []
    for spec in SECTIONS:
        if spec.name in ("removed", "residual"):
            continue                      # attestation, not the document
        value = getattr(doc, spec.attr, None)
        if not value:
            continue
        if spec.html == "opinions":
            parts.append("".join(_render_opinion(op) for op in value))
        elif spec.html in ("flow", "hm-or-flow"):
            parts.append(_render_blocks(value))
        elif spec.html == "hm":
            parts.append(render_hm_items(value))
        elif spec.html == "footnotes":
            parts.append(_render_footnotes(value))
        else:
            raise ValueError(
                f"render_body: unhandled section style {spec.html!r} for "
                f"{spec.name!r} — it would be dropped in silence")
    return "".join(parts)


def _render_removed(doc: m.Document) -> str:
    """Collapsed by default — the reviewer's first look should be the
    document itself; residual CONTENT (the real worklist) forces itself open."""
    out = []
    if doc.dropped:
        rows = "".join(
            f'<div><span class="chip kind">{escape(d.kind)}</span>'
            f"p{d.prov.page} · {escape(d.text)}</div>" for d in doc.dropped)
        out.append(
            f"<details><summary>removed · {len(doc.dropped)}</summary>"
            f'<div class="box removed">{rows}</div></details>')
    if doc.residual:
        n_content = sum(1 for d in doc.residual if d.kind == "content")
        rows = "".join(
            f'<div class="{d.kind}"><span class="chip kind">{escape(d.kind)}</span>'
            f"p{d.prov.page} · {escape(d.text)}</div>" for d in doc.residual)
        force = " open" if n_content else ""
        label = (f"residual · {len(doc.residual)}"
                 + (f" · {n_content} CONTENT" if n_content else ""))
        out.append(
            f"<details{force}><summary>{label}</summary>"
            f'<div class="box residual">{rows}</div></details>')
    return "".join(out)


_SOURCE_BANNER = {
    "ocr-scan": (
        "This document is a SCAN, read by OCR.",
        "The text below is a machine's reading of a page image, not the "
        "court's own type. The words are usable and the structure is real, "
        "but every coordinate is the scanner's guess, spelling and spacing "
        "may be wrong in ways nothing here can detect, and the page may "
        "carry marks no text layer records. Do not treat this as an "
        "authoritative transcription."),
    "scan": (
        "This document is a SCAN with no usable text layer.",
        "Nothing was parsed. What follows is whatever little text the file "
        "carries — a stamp, a header — and not the document."),
}


def _source_banner(kind: str) -> str:
    """The bar that says what the paper is, before it says anything else."""
    lead, rest = _SOURCE_BANNER.get(
        kind, (f"Source kind: {kind}.",
               "This document is not born-digital paper."))
    return (f'<div class="srcbanner"><b>⚠ {escape(lead)}</b> {escape(rest)} '
            f'<code>source={escape(kind)}</code></div>')


def render_html(doc: m.Document, title: str | None = None) -> str:
    meta = doc.meta
    title = title or f"{meta.court_id} — {meta.doc_type}"
    chips = [f'<span class="chip">{escape(meta.doc_type)}</span>']
    if meta.doc_style:
        chips.append(f'<span class="chip kind">{escape(meta.doc_style)}</span>')
    for w in doc.warnings:
        chips.append(f'<span class="chip warn" title="{escape(w)}">⚠</span>')
    head = (f"<h1>{escape(meta.court_label or meta.court_id)}</h1>"
            f'<div class="meta">{"".join(chips)} {escape(meta.source_path)}'
            f" · {meta.n_pages}pp</div>")

    body = [head]
    # WHAT THE PAPER IS, SAID FIRST. A scan's OCR text layer reads exactly
    # like a court's own type — same words, same order, no marker of any kind
    # — so a reader who does not already know cannot tell, and neither can
    # anything downstream. The chip row carried a '⚠' whose only explanation
    # was a hover title (nevapp/ccmsi_v._odell: ten pages of 200dpi raster,
    # graded A, indistinguishable from born-digital paper on the page). The
    # banner states it, and `meta name="centralia-source"` states it again in
    # a form a consumer can read without parsing the review furniture.
    if meta.source_kind:
        body.append(_source_banner(meta.source_kind))

    c = doc.criteria
    crit_rows = [(k, v) for k, v in (
        ("publication", c.publication_status),
        ("parties", " v. ".join(c.parties) if c.parties else None),
        ("citation", c.citation),
        ("docket", c.docket_number),
        ("other dockets", ", ".join(c.other_dockets) or None),
        ("decided", c.decision_date),
        ("argued/submitted", c.submitted),
        ("judges", c.judges),
        ("author", c.author),
        ("disposition", c.disposition),
        ("lower court", c.lower_court),
        ("lower court docket",
         ", ".join(c.lower_court_docket) or None),
        ("history", c.history),
        ("attorneys", c.attorneys),
    ) if v]
    if crit_rows:
        rows = "".join(
            f'<div><span class="chip kind">{escape(k)}</span>'
            f"{escape(str(v)[:300])}</div>" for k, v in crit_rows)
        # THE CASES THIS RECORD DECIDES, each named on its own. A
        # consolidated paper states one number per action and one caption per
        # number; listed as 'docket' plus 'other dockets' the numbers survive
        # and the grouping does not, so a reader cannot tell which parties go
        # with which number (the user, 2026-08-23: 'it would list case 1 and
        # case 2'). Restored here in the shape the sheet used before the
        # template rewrite dropped it.
        _cases = list(getattr(c, "cases", ()) or ())
        if len(_cases) > 1:
            for i, case in enumerate(_cases, 1):
                rows += (f'<div class="caseline"><b>case {i} of '
                         f"{len(_cases)}</b></div>")
                for k, v in (("docket", case.docket_number),
                             ("case name", case.case_name),
                             ("lower court", case.lower_court),
                             ("lower docket", case.lower_court_docket)):
                    if v:
                        rows += (f'<div class="caserow">'
                                 f'<span class="chip kind">{escape(k)}</span>'
                                 f"{escape(str(v)[:300])}</div>")
        _label = f"criteria · {len(crit_rows)}"
        if len(_cases) > 1:
            _label += f" · {len(_cases)} cases heard together"
        body.append(f"<details><summary>{escape(_label)}</summary>"
                    f'<div class="box">{rows}</div></details>')
    removed_html = _render_removed(doc)
    if removed_html:
        body.append(removed_html)

    _hm_sig = _hm_signature(doc)
    for spec in SECTIONS:
        if spec.html == "removed":
            continue  # rendered up top
        value = getattr(doc, spec.attr)
        if not value:
            continue
        if spec.name == "endmatter" and not all(
                isinstance(x, (m.HmLine, m.CaptionBlock, m.Rule,
                               m.Divider, m.Gap, m.ImageBlock))
                for x in value):
            # The roster is normally rebuilt into the page's own rows and
            # renders exactly like the headmatter. When provenance could not
            # place them the pipeline keeps the assembled BLOCKS instead —
            # and `render_hm_items` raises on a Paragraph, so that fallback
            # would take the whole document down. Render it as blocks.
            inner = _render_endmatter(value)
        elif spec.name == "signature" and all(
                isinstance(x, (m.HmLine, m.CaptionBlock, m.Rule,
                               m.Divider, m.Gap))
                for x in value):
            # A COURT THAT READ ITS OWN SIGNATURE BAND may hand over the
            # page's ROWS instead of assembled blocks, and rows are what a
            # two-abreast signature needs: guam sets two justices side by
            # side over drawn rules, and one flow paragraph per printed row
            # fuses the columns into a single run ('/s/ /s/ F. PHILIP
            # CARBULLIDO KATHERINE A. MARAMAN Associate Justice Associate
            # Justice' — three printed rows, six cells, one line). Rendered
            # the way the headmatter renders rows, the whitespace is the
            # page's. Courts that hand over Paragraphs (haw, dc, hawapp,
            # ohioctapp) still take the flow path below, exactly as before.
            inner = render_hm_items(value)
        elif spec.html == "hm":
            inner = render_hm_items(value)
        elif spec.html == "flow":
            inner = _render_blocks(value)
        elif spec.html == "footnotes":
            inner = _render_footnotes(value)
        elif spec.html == "opinions":
            inner = "".join(_render_opinion(op, _hm_sig) for op in value)
        else:
            raise ValueError(f"unknown html style {spec.html!r}")
        _sc = f' class="sec-{escape(spec.name)}"' if spec.name else ""
        _tagged = spec.name in ("headmatter", "endmatter")
        if _tagged and 'data-role="' in inner:
            # Mark the FIRST row of each run of one role: the margin label
            # names the section there, so the block reads as a sequence of
            # named parts rather than a wash of colour.
            import re as _rr
            _seen: list[str | None] = [None]

            def _mark(mo: "_rr.Match[str]") -> str:
                cls, rest, role = mo.group(1), mo.group(2), mo.group(3)
                if role != _seen[0]:
                    cls += " role-start"
                _seen[0] = role
                return f'<div class="{cls}"{rest}data-role="{role}"'

            inner = _rr.sub(
                r'<div class="(hmrow[^"]*)"([^>]*?)data-role="([a-z-]+)"',
                _mark, inner)
        _legend = ""
        if _tagged and 'data-role="' in inner:
            _roles = [("court", "court"), ("publication", "publication"),
                      ("banner", "banner/title"), ("title", "title"),
                      ("docket", "docket"), ("date", "date"),
                      ("panel", "panel"), ("lower-court", "lower court"),
                      ("caption", "caption"), ("counsel", "counsel"),
                      ("case-info", "case info"), ("disposition", "disposition"),
                      ("citation", "citation"), ("headnotes", "headnotes"),
                      ("syllabus", "syllabus"),
                      ("author", "author"),
                      ("summary", "summary")]
            _legend = (
                '<div class="hm-legend">read as: '
                + " ".join(f'<b data-role="{k}">{label}</b>'
                           for k, label in _roles
                           if f'data-role="{k}"' in inner)
                + " · untinted rows were not claimed by a court reader</div>")
        body.append(
            f"<section{_sc}><h2>{escape(spec.name)}</h2>{_legend}{inner}"
            f"</section>")

    return (f"<!doctype html><meta charset='utf-8'><title>{escape(title)}</title>"
            f"<meta name='centralia-source' "
            f"content='{escape(meta.source_kind or 'born-digital', quote=True)}'>"
            f"<style>{_CSS}</style>{''.join(body)}")
