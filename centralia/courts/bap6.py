"""Bankruptcy Appellate Panel of the Sixth Circuit ('bap6').

Everything unique to bap6 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'rail and fence', the Sixth Circuit's own stationery. The
panel sits inside the circuit and prints the circuit's paper: the caption's
column divider is DRAWN, and the glyph it is drawn with says which paper
this is. Nothing is decided by what a row says.

    ruled slip (41 of 42) — the caption is a BOX drawn in box-drawing
    glyphs ('┐' '│' '┘'), the court draws ONE 110.1pt rule on the page axis
    (x0=253.0 on a 612pt page) to open it, and every labelled section below
    is fenced above and below by a TYPED rule ('_________________'):

        RECOMMENDED FOR FULL-TEXT PUBLICATION      the publication flag, 9pt
        File Name: 19b0004p.06                     the slip's own file name
        BANKRUPTCY APPELLATE PANEL                 the banner, 15pt bold
        OF THE SIXTH CIRCUIT
        ────────────                               a DRAWN 110.1pt rule
        In re: EARL BENARD BLASINGAME;         ┐   the debtor block…
             Debtors.                          │
        ______________________________         │   …the IN-RE DIVIDER…
        CHURCH JOINT VENTURE, L.P.,            │
             Plaintiff-Appellant (18-8010), >  │   Nos. 18-8010/8013/8018
        v.                                     │   …and the BAP docket
        BETTYE SUE BEDWELL, Chapter 7 Trustee, │
             Defendant-Appellee (18-8010),     ┘
        Appeal from the United States Bankruptcy Court     the origin band
        for the Western District of Tennessee at Memphis.
        No. 08-28289; Adv. Pro. 15-00021—Jennie D. Latta, Judge.
        Argued:  February 12, 2019                        the dates
        Decided and Filed:  April 15, 2019
        Before: OPPERMAN, PRICE SMITH, and WISE, Bankruptcy Appellate
        Panel Judges.                                     the roster
        _________________                                 a TYPED fence
        COUNSEL                     (or LITIGANT, where a party appears pro se)
        ARGUED:  Bruce W. Akerly, MALONE AKERLY MARTIN PLLC, …
        HUMPHREY, J., filed the opinion of the Panel in which …  who wrote what
        _________________
        OPINION                     (or OPINION AND ORDER)
        _________________
        DANIEL S. OPPERMAN, Chief Bankruptcy Appellate Panel Judge.  Church…

    paren-rail slip (2 of 42) — NO drawn rule. A stacked ')' is the
    caption's divider and the whole zone system: the masthead is what
    stands above it, the caption is what stands inside it (left the
    parties, right the origin and the paper's name), and what follows is
    the roster and then the writing:

        No. 22-8007                                the docket, ABOVE the banner
        BANKRUPTCY APPELLATE PANEL
        OF THE SIXTH CIRCUIT
        In re: CURARE LABORATORY LLC,   )
                                        )   O R D E R
             Debtor.                    )
        Before:  CROOM, DALES, and MASHBURN, Bankruptcy Appellate Panel Judges.
        Appellants Solar Holdings Group, LLC …     an unsigned order: the
                                                   body opens with no byline

TWO FACTS ARE THE PANEL'S OWN, and neither is a circuit's:

  * THE IN-RE DIVIDER. A bankruptcy caption names the MAIN CASE first —
    'In re: <debtor>, Debtor.' — and then, under a rule the court sets
    across the left column only (typed on 12 records, DRAWN on 2), the
    parties to this appeal. The divider is what separates the debtor from
    the appellants, so `parties` and `case_name` are built from the rows
    BELOW it and the whole caption is still published verbatim.

  * THE ORIGIN BAND IS A BAND, not a row. The panel reviews a bankruptcy
    court, and on a direct appeal the paper names TWO tribunals with a
    typed fence between them ('Appeal from the United States District
    Court … / ____ / United States Bankruptcy Court …'). Read row by row
    the second statement opens nothing and ends the walk. So the zone
    between the caption box and the first DATE row (or, absent dates, the
    roster) is the origin, whole: what is shaped like a docket is a docket
    and everything else is the tribunal. Both landmarks are printed on
    every record.

The dispatch is the RAIL. A record whose caption draws neither divider is
not this contract and gets NOTHING — core's shared walk places those rows
unidentified, which is a smaller error than a confident misreading.

The reader claims HEADMATTER ONLY. It stops at the first byline, and
everything below is core's.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The panel signs with an ALL-CAPS name and its full designation ('DANIEL S.
# OPPERMAN, Chief Bankruptcy Appellate Panel Judge.'), and the circuit's own
# judges sign the two direct appeals that share this corpus ('MURPHY,
# Circuit Judge.'). Copied VERBATIM from the shared BAP registration this
# court used to sit in, plus the circuit titles those two records need.
BAP6 = register(CourtProfile(
    "bap6", "Bankruptcy Appellate Panel of the Sixth Circuit",
    byline=BylineGrammar(
        style="prose", allow_titlecase_name=True,
        # the parser spreads tight punctuation, so 'U.S.' reaches the title
        # match as 'U. S.' — both spellings are declared
        titles=("U. S. Bankruptcy Appellate Panel Judge",
                "U.S. Bankruptcy Appellate Panel Judge",
                "United States Bankruptcy Appellate Panel Judge",
                "Chief Bankruptcy Appellate Panel Judge",
                "Bankruptcy Appellate Panel Judge",
                "Chief Bankruptcy Judge", "Bankruptcy Judge",
                "Circuit Judge", "Chief Judge", "Judge")),
))

STYLE_RULED_SLIP = "ruled slip"          # box rail + a drawn fence
STYLE_PAREN_RAIL = "paren-rail slip"     # a ')' rail, no rules

# ---- bap6's declared facts (measured over the corpus, not tuned) ---------
# THE BOX: the caption's divider is drawn in box-drawing glyphs, corners
# included — '┐' opens it and '┘' closes it, and both are the rail.
_BOX = "│┃┐┘┌└├┤┬┴┼"
_BOX_FLOOR = 3
# THE PAREN RAIL: ')' occurs in ordinary prose, so a paren column has to
# earn the name. Six glyphs earn it outright; a SHORTER column earns it by
# standing ALONE — every glyph in it is the whole of its own row fragment,
# which punctuation inside a sentence never is. The panel's one unsigned
# order sets a three-row rail that way.
_PAREN_FLOOR, _PAREN_ALONE_FLOOR = 6, 3
# The template sets a '>' at the docket cell as part of the same drawn rail.
_RAIL_LEAD = ">"
# A glyph is the RAIL'S when it stands in the rail's own column. Measured:
# the box column is ~8pt wide ('│' at 342.9, '>' at 345.9-346.5), so 12pt
# clears the whole bracket and reaches nothing else on the row.
_RAIL_WINDOW = 12.0
# THE DRAWN FENCE that opens the ruled caption: 110.0-110.1pt wide, x0=253.0
# on a 612pt page — identical on all 41 ruled records. The same page draws
# an 'O R D E R' underline (52.7pt), an in-re divider (249.2pt) and a
# footnote separator (144pt), and the axis test takes none of them.
_DRAWN_FENCE = (100.0, 125.0)
_DRAWN_OFF_AXIS = 40.0
# How far below the caption the block may still run. The counsel block wraps
# to page 2 on part of the corpus; three pages is more than any of it needs.
_MAX_PAGES = 4
# THE RUNNING HEAD'S BAND. Every continuation page opens with the head —
# 'Nos. 18-8010/8013/8018  In re Blasingame  Page 2' — and the unsigned
# order sets a docket over a dressed folio ('- 2 -'). Measured over the
# corpus the head bottoms out at 55.8 and the body never opens above 80.2.
#
# Core recognizes the head by REPETITION, which needs pages to repeat on: a
# two-page record prints it once, and there the reader must know its own
# court's stationery.
_HEAD_BAND_MAX = 72.0

# SAME-ROW PIECES. pdfio splits a justified line at a wide inter-word gap,
# so one printed counsel row can arrive as two ('Louisville, Kentucky, for
# Appellant.' + 'Sandra D. Freeburger, DEITZ, SHIELDS &'). The panel's
# leading below the caption is 13.8pt, so anything inside 3pt is one row.
_ROW_TOL = 3.0

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# A LABEL WITH NO VALUE IS STILL THE DATE BAND.
_BARE_DATE = re.compile(
    r"^(?:Argued(?:\s+En\s+Banc)?(?:\s+and\s+Submitted)?|Submitted"
    r"|Reargued|Decided(?:\s+and\s+Filed)?|Filed|Amended|Entered)"
    r"\s*:?\s*$", re.I)
# A CONSOLIDATED docket drops the shared year on the numbers that follow
# ('Nos. 21-8005/8007') and keeps it where the years differ — one cell.
_DOCKET_TAIL = r"(?:[/,;]\s*(?:\d{2}-)?\d{2,5})*"
_MASTHEAD_DOCKET = re.compile(
    r"^(?:Case\s+)?Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$", re.I)
_CAPTION_DOCKET = re.compile(
    r"^Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$", re.I)
# The tribunal's own number, as the origin band prints it: 'No. 1:16-bk-
# 10407—Joan A. Lloyd, Judge.', 'No. 08-28289; Adv. Pro. 15-00021—Jennie D.
# Latta, Judge.', 'Nos. 18-bk-4808; 20-ap-80139—James W. Boyd, Bankruptcy
# Judge.'
_LOWER_DOCKET = re.compile(r"^(?:Adv\.\s+)?Nos?\.\s", re.I)

# THE COURT'S OWN SECTION LABELS, fenced by typed rules. A closed
# vocabulary of labels the court prints alone on a centred row.
# 'LITIGANT' is the panel's own heading for the block where the only
# appearance is a party's own ('ON BRIEF: … pro se.').
_LABEL_COUNSEL = ("COUNSEL", "LITIGANT", "LITIGANTS")
_LABEL_TITLE = ("OPINION", "OPINION AND ORDER", "AMENDED OPINION",
                "SUBSTITUTE OPINION", "CORRECTED OPINION", "ORDER",
                "AMENDED ORDER", "JUDGMENT", "OPINION AND JUDGMENT")

# ORIGIN OPENERS — how the panel names the tribunal it is reviewing, in
# both the roman form the ruled slip sets and the caps form the paren-rail
# one prints inside its caption box.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "on petition for review", "on petitions for review",
    "petition for review", "petitions for review",
    "on remand from", "on review of", "review of",
    "on direct appeal from", "on interlocutory appeal from",
)
# THE DATE LABELS, longest first so 'Decided and Filed' wins over 'Filed'.
_DATE_LABELS = ("argued and submitted", "decided and filed",
                "submitted on briefs", "reargued", "argued", "submitted",
                "decided", "amended", "filed", "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. 'debtor'/'debtors' is the bankruptcy caption's own status.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "applicants", "claimant", "claimants", "party-in-interest",
    # …and the ones only a bankruptcy caption prints.
    "creditor", "creditors", "possession",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# The publication flag, read on its stem so every form answers alike. The
# NOT- form is tested first: the others are its own suffix.
_UNPUBLISHED = "not recommended for publication"
_PUBLISHED = ("recommended for full-text publication",
              "recommended for publication")
# THE LIMITED-PRECEDENT NOTICE the panel prints in place of a flag on its
# unpublished paper ('By order of the Bankruptcy Appellate Panel, the
# precedential effect of this decision is limited to the case and parties
# pursuant to 6th Cir. BAP LBR 8024-1(b).'). It is the court's own
# publication apparatus, set in the flag's own band and its own size, so it
# stays where the page prints it and its meaning is copied into criteria —
# the same treatment ca6 gives 'Pursuant to Sixth Circuit I.O.P. 32.1(b)'.
_NOTICE_OPENER = "by order of the bankruptcy appellate panel"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squeeze(text: str) -> str:
    """'O R D E R' -> 'ORDER'. The panel letter-spaces the label on its
    unsigned orders; it is the same label."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _label(text: str, vocab: tuple) -> str | None:
    """The section label ``text`` sets, or None.

    A LABEL IS SET IN CAPS. Folding the case before the lookup made the
    court's own vocabulary match ordinary prose: jeff_moyer's disposition
    ends on the word 'opinion.' alone at the body rail, which read as the
    OPINION label, ended the walk one row early and handed the fence, the
    real label and the page-2 byline to the writing."""
    flat = _norm(text)
    if not flat or flat != flat.upper():
        return None
    sq = _squeeze(flat)
    return sq if sq in vocab else None


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("bankruptcy appellate panel",
                   "of the sixth circuit",
                   "bankruptcy appellate panel of the sixth circuit",
                   "united states court of appeals",
                   "for the sixth circuit",
                   "united states court of appeals for the sixth circuit")


