"""Bankruptcy Appellate Panel of the Tenth Circuit ('bap10').

Everything unique to bap10 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'railed ladder', the Tenth Circuit's own stationery set for
a bankruptcy panel. The paper draws its structure twice over, so nothing has
to be read to find it:

  * the CAPTION's column divider is a RULE THE PAGE DRAWS — a vertical rect
    at x=310.9 on a 612pt page (315.2 once, where the party column is set
    wider), 31 of 32 records. Its top and bottom BRACKET the caption
    exactly: the first caption row prints just below the rule's top and the
    fence that closes the caption just below its bottom, so the band needs
    no padding and guesses at no column;
  * every zone below it is FENCED. bap10 sets that fence three ways and all
    three are the same mark — a row of underscores typed on the page axis, a
    252pt rule DRAWN on the same axis, and (cory_markham) a 470.9pt one. The
    axis names it; the measure does not.

        BAP Appeal No. 25-6  Docket No. 25  Filed: …   the CM/ECF band
                                        FILED          the clerk's stamp,
        NOT FOR PUBLICATION¹                           set in its own column
        UNITED STATES BANKRUPTCY       U.S. Bankruptcy at the right edge
          APPELLATE PANEL                Appellate Panel
        OF THE TENTH CIRCUIT             November 10, 2025
        _________________________        Anne Zoltani / Clerk   ← a FENCE
        IN RE AMY LIEBL DARTER,   │  BAP No. WO-25-6   ← the DRAWN rail, the
             Debtor.              │                     panel's own docket
        _________________         │  Bankr. No. 23-11680  and the bankruptcy
        DOUGLAS GOULD, Trustee,   │  Adv. No. 23-1057     court's numbers
             Plaintiff-Appellee,  │  Chapter 7
        v.                        │
        KT WEAVER, …              │  OPINION
             Defendants-Appellants.
        _________________________
        Appeal from the United States Bankruptcy Court   the origin
        for the Western District of Oklahoma
        _________________________
        Submitted on the briefs.²          how the appeal was heard — or,
        _________________________          on the published slip, COUNSEL
        Before ROMERO, Chief Judge, HUNT, and HERREN, Bankruptcy Judges.
        _________________________
        HERREN, Bankruptcy Judge.          the first byline (p.2 usually)

Four measurements do all of the work and none of them reads a word:

  * a CAPTION is what stands between the drawn rail's top and its bottom,
    and its two columns are what stands either side of the rail;
  * a ZONE is what stands between two fences, and a zone is only claimed
    when a fence closes it — what follows the last fence is the writing's;
  * WITHIN a zone the ORIGIN is centred on the page axis and everything
    else the ladder carries — the roster, the appearances, the submission
    statement — is set at the BODY RAIL, so a zone holding both (zachary_rusk
    prints the origin and the submission with no fence between them) splits
    at the alignment change, never at a word;
  * the CLERK'S BOX is a second COLUMN in the masthead, not a stamp to be
    matched by wording. Its rows begin at x>=454 while the banner's and the
    publication flag's begin at x<=303 — a 150pt clear gap.

A COVER is a page that draws a rail AND names the court above it. A record
that draws no rail is not this paper and gets NOTHING: core's shared walk
places those rows unidentified, which is a smaller error than a confident
misreading. (One record — james_perry — draws its rail as a filled PATH
rather than a rect, and pdfio reads curves for horizontal rules only, so its
divider is invisible here. It returns NOTHING and core reads it.)

The reader claims HEADMATTER ONLY. It stops at the first byline, and
everything below — the writings, their footnotes, their paragraphs — is
core's. The FOOTNOTE ZONE is stepped over rather than walked into: bap10
draws the 144pt separator its notes hang under (at the body rail or at the
36pt indent), and on the records whose ladder wraps the page (trak-1's
consolidated caption) the block resumes at the top of the next one.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The bankruptcy panels' shared byline grammar, copied VERBATIM out of the
# `for _bap in (...)` loop bap10 used to sit in, so nothing about its bylines
# changes by being moved here.
BAP10 = register(CourtProfile(
    "bap10", "Bankruptcy Appellate Panel",
    byline=BylineGrammar(
        style="prose", allow_titlecase_name=True,
        # the parser spreads tight punctuation, so 'U.S.' reaches the
        # title match as 'U. S.' — both spellings are declared
        titles=("U. S. Bankruptcy Appellate Panel Judge",
                "U.S. Bankruptcy Appellate Panel Judge",
                "United States Bankruptcy Appellate Panel Judge",
                "Bankruptcy Appellate Panel Judge",
                "Chief Bankruptcy Judge", "Bankruptcy Judge",
                "Chief Judge", "Judge")),
))

STYLE_RAILED_LADDER = "railed ladder"

# ---- bap10's declared facts (measured over the corpus, not tuned) ---------
# THE DRAWN RAIL: the caption's column divider. Measured over 32 records:
# x=310.9 (30 of them), 315.2 (1), absent as a rect on 1 (james_perry draws
# it as a filled path); heights 209.3-481.6. 40pt is a fifth of the shortest
# box and far above any stray tick.
_RAIL_MIN_H = 40.0
_RAIL_X = (0.35, 0.75)          # as a fraction of the page width
# A caption that WRAPS carries its rail to the foot of page 1 and its closing
# fence onto page 2 (trak-1's consolidated pair of appeals).
_MAX_PAGES = 4

# THE FENCE, in the three ways this court sets it. All are centred on the
# page axis; measured centres 303.5-306.1 on a 612pt page, so 20pt is an
# order of magnitude more than the spread and still nowhere near an
# off-axis rule.
_FENCE = re.compile(r"^_{4,}$")
_AXIS_TOL = 20.0
# A DRAWN fence measures 252.0pt (glencove, irene_moden) or 470.9 (cory_
# markham). The publication flag's UNDERLINE is also on the axis and
# measures 54.2-145.1, so a floor at 150 separates them — and the underline
# test below separates them again, because an underline's ends coincide with
# the row it underlines and a fence's do not.
_DRAWN_FENCE_MIN_W = 150.0
_UNDERLINE_GAP = 16.0           # how far under its row an underline sits
_UNDERLINE_TOL = 8.0            # …and how nearly its ends coincide with it

# THE FOOTNOTE SEPARATOR bap10 draws: 144.0pt wide, at the body rail (x0=72)
# or at the 36pt paragraph indent (x0=108) — both occur. Everything at or
# below it on that page is the notes'; the ladder resumes on the next page.
_NOTE_RULE_W = (138.0, 150.0)
_NOTE_RULE_X0 = (0.0, 36.0)
_NOTE_RULE_TOL = 4.0

# THE CLERK'S BOX is the masthead's right-hand COLUMN — the panel's e-filing
# stamp ('FILED / U.S. Bankruptcy Appellate Panel / of the Tenth Circuit /
# November 10, 2025 / Anne Zoltani / Clerk'). Measured: its rows start at
# x>=454.0 and the banner's and flag's at x<=302.8 — a 150pt clear gap, so
# 380 divides them with room to spare either side.
_STAMP_X0 = 380.0
# …and where one line holds both columns, the extractor reports the gap
# between them. Ordinary word spaces on this paper run under 5pt.
_PIECE_GAP = 10.0
# The stamp sets its DATE a step larger than the 8pt panel name (12pt on a
# 13pt body) — the only row of the box that states a fact about the case.
_STAMP_DATE_MIN = 11.0

# THE BODY RAIL is where the roster, the appearances and the submission
# statement are set; the origin and the paper's own name are centred.
_RAIL_TOL = 3.0

# THE PANEL'S OWN DOCKET, as the caption's right column prints it:
# 'BAP No. WO-25-6', 'BAP No. CO-24-009', 'BAP No. NO-21-005'.
_BAP_DOCKET = re.compile(r"^BAP\s+Nos?\.\s*\S", re.I)
# The BANKRUPTCY COURT'S own numbers, printed under it: 'Bankr. No.
# 23-11680', 'Adv. No. 23-1057', 'Adv. Proc. No. 24-8012'.
_LOWER_DOCKET = re.compile(r"^(?:Bankr|Adv)\b[^0-9]*Nos?\.\s*\S", re.I)
# THE CHAPTER the case was filed under — part of the case's identity in a
# bankruptcy caption, printed in the same column as the numbers. It is NOT a
# docket: it names the relief the debtor filed under, and tinting it as one
# claimed a number the row does not carry (user, 2026-08-18).
_CHAPTER = re.compile(r"^Chapter\s+\d+\.?$", re.I)

# THE COURT'S BANNER, both rows and the one-line form.
_BANNER = ("united states bankruptcy appellate panel",
           "of the tenth circuit",
           "united states bankruptcy appellate panel of the tenth circuit")

# THE PUBLICATION FLAG, read with every space squeezed out.
_PUBLISHED = ("publish", "published", "forpublication")
_UNPUBLISHED = ("notforpublication", "unpublished", "donotpublish",
                "notrecommendedforpublication")

# ORIGIN OPENERS — the POSTURE bap10 states above the tribunal it reviews, a
# closed vocabulary of procedural stances (never a court NAME).
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "appeal of", "on appeal of", "on certification from",
    "certification from", "on remand from", "on review of", "review of",
    "petition for review", "on petition for review",
)
# HOW THE APPEAL WAS HEARD — a closed vocabulary of submission postures, the
# same class of fact as the origin opener. bap10 sets it at the body rail
# where the published slip sets its appearances, so the two need telling
# apart: 'Submitted on the briefs.', 'Oral argument …'.
_SUBMISSION_OPENERS = (
    "submitted on", "submitted without", "submitted", "oral argument",
    "argued and submitted", "argued",
)

# BENCH TITLES are a closed role vocabulary — a roster names judges and
# their office, and the office is not a judge.
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
_SUFFIXES = ("JR", "SR", "II", "III", "IV")
_ROSTER_OPENER = "before"
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "applicants", "claimant", "claimants", "party-in-interest", "trustee",
)
# The rule the court TYPES INSIDE THE PARTY COLUMN. It divides the caption's
# own sub-blocks: the bankruptcy case header ('IN RE <debtor>, / Debtor.')
# from the appeal's parties, and one consolidated appeal from the next
# (trak-1 types that one in dashes).
_COLUMN_RULE = re.compile(r"^[-–—_]{4,}$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squeeze(text: str) -> str:
    return "".join(_norm(text).lower().split()).strip(".:*†‡∗")


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") in _BANNER


def _flag(text: str) -> str | None:
    flat = _squeeze(text)
    if not flat or len(flat) > 40:
        return None
    # The flag carries the citation note's own mark ('NOT FOR PUBLICATION1'),
    # so the trailing digit is the note's, not the flag's.
    flat = flat.rstrip("0123456789")
    if flat in _UNPUBLISHED:
        return "unpublished"
    if flat in _PUBLISHED:
        return "published"
    return None


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_submission(text: str) -> bool:
    flat = _norm(text)
    return len(flat) <= 120 and flat.lower().startswith(_SUBMISSION_OPENERS)


def _at_rail(x0: float, body_x0: float) -> bool:
    return abs(x0 - body_x0) <= _RAIL_TOL


# --------------------------------------------------------------------------
# columns — the drawn rail, the clerk's box, and splitting a line at either
# --------------------------------------------------------------------------

def _sub(line, chars: list):
    """The part of ``line`` made of ``chars``, or None when that is nothing.
    Provenance is unchanged: a piece carries its whole line's id, because a
    line is the unit a claim consumes."""
    if not any((c.get("text") or "").strip() for c in chars):
        return None
    if len(chars) == len(line.chars):
        return line
    return _replace(line, chars=chars,
                    x0=min(c["x0"] for c in chars),
                    x1=max(c.get("x1", c["x0"]) for c in chars))


def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the rail, or None. A
    glyph belongs to the side its own MIDPOINT falls on — whether pdfio
    already broke the row at the divider is an accident of how wide the gap
    happened to be."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    return _sub(line, keep)


def _pieces(line) -> list:
    """``line`` broken at the wide gaps the page sets between COLUMNS. The
    masthead is two columns and the extractor sometimes merges a row of one
    with a row of the other; nothing else up there opens a 10pt hole."""
    inked = [c for c in line.chars if (c.get("text") or "").strip()]
    if not inked:
        return []
    inked.sort(key=lambda c: c["x0"])
    runs: list[list] = [[inked[0]]]
    for c in inked[1:]:
        prev = runs[-1][-1]
        if c["x0"] - prev.get("x1", prev["x0"]) > _PIECE_GAP:
            runs.append([c])
        else:
            runs[-1].append(c)
    out = []
    for run in runs:
        piece = _sub(line, run)
        if piece is not None:
            out.append(piece)
    return out


def _rails(model) -> list:
    """The caption dividers the document draws, in page order."""
    out = []
    for pm in model.pages[:_MAX_PAGES]:
        width = pm.width or 612.0
        for r in pm.v_rules:
            if r.height < _RAIL_MIN_H:
                continue
            if not (_RAIL_X[0] <= r.x / width <= _RAIL_X[1]):
                continue
            out.append((pm.number, r))
    out.sort(key=lambda pr: (pr[0], pr[1].top))
    return out


def _note_top(pm, body_x0: float) -> float | None:
    """Where this page draws its footnote separator, or None."""
    tops = [r.top for r in pm.h_rules
            if _NOTE_RULE_W[0] <= r.width <= _NOTE_RULE_W[1]
            and any(abs(r.x0 - body_x0 - off) <= _NOTE_RULE_TOL
                    for off in _NOTE_RULE_X0)]
    return min(tops) if tops else None


def _drawn_fences(pm, rows: list) -> list:
    """The fences this page DRAWS: a rule on the page axis, wide enough not
    to be the publication flag's underline, and whose ends do not coincide
    with the row above it.

    A drawn rule whose ends coincide with the row above is an UNDERLINE, not
    a fence — the same test ca1 needed for its counsel underlines and ca5 for
    its footnote separator, arrived at independently three times.
    """
    width = pm.width or 612.0
    out = []
    for r in pm.h_rules:
        if r.width < _DRAWN_FENCE_MIN_W:
            continue
        if abs((r.x0 + r.x1) / 2 - width / 2) > _AXIS_TOL:
            continue
        if any(0 < r.top - l.top <= _UNDERLINE_GAP
               and abs(l.x0 - r.x0) <= _UNDERLINE_TOL
               for l in rows if l.page == pm.number):
            continue
        out.append(r.top)
    return out


# --------------------------------------------------------------------------
# what the zones say
# --------------------------------------------------------------------------

def _panel_names(text: str) -> list:
    """The judges a roster names.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    'Before ROMERO, Chief Judge, HUNT, and HERREN, Bankruptcy Judges.' names
    three judges and two offices."""
    flat = _norm(text)
    at = flat.lower().find("sitting by")
    if at > 0:
        flat = flat[:at].rstrip(" ,")
    if flat.lower().startswith(_ROSTER_OPENER):
        flat = flat[len(_ROSTER_OPENER):]
    names: list = []
    for chunk in flat.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*†‡∗: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*†‡∗:0123456789 ").strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not
            # another judge.
            if names and name.rstrip(".").upper() in _SUFFIXES:
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _appeal_rows(caption_rows: list) -> list:
    """The caption's rows that state the APPEAL, dropping the bankruptcy
    case header above them.

    bap10's party column is set in sub-blocks divided by a rule the court
    TYPES in the column ('_________' under the debtor, '–––––––' between two
    consolidated appeals). The first sub-block is the bankruptcy case
    ('IN RE AMY LIEBL DARTER, MD, PC, / Debtor.'); the appeal's own parties
    are everything below it. Joined wholesale the case name reads 'IN RE AMY
    LIEBL DARTER, MD, PC v. …', which names the debtor as the appellant.
    """
    blocks: list[list[str]] = [[]]
    for row in caption_rows:
        if _COLUMN_RULE.match(_norm(row)):
            blocks.append([])
        else:
            blocks[-1].append(row)
    if len(blocks) < 2:
        return list(caption_rows)
    tail = [r for b in blocks[1:] for r in b]
    return tail or list(caption_rows)


def _sides(caption_rows: list):
    """The two party names either side of the caption's pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    status labels, the pivot and the rule between sub-blocks are apparatus,
    not names."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat or _COLUMN_RULE.match(flat):
            continue
        first = flat.split()[0].rstrip(".").lower()
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        bare = flat.rstrip(",. *†‡∗").lower()
        # A STATUS LABEL is hyphenated on this court's paper ('Plaintiff -
        # Appellee,'), so the hyphen separates roles the way a space does.
        # A party NAME that carries one survives, because EVERY word has to
        # be a status word for the row to be one.
        words = [w.strip(",.;–-/ ")
                 for w in bare.replace("–", " ").replace("-", " ")
                             .replace("/", " ").split()]
        if words and all(
                w in _STATUS_WORDS or w in ("and", "supporting", "the", "-",
                                            "third", "party", "pro", "se",
                                            "cross", "in", "interest", "of")
                or not w for w in words):
            continue
        if flat.lower().startswith(("v.", "vs.")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    # THE COMMA is the caption's own apparatus — it leads to the status row
    # below. The FULL STOP is not: it ends the abbreviation the party is
    # incorporated under ('BUSCH LAW FIRM, LLC.').
    if not (left and right and seen_pivot):
        return None
    _tail = ", *†‡∗"
    return (_norm(" ".join(left)).rstrip(_tail),
            _norm(" ".join(right)).rstrip(_tail))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="bap10")
