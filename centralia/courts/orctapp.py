"""Oregon Court of Appeals ('orctapp').

Everything unique to orctapp lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — orctapp is not a slip opinion either. All 42 records are pages
of the OREGON REPORTS ADVANCE SHEETS, the same bound half-measure volume its
Supreme Court is printed in (see or.py, which reads the same paper for a
different court and shares nothing with this file but the physics):

    ┌──────────────────────────────────────────────────────────────────┐
    │ No. 398          May 13, 2026                409  the page head  │
    ├────────────────── DRAWN RULE, top 49.1 ──────────────────────────┤
    │              IN THE COURT OF APPEALS OF THE      the masthead    │
    │                   STATE OF OREGON                                │
    │                                                                  │
    │                  CITY OF EUGENE,                                 │
    │                Plaintiff-Respondent,             the caption,    │
    │                        v.                        centred on the  │
    │              Hamid Michael HEJAZI,               block's own     │
    │               Defendant-Appellant.               axis            │
    │              Lane County Circuit Court                           │
    │               24CR16542, 24CR57085;              the numbers     │
    │      A184491 (Control), A184509, A186553         below, then this│
    │                                                  court's own     │
    │   Jay A. McAlpin, Judge.                         the judge below │
    │   Argued and submitted April 15, 2026.           the dates       │
    │   Kyle Krohn, Deputy Public Defender, argued the cause for       │
    │ appellant. …                                     counsel         │
    │   Before Tookey, Presiding Judge, Kamins, Judge, and             │
    │ Jacquot, Judge.                                  who sat         │
    │   TOOKEY, P. J.                                  the writing     │
    └──────────────────────────────────────────────────────────────────┘

---- orctapp's declared facts (measured over all 42 records) ---------------

THE DRAWN RULE IS THE PAGE'S OWN MEASURE, and it is the only reliable way to
find the axis. Measured on pages 1-3 of every record: 120 rules at top 49.1,
every one 301.5pt wide, x0 alternating 49.5 (72 pages) and 45.0 (71) as the
binding margin changes side each leaf. No record lacks it. So the rule states
the RAIL (its x0), the AXIS (x0 + 150.75) and the foot of the PAGE HEAD
(everything above it). Page width / 2 is the WRONG axis on this paper — the
type block is offset by the binding margin — and used as one it reads every
caption row as an indent.

CENTRED IS A MEASURED FACT AND IT DELIMITS THE CAPTION, with the same catch
or.py records: a JUSTIFIED WRAP fills the measure exactly, so its mid-point
sits on the axis too and width is what separates them. The caption band is
therefore the maximal run of rows within ±4pt of the axis AND under 295pt
wide, opening at the masthead; nothing below that run is read as caption.

THE NUMBERS COME IN TWO SERIES ON ONE ROW. This court's own docket is an
A-number, and the reporter prints the court below's number first, separated
by a semicolon: '24JU05821; A188495 (Control), A188260'. Read as one field
the trial number displaced the appellate one, so the semicolon splits them —
the A-numbers are `docket_number` plus `other_dockets`, and what stands
before the semicolon is `lower_court_docket`. '(Control)' marks the lead
appeal and is kept with the number it labels.

THE LADDER IS READ RUNG BY RUNG, each by its own landmark, because their
order is not stable — 'Before …' prints below the counsel on this court's
records, where its Supreme Court prints 'En Banc' above the origin:

  lower-court  'Lane County Circuit Court' and the like (73 rows)
  lower-judge  'Jay A. McAlpin, Judge.' — a short row ending in the title
               (59 rows). It is the judge BELOW, so it is `lower-court`: a
               `panel` tint here would say this court sat as one judge.
  date         'Argued and submitted April 15, 2026.' (45 rows) -> submitted
  panel        'Before Tookey, Presiding Judge, …' (43 rows)
  counsel      everything else in the ladder, which the reporter sets as
               PROSE paragraphs inside the block rather than as a roster

THE PAGE HEAD IS THE REPORTER'S, NOT THE COURT'S: a folio, the FILING DATE
and the advance sheet's own serial ('No. 398'), three pieces on one printed
row above the rule. Core knows the folio and cannot know the other two, which
are content by every test it has. They are dropped as the head they are and
the date is harvested into `criteria.decision_date`.

THE CITE AND THE SHORT NAME COME OUT OF THE RUNNING HEAD, the only place the
volume prints them — rectos read 'Cite as 349 Or App 409 (2026)', versos
'City of Eugene v. Hejazi'. Both are furniture and neither gets a row, but
'349 Or App 409' is Oregon's public-domain citation for this court and goes
to `criteria.citation`, the short form to `criteria.short_case_name`.

THE BYLINE ENDS THE READER. It is set in the abbreviated form the profile
declares ('EGAN, J.', 'AOYAGI, P. J.', 'LAGESEN, C. J.', 'PER CURIAM'), and
37 records sign on page 1 against 3 on page 2, so the walk is bounded at
three pages. Nothing at or below the byline is claimed — that row is the
anchor core opens the writing on.

THE 8pt APPARATUS IS CORE'S. Under the ladder the reporter types a rule 58.5pt
wide (22 of them across the corpus) and sets the origin's detail beneath it in
8pt. That is a footnote, it lives in core's footnote zone, and the zone is
subtracted from the stream before this reader runs.

THE CRITERIA FIELD NAMES ARE THE MODEL'S — `docket_number` plus
`other_dockets`, the numbers from below in `lower_court_docket`, an argued
date in `submitted`. Written under any other name they are attached by
setattr and never serialized: read as read, reported as nothing.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup

STYLE = "advance sheet"

# ---------------------------------------------------------------------------
# The paper, measured over all 42 records of /assets/orctapp.
# ---------------------------------------------------------------------------
# 120 rules at top 49.1 over pages 1-3, every one 301.5pt wide, x0 49.5 or
# 45.0 as the leaf turns. No record without one.
_RULE_TOP = 49.1
_RULE_TOP_TOL = 2.5
_MEASURE = 301.5
_AXIS_FROM_RAIL = _MEASURE / 2          # 150.75
_AXIS_TOL = 4.0
# A justified wrap is the measure on the nose and shares the axis; a genuinely
# centred row never fills it.
_CENTRED_WIDTH_MAX = 295.0
# The ladder: an opener stands ~15pt in from the rail, a wrap at the rail.
_LADDER_X_MAX = 22.0
# The paper is 11pt (2,288 rows). The reporter's apparatus is 8pt (84) and its
# block quotations 10pt (42); nothing the block prints is under 11pt.
_BODY_SIZE_MIN = 10.5
# 37 records sign on page 1, 3 on page 2.
_MAX_PAGES = 3
# Pieces the page set on ONE printed row: only the head does this (folio,
# date and serial). A justified line never leaves that much between pieces.
_SAME_ROW_SPLIT = 20.0

_MASTHEAD_1 = re.compile(r"^IN THE COURT OF APPEALS OF THE$", re.I)
_MASTHEAD_2 = re.compile(r"^STATE OF OREGON$", re.I)

_HEAD_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
_HEAD_SERIAL = re.compile(r"^No\.\s*\d+$", re.I)
# The running head, on every page but the first.
_CITE_AS = re.compile(r"^Cite as\s+(\d+\s+Or\s+App\s+\d+)\s*\(\d{4}\)\.?$", re.I)

# THIS COURT'S OWN NUMBER is an A-number; '(Control)' labels the lead appeal.
_A_NUMBER = re.compile(r"^A\d{5,6}(?:\s*\(Control\))?$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# The party's position, printed on its own row under the name.
_PARTY_STATUS = re.compile(
    r"^(?:Plaintiff|Defendant|Petitioner|Respondent|Appellant|Appellee"
    r"|Relator|Intervenor|Third-Party Plaintiff|Third-Party Defendant"
    r"|Cross-Appellant|Cross-Respondent|Adverse Party|Youth|Child|Mother"
    r"|Father|Parent|Guardian|Personal Representative)"
    r"[\w\s/-]*[,.]$", re.I)
# The court, board or agency the case came from.
_LOWER_COURT = re.compile(
    r"\b(?:Circuit Court|Tax Court|Justice Court|Municipal Court"
    r"|Juvenile Court|Board of Parole|Employment Relations Board"
    r"|Land Use Board of Appeals|Public Utility Commission"
    r"|Workers.? Compensation Board|Department of\b)", re.I)
# The judge BELOW: a short row that closes on the title.
_LOWER_JUDGE = re.compile(
    r",\s*(?:Judge|Senior Judge|Judge pro tempore|Magistrate"
    r"|Administrative Law Judge)\.$", re.I)
_DATES = re.compile(
    r"^(?:Argued and submitted|Submitted|Argued|Resubmitted|On the record"
    r"|On record|Reargued)\b", re.I)
_PANEL = re.compile(r"^Before\b|^En Banc\b", re.I)
_NO_APPEARANCE = re.compile(r"^No appearance\b", re.I)
# THE BYLINE IS THE SURNAME IN CAPS, and the profile's grammar is not a fine
# enough sieve for this page: 'Rebecca D. Guptill, Judge.' — the judge BELOW,
# printed two rungs above — parses as a byline under it, so the walk ended on
# the trial judge and read her as the author of the opinion (leckenby), while
# the rungs left behind became a phantom `order` writing on 10 records. The
# reporter sets the author's surname in caps over an abbreviated title, and
# the judge below in mixed case over a spelled one; that is the difference.
_BYLINE = re.compile(
    r"^[A-Z][A-Z'’’.\- ]{1,28},\s*(?:C\.\s*J\.|P\.\s*J\.|V\.\s*C\.\s*J\."
    r"|J\.|JJ\.)$")
_PER_CURIAM = re.compile(r"^PER CURIAM\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="orctapp")
def read_headmatter_orctapp(model, geom, **_):
    """Read the advance sheet's block for this court, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]

    # THE RULE STATES THE RAIL AND THE AXIS. Without it there is no axis this
    # reader can trust, so it declines rather than measuring from the paper.
    head_rule = next(
        (r for r in sorted(getattr(page1, "h_rules", []), key=lambda x: x.top)
         if abs(r.top - _RULE_TOP) <= _RULE_TOP_TOL
         and abs((r.x1 - r.x0) - _MEASURE) <= 6.0), None)
    if head_rule is None:
        return NOTHING
    rail = head_rule.x0
    axis = rail + _AXIS_FROM_RAIL

    rows = _rows(model, _MAX_PAGES)
    if len(rows) < 6:
        return NOTHING

    def centred(group) -> bool:
        x0 = min(l.x0 for l in group)
        x1 = max(l.x1 for l in group)
        if abs((x0 + x1) / 2 - axis) > _AXIS_TOL:
            return False
        if (x1 - x0) <= _CENTRED_WIDTH_MAX:
            return True
        # A CENTRED ROW CAN FILL THE MEASURE. Width alone tells a centred row
        # from a justified wrap only while no caption row happens to be the
        # measure wide — and 'BOARD OF PAROLE AND POST-PRISON SUPERVISION,'
        # is 301.5pt on the nose, the measure exactly. Thrown out by width it
        # closed the caption band before the docket row and the whole claim
        # collapsed (lorengel returned NOTHING). The reporter sets party
        # names in CAPS and counsel in mixed case, so case decides where
        # width cannot.
        text = _norm(" ".join(l.plain for l in group))
        letters = [c for c in text if c.isalpha()]
        return bool(letters) and not any(c.islower() for c in letters)

    # THE DISPATCH: the two masthead rows, centred on the axis, below the
    # rule. Never an ordinal — the head above the rule is one printed row on
    # some records and two on others.
    mast = None
    for idx, group in enumerate(rows[:8]):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD_1.match(text) and centred(group):
            nxt = _norm(" ".join(l.plain for l in rows[idx + 1])) \
                if idx + 1 < len(rows) else ""
            if _MASTHEAD_2.match(nxt):
                mast = idx
                break
    if mast is None:
        return NOTHING

    ctx = _Ctx()
    parties: list[str] = []
    below: list[str] = []
    panel: list[str] = []

    # ---- the nonprecedential notice, BELOW the rule and above the masthead
    # 10 of the 42 records print it, always three rows and always the same
    # sentence: 'This is a nonprecedential memorandum opinion pursuant to
    # ORAP 10.30 and may not be cited except as provided in ORAP 10.30(1).'
    # It stands between the page head and the masthead, so neither the head
    # loop nor the caption walk saw it — and left in the stream those three
    # rows opened a PHANTOM `order` writing whose author core then scavenged
    # from the trial judge's row ('Rebecca D. Guptill, Judge.' on leckenby).
    # It is the court saying whether this may be cited, which is what
    # `publication` is.
    notice = [g for g in rows[:mast]
              if g[0].page == 1 and g[0].top > head_rule.top]
    if notice:
        ctx.crit.setdefault("publication_status", "unpublished")
        for group in notice:
            ctx.emit(group, "publication")

    # ---- the page head, above the rule ----------------------------------
    for group in rows[:mast]:
        if group[0].page != 1 or group[0].top >= head_rule.top:
            continue
        for piece in group:
            one = _norm(piece.plain)
            if _HEAD_DATE.match(one):
                ctx.crit.setdefault("decision_date", one)
            ctx.dropped.append(m.Dropped(
                text=one, prov=m.Prov(piece.page, (piece.id,)),
                kind="running-head"))
            ctx.consumed.add(piece.id)

    # ---- the running head on later pages: the cite and the short name ----
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if line.top >= _RULE_TOP + _RULE_TOP_TOL:
                continue
            one = _norm(line.plain)
            cite = _CITE_AS.match(one)
            if cite:
                ctx.crit.setdefault("citation", cite.group(1))
            elif " v. " in one and len(one) < 70 and not one[:1].isdigit():
                ctx.crit.setdefault("short_case_name", one)

    # ---- the caption band, then the ladder ------------------------------
    in_caption = True
    for group in rows[mast:]:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text or (pieces[0].size or 0.0) < _BODY_SIZE_MIN:
            continue
        if pieces[0].page == 1 and pieces[0].top < head_rule.top:
            continue

        # THE BYLINE ENDS THE READER and is never claimed.
        if _BYLINE.match(text) or _PER_CURIAM.match(text):
            break

        if in_caption and centred(group):
            if _MASTHEAD_1.match(text) or _MASTHEAD_2.match(text):
                ctx.crit.setdefault("court", "Court of Appeals of the State "
                                             "of Oregon")
                ctx.emit(pieces, "court")
                continue
            if _numbers_row(text):
                _read_numbers(ctx, text)
                ctx.emit(pieces, "docket")
                continue
            if _LOWER_COURT.search(text):
                below.append(text)
                ctx.crit.setdefault("lower_court", text)
                ctx.emit(pieces, "lower-court")
                continue
            if _PARTY_STATUS.match(text) or _PIVOT.match(text):
                ctx.emit(pieces, "caption")
                continue
            parties.append(text.rstrip(","))
            ctx.emit(pieces, "caption")
            continue
        # A row off the axis, or too wide for it, has left the caption for
        # good — the band is one run and never resumes.
        in_caption = False

        if _PANEL.match(text) or (panel and pieces[0].x0 <= rail + 2.0
                                  and not _DATES.match(text)
                                  and len(panel) == 1):
            panel.append(text)
            ctx.emit(pieces, "panel", centre=False)
            continue
        if _DATES.match(text):
            ctx.crit.setdefault("submitted", text.rstrip("."))
            ctx.emit(pieces, "date", centre=False)
            continue
        if _LOWER_JUDGE.search(text) and len(text) < 70:
            below.append(text)
            ctx.emit(pieces, "lower-court", centre=False)
            continue
        if _LOWER_COURT.search(text) and len(text) < 70:
            below.append(text)
            ctx.crit.setdefault("lower_court", text)
            ctx.emit(pieces, "lower-court", centre=False)
            continue
        # EVERYTHING ELSE IN THE LADDER IS COUNSEL, which this reporter sets
        # as prose paragraphs inside the block and not as a roster.
        ctx.attorney(pieces)

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if parties:
        ctx.crit.setdefault("parties", parties[:8])
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
    if panel:
        ctx.crit.setdefault(
            "judges", re.sub(r"^Before\s+", "", " ".join(panel)).strip(" ."))
    ctx.crit["headmatter_style"] = STYLE
    return ctx.result()