def _is_flag(text: str) -> str | None:
    low = _norm(text).lower().rstrip(".")
    if low.startswith(_UNPUBLISHED):
        return "unpublished"
    if low.startswith(_PUBLISHED):
        return "published"
    return None


def _is_stamp(text: str) -> bool:
    """The court's own slip apparatus above the banner: the file name of the
    slip itself, and the I.O.P. citation the circuit's flag issues under."""
    low = _norm(text).lower()
    return (low.startswith("file name")
            or low.startswith("pursuant to sixth circuit"))


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_disposition(text: str) -> bool:
    """'HUMPHREY, J., filed the opinion of the Bankruptcy Appellate Panel in
    which BUCHANAN, J., joined.  DALES, J. (pp. 27–28), filed a separate
    opinion concurring in the result.'

    The panel states who wrote what in a row of its own between the
    appearances and the OPINION fence. It reads like a byline and names
    judges like a roster, so without a test of its own it ends the reader
    one section early. The panel's formula is 'filed' where the circuit's is
    'delivered'; both spellings occur in this corpus, and both are the
    opinion of the panel or a separate one."""
    low = _norm(text).lower()
    return any(k in low for k in
               ("filed the opinion", "delivered the opinion",
                "filed a separate", "delivered a separate",
                "delivered an order"))


