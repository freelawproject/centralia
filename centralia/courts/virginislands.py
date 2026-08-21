"""Supreme Court of the Virgin Islands ('virginislands').

THE CONTRACT. Every record in this corpus is the same slip: a caption
divided by a STACKED ')' rail — the parenthetical box — closed on the
born-digital sheets by a drawn rule of half the body measure, with the
origin / dates / citation set CENTERED under it and the roster and the
appearances set at the BODY RAIL:

    For Publication                                          11-12pt
    IN THE SUPREME COURT OF THE VIRGIN ISLANDS      the banner, 13-14pt
    ERBEY HOLDING CORPORATION, JOHN R. ) S. Ct. Civ. No. 2024-0003
    ERBEY FAMILY LIMITED PARTNERSHIP,  ) Re: Super. Ct. Civ. No. 146/2018
              Appellants/Plaintiffs,   )
    v.                                 )
    BLACKROCK FINANCIAL MANAGEMENT,    )
              Appellees/Defendants.    )
    ────────────────────────────       the caption's fence, 233-267pt
        On Appeal from the Superior Court of the Virgin Islands  centered
        Division of St. Croix                                    centered
        Superior Court Judge: Hon. Harold W.L. Willocks          centered
        Considered: July 15, 2024 / Filed: December 18, 2025      centered
        Cite as 2025 VI 25                                       centered
    BEFORE:  RHYS S. HODGE, Chief Justice; …          at the body rail
    APPEARANCES:                                      at the body rail
    Joel H. Holt, Esq. …
    OPINION OF THE COURT                       the writing label — CORE'S
    HODGE, Chief Justice.                      the byline — CORE'S

Two of the thirty-two records staple a CLERK'S NOTICE COVER in front of
that sheet ('NOTICE OF ENTRY OF FINAL JUDGMENT/ORDER'), and the cover
draws its caption instead of setting a rail: a vertical rule with a
horizontal of the same half measure closing its foot. Core does not see
the cover as a stapled document — its page-2 banner carries no filing
stamp in the top four rows — so the whole notice read as the opinion and
both records came back AUTHORLESS. The cover is front matter and is read
as such here; the writing then opens where the page opens it, at
'PER CURIAM.'.

THE DISPATCH IS THE DIVIDER, never a word. A page carrying the court's
banner over a stacked ')' rail is this contract; the notice cover is the
drawn box in front of it. A record drawing neither gets NOTHING and core's
shared walk places its rows unidentified, which is the smaller error.

TWENTY OF THE THIRTY-TWO SOURCES ARE SCANS. They are not image-only: the
scanner laid down an OCR text layer with real coordinates, and the rail
survives it in every one (4 to 22 glyphs in a column that wanders 1.5pt
on a clean sheet and 5pt on the worst). What does NOT survive is the drawn
ink — a scan has no h_rules at
all — so the caption's closing fence cannot be the thing that ends the
caption. The rail's own last glyph ends it instead, and the fence, where
the page really draws it, is re-emitted as the rule it is. Everything
below the caption is read by LANDMARK plus the two columns the page uses
(the centred axis and the body rail), which is the part of the geometry
OCR reproduces faithfully.

The reader claims HEADMATTER ONLY, and it ends at the first of four
things the page itself prints: the court's writing label ('OPINION OF THE
COURT', 'ORDER OF THE COURT', 'JUDGMENT'), a byline at the body rail, the
144pt footnote rule, or a footnote label opening a full-measure row at
that rail. The gap bound below those is a backstop, not a boundary — the
appearances block is a stack of entries separated by exactly the gap that
separates one block from the next, so nothing here may be ended by
whitespace alone.

ONE CORE DEFECT IS REPORTED, NOT FIXED. The registered byline grammar for
this court is `abbrev`, and the court signs its opinion of the Court in
PROSE — 'HODGE, Chief Justice.', 'SWAN, Associate Justice'. `abbrev`
matches none of them, so assembly falls through to the clerk's conformed
sign-off at the END of the document and thirty of the thirty-two records
are authored by '/s/ Rhys S. Hodge' or by a deputy clerk ('Jahkyda
Coakley', 'Reisha Corneiro'). The reader cannot use the shared parser as
its stop for the same reason, so it builds a prose one of its own below;
nothing outside this file uses it.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..profile import BylineGrammar
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# virginislands' profile is registered in the shared table; this file owns
# its reader only, and never re-declares the court.

STYLE_PAREN_RAIL = "parenthetical-box slip"
STYLE_NOTICE_COVER = "clerk's notice cover + parenthetical-box slip"

# ---- the court's declared facts (measured over all 32 records) ----------
# THE RAIL. ')' occurs in ordinary prose, so a divider is a COLUMN of them
# stacked at one x. The shortest rail in the corpus runs 4 glyphs (ranger,
# gibbs — short captions on a wide sheet); the tallest runs 22 (erbey).
_RAIL_FLOOR = 4
# A glyph belongs to the rail when it stands in the rail's own column. The
# rail wanders 1.5pt within a born-digital sheet and up to 5pt down an OCR
# page (in_re_garcia: 317.3 at the head, 312.5 at the foot); the nearest
# other ink on those rows — the docket column — is 20pt to its right, so
# 6pt reaches the rail and nothing else.
_RAIL_WINDOW = 6.0
# THE CAPTION FENCE: a drawn rule of HALF the body measure anchored on the
# left margin — 233.6 to 267.2pt over the sixteen sheets that draw ink,
# always at x0 71-72. The court's other rules are a different measure: the
# footnote separator is 144pt, the conformed-signature rule 116-163pt out
# in the right-hand column at x0>=356, and an emphasis underline under a
# caption cell is 99.7pt.
_FENCE_W = (200.0, 290.0)
_FENCE_X0_MAX = 120.0
# THE NOTICE COVER'S BOX: one vertical rule dividing the caption (55.3 and
# 82.8pt tall over the two records), closed at its foot by a horizontal of
# the same half measure the slip fences its caption with.
_BOX_RULE_MIN_H = 40.0
# HOW FAR A BLOCK WRAPS. The front matter is set at 13-14pt leading, and
# the gap between one APPEARANCE and the next runs 27.6pt on the digital
# sheets and up to 37.2 where the scanner stretched the page. That gap is
# not what ends anything, and it must not: the appearances block is a
# stack of entries separated by exactly it. What ends a block is the next
# LANDMARK — the writing label, the byline, the footnote rule, a footnote
# mark at the rail — and the bound below is only a backstop.
_BLOCK_GAP_MAX = 40.0
# …and a little more directly under a bare label row.
_LABEL_GAP_MAX = 46.0
# A block may WRAP THE PAGE: its continuation opens the next page's top
# (erbey and clark carry their appearances over) IN THE BLOCK'S OWN
# COLUMN — the body rail or the one step of indent the court sets its
# 'Attorney for …' rows at (36pt).
_TOP_BAND = 0.20
_WRAP_COLUMN = 45.0
# How far the front matter may run. Two sheets is all any record uses; the
# third is slack for the notice cover.
_MAX_PAGES = 3
# THE FOOTNOTE SEPARATOR the court rules at the body rail. Below it is the
# note, never the headmatter.
_FN_SEP_W = (130.0, 155.0)
# …and where the page is a SCAN there is no rule to find, so the note is
# known by what opens it: a footnote LABEL at the body rail on a row that
# runs the measure. The court sets the label as a superscript and the
# scanner flattens it — a bare numeral on the digital sheets, an apostrophe
# or an asterisk on the OCR ones.
_FN_MARKS = ("'", "\u2019", "\u2018", "*", "\u2020", "\u2021", "\u00b0",
             '"', "\u201c", "!", "|")
_FN_MEASURE = 0.62

# THE ORIGIN, as the court names the proceeding it is reviewing. A closed
# set of openers set at the head of the centred block.
_ORIGIN_OPENERS = (
    "on appeal from", "on appeals from", "on petition for",
    "on petitions for", "on application for", "on applications for",
    "on writ of", "on certified question", "on certification from",
    "on review of", "on rehearing", "on motion for",
    "on certiorari", "original jurisdiction",
)
# The rows that CONTINUE it, as the court sets them under the opener.
_ORIGIN_CONT = ("division of", "superior court judge", "before: hon.",
                "before hon.", "appellate division", "magistrate division")
# THE DATE LABELS. A closed vocabulary read off the label, not the date.
_DATE_LABELS = ("considered", "argued", "submitted", "filed", "decided",
                "heard", "reargued", "resubmitted")
# THE COURT'S OWN NEUTRAL CITATION, which it prints last in the centred
# block ('Cite as: 2025 VI 21').
_CITE_OPENER = "cite as"
# THE ROSTER LABEL and THE APPEARANCES LABEL, both at the BODY RAIL. The
# centred 'Before: Hon. …, Superior Court Judge' names the judge below and
# is told from the roster by its COLUMN, not by its wording.
_PANEL_LABELS = ("before",)
_COUNSEL_LABELS = ("appearance", "appearances", "attorney", "attorneys",
                   "counsel", "counsel of record", "appearances of counsel")
# THE COURT'S OWN NUMBER, and the number of the court below. Both stand in
# the caption's right column at the same size on the same rail; only the
# TRIBUNAL each names tells them apart, and within this judicial system
# that is a closed set of two.
_DOCKET_PREFIXES = ("s. ct.", "s.ct.", "sct-", "sct ", "s ct.",
                    "supreme court no")
_LOWER_PREFIXES = ("re:", "re.", "ref:")
# THE WRITING LABEL the court centres over every writing. It is the
# reader's stop; core anchors the writing on it.
_LABEL_WORDS = ("OPINION", "ORDER", "JUDGMENT", "MEMORANDUM", "DECREE",
                "MANDATE")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. This court hyphenates and slashes its compound roles
# ('Appellants/Plaintiffs', 'Appellee/Defendant').
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant",
    "applicants", "counter", "cross", "third", "party", "nominal",
    "interest", "in", "of", "and", "the", "pro", "se", "et", "al",
)
# BENCH WORDS — a closed vocabulary, so a roster never yields a justice
# called 'and' or one called 'Justices'.
_BENCH_WORDS = ("justice", "justices", "judge", "judges", "chief",
                "associate", "designated", "senior", "acting", "presiding",
                "hon", "honorable", "sitting", "designation", "retired",
                "participating")
_SUFFIXES = ("jr", "sr", "ii", "iii", "iv")

_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})")

# The court signs its opinion of the Court in PROSE ('HODGE, Chief
# Justice.'), which the registered `abbrev` grammar does not accept — see
# the note at the foot of this file. The reader needs a byline test that
# works today, so it builds its own; nothing outside this file uses it.
_BYLINE = BylineGrammar(style="prose", titles=("Justice", "Judge"))


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _label_of(text: str) -> str:
    """A row's LABEL: what stands before its colon, folded. 'APPEARANCES:'
    -> 'appearances'; 'Considered and Filed: August 20, 2025' ->
    'considered and filed'; a row with no colon folds whole."""
    flat = _norm(text)
    head = flat.split(":", 1)[0] if ":" in flat[:34] else flat
    return head.strip().strip(".,;!·*†‡'’ ").lower()


def _first_word(text: str) -> str:
    """The row's opening word, folded. THE COLON IS THE FIRST THING OCR
    LOSES on this paper — twenty of the thirty-two sheets print 'BEFORE'
    where the born-digital ones print 'BEFORE:' — so a label that shares
    its row with the block it opens has to be read off its first word."""
    flat = _norm(text)
    return flat.split()[0].strip(":.,;'’ ").lower() if flat.split() else ""


def _is_banner(text: str) -> bool:
    """The court naming itself, set 13-14pt over the caption. Applied only
    ABOVE the caption band, which is what keeps 'On Appeal from the
    Superior Court of the Virgin Islands' out of it."""
    low = _norm(text).lower()
    return ("court" in low and "supreme" in low and "virgin islands" in low)


