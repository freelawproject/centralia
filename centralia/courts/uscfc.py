"""United States Court of Federal Claims ('uscfc') — an Article I trial court.

THE PAPER. Two chambers keep two templates and the court prints both under
the same engraved masthead, `In the United States Court of Federal Claims`,
set at twice the body size across most of the measure. What stands under it
says which template this is, and the answer is DRAWN or TYPED — never a
word:

  1. `special master's ruled box` (30 of 32). The Office of Special Masters
     hears the Vaccine Act docket, and its cover fences the caption with a
     backwards C: one DRAWN vertical between the columns, a DRAWN horizontal
     across its head and another across its foot, both running from the body
     rail and STOPPING AT the vertical. ca9's figure and cit's exactly.

        CORRECTED                       a stamp on the paper, 10pt, centred
        In the United States Court of Federal Claims
              OFFICE OF SPECIAL MASTERS
                    No. 23-0033V
        ─────────────────────────────┐
        KRISTY ANDERSON,             │  Chief Special Master Corcoran
              Petitioner,            │  Filed: June 26, 2026
        v.                           │
        SECRETARY OF HEALTH AND      │
        HUMAN SERVICES,              │
              Respondent.            │
        ─────────────────────────────┘
        Jimmy Zgheib, Zgheib Sayad, PC, White Plains, NY, for Petitioner.
        Irene Angelica Firippis, U.S. Department of Justice, …, for Respondent.
                 DECISION ON ATTORNEY'S FEES AND COSTS
                 ─────────────────────────────────────   the writing opens

     THE RIGHT-HAND COLUMN IS THE BENCH. It carries the officer who decided
     the case and the day the paper was filed, and nothing else — over 30
     records it is those two rows or, where the chambers sets the date above
     the box instead (goodnight, moore), the officer alone.

  2. `judge's typed fence` (2 of 32). A judge of the court fences the same
     caption with TYPED rules instead of drawn ones — a row of asterisks
     above the parties and another below them (davis), or a row of
     underscores with a stacked ')' rail between the columns (dutch_ridge).
     The docket and the dates stand centred between the masthead and the
     first fence; the appearances stand below the last one with a hanging
     indent.

WHERE THE COVER ENDS: AT THE PAPER'S OWN NAME. Neither template prints a
prose byline on page 1 — the special master signs `s/Brian H. Corcoran`
three pages later and the judge signs the same way — so the landmark that
closes the cover is the row naming what the paper IS: `DECISION ON
ATTORNEY'S FEES AND COSTS`, `RULING ON ENTITLEMENT`, `OPINION AND ORDER`,
set on the page axis and UNDERLINED with a drawn rule whose ends coincide
with the row itself. All 32 records print one. That row is NOT claimed: it
is the writing's own heading, and core opens the opinion on it.

WHAT IS AND IS NOT A RULE. The court draws four kinds of horizontal on page
1 and only one of them is a fence: the caption box's head and foot (a fence),
the title's underline (an underline — its ends coincide with the row above),
the footnote separator (144pt at the body rail, below the zone) and the
hyperlink underline the Vaccine Rule 18(b) notice carries under its govinfo
URL (again coincident with its row). ca5's test tells all four apart.

THE DATE IS A LABEL, NOT A POSITION. `Filed:` inside the box, `Filed:` bold
above it, `(Filed: May 20, 2026)` parenthesised on the judge's stock, and
`Re-issued: May 20, 2026` where an opinion first issued under the protective
order is re-published with the parties' redactions adopted. The re-issue is
recorded as the paper's HISTORY: it is a fact about this document and not
the decision date.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import learn_vocabulary, line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# THE BENCH. A special master is not a judge and an absent profile would
# leave core reading 'Justice' only — every 'Chief Special Master' and
# 'Senior Judge' signature would parse as nothing and each authored decision
# would be typed 'order'. Longest title first: the parser takes the first
# match and 'Special Master' would eat the head of 'Chief Special Master'.
# `single_writing` is NOT declared — see below.
USCFC = register(CourtProfile(
    "uscfc", "United States Court of Federal Claims",
    byline=BylineGrammar(
        style="prose",
        titles=("Chief Special Master", "Special Master", "Chief Judge",
                "Senior Judge", "Judge"),
        allow_titlecase_name=True),
))

STYLE_OSM_BOX = "special master's ruled box"
STYLE_TYPED_FENCE = "judge's typed fence"

# ---- uscfc's declared facts (measured over the corpus, not tuned) --------
# THE BOX. Its vertical stands at x=292.3-292.4 on every one of the 30 OSM
# records — 0.478 of a 612pt page. The band admits a chambers that sets the
# columns a little differently without admitting the page's own axis.
_BOX_VRULE_BAND = (0.40, 0.62)
# The shortest box in the corpus is 135pt tall (booth, houle, kerr: a
# four-row caption); the tallest is 222pt (jacobs, an estate).
_BOX_VRULE_MIN_H = 90.0
# The head and foot run from the body rail (72.0) to the vertical: 220.3pt
# measured, invariant. Nothing else on the page draws a horizontal that long
# except the title's underline, and that one coincides with its row.
_BOX_RULE_MIN_W = 150.0
# HOW CLOSE THE STROKES OF ONE FIGURE COME. Measured: the vertical starts
# 0.3-0.6pt below the head and ends flush with the foot.
_BOX_JOIN = 12.0
# AN UNDERLINE IS A RULE WHOSE ENDS COINCIDE WITH THE ROW ABOVE IT. The
# court sets the title's rule under the WORDS and not under the footnote
# mark that rides on them, so the right end falls up to 5.1pt short
# (anderson: row 169.1-442.8, rule 169.1-437.8). The drop from the row's top
# to the rule is 8.8-12.0pt on a 12pt body.
_UNDERLINE_TOL = 8.0
_UNDERLINE_DROP = 20.0
# THE TITLE IS ON THE PAGE AXIS. Measured centre offsets over 32 records:
# 0.0-2.0pt. 25pt is core's own centring tolerance.
_TITLE_AXIS_TOL = 25.0
# A TYPED FENCE is a row of one glyph. davis types 25 asterisks, dutch_ridge
# 40 underscores; ten is well under either and well over any ellipsis.
_FENCE_MIN_GLYPHS = 10
# THE TYPED RAIL IS A COLUMN. dutch_ridge stacks 13 ')' glyphs within 4.0pt
# of x=329.4; 24pt admits a chambers that tabs the glyph on party rows.
_RAIL_COLUMN_TOL = 24.0
_RAIL_MIN_ROWS = 4
# A visual row is what the page printed on one line; pdfio splits a row at
# the caption's vertical and at wide column gaps.
_ROW_BAND = 2.5
# HOW FAR THE COVER MAY RUN. Every cover in the corpus closes on page 1.
# Two pages is one more than that, and the walk ends at the title either way.
_MAX_PAGES = 2
# THE BRACKETED KEYWORD BLOCK the court sets under the title of a bid
# protest runs to a handful of rows; eight is the bound.
_BRACKET_MAX_ROWS = 8

# THE COURT NAMES ITSELF. A closed set — its own name and the name of the
# office within it, never a test on anything it says about a case.
_BANNER = (
    "in the united states court of federal claims",
    "united states court of federal claims",
    "office of special masters",
)
# THE DOCKET, in the forms the two chambers write it: 'No. 23-0033V' (the
# Vaccine Act suffix), 'No. 24-364', 'No. 26-303C', 'Nos. 21-1 & 21-2'.
_DOCKET = re.compile(r"^\(?\s*(Nos?\.\s*\d.*?)\)?\s*$")
# THE DAY THE PAPER ISSUED, and the day it was published in redacted form.
_DATE = re.compile(
    r"^\(?\s*(Filed|Dated|Issued|Entered|Re-?issued|Re-?filed|"
    r"Filed under seal|Originally filed|Reissued for publication)"
    r"\s*:?\s*(.+?)\s*\)?\s*$", re.I)
_REISSUE = re.compile(r"^Re-?(issued|filed)", re.I)
# THE DECIDING OFFICER, as the caption's right-hand column announces him.
# A closed bench vocabulary; the NAME is never read by wording.
_OFFICER = re.compile(
    r"^((?:Chief\s+)?Special\s+Master|Chief\s+Judge|Senior\s+Judge|Judge)"
    r"\s+(\S.*?)\s*$")
# PARTY STATUS is a closed role vocabulary. uscfc's trial-court statuses,
# plus the ones a bid protest adds.
_STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
    "petitioners", "respondent", "respondents", "intervenor", "intervenors",
    "defendant-intervenor", "defendant-intervenors", "movant", "movants",
    "deceased", "counterclaimant", "counterclaim", "third-party",
    "consolidated", "amicus", "amici", "appellant", "appellee",
)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") in _BANNER


# A FOOTNOTE MARK IS A SUPERSCRIPT, and the page says which glyph is one.
# dutch_ridge sets 'Re-issued: May 20, 20261' and the trailing '1' is the
# note explaining the protective order — but stripping trailing DIGITS
# instead takes the last digit of a docket ('No. 24-364' -> 'No. 24-') and
# three digits of a year. The mark comes off the MARKUP, never the text.
_MARK_TAIL = re.compile(r"<footnotemark>[^<]*</footnotemark>\s*$")
_TAGS = re.compile(r"<[^>]+>")


def _unmarked(row: list) -> str:
    """The row's text with a trailing footnote mark removed."""
    return _norm(_TAGS.sub("", _MARK_TAIL.sub("", _markup(row))))


