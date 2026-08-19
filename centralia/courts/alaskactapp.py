"""Court of Appeals of the State of Alaska ('alaskactapp').

Everything unique to alaskactapp lives here. It imports core, never
another court file, and no other court file imports it.

THE CONTRACT — 'old-faithful', and it is a DRAWN shape, not a wording.
The Court of Appeals sets its front matter on one stationery, and every
one of the corpus's 42 records draws it identically:

    ONE vertical rule down the page axis (x 303-306 on a 612pt page,
    60-300pt tall), CLOSED by a horizontal of HALF the body measure
    (232-234pt) anchored on the left margin, whose right end stops ON the
    vertical. A vertical with a left-anchored horizontal under it is what
    the caption catalog calls Old Faithful, and the two rules together
    are the whole dispatch:

        NOTICE                                              11-12pt
        The text of this opinion can be corrected …         the notice
        IN THE COURT OF APPEALS OF THE STATE OF ALASKA      the banner, 13
        JAMES CLARKE,                │                      the caption:
                                     │ Court of Appeals No. A-14169
                     Appellant,      │ Trial Court No. 3KN-10-00805 CR
        v.                           │ O P I N I O N
        STATE OF ALASKA,             │
                     Appellee.       │ No. 2810 — July 25, 2025
        ─────────────────────         the caption's closing fence, 234pt
              Appeal from the Superior Court, Third Judicial …  the origin
              Appearances:  Nate Crowley, Attorney at Law …     the bar
              Before: Allard, Chief Judge, and Harbison …       the roster
              Judge ALLARD.                                     the byline

This is NOT the Supreme Court's paper. That court rails its caption with
a stacked ')' and names itself 'Supreme Court No. S-…'; this one draws
the rail and numbers itself 'Court of Appeals No. A-…'. What the two
share is the judicial SYSTEM, and that is what transfers: the notice
block, the half-measure closing fence, the origin / appearances / roster
blocks set at 15pt leading and stood off by 30, and the docket rule —
THIS court's own number is the one it prints under its own name, and
every other tribunal stating a 'No.'/'Nos.' (Trial, Superior, District)
sits below it.

A CONSOLIDATED record repeats the fence INSIDE the band, once per case
(rosenbruch-decker: one 299pt rule, fences at 397.9 and 547.2), exactly
as the Supreme Court does.

The reader claims HEADMATTER ONLY. It stops at the first byline — and
alaskactapp's byline is TITLE-LED ('Judge ALLARD.', 'Judge HARBISON,
writing for the Court.'), never name-led, so the stop is a closed
vocabulary of bench titles followed by an ALL-CAPS surname. A record
that draws neither the divider nor its fence is not this contract and
gets NOTHING: core's shared walk places those rows unidentified, which
is a smaller error than a confident misreading.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, is_caps_name
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# THE BYLINE alaskactapp signs its writings with is TITLE-LED and its name
# is ALL CAPS — 'Judge ALLARD.', 'Judge TERRELL, concurring in part and
# dissenting in part.', 'Judge HARBISON, with whom Judge TERRELL joins,
# concurring.'. Every byline in the corpus takes that form and no other,
# and the shared 'prose' grammar the registry declared ('ALLARD, Judge.')
# matches none of them — so every one of these 42 documents assembled
# authorless. The grammar is a court FACT, so it is declared here beside
# the reader that depends on it rather than in the shared table.
PROFILES["alaskactapp"] = _replace(
    PROFILES["alaskactapp"],
    byline=BylineGrammar(style="reversed",
                         rev_titles=("Chief Judge", "Senior Judge", "Judge")),
)
ALASKACTAPP: CourtProfile = PROFILES["alaskactapp"]

STYLE_OLD_FAITHFUL = "old-faithful"

# ---- alaskactapp's declared facts (measured over the corpus) --------------
# THE DIVIDER: one drawn vertical on the page axis. Measured x 303.1-306.0
# on a 612pt page (0.495-0.500 of the width) and 149.5-298.9pt tall.
_DIV_MIN_H = 60.0
_DIV_BAND = (0.30, 0.80)         # of the page width, as the catalog scores it
# THE CAPTION FENCE: HALF the body measure, anchored on the left margin —
# 232.4 to 234.0pt over the corpus, x0 70.0-72.0. It closes the caption and,
# on a consolidated record, separates the cases inside it. The court's other
# rules are different measures entirely: the 'O P I N I O N' underline is
# 72.7-73.0pt at x0>388, the footnote separator is 144pt, and the notice's
# 'Pacific Reporter' underline is 79.7-81.8pt at x0>=108.
_FENCE_W = (200.0, 275.0)
_FENCE_X0_MAX = 110.0
# HOW FAR A BLOCK WRAPS. The origin / appearances / roster blocks are set at
# 15pt leading (15.0, or 15.4 on the older template) and stood off from each
# other by 30. 24pt lies between the two everywhere in the corpus.
_BLOCK_LEAD_MAX = 24.0
# THE CAPTION'S OWN RHYTHM is different: it is set DOUBLE, 29.9-30.0pt row
# to row, and its right column sits on the left column's baselines. 32pt is
# what makes two caption rows adjacent; 24 would call them strangers.
_CAPTION_LEAD_MAX = 32.0
# A block may WRAP THE PAGE: burton-hill fills page 1 with its three-appellant
# appearances block and opens page 2 with 'Before:'.
_TOP_BAND = 0.20
# HOW FAR THE BLOCKS STAND IN. The origin / appearances / roster all open at
# x0 144 on a 72pt body rail and wrap at the same indent; body prose runs
# over to the margin. 60pt is half that step, so nothing at the rail passes.
_BLOCK_INDENT_MIN = 60.0
# How far the front matter may run. Two pages is one more than any
# alaskactapp record needs.
_MAX_PAGES = 2

# THE ORIGIN, as this court names the tribunal it is reviewing.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "cross-appeal from", "cross-appeals from",
    "petition for review from", "petitions for review from",
    "petition for review of", "petition for hearing from",
    "on petition for review from", "on rehearing from",
    "certified question from", "original application",
)
_COUNSEL_LABEL = "appearances"
_PANEL_LABEL = "before"
# THE COURT'S OWN NUMBER. Everything else in this judicial system that
# states a number — the Trial Court, the Superior Court, the District
# Court — sits below this one, so the closed vocabulary is the SHORT one.
_DOCKET_PREFIXES = ("court of appeals no", "court of appeals nos",
                    "court of appeals file no")
# THE PAPER'S OWN NAME, set in the caption's right column and letter-spaced.
_TITLE_WORDS = ("OPINION", "ORDER", "AMENDED OPINION", "CORRECTED OPINION",
                "SUBSTITUTE OPINION", "OPINION AND ORDER", "JUDGMENT")
# THE SLIP NUMBER row: 'No. 2810 — July 25, 2025'. The court numbers its
# published slips in one sequence and dates them on the same row.
_SLIP_OPENERS = ("no.", "opinion no.", "order no.")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "claimant", "claimants", "applicant",
    "applicants", "cross", "third", "party", "interest", "in", "of",
    "and", "the", "pro", "se",
)
# BENCH WORDS — a closed vocabulary, so a roster never yields a judge
# called 'and' or one called 'Judges'.
_BENCH_WORDS = ("judge", "judges", "justice", "justices", "chief", "senior",
                "superior", "court", "magistrate", "pro", "tem", "retired",
                "participating", "sitting", "by", "assignment")
_SUFFIXES = ("jr", "sr", "ii", "iii", "iv")
# THE BYLINE'S TITLES, longest first. The reader ends at the first row of
# this shape; assembly reads the same shape through the profile above.
_BYLINE_TITLES = ("Chief Judge", "Senior Judge", "Superior Court Judge",
                  "Judge")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _squeeze(text: str) -> str:
    """'O P I N I O N' -> 'OPINION'. The court letter-spaces the label in
    the caption's right column; it is the same label."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _is_banner(text: str) -> bool:
    """The court naming itself: 'IN THE COURT OF APPEALS OF THE STATE OF
    ALASKA'. Applied ONLY above the caption band, which is what keeps
    'Appeal from the Superior Court…' out of it."""
    low = _norm(text).lower()
    return ("court of appeals" in low and "alaska" in low
            and len(low.split()) >= 6)


