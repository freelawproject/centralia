"""Supreme Court of Florida ('fla').

Everything unique to fla lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Florida sets two papers, and each one FENCES itself with a
rule of a measure it uses for nothing else. The measure is the dispatch;
no word on the page decides anything:

    'engraved cover' (47 of 50) — a 37pt engraved masthead over a docket
    fenced ABOVE AND BELOW by a rule 84pt wide, centred on the page axis
    to the point (measured: 120 of 120 fences sit at offset 0.0). The pair
    REPEATS once per consolidated case, each caption stands under its own
    pair, and one release date closes the block for all of them:

        Supreme Court of Florida          the masthead, 37pt, centred
        ____________                      a fence ON THE AXIS…
        No. SC2026-0736                   …around the docket…
        ____________                      …and one under it
        ANDREW RICHARD LUKEHART,          the caption: a party, bold…
             Appellant,                   …and its status
        vs.                               …the pivot…
        STATE OF FLORIDA,
             Appellee.
        May 27, 2026                      the release date
        CORRECTED OPINION                 (the paper's name, when revised)
        PER CURIAM.                       …and the writing starts

    The fence is TYPED on 46 records and DRAWN on one; both are the same
    fence and the reader takes either. The court draws two other rules and
    neither is a fence: the footnote separator (144pt at the body rail,
    x0=72) is off the axis, and the 163pt rule under 'CORRECTED OPINION'
    is on the axis but its ends coincide with the row above it — an
    underline, not a section mark.

    'docket sheet' (3 of 50) — the clerk's disposition sheet. A 32pt
    masthead, a weekday-dated release row, a TWO-COLUMN caption, and one
    DRAWN 473pt rule across the whole measure. That rule is the parser:
    what stands above it is headmatter and what stands below it is the
    court's unsigned ruling. The caption's columns are divided by the
    widest band its own rows leave empty — 72pt at the narrowest, where
    the status indent inside a column is 17pt.

        Supreme Court of Florida                the masthead, 32pt
        THURSDAY, JUNE 11, 2026                 the release day
        The Florida Bar,            SC2024-1528       the caption: parties
             Complainant            Lower Tribunal No(s).:   left, docket
        v.                            2024-00,120(2A)        and origin right
        Kenneth Chesebro,
             Respondent
        ───────────────────────────────────     a DRAWN 473pt rule
        Respondent Kenneth Chesebro entered …   the ruling

A record that fences neither way is not one of these papers and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

WHAT THE READER DOES NOT TOUCH. fla prints its origin statement and its
appearance roster BELOW the writings on every adversarial record — the
profile declares ``counsel_after_writings`` and that roster is core's to
harvest. The reader stops at the first byline and never reaches into a
writing.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import register

FLA = register(CourtProfile(
    "fla", "Supreme Court of Florida",
    # 'PER CURIAM.' / 'GROSSHANS, J.' / 'TANENBAUM, J., concurring.' — the
    # court signs with an abbreviated title over an all-caps surname.
    byline=BylineGrammar(style="abbrev"),
    # THE ROSTER PRINTS LAST. Florida closes an adversarial record with the
    # origin statement and the appearances, after the writings ('An Appeal
    # from the Circuit Court in and for Duval County, …' / 'Dawn B.
    # Macready, Capital Collateral Regional Counsel, …, for Appellant').
    # Measured: 26 of the 50 records print one.
    counsel_after_writings=True,
))

STYLE_COVER = "engraved cover"          # the opinion paper: typed/drawn pair
STYLE_SHEET = "docket sheet"            # the clerk's disposition sheet

# ---- fla's declared facts (measured over the corpus, not tuned) ----------
# THE DOCKET FENCE. 120 fences over the corpus: 115 at 84.1pt, three at
# 91pt, one at 77pt, one at 70pt, and two DRAWN at 98.1pt — and every one
# of them centred on the page axis to within half a point.
_FENCE_MEASURE = (64.0, 104.0)
_FENCE_AXIS = 8.0
# THE SHEET FENCE: one drawn rule 473.3pt wide, 2pt off the axis, on all
# three docket sheets and on no cover.
_SHEET_MEASURE = 400.0
_SHEET_AXIS = 40.0
# THE MASTHEAD: 37pt on the cover, 32pt on the sheet, over a 14pt body.
# Either way it is the only row on the page set above 20pt.
_MASTHEAD_SIZE = 24.0
# HOW FAR THE BLOCK MAY RUN. A three-docket consolidation (state_attorneys)
# carries its caption onto page 2; nothing in the corpus needs a third.
_MAX_PAGES = 3
# THE CAPTION'S COLUMN DIVIDER on the docket sheet: the widest band the
# caption's own rows leave empty. Measured 72pt / 128pt / 177pt on the
# three sheets, against a 17pt status indent INSIDE a column.
_GUTTER_MIN = 40.0

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday",
             "saturday", "sunday")
# 'May 27, 2026' — fla sets its release date bare, with no label at all.
_DATE = re.compile(r"^([A-Z][a-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})\.?$")
# 'THURSDAY, JUNE 11, 2026' — the docket sheet dates its release by the day
# the Court sat.
_DAY_DATE = re.compile(r"^([A-Za-z]+),\s+([A-Za-z]+)\.?\s+(\d{1,2}),?\s+"
                       r"(\d{4})\.?$")
# THE COURT'S OWN DOCKET, in the two forms it prints: labelled inside the
# cover's fence pair, bare in the sheet's right column.
_DOCKET = re.compile(r"^(?:Nos?\.\s*)?SC\d{2,4}-\d{2,5}\.?$", re.I)
# THE PAPER'S OWN NAME, printed alone and centred under the date when the
# court reissues an opinion. A closed vocabulary of labels — never a test
# on anything the row says about a case.
_TITLE_WORDS = ("CORRECTED OPINION", "REVISED OPINION", "AMENDED OPINION",
                "SUBSTITUTED OPINION", "SUBSTITUTE OPINION",
                "CORRECTED ORDER", "AMENDED ORDER", "ON REHEARING",
                "ON MOTION FOR REHEARING", "ON REHEARING GRANTED")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. fla sets the plural as '(s)' on the docket sheet and as a plain
# 's' on the cover.
_STATUS_WORDS = (
    "appellant", "appellee", "petitioner", "respondent", "complainant",
    "plaintiff", "defendant", "intervenor", "movant", "amicus", "amici",
    "applicant", "claimant", "cross-appellant", "cross-appellee",
)
# The sheet's own label over the tribunal's numbers.
_LOWER_LABEL = "lower tribunal no"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_masthead(text: str) -> bool:
    """fla names itself on every paper it prints, in one row."""
    return _norm(text).lower().rstrip(".") == "supreme court of florida"


def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower().replace("(s)", "s")
    if not bare:
        return False
    words = [w.strip(",.;: ") for w in bare.split()]
    return all(w in _STATUS_WORDS or w.rstrip("s") in _STATUS_WORDS
               or w in ("and", "the", "cross", "etc")
               for w in words if w)


def _is_pivot(text: str) -> bool:
    flat = _norm(text).rstrip(".").lower()
    return flat in ("v", "vs")


def _date_value(text: str) -> str | None:
    """'May 27, 2026' as the page set it, or None. The month is a closed
    vocabulary; the value is a SLICE of the row, so the comma the court
    typed inside the date survives."""
    flat = _norm(text)
    mm = _DATE.match(flat)
    if mm and mm.group(1).lower().rstrip(".") in _MONTHS:
        return flat.rstrip(".")
    return None


def _day_date_value(text: str) -> str | None:
    """'THURSDAY, JUNE 11, 2026' -> 'JUNE 11, 2026'."""
    flat = _norm(text)
    mm = _DAY_DATE.match(flat)
    if mm is None:
        return None
    if mm.group(1).lower() not in _WEEKDAYS:
        return None
    if mm.group(2).lower().rstrip(".") not in _MONTHS:
        return None
    return f"{mm.group(2)} {mm.group(3)}, {mm.group(4)}"


def _title_label(text: str) -> str | None:
    flat = _norm(text).rstrip(".:").upper()
    return flat if flat in _TITLE_WORDS else None


# --------------------------------------------------------------------------
# the fences — fla's section marks, and the dispatch
# --------------------------------------------------------------------------

def _underlines(pm) -> set:
    """The tops of rules the page drew as UNDERLINES rather than fences.

    A rule whose ends coincide with the row just above it underscores that
    row; fla sets one under 'CORRECTED OPINION' at 163pt, on the axis,
    where a fence would also sit."""
    out = set()
    for r in pm.h_rules:
        for line in pm.lines:
            if not (0 < r.top - line.bottom < 14):
                continue
            if abs(line.x0 - r.x0) <= 3 and abs(line.x1 - r.x1) <= 3:
                out.add(round(r.top, 1))
    return out


def _drawn_fences(pm) -> list:
    """The tops of the DOCKET fences this page draws, in page order."""
    skip = _underlines(pm)
    out = []
    for r in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        if round(r.top, 1) in skip:
            continue
        out.append(r.top)
    return sorted(out)


def _sheet_fence(pm) -> float | None:
    """Where the docket sheet draws its full-measure rule, or None."""
    for r in pm.h_rules:
        if r.width < _SHEET_MEASURE:
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _SHEET_AXIS:
            continue
        return r.top
    return None


def _typed_fence(line, pm) -> bool:
    """A typed underscore row IS the same fence, when it is on the axis and
    in the same measure."""
    if not _TYPED_RULE.match(_norm(line.plain)):
        return False
    width = line.x1 - line.x0
    if not (_FENCE_MEASURE[0] <= width <= _FENCE_MEASURE[1]):
        return False
    return abs((line.x0 + line.x1) / 2 - pm.width / 2) <= _FENCE_AXIS


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="fla")
def read_headmatter_fla(model, geom, **_):
    """Read fla's fenced headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING
    if not any(_is_masthead(l.plain) for l in rows[:3]):
        return NOTHING                    # fla always names itself first

    ctx = _Ctx(model, geom, pages, body_size, rows)
    # THE FENCE IS THE DISPATCH. The cover's pair and the sheet's single
    # full-measure rule are different measures on the same axis, and no
    # record in the corpus draws both.
    if len(_drawn_fences(page1)) + sum(
            1 for l in page1.lines if _typed_fence(l, page1)) >= 2:
        return _read_cover(ctx)
    if _sheet_fence(page1) is not None:
        return _read_sheet(ctx)
    return NOTHING


