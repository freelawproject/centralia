"""Superior Court of Pennsylvania ('pasuperct') — the COLON-RAIL docket stack.

Everything unique to pasuperct lives here. It imports core, never another
court file, and no other court file imports it.

WHICH KIND OF TWO-COLUMN COURT THIS IS. Three shapes exist in the repo and
this is the FIRST of them: ca6 draws its divider (box-drawing glyphs, a
stacked ')'), va prints NO divider and the measured x0 threshold IS the
divider, and pasuperct — like its sibling pa, and like del with '§' — TYPES
its divider as a column of ':' glyphs. So the rail is real ink, it is found
by the x position of its own column, and nothing here is inferred from
wording. Page 1 of all 42 corpus records draws it; NO record on page 1 draws
a single h_rule or v_rule, so the typed colon is the only divider this paper
has.

    ┌──────────────────────────────────────────────────────────────────────┐
    │ J-A16045-26                                      the listing number  │
    │ NON-PRECEDENTIAL DECISION - SEE SUPERIOR COURT O.P. 65.37   the flag │
    │                              ── or, on a precedential paper ──       │
    │                       2026 PA Super 146          the public cite     │
    │                                                                      │
    │ IN RE: ADOPTION OF: J.D.L., A : IN THE SUPERIOR COURT OF  <- the box │
    │ MINOR                        :       PENNSYLVANIA                    │
    │                              :                                       │
    │ APPEAL OF: K.J.L., MOTHER    :                                       │
    │                              :                                       │
    │                              : No. 218 WDA 2026                      │
    │                                                                      │
    │        Appeal from the Order Entered January 29, 2026   the recital,  │
    │        In the Court of Common Pleas of Greene County    CENTRED under │
    │        Orphans' Court at No: 39 O.A. of 2025            its own box   │
    │                                                                      │
    │ BEFORE: McLAUGHLIN, J., KING, J., and BENDER, P.J.E.   the panel      │
    │ MEMORANDUM BY BENDER, P.J.E.:      FILED: August 11, 2026            │
    └──────────────────────────────────────────────────────────────────────┘

MEASURED FACTS (42 records in assets/pasuperct, page 1 of each, 612x792):

- THE RAIL IS A COLUMN OF ':' GLYPHS at one x, re-tabbed per document:
  318.1-332.5 over the corpus, so it is measured per record as the modal x0
  of the ':' glyphs on page 1. The modal column holds 9-29 glyphs; the next
  busiest colon column on any record holds 2 (the ordinary punctuation of
  'IN RE:', 'APPEAL OF:', 'at No(s):'), which is why the floor is 6.
- THE BOX IS A MAXIMAL RUN OF CONSECUTIVE RAIL ROWS. Checked over all 42
  records: not one row inside a run lacks a glyph in the rail's column, and
  not one row between two runs carries one. 35 records set one box; 7 set
  two (consolidated appeals — adoption_of_j.l., branch, bryant, guthrie,
  smith and both solomon records: 35 + 7, 49 boxes over the corpus). No
  record sets three.
- WHAT CLOSES A BOX IS A ROW THAT CROSSES THE RAIL WITHOUT A GLYPH IN IT.
  The recital is centred on the page axis (every one of its rows centres at
  305.4-305.9 on a 612pt page) and runs 113-450pt wide, so it always spans
  the rail's column while printing no colon there. A caption row never does:
  the left cell stops before the rail, the right cell starts after it, and
  the rows pdfio returns GLUED across the gap carry the rail glyph inside
  them.
- WHAT THE RIGHT COLUMN CARRIES is three things and nothing else: the
  court's own masthead over two rows ('IN THE SUPERIOR COURT OF' /
  'PENNSYLVANIA') and the appeal docket as a complete row ('No. 218 WDA
  2026' — number, a three-letter district code, year). 42 of 42.
- THE LEFT COLUMN carries party names (wrapping over as many rows as they
  need — pennesi runs to 15), the pivot 'v.', a party STATUS ('Appellant',
  'Appellants', 'Petitioner') and the court's own designation lines
  ('APPEAL OF: K.J.L., MOTHER', 'IN RE: S.C., AN INCAPACITATED PERSON').
- THE RECITAL follows each box, 2-3 rows, centred: 'Appeal from the {Order,
  Judgment of Sentence, PCRA Order, Decree, Suppression Order} Entered
  <date>' / 'In the Court of Common Pleas of <County> County <Division>' /
  'at No(s): <number below>'. 42 of 42.
- THE PANEL is one 'BEFORE:' row, wrapping to a second row on the en banc
  paper (ramsey, nine judges). 42 of 42.
- THE BYLINE is '<what the paper calls itself> BY <NAME>, <bench>:' —
  OPINION (29), MEMORANDUM (10), CONCURRING OPINION (1), DISSENTING OPINION
  (1), JUDGMENT ORDER (1). 42 of 42, each with a 'FILED[:] <date>' piece
  flush right on its own row.

FOUR TRAPS THIS PAPER SETS, all of them found in the geometry:

1. THE RAIL IS NOT ALWAYS ITS OWN PIECE. pdfio returns ': No. 218 WDA 2026'
   as one line beginning at the rail, and 'COMMONWEALTH OF PENNSYLVANIA : '
   / 'STADIA BROWN, AND ISAIAH LYLES :' / 'AND EDWARD J. MAZZONI AND ANN :'
   as single lines that cross it. A whole-line side test puts the docket in
   the party column and loses it (and core, reading these by line, dropped
   'COMMONWEALTH OF PENNSYLVANIA' out of the second box on both smith and
   solomon), so the row is split GLYPH BY GLYPH at the rail's x, the rail's
   own glyphs shed first.
2. A ':' IS ORDINARY PUNCTUATION IN THIS CAPTION. 'IN RE: ADOPTION OF:',
   'APPEAL OF: K.J.L., MOTHER', 'ESTATE OF: P.H., AN ALLEGED' all print one
   or two in the LEFT column, and the recital prints 'at No(s):'. Only
   glyphs in the rail's own column (+-3pt of the modal x) are rail — ca6's
   test, not a character test.
3. 'BEFORE' IS NOT ALWAYS ONE WORD TO pdfio. Three records return it kerned
   apart as 'B EFORE:' (bryant, pennesi, santos_hernandez, solomon_1) and
   two return it split into two pieces of one visual row ('BEFORE: ' at
   x0=72.0 and the roster at x0=144.0 — peay, robinson). The row is grouped
   by its top first, and the landmark tolerates the kerning break.
4. THE LISTING NUMBER IS NOT A DOCKET. 'J-A16045-26' is the court's
   argument-listing designation — the same string the folio repeats at the
   foot of every page — and it is `case-info`, exactly as pa files its
   '[J-80-2025]'. The appeal's real docket stands in the caption's RIGHT
   column ('No. 218 WDA 2026'), and `docket_number` gets that.

THE PUBLICATION FLAG IS NOT FURNITURE. 11 of the 42 records print
'NON-PRECEDENTIAL DECISION - SEE SUPERIOR COURT O.P. 65.37' between the
listing number and the box; core dropped it as a `status` banner. It is the
court stating how its own paper may be used, which is what `publication`
names, so it is claimed and rendered in place, with the fact ALSO in
`publication_status`. The other 31 print '2026 PA Super <n>' instead — the
court's public-domain citation, which is `citation`, never a docket.

AN AUTHORLESS PAPER IS NOT A DEFECT, and this court prints none: all 42
records sign their writing. THE BYLINE IS LEFT TO CORE all the same — the
reader claims the 'FILED:' piece beside it (its own line, right of the axis)
and stops without claiming the byline itself, so the writing still opens
where the court signs it.

Corpus split over the 42 records: 42 colon-rail, 0 NOTHING. Within that one
contract two FORMATS of the head band — 31 `colon-rail/cited` (the
precedential paper, '2026 PA Super <n>') and 11 `colon-rail/non-precedential`
(the memorandum, O.P. 65.37) — and orthogonally 35 single-box and 7
two-box records.
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
# 42 records hold 9-29 glyphs in theirs; the busiest rival column on any
# record holds 2.
_RAIL_FLOOR = 6
# The page axis, for the centred rows (the citation, the recital).
_AXIS_TOL = 14.0
# The recital is centred TIGHTLY: measured centres 305.4-305.9 against an
# axis of 306.0. The body's own first line is indented to x0=108 and centres
# at 324, so 6pt is what separates a recital row from a paragraph opener.
_RECITAL_AXIS_TOL = 6.0
# ...and a recital row never begins at the body rail. Measured x0 84.0-259.2
# against a 72.0 rail.
_RECITAL_INDENT_MIN = 6.0

# --------------------------------------------------------------------------
# the landmarks — closed vocabularies, never a name read by wording
# --------------------------------------------------------------------------

# 'J-A16045-26', 'J-S08044-26', 'J-E02007-25', 'J-M03005-26' — the court's
# argument-listing designation, repeated by the folio at the foot of every
# page. Caption apparatus, which is what `case-info` names.
_LISTING = re.compile(r"^J-[A-Z]\d+-\d{2}$")
# '2026 PA Super 146' — the court's public-domain citation.
_CITATION = re.compile(r"^(\d{4}\s+PA\s+Super\s+\d+)$", re.I)
# The court stating how its own paper may be used.
_PUBLICATION = re.compile(r"^NON-PRECEDENTIAL\s+DECISION\b", re.I)
# The court naming itself, over the two rows it sets it in.
_MASTHEAD = re.compile(
    r"^(?:IN\s+THE\s+SUPERIOR\s+COURT\s+OF(?:\s+PENNSYLVANIA)?"
    r"|PENNSYLVANIA)$", re.I)
_COURT_NAME = "IN THE SUPERIOR COURT OF PENNSYLVANIA"
# The appeal docket, as a COMPLETE row: a number, a district code and a year.
# Over the corpus: EDA/MDA/WDA (appeals from the three districts) and WDM
# (a petition for specialized review — swanson).
_DOCKET = re.compile(r"^Nos?\.\s*(\d+\s+[A-Z]{2,4}\s+\d{4})\.?$")
# The bench, and the kerning break pdfio puts inside the word (trap 3).
_BEFORE = re.compile(r"^B\s?EFORE\s*:?\s*(.*)$")
# A finite vocabulary of bench titles. The names are whatever stands between
# them ('FORD ELLIOTT' is one person, and 'P.J.E.' is nobody).
_BENCH_WORD = re.compile(r"^(?:C\.J\.|J\.|JJ\.|P\.J\.|P\.J\.E\.|J\.E\.)$")
# The roster is complete when its last row ENDS on a bench title. ramsey's
# nine-judge en banc roster wraps because its first row ends on a comma.
_ROSTER_END = re.compile(r",\s*(?:C\.J\.|JJ?\.|P\.J\.|P\.J\.E\.|J\.E\.)"
                         r"\s*[*†‡]?\s*$")
# '<what the paper calls itself> BY <NAME>, <bench>:'. Anchored on the
# paper's own name so that a caption row reading 'ESTATE OF GLENDON
# SMALLING, BY ' cannot be mistaken for a byline.
_BYLINE = re.compile(
    r"^(?:CONCURRING|DISSENTING|SUPPLEMENTAL|PLURALITY|JUDGMENT|MEMORANDUM"
    r"|OPINION|ORDER|STATEMENT)[A-Z ]*\s+BY\s+[A-Z][^,]*,\s*"
    r"(?:C\.J\.|P\.J\.E\.|P\.J\.|J\.E\.|JJ\.|J\.)\s*:?\s*$")
_FILED = re.compile(r"^FILED\s*:?\s*(.+?)\s*\.?$", re.I)
# The consolidation divider solomon types between its two boxes.
_TYPED_RULE = re.compile(r"^_{10,}$")

# The left column's furniture: party STATUS and the pivot are closed
# vocabularies; a party NAME is never read by wording.
_STATUS = re.compile(
    r"^(?:Appellants?|Appellees?|Petitioners?|Respondents?|Intervenors?"
    r"|Cross-Appellants?|Cross-Appellees?|Amic(?:us|i)(?:\s+Curiae)?"
    r"|Plaintiffs?|Defendants?)\b[.,]?$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# 'APPEAL OF: K.J.L., MOTHER' — caption apparatus, not a party name, so it
# is kept out of `parties` and `case_name` while still reading as caption.
_DESIGNATION = re.compile(r"^(?:APPEAL OF|APPEAL FROM|OBJECTION OF)\b", re.I)

# --------------------------------------------------------------------------
# the recital — what the court below was and what it called the case
# --------------------------------------------------------------------------

# The tribunals this court hears from, as a closed list.
_BELOW = re.compile(
    r"\b(Court of Common Pleas of [A-Z][A-Za-z’'\- ]*?County"
    r"|Court of Common Pleas"
    r"|Philadelphia Municipal Court)\b")
# The number the court below gave the case is whatever follows its own label.
# The forms this paper prints are wildly various ('CP-52-CR-0000328-2020',
# '0C2004418', '2021-04439-IR', '39 O.A. of 2025', 'FD 17-004053-007',
# '1522-1766', 'O.C. 2022-01946'), so the LABEL is read and the number is
# taken whole rather than pattern-matched.
_BELOW_NO = re.compile(r"\bNos?\(?s?\)?\s*[.:]\s*(\S.*)$")


# THE CRITERIA FIELD NAMES ARE THE MODEL'S — `Criteria` in centralia/model.py
# declares every one of them. A key written under an invented name is
# attached by setattr and never serializes: read as read, reported as
# nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="pasuperct")
def read_headmatter_pasuperct(model, geom, **_):
    """Read the Superior Court's colon-rail docket stack, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 6:
        return NOTHING
    # THE RAIL IS THE DISPATCH. Not the flag beside it, not the masthead —
    # the divider, which is the thing that survives the court changing its
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
    # `box` to the first row that is not a rail row; `recital` only ever
    # directly under a box (or under another recital row); `after` accepts
    # the panel and the byline and nothing else, and the byline stops the
    # reader. A row at no position this paper uses is left to core rather
    # than tinted with a role that would be a guess.
    state = "head"
    box: list = []                  # the rail rows of the box being read
    boxes: list[list] = []          # each box's (left_plain, right_plain)
    first_left: list[str] = []      # the first box's left rows, verbatim
    caption_rows: list[str] = []
    dockets: list[str] = []
    recitals: list[list[str]] = []
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
            if state in ("head", "recital", "after"):
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
                boxes.append((lp, rp))
                if not first_left:
                    first_left = lp
                caption_rows.extend(t for t in lp if t)
                for t in rp:
                    hit = _DOCKET.match(t)
                    if hit:
                        dockets.append(hit.group(1))
                    elif _MASTHEAD.match(t):
                        court_seen = True
            state = "recital"
            recitals.append([])
            continue

        # ---- the head band, above the first box --------------------------
        if state == "head":
            for part in pieces:
                one = _norm(part.plain)
                if _LISTING.match(one):
                    ctx.emit([part], "case-info", centre=False)
                elif _CITATION.match(one):
                    ctx.crit.setdefault("citation", one)
                    ctx.emit([part], "citation", centre=True)
                elif _PUBLICATION.match(one):
                    # THE COURT STATING HOW ITS OWN PAPER MAY BE USED.
                    ctx.crit.setdefault("publication_status", "unpublished")
                    ctx.emit([part], "publication",
                             centre=abs((part.x0 + part.x1) / 2 - axis)
                             <= _AXIS_TOL)
            idx += 1
            continue

        # ---- the consolidation divider the court TYPES between two boxes -
        if _TYPED_RULE.match(text):
            ctx.rule(page1.number, pieces)
            idx += 1
            continue

        # ---- the recital, centred under the box it belongs to ------------
        if state == "recital" and _is_recital(x0, x1, axis, body_x0):
            ctx.emit(pieces, "lower-court", centre=True)
            recitals[-1].append(text)
            idx += 1
            continue
        if state == "recital":
            state = "after"

        # ---- the panel ---------------------------------------------------
        bench = _BEFORE.match(text)
        if state == "after" and bench and not roster:
            ctx.emit(pieces, "panel", centre=False)
            roster.append(_norm(bench.group(1)))
            idx += 1
            # THE ROSTER IS COMPLETE WHEN IT ENDS ON A BENCH TITLE. ramsey
            # sets nine judges over two rows, the first ending on a comma.
            while idx < len(rows) and not _ROSTER_END.search(roster[-1]):
                nxt = sorted(rows[idx], key=lambda l: l.x0)
                one = _norm(" ".join(l.plain for l in nxt))
                if not one or not _ROSTER_END.search(one):
                    break
                ctx.emit(nxt, "panel", centre=False)
                roster.append(one)
                idx += 1
            continue

        # ---- the byline row: its DATE is the headmatter's, the byline is
        # ---- the writing's, and the reader stops here --------------------
        if state == "after" and any(_BYLINE.match(_norm(p.plain))
                                    for p in pieces):
            for part in pieces:
                dated = _FILED.match(_norm(part.plain))
                if dated:
                    ctx.crit.setdefault("decision_date",
                                        _norm(dated.group(1)))
                    ctx.emit([part], "date", centre=False, right=True)
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
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    groups = _party_groups(first_left)
    if len(groups) >= 2:
        # PARTIES ONLY WHERE THE COURT PRINTS THE PIVOT. An adoption or
        # guardianship caption ('IN RE: ADOPTION OF: J.D.L., A MINOR' /
        # 'APPEAL OF: K.J.L., MOTHER') has no two sides, and inventing them
        # from designation rows names the child as a litigant.
        ctx.crit.setdefault("parties", groups[:8])
        ctx.crit.setdefault("case_name", " v. ".join(groups))
    if roster:
        line = _norm(" ".join(roster))
        # THE PRINTED FORM BESIDE THE PARSED FORM. `panel_line` is the row
        # verbatim; `judges` is the roster with the FOOTNOTE MARK the court
        # hangs on a specially-assigned judge taken off it ('STEVENS,
        # P.J.E.*' — a mark is not part of anybody's title).
        ctx.crit.setdefault("judges", re.sub(r"[*†‡]\s*$", "", line).strip())
        ctx.crit.setdefault("panel_line", "BEFORE: " + line)
        names = _panel_names(line)
        if names:
            ctx.crit.setdefault("panel", names)
    flat = [t for seg in recitals for t in seg]
    if flat:
        hist = " ".join(flat)
        ctx.crit.setdefault("history", hist[:2000])
        below = _BELOW.search(hist)
        if below:
            ctx.crit.setdefault("lower_court", below.group(1))
        nos = []
        for seg in recitals:
            hit = _BELOW_NO.search(" ".join(seg))
            if hit:
                nos.append(_norm(hit.group(1)))
        nos = list(dict.fromkeys(nos))
        if nos:
            ctx.crit.setdefault("lower_court_docket", nos)

    # --- the gates: what this contract REQUIRES to have been read ---------
    if not boxes:
        return NOTHING              # no box: not this paper
    if not court_seen:
        return NOTHING              # the right column never named the court
    if "docket_number" not in ctx.crit:
        return NOTHING              # no appeal docket: the box was not read
    ctx.crit["headmatter_style"] = "colon-rail"
    return ctx.result()


