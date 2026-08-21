"""Maine Supreme Judicial Court ('me').

Everything unique to me lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — Maine LABELS ITS OWN HEADMATTER. It is the friendliest paper
in the corpus: the court prints a two-column ladder in which the left
column NAMES the row and the right column carries its value.

    ┌────────────────────────────────────────────────────────────────────┐
    │ MAINE SUPREME JUDICIAL COURT                  Reporter of Decisions│
    │ Decision:   2026 ME 14                                             │
    │ Docket:     Som-25-258                                             │
    │ Argued:     December 10, 2025                                      │
    │ Decided:    February 19, 2026                                      │
    │ Panel:      STANFILL, C.J., and MEAD, CONNORS, LAWRENCE, and …     │
    │                                                                    │
    │                   ADOPTION BY KATHLEEN C.            the caption   │
    │                                                                    │
    │ DOUGLAS, J.                                          the writing   │
    └────────────────────────────────────────────────────────────────────┘

THE LABEL IS THE LANDMARK, and it is read from the label column alone — the
LADDER, not an ordinal. Measured over 50 records the court prints these
labels: Decision, Docket, Argued, Submitted On Briefs, Decided, Panel,
Reporter, Majority, Dissent, Concurrence. A record that omits Argued (most
are submitted on briefs instead) still reads, and one that adds a Dissent
line reads that too, because nothing is indexed off a row NUMBER.

THE TYPE SEPARATES THE BLOCK FROM THE PAPER. The ladder is set at 11pt and
the opinion at 14pt. The caption between them is 14pt but CENTRED, and the
body is not — so the caption is the centred 14pt run above the first row
that opens at the body rail, which is the byline.

WHAT MAINE DOES NOT PRINT HERE: the appearances. Counsel is set at the END
of the paper, below the writings, and core's trailing-roster pass finds it
there; this reader does not claim it.

'Reporter of Decisions' is not a role — it is the label of the column the
Reporter's own apparatus stands in, and it is read as `case-info` rather
than tinted with a role it does not have.

THE COURT PRINTS TWO PAPERS. The ladder above is one of them. The other is
an Opinion of the Justices — the advisory answer Article VI, section 3 lets
the Legislature or the Governor ask for — and it carries no ladder at all:
a cover page, the neutral cite alone at the rail over a centred display
block. `_read_cover` reads that one, and the ladder reader hands off to it
when the masthead is not there to dispatch on.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import roster_names

_MASTHEAD = "maine supreme judicial court"
_MAX_PAGES = 2
# The ladder's type against the paper's. Measured: 11pt block, 14pt body on
# every record in the corpus.
_LADDER_SIZE_MAX = 12.5
_AXIS_TOL = 8.0
# The label column stands at the body rail; the value column at 135-144.
_LABEL_MAX_X0 = 80.0
_VALUE_MIN_X0 = 120.0

# WHAT EACH LABEL NAMES. The vocabulary is the court's own, measured over
# all 50 records; the value's role is looked up here and nowhere else.
_LABELS = {
    "decision": "citation",          # '2026 ME 14' — the public-domain cite
    "docket": "docket",
    "argued": "date",
    "submitted on briefs": "date",
    "submitted": "date",
    "decided": "date",
    "panel": "panel",
    "reporter": "case-info",
    "majority": "author",
    "dissent": "author",
    "dissenting": "author",
    "concurrence": "author",
    "concurring": "author",
    "amended": "date",
    "corrected": "date",
}
# The criteria a label fills, where the criterion exists.
_CRIT = {"decision": "citation", "docket": "docket_number",
         "decided": "decision_date", "argued": "submitted",
         "submitted on briefs": "submitted", "submitted": "submitted"}
_REPORTER_COL = re.compile(r"^Reporter of Decisions$", re.I)
_BYLINE = re.compile(
    r"^[A-Z][A-Za-z'’\-]+(?:,\s*[A-Z][A-Za-z'’\-]+)*,\s*"
    r"(?:C\.?\s*J\.?|J\.?|JJ\.?)\s*$")

# THE COVER of an Opinion of the Justices. See `_read_cover`.
_NEUTRAL_CITE = re.compile(r"^\d{4}\s+ME\s+\d+$")
_COVER_TITLE = "OPINION OF THE JUSTICES"
_COVER_DOCKET = re.compile(r"^Docket\s+No\.\s+(\S+)\s*$", re.I)
_COVER_DATE = re.compile(
    r"^(ARGUED|SUBMITTED|ANSWERED|DECIDED)\s+(.+?)\s*$", re.I)
# 'ANSWERED' is this paper's word for DECIDED; the rest mean what they mean
# in the ladder.
_COVER_CRIT = {"argued": "submitted", "submitted": "submitted",
               "answered": "decision_date", "decided": "decision_date"}
# The cover's leading, measured on opinion_of_the_justices_ranked-choice
# _voting: 16.3-16.5pt inside one element, 32.7-32.9pt between elements — an
# exact double. Anything over 1.5x the tightest gap on the sheet is a new
# element.
_ELEMENT_GAP = 1.5


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="me")
def read_headmatter_me(model, geom, **_):
    """Read Maine's labelled ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 4:
        return NOTHING
    # THE DISPATCH: the court names itself in the first row of the ladder,
    # at the label column, in ladder type. Where it does not, the sheet is
    # the court's OTHER paper and the cover reader answers for it.
    head = rows[0]
    if _norm(" ".join(l.plain for l in head)).lower().split("reporter")[0]\
            .strip() != _MASTHEAD:
        return _read_cover(rows, page1, body_x0)

    ctx = _Ctx()
    ladder_done = False
    pending: str | None = None
    caption: list[str] = []
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        size = first.size or 0.0

        if not ladder_done and size <= _LADDER_SIZE_MAX:
            # THE MASTHEAD ROW carries the Reporter's column label beside
            # it; they are two elements the page set on one line.
            if text.lower().startswith(_MASTHEAD):
                for piece in pieces:
                    one = _norm(piece.plain)
                    if not one:
                        continue
                    if _REPORTER_COL.match(one):
                        ctx.emit([piece], "case-info")
                    else:
                        ctx.crit.setdefault("court", one)
                        ctx.emit([piece], "court")
                continue
            # A LABEL SET OVER TWO ROWS. 'Submitted' stands alone at the
            # rail, with no colon and no value, and its tail, its colon and
            # its value are all on the row below ('On Briefs:  October 29,
            # 2025' — one run at x0 81.0, no value column to split at).
            # Read as two independent rows the first inherited the role
            # above it (the DOCKET) and the date the pair names was never
            # recorded: `submitted` was empty on all 8 records that print
            # it. The two halves are one element and the label is the join.
            if pending is None and len(pieces) == 1 \
                    and first.x0 <= _LABEL_MAX_X0 \
                    and not text.endswith(":") and text.lower() in _LABELS:
                pending = text.lower()
                ctx.emit(pieces, _LABELS[pending], centre=False)
                continue
            if pending is not None:
                tail, sep, rest = text.partition(":")
                if sep:
                    key = _norm(f"{pending} {tail}").lower()
                    ctx.emit(pieces, _LABELS.get(key, _LABELS[pending]),
                             centre=False)
                    crit = _CRIT.get(key) or _CRIT.get(pending)
                    if crit and rest.strip():
                        ctx.crit.setdefault(crit, _norm(rest))
                    pending = None
                    continue
                pending = None
            label, value = _split_ladder(pieces)
            if label is not None:
                key = _norm(label.plain).rstrip(":").lower()
                role = _LABELS.get(key)
                if role is None:
                    # AN UNKNOWN LABEL IS STILL A LABELLED ROW, and reading
                    # it as `case-info` says less than guessing at it: the
                    # court's vocabulary is open (it adds 'Amended' and
                    # 'Corrected' lines) and a wrong role is invisible.
                    role = "case-info"
                ctx.emit(pieces, role, centre=False)
                crit = _CRIT.get(key)
                if crit and value:
                    ctx.crit.setdefault(crit, _norm(value))
                # THE BENCH IS A CRITERION, not just a tint. The 'Panel:'
                # row prints on 48 of the 50 records and was READ on all of
                # them — tinted `panel`, placed in the right order — while
                # `judges`, `panel` and `panel_line` stayed empty on every
                # one, because a role is not a value. Split by core's own
                # roster rule so this court's list reads like every other
                # court's.
                if key == "panel" and value:
                    ctx.crit.setdefault("judges", _norm(value))
                    ctx.crit.setdefault("panel_line", _norm(value))
                    ctx.crit.setdefault("panel", roster_names(_norm(value)))
                continue
            # A ladder row with no label is the runover of the one above it.
            if ctx.items:
                ctx.emit(pieces, getattr(ctx.items[-1], "role", "case-info"),
                         centre=False)
                continue
            continue

        ladder_done = True
        # THE BYLINE ENDS THE READER. Maine signs its writings name-first at
        # the body rail, and that row is the paper, not the block.
        if abs(first.x0 - body_x0) <= 2.0 and _BYLINE.match(text):
            break
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - page1.width / 2) <= _AXIS_TOL
        if centred:
            caption.append(text)
            ctx.emit(pieces, "caption")
            continue
        # A row at the rail in paper type, before any byline, is the paper
        # opening — leave it to core.
        break

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("case_name", " ".join(caption))
        ctx.crit.setdefault("parties", caption)
    return ctx.result()


