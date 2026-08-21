"""Supreme Court of Maryland ('md').

Everything unique to md lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Maryland prints TWO papers, and one record may print both.
Neither is named by a word on the page; each is named by a rule the page
draws.

    'column fences' (27 of 50) — the opinion/certiorari cover. The whole
    caption is set in a COLUMN OF ITS OWN, on an axis ~108pt right of the
    page's (measured: fence centre 414.0 on 25 records, 402.6 on one,
    413.9 on the rest, against a page axis of 306). The column is divided
    into BANDS by a rule 252.0pt wide — typed as underscores on 15
    records, drawn as a rect on 12, never anything else and never any
    other measure. Two more rects, 152.8pt and 95.0pt, UNDERLINE the two
    masthead rows: their ends coincide with the row above them to a
    tenth of a point, which is what tells an underline from a fence.

        Circuit Court for Frederick County    10pt, at the page's rail —
        Case No.: C-10-CV-24-000717           the court BELOW, its number
        Argued: January 5, 2026               and the day it was heard
                            IN THE SUPREME COURT   underlined: the masthead
                                OF MARYLAND        underlined
                                  No. 33           the docket
                             September Term, 2025  the sitting
                    ____________________________   a FENCE, 252pt
                             KAPNECK 14-16, LLC    the caption…
                                    v.             …its pivot…
                          BKEEZY'S SPEAKEASY, LLC  …and the other side
                    ____________________________   a FENCE
                    Fader, C.J.,                   the roster: a stack,
                    Watts,                         left-aligned on ONE x
                    …                              …
                                   JJ.
                    ____________________________   a FENCE
                          Opinion by Gould, J.     the byline — LEFT to the
                    Watts, Eaves, and Killough,    writing, never claimed
                       JJ., concurs and dissents.  the vote
                    ____________________________   a FENCE
                          Filed: April 29, 2026    the day it was filed

    THE BANDS ARE NOT AT FIXED INDICES. Four fences on 21 records, five
    on two, seven on the three-way B.P. consolidation; the masthead and
    the docket share a band on some and are fenced apart on others. The
    band is the unit of meaning, and it is named by what it holds:

      - the ROSTER band is the one whose rows form a LEFT-ALIGNED STACK
        (three or more rows sharing one x0 to 1.5pt). There is exactly
        one, and it is the page's own pivot: everything above it that is
        not masthead-or-docket is the caption; the band below it is the
        byline; anything below that is the filing date.
      - the MASTHEAD is the row(s) carrying a drawn UNDERLINE.
      - the DOCKET and the SITTING are closed structural forms ('No. 33',
        'Nos. 4, 5, & 6', 'AG No. 2', 'September Term, 2025').

    Where the paper reports headnotes, the reporter sets them on the
    page(s) BEFORE the cover: an attribution line, then BOLD topical
    headings each over a roman précis. They stay in the headmatter — the
    block renders whole — marked `headnotes` and `summary`.

    'asterisk rail' (23 of 50, and the second page of 9 more) — the order.
    A rail of '*' glyphs on one x separates the parties (left) from the
    court, its docket and its sitting (right). The two columns keep
    INDEPENDENT baseline rhythms — bowler's rail steps 29.9pt while its
    right column steps 14.9 — so no row pairing survives, and the block is
    read as two column SEQUENCES with the rail's own row count beside
    them.

        KEVIN BOWLER              *   IN THE
                                  *   SUPREME COURT
        v.                        *   OF MARYLAND
                                  *   Petition No. 309
        STATE FARM MUTUAL         *   September Term, 2024
        AUTOMOBILE INSURANCE      *   (Cir. Ct. No. C-16-CV-24-000961)
        COMPANY                   *
                       O R D E R                  …and the writing starts

THE DISPATCH is two questions about the front of the document, both about
rules the page draws: does a page in the first six carry THREE OR MORE
252pt fences off the page axis (the cover), and does page 1 — or the page
right after that cover — carry THREE OR MORE rows whose only ink is '*'
(the rail). A record answering neither is not one of these papers and gets
NOTHING.

WHAT THE READER DOES NOT TOUCH. The byline ('Opinion by Gould, J.') and
the order's own heading ('PER CURIAM ORDER', 'O R D E R') are the
WRITING's, not the headmatter's; the reader stops short of both and lets
assembly anchor on them exactly as it does for any other court. md prints
no appearance of counsel anywhere in the corpus.

TWO pdfio DEFECTS THIS READER DEFENDS AGAINST, both of them one visual row
holding glyphs from two different baselines:

  - the cover's 10pt origin block is clustered into the 13pt column's
    rhythm, so 'Circuit Court for Anne Arundel County' and 'Case No.:
    C-02-CV-21-000250' come back interleaved character by character
    ('Ciarsceu Nit oC.:o uCr-t0 f2o-rC AVn-n2e1 -A00ru0n2d5e0l County' —
    3 rows over 2 records);
  - a rail glyph 7pt below its neighbour's baseline is welded onto the
    left cell ('IN THE MATTER OF THE PETITION *  ' — 10 rows over 5
    records).

Both are handled by reading the CHARS, not the line: the origin block is
re-split at its own baselines, and every rail row is partitioned at the
rail's x.
"""

