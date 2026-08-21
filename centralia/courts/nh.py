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
# HOW FAR THE BLOCK MAY RUN. Measured over all 50 records by where the first
# byline or '[¶1]' stands: page 1 on 41, page 2 on 7, page 3 on 1
# (contoocook_valley, whose 12 amicus appearances name the whole House and
# fill two sheets), and one record prints neither. Nothing needs a fourth.
# The walk ends at the court's own prose either way, so a record whose
# opinion opens on page 1 never reaches the second sheet.
_MAX_PAGES = 3

# A CENTRED ROW IS A SHORT ROW. The mid-point test alone calls a full-measure
# line centred whenever its text happens to balance: the first line of nh's
# appearances runs 108.0-511.8, whose centre is 310 against a page centre of
# 306, so 'Rath, Young, and Pignatelli, P.C., of Concord (Adam Pignatelli on
# the' was read as CAPTION on appeal_of_doe_bd._of_med. A caption row, a date
# row and the masthead are all short; prose fills the measure.
_CENTRED_WIDTH_MAX = 0.72
# THE APPEARANCES OPEN ON THE PARAGRAPH INDENT and run back to the rail
# (108.0 over 72.0, measured on all 50 records). Their naming phrase ('for
# the petitioner.') often falls on the SECOND or third line, so the entry
# cannot be recognised from its opening line's words — the indent is what
# opens it, once the court has printed its dates.
_INDENT = 36.0
_INDENT_TOL = 4.0

_NOTICE_OPEN = re.compile(r"^NOTICE:", re.I)
_TYPED_RULE = re.compile(r"^_{6,}$")
# 'Case No. 2023-0637' / 'Case Nos. 2023-0637, 2023-0641'
# 'Case No. 2023-0637' / 'Case Nos. 2023-0637, 2023-0641' — and on the one
# 2020 record in the corpus the older form 'No. 2019-0072', which the reader
# needs because the docket is what it dispatches on: without it
# `state_of_new_hampshire_v._joshua_l._shaw` returned NOTHING and lost its
# whole block.
# A DISCIPLINE DOCKET CARRIES A LETTER PREFIX: 'Case No. LD-2024-0005'
# (appeal_of_hoppock). Anchoring the number without it refused that record
# outright — the docket is what this reader dispatches on.
_DOCKET = re.compile(
    r"^(?:Case\s+)?Nos?\.\s*((?:[A-Z]{1,3}-)?\d{4}-\d{3,4}.*)$", re.I)
# 'Citation: Appeal of Doe (Bd. of Med.), 2025 N.H. 13'
_CITATION = re.compile(r"^Citation:\s*(.+)$", re.I)
# The two dates the court prints about the paper.
_DATE_LABEL = re.compile(
    r"^(Argued|Submitted|Reargued|Opinion Issued|Opinion Filed|Issued"
    r"|Decided):\s*(.+)$", re.I)
_DATE_CRIT = {"opinion issued": "decision_date", "opinion filed": "decision_date",
              "issued": "decision_date", "decided": "decision_date",
              "argued": "submitted", "reargued": "submitted",
              "submitted": "submitted"}
# The tribunal the appeal came from, printed at the rail above the docket and
# again in parentheses under the caption.
#
# A SUPERIOR COURT IS NAMED BY ITS COUNTY AND NOTHING ELSE. 29 of the 50
# records print the rail row as a bare county — 'Rockingham', 'Belknap',
# 'Hillsborough-northern judicial district' — with no court word in it at
# all, and a pattern built from court words missed every one of them. The
# cost was not one untinted row: an unclaimed row at the TOP of the block
# becomes the writing's first line, and core's 'a writing is never bisected'
# invariant (`pipeline.py` step 9b) then reunites every headmatter row below
# it into that writing. `state_v._zarella` shipped its docket, citation,
# caption, dates and all three appearances as body paragraphs, with a
# two-row headmatter left behind — and it graded C for the missing
# attorneys, not for the 15 rows that had been carried off.
#
# The ten counties are a closed vocabulary and the judicial-district
# qualifier Hillsborough alone carries is part of the name.
_COUNTIES = (r"Belknap|Carroll|Cheshire|Co[oö]s|Grafton|Hillsborough"
             r"|Merrimack|Rockingham|Strafford|Sullivan")
_TRIBUNAL = re.compile(
    r"\b(?:Board|Bureau|Commission|Committee|Department|Division|Council"
    r"|Superior Court|District Court|Probate|Circuit Court|Court"
    r"|Compensation Appeals)\b|^(?:%s)"
    r"(?:[-\s](?:northern|southern|eastern|western)?\s*"
    r"judicial\s+district)?\.?$" % _COUNTIES, re.I)
