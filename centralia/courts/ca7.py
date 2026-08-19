"""United States Court of Appeals for the Seventh Circuit ('ca7').

Everything unique to ca7 lives here. It imports core, never another court
file, and no other court file imports it.

ca7 prints TWO layouts, and each one names itself by a landmark it always
sets.

STYLE 'typed rules' — the slip opinion (97 of the corpus's 100 records).
The court fences every section of its headmatter with a TYPED RULE: twenty
underscores set at the body size, 120pt wide, centred on the page axis.
Nothing is drawn; the rule is characters.

    In the                                      the banner, 14/24/18pt
    United States Court of Appeals
    For the Seventh Circuit
    ____________________                        a typed 120pt fence
    No. 25-2054                                 the docket, at the rail
    UNITED STATES OF AMERICA,                   the caption: parties…
             Plaintiff-Appellee,                …their status, at the right
        v.                                      …the pivot, on the axis
    MONA GHOSH,
             Defendant-Appellant.
    ____________________
    Appeal from the United States District …    the origin, set 10pt
    No. 1:23-cr-00140 — Franklin U. Valderrama, Judge.
    ____________________
    ARGUED MAY 14, 2026 — DECIDED JULY 31, 2026 the dates
    ____________________
    Before RIPPLE, SCUDDER, and ST. EVE, …      the roster
    RIPPLE, Circuit Judge. Mona Ghosh pleaded…  the byline — the reader stops

THE FENCE MAKES THE BAND THE UNIT OF MEANING. Each band is asked once what
section it is, by its own landmark and not by its position: a consolidated
record prints docket-then-caption and then a SECOND caption with no docket
of its own (terry_ferguson), and a record with a full-measure typed rule
INSIDE the caption (bad_river) is using that rule as a divider between two
appeals, not as a fence — width tells the two apart.

The ORIGIN band is identified by GEOMETRY, not by wording: ca7 is the only
court in this corpus that sets one band of its headmatter a step SMALLER
than the body (10pt against 12pt), and that band is always the statement of
where the case came from.

Below the last fence lies the only UNFENCED region, and it holds two things
in a fixed order: the roster, then the writing. The roster is bounded by
ca7's own punctuation — it TERMINATES on a full stop ('… Circuit Judges.')
and its wraps do not ('Before ROVNER, JACKSON-AKIWUMI, and MALDONADO, Cir-'
/ 'cuit Judges.') — so the reader takes the 'Before …' row and every
unterminated continuation of it, and stops. An in-chambers opinion prints no
roster at all ('BRENNAN, Chief Judge, in chambers.'), and there the reader
claims nothing below the last fence.

STYLE 'order form' — the courthouse letterhead (3 records). NO rules at
all; the zones stand on whitespace, in the court's fixed order, and the
block is closed by the order's own LETTER-SPACED title:

    NONPRECEDENTIAL DISPOSITION                 the publication flag
    To be cited only in accordance with FED. R. APP. P. 32.1   (a notice)
    United States Court of Appeals              the banner, 26pt
    For the Seventh Circuit
    Chicago, Illinois 60604                     …with the courthouse address
    Submitted April 28, 2026*                   the dates, one per row
    Decided April 29, 2026
    Amended April 30, 2026
    Before                                      the roster opener, alone
    THOMAS L. KIRSCH II, Circuit Judge          …ONE JUDGE PER ROW
    JOSHUA P. KOLAR, Circuit Judge
    REBECCA TAIBLESON, Circuit Judge
    No. 25-1631                                 the docket, at the rail
    PAUL A. SMITH,          | Appeal from the United States District
        Plaintiff-Appellant,| Court for the Central District of Illinois.
        v.                  | No. 21-1236
    PAMELA E. HART …        | Colleen R. Lawless,
        Defendants-Appellees| Judge.
    O R D E R                                   the title — the reader stops

THE ROSTER IS A ZONE, and claiming it is the point: each of its rows is a
name and a bench title and nothing else, which is exactly the shape of a
byline, so row after row of them reads as three separate writings unless
the zone owns them. The caption below it is TWO COLUMNS held apart by
whitespace alone — the parties on the left, the court appealed from on the
right — and the gutter between them is MEASURED (the widest column of the
band that no glyph occupies on ANY row), never assumed.

The reader claims HEADMATTER ONLY. It stops at the first byline (slip) or
at the order's title (order form), and everything below is core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import FurnitureFinder
from . import register

# The circuits' shared byline grammar, copied VERBATIM out of the loop ca7
# used to sit in, so nothing about its bylines changes by being moved here.
CA7 = register(CourtProfile(
    "ca7", "United States Court of Appeals for the Seventh Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
    # ca7's own indent stops, measured over the corpus: the body sits on a
    # 144pt rail, a paragraph opens 18pt in, and a block quotation is set
    # out 36pt (and narrowed to 180-432). The default 12pt is not this
    # court's typography.
    para_indent_min=18.0,
))

STYLE_TYPED_RULES = "typed rules"
STYLE_ORDER_FORM = "order form"

# ---- ca7's declared facts (measured over the corpus, not tuned) -----------
# THE FENCE: twenty underscores at the body size — 120.0pt wide, x0=246 on a
# 612pt page, dead on the page axis, on every one of the 97 slip records.
# Width is the fact: the same court types a FULL-MEASURE underscore row
# (324pt, on the body rail) as a divider between two consolidated captions,
# and that one is not a fence.
_FENCE_WIDTH = (90.0, 150.0)
_FENCE_OFF_AXIS = 20.0
# THE ORIGIN BAND is set a step SMALLER than the body (10pt against 12pt) —
# the only band of the slip headmatter that is.
_SMALL_STEP = 1.0
# The order form's title, letter-spaced ('O R D E R'), and short.
_TITLE_MAX = 40

# THE DOCKET ROW. ca7 separates consolidated dockets every way it can — a
# comma, an ampersand, the word 'and', and a comma AND an ampersand together
# ('Nos. 23-2434, 23-2450, 23-2479, & 23-2652'). A pattern that allowed only
# ONE separator character rejected that row, and with the docket band
# unidentified the reader withdrew from all five records of that appeal.
_DOCKET_ROW = re.compile(
    r"^Nos?\.\s*\d{2}-\d{3,5}"
    r"(?:[\s,;&]+(?:and\s+)?\d{2}-\d{3,5})*\s*\.?$", re.I)
_TYPED_RULE = re.compile(r"^[_]{4,}$")
_FOLIO = re.compile(r"^[\-–—\s\[\(]*(?:Page\s+)?\d{1,3}[\-–—\s\]\)]*$", re.I)

# ORIGIN OPENERS — how ca7 names the tribunal it is reviewing. A closed
# vocabulary of the court's OWN openers; never a test on the tribunal's name.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "cross-appeals from", "petition for review", "petitions for review",
    "on petition for review", "on petitions for review", "petition for a writ",
    "petition for writ", "on motion for", "motion for leave",
    "application for", "on application for", "on remand from",
    "original proceeding", "on certification from", "certified question",
)
# THE DATE LABELS ca7 prints. Longest first so 'Submitted on briefs' wins
# over 'Submitted'.
_DATE_LABELS = ("argued and submitted", "submitted on briefs", "reargued",
                "resubmitted", "argued", "submitted", "decided", "amended",
                "filed", "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "applicants", "claimant", "claimants", "creditor", "creditors",
    "counter", "cross", "third", "party", "interest", "in", "and", "of",
    "the", "pro", "se", "curiae", "supporting",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# BENCH WORDS that close the origin's naming of the trial judge.
_BENCH = ("Judge", "Judges", "Chief Judge", "Senior Judge", "District Judge",
          "Magistrate Judge", "Bankruptcy Judge", "Circuit Judge",
          "Chief District Judge", "Senior District Judge", "Justice")
# The citation notice ca7 prints under its NONPRECEDENTIAL flag. Not the
# court's words about this case — recorded as a drop, like every notice.
_NOTICE_CUES = ("to be cited only in accordance", "nonprecedential",
                "non-precedential")
_PUBLICATION_FLAG = "nonprecedential disposition"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _markup(line) -> str:
    """The row as the page set it, inline bold/italic kept."""
    from ..resolve.footnotes import line_markup
    return _norm(line_markup(line))


def _unpadded(line):
    """The row with the ORDER FORM's padding spaces taken out.

    ca7 pads its two-column caption with explicit space glyphs and draws
    them right across the gutter — and past it, under the words of the other
    column. Sorted by x, those spaces land BETWEEN the letters they sit
    under and the row reads 'A   p peal from the United States District'.
    A space the page draws underneath a letter is not a word break, so the
    covered ones are dropped; every other glyph, and the row's identity,
    is untouched."""
    from ..pdfio.model import Line
    ink = [(c["x0"], c["x1"]) for c in line.chars
           if (c.get("text") or "").strip()]
    if not ink:
        return line
    keep = []
    for c in line.chars:
        if (c.get("text") or "").strip():
            keep.append(c)
            continue
        mid = (c["x0"] + c["x1"]) / 2
        if any(a < mid < b for a, b in ink):
            continue                        # drawn under a letter
        keep.append(c)
    if len(keep) == len(line.chars):
        return line
    return Line(id=line.id, page=line.page, x0=line.x0, x1=line.x1,
                top=line.top, bottom=line.bottom, chars=keep,
                col=line.col, row=line.row)


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("in the", "united states court of appeals",
                   "for the seventh circuit",
                   "united states court of appeals for the seventh circuit")


def _is_address(text: str) -> bool:
    """The courthouse address the ORDER FORM prints under its banner. A
    letterhead row, matched on its shape — a town, a state, a ZIP."""
    flat = _norm(text)
    toks = flat.rstrip(".").split()
    return (2 <= len(toks) <= 6 and toks[-1].isdigit() and len(toks[-1]) == 5
            and "," in flat)


def _origin_kind(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _joined(rows: list) -> str:
    """Rows joined the way the page wraps them.

    A row broken at a hyphen rejoins WITHOUT it when the continuation opens
    lower-case ('Cir-' / 'cuit Judges.') and WITH it when the continuation
    opens upper-case, because there the hyphen is part of the judge's own
    name ('JACKSON-' / 'AKIWUMI, Circuit Judges.')."""
    out = ""
    for row in rows:
        piece = _norm(row)
        if not piece:
            continue
        if not out:
            out = piece
            continue
        if out.endswith("-"):
            out = (out[:-1] + piece) if piece[:1].islower() else (out + piece)
        else:
            out = f"{out} {piece}"
    return out


def _labelled_dates(text: str) -> dict:
    """{'argued': 'MAY 14, 2026', 'decided': 'JULY 31, 2026'} out of ca7's
    date band ('ARGUED MAY 14, 2026 — DECIDED JULY 31, 2026'), or out of the
    order form's one-label-per-row stack ('Decided April 29, 2026')."""
    if len(text) > 160:
        return {}
    low = text.lower()
    hits = []
    for label in _DATE_LABELS:
        start = 0
        while True:
            at = low.find(label, start)
            if at < 0:
                break
            after = low[at + len(label):at + len(label) + 1]
            if (at == 0 or not low[at - 1].isalnum()) and after not in ("]", ")"):
                hits.append((at, label))
            start = at + len(label)
    if not hits:
        return {}
    hits.sort(key=lambda p: (p[0], -len(p[1])))
    picked: list = []
    for at, label in hits:
        if picked and at < picked[-1][0] + len(picked[-1][1]):
            continue
        picked.append((at, label))
    out: dict = {}
    for i, (at, label) in enumerate(picked):
        end = picked[i + 1][0] if i + 1 < len(picked) else len(text)
        seg = text[at + len(label):end]
        # THE DATE IS TAKEN IN THE FORM THE PAGE SET IT — the comma in
        # 'JULY 31, 2026' is part of the date, so the value is a SLICE of
        # the row and never a re-join of its tokens. ca7 sets the slip's
        # dates in CAPS and the order form's in titlecase; both are read.
        mm = re.search(r"([A-Za-z]{3,}\.?\s+\d{1,2},?\s+\d{4})", seg)
        if mm is None:
            continue
        if mm.group(1).split()[0].strip(".,").lower() not in _MONTHS:
            continue
        out[label.replace(" ", "_")] = _norm(mm.group(1))
    return out


