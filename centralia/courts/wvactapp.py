"""Intermediate Court of Appeals of West Virginia ('wvactapp').

Everything unique to wvactapp lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py.

THE COURT PRINTS TWO PAPERS, and they do not agree about where anything
stands. Measured over all 42 records: 26 are MEMORANDUM DECISIONS, whose
caption hangs at the left rail; 16 are TERM SLIPS, whose every row is centred
on the page axis. One reader, dispatched on the row the term slip prints and
the memorandum does not.

    THE MEMORANDUM DECISION (26 records)          the caption at the rail
    ┌────────────────────────────────────────────────────────────────────┐
    │  IN THE INTERMEDIATE COURT OF APPEALS OF WEST VIRGINIA  masthead   │
    │ ACNR RESOURCES, INC.,                      FILED     ┐            │
    │ Employer Below, Petitioner            August 6, 2026 │ the clerk's │
    │ v.) No. 26-ICA-41  (JCN: 2025002712)  ASHLEY N. DEEM,│ stamp, in   │
    │ JARED MCGINNIS,                        CHIEF DEPUTY  │ the MARGIN  │
    │ Claimant Below, Respondent                CLERK …    ┘            │
    │                 MEMORANDUM DECISION            what it is          │
    │ Petitioner ACNR Resources, Inc. appeals …      the writing         │
    └────────────────────────────────────────────────────────────────────┘

    THE TERM SLIP (16 records)                    everything on the axis
    ┌────────────────────────────────────────────────────────────────────┐
    │  IN THE INTERMEDIATE COURT OF APPEALS OF WEST VIRGINIA  masthead   │
    │                    Spring 2026 Term              the term          │
    │              ____________________                typed rules       │
    │                   No. 25-ICA-271                 the docket        │
    │              ____________________                                  │
    │                    CHANDRA T.,                                     │
    │              Respondent Below, Petitioner,       the caption,      │
    │                         v.                       centred           │
    │                    ROBERT M.,                                      │
    │              Petitioner Below, Respondent.                         │
    │ ─────────────────── full-measure rule ──────────────────────────── │
    │        Appeal from the Family Court of Kanawha County              │
    │             Honorable Kelly C. Pritt, Judge      the court below   │
    │            Civil Action No. FC-20-2021-D-56                        │
    │      AFFIRMED, in part, and REMANDED with instructions  what it did│
    │ ─────────────────── full-measure rule ──────────────────────────── │
    │              Submitted: January 14, 2026         the dates         │
    │                Filed: February 9, 2026                             │
    │  Rosalee Juba-Plumley, Esq.  │ Tim C. Carrico, Esq.  counsel, in   │
    │  Counsel for Petitioner      │ Counsel for Respondent  TWO COLUMNS │
    │ CHIEF JUDGE GREEAR delivered the Opinion of the Court.  the writing│
    └────────────────────────────────────────────────────────────────────┘

---- wvactapp's declared facts (measured over all 42 records) --------------

THE MASTHEAD IS THE DISPATCH, and it is the only row above the measure: 15pt
on 36 records and 14pt on 3 against a 13pt paper. Its midpoint sits on the
page axis (306 of 612) on 36 and at 324 on 3. Three records print it nowhere
this reader can see, and it declines on those rather than guess which paper
it is holding.

THE CLERK'S STAMP STANDS IN THE MARGIN, ON THE CAPTION'S OWN ROWS. 'FILED',
the release date, 'released at 3:00 p.m.' and 'ASHLEY N. DEEM, CHIEF DEPUTY
CLERK / INTERMEDIATE COURT OF APPEALS / OF WEST VIRGINIA' are set at x0 400
and beyond — 111 of the 156 stamp pieces bucket at 450 — in 14pt for the
first two and 7pt for the rest. They share printed rows with the party names,
so a row read WHOLE welds the clerk onto the caption: 'ACNR RESOURCES, INC.,
FILED'. Every row here is therefore read PIECE BY PIECE, and the stamp is
recorded as removed rather than dropped in silence.

WHICH PAPER: the term slip prints '<Season> <Year> Term' under the masthead
and the memorandum prints nothing there. That row, not the caption's
position, is the dispatch — position is what it decides, so it cannot also be
what selects.

WHAT CLOSES THE BLOCK differs with the paper, and neither can rely on a
signature: 29 of the 42 records have no byline at their head at all.
  · the memorandum closes on its own title, 'MEMORANDUM DECISION' (26 of 26),
    and the writing opens beneath it;
  · the term slip closes on the announcement, 'CHIEF JUDGE GREEAR delivered
    the Opinion of the Court.' (12) or 'JUDGE WHITE delivered …' (1), which
    the profile's `also_reversed` grammar parses as the author.

THE MEMORANDUM SIGNS AT THE FOOT, not the head: 'CONCURRED IN BY:' over the
judges who joined, on the last page. That is the court's own closing roster
and it stays in the writing where the court put it — a `panel` claim reaching
back into an assembled writing is the one thing a reader here must not do.

THE DOCKET IS AN ICA NUMBER and it does not stand alone: the memorandum sets
it on the PIVOT's row ('v.) No. 26-ICA-41  (JCN: 2025002712)'), with the
Workers' Compensation claim number beside it, and one record runs the docket
and a party name together ('No. 25-ICA-279 – Harvey Bellomy and Nancy
Bellomy'). So the number is matched inside its row, never as a whole row.

COUNSEL IS TWO COLUMNS on the term slip, over a whitespace gutter — 'Counsel
for Petitioner' at x0 108 against 'Counsel for Respondent' at 324/360. It is
emitted as one two-column block, which is what the page prints; a flat list
renders the petitioner's counsel as the respondent's.

THE CRITERIA FIELD NAMES ARE THE MODEL'S — `docket_number`, the claim number
below in `lower_court_docket`, an argued date in `submitted`. Written under
any other name they are attached by setattr and never serialized.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

STYLE_MEMO = "memorandum decision"
STYLE_TERM = "term slip"

_MASTHEAD = re.compile(
    r"^IN THE INTERMEDIATE COURT OF APPEALS OF WEST VIRGINIA$", re.I)
# 15pt on 36 records, 14pt on 3, against a 13pt paper.
_DISPLAY_MIN = 13.8
_MAX_PAGES = 2

# THE CLERK'S STAMP: everything from x0 400 rightward on the cover's own rows.
_STAMP_X0 = 400.0
_STAMP_CUES = re.compile(
    r"^FILED$|^released at\b|CHIEF DEPUTY CLERK|^INTERMEDIATE COURT OF APPEALS$"
    r"|^OF WEST VIRGINIA$|^\w+ \d{1,2}, \d{4}$", re.I)

_STAMP_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$", re.I)
_TERM = re.compile(r"^(?:Spring|Fall|Autumn|Winter|Summer|January|May"
                   r"|September)\s+\d{4}\s+Term$", re.I)
_TYPED_RULE = re.compile(r"^_{5,}$")
_DOCKET = re.compile(r"\bNos?\.\s*(\d{2}-ICA-\d+)", re.I)
_LOWER_NO = re.compile(
    r"\(?\b(?:JCN|BOR)\s*:\s*([\w-]+)\)?|^(?:Civil Action|Case|Action)\s+"
    r"Nos?\.\s*(.+?)\.?$", re.I)
_ORIGIN = re.compile(r"^Appeal from the\b|^On appeal from\b|^Petition for\b",
                     re.I)
_LOWER_JUDGE = re.compile(r"^(?:The )?Honorable\b", re.I)
_PARTY_STATUS = re.compile(
    r"\b(?:Below|Petitioner|Respondent|Appellant|Appellee|Claimant|Employer"
    r"|Plaintiff|Defendant|Intervenor)\b[\s,.]*$", re.I)
_PIVOT = re.compile(r"^v\.?\)?$|^vs\.?$", re.I)
_TITLE = re.compile(r"^MEMORANDUM DECISION$", re.I)
_DISPO = re.compile(
    r"^(?:AFFIRMED|REVERSED|VACATED|DISMISSED|REMANDED|GRANTED|DENIED"
    r"|WRIT|CERTIFIED)\b", re.I)
_DATES = re.compile(r"^(?:Submitted|Filed|Argued|Submitted on briefs)\s*:", re.I)
_COUNSEL_LABEL = re.compile(r"^Counsel for\b|,\s*Esq\.?$|^No appearance\b",
                            re.I)
# 'CHIEF JUDGE GREEAR delivered the Opinion of the Court.'
_ANNOUNCE = re.compile(
    r"^(?:CHIEF JUDGE|JUDGE)\s+[A-Z][A-Za-z'’-]*\s+delivered the Opinion",
    re.I)
# The court's own closing roster, at the FOOT — never claimed.
_CONCURRED = re.compile(r"^CONCURRED IN BY\s*:?$", re.I)


# The dissent's cover leads on its docket and the case name, run together.
_DOCKET_LED = re.compile(r"^Nos?\.\s*\d{2}-ICA-\d+\s*[–—-]\s*\S", re.I)
STYLE_DISSENT = "separate writing"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _read_dissent(rows: list, ctx_cls, body_size: float):
    """The separately published dissent: docket, case name, then the byline.

    Its rows share the clerk's stamp exactly as the other two papers do, so
    the stamp comes off the row first here too.
    """
    if not rows:
        return NOTHING
    ctx = ctx_cls()
    lead = _norm(" ".join(l.plain for l in rows[0]
                          if l.x0 < _STAMP_X0))
    if not _DOCKET_LED.match(lead):
        return NOTHING
    name: list[str] = []
    for group in rows:
        keep, stamp = _split_stamp(group, body_size)
        if stamp:
            for piece in stamp:
                one = _norm(piece.plain)
                if _STAMP_DATE.match(one):
                    ctx.crit.setdefault("decision_date", one)
            ctx.stamp(stamp)
        if not keep:
            continue
        text = _norm(" ".join(l.plain for l in keep))
        if not text:
            continue
        # THE BYLINE ENDS IT: 'WHITE, Judge, dissenting:' opens the writing.
        if re.match(r"^[A-Z][A-Za-z'\u2019-]*,\s*(?:Chief )?Judge",
                    text) and "delivered" not in text:
            break
        docket = _DOCKET.search(text)
        if docket and not ctx.crit.get("docket_number"):
            ctx.crit["docket_number"] = docket.group(1)
            after = text[docket.end():].lstrip(" .\u2013\u2014-")
            if after:
                name.append(after)
            ctx.emit(keep, "docket", centre=False)
            continue
        name.append(text)
        ctx.emit(keep, "caption", centre=False)
    if not ctx.crit.get("docket_number"):
        return NOTHING
    if name:
        ctx.crit["parties"] = [" ".join(name)[:300]]
    ctx.crit["headmatter_style"] = STYLE_DISSENT
    return ctx.result()


def _split_stamp(group: list, body_size: float):
    """The clerk's stamp shares the cover's printed rows, so it comes off the
    row before the row is read."""
    keep, stamp = [], []
    for piece in sorted(group, key=lambda l: l.x0):
        one = _norm(piece.plain)
        if piece.x0 >= _STAMP_X0 and (
                (piece.size or 0.0) < body_size - 1.0
                or _STAMP_CUES.match(one)):
            stamp.append(piece)
        else:
            keep.append(piece)
    return keep, stamp


@decider("headmatter.read", court="wvactapp")
def read_headmatter_wvactapp(model, geom, **_):
    """Read one of the court's two papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = geom.body_size if geom and geom.body_size else 13.0
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _rows(model, finder, _MAX_PAGES)
    if len(rows) < 4:
        return NOTHING

    mast = None
    for idx, group in enumerate(rows[:5]):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD.match(text) and (group[0].size or 0.0) >= _DISPLAY_MIN:
            mast = idx
            break
    if mast is None:
        # THE THIRD PAPER: a separately published dissent, which prints no
        # masthead at all. Its cover is the docket and the case name run
        # together at the rail ('No. 25-ICA-279 – Harvey Bellomy and Nancy
        # Bellomy v. Falcon Ridge Unit Owners' Association, Inc.', wrapping
        # onto a second row), the clerk's stamp in the margin, and then the
        # byline. Three of the 42 records are one of these, and read as
        # nothing at all core took the whole docket row for the docket
        # number.
        return _read_dissent(rows, ctx_cls=_Ctx, body_size=body_size)

    # WHICH PAPER. The term slip names its term; the memorandum names none.
    term_at = next(
        (i for i, g in enumerate(rows[mast + 1:mast + 4], start=mast + 1)
         if _TERM.match(_norm(" ".join(l.plain for l in g)))), None)
    style = STYLE_TERM if term_at is not None else STYLE_MEMO

    ctx = _Ctx()
    parties: list[str] = []
    below: list[str] = []
    counsel: list = []
    axis = page1.width / 2

    for group in rows[mast:]:
        pieces = sorted(group, key=lambda l: l.x0)
        # THE CLERK'S STAMP SHARES THE CAPTION'S ROWS, so it is taken off the
        # row before the row is read at all.
        keep, stamp = _split_stamp(pieces, body_size)
        if stamp:
            # THE FILED DATE IS IN THE STAMP, and on the memorandum it is the
            # only date the cover carries — dropped with the clerk's block it
            # left 26 records with no decision date at all.
            for piece in stamp:
                one = _norm(piece.plain)
                if _STAMP_DATE.match(one):
                    ctx.crit.setdefault("decision_date", one)
            ctx.stamp(stamp)
        if not keep:
            continue
        pieces = keep
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue

        # WHAT CLOSES THE BLOCK — the title on one paper, the announcement on
        # the other. Both are the court's, so both are claimed and the walk
        # ends after them.
        if _TITLE.match(text):
            ctx.emit(pieces, "title")
            break
        if _ANNOUNCE.match(text):
            # NOT CLAIMED. The announcement is the row core opens the writing
            # on — it is this paper's byline, and the profile's `also_reversed`
            # grammar parses it as one. Claimed here it left core no anchor,
            # and the rows above became a phantom `order` ahead of the
            # majority on every term slip. The author is still recovered.
            ctx.crit.setdefault("author_line", text)
            break
        if _CONCURRED.match(text):
            break

        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _TERM.match(text):
            ctx.emit(pieces, "case-info")
            continue
        if _TYPED_RULE.match(text):
            ctx.rule(pieces)
            continue
        docket = _DOCKET.search(text)
        if docket:
            ctx.crit.setdefault("docket_number", docket.group(1))
            for low in _LOWER_NO.finditer(text):
                got = low.group(1) or low.group(2)
                if got:
                    ctx.crit.setdefault("lower_court_docket", []).append(got)
            # The row may carry the pivot and a party name beside the number.
            ctx.emit(pieces, "docket", centre=(style == STYLE_TERM))
            continue
        if _ORIGIN.match(text):
            below.append(text)
            ctx.crit.setdefault("lower_court", text)
            ctx.emit(pieces, "lower-court")
            continue
        if _LOWER_JUDGE.match(text) or _LOWER_NO.match(text):
            below.append(text)
            for low in _LOWER_NO.finditer(text):
                got = low.group(1) or low.group(2)
                if got:
                    ctx.crit.setdefault("lower_court_docket", []).append(got)
            ctx.emit(pieces, "lower-court")
            continue
        if _DISPO.match(text):
            ctx.crit.setdefault("disposition", text)
            ctx.emit(pieces, "disposition")
            continue
        if _DATES.match(text):
            label, _, when = text.partition(":")
            if label.strip().lower() == "filed":
                ctx.crit.setdefault("decision_date", when.strip())
            else:
                ctx.crit.setdefault("submitted", text.strip("."))
            ctx.emit(pieces, "date")
            continue
        if _COUNSEL_LABEL.search(text):
            counsel.extend(pieces)
            continue
        if _PIVOT.match(text) or _PARTY_STATUS.search(text):
            ctx.emit(pieces, "caption", centre=(style == STYLE_TERM))
            continue
        parties.append(text.rstrip(","))
        ctx.emit(pieces, "caption", centre=(style == STYLE_TERM))

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if counsel:
        _pair_counsel(ctx, counsel, axis)
    if parties:
        ctx.crit.setdefault("parties", parties[:8])
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
    ctx.crit["headmatter_style"] = style
    return ctx.result()


