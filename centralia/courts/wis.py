"""Supreme Court of Wisconsin ('wis').

Everything unique to wis lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is already
registered in courts/__init__.py — this module only binds the reader.

THE CONTRACT. Wisconsin prints ONE paper, and every one of the 49 records
sets it the same way: a letterhead, then a stack of BANDS each closed by a
DRAWN FENCE. Nothing on the page is read by wording to decide the layout.

    ─────────────────────────────────────────────  the head rule (391.5pt,
                    2025 WI 23                     drawn, at the body rail)
              Supreme Court of Wisconsin           …the cite, 14pt, centred
                       (seal)                      …then the court names
                    ───────────                        itself IN PIXELS
                  JOSH KAUL, et al.,               fence · the CAPTION band
          Plantiffs-Respondents-Petitioners,           party roman,
                          v.                           status ITALIC,
         WISCONSIN STATE LEGISLATURE, et al.,          pivot italic and
               Defendants-Appellants.                  alone on its row
                    ───────────                    fence · the DOCKET band
                  No. 2022AP790
               Decided June 17, 2025
                    ───────────                    fence · the ORIGIN band
        REVIEW of a decision of the Court of Appeals.
    Dane County Circuit Court (Susan M. Crawford, J.) No. 2021CV1314
                    ───────────                    fence · the ANNOUNCEMENT
        HAGEDORN, J., delivered the majority opinion for a unanimous
    Court.
                    ───────────                    fence · and the writing
        ¶1  BRIAN HAGEDORN, J. This is a constitutional …      starts here

THE FENCE IS THE PARSER. It is a drawn rect, 118.5–118.8pt wide on a 612pt
page and centred on the page axis to within 0.4pt over all 49 records — the
ONLY other rule above the block's foot is the letterhead's head rule at
391.5pt, which is three times the measure and is never mistaken for it. A
record prints 3, 4 or 5 fences (5 records / 16 / 28); consecutive fences
enclose a band, and THE LAST FENCE CLOSES THE HEADMATTER. Everything below
it is the writing and the reader does not touch it.

WHICH BAND IS WHICH IS A GEOMETRY QUESTION, not an ordinal and not a title:

  * THE CAPTION BAND is the one carrying the PIVOT — an italic row whose
    whole text is 'v.'. All 49 print it, in the first band, always.
  * THE DOCKET BAND opens on wis's own docket form ('No. 2022AP790',
    'No. 2023AP1664-D', 'No. 2025XX1438', 'No. 2024AP330-OA') and closes on
    the release date ('Decided June 17, 2025', 'Filed November 25, 2025',
    'Decided Friday, June 27, 2025').
  * THE ANNOUNCEMENT BAND IS THE ONE THAT LEAVES THE PAGE AXIS. Every row
    of every caption/docket/origin band sits centred within 1.8pt of the
    axis; the announcement is a justified paragraph at the body rail, its
    first line indented 36pt and its last line short, and the smallest
    off-axis measure any of the 28 shows is 22.1pt. A 20pt gap either side
    of the test, so the band names itself by where it is set.
  * THE ORIGIN BAND is the centred band that is neither of the first two.

WHAT THE CAPTION BAND HOLDS. Party names are ROMAN, party statuses are
ITALIC, and the pivot is an italic row of its own — so a party and its
status are told apart by the typeface, never by a vocabulary of statuses. A
name or a status may WRAP (wisconsin_department_of_corrections sets 'STATE
OF WISCONSIN EX REL. WISCONSIN DEPARTMENT OF CORRECTIONS,' /
'DIVISION OF COMMUNITY CORRECTIONS,' as two roman rows;
wisconsin_state_legislature wraps a status over two italic ones), and a wrap
is invisible to the row test — which is why the case name is built from the
party names either side of the pivot and never by joining the band.

THE BAND'S OWN LEADING SEPARATES ITS GROUPS. Rows are grouped where the
vertical step exceeds 1.30x the band's median leading. Measured: inside a
group the step is 15.0–17.5pt; between groups it is 23.8, 29.0, 31.4 or
34.9pt. Two things need that split and nothing else does:

  * the INTERVENING PARTY (elizabeth_bothfeld,
    wisconsin_business_leaders_for_democracy — 'GLENN GROTHMAN ET AL.,' /
    'Intervening Defendants.' set 31.4pt below the first group);
  * the MATTER TITLE on the 15 disciplinary records ('IN THE MATTER OF
    DISCIPLINARY PROCEEDINGS AGAINST' / 'BRYANT H. KLOS, ATTORNEY AT LAW').
    It is told from a wrapped party name by having NO ITALIC ROW IN IT and
    standing above the first group that has one — a party group always
    prints its status. Read as a party it made the case name
    'IN THE MATTER OF … OFFICE OF LAWYER REGULATION v. BRYANT H. KLOS'.

THE COURT NAMES ITSELF IN PIXELS. 'Supreme Court of Wisconsin' is a 364x34pt
blackletter GRAPHIC and the seal below it is a 74x72pt graphic; there is no
text row for either on any of the 49 pages. `criteria.court` is therefore
left unset rather than invented — the profile's label is the only place the
court's name exists, and it is not a reading of this page. (Both graphics
are core's to place; see the note in the final answer about core filing the
seal as a body FIGURE, which is a core defect and not this reader's.)

WHAT THE READER DELIBERATELY LEAVES BEHIND. The 5 order records
(elizabeth_bothfeld x2, wisconsin_business_leaders x2,
planned_parenthood_of_wisconsin) print 'The Court entered the following
order on this date:' BELOW the last fence. That is the order's own opening
sentence, not headmatter, and it is what core opens the order writing on —
the same call vt makes for its entry orders. Claiming it would take a row
out of a writing.

THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
has no `docket` and no `cite` field: the docket is `docket_number` plus
`other_dockets`, and the court's public-domain cite is `citation`. Written
under any other name they are attached by setattr and never serialize.
"""

