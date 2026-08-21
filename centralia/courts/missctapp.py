"""Court of Appeals of the State of Mississippi ('missctapp').

SAME PAPER AS THE SUPREME COURT. All 30 records print the identical
CASE-HISTORY LADDER that `courts/miss.py` documents — the two Mississippi
appellate courts share one template and differ only in the masthead
('IN THE COURT OF APPEALS OF THE STATE OF MISSISSIPPI'), the docket suffix
('-COA' rather than '-SCT') and the bench title (J./P.J./C.J., not JUSTICE).
This file is nevertheless its own reader: miss's decider is registered for
miss alone, and three things measured differently here.

    ┌────────────────────────────────────────────────────────────────────┐
    │        IN THE COURT OF APPEALS OF THE STATE OF MISSISSIPPI         │
    │                   NO. 2025-CP-00575-COA                            │
    │ CARI WHITE                                            APPELLANT    │  ← the
    │ v.                                                                 │    caption:
    │ MATTHEW C. WHITE                                       APPELLEE    │    STATUS-FLUSH
    │                                                                    │
    │ DATE OF JUDGMENT:          04/30/2025                              │
    │ TRIAL JUDGE:               HON. JOSEPH PRESTON DURR                │
    │ COURT FROM WHICH APPEALED: COPIAH COUNTY CHANCERY COURT   the      │
    │ ATTORNEY FOR APPELLANT:    CARI WHITE (PRO SE)            ladder   │
    │ NATURE OF THE CASE:        CIVIL - CUSTODY                         │
    │ DISPOSITION:               AFFIRMED - 07/21/2026                    │
    │ MOTION FOR REHEARING FILED:                                        │
    │      BEFORE WILSON, P.J., EMFINGER AND LASSITTER ST. PÉ, JJ.       │  ← the bench
    │      EMFINGER, J., FOR THE COURT:                                  │  ← the paper
    └────────────────────────────────────────────────────────────────────┘

THE CAPTION IS TWO COLUMNS, NOT ONE ROW. The party names stand at the body
rail and the party STATUS is flush right against the right margin — measured
over all 30 records, the status cell's x1 lands in 532–540 on a 540pt
measure while the party cell it shares the row with never reaches 406. On a
wide caption the status starts as far left as x0=366, so the cell is
identified by its RIGHT edge, never by a left threshold. Joined into one
left-aligned row (which is what miss.py does) 'CARI WHITE APPELLANT' reads
as a party called APPELLANT; the page prints two columns and the render
draws two. A status that wraps ('APPELLANT/CROSS-' over 'APPELLEE') pairs
row by row with the party rows beside it, which is what a CaptionBlock is.

'DATE OF JUDGMENT:' IS THE LADDER'S LANDMARK. Every one of the 30 records
opens the table with it, so the ladder is entered on that label and not on
'the row is all caps and ends in a colon'. That test alone misreads the
caption of `in_re_order_of_direct_criminal_contempt_…`, whose third party
row is 'ATTORNEY ANDREW WILLCUTT:' — a colon-closed all-caps phrase at the
rail that is a PARTY, and which under a wording test would have opened the
table five rows early and taken the pivot and the second party with it.

A LABEL MAY WRAP, AND ITS VALUE RUNS BESIDE THE WRAP.
`ajinomoto_foods_north_america_…` prints

    TRIBUNAL FROM WHICH          MISSISSIPPI WORKERS' COMPENSATION
    APPEALED:                    COMMISSION

so the FIRST of the two label rows carries no colon at all. Once the ladder
is open every row at the rail belongs to it — nothing else in this paper
sets a row at x0=72 below the table's first label — so the wrap needs no
test of its own and keeps its own value cell beside it.

THE VALUE COLUMN IS NOT AT A FIXED x0. It prints at 290 on most records, at
292 on `…estate_of_grace_j._howell`, at 267 once
(`kadarron_foreman…`, 'ATTORNEY FOR APPELLEE:'), and a second-line value is
indented to 316. The column is a floor, not a coordinate.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import roster_names

_MASTHEAD = re.compile(
    r"^IN THE COURT OF APPEALS OF THE STATE OF MISSISSIPPI$", re.I)
_DOCKET = re.compile(r"^NOS?\.\s*\d{4}-[A-Z]{1,3}-\d{4,5}(?:-[A-Z]{2,4})?"
                     r"(?:\s*(?:,|and|&)\s*[\dA-Z-]+)*$", re.I)

# THE TWO COLUMNS, MEASURED OVER ALL 30 RECORDS.
_LABEL_MAX_X0 = 84.0        # labels sit at the body rail, x0=72
_VALUE_MIN_X0 = 258.0       # values at 267–316; the floor, not a coordinate
_STATUS_MIN_X0 = 340.0      # a status cell starts no further left than 366
_STATUS_RIGHT_SLOP = 22.0   # …and ends within this of the right margin

_LADDER_OPEN = re.compile(r"^DATE OF (?:JUDGMENT|ORDER)\b", re.I)
_LADDER_LABEL = re.compile(r"^([A-Z][A-Z0-9 /&'’.\-]*?):\s*(.*)$")
_CONSOLIDATED = re.compile(r"^CONSOLIDATED WITH$", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PANEL = re.compile(r"^(?:BEFORE\b|EN BANC\.?$)", re.I)
_PARA = re.compile(r"^¶\s*\d+\.?$")
# 'EMFINGER, J., FOR THE COURT:' / 'LASSITTER ST. PÉ, J., FOR THE COURT:' /
# 'CARLTON, P.J., FOR THE COURT:' / 'PER CURIAM.'  The Court of Appeals
# signs with the ABBREVIATED title, so miss's spelled-out JUSTICE|JUDGE
# pattern matches none of these.
_BYLINE = re.compile(
    r"^(?:[A-ZÁÉÍÓÚÑÀÈÊÔÇ][A-ZÁÉÍÓÚÑÀÈÊÔÇ'’\-]*"
    r"(?:[ ,]+[A-ZÁÉÍÓÚÑÀÈÊÔÇ][A-ZÁÉÍÓÚÑÀÈÊÔÇ'’\-]*)*,\s*"
    r"(?:[CPV]\.\s?)?J\.,\s*(?:FOR THE COURT|CONCURRING|DISSENTING|SPECIALLY)"
    r"\b.*|PER CURIAM\.?)$", re.I)

# WHAT EACH LABEL NAMES. The label's own words, and nowhere else — the court
# prints a different subset of the table on every record (a criminal appeal
# adds 'DISTRICT ATTORNEY:', a workers' compensation appeal swaps 'COURT FROM
# WHICH APPEALED' for 'TRIBUNAL FROM WHICH APPEALED'), so position names
# nothing. An unknown label reads as `case-info` rather than being guessed at.
_LABELS = (
    (re.compile(r"^(?:DATE OF JUDGMENT|DATE OF ORDER|TRIAL JUDGE"
                r"|(?:TRIAL |)COURT FROM WHICH APPEALED"
                r"|TRIBUNAL FROM WHICH|APPEALED:)", re.I), "lower-court"),
    (re.compile(r"ATTORNEYS?\b", re.I), "counsel"),
    (re.compile(r"^DISPOSITION", re.I), "disposition"),
)
_CRIT = ((re.compile(r"^TRIAL JUDGE", re.I), "lower_court_judge"),
         (re.compile(r"^(?:COURT|TRIBUNAL) FROM WHICH", re.I), "lower_court"),
         (re.compile(r"^DISPOSITION", re.I), "disposition"))
# 'DISPOSITION: AFFIRMED - 07/21/2026' is the ONLY place this paper states
# when it was handed down.
_DISPO_DATE = re.compile(r"-\s*(\d{1,2}/\d{1,2}/\d{4})\s*$")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="missctapp")
def read_headmatter_missctapp(model, geom, **_):
    """Read the Court of Appeals' case-history ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = geom.body_size if geom and geom.body_size else 13.0
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    right_x1 = geom.right_x1 if geom and geom.right_x1 else 540.0
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE BLOCK MAY RUN ONTO PAGE 2. A consolidated record prints two whole
    # case histories — `…estate_of_grace_j._howell…` sets its second docket,
    # caption and ladder below the first and the table breaks across the page,
    # its last four labels and the panel and byline landing at the top of
    # page 2. Read from page 1 alone the walk simply stopped at the foot of
    # the sheet and fifty words of the second appeal's counsel and
    # disposition went missing from the document entirely. The walk ends at
    # the byline wherever it falls, so taking two pages costs the other 29
    # records nothing — every one of them signs on page 1.
    rows = [r for pm in model.pages[:2] for r in _rows(pm, finder)]
    if len(rows) < 6:
        return NOTHING
    if not _MASTHEAD.match(_norm(" ".join(l.plain for l in rows[0]))):
        return NOTHING

    ctx = _Ctx()
    parties: list[str] = []
    last_role = "case-info"
    in_ladder = False
    seen_panel = False
    # WHOSE DISPOSITION A RUNOVER CONTINUES. A consolidated record states two
    # of them and only the FIRST is this document's; without the flag the
    # second appeal's wrapped value was appended to the first's.
    dispo_open = False
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]

        # THE PAPER BEGINS. Everything below the byline belongs to the
        # writing and nothing may be lifted out of it.
        if _PARA.match(_norm(first.plain)) or _BYLINE.match(text) \
                or (seen_panel and not _PANEL.match(text)):
            break
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DOCKET.match(text):
            nums = [t.strip() for t in
                    re.split(r",|\band\b|&", text.split(".", 1)[-1])
                    if t.strip()]
            for num in nums:
                if not ctx.crit.get("docket_number"):
                    ctx.crit["docket_number"] = num
                elif num != ctx.crit["docket_number"]:
                    ctx.crit.setdefault("other_dockets", []).append(num)
            in_ladder = False
            ctx.emit(pieces, "docket")
            continue
        if _PANEL.match(text):
            in_ladder = False
            seen_panel = True
            ctx.crit.setdefault("panel_line", text)
            roster = re.sub(r"^BEFORE\s*:?\s*", "", text, flags=re.I).strip()
            if roster and not roster.upper().startswith("EN BANC"):
                ctx.crit.setdefault("judges", roster)
                names = roster_names(roster)
                if names:
                    ctx.crit.setdefault("panel", names)
            ctx.emit(pieces, "panel")
            continue
        # A SECOND CASE: a consolidated record announces it and starts over
        # with its own docket, caption and ladder.
        if _CONSOLIDATED.match(text):
            in_ladder = False
            ctx.emit(pieces, "case-info")
            continue

        # A LADDER ROW. The table opens on its own landmark and, once open,
        # owns every row at the rail — including a label that wrapped and so
        # carries no colon of its own.
        at_rail = first.x0 <= _LABEL_MAX_X0
        if at_rail and (in_ladder or _LADDER_OPEN.match(text)):
            in_ladder = True
            lad = _LADDER_LABEL.match(text)
            label_text = (lad.group(1) + ":") if lad else text
            value_text = _norm(lad.group(2)) if lad else ""
            role = last_role if not lad else "case-info"
            for pat, r in _LABELS:
                if pat.search(label_text):
                    role = r
                    break
            last_role = role
            # WHERE pdfio SPLIT THE ROW decides how the cells are built, and
            # the reading is the same either way: separate pieces keep their
            # own provenance, a single fused line is divided at the colon.
            dispo_open = False
            value_parts = [p for p in pieces[1:] if p.x0 >= _VALUE_MIN_X0]
            if value_parts:
                ctx.ladder(pieces[0], value_parts, role)
                value_text = " ".join(_norm(p.plain) for p in value_parts)
            else:
                ctx.ladder_text(label_text, value_text, pieces, role)
            for pat, key in _CRIT:
                if pat.search(label_text) and value_text:
                    ctx.crit.setdefault(key, value_text)
            if role == "counsel" and value_text:
                ctx.counsel.append(f"{label_text} {value_text}".strip())
            elif role == "counsel":
                ctx.counsel.append(label_text)
            if role == "disposition" and value_text:
                dispo_open = ctx.crit.get("disposition") == value_text
                hit = _DISPO_DATE.search(value_text)
                if hit:
                    ctx.crit.setdefault("decision_date", hit.group(1))
            continue
        # A RUNOVER VALUE stands in the value column with no label beside it
        # and belongs to the label above.
        if in_ladder and first.x0 >= _VALUE_MIN_X0:
            ctx.ladder(None, pieces, last_role)
            if last_role == "counsel":
                ctx.counsel.append(text)
            # A DISPOSITION MAY WRAP, AND THE DATE IS ON THE LAST ROW.
            # `…estate_of_grace_j._howell…` sets 'ON DIRECT APPEAL:
            # AFFIRMED; ON' / 'CROSS-APPEAL: AFFIRMED - 07/21/2026', so the
            # only statement of the decision date is in the runover cell.
            elif dispo_open:
                hit = _DISPO_DATE.search(text)
                if hit:
                    ctx.crit.setdefault("decision_date", hit.group(1))
                ctx.crit["disposition"] = _norm(
                    ctx.crit["disposition"] + " " + text)
            continue

        # THE CAPTION: parties at the rail, status flush right. Nothing in
        # the block is left unclaimed — a hole here is not merely an untagged
        # row, it is a row core opens a WRITING on.
        status = None
        if len(pieces) > 1 and pieces[-1].x0 >= _STATUS_MIN_X0 \
                and pieces[-1].x1 >= right_x1 - _STATUS_RIGHT_SLOP:
            status = pieces[-1]
            pieces = pieces[:-1]
        left = _norm(" ".join(l.plain for l in pieces))
        if left and not _PIVOT.match(left):
            parties.append(left)
        ctx.caption(pieces, status)

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if parties:
        ctx.crit.setdefault("parties", parties[:10])
    if ctx.counsel:
        ctx.crit.setdefault("attorneys", "; ".join(ctx.counsel))
    ctx.crit.setdefault("headmatter_style", "case-history ladder")
    return ctx.result()