from __future__ import annotations

import re

from .. import model as m
from ..pdfio.model import Line
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.headmatter import find_date
from . import get_profile

# md's profile is registered in `courts/__init__.py`; this file adds only
# the reader, so importing it can never raise a duplicate registration.
MD = get_profile("md")

STYLE_COLUMN = "column fences"
STYLE_RAIL = "asterisk rail"
STYLE_BOTH = "column fences over asterisk rail"

# ---- md's declared facts (measured over the 50-record corpus) ------------
# THE FENCE. 252.0pt on every one of the 121 fences in the corpus; the
# masthead UNDERLINES are 152.8 and 95.0 and are never this measure.
_FENCE_MEASURE = (246.0, 258.0)
# …and it stands off the PAGE axis: the column's own axis is 96–108pt to
# its right, so a rule centred on the page is not this court's fence.
_OFF_AXIS_MIN = 60.0
# The fences of one cover agree on their centre to 10.2pt (cutchember sets
# one of six 10pt left of the other five).
_AXIS_SPREAD = 14.0
# HOW FAR FORWARD THE COVER MAY BE. The reporter sets at most three pages
# of headnotes before it (engage_armament 2, b.p. 3).
_MAX_HEAD_PAGES = 6
# A ROW IS CENTRED ON THE COLUMN when its midpoint sits on the column's
# axis. Kapneck's party rows are set 15–18pt right of it, so the band —
# not the row — declares the centring, and this tolerance only decides
# whether a row inside an already-centred band gets an indent.
_AXIS_TOL = 6.0
# THE ROSTER IS A STACK: three or more rows sharing one left edge.
_STACK_TOL = 1.5
_STACK_MIN = 3
# Two glyphs on one visual row whose tops differ by more than this came
# from two different baselines (see the pdfio note above).
_BASELINE_SPLIT = 3.0
# HALF THE RAIL'S CLEARANCE: a '*' is ~6.5pt wide and the columns stand
# 17pt off it on the tightest record.
_RAIL_HALF = 9.0
_RAIL_MIN_ROWS = 3

# THE COURT NAMING ITSELF, in the forms it prints across the two papers —
# whole on the cover, broken over the rail. A closed vocabulary of ONE
# court's own name, never a party or a court below.
_COURT_ROWS = frozenset({
    "IN THE", "IN THE SUPREME COURT", "SUPREME COURT", "OF MARYLAND",
    "SUPREME COURT OF MARYLAND", "IN THE SUPREME COURT OF MARYLAND",
})
# 'No. 33' / 'Nos. 39 & 40' / 'Nos. 4, 5, & 6' / 'AG No. 2' / 'Misc. No. 1'
# / 'Petition No. 309' — a closed structural form: an optional leader, the
# word No., and the numbers it names.
_DOCKET = re.compile(
    r"^(?:[A-Z][A-Za-z.]{0,11}\s+){0,2}Nos?\.\s*\d+[\d,&\s]*$")
# 'September Term, 2025' — the sitting.
_TERM = re.compile(r"^[A-Z][a-z]+\s+Term,?\s+\d{4}\.?$")
# 'Filed: April 29, 2026' / 'Argued: January 5, 2026' — a labelled date.
_DATED = re.compile(r"^(Filed|Argued|Submitted|Decided|Reargued)\s*:\s*(.+)$")
# 'Circuit Court for Frederick County' / 'District Court of Maryland' —
# the origin block's leader.
_ORIGIN_LEAD = ("circuit court", "district court", "court of special appeals",
                "appellate court", "orphans' court", "orphans’ court")
# 'Case No.: C-10-CV-24-000717' / '(Cir. Ct. No. C-16-CV-24-000961)' — the
# number a court BELOW gave the case.
_LOWER_NO = re.compile(r"^\(?\s*(?:Cir\.\s*Ct\.\s*)?Case\s*Nos?\.?\s*:?\s*(.+?)\)?$",
                       re.I)