from __future__ import annotations

import re
from statistics import median

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.headmatter import find_date

STYLE = "fenced letterhead"

# ---- wis's declared facts (measured over all 49 records, not tuned) ------

# THE FENCE. 190 drawn rects over the corpus, every one 118.5–118.8pt wide
# and centred on the page axis to within 0.4pt. The letterhead's head rule
# is 391.5pt, so the measure alone separates them; the axis is tested too,
# because the footnote separator (144.0pt at x0=108) is neither.
_FENCE_MEASURE = (100.0, 140.0)
_FENCE_AXIS = 6.0
# HOW MANY FENCES a record prints: 3 (5 records), 4 (16), 5 (28).
_FENCE_COUNT = (3, 5)
# A CENTRED BAND'S ROWS sit on the page axis — max measured offset 1.8pt.
# The announcement band's own minimum is 22.1pt, so the test has 20pt of
# clearance on both sides.
_AXIS_TOL = 6.0
# THE BAND'S GROUP BREAK. Inside a group the step is 15.0–17.5pt; between
# groups 23.8–34.9pt. Stated as a multiple of the band's OWN leading, so a
# record set on a different template still reads.
_GROUP_BREAK = 1.30
# THE ANNOUNCEMENT'S FIRST LINE is indented one 36pt step off the rail.
_RAIL_TOL = 2.0

# 'No. 2022AP790' / 'No. 2023AP1664-D' / 'No. 2025XX1438' /
# 'No. 2024AP330-OA' / 'No. 2023AP2319–CR' (an EN DASH on gasper) — this
# court's own docket, and only this court's.
_DOCKET = re.compile(r"^\d{4}[A-Z]{2}\d{1,5}(?:[-‐‑–][A-Z]{1,3})?$")
# The number a Wisconsin court BELOW gave the case: '2021CV1314', '2022TP86',
# '2023ME189', '2022JV71', '2016CF26', '2020SC979'.
_LOWER_DOCKET = re.compile(r"\b\d{4}[A-Z]{2}\d{1,6}\b")
# 'No. 2021CV1314' / 'No.' + '2018CV4971' across a wrap.
_LOWER_NO = re.compile(r"\bNos?\.?\s*(\d{4}[A-Z]{2}\d{1,6})\b")
# THE COURTS OF WISCONSIN, as this court names them in an origin statement.
# A closed vocabulary of court TYPES with the capitalised words that qualify
# them — never an open read of a court name.
_COURT_BELOW = re.compile(
    r"((?:[A-Z][\w.'’-]*\s+)*?(?:Circuit\s+Court|Court\s+of\s+Appeals))")
