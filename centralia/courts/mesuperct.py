"""Maine Superior Court ('mesuperct').

Everything unique to mesuperct lives here. It imports core, never another
court file, and no other court file imports it — NOT `me.py`. Maine's
Supreme Judicial Court prints a labelled two-column ladder ('Decision:' /
'Docket:' / 'Argued:' / 'Panel:' at the label rail, values at x0 135-144);
this court prints no ladder at all, no panel, no citation and no dates in
its block. Measured over all 20 records: 0 carry a 'Docket:'-style label
row. The two papers have nothing in common but the state, so nothing is
inherited.

THE PAPER IS A TRIAL-COURT PLEADING CAPTION, and every record in the corpus
is a scan with an OCR text layer (20 of 20 flagged `scanned-source`; the old
engine refused all 20 as non-born-digital, so there is no v1 oracle here and
the PDF is the only one).

    ┌──────────────────────────────────────────────────────────────────┐
    │ STATE OF MAINE                       SUPERIOR COURT              │  the
    │ OXFORD, ss.                          CIVIL ACTION                │  masthead
    │                                      Docket No. OXFSC-CIV-2024…  │  grid
    │                                                                  │
    │ ALAN ALBANASI, et al.,      )                                    │
    │                             )                                    │
    │        Plaintiffs           )                                    │  the
    │                             )                                    │  caption
    │   v.                        )        ORDER ON                    │  box
    │                             )        MOTIONS TO DISMISS          │
    │ VEDA MAKER, et al.,         )                                    │
    │        Defendants           )                                    │
    │                                                                  │
    │     Presently before the Court are Defendant Pine Tree Legal …   │  the order
    └──────────────────────────────────────────────────────────────────┘

TWO ZONES, EACH FOUND BY A LANDMARK, NEVER BY AN ORDINAL.

**THE MASTHEAD GRID** is a two-column band that opens the page and CLOSES ON
THE DOCKET ROW. Measured over all 19 parsed records the band is 3 rows and
the docket is the last of them — but the walk stops at the docket, not at a
count, because the row after it can sit only 13.3pt lower (becker_v._town_of
_freeport opens its rail one leading below the docket) and no whitespace
gap separates the two zones there.

Its right column names the court, and that is the DISPATCH. Counted over
all 19: SUPERIOR COURT 16, BUSINESS & CONSUMER COURT 1
(mystique_way_llc_v._twisted_river_holdings_llc), UNIFIED COURT 1
(state_of_maine_v._boyles), UNIFIED CRIMINAL COURT 1
(state_of_maine_v._erkson). The second row of that column is the division or
the seat — CIVIL ACTION 15, LOCATION: PORTLAND / LOCATION: Caribou /
AUGUSTA 3 — and it is read as `court` with the rest of the column rather
than sorted by its wording.

Its left column is 'STATE OF MAINE' over the county in the venue's own Latin
('OXFORD, ss.', 'CUMBERLAND, ss', 'SOMERSET, SS.'). 'ss.' is a closed
vocabulary of one and it is the landmark that says this is the masthead and
not a caption row.

**THE CAPTION BOX** runs from the docket row to the first row of the order,
and it is TWO COLUMNS: the parties and their statuses at the left, the name
of the paper at the right.

THE DIVIDER IS A COLUMN, NOT A GLYPH — because the glyph does not survive
the scan. 12 of the 19 records type a stacked ')' between the columns; the
OCR reads it as ')' on 10 of them and as 'e' / 'Ne' / 'e9' / 'e=' / 'Nowe'
on block_v._beal (12 of 17 rows 'e') and snow_v._corliss (9 of 9 'e'). So
the divider is found as GEOMETRY — four or more pieces no wider than 16pt
stacked within 3pt of one x, inside 60pt of the page axis, in one run with
no gap over 40pt — and the glyph the court types is a declared fact
(`_RAIL_GLYPH`) rather than a reading of the scan. What the scan actually
said is kept in the block's fingerprint, so the reproduction and the
measurement cannot disagree.

    railed (12)   albanasi, becker, block, chapdelaine, christian_hill,
                  cianchette, luongo, mystique, penquis, snow, boyles,
                  violette
    open   (7)    carrington, goddard, hogan, leahy, minerich, panella,
                  erkson

The 7 that draw nothing set the same two columns over a whitespace gutter,
and the columns split on the page's own 0.48 mark: over all 19 records no
left-column piece opens right of 0.36 of the measure and no right-column
piece opens left of 0.49 of it.

THE ORDER'S FIRST ROW ENDS THE BOX, and it is found two ways because the
court opens its papers two ways. FULL MEASURE — a row whose leading piece
starts within 55pt of the masthead's rail and ends within 35pt of the right
margin (16 of 19; the tolerance is 35 because leahy_v._mcanespie is a scan
of unjustified type whose body rows end anywhere from 499 to 541). Or
DISPLAY — a single piece over 40pt wide centred within 12pt of the page axis
('INTRODUCTION' on cianchette and hogan, 'OVERVIEW' on mystique). Both tests
read the LEADING piece only: christian_hill's caption row 'APPEALS BOARD OF
THE TOWN OF' + ') ORDER ON OUTSTANDING MOTIONS' spans the whole measure as a
ROW and would have ended the box eight rows early.

WHAT WAS WRONG BEFORE. Core's shared walk read this paper as a one-column
block and the damage ran both ways. albanasi_v._maker stopped the headmatter
mid-caption and gave the order 'v. ) ORDER ON', ') MOTIONS TO DISMISS',
'VEDA MAKER, et al., ) )' as its first three paragraphs. violette_v._violette
ran the other way and pulled twelve paragraphs of the order UP into the
headmatter (40 rows). panella_v._eastern_maine_medical_center did both at
once and listed 'as follows.' among its parties. christian_hill claimed 3
rows and no docket at all; hogan claimed the masthead and lost the caption.
Over the 19, `case_name` was empty on all 19 and `court` and `title` on all
19; `parties` was filled on 5 and carried the masthead inside it on 4 of
those ('STATE OF MAINE LINCOLN, ss. PATRICIA M. MINERICH, …').

WHAT THIS COURT DOES NOT PRINT ABOVE THE WRITING: a panel, a citation, a
date, a byline, an appearance roster. One justice signs at the FOOT, over
'Dated: October 21, 2024' and 'Justice, Maine Superior Court', and that band
is core's to read. So `roster_names()` has nothing to split here and this
file does not call it, `judges`/`panel` stay empty, and `single_writing` is
declared on the profile because a single justice's order cannot have two
writings — state_of_maine_v._erkson came back as two.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# ONE JUDGE, ONE WRITING. A state trial court's order is one justice ruling;
# there is nothing to concur in. state_of_maine_v._erkson came back as two
# orders broken mid-page, which is a split and not a reading.
MESUPERCT = CourtProfile(
    "mesuperct", "Maine Superior Court",
    single_writing=True,
)
# Installed over whatever the shared registry holds, so this file is the one
# place mesuperct is declared.
PROFILES[MESUPERCT.court_id] = MESUPERCT

STYLE_RAILED = "maine trial caption (parenthetical rail)"
STYLE_OPEN = "maine trial caption (open gutter)"

# ---- the masthead's landmarks --------------------------------------------
_STATE = re.compile(r"^STATE\s+OF\s+MAINE\s*,?\s*$", re.I)
# The venue in its own Latin. Five spellings of the separator over 19
# records — 'CUMBERLAND, ss.' / 'CUMBERLAND, ss' / 'SOMERSET, SS.' /
# 'KENNEBEG, ss.' (the scan's Kennebec) / 'OXFORD,ss.' with no space at all
# (albanasi_v._maker, which a regex demanding one refused outright and
# handed straight back to core).
_VENUE = re.compile(r"^[A-Z][A-Za-z\-]+\s*,?\s*(?:ss|SS)\s*\.?\s*$")
# Nine spellings over 19 records; the label is what is read, not the number.
# 'DOCKET NO gp OPP 08°' (hogan) is the scan's version of one and it is
# recorded as the page prints it — a court reader does not correct OCR.
_DOCKET = re.compile(r"^DOCKET\s+NOS?\b\.?\s*:?\s*(.*)$", re.I)

# ---- the caption's landmarks ---------------------------------------------
# The pivot, in the four forms the scans produce: 'v.' 'V.' 'Vv.' 'V,'.
_PIVOT = re.compile(r"^(?:v|vv|vs)\s*[.,]?\s*$", re.I)
# PARTY STATUS IS A CLOSED ROLE VOCABULARY (the one kind of caption wording
# it is legitimate to enumerate). A composite status is read by its parts,
# so 'Plaintiffs/Counterclaim Defendants' (snow_v._corliss) needs no entry
# of its own. 'patty-in-interest' is the scan's Party (christian_hill), and
# 'party-in' / 'interest' are the two halves carrington_mortgage_services
# prints on separate rows across a soft hyphen.
_STATUS = {
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "petitioner", "petitioners", "respondent", "respondents",
    "appellant", "appellants", "appellee", "appellees",
    "party-in-interest", "parties-in-interest", "patty-in-interest",
    "party-in", "parties-in", "interest",
    "movant", "movants", "intervenor", "intervenors",
    "counterclaim plaintiff", "counterclaim plaintiffs",
    "counterclaim defendant", "counterclaim defendants",
    "crossclaim plaintiff", "crossclaim defendant",
    "cross-claim plaintiff", "cross-claim defendant",
    "third-party plaintiff", "third-party defendant",
}
# A BARE 'and' is a joiner: it opens the next party group and belongs to
# neither. Inline 'and' inside a name ('and THE OFFICE OF MAINECARE') is not
# this row and is never tested.
_JOINER = {"and", "&"}

# ---- declared measures ---------------------------------------------------
# The divider the court types. Read off the 10 of 12 railed records whose
# scan preserved it; the two that did not still draw the column.
_RAIL_GLYPH = ")"
_RAIL_MAX_W = 16.0        # a divider piece is never wider than this
_RAIL_TOL = 3.0           # …and never further than this from its column
_RAIL_OFF_AXIS = 60.0     # the column stands this close to the page axis
_RAIL_FLOOR = 4           # fewer than four is not a column
_RAIL_GAP_MAX = 40.0      # one run: a bigger gap is a different thing
# Where the two columns part when the court draws nothing between them.
_GUTTER_FRACTION = 0.48
# The order's first row: how far it may indent from the masthead's rail…
_INDENT_MAX = 55.0
# …and how far short of the right margin it may still count as full measure.
_MEASURE_TOL = 35.0
# A display heading: this wide, and this close to the page axis.
_AXIS_TOL = 12.0
_DISPLAY_MIN_W = 40.0
# How far down page 1 the box may run before the claim is refused.
_BOX_ROWS_MAX = 40


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _key(text: str) -> str:
    """A caption row's comparison form: no soft hyphens, no trailing
    punctuation, folded case."""
    return _norm((text or "").replace("­", "")).strip(" .,;:").lower()


def _is_status(text: str) -> bool:
    parts = [p.strip() for p in _key(text).split("/")]
    return bool(parts) and all(p in _STATUS for p in parts if p)


def _inked(text: str) -> bool:
    """Does this piece carry a word at all? state_of_maine_v._erkson sets
    '. . ..•. . \xad' beside its defendant — ink the scan invented, and the
    only thing on the sheet that belongs in neither column."""
    return bool(re.search(r"[A-Za-z0-9]", text or ""))


# --------------------------------------------------------------------------
# rows and columns
# --------------------------------------------------------------------------

def _rows(pm, finder) -> list[list]:
    """Page 1's inked rows, furniture removed. Measured: the FurnitureFinder
    takes nothing from the top of any of the 19 parsed records — only the
    page-1 folios of leahy_v._mcanespie and panella_v._eastern_maine, both
    far below the block — so nothing has to be rescued from it here."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        if finder.kind(pm, line):
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _rail(pm, rows: list, below: float) -> dict | None:
    """The caption's divider COLUMN below ``below``, or None.

    Found by geometry, because the glyph does not survive a scan: narrow
    pieces stacked at one x near the page's axis, in a single run. The
    ``below`` bound keeps the masthead's own short right-column rows out of
    the seed, and the run bound keeps a page-1 folio at the same x out of it
    (leahy_v._mcanespie sets '1' at x0 307.7, one pt off where its sisters
    draw their rail)."""
    cand = [l for row in rows for l in row
            if l.top > below and l.plain.strip()
            and (l.x1 - l.x0) <= _RAIL_MAX_W
            and abs((l.x0 + l.x1) / 2 - pm.width / 2) <= _RAIL_OFF_AXIS]
    if len(cand) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(l.x0) for l in cand).most_common(1)[0]
    column = sorted((l for l in cand if abs(l.x0 - x) <= _RAIL_TOL),
                    key=lambda l: l.top)
    if len(column) < _RAIL_FLOOR:
        return None
    runs = [[column[0]]]
    for line in column[1:]:
        if line.top - runs[-1][-1].top <= _RAIL_GAP_MAX:
            runs[-1].append(line)
        else:
            runs.append([line])
    run = max(runs, key=len)
    if len(run) < _RAIL_FLOOR:
        return None
    read = Counter(_norm(l.plain) for l in run)
    return {"x": float(x), "top": run[0].top, "bottom": run[-1].top,
            "rows": len(run), "read": read.most_common(1)[0][0],
            "ids": {l.id for l in run}}