def _is_status_flag(text: str) -> bool:
    """'For Publication' / 'FOR PUBLICATION' — the publication flag the
    court sets above its banner. Core records it as a `status` drop for
    every court that prints one; a reader claiming the region inherits
    that duty."""
    return _norm(text).strip(" .*").lower() in (
        "for publication", "not for publication", "unpublished",
        "not published")


def _find_date(text: str) -> str | None:
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    got = _norm(mm.group(1))
    return got if got.split()[0].strip(".").lower() in _MONTHS else None


def _opens_footnote(text: str, x0: float, x1: float, width: float,
                    body_x0: float) -> bool:
    """Does this row open a page-foot NOTE? The court sets its footnotes at
    BODY SIZE under a 144pt rule, and a scan draws no rule at all — so on
    twenty of the thirty-two sheets the only thing that says 'note' is the
    label the court raises at its head and the fact that the row runs the
    full measure. An appearance never does both: it is a name, a firm and a
    town, none of them reaching half way across the page."""
    flat = _norm(text)
    if x0 > body_x0 + 8 or not flat:
        return False
    if (x1 - x0) < _FN_MEASURE * (width - 2 * body_x0):
        return False
    tok = flat.split()[0].strip("(),.")
    return (tok.isdigit() and len(tok) <= 2) or tok in _FN_MARKS


