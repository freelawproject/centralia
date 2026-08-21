"""Civil Court of the City of New York ('nycivct').

THE PAPER IS NOT THE COURT'S — IT IS THE REPORTER'S. Every record in this
corpus is a New York State Reporter *slip opinion*: the State Reporter takes
the judge's e-filed decision, stamps a machine-generated COVER SHEET on the
front of it, and republishes the two together. Page 1 is that cover; the
decision itself, with its own e-filing furniture and its own caption, starts
on page 2.

    ┌──────────────────────────────────────────────────────────────┐
    │                    Dhansingh v Hager                         │ 38.4 bold
    │                2026 NY Slip Op 31108(U)                      │ 56.2
    │                     March 27, 2026                           │ 74.2
    │      Civil Court of the City of New York, Kings County       │ 92.2
    │       Docket Number: Index No. L&T 324270-25                 │ 110.2
    │                Judge: Logan J. Schiff                        │ 128.2
    │                                                              │
    │  Cases posted with a "30000" identifier, i.e., 2013 NY Slip  │ 146.2 ┐
    │  Op 30001(U), are republished from various New York          │ 159.7 │ 13.5
    │  State and local government sources, including the New       │ 173.2 │ lead
    │  York State Unified Court System's eCourts Service.          │ 186.7 ┘
    │                                                              │       18.0 gap
    │  This opinion is uncorrected and not selected for official   │ 204.7 ┐
    │                       publication.                           │ 218.2 ┘
    │                                                              │
    │  file:///LRB-ALB-FS1/…/Dhansingh_Schiff_kgb.html[03/30/…]    │ 780.8, 9pt
    └──────────────────────────────────────────────────────────────┘

THE COVER IS TYPESET BY MACHINE AND ITS STACK IS INVARIANT. Measured on all
four records of the corpus (2023 and 2026 alike): six 12.0pt rows centred on
the page axis at tops 38.4 / 56.2 / 74.2 / 92.2 / 110.2 / 128.2, to 0.1pt,
the first of them the only bold row on the page. The notice below them sits
at 146.2 / 159.7 / 173.2 / 186.7 / 204.7 / 218.2, again to 0.1pt. Nothing
here is estimated; the rows are read where the reporter's template puts them.

THE LANDMARK IS THE REPORTER'S OWN NUMBER — `2026 NY Slip Op 31108(U)` in the
second row of page 1. That is the thing the State Reporter assigns and the
thing this contract is named for, not the court's name (which changes:
'Civil Court of the CITY of New York' three times, 'Civil Court of the STATE
of New York' once). No slip-op number, no claim: `NOTHING`, and core reads
the record as it would for any court.

THE CAVEAT IS TWO STATEMENTS, AND THE PAGE SEPARATES THEM. The four rows
from 146.2 say where the text came from — a republication provenance, the
reporter's furniture, recorded as `Dropped`. The two rows from 204.7 say
something else entirely: *This opinion is uncorrected and not selected for
official publication.* That is a PUBLICATION STATUS, and it is a fact about
the document, so it is kept as a headmatter row (role `publication`) and
read into `publication_status`. The two statements are told apart by
LEADING, not by wording: 13.5pt within a statement, 18.0pt between them — a
1.33x stand-off, in all four records.

THE COVER NAMES THE JUDGE INSTEAD OF THE JUDGE SIGNING. `Judge: Logan J.
Schiff` is an announcement, not a byline, and the decision on page 2 rarely
carries a byline core can read (`Present: Hon. Logan J. Schiff`,
`FRANCES A. ORTIZ, JUDGE`, `Hon. John A. Howard-Algarin`). It is handed to
core as `announced_author` — the label with its colon removed, so nothing
is invented — and core signs the lead writing with it where the document
prints no byline of its own. Three of the four records are signed this way.
The fourth is not: `Judge: Howard-Algarin` is a HYPHENATED title-case
surname, and the shared grammar's title-case fallback
(`resolve/bylines.py:782`) strips apostrophes but not hyphens before its
`isalpha()` test, where `is_caps_name` two hundred lines above strips both.
That is core's to fix, not this court's to work around.

THE SECOND PAPER MUST BE CLAIMED TOO (revised 2026-08-21). This reader used
to stop at the foot of the cover, on the reasoning that core's shared walk
would place page 2's caption and the writing would keep the rest. IT DOES
NOT: a court reader's items REPLACE the headmatter whole
(`pipeline.py:1564`), so a claim that ends inside the headmatter does not
leave the rest where core had it — it re-classifies it as BODY. On all four
records the decision opened on its own caption, mangled into prose and
blockquotes:

    Blockquote  CIVIL COURT OF THE CITY OF NEW YORK COUNTY OF BRONX: PART 11C
    Blockquote  CREDIT ACCEPTANCE CORPORATION, DECISION AND ORDER Index No. …
    Paragraph   Plaintiff,
    Blockquote  -against-Present: Hon. John A. Howard-Algarin

A partial claim on a two-paper record is worse than no claim at all.

THE DECISION'S CAPTION IS FENCED BY THE PLEADING RULE, and that is what the
reader looks for rather than a shape: a typed rule of dashes, above the
caption and below it. THE CAP IS SOMETIMES A LOWERCASE x — 'the typist's
shift key, not a different object' — and read case-sensitively the fence was
invisible on `credit_acceptance`, whose rules end in 'x'.

    credit_acceptance   2 fences   read      jober_upper_fifth   2 fences  read
    dhansingh           2 fences   read      yumi_acupuncture    0 fences  core's

`yumi_acupuncture` sets its caption as an UNRULED grid, and one sample of
that shape is not a contract: the reader returns NOTHING for that record
whole, cover included, so it reads exactly as it did before. The NYSCEF
stamps, the `[* n]` page marks and the folios stay core's furniture pass.

WHERE THE BENCH STANDS MOVES, so it is read by vocabulary and not position.
`dhansingh` prints 'Present: / Hon. Logan J. Schiff / Judge, Housing Court'
BELOW the closing fence; `credit_acceptance` prints 'Present: / Hon. John A.
Howard-Algarin' INSIDE the caption's right column. Both are the same fact.

THE COURT'S DECLARED FACTS. A Civil Court judge rules alone, so
`single_writing` is True: there is no bench here to concur in or dissent
from, and a record that came back with two writings would have been split,
not read.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from . import register

register(CourtProfile(
    "nycivct", "Civil Court of the City of New York",
    # THE JUDGE IS ANNOUNCED, NEVER SIGNED. The reporter's cover prints
    # 'Judge: Logan J. Schiff' and the decision below it closes without a
    # byline, so the only form this grammar ever has to read is the TITLE
    # THEN THE NAME — the reversed style, with the one title this bench
    # holds. 'Justice' would be wrong here: a Civil Court judge is a Judge.
    # Declared with a single title on purpose: the body sets 'Judge,
    # Housing Court' and 'Hon. …' inside its caption grid, and admitting
    # either as a byline would open a writing in the middle of a caption.
    byline=BylineGrammar(style="reversed", rev_titles=("Judge",),
                         allow_titlecase_name=True),
    single_writing=True,
    rollout="migrated",
))

# ---- the reporter's template, measured ------------------------------------

# Row 2 of the cover. The '(U)' suffix is the reporter's mark for a decision
# published only in the slip-opinion service; a corrected/selected one drops
# it, so the suffix is optional and its presence is not the test.
_SLIPOP = re.compile(r"^\d{4}\s+NY\s+Slip\s+Op\s+\d+\s*(\([A-Z]\))?$", re.I)
_DATE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
_COURT = re.compile(r"\bcourt\b", re.I)
_DOCKET = re.compile(r"^Docket\s+Numbers?:\s*(.+)$", re.I)
# The docket row prints the label the CLERK uses inside the label the
# REPORTER uses: 'Docket Number: Index No. L&T 324270-25'. Both come off.
_INDEX = re.compile(r"^(?:Index|Docket|File|Claim)\s+No\.?s?:?\s*", re.I)
_JUDGE = re.compile(r"^Judges?:\s*(.+)$", re.I)
_PROVENANCE = re.compile(r"^Cases posted with", re.I)
_FILEURL = re.compile(r"^file:///", re.I)

# The cover band: everything the template sets above 240pt on page 1.
_COVER_BOTTOM = 240.0
# The template's own two leadings, 13.5pt within a statement and 18.0pt
# between them. The fence is set between the two, not at either.
_STATEMENT_GAP = 15.5
# The axis tolerance the centred stack needs. The widest cover row runs
# 166.4-444.6, centre 305.5, against a 306.0 axis; 24pt is generous and
# still excludes anything set to a margin.
_AXIS_TOL = 24.0


# ---- page 2: the court's own decision ------------------------------------
# THE PLEADING PAPER'S TYPED FENCE, capped with either case of x.
_TYPED_RULE = re.compile(r"^[·•\s]*(?:[-‐-―=_]{6,}|[-‐-―]{3,}\s*[Xx])"
                         r"[·•\s]*[Xx]?\s*$")
# THE COURT NAMING ITSELF on its own paper, and the part it sits in.
_COURT_ROW = re.compile(r"^(?:CIVIL\s+COURT|COUNTY\s+OF|HOUSING\s+PART"
                        r"|PART\b|At\s+a\s+Term\b)", re.I)
# WHO IS SITTING. 'Present:' spaced out or welded, the honorific, and the
# bench title that follows it.
_PRESENT = re.compile(r"^(?:P\s*R\s*E\s*S\s*E?\s*N?\s*T\s*:?|Hon\.|Judge,)",
                      re.I)
_HON = re.compile(r"\bHon\.?\s+(?P<judge>[A-Z][^,]*?)"
                  r"(?:,\s*(?:J\.?S\.?C\.?|Judge)\b.*)?$", re.I)
# THE RIGHT COLUMN's labelled fields: the index number is the docket, the
# paper's own name is its title, and the bench line is the bench wherever the
# form happens to set it.
_R_INDEX = re.compile(r"^Index\s+No\.?:?\s*(?P<docket>.*)$", re.I)
_R_TITLE = re.compile(r"^(?:POST\s+TRIAL\s+)?DECISION\b", re.I)
# WHERE THE GUTTER FALLS: a share of the sheet, not a fixed rail — this
# court's four records set their right column at 252-391pt on a 612pt page.
_GUTTER = 0.4


def _norm(text: str) -> str:
    return " ".join((text or "").split())


class _Ctx:
    def __init__(self) -> None:
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.announced: str = ""

    def emit(self, line, role: str) -> None:
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.CENTER, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        self.consumed.add(line.id)

    def emit_group(self, group: list, role: str,
                   centre: bool = True) -> None:
        """A whole visual ROW, its cells left to right — the decision's own
        paper sets several cells on one printed line."""
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, lines: list, kind: str) -> None:
        if not lines:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(_norm(l.plain) for l in lines)[:1200],
            prov=m.Prov(lines[0].page, tuple(l.id for l in lines)),
            kind=kind))
        self.consumed.update(l.id for l in lines)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "announced_author": self.announced,
                "anchor_ids": [], "doc_type_final": m.DocType.OPINION}


def _cover_rows(page) -> list:
    """The template's rows: inked, centred on the page axis, above 240pt."""
    axis = page.width / 2.0
    rows = []
    for line in sorted(page.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or line.top >= _COVER_BOTTOM:
            continue
        if abs((line.x0 + line.x1) / 2.0 - axis) > _AXIS_TOL:
            continue
        rows.append(line)
    return rows


@decider("headmatter.read", court="nycivct")
def read_headmatter_nycivct(model, geom, **_):
    """Read the State Reporter's slip-opinion cover sheet, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rows = _cover_rows(page1)
    if len(rows) < 5:
        return NOTHING
    # THE LANDMARK: the reporter's own number, in the template's second row.
    if not any(_SLIPOP.match(_norm(l.plain)) for l in rows[:3]):
        return NOTHING

    ctx = _Ctx()
    # --- the six-row stack -------------------------------------------------
    stack, notice = [], []
    for line in rows:
        (notice if _PROVENANCE.match(_norm(line.plain)) or notice
         else stack).append(line)

    seen_cite = False
    for line in stack:
        text = _norm(line.plain)
        if _SLIPOP.match(text):
            ctx.crit.setdefault("citation", text)
            ctx.emit(line, "citation")
            seen_cite = True
            continue
        if not seen_cite:
            # Everything above the reporter's number is the case name it was
            # assigned to — one bold row in every record of this corpus.
            ctx.crit.setdefault("case_name", text)
            sides = [s.strip() for s in re.split(r"\s+v\.?\s+", text)
                     if s.strip()]
            if len(sides) == 2:
                ctx.crit.setdefault("parties", sides)
            ctx.crit.setdefault("caption", []).append(text)
            ctx.emit(line, "caption")
            continue
        if _DATE.match(text):
            ctx.crit.setdefault("decision_date", text)
            ctx.emit(line, "date")
            continue
        docket = _DOCKET.match(text)
        if docket:
            ctx.crit.setdefault("docket_number",
                                _INDEX.sub("", _norm(docket.group(1))))
            ctx.emit(line, "docket")
            continue
        judge = _JUDGE.match(text)
        if judge:
            name = _norm(judge.group(1))
            ctx.crit.setdefault("judges", name)
            # The label IS the title, so the announcement is handed over as
            # the row reads with its colon removed — nothing invented.
            ctx.announced = f"Judge {name}"

            ctx.emit(line, "author")
            continue
        if _COURT.search(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(line, "court")
            continue
        # A row the template does not print is left to core rather than
        # tinted with a role that would be a guess.
        continue

    # --- the caveat: two statements, told apart by leading -----------------
    if notice:
        groups: list[list] = [[notice[0]]]
        for prev, line in zip(notice, notice[1:]):
            if line.top - prev.top > _STATEMENT_GAP:
                groups.append([line])
            else:
                groups[-1].append(line)
        for group in groups:
            text = _norm(" ".join(l.plain for l in group))
            if _PROVENANCE.match(text):
                # Where the reporter got the text. Furniture.
                ctx.drop(group, "notice")
                continue
            # A REAL PUBLICATION STATUS, kept where the page prints it.
            ctx.crit.setdefault("publication_status", "unpublished")
            for line in group:
                ctx.emit(line, "publication")

    # --- the template's footer --------------------------------------------
    for line in page1.lines:
        if line.id not in ctx.consumed and _FILEURL.match(_norm(line.plain)):
            ctx.drop([line], "furniture")

    if "citation" not in ctx.crit:
        return NOTHING
    # --- the second paper: the decision's own caption ---------------------
    if len(model.pages) < 2 or not _read_decision(ctx, model, model.pages[1]):
        return NOTHING
    return ctx.result()


def _read_decision(ctx, model, pm) -> bool:
    """Page 2's caption, fenced by the pleading rule.

    Returns False where the band cannot be fenced — and the caller then
    withdraws the WHOLE claim, cover included, because a claim that ends
    inside the headmatter turns the rest of it into body."""
    from ..resolve.furniture import FurnitureFinder
    finder = FurnitureFinder(model, 72.0, 12.0)
    rows = _page_rows(pm, finder)
    fence = [i for i, g in enumerate(rows)
             if any(_TYPED_RULE.match(_norm(l.plain)) for l in g)]
    if len(fence) < 2:
        return False
    top, bottom = fence[0], fence[-1]
    if bottom - top < 2:
        return False

    # ---- above the fence: the court, and the bench where it stands there --
    for group in rows[:top]:
        text = _norm(" ".join(l.plain for l in group))
        if _PRESENT.match(text):
            _bench(ctx, group, text)
        elif _COURT_ROW.match(text):
            ctx.emit_group(group, "court")
            ctx.crit.setdefault("court", text)
        else:
            return False        # something stands above the caption

    # ---- the band: parties left, the form's fields right -----------------
    mid = pm.width * _GUTTER
    left: list = []
    right: list = []
    for group in rows[top:bottom + 1]:
        rail = [l for l in group if _TYPED_RULE.match(_norm(l.plain))]
        if rail:
            ctx.drop(rail, "rail")
        cells = [l for l in group if l not in rail]
        if not cells:
            continue
        l_cells = [l for l in cells if l.x0 < mid]
        r_cells = [l for l in cells if l.x0 >= mid]
        left.append(_cells(l_cells, "caption") if l_cells else _blank(pm))
        right.append(_cells(r_cells, _right_role(r_cells)) if r_cells
                     else _blank(pm))
        for cell in r_cells:
            _right_cell(ctx, _norm(cell.plain), [cell])
        ctx.consumed.update(l.id for l in cells)
    if not any(r.text.strip() for r in left):
        return False
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=None,
        prov=m.Prov(pm.number, tuple(
            l.id for g in rows[top:bottom + 1] for l in g))))

    # ---- below the fence: the bench, where this form sets it there -------
    for group in rows[bottom + 1:]:
        text = _norm(" ".join(l.plain for l in group))
        if not _PRESENT.match(text):
            break               # the decision's own words start here
        _bench(ctx, group, text)
    return True


def _bench(ctx, group, text: str) -> None:
    """The bench line, wherever the form sets it. The cover already
    announced the judge, so the name here CORROBORATES and never displaces
    it — `setdefault`, not assignment."""
    ctx.emit_group(group, "author", centre=False)
    hon = _HON.search(text)
    if hon:
        ctx.crit.setdefault("judges", _norm(hon.group("judge")))


def _right_cell(ctx, text: str, cells: list) -> None:
    index = _R_INDEX.match(text)
    if index and index.group("docket"):
        # The index number on the court's own paper. The cover already gave
        # it as 'Docket Number: Index No. …', so the cover's form stands.
        ctx.crit.setdefault("lower_court_docket", []).append(
            _norm(index.group("docket")))
    elif _R_TITLE.match(text):
        ctx.crit.setdefault("title", text)
    elif _PRESENT.match(text):
        hon = _HON.search(text)
        if hon:
            ctx.crit.setdefault("judges", _norm(hon.group("judge")))


def _right_role(cells: list) -> str:
    """What the decision's right column is saying on this row."""
    text = _norm(" ".join(c.plain for c in cells))
    if not text:
        return "caption"
    if _R_INDEX.match(text):
        return "docket"
    if _R_TITLE.match(text):
        return "title"
    if _PRESENT.match(text):
        return "author"
    return "case-info"


def _cells(cells: list, role: str) -> m.HmLine:
    """One side of a band row, every cell of it. EVERY CELL CARRIES A ROLE,
    blanks included — an untagged row is one nothing read."""
    parts = sorted(cells, key=lambda l: l.x0)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    first = parts[0]
    return m.HmLine(
        text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _blank(pm, role: str = "caption") -> m.HmLine:
    return m.HmLine(text="", prov=m.Prov(pm.number), role=role)


def _page_rows(pm, finder) -> list[list]:
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