# THE BENCH TITLE a judge's name is printed with, inside the origin's own
# parenthesis: '(Susan M. Crawford, J.)', '(Shelley J. Gaylord, Reserve J.)'.
# A closed role vocabulary, so 'Milton L. Childs Sr., J.' is one person.
_BENCH_TITLE = re.compile(r"^(?:Reserve|Chief|Acting|Res\.)?\s*(?:C\.)?J\.$")
# 'REBECCA FRANK DALLET, J., delivered the majority opinion of the Court, in
# which …' — the announcement's own opening. The name ends at the
# abbreviated title, and the VERB is what says this is an announcement.
_ANNOUNCE = re.compile(
    r"^(?P<name>[A-Z][A-Z.’' -]*?,\s*(?:C\.)?J\.)"
    r"\s*,\s*(?:delivered|filed|wrote|announced)\b")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _italic(line) -> bool:
    """The row is set in ITALIC — the majority of its alphanumeric glyphs.
    Punctuation left roman inside an italic passage does not vote."""
    seen = ital = 0
    for c in line.chars:
        t = c.get("text") or ""
        if not any(ch.isalnum() for ch in t):
            continue
        seen += 1
        if any(s in (c.get("fontname") or "") for s in ("Italic", "Oblique")):
            ital += 1
    return seen > 0 and ital * 2 > seen