class _Ctx:
    """What both walks share: the page models and the emit buffer."""

    def __init__(self, model, geom, pages, body_size, rows):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.rows = rows
        self.items: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, line, role: str):
        pm = self.pages[line.page]
        align = line_alignment(line, pm.width, self.geom,
                               banner_center_min_size=self.body_size + 2.0)
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        self.consumed.add(line.id)

    def rule(self, page: int, line=None, typed: bool = False,
             span: str = "center"):
        prov = m.Prov(page, (line.id,) if line is not None else ())
        self.items.append(m.Rule(prov=prov, typed=typed, span=span))
        if line is not None:
            self.consumed.add(line.id)

    def result(self, anchor_ids=(), doc_type=None):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": [], "consumed": self.consumed,
                "anchor_ids": list(anchor_ids), "doc_type_final": doc_type}


# ---- the engraved cover --------------------------------------------------

def _read_cover(ctx: _Ctx):
    parser = BylineParser(FLA.byline)
    # The stream the walk reads: content rows and DRAWN fences, merged by
    # where the page prints each. A typed fence is already a row.
    stream: list = []
    for line in ctx.rows:
        stream.append((line.page, line.top, "line", line))
    for pm in ctx.model.pages[:_MAX_PAGES]:
        for top in _drawn_fences(pm):
            stream.append((pm.number, top, "fence", None))
    stream.sort(key=lambda t: (t[0], t[1]))

    groups: list[list] = []               # caption rows, one list per case
    dockets: list[str] = []
    anchor_ids: list[int] = []
    state = "masthead"                    # masthead | docket | caption | dated
    in_docket = False
    signed = False

    for page, _top, kind, line in stream:
        if kind == "fence":
            ctx.rule(page)
            in_docket = not in_docket
            state = "docket" if in_docket else "caption"
            if not in_docket:
                groups.append([])
            continue
        text = _norm(line.plain)
        if _typed_fence(line, ctx.pages[line.page]):
            ctx.rule(page, line, typed=True)
            in_docket = not in_docket
            state = "docket" if in_docket else "caption"
            if not in_docket:
                groups.append([])
            continue
        # A BYLINE ENDS THE READER, always and everywhere.
        if parser.parse(text) is not None:
            signed = True
            break
        if state == "masthead":
            if not _is_masthead(text):
                return NOTHING            # not the cover this contract names
            ctx.crit.setdefault("court", text)
            ctx.emit(line, "court")
            continue
        if state == "docket":
            if not _DOCKET.match(text):
                return NOTHING            # the fence pair holds a docket
            dockets.append(text.rstrip("."))
            ctx.emit(line, "docket")
            continue
        if state == "caption":
            value = _date_value(text)
            if value is not None:
                ctx.crit.setdefault("decision_date", value)
                ctx.emit(line, "date")
                state = "dated"
                continue
            align = line_alignment(line, ctx.pages[line.page].width, ctx.geom,
                                   banner_center_min_size=ctx.body_size + 2.0)
            # A CAPTION ROW IS CENTRED OR BOLD. fla sets its party names in
            # bold and its statuses centred under them; body prose is
            # neither, so a walk that lost its byline stops here rather
            # than reading an opinion as a caption.
            if align != "C" and not line.all_bold:
                return NOTHING
            groups[-1].append(text)
            ctx.emit(line, "caption")
            continue
        # state == 'dated': only the paper's own name may follow the date.
        label = _title_label(text)
        if label is None:
            return NOTHING
        ctx.crit.setdefault("title", label)
        ctx.emit(line, "title")
        anchor_ids.append(line.id)
    if not signed or not dockets:
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE_COVER
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    caption = [t for g in groups for t in g]
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, groups[0])
    return ctx.result(anchor_ids)


