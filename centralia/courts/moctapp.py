"""Missouri Court of Appeals ('moctapp').

Everything unique to moctapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT. The three districts set one paper between them — a masthead
naming the court, a two-column caption, a centred origin block, and the
opinion — and the caption is held by a DIVIDER drawn in one of two ways.
Which one is printed is the dispatch; nothing below is decided by what a
row says.

    [seal]                                        an image, ~72x72pt
    In the                                        the masthead: the court
    Missouri Court of Appeals                     naming itself, its
    Western District                              district, its division
    STATE OF MISSOURI,        )                   the caption:
              Respondent,     )  WD87073            left of the divider the
    V.                        )  OPINION FILED:     parties, right of it
    CODY LEE KISER,           )  OCTOBER 7, 2025    the numbers and dates
              Appellant.      )
      Appeal from the Circuit Court of Saline County, Missouri   the origin
      The Honorable Dennis A. Rolf, Judge                        …its judge
    Before Division One:  Gary D. Witt, Presiding Judge, …       the panel
    AFFIRMED                                      what the court DID
    Cody L. Kiser appeals the judgment …          the opinion

TWO DIVIDERS, TWO CONTRACTS, DISJOINT OVER THE CORPUS.

  `paren-rail caption` (17 of 27) — a stacked ')' at one x in the page's
  middle third, exactly as the Supreme Court of Missouri sets it. A rail
  glyph is THE LAST INK ON ITS ROW: the left column ends at the rail and
  the right column, where there is one, is a separate run past the column
  gap. A ')' with text to its right is prose. Without that test the ')'
  closing a defined term in the opening paragraph joins the column and
  drags the band into the body; with it every record is a regular column
  at the caption's own leading.

  `drawn-rail caption` (10 of 27) — the Southern District sets the same
  caption with no glyph at all and DRAWS the divider: one vertical rule
  in the page's middle third, spanning the caption and nothing else. It
  is the band as well as the divider — measured, its top and bottom sit
  within 4pt of the caption's first and last rows on all ten records.

No record in the corpus prints both, and none prints neither. A record
that prints neither is not this paper and gets NOTHING: core's shared
walk places those rows unidentified, which is a smaller error than a
confident misreading.

THE ORIGIN MAY BE IN THE RIGHT-HAND CELL. Eastern District papers set
'Appeal from the Circuit Court' / 'of Franklin County' / 'Cause No.
18SL-CC02821-01' / 'Honorable Ellen H. Ribaudo' beside the parties
instead of centred below them, so the right column is read with the same
vocabulary as the block below the caption and the two agree.

MISSOURI SIGNS AT THE END. The author's name stands under the last
paragraph of the writing it closes. There is no byline in the front
matter; the reader ends where the centred apparatus stops and the
opinion's first indented paragraph begins — and the court states what it
DID in bold capitals at the body rail immediately before it.
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
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# moctapp's profile is registered in the shared table; this file owns its
# reader only. Look it up rather than re-declaring it, so the byline
# grammar can never drift from the one assembly uses — and so importing
# this module can never raise a duplicate-registration error.
MOCTAPP: CourtProfile = PROFILES["moctapp"]

STYLE_PAREN_RAIL = "paren-rail caption"
STYLE_DRAWN_RAIL = "drawn-rail caption"

# ---- moctapp's declared facts (measured over the corpus, not tuned) ------
# THE GLYPH RAIL. Counted as LINE-FINAL ')' glyphs stacked at one x. The
# shortest in the corpus is 8 glyphs, the tallest 17; the floor is kept at
# the Supreme Court's 3 because the test is line-finality, not height.
_PAREN_FLOOR = 3
_RAIL_TOL = 3.0
_RAIL_WINDOW = 6.0
# Both dividers stand in the page's MIDDLE THIRD. Measured 0.470 to 0.506
# for the glyph rail and 0.492 to 0.507 for the drawn one; expressed as a
# fraction of the page width so it survives a different paper size.
_RAIL_X_BAND = (0.40, 0.72)
# THE CAPTION'S LEADING is 11.0 to 16.1pt depending on the district. No
# record in this corpus consolidates two captions under one masthead, so
# the rail is grown as one run and any gap wider than five leadings ends
# it — that is what throws out a prose parenthesis further down the page.
_RAIL_GAP_MAX = 80.0
# THE DRAWN RAIL. One vertical rule, 125 to 209pt tall, spanning the
# caption. 60pt is taller than any stray box edge and shorter than the
# smallest caption measured.
_VRULE_MIN_H = 60.0
_VRULE_PAD = 4.0
# THE RIGHT CELL MAY OPEN A LEADING ABOVE THE RAIL's first glyph.
_RIGHT_ABOVE = 20.0
# HOW FAR THE CENTRED BLOCK BELOW THE CAPTION WRAPS. Its own leading is
# 11.0 to 16.9pt; 24pt lies above every wrap and below every section gap
# that is not already named by its own opener.
_BLOCK_LEAD_MAX = 24.0
# THE PARAGRAPH INDENT: 36pt on every record. The opinion's first line
# opens at body_x0 + 36 and its continuations at body_x0; no centred row
# of the front matter lands on either.
_PARA_INDENT = 36.0
_RAIL_SNAP = 1.5
# WHERE THE COURT STATES WHAT IT DID. 'AFFIRMED' / 'APPEAL DISMISSED' /
# 'VACATED AND REMANDED WITH INSTRUCTIONS', set BOLD, in CAPITALS, at the
# body rail, and on eight records underlined by a drawn rule of its own
# width. Opinion prose is never bold capitals, so the two never collide;
# 12pt is wider than the 0.0-7.0pt the districts vary the rail by.
_DISPOSITION_SLACK = 12.0
# The whole front matter fits page 1 on every record.
_MAX_PAGES = 1

# THE ORIGIN, as the court names the tribunal it is reviewing — a closed
# set of openers, printed centred below the caption or inside its right
# cell. Matched case-insensitively: the Western District sets it in
# capitals on some papers and title case on others.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "cross-appeal from", "cross-appeals from",
    "on appeal from", "appeal and cross-appeal from", "on transfer from",
    "original ", "petition for review", "on petition for review",
    "certified question", "on certification",
)
# THE TRIAL JUDGE, as the origin statement names them. The comma before
# the bench title is missing on one record ('Honorable Robert N. Mayer
# Judge'), so the title is optional.
_HONORABLE = re.compile(r"^(?:the\s+)?honorable\b", re.IGNORECASE)
# WHO SAT, as the roster names itself. A closed set of openers; the
# roster is the one front-matter row that runs to the body rail, so
# without this it would read as opinion prose and end the reader.
_PANEL_OPENERS = ("before ", "division one", "division two",
                  "division three", "division four", "division five",
                  "division six", "special division")
# BENCH TITLES — a finite role vocabulary. Read to tell a judge's NAME
# from the apparatus around it; a name is never read by wording.
_BENCH = {
    "judge", "judges", "chief judge", "presiding judge", "special judge",
    "senior judge", "circuit judge", "associate circuit judge",
    "chief judge presiding", "justice", "chief justice", "presiding",
    "j", "jj", "pj", "cj", "p j", "c j",
}
_PLURAL_BENCH = {"jj", "judges"}
# '…, Judge and W. Douglas Thomson, Judge' — a bench title and the NEXT
# judge's name inside one comma-piece, because the roster's last comma is
# optional.
_TITLE_THEN_NAME = re.compile(
    r"^(Chief\s+Judge|Presiding\s+Judge|Special\s+Judge|Senior\s+Judge|"
    r"Associate\s+Circuit\s+Judge|Circuit\s+Judge|Chief\s+Justice|"
    r"Judge|Justice)\b\.?\s+(?:and\s+|&\s+)?(.*)$", re.IGNORECASE)
_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
# THE COURT'S OWN NUMBER. The districts print it with an opener ('No.
# ED112609', 'Nos. SD38913 and SD38914') or bare ('WD87073'), so the bare
# form is a declared fact about this court's numbering: the district's
# two letters and four to six digits.
_DOCKET_OPENERS = ("no.", "nos.")
_BARE_DOCKET = re.compile(r"^(?:WD|ED|SD)\s?\d{4,6}[A-Z]?$")
# …and the number the court BELOW gave the case, which the Eastern
# District prints in the same cell ('Cause No. 18SL-CC02821-01').
_LOWER_DOCKET_OPENERS = ("cause no.", "case no.", "circuit court no.")
# THE DATE CELL. 'OPINION FILED:' may stand alone with its date on the
# row beneath it.
_DATE_OPENERS = ("opinion filed", "filed", "opinion issued",
                 "opinion modified", "opinion reissued", "order issued",
                 "opinion handed down")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"\b(" + "|".join(_MONTHS) + r")\.?\s+(\d{1,2}),\s*(\d{4})",
                   re.IGNORECASE)
# THE MASTHEAD, as the court names itself. Applied only ABOVE the caption
# band, which is what keeps 'APPEAL FROM THE CIRCUIT COURT OF …' out of
# it. 'In the' is the first of the three rows the Western District sets.
_MASTHEAD_EXACT = ("in the", "in division", "in banc", "en banc")
_DISTRICTS = ("western", "eastern", "southern")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. The court hyphenates its compound roles ('Plaintiff-Respondent',
# 'Respondent/Movant-Respondent') and stacks them with a slash.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "amicus", "amici", "curiae",
    "movant", "movants", "relator", "relators", "claimant", "claimants",
    "applicant", "applicants", "garnishor", "garnishee",
    "cross", "third", "party", "interest", "natural", "father", "mother",
    "in", "of", "and", "the", "pro", "se", "et", "al", "minor", "child",
    "children", "next", "friend", "friends", "individually",
)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_caps(text: str) -> bool:
    """ALL-CAPS as the court sets its own labels. Digits, punctuation and
    the roman-numeral apparatus of a docket do not vote."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _is_masthead(text: str) -> bool:
    """The court naming itself, the district it sits in, or the division
    it sat as. Applied only above the caption band."""
    low = _norm(text).lower().rstrip(".:")
    if low in _MASTHEAD_EXACT:
        return True
    if "court of appeals" in low and "missouri" in low:
        return True
    if low.endswith("district") and low.split()[0] in _DISTRICTS:
        return True
    return low.startswith("division ") or low == "special division"


