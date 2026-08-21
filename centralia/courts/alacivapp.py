"""Court of Civil Appeals of Alabama ('alacivapp').

THE PAPER. Every one of the 30 records is the Alabama appellate slip
opinion — the same 'fenced cover' the Supreme Court of Alabama sets on
136 of its 467 (see ``ala.py``). The Court of Civil Appeals prints
NOTHING ELSE: no clerk's certificate of judgment, no judicial-department
release list. Measured over the corpus, all 30 covers carry a 22.0pt
masthead a third of the way down page 1 and a typed underscore fence pair
175.0pt wide centred on the page axis:

    Rel: May 15, 2026                      the release stamp (9pt)
    Notice: This opinion is subject …      the reporter's notice (9pt×4)
    ALABAMA COURT OF CIVIL APPEALS         22pt, top 206-271 of 792
    OCTOBER TERM, 2025-2026                the sitting
    _________________________              a fence ON THE AXIS…
    CL-2025-0536                           …around the docket…
    _________________________              …and one under it
    Kayla Dykes                            the caption: a party…
    v.                                     …the pivot…
    Joshua Dykes                           …and the other side
    Appeal from Dallas Circuit Court       the origin
    (DR-24-900056)                         and its docket
    BOWDEN, Judge.                         …and the writing starts

THE DISPATCH is one question about page 1: is there a row set above 18pt
BELOW the page's top band, with a fence pair under it? That is the cover.
Anything else is not this paper and the reader returns NOTHING — the
masthead pinned INTO the top band is the Supreme Court's certificate and
no masthead at all is its release list, and this court files neither.

EVERY ROW ON THE COVER IS CENTRED on the page axis: a party list long
enough to fill the measure (war_paint's four-row list of state officers
at x0=72.7) still centres to within 2pt, so the cover declares its
alignment rather than inferring it per row. The block is set BOLD; the
only roman row in the corpus is the paper naming itself ('After Remand
from the Alabama Supreme Court'), which is the title test.

A CONSOLIDATION REPEATS THE FENCE PAIR once per case, and the docket row
between a pair may itself wrap (k.w.: five CL numbers over two rows). The
five-appeals-plus-mandamus consolidation carries its second caption to
the foot of page 1 and signs on page 2, so the reader is bounded at three
pages and stops at the byline.

WHAT THE READER DOES NOT TOUCH. Nothing above the masthead is content:
the 'Rel: <date>' stamp and the four-row reporter's notice are recorded
as Dropped, and the release date is read off the stamp. Page-2 running
heads are core's furniture. This court prints NO appearance of counsel
anywhere in the corpus, so `no-attorneys` fires on prose, not on a gap.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import register

# The court's own facts live with its reading: one file per court, and the
# registration moved out of ``courts/__init__.py`` with the port.
ALACIVAPP: CourtProfile = register(CourtProfile(
    "alacivapp", "Court of Civil Appeals of Alabama",
    # 'BOWDEN, Judge.' / 'MOORE, Presiding Judge.' / 'PER CURIAM.'
    byline=BylineGrammar(style="prose", titles=("Judge", "Presiding Judge")),
))

STYLE_COVER = "fenced cover"

# ---- alacivapp's declared facts (measured over the 30-record corpus) -----
# THE MASTHEAD is 22.0pt on all 30 covers; the body is 14.0pt on all 30.
_MASTHEAD_SIZE = 18.0
# WHERE THE MASTHEAD STANDS names the paper. The cover sets it at top
# 206-271 on a 792pt page (26-34%); a masthead pinned INSIDE the top band
# would be the Supreme Court's certificate, which this court never files.
_TOP_BAND = 0.10
# THE DOCKET FENCE: 64 typed underscore rules over the corpus, every one
# of them 175.0 or 175.2pt wide and centred on the 612pt page axis to
# 0.01pt. The measure is carried wide enough to survive a font change.
_FENCE_MEASURE = (165.0, 186.0)
_FENCE_AXIS = 6.0
# THE COVER CENTRES EVERY ROW on the page axis; the widest measured offset
# over the corpus is 2.0 (war_paint's officer list).
_AXIS_TOL = 4.0
# HOW FAR THE BLOCK MAY RUN. The k.w. consolidation fills page 1 and signs
# on page 2; nothing here needs a fourth page.
_MAX_PAGES = 3
# A row is AT THE RAIL when it starts on the body's left edge.
_RAIL_TOL = 1.5

_TYPED_RULE = re.compile(r"^_{6,}$")
# 'CL-2025-0536' — THIS court's docket, and only this court's. The Supreme
# Court's 'SC-' and the Court of Criminal Appeals' own numbers are never
# printed between these fences. Consolidated appeals are printed as a list
# ('CL-2025-0567 and CL-2025-0568'), so the fenced row is read as the
# sequence of dockets it names rather than as a single token.
_DOCKET = re.compile(r"^CL[-‑]\d{4}[-‑]\d{3,5}$")
# 'DR-24-900056' / 'JU-17-515.02' / 'CV-25-194' / 'DR-21-900294.01' — the
# number a court BELOW gave the case, in every form this court prints.
_LOWER_DOCKET = re.compile(
    r"\b[A-Z]{2,4}[-‑]\d{2,4}(?:[-‑]\d{1,6})?(?:\.\d{2})?\b")
# 'Rel: May 15, 2026' — the release stamp above the masthead.
_REL = "rel:"
# The sitting: 'OCTOBER TERM, 2025-2026' / 'SPECIAL TERM, 2026'. A closed
# structural form — the word TERM over a year — never a court or party.
_TERM = re.compile(r"^[A-Z]+\s+TERM,?\s+\d{4}(?:\s*[-‑]\s*\d{4})?\.?$")
# THE ORIGIN LEADERS: the closed vocabulary of ways this court states where
# a case came from. Never a court NAME.
_ORIGIN_LEADERS = ("appeal from", "appeals from", "on appeal from",
                   "certified question from", "certified questions from",
                   "on certified question from",
                   "review of", "on review from")
# THE PAPER THE PETITIONER FILED, printed in caps inside the caption:
# 'PETITION FOR WRIT OF MANDAMUS'.
_PETITION_LEAD = "PETITION FOR"
# 'In re' opens the case BELOW, not the origin — both are parenthesised.
_IN_RE = re.compile(r"^\(\s*in\s+re\b", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _docket_row(text: str) -> list:
    """The dockets a fenced row names, in order, or [] when it names none."""
    parts = [p for p in re.split(r"[,;]|\band\b", _norm(text).rstrip("."))
             if p.strip()]
    out = [_norm(p) for p in parts]
    return out if out and all(_DOCKET.match(t) for t in out) else []


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its wide gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    def markup(self):
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows, furniture removed, in the page's own order."""
    rows: list = []
    for pm in model.pages[:max_pages]:
        buckets: dict = {}
        loose: list = []
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            if line.row is not None:
                buckets.setdefault(line.row, []).append(line)
            else:
                loose.append(line)
        groups = list(buckets.values())
        # pdfio leaves `row` unset on pages it did not have to split; fall
        # back to a baseline test, which is what `row` encodes anyway.
        for line in sorted(loose, key=lambda l: (l.top, l.x0)):
            for g in groups:
                if g[0].row is None and abs(g[0].top - line.top) <= 2.0:
                    g.append(line)
                    break
            else:
                groups.append([line])
        rows.extend(_Row(g) for g in groups)
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _is_fence(row: _Row, page_width: float) -> bool:
    """The cover's docket fence: a typed underscore rule in this court's one
    measure, centred on the page axis."""
    if not _TYPED_RULE.match(row.text.replace(" ", "")):
        return False
    if not (_FENCE_MEASURE[0] <= row.x1 - row.x0 <= _FENCE_MEASURE[1]):
        return False
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _FENCE_AXIS