# --------------------------------------------------------------------------
# the visual row — every piece the page set on one baseline
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row. pdfio splits a justified line at its widest gaps, and
    the announcement band is justified, so a row is read as the pieces the
    page put on one baseline rather than piecewise."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold",
                 "italic", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.italic = all(_italic(p) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out

    def offset(self, page_width: float) -> float:
        return (self.x0 + self.x1) / 2 - page_width / 2

    def centred(self, page_width: float) -> bool:
        return abs(self.offset(page_width)) <= _AXIS_TOL


def _visual_rows(pm) -> list:
    """The page's content rows, in the page's own order."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [_Row(groups[k]) for k in order]


def _fences(pm) -> list:
    """The band fences this page draws, top to bottom."""
    return sorted(
        (r for r in (pm.h_rules or [])
         if _FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]
         and abs((r.x0 + r.x1) / 2 - pm.width / 2) <= _FENCE_AXIS),
        key=lambda r: r.top)


def _groups(band: list) -> list:
    """The band's rows, split where the page leaves a step bigger than its
    own leading. One group per printed party (or the matter title)."""
    if len(band) < 2:
        return [list(band)]
    steps = [b.top - a.top for a, b in zip(band, band[1:])]
    limit = _GROUP_BREAK * median(steps)
    out = [[band[0]]]
    for row, step in zip(band[1:], steps):
        if step > limit:
            out.append([row])
        else:
            out[-1].append(row)
    return out


# --------------------------------------------------------------------------
# the bands' own grammars
# --------------------------------------------------------------------------

def _is_pivot(row: _Row) -> bool:
    return row.italic and row.text.rstrip(".").strip().lower() == "v"


def _docket_row(text: str) -> list:
    """The dockets a row names, in order, or [] when it names none."""
    flat = _norm(text)
    low = flat.lower()
    for opener in ("nos.", "no."):
        if low.startswith(opener):
            flat = flat[len(opener):].strip()
            break
    else:
        return []
    parts = [p.strip() for p in re.split(r"[,;]|\band\b", flat) if p.strip()]
    return parts if parts and all(_DOCKET.match(p) for p in parts) else []


def _party_sides(groups: list) -> tuple:
    """(left, right, others) — the party names the caption prints.

    Built from the rows either side of the pivot, never by joining the
    band: a roman row is a name (and a name may wrap over two), an italic
    row is that party's status."""
    left: list[str] = []
    right: list[str] = []
    others: list[str] = []
    seen_pivot = False
    for group in groups:
        if not any(r.italic for r in group):
            continue                      # the matter title names no party
        names: list[str] = []
        buf: list[str] = []
        for row in group:
            if _is_pivot(row):
                if buf:
                    names.append(_norm(" ".join(buf)))
                    buf = []
                if names:
                    left.extend(names)
                    names = []
                seen_pivot = True
                continue
            if row.italic:                # a status closes the name above it
                if buf:
                    names.append(_norm(" ".join(buf)))
                    buf = []
                continue
            buf.append(row.text)
        if buf:
            names.append(_norm(" ".join(buf)))
        if not names:
            continue
        if seen_pivot and not right:
            right.extend(names)
        elif seen_pivot:
            others.extend(names)
        else:
            left.extend(names)
    trim = lambda s: s.rstrip(",;: ")     # noqa: E731
    return ([trim(n) for n in left], [trim(n) for n in right],
            [trim(n) for n in others])


def _judges(text: str) -> list:
    """The judge(s) below, out of the origin's own parentheses. The bench
    title is a closed role vocabulary, so a generational suffix stays with
    the name ('Milton L. Childs Sr., J.' is one person, and so is 'Shelley
    J. Gaylord, Reserve J.')."""
    out = []
    for inner in re.findall(r"\(([^)]*)\)", text):
        flat = _norm(inner).rstrip(";, ")
        head, sep, tail = flat.rpartition(",")
        if sep and _BENCH_TITLE.match(tail.strip()):
            flat = head.strip()
        if flat:
            out.append(flat)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The emit buffer and the criteria the bands fill."""

    def __init__(self, page_width: float, body_x0: float):
        self.page_width = page_width
        self.body_x0 = body_x0
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.summary: list = []
        self.announced: str | None = None

    def row(self, row: _Row, role: str, align: str = "C") -> None:
        rel = 0.0
        if align == "L":
            rel = round(row.x0 - self.body_x0, 1)
            if abs(rel) <= _RAIL_TOL:
                rel = 0.0
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, italic=row.italic, rel=rel, role=role))
        self.consumed.update(row.ids)

    def rule(self, page: int, span: str) -> None:
        self.items.append(m.Rule(prov=m.Prov(page), span=span))

    def result(self) -> dict:
        out = {"criteria": self.crit, "items": self.items, "attorneys": [],
               "dropped": self.dropped, "consumed": self.consumed,
               "summary": self.summary,
               "anchor_ids": [], "doc_type_final": None}
        if self.announced:
            out["announced_author"] = self.announced
        return out


@decider("headmatter.read", court="wis")
def read_headmatter_wis(model, geom, **_):
    """Read wis's fenced letterhead, or NOTHING."""
    if not model.pages:
        return NOTHING
    # THE BLOCK IS PAGE ONE, whole. The deepest fence in the corpus is at
    # top=659.3 (state_v._michael_joseph_gasper) on a 792pt page and every
    # record closes its block above the foot of the sheet, so the reader
    # never looks at a second page.
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 108.0
    fences = _fences(page1)
    # NO FENCE STACK, NO CLAIM. A record that does not print this paper is
    # left for core's shared walk.
    if not (_FENCE_COUNT[0] <= len(fences) <= _FENCE_COUNT[1]):
        return NOTHING
    foot = fences[-1].top
    rows = [r for r in _visual_rows(page1) if r.top < foot]
    if not rows:
        return NOTHING

    # THE LETTERHEAD: everything above the first fence. All 49 print exactly
    # one text row there — the court's public-domain cite, set above the
    # body size — and the court's name and seal, which are GRAPHICS.
    head = [r for r in rows if r.top < fences[0].top]
    body_size = geom.body_size if geom and geom.body_size else 12.0
    if len(head) != 1 or head[0].size <= body_size \
            or not head[0].centred(page1.width):
        return NOTHING

    # THE BANDS, each closed by its own fence.
    bands = []
    for lo, hi in zip(fences, fences[1:]):
        band = [r for r in rows if lo.top < r.top < hi.top]
        if not band:
            return NOTHING                # a fence pair always holds a band
        bands.append(band)
    if sum(len(b) for b in bands) + len(head) != len(rows):
        return NOTHING                    # a row fell between the fences

    # WHICH BAND IS WHICH — the pivot, the docket form, the page axis.
    kinds: list[str] = []
    for band in bands:
        if any(_is_pivot(r) for r in band):
            kinds.append("caption")
        elif _docket_row(band[0].text):
            kinds.append("docket")
        elif all(r.centred(page1.width) for r in band):
            kinds.append("origin")
        else:
            kinds.append("announcement")
    # …and the ORDER they come in is the contract. Anything else is not this
    # paper.
    if kinds[:2] != ["caption", "docket"] \
            or kinds[2:] not in ([], ["origin"], ["announcement"],
                                 ["origin", "announcement"]):
        return NOTHING

    ctx = _Ctx(page1.width, body_x0)
    # THE HEAD RULE — the letterhead's own 391.5pt line, three times the
    # fence's measure. A reader that claims the block re-emits its rules.
    for r in (page1.h_rules or []):
        if r.top < fences[0].top and r not in fences:
            ctx.rule(page1.number, "full")
    ctx.crit["headmatter_style"] = STYLE
    ctx.crit["citation"] = head[0].text
    ctx.row(head[0], "citation")

    for band, kind, fence in zip(bands, kinds, fences):
        # the fence that OPENS this band, drawn where the page draws it
        ctx.rule(page1.number, "center")
        if kind == "caption":
            _read_caption(ctx, band)
        elif kind == "docket":
            if not _read_docket(ctx, band):
                return NOTHING
        elif kind == "origin":
            _read_origin(ctx, band)
        else:
            _read_announcement(ctx, band)
    ctx.rule(page1.number, "center")      # …and the fence that closes it

    if not ctx.crit.get("docket_number"):
        return NOTHING
    return ctx.result()


# ---- the caption band ----------------------------------------------------

def _read_caption(ctx: _Ctx, band: list) -> None:
    groups = _groups(band)
    titled = True
    for group in groups:
        # A GROUP WITH NO ITALIC ROW standing above every group that has one
        # is the MATTER TITLE, not a party — the 15 disciplinary records set
        # 'IN THE MATTER OF DISCIPLINARY PROCEEDINGS AGAINST' over the
        # respondent's name and style him at law.
        if titled and not any(r.italic for r in group):
            for row in group:
                ctx.row(row, "case-info")
            continue
        titled = False
        for row in group:
            ctx.row(row, "caption")
    ctx.crit["caption"] = [r.text for r in band]
    # `parties` IS THE TWO SIDES OF THE PIVOT — the render joins the list
    # with ' v. ', so a third entry reads as a third side. Four records
    # (elizabeth_bothfeld x2, wisconsin_business_leaders x2) print an
    # INTERVENING party group below the pivot's own; it is a party, and it
    # is kept in `caption`, which is the verbatim record of the band, rather
    # than turned into 'A v. B v. C'.
    left, right, _others = _party_sides(groups)
    sides = [" ".join(left).strip(), " ".join(right).strip()]
    sides = [s for s in sides if s]
    if sides:
        ctx.crit["parties"] = sides
        ctx.crit["case_name"] = " v. ".join(sides)


# ---- the docket band -----------------------------------------------------

def _read_docket(ctx: _Ctx, band: list) -> bool:
    dockets: list[str] = []
    date = None
    for row in band:
        found = _docket_row(row.text)
        if found:
            dockets.extend(found)
            ctx.row(row, "docket")
            continue
        got = find_date(row.text)
        if got is None:
            return False                  # the band holds these two things
        date = date or got
        ctx.row(row, "date")
    if not dockets:
        return False
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    if date:
        ctx.crit["decision_date"] = date
    return True


# ---- the origin band -----------------------------------------------------

def _read_origin(ctx: _Ctx, band: list) -> None:
    """How the case came here, and the court it came from.

    Read as ONE statement, because the court wraps it: 'APPEAL from a
    judgment and an order of the Dane County Circuit' / 'Court (Diane
    Schlipper, J.), No. 2022CV1594' is one sentence in two rows, and
    'Milwaukee County Circuit Court (Christopher R. Foley, J.) No.' /
    '2018CV4971' breaks a docket across the measure."""
    whole = _norm(" ".join(r.text for r in band))
    courts = [_norm(c) for c in _COURT_BELOW.findall(whole)]
    role = "lower-court" if courts else "case-info"
    for row in band:
        ctx.row(row, role)
    ctx.crit["history"] = whole.rstrip(".")
    if courts:
        ctx.crit["lower_court"] = "; ".join(dict.fromkeys(courts))
    numbers = _LOWER_NO.findall(whole) or _LOWER_DOCKET.findall(whole)
    if numbers:
        ctx.crit["lower_court_docket"] = list(dict.fromkeys(numbers))
    judges = _judges(whole)
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)