def _find_date(text: str) -> str | None:
    """The date as the cell prints it, with the month normalized — the
    Western District sets 'OCTOBER 7, 2025' and the Eastern 'October 7,
    2025', and they are the same day."""
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    return f"{mm.group(1).capitalize()} {int(mm.group(2))}, {mm.group(3)}"


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _panel_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_PANEL_OPENERS)


def _centred(line, pm) -> bool:
    """Centred on the PAGE AXIS — the way the masthead and the origin
    block are set. The opinion's own first line is not: it opens at the
    paragraph indent and runs to the right margin."""
    return abs((line.x0 + line.x1) / 2.0 - (pm.width or 612.0) / 2.0) <= 4.0


# --------------------------------------------------------------------------
# the divider — the dispatch, drawn or set
# --------------------------------------------------------------------------

def _paren_rail(pm) -> dict | None:
    """The stacked ')' divider on ``pm``: {'x','top','bottom'}, or None.

    A rail glyph is the LAST INK ON ITS ROW and stands in a column shared
    by at least ``_PAREN_FLOOR`` others; the column is grown from its
    topmost glyph and stops at the first gap wider than five leadings.
    """
    cands: list = []
    for line in pm.lines:
        for ch in line.chars:
            if (ch.get("text") or "") != ")":
                continue
            if any((d.get("text") or "").strip() and d["x0"] > ch["x0"] + 0.5
                   for d in line.chars):
                continue
            cands.append(ch)
    lo, hi = (_RAIL_X_BAND[0] * (pm.width or 612.0),
              _RAIL_X_BAND[1] * (pm.width or 612.0))
    cands = [c for c in cands if lo <= c["x0"] <= hi]
    if len(cands) < _PAREN_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in cands).most_common(1)[0]
    stack = sorted((c for c in cands if abs(c["x0"] - x) <= _RAIL_TOL),
                   key=lambda c: c["top"])
    if len(stack) < _PAREN_FLOOR:
        return None
    grown = [stack[0]]
    for ch in stack[1:]:
        if ch["top"] - grown[-1]["top"] > _RAIL_GAP_MAX:
            break
        grown.append(ch)
    if len(grown) < _PAREN_FLOOR:
        return None
    # THE LINE-FINAL TEST TELLS A RAIL GLYPH FROM A PROSE ONE; ONCE THE
    # COLUMN IS KNOWN, MEMBERSHIP IS BY COLUMN. The Eastern District sets
    # the caption's FIRST row as ') No. ED112916' — one run, the rail
    # glyph with the docket to its right — so that row is not line-final
    # and the seeded run starts a leading too low. Grow the run outward
    # through every ')' standing in the rail's own column, one contiguous
    # step at a time, so a prose parenthesis further down the page is
    # still barred by the same gap bound that seeded the run.
    column = sorted((c for l in pm.lines for c in l.chars
                     if (c.get("text") or "") == ")"
                     and abs(c["x0"] - x) <= _RAIL_TOL),
                    key=lambda c: c["top"])
    lo_i = min(range(len(column)), key=lambda i: abs(column[i]["top"]
                                                    - grown[0]["top"]))
    hi_i = min(range(len(column)), key=lambda i: abs(column[i]["top"]
                                                    - grown[-1]["top"]))
    run = column[lo_i:hi_i + 1]
    for ch in reversed(column[:lo_i]):
        if run[0]["top"] - ch["top"] > _RAIL_GAP_MAX:
            break
        run.insert(0, ch)
    for ch in column[hi_i + 1:]:
        if ch["top"] - run[-1]["top"] > _RAIL_GAP_MAX:
            break
        run.append(ch)
    return {"style": STYLE_PAREN_RAIL, "glyph": ")", "x": float(x),
            "top": min(c["top"] for c in run),
            "bottom": max(c["bottom"] for c in run)}


