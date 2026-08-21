"""Court of Appeals of the State of Idaho ('idahoctapp').

Everything unique to idahoctapp lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is already
registered in `courts/__init__.py` — this module binds the reader only and
reads the byline grammar off the registry, so the two can never drift.

THE PUBLISHER IS THE SAME AS idaho's — the Idaho Supreme Court's clerk sets
both benches' slips on one piece of stationery — but the intermediate
court's paper is NOT the same paper, and three of its facts are its own:
the caption's right column carries a PUBLICATION NOTICE, the dockets are
CONSOLIDATED as a matter of routine, and most of these opinions are signed
by a single judge with no panel roster at all.

THE CONTRACT — 'paren-rail slip' (30 of 30). The caption's divider is a
TYPED COLUMN of ')' glyphs, measured per record at x 297.3-311.6 on a 612pt
page, and the caption is CLOSED by a DRAWN rule of HALF the body measure
(224.8-235.7pt, left-anchored at x0 71.3-72.0):

    IN THE COURT OF APPEALS OF THE STATE OF IDAHO   the banner, 12pt, centred
              Docket Nos. 51941, 51942 & 51943      the dockets, centred
     ANGELA MICHELLE GREEN,          )              the caption:
                                     )   Filed: July 31, 2026
            Petitioner-Appellant,    )   Melanie Gagnepain, Clerk
     v.                              )   THIS IS AN UNPUBLISHED
     STATE OF IDAHO,                 )   OPINION AND SHALL NOT
                                     )   BE CITED AS AUTHORITY
            Respondent.              )
    ______________________________)                the caption's DRAWN fence
        Appeal from the District Court of the First …    the origin
        Judgments summarily dismissing … relief, affirmed.   the outcome
        Angela Michelle Green, Boise, pro se appellant.      the bar
        Hon. Raúl R. Labrador, Attorney General; …
        ________________________________________            a TYPED rule
    MELANSON, Judge Pro Tem                                 the byline

    A record that types no ')' column is not this paper and the reader
    returns NOTHING: core's shared walk places those rows unidentified,
    which is a smaller error than a confident misreading.

THE TWO STACKS ARE NOT ROW-PAIRED. The court sets the party list on the
EVEN rows of a 13.8pt grid and the right column's facts on the ODD ones —
green's five party cells and five right-hand cells share only one baseline
out of ten — so a row pairing would pad each column with five phantom
blank cells. The right column is one independent block of facts about the
PAPER (when it was filed, who filed it, whether it may be cited) set
beside a party list of any length, exactly as illappct's origin column is,
and each column is collected on its own for the renderer to flow.

THE RAIL IS READ GLYPH BY GLYPH, never piece by piece. pdfio breaks a
caption baseline at its column gaps, and how many pieces come back is an
accident of how wide the gap happened to be: the same corpus hands back
`STATE OF IDAHO, DEPARTMENT OF ) Filed:  July 8, 2026` as ONE piece
(in_the_interest_of_john_doe), `ALLEGHENY CASUALTY COMPANY )` as one and
the rail alone as another. Membership is a glyph's own x against the
measured column — which is also what keeps the ')' closing
`Juvenile Under Eighteen (18) Years of Age.` in the party column where the
court set it, 150pt left of the rail.

THE FENCE INSIDE THE CAPTION IS A CASE DIVIDER, and the court draws it or
types it interchangeably. `state_v._john_doe` DRAWS a 235pt rule under the
juvenile's name; `rugged_rentals` TYPES the same divider as a run of
underscores in the left column between its complaint and its
cross-complaint. Both cut the caption into the cases it holds, and both
render as the rule the page shows.

THE DOCKETS ARE CONSOLIDATED AS A MATTER OF ROUTINE, and the court sets
them four ways — `Docket No. 51538`, `Docket Nos. 52430 & 52431`,
`Docket Nos. 51328/51329`, `Docket Nos. 51941, 51942 & 51943`. The first
is `docket_number`; the rest are `other_dockets`, which is where companion
APPEALS belong (a trial-court number would be `lower_court_docket`).

THE PUBLICATION NOTICE IS A FACT, NOT FURNITURE. Six records set
`THIS IS AN UNPUBLISHED / OPINION AND SHALL NOT / BE CITED AS AUTHORITY`
in the right column under the clerk. It is read as `publication` and left
where the page put it — dropping it as furniture would lose the court's own
statement of its paper's authority, and fusing it into the date row would
lose both. Its presence sets `publication_status`; its ABSENCE sets
nothing, because the court prints no counter-notice and 'Opinion Filed:'
versus 'Filed:' does not separate the two (cheng_yang files 'Filed:' and
carries no notice).

MOST OF THESE OPINIONS HAVE NO PANEL AND SOME HAVE NO AUTHOR. One judge
signs `LORELLO, Judge` / `TRIBE, Chief Judge` / `MELANSON, Judge Pro Tem`
with no roster; the per curiam affirmances print the roster instead, fenced
by a TYPED rule on each side (`Before TRIBE, Chief Judge; LORELLO Judge; /
and FLEMING, Judge`), and sign `PER CURIAM`. Authorless is not a defect
here and the reader never invents one.

WHERE THE READER STOPS. At the BODY RAIL. The court sets every block of
front matter one indent step (36pt) inside the rail at x=108 and signs
every writing AT it at x=72, so the floor is measured rather than parsed —
which is what ends the block on `MELANSON, Judge Pro Tem`, a byline whose
grammar core learned only because idahoctapp declared it. Everything at or
left of the rail below the caption is the writing's, and the reader does
not touch it.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder, is_folio_text
from . import get_profile

# The profile is NOT registered here — `courts/__init__.py` already holds
# it, and registering a second one raises. Look it up so the byline grammar
# the reader stops on is the one assembly signs with.
IDAHOCTAPP = get_profile("idahoctapp")

STYLE_PAREN_RAIL = "paren-rail slip"

# ---- idahoctapp's declared facts (measured over the 30-record corpus) ----
# THE PAREN RAIL. ')' occurs in ordinary prose — every one of these records
# cites a statute — so a divider has to be a COLUMN of them. Measured here
# the shortest column runs 10 glyphs and the tallest 41; six is the floor
# ca6's paren slip established and it is kept.
_RAIL_GLYPH = ")"
_RAIL_FLOOR = 6
# The rail's x is a PER-RECORD measurement, never a threshold: 297.3, 298.1,
# 298.4, 298.6, 302.1, 302.2, 302.3, 302.6, 302.8, 303.2, 306.8, 307.6 and
# 311.6 all occur. Within one document it varies by 0.1pt.
_RAIL_TOL = 3.0
# A glyph belongs to the rail when it stands in the rail's own column. The
# nearest other ink on those rows is 8pt away, so 6pt reaches the rail and
# nothing else.
_RAIL_WINDOW = 6.0
# A RAIL IS A CONTIGUOUS COLUMN. The court stacks its glyphs at 13.8pt and
# skips at most one caption row, so three leadings end the run — and a ')'
# that ordinary prose sets at the same x 200pt further down the page opens a
# run of its own instead of stretching the caption to the page foot.
_RAIL_RUN_GAP = 45.0
# THE CAPTION FENCE: a DRAWN rule of HALF the body measure anchored on the
# left margin — 224.8 to 235.7pt at x0 71.3-72.0. It closes the caption and
# repeats between the cases a consolidated caption holds. The court's other
# rules are a different measure entirely: the disposition's own underlines
# run 36.5-150.1pt at x0 108-459, and the footnote separator is 144pt.
_FENCE_W = (200.0, 275.0)
_FENCE_X0_MAX = 110.0
# HOW FAR A BLOCK WRAPS. The origin / outcome / appearances blocks are set
# at 13.8pt leading and separated by 27.6 — nothing in between anywhere in
# the corpus — so 16 takes a wrap and never a new rung.
_BLOCK_LEAD_MAX = 16.0
# WHERE THE FRONT MATTER SITS: one indent step (36pt) inside the body rail,
# everywhere below the caption. Half a step reaches every block and never
# the byline, which is AT the rail.
_INDENT_MIN = 18.0
# A block may WRAP THE PAGE: rugged_rentals finishes its appearances, types
# its rule and signs on page 2.
_TOP_BAND = 0.20
# How far the front matter may run. The longest caption in the corpus
# (tracy_allen: fourteen parties) still closes on page 1 and its ladder
# closes on page 2; three pages is slack.
_MAX_PAGES = 3
# THE FOOT the court prints on every page: a bare folio, centred, at 0.90
# of the sheet and below.
_FOOT_BAND = 0.90

# THE ORIGIN, as the court names what it is reviewing. A closed set of
# openers, applied only BELOW the caption.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "appeal of", "cross-appeal from",
    "cross-appeals from", "on appeal from", "petition for review",
    "on petition for review", "review of", "original proceeding",
)
# THE OUTCOME the court states under the origin. Its vocabulary is the
# closed set of dispositive participles; every other word in the block is
# the name of a paper or a court.
_OUTCOME_WORDS = (
    "affirmed", "reversed", "vacated", "remanded", "dismissed", "denied",
    "granted", "modified", "withdrawn", "sustained", "quashed", "released",
    "set aside", "annulled", "revoked", "disqualified", "suspended",
)
# THE COURT'S OWN NUMBER, set above the caption.
_DOCKET_PREFIXES = ("docket no", "docket nos", "case no", "case nos")
# THE FILING ROW: 'Filed:  July 31, 2026' / 'Opinion Filed:  June 11, 2026'.
_FILED_OPENERS = ("filed", "opinion filed", "order filed", "opinion issued",
                  "amended opinion filed", "substitute opinion filed")
# THE PUBLICATION NOTICE the court sets in the right column, in caps, over
# three rows. Two cues open it; nothing but its own caps carries it on.
_NOTICE_OPENERS = ("this is an unpublished", "this opinion is unpublished",
                   "this is an unpublished opinion", "not for publication")
# THE ROSTER, where the court prints one — the only labelled block on the
# page, and the only one the court fences on BOTH sides.
_PANEL_OPENER = "before"
# A TYPED RULE: the court's own section mark, a run of underscores alone on
# its row (48 of them at x0 162 or 180).
_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
_RULE_CHARS = set("_-–— ")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. The court hyphenates its compound roles and breaks them across
# rows ('Plaintiff-Counterdefendant-' / 'Appellant,').
_STATUS_WORDS = frozenset({
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant", "applicants",
    "counterclaimant", "counterclaimants", "counterdefendant",
    "counterdefendants", "crossclaimant", "crossclaimants",
    "crossdefendant", "crossdefendants", "counterclaim", "counter",
    "cross", "third", "party", "parties", "interest", "real", "juvenile",
    "juveniles", "child", "children", "surety", "employer",
    "in", "of", "and", "the", "pro", "se",
})


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_banner(text: str) -> bool:
    """The court naming itself. Read on the words that name a court of this
    state, not on which bench — and only ever ABOVE the caption band, which
    is what keeps 'Appeal from the District Court … State of Idaho' out."""
    low = _norm(text).lower()
    return ("court" in low and "idaho" in low
            and ("appeals" in low or "supreme" in low)
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
    """Does this block STATE THE COURT'S ACTION? The court writes it as a
    sentence naming the paper below and what became of it ('Judgment of
    conviction, affirmed and case remanded in part.'), and the participle
    may sit on the block's second row ('… vacated and' / 'case remanded.'),
    so the test is the closed participle vocabulary over the WHOLE block."""
    return _OUTCOME_RE.search(_norm(text).lower()) is not None


def _is_panel(text: str) -> bool:
    return _norm(text).lower().startswith(_PANEL_OPENER + " ")


def _is_foot(pm, line) -> bool:
    """The court's page foot: a bare folio, centred at the page bottom."""
    if line.top / (pm.height or 792.0) < _FOOT_BAND:
        return False
    return is_folio_text(_norm(line.plain))


# --------------------------------------------------------------------------
# the divider — the paper's only caption contract, and the dispatch
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


def _rail(pm) -> dict | None:
    """The ')' divider on ``pm``: {'x','top','bottom'}, or None.

    A rail is a COLUMN — glyphs stacked at one measured x — and a
    CONTIGUOUS one. The modal column alone is not enough: ordinary prose
    200pt below the caption sets a ')' within a point of the rail's own x,
    and taken into the stack it carries the caption's foot to the bottom of
    the page."""
    chars = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == _RAIL_GLYPH]
    if len(chars) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    at_x = float(x)
    stack = [c for c in chars if abs(c["x0"] - at_x) <= _RAIL_TOL]
    if not stack:
        return None
    run = max(_runs(stack), key=len)
    if len(run) < _RAIL_FLOOR:
        return None
    return {"x": at_x, "top": min(c["top"] for c in run),
            "bottom": max(c["bottom"] for c in run)}


