"""Supreme Court of Montana ('mont').

Everything unique to mont lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py (with `front_matter=('syllabus',)`).

THE CONTRACT — Montana stacks three centred identifiers, sets a caption at
the rail with its party roles indented beneath each group, and then prints
TWO LABELLED LADDERS: where the appeal came from, and who appeared.

    ┌────────────────────────────────────────────────────────────────────┐
    │                                              03/31/2026   e-filing │
    │                      DA 25-0040                           stamps   │
    │                                    Case Number: DA 25-0040         │
    │        IN THE SUPREME COURT OF THE STATE OF MONTANA   the masthead │
    │                       2025 MT 64                      the cite     │
    ├──────────────────────────── drawn rule ────────────────────────────┤
    │ ALL FAMILIES HEALTHCARE; BLUE                                      │
    │ MOUNTAIN CLINIC; and HELEN WEEMS,                     the caption  │
    │        Plaintiffs and Appellees,                                   │
    │ v.                                                                 │
    │ STATE OF MONTANA; …,                                               │
    │        Defendants and Appellants.                                  │
    ├──────────────────────────── drawn rule ────────────────────────────┤
    │ APPEAL FROM:  District Court of the First Judicial District,       │
    │               In and For the County of Lewis and Clark, Cause …    │
    │               Honorable Christopher D. Abbott, Presiding Judge     │
    │                                                                    │
    │ COUNSEL OF RECORD:                                                 │
    │     For Appellants:                                                │
    │        Austin Knudsen, Montana Attorney General, …                 │
    │     For Appellees:                                                 │
    │        Alex Rate, ACLU of Montana, Missoula, Montana               │
    └────────────────────────────────────────────────────────────────────┘

THE STAMPS ARE NOT THE PAPER. Two things on page 1 are the clerk's, not the
court's: a bare filing date flushed right in 9pt ('03/31/2026') and a 6pt
'Case Number: DA 25-0040' beside it. Both are dropped. They are found by
their TYPE — measured, the paper is 12.5-13pt and nothing the court prints
falls below 12pt — and never by position, because the stamp's coordinates
move from record to record.

THE LADDERS ARE READ OFF THEIR LABELS, at three depths: a heading at the
rail ('APPEAL FROM:', 'COUNSEL OF RECORD:'), a sub-heading a step in ('For
Appellants:'), and the entries a further step in. The depth says which is
which, and the label says what it names — never an ordinal, because a record
with three parties prints three sub-headings and one with a cross-appeal
prints 'For Cross-Appellant:' as well.

WHY THE DOCKET IS READ TWICE OVER. 'DA 25-0040' is centred above the
masthead as the court's own number; the same string appears in the 6pt clerk
stamp. The centred one is the docket; the stamp is dropped. Reading the
stamp instead would put a 6pt row in the block.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(
    r"^IN THE SUPREME COURT OF THE STATE OF MONTANA$", re.I)
_AXIS_TOL = 12.0
_MAX_PAGES = 3
# The paper's type. Measured: 12.5-13pt body; the clerk's stamps are 9pt and
# 6pt and nothing the court prints is below 12pt.
_STAMP_SIZE_MAX = 11.0

# 'DA 25-0040' / 'OP 25-0123' / 'PR 24-0456' — the court's own number.
_DOCKET = re.compile(r"^(?:DA|OP|PR|AF|ADM)\s*\d{2}-\d{4}"
                     r"(?:\s*(?:,|and|&)\s*(?:DA|OP|PR)?\s*\d{2}-\d{4})*$", re.I)
# '2025 MT 64' / '2026 MT 86' — the public-domain cite.
_CITE = re.compile(r"^\d{4}\s*MT\s*\d+[A-Z]?$", re.I)
_STAMP_CASE_NO = re.compile(r"^Case Number:", re.I)
_STAMP_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PARTY_ROLE = re.compile(
    r"^(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|Appellants?"
    r"|Appellees?|Relators?|Claimants?|Intervenors?|Movants?)\b"
    r"[\w\s,/-]*[,.]$", re.I)
# The two ladder headings, and the sub-heading a step in.
#
# THE ORIGIN LADDER OPENS TWO WAYS, and until 2026-08-21 only one was known.
# Montana heads the recital 'APPEAL FROM:' on an appeal and 'ORIGINAL
# PROCEEDING:' when it takes a case itself, and both open the same ladder of
# entries a step in from the rail. Unmatched, the heading fell to the caption
# catch-all and the ladder BELOW it went unclaimed — a hole inside the block,
# which the bisection invariant then hands to a writing along with everything
# after it. transparent_election_initiative_v._knudsen lost its entire
# counsel block into the majority's body that way, opening the opinion on
# 'Petition for Declaratory Judgment … COUNSEL OF RECORD: For Petitioners:
# …'; only the heading was ever claimed.
#
# `\s*` BETWEEN THE WORDS, because the paper does not always print the space
# into its text layer: matter_of_s.j.c._yinc reads 'APPEALFROM: District Court
# of the Thirteenth Judicial District,' welded, so the heading missed, its
# three continuation rows went unclaimed, and a phantom `order` writing opened
# on them holding the county, the cause numbers and the presiding judge as its
# whole body. That record is not alone — its opinion says 'Thirteenth
# JudicialDistrict', 'chronic abuse or neglectand', 'orderedtreatment' — so
# the lost space is a MEASUREMENT defect in this court's paper, reported not
# patched here (see the note at the end of this module's docstring).
_ORIGIN_HEAD = re.compile(r"^(?:APPEAL\s*FROM|ORIGINAL\s*PROCEEDING)\s*:",
                          re.I)
# An ORIGINAL PROCEEDING HAS NO COURT BELOW, so its recital is not a
# lower-court row. `case-info` is the role for caption apparatus that is none
# of the named things (model.py); tinting 'Petition for Declaratory Judgment'
# `lower-court` would be a confident wrong answer.
_ORIGINAL = re.compile(r"^ORIGINAL\s*PROCEEDING", re.I)
_COUNSEL_HEAD = re.compile(r"^COUNSEL OF RECORD:", re.I)
_COUNSEL_FOR = re.compile(r"^For\s+.+:$", re.I)
_JUDGE_BELOW = re.compile(r"^Honorable\b|Presiding Judge|,\s*Judge$", re.I)
# 'Justice Laurie McKinnon delivered the Opinion of the Court.'
_BYLINE = re.compile(
    r"^(?:Chief )?Justice\s+.+\s+delivered the (?:Opinion|Order)"
    r"|^PER CURIAM|^JUSTICE\s+[A-Z]", re.I)
_PARA = re.compile(r"^¶\s*\d+")
# THE BLOCK CLOSES ON DATES, not on counsel. Below the last appearance the
# court flushes right the two dates that bracket the appeal and then leaves
# the clerk a line to sign:
#     Submitted on Briefs: November 17, 2025      (x0 324.0)
#     Decided:  March 31, 2026                    (x0 381.8)
#     Filed:                                      (x0  72.0, no value)
#     __________________________________________  (x0 180.0)
# Measured on all_families_v._state. Read as counsel — which is the band they
# sit in — they graded the record down for a split label, and the two dates
# the paper states were nowhere in its criteria.
_DATE_LABEL = re.compile(
    r"^(Submitted on Briefs|Submitted|Argued|Reargued|Decided|Filed|Dated"
    r"|Heard|Ordered)\s*:\s*(.*)$", re.I)
_DATE_CRIT = {"decided": "decision_date", "submitted": "submitted",
              "submitted on briefs": "submitted", "argued": "submitted",
              "reargued": "submitted", "heard": "submitted"}
_TYPED_RULE = re.compile(r"^_{6,}$")


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="mont")
def read_headmatter_mont(model, geom, **_):
    """Read Montana's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.5)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 6:
        return NOTHING
    if not any(_MASTHEAD.match(_norm(" ".join(l.plain for l in g)))
               for g in rows[:8]):
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    below: list[str] = []
    band = "ident"          # ident | caption | appeal | counsel
    origin_role = "lower-court"   # …or `case-info` on an original proceeding
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        size = first.size or 0.0
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - page1.width / 2) <= _AXIS_TOL

        if _PARA.match(text) or _BYLINE.match(text):
            break                       # the paper begins
        # THE CLERK'S STAMPS, by their type.
        if size and size < _STAMP_SIZE_MAX \
                and (_STAMP_CASE_NO.match(text) or _STAMP_DATE.match(text)):
            ctx.drop(pieces, "stamp")
            continue
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _CITE.match(text):
            ctx.crit.setdefault("citation", text)
            ctx.emit(pieces, "citation")
            continue
        if _DOCKET.match(text) and band == "ident":
            _dk = [t.strip() for t in re.split(r",|\band\b|&", text)
                   if t.strip()]
            ctx.crit.setdefault("docket_number", _dk[0])
            if _dk[1:]:
                ctx.crit.setdefault("other_dockets", _dk[1:])
            ctx.emit(pieces, "docket")
            continue
        # ---- the ladders --------------------------------------------------
        # The closing dates and the clerk's signature line are read BEFORE
        # the counsel band, which would otherwise claim them.
        dated = _DATE_LABEL.match(text)
        if dated:
            key = _DATE_CRIT.get(dated.group(1).strip().lower())
            value = _norm(dated.group(2))
            if key and value:
                ctx.crit.setdefault(key, value)
            ctx.emit(pieces, "date", centre=False)
            continue
        if _TYPED_RULE.match(text):
            ctx.rule(first.page, tuple(p.id for p in pieces), typed=True)
            continue
        if _ORIGIN_HEAD.match(text):
            band = "appeal"
            origin_role = "case-info" if _ORIGINAL.match(text) else "lower-court"
            below.append(text)
            ctx.emit(pieces, origin_role, centre=False)
            continue
        if _COUNSEL_HEAD.match(text):
            band = "counsel"
            ctx.emit(pieces, "counsel", centre=False)
            continue
        if band == "appeal":
            # The appeal-from ladder's entries stand a step in from its
            # heading; anything at the rail has left the ladder.
            if first.x0 > body_x0 + 20.0:
                below.append(text)
                ctx.emit(pieces, origin_role, centre=False)
                if _JUDGE_BELOW.search(text):
                    ctx.crit.setdefault("lower_court_judge", text)
                continue
            band = "ident"
        if band == "counsel":
            ctx.emit(pieces, "counsel", centre=False)
            continue
        # ---- the caption --------------------------------------------------
        if _PIVOT.match(text) or _PARTY_ROLE.match(text):
            band = "caption"
            ctx.emit(pieces, "caption", centre=False)
            continue
        if not centred and first.x0 <= body_x0 + 70.0:
            band = "caption"
            caption.append(text)
            ctx.emit(pieces, "caption", centre=False)
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("parties", caption[:8])
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
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
    out: list[list] = []
    for k in order:
        row = groups[k]
        # A ROW WHOSE PIECES STAND APART is two elements the page set on one
        # line — the centred docket and the clerk's stamp beside it.
        if len(row) > 1:
            out.extend([piece] for piece in row)
        else:
            out.append(row)
    return out


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

    def rule(self, page: int, ids: tuple = (), typed: bool = False) -> None:
        self.items.append(m.Rule(prov=m.Prov(page, ids), typed=typed,
                                 span="center" if typed else "full"))
        self.consumed.update(ids)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
