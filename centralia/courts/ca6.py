"""United States Court of Appeals for the Sixth Circuit ('ca6').

Everything unique to ca6 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'rail and fence'. ca6 draws its caption's column divider,
and the glyph it draws it with says which of the court's two papers this
is. Nothing else has to be guessed at:

    published slip (65 of 103) — the caption is a BOX drawn in box-drawing
    glyphs ('┐' '│' '┘'), the court draws ONE 110pt rule on the page axis
    to open it, and every labelled section below it is fenced above and
    below by a TYPED rule ('_________________', 102pt, on the same axis):

        RECOMMENDED FOR PUBLICATION            the publication flag, 9pt
        Pursuant to Sixth Circuit I.O.P. 32.1(b)
        File Name: 26a0148p.06                 the court's slip file name
        UNITED STATES COURT OF APPEALS         the banner, 15pt bold
        FOR THE SIXTH CIRCUIT
        ────────────                           a DRAWN 110pt rule (x0=253)
        ALEXANDRE ANSARI,                  ┐   the caption box: parties…
              Plaintiff-Appellee,          │
                                           │>  No. 24-1743   …and the docket
        v.                                 │
        MOISES JIMENEZ,                    │
              Defendant-Appellant.         │
                                           ┘
        Appeal from the United States District Court …   the origin
        No. 2:20-cv-10719—Stephen Joseph Murphy III, District Judge.
        Argued:  December 10, 2025                       the dates
        Decided and Filed:  May 14, 2026
        Before:  BATCHELDER, GILMAN, and LARSEN, Circuit Judges.   the roster
        _________________                                a TYPED fence
        COUNSEL
        ARGUED:  Mary Massaron, PLUNKETT COONEY, …       the appearances
        CLAY, J., delivered the opinion of the court …   who wrote what
        _________________
        OPINION
        _________________
        LARSEN, Circuit Judge.  Alexandre Ansari was …   the first byline

    unpublished slip (38 of 103) — NO rules at all, drawn or typed. A
    stacked ')' is the caption's divider and the whole zone system: the
    masthead is what stands above it, the caption is what stands inside it
    (left: the parties; right: the origin, and the word OPINION), and the
    single row below it is the roster. The byline runs straight in:

        NOT RECOMMENDED FOR PUBLICATION
        File Name:  26a0335n.06
        Case No. 26-5006                       the docket, ABOVE the banner
        UNITED STATES COURT OF APPEALS
        FOR THE SIXTH CIRCUIT
        BIZZACK CONSTRUCTION, LLC,   )
              Plaintiff-Appellant,   )
                                     )  ON APPEAL FROM THE UNITED
        v.                           )  STATES DISTRICT COURT FOR
                                     )  THE EASTERN DISTRICT OF
        TRC ENGINEERS, INC.,         )  KENTUCKY
              Defendant-Appellee.    )
                                     )                  OPINION
        Before: DAVIS, MATHIS, and RITZ, Circuit Judges.
        MATHIS, Circuit Judge.  West Virginia awarded …

The dispatch is the RAIL, not the flag it prints beside it: over the whole
corpus the box rail and the 110pt drawn rule occur together on all 65
published records and on none of the 38 unpublished ones. A record whose
caption draws neither rail is not this contract and gets NOTHING.

The reader claims HEADMATTER ONLY. It stops at the first byline, and
everything below — the writings, their footnotes, their paragraphs — is
core's. Where an unsigned writing would have to open on the title row the
court fences ('ORDER'), that fence is left standing: an order that lost its
anchor is a worse trade than a title row nobody tagged.
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
# `_CIRCUIT_GRAMMAR` loop ca6 used to sit in, so nothing about its bylines
# changes by being moved here.
CA6 = register(CourtProfile(
    "ca6", "United States Court of Appeals for the Sixth Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_RULED_SLIP = "ruled slip"          # published: box rail + typed fences
STYLE_PAREN_RAIL = "paren-rail slip"     # unpublished: a ')' rail, no rules

# ---- ca6's declared facts (measured over the corpus, not tuned) ----------
# THE BOX: the published caption's divider is drawn in box-drawing glyphs,
# corners included — '┐' opens it and '┘' closes it, and both are the rail,
# not a cell.
_BOX = "│┃┐┘┌└├┤┬┴┼"
# THE PAREN RAIL: ')' occurs in ordinary prose, so it needs a taller stack
# before it counts as a divider. Six, the old reader's floor.
_BOX_FLOOR, _PAREN_FLOOR = 3, 6
# The published template sets a '>' at the docket cell as part of the same
# drawn rail; it arrives as its own glyph in the rail's column.
_RAIL_LEAD = ">"
# A glyph is the RAIL'S when it stands in the rail's own column. Measured:
# the box column is 8pt wide ('│' at 342.9, '>' at 346.5-349), so 12pt
# clears the whole bracket and reaches nothing else on the row.
_RAIL_WINDOW = 12.0
# THE DRAWN FENCE that opens the published caption: 110.1pt wide, x0=253.0
# on a 612pt page, top~166 — identical on all 65 published records.
_DRAWN_FENCE = (60.0, 200.0)
_DRAWN_OFF_AXIS = 40.0
# How far below the caption the block may still run. The counsel block
# wraps the page on 29 records; three pages is more than any of them needs.
_MAX_PAGES = 4
# THE RUNNING HEAD'S BAND. ca6 sets a one-row head on every continuation
# page — 'No. 24-1743  Ansari v. Jimenez  Page 2' — at top 55.8 in the
# published measure and 43.9 in the slip measure, and it WRAPS to a second
# row when the short case name is long (bonfiglioli runs to 69.6). Measured
# over the corpus the head band bottoms out at 69.6 and the body never opens
# above 73.8, so 72.0 separates them everywhere.
#
# Core recognizes the head by REPETITION, which needs pages to repeat on: a
# two-page record prints it once, and there the reader must know its own
# court's stationery (texas_assn read its page-2 head as an appearance).
_HEAD_BAND_MAX = 72.0

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# A LABEL WITH NO VALUE IS STILL THE DATE BAND: liles sets 'Decided and
# Filed:' alone, because the slip states no decision date. Read as an
# unknown row it ended the walk one line above the roster.
_BARE_DATE = re.compile(
    r"^(?:Argued(?:\s+En\s+Banc)?(?:\s+and\s+Submitted)?|Submitted"
    r"|Reargued|Decided(?:\s+and\s+Filed)?|Filed|Amended|Entered)"
    r"\s*:?\s*$", re.I)
# The rehearing posture and the tribunal share one origin band, and on part
# of the corpus they share one STATEMENT ('On Petition for Rehearing En
# Banc / United States District Court for the Western District of Tennessee
# at Memphis.'). The posture is history; what follows it is the origin.
_REHEARING_CLAUSE = re.compile(
    r"^(On\s+Petitions?\s+for\s+Rehearing(?:\s+En\s+Banc)?)\s*(.*)$",
    re.I | re.S)
# A CONSOLIDATED docket drops the shared year on the numbers that follow
# ('Nos. 24-3133/3206/3252') and keeps it where the years differ ('Nos.
# 24-6134/25-5111') — both forms are one docket cell.
_DOCKET_TAIL = r"(?:[/,;]\s*(?:\d{2}-)?\d{2,5})*"
_MASTHEAD_DOCKET = re.compile(
    r"^(?:Case\s+)?Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$", re.I)
_CAPTION_DOCKET = re.compile(
    r"^Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$", re.I)
# The lower tribunal's own number, as the origin band prints it:
# 'No. 2:20-cv-10719—Stephen Joseph Murphy III, District Judge.',
# 'No. A 046 526 935.', 'Federal Communications Commission, Agency No.
# 23-111.'
_LOWER_DOCKET = re.compile(r"^Nos?\.\s", re.I)
_AGENCY_NO = re.compile(r"\bAgency No\.", re.I)

# THE COURT'S OWN SECTION LABELS, fenced by typed rules. A closed
# vocabulary of labels the court prints alone on a centred row — never a
# test on anything it says about a case.
_LABEL_COUNSEL = ("COUNSEL",)
_LABEL_TITLE = ("OPINION", "AMENDED OPINION", "SUBSTITUTE OPINION",
                "CORRECTED OPINION", "ORDER", "AMENDED ORDER", "JUDGMENT")

# ORIGIN OPENERS — how ca6 names the tribunal it is reviewing, in both the
# roman form the published slip sets and the caps form the unpublished one
# prints inside its caption box.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "on appeals from",
    "cross-appeal from", "cross-appeals from",
    "on petition for review", "on petitions for review",
    "petition for review", "petitions for review",
    "on petition for rehearing", "on petitions for rehearing",
    "on remand from", "on review of", "review of",
    "on application for", "application for",
    "on petition for writ", "on petition for a writ",
    "on direct appeal from", "on interlocutory appeal from",
)
_REHEARING = ("on petition for rehearing", "on petitions for rehearing")
# THE DATE LABELS ca6 prints, longest first so 'Decided and Filed' wins
# over 'Filed'.
_DATE_LABELS = ("argued and submitted", "decided and filed",
                "submitted on briefs", "reargued", "argued", "submitted",
                "decided", "amended", "filed", "entered")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "amicus", "amici", "movant", "movants", "applicant",
    "applicants", "claimant", "claimants", "party-in-interest",
)
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
# The publication flag, read on its stem so both forms answer alike. The
# NOT- form is tested first: the other is its own suffix.
_UNPUBLISHED = "not recommended for publication"
_PUBLISHED = "recommended for publication"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _squeeze(text: str) -> str:
    """'O P I N I O N' -> 'OPINION'. ca6 letter-spaces the label on part of
    the unpublished corpus; it is the same label."""
    flat = _norm(text).rstrip(".:").upper()
    return re.sub(r"(?<=\b\w) (?=\w\b)", "", flat)


def _is_banner(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return low in ("united states court of appeals",
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
    """The court's own slip apparatus above the banner: the I.O.P. citation
    the flag is issued under, and the file name of the slip itself."""
    low = _norm(text).lower()
    return (low.startswith("pursuant to sixth circuit")
            or low.startswith("file name"))


def _origin_opener(text: str) -> bool:
    return _norm(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_disposition(text: str) -> bool:
    """'CLAY, J., delivered the opinion of the court in which COLE, J.,
    concurred.  MURPHY, J. (pp. 25–62), delivered a separate dissenting
    opinion.'

    ca6 states who wrote what in a row of its own between the appearances
    and the OPINION fence. It reads like a byline and names judges like a
    roster, so without a test of its own it ends the reader one section
    early. The court's formula is always 'delivered' — the opinion of the
    court, or a separate one, or an order."""
    low = _norm(text).lower()
    return ("delivered the opinion" in low or "delivered a separate" in low
            or "delivered an order" in low)


def _labelled_dates(text: str) -> dict:
    """{'argued': 'December 10, 2025', 'decided_and_filed': 'May 14, 2026'}.

    ca6 sets one label per centred row. A date row is SHORT — 'filed'
    inside prose is an ordinary English word."""
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
        # 'May 14, 2026' is part of the date, so the value is a SLICE of
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
    that are not TITLES — a closed bench vocabulary, never a case test.
    The designation clause a visiting judge carries ('… sitting by
    designation.') names nobody, so the roster ends where it begins."""
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
            # A generational SUFFIX is part of the judge's name, not
            # another judge.
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _trial_judge(text: str):
    """'No. 2:20-cv-10719—Stephen Joseph Murphy III, District Judge.' — the
    judge is the clause that ENDS on a bench word. Splitting on full stops
    instead cuts the clause at the judge's own middle initial."""
    flat = _norm(text)
    mm = re.search(r"[—–-]\s*([A-Z][^—–]*?,\s*(?:[A-Z][\w.]*\s+){0,3}"
                   r"(?:Chief\s+|Senior\s+|Magistrate\s+|District\s+|"
                   r"Bankruptcy\s+|Circuit\s+)?Judges?)\s*\.?$", flat)
    return _norm(mm.group(1)) if mm else None