def _join(texts, vocab: set | None = None) -> str:
    """Join the rows of one band the way the page reads it."""
    out = ""
    for piece in texts:
        piece = _norm(piece)
        if not piece:
            continue
        if not out:
            out = piece
            continue
        if out.endswith(("-", "–", "—")):
            if vocab:
                word = []
                for ch in reversed(out[:-1]):
                    if ch.isalpha() or ch in "’'":
                        word.append(ch)
                    else:
                        break
                head = piece.split()[0].strip("“”\"'’‘()[]{}.,;:!?")
                if word and ("".join(reversed(word)) + head).lower() in vocab:
                    out = out[:-1] + piece
                    continue
            out += piece
        else:
            out += " " + piece
    return out


def _sides(rows: list):
    """The party named on each side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    statuses, the joiners and the pivot are apparatus. A party that WRAPS is
    joined back together (the court sets an estate's administrator over four
    rows), and a party's own STATUS closes it: without that, a bid protest's
    defendant read as 'THE UNITED STATES, ASRC FEDERAL ADMINISTRATIVE
    SERVICES, LLC' — the government and the intervenor as one party."""
    sides: list = [[[]], [[]]]
    which = 0
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        first = flat.split()[0].rstrip(".").lower()
        if first in ("v", "vs") and len(flat) <= 6:
            which = 1
            continue
        bare = flat.rstrip(",. ").lower()
        words = [w.strip(",.;/ ") for w in bare.split()]
        is_status = bool(words) and all(
            w in _STATUS_WORDS or w in ("and", "the", "of", "") for w in words)
        if is_status or bare in ("and", "et al", "and,"):
            # the entry this status labels is complete
            if sides[which][-1]:
                sides[which].append([])
            continue
        sides[which][-1].append(flat)

    def _name(entries: list) -> str:
        for entry in entries:
            if entry:
                return _join(entry).rstrip(",")
        return ""
    return _name(sides[0]), _name(sides[1])