# ---- the announcement band ----------------------------------------------

def _join(pieces: list) -> str:
    """The band's rows as ONE paragraph. The court justifies the
    announcement to the measure, so its rows are a wrap and not lines."""
    text = ""
    for piece in pieces:
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return text



def _read_announcement(ctx: _Ctx, band: list) -> None:
    """The court announcing who wrote what — a justified paragraph at the
    body rail, kept whole, wrap and all. The roster inside it is recorded as
    PRINTED: parsing 'ANNETTE KINGSLAND ZIEGLER, REBECCA GRASSL BRADLEY,
    REBECCA FRANK DALLET, and JANET C. PROTASIEWICZ, JJ., joined' into names
    yields a justice called 'and', and the printed line is the fact."""
    whole = _norm(" ".join(r.text for r in band))
    # THE ANNOUNCEMENT IS A SECTION OF ITS OWN, not a row of the block. It is
    # the court's own account of who wrote what and who joined -- prose, in
    # sentences, and the only prose the letterhead prints. Emitted as
    # headmatter rows it rendered as four ragged lines labelled 'author'
    # inside the caption's furniture; handed over as `summary` it renders as
    # the paragraph it is, below the block (the user, 2026-08-20: 'the
    # headmatter has section author lets make it summary').
    ctx.summary.append(m.Paragraph(
        text=_join([r.markup() for r in band]),
        prov=m.Prov(band[0].page, tuple(i for r in band for i in r.ids))))
    ctx.consumed.update(i for r in band for i in r.ids)
    ctx.crit["panel_line"] = whole
    match = _ANNOUNCE.match(whole)
    if match:
        # …and the name it announces goes to core as ``announced_author``,
        # the contract va and tenn use. wis SIGNS every writing it prints
        # ('¶1 BRIAN HAGEDORN, J. This is …'), so core will not need it —
        # but a signature always outranks an announcement, and reporting it
        # costs nothing and covers an unsigned paper.
        ctx.announced = match.group("name")


