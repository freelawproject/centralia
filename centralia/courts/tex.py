"""Supreme Court of Texas ('tex').

Everything unique to tex lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'double-rule cassette' (50 of 50 records).

Texas prints ONE paper and fences it with ONE mark: a TYPED rule made of a
single repeated glyph (U+2550 BOX DRAWINGS DOUBLE HORIZONTAL), centred on
the page axis in TWO invariant measures. The MEASURE names the band, exactly
as ca5's drawn rule pair does:

    SHORT — 92.2pt (259.9-352.1 on a 612pt page), around THIS court's docket
    LONG  — 359.2pt (126.4-485.7), around where the case came from

Between the two bands stands the caption. The three together are one
CASSETTE, and a consolidation repeats the cassette rather than crowding one:

    Supreme Court of Texas                      the masthead — BLACKLETTER
    ══════════                                  the SHORT fence, on the axis
    No. 24-1070                                 …around the docket…
    ══════════                                  …and one under it
    River Creek Development Corporation …       the caption: a party…
      Petitioners,                              …its status, ITALIC…
    v.                                          …the pivot…
    Preston Hollow Capital, LLC; …              …the other side…
      Respondents                               …and its status
    ═══════════════════════════════════════     the LONG fence…
    On Petition for Review from the             …around the origin…
    Court of Appeals for the Third District     …which wraps…
    ═══════════════════════════════════════     …and one under it
    Argued March 3, 2026                        the sitting, BOLD, on the axis
    JUSTICE BUSBY delivered the opinion …       …and the writing begins

THE JOINERS. Two consolidation forms, both set ITALIC on the page axis
between tildes, and the difference is WHICH band they join:

    '~ consolidated with ~'  joins two DOCKET bands under one origin
                             (in_re_state_of_texas: two relators, two
                             dockets, one 'On Petitions for Writ of Quo
                             Warranto')
    '~ and ~'                joins two WHOLE cassettes — docket, caption
                             and origin each repeated. m.h. carries five
                             of them onto page 3.

THE DISPATCH is the fence, never the wording: page 1 must set at least one
SHORT pair and one LONG pair in tex's two measures, on the axis, with the
oversize masthead opening the page above them. A record that fences neither
is not this paper and gets NOTHING.

WHY THE FENCE IS READ AS GLYPHS AND NOT AS TEXT. river_creek_..._1 embeds
the fence font with no ToUnicode map, so its four fences extract as 98
literal '(cid:607)' glyphs — a single record scoring 294 where the other 49
score 0.06, and the whole reason tex was the only D-grade state supreme
court. The row is still a fence: one glyph repeated, in tex's measure, on
tex's axis. The reader tests THAT, re-emits the row as the typed rule it is,
and the undecodable glyphs never reach the page. Nothing is guessed and no
cid number is hardcoded.

WHERE THE READER STOPS. At the row after the last cassette's closing LONG
fence, unless that row is the sitting ('Argued <date>', BOLD, on the axis)
or a joiner. 'PER CURIAM' is bold and on the axis too, and it is the
WRITING's byline — the reader does not take it.

WHAT THE READER DOES NOT TOUCH. The folio at the page foot is core's
furniture. The trailer ('OPINION DELIVERED: June 5, 2026', bold at the rail
on the last page) is the writing's; the reader reads the date off it and
claims nothing, exactly as ala reads its release stamp.

tex prints NO appearance of counsel anywhere in the corpus.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser, is_per_curiam
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import PROFILES, get_profile, register

# tex's profile: a title-first byline over an all-caps surname.
# ('JUSTICE BUSBY delivered the opinion of the Court.' / 'JUSTICE HUDDLE,
#  joined by Justice Devine, …, concurring.' / 'PER CURIAM')
_TEX_PROFILE = CourtProfile(
    "tex", "Supreme Court of Texas",
    byline=BylineGrammar(style="reversed",
                         rev_titles=("JUSTICE", "CHIEF JUSTICE")),
)
TEX = (register(_TEX_PROFILE) if "tex" not in PROFILES
       else get_profile("tex"))

STYLE = "double-rule cassette"

# ---- tex's declared facts (measured over the 50-record corpus) -----------
# THE FENCE MEASURES. 200 fences over the corpus: 100 short at 92.2pt
# (259.9-352.1) and 100 long at 359.2pt (126.4-485.7), every one centred on
# the 612pt page's axis to a tenth of a point.
_SHORT_FENCE = (80.0, 110.0)
_LONG_FENCE = (330.0, 385.0)
_AXIS_TOL = 6.0
# A FENCE IS A ROW OF ONE GLYPH REPEATED. Ten of them on the short rule,
# thirty-nine on the long; six is well under either and well over anything
# the court sets as prose.
_FENCE_MIN_GLYPHS = 6
# THE MASTHEAD is set in a BLACKLETTER face at 28pt over a 12pt body — the
# only row on the page above body size, and the only one not in Century
# Schoolbook.
_MASTHEAD_SIZE = 18.0
# HOW FAR THE BLOCK MAY RUN. m.h. carries its fifth cassette to page 3;
# nothing in the corpus needs a fourth page.
_MAX_PAGES = 5
# A row is AT THE RAIL when it starts on the body's left edge; the writing's
# first row is indented 36pt past it.
_RAIL_TOL = 1.5

# 'No. 24-1070' / 'Nos. 24-1070 & 24-1071' — this court's own docket, and
# only this court's.
_DOCKET_ROW = re.compile(r"^Nos?\.\s*(.+)$")
_DOCKET = re.compile(r"^\d{2}[-‑]\d{4}$")
# THE JOINER: a tilde-fenced phrase, italic, on the page axis.
_JOINER = re.compile(r"^~\s*(.+?)\s*~$")
# THE SITTING: a closed vocabulary of the ways a court names the day it
# heard the case. Never a party or a court name.
_SITTING = ("argued", "reargued", "submitted", "resubmitted",
            "argued and submitted")
# THE TRAILER: 'OPINION DELIVERED: June 5, 2026' — bold, at the body rail,
# on the document's last page. The LEADER names the paper the court filed
# ('STATEMENT FILED: June 5, 2026' on a statement respecting a denial) and
# the verb names the act; both are closed vocabularies. A row whose fill is
# still BLANK ('OPINION FILED: _____________' — noyes_1 was released before
# the date was stamped) states no date, and a date carries a number.
_TRAILER = re.compile(
    r"^(?:OPINION|STATEMENT|ORDER|JUDGMENT)\s+"
    r"(?:DELIVERED|FILED|ISSUED)\s*:\s*(.+?)\.?$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold",
                 "italic", "text", "font")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.font = first.font
        self.text = _norm(" ".join(p.plain for p in self.pieces))
        # ITALIC is the caption's own role marker: a party STATUS
        # ('Petitioners,') and a consolidation JOINER are italic, the party
        # NAMES are roman. Punctuation is routinely left roman inside an
        # italic passage, so only the letters vote.
        seen = False
        ital = True
        for p in self.pieces:
            for c in p.chars:
                t = c.get("text") or ""
                if not any(ch.isalpha() for ch in t):
                    continue
                seen = True
                f = c.get("fontname") or ""
                if "Italic" not in f and "Oblique" not in f:
                    ital = False
        self.italic = seen and ital

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def glyphs(self) -> list:
        """The row's inked glyphs, as the text layer hands them back. An
        undecodable glyph is one item ('(cid:607)'), which is what lets the
        fence test see a rule the font map lost."""
        return [c.get("text") or "" for p in self.pieces for c in p.chars
                if (c.get("text") or "").strip()]

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows, furniture removed, in the page's own order.

    A READER THAT CLAIMS THE REGION INHERITS ITS FURNITURE — and must not
    lose its own landmarks to it. A consolidation carries the cassette onto
    page 2, where the SHORT fence that opens it stands in the top band and
    repeats page after page; core's running-head test reads exactly that
    shape. m.h. lost the fences opening its third and fifth cassettes, and
    with them two of its five dockets. A row that measures as one of tex's
    fences is structure, whatever else it also looks like.
    """
    rows: list = []
    for pm in model.pages[:max_pages]:
        buckets: dict = {}
        loose: list = []
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line) and not _fence(_Row([line]), pm.width):
                continue
            if line.row is not None:
                buckets.setdefault(line.row, []).append(line)
            else:
                loose.append(line)
        groups = list(buckets.values())
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

