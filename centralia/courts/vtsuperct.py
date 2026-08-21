"""Vermont Superior Court ('vtsuperct').

Everything unique to vtsuperct lives here. It imports core, never another
court file, and no other court file imports it — NOT `vt.py`. The Supreme
Court's two papers (the Reporter's notice slip with its whitespace-gutter
caption, and the '}' entry order) appear on NONE of these 42 records. A trial
court writes on the courthouse's own stationery, and that is what this file
reads.

THE PAPER IS A LETTERHEAD. Measured over all 42 records, page 1:

    ┌──────────────────────────────────────────────────────────────────────┐
    │                              Vermont Superior Court │ the e-filing   │
    │                                     Filed 04/17/26  │ stamp, flush   │
    │                                     Chittenden Unit │ right in the   │
    │                                                     │ TOP MARGIN     │
    │ VERMONT SUPERIOR COURT                CIVIL DIVISION │ court │ divn   │
    │ Chittenden Unit                 Case No. 22-CV-03657 │ seat  │ docket │
    │ 175 Main Street                                      │ the address —  │
    │ Burlington VT 05402                                  │ four rows of   │
    │ 802-863-3467                                         │ stationery,    │
    │ www.vermontjudiciary.org                             │ -> Dropped     │
    │                                                                      │
    │ Anna Ardesh,                     │ DECISION ON MOTIONS  the caption,  │
    │      Plaintiff                   │                      two columns   │
    │      v                           │                      over an       │
    │ O'Reilly Auto Enterprises, LLC,  │                      UNDRAWN       │
    │      Defendant                   │                      gutter        │
    │            RULING ON MOTIONS IN LIMINE       …then the sub-title      │
    │      This personal injury action arising out of a motor vehicle …     │
    └──────────────────────────────────────────────────────────────────────┘

37 of the 42 print the judiciary URL as the last row of that stationery
(fuzzily: OCR gives 'www.verm0ntjudiciary.org' on laundry_v._billings and
'wwwvermontjudiciaryorg' on lockerby_v._doc, so the row is matched on
'judiciary' alone). Two print no stationery at all (johnson_v._mrv_holdings,
utopian_v._castleton_state_college — 'STATE OF VERMONT' over 'SUPERIOR COURT
│ CIVIL DIVISION'), and two extract ZERO characters (chittenden_resorts_v.
_gerlach, crannell_v._pallito: pure scans, no OCR layer) and get NOTHING.

THE CLOSE IS THE PARAGRAPH INDENT, and it is invariant. Every one of the 40
records with text opens its first paragraph at the body rail + 36.0pt (range
34.8-36.3 over 40 records; nothing else in the head stands there). That is
where the reader stops, and it never reaches into the writing. The rail is
measured as the SMALLEST x0 that four or more page-1 rows below the
stationery share — `geom.body_x0` is 512.0 on mckenzie_v._quitin_point_condos
and 58.0 on lockerby_v._doc where the real rail is 72.2 and 57.6 (see CORE
DEFECTS below), and the letterhead's own rail is LEFT of the body's on
mason_v._jackson (68.4 vs 72.2) and peacefield_site_plan_approval (61.4 vs
72.0), so neither the profile's number nor the page's first row will do.

THREE HEADS, and the caption's own DIVIDER says which. Nothing is decided by
wording:

  * 'paren rail' (1 record — johnson_v._mrv_holdings). A ')' column, 42
    glyphs at x0=288.0. Corpus-wide this court types 42 parens in one column
    and never more than ONE at any other x, and draws 14 vertical rules over
    ~250 pages, none of them beside a caption — so the rail is johnson's
    alone and a drawn-divider branch would be a guess dressed as a reading.

  * 'gutter caption' (12 records — 3111_cross_road, anr_v._yates, ardesh,
    dearden, fish, hillview_heights, honos_real_estate, immich, state_v.
    _exxon_mobil, stewart, town_of_richford, town_of_rockingham). Two columns
    over an UNDRAWN gutter: the parties left, WHAT THE PAPER IS ('DECISION ON
    MOTION', 'MERITS DECISION', 'FINDINGS OF FACTS AND / CONCLUSIONS OF LAW')
    right. The gutter is the PAGE AXIS and the clearance is 18pt: over those
    12 records every left piece ends at or before x1=312.9 and every right
    piece starts at or after x0=324.0. Membership is by side, never by text.

  * 'single column' (27 records). No divider and no right column: the case
    name centred on the axis (26 of them — |centre − axis| ≤ 2.0 on every
    row of the band) or, on the one scan that prints none,
    utopian_v._castleton_state_college, a party stack at the rail.

WHAT THE PAPER CALLS ITSELF is a closed vocabulary — the court's own names
for its own papers, and the only place in this file where a row is read by
its words. In the single-column head the case name and the title are the
same size on in_re_thomas and state_v._tiktok (12.0/12.0), so size alone
cannot part them; the title opens on ENTRY / DECISION / ORDER / OPINION /
RULING / FINDINGS / MERITS / JUDGMENT / CONCLUSIONS on all 27, and no case
name in the corpus opens on any of them.

THE ENTRY ORDER IS A LABEL GRID (13 records). Under 'ENTRY REGARDING
MOTION(S)' the court sets a two-column grid — the label at the rail, the
value at x0=144 — and closes it with its ruling:

    Title:        Motion for Summary Judgment (Motion: 6)
    Filer:        Brian P. Monaghan
    Filed Date:   October 01, 2025
    The motion is GRANTED.

Five of the 13 print that last row (1124_harwood_hill, groundworks,
estate_of_mayotte, moody, peacefield); the other eight run straight into the
body. So THE DISPOSITION IS A LOOKAHEAD, not a landmark: after the grid the
reader scans up to eight rows for a row that opens 'The motion(s) is/are'
AND carries an upper-case ruling word, and claims through it when it finds
one. peacefield needs exactly that — it lists three further filings at the
paragraph indent (x0=108.5, full measure) BEFORE its ruling, and the indent
test alone hands six rows of the entry order to the writing.

SCAN DEBRIS IS RECORDED, NOT READ. Nine records carry stray glyph runs from
the raster the e-filing tool re-OCRs — 'KY' at x0=297.1 (1124_harwood_hill,
groundworks, honos, town_of_richford), '8 ESE' at 288.7 (honos), '1 SES' at
284.2 and 'WE' at 308.9 (peacefield), 'i?'/'J?4'/'£3' (laundry), '£3:'/'f1'
(lockerby), 'i'/'an' (stewart), a lone apostrophe (utopian). Left in, 'WE' is
peacefield's case name and the apostrophe is utopian's. A piece carrying
fewer than five alphanumerics that stands neither at the rail, nor at the
paragraph indent, nor in the grid's value column, nor right of the axis in a
docket or division cell, is that debris — recorded as Dropped, never
rendered as content. maynus_v._state's '15)' and rivard_v._state's '37)' are
grid-value and rail rows respectively, and are kept.

WHAT THIS FILE DOES NOT DO. There is no roster and no appearance block in
this court's headmatter: one judge signs at the FOOT ('Electronically signed
… / Timothy B. Tomasi, Superior Court Judge'), which is core's to read, and
where the appearances are named at all they are named in the first paragraph
of the ruling ('The Appellant was represented by Attorney Frank Urso'), where
nothing may reach in to take them. So `panel`, `judges` and `attorneys` are
left empty here BY MEASUREMENT — over all 42 records page 1 carries no row
that `roster_names()` could split.

CORE DEFECTS FOUND (reported, not patched):

 1. THE LETTERHEAD'S TELEPHONE NUMBER READS AS A DOCKET. Before this reader,
    19 of the 42 records carried `other_dockets=['802-951-1740']` (or the
    other seven courthouse numbers) and ardesh_v._oreilly_auto carried
    `docket_number='802-863-3467'` — its real number, 'Case Nos.
    22-CV-03657', was never read. `looks_like_docket` accepts a
    'nnn-nnn-nnnn' run.
 2. `geometry.measure` PUT THE BODY RAIL AT 512.0 on
    mckenzie_v._quitin_point_condos, whose text sets at 72.2 — the value is
    to the right of the page's own measure. On lockerby_v._doc and
    ard_realty_v._dept_health it reports 58.0, which is the rail, but a
    modal-x0 read of page 1 alone returns 94 (the block quotations); both
    numbers are wrong for one of the two records, which is why this file
    measures its own.
 3. FurnitureFinder CALLS THE MASTHEAD'S DOCKET CELL A STAMP. On
    laundry_v._billings 'Case No. 23—CV—01133' (top 89.5, flush right) is
    classified `stamp` and removed, so the record had no docket at all; on
    in_re_combs and mckenzie the masthead's court row is called a
    `running-head`. This reader walks the RAW rows for that reason.
"""