# --------------------------------------------------------------------------
# the court's other paper: an Opinion of the Justices
# --------------------------------------------------------------------------
# An advisory opinion is not an opinion in a case. Article VI, section 3 of
# the Maine Constitution lets the Legislature or the Governor put a question
# of law to the Justices INDIVIDUALLY, and the answer is printed as its own
# paper: no masthead, no ladder, no parties, no byline — a COVER, and page 1
# carries nothing but the cover (243 ink characters on the sheet).
#
#     2026 ME 32                                      <- alone at the rail
#
#                    OPINION OF THE JUSTICES           <- what the paper is
#                 OF THE SUPREME JUDICIAL COURT
#
#                 GIVEN UNDER THE PROVISIONS OF        <- the authority it
#       ARTICLE VI, SECTION 3 OF THE MAINE CONSTITUTION      is given under
#
#                      Docket No. OJ-26-1
#
#                    QUESTIONS PROPOUNDED BY           <- who asked, and in
#                    THE MAINE LEGISLATURE                what instrument
#                       IN A JOINT ORDER
#                    DATED FEBRUARY 10, 2026
#                     ARGUED APRIL 1, 2026             <- argued
#                    ANSWERED APRIL 6, 2026            <- decided
#
# Unread, every one of those rows was the opening of the MAJORITY: the whole
# cover rendered as the first paragraphs of the writing, the record carried
# no docket, no date, no citation and no case name, and its one headmatter
# row was core's fallback holding the cite alone (the user, 2026-08-20).
#
# THE LEADING GROUPS IT, and the grouping is the only thing that says where
# the title ends — 16.3-16.5pt inside an element against 32.7-32.9pt between
# them, an exact double. So the title is the run TIGHT TO the title row, not
# a fixed two rows.
#
# WHAT THIS COVER DOES NOT PRINT: a panel. The Justices sign the answer at
# the END, each name over its own '/s/', and core's signature pass reads it
# there — as it reads the appearances, which stand below the signatures.
# Nor does it name the court in a form worth recording: 'OF THE SUPREME
# JUDICIAL COURT' is half a title, not a masthead, so `court` is left unset
# rather than filled with a fragment.