def _name(ctx: _Ctx, rows: list) -> None:
    """The lead case's name, built from the party names either side of the
    pivot — never by joining the caption wholesale."""
    sides = _sides(rows)
    if sides:
        ctx.crit["parties"] = list(sides)
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        return
    one = _sides(rows, one_sided=True)
    if one:
        ctx.crit["parties"] = [one]
        ctx.crit["case_name"] = one


def _sides(rows: list, one_sided: bool = False):
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        if _is_pivot(flat):
            side = right
            seen_pivot = True
            continue
        if _is_status(flat):
            continue
        side.append(flat)
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# ---- the docket sheet ----------------------------------------------------

def _gutter(band: list) -> float | None:
    """The caption's own column divider: the widest vertical band its rows
    leave empty. Measured INSIDE the caption, never across the block."""
    spans = sorted((l.x0, l.x1) for l in band)
    if not spans:
        return None
    merged: list[list[float]] = []
    for x0, x1 in spans:
        if merged and x0 <= merged[-1][1] + 0.5:
            merged[-1][1] = max(merged[-1][1], x1)
        else:
            merged.append([x0, x1])
    gaps = [(merged[i + 1][0] - merged[i][1],
             (merged[i][1] + merged[i + 1][0]) / 2)
            for i in range(len(merged) - 1)]
    if not gaps:
        return None
    width, mid = max(gaps)
    return mid if width >= _GUTTER_MIN else None