def _shed(line, rail_x: float):
    """``line`` without the divider glyph it opens with, or None when the
    line WAS the divider.

    christian_hill_properties sets ') ORDER ON OUTSTANDING MOTIONS' as one
    piece — the rail glued to the title, because pdfio's column gap was not
    wide enough to break it. Split CHAR BY CHAR at the rail's own window:
    whether the row arrived already broken is an accident of the gap."""
    lo, hi = rail_x - _RAIL_TOL - 1.0, rail_x + _RAIL_MAX_W
    kept = [c for c in line.chars
            if not (lo <= c["x0"] <= hi
                    and (c.get("text") or "").strip() in ("", _RAIL_GLYPH))]
    if len(kept) == len(line.chars):
        return line
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept, x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _split(row: list, rail: dict | None, gutter: float):
    """One source row as (left pieces, right pieces, rail pieces).

    Column membership is decided by which side of the divider a piece opens
    on — never by what the piece says."""
    left, right, bars = [], [], []
    for piece in row:
        if rail is not None and abs(piece.x0 - rail["x"]) <= _RAIL_TOL:
            if (piece.x1 - piece.x0) <= _RAIL_MAX_W:
                bars.append(piece)
                continue
            bare = _shed(piece, rail["x"])
            if bare is None:
                bars.append(piece)
                continue
            right.append(bare)
            continue
        (left if piece.x0 < gutter else right).append(piece)
    return left, right, bars


