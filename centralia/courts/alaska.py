"""Supreme Court of the State of Alaska ('alaska').

Everything unique to alaska lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACTS. Alaska prints its front matter on stationery whose zones
are held by a caption DIVIDER, and the divider says which of the court's
two papers this is. Nothing is decided by what a row says:

    paren-rail opinion (48 of 50) — the caption's divider is a stacked
    ')' at x≈300-315, and the caption is CLOSED by a drawn rule of half
    the body measure (229-243pt, left-anchored at x0≈71). The same rule
    recurs INSIDE the band on a consolidated record, once per case:

        Notice:  This opinion is subject to correction before …   11pt
        THE SUPREME COURT OF THE STATE OF ALASKA         the banner, 13.6
        ALASKA DEMOCRATIC PARTY and  )                   the caption:
        ANITA THORNE,                )  Supreme Court No. S-19231
                     Appellants,     )  Superior Court No. 3AN-24-08665 CI
        v.                           )  O P I N I O N
        CAROL BEECHER, DIRECTOR,     )  No. 7776 – July 25, 2025
                     Appellees.      )
        ─────────────────────        the caption's closing fence, 236.9pt
              Appeal from the Superior Court of the State of …  the origin
              Appearances:  Thomas P. Amodio, Reeves Amodio …   the bar
              Before:  Maassen, Chief Justice, and Carney, …    the roster
              PATE, Justice.                                    the byline

    ruled caption box (2 of 50) — the court's ORDER paper draws the
    caption instead: THREE vertical rules (two borders and the divider
    between them) closed top and bottom by a full-measure horizontal.
    There is no byline; the order runs straight on under the roster.

        In the Supreme Court of the State of Alaska        20pt italic
        ────────────────────────────────────────────      the box head
        │ In the Disciplinary Matter Involving:  │ Supreme Court No. …  │
        │ Joshua M. Kindred,                     │ Order                │
        │            Respondent.                 │ Order No. 127 – …    │
        ────────────────────────────────────────────      the box foot
        ABA File No. 2024D147
        Before:  Carney, Chief Justice, and Borghesan and Pate, Justices.
        Bar Counsel for the Alaska Bar Association submitted its …

The dispatch is the DIVIDER — the ')' stack or the drawn box — never the
word OPINION or ORDER the court sets beside it. A record that draws
neither is not one of these contracts and gets NOTHING: core's shared
walk places those rows unidentified, which is a smaller error than a
confident misreading.

The reader claims HEADMATTER ONLY. It stops at the first byline, and on
the order paper at the first row below the roster that opens no landmark
of the court's own — everything below is core's.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder, is_folio_text
from . import PROFILES

# alaska's profile is registered in the shared table; this file owns its
# reader only. Look it up rather than re-declaring it, so the byline
# grammar can never drift from the one assembly uses.
ALASKA: CourtProfile = PROFILES["alaska"]

STYLE_PAREN_RAIL = "paren-rail opinion"
STYLE_RULED_BOX = "ruled caption box"

# ---- alaska's declared facts (measured over the corpus, not tuned) -------
# THE PAREN RAIL. ')' occurs in ordinary prose, so a divider has to be a
# COLUMN of them: six, the floor ca6's paren slip established. Measured
# here the shortest rail runs 8 glyphs and the tallest 32.
_PAREN_FLOOR = 6
# …but a caption that WRAPS THE PAGE carries as few as five glyphs onto
# the next one. There the column is already proved, so two is enough.
_PAREN_CONT_FLOOR = 2
# A glyph belongs to the rail when it stands in the rail's own column.
# The rail's x0 varies by 0.1pt within a document and the nearest other
# ink on those rows is 8pt away, so 6pt reaches the rail and nothing else
# — in particular not the ')' that closes '(Consolidated)' 90pt to its
# right.
_RAIL_WINDOW = 6.0
# THE CAPTION FENCE: a drawn rule of HALF the body measure, anchored on
# the left margin — 229.0 to 243.7pt over the corpus, always at x0 71-72
# on a 612pt page. It closes the caption, and on a consolidated record it
# also separates the cases inside it. The court's other rules are a
# different measure entirely: the 'O P I N I O N' underline is 75.7pt and
# sits at x0>319, the footnote separator is 144pt, and the order box is
# drawn at the full 458-468pt measure.
_FENCE_W = (200.0, 275.0)
_FENCE_X0_MAX = 110.0
# THE ORDER BOX: three vertical rules — two borders and the divider —
# spanning the same band, at least 60pt tall (measured 107.8 and 154.4).
_BOX_RULE_MIN_H = 60.0
# …closed by a horizontal at the FULL body measure.
_BOX_HEAD_W = 400.0
# HOW FAR A BLOCK WRAPS. The origin / appearances / roster blocks are set
# at 15.5pt leading and separated from each other by 31pt. 24pt lies
# between the two everywhere in the corpus, so it is what ends a block —
# and it is what stops the roster running into an unsigned order's first
# paragraph, which opens at the same rail with no byline to end it.
_BLOCK_LEAD_MAX = 24.0
# A block may WRAP THE PAGE: its continuation opens the next page's top.
_TOP_BAND = 0.20
# How far the front matter may run. Three pages is more than any alaska
# record needs (the longest consolidated caption uses two).
_MAX_PAGES = 3
# THE FOOT alaska prints on every page: a dressed folio and the slip
# opinion number on one row ('-2-    7776'). Below 90% of the page.
_FOOT_BAND = 0.90

# THE ORIGIN, as alaska names the court it is reviewing. A closed set of
# openers the court sets at the head of that block — 'Appeal from …',
# 'Appeals in File Nos. S-18318/18357 from …', 'Petition for Hearing
# from …'.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "appeal in file", "appeals in file",
    "cross-appeal from", "cross-appeals from",
    "petition for hearing from", "petitions for hearing from",
    "petition for review from", "petition for review of",
    "on petition for hearing from", "on rehearing from",
    "original application", "certified question from",
)
_COUNSEL_LABEL = "appearances"
_PANEL_LABEL = "before"
# THE LOWER TRIBUNAL'S OWN NUMBER, and this court's.
# THE COURT'S OWN NUMBER. Everything else in this judicial system that
# states a number — the Superior Court, the Court of Appeals, the
# Workers' Compensation Appeals Commission — sits below this one, so the
# vocabulary that has to be closed is the SHORT one.
_DOCKET_PREFIXES = ("supreme court no", "supreme court file no")
# The bar's own file numbers, which a disciplinary order prints under the
# box instead of a lower-court docket.
_BAR_PREFIXES = ("aba file no", "aba member no", "bar file no")
# THE PAPER'S OWN NAME, set in the caption's right column.
_TITLE_WORDS = ("OPINION", "ORDER", "AMENDED OPINION", "CORRECTED OPINION",
                "SUBSTITUTE OPINION", "AMENDED ORDER", "JUDGMENT",
                "OPINION AND ORDER")
# THE SLIP NUMBER row: 'No. 7776 – July 25, 2025' / 'Order No. 126 – June
# 13, 2025'. The court numbers its published slips in one sequence and
# dates them on the same row.
_SLIP_OPENERS = ("no.", "order no.", "opinion no.")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Alaska hyphenates its compound roles ('Intervenor-Appellee')
# and breaks them across rows ('Intervenor-' / 'Appellee.').
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant",
    "applicants", "cross", "third", "party", "interest", "in", "of",
    "and", "the", "pro", "se",
)
# BENCH WORDS — a closed vocabulary, so a roster never yields a justice
# called 'and' or one called 'Justices'.
_BENCH_WORDS = ("justice", "justices", "judge", "judges", "chief",
                "senior", "pro", "tem", "retired", "participating")
_SUFFIXES = ("jr", "sr", "ii", "iii", "iv")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _squeeze(text: str) -> str:
    """'O P I N I O N' -> 'OPINION'. Alaska letter-spaces the label on the
    opinion paper and sets it plain on the order paper; it is the same
    label."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _is_banner(text: str) -> bool:
    """The court naming itself. Alaska sets it two ways — 13.6pt caps on
    the opinion paper, 20pt italic title case on the disciplinary order —
    so the test is on the words, not the case. It is only ever applied
    ABOVE the caption band, which is what keeps 'Appeal from the Superior
    Court of the State of Alaska' out of it."""
    low = _norm(text).lower()
    return ("court" in low and "alaska" in low
            and "supreme" in low and len(low.split()) >= 6)


