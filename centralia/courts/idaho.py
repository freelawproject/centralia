"""Supreme Court of the State of Idaho ('idaho').

Everything unique to idaho lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT. Idaho sets its front matter on one piece of stationery,
and the caption's own DIVIDER says which of two ways the court drew it.
Nothing is decided by what a row says:

    paren-rail opinion (49 of 50) — the caption's divider is a stacked
    ')' at x≈288-329, and the caption is CLOSED by a rule of HALF the
    body measure (239-257pt, left-anchored at x0≈71) that the court
    either DRAWS or TYPES as a run of underscores in the left column:

        IN THE SUPREME COURT OF THE STATE OF IDAHO       the banner, 12pt
        Docket No. 51548-2024                            the docket, centred
        STATE OF IDAHO,              )                   the caption:
                   Plaintiff-Appellant, )  Boise, September 2025 Term
        v.                           )  Opinion filed: February 4, 2026
        LEWIS VANALEN BOREK,         )  Melanie Gagnepain, Clerk
                   Defendant-Respondent. )
        _____________________________)   the caption's closing fence
             Appeal from the District Court of the Fourth …  the origin
             The decision of the district court is reversed. the outcome
             Raúl R. Labrador, Idaho Attorney General, …     the bar
             _____________________                          a typed rule
        ZAHN, Justice.                                       the byline

    ruled caption box (1 of 50) — the court draws the divider instead:
    two verticals 18pt apart spanning the caption band, closed by a
    full-measure horizontal at their foot. The rows are the same rows.

The dispatch is the DIVIDER — the ')' stack or the drawn verticals —
never the word OPINION or ORDER the court sets beside it. A record that
draws neither is not this contract and gets NOTHING: core's shared walk
places those rows unidentified, which is a smaller error than a
confident misreading.

WHERE IDAHO DIFFERS FROM ALASKA, which prints the same paper:

  * the DOCKET is set above the caption, centred under the banner, not
    in the caption's right column; the right column carries the sitting
    term, the filing date, the clerk, and the paper's own name;
  * the caption's closing fence is TYPED as often as it is drawn — a run
    of underscores in the left column, running to the rail;
  * there is no 'Appearances:' label and no 'Before:' roster: the origin,
    the court's OUTCOME statement and the appearances are three unlabelled
    blocks in fixed order, each set one indent step (36pt) inside the
    body rail at 13.8pt leading with 19.8 to 27.6pt between them;
  * so the reader's floor is GEOMETRIC — the front matter below the
    caption is everything at the indent, and the byline is the first row
    back at the body rail. That bound holds even where the byline's own
    grammar is not one core knows ('LORELLO, Judge' — the corpus carries
    Court of Appeals opinions — or the abbreviated 'ZAHN, J.');
  * a rail is a CONTIGUOUS column: ordinary prose sets ')' at the rail's
    own x further down the page, and taken as rail glyphs those stretch
    the caption to the page foot (estate_of_kalinski).

The reader claims HEADMATTER ONLY. It stops at the first byline, or at
the first row back at the body rail, whichever comes first — everything
below is core's.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder, is_folio_text
from . import PROFILES

# idaho's profile is registered in the shared table; this file owns its
# reader only. Look it up rather than re-declaring it, so the byline
# grammar can never drift from the one assembly uses.
IDAHO: CourtProfile = PROFILES["idaho"]

STYLE_PAREN_RAIL = "paren-rail opinion"
STYLE_RULED_BOX = "ruled caption box"

# ---- idaho's declared facts (measured over the corpus, not tuned) --------
# THE PAREN RAIL. ')' occurs in ordinary prose, so a divider has to be a
# COLUMN of them: six, the floor ca6's paren slip established. Measured
# here the shortest rail runs 9 glyphs and the tallest 41.
_PAREN_FLOOR = 6
# …but a caption that WRAPS THE PAGE carries fewer glyphs onto the next
# one. There the column is already proved, so two is enough.
_PAREN_CONT_FLOOR = 2
# A glyph belongs to the rail when it stands in the rail's own column.
# The rail's x0 varies by 0.1pt within a document and the nearest other
# ink on those rows is 8pt away, so 6pt reaches the rail and nothing
# else — in particular not the ')' that closes '(18) Years of Age'.
_RAIL_WINDOW = 6.0
# A RAIL IS A CONTIGUOUS COLUMN. Idaho stacks its glyphs at 13.8pt and
# may skip one row of the caption, so three leadings end the run — and
# a ')' that ordinary prose sets at the same x 200pt further down the
# page starts a run of its own instead of extending the caption.
_RAIL_RUN_GAP = 45.0
# THE CAPTION FENCE: a rule of HALF the body measure anchored on the
# left margin — 239.8 to 257.3pt at x0 71.3-76.3 on a 612pt page, drawn
# on 27 records and typed as underscores on the rest. It closes the
# caption, and on a consolidated record it also separates the cases
# inside it. The court's other rules are a different measure entirely:
# the title underline is 41-131pt and sits at x0>264, and the footnote
# separator is 144pt at x0 234.
_FENCE_W = (200.0, 275.0)
_FENCE_X0_MAX = 110.0
# THE ORDER PAPER'S BOX: verticals spanning the caption band, at least
# 60pt tall (measured 165.7).
_BOX_RULE_MIN_H = 60.0
# HOW FAR A BLOCK WRAPS. The origin / outcome / appearances blocks are
# set at 13.8pt leading; the gap BETWEEN two blocks is 19.8 to 27.6pt,
# and 27.6 only where the page has room — a long caption squeezes the
# ladder to 19.8 (medical_recovery_services, doyle). Measured over the
# corpus: 197 gaps at 13.8 and 166 at 19.8 or more, nothing between.
_BLOCK_LEAD_MAX = 16.0
# WHERE THE FRONT MATTER SITS: one indent step (36pt) inside the body
# rail, everywhere below the caption. Half a step reaches the block and
# never the byline, which is AT the rail.
_INDENT_MIN = 18.0
# A block may WRAP THE PAGE: its continuation opens the next page's top.
_TOP_BAND = 0.20
# How far the front matter may run. Two pages is what the longest
# consolidated caption in the corpus needs; three is slack.
_MAX_PAGES = 3
# THE FOOT idaho prints on every page: a bare folio, centred, below 90%
# of the page.
_FOOT_BAND = 0.90

# THE ORIGIN, as idaho names the court or agency it is reviewing. A
# closed set of openers the court sets at the head of that block.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "appeal of", "cross-appeal from",
    "cross-appeals from", "original proceeding", "original action",
    "certified question", "certified questions", "on certification",
    "petition for review", "petitions for review", "on petition for review",
    "petition for writ", "review of", "on appeal from",
    "proceeding in the idaho supreme court",
)
# THE OUTCOME the court states under the origin — one block, always. Its
# vocabulary is the closed set of dispositive participles; every other
# word in it is the name of a court or a paper.
_OUTCOME_WORDS = (
    "affirmed", "reversed", "vacated", "remanded", "dismissed", "denied",
    "granted", "modified", "withdrawn", "sustained", "quashed", "released",
    "set aside", "annulled", "revoked", "disqualified", "suspended",
)
# THE COURT'S OWN NUMBER, set above the caption.
_DOCKET_PREFIXES = ("docket no", "docket nos", "supreme court docket no",
                    "case no", "case nos")
# THE PAPER'S OWN NAME, set in the caption's right column.
_TITLE_OPENERS = ("opinion", "order", "amended opinion", "substitute opinion",
                  "corrected opinion", "amended order", "judgment")
# …and the names that are COMPLETE in themselves. A title may wrap
# ('OPINION ON ORDER TO' / 'SHOW CAUSE'), but where the first cell already
# names the paper whole, what follows it in the same caps is the court's
# own NOTE about the paper, not more of its name ('AMENDED OPINION' /
# 'THE COURT'S PRIOR OPINION DATED DECEMBER 19, 2025 IS HEREBY AMENDED').
_TITLE_WHOLE = frozenset({
    "OPINION", "ORDER", "AMENDED OPINION", "SUBSTITUTE OPINION",
    "CORRECTED OPINION", "AMENDED ORDER", "SUBSTITUTE ORDER", "JUDGMENT",
    "OPINION AND ORDER", "ORDER ON REHEARING", "PER CURIAM OPINION",
})
# THE FILING ROW: 'Opinion filed: February 4, 2026'.
_FILED_OPENERS = ("opinion filed", "opinion field", "order filed",
                  "amended opinion filed", "substitute opinion filed",
                  "opinion issued", "filed")
# THE SITTING: 'Boise, September 2025 Term' — where and when the court sat.
_TERM_TAIL = "term"
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# A TYPED RULE: the court's own section mark, a run of underscores (or
# dashes) alone on its row.
_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Idaho hyphenates its compound roles ('Defendant-Respondent')
# and breaks them across rows.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant", "applicants",
    "counterclaimant", "counterdefendant", "crossclaimant", "cross",
    "third", "party", "interest", "in", "of", "and", "the", "pro", "se",
    "real", "counterclaim", "counter", "defendants", "employer", "surety",
)

def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _squeeze(text: str) -> str:
    """'O P I N I O N' -> 'OPINION'. Idaho sets its labels plain, but the
    same normalisation makes the two forms one."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _is_banner(text: str) -> bool:
    """The court naming itself. Idaho's corpus carries BOTH benches —
    'IN THE SUPREME COURT OF THE STATE OF IDAHO' and 'IN THE COURT OF
    APPEALS OF THE STATE OF IDAHO' — so the test is on the words that
    name a court of this state, not on which one. It is only ever applied
    ABOVE the caption band, which is what keeps 'Appeal from the District
    Court … of the State of Idaho' out of it."""
    low = _norm(text).lower()
    return ("court" in low and "idaho" in low
            and ("supreme" in low or "appeals" in low)
            and len(low.split()) >= 6)