def _on_axis(row: _Row, page_width: float) -> bool:
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _AXIS_TOL


def _fence(row: _Row, page_width: float) -> str | None:
    """'short' | 'long' | None — the typed double rule, named by its
    MEASURE. A fence is one glyph repeated, so a row whose font map was
    lost reads the same as one whose was not."""
    glyphs = row.glyphs
    if len(glyphs) < _FENCE_MIN_GLYPHS or len(set(glyphs)) != 1:
        return None
    if glyphs[0].isalnum():
        return None                       # a repeated LETTER is not a rule
    if not _on_axis(row, page_width):
        return None
    width = row.x1 - row.x0
    if _SHORT_FENCE[0] <= width <= _SHORT_FENCE[1]:
        return "short"
    if _LONG_FENCE[0] <= width <= _LONG_FENCE[1]:
        return "long"
    return None


def _dockets(text: str) -> list:
    """The dockets a fenced row names, in order, or [] when it names none."""
    mm = _DOCKET_ROW.match(_norm(text))
    if not mm:
        return []
    parts = [p.strip() for p in re.split(r"[,;&]|\band\b", mm.group(1))
             if p.strip()]
    return parts if parts and all(_DOCKET.match(p) for p in parts) else []


def _trailer_date(model) -> str | None:
    """'OPINION DELIVERED: June 5, 2026' — the day the court handed the
    paper down, printed at the foot of the last page. Read, never claimed:
    the row belongs to the writing."""
    for pm in reversed(model.pages):
        for line in pm.lines:
            mm = _TRAILER.match(_norm(line.plain))
            if mm and any(ch.isdigit() for ch in mm.group(1)):
                return mm.group(1).strip()
    return None


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------