def _read_cover(rows: list, page1, body_x0: float):
    """Read the cover of an Opinion of the Justices, or NOTHING."""
    groups = [sorted(g, key=lambda l: l.x0) for g in rows]
    texts = [_norm(" ".join(l.plain for l in g)) for g in groups]
    if _COVER_TITLE not in texts:
        return NOTHING
    # THE CITE OPENS IT, alone at the rail. It is the one row of the cover
    # that is not on the axis, and the only landmark that says the block
    # starts here rather than somewhere down the sheet.
    if not _NEUTRAL_CITE.match(texts[0]) \
            or abs(groups[0][0].x0 - body_x0) > 2.0:
        return NOTHING
    # EVERYTHING BELOW THE CITE STANDS ON THE PAGE'S AXIS. A cover is a
    # display block; a row at the rail under it would be the paper opening,
    # and this reader would have no business claiming it.
    for group in groups[1:]:
        mid = (group[0].x0 + max(l.x1 for l in group)) / 2
        if abs(mid - page1.width / 2) > _AXIS_TOL:
            return NOTHING

    tops = [g[0].top for g in groups[1:]]
    gaps = [b - a for a, b in zip(tops, tops[1:])]
    tight = min(gaps) if gaps else 0.0
    title_at = texts.index(_COVER_TITLE)
    title_last = title_at
    while title_last - 1 < len(gaps) \
            and gaps[title_last - 1] <= tight * _ELEMENT_GAP:
        title_last += 1

    ctx = _Ctx()
    ctx.emit(groups[0], "citation", centre=False)
    ctx.crit["citation"] = texts[0]
    for idx, group in enumerate(groups):
        if idx == 0:
            continue
        text = texts[idx]
        if title_at <= idx <= title_last:
            ctx.emit(group, "title")
            continue
        docket = _COVER_DOCKET.match(text)
        if docket:
            ctx.emit(group, "docket")
            ctx.crit.setdefault("docket_number", docket.group(1))
            continue
        dated = _COVER_DATE.match(text)
        if dated:
            ctx.emit(group, "date")
            crit = _COVER_CRIT.get(dated.group(1).lower())
            if crit:
                ctx.crit.setdefault(crit, _norm(dated.group(2)))
            continue
        # The authority, and who propounded the questions in what
        # instrument. Named apparatus with no role of its own.
        ctx.emit(group, "case-info")
    if not ctx.crit.get("docket_number"):
        return NOTHING
    name = " ".join(texts[title_at:title_last + 1])
    ctx.crit.setdefault("title", name)
    ctx.crit.setdefault("case_name", name)
    return ctx.result()


