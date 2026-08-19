"""United States Court of Appeals for the Tenth Circuit ('ca10').

Everything unique to ca10 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'railed ladder'. ca10 sets ONE paper and draws its own
structure twice over, so nothing has to be read to find it:

  * the CAPTION's column divider is a RULE THE PAGE DRAWS — a vertical rect
    at x=310.9 on a 612pt page (347.3 once, where the party column is set
    wider), 103 of 103 records, no exceptions. Its top and bottom BRACKET
    the caption exactly: on every record the first caption row prints just
    below the rule's top and the fence that closes the caption just below
    its bottom, so the band needs no padding and guesses at no column;
  * every zone below it is FENCED by a TYPED RULE — a row of underscores
    and nothing else, centred on the page axis (measured 305.8-307.5 over
    the corpus). The zones come in a fixed order and each is closed by the
    fence under it.

        Appellate Case: 25-5025  Document: 21  …   the CM/ECF band
                                        FILED       the clerk's e-filing
        UNITED STATES COURT OF APPEALS  United States Court of Appeals
        FOR THE TENTH CIRCUIT             Tenth Circuit    box, set in its
        ______________________            July 30, 2026    own column at
        KIANTRE BELCHER,        │         Christopher M.   the right edge
             Petitioner - Appellant,  │   Wolpert
        v.                      │  No. 25-5025     ← a DRAWN rail, and the
        CHRISTIE QUICK, Warden, │  (D.C. No. 4:18-CV-…)  origin cells
             Respondent - Appellee.   │  (N.D. Okla.)     beside it
        ______________________
        ORDER DENYING CERTIFICATE OF APPEALABILITY*   the paper's own name
        ______________________
        Before CARSON, BALDOCK, and KELLY, Circuit Judges.    the roster
        ______________________
        Kiantre Belcher, an Oklahoma prisoner, applies …   the writing

    A PUBLISHED slip prints two more zones between the caption and the
    roster — the origin ('Appeal from the United States District Court /
    for the District of Utah / (D.C. No. 2:21-CV-00582-TC)') and the
    appearances, unlabelled, at the body rail — and signs the writing with
    a byline fenced above and below. Both papers are the same ladder; a
    zone is identified by what stands in it, never by counting fences.

Three measurements do all of the work and none of them reads a word:

  * a CAPTION is what stands between the drawn rail's top and its bottom,
    and its two columns are what stands either side of the rail;
  * a ZONE is what stands between two typed fences, and a zone is only
    claimed when a fence closes it — what follows the last fence is the
    writing's;
  * the CLERK'S BOX is a second COLUMN in the masthead, not a stamp to be
    matched by wording. Its rows begin at x>=405 while the banner's begin
    at x<=278, and on four records the extractor merges the banner row and
    the box's date into one line — split at the column, the two halves go
    to their own zones (the second row of the box READS 'United States
    Court of Appeals', so a text test on the banner catches the stamp).

A COVER is a page that draws a rail AND names the court above it. Normally
there is one; a corrected opinion is stapled behind the errata order that
reissues it and each half carries its own, so the ladder is walked once per
cover. A page whose rail carries a caption that merely WRAPPED onto it has
no banner over it and opens no cover.

A record that draws no rail is not ca10's paper and gets NOTHING: core's
shared walk places those rows unidentified, which is a smaller error than
a confident misreading.

The reader claims HEADMATTER ONLY. It stops at the first byline, and
everything below — the writings, their footnotes, their paragraphs — is
core's. The FOOTNOTE ZONE is stepped over rather than walked into: ca10
draws the 144pt separator its notes hang under, and on the records whose
ladder wraps the page the block resumes at the top of the next one.
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

# The circuits' shared byline grammar, copied VERBATIM out of the
# `_CIRCUIT_GRAMMAR` loop ca10 used to sit in, so nothing about its bylines
# changes by being moved here.
CA10 = register(CourtProfile(
    "ca10", "United States Court of Appeals for the Tenth Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_RAILED_LADDER = "railed ladder"

# ---- ca10's declared facts (measured over the corpus, not tuned) ---------
# THE DRAWN RAIL: the caption's column divider. Measured over 103 records:
# x=310.9 (100 of them), 310.1 (2), 347.3 (1); heights 134.5-568.0. 40pt is
# a third of the shortest box and far above any stray tick.
_RAIL_MIN_H = 40.0
_RAIL_X = (0.35, 0.75)          # as a fraction of the page width
# A consolidated record draws ONE RAIL PER CASE (united_states_v._tew sets
# two boxes on page 1, fenced apart), and a caption that wraps carries its
# rail onto the next page (comanche_nation_v._ware).
_MAX_PAGES = 4

# THE TYPED FENCE: a row of underscores and nothing else, centred on the
# page axis. Measured centres 305.8-307.5 on a 612pt page; 20pt is an order
# of magnitude more than that spread and still nowhere near an off-axis rule.
_FENCE = re.compile(r"^_{4,}$")
_AXIS_TOL = 20.0

# THE FOOTNOTE SEPARATOR ca10 draws: 144.0pt wide at the body rail, on 127
# of the 128 drawn rules in the corpus's first three pages. Everything at or
# below it on that page is the notes' — the ladder resumes on the next page.
_NOTE_RULE_W = (138.0, 150.0)
_NOTE_RULE_X0 = 4.0

# THE CLERK'S BOX is the masthead's right-hand COLUMN. Measured: its rows
# start at x>=405.8 and the banner's at x<=277.4 — a 128pt clear gap, so
# 380 divides them with room to spare either side.
_STAMP_X0 = 380.0
# …and where one line holds both columns, the extractor reports the gap
# between them. The narrowest observed is 13pt; ordinary word spaces on
# this paper run under 5.
_PIECE_GAP = 10.0

# THE BODY RAIL is where the appearances and the roster are set, and
# nothing else in the block is.
_RAIL_TOL = 3.0

# A DOCKET is a FORM, never a wording: 'No. 25-5025', 'No. 24-1465*',
# 'Nos. 24-3133/3206'.
_DOCKET_TAIL = r"(?:[/,;&]\s*(?:\d{2}-)?[\dA-Za-z-]{2,8})*"
_DOCKET = re.compile(r"^Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL
                     + r"\s*[*†‡∗]?\.?$", re.I)
# The tribunal's OWN number, as the origin cell prints it:
# '(D.C. No. 4:18-CV-00018-CVE-JFJ)', '(D.C. Nos. 1:21-CV-00455-WJ-JFR &'.
_LOWER_DOCKET = re.compile(r"Nos?\.\s*\S", re.I)

# THE COURT'S BANNER, both rows and the one-line form.
_BANNER = ("united states court of appeals",
           "for the tenth circuit",
           "united states court of appeals for the tenth circuit")

# THE PUBLICATION FLAG. Read with every space squeezed out: devon_energy
# sets it 'PUBL ISH'.
_PUBLISHED = ("publish", "published", "forpublication")
_UNPUBLISHED = ("notforpublication", "unpublished", "donotpublish",
                "notrecommendedforpublication")

# ORIGIN OPENERS — the POSTURE ca10 states above the tribunal it reviews, a
# closed vocabulary of procedural stances (never a court NAME). Both cases
# occur: the published slip sets the band in caps on part of the corpus.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "petition for review", "petitions for review",
    "on petition for review", "on petitions for review",
    "petition for review of", "on remand from", "on review of", "review of",
    "on petition for rehearing", "on petitions for rehearing",
    "appeal of", "on appeal of", "on certification from",
    "certification from", "on petition for writ", "petition for writ",
    "on application for", "application for",
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
    "applicants", "claimant", "claimants", "party-in-interest",
)
# The caption's own divider between consolidated cases: a row of dashes the
# court types in the party column ('–––––––' / '-------').
_CASE_RULE = re.compile(r"^[-–—_]{4,}$")


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
    if flat in _UNPUBLISHED:
        return "unpublished"
    if flat in _PUBLISHED:
        return "published"
    return None


def _is_fence(line, width: float) -> bool:
    return bool(_FENCE.match(_norm(line.plain))
                and abs((line.x0 + line.x1) / 2 - width / 2) <= _AXIS_TOL)


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _at_rail(line, body_x0: float) -> bool:
    return abs(line.x0 - body_x0) <= _RAIL_TOL


def _is_docket(text: str) -> bool:
    return bool(_DOCKET.match(_norm(text)))


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
    with a row of the other; nothing else on this paper opens a 10pt hole."""
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