from __future__ import annotations

import re
from collections import Counter

from .. import model as m
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, Trace, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import read_parties
from . import PROFILES

# ---- the profile ---------------------------------------------------------
# ONE PAPER, ONE WRITING. This is a trial court: a single judge rules and
# signs at the foot, so there is no panel to concur in or dissent from.
# Measured over the corpus — 40 of 42 records assemble exactly one writing
# and the other two extract no text at all.
VTSUPERCT = CourtProfile(
    "vtsuperct", "Vermont Superior Court",
    single_writing=True,
)
PROFILES[VTSUPERCT.court_id] = VTSUPERCT

# ---- vtsuperct's declared facts (measured over all 42 records) -----------

# The whole block stands on page 1 on every record; nothing spills over.
_MAX_PAGES = 1
# THE PARAGRAPH INDENT. 36.0pt off the rail, measured 34.8-36.3 over the 40
# records with text. This is the CLOSE, so the tolerance is tight: the title
# of in_re_combs stands at rail+41.8 and must not be mistaken for it.
_PARA_INDENT = 36.0
# …and the tolerance is 2.5, not more. Measured over the 40 records the
# indent is 34.8-36.3 (|delta| <= 1.3), and two rows in the corpus stand
# just outside it and must NOT close the head: in_re_combs' title at
# rail+41.8, and utopian_v._castleton_state_college's SECOND title row at
# rail+39.4 — a scan, full measure, which at a tolerance of 3.5 read as the
# first paragraph and took half the title into the writing.
_PARA_TOL = 2.5
# …and a first body line runs at least this much of the measure (0.80-1.00
# over the corpus; the shortest is abel_v._doc at 0.85).
_BODY_MEASURE = 0.6
# A row is AT THE RAIL within this. The stationery's rail differs from the
# body's by up to 10.6pt (peacefield), so the two are measured separately.
_RAIL_TOL = 2.5
# The rail measurement: the smallest x0 that this many page-1 rows share,
# clustered within _RAIL_CLUSTER, ignoring the stationery band above
# _HEAD_BAND (every URL row in the corpus tops at 116.1-152.5).
_RAIL_MIN_ROWS = 4
_RAIL_CLUSTER = 1.5
_HEAD_BAND = 160.0
# THE GRID'S VALUE COLUMN, invariant at x0=144.0 over the 13 entry orders.
_GRID_VALUE = 144.0
# The e-filing stamp lives in the top margin, above everything.
_STAMP_TOP = 45.0
# A row is CENTRED ON THE PAGE AXIS within this. 2.0 covers the 26
# single-column heads; johnson_v._mrv_holdings is a skewed scan whose title
# centres 16.5pt left of the axis, so its band is bounded by the rail
# instead and this number does not have to carry it.
_AXIS_TOL = 6.0
# The gutter's clearance: over the 12 gutter captions every left piece ends
# by x1=312.9 and every right piece starts at x0=324.0 — 11pt of daylight
# either side of the axis.
_GUTTER_PAD = 12.0
# THE ')' RAIL. One record types one (johnson, 42 glyphs at x0=288.0); no
# other x in the corpus carries more than one paren at a line's own edge.
_RAIL_GLYPH = ")"
_RAIL_FLOOR = 3
_RAIL_WINDOW = 6.0
# How far past the grid the ruling may stand (peacefield: 7 rows).
_DISPO_LOOKAHEAD = 8
# Fewer alphanumerics than this and a stranded piece is scan debris.
_DEBRIS_ALNUM = 5

