"""Supreme Court of Missouri ('mo').

Everything unique to mo lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Missouri sets one paper, and its front matter is held by a
caption DIVIDER: a stacked ')' rail that runs the height of the caption
at a single x in the page's middle third. Nothing below is decided by
what a row says:

    [seal]                                       an image, 91x90pt
    SUPREME COURT OF MISSOURI                    the banner, 20pt or 13pt
    en banc                                      …and its second row
    STATE OF MISSOURI,          )                the caption:
                Respondent,     )  Opinion issued April 1, 2025
    v.                          )  No. SC100676
    ANTHONY TATE,               )
                Appellant.      )
       APPEAL FROM THE CIRCUIT COURT OF ST. LOUIS COUNTY   the origin
       The Honorable Stanley J. Wallach, Judge             …and its judge
    Anthony Tate appeals the circuit court's judgment …    the opinion

The dispatch is the RAIL, never the words beside it. A record that
stacks no rail is not this contract and gets NOTHING: core's shared walk
places those rows unidentified, which is a smaller error than a
confident misreading.

WHAT MAKES A RAIL GLYPH. ')' is ordinary punctuation, and a caption six
rows tall is only three glyphs on some of this court's disciplinary
papers — the floor ca6 and alaska use would miss them. Missouri prints
the rail as the LAST INK ON ITS ROW: the caption's left column ends at
the rail, and the right column, where there is one, is a separate run
past the column gap. A ')' with text to its right on the same line is
prose. That one test alone turns every record in the corpus into a
perfectly regular 15pt column and throws out the ')' that closes
'("the department") both appeal …' 90pt below the caption
(catharine_sue_carter, where a naive column ran the band 105pt long).

A CONSOLIDATED RECORD IS FENCED BY THE RAIL'S OWN BREAK. Missouri
draws no rule between two cases heard together; it stops the rail for
two rows, sets the word 'and' in the white, and starts the rail again
(laura_salamun, jessie_l._nelson). The break is 59.7 and 74.7pt where
every other step in the column is 15.0, so the CAPTION is cut where the
RAIL is, not where the word is — and each case keeps its own docket
cell and its own 'APPEAL FROM …'.

MISSOURI SIGNS AT THE END. The author's name stands under the last
paragraph of the writing it closes, not above the first. There is no
byline in the front matter; the reader ends where the caption's centred
apparatus stops and the opinion's first indented paragraph begins.
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

# mo's profile is registered in the shared table; this file owns its
# reader only. Look it up rather than re-declaring it, so the byline
# grammar can never drift from the one assembly uses.
MO: CourtProfile = PROFILES["mo"]

STYLE_PAREN_RAIL = "paren-rail caption"

# ---- mo's declared facts (measured over the corpus, not tuned) ----------
# THE RAIL. Counted as LINE-FINAL ')' glyphs stacked at one x. The
# shortest rail in the corpus is 3 glyphs (in_re_paul_eric_petruska,
# in_re_todd_n._agron) and the tallest 23 (the consolidated Williams
# record).
_PAREN_FLOOR = 3
# A glyph belongs to the rail when it stands in the rail's own column.
# The court sets the rail at 304, 306, 311, 324 or 360 on a 612pt page
# and never moves it within a document by more than 0.1pt.
_RAIL_TOL = 3.0
_RAIL_WINDOW = 6.0
# …and the rail always stands in the page's MIDDLE THIRD. Expressed as a
# fraction of the page width so it survives a different paper size:
# measured 0.497 to 0.588.
_RAIL_X_BAND = (0.40, 0.72)
# THE CAPTION'S LEADING: 15.0pt, invariant across all 50 records. Every
# consecutive pair of rail glyphs is 14.9 or 15.0pt apart except where a
# CONSOLIDATED caption breaks for its own 'and' — two rows of white and
# the second case's first party name, 74.7pt at the widest.
_RAIL_GAP_MAX = 80.0
# …and that break is also where a CONSOLIDATED record ends one case and
# begins the next. Missouri draws no fence between them — the only mark
# is the rail STOPPING for two rows and starting again, which is
# geometry, not the word 'and' the court sets in the gap. 35pt is two
# caption leadings: more than any wrap, less than any break.
_RAIL_BREAK = 35.0
# THE RIGHT CELL MAY OPEN A LEADING ABOVE THE RAIL. On the disciplinary
# papers the court sets 'Opinion issued December 10, 2024' one row above
# the caption's first ')' — 14.2 to 14.9pt. 'en banc', the row above
# that, never stands closer than 24.0pt to the rail's first glyph, so
# 20pt separates the two everywhere in the corpus.
_RIGHT_ABOVE = 20.0
# HOW FAR THE CENTRED BLOCK BELOW THE CAPTION WRAPS. The origin block is
# set at 15pt leading; the body opens 29.5-44.5pt below it. 24pt lies
# between the two everywhere in the corpus.
_BLOCK_LEAD_MAX = 24.0
# THE PARAGRAPH INDENT: 36pt, invariant. The opinion's first line opens
# at body_x0 + 36 and its continuations at body_x0; no row of the
# court's centred front matter ever lands on either rail except the
# origin statement, which names itself first.
_PARA_INDENT = 36.0
_RAIL_SNAP = 1.5
# The whole front matter fits page 1 on every record; the tallest
# caption (the consolidated Williams record) closes at y=546 of 792.
_MAX_PAGES = 1

# THE ORIGIN, as Missouri names the tribunal it is reviewing — a closed
# set of openers set at the head of that centred block. 'ORIGINAL ' also
# takes the court's own original proceedings ('ORIGINAL DISCIPLINARY
# PROCEEDING', 'ORIGINAL PROCEEDING IN PROHIBITION', 'ORIGINAL
# PROCEEDING: ELECTION CONTEST') — and the corpus's one typo,
# 'ORIGINAL DISCPLINARY PROCEEDING', which a spelled-out vocabulary
# would have dropped.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "cross-appeal from", "cross-appeals from",
    "on appeal from", "on transfer from", "original ", "certified question",
    "petition for review", "on petition for review", "on certification",
)
# THE BANNER: the court naming itself. Set 20pt on most papers and at
# BODY SIZE on others, so the test is on the words, and it is only ever
# applied ABOVE the caption band.
_BANNER_SECOND = ("en banc", "en banc.", "division one", "division two",
                  "division three", "division four")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# THE COURT'S OWN NUMBER, as the right cell states it: 'No. SC100676'.
_DOCKET_OPENERS = ("no.", "nos.", "case no.", "cause no.")
# The right cell's date row: 'Opinion issued April 1, 2025'.
_DATE_OPENERS = ("opinion issued", "opinion modified", "opinion filed",
                 "order issued", "opinion reissued")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read
# by wording. Missouri hyphenates its compound roles
# ('Appellant-Respondent', 'Respondent/Cross-Appellant') and stacks
# 'Movant/Petitioner'.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "intervenors-appellants", "amicus",
    "amici", "curiae", "movant", "movants", "relator", "relators",
    "claimant", "claimants", "applicant", "applicants", "cross", "third",
    "party", "interest", "in", "of", "and", "the", "pro", "se", "et", "al",
)
# THE TRIAL JUDGE, as the origin statement names them.
_TRIAL_JUDGE = re.compile(
    r"^The Honorable\s+(.+?),\s*"
    r"((?:Senior\s+|Chief\s+|Special\s+|Associate\s+|Presiding\s+)?"
    r"(?:Circuit\s+)?Judge)\.?$")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_banner(text: str) -> bool:
    """The court naming itself, or the division it sat as. Applied only
    above the caption band, which is what keeps 'APPEAL FROM THE CIRCUIT
    COURT OF ST. LOUIS COUNTY' out of it."""
    low = _norm(text).lower()
    if low.rstrip(".") in [b.rstrip(".") for b in _BANNER_SECOND]:
        return True
    return "court" in low and "missouri" in low and "supreme" in low