def _is_byline(text: str) -> bool:
    """'Judge ALLARD.' — this court's signature, title first and surname in
    caps. The TITLE is a closed vocabulary and the NAME is tested for case,
    never for spelling; that is what tells the byline apart from the prose
    that names some other court's judge ('Judge Friendly's proposal became
    the template…', 'Judge Victor D. Carlson. At the hearing…')."""
    flat = _norm(text)
    for title in _BYLINE_TITLES:
        if not flat.startswith(title + " "):
            continue
        rest = flat[len(title) + 1:].strip()
        head = rest.split(",")[0].split(".")[0].strip()
        if head and is_caps_name(head, max_tokens=2):
            return True
    return False


def _find_date(text: str) -> str | None:
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    return mm.group(1) if mm.group(1).split()[0].strip(".").lower() \
        in _MONTHS else None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


# --------------------------------------------------------------------------
# the divider and its fence — the dispatch
# --------------------------------------------------------------------------

def _divider(pm) -> dict | None:
    """The drawn caption divider on ``pm``: {'x','top','bottom'}, or None.

    A divider has to DIVIDE — it counts only where the caption sets text on
    both sides of it within its own vertical span. Without that test any
    tall stroke qualifies on height alone and every caption row falls to
    one side of it."""
    tall = [r for r in pm.v_rules
            if r.height >= _DIV_MIN_H
            and pm.width * _DIV_BAND[0] < r.x < pm.width * _DIV_BAND[1]]
    if not tall:
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
    for r in sorted(tall, key=lambda r: (abs(r.x - mid), -r.height)):
        if divides(r.x, r.top, r.bottom):
            return {"x": float(r.x), "top": r.top, "bottom": r.bottom}
    return None


