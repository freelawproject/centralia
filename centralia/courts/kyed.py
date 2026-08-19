"""United States District Court for the Eastern District of Kentucky ('kyed').

Everything unique to kyed lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'the ECF pleading order'. A federal district court is not a
publisher with a house style; it is a building full of chambers, each with
its own Word template. kyed's 25 records are three templates, and they are
the SAME PAPER with three different caption dividers. So the contract is
named for the paper and dispatched on the divider, and the divider is
measured, never read:

    the ECF overlay            the top band, on every page: a fielded
                               stamp CM/ECF prints over the court's own
                               sheet, sometimes wrapping to a second row
                               ('Case: 2:25-cv-00171-DLB-CJS  Doc #: 8
                                Filed: 05/20/26  Page: 1 of 19 - Page' /
                                'ID#: 132')
    the masthead               the leading run of CENTRED rows: the court,
                               the district, the division, the seat
    the caption band           parties, status, pivot, docket, title —
                               two columns, split at whatever the chambers
                               drew between them
    the closer                 a typed ASTERISK BAND ('* * * * * *',
                               '***  ***  ***  ***') on the page axis, or,
                               where a chambers types none, the caption
                               box's own FOOT RULE
    the body                   everything below the closer, core's

Three dividers, one per chambers, all three measured on page 1:

    GLYPH RAIL (7 records) — a stacked ')' between the columns:

        CELLMARK, INC.,             )
              Plaintiff,            ) Civil Action No. 2:24-cv-00181-SCM-CJS
        v.                          )
                                    )        MEMORANDUM OPINION
        ROBERT WEBSTER, et al.,     )              AND ORDER
              Defendants.           )
                    ***   ***   ***   ***

    DRAWN RAIL (6 records) — a DRAWN vertical stroke, closed at its foot by
    a drawn horizontal that stops AT the stroke (captions.py calls the shape
    'Old Faithful'):

        HEALTHCARE JUSTICE COALITION,   │  CASE NO. 5:25-cv-386-KKC
              Plaintiff,                │
        v.                              │  OPINION & ORDER
        UNITED HEALTHCARE OF            │  ────────────────
        KENTUCKY, et al.,               │
              Defendants.               │
        ────────────────────────────────┘   the foot rule = the closer

    FLUSH-RIGHT STATUS (12 records) — nothing is drawn at all. The party
    stands at the body rail and its STATUS is set flush right; the docket
    opens the band on its own row and the title shares the pivot's row:

        CIVIL ACTION NO. 25-171-DLB-CJS
        LINDA MOORE                                        PLAINTIFF
        v.            MEMORANDUM OPINION AND ORDER
        BOONE COUNTY SCHOOL BOARD OF EDUCATION, et al.    DEFENDANTS
                    * * * * * * * * * * * * * * * *

The dispatch is the DIVIDER and the CLOSER, never a title and never a
judge's initials in the docket. A record whose page 1 does not open with a
centred 'UNITED STATES DISTRICT COURT', or which closes its caption with
neither an asterisk band nor a foot rule, is not this contract and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

The reader claims HEADMATTER ONLY — the overlay, the masthead, the caption
band and the closer, all on page 1. It never touches a writing. kyed signs
nothing (its orders end 'This 4th day of August, 2026.' with no byline),
so the title row is the only thing an unsigned writing can anchor on: it is
claimed, and offered back through `anchor_ids` if the claim would otherwise
cost the document its opinion.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import (FurnitureFinder, _looks_like_efiling_stamp,
                                 is_folio_text)
from . import register

KYED = register(CourtProfile(
    "kyed", "United States District Court for the Eastern District of Kentucky",
    # District judges sign in the reversed form where they sign at all
    # ('RICHARD L. BOURGEOIS, JR. / UNITED STATES MAGISTRATE JUDGE'). No
    # record in this corpus does; the grammar is declared so that one which
    # does is read rather than missed.
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

STYLE_GLYPH_RAIL = "ecf order, glyph rail"
STYLE_DRAWN_RAIL = "ecf order, drawn rail"
STYLE_FLUSH_STATUS = "ecf order, flush-right status"

# ---- kyed's declared facts (measured over its 25 records) -----------------
# THE OVERLAY BAND. CM/ECF stamps the sheet above the court's own masthead:
# the stamp itself lands at top 13.0 and its wrapped tail ('ID#: 712') at
# 25.0, while the earliest masthead row in the corpus is at 60.4. The band
# is therefore defined by the masthead, not by a constant — everything above
# the first centred row is the overlay, and every one of those rows has to
# LOOK like the overlay or the record is not this paper.
#
# THE CLOSER BAND. The asterisk band lands between 267.0 and 328.4 on a
# 792pt page (34%-42%); the caption's foot rule between 267.8 and 326.7.
# 55% of the height clears both by a wide margin and still stands above the
# first body row on every record.
_CLOSER_BAND = 0.55
# THE OVERLAY BAND: 12% of the height (95pt on a 792pt sheet) holds the
# stamp and its wrapped tail and stands clear of the earliest masthead row.
_OVERLAY_BAND = 0.12
# THE ASTERISK BAND is typed, so its pitch varies by chambers ('* * * *',
# '***   ***', '* *  * *'). Five asterisks is the floor: no caption cell in
# the corpus carries more than one.
_ASTERISK_FLOOR = 5
# THE GLYPH RAIL. ')' occurs in ordinary prose and inside party names
# ('ENFORCEMENT ("ICE"), et al.'), so it counts as a divider only as a
# COLUMN — four or more stacked within 3pt of one x. Measured: the shortest
# rail in the corpus is 9 glyphs.
_RAIL_CHARS = ")]:*§}|"
_RAIL_FLOOR = 4
_RAIL_COLUMN = 3.0
# A glyph belongs to the rail when it stands in the rail's own column. The
# rail cell is ~7pt wide (')' at 307.6-311.6, with a trailing space to
# 314.6); 12pt clears the cell and reaches nothing else on the row.
_RAIL_WINDOW = 12.0
# THE DRAWN RAIL. A stroke at least 25pt tall standing between 35% and 75%
# of the measure. Measured: x = 304.6-317.8 on a 612pt page (50%-52%),
# heights 131-197pt. The band bound keeps a table border on a later page out.
_DRAWN_MIN_H = 25.0
_DRAWN_X = (0.35, 0.75)
# THE FOOT RULE closes the drawn-rail caption: a drawn horizontal starting
# at the body rail and ENDING at the rail's own x. Both ends are the test —
# a rule that ends short of the rail is the title's UNDERLINE (measured:
# every drawn horizontal in the band at x0 >= 173 is one), and a rule
# spanning the whole measure is a footnote separator.
_FOOT_RULE_END = 12.0

# THE PAPER'S OWN NAME, as the court prints it at the head of the sheet. The
# masthead is the court naming ITSELF, which is the one place a name may be
# read — and it is read on 'DISTRICT COURT' alone, because the district's own
# line carries a typo on part of the corpus ('EASTEN DISTRICT OF KENTUCKY').
_COURT_NAME = "district court"

# THE DOCKET, in every form the chambers write it: 'CIVIL ACTION NO.
# 25-171-DLB-CJS', 'CRIMINAL ACTION NO. 26-196-DLB', 'Case No.:
# 5:25-cv-00086-KKC', 'Civil Action No. 2:24-cv-00181-SCM-CJS', 'Civil No.
# 3:25-cv-00042-GFVT', 'No. 6:25-CV-109-HAI'.
_DOCKET = re.compile(
    r"^(?:(?:civil|criminal|misc(?:ellaneous)?\.?)\s+(?:action\s+)?)?"
    r"(?:case\s+)?nos?\.?\s*:?\s*(\S.*)$", re.I)
# THE TITLE is a closed vocabulary of the words a district court names its
# own paper with, tested on the row's LETTERS so that neither the wrap
# ('MEMORANDUM OPINION' / 'AND ORDER') nor the letter-spacing one chambers
# uses ('O PIN I ON AND ORDER') hides it. Nothing about the case is read.
_TITLE_WORDS = (
    "memorandum", "opinion", "order", "and", "judgment", "report",
    "recommendation", "adopting", "decision", "ruling", "findings", "fact",
    "conclusions", "law", "decree", "amended", "corrected", "supplemental",
    "initial", "screening", "review", "notice", "entry", "the", "of", "on",
)
# PARTY STATUS is a finite role vocabulary; a party NAME is never read by
# wording. kyed sets the status in caps flush right on one template and in
# title case under the party on the other two.
_STATUS_WORDS = (
    "plaintiff", "plaintiffs", "defendant", "defendants", "petitioner",
    "petitioners", "respondent", "respondents", "movant", "movants",
    "claimant", "claimants", "intervenor", "intervenors", "debtor",
    "debtors", "appellant", "appellants", "appellee", "appellees",
    "garnishee", "garnishees", "applicant", "applicants", "amicus", "amici",
)
_PIVOTS = ("v", "vs", "versus")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _letters(text: str) -> str:
    """The row's letters, lower-cased, '&' spelled out — the form the title
    vocabulary is tested against."""
    return re.sub(r"[^a-z]", "", _norm(text).lower().replace("&", "and"))


def _title_spelling(text: str):
    """The paper-name words ``text`` spells, or None.

    Segmentation, not a word split, because one chambers' template loses its
    word breaks in the PDF ('O PIN I ON AND ORDER'): the vocabulary that
    recognizes the row is the only thing that can spell it. A wrap fragment
    ('AND ORDER', '&') answers with its words; a party name ('ROBERT
    WEBSTER, et al.') answers None."""
    key = _letters(text)
    if not key or len(key) < 3:
        return None
    back: list = [None] * (len(key) + 1)
    reach = [True] + [False] * len(key)
    for i in range(len(key)):
        if not reach[i]:
            continue
        for word in _TITLE_WORDS:
            if key.startswith(word, i) and not reach[i + len(word)]:
                reach[i + len(word)] = True
                back[i + len(word)] = (i, word)
    if not reach[len(key)]:
        return None
    words: list[str] = []
    at = len(key)
    while at:
        at, word = back[at]
        words.append(word)
    return list(reversed(words))


def _is_title_row(text: str) -> bool:
    return _title_spelling(text) is not None


def _title_text(text: str) -> str:
    """The title as the criterion should carry it: the page's own form where
    the page set usable word breaks, and the vocabulary's spelling where it
    did not."""
    flat = _norm(text)
    tokens = [t.strip(",.;:") for t in
              flat.upper().replace("&", " AND ").split()]
    tokens = [t for t in tokens if t]
    if tokens and all(t.lower() in _TITLE_WORDS for t in tokens):
        return flat.upper()
    spelling = _title_spelling(flat)
    return " ".join(w.upper() for w in spelling) if spelling else flat.upper()


def _is_status_row(text: str) -> bool:
    """Is the row APPARATUS rather than a party? Every word has to be a
    status word, so a party carrying one ('DEFENDANT SERVICES, INC.')
    survives."""
    words = [w.strip(",.;:-–/() ").lower()
             for w in _norm(text).replace("-", " ").replace("/", " ").split()]
    words = [w for w in words if w]
    if not words:
        return False
    return all(w in _STATUS_WORDS or w in ("and", "the", "third", "party",
                                           "cross", "in", "interest", "of",
                                           "pro", "se", "counter")
               for w in words)


def _is_pivot_row(text: str) -> bool:
    flat = _norm(text).rstrip(".").lower()
    return flat in _PIVOTS


def _docket_value(text: str):
    """The docket the row states, or None. A number is required: 'No.' alone
    heads nothing, and 'Notice of…' is not a docket."""
    flat = _norm(text)
    if len(flat) > 90:
        return None
    mm = _DOCKET.match(flat)
    if mm is None:
        return None
    value = _norm(mm.group(1)).rstrip(".,")
    if not any(c.isdigit() for c in value):
        return None
    if re.search(r"[a-z]{4}", value) and not re.search(r"\d[-:]\d", value) \
            and not re.search(r"\d{2}-\d", value):
        return None                        # prose that merely opens 'No…'
    return value


def _is_asterisk_band(text: str) -> bool:
    flat = text.strip()
    return (bool(flat) and set(flat) <= {"*", " "}
            and flat.count("*") >= _ASTERISK_FLOOR)


def _looks_like_overlay(text: str) -> bool:
    """A row standing ABOVE the masthead: the CM/ECF stamp, its wrapped tail
    ('ID#: 712', '1102'), or an e-filing badge. Short, fielded, numeric —
    never a sentence."""
    flat = _norm(text)
    if not flat:
        return True
    if _looks_like_efiling_stamp(flat) or is_folio_text(flat):
        return True
    if len(flat) <= 40 and (re.search(r"\bID#?\s*[:.]", flat, re.I)
                            or re.fullmatch(r"[\d\s.,#:-]+", flat)
                            or flat.upper() in ("E-FILED", "FILED",
                                                "ENTERED", "RECEIVED")):
        return True
    return False


# --------------------------------------------------------------------------
# the divider and the closer — measured, then dispatched on
# --------------------------------------------------------------------------

def _glyph_rail(lines: list) -> dict | None:
    """A stacked column of one rail glyph, or None."""
    best = None
    for glyph in _RAIL_CHARS:
        chars = [c for l in lines for c in l.chars
                 if (c.get("text") or "") == glyph]
        if len(chars) < _RAIL_FLOOR:
            continue
        x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
        stack = [c for c in chars if abs(c["x0"] - x) < _RAIL_COLUMN]
        if len(stack) < _RAIL_FLOOR:
            continue
        found = {"glyph": glyph, "x": float(x), "n": len(stack),
                 "top": min(c["top"] for c in stack),
                 "bottom": max(c["bottom"] for c in stack)}
        if best is None or found["n"] > best["n"]:
            best = found
    return best


def _drawn_rail(pm, band: tuple) -> dict | None:
    """The chambers' drawn column divider, or None."""
    for v in pm.v_rules:
        if v.height < _DRAWN_MIN_H:
            continue
        if not (pm.width * _DRAWN_X[0] <= v.x <= pm.width * _DRAWN_X[1]):
            continue
        if v.bottom < band[0] or v.top > band[1]:
            continue
        return {"glyph": None, "x": float(v.x), "top": v.top,
                "bottom": v.bottom}
    return None


def _foot_rule(pm, band: tuple, mid: float | None, body_x0: float):
    """The caption box's foot: a drawn horizontal from the body rail to the
    divider. Returns the rule, or None."""
    if mid is None:
        return None
    for r in sorted(pm.h_rules, key=lambda r: r.top):
        if not (band[0] <= r.top <= band[1]):
            continue
        if r.x0 > body_x0 + 8:
            continue                       # starts inside the measure
        if abs(r.x1 - mid) <= _FOOT_RULE_END:
            return r
    return None


def _rail_chars(line, rail) -> list:
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    return [c for c in line.chars
            if (c.get("text") or "") == rail["glyph"] and lo <= c["x0"] <= hi]


def _shed_rail(line, rail):
    """``line`` without the rail's own glyphs, or None when the line WAS the
    rail. Identified by COLUMN, never by character: a ')' closing real text
    is not in the rail's column."""
    if rail is None or rail["glyph"] is None:
        return line
    drop = {id(c) for c in _rail_chars(line, rail)}
    if not drop:
        return line
    kept = [c for c in line.chars if id(c) not in drop]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept,
                    x0=min(c["x0"] for c in kept),
                    x1=max(c.get("x1", c["x0"]) for c in kept))


