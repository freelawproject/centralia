"""Court of Appeals of Georgia ('gactapp').

Everything unique to gactapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACTS. This court prints TWO papers and, like its Supreme Court
sibling, each one names itself by HOW IT SETS ITS OWN NAME on page 1.
Nothing is decided by what a case is called or by what kind of relief the
paper grants:

    'order sheet' (37 of 42) — the court's letterhead, engraved in TWO
    bold rows AT THE BODY RAIL above body size ('Court of Appeals' over
    'of the State of Georgia'), then a dateline, then the formula the
    clerk types before every order, then the docket-and-caption in bold
    caps.  THE ORDER ITSELF IS THE WRITING and the reader stops above it:

        Court of Appeals                      the letterhead, 21pt bold…
        of the State of Georgia               …in two rows, at x0=72
        July 31, 2026                         the release date…
        ATLANTA,____________________          …typed over its fill rule
        The Court of Appeals hereby passes the following order:
                                              the formula — apparatus
        A26D0635. AMANDA BRANCH v. RAM PARTNERS, LLC A/A/F SUTTER
        LAKE.                                 the docket and its caption
        Ram Partners, LLC a/a/f Sutter Lake brought this …   THE ORDER

    The same sheet is set at two measures — a 21pt letterhead on a 14pt
    body for the orders the judges write, a 20pt letterhead on a 12pt
    body for the clerk's minute orders — and the smaller one prints its
    dateline WHOLE on one row ('ATLANTA, August 11, 2026') where the
    larger one types the date above an underscore fill rule.  Both fall
    out of one dateline test; neither needs its own contract.

    'opinion cover' (5 of 42) — the signed opinion. There is no
    letterhead: the court names itself in ONE 21pt row at the rail, and
    everything above that row is the bench and the reporter's notice:

        FIRST DIVISION                        the division, on the axis
        BARNES, P. J.,                        …and its roster, two rows
        MARKLE and HODGES, JJ.
        NOTICE: Motions for reconsideration must be …   the 9–10pt
                                          advisory, claimed and dropped
        May 22, 2026                          the release, flush right
        In the Court of Appeals of Georgia    the court, 21pt, at x0=72
        A26A0830. COLL v. KELLY.              docket + caption, one row
        MARKLE, Judge.                        …and the writing starts

THE DISPATCH is one question about page 1: WHERE the court sets its own
name, and in how many rows.  Two bold rows above body size at the rail
open the order sheet; ONE row above body size at the rail opens the
opinion cover.  Over 42 records the two tests are exclusive and total.

THE FURNITURE THE CLAIM INHERITS.  Two pieces, both recorded, never
silently cut:

  * the FORMULA ('The Court of Appeals hereby passes the following
    order:') is the clerk's convening recital in Georgia's words — core
    already drops ca2's ('At a stated term of the United States Court of
    Appeals…') and ga's ('The Honorable Supreme Court met pursuant to
    adjournment') — so it is claimed and recorded as a recital.  One
    record (laborian_williams) prints the release date at the END of that
    row instead of above the fill rule; the date is taken out of it and
    merged into the dateline before the rest is dropped.
  * the RECONSIDERATION NOTICE on the opinion cover — four rows at 9 or
    10pt against a 14pt body.  Core's notice peel runs only on rows a
    reader left behind AND runs after assembly, so a reader that claims
    the block around it has to claim it too.

THE DATELINE IS ONE ROW OF THE PAGE SET IN TWO.  The 14pt sheet types
'ATLANTA,' followed by an underscore fill rule and prints the date ABOVE
the rule, so pdfio reads two rows where the page shows one line; they are
merged by position into a single 'date' row ('ATLANTA, July 31, 2026'),
with both line ids in its provenance.  This is the one merge in this
file, and it is the printed line being reassembled, not an append.

gactapp prints NO appearance of counsel anywhere in the corpus — no
roster, no 'Attorneys for', on any page of any of the 42 records (every
'attorney' in the corpus is prose about attorney fees) — so a missing
counsel section here is the paper, not a defect.

No record in this corpus carries an undecodable (cid:N) glyph.

KNOWN CORE DEFECT, NOT REPAIRED HERE (1 of 42, landren_gipson).  A
claimed headmatter leaves a body-only stream, and where no byline signs
it `assemble` falls back to hunting a doc-type HEADING — a short line
whose text classifies as ORDER / JUDGMENT.  A paragraph's own LAST line
is naturally short, and this record's reads 'order was entered, we
decline to transfer the application.', which clears the 0.8-of-measure
guard and classifies as ORDER.  The `headmatter_claimed` rule then keeps
that anchor beside `_body0` and cuts one order in two at the page break.
Core already drops such an anchor when the line is a bare disposition
(mass murray, mass gorbatova) and its own comment says dropping it 'can
only ever merge the two starts back into one'; the fix is to drop the
`_is_dispo_line` conjunct so ANY doc-type heading below the first
remaining segment is ignored under a claimed headmatter.  Proved by
monkey-patching that conjunct true: landren_gipson goes 2 writings -> 1
and no other gactapp record changes.  It belongs in assemble.py, not
here.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# gactapp's profile is registered in the shared table; this file owns its
# headmatter contract only. (Taken, never re-registered — a second
# `register()` for the same id raises and breaks the import for EVERY
# court.)
GACTAPP: CourtProfile = PROFILES["gactapp"]

STYLE_ORDER = "order sheet"
STYLE_COVER = "opinion cover"

# ---- gactapp's declared facts (measured over all 42 records) -------------
# THE COURT'S OWN NAME is the only thing on any page-1 above body size: the
# letterhead is 21pt (26 records) or 20pt (11), the cover's single row is
# 21pt, and the body under them is 14pt or 12pt. Nothing else on any of the
# 42 first pages reaches 18pt.
_MASTHEAD_MIN = 18.0
# THE RECONSIDERATION NOTICE is set UNDER the body — 10pt against 14 on
# four covers, 9pt on the fifth. The band, not its wording, is what
# separates it from the roster above it.
_NOTICE_MAX = 10.5
# A ROW IS AT THE RAIL when it starts on the body's left edge. Both papers
# set the court's name there and nothing else in the block does.
_RAIL = 72.0
_RAIL_TOL = 2.0
# THE COVER'S BENCH BLOCK IS CENTRED ON THE PAGE AXIS — over the five
# covers every roster row's midpoint sits within 0.2pt of 306.0. The
# release date beside it does not (c=457 / c=502), which is what tells
# them apart without reading either.
_AXIS_TOL = 6.0
# HOW FAR THE BLOCK MAY RUN. Both papers close on page 1: the order sheet
# because its order starts there, the cover because it is a cover.
_MAX_PAGES = 1
# HOW FAR DOWN THE COURT MAY NAME ITSELF. The cover sets three roster rows
# and a four-row notice above its name; the letterhead opens the page.
_HEAD_WINDOW = 10

# THIS COURT'S OWN DOCKET, always printed as the LEADER of the caption row:
# 'A26A2022' (appeal), 'A26D0635' (discretionary application), 'A26I0274'
# (interlocutory), 'A26O0014' (original), 'A27E0005' (emergency) — the term
# year, the docket letter, the sequence.
_DOCKET_LEAD = re.compile(r"^(A\d{2}[A-Z]\d{4})\.\s+(.+)$")
_MONTH = (r"(?:January|February|March|April|May|June|July|August|"
          r"September|October|November|December)")
_DATE = rf"{_MONTH}\s+\d{{1,2}},\s+\d{{4}}"
# The release date standing alone above the fill rule.
_DATE_ROW = re.compile(rf"^({_DATE})\.?$")
# The seat, with or without the date the 12pt sheet prints beside it, and
# with or without the underscore fill rule the 14pt sheet types after it.
_SEAT_ROW = re.compile(rf"^ATLANTA,\s*_*\s*({_DATE})?\s*_*$")
# …and the date where laborian_williams prints it: at the end of the
# formula's own row.
_TAIL_DATE = re.compile(rf"\s*({_DATE})\s*$")
# THE FORMULA the clerk types before every order — this court's convening
# recital. Matched as a PREFIX because one record prints the date after it
# and the 12pt sheet omits the colon.
_FORMULA = "the court of appeals hereby passes the following order"
# The reporter's advisory that opens the notice band on every cover.
_NOTICE_CUE = "notice:"
# The court naming itself, in each paper's words.
_COURT_ROW = "in the court of appeals of georgia"
_LETTERHEAD = ("court of appeals", "of the state of georgia")
# The bench's own division, as the cover heads it. A closed structural
# vocabulary — the court's five divisions — never a name.
_DIVISION = re.compile(
    r"^(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH)\s+DIVISION$")
# THE BENCH TITLES this court sets in its roster. A finite role vocabulary;
# what is left after they are struck out is a judge.
_BENCH_TITLES = ("P. J.", "PRESIDING JUDGE", "C. J.", "CHIEF JUDGE",
                 "SENIOR JUDGE", "SENIOR APPELLATE JUDGE", "JUDGE",
                 "JJ.", "J.")
# gactapp signs prose ('MARKLE, Judge.' / 'BARNES, Presiding Judge.').
# The byline ends the cover's reader; the order sheet has none and ends on
# the first row the court did not set in bold.
_BYLINE = BylineGrammar(style="prose",
                        titles=("Judge", "Presiding Judge", "Chief Judge"))


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the rows
# --------------------------------------------------------------------------

class _Ctx:
    """What the two walks share: the page models and the emit buffer."""

    def __init__(self, model, geom, pages, body_size):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.items: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, group: list, role: str, align: str | None = None,
             text: str | None = None, extra: list | None = None) -> None:
        """One headmatter row.

        ``text`` overrides what the row PRINTS (the dateline is one printed
        line pdfio reads as two, and the seat's underscore fill rule is not
        text); ``extra`` carries provenance for lines whose glyphs the
        override already accounts for. Geometry always comes from ``group``.
        """
        parts = sorted(group, key=lambda l: l.x0)
        first = parts[0]
        pm = self.pages[first.page]
        if text is None:
            text = ""
            for part in parts:
                piece = line_markup(part)
                text = (text.rstrip() + " " + piece.lstrip()) \
                    if text.strip() else piece
        if align is None:
            align = line_alignment(first, pm.width, self.geom,
                                   banner_center_min_size=self.body_size + 1.0)
        ids = tuple(p.id for p in parts) + tuple(
            l.id for l in (extra or []))
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, ids),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts),
            italic=all(bool(getattr(p, "all_italic", False)) for p in parts),
            role=role))
        self.consumed.update(ids)

    def drop(self, group: list, kind: str, text: str | None = None) -> None:
        ids = tuple(l.id for l in group)
        if text is None:
            text = _norm(" ".join(l.plain for l in group))
        self.dropped.append(m.Dropped(text=text[:1200],
                                      prov=m.Prov(group[0].page, ids),
                                      kind=kind))
        self.consumed.update(ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


def _rows(model, finder, max_pages: int) -> list[list]:
    """Content rows in page order, same-row pieces rejoined, furniture out."""
    out: list[list] = []
    for pm in model.pages[:max_pages]:
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            key = line.row if line.row is not None else round(line.top)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        out.extend(groups[k] for k in order)
    return out


def _text(group: list) -> str:
    return _norm(" ".join(l.plain for l in sorted(group, key=lambda l: l.x0)))


def _size(group: list) -> float:
    return max((l.size or 0.0) for l in group)


def _bold(group: list) -> bool:
    return all(bool(l.all_bold) for l in group)


def _at_rail(group: list) -> bool:
    return abs(min(l.x0 for l in group) - _RAIL) <= _RAIL_TOL


def _side(group: list, width: float) -> str:
    """Which side of the page axis the row's own measure sits on. The
    dateline is set right on both sheets and core reads it as left, because
    it stops short of the right margin by the width of the fill rule."""
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return "R" if (x0 + x1) / 2 > width / 2 else "L"


def _centred(group: list, width: float) -> bool:
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL


# --------------------------------------------------------------------------
# the dispatch
# --------------------------------------------------------------------------

@decider("headmatter.read", court="gactapp")
def read_headmatter_gactapp(model, geom, **_):
    """Read one of Georgia's two appellate papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    # geom is None on the shortest minute orders (a one-page sheet whose
    # body is four lines gives the measurer nothing to measure). Both of
    # this court's papers set the rail at 72.0 and the body at 12 or 14pt,
    # and the walk below reads sizes RELATIVE to nothing but the masthead,
    # so the fallbacks are only used for alignment and the notice test.
    body_size = geom.body_size if geom else 12.0
    body_x0 = geom.body_x0 if geom else _RAIL
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _rows(model, finder, _MAX_PAGES)
    if len(rows) < 4:
        return NOTHING
    pages = {pm.number: pm for pm in model.pages}
    ctx = _Ctx(model, geom, pages, body_size)

    p1 = [g for g in rows if g[0].page == 1]
    big = [i for i, g in enumerate(p1[:_HEAD_WINDOW])
           if _size(g) >= _MASTHEAD_MIN]
    if not big:
        return NOTHING
    # THE LETTERHEAD: two consecutive rows above body size at the rail,
    # naming the court across both of them.
    if (len(big) >= 2 and big[0] == 0 and big[1] == 1
            and [_text(p1[0]).lower(), _text(p1[1]).lower()]
            == list(_LETTERHEAD)
            and _at_rail(p1[0]) and _at_rail(p1[1])):
        return _read_order(ctx, rows)
    # THE COVER: one row above body size at the rail, naming the court whole.
    if (len(big) == 1 and _text(p1[big[0]]).lower() == _COURT_ROW
            and _at_rail(p1[big[0]])):
        return _read_cover(ctx, rows, big[0])
    return NOTHING