# --------------------------------------------------------------------------
# a VISUAL ROW is what the page printed on one line
# --------------------------------------------------------------------------

def _visual_rows(lines: list) -> list:
    out: list = []
    for line in sorted(lines, key=lambda l: (l.page, l.top, l.x0)):
        if out and out[-1][0].page == line.page \
                and abs(out[-1][0].top - line.top) <= _ROW_BAND:
            out[-1].append(line)
        else:
            out.append([line])
    for row in out:
        row.sort(key=lambda l: l.x0)
    return out


def _plain(row: list) -> str:
    text = ""
    for line in row:
        piece = _norm(line.plain)
        if not piece:
            continue
        text = (text + "  " + piece) if text else piece
    return text


def _markup(row: list) -> str:
    text = ""
    for line in row:
        piece = line_markup(line)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    return text


# --------------------------------------------------------------------------
# the drawings — the dispatch
# --------------------------------------------------------------------------

def _underlines(pm) -> set:
    """The rules on ``pm`` that UNDERLINE the row above them, keyed by the
    id of the rule and carrying the row they belong to."""
    out: dict = {}
    for rule in pm.h_rules:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            drop = rule.top - line.top
            if not (0 < drop <= _UNDERLINE_DROP):
                continue
            if abs(line.x0 - rule.x0) <= _UNDERLINE_TOL \
                    and rule.x1 <= line.x1 + _UNDERLINE_TOL \
                    and rule.width >= 0.7 * max(line.x1 - line.x0, 1.0):
                out[id(rule)] = line
                break
    return out