def _fences(pm) -> list:
    """Tops of the caption fence — the half-measure rule the court closes
    its caption with, and repeats between consolidated cases."""
    return sorted(r.top for r in pm.h_rules
                  if _FENCE_W[0] <= r.width <= _FENCE_W[1]
                  and r.x0 <= _FENCE_X0_MAX)


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.

    Split GLYPH BY GLYPH. pdfio already splits some rows at the vertical
    rule and leaves others whole depending on how wide the column gap
    happened to be; a whole-line test would put a row in one column or the
    other by luck."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
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
    234pt rule anchored on the left margin under a 53pt status label set at
    x=216 is not. pdfio tags by vertical proximity alone, so the closing
    fence can arrive as an underline on whatever row it happens to follow.
    The fence is structure — it renders as the rule the page drew, once."""
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


def _caption_block(rows: list, rail_x: float, pm, style_id: str | None):
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
            for side, bucket in ((_side(line, rail_x, "L"), l_cells),
                                 (_side(line, rail_x, "R"), r_cells)):
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
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop(); right.pop(); left_plain.pop(); right_plain.pop()
    if not left:
        return None, [], []
    ids = tuple(sorted(l.id for row in rows for l in row))
    block = m.CaptionBlock(
        left=left, right=right, rail="|", rail_rows=len(left),
        style_id=style_id, fp={"rail": "drawn", "mid_x": rail_x},
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
            continue
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
    # incorporated under.
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster. Split on the court's own
    punctuation and keep what is not a BENCH word. A star on the roster
    ('Mannheimer, Senior Judge.*') marks the assignment footnote, not a
    name."""
    body = _norm(text)
    at = body.find("[")
    if at >= 0:
        body = body[:at].rstrip()
    if body.lower().startswith(_PANEL_LABEL):
        body = body[len(_PANEL_LABEL):].lstrip(": ")
    names: list = []
    for chunk in body.replace(";", ",").replace(" and ", ", ").split(","):
        piece = chunk.strip().strip(".*†‡ ").strip()
        if not piece or not any(c.isalpha() for c in piece):
            continue
        if all(w.lower().strip(".*") in _BENCH_WORDS for w in piece.split()):
            continue
        if piece.lower().strip(".") in _SUFFIXES and names:
            names[-1] = f"{names[-1]}, {piece}"
            continue
        if piece not in names:
            names.append(piece)
    return names


def _docket_tail(text: str) -> bool:
    """Does ``text`` CONTINUE the docket cell above it?

    A docket wrap carries no prose: more of the numbers themselves
    ('A-13262, and A-13263', '& 3PA-20-02805 CR', '4FA-18-00525 CR
    (respectively)'). Every word is a number or a case-type code; only the
    court's own conjunctions join them."""
    flat = _norm(text)
    core = re.sub(r"\([^)]*\)", " ", flat).strip()
    if not core:
        return True
    if not any(c.isdigit() for c in core):
        return False
    return all(w.strip(".,/&") == w.strip(".,/&").upper() or w.lower() == "and"
               for w in core.split())


def _trial_judge(text: str) -> str | None:
    """'…Third Judicial District, Palmer, Kristen C. Stohler, Judge.' — who
    tried it, as the origin statement names them. The name is the clause
    that ENDS on a bench word, and a record may state two ('David V. George
    and M. Jude Pate, Judges.')."""
    found: list = []
    for mm in re.finditer(
            r",\s*([A-Z][^,]{1,70}?)\s*,\s*"
            r"((?:Senior\s+|Chief\s+|Pro\s+Tem\s+|Magistrate\s+|"
            r"Superior\s+Court\s+|District\s+Court\s+)?"
            r"Judges?)\s*\.", _norm(text)):
        name = f"{_norm(mm.group(1))}, {_norm(mm.group(2))}"
        if name not in found:
            found.append(name)
    return "; ".join(found) if found else None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="alaskactapp")