def _is_date_row(text: str) -> bool:
    return bool(_labelled_dates(text)) or bool(
        re.match(r"^[A-Za-z]{3,}\.?\s+\d{1,2},\s+\d{4}\*?$", _norm(text)))


def _panel_names(text: str) -> list:
    """The judges a 'Before …' roster names.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a name test."""
    body = _norm(text)
    for opener in ("before:", "before"):
        if body.lower().startswith(opener):
            body = body[len(opener):]
            break
    names: list = []
    for chunk in body.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*: ").strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX belongs to the judge's name, not to
            # another judge ('THOMAS L. KIRSCH II').
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _roster_row_name(text: str) -> str | None:
    """'FRANK H. EASTERBROOK, Circuit Judge' -> 'FRANK H. EASTERBROOK'.

    The ORDER FORM gives every judge a row and a bench title of their own,
    so the title is the row's terminator and the name is what precedes the
    last comma before it."""
    flat = _norm(text).rstrip(".")
    words = flat.split()
    if len(words) < 2 or words[-1].lower().rstrip(".") not in ("judge",
                                                              "judges"):
        return None
    cut = flat.rfind(",")
    name = (flat[:cut] if cut > 0 else flat).strip(" ,")
    return name or None


def _split_origin(text: str):
    """(forum, lower docket, trial judge) out of ca7's origin.

    'Appeal from the United States District Court for the Northern District
    of Illinois, Eastern Division. No. 1:23-cr-00140 - Franklin U.
    Valderrama, Judge.' - the forum runs to the full stop before the lower
    docket; the docket is the WHOLE 'No(s). ...' run (a consolidated record
    states two: 'Nos. 3:18-cv-00270 & 3:18-cv-00494'); and the judge is the
    clause that ends on a BENCH WORD, which the court sets after an EM DASH
    on the slip and on rows of its own on the order form.

    The dash that opens the judge's clause is the EM dash and only that: a
    hyphen search found the one inside the lower docket itself and named the
    judge 'cr-00140 - Franklin U. Valderrama'."""
    flat = _norm(text)
    docket = judge = None
    forum, tail = flat, None
    mm = re.search(r"(?:^|(?<=[.\s]))(Nos?\.)\s+", flat)
    if mm:
        forum = flat[:mm.start()].strip(" .")
        toks = flat[mm.end():].split()
        take: list = []
        for tok in toks:
            core = tok.strip(",;")
            if core in ("&", "and"):
                take.append(core)
                continue
            if (core[:1].isdigit() and any(c.isdigit() for c in core)
                    and ("-" in core or ":" in core)):
                take.append(core)
                continue
            break
        while take and take[-1] in ("&", "and"):
            take.pop()
        if take:
            docket = f"{mm.group(1)} " + " ".join(take)
            tail = _norm(" ".join(toks[len(take):]))
    jm = re.search(r"[\u2014\u2013]\s*(.+)$", flat)
    if jm:
        tail = _norm(jm.group(1))
    if tail:
        cut = tail.rstrip(".").rsplit(",", 1)
        if len(cut) == 2 and cut[1].strip() in _BENCH:
            judge = cut[0].strip()
    return forum or flat, docket, judge


