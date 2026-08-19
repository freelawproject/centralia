"""Supreme Court of Virginia ('va').

Everything unique to va lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACTS — two papers, and the page names which one it is in its very
first row.

1. THE ANNOUNCED CAPTION (41 of 50). No rule is drawn anywhere on the page.
   The court opens on its sitting roster at the body rail, sets the caption
   in TWO COLUMNS, and — this is the whole point of the paper — ANNOUNCES
   the author of the majority in the caption's right column instead of
   signing the writing:

       PRESENT:  All the Justices                     the roster, at the rail
       DEMEATRIC EUGENE BLOW                 the left column: the parties…
                             OPINION BY      …the right column: the label…
       v.  Record No. 250365                 …the pivot and the docket…
                             JUSTICE JUNIUS P. FULTON, III   …the AUTHOR…
                             APRIL 16, 2026                  …and the date
       COMMONWEALTH OF VIRGINIA              the left column resumes
       FROM THE COURT OF APPEALS OF VIRGINIA   the origin, ON THE PAGE AXIS
       After an undercover officer … — the body, indented 36pt

   THE DIVIDER IS NOT DRAWN, SO THE THRESHOLD IS THE DIVIDER.  va sets no
   rule and no rail glyph anywhere on this page — the gutter is white
   space, and the only measurement that separates the two stacks is where
   a row STARTS.  Every row of the announcement stack starts past
   ``_ANNOUNCE_X0`` (313-415pt over the corpus) and no left-column row
   ever starts past 145pt, a 168pt gutter with nothing in it; the columns
   are read by that x0 and never by wording.  The two stacks are rendered
   as a ``CaptionBlock`` with ``rail=None`` — the whitespace gutter — and
   they are NOT row-paired: on mast the announcement rows sit at
   117.9/131.6/145.5 against parties at 95.1/122.7/136.4/150.3, so each
   stack keeps its own leading and padding the short one would only add
   blank rows.  The block ends at the ORIGIN RECITAL — the first ALL-CAPS
   row below the announcement that is centred on the PAGE AXIS.  Nothing
   else in the caption is:  the announcement stack centres on 414-450,
   the parties on 110-205.  Below it the court may name the judges who
   tried the case (the bar-discipline records: 'Dontae L. Bugg, Chief
   Judge Designate,'), also on the axis and in title case, so the origin
   run continues while a row stays on the axis AND off both the body rail
   (72pt) and the paragraph indent (108pt).  The body is the first row
   that returns to one of those two.

2. THE CONVENING ORDER (9 of 50). The court convenes in writing, and says
   so in a masthead a full step larger than the body:

       VIRGINIA:                                      16.1pt bold
       In the Supreme Court of Virginia held at the Supreme Court Building
       City of Richmond on Thursday, the 12th day of February, 2026.  13.9pt
       Present: All the Justices                      the roster
       WILLIAM ELDRED NORWOOD,          APPELLANT,    the caption, labelled
       against    Record No. 241067                   the pivot and docket
                  Court of Appeals No. 1741-23-3      the docket below
       COMMONWEALTH OF VIRGINIA,         APPELLEE.
                          UPON AN APPEAL FROM A       the origin recital,
                          JUDGMENT RENDERED BY THE    FLUSH RIGHT…
                          COURT OF APPEALS OF VIRGINIA.
       Upon consideration of the record, briefs, …    the body

   …or, where the Court acts on a petition rather than an appeal, the same
   recital set on the axis in one row ('UPON A PETITION UNDER CODE
   § 8.01-670.2.').  Either way it opens 'UPON ' in capitals and leaves the
   left column entirely, and it is the last thing above the body.

THE DISPATCH is the page's first row: a masthead set a step over the body
is the convening order; an 'OPINION BY' row standing in the right column is
the announced caption.  A record printing neither is not this court's paper
and gets NOTHING — core's shared walk is a smaller error than a confident
misreading.

WHY THE ORDER FORM STAYS ONE COLUMN.  Its status labels ARE a second
cell — 'APPELLANT,' at x0=460 beside 'BOARD OF SUPERVISORS OF' at 72 —
but they are row-paired with the party they label and the page prints
them in reading order, so the flat sequence already reads party, status,
pivot, docket, party, status.  Setting them as a second stack would buy
nothing and cost the block a blank cell for every row that carries no
label.  No rail is drawn there either, so there is nothing to reproduce:
one column is the honest reading.  (The origin recital below the caption
is flush right, not a column — it is the last thing above the body.)

WHAT THE READER CANNOT DO ALONE.  On the announced caption the majority
carries NO byline: the author is a caption row, and the caption renders
whole.  Core signs a writing only from a byline left in the stream, so 38
of these 41 records came out with an unauthored majority.  Leaving the
announcement row unclaimed would sign the writing at the cost of tearing
the label ('OPINION BY') away from the name it labels and dropping the
two rows printed BELOW it into the opinion.  So the reader REPORTS what
the caption announced, in ``announced_author``, and core signs the lead
writing from it with the court's own grammar — only where the document
prints no byline of its own.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The grammar is unchanged from the shared registry: 'reversed' reads the
# caption's announcement ('JUSTICE D. ARTHUR KELSEY') and the in-body
# separate writings ('CHIEF JUSTICE POWELL, with whom JUSTICE MANN and
# JUSTICE FULTON join, dissenting.') with the same three titles.
register(CourtProfile(
    "va", "Supreme Court of Virginia",
    byline=BylineGrammar(style="reversed", opinion_by_headings=True,
                         rev_titles=("SENIOR JUSTICE", "CHIEF JUSTICE",
                                     "JUSTICE"),
                         titles=("Justice", "Chief Justice",
                                 "Senior Justice")),
    # PARAGRAPH INDENT. Virginia sets its body at a 72pt rail, opens every
    # paragraph 36pt in (x0=108.0) and insets a block quotation 72pt
    # (x0=144.0) — appian: 808 rows at 72, 127 at 108, 138 at 144. Twice
    # this value is the quotation fence, so it must fall strictly between
    # 36 and 72: at the 12.0 default the fence is 24pt and every ordinary
    # first line reads as a quotation opening (appian lost 8 paragraph
    # breaks that way).
    para_indent_min=24.0,
))

STYLE_ANNOUNCED = "announced caption"
STYLE_CONVENING = "convening order"

# ---- va's declared facts (measured over all 50 records) -----------------
# THE ANNOUNCEMENT COLUMN. 'OPINION BY' starts at 379.6-415.4, the author
# row at 313.4-365.0, the date at 356.9-415.4.  The left column's deepest
# start over the corpus is 144.0 (the order form's 'Record No.' cell) and
# 129.1 on the announced caption (mast's wrapped Court of Appeals numbers).
_ANNOUNCE_X0 = 300.0
# THE PAGE AXIS. Every origin recital on the announced caption centres
# within 0.3pt of 306.0 on a 612pt page; the widest caption row centres at
# 205 and the announcement stack at 414 or beyond.
_AXIS_SLACK = 12.0
# THE CONVENING MASTHEAD: 16.1pt over a 12pt body, with the recital under
# it at 13.9pt.  Nothing on an announced caption exceeds the body size.
_MASTHEAD_SIZE = 15.0
_RECITAL_SIZE = 13.0
# THE ORIGIN RECITAL of the order form is set FLUSH RIGHT to the text
# margin (x1 = 539.4-540.3 against a right_x1 of 537.9) or on the axis.
_FLUSH_RIGHT = 6.0
# THE ROSTER'S OWN WRAP. 'PRESENT: Powell, C.J., … and Millette and Mims,'
# runs over to 'S.JJ.' at the roster's single leading (13.7pt); the caption
# below stands off a full double space (25.7-27.6pt).
_ROSTER_WRAP_MAX = 20.0
# HOW FAR THE BLOCK MAY RUN. Every landmark in the corpus is inside the
# first 20 rows of page 1; a record needing more is not this paper.
_MAX_ROWS = 26
# The rail and the paragraph indent, as the court sets them.
_INDENT = 36.0
_RAIL_SLACK = 1.5
# THE DOCKET CELL is the only thing in the left column set off the party
# rail: 105-144pt against parties at 72-77. Its wrap sits in the same cell.
_DOCKET_CELL = 20.0

_STATUS = re.compile(
    r"^(APPELLANT|APPELLEE|PETITIONER|RESPONDENT|PLAINTIFF|DEFENDANT|"
    r"INTERVENOR|APPELLANTS|APPELLEES|PETITIONERS|RESPONDENTS|"
    r"PLAINTIFFS|DEFENDANTS|INTERVENORS)[,.]?$")
_DOCKET = re.compile(
    r"^(?:v\.\s+|against\s+)?(Record\s+No\.|Court\s+of\s+Appeals\s+Nos?\.|"
    r"Circuit\s+Court\s+No\.)\s*\S", re.IGNORECASE)
_RECORD_NO = re.compile(r"Record\s+No\.\s*([0-9]{6})", re.IGNORECASE)
_LOWER_NO = re.compile(
    r"(?:Court\s+of\s+Appeals|Circuit\s+Court)\s+Nos?\.\s*(.+)$",
    re.IGNORECASE)
_PIVOT = re.compile(r"^(v\.?|vs\.?|against)$", re.IGNORECASE)
_DATE = re.compile(
    r"^(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|"
    r"OCTOBER|NOVEMBER|DECEMBER)\s+\d{1,2},\s+\d{4}\.?$", re.IGNORECASE)
_HELD_DATE = re.compile(
    r"on\s+\w+day,?\s+the\s+(\d{1,2})(?:st|nd|rd|th)\s+day\s+of\s+"
    r"(\w+),?\s+(\d{4})", re.IGNORECASE)
_ROSTER_LABEL = re.compile(r"^PRESENT\s*:", re.IGNORECASE)
_ANNOUNCE_LABEL = re.compile(r"^OPINION\s+BY\s*:?$", re.IGNORECASE)
_CONVENING = re.compile(r"^VIRGINIA\s*:$", re.IGNORECASE)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _ink_x0(line) -> float:
    """Where the row's INK starts, not where its box does.

    A row the column-gap split left with its padding intact ('        Court
    of Appeals Nos. 1855-22-2,' on mast) has an x0 24pt left of its first
    glyph, and the render sets headmatter rows `white-space:pre-wrap` — so
    an indent measured from x0 and the spaces themselves would count the
    same gap twice, and the cell would hang 24pt past where the page puts
    it."""
    xs = [c["x0"] for c in (line.chars or [])
          if (c.get("text") or "").strip()]
    return min(xs) if xs else line.x0


def _is_caps(text: str) -> bool:
    t = _norm(text)
    return bool(t) and t == t.upper() and any(c.isalpha() for c in t)


def _panel_names(line: str) -> list[str]:
    """The surnames in 'Powell, C.J., Kelsey, McCullough, …, JJ., and
    Millette and Mims, S.JJ.' — a bench abbreviation is a role word, never
    a name, and 'All the Justices' names nobody."""
    body = _norm(line)
    body = re.sub(r"^PRESENT\s*:\s*", "", body, flags=re.IGNORECASE)
    if body.lower().startswith("all the justice"):
        return []
    out: list[str] = []
    for tok in re.split(r",|\band\b", body):
        tok = tok.strip().rstrip(".,")
        if not tok or "." in tok or not tok[:1].isupper():
            continue
        if tok.lower() in ("jj", "j", "s", "sjj", "cj"):
            continue
        out.append(tok)
    return out


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model, geom, body_size):
        self.geom = geom
        self.body_size = body_size
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.dropped: list = []

    def _line(self, line, role: str, align: str | None,
              rel: float = 0.0, trim: bool = False) -> m.HmLine:
        # ``align`` DECLARES the column. Measured per row, a right-column
        # cell whose text happens to run wide reads as left-aligned, so the
        # announcement stack came out with 'OPINION BY' right and the two
        # rows under it left — one column rendered as two.
        pm = self.pages[line.page]
        if align is None:
            align = line_alignment(line, pm.width, self.geom,
                                   banner_center_min_size=self.body_size + 2.0)
        text = line_markup(line)
        return m.HmLine(
            text=text.strip() if trim else text,
            prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role, rel=rel)

    def row(self, line, role: str, align: str | None = None,
            rel: float = 0.0):
        self.items.append(self._line(line, role, align, rel))
        self.consumed.add(line.id)

    def cell(self, line, role: str, align: str,
             rel: float = 0.0) -> m.HmLine:
        """A caption cell — built, not emitted: it goes in a CaptionBlock.

        A cell's own padding is not content: the column places it, so the
        text is trimmed and the offset is carried in `rel`."""
        self.consumed.add(line.id)
        return self._line(line, role, align, rel, trim=True)

    def caption(self, page: int, left: list, right: list,
                ids: list) -> None:
        # THE TWO STACKS ARE NOT ROW-PAIRED, and the gutter is white space.
        # va draws no rule and sets no rail glyph, so `rail=None` is the
        # measurement and not a default: the divider is the x0 threshold
        # this file declares. Each column flows on its own leading — the
        # announcement is set on its own axis a half-line off the party
        # rows it stands beside — so pairing them would only pad the short
        # column with blank tinted rows.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=0,
            style_id="whitespace-gutter",
            fp={"rail": None, "gutter_x0": _ANNOUNCE_X0},
            prov=m.Prov(page, tuple(sorted(ids)))))

    def result(self, doc_type=None, announced=None):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": doc_type,
                # WHO THE CAPTION SAYS WROTE IT. Reported, never lifted:
                # the row stays in the headmatter where the page prints it.
                "announced_author": announced}


def _case_name(ctx: _Ctx, rows: list[tuple[str, str]]) -> None:
    """The case's name, built from the party names either side of the pivot
    — never by joining the caption wholesale.

    A CONSOLIDATED caption repeats its own shape: Virginia stacks the cases
    party / pivot / party / party / pivot / party …, so the rows standing
    immediately above the NEXT pivot are the next case's appellant and
    belong to no part of this one. The lead case is the one named."""
    def party(span):
        # A party's STATUS is a role word, never part of its name: the
        # order form labels every side ('APPELLANTS,' / 'RESPONDENTS.').
        return [t.rstrip(",") for r, t in span if r == "caption"
                and not _STATUS.match(_norm(t).rstrip(",."))]

    pivots = [i for i, (_r, t) in enumerate(rows) if _is_pivot_row(t)]
    if not pivots:
        whole = _norm(" ".join(party(rows)))
        if whole:
            ctx.crit["parties"] = [whole.rstrip(",")]
            ctx.crit["case_name"] = whole.rstrip(",")
        return
    first = pivots[0]
    stop = len(rows)
    if len(pivots) > 1:
        stop = max(first + 1, pivots[1] - first)
    left = party(rows[:first])
    right = party(rows[first + 1:stop])
    one = _norm(" ".join(left)).rstrip(",")
    two = _norm(" ".join(right)).rstrip(",")
    if one and two:
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
    elif one or two:
        ctx.crit["parties"] = [one or two]
        ctx.crit["case_name"] = one or two


def _dockets(ctx: _Ctx, rows: list[tuple[str, str]]) -> None:
    """Every 'Record No.' the caption states, and the numbers the court
    below gave the case. A docket CELL may run over ('Court of Appeals
    Nos. 1855-22-2,' / '0876-23-2, 0940-23-2, and 0953-23-2'), and the
    wrap is joined to the row it continues."""
    cells: list[str] = []
    for role, raw in rows:
        row = _norm(raw)
        if role != "docket":
            cells.append("")
            continue
        if cells and cells[-1] and not _DOCKET.match(row):
            cells[-1] = _norm(cells[-1] + " " + row)
        else:
            cells.append(row)
    records: list[str] = []
    lower: list[str] = []
    for cell in cells:
        for mm in _RECORD_NO.finditer(cell):
            if mm.group(1) not in records:
                records.append(mm.group(1))
        lm = _LOWER_NO.search(cell)
        if lm:
            lower.append(_norm(lm.group(1)).rstrip(","))
    if records:
        ctx.crit["docket_number"] = f"Record No. {records[0]}"
        if records[1:]:
            ctx.crit["other_dockets"] = [f"Record No. {r}"
                                         for r in records[1:]]
    if lower:
        ctx.crit["lower_court_docket"] = lower


def _origin_criterion(ctx: _Ctx, rows: list[str]) -> None:
    """Where the matter came from, or what it came ON.

    Virginia closes its caption with one of two recitals, and they say
    different things. 'FROM THE COURT OF APPEALS OF VIRGINIA', 'UPON AN
    APPEAL FROM A JUDGMENT RENDERED BY …' and 'UPON A QUESTION OF LAW
    CERTIFIED BY …' all name a court below. 'UPON A PETITION FOR A WRIT OF
    ACTUAL INNOCENCE' and 'UPON A MOTION TO CLARIFY ORDER' name none —
    they are the Court's own original jurisdiction, and filing them as a
    lower court would invent one."""
    text = _norm(" ".join(rows)).rstrip(".")
    if not text:
        return
    ctx.crit["lower_court" if _names_a_court(text) else "motion"] = text


def _names_a_court(text: str) -> bool:
    up = text.upper()
    return (up.startswith("FROM ") or "APPEAL FROM" in up
            or "CERTIFIED BY" in up)


def _is_pivot_row(text: str) -> bool:
    """The caption's pivot: 'v.' or 'against', alone or heading the docket
    cell the court sets on the same row ('v.  Record No. 250365')."""
    row = _norm(text)
    if _PIVOT.match(row):
        return True
    parts = row.split()
    return bool(parts and _PIVOT.match(parts[0]) and _DOCKET.match(row))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="va")
def read_headmatter_va(model, geom, **_):
    """Read va's announced caption or its convening order, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    width = pm.width or 612.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = [l for l in pm.lines
            if l.plain.strip() and not finder.kind(pm, l)]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not rows:
        return NOTHING
    rows = rows[:_MAX_ROWS]

    if _CONVENING.match(_norm(rows[0].plain)) \
            and (rows[0].size or 0) >= _MASTHEAD_SIZE:
        return _read_order(model, geom, pm, rows, body_x0, body_size, width)
    return _read_announced(model, geom, pm, rows, body_x0, body_size, width)


def _on_axis(line, width: float) -> bool:
    return abs((line.x0 + line.x1) / 2.0 - width / 2.0) <= _AXIS_SLACK


def _at_rail(line, body_x0: float) -> bool:
    return (abs(line.x0 - body_x0) <= _RAIL_SLACK
            or abs(line.x0 - (body_x0 + _INDENT)) <= _RAIL_SLACK)


def _read_announced(model, geom, pm, rows, body_x0, body_size, width):
    """Contract 1 — the roster, the two-column caption, the axis origin."""
    ann = next((i for i, l in enumerate(rows)
                if _ink_x0(l) >= _ANNOUNCE_X0
                and _ANNOUNCE_LABEL.match(_norm(l.plain))), None)
    if ann is None:
        return NOTHING                    # no announcement: not this paper
    if not _ROSTER_LABEL.match(_norm(rows[0].plain)):
        return NOTHING                    # the roster always opens the page
    origin = next((i for i in range(ann + 1, len(rows))
                   if _is_caps(rows[i].plain) and _on_axis(rows[i], width)
                   and not _at_rail(rows[i], body_x0)), None)
    if origin is None:
        return NOTHING                    # nothing closes the caption

    ctx = _Ctx(model, geom, body_size)
    ctx.crit["headmatter_style"] = STYLE_ANNOUNCED

    # ---- the roster, and only its own wrap ------------------------------
    ctx.row(rows[0], "panel")
    roster = [_norm(rows[0].plain)]
    head = 1
    while (head < ann and rows[head].x0 <= body_x0 + _RAIL_SLACK
           and rows[head].top - rows[head - 1].top <= _ROSTER_WRAP_MAX):
        ctx.row(rows[head], "panel")
        roster.append(_norm(rows[head].plain))
        head += 1
    ctx.crit["panel_line"] = _norm(" ".join(roster))
    names = _panel_names(" ".join(roster))
    if names:
        ctx.crit["panel"] = names

    # ---- the caption: left column the parties, right the announcement ---
    # WHICH COLUMN a row is in is decided by where it starts, never by what
    # it says. Inside the left column the DOCKET CELL is the one thing set
    # off the party rail, and its wrap goes with it. The two columns go out
    # as ONE CaptionBlock: emitted as a flat sequence they interleave, and
    # a consolidated caption reads its cases out of order (antle came out
    # party / pivot / party / OPINION BY / author / party / date / pivot).
    # WHERE THE INK STARTS, not where the box does: the column-gap split
    # leaves a piece its padding, so mast's docket cell has an x0 24pt left
    # of its first glyph. Read on the box, a padded right-hand piece would
    # fall on the wrong side of the threshold that IS the divider.
    band = rows[head:origin]
    l_rows = [l for l in band if _ink_x0(l) < _ANNOUNCE_X0]
    r_rows = [l for l in band if _ink_x0(l) >= _ANNOUNCE_X0]
    # THE LEFT COLUMN'S OWN RAIL, measured inside the band. The docket cell
    # is the one thing set off it (mast: 129.1 against a 72.0 party rail),
    # and inside a column that offset is the cell's own indent — carried as
    # `rel` so the cell renders where the page prints it.
    own_x0 = min((_ink_x0(l) for l in l_rows), default=body_x0)
    left_cells: list = []
    right_cells: list = []
    left: list[tuple[str, str]] = []
    announced: str | None = None
    for line in r_rows:
        text = _norm(line.plain)
        # ONE COLUMN, so one alignment — declared, not measured per row.
        # The announcement stack is centred on its OWN axis (414.0-414.3 on
        # appian, 441.2-441.4 on blow, within 0.3pt inside a record), which
        # is what the right cell of the block centres on.
        if _ANNOUNCE_LABEL.match(text):
            right_cells.append(ctx.cell(line, "title", "C"))
        elif _DATE.match(text):
            ctx.crit.setdefault("decision_date", text.rstrip("."))
            right_cells.append(ctx.cell(line, "date", "C"))
        else:
            # THE ANNOUNCED AUTHOR — not the panel. va prints a real
            # roster row ('PRESENT: …') at the head of the same block,
            # and tagging both `panel` made the author and the bench
            # indistinguishable.
            ctx.crit.setdefault("judges", text)
            if announced is None:
                announced = text
            right_cells.append(ctx.cell(line, "author", "C"))
    for line in l_rows:
        text = _norm(line.plain)
        x0 = _ink_x0(line)
        off_rail = x0 >= own_x0 + _DOCKET_CELL
        role = "docket" if (_DOCKET.search(text) or off_rail) else "caption"
        left_cells.append(ctx.cell(line, role, "L",
                                   rel=x0 - own_x0 if off_rail else 0.0))
        left.append((role, text))
    ctx.caption(pm.number, left_cells, right_cells, [l.id for l in band])
    _case_name(ctx, left)
    _dockets(ctx, left)
    ctx.crit["caption"] = _norm(" ".join(t for _r, t in left))[:2000]

    # ---- the origin: the axis run, capitals then the trial bench --------
    # The run holds up to two things and they are told apart by case: the
    # recital is in capitals, the judges who tried it are not.
    court_rows: list[str] = []
    judge_rows: list[str] = []
    i = origin
    while i < len(rows):
        line = rows[i]
        if not _on_axis(line, width) or _at_rail(line, body_x0):
            break
        text = _norm(line.plain)
        (court_rows if _is_caps(text) else judge_rows).append(text)
        i += 1
    names = _names_a_court(" ".join(court_rows))
    for line in rows[origin:i]:
        ctx.row(line, "lower-court" if names or not _is_caps(line.plain)
                else "case-info")
    _origin_criterion(ctx, court_rows)
    if judge_rows:
        ctx.crit["lower_court_judge"] = _norm(" ".join(judge_rows))
    return ctx.result(m.DocType.OPINION, announced)


def _read_order(model, geom, pm, rows, body_x0, body_size, width):
    """Contract 2 — the convening recital, the labelled caption, 'UPON …'."""
    origin = next((i for i, l in enumerate(rows)
                   if _is_caps(l.plain)
                   and _norm(l.plain).upper().startswith("UPON ")
                   and not _at_rail(l, body_x0)), None)
    if origin is None:
        return NOTHING                    # nothing closes the caption

    ctx = _Ctx(model, geom, body_size)
    ctx.crit["headmatter_style"] = STYLE_CONVENING
    ctx.crit["court"] = "Supreme Court of Virginia"

    # ---- the masthead and the convening recital -------------------------
    head = 0
    while head < origin and (rows[head].size or 0) >= _RECITAL_SIZE:
        text = _norm(rows[head].plain)
        ctx.row(rows[head], "court")
        dm = _HELD_DATE.search(text)
        if dm and "decision_date" not in ctx.crit:
            ctx.crit["decision_date"] = \
                f"{dm.group(2).title()} {int(dm.group(1))}, {dm.group(3)}"
        head += 1
    if head == 0:
        return NOTHING                    # the order always convenes itself

    # ---- the roster -----------------------------------------------------
    if head < origin and _ROSTER_LABEL.match(_norm(rows[head].plain)):
        ctx.row(rows[head], "panel")
        ctx.crit["panel_line"] = _norm(rows[head].plain)
        names = _panel_names(rows[head].plain)
        if names:
            ctx.crit["panel"] = names
        head += 1

    # ---- the caption ----------------------------------------------------
    # ONE COLUMN, WITH A FLUSH-RIGHT STATUS CELL. The order form sets its
    # party rows at the rail, its docket cell 72pt in (144.0 against 72.0)
    # and the side's status hard against the text margin ('APPELLANT,' at
    # 460.3-538.7 on a 537.9 margin) — so the status is a CELL of the party
    # row, not a stack of its own, and the page prints the two in reading
    # order (party, status, pivot, docket, party, status). It stays one
    # column for that reason: a second stack would hold two cells against
    # five and would have to be padded with a blank for every row that
    # carries no label. What the column DOES get is a declared alignment —
    # measured per row it came out left for 'APPELLANT,' and right for
    # 'APPELLEE.', one column rendered as two — and the docket cell keeps
    # its own indent.
    left: list[tuple[str, str]] = []
    own_x0 = min((_ink_x0(l) for l in rows[head:origin]
                  if _ink_x0(l) < _ANNOUNCE_X0), default=body_x0)
    for line in rows[head:origin]:
        text = _norm(line.plain)
        role = "docket" if _DOCKET.match(text) else "caption"
        x0 = _ink_x0(line)
        if x0 >= _ANNOUNCE_X0:
            ctx.row(line, role, align="R")
        else:
            off = x0 >= own_x0 + _DOCKET_CELL
            ctx.row(line, role, align="L", rel=x0 - own_x0 if off else 0.0)
        left.append((role, text))
    _case_name(ctx, left)
    _dockets(ctx, left)
    ctx.crit["caption"] = _norm(" ".join(t for _r, t in left))[:2000]

    # ---- the origin recital: flush right, or on the axis -----------------
    court_rows: list[str] = []
    right_x1 = (geom.right_x1 if geom else 538.0)
    i = origin
    while i < len(rows):
        line = rows[i]
        if _at_rail(line, body_x0) or not _is_caps(line.plain):
            break
        if not (_on_axis(line, width)
                or line.x1 >= right_x1 - _FLUSH_RIGHT
                or line.x0 >= _ANNOUNCE_X0):
            break
        court_rows.append(_norm(line.plain))
        i += 1
    names = _names_a_court(" ".join(court_rows))
    # ONE RECITAL, ONE ALIGNMENT. Its three rows are set flush right
    # (x1 = 540.1-540.3 against a 537.9 margin) and ragged left, so
    # measured per row the first read right and the two under it left.
    flush = bool(rows[origin:i]) and all(
        l.x1 >= right_x1 - _FLUSH_RIGHT for l in rows[origin:i])
    for line in rows[origin:i]:
        ctx.row(line, "lower-court" if names else "case-info",
                align="R" if flush else None)
    _origin_criterion(ctx, court_rows)
    return ctx.result(m.DocType.ORDER)