def read_headmatter_alaskactapp(model, geom, **_):
    """Read alaskactapp's drawn-divider headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    div = _divider(page1)
    if div is None:
        return NOTHING                  # no caption divider: not this paper
    p1_fences = _fences(page1)
    closing = [t for t in p1_fences if t >= div["bottom"] - 2]
    if not closing:
        return NOTHING                  # a divider the court never closed

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.6
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue                # furniture the region inherits
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BAND. The caption occupies the divider's own vertical span, closed
    # by the fence under it; a consolidated caption fences each case inside
    # that same span.
    band = (div["top"] - 6.0, closing[0])
    fence_tops = [t for t in p1_fences if div["top"] < t < closing[0]]

    crit: dict = {"headmatter_style": STYLE_OLD_FAITHFUL}
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
        this court sets the label of a block in one column and its first
        entry in the next ('Before:' at 144, the roster at 193) — emitted
        separately those render as a label alone on a row."""
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
    # A NOTICE IS EVERYTHING ABOVE THE BANNER on this stationery — the
    # reporter-correction block the court heads every paper with. It is
    # bounded ABOVE THE BANNER, not merely 'above the caption': a row the
    # court sets between the banner and the caption belongs to the block,
    # and dropping it into the notice would swallow it silently.
    seen_banner = False
    for line in rows:
        if line.page != 1 or line.top >= band[0]:
            continue
        text = _norm(line.plain)
        if _is_banner(text):
            seen_banner = True
            banner_rows.append(text)
            emit(line, "court")
        elif seen_banner:
            emit(line, "summary", rel_from=body_x0)
        else:
            notice_lines.append(line)

    # ---- the caption ----------------------------------------------------
    band_lines = [l for l in rows
                  if l.page == 1 and band[0] <= l.top <= band[1]]
    visual: list = []
    for line in sorted(band_lines, key=lambda l: (l.top, l.x0)):
        line = _unfence(line, fence_tops + [band[1]])
        if visual and abs(visual[-1][0].top - line.top) <= 2:
            visual[-1].append(line)
        else:
            visual.append([line])
    # A consolidated caption is FENCED case by case; each fenced group is
    # one caption, and the rule between them renders where the page draws
    # it.
    groups: list = [[]]
    cuts = list(fence_tops)
    for row in visual:
        while cuts and row[0].top > cuts[0]:
            cuts.pop(0)
            groups.append([])
        groups[-1].append(row)
    head_prov = m.Prov(1, tuple(l.id for l in visual[0])) if visual \
        else m.Prov(1)
    for group in groups:
        if not group:
            continue
        block, lp, rp = _caption_block(group, div["x"], page1,
                                       STYLE_OLD_FAITHFUL)
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
    # A RULE RENDERS WHERE THE PAGE DRAWS IT, and the block is sorted back
    # into page order at the end — so a rule carries the provenance of the
    # row it follows.
    for t in fence_tops + [band[1]]:
        above = [l for l in band_lines if l.top < t]
        prov = m.Prov(1, tuple(l.id for l in above[-3:])) if above \
            else head_prov
        items.append(m.Rule(prov=prov, span="left"))

    if not caption_rows and not right_rows:
        return NOTHING

    # THE RIGHT COLUMN carries TWO numbers, and they are different things:
    # the number THIS court gave the case ('Court of Appeals No. A-14169')
    # and the number of the court it is reviewing ('Trial Court No.
    # 3KN-10-00805 CR'). They sit in the same column, one under the other,
    # at the same size on the same rail — geometry cannot tell them apart,
    # and nothing on the page does except the TRIBUNAL each row names.
    # That is a closed vocabulary of court names within one judicial
    # system, not an open reading of wording.
    prev_role = None
    prev_y = None
    docket_cells: list = []
    lower_cells: list = []
    slip_cells: list = []
    for row, flat, _y in right_rows:
        low = flat.lower()
        toks = [t.lower() for t in flat.split()]
        if _squeeze(flat) in _TITLE_WORDS:
            row.role = "title"
            crit.setdefault("title", _squeeze(flat))
        elif low.startswith(_DOCKET_PREFIXES):
            row.role = "docket"
            docket_cells.append(flat)
        elif low.startswith(_SLIP_OPENERS):
            row.role = "date"
            head = re.split("[–—]", flat)[0].strip().rstrip(",")
            if head:
                slip_cells.append(head)
            date = _find_date(flat)
            if date:
                crit.setdefault("decision_date", date)
        elif "no." in toks or "nos." in toks:
            # SOME OTHER TRIBUNAL'S NUMBER — the Trial Court's, the Superior
            # Court's, the District Court's. Every court in this system that
            # is not the Court of Appeals sits below it.
            row.role = "lower-court"
            lower_cells.append(flat)
        elif (prev_role == "title" and prev_y is not None
                and 0 < _y - prev_y <= _CAPTION_LEAD_MAX
                and not any(c.isdigit() for c in flat)):
            # THE PAPER'S NAME MAY CARRY A QUALIFIER on the row under it —
            # 'O P I N I O N' over 'As Amended' (vanderpool). One leading
            # below the title, stating no number, it is the title's own
            # second row, not a new cell.
            row.role = "title"
            crit["title"] = _norm(f"{crit.get('title', '')} {flat}")
        elif prev_role in ("docket", "lower-court") and _docket_tail(flat):
            # A DOCKET CELL MAY WRAP: the court breaks a long run of numbers
            # over two or three rows ('Court of Appeals Nos. A-13223,' /
            # 'A-13262, and A-13263').
            row.role = prev_role
            target = docket_cells if prev_role == "docket" else lower_cells
            if target:
                target[-1] = f"{target[-1]} {flat}"
        else:
            row.role = "case-info"
        prev_role = row.role
        prev_y = _y
    # A SLIP ROW MAY BREAK AT ITS DASH. keone_jason_lee sets 'No. 2719' and
    # 'February 4, 2022' as two runs of one row whose em dash the text layer
    # dropped; joined by the row they are one cell, and the date is on it.
    if crit.get("decision_date") is None:
        for row, flat, _y in right_rows:
            if row.role == "date":
                date = _find_date(flat)
                if date:
                    crit["decision_date"] = date
                    break
    # THE LEAD CASE'S NUMBER IS THE DOCKET; a consolidated record's other
    # captions state their own, and those are companion appeals.
    if docket_cells:
        crit.setdefault("docket_number", docket_cells[0])
    for extra in slip_cells + docket_cells[1:]:
        crit.setdefault("other_dockets", []).append(extra)
    if lower_cells:
        crit["lower_court_docket"] = lower_cells
    # WHAT THE PAPER SAYS IT IS. The caption's right column names this paper
    # 'O P I N I O N' and gives it a Pacific Reporter SLIP NUMBER ('No.
    # 2810 — July 25, 2025'); the notice above the banner says the text
    # 'can be corrected before the opinion is published in the Pacific
    # Reporter'. A slip number under that title is this court's declaration
    # that the paper is published — an unpublished disposition is titled
    # 'MEMORANDUM OPINION AND JUDGMENT' and this rule does not fire on it.
    #
    # Declared here because core reads publication status out of PROSE, and
    # a criminal appeal quoting its own earlier unpublished decision
    # ('Weston v. State, 2015 WL 5000563 … (unpublished)') in a FOOTNOTE
    # made five of these published slips read 'unpublished'.
    if slip_cells and crit.get("title", "").split()[:1] == ["OPINION"]:
        crit["publication_status"] = "published"

    # ---- everything below the caption, by landmark ----------------------
    below = [l for l in rows if l.page > 1 or l.top > band[1]]
    # Group the tail into VISUAL ROWS first: pdfio splits 'Before:' from its
    # roster at the column gap, and half a label opens no landmark.
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
        # A BYLINE ENDS THE READER, always and everywhere below the fence.
        if _is_byline(text):
            break
        opener = None
        if _origin_opener(text):
            opener = "lower-court"
        elif low.startswith(_COUNSEL_LABEL):
            opener = "counsel"
        elif low.startswith(_PANEL_LABEL):
            opener = "panel"
        if opener is None:
            # A CONTINUATION is bounded: the court sets these blocks at 15pt
            # leading and separates them by 30, so a row further down than
            # that opens something this contract does not name.
            if state is None or prev is None:
                break
            # …and it is INDENTED. This court sets the whole front matter
            # one full body rail in from the margin (x0 144 against a 72pt
            # body rail) and runs its wraps at that same indent; body prose
            # runs over to the margin itself.
            if row[0].x0 < body_x0 + _BLOCK_INDENT_MIN:
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
        if role == "lower-court":
            origin_rows.append(text)
        elif role == "counsel":
            counsel_rows.append(text)
        elif role == "panel":
            panel_rows.append(text)
        emit(row, role, rel_from=body_x0)
        state = role
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
            text = text.split(":", 1)[1].strip() if ":" in text[:16] else text
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

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
