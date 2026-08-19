"""Supreme Court of Kentucky ('ky').

Everything unique to ky lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — Kentucky sets its masthead in DISPLAY TYPE and flushes its
party roles to the right margin. The block is closed by a drawn rule.

    ┌────────────────────────────────────────────────────────────────────┐
    │                          RENDERED:  SEPTEMBER 18, 2025             │  the release
    │                                       TO BE PUBLISHED              │  publication
    │                Supreme Court of Kentucky        32pt — the masthead │
    │                     2024-SC-0350-DG             the docket          │
    │ ADAM WHEELER; COURTNEY L.                            APPELLANTS    │
    │ GRAHAM; AND STRAUSE LAW                                            │  the caption,
    │ GROUP, PLLC                                                        │  roles flushed
    │            ON REVIEW FROM COURT OF APPEALS                         │  right
    │ V.                        NO. 2023-CA-1147                         │
    │            BULLITT CIRCUIT COURT NO. 20-CI-00486                   │  the courts below
    │ CITY OF PIONEER VILLAGE,                              APPELLEE     │
    │ KENTUCKY                                                           │
    │            OPINION OF THE COURT BY JUSTICE KELLER   who wrote       │
    │                      AFFIRMING                      what it did     │
    ├──────────────────────────── drawn rule ────────────────────────────┤
    │     This matter comes before the Court upon discretionary review … │
    └────────────────────────────────────────────────────────────────────┘

THE MASTHEAD IS THE ONLY ROW IN DISPLAY TYPE — 32pt against a 12pt paper —
so it is found by its size and its text together and never by an ordinal.
Above it stand two stamps the court flushes right: the release date
('RENDERED: …', which is the decision date) and the publication status
('TO BE PUBLISHED' / 'NOT TO BE PUBLISHED').

THE BLOCK IS THREE ZONES, not two. Kentucky sets the parties at the left
rail, flushes their ROLE to the right margin on the same line, and prints
the courts below CENTRED between one party group and the next:

    ADAM WHEELER; COURTNEY L.                          APPELLANTS
    GRAHAM; AND STRAUSE LAW              <- left rail       ^ right margin
    GROUP, PLLC
                 ON REVIEW FROM COURT OF APPEALS      <- centred
    V.                    NO. 2023-CA-1147
                 BULLITT CIRCUIT COURT NO. 20-CI-00486
    CITY OF PIONEER VILLAGE,                           APPELLEE
    KENTUCKY

So a row is read PIECE BY PIECE, never joined, or the role welds onto the
end of the party's name. And the two caption columns are PAIRED: a party
group and the role that labels it are emitted as one `CaptionBlock`, which
is this repo's structure for a block the page sets in two columns. A centred
row is none of the three columns' business, so it CLOSES the pending block
and stands on its own — which is exactly how the page reads, one party group
per court below.

THE DRAWN RULE CLOSES THE BLOCK. Measured over 50 records the page draws one
rule and it sits between the disposition and the first paragraph of the
opinion, so the walk stops there. Where no rule is drawn the walk stops at
the disposition instead, which is the last row the court prints in the block.

'OPINION OF THE COURT BY JUSTICE KELLER' is read as `author`: Kentucky
announces who wrote in the block rather than signing the opinion, and that
is exactly what `author` names. The row beneath it ('AFFIRMING',
'REVERSING AND REMANDING') is the `disposition`.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = re.compile(r"^Supreme Court of Kentucky$", re.I)
_DISPLAY_MIN = 18.0
_AXIS_TOL = 10.0
_MAX_PAGES = 2

_RENDERED = re.compile(r"^RENDERED:\s*(.+)$", re.I)
_PUBLICATION = re.compile(r"^(?:NOT\s+)?TO BE PUBLISHED$", re.I)
# '2024-SC-0350-DG' / '2025-SC-0094-WC' — the court's own number.
_DOCKET = re.compile(r"^\d{4}-SC-\d{4}(?:-[A-Z]{1,3})?"
                     r"(?:\s*(?:,|and|&)\s*\d{4}-SC-\d{4}(?:-[A-Z]{1,3})?)*$",
                     re.I)
# The party role, standing alone at the right margin.
_PARTY_ROLE = re.compile(
    r"^(?:APPELLANT|APPELLEE|MOVANT|RESPONDENT|PETITIONER|CROSS-APPELLANT"
    r"|CROSS-APPELLEE|REAL PARTY IN INTEREST|INTERVENOR|AMICUS CURIAE)S?$",
    re.I)
_PIVOT = re.compile(r"^V\.?$|^VS\.?$", re.I)
# Where the case came from, and its number there.
_ON_REVIEW = re.compile(
    r"^(?:ON REVIEW FROM|ON APPEAL FROM|ON TRANSFER FROM|ON CERTIFICATION"
    r"|APPEAL FROM)\b", re.I)
_BELOW_NO = re.compile(
    r"^(?:NO\.|NOS\.)\s*\d{4}-CA-\d{3,4}|CIRCUIT COURT\s+NOS?\.|"
    r"^(?:.*\b(?:CIRCUIT|DISTRICT|FAMILY|WORKERS)\b.*\bNOS?\.)", re.I)
_OPINION_BY = re.compile(
    r"^(?:OPINION (?:AND ORDER )?OF THE COURT|OPINION)\s+BY\b|^OPINION BY\b",
    re.I)
_PER_CURIAM = re.compile(r"^(?:OPINION (?:AND ORDER )?OF THE COURT\s*)?"
                         r"PER CURIAM\.?$", re.I)
_DISPO = re.compile(
    r"^(?:AFFIRMING|REVERSING|VACATING|REMANDING|DISMISSING|AFFIRMED"
    r"|REVERSED|VACATED|DENYING|GRANTING|SUSTAINING|MODIFYING|SET ASIDE)"
    r"[\w\s,;'’&/-]*\.?$", re.I)
_RIGHT_COL_MIN = 0.60          # of the measure — where the role column sits
# THE CLOSING APPEARANCES. Kentucky prints counsel at the END of the paper,
# under its own labels, below the sitting roster and the vote line. The
# labels are the landmark; the roster and the vote ARE the court's writing
# and are left in the opinion where the court put them.
_COUNSEL_LABEL = re.compile(
    r"^(?:COUNSEL|ATTORNEYS?|BRIEFS?)\s+FOR\b|^COUNSEL\s*:|^APPEARANCES", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="ky")
def read_headmatter_ky(model, geom, **_):
    """Read Kentucky's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(page1, finder)
    if len(rows) < 4:
        return NOTHING
    # THE DISPATCH: the masthead, in display type, somewhere in the opening
    # rows — never at a fixed index, because the two stamps above it are
    # printed on some records and not others.
    mast = None
    for idx, group in enumerate(rows[:6]):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD.match(text) and (group[0].size or 0.0) >= _DISPLAY_MIN:
            mast = idx
            break
    if mast is None:
        return NOTHING

    # THE DRAWN RULE CLOSES THE BLOCK.
    stop = min((r.top for r in page1.h_rules if r.top > 100.0),
               default=float("inf"))

    ctx = _Ctx()
    caption: list[str] = []
    below: list[str] = []
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text or pieces[0].top >= stop:
            break
        first = pieces[0]
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - page1.width / 2) <= _AXIS_TOL

        rendered = _RENDERED.match(text)
        if rendered:
            ctx.crit.setdefault("decision_date", _norm(rendered.group(1)))
            ctx.emit(pieces, "date", centre=False)
            continue
        if _PUBLICATION.match(text):
            ctx.emit(pieces, "publication", centre=False)
            continue
        if _MASTHEAD.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DOCKET.match(text):
            ctx.crit.setdefault(
                "docket", [t.strip() for t in re.split(r",|\band\b|&", text)
                           if t.strip()])
            ctx.emit(pieces, "docket")
            continue
        if _OPINION_BY.match(text) or _PER_CURIAM.match(text):
            ctx.crit.setdefault("author_line", text)
            ctx.emit(pieces, "author")
            continue
        if centred and _DISPO.match(text):
            ctx.emit(pieces, "disposition")
            continue
        if _ON_REVIEW.match(text) or _BELOW_NO.match(text):
            below.append(text)
            ctx.emit(pieces, "lower-court")
            continue

        # A ROW IN THREE ZONES is read piece by piece: the party stands at
        # the rail, its ROLE at the right margin, and a court below in the
        # middle — all three on one printed line.
        for piece in pieces:
            one = _norm(piece.plain)
            if not one:
                continue
            right = piece.x0 >= page1.width * _RIGHT_COL_MIN
            mid = (piece.x0 + piece.x1) / 2
            middle = (not right and piece.x0 > body_x0 + 20.0
                      and abs(mid - page1.width / 2) <= 60.0)
            if right and _PARTY_ROLE.match(one):
                ctx.cap_right(piece)
                continue
            if _BELOW_NO.match(one) or _ON_REVIEW.match(one) or middle:
                below.append(one)
                ctx.flush_caption()
                ctx.emit([piece], "lower-court")
                continue
            if _PIVOT.match(one):
                ctx.cap_left(piece)
                continue
            caption.append(one)
            ctx.cap_left(piece)
    ctx.flush_caption()

    if not ctx.crit.get("docket"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("parties", caption[:8])
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
    _read_closing_counsel(ctx, model, finder)
    return ctx.result()


def _read_closing_counsel(ctx, model, finder) -> None:
    """The appearances Kentucky prints at the END of the paper.

        COUNSEL FOR APPELLANTS:
        Courtney L. Graham
        Strause Law Group PLLC

        COUNSEL FOR APPELLEE:
        Mark Edward Edison

    Claimed from the first label DOWN, and no further up: the rows above it
    ('Lambert, C.J.; … JJ., sitting.' and 'All concur. Goodwine, J., not
    sitting.') are the court's own closing lines — the panel and the vote —
    and they belong to the writing, not to a roster.
    """
    pm = model.pages[-1]
    lines = [l for l in sorted(pm.lines, key=lambda l: (l.top, l.x0))
             if l.plain.strip() and not finder.kind(pm, l)]
    start = next((i for i, l in enumerate(lines)
                  if _COUNSEL_LABEL.match(_norm(l.plain))), None)
    if start is None:
        return
    for line in lines[start:]:
        ctx.attorneys.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role="counsel"))
        ctx.consumed.add(line.id)


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
        self._left: list = []
        self._right: list = []
        self.attorneys: list = []

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        # A ROW THAT IS NOT THE CAPTION closes the pending pair: emitted
        # after it, the caption would render below a row the page prints
        # beneath it.
        if role != "caption":
            self.flush_caption()
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

    # ---- the paired caption ----------------------------------------------
    def _row(self, line, role: str):
        return m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role)

    def cap_left(self, line) -> None:
        self._left.append(self._row(line, "caption"))
        self.consumed.add(line.id)

    def cap_right(self, line) -> None:
        self._right.append(self._row(line, "caption"))
        self.consumed.add(line.id)

    def flush_caption(self) -> None:
        """A party group and the role that labels it are ONE block. With no
        role beside it the group is just rows — a CaptionBlock with an empty
        column would draw a gutter the page does not print."""
        if self._left and self._right:
            self.items.append(m.CaptionBlock(
                left=list(self._left), right=list(self._right), rail=None,
                prov=self._left[0].prov))
        else:
            self.items.extend(self._left or self._right)
        self._left, self._right = [], []

    def result(self) -> dict:
        self.flush_caption()
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
