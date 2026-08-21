"""Supreme Court of Pennsylvania ('pa') — the COLON-RAIL caption.

Everything unique to pa lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — pa sets a two-column caption box under a centred masthead and
rules the middle with a COLON on every row. This is the repo's reference for
the colon-rail family, so the rail does all of the column work here and
nothing is inferred from wording (ca6 is the standard being reproduced;
del.py is the same shape drawn with '§').

    ┌──────────────────────────────────────────────────────────────────────┐
    │                        [J-80-2025]                the session stamp  │
    │            IN THE SUPREME COURT OF PENNSYLVANIA   the masthead       │
    │                     WESTERN DISTRICT              the district       │
    │ TODD, C.J., DONOHUE, DOUGHERTY, WECHT, MUNDY, …   the roster         │
    │                                                                      │
    │ CLEARFIELD COUNTY, PENNSYLVANIA, : No. 10 WAP 2025      <- ONE line  │
    │                                 :                                    │
    │        Appellant                : Appeal from the Order of the       │
    │                                 : Commonwealth Court entered         │
    │                                 : November 1, 2024, at No. 193 CD    │
    │        v.                       : 2024, affirming the Order of the   │
    │ TRANSYSTEMS CORPORATION,        : February 15, 2024, at No. 2023-31- │
    │ SUCCESSOR TO L. ROBERT KIMBALL  : CD.                                │
    │ AND ASSOCIATES, INC., …         :                                    │
    │ FIORE, INC., AND SHOWALTER      : ARGUED: October 7, 2025            │
    │ MASONRY, INC.,                  :                                    │
    │        Appellees                :                                    │
    │                                                                      │
    │                         OPINION                   the title, UNDERLINED
    │ JUSTICE MUNDY            DECIDED: APRIL 30, 2026  the byline + date  │
    └──────────────────────────────────────────────────────────────────────┘

MEASURED FACTS (50 records in assets/pa, page 1 of each, 612pt measure):

- The masthead reads 'IN THE SUPREME COURT OF PENNSYLVANIA' on all 49
  records that carry text, at x0=173.3. It is FOUND, never indexed: 35
  records print the argument-session stamp ('[J-80-2025]',
  '[J-72A-2025 and J-72B-2025]', '[J-48-2025] [MO: Todd, C.J.]') ABOVE it
  and 14 print nothing there.
- The district row is one of EASTERN / MIDDLE / WESTERN DISTRICT.
- The bench roster prints in exactly one form over the corpus — 'TODD, C.J.,
  DONOHUE, DOUGHERTY, WECHT, MUNDY, BROBSON, McCAFFERY, JJ.' — at x0=62.6,
  LEFT of the 72.0 body rail, on 15 records (the majority writing of an
  argued case; a concurrence or dissent in the same case omits it).
- THE RAIL IS A COLUMN OF ':' GLYPHS at one x. That x is not a constant: it
  runs 323.4–340.9 across records (the court re-tabs the box per document),
  so it is measured per record as the modal x0 of the ':' glyphs on page 1.
  The modal column holds 7–32 glyphs on the 48 records that draw it.
- The title names the paper itself: OPINION (15), ORDER (17), CONCURRING
  OPINION (7), DISSENTING OPINION (6), CONCURRING AND DISSENTING OPINION
  (3), CONCURRING STATEMENT (1) — 49 of 49, always centred, always directly
  under the box.
- The drawn rule beneath the title is an UNDERLINE, not a fence: measured on
  clearfield it runs x0=280.7–331.4 against the title's own 280.7–331.5. It
  is not re-emitted as a Rule.
- The byline is 'JUSTICE <NAME>' (31), 'CHIEF JUSTICE TODD' (1) or 'PER
  CURIAM' (17), and where the court prints a decision date it shares that
  row, flush right at the measure ('DECIDED: APRIL 30, 2026', x1≈537).

THREE TRAPS THIS PAPER SETS, all of them found in the geometry:

1. THE RAIL IS NOT ALWAYS ITS OWN PIECE. pdfio returns ': No. 84 MAP 2024'
   as one line beginning at the rail, and on 12 records it returns the whole
   right cell GLUED to the left one — 'CLEARFIELD COUNTY, PENNSYLVANIA, :
   No. 10 WAP 2025' is a single line at x0=77.4 (the other eleven are the
   four downingtown records, two honey, two dravo, bird, buchtan and lee;
   1–4 such rows each). A whole-line side test puts
   the docket in the party column and loses it, so the row is split GLYPH BY
   GLYPH at the rail's x, the rail's own glyphs shed first.
2. A LEFT ROW AND THE GLYPH BESIDE IT DO NOT ALWAYS SHARE A TOP, and the
   left column can outrun the rail: `in_re_nom._of_lee_appeal_of_parker`
   prints 'OBJECTION OF: WILLIAM PARKER' at top=256.5 with the rail's last
   glyph at 242.7, and `in_re_nom._of_morris` prints 'SUBMITTED: April 11,
   2026' in the right column with NO glyph on its row. So the box is not
   bounded by the rail's own last row — it is the BAND between the rail's
   first row and the TITLE, which is the next landmark the paper prints.
3. A ':' IS ORDINARY PUNCTUATION IN THIS CAPTION. 'TAX PARCEL NO.: 33-5-
   43.3', 'APPEAL OF: CARMEUSE LIME, INC.', 'IN RE: DRAVO LLC' all print
   one in the LEFT column. Only glyphs in the rail's own column (±3pt of the
   modal x) are rail, which is ca6's test, not a character test.

THE SECOND DIVIDER: A WHITESPACE GUTTER. One record of the 50 —
`koger_t._aplt._v._pa_housing_finance_agency`, a pro-se order — sets the same
two columns with no rail at all (its modal ':' column holds one glyph). The
geometry is still there and is still measured, the same way the rail is: as a
COLUMN. The right cells' left edges stack at 350.2/350.6/350.6/351.1, the
left column's ink ends by x1=321.1, and NOTHING stands in the 29.1pt between
them, so the divider is that band's midpoint (335.6). See `_gutter`.

The gutter path is a FALLBACK, tried only where the rail is absent, and it
claims nothing on trust: the same glyph-by-glyph split runs on it, and the
read is accepted only if it puts the court's own docket form in the right
column. On koger that is the ONE glued row again — 'ELLIOT-TODD PARKER KOGER
AND TODD No. 29 WAP 2025' comes back as a single line spanning 78.5–445.9
because pdfio saw no break, but its own chars leave a 21.5pt hole at
329.6–351.1, so the divider falls inside that hole and the row tears where
the court set it. Nothing is torn by x0, and no wording is consulted.

Corpus split over the 50 records: 48 colon-rail, 1 whitespace-gutter, 1
NOTHING — `in_re_nom._of_griffith_apl._of_peake_1`, which is scanned and
carries no text layer at all.

WHAT THE RIGHT COLUMN CARRIES, measured over the 48 railed records, is three
things and nothing else: the court's own docket as a complete row ('No. 10
WAP 2025' — number, a two-to-four-letter district code, year), the argument
or submission date ('ARGUED:' / 'SUBMITTED:'), and the appeal-from recital
that runs over as many rows as it needs. A right-hand row that is none of
the first two is a row of that recital, which is why `lower-court` is what
the column reads as by default — it is a measurement of this paper, not a
catch-all.

THE BYLINE IS LEFT TO CORE. The reader claims the 'DECIDED:' piece of the
byline row (its own line, right of the axis) and stops without claiming the
byline itself, so the writing still opens where the court signs it. This
holds on both contracts: koger prints 'PER CURIAM' at x0=73.0 and 'DECIDED:
APRIL 30, 2026' at x0=384.5 on one row, and reads as author 'PER CURIAM' with
the date in the headmatter.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(r"^IN THE SUPREME COURT OF PENNSYLVANIA$", re.I)
_DISTRICT = re.compile(r"^(?:EASTERN|MIDDLE|WESTERN)\s+DISTRICT$", re.I)
# '[J-80-2025]', '[J-72A-2025 and J-72B-2025]', '[J-48-2025] [MO: Todd, C.J.]'
# — the court's argument-session designation, and on a separate writing the
# author of the majority. It is the same string the folio repeats at the foot
# of every page ('[J-48-2025] - 2'), so it is the court's own file mark:
# caption apparatus, which is what `case-info` names.
_SESSION = re.compile(r"^\[J-[^\]]+\](?:\s*\[[^\]]+\])?$")
_RAIL_GLYPH = ":"
# ca6's rail window: a glyph belongs to the rail when it stands in the rail's
# own COLUMN, never because of what character it is.
_RAIL_WINDOW = 3.0
# The modal ':' column must be a COLUMN, not an accident of punctuation. The
# 48 railed records hold 7–32 glyphs in theirs; koger's whitespace-gutter
# caption holds 1.
_RAIL_FLOOR = 4
_AXIS_TOL = 14.0

# THE WHITESPACE GUTTER — the fallback divider, for the record that sets the
# same two columns with no rail at all. It is measured the SAME way as the
# rail: as a COLUMN. The right cells' own left EDGES stack at one x
# (koger: 350.2, 350.6, 350.6, 351.1), so the stack is gathered in a window
# and the gutter is the empty band between the left column's furthest ink and
# that edge (321.1 → 350.2 on koger: 29.1pt).
_EDGE_WINDOW = 3.0
# Three cells make a column; two are a coincidence. koger's right column
# prints four rows (the docket and a three-row origin recital).
_EDGE_FLOOR = 3
# A gutter narrower than an em of body type is word spacing, not a divider.
_GUTTER_MIN = 12.0

# THE TITLE — what the paper calls ITSELF, a closed vocabulary of the six
# forms measured over the corpus plus the two-word variants the court builds
# from the same words ('OPINION IN SUPPORT OF AFFIRMANCE' is pa's own name
# for an evenly-divided writing).
_TITLE = re.compile(
    r"^(?:(?:CONCURRING|DISSENTING|PLURALITY|MAJORITY|SUPPLEMENTAL)"
    r"(?:\s+AND\s+(?:CONCURRING|DISSENTING))?\s+)?"
    r"(?:OPINION|STATEMENT|ORDER)"
    r"(?:\s+IN\s+SUPPORT\s+OF\s+(?:AFFIRMANCE|REVERSAL))?"
    r"(?:\s+ANNOUNCING\s+THE\s+JUDGMENT\s+OF\s+THE\s+COURT)?$")
# 'JUSTICE MUNDY' / 'CHIEF JUSTICE TODD' / 'PER CURIAM'. The court's
# BylineGrammar in courts/__init__.py is the same fact declared for core.
_BYLINE = re.compile(
    r"^(?:(?:CHIEF\s+)?JUSTICE\s+[A-Z][A-Za-z'’\-]+"
    r"|PER\s+CURIAM)\s*:?\.?$")
_DECIDED = re.compile(r"^DECIDED:\s*(.+?)\s*$", re.I)
# The bench roster: a run of surnames closed by a BENCH WORD. The suffixes
# are a finite vocabulary; the names are never read by wording.
_ROSTER = re.compile(r"(?:,\s*(?:C\.J\.|JJ?\.))\s*$")
_BENCH_WORD = re.compile(r"^(?:C\.J\.|J\.|JJ\.|P\.J\.|P\.J\.E\.)$")

# The right column's three tenants.
# The court's own docket, as a COMPLETE row: a number, a district code
# (EAP/MAP/WAP for appeals, EAL/MAL/WAL for allocatur petitions — all six
# occur), and a year. 'No. GD-20-010198, and remanding.' and 'No. CP-51-MD-'
# are rows of the appeal-from recital and do not match.
_DOCKET = re.compile(r"^Nos?\.\s*(\d+\s+[A-Z]{2,4}\s+\d{4})\.?$")
_DATE_LABEL = re.compile(
    r"^(ARGUED|SUBMITTED|REARGUED|RESUBMITTED|REVISED):\s*(.+)$", re.I)
_DATE_CRIT = {"argued": "submitted", "reargued": "submitted",
              "submitted": "submitted", "resubmitted": "submitted",
              "revised": "submitted"}
# The courts pa hears from, as a closed list. The origin recital names the
# tribunal appealed from in its first clause.
_BELOW = re.compile(
    r"\b(Commonwealth Court|Superior Court|Court of Common Pleas"
    r"|Court of Judicial Discipline|Disciplinary Board)\b")
# Numbers the court below gave the case, in the two forms this paper prints:
# an appellate docket ('193 CD 2024', '520 MDA 2022') and a trial-court
# number ('CP-67-CR-0007632-2018', 'GD-20-010198', 'CV-22-00115-OR').
_BELOW_NO = re.compile(
    r"\bNos?\.\s*(\d+\s+[A-Z]{2,4}\s+\d{4}"
    r"|[A-Z]{2}-\d[\w-]*\w"
    r"|\d{4}-\d+-[A-Z]{2,3})")

# The left column's furniture: party STATUS and the pivot are closed
# vocabularies; a party NAME is never read by wording.
_STATUS = re.compile(
    r"^(?:Appellants?|Appellees?|Petitioners?|Respondents?|Intervenors?"
    r"|Cross-Appellants?|Cross-Appellees?|Amic(?:us|i)(?:\s+Curiae)?"
    r"|Plaintiffs?|Defendants?)\b[.,]?$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# 'APPEAL OF: CARMEUSE LIME, INC.' / 'OBJECTION OF: WILLIAM PARKER' /
# 'TAX PARCEL NO.: 33-5-43.3' — caption apparatus, not a party name, so it
# is kept out of `parties` and `case_name` while still reading as caption.
_DESIGNATION = re.compile(
    r"^(?:APPEAL OF|OBJECTION OF|APPEAL FROM|TAX PARCEL NO)\b", re.I)


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="pa")
def read_headmatter_pa(model, geom, **_):
    """Read Pennsylvania's colon-rail box, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 4:
        return NOTHING
    # THE MASTHEAD IS FOUND, NOT INDEXED — the session stamp stands above it
    # on 35 records and nothing does on 14.
    mast = next((i for i, g in enumerate(rows[:4])
                 if _MASTHEAD.match(_norm(" ".join(l.plain for l in g)))),
                None)
    if mast is None:
        return NOTHING

    # THE HEADER BLOCK, by its own landmarks: the masthead, the district row
    # under it, and the roster where the case was argued. What follows is the
    # box, and finding it this way is what lets the gutter path bound the box
    # without a rail to anchor on.
    head_end = mast + 1
    while head_end < len(rows):
        _t = _norm(" ".join(l.plain for l in rows[head_end]))
        if _DISTRICT.match(_t) or _ROSTER.search(_t):
            head_end += 1
            continue
        break

    rail_x = _rail(page1)
    if rail_x is not None:
        # THE BAND IS THE BOX. It opens on the rail's first row and closes at
        # the TITLE, the next thing the paper prints — never at the rail's own
        # last glyph, which the left column outruns (trap 2 above).
        box_top = min((l.top for g in rows for l in g
                       if _rail_chars(l, rail_x)), default=None)
        style_id = "colon-rail"
    else:
        # NO RAIL: the box opens directly under the header block, and the
        # divider is measured from the band's own ink (see `_gutter`).
        box_top = rows[head_end][0].top if head_end < len(rows) else None
        style_id = "whitespace-gutter"
    if box_top is None:
        return NOTHING
    title_at = next((i for i, g in enumerate(rows)
                     if g[0].top > box_top
                     and _TITLE.match(_norm(" ".join(l.plain for l in g)))),
                    None)
    if title_at is None:
        return NOTHING              # nothing closes the box: not this paper
    box_bottom = rows[title_at][0].top
    # THE BYLINE ROW FOLLOWS THE TITLE, WHEREVER THE PAGE BREAK FALLS. On
    # `oag_v._gillece_appeal_of_gillece` (both records) the caption box runs
    # to top=605 and the title is the last row of page 1, so the court signs
    # at the top of page 2. The row is reached from the LANDMARK, not from a
    # page number: it is whatever follows the title.
    if title_at == len(rows) - 1 and len(model.pages) > 1:
        _over = _rows(model.pages[1], finder)
        if _over:
            rows = rows + [_over[0]]

    # THE DIVIDER. With a rail it is the rail's own x; without one it is the
    # midpoint of the measured gutter, and the same glyph-by-glyph split then
    # tears the glued row in the right place — no x0 test, no wording.
    gutter = None
    if rail_x is None:
        band = [l for g in rows for l in g
                if l.page == page1.number
                and box_top <= l.top < box_bottom and l.plain.strip()]
        gutter = _gutter(band, page1.width)
        if gutter is None:
            return NOTHING          # no divider of either kind: not this paper
        mid = gutter[2]
    else:
        mid = rail_x

    ctx = _Ctx()
    box_at: int | None = None       # where the box belongs among the items
    left: list = []
    right: list = []
    left_plain: list[str] = []
    right_plain: list[str] = []
    box_ids: set[int] = set()
    stop = False
    for idx, group in enumerate(rows):
        if stop:
            break
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        _x1 = max(l.x1 for l in pieces)
        centred = abs((first.x0 + _x1) / 2 - page1.width / 2) <= _AXIS_TOL

        # --- above the masthead: the session stamp, and only that ---------
        if idx < mast:
            if _SESSION.match(text):
                ctx.emit(pieces, "case-info")
            continue
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DISTRICT.match(text):
            # The court naming its own division — `court` covers the name,
            # the division and the seat.
            ctx.emit(pieces, "court")
            continue

        # --- the box ------------------------------------------------------
        # `first.page` guards the band: a row carried over from page 2 has a
        # page-relative top that falls inside page 1's box band.
        if first.page == page1.number and box_top <= first.top < box_bottom:
            if box_at is None:
                box_at = len(ctx.items)
            l_cells, r_cells = [], []
            for line in pieces:
                shed = line if rail_x is None else _shed_rail(line, rail_x)
                if shed is None:
                    continue        # the line WAS the rail
                for side, bucket in ((_side(shed, mid, "L"), l_cells),
                                     (_side(shed, mid, "R"), r_cells)):
                    if side is not None:
                        bucket.append(side)
            left.append(_cell(l_cells, "caption", page1))
            right.append(_cell(r_cells, _right_role(r_cells), page1))
            left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
            box_ids.update(l.id for l in pieces)
            continue

        # --- the roster, between the district and the box -----------------
        if first.page == page1.number and first.top < box_top \
                and _ROSTER.search(text):
            ctx.crit.setdefault("panel_line", text)
            _panel = _panel_names(text)
            if _panel:
                ctx.crit.setdefault("panel", _panel)
            ctx.emit(pieces, "panel", centre=False)
            continue

        # --- the title, and then the paper --------------------------------
        if idx == title_at:
            ctx.crit.setdefault("title", text)
            ctx.emit(pieces, "title", centre=centred)
            continue
        if any(_BYLINE.match(_norm(p.plain)) for p in pieces):
            # THE BYLINE STAYS WITH THE WRITING. Only the date beside it is
            # the headmatter's, and it is its own line on the page.
            for part in pieces:
                dated = _DECIDED.match(_norm(part.plain))
                if dated:
                    ctx.crit.setdefault("decision_date", _norm(dated.group(1)))
                    ctx.emit([part], "date", centre=False, right=True)
            stop = True
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    if not left:
        return NOTHING
    # The rail runs a few rows past the last words; ca6 and del trim the
    # empty tail pairs and so does this.
    while left and not _text_of(left[-1]) and not _text_of(right[-1]):
        left.pop()
        right.pop()
        left_plain.pop()
        right_plain.pop()
    if not left:
        return NOTHING
    fp = {"rail": _RAIL_GLYPH if rail_x is not None else None,
          "mid_x": round(mid, 1)}
    if gutter is not None:
        fp["gutter"] = [round(gutter[0], 1), round(gutter[1], 1)]
    block = m.CaptionBlock(
        left=left, right=right,
        rail=_RAIL_GLYPH if rail_x is not None else None,
        rail_rows=len(left), style_id=style_id, fp=fp,
        prov=m.Prov(page1.number, tuple(sorted(box_ids))))
    ctx.items.insert(box_at if box_at is not None else len(ctx.items), block)
    ctx.consumed.update(box_ids)

    # --- what the box said, in the model's own field names -----------------
    dockets = [mm.group(1) for mm in
               (_DOCKET.match(t) for t in right_plain) if mm]
    if not dockets:
        return NOTHING              # no docket: the box was not read
    ctx.crit["docket_number"] = dockets[0]
    if dockets[1:]:
        ctx.crit["other_dockets"] = dockets[1:]
    for text in right_plain:
        dated = _DATE_LABEL.match(text)
        if dated:
            key = _DATE_CRIT.get(dated.group(1).lower())
            if key:
                ctx.crit.setdefault(key, _norm(dated.group(2)))
    origin = [t for t in right_plain
              if t and not _DOCKET.match(t) and not _DATE_LABEL.match(t)]
    if origin:
        hist = _join_origin(origin)
        ctx.crit.setdefault("history", hist[:2000])
        below = _BELOW.search(hist)
        if below:
            ctx.crit.setdefault("lower_court", below.group(1))
        _nos = list(dict.fromkeys(mm.group(1) for mm in
                                  _BELOW_NO.finditer(hist)))
        if _nos:
            ctx.crit.setdefault("lower_court_docket", _nos)

    # THE PRINTED FORM BESIDE THE PARSED FORM: the caption rows verbatim, the
    # party groups, and the case name built from the names either side of the
    # pivot — joining the rows wholesale yields 'CLEARFIELD COUNTY,
    # PENNSYLVANIA, Appellant v. TRANSYSTEMS …'. Only the FIRST docket
    # segment feeds the name: a consolidated caption (downingtown, dravo,
    # smith) prints the same two parties twice, once per docket.
    caption_rows = [t for t in left_plain if t]
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows)
    groups = _party_groups(left_plain, right_plain)
    if groups:
        ctx.crit.setdefault("parties", groups[:8])
        ctx.crit.setdefault("case_name", " v. ".join(groups))
    ctx.crit["headmatter_style"] = style_id
    return ctx.result()


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _rail(pm) -> float | None:
    """The x of the caption's drawn divider on ``pm``, or None.

    A rail is a COLUMN: ':' glyphs stacked at one x, not a count of colons
    anywhere on the page. The x is measured per record because the court
    re-tabs the box per document (323.4–340.9 over the corpus)."""
    cols = Counter(round(c["x0"], 1) for l in pm.lines for c in l.chars
                   if (c.get("text") or "") == _RAIL_GLYPH)
    if not cols:
        return None
    x, _n = cols.most_common(1)[0]
    stack = sum(n for k, n in cols.items() if abs(k - x) <= _RAIL_WINDOW)
    if stack < _RAIL_FLOOR:
        return None
    return float(x)