def _find_date(text: str) -> str | None:
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    return mm.group(1) if mm.group(1).split()[0].strip(".").lower() \
        in _MONTHS else None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


_OUTCOME_RE = re.compile(
    r"\b(?:" + "|".join(w.replace(" ", r"\s+") for w in _OUTCOME_WORDS)
    + r")\b")


def _is_outcome(text: str) -> bool:
    """Does this block STATE THE COURT'S ACTION? Idaho writes it as a
    sentence ('The judgment of the district court is affirmed in part,
    vacated in part, and remanded for additional proceedings consistent
    with this opinion.'), so the fact to test is the closed vocabulary of
    dispositive participles, not the shape of the row — and the test is
    on the WHOLE BLOCK, because the participle may sit on its second row
    ('The appeal … is' / 'dismissed for lack of jurisdiction.')."""
    return _OUTCOME_RE.search(_norm(text).lower()) is not None


def _is_foot(pm, line) -> bool:
    """idaho's page foot: a bare folio, centred at the page bottom."""
    if line.top / (pm.height or 792.0) < _FOOT_BAND:
        return False
    return is_folio_text(_norm(line.plain))


# --------------------------------------------------------------------------
# the dividers — idaho's two caption contracts, and the dispatch
# --------------------------------------------------------------------------