def _drawn_box(pm):
    """The caption box drawn on ``pm``: a VERTICAL with a horizontal across
    its head and another across its foot, both stopping AT the vertical."""
    skip = set(_underlines(pm))
    lo, hi = pm.width * _BOX_VRULE_BAND[0], pm.width * _BOX_VRULE_BAND[1]
    rules = [r for r in pm.h_rules
             if r.width >= _BOX_RULE_MIN_W and id(r) not in skip]
    for v in pm.v_rules:
        if v.height < _BOX_VRULE_MIN_H or not lo < v.x < hi:
            continue
        heads = [r for r in rules if abs(r.top - v.top) <= _BOX_JOIN
                 and r.x1 >= v.x - _BOX_JOIN]
        feet = [r for r in rules if abs(r.top - v.bottom) <= _BOX_JOIN
                and r.x1 >= v.x - _BOX_JOIN]
        if heads and feet:
            return {"x": float(v.x), "top": min(r.top for r in heads),
                    "bottom": max(r.top for r in feet), "rail": None}
    return None


def _fence_glyph(text: str) -> str | None:
    """A TYPED fence row is a row of one glyph. The rail's own ')' may ride
    on the closing rule ('______________ )') and is not part of the count."""
    flat = "".join(text.split()).replace(")", "")
    if len(flat) < _FENCE_MIN_GLYPHS:
        return None
    if set(flat) == {"*"}:
        return "*"
    if set(flat) == {"_"}:
        return "_"
    return None


def _typed_fences(pm) -> list:
    return [l for l in pm.lines if _fence_glyph(l.plain)]