def read_headmatter_bap10(model, geom, **_):
    """Read bap10's railed-ladder headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    rails = _rails(model)
    if not rails:
        return NOTHING                    # no caption divider: not bap10's
    width = model.pages[0].width or 612.0
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0

    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(BAP10.byline)
    pages = {pm.number: pm for pm in model.pages}
    pnum = {l.page: pm.number for pm in model.pages for l in pm.lines}

    def PG(line) -> int:
        return pnum.get(line.page, line.page)

    # ---- the rows the block is made of ----------------------------------
    rows: list = []
    all_rows: list = []                   # …including the furniture
    for pm in model.pages[:_MAX_PAGES]:
        cut = _note_top(pm, body_x0)
        for line in pm.lines:
            if not line.plain.strip():
                continue
            all_rows.append(line)
            # THE FOOTNOTE ZONE is the notes', not the ladder's.
            if cut is not None and line.top >= cut:
                continue
            # FURNITURE the page carries into the region: the CM/ECF band
            # across every sheet and the foot folio. Core measures and
            # records those; the reader steps over them rather than claiming
            # them twice.
            if finder.kind(pm, line):
                continue
            rows.append(line)
    rows.sort(key=lambda l: (PG(l), l.top, l.x0))
    if not rows:
        return NOTHING

    bands = [(p, r.top, r.bottom, r.x) for p, r in rails]

    def in_caption(line):
        for p, top, bot, x in bands:
            if PG(line) == p and top < line.top < bot:
                return (p, top, bot, x)
        return None

    # ---- the COVER: a page that draws a rail AND names the court ---------
    rail_top_by_page: dict[int, float] = {}
    for p, r in rails:
        rail_top_by_page.setdefault(p, r.top)
    covers = [p for p in sorted(rail_top_by_page)
              if any(PG(l) == p and l.top < rail_top_by_page[p]
                     and _is_banner(_norm(_masthead_piece(l)))
                     for l in rows)]
    if not covers or covers[0] != rails[0][0]:
        return NOTHING

    crit: dict = {"headmatter_style": STYLE_RAILED_LADDER}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    anchor_ids: list[int] = []
    banner_rows: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    panel_rows: list[str] = []
    counsel_rows: list[str] = []
    submission_rows: list[str] = []
    dockets: list[str] = []
    lower_dockets: list[str] = []
    stamp_lines: list = []
    filed_date: list[str] = []

    def emit(line, role: str, text: str | None = None):
        pm = pages[PG(line)]
        align = line_alignment(line, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        items.append(m.HmLine(
            text=line_markup(line) if text is None else text,
            prov=m.Prov(PG(line), (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    def typed_fence(group: list) -> bool:
        """A row of underscores and nothing else, centred on the page axis.
        Tested on the whole visual ROW: where the drawn rail crosses the
        fence the extractor returns it as two pieces (michael_roberts), and
        each piece alone is off the axis."""
        text = "".join(_norm(l.plain) for l in group)
        if not _FENCE.match(text):
            return False
        x0 = min(l.x0 for l in group)
        x1 = max(l.x1 for l in group)
        return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL

    # ---- the ladder, cover by cover --------------------------------------
    for _n, cover in enumerate(covers):
        nxt = covers[_n + 1] if _n + 1 < len(covers) else None
        head_top = rail_top_by_page[cover]

        # THE COVER'S MARKS: its rows grouped into the VISUAL ROWS the page
        # set, with the fences the page DRAWS interleaved where it draws
        # them. A drawn fence carries no line of its own, so it inherits the
        # provenance of the row above it — core sorts the block back into the
        # page's order by provenance, and an item carrying none sorts to the
        # end (glencove's four fences landed under the roster).
        span_rows = [l for l in rows
                     if (PG(l), l.top) >= (cover, 0.0)
                     and (nxt is None or PG(l) < nxt)]
        marks: list = []                  # (page, top, kind, payload)
        group: list = []
        for line in sorted(span_rows, key=lambda l: (PG(l), l.top, l.x0)):
            if group and PG(group[0]) == PG(line) \
                    and abs(group[0].top - line.top) <= 2:
                group.append(line)
                continue
            if group:
                marks.append((PG(group[0]), group[0].top, "row", group))
            group = [line]
        if group:
            marks.append((PG(group[0]), group[0].top, "row", group))
        for pg in sorted({PG(l) for l in span_rows}):
            for top in _drawn_fences(pages[pg],
                                     [l for l in all_rows if PG(l) == pg]):
                marks.append((pg, top, "drawn-fence", None))
        marks.sort(key=lambda mk: (mk[0], mk[1]))

        # PLANNED FIRST, EMITTED SECOND, because one decision needs the whole
        # ladder: whether the paper SIGNS its writing.
        plan: list = []
        signed = False
        prev_row: list = []               # the row a drawn fence hangs under
        i = 0
        while i < len(marks):
            pg, top, kind, payload = marks[i]
            if kind == "drawn-fence":
                plan.append(("fence-drawn", pg, prev_row))
                i += 1
                continue
            if pg == cover and top < head_top:
                # ---- the masthead: what the page prints above its rail ----
                keep: list = []
                stamped = False
                for line in payload:
                    for piece in _pieces(line):
                        if piece.x0 >= _STAMP_X0:
                            # THE CLERK'S BOX, recorded as the page apparatus
                            # it is, whatever it says — its second row reads
                            # 'U.S. Bankruptcy Appellate Panel', which is
                            # also the banner's first.
                            stamp_lines.append(piece)
                            stamped = True
                            continue
                        keep.append((line, piece))
                if not keep:
                    consumed.update(l.id for l in payload)
                    i += 1
                    continue
                if len(keep) > 1:
                    return NOTHING        # not this masthead's two columns
                line, piece = keep[0]
                text = _norm(piece.plain)
                if typed_fence([piece]):
                    plan.append(("fence-typed", None, [line]))
                elif _is_banner(text):
                    banner_rows.append(text)
                    plan.append(("court", piece, [line]))
                elif _flag(text):
                    crit.setdefault("publication_status", _flag(text))
                    plan.append(("court", piece, [line]))
                else:
                    # An unread masthead row means this is not the cover the
                    # contract describes; core reads the whole document.
                    return NOTHING
                prev_row = payload
                i += 1
                continue
            box = in_caption(payload[0])
            if box is not None:
                j = i
                cap: list = []
                while j < len(marks) and marks[j][2] == "row" \
                        and in_caption(marks[j][3][0]) == box:
                    cap = cap + marks[j][3]
                    prev_row = marks[j][3]
                    j += 1
                plan.append(("caption", box, cap))
                i = j
                continue
            if typed_fence(payload):
                plan.append(("fence-typed", None, payload))
                prev_row = payload
                i += 1
                continue
            if any(parser.parse(_norm(l.plain)) is not None for l in payload):
                signed = True             # a byline ends the reader
                break
            # A ZONE IS WHAT STANDS BETWEEN TWO FENCES, and it is only the
            # block's when a fence CLOSES it: what follows the last fence the
            # court sets is the writing, whatever it looks like.
            j = i
            zone: list = []
            while j < len(marks):
                _pg2, _t2, kind2, pay2 = marks[j]
                if kind2 == "drawn-fence":
                    break
                if in_caption(pay2[0]) is not None or typed_fence(pay2):
                    break
                if any(parser.parse(_norm(l.plain)) is not None
                       for l in pay2):
                    break
                zone.append(pay2)
                j += 1
            closed = j < len(marks) and (
                marks[j][2] == "drawn-fence" or typed_fence(marks[j][3]))
            # A ZONE MAY HOLD TWO LANDMARKS (zachary_rusk prints the origin
            # and the submission statement with no fence between them), and
            # what separates them is the ALIGNMENT: the origin is centred on
            # the page axis, everything else the ladder carries is at the
            # body rail. Split the zone at the change, ask each run once.
            runs = _runs(zone, body_x0)
            roles = [_run_role(run, body_x0) for run in runs]
            # …or the zone is closed by the BYLINE. The roster is the
            # ladder's last rung and the court sometimes leaves it unfenced,
            # running the byline straight in (sean_brewer signs 'PER
            # CURIAM.' one row under 'Before SOMERS, JACOBVITZ, and PARKER,
            # Bankruptcy Judges,'). A ROSTER is safe to claim on a byline,
            # because the byline is where the reader stops anyway; nothing
            # else is, so the relief is granted to that one role and left
            # with an unclaimed zone otherwise.
            if not closed and roles == ["panel"] and j < len(marks) \
                    and marks[j][2] == "row" \
                    and any(parser.parse(_norm(l.plain)) is not None
                            for l in marks[j][3]):
                closed = True
            if not closed:
                break                     # no fence closed it
            for run, role in zip(runs, roles):
                if role is None:
                    return NOTHING        # a run this contract does not name
                plan.append((role, None, run))
            prev_row = zone[-1] if zone else prev_row
            i = j

        for kind, extra, payload in plan:
            if kind == "fence-drawn":
                # A DRAWN fence renders where the page draws it; it consumes
                # no line, and it takes the provenance of the row above so
                # the block keeps the page's order.
                prov = (m.Prov(PG(payload[0]), tuple(l.id for l in payload))
                        if payload else m.Prov(extra))
                items.append(m.Rule(prov=prov, span="full"))
                continue
            if kind == "fence-typed":
                items.append(m.Rule(
                    prov=m.Prov(PG(payload[0]),
                                tuple(l.id for l in payload)),
                    typed=True, span="full"))
                consumed.update(l.id for l in payload)
                continue
            if kind == "court":
                emit(payload[0], "court", text=line_markup(extra))
                continue
            if kind == "caption":
                block, left_plain, right_plain = _caption(
                    payload, extra, pages[extra[0]], geom, body_size)
                if block is None:
                    return NOTHING
                items.append(block)
                consumed.update(block.prov.line_ids)
                caption_rows.extend(t for t in left_plain if t)
                # THE RIGHT COLUMN carries the panel's own docket, the
                # bankruptcy court's numbers, the chapter the case was filed
                # under (case info, not a docket) and the paper's own name —
                # each tagged for what it is, so nothing in the box reads as
                # 'caption' by default.
                for row, flat in zip(block.right, right_plain):
                    if not flat:
                        continue
                    if _BAP_DOCKET.match(flat):
                        row.role = "docket"
                        dockets.append(flat.rstrip("."))
                    elif _LOWER_DOCKET.match(flat):
                        row.role = "lower-court"
                        lower_dockets.append(flat.rstrip("."))
                    elif _CHAPTER.match(flat):
                        row.role = "case-info"
                    elif _squeeze(flat) in ("opinion", "order", "judgment"):
                        row.role = "title"
                        crit.setdefault("title", _norm(flat).rstrip("."))
                    else:
                        caption_rows.append(flat)
                continue
            for row in payload:
                text = _norm(" ".join(l.plain.strip() for l in row))
                for line in row:
                    emit(line, kind)
                if kind == "panel":
                    panel_rows.append(text)
                elif kind == "counsel":
                    counsel_rows.append(text)
                elif kind == "case-info":
                    submission_rows.append(text)
                elif kind == "lower-court":
                    origin_rows.append(text)
                elif kind == "title":
                    crit.setdefault("title", text.rstrip("."))
                    if not signed:
                        anchor_ids.extend(l.id for l in row)

    if not banner_rows:
        return NOTHING                    # bap10 always names itself

    # THE CLERK'S BOX, recorded once as the block of apparatus it is. Its
    # 12pt row is the date the panel filed the decision — a fact the block
    # would otherwise lose, because this paper states no other date.
    if stamp_lines:
        stamp_lines.sort(key=lambda l: (PG(l), l.top, l.x0))
        for piece in stamp_lines:
            if (piece.size or 0) >= _STAMP_DATE_MIN and _is_date(piece.plain):
                filed_date.append(_norm(piece.plain))
        for _pg in sorted({PG(l) for l in stamp_lines}):
            _box = [l for l in stamp_lines if PG(l) == _pg]
            dropped.append(m.Dropped(
                text=_norm(" ".join(l.plain.strip() for l in _box))[:1200],
                prov=m.Prov(_pg, tuple(sorted({l.id for l in _box}))),
                kind="stamp"))
        consumed.update(l.id for l in stamp_lines)

    # ---- what the block says --------------------------------------------
    crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        sides = _sides(_appeal_rows(caption_rows))
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    if dockets:
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit.setdefault("other_dockets", []).extend(dockets[1:])
    if lower_dockets:
        crit.setdefault("other_dockets", []).extend(lower_dockets)
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith(_ROSTER_OPENER):
            roster = roster[len(_ROSTER_OPENER):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    if submission_rows:
        crit["submitted"] = _norm(" ".join(submission_rows))
    if filed_date:
        crit.setdefault("decision_date", filed_date[0])

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")


def _is_date(text: str) -> bool:
    """'November 10, 2025' — the stamp's own date row, read by FORM."""
    flat = _norm(text)
    mm = re.match(r"^([A-Z][a-z]+)\.?\s+\d{1,2},?\s+\d{4}\.?$", flat)
    return bool(mm) and mm.group(1).lower() in _MONTHS