def _find_date(text: str) -> str | None:
    mm = _DATE.search(_norm(text))
    if mm is None:
        return None
    return mm.group(1) if mm.group(1).split()[0].strip(".").lower() \
        in _MONTHS else None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _is_caps(text: str) -> bool:
    """ALL-CAPS as the court sets its own labels. Digits, punctuation and
    the roman-numeral apparatus of a docket do not vote."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _centred(line, pm) -> bool:
    """Centred on the PAGE AXIS — the way Missouri sets every row of the
    block under its caption. The opinion's own first line is not: it
    opens at the paragraph indent and runs to the right margin, and its
    midpoint lands 5 to 18pt right of the axis."""
    return abs((line.x0 + line.x1) / 2.0 - (pm.width or 612.0) / 2.0) <= 4.0


# --------------------------------------------------------------------------
# the divider — mo's one caption contract, and the dispatch
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The ')' divider on ``pm``: {'x','top','bottom'}, or None.

    A rail glyph is the LAST INK ON ITS ROW and stands in a column shared
    by at least ``_PAREN_FLOOR`` others; the column is grown from its
    topmost glyph and stops at the first gap wider than a consolidated
    caption's 'and' break. Both halves matter: without the line-final
    test a paren in the opening paragraph joins the column, and without
    the growth bound it drags the band 100pt into the body.
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
    return {"x": float(x), "top": min(c["top"] for c in grown),
            "bottom": max(c["bottom"] for c in grown),
            "tops": [c["top"] for c in grown]}


# --------------------------------------------------------------------------
# the caption
# --------------------------------------------------------------------------

def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the divider, or None.

    Split GLYPH BY GLYPH. Whether pdfio already broke a caption row at
    its column gap is an accident of how wide the gap happened to be: the
    same corpus sets 'ATTORNEYS' RETIREMENT SYSTEM, )' as one run and
    ')  ' / 'No. SC100376' as two, and a whole-line test puts the rail in
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


def _shed_rail(line, rail_x: float):
    """``line`` with the divider's own glyphs removed, or None when the
    line WAS the divider. The glyph is identified by its COLUMN, never by
    its character."""
    lo, hi = rail_x - _RAIL_WINDOW, rail_x + _RAIL_WINDOW
    kept = [c for c in line.chars
            if not ((c.get("text") or "") == ")" and lo <= c["x0"] <= hi)]
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
        if flat.lower().strip(",. ") == "and":
            continue          # the consolidation joiner, not a party
        bare = flat.rstrip(",.; ").lower()
        words = [w.strip(",.;-/ ") for w in
                 bare.replace("-", " ").replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or not w for w in words):
            # …except 'ET AL.', which the court sets on its own row when
            # the party name above it filled the column. It is part of
            # that name, not a status label.
            if words == ["et", "al"] and side:
                side[-1] = f"{side[-1].rstrip(', ')}, {flat.rstrip(', ')}"
            continue
        side.append(flat)
    if not (left and right and seen):
        one = _norm(" ".join(left + right)).rstrip(", ")
        return (one,) if one else ()
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _trial_judge(text: str) -> str | None:
    mm = _TRIAL_JUDGE.match(_norm(text))
    if mm is None:
        return None
    return f"{_norm(mm.group(1))}, {_norm(mm.group(2))}"


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="mo")
def read_headmatter_mo(model, geom, **_):
    """Read mo's paren-rail headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _rail(page1)
    if rail is None:
        return NOTHING              # no caption divider: not mo's paper

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    parser = BylineParser(MO.byline)
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE ROWS the reader may see. Furniture core already recorded is not
    # claimed: mo's page foot is a bare folio and core reads it.
    rows = [l for pm in model.pages[:_MAX_PAGES] for l in pm.lines
            if l.plain.strip() and finder.kind(pm, l) is None]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not rows:
        return NOTHING

    # THE BAND. The caption occupies the rail's own vertical span — and
    # the right cell that opens one leading above the rail's first glyph
    # belongs to it, so the band reaches up for anything printed to the
    # RIGHT of the rail within a leading of its head.
    top = rail["top"] - 4.0
    early = [l.top for l in rows
             if l.x0 > rail["x"] + 8 and rail["top"] - _RIGHT_ABOVE
             <= l.top < rail["top"]]
    if early:
        top = min(early) - 4.0
    bottom = rail["bottom"] + 4.0

    crit: dict = {"headmatter_style": STYLE_PAREN_RAIL}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    notice_lines: list = []
    banner_rows: list = []
    caption_rows: list = []
    origin_rows: list = []
    title_rows: list = []
    parties: list = []
    case_name: str | None = None

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
        if _is_banner(text):
            banner_rows.append(text)
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

    # A CONSOLIDATED RECORD IS FENCED BY THE RAIL'S OWN BREAK. Each run
    # of glyphs at the caption's leading is one case; the rows the court
    # sets in the gap ('Respondents.', the joining 'and') close the case
    # above them.
    cuts: list = []
    tops = rail.get("tops") or []
    for a, b in zip(tops, tops[1:]):
        if b - a > _RAIL_BREAK:
            cuts.append(b)
    groups: list = [[]]
    for row in visual:
        while cuts and row[0].top >= cuts[0] - 2:
            cuts.pop(0)
            groups.append([])
        groups[-1].append(row)

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

    docket_cells: list = []
    blocks_made = 0
    for group in groups:
        if not group:
            continue
        left_cells: list = []
        right_cells: list = []
        left_plain: list = []
        right_plain: list = []
        cap_ids: list = []
        drawn = 0
        for row in group:
            l_cells, r_cells = [], []
            railed = False
            for line in row:
                cap_ids.append(line.id)
                shed = _shed_rail(line, rail["x"])
                if shed is not line:
                    railed = True
                if shed is None:
                    continue
                for side, bucket in ((_side(shed, rail["x"], "L"), l_cells),
                                     (_side(shed, rail["x"], "R"), r_cells)):
                    if side is not None:
                        bucket.append(side)
            left_cells.append(
                cell(l_cells, "caption") if l_cells
                else m.HmLine(text="", prov=m.Prov(page1.number),
                              role="caption"))
            right_cells.append(
                cell(r_cells, "caption") if r_cells
                else m.HmLine(text="", prov=m.Prov(page1.number),
                              role="caption"))
            left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
            right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
            drawn += 1 if railed else 0

        # THE RAIL'S OWN RUN is not the caption's vertical rhythm: rows
        # that held nothing but a rail glyph are empty on both sides, and
        # left standing at the foot they render as phantom blank rows.
        while left_cells and not _strip_tags(left_cells[-1].text).strip() \
                and not _strip_tags(right_cells[-1].text).strip():
            left_cells.pop(); right_cells.pop()
            left_plain.pop(); right_plain.pop()
        if not left_cells:
            continue

        # A CAPTION ROW THAT LEAVES THE BODY RAIL is indented from the
        # CAPTION'S OWN rail — measured inside the band, never across the
        # headmatter. Missouri steps its status labels in by 36 to 144pt.
        own_x0 = min((c.x0 for c in left_cells
                      if _strip_tags(c.text).strip()), default=body_x0)
        for c in left_cells:
            if _strip_tags(c.text).strip() and c.x0 > own_x0 + 8:
                c.rel = min(c.x0 - own_x0, (page1.width or 612.0) * 0.5)

        # ---- what the right column says ---------------------------------
        prev_role = None
        for c, flat in zip(right_cells, right_plain):
            if not flat:
                continue
            low = flat.lower()
            if low.startswith(_DATE_OPENERS):
                c.role = "date"
                date = _find_date(flat)
                if date:
                    crit.setdefault("decision_date", date)
            elif low.startswith(_DOCKET_OPENERS):
                c.role = "docket"
                docket_cells.append(flat.rstrip(","))
            elif prev_role == "date":
                # A date cell may WRAP: 'Opinion issued August 12, 2025,' /
                # "and modified on the Court's own" / 'motion September 9,
                # 2025' is one statement set on three rows.
                c.role = "date"
            else:
                c.role = "case-info"
            prev_role = c.role

        block = m.CaptionBlock(
            left=left_cells, right=right_cells, rail=")",
            # THE RAIL RENDERS AS MANY GLYPHS AS THE PAGE DREW. A
            # consolidated caption sets rows in the break where there is
            # no rail at all ('Respondents.', the joining 'and'), and a
            # glyph per printed row would draw a rail the court did not.
            rail_rows=drawn or len(left_cells),
            style_id="parenthetical-box",
            fp={"rail": ")", "mid_x": rail["x"]},
            prov=m.Prov(page1.number, tuple(sorted(set(cap_ids)))))
        items.append(block)
        consumed.update(cap_ids)
        blocks_made += 1
        caption_rows.extend(t for t in left_plain if t)
        sides = _sides(left_plain)
        for s in sides:
            if s and s not in parties:
                parties.append(s)
        if case_name is None:
            if len(sides) == 2:
                case_name = f"{sides[0]} v. {sides[1]}"
            elif len(sides) == 1:
                case_name = sides[0]

    if not blocks_made:
        return NOTHING
    # THE LEAD CASE'S NUMBER IS THE DOCKET; a consolidated record's other
    # captions state their own, and those are companion appeals.
    if docket_cells:
        crit["docket_number"] = docket_cells[0]
        if len(docket_cells) > 1:
            crit["other_dockets"] = docket_cells[1:]

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
        # A BYLINE ENDS THE READER, always. Missouri prints none here —
        # it signs at the end of each writing — but the rule stands.
        if parser.parse(text) is not None:
            break
        if _origin_opener(text):
            opener = "lower-court"
        elif (_is_caps(text) and _centred(first, page1)
              and len(parts) == 1 and first.x1 < (page1.width or 612.0) - 60):
            # THE PAPER'S OWN NAME, where Missouri prints one instead of
            # an origin ('OPINION OVERRULING MOTION TO WITHDRAW' /
            # 'WARRANT OF EXECUTION'). Set in caps on the page axis, the
            # way the origin is; the opinion's own headings below it are
            # title case ('Introduction', 'Procedural History').
            opener = "title"
        else:
            # A CONTINUATION IS BOUNDED. The court sets this block at
            # 15pt leading and opens the opinion 29.5pt or more below it;
            # and the opinion's first line stands at the paragraph
            # indent, which no centred row of the block ever does.
            at_rail = (abs(first.x0 - body_x0) <= _RAIL_SNAP
                       or abs(first.x0 - body_x0 - _PARA_INDENT)
                       <= _RAIL_SNAP)
            if state is None or prev is None or at_rail:
                break
            if row[0].top - prev[0].top > _BLOCK_LEAD_MAX:
                break
            opener = state
        if opener == "lower-court":
            origin_rows.append((text, _origin_opener(text)))
        else:
            title_rows.append(text)
        emit(row, opener, align="C")
        state = opener
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
    if title_rows:
        crit["title"] = _norm(" ".join(title_rows))
    if origin_rows:
        # A CONSOLIDATED RECORD STATES ONE ORIGIN PER CASE, each opening on
        # its own 'APPEAL FROM …'; a single origin that wraps continues the
        # statement above it. Keep them apart, and name each trial judge
        # once — the same judge may have tried both cases.
        statements: list = []
        judges: list = []
        for text, is_opener in origin_rows:
            judge = _trial_judge(text)
            if judge is not None:
                if judge not in judges:
                    judges.append(judge)
                continue
            if is_opener or not statements:
                statements.append(text)
            else:
                statements[-1] = f"{statements[-1]} {text}"
        if statements:
            crit["lower_court"] = "; ".join(statements)
        if judges:
            crit["lower_court_judge"] = "; ".join(judges)

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