def _numbers_row(text: str) -> bool:
    """Does this centred row carry case numbers — this court's, the court
    below's, or both on one row separated by a semicolon?"""
    head, _, tail = text.rpartition(";")
    return any(_A_NUMBER.match(t.strip())
               for t in re.split(r",", tail or text) if t.strip())


def _read_numbers(ctx, text: str) -> None:
    """'24JU05821; A188495 (Control), A188260' — the trial number, then this
    court's. Read as one field the trial number displaced the appeal."""
    lower, sep, appellate = text.rpartition(";")
    if not sep:
        lower, appellate = "", text
    a_nums = [t.strip(" .") for t in appellate.split(",") if t.strip(" .")]
    if a_nums:
        if not ctx.crit.get("docket_number"):
            ctx.crit["docket_number"] = a_nums[0]
            if a_nums[1:]:
                ctx.crit["other_dockets"] = a_nums[1:]
        else:
            ctx.crit.setdefault("other_dockets", []).extend(a_nums)
    for one in (t.strip(" .") for t in lower.split(",") if t.strip(" .")):
        ctx.crit.setdefault("lower_court_docket", []).append(one)


def _rows(model, max_pages: int) -> list[list]:
    """Printed rows, in reading order, over the pages the block may reach.

    Rows are keyed on the page AND the baseline: two pages share a top, and
    keyed on the top alone page 2's head joined page 1's.
    """
    groups: dict = {}
    order: list = []
    for pm in model.pages[:max_pages]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            key = (pm.number, round(line.top, 1))
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
        self.attorneys: list = []

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

    def attorney(self, group: list) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.attorneys.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role="counsel"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