def _find_date(text: str) -> str | None:
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    return mm.group(1) if mm.group(1).split()[0].strip(".").lower() \
        in _MONTHS else None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _starts(text: str, prefixes) -> bool:
    return _norm(text).lower().lstrip(") ").startswith(prefixes)


def _is_foot(pm, line, row_lines) -> bool:
    """alaska's page foot: a dressed folio and the slip number on ONE row
    ('-2-    7776'), at the very bottom of the page. BOTH pieces are
    numerals, which is why core — whose folio test wants the numeral alone
    on its band, so a detached footnote label stays with its note — sees
    neither."""
    if line.top / (pm.height or 792.0) < _FOOT_BAND:
        return False
    return all(is_folio_text(_norm(l.plain)) for l in row_lines)


# --------------------------------------------------------------------------
# the dividers — alaska's two caption contracts, and the dispatch
# --------------------------------------------------------------------------

def _rail(pm, at_x: float | None = None) -> dict | None:
    """The ')' divider on ``pm``: {'x','top','bottom'}, or None. A rail is
    a COLUMN — glyphs stacked at one x, not a count of glyphs anywhere on
    the page.

    ``at_x`` asks for the CONTINUATION of a rail an earlier page already
    established. A caption that wraps the page carries as few as five
    glyphs onto the next one, which is under the floor a rail has to clear
    to be found from scratch — but the column is not in doubt once the
    page before it has proved it (orutsararmiut's second caption lost its
    origin, appearances and roster to that floor)."""
    from collections import Counter

    chars = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == ")"]
    if at_x is not None:
        stack = [c for c in chars if abs(c["x0"] - at_x) <= 3]
        if len(stack) < _PAREN_CONT_FLOOR:
            return None
        return {"x": float(at_x), "top": min(c["top"] for c in stack),
                "bottom": max(c["bottom"] for c in stack)}
    if len(chars) < _PAREN_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    stack = [c for c in chars if abs(c["x0"] - x) <= 3]
    if len(stack) < _PAREN_FLOOR:
        return None
    return {"x": float(x), "top": min(c["top"] for c in stack),
            "bottom": max(c["bottom"] for c in stack)}