# --------------------------------------------------------------------------
# writing.covers — Missouri gives every paper its own cover
# --------------------------------------------------------------------------
# Measured over all 50 records: 13 carry a separate writing, and every one of
# them heads it with the FULL COVER over again — the seal, 'SUPREME COURT OF
# MISSOURI', 'en banc', the caption over its ')' rail, the docket — and then
# a title naming the paper. The writing is signed only at its FOOT, flush
# right, so there is no byline at its head for core to find: all 16 separate
# writings were merged into the paper before them, and the principal opinion
# came back credited to whoever signed LAST (r.m.a.: 141 blocks under a
# dissenter's name).
#
# The titles, over the 16 later covers — the whole set, not a sample:
#
#     12  DISSENTING OPINION
#      2  SEPARATE OPINION
#      1  CONCURRING OPINION
#      1  SEPARATE OPINION CONCURRING IN PART AND DISSENTING IN PART
#
# 'SEPARATE OPINION' does not say which it is, so it is READ and not guessed:
# mcgaugh's opens "I concur in the dissenting opinion's analysis of article
# V, § 24.3" and mccarty's "For the reasons stated in my dissenting opinion
# in Lucas v. Ashcroft … I disagree this Court possesses original
# jurisdiction". One concurs, one dissents, under one title.
#
# THE COVER IS NOT SET IN A CONSTANT SIZE and the rail does not stand in a
# constant place: the banner is 20pt on twelve records and 13pt — body size —
# on phillip_weeks, whose rail is at x0 360 against d.j.'s 306 and mcgaugh's
# 310.6. So a cover is found by the words the court prints, never by measure
# or position.
_BANNER = "supreme court of missouri"
_EN_BANC = "en banc"
# The title always names itself an OPINION, in caps, and says what kind.
_TITLE = re.compile(r"^[A-Z][A-Z0-9 .,'()§-]*OPINION[A-Z0-9 .,'()§-]*$")
# What the writing's own first sentence says, when its title will not.
_CONCUR_CUE = ("i concur", "i fully concur", "i respectfully concur")
_DISSENT_CUE = ("i dissent", "i respectfully dissent", "i disagree",
                "respectfully dissent")