def _fences(pm) -> list:
    """Tops of the caption fence — the half-measure rule the court closes
    its caption with, and repeats between the cases it holds."""
    return sorted(r.top for r in pm.h_rules
                  if _FENCE_W[0] <= r.width <= _FENCE_W[1]
                  and r.x0 <= _FENCE_X0_MAX)


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, rail_x: float, want: str):
    """The part of ``line`` on one side of the rail, the rail's own glyphs
    shed, or None.

    Split GLYPH BY GLYPH. Whether pdfio already broke a caption baseline at
    its column gap is an accident of how wide the gap happened to be, and a
    whole-piece test puts the rail — and the cell fused to it — in one
    column or the other by luck."""
    keep = []
    for c in line.chars:
        t = c.get("text") or ""
        if t == _RAIL_GLYPH and abs(c["x0"] - rail_x) <= _RAIL_WINDOW:
            continue
        mid = (c["x0"] + c.get("x1", c["x0"])) / 2.0
        if (mid < rail_x) == (want == "L"):
            keep.append(c)
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _unfence(line, fence_tops: list):
    """``line`` with any underline the CAPTION FENCE put on it cleared.

    A drawn rule whose ends coincide with the row above is an underline; a
    226pt rule anchored on the left margin under a status label set at x=113
    is not. pdfio tags by vertical proximity alone, so the caption's closing
    fence arrives as an underline on whatever row it happens to follow. The
    fence is structure — it renders as the rule the page drew, once."""
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
        if set(flat) <= _RULE_CHARS and len(flat) >= 3:
            continue          # the court's own typed divider, not a name
        bare = flat.rstrip(",.; ").lower()
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            continue
        side.append(flat)
    # THE COMMA is the caption's own apparatus, leading to the status row
    # under it; the FULL STOP is not — it ends the abbreviation a party is
    # incorporated under ('BISTLINE LAW, PLLC.').
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the origin's own judge
# --------------------------------------------------------------------------

