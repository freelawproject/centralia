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
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

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
    # at the label column, in ladder type.
    head = rows[0]
    if _norm(" ".join(l.plain for l in head)).lower().split("reporter")[0]\
            .strip() != _MASTHEAD:
        return NOTHING

    ctx = _Ctx()
    ladder_done = False
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


def _is_ladder_label(pm, line) -> bool:
    """A word from the court's OWN LABEL VOCABULARY, in ladder type, at the
    label rail of page 1 — the ladder, never furniture.

    core's corner-stamp rule fires on a short sub-body-size line pinned in
    the left third of the top 19% of a page, which is where this ladder's
    label column stands; it already spares a label that carries its colon
    ('Docket:'). But Maine splits ONE label across TWO rows and the first
    half has no colon: MEASURED in me/amelia_johnson_v._michael_osseyran,
    'Submitted' stands alone at x0 72.0, 11.04pt, above 'On Briefs:
    October 29, 2025'. Its top sat at 0.1914 of the page — a hair outside
    the 0.19 band — until pdfio stopped reading a lying /Descent, which put
    the whole ladder back on its true baselines at 0.161 and handed the row
    to the stamp rule. Eight of the 50 records print it."""
    if pm.number != 1 or line.x0 > _LABEL_MAX_X0:
        return False
    if not line.size or line.size > _LADDER_SIZE_MAX:
        return False
    return _norm(line.plain).rstrip(":").lower() in _LABELS


def _rows(pm, finder) -> list[list]:
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        if finder.kind(pm, line) and not _is_ladder_label(pm, line):
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