def _cover_kind(title: str, opening: str) -> str | None:
    """The kind phrase this paper's title states, read where it will not."""
    t = " ".join(title.split()).lower()
    if "concur" in t and "part" in t and "dissent" in t:
        return "concurring in part and dissenting in part"
    if "dissent" in t:
        return "dissenting"
    if "concur" in t:
        return "concurring"
    if t.startswith("separate opinion"):
        # THE ORDER OF THESE TWO TESTS IS THE WHOLE READING. Both openings
        # contain the word 'dissenting': mcgaugh CONCURS in the dissenting
        # opinion ("I concur in the dissenting opinion's analysis of article
        # V, § 24.3") and mccarty DISSENTS by reference to one ("For the
        # reasons stated in my dissenting opinion in Lucas v. Ashcroft …
        # I disagree this Court possesses original jurisdiction"). So how it
        # OPENS decides first, and only then what it says — and the sentence
        # runs past the first printed row, which is why several are read.
        low = " ".join(opening.split()).lower()
        if any(low.startswith(c) for c in _CONCUR_CUE):
            return "concurring"
        if any(c in low for c in _DISSENT_CUE):
            return "dissenting"
        # A separate paper that states neither is still separate, and typing
        # it `majority` would give the document two of those.
        return "concurring"
    return None


