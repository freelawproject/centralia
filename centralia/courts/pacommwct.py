"""Commonwealth Court of Pennsylvania ('pacommwct') — the COLON-RAIL stack.

Everything unique to pacommwct lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py, beside its two Pennsylvania siblings.

WHICH KIND OF TWO-COLUMN COURT THIS IS. The third of the colon-rail family
(pa, pasuperct, and del with '§'): the divider is TYPED, as a column of ':'
glyphs, so the rail is real ink, it is found by the x position of its own
column, and nothing here is inferred from wording. Page 1 of all 42 corpus
records draws it.

    ┌──────────────────────────────────────────────────────────────────────┐
    │        IN THE COMMONWEALTH COURT OF PENNSYLVANIA   the masthead,     │
    │                                                    CENTRED, row 1    │
    │ Anthony Morinelli,                :                     <- the box   │
    │               Petitioner          :                                  │
    │                                   :                                  │
    │            v.                     :                                  │
    │                                   :                                  │
    │ Unemployment Compensation         :                                  │
    │ Board of Review,                  : No. 241 C.D. 2025    the docket  │
    │              Respondent           : Submitted: June 16, 2026  the    │
    │                                                       submission date│
    │ BEFORE: HONORABLE ANNE E. COVEY, Judge          the panel, wrapping  │
    │         HONORABLE STACY WALLACE, Judge          one judge per row    │
    │         HONORABLE STELLA M. TSAI, Judge                              │
    │                                                                      │
    │ OPINION NOT REPORTED                            the publication flag │
    │                                                                      │
    │ MEMORANDUM OPINION BY                           the writing's own    │
    │ JUDGE COVEY            FILED: August 4, 2026    byline — LEFT TO CORE│
    └──────────────────────────────────────────────────────────────────────┘

MEASURED FACTS (42 records in assets/pacommwct, page 1 of each, 612x792):

- THE MASTHEAD IS ROW 1 AND IT IS THE COURT NAMING ITSELF: 'IN THE
  COMMONWEALTH COURT OF PENNSYLVANIA', 42 of 42, centred (x0 127.7-145.7,
  x1 484.0-504.4 — centre 305.9-324.9 against a 306.0 axis). Unlike
  pasuperct, which sets its masthead INSIDE the box's right column, this
  court prints it above the box; and unlike pasuperct there is NOTHING else
  in the head band — no listing number, no public-domain citation.
- THE RAIL IS A COLUMN OF ':' GLYPHS at one x, re-tabbed per document:
  288.1-310.6 over the corpus, so it is measured per record as the modal x0
  of the ':' glyphs on page 1. The modal column holds 6-22 glyphs; the next
  busiest colon column on any record holds ONE (the ordinary punctuation of
  'In re:', 'Appeal of:', 'Submitted:'), which is why the floor is 5.
- THE BOX IS A MAXIMAL RUN OF CONSECUTIVE RAIL ROWS, and over all 42 records
  there is exactly ONE run: not one row inside the band lacks a glyph in the
  rail's column. So this paper sets no consolidation divider and no second
  box — a consolidated appeal stacks its segments INSIDE the one box
  (js_technology, pa_department_of_revenue) with a docket beside each.
- WHAT THE RIGHT COLUMN CARRIES is four things and nothing else, 42 of 42:
  the appeal docket as a complete row ('No. 241 C.D. 2025', 'No. 282 M.D.
  2023', '136 M.D. 2026' with no prefix, 'Nos. 944 and 1162-1169 C.D. 2023'),
  the submission or argument date ('Submitted: June 16, 2026' 27 records,
  'Argued: May 12, 2026' 15), and two notes the court sets in capitals —
  'CASES CONSOLIDATED' (4) and 'CASE SEALED' (2).
- THE LEFT COLUMN carries party names (wrapping over as many rows as they
  need — carlino runs to 15), the pivot 'v.' (twice on a third-party
  joinder: trivelpiece, gabra), a party STATUS ('Appellant', 'Petitioners',
  'Respondents') and the court's own designation rows ('Appeal of: Borough
  of Prospect Park', 'Objection of: Lawrence S. Sparano', 'In re: Nomination
  Petition of Martin B. Flynn').
- THERE IS NO ORIGIN RECITAL. pa and pasuperct both print one ('Appeal from
  the Order Entered …' / 'In the Court of Common Pleas of … County'); this
  court prints NONE on page 1 of any of the 42 records, so `lower_court`,
  `lower_court_docket` and `history` are left unset. The tribunal below is
  named only as a PARTY ('Unemployment Compensation Board of Review',
  'Pennsylvania Parole Board') — which is a party name, and reading it as
  the court below would be an inference the page does not make.
- THE PANEL is 'BEFORE: HONORABLE <NAME>, <bench>' with ONE JUDGE PER ROW,
  the wraps indented to 136.8-144.0 against a 64.8-72.0 body rail: 3 judges
  on a normal panel, 7 on the en banc papers (abdulhay, giant_eagle,
  pa_department, passhe, s.j._hill, js_technology), 1 on the single-judge
  election paper (in_re_nomination). 41 of 42 — g._wilkins is PER CURIAM and
  prints no roster at all, which is the court's own choice and not a defect.
- THE BYLINE names the paper first and the judge second, over ONE or TWO
  rows: 'OPINION' / 'BY JUDGE McCULLOUGH', 'MEMORANDUM OPINION BY' / 'JUDGE
  COVEY', 'OPINION BY JUDGE WOJCIK' (one row, giant_eagle), 'OPINION1' / 'BY
  JUDGE FIZZANO CANNON' (a footnote mark on the paper's own name, passhe),
  'OPINION' / 'PER CURIAM' (g._wilkins). Each carries a 'FILED: <date>'
  piece flush right, on the title row (norman) or on the name row (the other
  41).

FOUR TRAPS THIS PAPER SETS, all of them found in the geometry:

1. THE RAIL IS NOT ALWAYS ITS OWN PIECE. pdfio returns ': No. 241 C.D. 2025'
   as one line beginning at the rail, and 'Brian S. Goldthorpe and Bruce E.
   Yelk :' / 'Winters, George Scherbak, Brandywine :' / 'Associates, L.P.,
   L&R Partnership, LLC,:' as single lines that CROSS it. A whole-line side
   test puts the docket in the party column and loses it, so the row is
   split GLYPH BY GLYPH at the rail's x, the rail's own glyphs shed first.
2. A ':' IS ORDINARY PUNCTUATION IN THIS CAPTION. 'In re: Nomination
   Petition of Martin B. Flynn', 'Appeal of: Brandywine Village',
   'Objection of: Lawrence S. Sparano' all print one in the LEFT column, and
   the right column's own date rows print 'Submitted:' / 'Argued:'. Only
   glyphs in the rail's own column (±3pt of the modal x) are rail — ca6's
   test, not a character test.
3. THE ROW, NOT THE LINE, IS THE UNIT. pdfio splits at the column gap (the
   'column-gap-split' event fires on 5-10 rows of every record), so 'JUDGE
   COVEY' and 'FILED: August 4, 2026' arrive as two pieces of ONE visual
   row, and so do a party name and the docket beside it. Rows are grouped by
   `top` first.
4. POPULATE THE CRITERIA BEFORE GATING ON THEM. wyo shipped its
   `docket_number` gate one line above the walk that fills it and refused
   all 50 of its own correctly-read records; the gates here stand after the
   whole box has been read.

THE PUBLICATION FLAG IS NOT FURNITURE. 10 of the 42 records print 'OPINION
NOT REPORTED' between the panel and the byline — the court stating how its
own paper may be used, which is what `publication` names. It is claimed and
rendered in place, with the fact ALSO in `publication_status`.

THE BYLINE IS LEFT TO CORE. The reader claims the 'FILED:' piece beside it
(its own line, right of the rail) and stops without claiming the byline
itself, so the writing still opens where the court names its author. The
paper's name and the judge's name stand on two rows here, which is what the
profile's `opinion_by_headings` grammar is for.

Corpus split over the 42 records: 42 colon-rail, 0 NOTHING. Within that one
contract two FORMATS of the band below the box — 32 `colon-rail/reported`
and 10 `colon-rail/not-reported` (the memorandum) — and orthogonally 35
single-segment records, 3 multi-docket (consolidated) and 2 with a
third-party joinder pivot.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# --------------------------------------------------------------------------
# the rail — declared facts of THIS paper, measured over its own corpus
# --------------------------------------------------------------------------

_RAIL_GLYPH = ":"
# ca6's rail window: a glyph belongs to the rail when it stands in the rail's
# own COLUMN, never because of what character it is.
_RAIL_WINDOW = 3.0
# The modal ':' column must be a COLUMN, not an accident of punctuation. The
# 42 records hold 6-22 glyphs in theirs; the busiest rival column on any
# record holds 1.
_RAIL_FLOOR = 5
# The page axis, for the centred masthead. Measured centres 305.9-324.9 on a
# 612pt page: the court centres the masthead on the MEASURE, and where the
# measure is offset (carlino's body rail is 64.8, right edge 547.4) the
# centre goes with it.
_AXIS_TOL = 20.0

# --------------------------------------------------------------------------
# the landmarks — closed vocabularies, never a name read by wording
# --------------------------------------------------------------------------

# The court naming itself. One row, 42 of 42.
_MASTHEAD = re.compile(
    r"^IN\s+THE\s+COMMONWEALTH\s+COURT\s+OF\s+PENNSYLVANIA$", re.I)
_COURT_NAME = "IN THE COMMONWEALTH COURT OF PENNSYLVANIA"
# The appeal docket, as a COMPLETE row: a number (or a run of numbers), a
# two-letter docket code with its periods, and a year. Over the corpus only
# C.D. (the Commonwealth docket) and M.D. (the miscellaneous docket) occur;
# the 'No.' prefix is present on 41 records and absent on one
# (in_re_nomination prints a bare '136 M.D. 2026'), so the prefix is
# optional. Applied ONLY to a right-hand cell, which carries four things.
_DOCKET = re.compile(
    r"^(?:Nos?\.\s*)?(\d[\d\s,\-]*(?:and\s+[\d\s,\-]+)?[A-Z]\.[A-Z]\.\s+\d{4})"
    r"\.?$")
# The date the case was argued or submitted on the briefs. `submitted` is
# the model's field for both (the render labels it 'argued/submitted'), and
# it is NOT the decision date, which the byline row prints as 'FILED:'.
_SUBMITTED = re.compile(
    r"^(Submitted|Argued|Reargued|Resubmitted)\s*:\s*(.+?)\.?$", re.I)
# The two notes this court sets in capitals in the right column.
_CASE_NOTE = re.compile(r"^CASES?\s+(?:CONSOLIDATED|SEALED)\.?$", re.I)
# The bench. 'BEFORE:' opens the roster and every row of it — the first one
# included — names its judge with the court's own honorific.
_BEFORE = re.compile(r"^B\s?EFORE\s*:?\s*(.*)$", re.I)
_HONORABLE = re.compile(r"^HONORABLE\b", re.I)
# 'HONORABLE ANNE E. COVEY, Judge' / '… , President Judge' / '… , Senior
# Judge' / '… , Judge (P.)' — the honorific and the bench title are a closed
# vocabulary; the NAME is whatever stands between them.
_ROSTER_ROW = re.compile(
    r"^HONORABLE\s+(.+?),\s*(?:President\s+Judge|Senior\s+Judge|Judge)"
    r"(?:\s*\([A-Z]\.\))?\s*[*†‡]?\s*$", re.I)
# The court stating how its own paper may be used.
_PUBLICATION = re.compile(r"^OPINION\s+NOT\s+REPORTED\.?$", re.I)
# WHAT THE PAPER CALLS ITSELF — the first row of the byline, and the row
# that ends this reader. The trailing digit is the footnote mark passhe
# hangs on the word 'OPINION'; the trailing 'BY …' is the fold the court
# uses when the judge's name will not fit beside it.
_PAPER = re.compile(
    r"^(?:MEMORANDUM\s+|CONCURRING\s+|DISSENTING\s+)*"
    r"(?:OPINION|MEMORANDUM|ORDER|STATEMENT)\d*"
    r"(?:\s+BY\b.*)?$", re.I)
# …and its second row: who signed it. 'BY JUDGE McCULLOUGH', 'JUDGE COVEY',
# 'PRESIDENT JUDGE COHN JUBELIRER', 'BY SENIOR JUDGE LEAVITT', 'PER CURIAM'.
_SIGNER = re.compile(
    r"^(?:BY\s+)?(?:PER\s+CURIAM|(?:PRESIDENT\s+|SENIOR\s+)?JUDGE\b.*)\d*$",
    re.I)
_FILED = re.compile(r"^FILED\s*:?\s*(.+?)\s*\.?$", re.I)

# The left column's furniture: party STATUS and the pivot are closed
# vocabularies; a party NAME is never read by wording.
_STATUS = re.compile(
    r"^(?:Appellants?|Appellees?|Petitioners?|Respondents?|Intervenors?"
    r"|Cross-Appellants?|Cross-Appellees?|Amic(?:us|i)(?:\s+Curiae)?"
    r"|Plaintiffs?|Defendants?|Objectors?)\b[.,]?$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# 'Appeal of: Borough of Prospect Park' / 'Objection of: Lawrence S.
# Sparano' / 'In re: Nomination Petition of …' — caption apparatus, not a
# party name, so it is kept out of `parties` and `case_name` while still
# reading as caption.
_DESIGNATION = re.compile(
    r"^(?:Appeal\s+of|Appeal\s+from|Objection\s+of|In\s+re)\b", re.I)


# THE CRITERIA FIELD NAMES ARE THE MODEL'S — `Criteria` in centralia/model.py
# declares every one of them. A key written under an invented name is
# attached by setattr and never serializes: read as read, reported as
# nothing. The argued/submitted date is `submitted`; the FILED date is
# `decision_date`; they are two different dates and neither substitutes.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="pacommwct")
def read_headmatter_pacommwct(model, geom, **_):
    """Read the Commonwealth Court's colon-rail agency stack, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 5:
        return NOTHING
    # THE RAIL IS THE DISPATCH. Not the masthead, not the flag below the box
    # — the divider, which is the thing that survives the court changing its
    # wording. No rail, no claim.
    rail_x = _rail(page1)
    if rail_x is None:
        return NOTHING
    railed = [_is_rail(g, rail_x) for g in rows]
    if not any(railed):
        return NOTHING

    ctx = _Ctx()
    axis = page1.width / 2
    # THE WALK IS BOUNDED AT EVERY STATE. `head` runs to the first rail row;
    # `box` to the first row that is not a rail row; `after` accepts the
    # roster, the publication flag and the byline and nothing else, and the
    # byline stops the reader. A row at no position this paper uses is left
    # to core rather than tinted with a role that would be a guess.
    state = "head"
    box: list = []                  # the rail rows of the box being read
    boxes = 0
    left_plain: list[str] = []       # the box's left rows, verbatim
    dockets: list[str] = []
    roster: list[str] = []
    court_seen = False

    idx = 0
    while idx < len(rows):
        group = rows[idx]
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            idx += 1
            continue
        x0 = min(l.x0 for l in pieces)
        x1 = max(l.x1 for l in pieces)
        centred = abs((x0 + x1) / 2 - axis) <= _AXIS_TOL

        # ---- the box: a maximal run of consecutive rail rows -------------
        if railed[idx]:
            if state != "box":
                state = "box"
                box = []
            box.append(pieces)
            idx += 1
            if idx < len(rows) and railed[idx]:
                continue
            # the run has ended: close the box
            left, right, lp, rp, ids = _read_box(box, rail_x, page1)
            if left or right:
                ctx.caption(page1.number, left, right, len(box), ids,
                            "colon-rail" if not boxes else None)
                boxes += 1
                left_plain.extend(lp)
                for one in rp:
                    hit = _DOCKET.match(one)
                    if hit:
                        dockets.append(_norm(hit.group(1)))
                    else:
                        dated = _SUBMITTED.match(one)
                        if dated:
                            ctx.crit.setdefault("submitted",
                                                _norm(dated.group(2)))
            state = "after"
            continue

        # ---- the head band, above the box --------------------------------
        if state == "head":
            if _MASTHEAD.match(text):
                court_seen = True
                ctx.emit(pieces, "court", centre=centred)
            idx += 1
            continue

        # ---- the panel: 'BEFORE:' and one honorific per row --------------
        bench = _BEFORE.match(text)
        if state == "after" and bench and not roster:
            ctx.emit(pieces, "panel", centre=False, body_x0=body_x0)
            roster.append(_norm(bench.group(1)))
            idx += 1
            # THE ROSTER RUNS WHILE THE COURT KEEPS NAMING JUDGES. Every row
            # of it opens on the court's own honorific, indented under the
            # first; 3 judges normally, 7 en banc, 1 on the election paper.
            while idx < len(rows):
                nxt = sorted(rows[idx], key=lambda l: l.x0)
                one = _norm(" ".join(l.plain for l in nxt))
                if not _HONORABLE.match(one):
                    break
                ctx.emit(nxt, "panel", centre=False, body_x0=body_x0)
                roster.append(one)
                idx += 1
            continue

        # ---- the court stating how its own paper may be used -------------
        if state == "after" and _PUBLICATION.match(text):
            ctx.crit.setdefault("publication_status", "unpublished")
            ctx.emit(pieces, "publication", centre=centred)
            idx += 1
            continue

        # ---- the byline: its DATE is the headmatter's, the byline is the
        # ---- writing's, and the reader stops here ------------------------
        if state == "after" and _is_byline(pieces):
            _claim_filed(ctx, pieces)
            # THE PAPER'S NAME AND THE JUDGE'S NAME STAND ON TWO ROWS, and
            # the 'FILED:' piece sits on one of them (the title row on
            # norman, the name row on the other 41). Both are inspected;
            # neither byline row is claimed.
            if idx + 1 < len(rows):
                nxt = sorted(rows[idx + 1], key=lambda l: l.x0)
                if _is_signer(nxt):
                    _claim_filed(ctx, nxt)
            break

        # ---- a row at no position this paper uses ------------------------
        if state == "after":
            break
        idx += 1

    # --- WHAT THE PAGE SAID, populated BEFORE it is judged ----------------
    # (wyo shipped its docket gate one line above the walk that fills it and
    # refused all 50 of its own correctly-read records.)
    if dockets:
        ctx.crit["docket_number"] = dockets[0]
        if dockets[1:]:
            ctx.crit["other_dockets"] = dockets[1:]
    if court_seen:
        ctx.crit.setdefault("court", _COURT_NAME)
    caption_rows = [t for t in left_plain if t]
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    groups = _party_groups(left_plain)
    if len(groups) >= 2:
        # PARTIES ONLY WHERE THE COURT PRINTS THE PIVOT. An election
        # objection ('In re: Nomination Petition of Martin B. Flynn' /
        # 'Objection of: Lawrence S. Sparano') has no two sides, and
        # inventing them from designation rows names the candidate as a
        # litigant against himself.
        ctx.crit.setdefault("parties", groups[:8])
        ctx.crit.setdefault("case_name", " v. ".join(groups))
    if roster:
        line = _norm(" ".join(roster))
        # THE PRINTED FORM BESIDE THE PARSED FORM. `panel_line` is the
        # roster verbatim; `panel` is the judges' names, taken from between
        # the honorific and the bench title.
        ctx.crit.setdefault("judges", line)
        ctx.crit.setdefault("panel_line", "BEFORE: " + line)
        names = _panel_names(roster)
        if names:
            ctx.crit.setdefault("panel", names)

    # --- the gates: what this contract REQUIRES to have been read ---------
    if not boxes:
        return NOTHING              # no box: not this paper
    if not court_seen:
        return NOTHING              # the masthead never named the court
    if "docket_number" not in ctx.crit:
        return NOTHING              # no docket: the right column was missed
    ctx.crit["headmatter_style"] = "colon-rail"
    return ctx.result()


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _rail(pm) -> float | None:
    """The x of the caption's typed divider on ``pm``, or None.

    A rail is a COLUMN: ':' glyphs stacked at one x, not a count of colons
    anywhere on the page. The x is measured per record because the court
    re-tabs the box per document (288.1-310.6 over the corpus)."""
    cols = Counter(round(c["x0"], 1) for l in pm.lines for c in l.chars
                   if (c.get("text") or "") == _RAIL_GLYPH)
    if not cols:
        return None
    x, _n = cols.most_common(1)[0]
    stack = sum(n for k, n in cols.items() if abs(k - x) <= _RAIL_WINDOW)
    if stack < _RAIL_FLOOR:
        return None
    return float(x)