def _read_sheet(ctx: _Ctx):
    pm = ctx.model.pages[0]
    fence_top = _sheet_fence(pm)
    # WHICH SIDE OF THE RULE A ROW STANDS ON is decided by where the row
    # STARTS. The last caption row's descenders reach past the fence
    # ('Respondent(s)' tops at 336.9 under a rule at 349.7), and a test on
    # the row's bottom left it below the fence and inside the writing.
    above = [l for l in ctx.rows if l.page == 1 and l.top < fence_top]
    if not above:
        return NOTHING

    band: list = []                       # the caption's own rows
    for line in above:
        text = _norm(line.plain)
        if _is_masthead(text) or (line.size or 0) >= _MASTHEAD_SIZE:
            if not _is_masthead(text):
                return NOTHING
            ctx.crit.setdefault("court", text)
            ctx.emit(line, "court")
            continue
        value = _day_date_value(text)
        if value is not None and not band:
            ctx.crit.setdefault("decision_date", value)
            ctx.crit.setdefault("panel_line", text)   # the day the Court sat
            ctx.emit(line, "date")
            continue
        band.append(line)
    if not band:
        return NOTHING

    mid = _gutter(band)
    block, left_plain, right_plain = _caption(band, mid, pm, ctx)
    if block is None:
        return NOTHING
    ctx.items.append(block)
    ctx.consumed.update(block.prov.line_ids)
    # THE RIGHT COLUMN carries this court's docket and the tribunal's own
    # numbers; each cell is tagged for what it is, so nothing in the box
    # reads as 'caption' by default.
    lower: list[str] = []
    for row, flat in zip(block.right, right_plain):
        if not flat:
            continue
        if _DOCKET.match(flat):
            row.role = "docket"
            if ctx.crit.get("docket_number"):
                ctx.crit.setdefault("other_dockets", []).append(
                    flat.rstrip("."))
            else:
                ctx.crit["docket_number"] = flat.rstrip(".")
            continue
        row.role = "lower-court"
        if flat.lower().startswith(_LOWER_LABEL):
            continue
        lower.append(flat.rstrip(";"))
    if lower:
        ctx.crit.setdefault("other_dockets", []).extend(lower)
    caption = [t for t in left_plain if t]
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, caption)
    # THE FENCE renders where the page draws it: a reader that claims the
    # region inherits the court's own section marks, and core only draws
    # them for rows the reader left behind.
    ctx.rule(1, span="full")
    ctx.crit["headmatter_style"] = STYLE_SHEET
    return ctx.result()