# --------------------------------------------------------------------------
# the order sheet
# --------------------------------------------------------------------------

def _read_order(ctx: _Ctx, rows: list):
    """The letterhead sheet: the court's name, the dateline, the clerk's
    formula, and the docket-and-caption. The order below it is the writing."""
    p1 = [g for g in rows if g[0].page == 1]
    ctx.emit(p1[0], "court")
    ctx.emit(p1[1], "court")
    ctx.crit["court"] = f"{_text(p1[0])} {_text(p1[1])}"

    seat: list | None = None        # the 'ATLANTA,' row and its fill rule
    stamp: list | None = None       # the release date typed above the rule
    date: str | None = None
    dockets: list[str] = []
    caption: list[str] = []
    state = "dateline"
    for group in p1[2:]:
        text = _text(group)
        if state == "dateline":
            mm = _DATE_ROW.match(text)
            if mm is not None and stamp is None:
                stamp = group
                continue
            mm = _SEAT_ROW.match(text)
            if mm is not None and seat is None:
                seat = group
                date = date or mm.group(1)
                continue
            if not text.lower().startswith(_FORMULA):
                return NOTHING          # an unread row inside the dateline
            # THE FORMULA CLOSES THE DATELINE. Flush what the dateline
            # collected as ONE row — it is one printed line — taking the
            # date off the formula's own row first where that is where the
            # sheet put it.
            tail = _TAIL_DATE.search(text)
            recital, carried = text, None
            if tail is not None:
                date = date or _norm(tail.group(1))
                recital = text[:tail.start()].rstrip()
                carried = group
            if date is None and stamp is not None:
                date = _norm(_text(stamp)).rstrip(".")
            if seat is not None:
                ctx.emit(seat, "date", _side(seat, ctx.pages[1].width),
                         text=f"ATLANTA, {date}" if date else "ATLANTA,",
                         extra=(stamp or []) + (carried or []))
            elif stamp is not None:
                ctx.emit(stamp, "date", _side(stamp, ctx.pages[1].width),
                         text=date, extra=(carried or []))
            if date:
                ctx.crit["decision_date"] = date
            ctx.drop(group, "recital", text=recital)
            state = "caption"
            continue
        # THE CAPTION BLOCK is the only bold matter on the sheet, and it
        # ends where the court stops setting bold — which is the first line
        # of the order. Nothing is read out of the order.
        if not _bold(group):
            break
        if not dockets:
            mm = _DOCKET_LEAD.match(text)
            if mm is None:
                return NOTHING      # bold, but not this court's docket
            dockets.append(mm.group(1))
            caption.append(_norm(mm.group(2)))
        else:
            caption.append(text)
        ctx.emit(group, "caption")
    if state != "caption" or not dockets:
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_ORDER
    _record(ctx, dockets, caption)
    return ctx.result()


