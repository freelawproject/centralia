"""Bankruptcy Appellate Panel of the Ninth Circuit ('bap9').

Everything unique to bap9 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'shelved cover'. The panel DRAWS its caption's structure
with two horizontal rules and nothing else. Both start at the body rail and
run 268pt — a little under half a 612pt measure — and they are the only
rules of that measure on the sheet (the footnote separator under them is
144pt at the same rail, and nothing else is drawn at all). They are
SHELVES: the upper one closes the bankruptcy case's own style, the lower
one closes the appeal's parties, and THEIR RIGHT END IS THE CAPTION'S
COLUMN BOUNDARY — everything left of it is the party column, everything
right of it the panel's docket, the bankruptcy court's own numbers, and
the one bold cell that says what the paper is.

    FILED                              the clerk's stamp, the only ARIAL
    NOV 19 2025                          on a sheet set in Palatino
    SUSAN M. SPRAUL, CLERK
    U.S. BKCY. APP. PANEL
    OF THE NINTH CIRCUIT
    NOT FOR PUBLICATION                the publication flag, 16pt bold
    UNITED STATES BANKRUPTCY           the banner, 14pt bold, two rows
    APPELLATE PANEL
    OF THE NINTH CIRCUIT
    In re:                  BAP No. NV-25-1026-BCN      the panel's docket
    MP REORGANIZATION,      Bk. No. 22-14422-nmc        the court below's
         Debtor.            Adv. No. 23-01093-nmc         own numbers
    ────────────────────                               THE UPPER SHELF
    RYAN DREXLER,           MEMORANDUM*                what the paper IS
    v.     Appellant,                                    (the only BOLD
    EMPERY TAX EFFICIENT, LP,                             cell in the box)
         Appellee.
    ────────────────────                               THE LOWER SHELF
    Appeal from the United States Bankruptcy Court     the origin — a
    for the District of Nevada                           BANKRUPTCY court
    Natalie M. Cox, Chief Bankruptcy Judge, Presiding    and who tried it
    APPEARANCES                                        (11 of 32 records)
    Amy N. Tirre … argued for appellants; …
    Before: BRAND, CORBIT, and NIEMANN, Bankruptcy Judges.   the roster
    Memorandum by Judge Brand                          who wrote what
    Dissent by Judge Corbit                              (5 of 32)
    BRAND, Bankruptcy Judge:                           a byline, on the
    INTRODUCTION                                         6 SIGNED records

WHERE A WRITING STARTS, on this court's paper, is NOT marked by a byline.
26 of the 32 records are the panel's own unsigned MEMORANDUM and open
straight into a centred bold 'INTRODUCTION' (debbie_reid_ogorman opens
into plain prose at the paragraph indent, with no heading at all); the
other six are signed. So the reader cannot stop at 'the first byline' and
be done — it stops at THE FIRST ROW THIS CONTRACT DOES NOT NAME, which is
that heading, that prose, or that byline, whichever the record prints. It
never reaches into what follows.

WHY CORE COULD NOT READ IT. The origin's third row is
'Noah G. Hillen, Chief Bankruptcy Judge, Presiding' — and under the
panels' declared byline grammar that parses as a byline (name, title, kind
'Presiding'). Core anchored every one of the 32 records' writings on the
BANKRUPTCY judge's name, swallowed the panel roster into the opinion's
first paragraph, and lost the per curiam. The band is the unit of meaning
here, as it is on ca4's fenced paper: the origin is opened by its own
statement and the rows under it belong to that band whatever they parse as
alone.

Two measurements do the rest and neither reads a word:

  * A BAND is what a 24pt gap separates. The court sets 18.9pt between the
    rows of one statement and 30.8–37.9pt between statements, everywhere on
    the corpus; the body's own leading is 28.3pt, so no body row can ever
    join a headmatter band.
  * THE CLERK'S STAMP IS A TYPEFACE. The opinion is set in Palatino
    Linotype throughout and the stamp is the only Arial on the sheet — page
    1 of all 32 records, no page after it, nothing else. Position cannot do
    this job: the stamp's rows share baselines with the banner and the
    flag, so pdfio hands back one line reading 'UNITED STATES BANKRUPTCY
    APPELLATE PANEL OF THE NINTH CIRCUIT' (miomni) with the stamp's third
    row welded onto the banner's first.

A record that draws no shelf pair is not this court's paper and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

The reader claims HEADMATTER ONLY, and nothing is lifted out of it — the
appearances stay where the page prints them, their text copied into the
criteria.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The bankruptcy panels' shared byline grammar, copied VERBATIM out of the
# `_bap` loop bap9 used to sit in, so nothing about its bylines changes by
# being moved here.
BAP9 = register(CourtProfile(
    "bap9", "Bankruptcy Appellate Panel of the Ninth Circuit",
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

STYLE_SHELVED = "shelved cover"

# ---- bap9's declared facts (measured over the corpus, not tuned) ---------
# THE SHELVES: drawn at the body rail, 267.6–275.2pt wide over the 32
# records. The window is wide enough for the widest and far clear of the
# 144pt footnote separator drawn at the same rail.
_SHELF_W = (250.0, 290.0)
# How far a shelf's x0 may sit from the measured body rail. The sheet's
# origin drifts (63.4 → 72.0) and pdfio reports the rule 0.2–0.7pt off it;
# one record draws its lower shelf 0.7pt left of its upper one.
_RAIL_SLOP = 3.0
# THE COLUMN BOUNDARY is the shelves' right end. The right column's own
# runs start 4.5–6pt beyond it; nothing in the left column reaches it.
_SPLIT_SLOP = 2.0
# ONE CAPTION ROW is one baseline. The court lifts the pivot a hair above
# the status label it shares a line with ('v .' at 334.5, 'Appellant,' at
# 336.7 — james_slade, miomni, mp_reorganization), so the pairing window
# has to clear 2.2pt.
_ROW_SLOP = 3.0
# A BAND is what a 24pt gap separates: 18.9pt inside a statement,
# 30.8–37.9pt between statements, 28.3pt between body lines.
_BAND_GAP = 24.0
# THE FOOTNOTE SEPARATOR: 144pt at the body rail. Rows below it on a page
# are notes, not headmatter — they are core's, and the reader must not
# mistake one for the row that ends the block.
_SEP_W = 144.0
_SEP_SLOP = 4.0
# CENTRING, measured inside the cover: the flag, the banner and the origin
# all put their midpoint within 1pt of the sheet's axis; every other row
# the reader claims stands at the body rail.
_CENTER_SLOP = 8.0
# How far the headmatter may run. matheson fills page 1 with its caption
# and states who wrote what, and signs, at the top of page 2.
_MAX_PAGES = 3
# THE CLERK'S STAMP is the only Arial on a sheet set in Palatino Linotype.
_STAMP_FACE = "Arial"
_STAMP_DATE = re.compile(r"\b([A-Z]{3,9}\.?\s+\d{1,2},?\s+\d{4})\b")

# HOW THE PANEL NUMBERS A CASE — its own docket, and the two numbers the
# bankruptcy court below assigned. A closed vocabulary of the court's own
# numbering labels; no party or court NAME is ever read by wording.
_BAP_DOCKET = re.compile(r"^BAP\s+Nos?\.", re.I)
_LOWER_DOCKET = re.compile(r"^(?:Bk\.|Bky\.|Adv\.|BK|Adv)\s*Nos?\.", re.I)
# HOW THE PANEL NAMES THE COURT IT REVIEWS.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "appeal of", "appeals of", "on remand from", "on review of",
    "on petition for review", "on petitions for review",
)
# THE APPEARANCES LABEL, as this clerk sets it (with and without a colon).
_LABEL_COUNSEL = ("APPEARANCES",)
# WHO WROTE WHAT — the panel's own formula, one statement per row. The
# paper kinds are a closed vocabulary; the judge named after them is not
# read at all.
_DESCRIPTOR_OPENERS = (
    "memorandum by", "opinion by", "amended opinion by", "order by",
    "concurrence by", "dissent by", "partial concurrence by",
    "partial dissent by", "concurrence and dissent by",
    "partial concurrence and partial dissent by",
    "concurrence and partial dissent by",
)
# THE PUBLICATION FLAG, read on its stem so both forms answer alike.
_UNPUBLISHED = "not for publication"
_PUBLISHED = "ordered published"
# BENCH WORDS — a closed role vocabulary, used to keep a title out of the
# roster's list of names.
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. 'Trustee' is deliberately NOT here: on this court's paper it is
# part of the party's name ('TIMOTHY W. HOFFMAN, Chapter 7 / Trustee,'),
# and dropping it renames the party.
_STATUS_WORDS = frozenset((
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "applicants", "claimant", "claimants", "creditor", "creditors",
    "interested",
))
_STATUS_GLUE = frozenset((
    "and", "the", "party", "parties", "in", "of", "interest", "pro", "se",
    "cross", "third", "supporting", "", "-",
))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _bare(text: str) -> str:
    """The row with the court's own reference marks off it. The disposition
    label carries the footnote that states why it is unpublished."""
    return _norm(text).strip(" .:;*∗†‡")


def _is_flag(text: str) -> str | None:
    low = _norm(text).lower().rstrip(" .*∗")
    if low.startswith(_UNPUBLISHED):
        return "unpublished"
    if low.startswith(_PUBLISHED):
        return "published"
    return None


def _is_banner(text: str) -> bool:
    low = _bare(text).lower()
    return low in ("united states bankruptcy appellate panel",
                   "of the ninth circuit",
                   "united states bankruptcy appellate panel of the "
                   "ninth circuit")


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().startswith(_ORIGIN_OPENERS)


def _is_counsel_label(text: str) -> bool:
    return _bare(text).upper() in _LABEL_COUNSEL


def _is_descriptor(text: str) -> bool:
    low = _bare(text).lower()
    return len(low) <= 80 and low.startswith(_DESCRIPTOR_OPENERS)


def _opens_landmark(text: str) -> bool:
    return bool(_origin_opener(text) or _is_counsel_label(text)
                or _is_descriptor(text)
                or _norm(text).lower().startswith("before"))


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test. A
    judge sitting by designation carries a reference mark ('PEARSON,1'),
    which is apparatus and not part of the name."""
    body = _norm(text)
    for opener in ("before:", "before"):
        if body.lower().startswith(opener):
            body = body[len(opener):]
            break
    names: list = []
    for chunk in body.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*∗: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*∗: ").strip()
            name = re.sub(r"[\d*∗†‡]+$", "", name).strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not
            # another judge.
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _sides(caption_rows: list, one_sided: bool = False):
    """The party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale —
    the status labels and the pivot are apparatus, not names."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        first = flat.split()[0].rstrip(".").lower() if flat.split() else ""
        # The clerk spaces the pivot on part of the corpus ('v .').
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        bare = flat.rstrip(",. ").lower()
        words = [w.strip(",.;–-/ ")
                 for w in bare.replace("–", " ").replace("-", " ")
                              .replace("/", " ").split()]
        if words and all(w in _STATUS_WORDS or w in _STATUS_GLUE
                         for w in words):
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
    # incorporated under ('MANN MORTGAGE, LLC.'), and stripping it renames
    # the party.
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the shelves — bap9's caption fences, and the dispatch
# --------------------------------------------------------------------------

def _shelves(pm, body_x0: float) -> list:
    """The page's caption shelves as (top, x1), in the order drawn.

    A rule is a shelf when it starts at the body rail and runs the shelf
    measure. Both tests are needed: the footnote separator starts at the
    same rail and is 144pt, and no other rule is drawn on the sheet."""
    found = [(r.top, r.x1) for r in pm.h_rules
             if abs(r.x0 - body_x0) <= _RAIL_SLOP
             and _SHELF_W[0] <= r.width <= _SHELF_W[1]]
    return sorted(found)


def _notes_top(pm, body_x0: float) -> float:
    """Where this page's footnotes begin, or the page's foot. A reader that
    claims a region does NOT claim the notes under it."""
    tops = [r.top for r in pm.h_rules
            if abs(r.x0 - body_x0) <= _RAIL_SLOP
            and abs(r.width - _SEP_W) <= _SEP_SLOP]
    return min(tops) if tops else float(pm.height)


def _is_stamp_char(char) -> bool:
    return _STAMP_FACE in (char.get("fontname") or "")


def _shed_stamp(line):
    """``line`` with the clerk's stamp taken off it, or None when the line
    WAS the stamp — plus the stamp's own chars.

    The stamp shares baselines with the banner and the flag, so a
    whole-line test cannot classify what pdfio returns; splitting by char
    can, and the typeface is the split."""
    stamp = [c for c in line.chars if _is_stamp_char(c)]
    if not stamp:
        return line, []
    kept = [c for c in line.chars if not _is_stamp_char(c)]
    if not any((c.get("text") or "").strip() for c in kept):
        return None, stamp
    x0 = min(c["x0"] for c in kept)
    x1 = max(c.get("x1", c["x0"]) for c in kept)
    return _replace(line, chars=kept, x0=x0, x1=x1), stamp


def _stamp_rows(chars: list) -> list:
    """The stamp's chars read back as the rows the clerk set them in.

    By the time the line builder has split runs at their x-gaps — and, on
    five records, interleaved two of the stamp's rows into one line — the
    stamp survives only as fragments. Grouping the raw chars by BASELINE
    puts them back."""
    from ..pdfio.text import plain_text
    rows: dict = {}
    for char in chars:
        rows.setdefault(round(char.get("top", 0)), []).append(char)
    out = []
    for top in sorted(rows):
        text = _norm(plain_text(sorted(rows[top],
                                       key=lambda c: c.get("x0", 0))))
        if text:
            out.append(text)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="bap9")
def read_headmatter_bap9(model, geom, **_):
    """Read bap9's shelved cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    shelves = _shelves(page1, body_x0)
    if len(shelves) != 2:
        return NOTHING                    # no shelf pair: not bap9's paper
    split_x = max(x1 for _t, x1 in shelves)
    cap_end = shelves[-1][0]

    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(BAP9.byline)
    pages = {pm.number: pm for pm in model.pages}

    rows: list = []                       # content lines, in page order
    stamp_all: list = []                  # every stamp char on page 1
    stamp_mine: list = []                 # …the ones core left behind
    stamp_ids: set[int] = set()
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if pm.number == 1:
                stamp_all.extend(c for c in line.chars if _is_stamp_char(c))
            # FURNITURE core already measured and recorded — the stamp rows
            # it recognized, the foot folio. The reader steps over those
            # rather than claiming them twice.
            if finder.kind(pm, line):
                continue
            if pm.number == 1:
                kept, shed = _shed_stamp(line)
                if shed:
                    stamp_mine.extend(shed)
                    stamp_ids.add(line.id)
                if kept is None:
                    continue              # the line WAS the stamp
                line = kept
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING

    # THE CAPTION ZONE opens at the first baseline that carries a genuine
    # second column — a run starting beyond the shelves' right end. That is
    # what separates the caption from the banner above it, which crosses the
    # same boundary but does so as one unbroken run of text.
    starts = [l.top for l in rows
              if l.page == 1 and l.top < cap_end
              and l.x0 >= split_x - _SPLIT_SLOP]
    if not starts:
        return NOTHING
    cap_start = min(starts)
    if not any(_is_banner(l.plain) for l in rows
               if l.page == 1 and l.top < cap_start):
        return NOTHING                    # bap9 always names itself

    crit: dict = {"headmatter_style": STYLE_SHELVED}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    banner_rows: list[str] = []
    debtor_rows: list[str] = []
    party_rows: list[str] = []
    origin_rows: list[str] = []
    panel_rows: list[str] = []
    counsel_rows: list[str] = []
    descriptor_rows: list[str] = []
    dockets: list[str] = []
    lower_dockets: list[str] = []
    titles: list[str] = []

    def align_of(line, pm):
        """The cover sets exactly two alignments: a display row centred on
        the sheet's axis, and prose flush at the body rail."""
        mid = (line.x0 + line.x1) / 2.0
        if (line.x0 > body_x0 + 3.0
                and abs(mid - (pm.width or 612.0) / 2.0) <= _CENTER_SLOP):
            return m.Align.CENTER
        return m.Align.LEFT

    def emit(line, role: str, pm):
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=align_of(line, pm), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    # ---- the masthead: everything page 1 prints above the caption -------
    for line in rows:
        if line.page != 1 or line.top >= cap_start - _ROW_SLOP:
            continue
        text = _norm(line.plain)
        flag = _is_flag(text)
        if flag:
            crit.setdefault("publication_status", flag)
            emit(line, "court", page1)
        elif _is_banner(text):
            banner_rows.append(_bare(text))
            emit(line, "court", page1)
        else:
            # An unread masthead row means this is not the cover the
            # contract describes; core reads the whole document instead.
            return NOTHING

    # ---- the caption: two blocks, one per shelf -------------------------
    for at, (shelf_top, _x1) in enumerate(shelves):
        lo = cap_start - _ROW_SLOP if at == 0 else shelves[at - 1][0]
        box = [l for l in rows
               if l.page == 1 and lo < l.top <= shelf_top]
        block, left_plain = _caption(box, split_x, page1, align_of)
        if block is None:
            return NOTHING
        items.append(block)
        consumed.update(block.prov.line_ids)
        (debtor_rows if at == 0 else party_rows).extend(
            t for t in left_plain if t)
        # THE RIGHT COLUMN is grouped by the label that opens each cell: a
        # cell that opens none continues the group above it (a second BAP
        # number, or the parenthetical that says the appeals are related).
        group = None
        for row in block.right:
            flat = _norm(_strip_tags(row.text))
            if not flat:
                continue
            if row.bold:
                # WHAT THE PAPER IS, in the only BOLD cell in the box.
                titles.append(_bare(flat).upper())
                row.role = "title"
                group = None
            elif _BAP_DOCKET.match(flat):
                dockets.append(flat)
                row.role = "docket"
                group = "docket"
            elif _LOWER_DOCKET.match(flat):
                lower_dockets.append(flat)
                row.role = "lower-court"
                group = "lower"
            elif group == "docket":
                dockets.append(flat)
                row.role = "docket"
            elif group == "lower":
                lower_dockets.append(flat)
                row.role = "lower-court"
            else:
                party_rows.append(flat)
        # A READER THAT CLAIMS THE REGION INHERITS THE COURT'S DRAWING: the
        # shelf renders where the page draws it, over the column it spans.
        # Core only draws it for rows the reader left behind.
        items.append(m.Rule(prov=block.prov, span="left"))

    # ---- the bands below the lower shelf --------------------------------
    stop = False
    state = "cover"
    for pm in model.pages[:_MAX_PAGES]:
        if stop:
            break
        notes = _notes_top(pm, body_x0)
        free = [l for l in rows
                if l.page == pm.number and l.id not in consumed
                and l.top < notes
                and (pm.number > 1 or l.top > cap_end)]
        if not free:
            continue
        # THE BAND IS THE UNIT OF MEANING, not the row: the origin states
        # the court, the district and the judge who tried it on three rows
        # of one statement, and the third of them parses as a byline.
        bands: list = [[free[0]]]
        for a, b in zip(free, free[1:]):
            if (b.top - a.top) <= _BAND_GAP:
                bands[-1].append(b)
            else:
                bands.append([b])
        for band in bands:
            first = _norm(band[0].plain)
            printed = _norm(" ".join(_norm(l.plain) for l in band))
            if _origin_opener(first):
                # The trial judge is the 'Presiding' byline the origin
                # closes on; what stands above it is the court reviewed.
                said = []
                for line in band:
                    who = parser.parse(_norm(line.plain))
                    if who is not None and (who.kind or "").lower() \
                            == "presiding":
                        crit.setdefault("lower_court_judge", who.name)
                    else:
                        said.append(_norm(line.plain))
                    emit(line, "lower-court", pm)
                if said:
                    origin_rows.append(_norm(" ".join(said)))
                state = "cover"
                continue
            if _is_counsel_label(first):
                for line in band:
                    emit(line, "counsel", pm)
                counsel_rows.extend(_norm(l.plain) for l in band[1:])
                state = "counsel"
                continue
            if first.lower().startswith("before"):
                panel_rows.append(printed)
                for line in band:
                    emit(line, "panel", pm)
                state = "cover"
                continue
            if _is_descriptor(first):
                descriptor_rows.append(printed)
                for line in band:
                    emit(line, "summary", pm)
                state = "cover"
                continue
            # A BYLINE ENDS THE READER, and so does anything this contract
            # does not name — the centred bold heading the unsigned
            # memorandum opens on, or its first paragraph.
            if state == "counsel" and not _opens_landmark(first) \
                    and parser.parse(first) is None:
                counsel_rows.append(printed)
                for line in band:
                    emit(line, "counsel", pm)
                continue
            stop = True
            break

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if titles:
        crit["title"] = titles[0]
    caption_rows = debtor_rows + party_rows
    if caption_rows:
        crit["caption"] = caption_rows
    # THE APPEAL'S PARTIES are the block the SHELVES separate: what stands
    # above the upper shelf is the bankruptcy case's own style ('In re:
    # MARC HOWELL, Debtor.'), and joining the two makes every record read
    # 'MARC HOWELL v. MARC HOWELL'.
    sides = _sides(party_rows)
    if sides:
        crit["parties"] = list(sides)
        crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    else:
        one = _sides(party_rows, one_sided=True)
        if one:
            crit["parties"] = [one]
            crit["case_name"] = one
    if dockets:
        crit["docket_number"] = dockets[0]
        if dockets[1:]:
            crit.setdefault("other_dockets", []).extend(dockets[1:])
    if lower_dockets:
        crit.setdefault("other_dockets", []).extend(lower_dockets)
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    if panel_rows:
        printed = _norm(" ".join(panel_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    # WHO WROTE WHAT is recorded by TAGGING the rows the court sets it on;
    # the model declares no field for authorship, and `disposition` is a
    # different fact (the ruling the writing closes on).

    # ---- the clerk's stamp: read, then recorded -------------------------
    # The DATE is read off the whole column, furniture rows included — core
    # recognizes most of the stamp and drops it before the reader ever sees
    # it, and the day the panel filed the paper is the one fact it carries.
    joined = " ".join(_stamp_rows(stamp_all))
    hit = _STAMP_DATE.search(joined)
    if hit:
        crit.setdefault("decision_date", _norm(hit.group(1)))
    # A CLAIM MUST BE TOTAL: the stamp rows the reader took off the sheet
    # are recorded, never silently swallowed.
    if stamp_mine:
        dropped.append(m.Dropped(
            text=" ".join(_stamp_rows(stamp_mine)),
            prov=m.Prov(1, tuple(sorted(stamp_ids))), kind="stamp"))
        consumed.update(stamp_ids)

    if not caption_rows:
        return NOTHING

    # WHAT THE PAPER IS, the panel states in its own caption. A memorandum
    # disposition is the panel's decision of the appeal — unsigned, but an
    # opinion — and without the label an unbylined writing types as an
    # order by default.
    doc_type_final = None
    if titles:
        head = titles[0]
        if "ORDER" in head and "OPINION" not in head:
            doc_type_final = m.DocType.ORDER
        elif "OPINION" in head or "MEMORANDUM" in head:
            doc_type_final = m.DocType.OPINION

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": [], "doc_type_final": doc_type_final}


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _caption(box_lines: list, split_x: float, pm, align_of):
    """One shelved caption block, plus the left column's own text.

    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned: a side
    with nothing on a baseline still occupies it, or 'Bk. No. …' rides up
    off the party row the page prints it beside. The columns are held apart
    by WHITESPACE, not by a drawn vertical or a glyph — so ``rail`` is
    None and the renderer draws no divider, because the page draws none."""
    rows: list[list] = []
    for line in sorted(box_lines, key=lambda l: (l.top, l.x0)):
        if rows and abs(rows[-1][0].top - line.top) <= _ROW_SLOP:
            rows[-1].append(line)
        else:
            rows.append([line])
    if not rows:
        return None, []

    left_x0 = min((l.x0 for row in rows for l in row
                   if l.x0 < split_x - _SPLIT_SLOP), default=pm.width)

    def cell(parts: list, indent: bool):
        parts = sorted(parts, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        rel = round(first.x0 - left_x0) if indent else 0.0
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(p.all_bold for p in parts),
            rel=max(rel, 0.0), role="caption")

    def blank():
        return m.HmLine(text="", prov=m.Prov(pm.number), role="caption")

    left, right, left_plain = [], [], []
    for row in rows:
        l_cells = [l for l in row if l.x0 < split_x - _SPLIT_SLOP]
        r_cells = [l for l in row if l.x0 >= split_x - _SPLIT_SLOP]
        left.append(cell(l_cells, True) if l_cells else blank())
        right.append(cell(r_cells, False) if r_cells else blank())
        # THE CRITERIA READ THE PAGE'S OWN TEXT, row by row and never the
        # markup: the pivot and the status label the clerk sets on one
        # baseline are two caption rows, and joined into one the pivot
        # takes the status label for the party on the far side of it.
        left_plain.extend(_norm(l.plain) for l in sorted(l_cells,
                                                         key=lambda l: l.x0))
    block = m.CaptionBlock(
        left=left, right=right, rail=None, rail_rows=0,
        style_id="shelved",
        fp={"split_x": split_x, "left_x0": left_x0},
        prov=m.Prov(pm.number,
                    tuple(sorted(l.id for row in rows for l in row))))
    return block, left_plain
