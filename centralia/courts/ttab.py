"""Trademark Trial and Appeal Board ('ttab') — an ADMINISTRATIVE BOARD.

Everything unique to ttab lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE BOARD STAMPS ITS OWN PAPER, and the stamp is the first thing on the page:

    THIS OPINION IS A            <- the Board's PUBLICATION STATUS, stated
    PRECEDENT OF THE TTAB           about this paper, in its own words

That is not boilerplate. `This Opinion is a Precedent of the TTAB` and its
twin `… is Not a Precedent …` are the Board's precedential designation — the
thing that decides whether the decision binds later panels — and the Board
prints it on 31 of the 32 records here (22 say OPINION, 9 say ORDER; the
thirty-second is a REDESIGNATION cover, which carries no stamp of its own
and staples the stamped decision behind it). It is read as
`publication_status` and as `doc_type_final`: the paper names its own kind,
and nothing else on the page does.

TWO PAPERS, TWO LAYOUTS. Which one this is, is decided by a MEASUREMENT of
the top band, never by the words in it — both open on the same six words.

FORMAT A — 'centred slip' (23 of 32). The agency banner is set CENTRED on
the page axis at body size, and the sections below it are fenced by TYPED
rules the Board strikes on that same axis ('_____', '————', 30-48pt wide,
centred within 3pt of 306.0):

    ┌───────────────────────────────────────────────────────────┐
    │                    This Opinion is a                      │  publication
    │                  Precedent of the TTAB                    │
    │  Hearing: May 22, 2025            Mailed: Sept 22, 2025   │  date(s)
    │        UNITED STATES PATENT AND TRADEMARK OFFICE          │  court
    │                        _____                              │
    │              Trademark Trial and Appeal Board             │  court
    │                        _____                              │
    │             El Roblar Investment Property LLC             │  caption
    │                          v.                               │
    │                      Bianca Roe                           │
    │                        _____                              │
    │                Opposition No. 91272200                    │  docket
    │                        _____                              │
    │  Wesley M. Mullen … of Mullen P.C.                        │  counsel
    │      for El Roblar Investment Property LLC.               │
    │  Curtis W. Herron … for Bianca Roe.                       │
    │                        _____                              │
    │  Before Larkin, Dunn, and Stanley,                        │  panel
    │      Administrative Trademark Judges.                     │
    │  Opinion by Larkin, Administrative Trademark Judge:       │  <- the STOP
    └───────────────────────────────────────────────────────────┘

FORMAT B — 'letterhead order' (8 of 32, plus the redesignation cover). No
centred banner: the agency's MAILING LETTERHEAD is set in the right half of
the page, and it is set SMALLER than the body (11.0-11.2pt against a 12.0pt
measure) — that size step, not the address wording, is what identifies it.
The Board's stamp stands beside it in the LEFT half at full body size, so
the two never merge:

    ┌───────────────────────────────────────────────────────────┐
    │                    │  UNITED STATES PATENT AND TRADEMARK … │  letterhead
    │  THIS ORDER IS A   │  Trademark Trial and Appeal Board     │  (11pt,
    │  PRECEDENT OF THE  │  P.O. Box 1451                        │   dropped as
    │  TTAB              │  Alexandria, VA 22313-1451            │   furniture)
    │                    │  General Contact Number: 571-272-8500 │
    │                    │  General Email: TTABInfo@uspto.gov    │
    │  Ferrell           │                                       │  initials
    │                       July 18, 2024                        │  date
    │                       Opposition No. 91285851              │  docket
    │                       Blizzard Entertainment, Inc.         │  caption
    │                             v.                             │
    │                       Ava Labs, Inc.                       │
    │  Before Rogers, Chief Administrative Trademark Judge, and  │  panel
    │  Heasley and Elgin, Administrative Trademark Judges.       │
    │  By the Board:                                             │  <- the STOP
    └───────────────────────────────────────────────────────────┘

The two formats print the SAME elements — stamp, dates, docket, caption,
panel — in a different ORDER (Format A captions above the docket, Format B
below it) and at a different measure. So the walk is landmark-driven rather
than positional: each row is asked what it is, and the format decides only
where the cover STARTS (at the centred banner, or at the first row below the
letterhead) and how wide the caption column is.

WHAT IS FURNITURE HERE. The mailing letterhead (six rows, 11pt, right of the
axis) and the Board employee's INITIALS at the body rail ('WBC', 'Ferrell',
'Vigil', 'mbm' — routing marks for the mailroom, 8 records) are recorded as
`Dropped`. Nothing else is: the stamp is a fact about the paper, and the
dates are the record's own.

THE PAPER'S TYPE. Core reads `Administrative Trademark Judge` through the
`opinion_by_headings` grammar ('Opinion by Pologeorgis, Administrative
Trademark Judge:'), which needs the office declared in `abbrev_titles` — see
courts/__init__.py. The Board's INSTITUTIONAL rulings are signed 'By the
Board:' / 'By the Trademark Trial and Appeal Board:' and by its
interlocutory attorneys ('Michael Webster, Managing Interlocutory
Attorney'); those are not judge bylines and core assembles them unsigned, so
the type comes from the stamp instead.

WHAT THIS FILE DOES NOT DO. Footnotes, paragraphing, the body's block
quotations and the running heads are all core's. The reader stops at the
byline and never reaches into a writing.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..profile import CourtProfile
from ..resolve.bylines import DEFAULT_ABBREV, BylineGrammar
from . import register

# THE BENCH'S OFFICE, spelled out. The Board's judges sign 'Opinion by
# Cataldo, Administrative Trademark Judge:' — an OPINION-BY heading, not a
# signature, so the grammar reads it through `opinion_by_headings`; that
# path names the office from `abbrev_titles`, which is why the full title is
# declared there as its own 'abbreviation'. Without it the office parses as
# nothing, every one of the 23 authored decisions assembles unsigned, and
# core types the paper 'order' (measured: 32 of 32 records came back
# 'order').
_ATJ = "Administrative Trademark Judge"
_TTAB_TITLES = (
    "Chief Administrative Trademark Judge",
    "Deputy Chief Administrative Trademark Judge",
    "Acting Deputy Chief Administrative Trademark Judge",
    _ATJ,
)
PROFILE = register(CourtProfile(
    "ttab", "Trademark Trial and Appeal Board",
    byline=BylineGrammar(
        style="prose",
        titles=_TTAB_TITLES,
        opinion_by_headings=True,
        abbrev_titles=tuple((t, t) for t in _TTAB_TITLES) + DEFAULT_ABBREV,
    ),
    rollout="migrated",
))

# How far off the page axis a row may sit and still be 'centred on it'. The
# Board's typed fences run 30-48pt wide and are struck within 1pt of 306.0;
# its banner rows centre within 3pt. 14pt leaves room for the ragged
# right-hand edge of a long centred party name.
_AXIS_TOL = 14.0
# The letterhead's OWN LEADING. Its rows sit 6.4-18.6pt apart; the cover
# below it opens 34.9pt down at the closest. 25pt separates the two on
# every record that prints one.
_LH_LEAD = 25.0
# The one row of the block that can only be a mailing address.
_PO_BOX = re.compile(r"^P\.?\s?O\.?\s+Box\b", re.I)
_MAX_PAGES = 2
# A typed fence: underscores or em/en dashes and nothing else.
_FENCE = re.compile(r"^[_—–‒\-¯]{2,}$")

_BANNER = "UNITED STATES PATENT AND TRADEMARK OFFICE"
_BOARD = "Trademark Trial and Appeal Board"

# THE BOARD'S OWN STAMP. Printed in two or three rows and in five different
# cases across the corpus ('THIS OPINION IS A', 'This Opinion is a', 'This
# Opinion Is A', 'This Opinion Is a', 'This opinion is a'), so it is matched
# case-insensitively and read as a RUN: the run opens on the 'THIS … IS'
# row and closes on the row that ends in 'TTAB'.
_STAMP_OPEN = re.compile(
    r"^THIS\s+(?P<kind>OPINION|ORDER|DECISION)\s+IS\s+(?:A|NOT\s+A)\s*$",
    re.I)
_STAMP_TAIL = re.compile(r"^(?:PRECEDENT\s+OF\s+THE(?:\s+TTAB)?|TTAB)\s*$",
                         re.I)
_STAMP_NOT = re.compile(r"\bIS\s+NOT\s+A\b", re.I)

# The dates the cover carries. 'Mailed:' is the decision date; a hearing
# date is the day the Board sat.
_MAILED = re.compile(
    r"^(?:(?:Original\s+Decision|Redesignation|Reissued|Corrected)\s+)?"
    r"Mailed\s*:\s*(?P<date>.+?)\s*$", re.I)
_HEARING = re.compile(r"^(?:Oral\s+)?Hearing\s*:\s*(?P<date>.+?)\s*$", re.I)
# Format B sets the mailing date bare, with no label.
_BARE_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")

# THE PROCEEDING NUMBERS. A closed list of the Board's own proceeding
# KINDS — never the number's shape, which changes between them
# ('91285851', '2022-100137E for Registration No. 5376467').
_DOCKET = re.compile(
    r"^(?P<kind>Opposition|Cancellation|Serial|Reexamination|Expungement"
    r"|Concurrent\s+Use|Petition|Application|Registration)\s+Nos?\.?\s*"
    r"(?P<rest>.*)$", re.I)
# A runover row of bare numbers under 'Opposition Nos.' (mountain_gateway
# lists a parent and a child proceeding, one to a row).
_BARE_NOS = re.compile(r"^\d[\d\-]{4,}[A-Z]?(?:\s*\([^)]+\))?$")

# THE EX PARTE CAPTION is one row and names itself.
_IN_RE = re.compile(r"^In re\b", re.I)
_PIVOT = re.compile(r"^v\.?$", re.I)

_PANEL = re.compile(r"^Before\b", re.I)

# THE BOARD'S BYLINES — the STOP, not the parse. Four forms:
#   'Opinion by Cataldo, Administrative Trademark Judge:'  (a judge)
#   'By the Board:' / 'By the Trademark Trial and Appeal Board:'
#   'Michael Webster, Managing Interlocutory Attorney'     (one row)
#   'M. Catherine Faint,' / 'Interlocutory Attorney:'      (two rows)
_BYLINE = re.compile(
    r"^(?:Opinion|Decision|Order)\s+by\s+.+?[:.]?\s*\d{0,2}$", re.I)
_BY_THE_BOARD = re.compile(
    r"^By\s+the\s+(?:Board|Trademark\s+Trial\s+and\s+Appeal\s+Board)\s*:",
    re.I)
# The offices a Board attorney signs an interlocutory order under. Narrow on
# purpose: the panel roster ('… Administrative Trademark Judges.') and the
# examining attorney's counsel entry ('Andrea Cornwell, Trademark Examining
# Attorney, Law Office 115,') both end in a comma-title and would otherwise
# read as bylines and open a writing at the caption.
_SIGNER_OFFICES = (
    "Interlocutory Attorney",
    "Managing Interlocutory Attorney",
    "Supervisory Interlocutory Attorney",
    "Paralegal Specialist",
)
_SIGNER_ONE = re.compile(
    r"^[A-Z][A-Za-z.'’\- ]{2,40},\s*(?:" +
    "|".join(re.escape(o) for o in _SIGNER_OFFICES) + r")\s*:?\s*$")
_SIGNER_NAME = re.compile(r"^[A-Z][A-Za-z.'’\- ]{2,40},\s*$")
_SIGNER_OFFICE = re.compile(
    r"^(?:" + "|".join(re.escape(o) for o in _SIGNER_OFFICES) + r")\s*:\s*$")

# A COUNSEL ENTRY closes on a period; its continuation is indented from the
# body rail. The block is bounded by the fences either side of it, so no
# wording test opens it — but the ' for <party>.' tail is what tells the two
# sides apart when the criteria are built.
_FOR_PARTY = re.compile(r"\bfor\s+(?P<who>[^,]+?)\.\s*\d?\s*$")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _flat(row) -> str:
    return _norm(re.sub(r"<[^>]+>", "", getattr(row, "text", "") or ""))


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.doc_type = None
        self.body_x0 = 72.0
        self.width = 612.0

    def emit(self, group: list, role: str, centre: bool = False,
             right: bool = False) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        align = (m.Align.CENTER if centre
                 else m.Align.RIGHT if right else m.Align.LEFT)
        # A LEFT row set in from the rail keeps its indent. The Board's
        # counsel continuations stand 16-22pt in, and its letterhead-order
        # cover sets the whole caption 216pt in — reproduce both, as core's
        # shared walk does for the rows it places.
        rel = 0.0
        if align is m.Align.LEFT and first.x0 > self.body_x0 + 12:
            rel = min(first.x0 - self.body_x0, self.width * 0.6)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        self.consumed.update(p.id for p in parts)

    def rule(self, group: list) -> None:
        self.items.append(m.Rule(
            prov=m.Prov(group[0].page, tuple(l.id for l in group)),
            span="full", typed=True))
        self.consumed.update(l.id for l in group)

    def drop(self, group: list, kind: str) -> None:
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in group))[:400],
            prov=m.Prov(group[0].page, tuple(l.id for l in group)),
            kind=kind))
        self.consumed.update(l.id for l in group)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": self.doc_type}


def _rows(pm, finder) -> list[list]:
    """The page's inked rows, furniture removed, grouped by baseline. A
    justified row that pdfio split at a wide gap comes back as one group —
    the Board sets its docket label and its number in one row and 28pt
    apart ('Opposition Nos.' / '91283412 (parent)')."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        key = round(line.top, 0)
        hit = next((k for k in groups if abs(k - key) <= 1.0), None)
        if hit is None:
            groups[key] = []
            order.append(key)
            hit = key
        groups[hit].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _centred(pieces, width: float) -> bool:
    lo = min(l.x0 for l in pieces)
    hi = max(l.x1 for l in pieces)
    return abs((lo + hi) / 2 - width / 2) <= _AXIS_TOL