# --------------------------------------------------------------------------
# image.role — this court's letterhead IS a picture
# --------------------------------------------------------------------------
# Measured over the corpus: every record prints its letterhead as two
# graphics on page one and prints no other graphic anywhere —
#
#     364.1x33.7   the court's WORDMARK, set at x0 123.8 across the axis
#      73.6x72.5   the court's SEAL, centred on the page axis beneath it
#
# — and both stand ABOVE THE FIRST FENCE, the same landmark this reader cuts
# its own bands on (the shallowest fence measured opens at top 257.5; the
# seal closes at 242.5). No page of this court prints a figure.
#
# Left to core's geometry the seal was neither above all the type — the
# citation ('2025 WI 53') is set above the letterhead, not below it — nor
# small enough to ignore, so it was read as a printed exhibit and carried
# into the body as a data URI: the court's seal planted inside the order
# (the user, 2026-08-20: 'lets pull the court seal on every one').
@decider("image.role", court="wis")
def image_role_wis(page=None, image=None, **_):
    """Stationery, surfaced as a removal with the reason the page shows.
    NOTHING for a graphic standing below the letterhead, where core's own
    geometry is a better answer than this court's guess."""
    if page is None or image is None or page.number != 1:
        return NOTHING
    fences = _fences(page)
    if not fences or image.bottom > fences[0].top:
        return NOTHING
    wide = (image.x1 - image.x0) > 2.5 * (image.bottom - image.top)
    return "the court's wordmark" if wide else "the court's seal"