def _sides(caption_rows: list, one_sided: bool = False):
    """The two party names either side of the pivot.

    Built from the party NAMES — the status labels and the pivot are
    apparatus, and joining the caption wholesale names neither side."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat or _TYPED_RULE.match(flat):
            continue
        first = flat.split()[0].rstrip(".").lower()
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        # A STATUS ROW is a role label, not a party. ca7 HYPHENATES its
        # statuses ('Plaintiffs-Appellees/Cross-Appellants,') where ca4
        # spaces them, so the row is split on the court's own punctuation
        # before the closed role vocabulary is applied. Matched whole, not
        # one of them was recognized and every case name carried its
        # apparatus ('UNITED STATES OF AMERICA, Plaintiff-Appellee v. ...').
        bare = flat.rstrip(",. ").lower()
        words = [w for w in re.split(r"[\s,./;:\u2013\u2014-]+", bare) if w]
        if words and all(w in _STATUS_WORDS for w in words):
            continue
        if flat.lower().startswith(("v.", "vs.")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    # A PARTY NAME MAY WRAP, and ca7 breaks it at a hyphen ('CHICAGO-' /
    # 'OHIO VALLEY …'), so the sides are rejoined the way the page wraps
    # them rather than with a blank between every row.
    if one_sided:
        return _joined(left + right).rstrip(",. ") or None
    if not (left and right and seen_pivot):
        return None
    return (_joined(left).rstrip(",. "), _joined(right).rstrip(",. "))


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------

def _fences(pm) -> list:
    """The tops of the page's typed section fences."""
    out = []
    for line in pm.lines:
        text = line.plain.strip()
        if not _TYPED_RULE.match(text):
            continue
        width = line.x1 - line.x0
        if not (_FENCE_WIDTH[0] <= width <= _FENCE_WIDTH[1]):
            continue
        if abs((line.x0 + line.x1) / 2 - pm.width / 2) > _FENCE_OFF_AXIS:
            continue
        out.append(line.top)
    return sorted(out)