STYLE_RAIL = "paren rail"
STYLE_GUTTER = "gutter caption"
STYLE_SINGLE = "single column"

# ---- what the masthead says (closed vocabularies) ------------------------

# The court, at the rail. 'VERMONT SUPERIOR COURT' on 36 records,
# 'SUPERIOR COURT' on 3 (abel, in_re_thomas, laundry, johnson, utopian).
_COURT_ROW = re.compile(r"^(?:VERMONT\s+)?SUPERIOR\s+COURT\s*$", re.I)
# 'STATE OF VERMONT', centred, above the masthead on the two records that
# print no stationery. Required WITHOUT a trailing comma: 'STATE OF
# VERMONT,' is state_v._exxon_mobil's plaintiff, in its caption.
_STATE_ROW = re.compile(r"^STATE\s+OF\s+VERMONT$", re.I)
# The division: 'CIVIL DIVISION' (32) / 'ENVIRONMENTAL DIVISION' (2) flush
# right, or 'Environmental Division' (6) at the rail on the row below.
_DIVISION = re.compile(
    r"^(?:CIVIL|ENVIRONMENTAL|CRIMINAL|FAMILY|PROBATE)\s+DIVISION\s*$", re.I)
# The seat: '<County> Unit'. OCR welds the address into it on
# stewart_v._vt_construction ('PGOranBdoxIsl7e Unit'), so the row is matched
# on the word alone.
_UNIT = re.compile(r"\bUnits?\b", re.I)
# The docket, flush right: 'Case No. 25-CV-01029' / 'Case Nos. 22-CV-03657'
# / 'Docket No. 24-ENV-00103' / 'Case NO. 23-SC-01948' / 'No. 21-CV-171'.
_DOCKET = re.compile(r"^(?:Case|Docket|File)?\s*Nos?\.?\s*:?\s*(\S.*)$", re.I)
# …and what a docket number looks like once the label is off: two digits, a
# division tag, a serial. 'Case No. 23—CV—01133' arrives em-dashed.
_DOCKET_BODY = re.compile(
    r"^\d{2}\s*[-—–]\s*[A-Z]{2,4}\s*[-—–]\s*\d{3,6}$", re.I)