# --------------------------------------------------------------------------
# the rail
# --------------------------------------------------------------------------

def _rail(pm) -> float | None:
    """The x of the caption's typed divider on ``pm``, or None.

    A rail is a COLUMN: ':' glyphs stacked at one x, not a count of colons
    anywhere on the page. The x is measured per record because the court
    re-tabs the box per document (318.1-332.5 over the corpus)."""
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
    stands in the rail's own column — which is what a caption row prints and
    a recital row, crossing the same column, does not."""
    return any(_rail_chars(l, rail_x) for l in group)


def _is_recital(x0: float, x1: float, axis: float, body_x0: float) -> bool:
    """Is this row one of the origin recital's? It is CENTRED on the page
    axis to within 6pt and it does not begin at the body rail. Both halves
    are needed: the body's full-measure lines centre on the axis exactly and
    are caught by the rail test, and its indented paragraph openers begin
    inside the measure but centre 18pt right of the axis."""
    return (abs((x0 + x1) / 2 - axis) <= _RECITAL_AXIS_TOL
            and x0 >= body_x0 + _RECITAL_INDENT_MIN)


def _shed_rail(line, rail_x: float):
    """``line`` with the rail's glyphs removed, or None when the line WAS
    the rail. The glyph is identified by its COLUMN, never by its character:
    'IN RE: ADOPTION OF:' and 'at No(s):' print colons elsewhere and keep
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
    'COMMONWEALTH OF PENNSYLVANIA : ' — one line — wholly in the party
    column, which is how core lost that party out of the second box on both
    smith and solomon."""
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
        # row of the box and most of those rows carry no words at all
        # (adoption's first box: nine rail rows, three party rows, three
        # right-hand rows), so padding the columns to a common length would
        # add nothing but blank tinted rows. Each column flows on its own;
        # the true rail height is recorded on the block.
        if l_cells:
            left.append(_cell(l_cells, "caption", pm))
            left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        if r_cells:
            right.append(_cell(r_cells, _right_role(r_cells), pm))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    return left, right, left_plain, right_plain, ids


def _right_role(cells: list) -> str:
    """What the right column is saying on this row. Each of its three
    tenants by its own landmark; over the corpus it carries nothing else,
    so `case-info` is a residual that never fires rather than a catch-all."""
    text = _norm(" ".join(c.plain for c in cells))
    if _MASTHEAD.match(text):
        return "court"
    if _DOCKET.match(text):
        return "docket"
    return "case-info"


# --------------------------------------------------------------------------
# what the box and the recital said
# --------------------------------------------------------------------------

def _panel_names(text: str) -> list[str]:
    """The roster's surnames. The BENCH TITLES are a closed vocabulary; the
    names are whatever stands between them ('FORD ELLIOTT' is one person,
    'McLAUGHLIN' is one, and 'P.J.E.' is nobody). The asterisk the court
    hangs on a specially-assigned judge is a footnote mark, not a name."""
    out = []
    for token in re.split(r",|\band\b", text):
        token = token.strip().strip("*†‡").strip()
        if not token or _BENCH_WORD.match(token):
            continue
        out.append(token)
    return out


def _party_groups(left_plain: list[str]) -> list[str]:
    """The party names of the first docket segment, in printed order, one
    entry per side of the pivot. Statuses, the pivot and the caption's own
    designation lines are dropped; a party name that wraps over rows is
    rejoined. Returns fewer than two groups where the court printed no
    pivot, which is the caller's signal that this caption has no sides."""
    groups: list[list[str]] = [[]]
    seen_pivot = False
    for text in left_plain:
        if not text:
            continue
        if _PIVOT.match(text):
            groups.append([])
            seen_pivot = True
            continue
        if _DESIGNATION.match(text):
            # THE DESIGNATION CLOSES THE PARTY LIST of its segment, and its
            # own WRAP rows are not party names either ('APPEAL OF:
            # GILLILAND VANASDALE' / 'LAW OFFICE, LLC').
            break
        if _STATUS.match(text):
            continue
        groups[-1].append(text)
    if not seen_pivot:
        return []
    # The trailing comma is stripped from the JOINED name, never row by row:
    # 'RICHARD E. PENNESI AND MICHELE' / 'A. PENNESI, HUSBAND AND WIFE;' is
    # one party whose first row ends where the measure ran out.
    out = [_norm(" ".join(g)).rstrip(",;") for g in groups if g]
    return [t for t in out if t]


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