def _drawn_rail(pm) -> dict | None:
    """The DRAWN divider — one vertical rule in the page's middle third,
    tall enough to be a caption's and not a box edge. It is the band as
    well as the divider: on all ten Southern District records its top and
    bottom stand within 4pt of the caption's first and last rows."""
    lo, hi = (_RAIL_X_BAND[0] * (pm.width or 612.0),
              _RAIL_X_BAND[1] * (pm.width or 612.0))
    best = None
    for v in (getattr(pm, "v_rules", None) or []):
        if not (lo <= v.x <= hi):
            continue
        if (v.bottom - v.top) < _VRULE_MIN_H:
            continue
        if best is None or (v.bottom - v.top) > (best.bottom - best.top):
            best = v
    if best is None:
        return None
    return {"style": STYLE_DRAWN_RAIL, "glyph": None, "x": float(best.x),
            "top": float(best.top), "bottom": float(best.bottom)}


def _divider(pm) -> dict | None:
    """Which caption contract this record prints, or None. The glyph rail
    is tried first because it is the caption's own ink; the two are
    disjoint over the corpus, so the order is documentation, not a
    tie-break."""
    return _paren_rail(pm) or _drawn_rail(pm)


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.

    Split GLYPH BY GLYPH. Whether pdfio already broke a caption row at
    its column gap is an accident of how wide the gap happened to be: the
    same corpus sets ') WD87653' as one run and ')' / 'WD87073' as two,
    and a whole-line test puts the rail in one column or the other by
    luck."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _shed_rail(line, rail: dict):
    """``line`` with the divider's own glyphs removed, or None when the
    line WAS the divider. The glyph is identified by its COLUMN, never by
    its character — and a DRAWN divider sheds nothing, because the page
    drew it rather than setting it."""
    if rail["glyph"] is None:
        return line
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == rail["glyph"]
                    and lo <= c["x0"] <= hi)]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    if len(kept) == len(line.chars):
        return line
    return _replace(line, chars=kept)