def _on_axis(row: _Row, page_width: float) -> bool:
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _AXIS_TOL


def _release_date(model) -> str | None:
    """'Rel: May 15, 2026' -> 'May 15, 2026'. The court types the stamp by
    hand and sometimes doubles a comma ('July 17, ,2026'); the date is read
    as printed and normalised only for whitespace."""
    page1 = model.pages[0]
    for line in page1.lines:
        flat = _norm(line.plain)
        if flat[:len(_REL)].lower() == _REL and line.top < page1.height * 0.2:
            rest = flat[len(_REL):].strip()
            if rest:
                return rest
    return None


def _lower_dockets(text: str) -> list:
    return [_norm(t) for t in _LOWER_DOCKET.findall(text)]


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------

def _sides(text: str) -> tuple | None:
    """The two party names either side of the caption's pivot. The pivot is
    a free-standing 'v.', so an abbreviation inside a name cannot be it."""
    parts = re.split(r"(?<=[\s\w.,;)])\s+v\.?\s+", text, maxsplit=1)
    if len(parts) != 2:
        return None
    left, right = _norm(parts[0]).rstrip(",; "), _norm(parts[1]).rstrip(",; ")
    return (left, right) if left and right else None


def _name_from(ctx, parties_text: str) -> None:
    sides = _sides(parties_text)
    if sides:
        ctx.crit["parties"] = list(sides)
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    elif parties_text:
        ctx.crit["parties"] = [parties_text]
        ctx.crit["case_name"] = parties_text