_CIR_CT_NO = re.compile(r"^\(\s*Cir\.\s*Ct\.\s*Nos?\.\s*(.+?)\s*\)$", re.I)
# The pivot: a row whose whole ink is 'v.'.
_PIVOT = re.compile(r"^v\.?$", re.I)
# 'JJ.' / 'J.' — the roster's closing bench abbreviation.
_BENCH_CLOSE = re.compile(r"^J{1,2}\.$")
# The paper naming itself at the foot of the cover, where it is an ORDER
# rather than a signed opinion ('PER CURIAM ORDER', 'ORDER').
_ORDER_HEAD = re.compile(r"^[A-Z][A-Z .]*ORDER$")


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# reading the CHARS, not the line
# --------------------------------------------------------------------------

def _sub_line(src: Line, chars: list) -> Line | None:
    """A Line rebuilt from a subset of another's chars — the way to read a
    row pdfio welded together out of two baselines. Keeps the source id, so
    provenance survives."""
    chars = [c for c in chars if (c.get("text") or "") != ""]
    if not chars or not any((c.get("text") or "").strip() for c in chars):
        return None
    return Line(
        id=src.id, page=src.page,
        x0=min(c["x0"] for c in chars), x1=max(c["x1"] for c in chars),
        top=min(c.get("top", src.top) for c in chars),
        bottom=max(c.get("bottom", src.bottom) for c in chars),
        chars=chars, col=src.col, row=src.row)


def _debaseline(line: Line) -> list[Line]:
    """One line per BASELINE the row's glyphs actually sit on. pdfio clusters
    the cover's 10pt origin block into the 13pt column's rhythm and hands
    back two rows interleaved glyph by glyph; their tops still say which
    row each glyph came from."""
    inked = [c for c in line.chars if (c.get("text") or "").strip()]
    if not inked:
        return [line]
    tops = sorted({round(c.get("top", line.top), 1) for c in inked})
    if not tops or tops[-1] - tops[0] <= _BASELINE_SPLIT:
        return [line]
    groups: list[list[float]] = [[tops[0]]]
    for t in tops[1:]:
        if t - groups[-1][-1] <= _BASELINE_SPLIT:
            groups[-1].append(t)
        else:
            groups.append([t])
    if len(groups) < 2:
        return [line]
    out = []
    for g in groups:
        lo, hi = g[0] - 0.5, g[-1] + 0.5
        sub = _sub_line(line, [c for c in line.chars
                               if lo <= round(c.get("top", line.top), 1) <= hi])
        if sub is not None:
            out.append(sub)
    return out or [line]


def _rows(lines: list[Line], tol: float = 2.5) -> list[list[Line]]:
    """Lines grouped into the visual rows the page set them on."""
    out: list[list[Line]] = []
    for line in sorted(lines, key=lambda l: (l.top, l.x0)):
        if out and abs(out[-1][0].top - line.top) <= tol:
            out[-1].append(line)
        else:
            out.append([line])
    for group in out:
        group.sort(key=lambda l: l.x0)
    return out


def _row_text(group: list[Line]) -> str:
    return _norm(" ".join(l.plain for l in group))


def _row_markup(group: list[Line]) -> str:
    out = ""
    for line in group:
        piece = line_markup(line)
        out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() else piece
    return out


def _join_markup(pieces: list[str]) -> str:
    """Wrapped rows as one statement. A row ENDING on a hyphen closed a word
    the measure broke; joined with a space it reads as an unclosed
    hyphenation."""
    out = ""
    for piece in pieces:
        piece = piece.strip()
        if not out:
            out = piece
        elif out.endswith("-") and piece[:1].islower():
            out += piece
        else:
            out += " " + piece
    return out


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

class _Fence:
    """One band divider of the caption column, drawn or typed."""

    __slots__ = ("top", "x0", "x1", "lines")

    def __init__(self, top: float, x0: float, x1: float, lines: list):
        self.top, self.x0, self.x1, self.lines = top, x0, x1, lines

    @property
    def center(self) -> float:
        return (self.x0 + self.x1) / 2