def _sides(rows: list):
    """The party names either side of the 'v.' pivot, built from the
    party NAMES — never by joining the caption wholesale, because the
    status labels and the pivot are apparatus, not names."""
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
        bare = flat.rstrip(",.; ").lower()
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            # …except 'ET AL.', which the court sets on its own row when
            # the party name above it filled the column. It is part of
            # that name, not a status label.
            if words[:2] == ["et", "al"] and side:
                side[-1] = f"{side[-1].rstrip(', ')}, {flat.rstrip(', ')}"
            continue
        side.append(flat)
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _judge_name(text: str) -> str | None:
    """The trial judge, as the origin statement names them: everything
    after 'Honorable', with the bench title kept as printed."""
    flat = _norm(text).rstrip(".")
    mm = _HONORABLE.match(flat)
    if mm is None:
        return None
    name = flat[mm.end():].strip(" ,")
    return name or None


def _parse_panel(text: str) -> list[str]:
    """Who sat, from the roster the court prints. Walk the comma-separated
    pieces and close a name at the first piece that IS a bench title; a
    generational suffix joins the name it follows, and a PLURAL title
    ('JJ.') closes two names joined by 'and'. Returns [] rather than a
    guess — the printed roster is kept beside this either way."""
    flat = _norm(text)
    if ":" in flat:
        flat = flat.split(":", 1)[1]
    out: list[str] = []
    current: list[str] = []

    def flush(title: str | None) -> None:
        if not current:
            return
        name = _norm(" ".join(current)).replace(" ,", ",").strip(" ,")
        name = re.sub(r",(?=\S)", ", ", name)
        current.clear()
        if not name:
            return
        parts = [name]
        if title and title in _PLURAL_BENCH:
            parts = [p.strip() for p in re.split(r"\s+and\s+", name)
                     if p.strip()]
        for p in parts:
            p = re.sub(r"^(?:and|&)\s+", "", p).strip(" ,")
            if p and p not in out:
                out.append(p)

    for piece in flat.split(","):
        piece = piece.strip()
        if not piece:
            continue
        key = _norm(piece.lower().rstrip(".").replace(".", " "))
        if key in _SUFFIXES:
            # A GENERATIONAL SUFFIX JOINS THE NAME IT FOLLOWS, and it is
            # set off by the same comma the roster separates judges with.
            current.append("," + piece)
            continue
        if key in _BENCH:
            if key == "presiding" and not current:
                continue        # a modifier on the title just closed
            flush(key)
            continue
        # THE ROSTER'S LAST COMMA IS OPTIONAL: '…, Judge and W. Douglas
        # Thomson, Judge' sets a title and the next judge's name in ONE
        # comma-piece. Close the name the title belongs to and carry on
        # with the rest of the piece, or the two run together into a
        # judge called 'Alok Ahuja Judge and Karen King Mitchell'.
        mm = _TITLE_THEN_NAME.match(piece)
        if mm is not None:
            flush(_norm(mm.group(1).lower().replace(".", " ")))
            rest = mm.group(2).strip()
            if rest:
                current.append(rest)
            continue
        # 'Alok Ahuja and Karen King Mitchell, JJ.' — one piece, two names.
        current.append(piece)
    flush(None)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="moctapp")