def _masthead_piece(line) -> str:
    """The text of ``line`` OUTSIDE the clerk's column. The masthead is two
    columns and the extractor sometimes merges a banner row with the box's
    date; the banner is what stands left of the box."""
    return " ".join(p.plain for p in _pieces(line) if p.x0 < _STAMP_X0)


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
            and abs(r.x0 - body_x0) <= _NOTE_RULE_X0]
    return min(tops) if tops else None


# --------------------------------------------------------------------------
# what the zones say
# --------------------------------------------------------------------------

def _panel_names(text: str) -> list:
    """The judges a roster names.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    'Before HOLMES, Chief Judge, EBEL, and CARSON, Circuit Judges.' names
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
            name = part.strip().strip(".*†‡∗: ").strip()
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


def _sides(caption_rows: list):
    """The two party names either side of the caption's pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    status labels, the pivot and the rule between consolidated cases are
    apparatus, not names."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat or _CASE_RULE.match(flat):
            continue
        first = flat.split()[0].rstrip(".").lower()
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        # A FOOTNOTE MARK ON A STATUS ROW belongs to the note, not to the
        # party ('Respondent.*' — the substitution note on an immigration
        # petition), so it is stripped before the role test.
        bare = flat.rstrip(",. *†‡∗").lower()
        # A STATUS LABEL is hyphenated on this court's paper ('Petitioner -
        # Appellant,'), so the hyphen separates roles the way a space does.
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
    # incorporated under ('OL PRIVATE COUNSEL, LLC.').
    if not (left and right and seen_pivot):
        return None
    _tail = ", *†‡∗"
    return (_norm(" ".join(left)).rstrip(_tail),
            _norm(" ".join(right)).rstrip(_tail))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ca10")