# WHO TRIED IT, as the origin statement names them. 'Hon.' is the landmark
# the court prints before every one of them, and the BENCH TITLE that
# follows a comma-run of names applies to all of them:
#   'Hon. Darren B. Simpson, District Judge.'
#   'Hon. Sunil Ramalingam, Magistrate.'
#   'Hon. Stephen S. Dunn, Senior District Judge.'
#   'Hon. Cynthia K.C. Meyer, Hon. Scott Wayman, and Hon. Barbara
#    Buchanan, District Judges.'
_HON = re.compile(r"Hon\.\s+([A-Z][A-Za-z’'.\-]*"
                  r"(?:\s+[A-Z][A-Za-z’'.\-]*)*)")
_BENCH = re.compile(
    r"\b((?:Senior|Chief|Acting|Presiding|Special)\s+)?"
    r"((?:District|Magistrate|Supreme\s+Court)\s+)?"
    r"(Judges?|Magistrates?)(\s+Pro\s+Tem(?:pore)?)?\b")
_BENCH_PLURAL = re.compile(r"\b(Judge|Magistrate)s\b")


def _trial_judges(text: str) -> str | None:
    flat = _norm(text)
    names = [(mm.group(1).rstrip(".,;"), mm.end()) for mm in _HON.finditer(flat)]
    if not names:
        return None
    titles = [(mm.start(), _norm(mm.group(0))) for mm in _BENCH.finditer(flat)]
    found: list = []
    shared = Counter()
    for name, end in names:
        title = next((t for pos, t in titles if pos >= end), None)
        shared[title] += 1
        found.append((name, title))
    out: list = []
    for name, title in found:
        if title is None:
            entry = name
        else:
            # One title over several names is printed plural; each judge
            # holds it singly.
            printed = _BENCH_PLURAL.sub(r"\1", title) \
                if shared[title] > 1 else title
            entry = f"{name}, {printed}"
        if entry not in out:
            out.append(entry)
    return "; ".join(out) if out else None