def _tidy(markup: str) -> str:
    """Leading whitespace off a standalone row, INCLUDING whitespace inside
    the opening tag. The court sets 'FILED:' on a tab and pdfio keeps the
    real space glyphs, so the markup arrives as '<strong>        FILED:
    August 11, 2026</strong>'; the render preserves it (`white-space:
    pre-wrap`) and it fights the row's own alignment, which is what carries
    the position. The caption CELLS keep their spacing — there the gap after
    the rail is the page's own column gutter."""
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
    row at its wide gaps, so the row — not the line — is the unit: 'BEFORE: '
    and its roster arrive as two pieces of one row (peay, robinson), and so
    do the byline and the filing date."""
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

    def _line(self, parts: list, role: str, align) -> m.HmLine:
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=_tidy(text.strip()),
            prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def emit(self, group: list, role: str, centre: bool = True,
             right: bool = False) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        align = (m.Align.RIGHT if right else
                 m.Align.CENTER if centre else m.Align.LEFT)
        self.items.append(self._line(parts, role, align))
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

    def rule(self, page: int, parts: list) -> None:
        """The court TYPED a rule between two caption boxes. It is the
        page's own furniture, re-emitted where it stands — a reader that
        claims the block inherits the job of drawing its fences."""
        self.items.append(m.Rule(
            prov=m.Prov(page, tuple(p.id for p in parts)),
            span="full", typed=True))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