# --------------------------------------------------------------------------
# the rail — ca6's caption divider, and the dispatch
# --------------------------------------------------------------------------

def _rail(pm) -> dict | None:
    """The caption's drawn divider on ``pm``: {'glyph', 'x', 'top',
    'bottom', 'chars'}, or None.

    The box glyphs are tried first and the paren rail second, because ')'
    also occurs in ordinary prose. A rail is a COLUMN: glyphs stacked at
    one x, not a count of glyphs anywhere on the page."""
    from collections import Counter

    def column(chars, floor):
        if len(chars) < floor:
            return None
        x, _n = Counter(round(c["x0"]) for c in chars).most_common(1)[0]
        stack = [c for c in chars if abs(c["x0"] - x) < 3]
        if len(stack) < floor:
            return None
        return {"x": float(x),
                "top": min(c["top"] for c in stack),
                "bottom": max(c["bottom"] for c in stack)}

    glyphs = [(c.get("text") or "", c) for l in pm.lines for c in l.chars]
    box = [c for t, c in glyphs if t in _BOX]
    found = column(box, _BOX_FLOOR)
    if found is not None:
        found["glyph"] = "│"
        return found
    paren = [c for t, c in glyphs if t == ")"]
    found = column(paren, _PAREN_FLOOR)
    if found is not None:
        found["glyph"] = ")"
        return found
    return None