def _order_title(pm):
    """The order form's letter-spaced title row ('O R D E R'), or None."""
    for line in sorted(pm.lines, key=lambda l: l.top):
        text = _norm(line.plain)
        if len(text) > _TITLE_MAX:
            continue
        if "".join(text.split()).upper().rstrip(".") == "ORDER":
            return line
    return None


@decider("headmatter.read", court="ca7")
def read_headmatter_ca7(model, geom, **_):
    """Read ca7's headmatter, or NOTHING.

    NOTHING is returned for anything that is not one of the two contracts
    above: core's shared walk places those rows unidentified, which is a
    smaller error than a confident misreading."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    if len(_fences(page1)) >= 2:
        return _read_typed_rules(model, geom)
    return _read_order_form(model, geom)


def _rows(model, geom, pages: int):
    """(page-model, line) for every content row of the first ``pages``
    pages, in page order, with the page's own furniture stepped over."""
    finder = FurnitureFinder(model, geom.body_x0 if geom else 144.0,
                             geom.body_size if geom else 12.0)
    out = []
    dropped = []
    for pm in model.pages[:pages]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            kind = finder.kind(pm, line)
            if kind or (pm.number > 1 and _FOLIO.match(_norm(line.plain))):
                dropped.append((kind or "folio", pm, line))
                continue
            out.append((pm, line))
    return out, dropped