# --------------------------------------------------------------------------
# the opinion cover
# --------------------------------------------------------------------------

def _read_cover(ctx: _Ctx, rows: list, court_at: int):
    """The signed opinion's cover: the bench, the notice, the release date,
    the court's name, and the docket-and-caption. The byline ends it."""
    p1 = [g for g in rows if g[0].page == 1]
    page1 = ctx.pages[1]
    roster: list[str] = []
    notice: list = []
    date: str | None = None
    division: str | None = None
    for group in p1[:court_at]:
        text = _text(group)
        # THE NOTICE BAND is set under the body and closes the bench block.
        if _size(group) <= _NOTICE_MAX:
            if not notice and not text.lower().startswith(_NOTICE_CUE):
                return NOTHING
            notice.append(group)
            continue
        if notice:
            # After the notice only the release date stands above the name.
            mm = _DATE_ROW.match(text)
            if mm is None or date is not None:
                return NOTHING
            date = _norm(mm.group(1))
            ctx.crit["decision_date"] = date
            ctx.emit(group, "date", _side(group, page1.width))
            continue
        if not _centred(group, page1.width):
            return NOTHING          # the bench block is on the axis
        if _DIVISION.match(text):
            division = text
            ctx.emit(group, "court", "C")
            continue
        roster.append(text)
        ctx.emit(group, "panel", "C")
    if not notice or not roster:
        return NOTHING
    ctx.drop([l for g in notice for l in g], "notice")
    ctx.emit(p1[court_at], "court")
    name = _text(p1[court_at]).removeprefix("In the ")
    ctx.crit["court"] = f"{name}, {division}" if division else name

    if court_at + 2 >= len(p1):
        return NOTHING
    mm = _DOCKET_LEAD.match(_text(p1[court_at + 1]))
    if mm is None:
        return NOTHING
    ctx.emit(p1[court_at + 1], "caption")
    if BylineParser(_BYLINE).parse(_text(p1[court_at + 2])) is None:
        return NOTHING              # the cover must hand over to a byline
    ctx.crit["panel_line"] = _norm(" ".join(roster))
    panel = _panel(roster)
    if panel:
        ctx.crit["panel"] = panel
    ctx.crit["headmatter_style"] = STYLE_COVER
    _record(ctx, [mm.group(1)], [_norm(mm.group(2))])
    return ctx.result()