def _gutter(lines: list, width: float):
    """The caption's WHITESPACE divider as (lo, hi, mid), or None.

    Measured from the band's own ink, never from a fixed fraction of the
    measure, and by the same reasoning as the rail: a divider is a COLUMN.
    The right cells' left edges stack at one x; the gutter is the empty band
    between the left column's furthest ink and that edge; and every line in
    the band must respect it — end before it, begin at or after it, or CROSS
    IT WHOLE, which is the row pdfio could not split.

    Measured on `koger_t._aplt._v._pa_housing_finance_agency`, the one record
    of the 50 that draws no rail: right edges 350.2/350.6/350.6/351.1, left
    ink ending by x1=321.1, nothing at all inside the 29.1pt between them,
    and one crossing row ('ELLIOT-TODD PARKER KOGER AND TODD No. 29 WAP
    2025', 78.5–445.9, whose own chars leave a 21.5pt hole at 329.6–351.1).
    """
    axis = width / 2
    starts = Counter(round(l.x0, 1) for l in lines if l.x0 > axis)
    if not starts:
        return None
    x, _n = starts.most_common(1)[0]
    stack = [l for l in lines if abs(l.x0 - x) <= _EDGE_WINDOW]
    if len(stack) < _EDGE_FLOOR:
        return None
    hi = min(l.x0 for l in stack)
    inside = [l for l in lines if l.x1 <= hi]
    if not inside:
        return None
    lo = max(l.x1 for l in inside)
    if hi - lo < _GUTTER_MIN:
        return None
    for line in lines:
        if line.x1 <= lo or line.x0 >= hi:
            continue                # respects the gutter
        if line.x0 < lo and line.x1 > hi:
            continue                # crosses it whole: a glued row
        return None                 # ink INSIDE the gutter: no gutter
    return lo, hi, (lo + hi) / 2