def _runs(chars: list) -> list:
    """``chars`` split into vertically CONTIGUOUS runs."""
    out: list = []
    for c in sorted(chars, key=lambda c: c["top"]):
        if out and c["top"] - out[-1][-1]["top"] <= _RAIL_RUN_GAP:
            out[-1].append(c)
        else:
            out.append([c])
    return out


def _rail(pm, at_x: float | None = None) -> dict | None:
    """The ')' divider on ``pm``: {'x','top','bottom'}, or None.

    A rail is a COLUMN — glyphs stacked at one x — and a CONTIGUOUS one.
    The modal column alone is not enough: ordinary prose 200pt below the
    caption sets a ')' within a point of the rail's own x, and taken into
    the stack it carries the caption's foot to the bottom of the page.

    ``at_x`` asks for the CONTINUATION of a rail an earlier page already
    established; there the column is not in doubt, so two glyphs are
    enough, but the run has to OPEN the page — a caption continues only
    at the top of the sheet it ran onto."""
    chars = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == ")"]
    if at_x is None:
        if len(chars) < _PAREN_FLOOR:
            return None
        x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
        at_x, floor, top_only = float(x), _PAREN_FLOOR, False
    else:
        floor, top_only = _PAREN_CONT_FLOOR, True
    stack = [c for c in chars if abs(c["x0"] - at_x) <= 3]
    if not stack:
        return None
    runs = _runs(stack)
    if top_only:
        run = runs[0]
        if run[0]["top"] > (pm.height or 792.0) * _TOP_BAND:
            return None
    else:
        run = max(runs, key=len)
    if len(run) < floor:
        return None
    return {"x": float(at_x), "top": min(c["top"] for c in run),
            "bottom": max(c["bottom"] for c in run)}