def _box(pm) -> dict | None:
    """The ORDER paper's drawn caption box: {'x','top','bottom','head',
    'foot'}, or None.

    A divider has to DIVIDE — the court also rules the box's own left and
    right borders at the same height, and on height alone the left border
    qualifies and every caption row falls to its right. The divider is the
    vertical that has caption text on BOTH sides of it."""
    tall = [r for r in pm.v_rules if r.height >= _BOX_RULE_MIN_H]
    if len(tall) < 3:
        return None

    def divides(x, top, bottom):
        left = right = False
        for line in pm.lines:
            if not (top - 2 <= line.top <= bottom + 2):
                continue
            for c in line.chars:
                if not (c.get("text") or "").strip():
                    continue
                if c["x1"] <= x - 2:
                    left = True
                elif c["x0"] >= x + 2:
                    right = True
        return left and right

    mid = pm.width / 2.0
    for r in sorted(tall, key=lambda r: abs(r.x - mid)):
        if divides(r.x, r.top, r.bottom):
            heads = sorted(
                (h.top for h in pm.h_rules if h.width >= _BOX_HEAD_W
                 and abs(h.top - r.top) <= 12),
                key=lambda t: abs(t - r.top))
            feet = sorted(
                (h.top for h in pm.h_rules if h.width >= _BOX_HEAD_W
                 and abs(h.top - r.bottom) <= 12),
                key=lambda t: abs(t - r.bottom))
            if not heads or not feet:
                return None
            return {"x": float(r.x), "top": r.top, "bottom": r.bottom,
                    "head": heads[0], "foot": feet[0]}
    return None