def _rail_chars(line, rail_x: float) -> list:
    """The chars of ``line`` that stand in the rail's own column."""
    return [c for c in line.chars
            if (c.get("text") or "") == _RAIL_GLYPH
            and abs(c["x0"] - rail_x) <= _RAIL_WINDOW]


def _shed_rail(line, rail_x: float):
    """``line`` with the rail's glyphs removed, or None when the line WAS
    the rail. The glyph is identified by its COLUMN, never by its character:
    'TAX PARCEL NO.: 33-5-43.3' and 'IN RE: DRAVO LLC' print a colon in the
    left column and keep it."""
    rails = {id(c) for c in _rail_chars(line, rail_x)}
    if not rails:
        return line
    kept = [c for c in line.chars if id(c) not in rails]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    x0 = min(c["x0"] for c in kept)
    x1 = max(c.get("x1", c["x0"]) for c in kept)
    return _replace(line, chars=kept, x0=x0, x1=x1)


def _side(line, mid: float, want: str):
    """The part of ``line`` on one side of the rail, or None. The split is
    GLYPH BY GLYPH: whether pdfio broke a row at its column gap is an
    accident of how wide the gap happened to be, and a whole-line test put
    'CLEARFIELD COUNTY, PENNSYLVANIA, : No. 10 WAP 2025' — one line — wholly
    in the party column, losing the docket."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


def _right_role(cells: list) -> str:
    """What the right column is saying on this row. Each tenant by its own
    landmark; a runover line keeps company with `lower-court`, which is what
    the column carries whenever it is neither the docket nor a date (see the
    docstring — measured, not assumed)."""
    text = _norm(" ".join(c.plain for c in cells))
    if not text:
        return "caption"
    if _DOCKET.match(text):
        return "docket"
    if _DATE_LABEL.match(text):
        return "date"
    return "lower-court"


# --------------------------------------------------------------------------
# what the box said
# --------------------------------------------------------------------------

def _panel_names(text: str) -> list[str]:
    """The roster's surnames. The BENCH WORDS are a closed vocabulary; the
    names are whatever stands between them ('McCAFFERY' is one person, and
    'JJ.' is nobody)."""
    out = []
    for token in text.split(","):
        token = token.strip().rstrip(".")
        if not token or _BENCH_WORD.match(token + "."):
            continue
        if _BENCH_WORD.match(token):
            continue
        out.append(token)
    return out


def _party_groups(left_plain: list[str], right_plain: list[str]) -> list[str]:
    """The party names of the FIRST docket segment, in printed order, one
    entry per side of the pivot. Statuses, the pivot and the caption's own
    apparatus ('APPEAL OF:', 'TAX PARCEL NO.:') are dropped; a party name
    that wraps over rows is rejoined."""
    end = next((i for i in range(1, len(right_plain))
                if _DOCKET.match(right_plain[i])), len(right_plain))
    groups: list[list[str]] = [[]]
    for text in left_plain[:end]:
        if not text:
            continue
        if _PIVOT.match(text):
            groups.append([])
            continue
        if _DESIGNATION.match(text):
            # THE DESIGNATION CLOSES THE PARTY LIST of its segment. It is the
            # last thing the left column prints in every record measured
            # (smith, dravo, downingtown, gillece, honey, lee), and its own
            # WRAP rows are not party names — read as such they appended
            # 'SCHOOL DISTRICT' to Chester County's name.
            break
        if _STATUS.match(text):
            continue
        groups[-1].append(text)
    # The trailing comma is stripped from the JOINED name, never row by row:
    # 'TRANSYSTEMS CORPORATION,' / 'SUCCESSOR TO L. ROBERT KIMBALL' is one
    # party whose first row ends in a comma the printed name keeps.
    out = [_norm(" ".join(g)).rstrip(",") for g in groups if g]
    return [t for t in out if t]


def _join_origin(rows: list[str]) -> str:
    """The appeal-from recital as one string. A row that ENDS ON A HYPHEN is
    a docket broken across rows, never a word: the court prints 'at No. CP-
    51-MD-' / '0001772-2022' and 'No. 2019-' / '11728-AB', and joining those
    with a space reported the number below as 'CP-51-MD' — a truncation that
    reads like a fact. Nothing else in the recital ends a row on a hyphen."""
    out = ""
    for text in rows:
        if not out:
            out = text
        elif out.endswith("-"):
            out += text
        else:
            out += " " + text
    return out


def _tidy(markup: str) -> str:
    """Leading whitespace off a standalone row, INCLUDING whitespace inside
    the opening tag. The court sets 'DECIDED:' on a tab and pdfio keeps the
    real space glyphs, so the markup arrives as '<strong>   DECIDED:  April
    30, 2026</strong>'; the render preserves it (`white-space: pre-wrap`) and
    it fights the row's own alignment, which is what carries the position.
    The caption CELLS keep their spacing — there the gap after the rail is
    the page's own column gutter."""
    return re.sub(r"^(\s*(?:<[a-z]+>\s*)*)",
                  lambda mm: re.sub(r"\s+", "", mm.group(1)), markup)


def _text_of(row) -> str:
    return re.sub(r"<[^>]+>", "", getattr(row, "text", "") or "").strip()


def _cell(cells: list, role: str, pm):
    cells = sorted(cells, key=lambda l: l.x0)
    if not cells:
        return m.HmLine(text="", prov=m.Prov(pm.number), align=m.Align.LEFT,
                        role=role)
    text = ""
    for part in cells:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
            else piece
    return m.HmLine(
        text=text, prov=m.Prov(cells[0].page, tuple(c.id for c in cells)),
        align=m.Align.LEFT, x0=cells[0].x0, size=cells[0].size or 0.0,
        bold=all(bool(c.all_bold) for c in cells), role=role)


def _rows(pm, finder) -> list[list]:
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


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True,
             right: bool = False) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        align = (m.Align.RIGHT if right else
                 m.Align.CENTER if centre else m.Align.LEFT)
        self.items.append(m.HmLine(
            text=_tidy(text.strip()),
            prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    # NO `drop` HERE, deliberately: this reader records everything it
    # consumes as an item, so nothing needs a Dropped. The rows it does not
    # identify are left UNCONSUMED for core, which is the measurable
    # alternative to a guessed role.

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