# ALIGNMENT IS DECLARED BY THE BAND, NOT GUESSED FROM THE ROW. ca7 sets each
# section of its headmatter one way and only one way — the banner, the origin
# and the dates on the page axis, the docket and the roster at the rail (the
# roster with the body's own 18pt first-line indent, which is a paragraph
# opening and not a shift of the row) — so the band that identified the row
# also states how the page placed it. Measured row by row instead, a roster
# line whose midpoint happens to land within 8pt of the axis reads as
# centred and a centred origin row that fills 91% of the measure reads as
# flush left; both were doing exactly that.
#
# The CAPTION is the one band that mixes all three, and there the row is
# measured: the party names sit at the rail, the pivot on the axis, and the
# party STATUS flush to the measure's right edge ('Plaintiff-Appellee,' and
# 'Counter-Defendants, Appellees/Cross-Appellants.' both end at 468).
_STATUS_MAX = 0.85          # a flush-right status row is short of the measure
_CENTER_MAX = 0.60          # …and so is the pivot
_EDGE = 3.0
_AXIS = 8.0


def _caption_align(line, pm, geom) -> str:
    rail = geom.body_x0 if geom else 72.0
    right = geom.right_x1 if geom else (pm.width - rail)
    span = right - rail
    width = line.x1 - line.x0
    if span <= 0 or line.x0 <= rail + 12:
        return "L"
    if abs(line.x1 - right) <= _EDGE and width <= _STATUS_MAX * span:
        return "R"
    if (abs((line.x0 + line.x1) / 2 - pm.width / 2) <= _AXIS
            and width <= _CENTER_MAX * span):
        return "C"
    return "L"


