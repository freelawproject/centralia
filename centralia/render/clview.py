"""THE COURTLISTENER VIEW: this record as an ingest would store it.

The review sheet answers 'did we read the page right'. This answers a
different question — 'does what we read SURVIVE the translation into
CourtListener's model, and what falls on the floor' (the user, 2026-08-23:
'a toggle to render the CL view so i can see how things translate if they
translate').

So every row here is one CL field, in CL's own vocabulary, with three
things beside it: the value an ingest would write, WHERE it came from in
our model, and — where a field cannot be filled — whether that is because
the document does not carry it or because CL has nowhere to put what we
have. The second kind is the finding. It is drawn in the red the review
sheet reserves for a defect.

THE FIELD LISTS ARE CL'S OWN, read off the live API (clusters: 46 fields,
opinions: 30, the `type` vocabulary: 13 codes) rather than remembered. A
field CL renamed or dropped would otherwise quietly become a lie told in a
table that looks authoritative.
"""

from __future__ import annotations

from html import escape

from .. import model as m
from ..dates import to_iso
from .casebody import render_casebody
from .html import opinion_text, render_headmatter, render_opinion

# --------------------------------------------------------------------------
# the vocabulary CL stores opinions under
# --------------------------------------------------------------------------
# OUR kind -> (CL type code, per_curiam). A court's own word for its paper is
# richer than CL's list: 'concurrence-in-result' and
# 'concurring-in-part-and-dissenting-in-part' both land on the nearest code
# CL has, and the mapping says so rather than inventing a code.
_TYPE = {
    "majority": ("020lead", False),
    "per-curiam": ("020lead", True),
    "concurrence": ("030concurrence", False),
    "concurrence-in-result": ("030concurrence", False),
    "concurring-in-part-and-dissenting-in-part": ("035concurrenceinpart", False),
    "dissent": ("040dissent", False),
    "addendum": ("050addendum", False),
    "rehearing": ("070rehearing", False),
    "order": ("010combined", False),
}
_TYPE_NOTE = {
    "per-curiam": "020lead with per_curiam=True — CL has no per-curiam code",
    "concurrence-in-result": "nearest code; 'in result' is not in CL's list",
    "concurring-in-part-and-dissenting-in-part":
        "035concurrenceinpart — the dissenting half of the kind is lost",
}

# What a court files that is NOT its own writing. CL should not ingest these
# as opinions at all; the view says so at the top instead of translating a
# party's filing into a court's opinion (the user, on an akd complaint:
# 'we want to be able to recognize this as not an opinion and not ingest it
# on the CL side').
_NOT_AN_OPINION = {
    m.DocType.FILING: "a party's filing, not the court's writing",
    m.DocType.NOTICE: "a notice, not a writing",
    m.DocType.CERTIFICATE: "a clerk's certificate, not a writing",
    m.DocType.JUDGMENT: "a judgment form — no reasoning to ingest",
}

_STATUS = {"published": "Published", "unpublished": "Unpublished"}


def _cl_type(op: m.Opinion, n_writings: int) -> tuple[str, bool, str]:
    """One writing's CL type, its per_curiam flag, and the caveat if any.

    A LONE WRITING IS THE WHOLE PAPER. CL's scrapers file a single-opinion
    cluster as '010combined', and calling it a lead opinion implies siblings
    that do not exist — so the lead code is used only where the document
    really does carry more than one writing."""
    code, per_curiam = _TYPE.get(op.type, ("010combined", False))
    note = _TYPE_NOTE.get(op.type, "")
    if op.type not in _TYPE:
        note = f"no CL code for {op.type!r} — filed as a combined opinion"
    elif n_writings == 1 and code == "020lead":
        code, note = "010combined", ("a lone writing is the whole paper; "
                                     "CL files that as combined")
    return code, per_curiam, note


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