def _case_name(rows: list) -> tuple:
    """(parties, case_name) from ONE cassette's caption rows.

    Built from the party names either side of the pivot — never by joining
    the caption wholesale. The pivot is a row of its own ('v.'); the party
    STATUS is italic and names no party.
    """
    left: list = []
    right: list = []
    side = left
    for row in rows:
        if row.italic:
            continue                      # 'Petitioners,' / 'Relator'
        flat = _norm(row.text)
        if side is left and flat.rstrip(".").lower() == "v":
            side = right
            continue
        side.append(flat)
    lhs = _norm(" ".join(left)).rstrip(",; ")
    rhs = _norm(" ".join(right)).rstrip(",; ")
    if lhs and rhs:
        return [lhs, rhs], f"{lhs} v. {rhs}"
    return ([lhs], lhs) if lhs else ([], None)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, body_x0):
        self.model = model
        self.body_x0 = body_x0
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align: str | None = None) -> None:
        pm = self.pages[row.page]
        if align is None:
            align = "C" if _on_axis(row, pm.width) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, italic=row.italic, role=role))
        self.consumed.update(row.ids)

    def rule(self, row: _Row) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids),
                                 typed=True, span="center"))
        self.consumed.update(row.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


@decider("headmatter.read", court="tex")
def read_headmatter_tex(model, geom, **_):
    """Read tex's double-rule cassette, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 108.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if not rows:
        return NOTHING

    p1 = [r for r in rows if r.page == 1]
    kinds = [_fence(r, page1.width) for r in p1]
    if kinds.count("short") < 2 or kinds.count("long") < 2:
        return NOTHING
    big = [r for r in p1 if r.size >= _MASTHEAD_SIZE]
    if len(big) != 1 or big[0].top > p1[0].top:
        return NOTHING                    # the masthead opens the paper

    ctx = _Ctx(model, body_x0)
    return _read_cassettes(ctx, rows, big[0])


def _read_cassettes(ctx: _Ctx, rows: list, masthead: _Row):
    parser = BylineParser(TEX.byline)
    dockets: list = []
    groups: list = []                     # caption rows, one list per case
    origins: list = []                    # origin rows, one list per case
    in_docket = False
    in_origin = False
    closed = False                        # a cassette's origin band closed
    signed = False
    started = False
    for row in rows:
        pm = ctx.pages[row.page]
        if not started:
            if row is masthead:
                started = True
                ctx.crit["court"] = row.text
                ctx.emit(row, "court", "C")
                continue
            return NOTHING                # nothing stands above the masthead
        kind = _fence(row, pm.width)
        if kind == "short":
            if in_origin:
                return NOTHING
            ctx.rule(row)
            in_docket = not in_docket
            if not in_docket:
                groups.append([])
                closed = False
            continue
        if kind == "long":
            if in_docket:
                return NOTHING
            ctx.rule(row)
            in_origin = not in_origin
            if in_origin:
                origins.append([])
            else:
                closed = True
            continue
        if in_docket:
            found = _dockets(row.text)
            if not found:
                return NOTHING            # the short pair holds a docket
            dockets.extend(found)
            ctx.emit(row, "docket", "C")
            continue
        if in_origin:
            origins[-1].append(row.text)
            ctx.emit(row, "lower-court", "C")
            continue
        # A JOINER is italic, tilde-fenced and on the axis; it stands
        # between two docket bands or between two whole cassettes.
        if row.italic and _JOINER.match(row.text) and _on_axis(row, pm.width):
            ctx.emit(row, "title", "C")
            closed = False
            continue
        if not closed:
            if not groups:
                return NOTHING            # the caption follows the docket
            groups[-1].append(row)
            ctx.emit(row, "caption", "C")
            continue
        # PAST THE LAST CASSETTE. Only the sitting belongs to the
        # headmatter; 'PER CURIAM' is bold and on the axis too, and it is
        # the WRITING's byline.
        _lead, _, _rest = row.text.partition(" ")
        if (row.bold and _on_axis(row, pm.width) and not is_per_curiam(row.text)
                and _lead.lower() in _SITTING and _rest.strip()):
            ctx.crit["submitted"] = _norm(_rest).rstrip(".")
            ctx.emit(row, "date", "C")
            continue
        # THE WRITING BEGINS where the page leaves the cassette's axis for
        # the body's own paragraph indent. Two of its three forms parse as a
        # byline alone ('PER CURIAM', 'JUSTICE BUSBY delivered …'); the third
        # is the FOLDED byline, which carries its joiner roster on the first
        # row and its kind clause on the second ('JUSTICE HUDDLE, joined by
        # Justice Devine, Justice Young, and' / 'Justice Sullivan,
        # concurring.') and which no single-row grammar can parse — 14 of the
        # 50 records open that way. All three sit at the paragraph indent,
        # OFF the axis, and that is the measurement the reader needs.
        signed = bool(is_per_curiam(row.text) or parser.parse(row.text)
                      or (row.x0 > ctx.body_x0 + _RAIL_TOL
                          and not _on_axis(row, pm.width)))
        break
    if not (signed and dockets and groups and any(groups) and origins):
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE
    ctx.crit["docket_number"] = f"No. {dockets[0]}"
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = [f"No. {d}" for d in dockets[1:]]
    ctx.crit["caption"] = [r.text for g in groups for r in g]
    lead = next((g for g in groups if g), [])
    parties, name = _case_name(lead)
    if parties:
        ctx.crit["parties"] = parties
    if name:
        ctx.crit["case_name"] = name
    if origins and origins[0]:
        ctx.crit["lower_court"] = _norm(" ".join(origins[0]))
    date = _trailer_date(ctx.model)
    if date:
        ctx.crit["decision_date"] = date
    return ctx.result()