def _record_origin(ctx, printed: str) -> None:
    """The origin as the page prints it, plus the numbers inside it."""
    flat = _norm(printed)
    if not flat:
        return
    prev = ctx.crit.get("lower_court")
    ctx.crit["lower_court"] = f"{prev} {flat}" if prev else flat
    for dk in _lower_dockets(flat):
        if dk not in ctx.crit.setdefault("lower_court_docket", []):
            ctx.crit["lower_court_docket"].append(dk)


def _cover_parties(rows: list) -> str:
    """The lead case's parties, built from the rows either side of the
    cover's own pivot row — never by joining the caption wholesale.

    A pivot on the cover is a row of its own ('v.'). THE CASE BELOW is
    parenthesised ('Ex parte Melester Ford' / 'PETITION FOR WRIT OF
    MANDAMUS' / '(In re: Janae Mitchell' / 'v.' / 'Melester Ford)') and
    carries a pivot of its own; the parenthesis opens it, and nothing from
    there on names a party to THIS proceeding."""
    left: list = []
    right: list = []
    side = left
    for text in rows:
        flat = _norm(text)
        if flat.startswith("("):
            break
        if side is left and flat.rstrip(".").lower() == "v":
            side = right
            continue
        side.append(flat)
    if right:
        return f"{_norm(' '.join(left)).rstrip(',; ')} v. " \
               f"{_norm(' '.join(right)).rstrip(',; ')}"
    return _norm(" ".join(left)).rstrip(",; ")


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The page models and the emit buffer."""

    def __init__(self, model, geom, rows, body_x0, body_size):
        self.model = model
        self.geom = geom
        self.rows = rows
        self.body_x0 = body_x0
        self.body_size = body_size
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align: str | None = None) -> None:
        pm = self.pages[row.page]
        if align is None:
            align = "C" if (_on_axis(row, pm.width)
                            and row.x0 > self.body_x0 + _RAIL_TOL) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def rule(self, row: _Row) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids),
                                 typed=True, span="center"))
        self.consumed.update(row.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


@decider("headmatter.read", court="alacivapp")
def read_headmatter_alacivapp(model, geom, **_):
    """Read the fenced cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if not rows:
        return NOTHING
    ctx = _Ctx(model, geom, rows, body_x0, body_size)

    p1 = [r for r in rows if r.page == 1]
    big = [r for r in p1 if r.size >= _MASTHEAD_SIZE]
    fences = [r for r in p1 if _is_fence(r, page1.width)]
    # THE MASTHEAD'S POSITION AND THE FENCE PAIR NAME THE PAPER.
    if big and big[0].top >= _TOP_BAND * page1.height and len(fences) >= 2:
        return _read_cover(ctx, big[0])
    return NOTHING