# The stationery's address rows, and the row that closes the band.
_URL = re.compile(r"judiciary", re.I)

# The e-filing stamp's own rows, flush right in the top margin. Matched
# loosely because the tool rasterises and re-OCRs them ('7ermont Superior
# Court', 'Chittenden UUnit', 'Washington Cae', 'Filed 01/0').
_STAMP_FILED = re.compile(r"^Filed\b\s*(\d{1,2}/\d{1,2}/\d{2,4})?", re.I)

# ---- what the paper calls itself ----------------------------------------
# A CLOSED VOCABULARY: the court's own names for its own papers. Used only
# to part the case name from the title in the single-column head.
_TITLE_OPENERS = (
    "entry", "decision", "order", "opinion", "ruling", "findings",
    "merits", "judgment", "conclusions", "memorandum",
)
# The ruling that closes an entry order.
_DISPOSITION = re.compile(r"^The\s+motions?\s+(?:is|are|was|were)\b", re.I)
# The grid's labels, at the rail.
_GRID_LABEL = re.compile(
    r"^(?:Title|Filer|Filed\s+[Dd]ate|Motion|Response|Reply)\s*:", re.I)
# The pivot, which is short and must never read as debris.
_PIVOT = re.compile(r"^v(?:s)?\.?$", re.I)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _alnum(text: str) -> int:
    return sum(1 for c in text if c.isalnum())


# --------------------------------------------------------------------------
# the page, measured
# --------------------------------------------------------------------------

def _raw_rows(pm) -> list[list]:
    """Every inked row of the page, grouped by baseline, FURNITURE INCLUDED.

    The stationery is furniture to core and content to this court:
    FurnitureFinder calls laundry_v._billings' masthead docket cell a
    `stamp` and in_re_combs' masthead a `running-head`, so a filtered walk
    never sees the docket at all (core defect 3)."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _measure_rail(pm) -> float | None:
    """The BODY rail: the smallest x0 that _RAIL_MIN_ROWS page-1 rows share
    below the stationery band. See the docstring on why neither
    `geom.body_x0` nor the page's first row will do."""
    xs = sorted(l.x0 for l in pm.lines
                if l.plain.strip() and l.top >= _HEAD_BAND)
    for i, x in enumerate(xs):
        n = sum(1 for y in xs[i:] if y - x <= _RAIL_CLUSTER)
        if n >= _RAIL_MIN_ROWS:
            band = [y for y in xs[i:] if y - x <= _RAIL_CLUSTER]
            return sum(band) / len(band)
    return None


def _paren_rail(pm) -> float | None:
    """The ')' column, or None — a COLUMN of glyphs at one x, seeded from
    the parens that stand at a line's own edge (the delsuperct reading)."""
    edge: list = []
    for line in pm.lines:
        inked = [c for c in line.chars if (c.get("text") or "").strip()]
        for c in (inked[:1] + inked[-1:]):
            if (c.get("text") or "") == _RAIL_GLYPH:
                edge.append(c)
    if len(edge) < _RAIL_FLOOR:
        return None
    x, n = Counter(round(c["x0"]) for c in edge).most_common(1)[0]
    if n < _RAIL_FLOOR:
        return None
    return float(x)


