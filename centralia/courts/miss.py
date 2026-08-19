"""Supreme Court of Mississippi ('miss').

Everything unique to miss lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — Mississippi prints a CASE-HISTORY LADDER. Above it stands a
plain centred masthead and docket, and an all-caps caption at the rail;
below it, the panel and the byline. The ladder is a two-column table in
which the left column NAMES the row.

    ┌────────────────────────────────────────────────────────────────────┐
    │              IN THE SUPREME COURT OF MISSISSIPPI     the masthead  │
    │                   NO. 2024-CA-01277-SCT              the docket    │
    │ ANDREW MALLETTE, M.D. AND THE                                      │
    │ SURGICAL CLINIC ASSOCIATES, P.A.                     the caption,  │
    │ v.                                                   all caps      │
    │ NITKIA RHEA REVETTE, IN HER CAPACITIES …                           │
    │                                                                    │
    │ DATE OF JUDGMENT:          10/16/2024                              │
    │ TRIAL JUDGE:               HON. WINSTON L. KIDD                    │
    │ TRIAL COURT ATTORNEYS:     WILLIAM MONROE QUIN, II                 │
    │                            TIMOTHY LEE SENSING          the ladder │
    │ COURT FROM WHICH APPEALED: HINDS COUNTY CIRCUIT COURT              │
    │ ATTORNEYS FOR APPELLANTS:  TIMOTHY LEE SENSING                     │
    │ NATURE OF THE CASE:        CIVIL - WRONGFUL DEATH                  │
    │ DISPOSITION:               AFFIRMED AND REMANDED - 03/26/2026       │
    │ MOTION FOR REHEARING FILED:                                        │
    │        BEFORE COLEMAN, P.J., ISHEE AND BRANNING, JJ.    the panel  │
    │        COLEMAN, PRESIDING JUSTICE, FOR THE COURT:       the writing │
    └────────────────────────────────────────────────────────────────────┘

THE LABEL IS THE LANDMARK. Roles come from the label's own words and from
nowhere else — not from the row's position, because the court prints a
different subset of the ladder on every record (a criminal appeal adds
'ATTORNEY FOR APPELLANT: OFFICE OF STATE PUBLIC DEFENDER', a rehearing adds
'MANDATE ISSUED'), and an unknown label is read as `case-info` rather than
guessed at.

A LABEL WITH NO VALUE IS STILL A ROW. 'MOTION FOR REHEARING FILED:' prints
empty on most records; it is the court saying none was filed, and it is read.

THE VALUE COLUMN RUNS OVER. A ladder entry with several values prints one
per line, the first beside its label and the rest alone in the value column
— so a row in the value column with no label belongs to the label above it.

THE BYLINE ENDS THE READER. Mississippi signs 'COLEMAN, PRESIDING JUSTICE,
FOR THE COURT:' in bold beneath the 'BEFORE …' panel row, and that is the
paper, not the block.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(
    r"^IN THE (?:SUPREME COURT OF MISSISSIPPI"
    r"|COURT OF APPEALS OF THE STATE OF MISSISSIPPI)$", re.I)
_DOCKET = re.compile(r"^NOS?\.\s*\d{4}-[A-Z]{1,3}-\d{4,5}(?:-[A-Z]{2,4})?"
                     r"(?:\s*(?:,|and|&)\s*[\dA-Z-]+)*$", re.I)
_AXIS_TOL = 10.0
_MAX_PAGES = 2
# The ladder's two columns, measured: labels at the body rail, values at 290.
_LABEL_MAX_X0 = 80.0
_VALUE_MIN_X0 = 270.0

# WHAT EACH LABEL NAMES.
_LABELS = (
    (re.compile(r"^(?:DATE OF JUDGMENT|TRIAL JUDGE|COURT FROM WHICH APPEALED"
                r"|COURT FROM WHICH APPEALED FROM|DATE OF ORDER)", re.I),
     "lower-court"),
    (re.compile(r"ATTORNEYS?\b", re.I), "counsel"),
    (re.compile(r"^NATURE OF THE CASE", re.I), "case-info"),
    (re.compile(r"^DISPOSITION", re.I), "disposition"),
    (re.compile(r"^(?:MOTION FOR REHEARING FILED|MANDATE ISSUED"
                r"|DATE OF MANDATE)", re.I), "case-info"),
)
_CRIT = ((re.compile(r"^TRIAL JUDGE", re.I), "lower_court_judge"),
         (re.compile(r"^COURT FROM WHICH APPEALED", re.I), "lower_court"),
         (re.compile(r"^DISPOSITION", re.I), "disposition"))

_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PANEL = re.compile(r"^(?:BEFORE\b|EN BANC\.?$)", re.I)
# 'COLEMAN, PRESIDING JUSTICE, FOR THE COURT:' / 'ISHEE, JUSTICE, FOR THE
# COURT:' / 'PER CURIAM.'
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Z'’\-]+(?:,\s*[A-Z][A-Z'’\-]+)*,\s*"
    r"(?:PRESIDING\s+|CHIEF\s+)?(?:JUSTICE|JUDGE)\b.*|PER CURIAM\.?)$", re.I)
_PARA = re.compile(r"^¶\s*\d+\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="miss")
def read_headmatter_miss(model, geom, **_):
    """Read Mississippi's ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 4:
        return NOTHING
    if not _MASTHEAD.match(_norm(" ".join(l.plain for l in rows[0]))):
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    last_role = "case-info"
    in_ladder = False
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]

        if _PARA.match(_norm(first.plain)) or _BYLINE.match(text):
            break                       # the paper begins
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DOCKET.match(text):
            ctx.crit.setdefault(
                "docket", [t.strip() for t in
                           re.split(r",|\band\b|&", text.split(".", 1)[-1])
                           if t.strip()])
            ctx.emit(pieces, "docket")
            continue
        if _PANEL.match(text):
            in_ladder = False
            ctx.crit.setdefault("panel_line", text)
            ctx.emit(pieces, "panel")
            continue

        # A LADDER ROW: a label at the rail, its value out at 290.
        label = first if (first.x0 <= _LABEL_MAX_X0
                          and _norm(first.plain).endswith(":")) else None
        if label is not None:
            in_ladder = True
            role = "case-info"
            for pat, r in _LABELS:
                if pat.search(_norm(label.plain)):
                    role = r
                    break
            last_role = role
            ctx.emit(pieces, role, centre=False)
            value = " ".join(_norm(p.plain) for p in pieces[1:]
                             if p.x0 >= _VALUE_MIN_X0)
            for pat, key in _CRIT:
                if pat.search(_norm(label.plain)) and value:
                    ctx.crit.setdefault(key, value)
            continue
        # A RUNOVER VALUE belongs to the label above it.
        if in_ladder and first.x0 >= _VALUE_MIN_X0:
            ctx.emit(pieces, last_role, centre=False)
            continue

        if in_ladder:
            # Past the ladder and not a panel or a byline: leave it to core
            # rather than tint it with the nearest neighbour's role.
            continue
        # THE CAPTION is the all-caps run between the docket and the ladder.
        if _PIVOT.match(text):
            ctx.emit(pieces, "caption", centre=False)
            continue
        caption.append(text)
        ctx.emit(pieces, "caption", centre=False)

    if not ctx.crit.get("docket"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("parties", caption[:8])
    return ctx.result()


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