def _fences(pm) -> list[_Fence]:
    """The 252pt band dividers of this page's caption column — the DRAWN
    rects and the TYPED underscore rows both, and neither the masthead's
    underlines (152.8 / 95.0) nor anything centred on the page."""
    found: list[_Fence] = []
    for rule in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= rule.width <= _FENCE_MEASURE[1]):
            continue
        if abs((rule.x0 + rule.x1) / 2 - pm.width / 2) < _OFF_AXIS_MIN:
            continue
        found.append(_Fence(rule.top, rule.x0, rule.x1, []))
    for group in _rows(pm.lines):
        text = _row_text(group).replace(" ", "")
        if len(text) < 12 or set(text) != {"_"}:
            continue
        x0 = min(l.x0 for l in group)
        x1 = max(l.x1 for l in group)
        if not (_FENCE_MEASURE[0] <= x1 - x0 <= _FENCE_MEASURE[1]):
            continue
        if abs((x0 + x1) / 2 - pm.width / 2) < _OFF_AXIS_MIN:
            continue
        found.append(_Fence(group[0].top, x0, x1, list(group)))
    found.sort(key=lambda f: f.top)
    if len(found) < 3:
        return []
    # THE FENCES OF ONE COVER AGREE ON THEIR CENTRE. Anything that does not
    # belongs to some other structure.
    centers = sorted(f.center for f in found)
    axis = centers[len(centers) // 2]
    found = [f for f in found if abs(f.center - axis) <= _AXIS_SPREAD]
    return found if len(found) >= 3 else []


def _underlined(pm, group: list[Line]) -> bool:
    """A drawn rule whose ends coincide with this row is an UNDERLINE, and on
    md's cover only the masthead carries one."""
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    top = max(l.bottom for l in group)
    return any(abs(r.x0 - x0) <= 2.0 and abs(r.x1 - x1) <= 2.0
               and 0 <= r.top - top <= 16.0
               for r in pm.h_rules)


def _rail_x(pm) -> float | None:
    """The x the page rails its '*' glyphs on, or None."""
    xs = [(c["x0"] + c["x1"]) / 2 for l in pm.lines for c in l.chars
          if (c.get("text") or "").strip() == "*"]
    if len(xs) < _RAIL_MIN_ROWS:
        return None
    xs.sort()
    return xs[len(xs) // 2]


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom):
        self.model = model
        self.geom = geom
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.anchors: list = []
        self.doc_type: object = None

    # -- emit ------------------------------------------------------------
    def line(self, group: list[Line], role: str, align: str = "L",
             rel: float = 0.0, text: str | None = None) -> m.HmLine:
        first = group[0]
        return m.HmLine(
            text=text if text is not None else _row_markup(group),
            prov=m.Prov(first.page, tuple(l.id for l in group)),
            align=m.Align(align), x0=first.x0,
            size=max(l.size or 0.0 for l in group),
            bold=all(l.all_bold for l in group), rel=rel, role=role)

    def emit(self, group: list[Line], role: str, align: str = "L",
             rel: float = 0.0, text: str | None = None) -> m.HmLine:
        row = self.line(group, role, align, rel, text)
        self.items.append(row)
        self.consumed.update(row.prov.line_ids)
        return row

    def fence(self, fence: _Fence, after: m.HmLine | None) -> None:
        """A FENCE RENDERS WHERE THE PAGE DREW IT.

        A TYPED fence is a row of its own, so it carries its own line ids —
        which both places it exactly and PLACES ITS TEXT: given the prov of
        the row above instead, its underscores were consumed and never
        recorded, and came back as four residual furniture lines on every
        typed cover. A DRAWN fence has no line to carry, and core sorts an
        id-less item to the position of its neighbour, so it borrows the
        prov of the row it stands under and stays put."""
        if fence.lines:
            prov = m.Prov(fence.lines[0].page,
                          tuple(l.id for l in fence.lines))
        elif after is not None:
            prov = m.Prov(after.prov.page, after.prov.line_ids)
        else:
            prov = m.Prov(self.model.pages[0].number)
        self.items.append(m.Rule(prov=prov, typed=bool(fence.lines),
                                 span="center"))
        self.consumed.update(l.id for l in fence.lines)

    def add(self, key: str, value) -> None:
        if isinstance(value, list):
            bucket = self.crit.setdefault(key, [])
            for v in value:
                if v not in bucket:
                    bucket.append(v)
        elif self.crit.get(key) is None:
            self.crit[key] = value

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchors, "doc_type_final": self.doc_type}


# ---- the reporter's headnote pages ---------------------------------------