def _split_ladder(pieces: list) -> tuple:
    """A ladder row is a LABEL at the rail and a VALUE out at the value
    column. Returns (label_line, value_text) or (None, None)."""
    if len(pieces) < 2:
        return None, None
    first = pieces[0]
    if first.x0 > _LABEL_MAX_X0 or not _norm(first.plain).endswith(":"):
        return None, None
    rest = [p for p in pieces[1:] if p.x0 >= _VALUE_MIN_X0]
    if not rest:
        return None, None
    return first, " ".join(_norm(p.plain) for p in rest)


def _label_key(line) -> str | None:
    """The label a ladder row opens with, normalized, or None.

    The court's vocabulary is OPEN — it adds 'Amended' and 'Corrected' lines
    and it splits 'Submitted' / 'On Briefs:' across two rows — so a row that
    carries its colon is a labelled row whether or not the word is in
    `_LABELS`, and a bare word is one when the vocabulary knows it."""
    text = _norm(line.plain)
    if not text:
        return None
    key = text.rstrip(":").lower()
    if key in _LABELS or text.endswith(":"):
        return key
    return None


def _is_ladder_row(pm, line) -> bool:
    """A row of the LADDER — its label at the rail, or the VALUE standing out
    at the value column beside one — on page 1, in ladder type. The ladder,
    never furniture.

    core's corner-stamp rule fires on a short sub-body-size line pinned in
    the left third of the top 19% of a page, and BOTH of the ladder's
    columns stand there.

    THE LABEL: core already spares a label that carries its colon
    ('Docket:'). But Maine splits ONE label across TWO rows and the first
    half has no colon: MEASURED in me/amelia_johnson_v._michael_osseyran,
    'Submitted' stands alone at x0 72.0, 11.04pt, above 'On Briefs:
    October 29, 2025'. Its top sat at 0.1914 of the page — a hair outside
    the 0.19 band — until pdfio stopped reading a lying /Descent, which put
    the whole ladder back on its true baselines at 0.161 and handed the row
    to the stamp rule. Eight of the 50 records print it.

    THE VALUE: core spares Maine's neutral cite and the hyphenated docket
    form ('Som-25-258') by pattern, and the values are otherwise ordinary
    short strings. MEASURED in me/state_of_maine_v._jesse_r._pelletier, this
    court prints its docket with a SPACE ('Han 25-333', not 'Han-25-333')
    and sets both of its dates narrow enough to clear the left third
    ('April 8, 2026' x1 196.2, 'June 2, 2026' x1 193.6, against 0.35 of 612
    = 214.2) — so the docket and both dates went as corner stamps, the
    ladder lost three of its six values, and with no `docket_number` the
    reader returned NOTHING and the whole block fell to core (the user,
    2026-08-20). adoption_by_kathleen_c. escapes only because its values are
    set 9pt further right and run past the third.

    The test is the ROW, not the string: a value is whatever stands at the
    value column beside a label. No form of docket or date is enumerated
    here, so the next one the court prints reads too."""
    if pm.number != 1 or not line.size or line.size > _LADDER_SIZE_MAX:
        return False
    if line.x0 <= _LABEL_MAX_X0:
        return _label_key(line) is not None
    if line.x0 < _VALUE_MIN_X0:
        return False
    return any(other is not line and abs(other.top - line.top) <= 2.0
               and other.x0 <= _LABEL_MAX_X0
               and _label_key(other) is not None
               for other in pm.lines)


def _rows(pm, finder) -> list[list]:
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        if finder.kind(pm, line) and not _is_ladder_row(pm, line):
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

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