def _labelled_dates(text: str) -> dict:
    """{'argued': 'February 12, 2019', 'decided_and_filed': 'April 15,
    2019'}. One label per centred row. A date row is SHORT — 'filed' inside
    prose is an ordinary English word."""
    if len(text) > 120:
        return {}
    low = text.lower()
    hits = []
    for label in _DATE_LABELS:
        at = low.find(label)
        if at < 0:
            continue
        if at and low[at - 1].isalnum():
            continue
        hits.append((at, label))
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
        # A DATE VALUE IS READ IN THE FORM THE PAGE SET IT — the comma in
        # 'April 15, 2019' is part of the date, so the value is a SLICE of
        # the row, never a re-join of its tokens.
        mm = re.search(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}"
                       r"|\d{1,2}\s+[A-Z][a-z]+\.?\s+\d{4})", seg)
        if mm is None:
            continue
        first = mm.group(1).split()[0].strip(".,").lower()
        if first not in _MONTHS and not first.isdigit():
            continue
        out[label.replace(" ", "_")] = _norm(mm.group(1))
    return out


def _is_date_row(text: str) -> bool:
    flat = _norm(text)
    if len(flat) > 120:
        return False
    low = flat.lower()
    return bool(_labelled_dates(flat)) and any(
        low.startswith(lab) for lab in _DATE_LABELS)


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test. The
    panel wraps its roster when a judge carries the chief's designation
    ('Before: BAUKNIGHT, Chief Judge; GREGG, and MASHBURN, / Bankruptcy
    Appellate Panel Judges.')."""
    flat = _norm(text)
    at = flat.lower().find("sitting by")
    if at > 0:
        flat = flat[:at].rstrip(" ,")
    body = flat
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
            # A generational SUFFIX is part of the judge's name, not another
            # judge.
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _trial_judge(text: str):
    """'No. 1:16-bk-10407—Joan A. Lloyd, Judge.' — the judge is the clause
    that ENDS on a bench word. Splitting on full stops instead cuts the
    clause at the judge's own middle initial."""
    flat = _norm(text)
    mm = re.search(r"[—–-]\s*([A-Z][^—–]*?,\s*(?:[A-Z][\w.]*\s+){0,3}"
                   r"(?:Chief\s+|Senior\s+|Magistrate\s+|District\s+|"
                   r"Bankruptcy\s+|Circuit\s+)?Judges?)\s*\.?$", flat)
    return _norm(mm.group(1)) if mm else None


# --------------------------------------------------------------------------
# the rail — bap6's caption divider, and the dispatch
# --------------------------------------------------------------------------

def _column(chars: list, floor: int) -> dict | None:
    if len(chars) < floor:
        return None
    x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
    stack = [c for c in chars if abs(c["x0"] - x) < 3]
    if len(stack) < floor:
        return None
    return {"x": float(x),
            "top": min(c["top"] for c in stack),
            "bottom": max(c["bottom"] for c in stack)}


def _rail(pm) -> dict | None:
    """The caption's drawn divider on ``pm``: {'glyph', 'x', 'top',
    'bottom'}, or None.

    The box glyphs are tried first and the paren rail second, because ')'
    also occurs in ordinary prose. A rail is a COLUMN: glyphs stacked at one
    x, not a count of glyphs anywhere on the page."""
    box, paren, alone = [], [], []
    for line in pm.lines:
        solo = _norm(line.plain) == ")"
        for c in line.chars:
            t = c.get("text") or ""
            if t in _BOX:
                box.append(c)
            elif t == ")":
                paren.append(c)
                if solo:
                    alone.append(c)
    found = _column(box, _BOX_FLOOR)
    if found is not None:
        found["glyph"] = "│"
        return found
    found = _column(paren, _PAREN_FLOOR) or _column(alone, _PAREN_ALONE_FLOOR)
    if found is not None:
        found["glyph"] = ")"
        return found
    return None


def _drawn_fence(pm) -> float | None:
    """Where the ruled slip draws its 110pt rule, or None. The same page
    draws an underline, an in-re divider and a footnote separator; the axis
    test takes none of them."""
    for r in pm.h_rules:
        if not (_DRAWN_FENCE[0] <= r.width <= _DRAWN_FENCE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _DRAWN_OFF_AXIS:
            continue
        return r.top
    return None


def _rail_chars(line, rail) -> list:
    """The chars of ``line`` that belong to the rail's own column."""
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    keep = []
    for c in line.chars:
        t = (c.get("text") or "")
        if not t.strip():
            continue
        if (t in _BOX or t == rail["glyph"] or t == _RAIL_LEAD) \
                and lo <= c["x0"] <= hi:
            keep.append(c)
    return keep


def _shed_rail(line, rail):
    """``line`` with the rail's glyphs removed, or None when the line WAS the
    rail. The glyph is identified by its COLUMN, never by its character."""
    rails = {id(c) for c in _rail_chars(line, rail)}
    if not rails:
        return line
    kept = [c for c in line.chars if id(c) not in rails]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept)


def _merge_rows(lines: list, ids: dict) -> list:
    """Same-row pieces are ONE row.

    A justified line pdfio broke at a wide gap looks like two rows outside
    each other's column, which ends the counsel block mid-entry. PROVENANCE
    SURVIVES THE MERGE: the pieces' line ids merge with their text, keyed on
    the lead piece's id so nothing a merged row is placed into loses the
    lines it came from."""
    out: list = []
    for line in lines:
        if out and out[-1].page == line.page \
                and abs(out[-1].top - line.top) <= _ROW_TOL:
            prev = out[-1]
            merged = _replace(
                prev, chars=sorted(prev.chars + line.chars,
                                   key=lambda c: c["x0"]),
                x0=min(prev.x0, line.x0), x1=max(prev.x1, line.x1),
                top=min(prev.top, line.top),
                bottom=max(prev.bottom, line.bottom))
            ids[merged.id] = ids.get(prev.id, (prev.id,)) + (line.id,)
            out[-1] = merged
        else:
            out.append(line)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="bap6")