_PARENTHETICAL = re.compile(r"^\(.*\)$")
# A CONSOLIDATED DOCKET WRAPS. 'Case Nos. 2024-0187' sets its second number
# on the row below it, bare — and an unclaimed row inside the block is not a
# cosmetic loss: it becomes the document's FIRST writing. state_v._dunbar and
# state_v._miller each rendered a phantom one-line 'order' holding nothing
# but '2024-0188' beside the real majority, which is what the user saw as
# 'this isn't two writings'.
_DOCKET_WRAP = re.compile(r"^\d{4}-\d{3,4}[,;]?$")
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
# THE BYLINE WELDED TO ITS FIRST SENTENCE. The 2020 record in this corpus
# sets 'HANTZ MARCONI, J.  The defendant, Joshua L. Shaw, appeals his
# conviction …' as ONE row, so `_BYLINE` — which requires the row to hold
# nothing but the byline — never matched it and the APPEARANCES BAND NEVER
# CLOSED: once opened it claims every row until the byline, and it took the
# whole opinion, 95 rows over three pages, tagged `counsel`. Nothing else
# opened the writing either, so the record came back as an unsigned 'order'.
# The row itself is LEFT IN THE STREAM — core's parser reads the welded form
# correctly (`Byline(name='HANTZ MARCONI', title='Justice', end=17)`); what
# was missing was only this reader knowing where to stop.
_BYLINE_HEAD = re.compile(
    r"^(?:[A-Z][A-Za-z'’\-]+(?:\s+[A-Z][A-Za-z'’\-]+)*,\s*"
    r"(?:C\.\s?J\.|JJ?\.)|PER CURIAM\.)\s")


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


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

    # THE BLOCK DOES NOT STOP AT THE PAGE BREAK. `_MAX_PAGES` was declared
    # from the first version of this reader and never used: the rows came
    # from page 1 alone, so on the 12 records whose appearances run over
    # onto page 2 the band was cut at the break, and the entries below it
    # became the writing's opening paragraphs. state_v._zarella lists six
    # appearances — three parties and three amici — and shipped the last two
    # as body prose with no byline read at all.
    #
    # The walk still ends where it always did, at the court's own prose, so
    # a record whose opinion opens on page 1 never reaches the second page.
    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm, finder)]
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
    appearances: list[str] = []
    band = "ident"          # ident | caption | counsel
    for idx, group in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        _x1 = max(l.x1 for l in pieces)
        centred = (abs((first.x0 + _x1) / 2 - page1.width / 2) <= _AXIS_TOL
                   and (_x1 - first.x0) <= page1.width * _CENTRED_WIDTH_MAX)

        # THE NOTICE is everything above the masthead.
        if idx < mast:
            ctx.drop(pieces, "notice")
            continue
        if _PARA.match(text) or (band != "ident"
                                 and (_BYLINE.match(text)
                                      or _BYLINE_HEAD.match(text))):
            break                       # the paper begins
        if _TYPED_RULE.match(text):
            ctx.rule(first.page, tuple(p.id for p in pieces), typed=True)
            continue
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        # The wrap belongs to the docket above it, and to `other_dockets`.
        if ctx.crit.get("docket_number") and not ctx.crit.get("citation") \
                and _DOCKET_WRAP.match(text):
            ctx.crit.setdefault("other_dockets", []).append(
                text.rstrip(",;"))
            ctx.emit(pieces, "docket", centre=False)
            continue
        docket = _DOCKET.match(text)
        if docket:
            _dk = [t.strip() for t in docket.group(1).split(",") if t.strip()]
            ctx.crit.setdefault("docket_number", _dk[0])
            if _dk[1:]:
                ctx.crit.setdefault("other_dockets", _dk[1:])
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
        # representation on their own. A fresh entry is opened by the INDENT
        # once the dates are in, which is what catches the first line of the
        # first entry — its naming phrase is two lines further down.
        if band != "counsel" and ctx.crit.get("decision_date") \
                and abs(first.x0 - (body_x0 + _INDENT)) <= _INDENT_TOL:
            band = "counsel"
        if _COUNSEL.search(text) or _ORALLY.search(text) or band == "counsel":
            band = "counsel"
            appearances.append(text)
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
        # A CENTRED BLOCK'S FIRST LINE NEED NOT LOOK CENTRED. The caption is
        # set centred, but a long one wraps, and its first row then runs
        # nearly the full measure with its mid-point pulled off the axis:
        # 'IN THE MATTER OF MARIA CRISTINA JARERO PENICHET AND' sits 18pt
        # right of centre and 62% of the sheet wide, so both halves of the
        # centred test refuse it. What identifies it is not its position but
        # WHERE IN THE BLOCK IT STANDS — below the citation, above the first
        # date, which on this paper is the caption band and nothing else.
        if ctx.crit.get("citation") and not (ctx.crit.get("submitted")
                                             or ctx.crit.get("decision_date")):
            band = "caption"
            caption.append(text)
            ctx.emit(pieces, "caption")
            continue
        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess. It is left KNOWING the
        # cost: an unclaimed row at the top of the block becomes the
        # writing's first line, and core's step-9b invariant then reunites
        # the whole block into that writing.
        continue

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("case_name", " ".join(caption))
        ctx.crit.setdefault("parties", caption[:6])
    if below:
        ctx.crit.setdefault("lower_court", below[0])
    # TINTED IS NOT RECORDED. The appearances were identified and rendered in
    # place from the first version of this reader, but nothing ever wrote them
    # to `criteria.attorneys`, so 28 of the 50 records shipped with no
    # attorneys anywhere a query could reach — the single largest defect in
    # this court's grade. They stay where the page prints them AND are
    # recorded; a court that sets its appearances in the headmatter renders
    # them there, and what matters is that they were read.
    if appearances:
        ctx.crit["attorneys"] = " ".join(appearances)
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