def _letterhead(rows: list) -> list:
    """The agency's MAILING letterhead, as a run of PIECES in one column.

    Anchored on the one row that can only be a mailing address ('P.O. Box
    1451'), and bounded by its OWN LEADING: the block sets 6.4-18.6pt
    between its rows and stands 34.9-43.2pt clear of the cover beneath it,
    so a 25pt fence separates the two on all nine records that print one.
    Size is not the test — the letterhead is 11.0-11.2pt on eight of them
    and full 12.0pt body measure on the ninth (august_storck), where a
    size rule read the address block as the caption."""
    at_col: list = []
    col = None
    for group in rows:
        for line in group:
            if col is None and _PO_BOX.match(_norm(line.plain)):
                col = line.x0
    if col is None:
        return []
    for group in rows:
        at_col.extend(l for l in group if abs(l.x0 - col) <= 3.0)
    at_col.sort(key=lambda l: l.top)
    i = next(i for i, l in enumerate(at_col)
             if _PO_BOX.match(_norm(l.plain)))
    lo = i
    while lo > 0 and at_col[lo].top - at_col[lo - 1].top <= _LH_LEAD:
        lo -= 1
    hi = i
    while hi + 1 < len(at_col) \
            and at_col[hi + 1].top - at_col[hi].top <= _LH_LEAD:
        hi += 1
    return [[l] for l in at_col[lo:hi + 1]]