_CSS = """
body { font:14px/1.55 system-ui,-apple-system,Segoe UI,sans-serif; color:#1a1a1a;
       background:#fdfdfc; max-width:min(1100px,95vw); margin:1.4em auto 5em;
       padding:0 1.4em }
h1 { font-size:1.05em; margin:0 0 .1em } h1 span { color:#777; font-weight:400 }
.sub { color:#777; font-size:12px; margin-bottom:1.4em }
h2 { font:600 11px system-ui,sans-serif; text-transform:uppercase;
     letter-spacing:.09em; color:#666; border-bottom:1px solid #ddd;
     padding-bottom:3px; margin:2em 0 .5em }
h2 code { font:600 11px ui-monospace,Menlo,monospace; color:#6b4b9a;
          text-transform:none; letter-spacing:0 }
table { border-collapse:collapse; width:100%; font-size:13px }
td { border-top:1px solid #eee; padding:.34em .5em; vertical-align:top }
td.f { width:16em; font:600 12px ui-monospace,Menlo,monospace; color:#444;
       white-space:nowrap }
td.v { width:auto }
td.s { width:17em; color:#888; font-size:11.5px }
tr.empty td.v { color:#bbb }
tr.lost td.f { color:#b3372f } tr.lost td.v { color:#b3372f }
tr.lost td.s { color:#b3372f }
.warn { border:1px solid #b3372f; border-left-width:6px; border-radius:4px;
        background:#fdf3f2; color:#7a2620; padding:.6em .9em; margin:0 0 1.2em }
.warn b { letter-spacing:.02em }
.chip { display:inline-block; font:600 11px system-ui,sans-serif; color:#fff;
        background:#6b4b9a; border-radius:9px; padding:1px 9px; margin-right:.4em }
.chip.t { background:#3d6b8a; font-family:ui-monospace,Menlo,monospace }
.chip.pc { background:#8a6b3d }
.note { color:#8a6b3d; font-size:11.5px }
.body { border:1px solid #ddd; border-radius:5px; padding:.9em 1.1em;
        margin:.7em 0 0; background:#fff; font:15px/1.6 Georgia,serif }
.body h3 { font-size:1em } .body blockquote { margin:.7em 0 .7em 1.6em }
.body .fns { border-top:1px solid #ddd; margin-top:1em; padding-top:.6em;
             font-size:.88em }
.body .fn { display:flex; gap:.5em } .body .fn .lbl { color:#777 }
.body .pg { display:none } .body .pgbreak { display:none }
.body .byline { font-variant:small-caps; margin:.4em 0 }
.body .sig { margin-top:1em; font-style:italic }
pre.x { font:11.5px/1.45 ui-monospace,Menlo,monospace; background:#f7f6f4;
        border:1px solid #e6e4e0; border-radius:5px; padding:.7em .8em;
        overflow-x:auto; max-height:22em; white-space:pre-wrap;
        word-break:break-word }
details { margin:.6em 0 } summary { cursor:pointer; color:#666; font-size:12px }
/* THE ISLAND. Our headmatter markup is rendered here with NOTHING of ours
   applied to it — no `.hmrow`, no `.caption`, no `--rel` — because that is
   the truth of what CL stores: one html blob and its own site stylesheet.
   Anything that needs a class of ours to mean something is already gone by
   the time it reaches the page, and the point of this view is to SEE that.
   Only a plausible body font is set, the way any host page would. */
.island { border:1px solid #ddd; border-radius:5px; background:#fff;
          padding:1.1em 1.3em; font:16px/1.5 Georgia,"Times New Roman",serif;
          color:#111 }
.island div, .island p { margin:0 }
.island td { border:0; padding:0 }
.island table { border-collapse:collapse }
.lose { font-size:12.5px; margin:.2em 0 .9em }
.lose b { color:#b3372f } .lose i { color:#777; font-style:normal }
.lab { font:600 11px system-ui,sans-serif; text-transform:uppercase;
       letter-spacing:.07em; color:#8a6b3d; margin:1.1em 0 .3em }
"""


def _row(field: str, value: str, source: str, lost: bool = False) -> str:
    cls = "lost" if lost else ("empty" if not value else "")
    return (f'<tr class="{cls}"><td class="f">{escape(field)}</td>'
            f'<td class="v">{value or "—"}</td>'
            f'<td class="s">{escape(source)}</td></tr>')


def _trim(text: str, n: int = 300) -> str:
    text = " ".join((text or "").split())
    return escape(text if len(text) <= n else text[:n] + " …")