def _rows(pm, finder) -> list[list]:
    """Page 1's rows, top to bottom, furniture removed."""
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
    """The emit buffer: what the walk placed, and where it came from.

    Two tables are open at different times — the caption (parties | status)
    and the ladder (label | value) — and each is flushed as one CaptionBlock
    the moment a row that is not one of its rows arrives. Emitted any later
    the block would render below matter the page prints beneath it.
    """

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.counsel: list[str] = []
        self._open: str | None = None
        self._l: list = []
        self._r: list = []

    # -- cells --------------------------------------------------------------
    def _cell(self, parts, role: str, align=m.Align.LEFT):
        """One cell. An empty cell holds its row's place so the two columns
        stay level."""
        parts = sorted(parts or [], key=lambda l: l.x0)
        if not parts:
            return m.HmLine(text="", prov=m.Prov(1), align=align, role=role)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.consumed.update(p.id for p in parts)
        return m.HmLine(
            text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            align=align, x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def _flush(self) -> None:
        if not self._l:
            self._open = None
            return
        style = "status-flush" if self._open == "caption" else "case-history"
        prov = self._l[0].prov if self._l[0].prov.line_ids else self._r[0].prov
        self.items.append(m.CaptionBlock(
            left=list(self._l), right=list(self._r), rail=None,
            rail_rows=len(self._l), style_id=style, prov=prov))
        self._l, self._r, self._open = [], [], None

    def _row(self, kind: str, left, right) -> None:
        if self._open != kind:
            self._flush()
            self._open = kind
        self._l.append(left)
        self._r.append(right)

    # -- the caption --------------------------------------------------------
    def caption(self, party_parts, status) -> None:
        self._row("caption", self._cell(party_parts, "caption"),
                  self._cell([status] if status is not None else [],
                             "caption", align=m.Align.RIGHT))

    # -- the ladder ---------------------------------------------------------
    def ladder(self, label, value_parts, role: str) -> None:
        self._row("ladder",
                  self._cell([label] if label is not None else [], role),
                  self._cell(value_parts, role))

    def ladder_text(self, label_text: str, value_text: str, pieces: list,
                    role: str) -> None:
        """One ladder row pdfio returned as a SINGLE line. Both cells carry
        the whole row's provenance — the row is one printed line, and
        splitting its ids would claim characters, not lines."""
        prov = m.Prov(pieces[0].page, tuple(p.id for p in pieces))
        size = pieces[0].size or 0.0
        self._row("ladder",
                  m.HmLine(text=label_text, prov=prov, align=m.Align.LEFT,
                           x0=pieces[0].x0, size=size, role=role),
                  m.HmLine(text=value_text, prov=prov, align=m.Align.LEFT,
                           x0=pieces[0].x0, size=size, role=role))
        self.consumed.update(p.id for p in pieces)

    # -- single rows --------------------------------------------------------
    def emit(self, group: list, role: str, centre: bool = True) -> None:
        self._flush()
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(parts[0].page,
                                   tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        self._flush()
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