def _fences(pm) -> list:
    """Tops of the caption fence — the half-measure rule alaska closes its
    caption with, and repeats between consolidated cases."""
    out = [r.top for r in pm.h_rules
           if _FENCE_W[0] <= r.width <= _FENCE_W[1] and r.x0 <= _FENCE_X0_MAX]
    return sorted(out)


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.

    Split GLYPH BY GLYPH. Whether pdfio already broke a caption row at its
    column gap is an accident of how wide the gap happened to be: the same
    corpus sets 'STATE OF ALASKA, DEPARTMENT )' as one run and ') Supreme
    Court Nos. S-19535/19536' as another, and a whole-line test puts the
    rail in one column or the other by luck."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _shed_rail(line, rail_x: float, glyph: str | None):
    """``line`` with the divider's own glyphs removed, or None when the
    line WAS the divider. The glyph is identified by its COLUMN, never by
    its character — the ')' that closes '(Consolidated)' is 90pt right of
    the rail and stays."""
    if glyph is None:
        return line
    lo, hi = rail_x - _RAIL_WINDOW, rail_x + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == glyph and lo <= c["x0"] <= hi)]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    if len(kept) == len(line.chars):
        return line
    return _replace(line, chars=kept)


def _unfence(line, fence_tops: list):
    """``line`` with any underline the CAPTION FENCE put on it cleared.

    A drawn rule whose ends coincide with the row above is an underline; a
    236pt rule anchored on the left margin under a 55pt row set at x=180
    is not. pdfio tags by vertical proximity alone, so the caption's
    closing fence arrives as an underline on whatever row it happens to
    follow ('<u>Appellee.</u>'). The fence is structure — it renders as
    the rule the page drew, once."""
    if not fence_tops or not line.chars:
        return line
    base = max(c["bottom"] for c in line.chars)
    if not any(-2.5 <= (t - base) <= 5.0 for t in fence_tops):
        return line
    if not any(c.get("_underline") for c in line.chars):
        return line
    kept = []
    for c in line.chars:
        if c.get("_underline"):
            c = dict(c)
            c.pop("_underline", None)
        kept.append(c)
    return _replace(line, chars=kept)


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _caption_block(rows: list, rail_x: float, glyph: str | None, pm,
                   style_id: str | None):
    """One caption case as a CaptionBlock, plus each column's plain text.

    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned."""
    def cell(cells: list, role: str):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align("L"), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    left, right, left_plain, right_plain = [], [], [], []
    for row in rows:
        l_cells, r_cells = [], []
        for line in row:
            shed = _shed_rail(line, rail_x, glyph)
            if shed is None:
                continue
            for side, bucket in ((_side(shed, rail_x, "L"), l_cells),
                                 (_side(shed, rail_x, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        left.append(cell(l_cells, "caption") if l_cells
                    else m.HmLine(text="", prov=m.Prov(pm.number),
                                  role="caption"))
        right.append(cell(r_cells, "caption") if r_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number),
                                   role="caption"))
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: the rows
    # that held nothing but a rail glyph are empty on both sides, and left
    # standing they render as phantom blank rows at the block's foot.
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop(); right.pop(); left_plain.pop(); right_plain.pop()
    if not left:
        return None, [], []
    ids = tuple(sorted(l.id for row in rows for l in row))
    block = m.CaptionBlock(
        left=left, right=right, rail=glyph or "|", rail_rows=len(left),
        style_id=style_id,
        fp={"rail": glyph or "drawn", "mid_x": rail_x},
        prov=m.Prov(pm.number, ids))
    return block, left_plain, right_plain


def _sides(rows: list):
    """The party names either side of the 'v.' pivot, built from the party
    NAMES — never by joining the caption wholesale, because the status
    labels and the pivot are apparatus, not names."""
    left, right, side, seen = [], [], None, False
    left_l: list = []
    side = left_l
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        head = flat.split()[0].rstrip(".").lower()
        if head in ("v", "vs") and len(flat) <= 6:
            side = right
            seen = True
            continue
        if set(flat) <= set("_-–— ") and len(flat) >= 3:
            continue          # the court's own typed separator, not a name
        bare = flat.rstrip(",.; ").lower()
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        if head in ("v.", "vs."):
            side = right
            seen = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    left = left_l
    # THE COMMA is the caption's own apparatus, leading to the status row
    # under it; the FULL STOP is not — it ends the abbreviation a party is
    # incorporated under ('DONLIN GOLD, LLC.').
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _panel_names(text: str) -> list:
    """The justices named in a 'Before …' roster. Split on the court's own
    punctuation and keep what is not a BENCH word; a bracketed recusal
    ('[Oravec, Justice, not participating.]') names a justice too, and is
    read the same way."""
    body = _norm(text)
    # A BRACKETED CLAUSE IS A RECUSAL, and a justice who did not sit is
    # not on the panel. It stays in `panel_line` and `judges`, which are
    # the roster AS PRINTED; `panel` is who heard the case.
    at = body.find("[")
    if at >= 0:
        body = body[:at].rstrip()
    low = body.lower()
    if low.startswith(_PANEL_LABEL):
        body = body[len(_PANEL_LABEL):].lstrip(": ")
    names: list = []
    for chunk in body.replace(";", ",").replace(" and ", ", ").split(","):
        piece = chunk.strip().strip(".* ").strip()
        if not piece or not any(c.isalpha() for c in piece):
            continue
        if all(w.lower().strip(".") in _BENCH_WORDS for w in piece.split()):
            continue
        if piece.lower().strip(".") in _SUFFIXES and names:
            names[-1] = f"{names[-1]}, {piece}"
            continue
        if piece not in names:
            names.append(piece)
    return names


def _docket_tail(text: str) -> bool:
    """Does ``text`` CONTINUE the docket cell above it?

    A docket wrap carries no prose: a parenthesized qualifier the court
    sets under the numbers it applies to ('(Consolidated)'), or more of
    the numbers themselves ('and 3AN-21-04505 CI (Consolidated)',
    '00010 CN (Consolidated)' where the pair broke mid-number). Every
    word is a number or a case-type code; only the court's own
    conjunction joins them."""
    flat = _norm(text)
    core = re.sub(r"\([^)]*\)", " ", flat).strip()
    if not core:
        return True
    if not any(c.isdigit() for c in core):
        return False
    return all(w.strip(".,/") == w.strip(".,/").upper() or w.lower() == "and"
               for w in core.split())


def _trial_judge(text: str) -> str | None:
    """'…Third Judicial District, Anchorage, Ian Wheeles, Judge.' — who
    tried it, as the origin statement names them. The name is the clause
    that ENDS on a bench word, and a consolidated record states one per
    case ('…Dani Crosby, Judge.  Appeals in File Nos. S-18420/18570 from
    …Thomas A. Matthews, Judge.')."""
    found: list = []
    for mm in re.finditer(
            r",\s*([A-Z][^,]{1,60}?)\s*,\s*"
            r"((?:Senior\s+|Chief\s+|Pro\s+Tem\s+|Superior\s+Court\s+)?"
            r"Judges?)\s*\.", _norm(text)):
        name = f"{_norm(mm.group(1))}, {_norm(mm.group(2))}"
        if name not in found:
            found.append(name)
    return "; ".join(found) if found else None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="alaska")