def _read_headnotes(ctx: _Ctx, pages: list) -> None:
    """The page(s) the reporter sets before the cover: an attribution line,
    then BOLD topical headings each over a roman précis. Each unit wraps
    over several rows and a blank band is the separator — so runs of
    consecutive rows of one weight are one row of the block."""
    groups: list[list[list[Line]]] = []
    prev = None
    for pm in pages:
        rows = [g for g in _rows(pm.lines) if _row_text(g)]
        if not rows:
            continue
        steps = sorted(rows[i + 1][0].top - rows[i][0].top
                       for i in range(len(rows) - 1))
        step = steps[len(steps) // 2] if steps else 15.0
        for group in rows:
            bold = all(l.all_bold for l in group)
            gap = (group[0].top - prev[0][-1][0].top) if prev and \
                prev[1] == pm.number else None
            if (prev is None or prev[2] != bold or gap is None
                    or gap > step * 1.45):
                groups.append([group])
            else:
                groups[-1].append(group)
            prev = (groups[-1], pm.number, bold)
    for index, unit in enumerate(groups):
        flat = [l for g in unit for l in g]
        bold = all(l.all_bold for l in flat)
        # THE ATTRIBUTION LINE opens the block: the reporter's own statement
        # of what this paper is ('<case>, No. 33, September Term, 2025.
        # Opinion by Gould, J.'). It is caption apparatus, not a headnote.
        role = "case-info" if index == 0 and not bold else (
            "headnotes" if bold else "summary")
        ctx.items.append(m.HmLine(
            text=_join_markup([_row_markup(g) for g in unit]),
            prov=m.Prov(flat[0].page, tuple(l.id for l in flat)),
            align=m.Align("L"), x0=flat[0].x0,
            size=max(l.size or 0.0 for l in flat), bold=bold, role=role))
        ctx.consumed.update(l.id for l in flat)


# ---- the cover's own origin block ----------------------------------------

def _read_origin(ctx: _Ctx, pm, lines: list[Line]) -> None:
    """The 10pt block at the page's own rail: the court below, the number it
    gave the case, and the day this court heard it."""
    parts: list[Line] = []
    for line in lines:
        parts.extend(_debaseline(line))
    for group in _rows(parts, tol=1.5):
        text = _row_text(group)
        if not text:
            continue
        low = text.lower()
        dated = _DATED.match(text)
        if dated:
            value = find_date(dated.group(2)) or dated.group(2).strip()
            ctx.emit(group, "date")
            if dated.group(1) in ("Argued", "Submitted", "Reargued"):
                ctx.add("submitted", value)
            else:
                ctx.add("decision_date", value)
            continue
        number = _LOWER_NO.match(text)
        if number and "no" in low:
            ctx.emit(group, "lower-court")
            ctx.add("lower_court_docket", [_norm(number.group(1))])
            continue
        ctx.emit(group, "lower-court")
        if any(low.startswith(lead) for lead in _ORIGIN_LEAD):
            prev = ctx.crit.get("lower_court")
            ctx.crit["lower_court"] = f"{prev}; {text}" if prev else text


# ---- the cover ------------------------------------------------------------

def _band_head_row(ctx: _Ctx, pm, group: list[Line], axis: float) -> str:
    """The role of one row in a HEAD band: the court naming itself, the
    docket it gave the case, or the sitting it heard it in."""
    text = _row_text(group)
    if _TERM.match(text):
        return "date"
    if _DOCKET.match(text):
        return "docket"
    if text.upper() in _COURT_ROWS or _underlined(pm, group):
        return "court"
    return "case-info"


def _is_head_band(ctx: _Ctx, pm, band: list[list[Line]]) -> bool:
    return all(_band_head_row(ctx, pm, g, 0.0) in ("court", "docket", "date")
               for g in band)


def _is_stack(band: list[list[Line]]) -> bool:
    """A ROSTER IS A STACK — three or more rows on one left edge."""
    if len(band) < _STACK_MIN:
        return False
    xs = [g[0].x0 for g in band]
    for x in xs:
        if sum(1 for other in xs if abs(other - x) <= _STACK_TOL) >= _STACK_MIN:
            return True
    return False


def _read_cover(ctx: _Ctx, pm, fences: list[_Fence]) -> bool:
    axis = sorted(f.center for f in fences)[len(fences) // 2]
    col_x0 = min(f.x0 for f in fences)
    lines = [l for l in pm.lines if l.plain.strip()]
    origin = [l for l in lines if l.x1 <= col_x0 - 20.0]
    column = [l for l in lines if l.x1 > col_x0 - 20.0
              and not any(l is f_l for f in fences for f_l in f.lines)]
    fence_ids = {l.id for f in fences for l in f.lines}
    column = [l for l in column if l.id not in fence_ids]
    bands: list[list[list[Line]]] = []
    edges = [f.top for f in fences]
    for group in _rows(column):
        index = sum(1 for e in edges if group[0].top > e)
        while len(bands) <= index:
            bands.append([])
        bands[index].append(group)
    if not any(bands):
        return False

    # THE ROSTER BAND IS THE PAGE'S PIVOT: what stands above it is masthead
    # and caption, what stands below it is the byline and the filing date.
    stack = next((i for i, b in enumerate(bands) if _is_stack(b)), None)
    if stack is None:
        return False

    def emit_band(band, role, align_all=True):
        last = None
        for group in band:
            centred = abs((min(l.x0 for l in group)
                           + max(l.x1 for l in group)) / 2 - axis) <= _AXIS_TOL
            if align_all or centred:
                last = ctx.emit(group, role, "C")
            else:
                last = ctx.emit(group, role, "L",
                                rel=max(0.0, group[0].x0 - col_x0))
        return last

    if origin:
        _read_origin(ctx, pm, origin)

    last: m.HmLine | None = None
    caption_open = False
    for index, band in enumerate(bands):
        if index and index - 1 < len(fences):
            ctx.fence(fences[index - 1], last)
        if not band:
            continue
        if index == stack:
            last = _read_roster(ctx, band, col_x0)
            caption_open = False
        elif index < stack:
            if not caption_open and _is_head_band(ctx, pm, band):
                for group in band:
                    role = _band_head_row(ctx, pm, group, axis)
                    last = ctx.emit(group, role, "C")
                    text = _row_text(group)
                    if role == "docket":
                        ctx.add("docket_number", text)
                    elif role == "court":
                        ctx.crit["court"] = _norm(
                            f"{ctx.crit.get('court', '')} {text}")
            else:
                caption_open = True
                last = _read_caption(ctx, band, axis, col_x0)
        elif index == stack + 1:
            last = _read_author(ctx, band, axis, col_x0) or last
        else:
            last = _read_foot(ctx, band, axis, col_x0) or last
    for extra in range(len(bands) - 1, len(fences)):
        ctx.fence(fences[extra], last)
    ctx.add("headmatter_style", STYLE_COLUMN)
    return True


def _read_roster(ctx: _Ctx, band, col_x0: float):
    """The roster, as printed and as parsed. A row opening on '(' continues
    the judge above it ('McDonald, Robert N.' / '(Senior Justice, Specially
    Assigned),')."""
    names: list[str] = []
    printed: list[str] = []
    last = None
    for group in band:
        text = _row_text(group)
        last = ctx.emit(group, "panel", "L",
                        rel=max(0.0, group[0].x0 - col_x0))
        printed.append(text)
        bare = text.rstrip(",. ")
        if _BENCH_CLOSE.match(text):
            continue
        if text.startswith("(") and names:
            names[-1] = f"{names[-1]} {text.rstrip(',')}"
        elif bare:
            names.append(bare)
    if names:
        ctx.add("panel", names)
    if printed:
        ctx.add("panel_line", " ".join(printed))
    return last


def _read_caption(ctx: _Ctx, band, axis: float, col_x0: float):
    """One caption band: the party names either side of the printed pivot.
    THE BAND declares the centring — kapneck sets its party rows 15-18pt
    right of the axis its own fences draw, and read row by row every one of
    them would render as an indent."""
    last = None
    left: list[str] = []
    right: list[str] = []
    side = left
    rows: list[str] = []
    for group in band:
        text = _row_text(group)
        last = ctx.emit(group, "caption", "C")
        rows.append(text)
        if _PIVOT.match(text):
            side = right
            continue
        side.append(text)
    ctx.add("caption", rows)
    lead = _norm(" ".join(left)).rstrip(",; ")
    trail = _norm(" ".join(right)).rstrip(",; ")
    if lead and not ctx.crit.get("parties"):
        ctx.crit["parties"] = [lead, trail] if trail else [lead]
        ctx.crit["case_name"] = f"{lead} v. {trail}" if trail else lead
    return last


def _units(band: list[list[Line]]) -> list[list[list[Line]]]:
    """The band's rows grouped into the STATEMENTS they wrap into. Every
    statement md sets below the roster is a sentence, so a row that does not
    end on a full stop is still mid-statement ('Watts, Eaves, and Killough,
    JJ.,' / 'concurs and dissents.')."""
    units: list[list[list[Line]]] = []
    for group in band:
        if units and not _row_text(units[-1][-1]).rstrip().endswith("."):
            units[-1].append(group)
        else:
            units.append([group])
    return units


def _read_author(ctx: _Ctx, band, axis: float, col_x0: float):
    """The band under the roster: the court's byline and its vote.

    THE BYLINE IS THE WRITING'S. 'Opinion by Gould, J.' is what assembly
    anchors the lead opinion on, and a reader that claims it takes the
    document's only statement of who wrote it out of the writing — so it is
    passed over, exactly as ala passes over 'CERTIFICATE OF JUDGMENT'. The
    same goes for an order's own heading ('PER CURIAM ORDER'), whose text
    is still recorded as what the paper calls itself."""
    from ..resolve.bylines import BylineParser
    parser = BylineParser(MD.byline)
    last = None
    for index, unit in enumerate(_units(band)):
        text = _norm(" ".join(_row_text(g) for g in unit))
        flat = [l for g in unit for l in g]
        if index == 0:
            if parser.parse(text) is not None and not _ORDER_HEAD.match(text):
                continue                 # the writing's byline
            if _ORDER_HEAD.match(text):
                # THE PAPER NAMING ITSELF ('PER CURIAM ORDER'). Left in the
                # stream core reads it as a per-curiam BYLINE, keeps 'ORDER'
                # as the writing's first paragraph, and — because the writing
                # then opens ABOVE the last row of the cover — pulls the
                # filing date in after it (9 records). It is a headmatter
                # row, so it is claimed as one; its id goes to `anchor_ids`
                # so core can hand it back if the claim costs the document
                # its writing, and the paper is still typed an order.
                last = ctx.emit(unit[0], "title", "C")
                ctx.anchors.extend(last.prov.line_ids)
                ctx.crit["title"] = text
                ctx.doc_type = m.DocType.ORDER
                continue
        # THE VOTE: who concurred, who dissented. It is the roster speaking,
        # not the author, and it wraps.
        last = ctx.items.append(m.HmLine(
            text=_join_markup([_row_markup(g) for g in unit]),
            prov=m.Prov(flat[0].page, tuple(l.id for l in flat)),
            align=m.Align("C"), x0=flat[0].x0,
            size=max(l.size or 0.0 for l in flat), role="panel")) \
            or ctx.items[-1]
        ctx.consumed.update(l.id for l in flat)
    return last


def _read_foot(ctx: _Ctx, band, axis: float, col_x0: float):
    """Below the last fence: the day the court filed the paper."""
    last = None
    for unit in _units(band):
        text = _norm(" ".join(_row_text(g) for g in unit))
        flat = [l for g in unit for l in g]
        dated = _DATED.match(text)
        role = "date" if dated else "case-info"
        last = ctx.emit(flat, role, "C",
                        text=_join_markup([_row_markup(g) for g in unit]))
        if dated:
            value = find_date(dated.group(2)) or dated.group(2).strip()
            if dated.group(1) in ("Argued", "Submitted", "Reargued"):
                ctx.add("submitted", value)
            else:
                ctx.crit["decision_date"] = value
    return last


# ---- the asterisk rail ----------------------------------------------------

def _rail_role(text: str) -> str:
    if text.upper() in _COURT_ROWS:
        return "court"
    if _DOCKET.match(text):
        return "docket"
    if _TERM.match(text):
        return "date"
    if _CIR_CT_NO.match(text) or _LOWER_NO.match(text):
        return "lower-court"
    return "case-info"


def _read_rail(ctx: _Ctx, pm, rail_x: float, first: bool) -> bool:
    """The order's caption: two column SEQUENCES either side of a rail of
    '*' glyphs. The columns keep independent baseline rhythms, so nothing
    pairs row for row; each column is read in its own order and the rail
    reports how many glyphs it drew."""
    lo, hi = rail_x - _RAIL_HALF, rail_x + _RAIL_HALF
    groups: list[list[Line]] = []
    by_row: dict = {}
    loose: list[list[Line]] = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        if line.row is not None:
            by_row.setdefault(line.row, []).append(line)
        else:
            loose.append([line])
    groups = sorted(list(by_row.values()) + loose,
                    key=lambda g: (min(l.top for l in g),
                                   min(l.x0 for l in g)))

    def cells(group):
        left, rail, right = [], [], []
        for line in group:
            for c in line.chars:
                cx = (c["x0"] + c["x1"]) / 2
                (left if cx < lo else (rail if cx <= hi else right)).append(
                    (line, c))
        return left, rail, right

    starred = [i for i, g in enumerate(groups)
               if any((c.get("text") or "").strip() == "*"
                      for l in g for c in l.chars
                      if lo <= (c["x0"] + c["x1"]) / 2 <= hi)]
    if len(starred) < _RAIL_MIN_ROWS:
        return False
    zone = groups[starred[0]:starred[-1] + 1]

    left_rows: list[m.HmLine] = []
    right_rows: list[m.HmLine] = []
    rail_rows = 0
    ids: list[int] = []
    parties_left: list[str] = []
    parties_right: list[str] = []
    side = parties_left
    for group in zone:
        left, rail, right = cells(group)
        if any((c.get("text") or "").strip() == "*" for _l, c in rail):
            rail_rows += 1
        for line in group:
            ids.append(line.id)
        for bucket, out, role in ((left, left_rows, None),
                                  (right, right_rows, None)):
            if not bucket:
                continue
            by_line: dict = {}
            for line, c in bucket:
                by_line.setdefault(line.id, [line, []])[1].append(c)
            subs = [_sub_line(line, chars) for line, chars in by_line.values()]
            subs = [s for s in subs if s is not None]
            if not subs:
                continue
            text = _norm(" ".join(s.plain for s in subs))
            if not text:
                continue
            if bucket is left:
                out.append(ctx.line(subs, "caption", "L",
                                    text=_row_markup(subs)))
                if _PIVOT.match(text):
                    side = parties_right
                else:
                    side.append(text)
            else:
                kind = _rail_role(text)
                out.append(ctx.line(subs, kind, "L", text=_row_markup(subs)))
                if kind == "docket":
                    ctx.add("docket_number", text)
                elif kind == "court":
                    ctx.crit["court"] = _norm(
                        f"{ctx.crit.get('court', '')} {text}")
                elif kind == "lower-court":
                    mm = _CIR_CT_NO.match(text) or _LOWER_NO.match(text)
                    if mm:
                        ctx.add("lower_court_docket", [_norm(mm.group(1))])
    if not (left_rows or right_rows):
        return False
    ctx.items.append(m.CaptionBlock(
        left=left_rows, right=right_rows, rail="*", rail_rows=rail_rows,
        style_id=STYLE_RAIL,
        fp={"rail": "*", "rail_x": rail_x},
        prov=m.Prov(pm.number, tuple(sorted(set(ids))))))
    ctx.consumed.update(ids)
    lead = _norm(" ".join(parties_left)).rstrip(",; ")
    trail = _norm(" ".join(parties_right)).rstrip(",; ")
    if lead and not ctx.crit.get("parties"):
        ctx.crit["parties"] = [lead, trail] if trail else [lead]
        ctx.crit["case_name"] = f"{lead} v. {trail}" if trail else lead
    if first:
        ctx.add("caption", [r for r in parties_left + parties_right])
    return True


# --------------------------------------------------------------------------
# the dispatch
# --------------------------------------------------------------------------

@decider("headmatter.read", court="md")
def read_headmatter_md(model, geom, **_):
    """Read one of md's two papers — or both, or NOTHING."""
    if not model.pages:
        return NOTHING
    cover = None
    fences: list[_Fence] = []
    for pm in model.pages[:_MAX_HEAD_PAGES]:
        found = _fences(pm)
        if found:
            cover, fences = pm, found
            break
    rail_page = None
    if cover is None:
        pm = model.pages[0]
        if _rail_x(pm) is not None:
            rail_page = pm
    elif cover.number < model.n_pages:
        pm = model.pages[cover.number]
        if _rail_x(pm) is not None:
            rail_page = pm
    if cover is None and rail_page is None:
        return NOTHING

    ctx = _Ctx(model, geom)
    ok = False
    if cover is not None:
        if cover.number > 1:
            _read_headnotes(ctx, model.pages[:cover.number - 1])
        ok = _read_cover(ctx, cover, fences)
        if not ok:
            return NOTHING
    if rail_page is not None:
        rail_x = _rail_x(rail_page)
        got = _read_rail(ctx, rail_page, rail_x, first=cover is None)
        if got:
            ctx.crit["headmatter_style"] = (
                STYLE_BOTH if cover is not None else STYLE_RAIL)
        ok = ok or got
    if not ok:
        return NOTHING
    if ctx.crit.get("court"):
        ctx.crit["court"] = _norm(ctx.crit["court"])
    return ctx.result()