def read_headmatter_ca10(model, geom, **_):
    """Read ca10's railed-ladder headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    rails = _rails(model)
    if not rails:
        return NOTHING                    # no caption divider: not ca10's
    width = model.pages[0].width or 612.0
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0

    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(CA10.byline)
    pages = {pm.number: pm for pm in model.pages}
    # A STAPLED RECORD IS EXTRACTED PART BY PART, and core renumbers each
    # part's pages from 1 while the lines keep the PDF's own numbering. The
    # page a row belongs to is therefore the page that HOLDS it, never the
    # number the row remembers.
    pnum = {l.page: pm.number for pm in model.pages for l in pm.lines}

    def PG(line) -> int:
        return pnum.get(line.page, line.page)

    # ---- the rows the block is made of ----------------------------------
    rows: list = []
    furniture_fences: set[int] = set()
    for pm in model.pages[:_MAX_PAGES]:
        cut = _note_top(pm, body_x0)
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # THE FOOTNOTE ZONE is the notes', not the ladder's: ca10 draws
            # the separator they hang under, and on the records whose ladder
            # wraps the page the block resumes at the top of the next one.
            if cut is not None and line.top >= cut:
                continue
            # FURNITURE the page carries into the region: the CM/ECF band
            # and the foot folio. Core measures and records those; the
            # reader steps over them rather than claiming them twice.
            if finder.kind(pm, line):
                # …but A FENCE STILL CLOSES ITS ZONE. A ladder that wraps
                # prints its next fence at the top of the following page,
                # where core's repeated-top-key measurement reads the
                # identical row of underscores as a running head. The row
                # stays core's — recorded as removed, never claimed — while
                # the zone it closes is still closed by it.
                if _is_fence(line, pm.width or 612.0):
                    furniture_fences.add(line.id)
                    rows.append(line)
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

    # ---- the COVERS: a page that draws a rail AND names the court ---------
    # A ca10 record is normally one document with one cover, but a corrected
    # opinion is STAPLED behind the errata order that reissues it and each
    # half carries its own. A page whose rail stands under the court's own
    # banner opens a cover; a page whose rail carries a caption that merely
    # WRAPPED onto it does not (comanche_nation's parties run past the foot
    # of page 1 and its second rail has nothing above it).
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
    dockets: list[str] = []
    lower_dockets: list[str] = []
    tribunals: list[str] = []
    stamp_lines: list = []
    filed_date: list[str] = []

    def emit(line, role: str, text: str | None = None):
        pm = pages[PG(line)]
        align = line_alignment(line, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        # NO REL OFFSET: every row of this block is either centred on the
        # page axis, set at the body rail, or inside the caption box, so a
        # column offset would be an invention.
        items.append(m.HmLine(
            text=line_markup(line) if text is None else text,
            prov=m.Prov(PG(line), (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    def fence(line):
        if line.id in furniture_fences:
            return                        # core recorded it as removed
        items.append(m.Rule(prov=m.Prov(PG(line), (line.id,)),
                            typed=True, span="full"))
        consumed.add(line.id)

    # ---- each cover, in the page's own order -----------------------------
    for _n, cover in enumerate(covers):
        nxt = covers[_n + 1] if _n + 1 < len(covers) else None
        head_top = rail_top_by_page[cover]

        # ---- the masthead: what the cover page prints above its rail ------
        for line in rows:
            if PG(line) != cover or line.top >= head_top:
                continue
            keep: list = []
            for piece in _pieces(line):
                if piece.x0 >= _STAMP_X0:
                    # THE CLERK'S BOX: the court's e-filing stamp, set in
                    # its own column. Recorded as removed page apparatus,
                    # whatever it says — its second row reads 'United States
                    # Court of Appeals', which is also the banner's first.
                    stamp_lines.append(piece)
                    continue
                keep.append(piece)
            if not keep:
                consumed.add(line.id)
                continue
            if len(keep) > 1:
                return NOTHING            # not this masthead's two columns
            piece = keep[0]
            text = _norm(piece.plain)
            if _is_fence(piece, width):
                fence(line)
            elif _is_banner(text):
                banner_rows.append(text)
                emit(line, "court", text=line_markup(piece))
            elif _flag(text):
                crit.setdefault("publication_status", _flag(text))
                emit(line, "court", text=line_markup(piece))
            else:
                # An unread masthead row means this is not the cover the
                # contract describes; core reads the whole document instead.
                return NOTHING

        # ---- the ladder: caption boxes and fenced zones -------------------
        # PLANNED FIRST, EMITTED SECOND, because one decision needs the whole
        # ladder: whether the paper SIGNS its writing. ca10's unpublished
        # order names itself ('ORDER AND JUDGMENT') and then runs straight in
        # with no byline at all, and that name is the only thing its writing
        # can anchor on — claimed into the block it costs the document its
        # opening.
        tail = [l for l in rows
                if (PG(l), l.top) > (cover, head_top)
                and (nxt is None or PG(l) < nxt)]
        plan: list = []
        signed = False
        i = 0
        while i < len(tail):
            line = tail[i]
            box = in_caption(line)
            if box is not None:
                j = i
                while j < len(tail) and in_caption(tail[j]) == box:
                    j += 1
                plan.append(("caption", box, tail[i:j]))
                i = j
                continue
            if _is_fence(line, width):
                plan.append(("fence", line))
                i += 1
                continue
            if parser.parse(_norm(line.plain)) is not None:
                signed = True             # a byline ends the reader
                break
            # A ZONE IS WHAT STANDS BETWEEN TWO FENCES, and it is only the
            # block's when a fence CLOSES it: what follows the last fence
            # the court types is the writing, whatever it looks like.
            j = i
            while j < len(tail) and not _is_fence(tail[j], width) \
                    and in_caption(tail[j]) is None \
                    and parser.parse(_norm(tail[j].plain)) is None:
                j += 1
            if j >= len(tail) or not _is_fence(tail[j], width):
                break                     # no fence closed it
            role = _zone_role(tail[i:j], body_x0)
            if role is None:
                break                     # a zone this contract does not name
            plan.append((role, tail[i:j]))
            i = j

        for entry in plan:
            if entry[0] == "fence":
                fence(entry[1])
                continue
            if entry[0] == "caption":
                _, box, box_lines = entry
                block, left_plain, right_plain = _caption(
                    box_lines, box, pages[box[0]], geom, body_size)
                if block is None:
                    return NOTHING
                items.append(block)
                consumed.update(block.prov.line_ids)
                caption_rows.extend(t for t in left_plain if t)
                # THE RIGHT COLUMN carries the docket and the origin cells,
                # each tagged for what it is — nothing in the box reads as
                # 'caption' by default.
                for row, flat in zip(block.right, right_plain):
                    if not flat:
                        continue
                    if _is_docket(flat):
                        row.role = "docket"
                        dockets.append(flat.rstrip(".").rstrip("*†‡∗"))
                    elif _LOWER_DOCKET.search(flat):
                        row.role = "lower-court"
                        lower_dockets.append(flat)
                    elif flat.startswith("(") and len(flat) <= 40:
                        row.role = "lower-court"
                        tribunals.append(flat.strip("()"))
                    else:
                        caption_rows.append(flat)
                continue
            role, zone = entry
            if role == "title":
                # THE PAPER'S OWN NAME. On an unsigned order it is also the
                # only thing that writing can anchor on, so its ids go to the
                # rescue anchor: claimed, but returned to the stream if the
                # claim would otherwise leave the document with no writing.
                crit.setdefault(
                    "title", _norm(zone[0].plain).rstrip("*†‡∗ "))
                if not signed:
                    anchor_ids.extend(l.id for l in zone)
            for l2 in zone:
                text = _norm(l2.plain)
                emit(l2, role)
                if role == "panel":
                    panel_rows.append(text)
                elif role == "counsel":
                    counsel_rows.append(text)
                elif role == "lower-court":
                    if _LOWER_DOCKET.search(text) and text.startswith("("):
                        lower_dockets.append(text)
                    else:
                        origin_rows.append(text)

    if not banner_rows:
        return NOTHING                    # ca10 always names itself

    # THE CLERK'S BOX, recorded once as the block of apparatus it is. Its
    # 14pt row is the date the court filed the decision — the only date the
    # paper states, and a fact the block would otherwise lose.
    if stamp_lines:
        stamp_lines.sort(key=lambda l: (PG(l), l.top, l.x0))
        for piece in stamp_lines:
            # The box sets its DATE a step larger than everything else in
            # it (14pt against 12 on a 13pt body) — that is the only row of
            # the stamp that states a fact about the decision.
            if (piece.size or 0) >= body_size + 1.0:
                filed_date.append(_norm(piece.plain))
        for _pg in sorted({PG(l) for l in stamp_lines}):
            _box = [l for l in stamp_lines if PG(l) == _pg]
            dropped.append(m.Dropped(
                text=_norm(" ".join(l.plain.strip() for l in _box))[:1200],
                prov=m.Prov(_pg, tuple(sorted({l.id for l in _box}))),
                kind="stamp"))
        consumed.update(l.id for l in stamp_lines)

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        sides = _sides(caption_rows)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    if dockets:
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit["other_dockets"] = dockets[1:]
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    elif tribunals:
        crit["lower_court"] = _norm(" ".join(tribunals))
    if lower_dockets:
        crit.setdefault("other_dockets", []).extend(
            _norm(d).strip("()") for d in lower_dockets)
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith(_ROSTER_OPENER):
            roster = roster[len(_ROSTER_OPENER):].lstrip(": ")
        # THE PRINTED FORM keeps the roster's footnote mark; the PARSED one
        # does not — the mark belongs to the note, not to the bench.
        crit["judges"] = roster.rstrip("*†‡∗ ") or roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    if filed_date:
        crit.setdefault("decision_date", filed_date[0])

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


def _zone_role(zone: list, body_x0: float) -> str | None:
    """What the zone between two fences IS, asked once for the whole band.

    The roster and the appearances are the only zones ca10 sets at the BODY
    RAIL; everything else in the ladder is centred on the page axis. Which
    of the two a rail zone is, the roster's own opener says. A centred zone
    states either the POSTURE the case arrives on or the paper's own name,
    and the posture is a closed vocabulary of procedural stances."""
    if not zone:
        return None
    first = _norm(zone[0].plain)
    if first.lower().startswith(_ROSTER_OPENER):
        return "panel"
    if all(_at_rail(l, body_x0) for l in zone):
        return "counsel"
    if not all(l.all_bold for l in zone):
        return None
    return "lower-court" if _origin_opener(first) else "title"


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