def _pair_counsel(ctx, lines: list, axis: float) -> None:
    """The term slip sets counsel in TWO COLUMNS over a whitespace gutter, so
    it is one two-column block: 'Counsel for Petitioner' at x0 108 against
    'Counsel for Respondent' at 324/360. Emitted as a flat list the
    petitioner's counsel reads as the respondent's."""
    rail = min(l.x0 for l in lines)
    seconds = sorted({round(l.x0, 1) for l in lines if l.x0 > rail + 100.0})
    gutter = seconds[0] if seconds else None

    def _row(line):
        return m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role="counsel")

    left = [l for l in lines if gutter is None or l.x0 < gutter - 1.0]
    right = [l for l in lines if gutter is not None and l.x0 >= gutter - 1.0]
    ctx.consumed.update(l.id for l in lines)
    if left and right:
        ctx.items.append(m.CaptionBlock(
            left=[_row(l) for l in left], right=[_row(l) for l in right],
            rail=None, prov=m.Prov(lines[0].page, (lines[0].id,))))
        return
    ctx.items.extend(_row(l) for l in (left or right))


def _rows(model, finder, max_pages: int) -> list[list]:
    groups: dict = {}
    order: list = []
    for pm in model.pages[:max_pages]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip() or finder.kind(pm, line):
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

    def stamp(self, group: list) -> None:
        """The clerk's stamp: recorded as removed, never dropped in silence."""
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=" ".join(" ".join(p.plain.split()) for p in parts)[:200],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind="stamp"))
        self.consumed.update(p.id for p in parts)

    def rule(self, group: list) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