def _masthead_piece(line) -> str:
    """The text of ``line`` OUTSIDE the clerk's column."""
    return " ".join(p.plain for p in _pieces(line) if p.x0 < _STAMP_X0)


def _runs(zone: list, body_x0: float) -> list:
    """``zone`` split into runs of rows that share an ALIGNMENT — at the body
    rail, or off it. The ladder sets the origin centred and everything else
    at the rail, so the change of column is the change of section."""
    out: list = []
    last = None
    for row in zone:
        here = _at_rail(min(l.x0 for l in row), body_x0)
        if last is None or here != last:
            out.append([])
            last = here
        out[-1].append(row)
    return out


def _run_role(run: list, body_x0: float) -> str | None:
    """What a run of same-aligned rows IS, asked once for the whole run.

    The roster, the appearances and the submission statement are the only
    things bap10 sets at the BODY RAIL; the origin and the paper's own name
    are centred on the page axis. Which of the three a rail run is, the
    roster's own opener and the submission's own posture say — two closed
    role vocabularies, never a test on anything a case says."""
    if not run:
        return None
    first = _norm(" ".join(l.plain.strip() for l in run[0]))
    if _at_rail(min(l.x0 for l in run[0]), body_x0):
        if first.lower().startswith(_ROSTER_OPENER):
            return "panel"
        if _is_submission(first):
            # NOT a date: 'Submitted on the briefs.' states the POSTURE the
            # appeal was heard in and carries no date at all. Tinting it as
            # one said the reader had found a date on the page (user,
            # 2026-08-18). It still feeds the `submitted` criterion below.
            return "case-info"
        return "counsel"
    if _origin_opener(first):
        return "lower-court"
    if all(l.all_bold for row in run for l in row):
        return "title"
    return None


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _caption(box_lines: list, box, pm, geom, body_size: float):
    """One caption box as a CaptionBlock, plus each column's plain text.

    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned, and the
    side a glyph belongs to is decided by which side of the DRAWN rail its
    own midpoint falls on."""
    mid = box[3]
    rows: list[list] = []
    for line in sorted(box_lines, key=lambda l: (l.top, l.x0)):
        if rows and abs(rows[-1][0].top - line.top) <= 2:
            rows[-1].append(line)
        else:
            rows.append([line])
    if not rows:
        return None, [], []

    def cell(cells: list):
        parts = sorted(cells, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        align = line_alignment(first, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        return m.HmLine(
            text=text,
            prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role="caption")

    left, right = [], []
    left_plain, right_plain = [], []
    for row in rows:
        l_cells, r_cells = [], []
        for line in row:
            for side, bucket in ((_side(line, mid, "L"), l_cells),
                                 (_side(line, mid, "R"), r_cells)):
                if side is not None:
                    bucket.append(side)
        left.append(cell(l_cells) if l_cells
                    else m.HmLine(text="", prov=m.Prov(pm.number),
                                  role="caption"))
        right.append(cell(r_cells) if r_cells
                     else m.HmLine(text="", prov=m.Prov(pm.number),
                                   role="caption"))
        # THE CRITERIA READ THE PAGE'S OWN TEXT, never the markup: joining
        # the rendered form back into a scalar double-escapes every
        # ampersand the caption prints.
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop()
        right.pop()
        left_plain.pop()
        right_plain.pop()
    block = m.CaptionBlock(
        left=left, right=right, rail="|", rail_rows=len(left),
        fp={"rail": "drawn", "rail_band": (box[1], box[2]), "mid_x": mid},
        prov=m.Prov(pm.number, tuple(sorted(l.id for l in box_lines))))
    return block, left_plain, right_plain