class _Emitter:
    """Rows out, tagged, with every claimed line accounted for."""

    def __init__(self, geom):
        self.geom = geom
        self.items: list = []
        self.consumed: set[int] = set()

    def line(self, pm, line, role: str, align: str = ""):
        if not align:
            align = _caption_align(line, pm, self.geom)
        self.items.append(m.HmLine(
            text=_markup(line), prov=m.Prov(pm.number, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(getattr(line, "all_bold", False)), rel=0.0, role=role))
        self.consumed.add(line.id)

    def rule(self, pm, line, span: str = "full"):
        self.items.append(m.Rule(prov=m.Prov(pm.number, (line.id,)),
                                 typed=True, span=span))
        self.consumed.add(line.id)


# --------------------------------------------------------------------------
# STYLE 'typed rules' — the slip opinion
# --------------------------------------------------------------------------

def _read_typed_rules(model, geom):
    rows, _furniture = _rows(model, geom, 4)
    if not rows:
        return NOTHING
    body_size = geom.body_size if geom else 12.0

    def is_fence(pm, line) -> bool:
        text = line.plain.strip()
        if not _TYPED_RULE.match(text):
            return False
        width = line.x1 - line.x0
        return (_FENCE_WIDTH[0] <= width <= _FENCE_WIDTH[1]
                and abs((line.x0 + line.x1) / 2 - pm.width / 2)
                <= _FENCE_OFF_AXIS)

    # ---- bands, split at the fences -------------------------------------
    bands: list = [[]]
    fence_rows: list = []
    for pm, line in rows:
        if is_fence(pm, line):
            fence_rows.append((pm, line))
            bands.append([])
        else:
            bands[-1].append((pm, line))
    if len(fence_rows) < 2:
        return NOTHING
    # The banner must open the block — ca7 always names itself first.
    if not bands[0] or not all(_is_banner(l.plain) for _, l in bands[0]):
        return NOTHING

    # ---- what each band is ----------------------------------------------
    kinds: list = []
    seen_caption = False
    for i, band in enumerate(bands):
        texts = [_norm(l.plain) for _, l in band]
        head = texts[0] if texts else ""
        sizes = [l.size or body_size for _, l in band]
        if i == 0:
            kind = "court"
        elif not band:
            kind = "empty"
        elif i == len(bands) - 1:
            kind = "tail"                    # the only UNFENCED region
        elif _DOCKET_ROW.match(head):
            kind = "docket"
            seen_caption = True
        elif sizes and max(sizes) <= body_size - _SMALL_STEP:
            # THE STEP DOWN IS THE ORIGIN. ca7 sets exactly one band of its
            # headmatter below the body size, and it is always the statement
            # of where the case came from — read by measurement, so a forum
            # this court has never reviewed before still lands correctly.
            kind = "lower-court"
        elif any(_labelled_dates(t) for t in texts):
            kind = "date"
        elif _origin_kind(head):
            kind = "lower-court"
        elif seen_caption:
            # A CONSOLIDATED RECORD REPEATS THE CAPTION WITHOUT REPEATING
            # THE DOCKET (terry_ferguson prints the direct appeal's caption
            # and the § 2255 caption under one docket row).
            kind = "caption"
        else:
            return NOTHING                   # not this contract
        kinds.append(kind)

    # ---- where the reader stops -----------------------------------------
    # Below the last fence the court prints the roster and then the writing.
    # The roster is bounded by ca7's own punctuation: it ends on a full stop
    # and its wraps do not.
    tail = list(bands[-1])
    roster: list = []
    if tail and _norm(tail[0][1].plain).lower().startswith("before"):
        for pm, line in tail:
            roster.append((pm, line))
            if _norm(line.plain).rstrip().endswith((".", ":")):
                break
        else:
            roster = []                      # never terminated — not a roster
    bands[-1] = roster
    if "docket" not in kinds and "caption" not in kinds:
        return NOTHING

    # ---- emit ------------------------------------------------------------
    out = _Emitter(geom)
    crit: dict = {"headmatter_style": STYLE_TYPED_RULES}
    banner_rows: list = []
    caption_rows: list = []
    lead_caption: list = []
    origin_bands: list = []
    roster_rows: list = []
    dates: dict = {}

    fi = 0
    for i, (band, kind) in enumerate(zip(bands, kinds)):
        for pm, line in band:
            text = _norm(line.plain)
            if kind == "court":
                if text.lower() != "in the":
                    banner_rows.append(text)
                out.line(pm, line, "court", "C")
            elif kind == "docket":
                if _DOCKET_ROW.match(text):
                    if not crit.get("docket_number"):
                        crit["docket_number"] = text.rstrip(".")
                    else:
                        crit.setdefault("other_dockets", []).append(text)
                    out.line(pm, line, "docket", "L")
                else:
                    caption_rows.append(text)
                    if not origin_bands:
                        lead_caption.append(text)
                    out.line(pm, line, "caption")
            elif kind == "caption":
                if _TYPED_RULE.match(text):
                    # The court's own divider between two consolidated
                    # captions — a rule, not a row.
                    out.rule(pm, line)
                    continue
                caption_rows.append(text)
                out.line(pm, line, "caption")
            elif kind == "lower-court":
                if not origin_bands or origin_bands[-1][0] is not band:
                    origin_bands.append((band, []))
                origin_bands[-1][1].append(text)
                out.line(pm, line, "lower-court", "C")
            elif kind == "date":
                dates.update(_labelled_dates(text))
                out.line(pm, line, "date", "C")
            elif kind == "tail":
                roster_rows.append(text)
                out.line(pm, line, "panel", "L")
        # THE FENCE ITSELF RENDERS. It is not furniture — it is the court's
        # own section mark, and a total claim silences core's shared walk,
        # which is what would otherwise have drawn it.
        if fi < len(fence_rows) and i < len(bands) - 1:
            pm, line = fence_rows[fi]
            out.rule(pm, line)
            fi += 1

    if banner_rows:
        crit["court"] = _joined(banner_rows)
    if caption_rows:
        crit["caption"] = caption_rows
        _apply_parties(crit, lead_caption or caption_rows)
    for n, (_band, texts) in enumerate(origin_bands):
        printed = _joined(texts)
        _forum, lower_docket, judge = _split_origin(printed)
        if n == 0:
            crit["lower_court"] = printed
            if judge:
                crit["lower_court_judge"] = judge
        if lower_docket:
            crit.setdefault("other_dockets", []).append(lower_docket)
    if roster_rows:
        printed = _joined(roster_rows)
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    _apply_dates(crit, dates)

    # THE PAGE'S FURNITURE IS NOT CLAIMED. The reader steps over the running
    # head and the folio rather than consuming them, so core's own sweep
    # measures and records them once, where every other court's are recorded.
    return {"criteria": crit, "items": out.items, "attorneys": [],
            "dropped": [], "consumed": out.consumed, "anchor_ids": [],
            "doc_type_final": None}


# --------------------------------------------------------------------------
# STYLE 'order form' — the courthouse letterhead
# --------------------------------------------------------------------------

def _read_order_form(model, geom):
    page1 = model.pages[0]
    title = _order_title(page1)
    if title is None:
        return NOTHING
    rows = [(page1, l) for l in sorted(page1.lines, key=lambda l: (l.top, l.x0))
            if l.plain.strip() and l.top < title.top]
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for _, l in rows[:6]):
        return NOTHING
    if not any(_is_address(l.plain) for _, l in rows[:8]):
        return NOTHING                      # not the letterhead

    # ---- the zones, in the court's fixed order ---------------------------
    docket_at = next((i for i, (_p, l) in enumerate(rows)
                      if _DOCKET_ROW.match(_norm(l.plain))), None)
    if docket_at is None:
        return NOTHING
    head, caption = rows[:docket_at + 1], rows[docket_at + 1:]

    out = _Emitter(geom)
    crit: dict = {"headmatter_style": STYLE_ORDER_FORM}
    dropped: list = []
    banner_rows: list = []
    roster_rows: list = []
    notice: list = []
    dates: dict = {}
    state = "court"
    for pm, line in head:
        text = _norm(line.plain)
        low = text.lower()
        if any(cue in low for cue in _NOTICE_CUES) \
                and low.strip(" .*") != _PUBLICATION_FLAG:
            notice.append((pm, line))
            continue
        if low.strip(" .*") == _PUBLICATION_FLAG:
            crit.setdefault("publication_status", "unpublished")
            crit.setdefault("title", text)
            out.line(pm, line, "court", "C")
            continue
        if _DOCKET_ROW.match(text):
            crit["docket_number"] = text.rstrip(".")
            out.line(pm, line, "docket", "L")
            continue
        if state == "panel" or low.rstrip(":") == "before":
            state = "panel"
            roster_rows.append(text)
            out.line(pm, line, "panel", "C")
            continue
        if _is_date_row(text):
            dates.update(_labelled_dates(text) or {"filed": text.rstrip("*")})
            state = "date"
            out.line(pm, line, "date", "C")
            continue
        if _is_banner(text) or _is_address(text):
            banner_rows.append(text)
            out.line(pm, line, "court", "C")
            continue
        return NOTHING                       # an unread row is not a claim

    # ---- the two-column caption -----------------------------------------
    block = _caption_block(page1, caption, geom, out)
    if block is None:
        return NOTHING

    left_rows, right_rows = block
    if banner_rows:
        crit["court"] = _joined([t for t in banner_rows
                                 if not _is_address(t)])
    if roster_rows:
        printed = _joined(roster_rows)
        crit["panel_line"] = printed
        crit["judges"] = printed[len("Before"):].lstrip(": ") \
            if printed.lower().startswith("before") else printed
        # ONE JUDGE PER ROW: the bench title closes each row, so the roster
        # is read row by row and not by splitting the whole list on commas
        # (which gave the panel one judge and two orphaned titles).
        names = [n for n in (_roster_row_name(t) for t in roster_rows) if n]
        if not names:
            names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if left_rows:
        crit["caption"] = left_rows
        _apply_parties(crit, left_rows)
    if right_rows:
        printed = _joined(right_rows)
        crit["lower_court"] = printed
        _forum, lower_docket, judge = _split_origin(printed)
        if lower_docket:
            crit.setdefault("other_dockets", []).append(lower_docket)
        if judge:
            crit["lower_court_judge"] = judge
    _apply_dates(crit, dates)

    if notice:
        dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for _p, l in notice))[:1200],
            prov=m.Prov(notice[0][0].number, tuple(l.id for _p, l in notice)),
            kind="notice"))
        out.consumed.update(l.id for _p, l in notice)

    # A NONPRECEDENTIAL DISPOSITION is the court's decision of the appeal —
    # the paper is an opinion, whatever its title says.
    final = None
    if crit.get("publication_status") == "unpublished":
        final = m.DocType.OPINION
    return {"criteria": crit, "items": out.items, "attorneys": [],
            "dropped": dropped, "consumed": out.consumed, "anchor_ids": [],
            "doc_type_final": final}