def _is_mark(line, body_x0: float) -> bool:
    """A Board employee's ROUTING MARK at the body rail — 'WBC', 'Ferrell',
    'mbm', 'Vigil'. The mailroom's initials or the interlocutory attorney's
    surname, printed above the cover so the paper can be filed; 8 of the 32
    records carry one. One short all-alphabetic token at the rail, and it
    shares its row with the mailing date as often as it stands alone
    ('Vigil' beside 'Mailed: November 24, 2025'), so it is peeled off the
    row PIECE BY PIECE rather than tested whole."""
    if abs(line.x0 - body_x0) > 2.0:
        return False
    text = _norm(line.plain)
    return bool(text) and len(text) <= 14 and text.replace(" ", "").isalpha()


def _is_byline(text: str, nxt: str) -> bool:
    """The row the writing opens on — where this reader stops."""
    if _BY_THE_BOARD.match(text):
        return True
    if _BYLINE.match(text) and len(text) <= 90:
        return True
    if _SIGNER_ONE.match(text):
        return True
    if _SIGNER_NAME.match(text) and _SIGNER_OFFICE.match(nxt):
        return True
    return False


@decider("headmatter.read", court="ttab")
def read_headmatter_ttab(model=None, geom=None, **_):
    """Read the Board's cover — the centred slip or the letterhead order —
    or NOTHING."""
    if model is None or not model.pages:
        return NOTHING
    width = model.pages[0].width or 612.0
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    body_size = geom.body_size if geom and geom.body_size else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(model.pages[0], finder)
    if not rows:
        return NOTHING

    head = _letterhead(rows)
    head_ids = {l.id for g in head for l in g}
    # THE DISPATCH: the centred banner names Format A. Sought in the rows the
    # letterhead does not own, so the letterhead's own copy of the same six
    # words (flush left at x0 288, 11pt) cannot answer for it.
    banner_at = None
    for i, group in enumerate(rows):
        rest = [l for l in group if l.id not in head_ids]
        if not rest:
            continue
        if _norm(" ".join(l.plain for l in rest)).upper() == _BANNER \
                and _centred(rest, width):
            banner_at = i
            break
    if banner_at is None and not head:
        return NOTHING                      # not a paper this Board prints

    ctx = _Ctx()
    ctx.body_x0, ctx.width = body_x0, width
    style = "centred-slip" if banner_at is not None else "letterhead-order"
    # THE PAGE AXIS IS ONLY A MEASURE ON THE CENTRED SLIP. The letterhead
    # order sets its whole cover against a column rail at x0 288, and a
    # short party name there ('Zeeth Ltd.', ink 288.1-344.4) drifts within
    # 10pt of the axis and reads as centred to a page-wide test — rendering
    # one row of a left-aligned caption centred (the ca5 reading: measure
    # the rail INSIDE the band).
    axis = _centred if banner_at is not None else (lambda *_a: False)
    ctx.crit["headmatter_style"] = style
    ctx.crit["court"] = _BOARD
    for group in head:
        ctx.drop(group, "margin")

    caption_rows: list[str] = []
    counsel_text: list[str] = []
    stamp_open = False
    # THE COVER OPENS at the centred banner on Format A, and at the row
    # under the letterhead on Format B — which prints no banner of its own,
    # the agency's name being part of the mailing block that was just
    # dropped. Nothing above the Format-A banner but the stamp and the
    # dates is this reader's to name.
    band = "head" if banner_at is not None else "cover"
    seen_docket = False

    texts = [_norm(" ".join(l.plain for l in [x for x in g
                                              if x.id not in head_ids]))
             for g in rows]

    for i, group in enumerate(rows):
        pieces = [l for l in group if l.id not in head_ids]
        if not pieces:
            continue
        text = texts[i]
        if not text:
            continue
        nxt = next((texts[j] for j in range(i + 1, len(rows))
                    if texts[j]), "")

        # --- the mailroom's routing mark, peeled off its row -----------
        if not seen_docket and band in ("head", "cover"):
            marks = [l for l in pieces if _is_mark(l, body_x0)]
            if marks and len(marks) < len(pieces):
                ctx.drop(marks, "margin")
                pieces = [l for l in pieces if l not in marks]
                text = _norm(" ".join(l.plain for l in pieces))
            elif marks and not _STAMP_TAIL.match(text) \
                    and not _STAMP_OPEN.match(text):
                ctx.drop(marks, "margin")
                continue

        if _is_byline(text, nxt):
            break                                   # the writing begins

        if _FENCE.match(text) and _centred(pieces, width):
            ctx.rule(pieces)
            if band == "counsel":
                band = "panel-wait"
            continue

        # --- the Board's own stamp -------------------------------------
        opened = _STAMP_OPEN.match(text)
        if opened:
            stamp_open = True
            ctx.crit["publication_status"] = (
                "non-precedential" if _STAMP_NOT.search(text)
                else "precedential")
            ctx.doc_type = (m.DocType.ORDER
                            if opened.group("kind").upper() == "ORDER"
                            else m.DocType.OPINION)
            ctx.emit(pieces, "publication", centre=axis(pieces, width))
            continue
        if stamp_open and _STAMP_TAIL.match(text):
            ctx.emit(pieces, "publication", centre=axis(pieces, width))
            if text.rstrip(". ").upper().endswith("TTAB"):
                stamp_open = False
            continue
        stamp_open = False


        # --- the dates -------------------------------------------------
        mailed = _MAILED.match(text)
        hearing = _HEARING.match(text)
        if mailed or hearing or (_BARE_DATE.match(text) and not seen_docket):
            # A hearing date and a mailing date share one row.
            for part in pieces:
                pt = _norm(part.plain)
                mm = _MAILED.match(pt)
                if mm:
                    ctx.crit.setdefault("decision_date",
                                        _norm(mm.group("date")))
                elif _HEARING.match(pt):
                    ctx.crit.setdefault(
                        "submitted", _norm(_HEARING.match(pt).group("date")))
                elif _BARE_DATE.match(pt):
                    ctx.crit.setdefault("decision_date", pt)
            # A 'Mailed:' date set hard against the right margin is flush
            # right; the letterhead order's bare date sits in its caption
            # COLUMN and keeps that column's indent.
            right = bool(len(pieces) == 1 and pieces[0].x1 >= width - 80.0)
            ctx.emit(pieces, "date", right=right)
            continue

        # --- the agency and the Board naming themselves ----------------
        if text.upper() == _BANNER and _centred(pieces, width):
            ctx.emit(pieces, "court", centre=True)
            band = "cover"
            continue
        if text == _BOARD and _centred(pieces, width):
            ctx.emit(pieces, "court", centre=axis(pieces, width))
            band = "cover"
            continue
        if band == "head":
            continue        # above the cover: not this reader's to name

        # --- the proceeding numbers ------------------------------------
        dk = _DOCKET.match(text)
        if dk:
            seen_docket = True
            band = "docket"
            _add_docket(ctx, text)
            ctx.emit(pieces, "docket", centre=axis(pieces, width))
            continue
        if band == "docket" and _BARE_NOS.match(text):
            ctx.crit.setdefault("other_dockets", []).append(text)
            ctx.emit(pieces, "docket", centre=axis(pieces, width))
            continue

        # --- who sat ---------------------------------------------------
        if _PANEL.match(text) or band == "panel":
            band = "panel"
            if "panel_line" in ctx.crit:
                ctx.crit["panel_line"] = _norm(
                    f"{ctx.crit['panel_line']} {text}")
            else:
                ctx.crit["panel_line"] = text
            ctx.crit["judges"] = re.sub(r"^Before\s+", "",
                                        ctx.crit["panel_line"], flags=re.I)
            ctx.emit(pieces, "panel")
            continue

        # --- the caption, and the appearances --------------------------
        # THE CAPTION IS CENTRED on Format A and set at the letterhead
        # column on Format B; the appearances are always at the BODY RAIL,
        # and only Format A prints them. That is the whole distinction, and
        # it is a column test.
        at_rail = min(l.x0 for l in pieces) <= body_x0 + 2.0
        if band in ("cover", "docket") and not at_rail:
            caption_rows.append(text)
            ctx.emit(pieces, "caption", centre=axis(pieces, width))
            continue
        if band in ("docket", "counsel", "panel-wait") and at_rail:
            band = "counsel"
            counsel_text.append(text)
            ctx.emit(pieces, "counsel")
            continue
        if band == "counsel":
            counsel_text.append(text)
            ctx.emit(pieces, "counsel")
            continue
        # A row at no position this cover uses is left to core.
        continue

    if not ctx.items:
        return NOTHING
    _finish(ctx, caption_rows, counsel_text)
    return ctx.result()