def read_headmatter_bap6(model, geom, **_):
    """Read bap6's rail-and-fence headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _rail(page1)
    if rail is None:
        return NOTHING                    # no caption divider: not bap6's
    fence_top = _drawn_fence(page1)
    if rail["glyph"] == "│":
        if fence_top is None or fence_top > rail["top"]:
            return NOTHING                # the box always comes ruled
        style = STYLE_RULED_SLIP
    else:
        style = STYLE_PAREN_RAIL

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(BAP6.byline)
    pages = {pm.number: pm for pm in model.pages}

    rows: list = []                       # content lines, in page order
    head_lines: list = []                 # the running head, page by page
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: the one-row running
            # head and the foot folio. Core measures and records those; the
            # reader steps over them rather than claiming them twice — and
            # takes the head core could not see, because a reader that claims
            # a region inherits its furniture.
            if finder.kind(pm, line):
                continue
            if pm.number > 1 and line.top < _HEAD_BAND_MAX:
                head_lines.append(line)
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for l in rows[:8]):
        return NOTHING                    # the paper always names its court

    band = (rail["top"] - 6.0, rail["bottom"] + 6.0)
    box_lines = [l for l in rows
                 if l.page == 1 and band[0] <= l.top <= band[1]]
    if not box_lines:
        return NOTHING

    crit: dict = {"headmatter_style": style}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    anchor_ids: list[int] = []
    banner_rows: list[str] = []
    caption_rows: list[str] = []
    party_rows: list[str] = []
    origin_rows: list[str] = []
    panel_rows: list[str] = []
    counsel_rows: list[str] = []
    disposition_rows: list[str] = []
    dates: dict = {}
    lower_dockets: list[str] = []

    row_ids: dict = {}                # merged row -> the pieces it came from

    def emit(line, role: str, text: str | None = None, rel_from: float = 0.0):
        pm = pages[line.page]
        align = line_alignment(line, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        rel = 0.0
        if rel_from and align == "L" and line.x0 > rel_from + 12:
            rel = min(line.x0 - rel_from, (pm.width or 612.0) * 0.6)
        ids = row_ids.get(line.id, (line.id,))
        items.append(m.HmLine(
            text=line_markup(line) if text is None else text,
            prov=m.Prov(line.page, ids),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role))
        consumed.update(ids)

    # ---- the masthead: everything the page prints above the rail --------
    notice_open = False
    for line in rows:
        if line.page != 1 or line.top >= band[0]:
            continue
        text = _norm(line.plain)
        flag = _is_flag(text)
        if notice_open:
            # THE NOTICE IS A RUN, and it closes on its own sentence: the
            # rows after its opener carry no cue of their own ('of this
            # decision is limited to the case and parties pursuant to').
            emit(line, "court")
            notice_open = not text.rstrip().endswith(".")
        elif flag:
            crit.setdefault("publication_status", flag)
            emit(line, "court")
        elif text.lower().startswith(_NOTICE_OPENER):
            crit.setdefault("publication_status", "unpublished")
            emit(line, "court")
            notice_open = not text.rstrip().endswith(".")
        elif _is_stamp(text):
            emit(line, "court")
        elif _is_banner(text):
            banner_rows.append(text)
            emit(line, "court")
        elif _MASTHEAD_DOCKET.match(text):
            # The PAREN-RAIL slip states its docket ABOVE the banner; the
            # ruled one states it inside the caption box.
            crit.setdefault("docket_number", text.rstrip("."))
            emit(line, "docket")
        else:
            # An unread masthead row means this is not the cover the
            # contract describes; core reads the whole document instead.
            return NOTHING

    # THE DRAWN FENCE renders where the page draws it. A reader that claims
    # the region inherits the court's own section marks, and core only draws
    # them for rows the reader left behind.
    if fence_top is not None and items:
        items.append(m.Rule(prov=items[-1].prov, span="full"))

    # ---- the caption box ------------------------------------------------
    block, cap_left, cap_right, below_divider = _caption(
        box_lines, rail, pages[1], geom, body_size)
    if block is None:
        return NOTHING
    items.append(block)
    consumed.update(block.prov.line_ids)
    caption_rows = [t for t in cap_left if t]
    # THE IN-RE DIVIDER separates the debtor from the parties to the appeal;
    # `parties` is built from what stands below it, and the whole caption is
    # published either way.
    party_rows = [t for t in cap_left[below_divider:] if t]
    # THE RIGHT COLUMN carries the docket on the ruled slip and the origin
    # plus the paper's name on the paren-rail one — each cell is tagged for
    # what it is, so nothing in the box reads as 'caption' by default.
    origin_cells: list[str] = []
    for row, flat in zip(block.right, cap_right):
        if not flat:
            continue
        if _CAPTION_DOCKET.match(flat):
            row.role = "docket"
            if crit.get("docket_number"):
                crit.setdefault("other_dockets", []).append(flat.rstrip("."))
            else:
                crit["docket_number"] = flat.rstrip(".")
        elif _label(flat, _LABEL_TITLE):
            row.role = "title"
            crit.setdefault("title", _label(flat, _LABEL_TITLE))
        elif origin_cells or _origin_opener(flat):
            row.role = "lower-court"
            origin_cells.append(flat)
        else:
            caption_rows.append(flat)
            party_rows.append(flat)
    if origin_cells:
        origin_rows.append(" ".join(origin_cells))

    # ---- everything below the box, by landmark --------------------------
    below = _merge_rows([l for l in rows if l.page > 1 or l.top > band[1]],
                        row_ids)
    # THE ORIGIN BAND. Both its ends are landmarks the panel prints on every
    # record: the caption box above, and the first date row — or, where the
    # slip states no date, the roster — below. Inside it, what is shaped
    # like a docket is a docket and everything else is the tribunal, so the
    # second statement of a two-tribunal origin needs no opener of its own.
    origin_end = len(below)
    for k, l2 in enumerate(below):
        t2 = _norm(l2.plain)
        if _is_date_row(t2) or _BARE_DATE.match(t2) \
                or t2.lower().startswith("before") \
                or _label(t2, _LABEL_COUNSEL) \
                or _label(t2, _LABEL_TITLE):
            origin_end = k
            break
    state = "tail"
    stop = False
    i = 0
    while i < len(below) and not stop:
        line = below[i]
        text = _norm(line.plain)
        low = text.lower()

        def run_on(j: int) -> int:
            """How many rows this statement WRAPS onto: the panel ends every
            one of its tail statements on a full stop and starts the next on
            its own row. A row that OPENS a landmark of its own ends the
            wrap whatever the row above it ended on."""
            k = j
            while (k + 1 < len(below)
                   and not _norm(below[k].plain).rstrip().endswith(
                       (".", ":", "!", "?"))
                   and below[k + 1].page == below[k].page
                   and not _opens_landmark(_norm(below[k + 1].plain))):
                k += 1
            return k

        # THE DISPOSITION IS A PARAGRAPH, and every row of it names judges
        # the way a byline does. What separates its continuation from the
        # writing's own byline is where the court sets it: the panel indents
        # the statement's first row to the paragraph indent and runs the
        # rest back to the body rail, and it signs every writing at the
        # indent.
        if (state == "summary"
                and abs(line.x0 - body_x0) <= 2.5
                and line.page == below[i - 1].page
                and not _opens_landmark(text)):
            disposition_rows.append(text)
            emit(line, "summary")
            i += 1
            continue
        # A BYLINE ENDS THE READER, always and everywhere below the box.
        if parser.parse(text) is not None and not _is_disposition(text):
            break
        if _TYPED_RULE.match(text):
            # A TYPED FENCE closes whatever section was open — except inside
            # the origin band, where the panel uses it to separate the two
            # tribunals of a direct appeal. It is the court's own section
            # mark, so it renders where the page types it; the fence that
            # OPENS a title the writing needs as its anchor is left standing.
            nxt = below[i + 1] if i + 1 < len(below) else None
            if nxt is not None and _label(nxt.plain, _LABEL_TITLE) \
                    and not _claimable_title(below, i + 1, parser):
                break
            _rids = row_ids.get(line.id, (line.id,))
            items.append(m.Rule(prov=m.Prov(line.page, _rids),
                                typed=True, span="full"))
            consumed.update(_rids)
            if i >= origin_end:
                state = "tail"
            i += 1
            continue
        if _label(text, _LABEL_COUNSEL):
            emit(line, "counsel")
            state = "counsel"
            i += 1
            continue
        _tl = _label(text, _LABEL_TITLE)
        if _tl:
            if not _claimable_title(below, i, parser):
                break
            crit.setdefault("title", _tl)
            emit(line, "title")
            anchor_ids.append(line.id)
            state = "tail"
            i += 1
            continue
        if _is_disposition(text):
            end = run_on(i)
            for l2 in below[i:end + 1]:
                disposition_rows.append(_norm(l2.plain))
                emit(l2, "summary")
            state = "summary"
            i = end + 1
            continue
        if state == "counsel":
            # INSIDE THE APPEARANCES only the court's own fence and its
            # disposition row interrupt: an entry opening 'ARGUED:' is an
            # appearance, not a date band, and the block runs to the rule
            # the court types under it.
            counsel_rows.append(text)
            emit(line, "counsel", rel_from=body_x0)
            i += 1
            continue
        if low.startswith("before"):
            end = run_on(i)
            for l2 in below[i:end + 1]:
                panel_rows.append(_norm(l2.plain))
                emit(l2, "panel")
            i = end + 1
            continue
        if _is_date_row(text) or _BARE_DATE.match(text):
            dates.update(_labelled_dates(text))
            emit(line, "date")
            i += 1
            continue
        if _LOWER_DOCKET.match(text):
            end = run_on(i)
            printed = _norm(" ".join(_norm(l2.plain)
                                     for l2 in below[i:end + 1]))
            lower_dockets.append(printed)
            for l2 in below[i:end + 1]:
                emit(l2, "lower-court")
            i = end + 1
            continue
        if i < origin_end or _origin_opener(text):
            end = run_on(i)
            printed = _norm(" ".join(_norm(l2.plain)
                                     for l2 in below[i:end + 1]))
            origin_rows.append(printed)
            for l2 in below[i:end + 1]:
                emit(l2, "lower-court")
            i = end + 1
            continue
        stop = True                       # a row this contract does not name

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        source = party_rows or caption_rows
        sides = _sides(source)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            one = _sides(source, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    for printed in lower_dockets:
        judge = _trial_judge(printed)
        if judge:
            crit.setdefault("lower_court_judge", judge)
        mm = re.match(r"^(Nos?\.\s*[^—–]+?)\s*(?:[—–]|$)", printed)
        if mm:
            crit.setdefault("other_dockets", []).append(
                _norm(mm.group(1)).rstrip("."))
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
    if disposition_rows:
        crit["disposition"] = _norm(" ".join(disposition_rows))
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE — its text is
        # copied into the criteria, the rows stay where the page put them.
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    for label, value in dates.items():
        if label in ("decided", "decided_and_filed", "filed", "amended",
                     "entered"):
            crit.setdefault("decision_date", value)
        elif label in ("submitted", "submitted_on_briefs",
                       "argued_and_submitted"):
            crit.setdefault("submitted", value)

    # A CLAIM MUST BE TOTAL: the head rows the reader stepped over are
    # recorded, not silently swallowed — and only for the pages the claim
    # actually reached, so a head on a page the writing owns is untouched.
    _last = max((l.page for l in rows if l.id in consumed), default=1)
    for line in head_lines:
        if line.page > _last:
            continue
        dropped.append(m.Dropped(
            text=_norm(line.plain), prov=m.Prov(line.page, (line.id,)),
            kind="running-head"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed,
            "anchor_ids": anchor_ids, "doc_type_final": None}


def _opens_landmark(text: str) -> bool:
    """Does ``text`` open a section of its own? The wrap rule needs this: a
    statement the court left unterminated still ends where the next landmark
    starts."""
    low = _norm(text).lower()
    return bool(_TYPED_RULE.match(text)
                or _label(text, _LABEL_COUNSEL)
                or _label(text, _LABEL_TITLE)
                or low.startswith("before")
                or _origin_opener(text)
                or _LOWER_DOCKET.match(text)
                or _is_date_row(text)
                or _BARE_DATE.match(text)
                or _is_disposition(text))


def _claimable_title(below: list, at: int, parser) -> bool:
    """Is the label row at ``below[at]`` the headmatter's, or the writing's
    anchor?

    The panel fences 'OPINION' above the byline that signs it and 'ORDER'
    above an order nobody signs. The label is headmatter when the writing
    under it opens on a byline of its own; where it does not, the label is
    the only thing that anchor can be, and claiming it costs the document
    its writing."""
    k = at + 1
    while k < len(below):
        text = _norm(below[k].plain)
        if _TYPED_RULE.match(text):
            k += 1
            continue
        return parser.parse(text) is not None
    return False


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the rail, or None."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


def _caption(box_lines: list, rail: dict, pm, geom, body_size: float):
    """bap6's caption box as a CaptionBlock, the two columns' text, and the
    row index just below the IN-RE DIVIDER.

    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned, and the
    rail's own glyphs — corners included — are shed from the cells they fell
    into. Whether a glyph landed inside a cell was pure accident: the column
    split keeps chars left of the divider or right of it, so a glyph whose
    x0 sat exactly on the divider went one way and an identical one a hair
    left of it went the other."""
    mid = rail["x"]
    rows: list[list] = []
    for line in sorted(box_lines, key=lambda l: (l.top, l.x0)):
        shed = _shed_rail(line, rail)
        if shed is None:
            continue                      # the line WAS the rail
        if rows and abs(rows[-1][0].top - shed.top) <= 2:
            rows[-1].append(shed)
        else:
            rows.append([shed])
    if not rows:
        return None, [], [], 0

    # THE IN-RE DIVIDER: a rule the court sets across the LEFT COLUMN ONLY,
    # between the main case and this appeal. It is typed on most of the
    # corpus and DRAWN on the rest, and either way it ends short of the rail
    # — which is what tells it from the page-axis fence above the box.
    divider_bottom = None
    for r in getattr(pm, "h_rules", ()):
        if r.x1 < mid and rail["top"] <= r.top <= rail["bottom"]:
            divider_bottom = max(divider_bottom or 0.0, r.top)

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
    below_divider = 0
    for row in rows:
        # SIDES SPLIT AT THE RAIL ITSELF, glyph by glyph. Whether pdfio
        # already broke a justified row at its column gap is an accident of
        # how wide the gap happened to be — blasingame sets 'Plaintiff-
        # Appellant (18-8010), > Nos. 18-8010/8013/8018' as ONE run, and a
        # whole-line test put its docket in the party column.
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
        # ampersand the caption prints ('DINSMORE &amp;amp; SHOHL').
        lp = _norm(" ".join(c.plain for c in l_cells))
        left_plain.append(lp)
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
        top = row[0].top
        if _TYPED_RULE.match(lp) or (divider_bottom is not None
                                     and top <= divider_bottom):
            below_divider = len(left)
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: once the
    # glyphs are gone the rows that held nothing else are empty on BOTH
    # sides, and left standing they render as phantom blank rows.
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop()
        right.pop()
        left_plain.pop()
        right_plain.pop()
    below_divider = min(below_divider, len(left))
    block = m.CaptionBlock(
        left=left, right=right, rail=rail["glyph"], rail_rows=len(left),
        style_id=("parenthetical-box" if rail["glyph"] == ")" else None),
        fp={"rail": rail["glyph"], "rail_band": (rail["top"], rail["bottom"]),
            "mid_x": mid},
        prov=m.Prov(pm.number, tuple(sorted(l.id for l in box_lines))))
    return block, left_plain, right_plain, below_divider


def _all_status(chunk: str) -> bool:
    """Is ``chunk`` nothing but party STATUS?

    A STATUS ROW may be TAGGED with the appeal it belongs to ('Plaintiff-
    Appellant (18-8010),', 'Defendants-Appellees/Cross-Appellants (18-8013 &
    18-8018).'). The tag is apparatus: it says WHICH appeal the status is
    for, and it names nobody. A STATUS LABEL is hyphenated on this court's
    paper, so the hyphen separates roles the way a space does elsewhere; a
    party NAME that carries one survives, because every word has to be a
    status word for the chunk to be one."""
    bare = re.sub(r"\([^)]*\)", " ", chunk).strip().rstrip(",. ").lower()
    words = [w.strip(",.;–-/ ")
             for w in bare.replace("–", " ").replace("-", " ")
                          .replace("/", " ").split()]
    return bool(words) and all(
        w in _STATUS_WORDS or w in ("and", "supporting", "the", "-", "third",
                                    "party", "pro", "se", "cross", "in",
                                    "interest", "of")
        or not w for w in words)


def _shed_status_tail(flat: str) -> str:
    """'STEVEN K. BAILEY,  Defendant-Appellee.' -> 'STEVEN K. BAILEY'.

    Where the caption's own leading leaves room the panel sets a party and
    its appellate role side by side on ONE printed row, and the row is the
    unit the reader publishes. The role is still apparatus — but a CAPACITY
    is not ('DONALD F. HARKER, Trustee', 'BETTYE SUE BEDWELL, Chapter 7
    Trustee'), which is why only the closed role vocabulary is shed and only
    from the end."""
    parts = flat.rstrip(",. ").split(",")
    while len(parts) > 1 and _all_status(parts[-1]):
        parts.pop()
    return ",".join(parts).rstrip(", ") or flat


def _sides(caption_rows: list, one_sided: bool = False):
    """The two party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    status labels, the appeal numbers they are tagged with and the pivot are
    apparatus, not names."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _norm(row)
        if not flat or not any(c.isalpha() for c in flat):
            continue                      # the in-re divider, drawn or typed
        first = flat.split()[0].rstrip(".").lower() if flat.split() else ""
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        if _all_status(flat):
            continue
        if flat.lower().startswith(("v.", "vs.")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1] if len(flat.split()) > 1 else ""
            if not flat:
                continue
        side.append(_shed_status_tail(flat))
    # THE COMMA is the caption's own apparatus — it leads to the status row
    # below. The FULL STOP is not: it ends the abbreviation the party is
    # incorporated under ('PHOENIX MANAGEMENT SERVICES LLC.'), and stripping
    # it renames the party.
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))