def _rail_chars(line, rail_x: float) -> list:
    """The chars of ``line`` that stand in the rail's own column."""
    return [c for c in line.chars
            if (c.get("text") or "") == _RAIL_GLYPH
            and abs(c["x0"] - rail_x) <= _RAIL_WINDOW]


def _is_rail(group: list, rail_x: float) -> bool:
    """Is this visual ROW one of the box's rows? True where any glyph of it
    stands in the rail's own column."""
    return any(_rail_chars(l, rail_x) for l in group)


def _shed_rail(line, rail_x: float):
    """``line`` with the rail's glyphs removed, or None when the line WAS
    the rail. The glyph is identified by its COLUMN, never by its character:
    'In re:', 'Appeal of:' and 'Submitted:' print colons elsewhere and keep
    them."""
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
    'Brian S. Goldthorpe and Bruce E. Yelk :' — one line — wholly in the
    party column while putting ': No. 241 C.D. 2025' there too."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


def _read_box(box: list, rail_x: float, pm):
    """One caption box, torn at the rail. Returns the two stacks, their
    plain text and the ids consumed."""
    left: list = []
    right: list = []
    left_plain: list[str] = []
    right_plain: list[str] = []
    ids: set[int] = set()
    for pieces in box:
        l_cells, r_cells = [], []
        for line in pieces:
            shed = _shed_rail(line, rail_x)
            if shed is None:
                continue            # the line WAS the rail
            for side, bucket in ((_side(shed, rail_x, "L"), l_cells),
                                 (_side(shed, rail_x, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        ids.update(l.id for l in pieces)
        # THE TWO STACKS ARE NOT ROW-PAIRED. The rail runs a glyph on every
        # row of the box and most of those rows carry no words in the right
        # column at all (morinelli: eight rail rows, six party rows, two
        # right-hand rows), so padding the columns to a common length would
        # add nothing but blank tinted rows. Each column flows on its own;
        # the true rail height is recorded on the block.
        if l_cells:
            left.append(_cell(l_cells, "caption", pm))
            left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        else:
            # A BLANK LEFT CELL IS STILL A ROW OF THE PARTY STACK, for the
            # party reader: 'Petitioner' / '' / 'v.' is where the court
            # breaks its segments, and collapsing the blanks out of the
            # sequence would join a status to the pivot below it.
            left_plain.append("")
        if r_cells:
            right.append(_cell(r_cells, _right_role(r_cells), pm))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    return left, right, left_plain, right_plain, ids


def _right_role(cells: list) -> str:
    """What the right column is saying on this row. Each of its tenants by
    its own landmark; over the corpus it carries nothing else, so
    `case-info` catches only the court's own capitalised notes."""
    text = _norm(" ".join(c.plain for c in cells))
    if _DOCKET.match(text):
        return "docket"
    if _SUBMITTED.match(text):
        return "date"
    if _CASE_NOTE.match(text):
        return "case-info"
    return "case-info"


# --------------------------------------------------------------------------
# the byline band — inspected, never claimed
# --------------------------------------------------------------------------

def _pieces_minus_filed(pieces: list) -> str:
    """The row's text with any 'FILED:' piece taken off. norman prints
    'OPINION' and 'FILED: May 18, 2026' as two pieces of one row, so the
    row's own words are only readable with the date piece set aside."""
    return _norm(" ".join(p.plain for p in pieces
                          if not _FILED.match(_norm(p.plain))))


def _is_byline(pieces: list) -> bool:
    """Is this the row where the court names its paper? That row opens the
    writing, so the reader claims only the date beside it and stops."""
    text = _pieces_minus_filed(pieces)
    return bool(text) and bool(_PAPER.match(text))


def _is_signer(pieces: list) -> bool:
    """…and is the row under it the one where the court names the judge?"""
    text = _pieces_minus_filed(pieces)
    return bool(text) and bool(_SIGNER.match(text))


def _claim_filed(ctx, pieces: list) -> None:
    """The 'FILED: <date>' piece of a byline row — the decision date, which
    is the last thing the headmatter says and belongs in it. The byline
    itself is not claimed."""
    for part in pieces:
        dated = _FILED.match(_norm(part.plain))
        if dated:
            ctx.crit.setdefault("decision_date", _norm(dated.group(1)))
            ctx.emit([part], "date", centre=False, right=True)


# --------------------------------------------------------------------------
# what the box and the roster said
# --------------------------------------------------------------------------

def _panel_names(roster: list[str]) -> list[str]:
    """The roster's names, one per row. The honorific and the bench title
    are a closed vocabulary ('HONORABLE …, President Judge', '…, Senior
    Judge', '…, Judge (P.)'); the name is whatever stands between them, so
    'RENÉE COHN JUBELIRER' is one person and 'Judge' is nobody."""
    out = []
    for row in roster:
        hit = _ROSTER_ROW.match(row)
        if hit:
            out.append(_norm(hit.group(1)))
    return out


def _party_groups(left_plain: list[str]) -> list[str]:
    """The party names of the FIRST docket segment, in printed order, one
    entry per side of the pivot. Statuses, the pivot and the caption's own
    designation rows are dropped; a party name that wraps over rows is
    rejoined. Returns fewer than two groups where the court printed no
    pivot, which is the caller's signal that this caption has no sides."""
    groups: list[list[str]] = [[]]
    seen_pivot = False
    last_status = False
    for text in left_plain:
        if not text:
            continue
        if _PIVOT.match(text):
            groups.append([])
            seen_pivot = True
            last_status = False
            continue
        if _DESIGNATION.match(text):
            # THE DESIGNATION CLOSES THE PARTY LIST of its segment, and its
            # own WRAP rows are not party names either ('Appeal of:
            # Brandywine Village' / 'Associates, L.P., L&R Partnership,
            # LLC,').
            break
        if _STATUS.match(text):
            last_status = True
            continue
        if last_status:
            # A CONSOLIDATED CAPTION STACKS ITS SEGMENTS IN ONE BOX. The
            # court closes a segment with a status row and opens the next
            # with a party name ('Respondents' / 'Dish Network, LLC,' —
            # js_technology; 'Respondent' / 'Scientific Games, LLC,' —
            # pa_department). A status followed by a NAME rather than a
            # pivot is that boundary, and the parties of this case are the
            # ones the first segment names. 2 of 42 records.
            break
        groups[-1].append(text)
    if not seen_pivot:
        return []
    # The trailing comma is stripped from the JOINED name, never row by row:
    # 'Gazi Abdulhay, Ali Abdulhay,' / 'Nabil Abdulhay, and Valley Land' /
    # 'Holdings, LLC,' is one side whose rows end where the measure ran out.
    out = [_norm(" ".join(g)).rstrip(",;") for g in groups if g]
    return [t for t in out if t]


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

def _tidy(markup: str) -> str:
    """Leading whitespace off a standalone row, INCLUDING whitespace inside
    the opening tag. The court sets 'FILED:' on a tab and pdfio keeps the
    real space glyphs, so the markup arrives as '   FILED: August 4, 2026';
    the render preserves it (`white-space: pre-wrap`) and it fights the
    row's own alignment, which is what carries the position. The caption
    CELLS keep their spacing — there the gap after the rail is the page's
    own column gutter."""
    return re.sub(r"^(\s*(?:<[a-z]+>\s*)*)",
                  lambda mm: re.sub(r"\s+", "", mm.group(1)), markup)


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
    """Page ``pm``'s visual rows, grouped by top. pdfio splits a justified
    row at its wide gaps ('column-gap-split' fires on 5-10 rows of every
    record here), so the row — not the line — is the unit: a party name and
    the docket beside it arrive as two pieces of one row, and so do the
    byline and the filing date."""
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

    def _line(self, parts: list, role: str, align, rel: float) -> m.HmLine:
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=_tidy(text.strip()),
            prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0, rel=rel,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def emit(self, group: list, role: str, centre: bool = True,
             right: bool = False, body_x0: float | None = None) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        align = (m.Align.RIGHT if right else
                 m.Align.CENTER if centre else m.Align.LEFT)
        # THE ROSTER'S WRAPS ARE INDENTED UNDER THE FIRST NAME (136.8-144.0
        # against a 64.8-72.0 body rail) and that indent is how the page
        # says they belong to the row above. `rel` is what carries it.
        rel = 0.0
        if body_x0 is not None and align is m.Align.LEFT:
            rel = max(0.0, round(parts[0].x0 - body_x0, 1))
        self.items.append(self._line(parts, role, align, rel))
        self.consumed.update(p.id for p in parts)

    def caption(self, page: int, left: list, right: list, rail_rows: int,
                ids: set, style_id: str | None) -> None:
        # `rail_rows` is what the RENDERER draws the divider from, so it is
        # the height of the taller stack; the number of rail rows the page
        # actually prints is a measured fact and goes on `fp`.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=_RAIL_GLYPH,
            rail_rows=max(len(left), len(right), 1), style_id=style_id,
            fp={"rail": _RAIL_GLYPH, "rail_rows": rail_rows},
            prov=m.Prov(page, tuple(sorted(ids)))))
        self.consumed.update(ids)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# writing.covers — the announcement, over TWO rows
# --------------------------------------------------------------------------
# THE DOCSTRING ABOVE LEFT THE BYLINE TO CORE, on the reasoning that "the
# paper's name and the judge's name stand on two rows here, which is what
# the profile's `opinion_by_headings` grammar is for." That was measured
# wrong. A grammar parses a ROW, and no row of this pair is a byline on its
# own: 'MEMORANDUM OPINION BY' names no judge and 'JUDGE COVEY' names no
# paper. Counted over all 42 records, 12 of the 13 announcements did not
# parse at all — only giant_eagle's, which happens to fit on one row
# ('OPINION BY JUDGE WOJCIK').
#
# WHAT THAT COST, both directions:
#   * city_of_lancaster_v._i._grivas — the unparsed 'MEMORANDUM OPINION BY'
#     stood unclaimed above the writing and opened a PHANTOM: a 3-block
#     'majority' holding the announcement and one paragraph, with the real
#     opinion following it as an 83-block 'order'.
#   * g._abdulhay_v._upper_macungie_twp._zhb prints a CONCURRING OPINION and
#     came back with ONE writing — the concurrence swallowed into a 151-block
#     majority.
#   * passhe_v._plrb prints a CONCURRING AND DISSENTING OPINION and came back
#     with ONE writing, typed `order`, 135 blocks, authored 'MATTHEW S. WOLF,
#     Judge' — the SEPARATE judge's name on the whole paper.
# (the user, 2026-08-20, on records with two or more writings: 'those with 2
# or more are all wrong creating second opinions incorrectly'. The count was
# the symptom; the cause runs both ways, and merging is the commoner half.)
#
# THE FORM, measured over every announcement in the corpus — a row PAIR at
# the body rail, never anywhere else:
#
#      OPINION                     BY JUDGE McCULLOUGH          7
#      OPINION                     BY JUDGE FIZZANO CANNON      7
#      MEMORANDUM OPINION          BY JUDGE WALLACE             6
#      OPINION BY                  JUDGE COVEY                  4
#      OPINION BY                  PRESIDENT JUDGE COHN JUBELIRER
#      OPINION                     BY SENIOR JUDGE LEAVITT
#      OPINION1                    BY JUDGE FIZZANO CANNON      (a footnote
#      OPINION                     PER CURIAM                    mark on the
#      DISSENTING OPINION          BY JUDGE FIZZANO CANNON       paper's name)
#      CONCURRING OPINION BY       PRESIDENT JUDGE COHN JUBELIRER
#      CONCURRING AND DISSENTING OPINION BY   JUDGE WOLF
#
# The first row states the KIND and may carry the 'BY'; the second names the
# judge and may carry it instead. The lead announcement stands on page 1 and
# every separate writing on page 2 or later, but position is not the test —
# the printed words are.
_ANN_HEAD = re.compile(
    r"^(?P<kind>(?:[A-Z][A-Z ]*\s)?OPINION)\d*(?:\s+BY)?$")
_ANN_NAME = re.compile(
    r"^(?:BY\s+)?(?:PRESIDENT\s+|SENIOR\s+|ACTING\s+)?"
    r"(?:JUDGE|JUSTICE)\s+\S.*$|^PER\s+CURIAM$", re.I)
# 'OPINION' alone is the court's opinion. Anything else the first row says
# is the kind, and it goes through `normalize_opinion_type` like a byline's.
_ANN_PLAIN = ("opinion", "memorandum opinion")
_ANN_RAIL_TOL = 10.0


@decider("writing.covers", court="pacommwct")
def writing_covers_pacommwct(model=None, geom=None, **_):
    """Where each writing opens, and the kind its announcement states."""
    if model is None:
        return NOTHING
    rail = geom.body_x0 if geom and geom.body_x0 else 72.0
    starts: dict[int, str] = {}
    for pm in model.pages:
        rows: dict = {}
        for line in pm.lines:
            if line.plain.strip():
                rows.setdefault(round(line.top, 1), []).append(line)
        tops = sorted(rows)
        for i, top in enumerate(tops[:-1]):
            pieces = sorted(rows[top], key=lambda l: l.x0)
            head = " ".join(pieces[0].plain.split())
            said = _ANN_HEAD.match(head)
            if not said or pieces[0].x0 > rail + _ANN_RAIL_TOL:
                continue
            nxt = sorted(rows[tops[i + 1]], key=lambda l: l.x0)
            if nxt[0].x0 > rail + _ANN_RAIL_TOL:
                continue
            if not _ANN_NAME.match(" ".join(nxt[0].plain.split())):
                continue
            kind = " ".join(said.group("kind").split()).lower()
            starts[pieces[0].id] = ("majority" if kind in _ANN_PLAIN
                                    else kind.replace(" opinion", ""))
    return {"starts": starts, "drop": []} if starts else NOTHING
