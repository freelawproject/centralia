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
# THE DISPOSITION STATES THE DATE. Mississippi prints no separate decision
# date: 'DISPOSITION: AFFIRMED AND REMANDED - 03/26/2026' is the only place
# the paper says when it was handed down, so the date is read out of it.
_DISPO_DATE = re.compile(r"-\s*(\d{1,2}/\d{1,2}/\d{4})\s*$")
_CRIT = ((re.compile(r"^TRIAL JUDGE", re.I), "lower_court_judge"),
         (re.compile(r"^COURT FROM WHICH APPEALED", re.I), "lower_court"),
         (re.compile(r"^DISPOSITION", re.I), "disposition"))

# A LADDER ROW IS NAMED BY ITS LABEL, and the label is an all-caps phrase
# closed by a colon. It is NOT identified by 'the line ends with a colon':
# pdfio returns the label and its value as one line whenever the gap between
# the columns is narrow, so on
# `benard_hubbard_ii_v._nexion_health_at_clinton_inc._dba_woodlands` every
# row came back as 'DATE OF JUDGMENT: 12/18/2024' and the whole table was
# read as CAPTION. The colon splits the row wherever pdfio happened to break
# it.
_LADDER_LABEL = re.compile(r"^([A-Z][A-Z0-9 /&'’.\-]*?):\s*(.*)$")
# A consolidated record prints a SECOND case below the first, under its own
# announcement. Measured: 'CONSOLIDATED WITH' centred, then a second docket,
# caption and ladder.
_CONSOLIDATED = re.compile(r"^CONSOLIDATED WITH$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PANEL = re.compile(r"^(?:BEFORE\b|EN BANC\.?$)", re.I)
# 'COLEMAN, PRESIDING JUSTICE, FOR THE COURT:' / 'ISHEE, JUSTICE, FOR THE
# COURT:' / 'PER CURIAM.'
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Z'’\-]+(?:,\s*[A-Z][A-Z'’\-]+)*,\s*"
    r"(?:PRESIDING\s+|CHIEF\s+)?(?:JUSTICE|JUDGE)\b.*|PER CURIAM\.?)$", re.I)
_PARA = re.compile(r"^¶\s*\d+\.?$")


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


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
            ctx.flush_ladder()
            break                       # the paper begins
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DOCKET.match(text):
            _dk = [t.strip() for t in
                   re.split(r",|\band\b|&", text.split(".", 1)[-1])
                   if t.strip()]
            ctx.crit.setdefault("docket_number", _dk[0])
            if _dk[1:]:
                ctx.crit.setdefault("other_dockets", _dk[1:])
            ctx.emit(pieces, "docket")
            continue
        if _PANEL.match(text):
            in_ladder = False
            ctx.flush_ladder()
            ctx.crit.setdefault("panel_line", text)
            ctx.emit(pieces, "panel")
            continue

        # A SECOND CASE. A consolidated record announces it and starts over
        # with its own docket, caption and ladder, so the ladder is closed
        # and the walk returns to the caption band. Skipping this dropped
        # everything below it out of the block.
        if _CONSOLIDATED.match(text):
            in_ladder = False
            ctx.flush_ladder()
            ctx.emit(pieces, "case-info")
            continue

        # A LADDER ROW: a label, and its value in the second column.
        lad = _LADDER_LABEL.match(text) if first.x0 <= _LABEL_MAX_X0 else None
        if lad is not None:
            in_ladder = True
            label_text, value_text = lad.group(1) + ":", _norm(lad.group(2))
            role = "case-info"
            for pat, r in _LABELS:
                if pat.search(label_text):
                    role = r
                    break
            last_role = role
            # WHERE pdfio SPLIT THE ROW decides how the cells are built, and
            # the reading is the same either way: separate pieces keep their
            # own provenance, a single line is divided at the colon.
            value_parts = [p for p in pieces[1:] if p.x0 >= _VALUE_MIN_X0]
            if len(pieces) > 1 and value_parts:
                ctx.ladder(pieces[0], value_parts, role)
                value_text = " ".join(_norm(p.plain) for p in value_parts)
            else:
                ctx.ladder_text(label_text, value_text, pieces, role)
            for pat, key in _CRIT:
                if pat.search(label_text) and value_text:
                    ctx.crit.setdefault(key, value_text)
            if role == "disposition" and value_text:
                _d = _DISPO_DATE.search(value_text)
                if _d:
                    ctx.crit.setdefault("decision_date", _d.group(1))
            continue
        # A RUNOVER VALUE belongs to the label above it, and stands in the
        # value column with NO label beside it.
        if in_ladder and first.x0 >= _VALUE_MIN_X0:
            ctx.ladder(None, pieces, last_role)
            continue

        # THE CAPTION is the all-caps run between a docket and its ladder.
        # NOTHING IN THE BLOCK IS LEFT UNCLAIMED: a hole here is not merely
        # an untagged row — core opens a WRITING on it and the bisection
        # invariant then pulls the rows around it into that writing, which is
        # how `billy_ray_gibson_aka_billy_gibson_v._state_of_mississippi`
        # came to have a line of its headmatter standing as an opinion.
        ctx.flush_ladder()
        in_ladder = False
        if not _PIVOT.match(text):
            caption.append(text)
        ctx.emit(pieces, "caption", centre=False)

    if not ctx.crit.get("docket_number"):
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
        self._lab: list = []
        self._val: list = []

    def _cell(self, parts, role: str):
        """One cell of the ladder. An empty cell holds its row's place so the
        two columns stay level."""
        parts = sorted(parts or [], key=lambda l: l.x0)
        if not parts:
            return m.HmLine(text="", prov=m.Prov(1), align=m.Align.LEFT,
                            role=role)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.consumed.update(p.id for p in parts)
        return m.HmLine(
            text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def ladder_text(self, label_text: str, value_text: str, pieces: list,
                    role: str) -> None:
        """One ladder row that pdfio returned as a SINGLE line. Both cells
        carry the whole row's provenance — the row is one printed line, and
        splitting its ids would claim characters, not lines."""
        prov = m.Prov(pieces[0].page, tuple(p.id for p in pieces))
        size = pieces[0].size or 0.0
        self._lab.append(m.HmLine(text=label_text, prov=prov,
                                  align=m.Align.LEFT, x0=pieces[0].x0,
                                  size=size, role=role))
        self._val.append(m.HmLine(text=value_text, prov=prov,
                                  align=m.Align.LEFT, x0=pieces[0].x0,
                                  size=size, role=role))
        self.consumed.update(p.id for p in pieces)

    def ladder(self, label, value_parts, role: str) -> None:
        """One printed row of the case-history table: its LABEL and its
        VALUE, each in its own column.

        Joined into a single row the table reads as a wall — the label runs
        into its own value, and a runover value, which has no label at all,
        stands alone as an orphan with no idea what it belongs to. The page
        prints two columns and the render draws two.
        """
        self._lab.append(self._cell([label] if label is not None else [], role))
        self._val.append(self._cell(value_parts, role))

    def flush_ladder(self) -> None:
        if not self._lab:
            return
        self.items.append(m.CaptionBlock(
            left=list(self._lab), right=list(self._val), rail=None,
            rail_rows=len(self._lab), style_id="case-history",
            prov=self._lab[0].prov if self._lab[0].prov.line_ids
            else self._val[0].prov))
        self._lab, self._val = [], []

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        # A ROW THAT IS NOT A LADDER ROW closes the table: emitted after it,
        # the table would render below a row the page prints beneath it.
        if not getattr(self, "_in_flush", False):
            self.flush_ladder()
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
        self.flush_ladder()
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