def _is_writing_label(text: str, x0: float, body_x0: float) -> bool:
    """The centred ALL-CAPS label the court sets over each writing. It is
    the reader's stop and core's anchor, so it is never claimed."""
    flat = _norm(text).rstrip(".:")
    if not flat or len(flat) > 44 or flat != flat.upper():
        return False
    if x0 <= body_x0 + 30:
        return False                       # at the rail: not the label
    words = set(flat.replace("/", " ").split())
    return bool(words & set(_LABEL_WORDS))


# --------------------------------------------------------------------------
# the dividers — the dispatch
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The ')' divider on ``pm``: {'x','top','bottom'}, or None. A rail is
    a COLUMN of glyphs stacked at one x, not a count of ')' anywhere on the
    page."""
    chars = [c for line in pm.lines for c in line.chars
             if (c.get("text") or "") == ")"]
    if len(chars) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    stack = [c for c in chars if abs(c["x0"] - x) <= _RAIL_WINDOW]
    if len(stack) < _RAIL_FLOOR:
        return None
    return {"x": float(x), "top": min(c["top"] for c in stack),
            "bottom": max(c["bottom"] for c in stack)}


def _box(pm) -> dict | None:
    """The notice cover's DRAWN caption divider: {'x','top','foot'}, or
    None. A divider has to DIVIDE — the cover rules one vertical only, and
    it is confirmed by caption text standing on BOTH sides of it and by
    the half-measure horizontal that closes its foot."""
    for r in sorted((v for v in pm.v_rules if v.height >= _BOX_RULE_MIN_H),
                    key=lambda v: abs(v.x - pm.width / 2.0)):
        left = right = False
        for line in pm.lines:
            if not (r.top - 2 <= line.top <= r.bottom + 2):
                continue
            for c in line.chars:
                if not (c.get("text") or "").strip():
                    continue
                if c["x1"] <= r.x - 2:
                    left = True
                elif c["x0"] >= r.x + 2:
                    right = True
        if not (left and right):
            continue
        feet = [h.top for h in pm.h_rules
                if _FENCE_W[0] <= h.width <= _FENCE_W[1]
                and h.x0 <= _FENCE_X0_MAX and abs(h.top - r.bottom) <= 12]
        if not feet:
            continue
        return {"x": float(r.x), "top": r.top, "foot": feet[0]}
    return None


def _fences(pm) -> list:
    """Tops of the caption fence — the half-measure rule the born-digital
    sheet closes its caption with. A scan draws no ink and has none."""
    return sorted(r.top for r in pm.h_rules
                  if _FENCE_W[0] <= r.width <= _FENCE_W[1]
                  and r.x0 <= _FENCE_X0_MAX)


def _fn_sep(pm) -> float | None:
    """Top of the footnote separator the court rules at the body rail, or
    None. Below it is a note, never the front matter."""
    tops = sorted(r.top for r in pm.h_rules
                  if _FN_SEP_W[0] <= r.width <= _FN_SEP_W[1]
                  and r.x0 <= _FENCE_X0_MAX)
    return tops[0] if tops else None


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.
    Split GLYPH BY GLYPH: whether pdfio already broke a caption row at its
    column gap is an accident of how wide that gap happened to be, and the
    OCR sheets set party name, rail and docket as one run about as often
    as three."""
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
    its character."""
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
    """``line`` with any underline the CAPTION FENCE put on it cleared. A
    drawn rule whose ends coincide with the row above is an underline; a
    266pt rule anchored on the left margin under a 112pt status row set at
    x=104 is not."""
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


def _caption_block(rows: list, rail_x: float, glyph: str | None, pm):
    """One caption as a CaptionBlock, plus each column's plain text. Cells
    are PAIRED BY VISUAL ROW so the two stacks stay aligned."""
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
        style_id="parenthetical-box",
        fp={"rail": glyph or "drawn", "mid_x": rail_x},
        prov=m.Prov(pm.number, ids))
    return block, left_plain, right_plain


def _sides(rows: list):
    """The party names either side of the pivot, built from the party
    NAMES — never by joining the caption wholesale, because the status
    labels and the pivot are apparatus, not names.

    THE PIVOT IS A LENGTH, not a word. This court sets 'v.' alone in the
    left column, and twenty of its thirty-two sheets are OCR — the same
    glyph comes back as 'v', 'Vv', 'V', '¥', 'q'. Nothing two characters
    long is a party, so the pivot is the short row and the vocabulary
    stays closed."""
    left: list = []
    right: list = []
    side, seen = left, False
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        bare = flat.strip(".,;:_- ")
        if len(bare) <= 2 and not seen:
            side, seen = right, True
            continue
        if set(flat) <= set("_-–— ") and len(flat) >= 3:
            continue          # a typed separator, not a name
        words = [w.strip(",.;:-/ ") for w in
                 bare.rstrip(".,").replace("-", " ").replace("/", " ").split()]
        if words and all(w.lower() in _STATUS_WORDS or not w for w in words):
            continue
        side.append(flat)
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _panel_names(text: str) -> list:
    """The justices named in a 'BEFORE …' roster. Split on the court's own
    punctuation and keep what is not a BENCH word — without which the
    roster yields a justice called 'Chief' and one called 'and'."""
    body = _norm(text)
    if _first_word(body) in _PANEL_LABELS:
        body = body.split(":", 1)[1] if ":" in body[:12] else \
            body.split(None, 1)[1] if len(body.split()) > 1 else ""
    at = body.find("[")
    if at >= 0:
        body = body[:at].rstrip()
    names: list = []
    for chunk in body.replace(";", ",").replace(" and ", ", ").split(","):
        piece = chunk.strip().strip(".!*†‡'’ ").strip()
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

    A docket wrap carries no prose: more of the numbers themselves, the
    island code the court sets under the number it qualifies ('(STT)'),
    or the court's own note that the numbers travel together
    ('Consolidated Cases'). Every word is a number, an upper-case code, or
    one of the court's two joining words."""
    flat = _norm(text)
    core = re.sub(r"\([^)]*\)", " ", flat).strip()
    if not core:
        return True                       # '(STT)' — the island code alone
    joiners = ("and", "consolidated", "cases", "case", "no", "nos")
    return all(w.strip(".,/;") == w.strip(".,/;").upper()
               or w.lower().strip(".,/;") in joiners
               for w in core.split())