def _box(pm) -> dict | None:
    """The ORDER paper's drawn caption box: {'x','top','bottom','foot'},
    or None.

    A divider has to DIVIDE — the court also rules the box's right border
    at the same height, and on height alone that qualifies with every
    caption row to its left. The divider is the vertical that has caption
    text on BOTH sides of it."""
    tall = [r for r in pm.v_rules if r.height >= _BOX_RULE_MIN_H]
    if len(tall) < 2:
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
        if not divides(r.x, r.top, r.bottom):
            continue
        feet = sorted((h.top for h in pm.h_rules
                       if abs(h.top - r.bottom) <= 12),
                      key=lambda t: abs(t - r.bottom))
        return {"x": float(r.x), "top": r.top, "bottom": r.bottom,
                "foot": feet[0] if feet else r.bottom}
    return None


def _fences(pm) -> list:
    """Tops of the caption fence — the half-measure rule idaho closes its
    caption with, and repeats between consolidated cases."""
    return sorted(r.top for r in pm.h_rules
                  if _FENCE_W[0] <= r.width <= _FENCE_W[1]
                  and r.x0 <= _FENCE_X0_MAX)


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.

    Split GLYPH BY GLYPH. Whether pdfio already broke a caption row at its
    column gap is an accident of how wide the gap happened to be: the same
    corpus sets 'Children Under Eighteen (18) Years of Age. )' as one run
    and the rail alone as another, and a whole-line test puts the rail in
    one column or the other by luck."""
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
    its character — the ')' that closes '(18) Years of Age' is 100pt left
    of the rail and stays."""
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
    249pt rule anchored on the left margin under a status label set at
    x=92 is not. pdfio tags by vertical proximity alone, so the caption's
    closing fence arrives as an underline on whatever row it happens to
    follow ('<u>Defendant-Respondent.</u>'). The fence is structure — it
    renders as the rule the page drew, once."""
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
    left: list = []
    right: list = []
    side, seen = left, False
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        head = flat.split()[0].rstrip(".").lower()
        if head in ("v", "vs") and len(flat) <= 6:
            side, seen = right, True
            continue
        if set(flat) <= set("_-–— ") and len(flat) >= 3:
            continue          # the court's own typed fence, not a name
        bare = flat.rstrip(",.; ").lower()
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        if head in ("v.", "vs."):
            side, seen = right, True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    # THE COMMA is the caption's own apparatus, leading to the status row
    # under it; the FULL STOP is not — it ends the abbreviation a party is
    # incorporated under ('MURPHY LAW OFFICE, PLLC.').
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


_JUDGE_TITLE = re.compile(
    r"\b((?:Senior\s+|Chief\s+|Presiding\s+|Special\s+|Acting\s+)?"
    r"(?:District|Magistrate|Supreme\s+Court|Hearing)?\s*Judges?"
    r"(?:\s+Pro\s+Tem(?:pore)?)?)\s*[.,;]")
# The words an origin statement is BUILT from — the courts, the places and
# the court's own connectives. A judge's name is what stands between them
# and the bench title.
_ORIGIN_WORDS = frozenset({
    "appeal", "appeals", "from", "of", "the", "state", "idaho", "county",
    "court", "courts", "district", "judicial", "division", "commission",
    "board", "industrial", "original", "proceeding", "in", "for", "and",
    "matter", "case", "review", "petition", "writ", "seeking", "on",
    "certified", "question", "supreme", "magistrate", "before",
    # …and the bench itself, so a walk back from the SECOND judge named
    # in an origin does not run through the first one's title
    # ('… Magistrate Judge. Bruce L. Pickett, District Judge.').
    "judge", "judges", "senior", "chief", "presiding", "pro", "tem",
    "tempore", "special", "acting",
})
_NAME_TOKEN = re.compile(r"^(?:Mc|Mac|O[’']|D[’']|St\.\s?)?"
                         r"[A-Z][A-Za-z’'\-]*[.,;]?$")


def _trial_judge(text: str) -> str | None:
    """'…Fourth Judicial District of the State of Idaho, Ada County.
    Derrick J. O'Neill, District Judge.' — who tried it, as the origin
    statement names them.

    The BENCH TITLE is the landmark; the name is the run of name tokens
    standing immediately before it, and it ends where the statement's own
    vocabulary begins ('… Ada County.'). A record reviewed twice states
    one judge per court ('Gerald F. Schroeder, Senior District Judge.
    Matthew Haynes, Magistrate Judge.'), and a court may name a pair
    ('Anna Eckhart and Katherine Murdock, Magistrate Judges.')."""
    flat = _norm(text)
    toks = flat.split()
    starts: dict = {}
    pos = 0
    for i, tok in enumerate(toks):
        starts[pos] = i
        pos += len(tok) + 1
    found: list = []
    for mm in _JUDGE_TITLE.finditer(flat):
        i = starts.get(mm.start())
        if i is None or i == 0:
            continue
        name: list = []
        j = i - 1
        while j >= 0 and len(name) < 6:
            tok = toks[j]
            bare = tok.strip(".,;:").lower()
            if bare == "and" and name:
                name.insert(0, tok)
                j -= 1
                continue
            if bare in _ORIGIN_WORDS or not _NAME_TOKEN.match(tok):
                break
            name.insert(0, tok)
            # A token that CLOSES on a stop is the head of the name only
            # when it is an initial ('J.'); otherwise the name began here.
            j -= 1
        while name and name[0].strip(".,;:").lower() == "and":
            name.pop(0)
        if not name:
            continue
        printed = _norm(" ".join(name)).rstrip(",;")
        entry = f"{printed}, {_norm(mm.group(1))}"
        if entry not in found:
            found.append(entry)
    return "; ".join(found) if found else None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="idaho")
def read_headmatter_idaho(model, geom, **_):
    """Read idaho's caption-divider headmatter, or NOTHING."""
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
            return NOTHING          # no caption divider: not idaho's
        style, glyph = STYLE_RULED_BOX, None

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    parser = BylineParser(IDAHO.byline)
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS the reader may see, and the FURNITURE it inherits by
    # claiming the region: idaho's bare centred folio.
    rows: list = []
    foot_lines: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if _is_foot(pm, line) or finder.kind(pm, line):
                foot_lines.append(line)
            else:
                rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BANDS. The caption occupies the divider's own vertical span,
    # closed by the fence the court draws (or types) under it — and a
    # consolidated caption too long for one page runs onto the next,
    # where the court sets the rail again.
    bands: dict = {}
    fences: dict = {}
    for pm in model.pages[:_MAX_PAGES]:
        if box is not None:
            bands[1] = (box["top"] - 6.0, box["foot"])
            fences[1] = [box["foot"]]
            break
        if pm.number > 1:
            # A CAPTION CONTINUES ONLY WHERE IT RAN OUT OF PAGE. Anything
            # printed under the previous page's fence closed the caption
            # there, and a ')' on the next page is then some other row's
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
        # THE ORIGIN CLOSES THE CAPTION WHATEVER THE RAIL DOES. It is the
        # first landmark of the block below, set at the indent, and no
        # caption row ever stands under it.
        origin = [l.top for l in rows
                  if l.page == pm.number and l.top > r["top"]
                  and _origin_opener(l.plain)]
        if origin:
            bottom = min(bottom, origin[0] - 4.0)
        bands[pm.number] = (r["top"] - 6.0, bottom)
        fences[pm.number] = [t for t in fs if r["top"] < t <= bottom]
        if not close:
            break

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    banner_rows: list = []
    caption_rows: list = []
    right_rows: list = []
    origin_rows: list = []
    outcome_rows: list = []
    counsel_rows: list = []
    parties: list = []
    case_name: str | None = None

    def emit(row, role: str, rel_from: float | None = None,
             align: str = "L"):
        """One HEADMATTER ROW, from the one or more line objects the page
        set on that baseline. pdfio splits a row at its column gaps, and
        a justified counsel row can arrive in three pieces."""
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
        if align == "L" and rel_from is not None and first.x0 > rel_from + 12:
            rel = min(first.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), rel=rel, role=role))
        consumed.update(p.id for p in parts)

    def visual(lines: list) -> list:
        """``lines`` grouped into the rows the PAGE set them on."""
        out: list = []
        for line in sorted(lines, key=lambda l: (l.page, l.top, l.x0)):
            if out and out[-1][0].page == line.page \
                    and abs(out[-1][0].top - line.top) <= 2:
                out[-1].append(line)
            else:
                out.append([line])
        return out

    # ---- the masthead: everything page 1 prints above the caption -------
    top_of_caption = bands.get(1, (10 ** 6, 0))[0]
    for row in visual([l for l in rows
                       if l.page == 1 and l.top < top_of_caption]):
        text = _norm(" ".join(l.plain for l in
                              sorted(row, key=lambda l: l.x0)))
        low = text.lower()
        if _is_banner(text):
            banner_rows.append(text)
            emit(row, "court", align="C")
        elif low.startswith(_DOCKET_PREFIXES):
            # THE COURT'S OWN NUMBER, which idaho sets above the caption
            # rather than beside it. A consolidated record states them on
            # one row ('Docket Nos. 53148 and 53137').
            crit.setdefault("docket_number", text)
            emit(row, "docket", align="C")
        else:
            # Named neither, and still the court's own front matter: the
            # row is kept where the page put it and marked as what it is.
            emit(row, "case-info", align="C")

    # ---- the caption ----------------------------------------------------
    for pno, (top, bottom) in sorted(bands.items()):
        pm = pages[pno]
        band_lines = [l for l in rows
                      if l.page == pno and top <= l.top <= bottom]
        if not band_lines:
            continue
        fence_tops = fences.get(pno) or []
        band_rows = [[_unfence(l, fence_tops) for l in row]
                     for row in visual(band_lines)]
        # A consolidated caption is FENCED case by case; each fenced group
        # is one caption, and the rule between them renders where the page
        # draws it.
        groups: list = [[]]
        cuts = [] if box is not None else list(fence_tops)
        for row in band_rows:
            while cuts and row[0].top > cuts[0]:
                cuts.pop(0)
                groups.append([])
            groups[-1].append(row)
        rail_x = box["x"] if box is not None else rail["x"]
        style_id = "parenthetical-box" if glyph == ")" else "ruled-box"
        head_prov = m.Prov(pno, tuple(l.id for l in band_rows[0]))
        for group in groups:
            if not group:
                continue
            block, lp, rp = _caption_block(group, rail_x, glyph, pm, style_id)
            if block is None:
                continue
            items.append(block)
            consumed.update(block.prov.line_ids)
            caption_rows.extend(t for t in lp if t)
            right_rows.extend((r, t) for r, t in zip(block.right, rp) if t)
            sides = _sides(lp)
            for s in sides:
                if s and s not in parties:
                    parties.append(s)
            if case_name is None and len(sides) == 2:
                case_name = f"{sides[0]} v. {sides[1]}"
            elif case_name is None and len(sides) == 1:
                case_name = sides[0]
        # A RULE RENDERS WHERE THE PAGE DRAWS IT, and the block is sorted
        # back into page order at the end — so a rule carries the
        # provenance of the row it follows.
        for t in fence_tops:
            above = [l for l in band_lines if l.top < t]
            prov = m.Prov(pno, tuple(l.id for l in above[-3:])) if above \
                else head_prov
            items.append(m.Rule(prov=prov,
                                span="full" if box is not None else "left"))

    if not caption_rows and not right_rows:
        return NOTHING

    # THE RIGHT COLUMN carries the sitting, the filing date, the clerk and
    # — when the paper is not the court's ordinary opinion — its own name.
    # None of them is a docket: idaho sets the number above the caption.
    title_cells: list = []
    for row, flat in right_rows:
        low = flat.lower().rstrip(".:")
        if low.startswith(_FILED_OPENERS):
            row.role = "date"
            date = _find_date(flat)
            if date:
                crit.setdefault("decision_date", date)
        elif low.endswith(_TERM_TAIL):
            # 'Boise, September 2025 Term' — where and when the court sat.
            row.role = "date"
        elif (low.startswith(_TITLE_OPENERS) and flat == flat.upper()
                and not title_cells):
            row.role = "title"
            title_cells.append(flat)
        elif (title_cells and flat == flat.upper()
                and _squeeze(" ".join(title_cells)) not in _TITLE_WHOLE):
            # THE PAPER'S NAME MAY WRAP ('OPINION ON ORDER TO' / 'SHOW
            # CAUSE') — but only while it is not yet a whole name.
            row.role = "title"
            title_cells.append(flat)
        else:
            row.role = "case-info"
    if title_cells:
        crit.setdefault("title", _norm(" ".join(title_cells)))

    # ---- everything below the caption, by landmark ----------------------
    last_band = max(bands) if bands else 1
    below = [l for l in rows
             if (l.page > last_band
                 or (l.page == last_band and l.top > bands[last_band][1]))]

    # THE BLOCK IS THE UNIT OF MEANING, not the row. Idaho's ladder is
    # three unlabelled blocks in fixed order, and what a block IS can be
    # stated on its second row as readily as its first — the outcome of
    # city_of_idaho_falls reads 'The appeal from the district court's
    # decision upholding the Director's order is' / 'dismissed for lack
    # of jurisdiction.' Ask once per block.
    kept: list = []                 # (row, text, opens) | (row, text, "rule")
    prev: list | None = None
    for row in visual(below):
        parts = sorted(row, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in parts))
        # A BYLINE ENDS THE READER — and so does the BODY RAIL, which is
        # the same boundary measured rather than parsed: idaho sets every
        # front-matter block one indent step inside the rail and signs
        # every writing AT it. That is what ends the block on a record
        # whose byline core's grammar does not know ('LORELLO, Judge').
        if parser.parse(text) is not None:
            break
        if parts[0].x0 < body_x0 + _INDENT_MIN:
            break
        if _TYPED_RULE.match(text):
            # A TYPED RULE is the court's own section mark, closing the
            # appearances. The court sets it one leading under the last
            # row of the bar — the gap does not say it is a new block, so
            # it is recognized by what it is drawn with.
            kept.append((row, text, "rule"))
            prev = row
            continue
        # A CONTINUATION is bounded: the court sets these blocks at 13.8pt
        # leading and separates them by 19.8 or more, so a row further
        # down than that opens the NEXT rung of the ladder.
        opens = True
        if prev is not None and kept and kept[-1][2] != "rule":
            gap = row[0].top - prev[0].top
            same_page = row[0].page == prev[0].page
            wraps = (not same_page and row[0].page == prev[0].page + 1
                     and row[0].top
                     <= pages[row[0].page].height * _TOP_BAND)
            opens = not ((same_page and gap <= _BLOCK_LEAD_MAX) or wraps)
        kept.append((row, text, opens))
        prev = row

    # THE LADDER, in the order idaho always prints it: the origin, the
    # court's own outcome, then the appearances. The origin names itself;
    # the outcome states a dispositive act; whatever follows is the bar.
    # A record may print fewer rungs — a child-protection appeal states no
    # origin and no outcome (jane_doe) — but never a different order.
    roles: list = []
    state = None
    for row, text, opens in kept:
        if opens == "rule":
            roles.append("rule")
            continue
        if opens:
            block = [text]
            for r2, t2, o2 in kept[len(roles) + 1:]:
                if o2 is not False:
                    break
                block.append(t2)
            joined = " ".join(block)
            if _origin_opener(joined):
                state = "lower-court"
            elif state in (None, "lower-court") and _is_outcome(joined):
                state = "summary"
            else:
                state = "counsel"
        roles.append(state)

    for (row, text, opens), role in zip(kept, roles):
        parts = sorted(row, key=lambda l: l.x0)
        if role == "rule":
            items.append(m.Rule(prov=m.Prov(parts[0].page,
                                            tuple(p.id for p in parts)),
                                typed=True, span="center"))
            consumed.update(p.id for p in parts)
            continue
        if role == "lower-court":
            origin_rows.append(text)
        elif role == "summary":
            outcome_rows.append(text)
        else:
            counsel_rows.append(text)
        emit(row, role, rel_from=body_x0)

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
    if outcome_rows:
        crit["disposition"] = _norm(" ".join(outcome_rows))
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]

    # ---- a claim must be TOTAL ------------------------------------------
    # A READER INHERITS THE FURNITURE OF THE REGION IT CLAIMS — and no
    # more. idaho's folio sits at the page BOTTOM, so it belongs to this
    # block only on a page the reader owns end to end; on the page where
    # the claim stops at the bar, everything under it is the writing's,
    # its own foot included.
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
