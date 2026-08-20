"""The Business Court of Texas ('texbizct').

Everything unique to texbizct lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is carried
in this file (the `mass.py` pattern) and registered into `PROFILES` below.

WHAT THIS COURT IS. A trial court created in 2024 — a specialist business
docket sitting in eleven numbered divisions across the state. It is NOT the
Supreme Court of Texas, and it does not print that court's paper: there is no
panel, no roster of appearances, no argued/decided pair, no lower court. A
single judge decides a motion and files a memorandum opinion. What it DOES
print is a cover sheet, and it prints one for every writing it files.

IS THIS AN ECF FILING? No. The section-rail caption is the same shape the
federal Texas district courts set (`centralia/districts/ecf.py`, the glyph
rail), and the rail's glyph — '§' — is the Texas state-court convention both
lanes inherited. But NOTHING ELSE of the ECF pleading order is here: no
CM/ECF header stamp fielded across the top of every page, no
'IN THE UNITED STATES DISTRICT COURT FOR THE …' masthead, no asterisk band
closing the caption, no 'Civil Action No.'. Instead the court prints its own
public-domain citation above the masthead, a state-court clerk's FILED stamp
where it prints one, and it fences the paper's title between two TYPED RULES
of box-drawing characters. The shared ECF reader would find none of its
landmarks, so this file reads the cover itself.

THE COVER — one sheet, 612x792, 12–13pt Courier, body rail at x0=72:

    FILED IN                          the clerk's stamp, flush right in the
    BUSINESS COURT OF TEXAS           top band; on 14 of 42 records only,
    BEVERLY CRUMLEY, CLERK            and pure furniture -> Dropped
    ENTERED
    4/8/2026

              2026 Tex. Bus. 35       the court's own PUBLIC-DOMAIN CITATION,
                                      centred, always the first row of type
                                      under the stamp -> criteria.citation

        The Business Court of Texas,  the masthead: the court, then its
              Eleventh Division       DIVISION, two centred rows

    M. BROWN,                    §    the caption: two columns split by a
        Plaintiff,               §    stacked '§' RAIL. Left, the parties and
    v.                           §  Cause No. 25-BC11B-0099
    EXXON MOBIL CORPORATION,     §    their status; right, the cause number
        Defendant.               §    and nothing else.

    ═══════════════════════════════   a TYPED RULE of box-drawing characters
            Syllabus*                 the paper's TITLE, centred
    ═══════════════════════════════   and the closing rule

    This opinion addresses …          and the writing begins

TWO PAPERS, and THE TITLE BAND'S FENCE names them (42 records, 36/6, nothing
left over):

  * 'fenced title' (36) — the title stands between two typed '═' rules. This
    is the court's current cover and every division except the Eighth sets
    it.

  * 'bare title' (6) — no rules are typed at all; the title is a lone BOLD
    CENTRED row standing in the whitespace under the caption
    ('MEMORANDUM OPINION'). The Eighth Division's chambers set this, and so
    do the four records that reach us as SCANS.

A record printing neither a masthead nor a rail is not this paper and gets
NOTHING.

THE COVER IS PER-WRITING, NOT PER-DOCUMENT. Six records print the cover
TWICE: once over a staff-written 'Syllabus' and again, overleaf, over the
opinion the syllabus describes (brown_v._exxon_mobil, bnsf_railway,
enosis_investments — where the second cover is on page 3, not page 2 —
gosecure, jeremiah_counsel, dk_trading). The second cover is not a running
head and it is not a repeat of the first: it is the next writing's own cover
sheet, with its own title. So the reader looks for a cover on every one of
the first three pages and reads each one it finds, in place. Read as
front matter only, the second cover's title was left unclaimed and the
`Syllabus` band above it became the document's only writing.

FOUR RECORDS ARE SCANS. `local_marketing_v._bennett`, `may_v._ineos`,
`plains_pipeline_v._arrowhead` and `stratton_v._hogan` come back from pdfio
with `image_area == 1.00` — a FULL-BLEED RASTER of the whole sheet with an
OCR text layer over it, which is why the render puts an `image` chip on them.
They are not born-digital: the type sizes jitter by a tenth of a point from
row to row and the OCR mangles a word here and there ('Plaint·iff', 'ROBERTS.
MAY' for 'ROBERT S. MAY'). The layout survives that intact — the rail is
still a column of '§' and the masthead is still two centred rows — so they
are read like any other bare-title record, and the raster is left to core's
image handling. Nothing is corrected: an OCR error is what the page says.

WHAT THIS READER DECLINES. On two records the party list is long enough to
fill page 1 by itself — fischer_v._fischer names fourteen defendants and
may_v._ineos_usa_oil__gas (a scan) names twenty — so the caption box runs to
the foot of the sheet and the TITLE BAND STANDS OVERLEAF, without a masthead
above it to say it is a cover. This reader does not follow it there: the
title band's own fence is not enough to tell a title from a section heading
on a page that prints no cover, so the row is left unclaimed and core makes
it the writing's heading, which is where it belongs anyway. `criteria.title`
is the only thing lost, and nothing is mis-tagged to gain it.

WHAT IS NOT HERE. No counsel block: this court does not print appearances on
the cover at all (checked over all 42). No panel: a single judge signs. No
dates in the front matter: the clerk's stamp carries the filing date and it
is furniture. So this reader emits exactly five roles — `citation`, `court`,
`caption`/`docket` (inside the block), and `title` — and drops the stamp.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# --------------------------------------------------------------------------
# the court
# --------------------------------------------------------------------------

TEXBIZCT = CourtProfile(
    "texbizct", "The Business Court of Texas",
    # ONE PAPER, ONE WRITING: a trial court is one judge ruling on a motion,
    # so there is no second writing to concur in or dissent from. The six
    # syllabus records print two SECTIONS, not two opinions — the syllabus is
    # court staff's precis and says so in its own footnote.
    single_writing=True,
    # The judge signs in the reversed form: the name over the office.
    byline=BylineGrammar(style="reversed",
                         rev_titles=("Judge, Business Court of Texas",
                                     "Judge", "Presiding Judge")),
)
PROFILES[TEXBIZCT.court_id] = TEXBIZCT

STYLE_FENCED = "texbizct cover, fenced title"
STYLE_BARE = "texbizct cover, bare title"

# --------------------------------------------------------------------------
# the landmarks — each one MEASURED, and none of them a case's words
# --------------------------------------------------------------------------

# The masthead. The court sets its name in title case in most divisions and
# in full caps in the Eighth, and the trailing comma is a typographic choice
# ('The Business Court of Texas,' / 'THE BUSINESS COURT OF TEXAS'), so the
# match is on the court's name alone and the case is ignored.
_MASTHEAD = re.compile(r"^THE\s+BUSINESS\s+COURT\s+OF\s+TEXAS\s*,?$", re.I)
# The division row that stands under it. A closed vocabulary: eleven numbered
# divisions — but the chambers write the number BOTH WAYS, as an ordinal word
# ('Eleventh Division') and as a numeral ('1st Division',
# dallas_sports_club_v._dse_hockey_arena). Read only as words, the numeral
# form fell through to the box branch and was tinted `caption` — a party row
# that is not a party, which is worse than an untagged row.
_DIVISION = re.compile(
    r"^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth"
    r"|Eleventh|\d{1,2}(?:st|nd|rd|th))\s+Division\s*,?$", re.I)
# The court's own public-domain citation. The reporter's abbreviation is
# still settling: 36 records print '2026 Tex. Bus. 35' and two print
# '2026 Tex. Bus. Ct. 47' (both synergy_thermogen records), so the 'Ct.' is
# optional. Four records print no citation at all
# (plains_pipeline_v._arrowhead, dallas_sports_group_v._dse_hockey_club, and
# the two the clerk stamped over) — no citation read is not an error.
_CITATION = re.compile(
    r"^(\d{4}\s+Tex\.\s*Bus\.(?:\s*Ct\.)?\s*\d+)\s*$", re.I)
# The clerk's FILED stamp. Two cues, and it is a RUN: the run opens on
# 'FILED IN' and the rows under it name the court, the clerk, the action and
# the date. Identified as a run in the TOP BAND, never row by row — 'BUSINESS
# COURT OF TEXAS' alone is also the masthead.
_STAMP_OPEN = re.compile(r"^(FILED IN|E-?FILED)\b", re.I)
_STAMP_ROWS = re.compile(
    r"^(BUSINESS COURT OF TEXAS|[A-Z][A-Za-z.\s]+,\s*(DEPUTY )?CLERK"
    r"|ENTERED|FILED|ACCEPTED|\d{1,2}/\d{1,2}/\d{4}"
    r"|\d{1,2}/\d{1,2}/\d{4}\s+\d.*)$", re.I)
# The right column's only tenant: the cause number the Business Court
# assigns. '25-BC11B-0099' — two-digit year, 'BC', the division, a letter for
# the judge, the sequence. Read as a labelled number so a division that
# labels it 'Cause Number' or 'Case No.' is still read.
_CAUSE = re.compile(
    r"^(?:Cause|Case)\s*(?:No\.?|Number)\s*[:.]?\s*(\S.*)$", re.I)
# The typed rule: a run of box-drawing horizontals and nothing else.
_TYPED_RULE = re.compile(r"^[═=─—_]{8,}$")
# The pivot, on its own row in the party column.
_PIVOT = re.compile(r"^v\s*\.?\s*$|^vs\s*\.?\s*$", re.I)
# A party's STATUS — a closed role vocabulary, and the reason a status row is
# not mistaken for a party name. Texas trial-court practice sets these and
# their counter- and third-party compounds.
_STATUS = re.compile(
    r"^(Plaintiffs?|Defendants?|Petitioners?|Respondents?|Intervenors?"
    r"|Relators?|Counter-?(Plaintiffs?|Defendants?|Claimants?)"
    r"|Third-?Party\s+(Plaintiffs?|Defendants?)|Cross-?(Plaintiffs?"
    r"|Defendants?)|Movants?|Appellants?|Appellees?)\b", re.I)
# The paragraph mark the body opens on. This court numbers every paragraph,
# so the first '¶' is the end of the cover as surely as a byline is.
_PARA = re.compile(r"^¶\s*\d+")

_RAIL_GLYPH = "§"
_RAIL_WINDOW = 8.0        # a glyph this close to the rail's x IS the rail
_RAIL_GAP_MAX = 60.0      # …and the next row of the same rail is this near
_RAIL_MIN_ROWS = 3        # fewer stacked glyphs than this is not a rail
_AXIS_TOL = 26.0          # centred on the page axis, at this court's measure
_COVER_PAGES = 3          # the second cover is never later than page 3
_TOP_BAND = 110.0         # the stamp's band, in points from the sheet's head
_TITLE_ROWS_MAX = 6       # the longest title the court prints is four rows


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The caption's rail on ``pm``: {'x', 'top', 'bottom'}, or None.

    A rail is a COLUMN of '§' — glyphs stacked at one x — grown outward one
    contiguous step at a time, so a section sign standing somewhere else on
    the page (a footnote's 'Tex. Gov't Code § 25A.004') is barred by the gap
    bound however close its x happens to fall. Delaware's reader arrived at
    the same test independently; this is the same paper's divider.
    """
    chars = [c for line in pm.lines for c in line.chars
             if (c.get("text") or "") == _RAIL_GLYPH]
    if not chars:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    column = sorted((c for c in chars if abs(c["x0"] - x) <= 4.0),
                    key=lambda c: c["top"])
    if len(column) < _RAIL_MIN_ROWS:
        return None
    run = [column[0]]
    for ch in column[1:]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    if len(run) < _RAIL_MIN_ROWS:
        return None
    return {"x": float(x), "top": min(c["top"] for c in run),
            "bottom": max(c["top"] for c in run)}