# The Board's own proceeding number, inside the row that prints it:
# '91277224', '2022-100137E'. What follows ' for ' is the REGISTRATION the
# proceeding is about, not a docket of its own.
_NUMBER = re.compile(r"\b\d[\w\-]{3,}\b")


def _add_docket(ctx, text: str) -> None:
    """'Opposition No. 91277224' / 'Opposition Nos. 91283412 (parent)' /
    'Expungement No. 2022-100137E for Registration No. 5376467'."""
    dk = _DOCKET.match(text)
    if not dk:
        return
    head = re.split(r"\s+for\s+", _norm(dk.group("rest")), maxsplit=1)[0]
    for num in _NUMBER.findall(head) or [_norm(dk.group("rest"))]:
        if not num:
            continue
        if "docket_number" not in ctx.crit:
            ctx.crit["docket_number"] = num
        elif num not in ctx.crit.get("other_dockets", []):
            ctx.crit.setdefault("other_dockets", []).append(num)


def _finish(ctx, caption_rows: list[str], counsel_text: list[str]) -> None:
    """The parsed forms, built beside the printed ones."""
    if caption_rows:
        ctx.crit["caption"] = list(caption_rows)
        left: list[str] = []
        right: list[str] = []
        side = left
        pivoted = False
        caption_rows = [re.sub(r"\s*\d{1,2}$", "", r) for r in caption_rows]
        for row in caption_rows:
            if _PIVOT.match(row):
                side = right
                pivoted = True
                continue
            side.append(row)
        if pivoted and left and right:
            ctx.crit["parties"] = [_norm(" ".join(left)).rstrip(","),
                                   _norm(" ".join(right)).rstrip(",")]
            ctx.crit["case_name"] = " v. ".join(ctx.crit["parties"])
        else:
            # AN EX PARTE APPEAL HAS ONE SIDE. 'In re Gail Weiss' is the
            # whole case name, and rendering `parties` as 'A v. B' would
            # invent an adversary — so the single row is the case name and
            # `parties` stays empty.
            ctx.crit["case_name"] = _norm(" ".join(caption_rows))
    if counsel_text:
        ctx.crit["attorneys"] = " ".join(counsel_text)[:2000]