def _shed_rail(line, rail_x: float):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character."""
    from dataclasses import replace as _replace
    lo, hi = rail_x - _RAIL_WINDOW, rail_x + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == _RAIL_GLYPH
                    and lo <= c["x0"] <= hi)]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, pm, rail: float, finder=None):
        self.pm = pm
        self.finder = finder
        self.rail = rail
        self.axis = pm.width / 2.0
        self.right = max((l.x1 for l in pm.lines if l.plain.strip()),
                         default=pm.width - 72.0)
        self.items: list = []
        self.dropped: list = []
        self.consumed: set = set()
        self.anchor: list = []
        self.crit: dict = {}

    # -- geometry the whole walk asks about --------------------------------

    def at_rail(self, line) -> bool:
        return abs(line.x0 - self.rail) <= _RAIL_TOL

    def at_indent(self, line) -> bool:
        return abs(line.x0 - (self.rail + _PARA_INDENT)) <= _PARA_TOL

    def centred(self, pieces) -> bool:
        x0 = min(p.x0 for p in pieces)
        x1 = max(p.x1 for p in pieces)
        return abs((x0 + x1) / 2.0 - self.axis) <= _AXIS_TOL

    def is_body(self, pieces) -> bool:
        """BODY PROSE: one piece at the paragraph indent, full measure."""
        if len(pieces) != 1:
            return False
        line = pieces[0]
        if not self.at_indent(line):
            return False
        measure = self.right - self.rail
        return measure > 0 and (line.x1 - line.x0) >= _BODY_MEASURE * measure

    def is_debris(self, line) -> bool:
        """A stray glyph run from the raster the e-filing tool re-OCRs."""
        text = _norm(line.plain)
        if _alnum(text) >= _DEBRIS_ALNUM or not text:
            return False
        if _PIVOT.match(text.rstrip(",")):
            return False
        if set(text) <= {_RAIL_GLYPH}:
            return False    # the divider, not debris — the rail sheds it
        for edge in (self.rail, self.rail + _PARA_INDENT, _GRID_VALUE):
            if abs(line.x0 - edge) <= _RAIL_TOL + 2.0:
                return False
        return True

    # -- emitting ---------------------------------------------------------

    def _hm(self, pieces, role: str, align: m.Align) -> m.HmLine:
        text = ""
        for part in pieces:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = pieces[0]
        return m.HmLine(
            text=text.strip(), prov=m.Prov(first.page,
                                           tuple(p.id for p in pieces)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in pieces), role=role)

    def row(self, pieces, role: str, align: m.Align | None = None) -> None:
        if not pieces:
            return
        if align is None:
            align = m.Align.CENTER if self.centred(pieces) else m.Align.LEFT
        self.items.append(self._hm(pieces, role, align))
        self.consumed.update(p.id for p in pieces)

    def cell(self, pieces, role: str) -> m.HmLine:
        """A column cell — built, not emitted: it goes in a CaptionBlock."""
        self.consumed.update(p.id for p in pieces)
        return self._hm(pieces, role, m.Align.LEFT)

    def blank(self) -> m.HmLine:
        return m.HmLine(text="", prov=m.Prov(self.pm.number), role="")

    def caption(self, left: list, right: list, rail, ids) -> None:
        # THE GUTTER IS WHITE SPACE on 12 of the 13 two-column records, and
        # `rail=None` is a measurement: this court draws 14 vertical rules
        # over ~250 pages and none of them beside a caption. What it does
        # type — johnson's ')' column — is recorded, so the label and the
        # reproduction cannot disagree.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=rail, rail_rows=len(left),
            style_id="whitespace-gutter" if rail is None else "paren-rail",
            fp={"rail": rail, "axis": round(self.axis, 1),
                "gutter_pad": _GUTTER_PAD},
            prov=m.Prov(self.pm.number, tuple(sorted(ids)))))

    def drop(self, pieces, kind: str) -> None:
        if not pieces:
            return
        # CORE RECORDS ITS OWN FURNITURE. Where FurnitureFinder classifies a
        # row, the pipeline publishes a Dropped for it whether this reader
        # consumed it or not (measured on fish_v._diocese_of_gaylord: the
        # three stamp rows and '175 Main Street' appear in `doc.dropped`
        # either way), so recording them again lists the same stamp twice.
        # The rows it does NOT classify — rivard, winney, utopian, mason —
        # are this reader's to record, and they are recorded.
        if self.finder is not None:
            mine = [p for p in pieces if not self.finder.kind(self.pm, p)]
            self.consumed.update(p.id for p in pieces)
            pieces = mine
            if not pieces:
                return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in pieces))[:400],
            prov=m.Prov(pieces[0].page, tuple(p.id for p in pieces)),
            kind=kind))
        self.consumed.update(p.id for p in pieces)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="vtsuperct")
def read_headmatter_vtsuperct(model, geom, **_):
    """Read the courthouse's letterhead and the head below it, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    if pm.ink_chars == 0:
        return NOTHING            # a pure scan: nothing to read
    rows = _raw_rows(pm)
    if len(rows) < 4:
        return NOTHING
    rail = _measure_rail(pm)
    if rail is None:
        return NOTHING
    finder = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                             geom.body_size if geom else 12.0)
    ctx = _Ctx(pm, rail, finder)

    i = _read_stamp(ctx, rows)
    i = _read_masthead(ctx, rows, i)
    if not any(it.role == "court" for it in ctx.items
               if isinstance(it, m.HmLine)):
        return NOTHING            # no masthead: not this paper
    i = _read_stationery(ctx, rows, i)

    close = _find_close(ctx, rows, i)
    if close is None:
        return NOTHING            # the head never ends: refuse the record
    band = [g for g in rows[i:close] if not _drop_debris(ctx, g)]
    if not band:
        ctx.crit["headmatter_style"] = STYLE_SINGLE
        return ctx.result()

    paren = _paren_rail(pm)
    if paren is not None:
        _read_railed(ctx, band, paren)
    elif _has_right_column(ctx, band):
        _read_gutter(ctx, band)
    else:
        _read_single(ctx, band)
    return ctx.result()