def _shed(line, rail):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == _RAIL_GLYPH
                    and lo <= c["x0"] <= hi)]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the rail, or None.

    THE SPLIT IS CHAR BY CHAR, not by the row's own x0 — whether pdfio broke a
    row at its column gap is an accident of how wide the gap happened to be.
    simpson_v._simson returns 'BOBBY R. SIMPSON and HARDBALL §' as one run
    reaching from the party column across the rail, and may_v._ineos (a scan)
    returns 'ROBERTS. MAY, FOXBOROUGH ENERGY §' the same way. By the row's x0
    both would file the rail's glyph in the party column."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _strip_rail(text: str) -> str:
    """The glyph off whichever side pdfio glued it to. It is the drawn
    divider, not a word of either column."""
    text = text.strip()
    while text.startswith(_RAIL_GLYPH):
        text = text[len(_RAIL_GLYPH):].lstrip()
    while text.endswith(_RAIL_GLYPH):
        text = text[:-len(_RAIL_GLYPH)].rstrip()
    return text


def _rows(pm, finder) -> list[list]:
    """The page's rows, each a list of the same-baseline pieces."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


def _box_close(rows: list, rail: dict) -> float:
    """THE BOX'S LAST ROW IS NOT ALWAYS ITS LAST '§'.

    The rail is drawn BESIDE the party stack, and this court's chambers
    routinely set the stack's closing status row one pitch BELOW the last
    glyph: 'Defendants.' stands at 385.9 on yaun_v._battle__sands_energy
    where the rail's last glyph is at 379.7, and 'Defendants' at 407.2 on
    dallas_sports_club where it is at 395.2. Closed at the glyph, that row
    fell out of the box, sat at the party indent so it was not centred, and
    ENDED THE WALK — so the title band below it was never reached and seven
    records lost their `title`.

    Measured in the box's OWN PITCH (the smallest gap between the rail's
    rows): the row below the last glyph stands ONE pitch down where it is the
    stack's closing status, and the typed '═' rule the court fences the title
    with stands further. So a row belongs to the box when it follows within
    one and a half pitches AND stands wholly left of the rail's column — the
    same two questions the split inside the box asks, and no wording either
    time.
    """
    tops = sorted({round(g[0].top, 1) for g in rows
                   if rail["top"] - 1.0 <= g[0].top <= rail["bottom"] + 1.0})
    gaps = [b - a for a, b in zip(tops, tops[1:]) if b - a > 1.0]
    pitch = min(gaps) if gaps else 16.0
    bottom = rail["bottom"]
    for group in rows:
        top = group[0].top
        if top <= bottom + 1.0:
            continue
        if top - bottom > pitch * 1.5:
            break
        if max(l.x1 for l in group) >= rail["x"]:
            break               # it reaches the rail's column: not the stack
        bottom = top
    return bottom, pitch


def _row(parts: list, role: str):
    """One printed row of a caption column, as an HmLine. Provenance
    survives the merge: every piece's id goes into the Prov."""
    parts = sorted(parts, key=lambda l: l.x0)
    if not parts:
        return m.HmLine(text="", prov=m.Prov(1), align=m.Align.LEFT, role=role)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return m.HmLine(
        text=_strip_rail(text),
        prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from. A claim must be TOTAL:
    every id in `consumed` is in an item, a block, or a Dropped."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.anchor: list[int] = []

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def rule(self, group: list) -> None:
        """A TYPED rule the court set as a fence — drawn by the render, not
        printed as forty box-drawing characters of text."""
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="texbizct")
def read_headmatter_texbizct(model, geom, **_):
    """Read the Business Court's cover sheet(s), or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    ctx = _Ctx()
    styles: list[str] = []
    read_any = False
    for pm in model.pages[:_COVER_PAGES]:
        style = _read_cover(pm, ctx, finder, first=not read_any)
        if style is None:
            # A page without a cover ends the search only if we already have
            # one: the second cover stands on page 3 on enosis_investments,
            # with a page of syllabus prose between.
            continue
        styles.append(style)
        read_any = True
    if not read_any:
        return NOTHING
    ctx.crit.setdefault("headmatter_style", styles[0])
    return ctx.result()


def _read_cover(pm, ctx: _Ctx, finder, first: bool) -> str | None:
    """Read one cover sheet off page ``pm``, in place. Returns the style
    name, or None when this page prints no cover.

    THE DISPATCH IS THE LANDMARK PAIR, never a title: the masthead naming
    the court and the '§' RAIL beneath it. Either alone is not the cover —
    a footnote citing 'Tex. Gov't Code § 25A.004' stacks no column, and the
    masthead's words appear inside the clerk's stamp as well.
    """
    rows = _rows(pm, finder)
    if len(rows) < 4:
        return None
    mast = None
    for i, group in enumerate(rows):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD.match(text) and group[0].top > _TOP_BAND:
            mast = i
            break
    if mast is None:
        return None
    rail = _rail(pm)
    if rail is None or rail["top"] < rows[mast][0].top:
        return None
    mid = rail["x"]

    # THE BOX IS THE BAND THE RAIL'S OWN COLUMN SPANS, and one pitch past its
    # foot (see `_box_close`). A row of the party column and the '§' beside it
    # do not always share a top, so a row carrying no glyph does not mean the
    # box has closed.
    box_bottom, pitch = _box_close(rows, rail)

    left: list = []
    right: list = []
    parties: list[str] = []
    cause: str | None = None
    box_ids: set[int] = set()
    band = "head" if first else "cover"
    title_rows: list[list] = []

    for idx, group in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        top = pieces[0].top
        span0, span1 = pieces[0].x0, max(l.x1 for l in pieces)
        centred = abs((span0 + span1) / 2 - pm.width / 2) <= _AXIS_TOL

        # --- above the masthead: the stamp and the citation ---------------
        if idx < mast:
            # THE CITATION AND THE STAMP CAN SHARE A BASELINE. The stamp is
            # set flush right and the citation on the page axis, and on
            # crain_v._northern the clerk's date lands on the citation's own
            # line: pdfio returns them as two pieces of one row
            # ('2026 Tex. Bus. 11' + '3/11/2026'). Read as a joined row it
            # matched neither pattern, so the citation was dropped as part of
            # the stamp. The pieces are therefore judged ONE AT A TIME.
            cite = [p for p in pieces if _CITATION.match(_norm(p.plain))]
            if cite:
                if first:
                    ctx.crit.setdefault(
                        "citation", _norm(cite[0].plain))
                ctx.emit(cite, "citation")
                rest = [p for p in pieces if p not in cite]
                if rest and top <= _TOP_BAND:
                    ctx.drop(rest, "stamp")
                continue
            if top <= _TOP_BAND and (_STAMP_OPEN.match(text)
                                     or _STAMP_ROWS.match(text)):
                ctx.drop(pieces, "stamp")
                continue
            # Anything else above the masthead is at no position this paper
            # uses; left to core rather than tinted with a guess.
            continue

        if _MASTHEAD.match(text) or _DIVISION.match(text):
            if first:
                prior = ctx.crit.get("court")
                ctx.crit["court"] = f"{prior}, {text}" if prior else text
            ctx.emit(pieces, "court")
            continue

        # --- the box ------------------------------------------------------
        # THE BOX HAS A HEAD AS WELL AS A FOOT. Bounded only below, the
        # branch took every row standing between the masthead and the rail's
        # first glyph — which is where an unrecognized masthead row stands
        # ('1st Division') — and filed it in the party column.
        if band != "title" and rail["top"] - pitch <= top <= box_bottom + 1.0:
            l_parts, r_parts = [], []
            for line in pieces:
                bare = _shed(line, rail)
                if bare is None:
                    continue
                for want, bucket in (("L", l_parts), ("R", r_parts)):
                    part = _side(bare, mid, want)
                    if part is not None:
                        bucket.append(part)
            r_text = _strip_rail(_norm(" ".join(l.plain for l in r_parts)))
            got = _CAUSE.match(r_text)
            left.append(_row(l_parts, "caption"))
            right.append(_row(r_parts, "docket" if got else "caption"))
            box_ids.update(l.id for l in pieces)
            for part in l_parts:
                one = _norm(part.plain).rstrip(",")
                if one and not _PIVOT.match(one) and not _STATUS.match(one):
                    parties.append(one)
            if got and cause is None:
                cause = _norm(got.group(1))
            band = "box"
            continue
        if band == "box":
            band = "title"

        # --- the title band ----------------------------------------------
        if band != "title":
            continue
        if _TYPED_RULE.match(text):
            ctx.rule(pieces)
            # The closing rule ends the cover. The opening one does not.
            if title_rows:
                break
            continue
        if _PARA.match(text) or not centred:
            break               # the writing has begun
        title_rows.append(pieces)
        if len(title_rows) >= _TITLE_ROWS_MAX:
            break

    if not left:
        return None
    fenced = any(isinstance(i, m.Rule) for i in ctx.items[-4:])

    # THE BOX, placed where the page prints it. The rail runs a few rows past
    # the last words, and those empty pairs are trimmed (ca6's rule).
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
    if not left:
        return None
    block = m.CaptionBlock(
        left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
        style_id="section-rail",
        fp={"rail": _RAIL_GLYPH, "mid_x": round(mid, 1)},
        prov=m.Prov(pm.number, tuple(sorted(box_ids))))
    # The block goes in ahead of the title band and the rules, and behind the
    # citation and the masthead — the page's own order, never appended.
    head = [i for i in ctx.items
            if getattr(i, "role", "") in ("citation", "court")
            or isinstance(i, m.CaptionBlock)]
    ctx.items = head + [block] + [i for i in ctx.items if i not in head]
    ctx.consumed.update(box_ids)

    # THE TITLE, and it is also the writing's anchor: an unsigned memorandum
    # opinion has nothing else to open on, so its ids go to `anchor_ids` for
    # core's rescue pass.
    for pieces in title_rows:
        ctx.emit(pieces, "title")
        ctx.anchor.extend(p.id for p in pieces)
    if title_rows and first:
        ctx.crit.setdefault("title", _norm(" ".join(
            _norm(" ".join(l.plain for l in sorted(g, key=lambda l: l.x0)))
            for g in title_rows)))
    if first:
        if cause:
            ctx.crit.setdefault("docket_number", cause)
        elif parties:
            pass
        if parties:
            ctx.crit.setdefault("parties", parties[:8])
            ctx.crit.setdefault("caption", [_text_of(r) for r in left
                                            if _text_of(r)][:12])
    elif cause and not ctx.crit.get("docket_number"):
        ctx.crit["docket_number"] = cause
    return STYLE_FENCED if fenced else STYLE_BARE