def render_cl(doc: m.Document, status: str = "") -> str:
    """The whole translation, as one page."""
    c = doc.criteria
    n = len(doc.opinions)
    parts = [f"<title>CL view — {escape(doc.meta.court_id)}</title>",
             f"<style>{_CSS}</style>",
             f'<h1>{escape(c.case_name or c.parties and c.parties[0] or "—")}'
             f'</h1>',
             f'<div class="sub">{escape(doc.meta.court_label or "")} · '
             f'{escape(str(doc.meta.doc_type))} · {doc.meta.n_pages}pp · '
             f'what an ingest would write, field by field</div>']

    # ---- the gate: is this a court's writing at all? ---------------------
    if doc.meta.doc_type in _NOT_AN_OPINION:
        parts.append(
            f'<div class="warn"><b>DO NOT INGEST.</b> This record is '
            f'{escape(_NOT_AN_OPINION[doc.meta.doc_type])} — read as '
            f'<code>{escape(str(doc.meta.doc_type))}</code>. Everything below '
            f'is what the fields WOULD hold; the paper still has no business '
            f'in an opinion cluster.</div>')
    elif not doc.opinions:
        parts.append('<div class="warn"><b>NOTHING TO INGEST.</b> No writing '
                     'was read out of this record, so a cluster would be '
                     'created with no opinion under it.</div>')

    # ---- Docket ----------------------------------------------------------
    parts.append('<h2>Docket <code>/api/rest/v4/dockets/</code></h2><table>')
    parts.append(_row("court", escape(doc.meta.court_id), "meta.court_id"))
    parts.append(_row("docket_number", escape(c.docket_number or ""),
                      "criteria.docket_number"))
    parts.append(_row("case_name", _trim(c.case_name or ""),
                      "criteria.case_name"))
    parts.append(_row("case_name_short", escape(c.short_case_name or ""),
                      "criteria.short_case_name"))
    parts.append(_row("case_name_full", _trim(" ".join(c.caption)),
                      "criteria.caption (rows, verbatim)"))
    parts.append(_row("date_filed", escape(to_iso(c.decision_date) or ""),
                      "criteria.decision_date → ISO"))
    parts.append(_row("appeal_from_str", escape(c.lower_court or ""),
                      "criteria.lower_court"))
    parts.append(_row("assigned_to_str", escape(c.lower_court_judge or ""),
                      "criteria.lower_court_judge"))
    parts.append(_row("panel_str", escape(c.panel_line or ""),
                      "criteria.panel_line"))
    if c.other_dockets:
        parts.append(_row(
            "— (companion appeals)", escape(", ".join(c.other_dockets)),
            f"criteria.other_dockets ({len(c.other_dockets)}) — a cluster "
            f"hangs off ONE docket", lost=True))
    if c.lower_court_docket:
        parts.append(_row("(originating court)",
                          escape(", ".join(c.lower_court_docket)),
                          "criteria.lower_court_docket — belongs on "
                          "originating-court-information"))
    parts.append("</table>")

    # ---- the cases the paper decides ------------------------------------
    # A CONSOLIDATED RECORD IS MORE THAN ONE CASE, and a cluster hangs off
    # ONE docket. The grouping is READ — each number with its own parties —
    # so the translation can state the cost exactly: one of these becomes
    # the cluster and the rest are numbers on a docket nobody created.
    cases = list(c.cases or ())
    if len(cases) > 1:
        parts.append(f"<h2>{len(cases)} cases heard together</h2>"
                     f'<div class="warn"><b>ONE CLUSTER, {len(cases)} CASES.'
                     f"</b> CL hangs an OpinionCluster off a single docket. "
                     f"This paper decides {len(cases)} actions, each with its "
                     f"own number and its own parties — so an ingest either "
                     f"creates {len(cases)} dockets pointing at one cluster, "
                     f"or {len(cases) - 1} of these case names are never "
                     f"stored anywhere.</div><table>")
        for i, case in enumerate(cases, 1):
            lead = " (the lead — this is what cluster.case_name holds)" \
                if i == 1 else ""
            parts.append(_row(f"case {i} · docket_number",
                              escape(case.docket_number), f"case {i}"))
            parts.append(_row(f"case {i} · case_name",
                              _trim(case.case_name),
                              f"built from case {i}'s own caption rows{lead}",
                              lost=(i > 1)))
        parts.append("</table>")

    # ---- OpinionCluster --------------------------------------------------
    parts.append('<h2>OpinionCluster <code>/api/rest/v4/clusters/</code>'
                 "</h2><table>")
    _pub = _STATUS.get((c.publication_status or "").lower(), "")
    parts.append(_row("precedential_status", escape(_pub or "Unknown"),
                      "criteria.publication_status" if _pub
                      else "not printed — CL default 'Unknown'"))
    parts.append(_row("date_filed", escape(to_iso(c.decision_date) or ""),
                      "criteria.decision_date → ISO"))
    parts.append(_row("date_filed_is_approximate", "false", "always false"))
    parts.append(_row("judges", escape(c.judges or ""), "criteria.judges"))
    parts.append(_row("panel", escape(" · ".join(c.panel)),
                      "criteria.panel — CL wants Judge IDs, "
                      "these are strings", lost=bool(c.panel)))
    parts.append(_row("attorneys", _trim(c.attorneys or ""),
                      "criteria.attorneys"))
    parts.append(_row("syllabus", _trim(_precis(doc, "syllabus")),
                      "doc.syllabus + headmatter rows read as syllabus"))
    parts.append(_row("headnotes", _trim(_precis(doc, "headnotes")),
                      "doc.headnotes + headmatter rows read as headnotes"))
    parts.append(_row("summary", _trim(_precis(doc, "summary")),
                      "doc.summary + headmatter rows read as summary"))
    parts.append(_row("disposition", escape(c.disposition or ""),
                      "criteria.disposition"))
    parts.append(_row("history", escape(c.history or ""), "criteria.history"))
    parts.append(_row("other_dates", escape(_other_dates(c)),
                      "criteria.date_argued / date_submitted / date_reargued"))
    parts.append(_row("headmatter", f"{_hm_rows(doc)} rows of HTML "
                      "— reconstructed below",
                      "doc.headmatter — CL keeps ONE html blob, so the "
                      "per-row roles do not survive"))
    parts.append(_row("posture", "", "nothing read for it"))
    parts.append(_row("procedural_history", "", "nothing read for it"))
    parts.append(_row("nature_of_suit", "", "nothing read for it"))
    parts.append(_row("cross_reference", "", "nothing read for it"))
    parts.append(_row("correction", "", "nothing read for it"))
    parts.append(_row("arguments", "", "nothing read for it"))
    parts.append(_row("source", "C (court website)",
                      "the ingest decides; this reads court PDFs"))
    if c.citation:
        parts.append(_row(
            "citations[]", escape(c.citation),
            "criteria.citation — CL wants volume/reporter/page split out",
            lost=True))
    parts.append("</table>")

    # ---- what CL has no field for ---------------------------------------
    lost = _no_home(doc, c)
    if lost:
        parts.append("<h2>Read, but CL has nowhere to put it</h2><table>")
        for field, value, why in lost:
            parts.append(_row(field, value, why, lost=True))
        parts.append("</table>")

    # ---- the writings ----------------------------------------------------
    for i, op in enumerate(doc.opinions, start=1):
        code, per_curiam, note = _cl_type(op, n)
        head = (f'<h2>Opinion {i} of {n} '
                f'<code>/api/rest/v4/opinions/</code></h2>'
                f'<div><span class="chip t">{escape(code)}</span>'
                f'<span class="chip">{escape(op.type)}</span>')
        if per_curiam:
            head += '<span class="chip pc">per_curiam</span>'
        if note:
            head += f'<span class="note">{escape(note)}</span>'
        parts.append(head + "</div><table>")
        parts.append(_row("ordering_key", str(i), "position in the document"))
        parts.append(_row("type", escape(code), f"our {op.type!r}"))
        parts.append(_row("per_curiam", "true" if per_curiam else "false",
                          "the byline's own kind"))
        parts.append(_row("author_str",
                          escape(op.author_name or _bare(op.author)),
                          "opinion.author_name (parsed from the byline)"))
        parts.append(_row("joined_by_str", "",
                          "the joiners are not read out yet"))
        parts.append(_row("plain_text", f"{len(opinion_text(op)):,} chars",
                          "opinion_text(op)"))
        parts.append(_row("html", f"{len(render_opinion(op)):,} chars",
                          "render_opinion(op) — shown below"))
        parts.append(_row("page_count", str(doc.meta.n_pages),
                          "meta.n_pages (the whole PDF)"))
        parts.append(_row("extracted_by_ocr",
                          "true" if doc.meta.scan_pages else "false",
                          "meta.scan_pages"))
        parts.append(_row("sha1", "", "the ingest computes it from the PDF"))
        parts.append(_row("download_url / local_path", "",
                          "the ingest sets these"))
        if op.footnotes:
            parts.append(_row(
                f"footnotes ({len(op.footnotes)})",
                escape(" ".join(f.label for f in op.footnotes)),
                "kept INSIDE html — CL has no footnote table"))
        parts.append("</table>")
        parts.append(f'<div class="body">{render_opinion(op)}</div>')

    # ---- the headmatter, RECONSTRUCTED ----------------------------------
    parts.append(_headmatter_section(doc))

    # ---- the casebody XML, which has its own CL home ---------------------
    parts.append("<h2>xml_harvard <code>casebody</code></h2>"
                 '<details><summary>the same record as casebody XML — the '
                 "one field that holds our structure whole</summary>"
                 f'<pre class="x">{escape(render_casebody(doc))}</pre>'
                 "</details>")
    return "".join(parts)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _bare(markup: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", markup or "")


def _precis(doc: m.Document, role: str) -> str:
    """The same merge `centralia.read` does: flow blocks, then headmatter
    rows carrying that role."""
    parts = [_bare(getattr(b, "text", ""))
             for b in getattr(doc, role, ()) or ()]
    parts += [_bare(getattr(i, "text", "")) for i in doc.headmatter
              if getattr(i, "role", "") == role and getattr(i, "text", "")]
    return " ".join(p for p in parts if p)


def _other_dates(c: m.Criteria) -> str:
    bits = [f"{label}: {value}" for label, value in
            (("argued", c.date_argued), ("submitted", c.date_submitted),
             ("reargued", c.date_reargued))
            if value]
    if not bits and c.submitted:
        bits = [f"submitted: {c.submitted}"]
    return "; ".join(bits)


def _hm_rows(doc: m.Document) -> int:
    n = 0
    for item in doc.headmatter:
        if isinstance(item, m.HmLine) and (item.text or "").strip():
            n += 1
        elif isinstance(item, m.CaptionBlock):
            n += sum(1 for r in (*item.left, *item.right)
                     if (r.text or "").strip())
    return n


def _no_home(doc: m.Document, c: m.Criteria) -> list[tuple[str, str, str]]:
    """Everything we READ that CL's model cannot hold. This is the list the
    view exists for — a field left empty because the page never printed it
    is not a loss, and a field left empty because CL has no column for what
    the page DID print is."""
    out: list[tuple[str, str, str]] = []
    if c.title:
        out.append(("title", escape(c.title),
                    "what the paper calls itself — no cluster field"))
    if c.lower_court_docket:
        out.append(("lower_court_docket", escape(", ".join(c.lower_court_docket)),
                    "the court below's number — belongs on "
                    "originating-court-information, not the cluster"))
    if c.motion:
        out.append(("motion", escape(c.motion), "no cluster field"))
    if c.parties:
        out.append(("parties[]", _trim(" | ".join(c.parties)),
                    "the sides, split — CL keeps only the joined case_name "
                    "(parties live on a RECAP docket, not a cluster)"))
    if doc.attorneys:
        out.append((f"endmatter ({len(doc.attorneys)} rows)",
                    _trim(" ".join(_bare(getattr(a, "text", ""))
                                   for a in doc.attorneys)),
                    "the appearances the court printed BELOW its writings — "
                    "cluster.attorneys is one string"))
    if doc.headmatter_footnotes:
        out.append((f"headmatter footnotes "
                    f"({len(doc.headmatter_footnotes)})",
                    escape(" ".join(f.label
                                    for f in doc.headmatter_footnotes)),
                    "notes hanging off the COVER, not off a writing"))
    if doc.trailer:
        out.append((f"trailer ({len(doc.trailer)})",
                    _trim(" ".join(_bare(getattr(b, "text", ""))
                                   for b in doc.trailer)),
                    "what the court printed after the last writing"))
    if doc.residual:
        content = [r for r in doc.residual if r.kind == "content"]
        if content:
            out.append((f"residual ({len(content)})",
                        _trim(" ".join(r.text for r in content)),
                        "SOURCE LINES NO STAGE CLAIMED — these are missing "
                        "from every field above"))
    return out


# --------------------------------------------------------------------------
# the headmatter, as the receiving page would actually draw it
# --------------------------------------------------------------------------
# OUR LAYOUT LIVES IN OUR STYLESHEET. The review sheet reproduces a cover
# faithfully — centred rows centred, a two-column caption in two columns
# either side of the rail the page draws, a hanging indent where the court
# hung one — and every one of those is carried by a CLASS (`hmrow ac`,
# `caption`/`cap-left`/`cap-right`/`rail`) or a custom property (`--rel`)
# that only our CSS understands. CL stores ONE html blob and draws it with
# its own site styles, so the question the user asked — 'is it readable when
# reconstructed for more complex headmatters?' — is answered by rendering it
# with none of ours applied, and by counting exactly what stops meaning
# anything when we do.
import re as _re

_ROW_CLASS = _re.compile(r'<div class="hmrow([^"]*)"')
_CAPTION = _re.compile(r'<div class="caption"')
_RAIL = _re.compile(r'<div class="rail ([a-z]+)"')
_REL = _re.compile(r"--rel:")
_INLINE_SIZE = _re.compile(r"font-size:")
_RULE = _re.compile(r'<div class="(typedrule|rule|divider)')


def _headmatter_section(doc: m.Document) -> str:
    html = render_headmatter(doc)
    if not html.strip():
        return ""
    classes = _ROW_CLASS.findall(html)
    centred = sum(1 for c in classes if " ac" in c)
    righted = sum(1 for c in classes if " ar" in c)
    captions = len(_CAPTION.findall(html))
    rails = [g for g in _RAIL.findall(html) if g != "open"]
    rels = len(_REL.findall(html))
    rules = len(_RULE.findall(html))
    sizes = len(_INLINE_SIZE.findall(html))

    lost: list[str] = []
    if captions:
        lost.append(f"<b>{captions} two-column caption"
                    f"{'s' if captions > 1 else ''}</b> collapse to stacked "
                    f"rows — the columns are a CSS grid of ours")
    if rails:
        lost.append(f"<b>{len(rails)} rail{'s' if len(rails) > 1 else ''}</b> "
                    f"the page draws down the middle of the caption "
                    f"({', '.join(sorted(set(rails)))})")
    if centred:
        lost.append(f"<b>{centred} centred row"
                    f"{'s' if centred > 1 else ''}</b> lose their centring "
                    f"(class <code>ac</code>, not an inline style)")
    if righted:
        lost.append(f"<b>{righted} flush-right row"
                    f"{'s' if righted > 1 else ''}</b> lose their alignment")
    if rels:
        lost.append(f"<b>{rels} hanging indent"
                    f"{'s' if rels > 1 else ''}</b> (<code>--rel</code>)")
    if rules:
        lost.append(f"<b>{rules} rule{'s' if rules > 1 else ''}</b> the page "
                    f"draws — they render as empty divs")
    # ESCAPED: naming the tags is not opening them. Written raw, this line
    # opened an <em>, a <strong> and a <u> that nothing closed, and every
    # row of the cover below inherited all three.
    kept = [f"{len(classes)} rows in the page's own order", "the text itself",
            escape("inline <em>/<strong>/<u> markup")]
    if sizes:
        kept.append(f"{sizes} inline font-size{'s' if sizes > 1 else ''}")

    out = ["<h2>cluster.headmatter <code>reconstructed, with none of our "
           "CSS</code></h2>"]
    if lost:
        out.append(
            '<div class="warn"><b>THIS IS WHAT CL WOULD DRAW.</b> The cover '
            "below is our own headmatter HTML with our stylesheet taken away "
            "— which is what CL has, since it stores the blob and draws it "
            "with its own site styles. Everything in red is layout our "
            "markup states in a CLASS, so it means nothing on the receiving "
            "page.</div>")
    out.append('<div class="lose">')
    out.append("<i>survives:</i> " + "; ".join(kept) + ".")
    if lost:
        out.append("<br><i>does not:</i> " + "; ".join(lost) + ".")
    out.append("</div>")
    out.append('<div class="lab">as stored today</div>')
    out.append(f'<div class="island">{html}</div>')
    out.append("<details><summary>the html itself — what would be written to "
               "<code>cluster.headmatter</code></summary>"
               f'<pre class="x">{escape(html)}</pre></details>')

    # THE SAME COVER, SAID PORTABLY. Drawn in the same island, with the same
    # nothing applied to it — so the difference on the screen is the
    # difference the markup makes.
    port = _portable_hm(doc.headmatter)
    out.append('<div class="lab">the same rows with the layout stated '
               "INLINE — what an ingest could be handed instead</div>")
    out.append(f'<div class="island">{port}</div>')
    out.append("<details><summary>that html</summary>"
               f'<pre class="x">{escape(port)}</pre></details>')
    return "".join(out)


# --------------------------------------------------------------------------
# the same cover, said in a way that survives the trip
# --------------------------------------------------------------------------
# THE LAYOUT HAS TO BE IN THE MARKUP, not in a stylesheet the receiving page
# has never seen. Every carrier below is inline: alignment as `text-align`,
# a hanging indent as `margin-left`, a two-column caption as a TABLE ROW PER
# PRINTED ROW — which is the thing that actually matters, because it keeps
# each docket number beside the party row the court set it beside instead of
# dumping every number after every party — and a rule the page draws as an
# <hr> that draws. Nothing here needs a class to mean something.
def _portable_hm(items: list, base_size: float = 12.0) -> str:
    out: list[str] = []
    for item in items:
        match item:
            case m.HmLine():
                out.append(_portable_row(item, base_size))
            case m.CaptionBlock():
                out.append(_portable_caption(item, base_size))
            case m.Rule():
                width = {"full": "100%", "left": "48%", "right": "48%",
                         "center": "40%"}.get(item.span, "100%")
                margin = "0 auto" if item.span == "center" else (
                    "0 0 0 auto" if item.span == "right" else "0")
                out.append(f'<hr style="border:0;border-top:1px solid #999;'
                           f'width:{width};margin:.45em {margin}">')
            case m.Divider():
                pass                       # a boundary, not a mark
            case m.Gap():
                out.append(f'<div style="height:{item.lines}em"></div>')
            case m.ImageBlock():
                dim = ""
                if item.width and item.height:
                    dim = f' width="{item.width:.0f}" height="{item.height:.0f}"'
                out.append(f'<img src="{item.src}"{dim} alt="">')
    return "".join(out)


def _portable_style(row: m.HmLine, base_size: float) -> str:
    bits = []
    if row.align is m.Align.CENTER:
        bits.append("text-align:center")
    elif row.align is m.Align.RIGHT:
        bits.append("text-align:right")
    if base_size and row.size and abs(row.size - base_size) >= 1.0:
        bits.append(f"font-size:{row.size / base_size:.2f}em")
    if row.rel:
        bits.append(f"margin-left:{row.rel:.0f}pt")
    return ";".join(bits)


def _portable_row(row: m.HmLine, base_size: float) -> str:
    text = row.text or ""
    if not text.strip():
        return '<div style="height:.9em"></div>'
    style = _portable_style(row, base_size)
    s = f' style="{style}"' if style else ""
    return f"<div{s}>{text}</div>"


def _portable_caption(block: m.CaptionBlock, base_size: float) -> str:
    """A two-column caption as a table, ONE ROW PER PRINTED ROW.

    The cells are already paired by the row they came off the page on, so
    the pairing is the thing to keep: it is what puts 'Case No.
    3:25-cv-00316-SLG' beside its own action instead of after it."""
    rows = []
    rail = block.rail if block.rail and block.rail != "|" else ""
    border = ("border-left:1px solid #999"
              if block.rail == "|" else "")
    for left, right in zip(block.left, block.right):
        lt = (left.text or "") if left is not None else ""
        rt = (right.text or "") if right is not None else ""
        ls = _portable_style(left, base_size) if left is not None else ""
        rs = _portable_style(right, base_size) if right is not None else ""
        rows.append(
            '<tr>'
            f'<td style="width:52%;vertical-align:top;padding:.05em .4em .05em 0;'
            f'{ls}">{lt or "&nbsp;"}</td>'
            f'<td style="width:1em;text-align:center;vertical-align:top;'
            f'padding:.05em .3em;{border}">{escape(rail)}</td>'
            f'<td style="width:47%;vertical-align:top;padding:.05em 0 .05em .4em;'
            f'{rs}">{rt or "&nbsp;"}</td></tr>')
    return ('<table style="width:100%;border-collapse:collapse;'
            f'margin:.3em 0">{"".join(rows)}</table>')
