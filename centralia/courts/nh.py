"""Supreme Court of New Hampshire ('nh').

Everything unique to nh lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — New Hampshire fronts every opinion with a NINE-LINE NOTICE,
then names itself, then draws a typed rule, and then sets a block in two
positions: the case's own identifiers at the rail, and everything the court
says about the paper CENTRED.

    ┌────────────────────────────────────────────────────────────────────┐
    │ NOTICE:  This opinion is subject to motions for rehearing …        │
    │ well as formal revision before publication in the New Hampshire …  │  the notice,
    │ Readers are requested to notify the Reporter, Supreme Court of …   │  nine lines,
    │ … reporter@courts.state.nh.us.  Opinions are available on …        │  furniture
    │                                                                    │
    │            THE SUPREME COURT OF NEW HAMPSHIRE      the masthead    │
    │                 ___________________________        a TYPED rule    │
    │ New Hampshire Board of Medicine                    the tribunal    │
    │ Case No. 2023-0637                                 the docket      │
    │ Citation: Appeal of Doe (Bd. of Med.), 2025 N.H. 13   the cite      │
    │                                                                    │
    │                  APPEAL OF JOHN DOE                the caption     │
    │            (New Hampshire Board of Medicine)                        │
    │                Argued: June 27, 2024                               │
    │            Opinion Issued: March 18, 2025          the dates       │
    │                                                                    │
    │     Rath, Young, and Pignatelli, P.C., of Concord (Adam …          │  the
    │ brief and orally), for the petitioner.                             │  appearances
    │     John M. Formella, attorney general, … for the respondent.      │
    │                                                                    │
    │     COUNTWAY, J.                                   the writing     │
    └────────────────────────────────────────────────────────────────────┘

THE NOTICE IS FURNITURE and it names itself: it opens 'NOTICE:' and every
line of it stands at the body rail above the masthead. It is dropped, not
tinted with a role — it is the Reporter's standing warning about rehearing
and revision, printed identically on all 50 records, and no part of it is
the court's writing.

THE RAIL SAYS 'CASE', THE AXIS SAYS 'PAPER'. Measured over 50 records, the
three rail rows below the masthead are the tribunal appealed from, the case
number and the court's own public-domain citation; everything the court sets
CENTRED — the caption, the tribunal in parentheses beneath it, and the two
dates — is about the paper. Each is still read by its own landmark, because
a record with no argument prints 'Submitted:' instead of 'Argued:' and one
originating here prints no tribunal row at all.

THE APPEARANCES ARE PROSE, opening on an indent and running back to the
rail, and they name themselves in their last words ('for the petitioner.').

THE BYLINE ENDS THE READER. New Hampshire signs name-first on the paragraph
indent ('COUNTWAY, J.'), and that row is the paper, not the block.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(r"^THE SUPREME COURT OF NEW HAMPSHIRE$", re.I)
_AXIS_TOL = 10.0
_MAX_PAGES = 2

_NOTICE_OPEN = re.compile(r"^NOTICE:", re.I)
_TYPED_RULE = re.compile(r"^_{6,}$")
# 'Case No. 2023-0637' / 'Case Nos. 2023-0637, 2023-0641'
_DOCKET = re.compile(r"^Case Nos?\.\s*(.+)$", re.I)
# 'Citation: Appeal of Doe (Bd. of Med.), 2025 N.H. 13'
_CITATION = re.compile(r"^Citation:\s*(.+)$", re.I)
# The two dates the court prints about the paper.
_DATE_LABEL = re.compile(
    r"^(Argued|Submitted|Reargued|Opinion Issued|Opinion Filed|Issued"
    r"|Decided):\s*(.+)$", re.I)
_DATE_CRIT = {"opinion issued": "decision_date", "opinion filed": "decision_date",
              "issued": "decision_date", "decided": "decision_date",
              "argued": "argued", "reargued": "argued",
              "submitted": "submitted"}
# The tribunal the appeal came from, printed at the rail above the docket and
# again in parentheses under the caption.
_TRIBUNAL = re.compile(
    r"\b(?:Board|Bureau|Commission|Department|Division|Council"
    r"|Superior Court|District Court|Probate|Circuit Court|Court"
    r"|Compensation Appeals)\b", re.I)
_PARENTHETICAL = re.compile(r"^\(.*\)$")
# The appearances name themselves in their last words.
_COUNSEL = re.compile(
    r"for the (?:petitioner|respondent|plaintiff|defendant|appellant"
    r"|appellee|state|intervenor|amicus)", re.I)
_ORALLY = re.compile(r"\b(?:on the brief|orally|self-represented|pro se)\b",
                     re.I)
# 'COUNTWAY, J.' / 'MacDONALD, C.J.' / 'PER CURIAM.'
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z'’\-]+(?:,\s*[A-Z][A-Za-z'’\-]+)*,\s*"
    r"(?:C\.?\s*J\.?|JJ?\.?)|PER CURIAM\.?)$")
_PARA = re.compile(r"^\[¶\s*\d+\]")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="nh")
def read_headmatter_nh(model, geom, **_):
    """Read New Hampshire's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 6:
        return NOTHING
    # THE DISPATCH: the masthead, wherever the notice above it happens to
    # end. Never an ordinal — the notice is nine lines on most records and
    # ten where the URL wraps.
    mast = next((i for i, g in enumerate(rows[:16])
                 if _MASTHEAD.match(_norm(" ".join(l.plain for l in g)))), None)
    if mast is None:
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    below: list[str] = []
    band = "ident"          # ident | caption | counsel
    for idx, group in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - page1.width / 2) <= _AXIS_TOL

        # THE NOTICE is everything above the masthead.
        if idx < mast:
            ctx.drop(pieces, "notice")
            continue
        if _PARA.match(text) or (band != "ident" and _BYLINE.match(text)):
            break                       # the paper begins
        if _TYPED_RULE.match(text):
            ctx.rule(first.page, tuple(p.id for p in pieces), typed=True)
            continue
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        docket = _DOCKET.match(text)
        if docket:
            ctx.crit.setdefault(
                "docket", [t.strip() for t in docket.group(1).split(",")
                           if t.strip()])
            ctx.emit(pieces, "docket", centre=False)
            continue
        cite = _CITATION.match(text)
        if cite:
            ctx.crit.setdefault("citation", _norm(cite.group(1)))
            ctx.emit(pieces, "citation", centre=False)
            continue
        dated = _DATE_LABEL.match(text)
        if dated:
            key = _DATE_CRIT.get(dated.group(1).lower())
            if key:
                ctx.crit.setdefault(key, _norm(dated.group(2)))
            ctx.emit(pieces, "date")
            continue
        # THE APPEARANCES name themselves, and once opened the band runs to
        # the byline: an entry's second and third lines say nothing about
        # representation on their own.
        if _COUNSEL.search(text) or _ORALLY.search(text) or band == "counsel":
            band = "counsel"
            ctx.emit(pieces, "counsel", centre=False)
            continue
        # THE TRIBUNAL, at the rail before the caption or parenthesised
        # beneath it.
        if _TRIBUNAL.search(text) and (band == "ident" or _PARENTHETICAL.match(text)):
            below.append(text)
            ctx.emit(pieces, "lower-court", centre=centred)
            continue
        if centred:
            band = "caption"
            caption.append(text)
            ctx.emit(pieces, "caption")
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue

    if not ctx.crit.get("docket"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("case_name", " ".join(caption))
        ctx.crit.setdefault("parties", caption[:6])
    if below:
        ctx.crit.setdefault("lower_court", below[0])
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

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int, ids: tuple = (), typed: bool = False) -> None:
        self.items.append(m.Rule(prov=m.Prov(page, ids), typed=typed,
                                 span="center" if typed else "full"))
        self.consumed.update(ids)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