def read_headmatter_moctapp(model, geom, **_):
    """Read moctapp's caption-divider headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _divider(page1)
    if rail is None:
        return NOTHING              # no caption divider: not this paper

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    parser = BylineParser(MOCTAPP.byline)
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = [l for pm in model.pages[:_MAX_PAGES] for l in pm.lines
            if l.plain.strip() and finder.kind(pm, l) is None]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BAND. A drawn divider IS the band. A glyph rail occupies the
    # caption's own vertical span, and the right cell that opens one
    # leading above its first glyph belongs to it, so the band reaches up
    # for anything printed to the RIGHT of the rail within a leading.
    if rail["glyph"] is None:
        top, bottom = rail["top"] - _VRULE_PAD, rail["bottom"] + _VRULE_PAD
    else:
        top = rail["top"] - 4.0
        early = [l.top for l in rows
                 if l.x0 > rail["x"] + 8 and rail["top"] - _RIGHT_ABOVE
                 <= l.top < rail["top"]]
        if early:
            top = min(early) - 4.0
        bottom = rail["bottom"] + 4.0

    crit: dict = {"headmatter_style": rail["style"]}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    notice_lines: list = []
    masthead_rows: list = []
    caption_rows: list = []
    origin_rows: list = []
    judge_rows: list = []
    panel_rows: list = []
    disposition_rows: list = []
    lower_dockets: list = []
    parties: list = []
    case_name: str | None = None
    docket_cells: list = []
    date_seen: str | None = None

    def emit(row, role: str, align: str = "L", rel: float = 0.0):
        """One HEADMATTER ROW, from the one or more line objects the page
        set on that baseline."""
        parts = sorted(row if isinstance(row, list) else [row],
                       key=lambda l: l.x0)
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), rel=rel, role=role))
        consumed.update(p.id for p in parts)

    # ---- the masthead: everything page 1 prints above the caption -------
    for line in rows:
        if line.top >= top:
            continue
        text = _norm(line.plain)
        if _is_masthead(text):
            masthead_rows.append(text)
            emit(line, "court", align="C")
        else:
            # Recorded, never silently swallowed.
            notice_lines.append(line)

    # ---- the caption ----------------------------------------------------
    band = [l for l in rows if top <= l.top <= bottom]
    if not band:
        return NOTHING
    visual: list = []
    for line in sorted(band, key=lambda l: (l.top, l.x0)):
        if visual and abs(visual[-1][0].top - line.top) <= 2.5:
            visual[-1].append(line)
        else:
            visual.append([line])

    def cell(cells: list, role: str):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align("L"), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role=role)

    left_cells: list = []
    right_cells: list = []
    left_plain: list = []
    right_plain: list = []
    cap_ids: list = []
    drawn = 0
    for row in visual:
        l_cells, r_cells = [], []
        railed = False
        for line in row:
            cap_ids.append(line.id)
            shed = _shed_rail(line, rail)
            if shed is not line:
                railed = True
            if shed is None:
                continue
            for sd, bucket in ((_side(shed, rail["x"], "L"), l_cells),
                               (_side(shed, rail["x"], "R"), r_cells)):
                if sd is not None:
                    bucket.append(sd)
        left_cells.append(
            cell(l_cells, "caption") if l_cells
            else m.HmLine(text="", prov=m.Prov(page1.number), role="caption"))
        right_cells.append(
            cell(r_cells, "caption") if r_cells
            else m.HmLine(text="", prov=m.Prov(page1.number), role="caption"))
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
        drawn += 1 if railed else 0

    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: rows that
    # held nothing but a rail glyph are empty on both sides, and left
    # standing at the foot they render as phantom blank rows.
    while left_cells and not _strip_tags(left_cells[-1].text).strip() \
            and not _strip_tags(right_cells[-1].text).strip():
        left_cells.pop(); right_cells.pop()
        left_plain.pop(); right_plain.pop()
    if not left_cells:
        return NOTHING

    # A CAPTION ROW THAT LEAVES THE BODY RAIL is indented from the
    # CAPTION'S OWN rail — measured inside the band, never across the
    # headmatter.
    own_x0 = min((c.x0 for c in left_cells
                  if _strip_tags(c.text).strip()), default=body_x0)
    for c in left_cells:
        if _strip_tags(c.text).strip() and c.x0 > own_x0 + 8:
            c.rel = min(c.x0 - own_x0, (page1.width or 612.0) * 0.5)

    # ---- what the right column says -------------------------------------
    prev_role = None
    for c, flat in zip(right_cells, right_plain):
        if not flat:
            continue
        low = flat.lower()
        date = _find_date(flat)
        if low.startswith(_DATE_OPENERS):
            c.role = "date"
            if date and date_seen is None:
                date_seen = date
        elif low.startswith(_LOWER_DOCKET_OPENERS):
            # The number the court BELOW gave the case, not a companion
            # appeal — the Eastern District prints both in this cell.
            c.role = "lower-court"
            lower_dockets.append(flat.rstrip(","))
        elif low.startswith(_DOCKET_OPENERS) or _BARE_DOCKET.match(flat):
            c.role = "docket"
            docket_cells.append(flat.rstrip(","))
        elif _origin_opener(flat):
            c.role = "lower-court"
            origin_rows.append((flat, True))
        elif _HONORABLE.match(flat):
            c.role = "lower-court"
            judge_rows.append(flat)
        elif prev_role == "date" and date:
            # 'OPINION FILED:' stands alone with its date beneath it.
            c.role = "date"
            if date_seen is None:
                date_seen = date
        elif prev_role == "lower-court" and not flat.startswith("("):
            c.role = "lower-court"
            origin_rows.append((flat, False))
        else:
            c.role = "case-info"
        prev_role = c.role

    items.append(m.CaptionBlock(
        left=left_cells, right=right_cells, rail=rail["glyph"],
        # THE RAIL RENDERS AS MANY GLYPHS AS THE PAGE DREW; a drawn
        # divider draws none.
        rail_rows=drawn if rail["glyph"] else 0,
        style_id=("parenthetical-box" if rail["glyph"] else "open-range"),
        fp={"rail": rail["glyph"], "mid_x": rail["x"]},
        prov=m.Prov(page1.number, tuple(sorted(set(cap_ids))))))
    consumed.update(cap_ids)
    caption_rows.extend(t for t in left_plain if t)
    sides = _sides(left_plain)
    for s in sides:
        if s and s not in parties:
            parties.append(s)
    if len(sides) == 2:
        case_name = f"{sides[0]} v. {sides[1]}"
    elif len(sides) == 1:
        case_name = sides[0]

    # ---- the centred block below the caption -----------------------------
    below = [l for l in rows if l.top > bottom]
    tail: list = []
    for line in below:
        if tail and abs(tail[-1][0].top - line.top) <= 2.5:
            tail[-1].append(line)
        else:
            tail.append([line])

    state = None
    prev = None
    for row in tail:
        parts = sorted(row, key=lambda l: l.x0)
        first = parts[0]
        text = _norm(" ".join(l.plain for l in parts))
        at_rail = (abs(first.x0 - body_x0) <= _RAIL_SNAP
                   or abs(first.x0 - body_x0 - _PARA_INDENT) <= _RAIL_SNAP)
        near = prev is not None and row[0].top - prev[0].top <= _BLOCK_LEAD_MAX
        # A ROSTER ROW THAT PARSES AS A BYLINE IS STILL THE ROSTER. The
        # court wraps 'Before Division One: … and Karen King' / 'Mitchell,
        # Judge', and the second row alone is a perfect byline — read as
        # one it ended the reader and was credited with the opinion. It is
        # inside the roster the row above it opened, so it belongs to it
        # whatever it looks like alone; the byline test runs only outside.
        in_roster = state == "panel" and near and not at_rail
        # A BYLINE ENDS THE READER, always. Missouri prints none here —
        # it signs at the end of each writing — but the rule stands.
        if not in_roster and parser.parse(text) is not None:
            break
        if _origin_opener(text):
            role = "lower-court"
            origin_rows.append((text, True))
        elif _HONORABLE.match(text):
            role = "lower-court"
            judge_rows.append(text)
        elif _panel_opener(text) and len(parts) == 1:
            # THE ROSTER is the one front-matter row that runs to the body
            # rail; it is named by its own opener before the rail is asked
            # about, or it would read as opinion prose and end the reader.
            role = "panel"
            panel_rows.append(text)
        elif (all(p.all_bold for p in parts) and _is_caps(text)
              and abs(first.x0 - body_x0) <= _DISPOSITION_SLACK
              and len(parts) == 1):
            # WHAT THE COURT DID, in bold capitals at the body rail.
            role = "disposition"
            disposition_rows.append(text)
        else:
            # A CONTINUATION IS BOUNDED. The block is set at its own
            # leading and the opinion opens further below it; and the
            # opinion's first line stands at the paragraph indent, which
            # no centred row of the block ever does.
            if state is None or prev is None or at_rail or not near:
                break
            role = state
            if role == "lower-court":
                origin_rows.append((text, False))
            elif role == "panel":
                panel_rows.append(text)
            elif role == "disposition":
                disposition_rows.append(text)
        emit(row, role, align="C" if _centred(first, page1) else "L")
        state = role
        prev = row

    # ---- what the block says --------------------------------------------
    if masthead_rows:
        crit["court"] = _norm(" ".join(masthead_rows))
    if caption_rows:
        crit["caption"] = caption_rows
    if parties:
        crit["parties"] = parties
    if case_name:
        crit["case_name"] = case_name
    if date_seen:
        crit["decision_date"] = date_seen
    if docket_cells:
        crit["docket_number"] = docket_cells[0]
        if len(docket_cells) > 1:
            crit["other_dockets"] = docket_cells[1:]
    if lower_dockets:
        crit["lower_court_docket"] = lower_dockets
    if origin_rows:
        statements: list = []
        for text, is_opener in origin_rows:
            if is_opener or not statements:
                statements.append(text)
            else:
                statements[-1] = f"{statements[-1]} {text}"
        crit["lower_court"] = "; ".join(statements)
    if judge_rows:
        judges = []
        for text in judge_rows:
            name = _judge_name(text)
            if name and name not in judges:
                judges.append(name)
        if judges:
            crit["lower_court_judge"] = "; ".join(judges)
    if panel_rows:
        line_text = _norm(" ".join(panel_rows))
        crit["panel_line"] = line_text
        seated = _parse_panel(line_text)
        if len(seated) >= 2:
            crit["panel"] = seated
    if disposition_rows:
        crit["disposition"] = _norm(" ".join(disposition_rows))

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