def _rail_x(lines: list) -> float | None:
    """The x of a stacked ')' rail, or None. A rail is a COLUMN: at least
    four rows whose whole content is the glyph, standing at one x."""
    xs = sorted(l.x0 for l in lines if _norm(l.plain) == ")")
    if len(xs) < _RAIL_MIN_ROWS:
        return None
    mid = xs[len(xs) // 2]
    if xs[-1] - xs[0] > _RAIL_COLUMN_TOL:
        return None
    return mid


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------

@decider("headmatter.read", court="uscfc")
def read_headmatter_uscfc(model, geom, **_):
    """Read uscfc's cover, or NOTHING.

    NOTHING is returned for anything that is neither of the two papers
    above: core's shared walk places those rows unidentified, which is a
    smaller error than a confident misreading."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    vocab = learn_vocabulary(model)
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(USCFC.byline)
    page1 = model.pages[0]
    pages = {pm.number: pm for pm in model.pages}

    lines: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            lines.append(line)
    if not lines:
        return NOTHING
    by_page: dict = {}
    for line in sorted(lines, key=lambda l: (l.page, l.top, l.x0)):
        by_page.setdefault(line.page, []).append(line)
    p1_lines = by_page.get(page1.number, [])

    # THE COURT NAMES ITSELF FIRST. Without that row this is not uscfc's
    # cover and the reader has nothing to say.
    if not any(_is_banner(_plain(r)) for r in _visual_rows(p1_lines)[:5]):
        return NOTHING

    # ---- the dispatch: which drawing states the caption's zones ---------
    box = _drawn_box(page1)
    rail = None
    if box is not None:
        style = STYLE_OSM_BOX
    else:
        fences = _typed_fences(page1)
        if len(fences) < 2:
            return NOTHING
        style = STYLE_TYPED_FENCE
        top = min(l.top for l in fences)
        bottom = max(l.top for l in fences)
        rail = _rail_x([l for l in p1_lines if top < l.top < bottom])
        box = {"x": rail, "top": top, "bottom": bottom,
               "rail": ")" if rail is not None else None}
        fence_ids = {l.id for l in fences}

    # THE PAPER'S OWN NAME CLOSES THE COVER: a row on the page axis with a
    # drawn rule under it whose ends coincide with the row itself.
    title_top = None
    for rule_id, line in _underlines(page1).items():
        if line.top <= box["bottom"]:
            continue
        if abs((line.x0 + line.x1) / 2 - page1.width / 2) > _TITLE_AXIS_TOL:
            continue
        if title_top is None or line.top < title_top:
            title_top = line.top
    if title_top is None:
        return NOTHING

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    banner_rows: list = []
    caption_rows: list = []
    counsel_rows: list = []
    bracket_rows: list = []
    officers: list = []
    dockets: list = []
    dates: list = []
    reissues: list = []
    stamps: list = []

    def emit(row: list, role: str, rel_from: float = 0.0):
        first = row[0]
        pm = pages[first.page]
        align = line_alignment(first, pm.width, geom,
                               banner_center_min_size=body_size + 1.0)
        rel = 0.0
        if rel_from and align == "L" and first.x0 > rel_from + 12:
            rel = min(first.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=_markup(row), prov=m.Prov(first.page,
                                           tuple(l.id for l in row)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(l.all_bold for l in row), rel=rel, role=role))
        consumed.update(l.id for l in row)
        return items[-1]

    def _read_above(row: list):
        """A row the court set ABOVE its caption: the stamp on the paper,
        the court naming itself, the docket, the day it was filed."""
        text = _unmarked(row)
        if _is_banner(text):
            banner_rows.append(text)
            emit(row, "court")
            return
        dm = _DOCKET.match(text)
        if dm:
            dockets.append(_norm(dm.group(1)))
            emit(row, "docket")
            return
        dt = _DATE.match(text)
        if dt:
            if _REISSUE.match(text):
                reissues.append(text)
            else:
                dates.append(_norm(dt.group(2)))
            emit(row, "date")
            return
        stamps.append(text)
        emit(row, "case-info")

    def _cell(cells: list, role: str, pm):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align(line_alignment(
                first, pm.width, geom,
                banner_center_min_size=body_size + 1.0)),
            x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    def _strip_rail(line, glyph: str, mid: float):
        """Drop the rail's own glyphs out of a cell. The rail is a COLUMN: a
        glyph belongs to it when it stands at the column's x — a ')' anywhere
        else on the row is the court's own punctuation."""
        keep = [c for c in line.chars
                if not ((c.get("text") or "").strip() == glyph
                        and abs((c["x0"] + c.get("x1", c["x0"])) / 2 - mid)
                        <= _RAIL_COLUMN_TOL)
                and (c.get("text") or "") != ""]
        if not any((c.get("text") or "").strip() for c in keep):
            return None
        if len(keep) == len(line.chars):
            return line
        from dataclasses import replace as _replace
        return _replace(line, chars=keep,
                        x0=min(c["x0"] for c in keep),
                        x1=max(c.get("x1", c["x0"]) for c in keep))

    # ---- the zones -------------------------------------------------------
    # ABOVE THE CAPTION: the masthead band.
    for row in _visual_rows([l for l in p1_lines if l.top < box["top"]]):
        _read_above(row)

    # THE CAPTION. Column membership is decided by which side of the drawing
    # a cell sits on — never by what the cell says.
    band = [l for l in p1_lines if box["top"] <= l.top <= box["bottom"]]
    if style is STYLE_TYPED_FENCE:
        # A CLAIM MUST BE TOTAL: the typed fence is the page's own drawing
        # and is RE-EMITTED as a rule, not merely stepped over. Left
        # unplaced it came back as residual furniture on dutch_ridge.
        for line in [l for l in band if l.id in fence_ids]:
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                span="left", typed=True))
            consumed.add(line.id)
        band = [l for l in band if l.id not in fence_ids]
    mid = box["x"] if box["x"] is not None else page1.width
    glyph = box["rail"]
    cells_l: list = []
    cells_r: list = []
    left_plain: list = []
    right_plain: list = []
    for row in _visual_rows(band):
        if glyph and all(_norm(l.plain).strip(glyph) == "" for l in row):
            consumed.update(l.id for l in row)     # a bare rail row
            continue
        l_cells = [l for l in row if (l.x0 + l.x1) / 2 < mid]
        r_cells = [l for l in row if l not in l_cells]
        if glyph:
            l_cells = [c for c in (_strip_rail(l, glyph, mid)
                                   for l in l_cells) if c is not None]
            r_cells = [c for c in (_strip_rail(l, glyph, mid)
                                   for l in r_cells) if c is not None]
        if not l_cells and not r_cells:
            continue
        cells_l.append(l_cells)
        cells_r.append(r_cells)
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    # THE RIGHT COLUMN IS NOT MORE CAPTION. It carries the officer who
    # decided the case and the day the paper was filed, and each cell is
    # named for what it is.
    roles_r: list = []
    for k, cells in enumerate(cells_r):
        text = _unmarked(cells) if cells else right_plain[k]
        om = _OFFICER.match(text)
        dt = _DATE.match(text)
        if om:
            officers.append(text)
            roles_r.append("panel")
        elif dt:
            if _REISSUE.match(text):
                reissues.append(text)
            else:
                dates.append(_norm(dt.group(2)))
            roles_r.append("date")
        else:
            roles_r.append("caption")
    left = [_cell(c, "caption", page1) if c
            else m.HmLine(text="", prov=m.Prov(page1.number), role="caption")
            for c in cells_l]
    right = [_cell(c, roles_r[k], page1) if c
             else m.HmLine(text="", prov=m.Prov(page1.number),
                           role=roles_r[k])
             for k, c in enumerate(cells_r)]
    caption_rows.extend(t for t in left_plain if t)
    if not any(right_plain):
        right = []
    items.append(m.CaptionBlock(
        left=left, right=right, rail=glyph or "|", rail_rows=len(left),
        style_id="backwards-c" if not glyph else "glyph-rail",
        fp={"rail": glyph or "drawn", "mid_x": mid,
            "rail_band": (box["top"], box["bottom"])},
        prov=m.Prov(page1.number, tuple(sorted(l.id for l in band)))))
    consumed.update(l.id for l in band)

    # ---- the tail: the appearances, fenced above by the caption and below
    # by the paper's own name.
    tail = _visual_rows([l for l in p1_lines
                         if box["bottom"] < l.top < title_top])
    i = 0
    while i < len(tail):
        row = tail[i]
        text = _plain(row)
        parsed = parser.parse(text)
        if parsed is not None and text[:parsed.end].rstrip().endswith((":", ".")):
            break                       # a byline would end the reader
        if text.startswith("["):
            end = i
            while end < len(tail) and end - i < _BRACKET_MAX_ROWS:
                if _plain(tail[end]).rstrip().endswith("]"):
                    break
                end += 1
            for r2 in tail[i:end + 1]:
                bracket_rows.append(_plain(r2))
                emit(r2, "summary")
            i = end + 1
            continue
        dt = _DATE.match(_unmarked(row))
        if dt:
            if _REISSUE.match(text):
                reissues.append(_unmarked(row))
            else:
                dates.append(_norm(dt.group(2)))
            emit(row, "date")
            i += 1
            continue
        counsel_rows.append(text)
        emit(row, "counsel", rel_from=body_x0)
        i += 1

    # ---- what the block says ---------------------------------------------
    if banner_rows:
        crit["court"] = ", ".join(banner_rows)
    if stamps:
        # 'CORRECTED' — a stamp on the paper. It is the document's history,
        # not its name and not its status.
        crit["history"] = "; ".join(stamps + reissues)
    elif reissues:
        crit["history"] = "; ".join(reissues)
    if caption_rows:
        crit["caption"] = caption_rows
        first, second = _sides(caption_rows)
        if first and second:
            crit["parties"] = [first, second]
            crit["case_name"] = f"{first} v. {second}"
        elif first:
            crit["parties"] = [first]
            crit["case_name"] = first
    if dockets:
        crit["docket_number"] = dockets[0]
        others = [d for d in dockets[1:] if d != dockets[0]]
        if others:
            crit["other_dockets"] = others
    if officers:
        printed = "; ".join(dict.fromkeys(officers))
        crit["panel_line"] = printed
        crit["judges"] = printed
        names = []
        for text in officers:
            om = _OFFICER.match(text)
            if om and om.group(2) not in names:
                names.append(om.group(2))
        if names:
            crit["panel"] = names
    if dates:
        crit["decision_date"] = dates[0]
    if bracket_rows:
        crit["disposition"] = _join(bracket_rows, vocab).strip("[] ").strip()
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        # An appearance that WRAPS is one entry: the court sets a new one a
        # full paragraph below the last (OSM's two leadings) or opens it with
        # a hanging indent (the judge's stock), and the tail of every entry
        # says whom it is for.
        crit["attorneys"] = _join(counsel_rows, vocab)[:4000]

    # A CLAIM MUST BE TOTAL. The reader steps over the court's stationery
    # rather than claiming it: core's furniture pass already recorded the
    # folio, and a second record of the same row would report it twice.
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": [], "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