def _drop_debris(ctx: _Ctx, group: list) -> bool:
    """Record the raster's stray glyphs. True when the whole row was one."""
    junk = [l for l in group if ctx.is_debris(l)]
    if not junk:
        return False
    ctx.drop(junk, "scan-debris")
    for l in junk:
        group.remove(l)
    return not group


# ---- the stamp -----------------------------------------------------------

def _read_stamp(ctx: _Ctx, rows: list) -> int:
    """The e-filing stamp: 2-4 rows flush right in the TOP MARGIN, and the
    only place the record states the day it was filed. 34 of the 42 print
    one; the date is read only when OCR returned it whole."""
    i = 0
    band: list = []
    while i < len(rows) and rows[i][0].top < _STAMP_TOP:
        band.extend(rows[i])
        i += 1
    if not band:
        return 0
    for line in band:
        mo = _STAMP_FILED.match(_norm(line.plain))
        if mo and mo.group(1):
            ctx.crit.setdefault("decision_date", mo.group(1))
    ctx.drop(band, "stamp")
    return i


# ---- the masthead --------------------------------------------------------

def _right_cell(ctx: _Ctx, pieces: list) -> list:
    """The masthead's right column: a piece RIGHT OF THE AXIS that names a
    division or carries a docket. Read by that closed vocabulary and not by
    being flush right — utopian_v._castleton_state_college is a scan whose
    'CIVIL DIVISION' stops 88pt short of the measure."""
    out = []
    for p in pieces:
        if p.x0 <= ctx.axis - 20.0:
            continue
        text = _norm(p.plain)
        if _DIVISION.match(text) or _docket_of(text):
            out.append(p)
    return out


def _docket_of(text: str) -> str | None:
    mo = _DOCKET.match(_norm(text))
    if not mo:
        return None
    body = _norm(mo.group(1)).rstrip(".,;")
    return body if _DOCKET_BODY.match(body) else None