def _drawn_fence(pm) -> float | None:
    """Where the published slip draws its 110pt rule, or None. A rule that
    spans the measure is an underline or a footnote separator, not a
    fence."""
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
    """``line`` with the rail's glyphs removed, or None when the line WAS
    the rail. The glyph is identified by its COLUMN, never by its
    character: a ')' that closes real text is not in the rail's column,
    and the same corpus sets identical glyphs inside and outside a cell
    purely by where the column split fell."""
    rails = {id(c) for c in _rail_chars(line, rail)}
    if not rails:
        return line
    kept = [c for c in line.chars if id(c) not in rails]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, chars=kept)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ca6")
def read_headmatter_ca6(model, geom, **_):
    """Read ca6's rail-and-fence headmatter, or NOTHING.

    NOTHING is returned for anything that is not one of the two contracts
    above: core's shared walk places those rows unidentified, which is a
    smaller error than a confident misreading."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    rail = _rail(page1)
    if rail is None:
        return NOTHING                    # no caption divider: not ca6's
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
    parser = BylineParser(CA6.byline)
    pages = {pm.number: pm for pm in model.pages}

    rows: list = []                       # content lines, in page order
    head_lines: list = []                 # the running head, page by page
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: ca6's one-row
            # running head and the foot folio. Core measures and records
            # those; the reader steps over them rather than claiming them
            # twice — and takes the head core could not see, because a
            # reader that claims a region inherits its furniture.
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
        return NOTHING                    # ca6 always names itself

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
    origin_rows: list[str] = []
    history_rows: list[str] = []
    panel_rows: list[str] = []
    counsel_rows: list[str] = []
    disposition_rows: list[str] = []
    dates: dict = {}
    lower_dockets: list[str] = []

    def emit(line, role: str, text: str | None = None, rel_from: float = 0.0):
        pm = pages[line.page]
        align = line_alignment(line, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        rel = 0.0
        if rel_from and align == "L" and line.x0 > rel_from + 12:
            rel = min(line.x0 - rel_from, (pm.width or 612.0) * 0.6)
        items.append(m.HmLine(
            text=line_markup(line) if text is None else text,
            prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role))
        consumed.add(line.id)

    # ---- the masthead: everything the page prints above the rail --------
    for line in rows:
        if line.page != 1 or line.top >= band[0]:
            continue
        text = _norm(line.plain)
        flag = _is_flag(text)
        if flag:
            crit.setdefault("publication_status", flag)
            emit(line, "court")
        elif _is_stamp(text):
            emit(line, "court")
        elif _is_banner(text):
            banner_rows.append(text)
            emit(line, "court")
        elif _MASTHEAD_DOCKET.match(text):
            # The UNPUBLISHED slip states its docket ABOVE the banner; the
            # published one states it inside the caption box.
            crit.setdefault("docket_number", text.rstrip("."))
            emit(line, "docket")
        else:
            # An unread masthead row means this is not the cover the
            # contract describes; core reads the whole document instead.
            return NOTHING

    # THE DRAWN FENCE renders where the page draws it. A reader that claims
    # the region inherits the court's own section marks, and core only
    # draws them for rows the reader left behind.
    if fence_top is not None and items:
        items.append(m.Rule(prov=items[-1].prov, span="full"))

    # ---- the caption box ------------------------------------------------
    block, cap_left, cap_right = _caption(box_lines, rail, pages[1], geom,
                                          body_size)
    if block is None:
        return NOTHING
    items.append(block)
    consumed.update(block.prov.line_ids)
    caption_rows = [t for t in cap_left if t]
    # THE RIGHT COLUMN carries the docket on the published slip and the
    # origin plus the OPINION label on the unpublished one — each cell is
    # tagged for what it is, so nothing in the box reads as 'caption' by
    # default.
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
        elif _squeeze(flat) in _LABEL_TITLE:
            row.role = "title"
            crit.setdefault("title", _squeeze(flat))
        elif origin_cells or _origin_opener(flat):
            row.role = "lower-court"
            origin_cells.append(flat)
        else:
            caption_rows.append(flat)
    if origin_cells:
        origin_rows.append(" ".join(origin_cells))

    # ---- everything below the box, by landmark --------------------------
    below = [l for l in rows if l.page > 1 or l.top > band[1]]
    state = "tail"
    stop = False
    i = 0
    while i < len(below) and not stop:
        line = below[i]
        text = _norm(line.plain)
        low = text.lower()

        def run_on(j: int) -> int:
            """How many rows this statement WRAPS onto: ca6 ends every one
            of its tail statements on a full stop, and starts the next on
            its own row.

            …but an unterminated row is not licence to swallow the next
            SECTION. roberts prints 'On Petition for Rehearing En Banc'
            with no stop and states its origin under it, and joined the two
            the record reported a rehearing and no lower court at all. A
            row that OPENS a landmark of its own ends the wrap whatever the
            row above it ended on."""
            k = j
            while (k + 1 < len(below)
                   and not _norm(below[k].plain).rstrip().endswith(
                       (".", ":", "!", "?"))
                   and below[k + 1].page == below[k].page
                   and not _opens_landmark(_norm(below[k + 1].plain))):
                k += 1
            return k

        # THE DISPOSITION IS A PARAGRAPH, and every row of it names judges
        # the way a byline does ('BOGGS, J., concurred in the judgment
        # only.' parses as one). What separates its continuation from the
        # writing's own byline is where the court sets it: ca6 indents the
        # statement's first row to the paragraph indent and runs the rest
        # back to the body rail, and it signs every writing at the indent.
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
            # A TYPED FENCE closes whatever section was open. It is the
            # court's own section mark, so it renders where the page types
            # it — but the fence that OPENS a title the writing needs as
            # its anchor is left standing (see below).
            nxt = below[i + 1] if i + 1 < len(below) else None
            if nxt is not None and _squeeze(nxt.plain) in _LABEL_TITLE \
                    and not _claimable_title(below, i + 1, parser):
                break
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            consumed.add(line.id)
            state = "tail"
            i += 1
            continue
        if _squeeze(text) in _LABEL_COUNSEL:
            emit(line, "counsel")
            state = "counsel"
            i += 1
            continue
        if _squeeze(text) in _LABEL_TITLE:
            if not _claimable_title(below, i, parser):
                break
            crit.setdefault("title", _squeeze(text))
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
            # disposition row interrupt: an entry opening 'ARGUED EN BANC:'
            # is an appearance, not a date band, and the block runs to the
            # rule the court types under it.
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
        if _origin_opener(text):
            end = run_on(i)
            printed = _norm(" ".join(_norm(l2.plain)
                                     for l2 in below[i:end + 1]))
            (history_rows if low.startswith(_REHEARING)
             else origin_rows).append(printed)
            for l2 in below[i:end + 1]:
                emit(l2, "lower-court")
            i = end + 1
            continue
        if _LOWER_DOCKET.match(text) or _AGENCY_NO.search(text):
            end = run_on(i)
            printed = _norm(" ".join(_norm(l2.plain)
                                     for l2 in below[i:end + 1]))
            lower_dockets.append(printed)
            for l2 in below[i:end + 1]:
                emit(l2, "lower-court")
            i = end + 1
            continue
        if _is_date_row(text) or _BARE_DATE.match(text):
            dates.update(_labelled_dates(text))
            emit(line, "date")
            i += 1
            continue
        stop = True                       # a row this contract does not name

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
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
    # THE ORIGIN BAND states the POSTURE and the TRIBUNAL, sometimes in two
    # statements and sometimes in one. Both are facts and neither
    # substitutes for the other: the rehearing clause is the history, and
    # what stands after it — on its own row or on the same one — is the
    # court being reviewed.
    for printed in list(history_rows):
        mm = _REHEARING_CLAUSE.match(printed)
        if mm is None:
            continue
        history_rows[history_rows.index(printed)] = _norm(mm.group(1))
        tail = _norm(mm.group(2))
        if tail:
            origin_rows.insert(0, tail)
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    if history_rows:
        crit["history"] = _norm(" ".join(history_rows))
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
    """Does ``text`` open a section of its own? The wrap rule needs this:
    a statement the court left unterminated still ends where the next
    landmark starts."""
    low = _norm(text).lower()
    return bool(_TYPED_RULE.match(text)
                or _squeeze(text) in _LABEL_COUNSEL
                or _squeeze(text) in _LABEL_TITLE
                or low.startswith("before")
                or _origin_opener(text)
                or _LOWER_DOCKET.match(text)
                or _is_date_row(text)
                or _BARE_DATE.match(text)
                or _is_disposition(text))


def _claimable_title(below: list, at: int, parser) -> bool:
    """Is the label row at ``below[at]`` the headmatter's, or the writing's
    anchor?

    ca6 fences 'OPINION' above the byline that signs it and 'ORDER' above
    an order nobody signs. The label is headmatter when the writing under
    it opens on a byline of its own; where it does not, the label is the
    only thing that anchor can be, and claiming it costs the document its
    writing."""
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
    """ca6's caption box as a CaptionBlock, plus the left column's text.

    Cells are PAIRED BY VISUAL ROW so the two stacks stay aligned, and the
    rail's own glyphs — corners included — are shed from the cells they
    fell into. Whether a glyph landed inside a cell was pure accident: the
    column split keeps chars left of the divider or right of it, so a glyph
    whose x0 sat exactly on the divider went one way and an identical one a
    hair left of it went the other."""
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
        # SIDES SPLIT AT THE RAIL ITSELF, glyph by glyph. Whether pdfio
        # already broke a justified row at its column gap is an accident of
        # how wide the gap happened to be — fischer sets 'Plaintiffs-
        # Appellees/Cross-Appellants, > Nos. 25-5385/5400' as ONE run, and
        # a whole-line test put its docket in the party column.
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
        # ampersand the caption prints ('NCTA&amp;amp;THE INTERNET').
        left_plain.append(_norm(" ".join(c.plain for c in l_cells)))
        right_plain.append(_norm(" ".join(c.plain for c in r_cells)))
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: once the
    # glyphs are gone the rows that held nothing else are empty on BOTH
    # sides, and left standing they render as phantom blank rows.
    while left and not _strip_tags(left[-1].text).strip() \
            and not _strip_tags(right[-1].text).strip():
        left.pop()
        right.pop()
        left_plain.pop()
        right_plain.pop()
    block = m.CaptionBlock(
        left=left, right=right, rail=rail["glyph"], rail_rows=len(left),
        style_id=("parenthetical-box" if rail["glyph"] == ")" else None),
        fp={"rail": rail["glyph"], "rail_band": (rail["top"], rail["bottom"]),
            "mid_x": mid},
        prov=m.Prov(pm.number, tuple(sorted(l.id for l in box_lines))))
    return block, left_plain, right_plain


def _sides(caption_rows: list, one_sided: bool = False):
    """The two party names either side of the pivot.

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
        if first in ("v", "vs") and len(flat) <= 6:
            side = right
            seen_pivot = True
            continue
        bare = flat.rstrip(",. ").lower()
        # A STATUS LABEL is hyphenated on this court's paper
        # ('Plaintiff-Appellee,'), so the hyphen separates roles the
        # way a space does elsewhere. A party NAME that carries one
        # ("RAMOS-RAMOS") survives, because every word has to be a
        # status word for the row to be one.
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
    # incorporated under ('MIDWEST ENGINEERED COMPONENTS, INC.'), and
    # stripping it renames the party.
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))