def read_headmatter_alaska(model, geom, **_):
    """Read alaska's caption-divider headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _rail(page1)
    box = None
    if rail is not None:
        style, glyph = STYLE_PAREN_RAIL, ")"
    else:
        box = _box(page1)
        if box is None:
            return NOTHING          # no caption divider: not alaska's
        style, glyph = STYLE_RULED_BOX, None

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.6
    parser = BylineParser(ALASKA.byline)
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS the reader may see, and the FURNITURE it inherits by
    # claiming the region: alaska's foot row, which core reads as neither
    # folio nor running foot because both of its pieces are numerals.
    rows: list = []
    foot_lines: list = []
    for pm in model.pages[:_MAX_PAGES]:
        by_row: dict = {}
        for line in pm.lines:
            if line.plain.strip():
                by_row.setdefault(line.row if line.row is not None
                                  else ("t", round(line.top)), []).append(line)
        for line in pm.lines:
            if not line.plain.strip():
                continue
            key = line.row if line.row is not None else ("t", round(line.top))
            if _is_foot(pm, line, by_row[key]) or finder.kind(pm, line):
                foot_lines.append(line)
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BANDS. The caption occupies the divider's own vertical span,
    # closed by the fence the court draws under it — and a consolidated
    # caption too long for one page runs onto the next, where the court
    # sets the rail again and fences it again.
    bands: dict = {}
    fences: dict = {}
    for pm in model.pages[:_MAX_PAGES]:
        if box is not None:
            bands[1] = (box["head"], box["foot"])
            # The box's own borders underline whatever row they happen to
            # follow, exactly as the paren paper's closing fence does.
            fences[1] = [box["head"], box["foot"]]
            break
        if pm.number > 1:
            # A CAPTION CONTINUES ONLY WHERE IT RAN OUT OF PAGE. Anything
            # printed under the previous page's fence closed the caption
            # there, and a ')' on the next page is then some other page's
            # punctuation.
            prev = bands.get(pm.number - 1)
            if prev is None or any(l.page == pm.number - 1 and l.top > prev[1]
                                   for l in rows):
                break
            r = _rail(pm, at_x=rail["x"])
        else:
            r = rail
        if r is None:
            break
        fs = _fences(pm)
        close = [t for t in fs if t >= r["bottom"] - 2]
        bottom = close[0] if close else r["bottom"] + 6.0
        bands[pm.number] = (r["top"] - 6.0, bottom)
        fences[pm.number] = [t for t in fs if r["top"] < t < bottom]
        if close:
            fences[pm.number].append(bottom)
        else:
            break

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    notice_lines: list = []
    banner_rows: list = []
    caption_rows: list = []
    right_rows: list = []
    origin_rows: list = []
    counsel_rows: list = []
    panel_rows: list = []
    parties: list = []
    case_name: str | None = None

    def emit(row, role: str, rel_from: float | None = None):
        """One HEADMATTER ROW, from the one or more line objects the page
        set on that baseline. pdfio splits a row at its column gaps, and
        alaska sets the label of a block in one column and its first entry
        in the next ('Before:' at 144, the roster at 216; 'Appearances:'
        at 144, counsel at 229.5) — emitted separately those render as a
        label alone on a row and its value on the next."""
        parts = sorted(row if isinstance(row, list) else [row],
                       key=lambda l: l.x0)
        first = parts[0]
        pm = pages[first.page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        rel = 0.0
        align = "L"
        if role == "court":
            align = "C"
        elif rel_from is not None and first.x0 > rel_from + 12:
            rel = min(first.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), rel=rel, role=role))
        consumed.update(p.id for p in parts)

    # ---- the masthead: everything page 1 prints above the caption -------
    top_of_caption = bands.get(1, (10 ** 6, 0))[0]
    for line in rows:
        if line.page != 1 or line.top >= top_of_caption:
            continue
        text = _norm(line.plain)
        if _is_banner(text):
            banner_rows.append(text)
            emit(line, "court")
        else:
            # A NOTICE IS EVERYTHING ABOVE THE BANNER on this stationery —
            # the reporter-correction block the court heads every paper
            # with. Recorded, never silently swallowed.
            notice_lines.append(line)

    # ---- the caption ----------------------------------------------------
    for pno, (top, bottom) in sorted(bands.items()):
        pm = pages[pno]
        band_lines = [l for l in rows if l.page == pno and top <= l.top <= bottom]
        if not band_lines:
            continue
        fence_tops = fences.get(pno) or []
        visual: list = []
        for line in sorted(band_lines, key=lambda l: (l.top, l.x0)):
            line = _unfence(line, fence_tops)
            if visual and abs(visual[-1][0].top - line.top) <= 2:
                visual[-1].append(line)
            else:
                visual.append([line])
        # A consolidated caption is FENCED case by case; each fenced group
        # is one caption, and the rule between them renders where the page
        # draws it.
        groups: list = [[]]
        cuts = [] if box is not None else [t for t in fence_tops]
        for row in visual:
            while cuts and row[0].top > cuts[0]:
                cuts.pop(0)
                groups.append([])
            groups[-1].append(row)
        rail_x = box["x"] if box is not None else rail["x"]
        style_id = ("parenthetical-box" if glyph == ")" else "ruled-box")
        # A RULE RENDERS WHERE THE PAGE DRAWS IT, and the block is sorted
        # back into page order at the end — so a rule carries the
        # provenance of the row it follows. Given no line of its own it
        # sorts past every row in the document and lands at the foot.
        head_prov = m.Prov(pno, tuple(l.id for l in visual[0]))
        if box is not None:
            items.append(m.Rule(prov=head_prov, span="full"))
        for gi, group in enumerate(groups):
            if not group:
                continue
            block, lp, rp = _caption_block(group, rail_x, glyph, pm, style_id)
            if block is None:
                continue
            items.append(block)
            consumed.update(block.prov.line_ids)
            caption_rows.extend(t for t in lp if t)
            tops = [g[0].top for g in group][:len(block.right)]
            right_rows.extend(
                (r, t, y) for r, t, y in zip(block.right, rp, tops) if t)
            sides = _sides(lp)
            for s in sides:
                if s and s not in parties:
                    parties.append(s)
            if case_name is None and len(sides) == 2:
                case_name = f"{sides[0]} v. {sides[1]}"
            elif case_name is None and len(sides) == 1:
                case_name = sides[0]
        for t in (() if box is not None else fence_tops):
            above = [l for l in band_lines if l.top < t]
            prov = m.Prov(pno, tuple(l.id for l in above[-3:])) if above \
                else head_prov
            items.append(m.Rule(prov=prov, span="left"))
        if box is not None:
            tail_prov = m.Prov(pno, tuple(l.id for l in visual[-1]))
            items.append(m.Rule(prov=tail_prov, span="full"))

    if not caption_rows and not right_rows:
        return NOTHING

    # THE RIGHT COLUMN carries TWO numbers, and they are different things:
    # the number THIS court gave the case ('Supreme Court No. S-19231')
    # and the number of the court it is reviewing ('Superior Court No.
    # 3AN-24-08665 CI'). They sit in the same column, one directly under
    # the other, at the same size on the same rail — geometry cannot tell
    # them apart, and nothing on the page does except the TRIBUNAL each
    # row names. That is a closed vocabulary of court names within one
    # judicial system, not an open reading of wording: the Supreme Court
    # is this court, and the Superior Court / Court of Appeals / District
    # Court / Trial Court are the ones below it.
    prev_role = None
    docket_cells: list = []          # this court's own numbers, in order
    lower_cells: list = []           # the numbers of the courts below
    slip_cells: list = []            # 'No. 7776' — the published slip
    for row, flat, _y in right_rows:
        low = flat.lower()
        toks = [t.lower() for t in flat.split()]
        if _squeeze(flat) in _TITLE_WORDS:
            row.role = "title"
            crit.setdefault("title", _squeeze(flat))
        elif low.startswith(_SLIP_OPENERS):
            row.role = "date"
            head = flat.split("–")[0].split("—")[0].strip().rstrip(",")
            if head:
                slip_cells.append(head)
            date = _find_date(flat)
            if date:
                crit.setdefault("decision_date", date)
        elif low.startswith(_DOCKET_PREFIXES):
            row.role = "docket"
            docket_cells.append(flat)
        elif "no." in toks or "nos." in toks:
            # SOME OTHER TRIBUNAL'S NUMBER — the Superior Court's, the
            # Court of Appeals', the Workers' Compensation Appeals
            # Commission's. Every court in this system that is not the
            # Supreme Court sits below it.
            row.role = "lower-court"
            lower_cells.append(flat)
        elif prev_role in ("docket", "lower-court") and _docket_tail(flat):
            # A DOCKET CELL MAY WRAP. The court sets '(Consolidated)'
            # under the numbers it qualifies and breaks a long run of them
            # over two or three rows. The continuation belongs to the cell
            # above it, whichever of the two numbers that was.
            row.role = prev_role
            target = docket_cells if prev_role == "docket" else lower_cells
            if target:
                target[-1] = f"{target[-1]} {flat}"
        else:
            row.role = "case-info"
        prev_role = row.role
    # …and a cell may wrap UPWARD too: the tribunal's NAME can stand a row
    # above the number that identifies it ('Alaska Workers’
    # Compensation Appeals' / 'Commission No. 22-012'). A row the walk
    # could not name that sits one leading above a docket row, and states
    # no number of its own, is that docket cell's opening.
    for k in range(len(right_rows) - 2, -1, -1):
        row, flat, y = right_rows[k]
        nxt, ntext, ny = right_rows[k + 1]
        if (row.role == "case-info" and nxt.role in ("docket", "lower-court")
                and 0 < ny - y <= _BLOCK_LEAD_MAX
                and not any(c.isdigit() for c in flat)):
            row.role = nxt.role
            target = docket_cells if nxt.role == "docket" else lower_cells
            for n, cell in enumerate(target):
                if cell.startswith(ntext):
                    target[n] = f"{flat} {cell}"
                    break
    # THE LEAD CASE'S NUMBER IS THE DOCKET; a consolidated record's other
    # captions state their own, and those are companion appeals.
    if docket_cells:
        crit.setdefault("docket_number", docket_cells[0])
    for extra in slip_cells + docket_cells[1:]:
        crit.setdefault("other_dockets", []).append(extra)
    if lower_cells:
        crit["lower_court_docket"] = lower_cells

    # ---- everything below the caption, by landmark ----------------------
    last_band = max(bands) if bands else 1
    below = [l for l in rows
             if (l.page > last_band
                 or (l.page == last_band and l.top > bands[last_band][1]))]
    # Group the tail into VISUAL ROWS first: pdfio splits 'Appearances:'
    # from its first entry at the column gap, and half a label opens no
    # landmark.
    tail: list = []
    for line in below:
        if tail and tail[-1][0].page == line.page \
                and abs(tail[-1][0].top - line.top) <= 2:
            tail[-1].append(line)
        else:
            tail.append([line])

    state = None
    prev: list | None = None
    for row in tail:
        text = _norm(" ".join(l.plain for l in sorted(row, key=lambda l: l.x0)))
        low = text.lower()
        # A BYLINE ENDS THE READER, always and everywhere below the box.
        if parser.parse(text) is not None:
            break
        opener = None
        if _origin_opener(text):
            opener = "lower-court"
        elif low.startswith(_COUNSEL_LABEL):
            opener = "counsel"
        elif low.startswith(_PANEL_LABEL):
            opener = "panel"
        elif _starts(text, _BAR_PREFIXES):
            opener = "docket"
        elif low.startswith("[") and state == "panel":
            opener = "panel"          # a bracketed recusal is the roster's
        if opener is None:
            # A CONTINUATION is bounded: the court sets these blocks at
            # 15.5pt leading and separates them by 31, so a row further
            # down than that opens something this contract does not name —
            # and on the order paper, with no byline to stop at, that row
            # is the order's own first paragraph.
            if state is None or prev is None:
                break
            gap = row[0].top - prev[0].top
            same_page = row[0].page == prev[0].page
            wraps = (not same_page and row[0].page == prev[0].page + 1
                     and row[0].top
                     <= pages[row[0].page].height * _TOP_BAND)
            if not ((same_page and gap <= _BLOCK_LEAD_MAX) or wraps):
                break
            opener = state
        role = opener
        if role == "docket":
            crit.setdefault("other_dockets", []).append(text)
        elif role == "lower-court":
            origin_rows.append(text)
        elif role == "counsel":
            counsel_rows.append(text)
        elif role == "panel":
            panel_rows.append(text)
        emit(row, role, rel_from=body_x0)
        state = role if role != "docket" else state
        prev = row

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name
    if origin_rows:
        printed = _norm(" ".join(origin_rows))
        crit["lower_court"] = printed
        judge = _trial_judge(printed)
        if judge:
            crit["lower_court_judge"] = judge
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        text = _norm(" ".join(counsel_rows))
        if text.lower().startswith(_COUNSEL_LABEL):
            text = text.split(":", 1)[1].strip() if ":" in text[:14] else text
        crit["attorneys"] = text[:4000]
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith(_PANEL_LABEL):
            roster = roster[len(_PANEL_LABEL):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names

    # ---- a claim must be TOTAL ------------------------------------------
    if notice_lines:
        dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in notice_lines))[:1200],
            prov=m.Prov(1, tuple(l.id for l in notice_lines)),
            kind="notice"))
        consumed.update(l.id for l in notice_lines)
    # A READER INHERITS THE FURNITURE OF THE REGION IT CLAIMS — and no
    # more. alaska's foot sits at the page BOTTOM, so it belongs to this
    # block only on a page the reader owns end to end; on the page where
    # the claim stops at the roster, everything under that roster is the
    # writing's, its own foot included.
    _mine = {pno for pno in {l.page for l in rows}
             if all(l.id in consumed for l in rows if l.page == pno)}
    for line in foot_lines:
        if line.page not in _mine:
            continue
        dropped.append(m.Dropped(
            text=_norm(line.plain), prov=m.Prov(line.page, (line.id,)),
            kind="folio"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