def _read_cover(ctx: _Ctx, masthead: _Row):
    parser = BylineParser(ALACIVAPP.byline)
    dockets: list = []
    groups: list = []                     # caption rows, one list per case
    in_docket = False
    in_title = False
    in_origin = False
    signed = False
    started = False
    notice: list = []
    for row in ctx.rows:
        if not started:
            if row is masthead:
                started = True
                ctx.crit["court"] = row.text
                ctx.emit(row, "court", "C")
                continue
            # A READER THAT CLAIMS THE REGION INHERITS ITS FURNITURE.
            # THE COVER OPENS ON ITS MASTHEAD: everything printed above it
            # is the release stamp and the reporter's revision notice, and
            # POSITION says so, not size. Core's notice peel runs only on
            # rows the reader left behind; left behind alone, the notice
            # assembles as an authorless writing.
            notice.append(row)
            continue
        pm = ctx.pages[row.page]
        if _is_fence(row, pm.width):
            ctx.rule(row)
            in_docket = not in_docket
            in_title = in_origin = False
            if not in_docket:
                groups.append([])
            continue
        if parser.parse(row.text) is not None:
            signed = True
            break
        if in_docket:
            # THE DOCKET ROW MAY WRAP: k.w. sets five CL numbers over two
            # rows between one fence pair.
            found = _docket_row(row.text)
            if not found:
                return NOTHING            # the fence pair holds a docket
            dockets.extend(found)
            ctx.emit(row, "docket", "C")
            continue
        if not groups:
            # Above the first fence the court names its sitting.
            if _TERM.match(row.text.upper()):
                ctx.emit(row, "date", "C")
                continue
            return NOTHING
        # THE COVER SETS ITS CAPTION BLOCK IN BOLD. A ROMAN row inside it
        # is the paper naming itself — 'After Remand from the Alabama
        # Supreme Court'. Measured: exactly one roman row in the 30 covers,
        # and that is it.
        if not row.bold:
            ctx.crit.setdefault("title", row.text.rstrip("."))
            ctx.emit(row, "title", "C")
            in_title = in_origin = False
            continue
        low = row.text.lower()
        opens_origin = any(low.startswith(lead) for lead in _ORIGIN_LEADERS)
        if not opens_origin and row.text.startswith("(") \
                and not _IN_RE.match(row.text):
            opens_origin = bool(_lower_dockets(row.text.strip("()")))
        # AN ORIGIN STATEMENT WRAPS. '(JU-17-515.02, JU-17-515.03,
        # JU-17-515.04, JU-17-515.05,' / 'and JU-17-515.06)' is one
        # statement in two rows; read row by row, the continuation joined
        # the party names. Once the origin opens it runs to the fence that
        # opens the next case, or to the byline.
        if opens_origin or in_origin:
            in_origin = True
            if len(groups) == 1:          # the lead case's origin
                _record_origin(ctx, row.text)
            else:
                for dk in _lower_dockets(row.text):
                    if dk not in ctx.crit.setdefault("lower_court_docket",
                                                     []):
                        ctx.crit["lower_court_docket"].append(dk)
            ctx.emit(row, "lower-court", "C")
            in_title = False
            continue
        if row.text.startswith(_PETITION_LEAD) or (
                in_title and row.text == row.text.upper()):
            # …of the LEAD case only: a consolidation repeats the same
            # petition title once per case, and merged they read twice over.
            if len(groups) == 1:
                prev = ctx.crit.get("history")
                ctx.crit["history"] = (f"{prev} {row.text}" if prev
                                       else row.text)
            in_title = True
            ctx.emit(row, "title", "C")
            continue
        in_title = False
        groups[-1].append(row.text)
        ctx.emit(row, "caption", "C")
    if not (signed and dockets and groups and any(groups)):
        return NOTHING
    for kind, band in (("stamp", [r for r in notice
                                  if r.text[:len(_REL)].lower() == _REL]),
                       ("notice", [r for r in notice
                                   if r.text[:len(_REL)].lower() != _REL])):
        if not band:
            continue
        ctx.dropped.append(m.Dropped(
            text=" ".join(r.text for r in band)[:1200],
            prov=m.Prov(band[0].page,
                        tuple(i for r in band for i in r.ids)),
            kind=kind))
        for r in band:
            ctx.consumed.update(r.ids)
    ctx.crit["headmatter_style"] = STYLE_COVER
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    caption = [t for g in groups for t in g]
    ctx.crit["caption"] = caption
    lead = next((g for g in groups if g), [])
    _name_from(ctx, _cover_parties(lead))
    date = _release_date(ctx.model)
    if date:
        ctx.crit["decision_date"] = date
    return ctx.result()