def _caption_block(pm, rows: list, geom, out: _Emitter):
    """ca7's order-form caption, split at its MEASURED gutter.

    The two columns are held apart by whitespace alone, so the gutter is the
    widest column of the caption band that no glyph occupies ON ANY ROW —
    measured per row and intersected, because measured as one union over the
    band it disappears (the left column's longest row and the right column's
    rows together tile the width). Never invented: where no such column
    exists this is not a two-column caption and nothing is split."""
    if not rows:
        return None
    chars = [c for _p, l in rows for c in l.chars
             if (c.get("text") or "").strip()]
    if not chars:
        return None
    left = min(c["x0"] for c in chars)
    right = max(c["x1"] for c in chars)
    by_row: dict = {}
    for _p, line in rows:
        for c in line.chars:
            if (c.get("text") or "").strip():
                by_row.setdefault(round(line.top / 3.0), []).append(c)
    empty = [(left, right)]
    for cells in by_row.values():
        spans = sorted((c["x0"], c["x1"]) for c in cells)
        holes, reach = [], spans[0][1]
        if spans[0][0] > left:
            holes.append((left, spans[0][0]))
        for x0, x1 in spans:
            if x0 > reach:
                holes.append((reach, x0))
            reach = max(reach, x1)
        if reach < right:
            holes.append((reach, right))
        empty = [(max(a0, b0), min(a1, b1))
                 for a0, a1 in empty for b0, b1 in holes
                 if min(a1, b1) - max(a0, b0) > 0]
        if not empty:
            return None
    gap_at, gap_w = None, 0.0
    for x0, x1 in empty:
        if x1 - x0 > gap_w:
            gap_w, gap_at = x1 - x0, (x0 + x1) / 2.0
    # A GUTTER, NOT AN INDENT: wider than the deepest indent the caption
    # itself uses, with text on both sides of it.
    if gap_at is None or gap_w < 12.0:
        return None
    if gap_at - left < 60.0 or right - gap_at < 60.0:
        return None

    visual: list = []
    for _p, line in rows:
        if visual and abs(visual[-1][0] - line.top) <= 2:
            visual[-1][1].append(line)
        else:
            visual.append((line.top, [line]))
    lefts: list = []
    rights: list = []
    left_text: list = []
    right_text: list = []
    ids: list = []

    def cell(cells: list, role: str):
        # A CELL IS PLACED BY ITS COLUMN, not by an offset: the renderer
        # stacks each side in its own column, and an offset there translates
        # the whole row — tint and all — out past the column's right edge.
        joined = "  ".join(_markup(_unpadded(c))
                           for c in sorted(cells, key=lambda l: l.x0))
        first = sorted(cells, key=lambda l: l.x0)[0]
        ids.extend(c.id for c in cells)
        return m.HmLine(text=joined, prov=m.Prov(
            pm.number, tuple(c.id for c in cells)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(getattr(c, "all_bold", False)) for c in cells),
            rel=0.0, role=role)

    for _top, cells in visual:
        l_cells = [c for c in cells if (c.x0 + c.x1) / 2 < gap_at]
        r_cells = [c for c in cells if (c.x0 + c.x1) / 2 >= gap_at]
        # A PAD is not a row of the page — it is the spacer that keeps the
        # two stacks on the same baselines, so it carries no role.
        lefts.append(cell(l_cells, "caption") if l_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number)))
        rights.append(cell(r_cells, "lower-court") if r_cells
                      else m.HmLine(text="", prov=m.Prov(pm.number)))
        if l_cells:
            left_text.append(_norm(" ".join(
                _unpadded(c).plain
                for c in sorted(l_cells, key=lambda l: l.x0))))
        if r_cells:
            right_text.append(_norm(" ".join(
                _unpadded(c).plain
                for c in sorted(r_cells, key=lambda l: l.x0))))
    if not left_text or not right_text:
        return None
    # A PAD BELOW THE LAST CELL OF ITS SIDE HOLDS NOTHING IN LINE. The two
    # stacks are padded so their rows share baselines; once one side has run
    # out, its remaining pads are blank rows under the block and nothing
    # else (the order form's caption runs four rows longer on the left).
    for side in (lefts, rights):
        while side and not side[-1].text:
            side.pop()
    out.items.append(m.CaptionBlock(
        left=lefts, right=rights, rail=None, rail_rows=len(lefts),
        style_id=STYLE_ORDER_FORM, fp={"mid_x": gap_at},
        prov=m.Prov(pm.number, tuple(sorted(ids)))))
    out.consumed.update(ids)
    return left_text, right_text


# --------------------------------------------------------------------------
# shared publication
# --------------------------------------------------------------------------

def _apply_parties(crit: dict, caption_rows: list) -> None:
    sides = _sides(caption_rows)
    if sides:
        crit["parties"] = list(sides)
        crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        return
    # A ONE-SIDED caption is still a caption ('IN RE: STEPHEN FALKNER').
    one = _sides(caption_rows, one_sided=True)
    if one:
        crit["parties"] = [one]
        crit["case_name"] = one


def _apply_dates(crit: dict, dates: dict) -> None:
    for label in ("decided", "amended", "filed", "entered"):
        if dates.get(label) and not crit.get("decision_date"):
            crit["decision_date"] = dates[label]
    for label in ("submitted", "submitted_on_briefs", "resubmitted",
                  "argued", "argued_and_submitted", "reargued"):
        if dates.get(label) and not crit.get("submitted"):
            crit["submitted"] = dates[label]