def _read_masthead(ctx: _Ctx, rows: list, i: int) -> int:
    """'STATE OF VERMONT' / the court and its division / the seat and the
    docket. Read until a row carries none of those."""
    seen_court = False
    while i < len(rows):
        group = list(rows[i])
        if _drop_debris(ctx, group):
            i += 1
            continue
        right = _right_cell(ctx, group)
        left = [p for p in group if p not in right]
        ltext = _norm(" ".join(p.plain for p in left))
        is_state = bool(_STATE_ROW.match(ltext)) and ctx.centred(left)
        is_court = bool(_COURT_ROW.match(ltext))
        is_seat = bool(_UNIT.search(ltext) or _DIVISION.match(ltext)) \
            and len(ltext) < 60
        if not (is_state or is_court or is_seat or right):
            break
        seen_court = seen_court or is_court or is_state
        if not seen_court:
            break                 # the masthead opens on the court, always
        # Anything on a masthead row that is neither the court's own cell
        # nor a division/docket is the raster's debris.
        stray = [p for p in left
                 if not (is_state or is_court or is_seat) or ctx.is_debris(p)]
        if stray:
            ctx.drop(stray, "scan-debris")
            left = [p for p in left if p not in stray]
        if left:
            ctx.row(left, "court",
                    m.Align.CENTER if is_state else m.Align.LEFT)
            if is_court or is_state:
                ctx.crit.setdefault("court", ltext)
        for p in right:
            docket = _docket_of(_norm(p.plain))
            if docket:
                ctx.row([p], "docket", m.Align.RIGHT)
                if "docket_number" not in ctx.crit:
                    ctx.crit["docket_number"] = docket
                else:
                    ctx.crit.setdefault("other_dockets", []).append(docket)
            else:
                ctx.row([p], "court", m.Align.RIGHT)
                div = _norm(p.plain)
                if ctx.crit.get("court") and div.lower() not in \
                        ctx.crit["court"].lower():
                    ctx.crit["court"] = f"{ctx.crit['court']}, {div}"
        i += 1
    return i


def _read_stationery(ctx: _Ctx, rows: list, i: int) -> int:
    """The courthouse's ADDRESS — street, town, telephone, url. Four rows of
    printed stationery, recorded as Dropped and never rendered as content.
    Bounded by the URL row: 37 of the 42 print one, and the two that print
    no stationery at all have no band here to find."""
    end = None
    for j in range(i, min(i + 6, len(rows))):
        if any(_URL.search(_norm(p.plain)) for p in rows[j]):
            end = j
            break
    if end is None:
        return i
    band = [p for g in rows[i:end + 1] for p in g]
    ctx.drop(band, "letterhead")
    return end + 1


# ---- the close -----------------------------------------------------------

def _find_close(ctx: _Ctx, rows: list, i: int) -> int | None:
    """Where the head ends: the first BODY PROSE row, extended past an entry
    order's grid to the ruling that closes it."""
    body = None
    for j in range(i, len(rows)):
        if ctx.is_body(rows[j]):
            body = j
            break
    if body is None:
        return None
    grid = None
    for j in range(i, body):
        if any(_GRID_LABEL.match(_norm(p.plain)) for p in rows[j]):
            grid = j
    if grid is None:
        return body
    for j in range(body, min(grid + 1 + _DISPO_LOOKAHEAD, len(rows))):
        text = _norm(" ".join(p.plain for p in rows[j]))
        if _DISPOSITION.match(text) and re.search(r"\b[A-Z]{4,}\b", text):
            return j + 1
    return body


# ---- the three heads -----------------------------------------------------

def _has_right_column(ctx: _Ctx, band: list) -> bool:
    return any(p.x0 >= ctx.axis + _GUTTER_PAD for g in band for p in g)


def _is_title_row(ctx: _Ctx, group: list) -> bool:
    text = _norm(" ".join(p.plain for p in group))
    head = re.sub(r"[^A-Za-z].*$", "", text).lower()
    return head in _TITLE_OPENERS


def _read_gutter(ctx: _Ctx, band: list) -> None:
    """Two columns over the page axis: the parties left, the paper's name
    right; then the centred sub-title, which spans both."""
    left: list = []
    right: list = []
    ids: list = []
    caption_rows: list = []
    title_rows: list = []
    tail = False
    for group in band:
        l = [p for p in group if p.x0 < ctx.axis + _GUTTER_PAD]
        r = [p for p in group if p.x0 >= ctx.axis + _GUTTER_PAD]
        if not r and (tail or (left and ctx.centred(l)
                              and _is_title_row(ctx, l))):
            tail = True
            ctx.row(l, "title")
            title_rows.append(_norm(" ".join(p.plain for p in l)))
            continue
        lc = ctx.cell(l, "caption") if l else ctx.blank()
        rc = ctx.cell(r, "title") if r else ctx.blank()
        left.append(lc)
        right.append(rc)
        ids.extend(p.id for p in group)
        if l:
            caption_rows.append(_norm(" ".join(p.plain for p in l)))
        if r:
            title_rows.append(_norm(" ".join(p.plain for p in r)))
    # THE BLOCK IS EMITTED WHERE IT STANDS, before the sub-title rows the
    # walk already placed — the headmatter keeps the page's order.
    if left:
        block = m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=len(left),
            style_id="whitespace-gutter",
            fp={"rail": None, "axis": round(ctx.axis, 1),
                "gutter_pad": _GUTTER_PAD},
            prov=m.Prov(ctx.pm.number, tuple(sorted(ids))))
        ctx.items.insert(0 if not ctx.items else _insert_at(ctx), block)
    _finish(ctx, STYLE_GUTTER, caption_rows, title_rows)