def _trial_judge(rows: list) -> str | None:
    """Who tried it, as the origin block names them: 'Superior Court Judge:
    Hon. Harold W.L. Willocks' or 'Before: Hon. Ernest J. Morris, Jr.,
    Superior Court Judge'."""
    for row in rows:
        flat = _norm(row)
        low = flat.lower()
        if low.startswith(("superior court judge", "magistrate judge",
                           "appellate division judge")):
            tail = flat.split(":", 1)[1].strip() if ":" in flat else ""
            if tail:
                return tail
        if low.startswith(("before:", "before ")) and "hon." in low:
            tail = flat.split(":", 1)[1].strip() if ":" in flat else flat
            return tail.rstrip(".")
    return None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="virginislands")
def read_headmatter_virginislands(model, geom, **_):
    """Read the parenthetical-box headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING

    # ---- the dispatch: which page carries the rail, and is a cover in
    # front of it? -------------------------------------------------------
    rail = None
    rail_pm = None
    for pm in model.pages[:2]:
        got = _rail(pm)
        if got is None:
            continue
        banner = [l for l in pm.lines
                  if l.top < got["top"] and _is_banner(l.plain)]
        if not banner:
            continue
        rail, rail_pm = got, pm
        break
    if rail is None:
        return NOTHING
    cover = _box(model.pages[0]) if rail_pm.number == 2 else None
    if rail_pm.number == 2 and cover is None:
        return NOTHING              # a page-2 rail with no cover in front

    style = STYLE_NOTICE_COVER if cover else STYLE_PAREN_RAIL
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    parser = BylineParser(_BYLINE)
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # ---- the rows the reader may see, and the furniture it inherits ----
    rows: list = []
    furniture: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                furniture.append(line)
            else:
                rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    status_lines: list = []
    banner_rows: list = []
    caption_rows: list = []
    right_rows: list = []
    origin_rows: list = []
    counsel_rows: list = []
    panel_rows: list = []
    cover_rows: list = []
    parties: list = []
    case_name: str | None = None
    docket_cells: list = []
    lower_cells: list = []

    def visual(lines: list) -> list:
        """Group lines into the rows the PAGE prints. pdfio splits a row at
        its column gaps, and this court sets a block's label in one column
        and its first entry in the next ('BEFORE:' at 72, the roster at
        144) — emitted separately those render as a label alone on a row."""
        out: list = []
        for line in sorted(lines, key=lambda l: (l.page, l.top, l.x0)):
            if out and out[-1][0].page == line.page \
                    and abs(out[-1][0].top - line.top) <= 2:
                out[-1].append(line)
            else:
                out.append([line])
        return out

    def emit(row, role: str, align: str = "L",
             rel_from: float | None = None):
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
        if rel_from is not None and first.x0 > rel_from + 12:
            rel = min(first.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), rel=rel, role=role))
        consumed.update(p.id for p in parts)

    def caption_band(pm, top: float, bottom: float, rail_x: float,
                     glyph: str | None, fence_tops: list,
                     is_slip: bool = True):
        """Read one caption band into a CaptionBlock and record what its
        two columns say. Returns the provenance of the band's LAST row —
        a rule renders where the page draws it, and the block is sorted
        back into page order at the end, so a rule given no line of its
        own sorts past every row in the document and lands at the foot."""
        nonlocal case_name
        band = [l for l in rows
                if l.page == pm.number and top <= l.top <= bottom]
        if not band:
            return m.Prov(pm.number, ())
        vis = [[_unfence(l, fence_tops) for l in row]
               for row in visual(band)]
        tail = m.Prov(pm.number, tuple(l.id for l in vis[-1]))
        block, lp, rp = _caption_block(vis, rail_x, glyph, pm)
        if block is None:
            return tail
        items.append(block)
        consumed.update(block.prov.line_ids)
        right_rows.extend((r, t, is_slip) for r, t in zip(block.right, rp)
                          if t)
        # THE COVER'S CAPTION IS THE SLIP'S CAPTION, set again by the
        # clerk in the clerk's own house style ('SCT-Civ-2025-0205' for
        # 'S. Ct. Civ. No. 2025-0205', 'In Re:' for 'IN RE:'). It renders
        # where the page prints it; what the document IS gets read off the
        # court's own sheet, so the same case never arrives twice.
        if not is_slip:
            return tail
        caption_rows.extend(t for t in lp if t)
        sides = _sides(lp)
        for one in sides:
            if one and one not in parties:
                parties.append(one)
        if case_name is None and len(sides) == 2:
            case_name = f"{sides[0]} v. {sides[1]}"
        elif case_name is None and len(sides) == 1:
            case_name = sides[0]
        return tail

    # ---- the clerk's notice cover, where one is stapled in front -------
    if cover is not None:
        pm = model.pages[0]
        for row in visual([l for l in rows if l.page == 1
                           and l.top < cover["top"] - 2]):
            text = _norm(" ".join(l.plain for l in row))
            if _is_status_flag(text):
                status_lines.extend(row)
            elif _is_banner(text):
                banner_rows.append(text)
                emit(row, "court", align="C")
            else:
                emit(row, "summary")
        tail = caption_band(pm, cover["top"] - 6.0, cover["foot"],
                            cover["x"], None, [cover["foot"]],
                            is_slip=False)
        items.append(m.Rule(prov=tail, span="left"))
        # BELOW THE BOX the cover states what it is and who was served.
        for row in visual([l for l in rows if l.page == 1
                           and l.top > cover["foot"]]):
            text = _norm(" ".join(sorted(row, key=lambda l: l.x0)[i].plain
                                  for i in range(len(row))))
            flat = _norm(text).rstrip(".:")
            role = "title" if (flat == flat.upper() and len(flat) <= 60
                               and any(w in flat for w in _LABEL_WORDS)) \
                else "summary"
            if role == "title":
                crit.setdefault("title", flat)
            cover_rows.append(text)
            emit(row, role, align="L", rel_from=body_x0)

    # ---- the masthead: everything the rail page prints above the caption
    pm = rail_pm
    fence_tops = _fences(pm)
    banner_bottom = 0.0
    for row in visual([l for l in rows if l.page == pm.number
                       and l.top < rail["top"] + 2]):
        text = _norm(" ".join(l.plain for l in row))
        if _is_banner(text):
            banner_rows.append(text)
            emit(row, "court", align="C")
            banner_bottom = max(l.bottom for l in row)
        elif _is_status_flag(text):
            status_lines.extend(row)
        elif banner_bottom == 0.0:
            # Anything else ABOVE the banner is the sheet's own furniture.
            status_lines.extend(row)

    # ---- the caption ---------------------------------------------------
    close = [t for t in fence_tops if t >= rail["bottom"] - 2]
    bottom = close[0] if close else rail["bottom"] + 6.0
    tail = caption_band(pm, banner_bottom + 2.0, bottom, rail["x"], ")",
                        fence_tops)
    if not caption_rows and not right_rows:
        return NOTHING
    if close:
        items.append(m.Rule(prov=tail, span="left"))

    # ---- the caption's RIGHT COLUMN: two numbers, two tribunals --------
    prev_role = None
    for row, flat, is_slip in right_rows:
        # THE RAIL LEAVES DEBRIS ON AN OCR PAGE. in_re_garcia's scanner
        # read the divider as ')_' and split the underscore into the right
        # column, which pushed the court's own docket out of the closed
        # vocabulary and left the record with none.
        low = flat.lower().lstrip(") _|]}·-–—.\u2019'")
        if low.startswith(_DOCKET_PREFIXES):
            row.role = "docket"
            if is_slip:
                docket_cells.append(_norm(flat.lstrip(") _|]}·-–—.")))
        elif low.startswith(_LOWER_PREFIXES):
            row.role = "lower-court"
            if is_slip:
                lower_cells.append(_norm(flat.lstrip(") _|]}·-–—.")))
        elif prev_role in ("docket", "lower-court") and _docket_tail(flat):
            row.role = prev_role
            target = docket_cells if prev_role == "docket" else lower_cells
            if target and is_slip:
                target[-1] = f"{target[-1]} {_norm(flat)}"
        else:
            row.role = "caption"
        prev_role = row.role if row.role != "caption" else prev_role
    if docket_cells:
        crit["docket_number"] = docket_cells[0]
        for extra in docket_cells[1:]:
            crit.setdefault("other_dockets", []).append(extra)
    if lower_cells:
        crit["lower_court_docket"] = lower_cells

    # ---- everything below the caption, by landmark ---------------------
    fn_tops = {p: _fn_sep(pages[p]) for p in
               range(pm.number, min(pm.number + 2, len(model.pages)) + 1)
               if p in pages}
    below = [l for l in rows
             if (l.page > pm.number
                 or (l.page == pm.number and l.top > bottom))]
    state = None
    prev: list | None = None
    prev_label = False
    for row in visual(below):
        ordered = sorted(row, key=lambda l: l.x0)
        first = ordered[0]
        text = _norm(" ".join(l.plain for l in ordered))
        # THE READER STOPS AT THE COURT'S OWN WRITING LABEL, and at a
        # byline where the paper carries none. Nothing below is its
        # business.
        if _is_writing_label(text, first.x0, body_x0):
            break
        # A BYLINE SITS AT THE BODY RAIL. The roster's continuation does
        # not — it stands in the roster's own column (x0=144 against a
        # rail of 70-84) and it reads exactly like one ('HAROLD W.L.
        # WILLOCKS, Associate Justice.'). Tested without the column the
        # reader ended at the roster's second row and lost every
        # appearance in the volume.
        if first.x0 <= body_x0 + 8 and parser.parse(text) is not None:
            break
        # …and at the footnote separator: what the court rules off at the
        # page foot is a note, whatever column it stands in.
        sep = fn_tops.get(first.page)
        if sep is not None and first.top > sep:
            break
        if _opens_footnote(text, first.x0,
                           max(l.x1 for l in row),
                           pages[first.page].width or 612.0, body_x0):
            break
        word = _first_word(text)
        at_rail = first.x0 <= body_x0 + 8
        # THE APPEARANCES LABEL STANDS ALONE on its row; the roster label
        # shares its row with the roster. So the one is read as a whole
        # row and the other as a first word — and 'Attorney for Appellee'
        # deep inside the block, which opens on the same word, is neither.
        bare = _norm(text).strip(":. ").lower()
        opener = None
        if text.lower().startswith(_ORIGIN_OPENERS):
            opener = "lower-court"
        elif word in _PANEL_LABELS and at_rail:
            opener = "panel"
        elif bare in _COUNSEL_LABELS and at_rail:
            opener = "counsel"
        elif word in _DATE_LABELS and ":" in text[:34]:
            opener = "date"
        elif text.lower().startswith(_CITE_OPENER):
            opener = "docket"
        elif state == "lower-court" and text.lower().startswith(_ORIGIN_CONT):
            opener = "lower-court"
        if opener is None:
            # A CONTINUATION IS BOUNDED. Everything this contract does not
            # name, more than a block's gap below the row before it, is the
            # page-foot note or the writing itself.
            if state is None or prev is None:
                break
            gap = first.top - prev[0].top
            same_page = first.page == prev[0].page
            # A BLOCK'S CONTINUATION OPENS IN THE BLOCK'S OWN COLUMN.
            # Across a page turn that is the only thing left to test, and
            # it matters: penn's running head survives core's head tests
            # in one piece ('2026 V16', out at x=287 on a body rail of 84)
            # and read as a wrap it put the head into the appearances.
            wraps = (not same_page and first.page == prev[0].page + 1
                     and first.top
                     <= (pages[first.page].height or 792.0) * _TOP_BAND
                     and first.x0 <= body_x0 + _WRAP_COLUMN)
            cap = _LABEL_GAP_MAX if prev_label else _BLOCK_GAP_MAX
            if not ((same_page and gap <= cap) or wraps):
                break
            opener = state
        role = opener
        align = "C" if role in ("lower-court", "date", "docket") \
            and not at_rail else "L"
        if role == "lower-court":
            origin_rows.append(text)
        elif role == "counsel":
            counsel_rows.append(text)
        elif role == "panel":
            panel_rows.append(text)
        elif role == "date":
            date = _find_date(text)
            if date and _label_of(text).endswith(
                    ("filed", "decided", "considered and filed")):
                crit["decision_date"] = date
            elif date:
                crit.setdefault("submitted", text)
        elif role == "docket":
            cite = _norm(text)
            if cite.lower().startswith(_CITE_OPENER):
                cite = cite[len(_CITE_OPENER):].lstrip(": ")
            crit.setdefault("other_dockets", []).append(cite)
        emit(row, role, align=align, rel_from=body_x0)
        prev_label = bare in _COUNSEL_LABELS
        state = role if role != "docket" else state
        prev = ordered

    # ---- what the block says -------------------------------------------
    if banner_rows:
        crit["court"] = _norm(banner_rows[0])
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
        judge = _trial_judge(origin_rows)
        if judge:
            crit["lower_court_judge"] = judge
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        text = _norm(" ".join(counsel_rows))
        if _norm(counsel_rows[0]).strip(":. ").lower() in _COUNSEL_LABELS:
            text = _norm(" ".join(counsel_rows[1:])) \
                if len(counsel_rows) > 1 else text
        crit["attorneys"] = text[:4000]
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if _first_word(roster) in _PANEL_LABELS:
            roster = roster.split(":", 1)[1].lstrip() if ":" in roster[:12] \
                else roster.split(None, 1)[1] if len(roster.split()) > 1 \
                else roster
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if cover_rows:
        crit.setdefault("history", _norm(" ".join(cover_rows))[:600])

    # ---- a claim must be TOTAL ------------------------------------------
    if status_lines:
        dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in status_lines))[:200],
            prov=m.Prov(status_lines[0].page,
                        tuple(l.id for l in status_lines)),
            kind="status"))
        consumed.update(l.id for l in status_lines)
    # A READER INHERITS THE FURNITURE OF THE REGION IT CLAIMS — and no
    # more. On a page the reader owns end to end, the running head and the
    # folio are its; on the page where the claim stops at the roster,
    # everything under that roster is the writing's, its own foot included.
    mine = {p for p in {l.page for l in rows}
            if all(l.id in consumed for l in rows if l.page == p)}
    for line in furniture:
        if line.page not in mine:
            continue
        dropped.append(m.Dropped(
            text=_norm(line.plain), prov=m.Prov(line.page, (line.id,)),
            kind=finder.kind(pages[line.page], line) or "furniture"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