def _caption(band: list, mid: float | None, pm, ctx: _Ctx):
    """The docket sheet's caption as a CaptionBlock, plus each column's
    text. Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned."""
    rows: list[list] = []
    for line in sorted(band, key=lambda l: (l.top, l.x0)):
        if rows and abs(rows[-1][0].top - line.top) <= 3:
            rows[-1].append(line)
        else:
            rows.append([line])
    if not rows:
        return None, [], []

    def cell(cells: list, role: str):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        align = line_alignment(first, pm.width, ctx.geom,
                               banner_center_min_size=ctx.body_size + 2.0)
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    left, right = [], []
    left_plain, right_plain = [], []
    for row in rows:
        l_cells = [l for l in row if mid is None or l.x1 <= mid]
        r_cells = [l for l in row if mid is not None and l.x1 > mid]
        left.append(cell(l_cells, "caption") if l_cells
                    else m.HmLine(text="", prov=m.Prov(pm.number)))
        right.append(cell(r_cells, "docket") if r_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number)))
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    # A COLUMN ENDS AT ITS OWN LAST CELL. The two stacks render side by
    # side, not row by row, so a right column shorter than the left one
    # does not need padding — and padded it drew five tinted blank rows
    # beside mendivil's single docket.
    for col, plain in ((left, left_plain), (right, right_plain)):
        while col and not plain[len(col) - 1]:
            col.pop()
    block = m.CaptionBlock(
        left=left, right=right, rail=None, rail_rows=len(left),
        fp={"rail": None, "mid_x": mid},
        prov=m.Prov(pm.number, tuple(sorted(l.id for l in band))))
    return block, left_plain, right_plain