@decider("writing.covers", court="mo")
def writing_covers_mo(model=None, **_):
    """Where each of Missouri's papers begins, and which rows are its cover.

    Returns the line the writing opens on (its title) mapped to the kind that
    title states, plus every cover row above the title to be recorded as
    removed. Page 1's cover is the document's own headmatter and is left
    alone. A record with a single cover reaches none of this.
    """
    if model is None or len(model.pages) < 2:
        return NOTHING
    starts: dict[int, str] = {}
    drop: list[int] = []
    for pm in model.pages[1:]:
        rows = sorted((l for l in pm.lines if l.plain.strip()),
                      key=lambda l: l.top)
        if not rows:
            continue
        # THE COVER NAMES THE COURT IN ITS TOP BAND. Six rows, because the
        # seal may be cropped into rows above the banner on a scanned record.
        if not any(_norm(l.plain).lower() == _BANNER for l in rows[:6]):
            continue
        title_at = None
        for i, line in enumerate(rows):
            text = _norm(line.plain)
            if _TITLE.match(text) and text.lower() != _BANNER:
                title_at = i
                break
        if title_at is None:
            continue
        # The opening SENTENCE, not the opening row: mccarty's runs three
        # printed rows before it says which way it goes.
        opening = _norm(" ".join(l.plain
                                 for l in rows[title_at + 1:title_at + 5]))
        kind = _cover_kind(_norm(rows[title_at].plain), opening)
        if kind is None:
            continue
        starts[rows[title_at].id] = kind
        # THE COVER IS EVERY ROW ABOVE THE TITLE, and only those: the title
        # itself is the writing's own heading, and the body opens beneath it
        # on the same page.
        drop.extend(l.id for l in rows[:title_at])
    if not starts:
        return NOTHING
    return {"starts": starts, "drop": drop}


# THE SEAL ON A LATER COVER. Core sends a page-1 seal to the head of the
# headmatter (the user's call, 2026-08-19: "it doesn't need to go into the
# opinion since it's not part of it … just put it at the top centered of the
# headmatter") — but that test is bounded to page 1, so the SAME device
# printed on a dissent's cover eleven pages in failed it, passed the figure
# test instead, and was cropped and planted inside the dissent as though
# Missouri had printed an exhibit. It is the same seal on the same
# stationery: cover matter, recorded as removed. Page 1 keeps core's
# behaviour untouched — this answers only for the later covers.
@decider("image.role", court="mo")
def image_role_mo(model=None, page=None, image=None, **_):
    """A graphic on a stapled paper's own cover is the court's seal."""
    if model is None or page is None or image is None or page.number == 1:
        return NOTHING
    rows = sorted((l for l in page.lines if l.plain.strip()),
                  key=lambda l: l.top)
    if not any(_norm(l.plain).lower() == _BANNER for l in rows[:6]):
        return NOTHING
    title = next((l for l in rows if _TITLE.match(_norm(l.plain))
                  and _norm(l.plain).lower() != _BANNER), None)
    if title is None or image.top > title.top:
        return NOTHING
    return "the court's seal"