def _panel(roster: list[str]) -> list[str]:
    """The bench, from the roster's own words: strike the closed set of
    bench titles and what is left is a judge. Never a wording guess — if a
    piece does not read as a plain surname the parse is abandoned and only
    the printed `panel_line` survives."""
    out: list[str] = []
    for piece in re.split(r",|\band\b", " ".join(roster)):
        name = _norm(piece).rstrip(".,")
        for title in _BENCH_TITLES:
            low, tl = name.upper(), title.rstrip(".")
            if low == tl or low + "." == title:
                name = ""
                break
            if low.startswith(title + " "):
                name = name[len(title) + 1:]
        name = _norm(name).rstrip(".,")
        if not name:
            continue
        if not re.fullmatch(r"[A-Z][A-Za-z'\-]+", name):
            return []
        out.append(name)
    return out


# --------------------------------------------------------------------------
# what the page said
# --------------------------------------------------------------------------

def _record(ctx: _Ctx, dockets: list, caption: list) -> None:
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, caption)


def _name(ctx: _Ctx, caption: list) -> None:
    """The case's name, from the party names either side of the pivot this
    court always sets INSIDE the caption row — never by joining the rows and
    calling the result a name."""
    whole = _norm(" ".join(caption)).rstrip(". ")
    parts = re.split(r"(?<=\s)vs?\.\s", _norm(" ".join(caption)))
    if len(parts) == 2:
        one, two = (_norm(parts[0]).rstrip(", "),
                    _norm(parts[1]).rstrip(". ").rstrip(", "))
        if one and two:
            ctx.crit["parties"] = [one, two]
            ctx.crit["case_name"] = f"{one} v. {two}"
            return
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole
