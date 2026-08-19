"""Supreme Court of North Dakota ('nd').

Everything unique to nd lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'fenced citation and docket'. North Dakota sets one paper,
and it FENCES the two numbers it assigns the case. Page 1 draws an even
number of horizontal vector rules in a single invariant measure — 218.9pt
wide, x0=196.6, centred on the 612pt page's axis — and they come in PAIRS
27.7 to 34.7pt apart. The pairs, not the words, name every zone:

    [seal]                                        an image, 200x50pt
    IN THE SUPREME COURT                          the masthead, 16pt
    STATE OF NORTH DAKOTA
    ──────────────────────                        FENCE (218.9pt, on axis)
    2026 ND 72                                    the NEUTRAL CITATION
    ──────────────────────                        FENCE
    Jarrod Jashawn Adams,        Petitioner and Appellant   the caption:
         v.                                       party left, STATUS right
    State of North Dakota,       Respondent and Appellee
    ──────────────────────                        FENCE
    No. 20250337                                  the DOCKET
    ──────────────────────                        FENCE
    Appeal from the District Court of Grand Forks County, Northeast
    Central Judicial District, the Honorable M. Jason McCarthy, Judge.
    AFFIRMED.                                     the disposition
    Per Curiam.                                   the announced author
    Kiara C. Kraus-Parr, Grand Forks, ND, for petitioner and appellant;
    on brief.                                     the appearances

    ────────────── page 2 (or 3) ──────────────
    Adams v. State                                the writing's TITLE BLOCK
    No. 20250337                                  — bold, centred, once
    Per Curiam.                                   the byline. The reader
    [¶1] Jarrod Jashawn Adams appeals …           stops here.

The fence measure is the same on all 50 records and the fence count is 4
or 6. Pair 0 always holds the neutral citation; every LATER pair holds a
docket, and the band BETWEEN two consecutive pairs is a caption. A
CONSOLIDATED record is fenced the same way — it prints a second caption
and a second docket inside its own pair (interest_of_d.g.,
interest_of_m.s.h.), so 'two cases heard together' needs no special case:
it is just a third pair. A record that draws no such pair is not this
contract and gets NOTHING; core's shared walk places those rows
unidentified, which is a smaller error than a confident misreading.

THE CAPTION IS TWO COLUMNS WITH NO DIVIDER — nd draws neither rule nor
glyph between them, so the columns are read off the two RAILS the page
sets them against:

  * the LEFT column stands at the BODY RAIL (x0=72.0 on every record;
    the 'v.' pivot and the co-party joiner 'and' one 36pt step in at
    108.0), and it is ragged right — the longest left row in the corpus
    closes at x1=424.0, 116pt short of the measure;
  * the RIGHT column is FLUSH RIGHT on the CAPTION'S OWN right rail
    (x1=540.0, never left of 522.0), and never opens left of x0=289.9.

Measured inside the band, never across the headmatter: marschner's
'Plaintiff, Appellee, and Cross-Appellant' opens at x0=304.3, LEFT of the
page axis, and a shared 0.6-of-the-width test reads it as an indent
instead of a flush-right cell.

THE STATUS LABEL IS THE CAPTION'S DELIMITER. North Dakota sets a party's
status on the LAST row of the group it labels, so a party that runs to six
rows (rousseau_v._armstrong: 'Governor Kelly Armstrong,' … 'process,') is
one party because only its last row carries a cell in the right column.
Nothing is grouped by leading — the same 22.3pt step that separates two
parties in one record continues a single party's name in another.

A CAPTION MAY OPEN WITH A PREAMBLE — the matter's own title ('In the
Interest of B.P., Child', 'In the Matter of the Adoption of K.J.K.'). It is
the band's first row, it carries no cell in the right column, and it stands
37.8 to 44.5pt above the first party where the caption's own step is never
more than 24.9pt. It is caption, and it is not a party.

NORTH DAKOTA ANNOUNCES ITS AUTHOR AND THEN SIGNS. Page 1 states 'Opinion
of the Court by Tufte, Justice.' (32 records) or 'Per Curiam.' (18) in
roman type at the body rail; the writing opens overleaf with the same name
set BOLD. Both are true, and the announcement is headmatter: left in the
stream it parsed as a second byline and every per-curiam record rendered
two writings, one of them holding nothing but the title block.

THE WRITING'S TITLE BLOCK IS NOT A RUNNING HEAD. The short case name and
the docket are set bold and centred at the top of the opinion's FIRST page
and on no other page, so core's repetition test can never see them (nd's
`top_keys` is empty on all 50 records) — they rendered as a centred heading
inside the writing, or, where a consolidated record put them a page later,
as the tail of the counsel block. The reader claims them as furniture,
records them as Dropped, and keeps the short case name.

The reader ends at the first ALL-BOLD row AT THE BODY RAIL, which is the
byline. It never reaches into a writing: the byline itself is left in the
stream, so assembly anchors exactly where it did before.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# nd's profile is registered in the shared table; this file owns its reader
# only. Look it up rather than re-declaring it, so the byline grammar can
# never drift from the one assembly uses (and so importing this module can
# never raise 'duplicate profile', which would break EVERY court).
ND: CourtProfile = PROFILES["nd"]

STYLE_FENCED = "fenced citation and docket"

# ---- nd's declared facts (measured over the corpus, not tuned) -----------
# THE FENCE: a drawn horizontal vector rule, 218.9pt wide on every rule of
# every record, x0=196.6 on a 612pt page — its midpoint is the page axis to
# within 0.05pt. Expressed as a fraction of the page width so it survives a
# different paper size (218.9/612 = 0.3577).
_FENCE_MEASURE = 0.3577
_FENCE_MEASURE_TOL = 0.02
# …and it must stand ON THE PAGE AXIS. The same measure off the axis means
# something else entirely: nd draws its FOOTNOTE separator as a short
# (~143pt) left-anchored vector line, and a width test alone would take it.
_FENCE_AXIS_TOL = 6.0
# THE PAIR: two fences 27.7pt apart on 48 records and 33.8 to 34.7pt on the
# rest, where the compositor left the caption above them short. No two
# fences of DIFFERENT pairs ever stand closer than 99.5pt.
_PAIR_MAX = 60.0
# THE FENCE COUNT is 4 (48 records) or 6 (the two consolidated ones), so at
# least two pairs: one for the citation and one for the docket.
_MIN_PAIRS = 2
# ROWS ON ONE BASELINE. A caption row's two cells share their top to within
# 0.1pt; the tightest DIFFERENT baselines in the block are 15.7pt apart.
_SAME_ROW = 3.0
# THE CAPTION'S RIGHT RAIL. Every status cell closes between x1=522.0 and
# x1=540.0; the longest LEFT row closes at 424.0.
_RIGHT_RAIL_TOL = 24.0
# …and no status cell opens left of x0=289.9, while every left row opens at
# the body rail (72.0) or one 36pt step in (108.0).
_RIGHT_MIN_INSET = 120.0
# THE PREAMBLE'S STAND-OFF: 37.8pt (18.9pt captions) or 44.5pt (22.3pt ones)
# where the caption's own step never exceeds 24.9pt.
_CAP_PREAMBLE_MIN = 30.0
# BELOW THE LAST FENCE the leading is binary: 15.7, 15.8 or 18.9pt continues
# the statement above, 28.7, 28.8 or 31.9pt opens a new one. Nothing in the
# corpus falls between 18.9 and 28.7.
_TAIL_WRAP_MAX = 24.0
# THE PIVOT AND THE JOINER: one 36pt step in from the body rail, and short.
_PIVOT_INDENT = 36.0
_RAIL_SNAP = 3.0
# THE TITLE BLOCK sits in the top 16% of the opinion's first page (74.5 and
# 89.9pt of 792), bold and centred; the byline follows at 118.4.
_HEAD_BAND = 0.16
# The whole front matter closes on page 1 (48 records), page 2 (the two
# consolidated ones, whose counsel block runs over) — the byline is never
# later than page 3.
_MAX_PAGES = 4

# THE ORIGIN, as North Dakota names the tribunal it is reviewing. All 50
# records open it 'Appeal from the …'; the rest of the openers are the forms
# the court uses elsewhere and are listed so a record that states one is
# read rather than dropped into counsel.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "cross-appeal from", "cross-appeals from",
    "on appeal from", "certified question", "original proceeding",
    "petition for", "on petition for", "on certification", "on remand from",
)
# THE ANNOUNCEMENT: 'Opinion of the Court by Tufte, Justice.' — the court
# naming its own author, in roman, at the body rail.
_ANNOUNCE_OPENER = "opinion of the court by"
_PER_CURIAM = ("per curiam", "per curiam.")
# …and the name inside it, cut at the judicial TITLE so the joinder clause
# ('…, in which Justices Jensen and Bahr joined.') is not read as part of
# the name.
_ANNOUNCED = re.compile(
    r"^Opinion of the Court by\s+(.+?),\s*"
    r"((?:Chief\s+|Surrogate\s+)?Justice|District Judge)\b", re.IGNORECASE)
# THE TRIAL JUDGE, as the origin statement names them — the last clause of
# the sentence, on all 50 records.
_TRIAL_JUDGE = re.compile(
    r",\s*(?:the\s+)?Honorable\s+(.+?),\s*"
    r"((?:Surrogate\s+|Special\s+|Presiding\s+)?"
    r"(?:Judicial\s+Referee|Judge))\.?\s*$", re.IGNORECASE)
# THE PIVOT and THE JOINER, as short rows one step in from the rail.
_PIVOTS = ("v.", "v", "vs.", "vs")
_JOINERS = ("and", "and,")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_caps(text: str) -> bool:
    """ALL-CAPS as the court sets its disposition ('AFFIRMED IN PART,
    REVERSED IN PART, AND REMANDED.'). Digits and punctuation do not vote."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _is_author(text: str) -> bool:
    low = _norm(text).lower()
    return low.startswith(_ANNOUNCE_OPENER) or low in _PER_CURIAM


def _is_masthead(text: str) -> bool:
    """The court naming itself. Applied ONLY above the first fence, which is
    what keeps 'Appeal from the District Court …' out of it."""
    low = _norm(text).lower().rstrip(".")
    return low in ("in the supreme court", "state of north dakota",
                   "supreme court of north dakota",
                   "in the supreme court of north dakota")


# --------------------------------------------------------------------------
# the fences — nd's one contract, and the dispatch
# --------------------------------------------------------------------------

def _fences(pm) -> list[float]:
    """The tops of page ``pm``'s fence rules, in page order.

    A fence is the court's own invariant measure standing on the page axis.
    Both halves matter: the measure alone takes the footnote separator on a
    later page, and the axis alone takes any full-measure table border.
    """
    out: list[float] = []
    width = pm.width or 612.0
    for rule in pm.h_rules:
        if abs(rule.width / width - _FENCE_MEASURE) > _FENCE_MEASURE_TOL:
            continue
        if abs((rule.x0 + rule.x1) / 2.0 - width / 2.0) > _FENCE_AXIS_TOL:
            continue
        out.append(float(rule.top))
    return sorted(out)


def _pairs(tops: list[float]) -> list[tuple[float, float]]:
    """The fences taken in PAIRS, top to bottom. A pair is two fences closer
    together than any two fences of different pairs; an unpaired fence means
    this is not the contract and the caller returns NOTHING."""
    out: list[tuple[float, float]] = []
    i = 0
    while i + 1 < len(tops):
        if tops[i + 1] - tops[i] > _PAIR_MAX:
            return []
        out.append((tops[i], tops[i + 1]))
        i += 2
    return out if i == len(tops) else []


# --------------------------------------------------------------------------
# the caption's two columns
# --------------------------------------------------------------------------

def _split_at_widest_gap(line):
    """``line`` cut into (left, right) at its widest interior whitespace.

    Whether pdfio already broke a caption row at its column gap is an
    accident of how wide the gap happened to be — the same corpus sets a
    25.4pt gap (alber) and an 85.3pt one (marschner). Every row in this
    corpus arrives split; a row that spans BOTH rails is cut here rather
    than filed whole into one column by luck.
    """
    inked = [c for c in line.chars if (c.get("text") or "").strip()]
    if len(inked) < 2:
        return line, None
    best, at = 0.0, None
    for a, b in zip(inked, inked[1:]):
        gap = b["x0"] - a.get("x1", a["x0"])
        if gap > best:
            best, at = gap, b["x0"]
    if at is None or best < 12.0:
        return line, None
    left = [c for c in line.chars if c["x0"] < at]
    right = [c for c in line.chars if c["x0"] >= at]
    if not (any((c.get("text") or "").strip() for c in left)
            and any((c.get("text") or "").strip() for c in right)):
        return line, None
    return (_replace(line, chars=left,
                     x0=min(c["x0"] for c in left),
                     x1=max(c.get("x1", c["x0"]) for c in left)),
            _replace(line, chars=right,
                     x0=min(c["x0"] for c in right),
                     x1=max(c.get("x1", c["x0"]) for c in right)))


def _columns(rows: list, body_x0: float, right_rail: float):
    """Each visual row of the caption band as (left_pieces, right_pieces).

    Column membership is decided by the two RAILS the page sets, never by
    what a row says: at the body rail (or one 36pt step in) it is a party,
    flush right on the caption's own rail it is that party's status.
    """
    out: list[tuple[list, list]] = []
    for row in rows:
        left, right = [], []
        for line in sorted(row, key=lambda l: l.x0):
            pieces = [line]
            if (line.x0 <= body_x0 + _PIVOT_INDENT + _RAIL_SNAP
                    and line.x1 >= right_rail - _RIGHT_RAIL_TOL):
                a, b = _split_at_widest_gap(line)
                pieces = [a, b] if b is not None else [a]
            for piece in pieces:
                if (piece.x1 >= right_rail - _RIGHT_RAIL_TOL
                        and piece.x0 >= body_x0 + _RIGHT_MIN_INSET):
                    right.append(piece)
                else:
                    left.append(piece)
        out.append((left, right))
    return out


def _parties(cells: list[tuple[str, bool]]) -> tuple[list[str], list[str]]:
    """The caption's party groups, either side of the pivot.

    ``cells`` is the left column top to bottom as (text, closed), where
    ``closed`` says the row carries a cell in the RIGHT column — the status
    label North Dakota sets on the last row of the group it labels. That
    label, not the leading, ends a party.
    """
    left: list[str] = []
    right: list[str] = []
    side, seen, group = left, False, []

    def flush():
        if group:
            joined = _norm(" ".join(group)).rstrip(",; ")
            if joined:
                side.append(joined)
            group.clear()

    for text, closed in cells:
        flat = _norm(text)
        if not flat:
            continue
        head = flat.rstrip(".,").lower()
        if head in _PIVOTS and len(flat) <= 4:
            flush()
            side, seen = right, True
            continue
        if head in _JOINERS:
            flush()
            continue
        group.append(flat)
        if closed:
            flush()
    flush()
    return left, right


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="nd")
def read_headmatter_nd(model, geom, **_):
    """Read nd's fenced headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    pairs = _pairs(_fences(page1))
    if len(pairs) < _MIN_PAIRS:
        return NOTHING              # no fence pair: not nd's paper

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    parser = BylineParser(ND.byline)
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS the reader may see. Furniture core already measured is not
    # claimed twice: nd's page foot is a bare folio and core reads it.
    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if line.plain.strip() and finder.kind(pm, line) is None:
                rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    # THE END OF THE READER: the first ALL-BOLD row at the body rail that
    # also PARSES as a byline under the court's own grammar. Geometry and
    # grammar must agree — the writing's title block is bold too, but it is
    # centred and it parses as nothing; nothing on page 1 is bold at all.
    # The byline itself is never claimed, so assembly anchors where it did.
    byline = next((l for l in rows
                   if l.all_bold and abs(l.x0 - body_x0) <= _RAIL_SNAP
                   and parser.parse(_norm(l.plain)) is not None), None)
    if byline is None:
        return NOTHING              # no byline in the front matter: not nd's
    stop = (byline.page, byline.top)
    rows = [l for l in rows if (l.page, l.top) < stop]

    # THE WRITING'S TITLE BLOCK — bold and centred in the head band of the
    # byline's own page, printed once in the whole document. It is furniture,
    # and it is taken OUT of the reader's rows before they are read: left in,
    # it read as one more counsel entry (nd's counsel block is the last thing
    # above it, and a page break carries no leading to measure).
    head_page = pages[byline.page]
    head = sorted((l for l in rows
                   if l.page == byline.page and l.all_bold
                   and l.top < (head_page.height or 792.0) * _HEAD_BAND
                   and abs(l.x0 - body_x0) > _RAIL_SNAP),
                  key=lambda l: l.top)
    head_ids = {l.id for l in head}
    rows = [l for l in rows if l.id not in head_ids]

    crit: dict = {"headmatter_style": STYLE_FENCED}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    unread: list = []
    masthead: list[str] = []
    caption_rows: list[str] = []
    parties: list[str] = []
    dockets: list[str] = []
    citations: list[str] = []
    origin_rows: list[str] = []
    disposition_rows: list[str] = []
    counsel_rows: list[str] = []
    announced: str | None = None
    case_name: str | None = None

    def hmline(parts, role: str, align: str | None = None,
               rel: float = 0.0) -> m.HmLine:
        """One HEADMATTER ROW, from the one or more pieces the page set on
        that baseline. Provenance survives the merge."""
        parts = sorted(parts, key=lambda l: l.x0)
        first = parts[0]
        pm = pages[first.page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        if align is None:
            align = line_alignment(first, pm.width, geom,
                                   banner_center_min_size=body_size + 2.0)
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), rel=rel, role=role)

    def emit(parts, role: str, align: str | None = None, rel: float = 0.0):
        row = hmline(parts if isinstance(parts, list) else [parts],
                     role, align, rel)
        items.append(row)
        consumed.update(row.prov.line_ids)
        return row

    def fence(after):
        """A FENCE RENDERS WHERE THE PAGE DRAWS IT. Core re-sorts the block
        by the source position of each item's provenance, so a rule carrying
        none sorts to the end; it takes the prov of the row it stands under
        and stays put."""
        items.append(m.Rule(
            prov=m.Prov(after.prov.page, after.prov.line_ids)
            if after is not None else m.Prov(page1.number),
            span="center"))

    def baselines(band: list) -> list[list]:
        out: list[list] = []
        for line in sorted(band, key=lambda l: (l.page, l.top, l.x0)):
            if out and out[-1][0].page == line.page \
                    and abs(out[-1][0].top - line.top) <= _SAME_ROW:
                out[-1].append(line)
            else:
                out.append([line])
        return out

    page1_rows = [l for l in rows if l.page == 1]
    last = None

    # ---- the masthead: everything page 1 prints above the first fence ----
    masthead_fonts: set[str] = set()
    for row in baselines([l for l in page1_rows if l.top < pairs[0][0]]):
        text = _norm(" ".join(l.plain for l in row))
        if _is_masthead(text):
            masthead.append(text)
            masthead_fonts.update(l.font for l in row)
            last = emit(row, "court", align="C")
        else:
            unread.append(row)      # recorded, never silently swallowed
    fence(last)

    # ---- the fenced zones, pair by pair ---------------------------------
    # Pair 0 holds the NEUTRAL CITATION the court assigns its own opinion —
    # neither a docket nor a companion appeal. Every later pair holds a
    # docket, and the band between two consecutive pairs is a caption.
    for index, (top, bottom) in enumerate(pairs):
        inside = [l for l in page1_rows if top < l.top < bottom]
        role = "citation" if index == 0 else "docket"
        for row in baselines(inside):
            text = _norm(" ".join(l.plain for l in row))
            last = emit(row, role, align="C")
            (citations if index == 0 else dockets).append(text.rstrip(","))
        fence(last)

        nxt = pairs[index + 1][0] if index + 1 < len(pairs) else None
        if nxt is None:
            break
        band = baselines([l for l in page1_rows if bottom < l.top < nxt])
        if not band:
            continue

        # THE CAPTION. Its columns are the two rails, and its right rail is
        # measured INSIDE the band — never across the headmatter.
        right_rail = max(l.x1 for row in band for l in row)
        columns = _columns(band, body_x0, right_rail)

        # A PREAMBLE is the band's first row carrying no cell in the right
        # column and standing further above the first party than the
        # caption's own step ever reaches.
        preamble = 0
        if len(band) > 1 and not columns[0][1] and columns[0][0]:
            if band[1][0].top - band[0][0].top >= _CAP_PREAMBLE_MIN:
                preamble = 1

        left_cells: list = []
        right_cells: list = []
        cells: list[tuple[str, bool]] = []
        cap_ids: list[int] = []
        own_x0 = min((p.x0 for l, _r in columns for p in l), default=body_x0)
        for pos, (row, (left, right)) in enumerate(zip(band, columns)):
            cap_ids.extend(l.id for l in row)
            rel = 0.0
            if left and left[0].x0 > own_x0 + _RAIL_SNAP:
                rel = min(left[0].x0 - own_x0, (page1.width or 612.0) * 0.5)
            left_cells.append(
                hmline(left, "caption", align="L", rel=rel) if left
                else m.HmLine(text="", prov=m.Prov(band[pos][0].page),
                              role="caption"))
            right_cells.append(
                hmline(right, "caption", align="R") if right
                else m.HmLine(text="", prov=m.Prov(band[pos][0].page),
                              role="caption"))
            text = _norm(" ".join(l.plain for l in left))
            if text:
                caption_rows.append(text)
            if pos >= preamble:
                cells.append((text, bool(right)))
            status = _norm(" ".join(l.plain for l in right))
            if status:
                caption_rows.append(status)

        items.append(m.CaptionBlock(
            left=left_cells, right=right_cells, rail=None, rail_rows=0,
            style_id="whitespace-gutter",
            fp={"rail": None, "right_rail": right_rail,
                "body_x0": own_x0},
            prov=m.Prov(page1.number, tuple(sorted(set(cap_ids))))))
        consumed.update(cap_ids)
        last = left_cells[-1] if _strip_tags(left_cells[-1].text).strip() \
            else right_cells[-1]

        lefts, rights = _parties(cells)
        for name in lefts + rights:
            if name not in parties:
                parties.append(name)
        if case_name is None and lefts and rights:
            case_name = f"{lefts[0]} v. {rights[0]}"
        elif case_name is None and lefts:
            case_name = lefts[0]

    # ---- the tail: origin, disposition, announced author, appearances ----
    # Below the last fence the leading is binary — 15.7 to 18.9pt continues
    # the statement above it, 28.7pt or more opens a new one. Each new
    # statement names itself; a continuation inherits the role.
    tail = baselines([l for l in rows
                      if l.page > 1 or l.top > pairs[-1][1]])
    state: str | None = None
    prev = None
    for row in tail:
        text = _norm(" ".join(l.plain for l in row))
        first = row[0]
        wrap = (prev is not None and state is not None
                and first.page == prev[0].page
                and first.top - prev[0].top <= _TAIL_WRAP_MAX)
        if wrap:
            role = state
        elif _origin_opener(text):
            role = "lower-court"
        elif _is_author(text):
            role = "author"
        elif _is_caps(text):
            role = "disposition"
        else:
            role = "counsel"
        if role == "lower-court":
            if wrap and origin_rows:
                origin_rows[-1] = f"{origin_rows[-1]} {text}"
            else:
                origin_rows.append(text)
        elif role == "disposition":
            disposition_rows.append(text)
        elif role == "author":
            if not wrap:
                hit = _ANNOUNCED.match(text)
                if hit and announced is None:
                    announced = f"{_norm(hit.group(1))}, {_norm(hit.group(2))}."
        else:
            counsel_rows.append(text)
        emit(row, role, align="L")
        state, prev = role, row

    # THE TITLE BLOCK, recorded — a claim must be TOTAL, and its short case
    # name is the only place the document states one.
    if head:
        crit.setdefault("short_case_name", _norm(head[0].plain))
        dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in head)),
            prov=m.Prov(byline.page, tuple(l.id for l in head)),
            kind="running-head"))
        consumed.update(head_ids)

    # ---- what the block says ---------------------------------------------
    if masthead:
        crit["court"] = _norm(" ".join(masthead))
    if citations:
        crit["citation"] = citations[0]
    if dockets:
        # THE LEAD CASE'S NUMBER IS THE DOCKET; a consolidated record fences
        # a second one of its own, and that is a companion appeal.
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit["other_dockets"] = dockets[1:]
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name
    if origin_rows:
        crit["lower_court"] = "; ".join(origin_rows)
        judges: list[str] = []
        for text in origin_rows:
            hit = _TRIAL_JUDGE.search(text)
            if hit:
                who = f"{_norm(hit.group(1))}, {_norm(hit.group(2))}"
                if who not in judges:
                    judges.append(who)
        if judges:
            crit["lower_court_judge"] = "; ".join(judges)
    if disposition_rows:
        crit["disposition"] = " ".join(disposition_rows)
    if counsel_rows:
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]

    # ---- a claim must be TOTAL ------------------------------------------
    # The only row the corpus prints above the first fence that is not the
    # masthead is a CLERK'S STAMP applied after typesetting ('Substitute
    # Opinion Pages 5-11 Filed 2/25/26 by Clerk of the Supreme Court' —
    # pederson_v._state). The TYPEFACE is the evidence: the court sets its
    # own page in QTPalatine and the clerk's line arrives in
    # CenturySchoolbook. A row in the court's own face is a notice.
    for row in unread:
        kind = "notice" if any(l.font in masthead_fonts for l in row) \
            else "stamp"
        dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in row))[:1200],
            prov=m.Prov(row[0].page, tuple(l.id for l in row)),
            kind=kind))
        consumed.update(l.id for l in row)

    out = {"criteria": crit, "items": items, "attorneys": [],
           "dropped": dropped, "consumed": consumed,
           "anchor_ids": [], "doc_type_final": None}
    if announced:
        out["announced_author"] = announced
    return out