# --------------------------------------------------------------------------
# where the box ends
# --------------------------------------------------------------------------

def _opens_the_order(row: list, pm, lrail: float, right_x1: float) -> bool:
    """Is this row the first row of the order?

    Read off the LEADING piece alone. A caption row whose right column runs
    to the margin reaches the measure as a ROW, and tested that way
    christian_hill's box ended eight rows early."""
    lead = row[0]
    if lead.x0 <= lrail + _INDENT_MAX and lead.x1 >= right_x1 - _MEASURE_TOL:
        return True
    if len(row) == 1 and (lead.x1 - lead.x0) >= _DISPLAY_MIN_W \
            and abs((lead.x0 + lead.x1) / 2 - pm.width / 2) <= _AXIS_TOL:
        return True
    return False


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------

@decider("headmatter.read", court="mesuperct")
def read_headmatter_mesuperct(model, geom, **_):
    """Read Maine's trial-court caption, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    if not page1.lines:
        return NOTHING            # dewolfe_v._agro: a scan with no text layer
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _rows(page1, finder)
    if len(rows) < 5:
        return NOTHING

    gutter0 = page1.width * _GUTTER_FRACTION
    # THE MASTHEAD IS THE DISPATCH: the state at the rail, the court beside
    # it, the venue's 'ss.' under it, and the docket closing the band.
    head_left = [p for p in rows[0] if p.x0 < gutter0]
    head_right = [p for p in rows[0] if p.x0 >= gutter0]
    if not head_left or not head_right \
            or not _STATE.match(_norm(head_left[0].plain)):
        return NOTHING
    if not any(_VENUE.match(_norm(p.plain))
               for row in rows[1:4] for p in row if p.x0 < gutter0):
        return NOTHING
    mast_end = None
    for idx, row in enumerate(rows[:6]):
        if any(_DOCKET.match(_norm(p.plain)) for p in row):
            mast_end = idx
            break
    if mast_end is None:
        return NOTHING

    rail = _rail(page1, rows, rows[mast_end][0].top)
    gutter = rail["x"] if rail else gutter0
    lrail = min(p.x0 for p in head_left)
    right_x1 = geom.right_x1 if geom and geom.right_x1 \
        else page1.width - lrail

    ctx = _Ctx()

    # ---- the masthead grid ----------------------------------------------
    mast_left: list = []
    mast_right: list = []
    mast_ids: set[int] = set()
    for row in rows[:mast_end + 1]:
        left, right, bars = _split(row, None, gutter)
        mast_ids.update(p.id for p in row)
        mast_left.append(ctx.cell(left, "court"))
        role = "docket"
        for piece in right:
            if not _DOCKET.match(_norm(piece.plain)):
                role = "court"
                break
        mast_right.append(ctx.cell(right, role))
        if role == "docket" and right:
            got = _DOCKET.match(_norm(right[0].plain))
            value = _norm(got.group(1)) if got else ""
            ctx.crit.setdefault("docket_number",
                                value or _norm(right[0].plain))
    # The court naming itself, as printed.
    ctx.crit.setdefault("court", _norm(head_right[0].plain))
    ctx.items.append(m.CaptionBlock(
        left=mast_left, right=mast_right, rail=None,
        rail_rows=len(mast_left), style_id="masthead-grid",
        fp={"rows": len(mast_left), "gutter_x": round(gutter, 1)},
        prov=m.Prov(page1.number, tuple(sorted(mast_ids)))))
    ctx.consumed.update(mast_ids)

    # ---- the caption box -------------------------------------------------
    cap_left: list = []
    cap_right: list = []
    cap_ids: set[int] = set()
    groups: list[list[str]] = [[]]
    pivot_at: int | None = None
    title: list[str] = []
    ended = False
    for row in rows[mast_end + 1:mast_end + 1 + _BOX_ROWS_MAX]:
        if _opens_the_order(row, page1, lrail, right_x1):
            ended = True
            break
        left, right, bars = _split(row, rail, gutter)
        cap_ids.update(p.id for p in row)
        # Ink the scan invented belongs in neither column.
        noise = [p for p in (left + right) if not _inked(p.plain)]
        for piece in noise:
            ctx.dropped.append(m.Dropped(
                text=_norm(piece.plain), prov=m.Prov(page1.number,
                                                     (piece.id,)),
                kind="margin"))
        left = [p for p in left if _inked(p.plain)]
        right = [p for p in right if _inked(p.plain)]
        # THE PARTIES ARE READ PIECE BY PIECE, not row by row:
        # chapdelaine_v._48_cedar_beach_road_ii_llc sets 'v.' and
        # 'Plaintiff,' on one baseline, and joined they are neither.
        for piece in left:
            text = _norm(piece.plain)
            if _PIVOT.match(text):
                if pivot_at is None:
                    pivot_at = len(groups)
                groups.append([])
            elif _is_status(text) or _key(text) in _JOINER:
                groups.append([])
            else:
                groups[-1].append(text)
        for piece in right:
            title.append(_norm(piece.plain))
        cap_left.append(ctx.cell(left, "caption"))
        cap_right.append(ctx.cell(right, "title"))
    if not ended:
        # The order never opened: the walk would be claiming the sheet.
        return NOTHING

    # The rail runs a few rows past the last words at each end; trim the
    # empty pairs there and keep the interior ones, which are the page's own
    # vertical rhythm.
    while cap_left and not cap_left[0].text and not cap_right[0].text:
        cap_left.pop(0)
        cap_right.pop(0)
    while cap_left and not cap_left[-1].text and not cap_right[-1].text:
        cap_left.pop()
        cap_right.pop()
    if not cap_left:
        return NOTHING
    # THE DIVIDER THE SCAN DESTROYED IS STILL RECORDED. Where the column's
    # own reading is not the glyph the court types, the rail is reproduced
    # from the declared fact and what the OCR actually said is recorded as
    # removed — block_v._beal ('e' x12, 'Ne' x2, 'e9', 'e=', 'Nowe') and
    # snow_v._corliss ('e' x9). Reproduced as read it would print 'e' down
    # the middle of the caption; dropped silently, five word types would
    # leave the record with nothing to say where they went.
    if rail and rail["read"] != _RAIL_GLYPH:
        # Only the bars this claim actually took: a rail piece the box did
        # not reach is still core's, and recorded here it would be reported
        # twice.
        _bars = [l for row in rows for l in row
                 if l.id in rail["ids"] and l.id in cap_ids]
        if _bars:
            ctx.dropped.append(m.Dropped(
                text=" ".join(_norm(l.plain) for l in _bars),
                prov=m.Prov(page1.number, tuple(sorted(l.id for l in _bars))),
                kind="rail"))
    ctx.items.append(m.CaptionBlock(
        left=cap_left, right=cap_right,
        rail=(_RAIL_GLYPH if rail else None), rail_rows=len(cap_left),
        style_id="parenthetical-rail" if rail else "open-gutter",
        fp={"rail": _RAIL_GLYPH if rail else None,
            "rail_read": rail["read"] if rail else None,
            "rail_rows": rail["rows"] if rail else 0,
            "mid_x": round(gutter, 1)},
        prov=m.Prov(page1.number, tuple(sorted(cap_ids)))))
    ctx.consumed.update(cap_ids)

    # THE PARSED FORM IS NOT THE PRINTED FORM. A pleading caption ends every
    # party with the comma that introduces its status row; `caption` keeps
    # the rows verbatim and these are the names, so the comma goes.
    named = [" ".join(g).rstrip(" ,;") for g in groups if g]
    named = [n for n in named if n]
    if named:
        ctx.crit.setdefault("parties", named)
    if pivot_at is not None:
        before = [" ".join(g) for g in groups[:pivot_at] if g]
        after = [" ".join(g) for g in groups[pivot_at:] if g]
        if before and after:
            ctx.crit.setdefault("case_name",
                                f"{before[0]} v. {after[0]}")
    caption_rows = [r.text for r in cap_left if r.text]
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows)
    if title:
        ctx.crit.setdefault("title", " ".join(title))
    ctx.crit["headmatter_style"] = STYLE_RAILED if rail else STYLE_OPEN
    return ctx.result()


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def cell(self, pieces: list, role: str) -> m.HmLine:
        """One column's share of one source row — built, not emitted: it goes
        into a CaptionBlock. An EMPTY cell is still a row: it holds the two
        columns level, and it carries the column's role so no row of a
        claimed block goes untinted."""
        parts = sorted(pieces, key=lambda l: l.x0)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0] if parts else None
        return m.HmLine(
            text=text,
            prov=m.Prov(first.page if first else 1,
                        tuple(p.id for p in parts)),
            align=m.Align.LEFT,
            x0=first.x0 if first else 0.0,
            size=(first.size or 0.0) if first else 0.0,
            bold=bool(parts) and all(bool(p.all_bold) for p in parts),
            role=role)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