def _panel_names(text: str) -> list:
    """'Before TRIBE, Chief Judge; LORELLO Judge; and FLEMING, Judge' — the
    roster as the court prints it, one judge per entry."""
    flat = _norm(text)
    flat = re.sub(r"^[Bb]efore\s+", "", flat).rstrip(".")
    out: list = []
    for piece in re.split(r";|\band\b", flat):
        entry = _norm(piece).strip(",; ")
        if entry:
            out.append(entry)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="idahoctapp")
def read_headmatter_idahoctapp(model, geom, **_):
    """Read idahoctapp's paren-railed slip, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _rail(page1)
    if rail is None:
        return NOTHING              # no ')' column: not this paper

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    parser = BylineParser(IDAHOCTAPP.byline)
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE ROWS the reader may see, and the FURNITURE it inherits by
    # claiming the region: the bare centred folio at the page foot.
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

    # THE CAPTION BAND: the rail's own vertical span, closed by the DRAWN
    # fence under it, and by the origin statement whatever the rail does —
    # the origin is the first landmark of the block below and no caption row
    # ever stands under it.
    fs = _fences(page1)
    close = [t for t in fs if t >= rail["bottom"] - 2]
    bottom = close[0] if close else rail["bottom"] + 6.0
    origin = [l.top for l in rows
              if l.page == 1 and l.top > rail["top"] and _origin_opener(l.plain)]
    if origin:
        bottom = min(bottom, origin[0] - 4.0)
    band = (rail["top"] - 6.0, bottom)
    fence_tops = [t for t in fs if rail["top"] < t <= bottom]

    crit: dict = {"headmatter_style": STYLE_PAREN_RAIL}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    banner_rows: list = []
    caption_rows: list = []
    origin_rows: list = []
    outcome_rows: list = []
    counsel_rows: list = []
    panel_rows: list = []
    parties: list = []
    case_name: str | None = None
    dockets: list = []

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

    def hmline(parts: list, role: str, align: str = "L",
               rel_from: float | None = None) -> m.HmLine:
        """One HEADMATTER ROW, from the one or more line objects the page set
        on that baseline. pdfio splits a row at its column gaps, and a
        justified counsel row can arrive in three pieces."""
        parts = sorted(parts, key=lambda l: l.x0)
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
        consumed.update(p.id for p in parts)
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), rel=rel, role=role)

    def emit(parts: list, role: str, align: str = "L",
             rel_from: float | None = None) -> None:
        items.append(hmline(parts, role, align, rel_from))

    # ---- the masthead: everything page 1 prints above the caption -------
    for row in visual([l for l in rows if l.page == 1 and l.top < band[0]]):
        text = _norm(" ".join(l.plain for l in sorted(row, key=lambda l: l.x0)))
        low = text.lower()
        if _is_banner(text):
            banner_rows.append(text)
            emit(row, "court", align="C")
        elif low.startswith(_DOCKET_PREFIXES):
            # THE COURT'S OWN NUMBERS, which this court sets above the
            # caption rather than beside it, and consolidates as a matter of
            # routine: 'Docket Nos. 51941, 51942 & 51943',
            # 'Docket Nos. 51328/51329', 'Docket Nos. 52430 & 52431'.
            body = re.sub(r"^\s*(?:supreme\s+court\s+)?"
                          r"(?:docket|case)\s+nos?\.?\s*", "", text,
                          flags=re.I)
            for piece in re.split(r"[,/&]|\band\b", body):
                num = _norm(piece).strip(".,;& ")
                if num and num not in dockets:
                    dockets.append(num)
            emit(row, "docket", align="C")
        else:
            # Named neither, and still the court's own front matter: the row
            # is kept where the page put it and marked as what it is.
            emit(row, "case-info", align="C")

    # ---- the caption ----------------------------------------------------
    band_lines = [l for l in rows if l.page == 1 and band[0] <= l.top <= band[1]]
    band_rows = [[_unfence(l, fence_tops) for l in row]
                 for row in visual(band_lines)]
    rail_x = rail["x"]

    def rule_for(parts: list, typed: bool, span: str) -> None:
        """A RULE RENDERS WHERE THE PAGE DRAWS IT, so it carries the
        provenance of the rows it follows."""
        prov = m.Prov(1, tuple(l.id for l in parts)) if parts else m.Prov(1)
        items.append(m.Rule(prov=prov, typed=typed, span=span))

    # A CONSOLIDATED CAPTION IS FENCED CASE BY CASE, and the court draws
    # that fence or TYPES it interchangeably. Both cut the caption into the
    # cases it holds; both render as the rule the page shows.
    groups: list = [[]]
    cuts: list = []
    pending = list(fence_tops)
    for row in band_rows:
        while pending and row[0].top > pending[0]:
            t = pending.pop(0)
            groups.append([])
            cuts.append(("drawn", [l for l in band_lines if l.top < t][-3:]))
        shed = [_side(l, rail_x, w) for l in row for w in ("L", "R")]
        flat = _norm(" ".join(s.plain for s in shed if s is not None))
        if flat and set(flat) <= _RULE_CHARS and len(flat) >= 3:
            consumed.update(l.id for l in row)
            groups.append([])
            cuts.append(("typed", list(row)))
            continue
        groups[-1].append(row)
    # The fence the court draws to CLOSE the caption is not a cut inside it.
    while pending:
        t = pending.pop(0)
        cuts.append(("close", [l for l in band_lines if l.top < t][-3:]))

    def cell(parts: list, role: str) -> m.HmLine:
        return hmline(parts, role, align="L")

    two_sided: list = []
    one_sided: list = []
    for gi, group in enumerate(groups):
        if group:
            left: list = []
            right: list = []
            l_plain: list = []
            ids: list = []
            for row in group:
                for want, stack, plains in (("L", left, l_plain),
                                            ("R", right, None)):
                    parts = [s for s in (_side(l, rail_x, want) for l in row)
                             if s is not None]
                    if not parts:
                        continue
                    stack.append(cell(parts, "caption"))
                    if plains is not None:
                        plains.append(_norm(" ".join(p.plain for p in parts)))
                # A row that held nothing but the rail is claimed either
                # way — read as text it carries nothing, so it is emitted as
                # nothing rather than as a phantom blank cell.
                consumed.update(l.id for l in row)
                ids.extend(l.id for l in row)
            if left or right:
                items.append(m.CaptionBlock(
                    left=left, right=right, rail=_RAIL_GLYPH,
                    rail_rows=max(len(left), len(right), 1),
                    style_id="parenthetical-rail",
                    fp={"rail": _RAIL_GLYPH, "mid_x": rail_x},
                    prov=m.Prov(1, tuple(sorted(ids)))))
                caption_rows.extend(t for t in l_plain if t)
                sides = _sides(l_plain)
                for s in sides:
                    if s and s not in parties:
                        parties.append(s)
                if len(sides) == 2:
                    two_sided.append(f"{sides[0]} v. {sides[1]}")
                elif len(sides) == 1:
                    one_sided.append(sides[0])
        if gi < len(cuts):
            kind, parts = cuts[gi]
            rule_for(parts, typed=(kind == "typed"),
                     span="center" if kind == "typed" else "left")
    for kind, parts in cuts[len(groups):]:
        rule_for(parts, typed=(kind == "typed"),
                 span="center" if kind == "typed" else "left")

    if not caption_rows:
        return NOTHING              # a rail with no parties is not a caption

    # THE CASE NAME comes from a caption that HAS a pivot. The juvenile
    # papers open with an unpivoted style row ('In the Interest of: John Doe
    # (2024-37) / Juvenile Under Eighteen (18) Years of Age.') fenced above
    # the parties, and that row names the child, not the case.
    case_name = two_sided[0] if two_sided else \
        (one_sided[0] if one_sided else None)

    # ---- the right column, read as the facts it stacks -------------------
    # A filing date, the CLERK who filed it, and — on the papers the court
    # does not publish — its own notice about citing them. Three distinct
    # facts in one column; none of them is a docket, which this court sets
    # above the caption.
    notice: list = []
    in_notice = False
    for block in items:
        if not isinstance(block, m.CaptionBlock):
            continue
        for row in block.right:
            flat = _norm(_strip_tags(row.text))
            low = flat.lower().rstrip(".:")
            caps = flat == flat.upper() and any(c.isalpha() for c in flat)
            # THE NOTICE IS A RUN, and it does NOT close on a sentence: the
            # court sets its last row without a stop ('BE CITED AS
            # AUTHORITY'), so what carries the run on is its own CAPS and
            # what ends it is the first cell set otherwise. Two cues open
            # it; nothing is read out of its middle.
            if low.startswith(_NOTICE_OPENERS):
                in_notice = True
            elif in_notice and not caps:
                in_notice = False
            if in_notice:
                row.role = "publication"
                notice.append(flat)
            elif low.startswith(_FILED_OPENERS):
                row.role = "date"
                date = _find_date(flat)
                if date:
                    crit.setdefault("decision_date", date)
            else:
                # THE CLERK who filed it ('Melanie Gagnepain, Clerk') — a
                # fact about the paper that the vocabulary has no field for
                # and that is not the date beside it. It stays where the
                # page set it, marked as the caption apparatus it is.
                row.role = "case-info"

    # ---- everything below the caption, by landmark ----------------------
    below = [l for l in rows if l.page > 1 or l.top > band[1]]

    # THE BLOCK IS THE UNIT OF MEANING, not the row. The ladder is four
    # unlabelled rungs in fixed order — origin, outcome, appearances, and on
    # the per curiam papers a fenced roster — and what a block IS can be
    # stated on its second row as readily as its first ('… vacated and' /
    # 'case remanded.'). Ask once per block.
    kept: list = []                 # (row, text, opens) | (row, text, 'rule')
    prev: list | None = None
    for row in visual(below):
        parts = sorted(row, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in parts))
        # A BYLINE ENDS THE READER — and so does the BODY RAIL, which is the
        # same boundary measured rather than parsed: the court sets every
        # front-matter block one indent step inside the rail and signs every
        # writing AT it.
        if parser.parse(text) is not None:
            break
        if parts[0].x0 < body_x0 + _INDENT_MIN:
            break
        if _TYPED_RULE.match(text):
            # A TYPED RULE is the court's own section mark. The court sets it
            # one leading under the last row of the bar — the gap does not
            # say it is a new block, so it is recognized by what it is drawn
            # with.
            kept.append((row, text, "rule"))
            prev = row
            continue
        opens = True
        if prev is not None and kept and kept[-1][2] != "rule":
            gap = row[0].top - prev[0].top
            same_page = row[0].page == prev[0].page
            wraps = (not same_page and row[0].page == prev[0].page + 1
                     and row[0].top
                     <= (pages[row[0].page].height or 792.0) * _TOP_BAND)
            opens = not ((same_page and gap <= _BLOCK_LEAD_MAX) or wraps)
        kept.append((row, text, opens))
        prev = row

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
            elif _is_panel(joined):
                state = "panel"
            elif state in (None, "lower-court") and _is_outcome(joined):
                state = "disposition"
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
        elif role == "disposition":
            outcome_rows.append(text)
        elif role == "panel":
            panel_rows.append(text)
        else:
            counsel_rows.append(text)
        emit(parts, role, align=("C" if role == "panel" else "L"),
             rel_from=(None if role == "panel" else body_x0))

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if dockets:
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit["other_dockets"] = dockets[1:]
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name
    if notice:
        # THE COURT'S OWN STATEMENT about its paper's authority. Present, it
        # says the paper is unpublished; ABSENT, it says nothing at all, and
        # the reader states nothing.
        crit["publication_status"] = "unpublished"
    if origin_rows:
        printed = _norm(" ".join(origin_rows))
        crit["lower_court"] = printed
        judge = _trial_judges(printed)
        if judge:
            crit["lower_court_judge"] = judge
    if outcome_rows:
        crit["disposition"] = _norm(" ".join(outcome_rows))
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        # (Core cannot reach them itself: queue item 41.)
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]

    # ---- a claim must be TOTAL ------------------------------------------
    # Every line the reader CONSUMED above is in an item or a Rule; the
    # page foot is the one thing it set aside, and it is NOT the reader's
    # to record. Core's own furniture pass already drops this court's bare
    # centred folio on every page (verified with the decider popped: the
    # same `Dropped(kind='folio')` appears without this reader), so
    # recording it here again produces the SAME line twice — which is what
    # rugged_rentals showed, two identical page-1 folio drops, on the one
    # record whose page 1 the reader owns end to end. Queue item 46 is this
    # collision seen from the other side. The foot is excluded from `rows`
    # so it can never land in the caption band, and left unclaimed so the
    # pass that already owns it keeps owning it.
    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