def _side(line, mid: float, want: str):
    """The part of ``line`` lying one side of the divider, or None. Split
    glyph by glyph: whether pdfio already broke a row at its column gap is an
    accident of how wide the gap happened to be, and one chambers sets
    ')Civil Action No. 2:24-cv-00181-SCM-CJS' as a single run."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="kyed")
def read_headmatter_kyed(model, geom, **_):
    """Read kyed's ECF pleading order, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    pw, ph = pm.width, pm.height
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)

    live = [l for l in pm.lines if l.plain.strip()]
    live.sort(key=lambda l: (l.top, l.x0))
    if not live:
        return NOTHING

    def align(line) -> str:
        return line_alignment(line, pw, geom,
                              banner_center_min_size=body_size + 2.0)

    # ---- the overlay comes FIRST, and it is not always one row ----------
    # CM/ECF wraps its stamp when the case number is long, and the wrapped
    # tail ('ID#: 712', '1102') is a short CENTRED row — read as the start of
    # the masthead it ended the walk on 14 of 25 records before this loop
    # was written. The overlay is the leading run of rows that look like the
    # overlay, inside the top band the court leaves for it (the earliest
    # masthead row in the corpus is at 60.4 on a 792pt page; the stamp's
    # tail at 25.0).
    mast_at = 0
    while (mast_at < len(live) and live[mast_at].top < ph * _OVERLAY_BAND
           and _looks_like_overlay(live[mast_at].plain)):
        mast_at += 1
    overlay = live[:mast_at]
    if mast_at >= len(live):
        return NOTHING

    # ---- the masthead: the leading run of CENTRED rows ------------------
    if align(live[mast_at]) != "C":
        return NOTHING
    if _COURT_NAME not in _norm(live[mast_at].plain).lower():
        return NOTHING                     # kyed always names itself first
    mast: list = []
    j = mast_at
    while j < len(live) and align(live[j]) == "C":
        mast.append(live[j])
        j += 1
    band_lo = mast[-1].bottom

    # ---- the closer -----------------------------------------------------
    band_hi = ph * _CLOSER_BAND
    closer = None
    for line in live[j:]:
        if line.top > band_hi:
            break
        if _is_asterisk_band(line.plain):
            closer = line
            break
    cap_band = (band_lo, closer.top if closer else band_hi)

    # ---- the divider ----------------------------------------------------
    in_band = [l for l in live[j:]
               if l.top >= cap_band[0] and l.top <= cap_band[1] + 2
               and l is not closer]
    if not in_band:
        return NOTHING
    rail = _glyph_rail(in_band) or _drawn_rail(pm, cap_band)
    mid = rail["x"] if rail else None
    foot = _foot_rule(pm, (cap_band[0], band_hi), mid, body_x0)
    if closer is None:
        if foot is None:
            return NOTHING                 # neither closer: not this paper
        cap_band = (band_lo, foot.top)
        in_band = [l for l in in_band if l.top < foot.top]
        if not in_band:
            return NOTHING
    if rail is None:
        style = STYLE_FLUSH_STATUS
    elif rail["glyph"] is None:
        style = STYLE_DRAWN_RAIL
    else:
        style = STYLE_GLYPH_RAIL

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    anchor_ids: list[int] = []

    # ---- the overlay is recorded, never rendered ------------------------
    # A claim must be TOTAL: a row the reader steps over is placed or
    # recorded. Core sees the stamp's first row by repetition and misses its
    # wrapped tail ('ID#: 132' rendered as an unread headmatter row, and
    # 'ID#: 16633' was read as the docket); a reader that claims the region
    # inherits its furniture.
    for line in overlay:
        # Core's furniture pass already surfaced what it could SEE by
        # repetition (the stamp's first row, a bare-numeral tail read as a
        # folio); recording those again puts the same row in `removed`
        # twice. Only what core missed is recorded here — the id is consumed
        # either way, so the claim stays total.
        if finder.kind(pm, line) is None:
            dropped.append(m.Dropped(text=_norm(line.plain),
                                     prov=m.Prov(1, (line.id,)),
                                     kind="stamp"))
        consumed.add(line.id)

    def emit(line, role: str):
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(1, (line.id,)),
            align=m.Align(align(line)), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    court_rows: list[str] = []
    for line in mast:
        court_rows.append(_norm(line.plain))
        emit(line, "court")

    # ---- the caption band, row by visual row ---------------------------
    rows: list[list] = []
    rail_only: list = []
    for line in sorted(in_band, key=lambda l: (l.top, l.x0)):
        shed = _shed_rail(line, rail)
        if shed is None:
            # THE PIECE WAS THE RAIL. It is still a line the reader took out
            # of the stream, so it is consumed here: left behind, the naked
            # glyphs opened the writing with six paragraphs reading ') )'.
            # The CaptionBlock's own `rail` reproduces them.
            rail_only.append(line)
            continue
        if rows and abs(rows[-1][0].top - shed.top) <= 2.5:
            rows[-1].append(shed)
        else:
            rows.append([shed])
    if not rows:
        return NOTHING
    for line in rail_only:
        consumed.add(line.id)

    def cell(parts: list):
        parts = sorted(parts, key=lambda l: l.x0)
        text = ""
        for p in parts:
            piece = line_markup(p)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(1, tuple(p.id for p in parts)),
            align=m.Align(align(first)), x0=first.x0,
            size=first.size or 0.0,
            bold=all(p.all_bold for p in parts), role="caption")

    def blank():
        return m.HmLine(text="", prov=m.Prov(1), role="caption")

    left: list = []
    right: list = []
    left_plain: list[str] = []
    right_plain: list[str] = []
    for row in rows:
        l_parts: list = []
        r_parts: list = []
        if mid is not None:
            for line in row:
                for side, bucket in ((_side(line, mid, "L"), l_parts),
                                     (_side(line, mid, "R"), r_parts)):
                    if side is not None:
                        bucket.append(side)
        else:
            # NO DIVIDER IS DRAWN, so the columns are the row's own PIECES:
            # pdfio split this row at the whitespace gutter the chambers
            # typed, and the first piece stands at the body rail while the
            # rest stand out to the right. A lone piece is placed by where it
            # starts — the status cell and the title both begin far right of
            # the rail, and the party and the pivot both begin on it.
            ordered = sorted(row, key=lambda l: l.x0)
            if len(ordered) >= 2:
                l_parts = [ordered[0]]
                r_parts = ordered[1:]
            elif ordered[0].x0 <= body_x0 + 40:
                l_parts = [ordered[0]]
            else:
                r_parts = [ordered[0]]
        left.append(cell(l_parts) if l_parts else blank())
        right.append(cell(r_parts) if r_parts else blank())
        for p in l_parts + r_parts:
            consumed.add(p.id)
        left_plain.append(_norm(" ".join(p.plain for p in l_parts)))
        right_plain.append(_norm(" ".join(p.plain for p in r_parts)))

    # ---- what each cell IS ---------------------------------------------
    caption_rows: list[str] = []
    title_parts: list[str] = []
    for column, texts in ((left, left_plain), (right, right_plain)):
        open_title = False
        for cellrow, flat in zip(column, texts):
            if not flat:
                open_title = False
                continue
            docket = _docket_value(flat)
            if docket is not None:
                cellrow.role = "docket"
                if crit.get("docket_number"):
                    crit.setdefault("other_dockets", []).append(docket)
                else:
                    crit["docket_number"] = docket
                open_title = False
                continue
            # THE TITLE WRAPS, and its fragments are only the title where
            # they CONTINUE one: 'AND ORDER' opening a column would be an
            # unread row, not a paper name.
            if _is_title_row(flat) and not _is_status_row(flat) \
                    and (open_title or _letters(flat).startswith(
                        ("memorandum", "opinion", "order", "judgment",
                         "report", "findings", "ruling", "decision",
                         "notice", "amended", "corrected"))):
                cellrow.role = "title"
                title_parts.append(_title_text(flat))
                anchor_ids.extend(cellrow.prov.line_ids)
                open_title = True
                continue
            open_title = False
            if column is left:
                caption_rows.append(_norm(flat))
    # THE RAIL'S OWN RUN is not the caption's rhythm: rows that held only
    # the divider are empty on both sides and render as phantom blanks.
    def _bare(row) -> bool:
        return not re.sub(r"<[^>]+>", "", row.text or "").strip()
    while left and _bare(left[-1]) and _bare(right[-1]):
        left.pop(); right.pop(); left_plain.pop(); right_plain.pop()
    items.append(m.CaptionBlock(
        left=left, right=right,
        rail=(rail["glyph"] if rail else None), rail_rows=len(left),
        style_id=None,
        fp={"rail": rail["glyph"] if rail else None, "mid_x": mid,
            "band": cap_band},
        prov=m.Prov(1, tuple(sorted(l.id for l in in_band)))))

    # ---- the closer, and the foot rule the box draws --------------------
    # A DRAWN RULE WHOSE ENDS COINCIDE WITH THE ROW ABOVE IT IS AN
    # UNDERLINE, not a fence: every chambers underscores its title, and
    # those rules are emphasis and are not re-emitted. The foot rule reaches
    # from the body rail to the divider and IS the box's border.
    if foot is not None:
        items.append(m.Rule(prov=m.Prov(1, ()), span="left"))
    if closer is not None:
        items.append(m.Rule(prov=m.Prov(1, (closer.id,)), typed=True,
                            span="center"))
        consumed.add(closer.id)

    # ---- what the block says -------------------------------------------
    if court_rows:
        crit["court"] = _norm(" ".join(court_rows))
    if title_parts:
        crit["title"] = _norm(" ".join(title_parts))
    if caption_rows:
        crit["caption"] = caption_rows
        sides = _sides(caption_rows)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            one = _sides(caption_rows, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


def _sides(caption_rows: list, one_sided: bool = False):
    """The party names either side of the pivot, built from the NAMES —
    never by joining the caption wholesale, which yields 'CIVIL ACTION NO.
    25-171-DLB-CJS LINDA MOORE'."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat:
            continue
        if _is_pivot_row(flat):
            side = right
            seen = True
            continue
        if _is_status_row(flat):
            continue
        head = flat.split(None, 1)
        if head and head[0].rstrip(".").lower() in _PIVOTS:
            side = right
            seen = True
            flat = _norm(head[1]) if len(head) > 1 else ""
            if not flat:
                continue
        side.append(flat)
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))