def _insert_at(ctx: _Ctx) -> int:
    """Where the caption block belongs: after the masthead, before whatever
    the walk placed from below it."""
    for k, it in enumerate(ctx.items):
        if isinstance(it, m.HmLine) and it.role == "title":
            return k
    return len(ctx.items)


def _read_railed(ctx: _Ctx, band: list, paren: float) -> None:
    """johnson_v._mrv_holdings: a ')' column at x0=288.0 and nothing to the
    right of it. The rail defines the zone, so the caption ends where the
    rail ends and the title stands below it."""
    foot = max((c["bottom"] for line in ctx.pm.lines for c in line.chars
                if (c.get("text") or "") == _RAIL_GLYPH
                and abs(c["x0"] - paren) <= _RAIL_WINDOW), default=0.0)
    left: list = []
    right: list = []
    ids: list = []
    caption_rows: list = []
    title_rows: list = []
    for group in band:
        shed = [s for s in (_shed_rail(p, paren) for p in group)
                if s is not None]
        if group[0].top > foot:
            if shed:
                ctx.row(shed, "title")
                title_rows.append(_norm(" ".join(p.plain for p in shed)))
            ctx.consumed.update(p.id for p in group)
            continue
        l = [p for p in shed if p.x0 < paren]
        r = [p for p in shed if p.x0 >= paren]
        left.append(ctx.cell(l, "caption") if l else ctx.blank())
        right.append(ctx.cell(r, "title") if r else ctx.blank())
        ids.extend(p.id for p in group)
        ctx.consumed.update(p.id for p in group)
        if l:
            caption_rows.append(_norm(" ".join(p.plain for p in l)))
        if r:
            title_rows.append(_norm(" ".join(p.plain for p in r)))
    if left:
        block = m.CaptionBlock(
            left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
            style_id="paren-rail",
            fp={"rail": _RAIL_GLYPH, "x": round(paren, 1)},
            prov=m.Prov(ctx.pm.number, tuple(sorted(ids))))
        ctx.items.insert(_insert_at(ctx), block)
    _finish(ctx, STYLE_RAIL, caption_rows, title_rows)


def _read_single(ctx: _Ctx, band: list) -> None:
    """No divider and no right column: the case name, the paper's name, and
    — where the court writes an entry order — its label grid and ruling."""
    caption_rows: list = []
    title_rows: list = []
    state = "caption"
    for group in band:
        text = _norm(" ".join(p.plain for p in group))
        if _DISPOSITION.match(text):
            ctx.row(group, "disposition")
            ctx.crit.setdefault("disposition", text)
            state = "grid"
            continue
        if state != "grid" and (_GRID_LABEL.match(text)
                                or (state == "title"
                                    and len(group) > 1
                                    and abs(group[1].x0 - _GRID_VALUE) <= 3)):
            state = "grid"
        if state == "grid":
            ctx.row(group, "case-info", m.Align.LEFT)
            mo = _GRID_LABEL.match(text)
            if mo and mo.group(0).lower().startswith("title"):
                ctx.crit.setdefault("motion", _norm(text[mo.end():]))
            continue
        if state == "caption" and _is_title_row(ctx, group):
            state = "title"
        if state == "caption":
            ctx.row(group, "caption")
            caption_rows.append(text)
        else:
            ctx.row(group, "title")
            title_rows.append(text)
    _finish(ctx, STYLE_SINGLE, caption_rows, title_rows)


# ---- what the head yields ------------------------------------------------

def _finish(ctx: _Ctx, style: str, caption_rows: list,
            title_rows: list) -> None:
    ctx.crit["headmatter_style"] = style
    if caption_rows:
        ctx.crit["caption"] = caption_rows
        sides = [s.strip(" ,;.") for s in read_parties(caption_rows, Trace())]
        sides = [s for s in sides if s]
        if sides:
            ctx.crit["parties"] = sides
            if len(sides) >= 2:
                ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
            else:
                ctx.crit["case_name"] = sides[0]
        elif len(caption_rows) == 1:
            ctx.crit["case_name"] = caption_rows[0]
    if title_rows:
        ctx.crit["title"] = _norm(" ".join(title_rows))[:300]
