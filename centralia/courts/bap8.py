"""Bankruptcy Appellate Panel of the Eighth Circuit ('bap8').

Everything unique to bap8 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'typed ladder'. The panel sits under the Eighth Circuit and
is issued the circuit clerk's stationery, so its cover states its own
structure in ink exactly the way ca8's does — with one difference that
matters, recorded below:

  * the MASTHEAD is ENGRAVED — both rows set in a blackletter display face
    (`OldEnglishTextMT`) that occurs nowhere else in the document, the first
    at 21pt against a 14pt body. 27 of 27 records, no exceptions;
  * every zone below it is FENCED by a TYPED RULE — a row of underscores
    and nothing else, centred on THE SHEET'S OWN AXIS. The zones come in a
    fixed order and each is closed by the fence under it:

        United States Bankruptcy Appellate Panel   the engraved masthead
        For the Eighth Circuit
        ___________________________                a TYPED fence
        No. 21-6002                                the BAP docket
        ___________________________
        In re: Anthony Ray Lincoln                 the bankruptcy case's
             Debtor                                  own style…
        ------------------------------             …a DIVIDER…
        Anthony Ray Lincoln                        …and the appeal's
             Debtor - Appellant                      parties, each with a
        v.                                           STATUS row set right
        James L. Snyder                              of the axis
             Acting U.S. Trustee - Appellee
        ____________
        Appeal from United States Bankruptcy Court  the origin — the
        for the Southern District of Iowa -           BANKRUPTCY court,
             Council Bluffs                           named by POSITION
        ____________
        Submitted: July 21, 2021                   the dates
        Filed:  July 28, 2021
        [Published]                                the publication flag,
        ____________                                 where the clerk sets it
        Before SALADINO, DOW and RIDGWAY, Bankruptcy Judges.   the roster,
        ____________                                  alone at the BODY RAIL
        SALADINO, Bankruptcy Judge                 the first byline

    A consolidated record repeats DOCKET-then-CAPTION and states the origin
    ONCE below the last of them (madison_resource_funding runs two petitions
    and reaches its roster on page 2); so does a record whose cover fills the
    sheet (richard_berkshire prints its roster at the head of page 2).

Three measurements do all of the work and none of them reads a word:

  * a ZONE is what stands between two typed fences;
  * a STATUS row is the row set in THE STATUS COLUMN — centred RIGHT of the
    sheet's axis, where every other centred row on the cover is symmetric
    about it. A zone holding one is a CAPTION; one that does not is the
    docket, the origin, the dates or the roster;
  * the ROSTER is the one zone set at the BODY RAIL.

THE DIFFERENCE FROM ca8, and it is the whole reason this file is not a
call into that one: **ca8 identifies its caption by the ITALIC its status
rows are set in, and bap8's clerk does not set them consistently.** Over
the 27 records the status rows are italic on 21 and plain roman on six
(hartford, kanyon, both richard_berkshire filings, chapter_jackson's
'Debtor.', citizens' 'Debtor'), and on two more the italic run covers only
half the row ('Debtors - Appellants' at 0.56). The face is not the fact;
the COLUMN is. Every status row on every record — italic or roman — is
centred right of the sheet's axis, and nothing else on the cover is.

The second difference is what the divider divides. ca8 types a hyphen rule
to put the amici below the parties; bap8 types the same rule (or a full
underscore fence — machele_goetz, natalia_lamonda, timothy_davies) to put
the APPEAL'S PARTIES below the bankruptcy case's own style. So the party
stack is the segment holding the pivot, and the 'In re:' stack above it is
the case being appealed from, not a party to the appeal — joined wholesale
the record is called 'In re: Anthony Ray Lincoln v. Anthony Ray Lincoln v.
James L. Snyder Acting U.S. Trustee - Appellee', which is what core's
shared walk produced before this reader existed.

THE AXIS IS MEASURED, NOT ASSUMED. 25 records centre the ladder on the page
axis (306.0 on a 612pt sheet); timothy_davies sets the whole cover 6.5pt
left of it and its roster 4pt left of the body rail. Taking the axis from
the fences the sheet actually types costs nothing and reads that record.

A record that does not draw this ladder is not bap8's paper and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

The reader claims HEADMATTER ONLY. It ends at the fence that closes the
roster; the byline under it, the writings and their footnotes are core's.
"""

from __future__ import annotations

import re
from statistics import median

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The bankruptcy panels' shared byline grammar, copied VERBATIM out of the
# `_bap` loop bap8 used to sit in, so nothing about its bylines changes by
# being moved here.
BAP8 = register(CourtProfile(
    "bap8", "Bankruptcy Appellate Panel of the Eighth Circuit",
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

STYLE_TYPED_LADDER = "typed ladder"

# ---- bap8's declared facts (measured over the corpus, not tuned) ---------
# THE FENCE: a row of underscores and nothing else. Four is the floor; the
# clerk types 12, 16, 18, 27, 30 and 31 of them and every one is a fence.
_FENCE = re.compile(r"^_{4,}$")
# THE DIVIDER typed in HYPHENS instead. It separates the bankruptcy case's
# own style from the appeal's parties INSIDE one fenced caption zone (22
# records), so it is drawn where the page types it but it does not close a
# zone. On the other five the clerk types an underscore fence there and the
# caption arrives as two zones — the same division, read the same way.
_SUBRULE = re.compile(r"^[-–—]{4,}$")
# THE SHEET'S AXIS is the median midpoint of the rules the cover types.
# Measured: 26 records land on 305.9-306.1 of a 612pt sheet; timothy_davies
# sets its whole cover on 299.5-300.5. A rule more than 20pt off the axis
# its own sheet declares is not one of this ladder's fences.
_AXIS_TOL = 20.0
# …and the axis the sheet declares may not be far off the page's. 30pt is
# four times the largest departure in the corpus (6.5pt).
_AXIS_DRIFT_MAX = 30.0
# A ROW is centred when its own midpoint is on that axis. Everything on the
# cover is except the status rows (their own column) and the roster (the
# body rail).
_ROW_AXIS_TOL = 8.0
# THE STATUS COLUMN: a status row is centred RIGHT of the axis. Measured,
# the status midpoints run axis+3.5 to axis+54 and the cover's centred rows
# never leave axis±2. The column reaches LEFT to axis-49 at its widest
# ('Acting U.S. Trustee - Appellee'), so 60pt takes the whole column — and
# still stops 138pt short of the paragraph indent (x0 106.9-108), which is
# the one other thing on these sheets whose midpoint sits right of the axis.
_STATUS_REACH = 60.0
# THE BODY RAIL is where the roster is set, and only the roster. 6pt covers
# timothy_davies' 4pt departure and reaches nothing else: the next row left
# of the status column starts 180pt further right.
_RAIL_TOL = 6.0
# THE ENGRAVED MASTHEAD: one display face over both rows, the first at 1.5x
# the body. 1.3 is the floor; nothing else in the document comes near it.
_MASTHEAD_RATIO = 1.3
_MASTHEAD_ROWS = 4
# How far the ladder may run. madison_resource_funding consolidates two
# petitions and reaches its roster on page 2; nothing here needs more.
_MAX_PAGES = 8
# The ladder cannot be shorter than its own zones: masthead | docket |
# caption | origin | dates | roster needs five fences to fence them.
_MIN_FENCES = 5

# A DOCKET is a FORM, never a wording. The panel's own number: 'No.
# 21-6002', and the consolidated forms the circuit family sets.
_DOCKET_TAIL = r"(?:[/,;]\s*(?:\d{2}-)?\d{2,5})*"
_DOCKET = re.compile(r"^Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$",
                     re.I)
# THE PUBLICATION FLAG, bracketed on its own row: '[Published]'.
_FLAG = re.compile(r"^\[\s*(Un)?published\s*\]$", re.I)
# THE DATE LABELS bap8 prints. It sets one label per centred row; the
# family's other forms are kept so a record that argues a case still reads.
_DATE_LABELS = ("submitted on briefs", "argued and submitted", "resubmitted",
                "reargued", "submitted", "argued", "decided", "amended",
                "entered", "filed")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE_VALUE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}"
                         r"|\d{1,2}\s+[A-Z][a-z]+\.?\s+\d{4})")
# THE ROSTER OPENER, stripped so `judges` reads as the bench does. The
# roster is FOUND by its rail, not by this word.
_ROSTER_OPENER = "before"
# BENCH TITLES are a closed role vocabulary — a roster row names judges and
# their office, and the office is not a judge.
_TITLE_WORDS = ("judge", "judges", "justice", "justices")
_SUFFIXES = ("JR", "SR", "II", "III", "IV")
# PARTY STATUS words, used ONLY to tell a principal party from a friend of
# the court. Which rows ARE statuses is decided by the column, not here.
_AMICUS_WORDS = ("amicus", "amici", "intervenor", "intervenors")
# THE PIVOT, as bap8 sets it: alone on a centred row.
_PIVOT = ("v.", "vs.", "v", "vs")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _unmarked(line) -> str:
    """The row's text with any FOOTNOTE REFERENCE dropped. The printed form
    keeps the mark — `caption` reproduces the row as the page sets it — but
    a party is not called '1'."""
    markup = re.sub(r"<footnotemark>.*?</footnotemark>", "", line_markup(line))
    flat = re.sub(r"<[^>]+>", "", markup)
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'")):
        flat = flat.replace(ent, ch)
    return _norm(flat)


# --------------------------------------------------------------------------
# the sheet's own axis, and the three positions it sets rows in
# --------------------------------------------------------------------------

def _mid(line) -> float:
    return (line.x0 + line.x1) / 2.0


def _rule_shaped(line) -> bool:
    flat = _norm(line.plain)
    return bool(_FENCE.match(flat) or _SUBRULE.match(flat))


def _sheet_axis(pm, width: float) -> float | None:
    """The axis the cover types its rules on, or None where it types none.

    Measured off the page rather than assumed to be the page's centre: the
    clerk's template drifts, and a sheet set 6.5pt left is still this
    ladder."""
    mids = [_mid(l) for l in pm.lines
            if l.plain.strip() and _rule_shaped(l)]
    if len(mids) < _MIN_FENCES:
        return None
    axis = median(mids)
    if abs(axis - width / 2.0) > _AXIS_DRIFT_MAX:
        return None
    return axis


def _is_fence(line, axis: float) -> bool:
    return bool(_FENCE.match(_norm(line.plain))
                and abs(_mid(line) - axis) <= _AXIS_TOL)


def _is_subrule(line, axis: float) -> bool:
    return bool(_SUBRULE.match(_norm(line.plain))
                and abs(_mid(line) - axis) <= _AXIS_TOL)


def _on_axis(line, axis: float) -> bool:
    return abs(_mid(line) - axis) <= _ROW_AXIS_TOL


def _is_status(line, axis: float) -> bool:
    """Is ``line`` set in the STATUS COLUMN — centred right of the sheet's
    axis, and reaching no further left than the column does?

    This is the test ca8 makes on the italic face. bap8's clerk sets the
    same rows roman on six of 27 records, so the face cannot carry it and
    the column does."""
    return _mid(line) > axis + _ROW_AXIS_TOL and line.x0 > axis - _STATUS_REACH


def _at_rail(line, body_x0: float) -> bool:
    return abs(line.x0 - body_x0) <= _RAIL_TOL


def _on_ladder(line, axis: float, body_x0: float) -> bool:
    """Is ``line`` set the way the ladder sets its rows?

    Three positions and no others, over all 27 records: ON THE AXIS (the
    masthead, the fences, the docket, the caption's names, the origin, the
    dates), IN THE STATUS COLUMN, or AT THE BODY RAIL (the roster). A row
    set anywhere else ends the ladder's occupancy of this page — which is
    how the body is kept out of a zone the ladder is holding open across a
    page break: bap8 opens every paragraph at x0 108, whose midpoint lands
    18pt right of the axis but whose left edge is nowhere near the status
    column."""
    return (_on_axis(line, axis) or _is_status(line, axis)
            or _at_rail(line, body_x0))


# --------------------------------------------------------------------------
# the zones — what stands between two fences, and what each one is
# --------------------------------------------------------------------------

def _is_docket_zone(zone: list) -> bool:
    return bool(zone) and all(_DOCKET.match(_norm(l.plain)) for l in zone)


def _is_caption_zone(zone: list, axis: float) -> bool:
    """A caption states a party's STATUS, and bap8 sets every status in the
    column right of the axis. Nothing else on the cover is set there, so
    one status row identifies the zone whatever the parties are called."""
    return any(_is_status(l, axis) for l in zone)


def _labelled_date(text: str):
    """('submitted', 'July 21, 2021') — the label the row opens with and the
    date it states, sliced out of the row in the form the page set it."""
    flat = _norm(text)
    if len(flat) > 120:
        return None
    low = flat.lower()
    for label in _DATE_LABELS:
        if not low.startswith(label):
            continue
        rest = flat[len(label):].lstrip(" :—-")
        mm = _DATE_VALUE.search(rest)
        if mm is None:
            continue
        first = mm.group(1).split()[0].strip(".,").lower()
        if first not in _MONTHS and not first.isdigit():
            continue
        return label.replace(" ", "_"), _norm(mm.group(1))
    return None


def _is_dates_zone(zone: list) -> bool:
    """Every row is either a labelled date or the bracketed publication
    flag — a zone with anything else in it is not the date band."""
    if not zone:
        return False
    seen = False
    for line in zone:
        text = _norm(line.plain)
        if _labelled_date(text):
            seen = True
        elif not _FLAG.match(text):
            return False
    return seen


def _is_roster_zone(zone: list, body_x0: float) -> bool:
    """The roster is the one zone bap8 sets at the BODY RAIL; every other
    row on the cover is centred on the axis or in the status column."""
    return bool(zone) and all(_at_rail(l, body_x0) for l in zone)


# --------------------------------------------------------------------------
# what the caption says
# --------------------------------------------------------------------------

def _panel_names(text: str) -> list:
    """The judges a roster names.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    'Before HASTINGS, Chief Judge, SURRATT-STATES and NORTON, Bankruptcy
    Judges.' names three judges and two offices."""
    flat = _norm(text)
    at = flat.lower().find("sitting by")
    if at > 0:
        flat = flat[:at].rstrip(" ,")
    if flat.lower().startswith(_ROSTER_OPENER):
        flat = flat[len(_ROSTER_OPENER):]
    names: list = []
    for chunk in flat.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _TITLE_WORDS):
            continue
        # 'SCHERMER and SALADINO' is two judges; the clerk sets the
        # conjunction in caps as often as in lower case.
        for part in re.split(r"\s+(?:and|AND)\s+", piece):
            name = part.strip().strip(".*: ").strip()
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


def _is_pivot(text: str) -> bool:
    return text.rstrip(".").lower() in [p.rstrip(".") for p in _PIVOT]


def _party_stack(segments: list) -> list:
    """Which of the caption's stacks holds the APPEAL'S parties.

    bap8 sets two stacks with a typed rule between them: the bankruptcy
    case's own style ('In re: Anthony Ray Lincoln / Debtor') above it, the
    appeal's parties below. The stack holding the PIVOT is the appeal's;
    where the clerk types no pivot at all the last stack is."""
    for seg in segments:
        if any(_is_pivot(_norm(l.plain)) for l in seg):
            return seg
    return segments[-1] if segments else []


def _sides(stack: list, axis: float):
    """The two party names either side of the caption's pivot.

    Built from the party NAMES, never by joining the caption wholesale: the
    status rows are apparatus, and a friend of the court is not what the
    case is called. A group runs from wherever the last one ended to the
    STATUS row that names it; the pivot moves the groups from one side to
    the other."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    names: list[str] = []
    for line in stack:
        text = _unmarked(line)
        if not text:
            continue
        if _is_status(line, axis):
            words = text.lower().replace("-", " ").replace("(s)", "").split()
            if names and not any(w in _AMICUS_WORDS for w in words):
                side.append(" ".join(names))
            names = []
            continue
        if _is_pivot(text):
            side = right
            seen_pivot = True
            names = []
            continue
        names.append(text)
    if names:
        side.append(" ".join(names))
    if not (left and right and seen_pivot):
        return None
    # TWO PARTIES ON ONE SIDE are two parties. The clerk stacks them
    # ('Adam R. Schiller / Debtor - Appellee / Kyle Carlson / Trustee -
    # Appellee') and, where it names them on ONE row, separates them with
    # a semicolon ('Steven L. Swackhammer; Michele M. Swackhammer'). That
    # is the page's own separator, so the stacked form is joined with it
    # too rather than run together into one invented name.
    return ("; ".join(_norm(g).rstrip(", ") for g in left),
            "; ".join(_norm(g).rstrip(", ") for g in right))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="bap8")
def read_headmatter_bap8(model, geom, **_):
    """Read bap8's typed-ladder headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    width = model.pages[0].width or 612.0
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    axis = _sheet_axis(model.pages[0], width)
    if axis is None:
        return NOTHING                    # no typed ladder: not bap8's paper

    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}
    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: bap8's foot folio
            # ('- 2 -'), which falls under a consolidated caption. Core
            # measures and records those; the reader steps over them rather
            # than claiming them twice.
            if finder.kind(pm, line):
                continue
            # THE LADDER RUNS DOWN EACH PAGE IN ONE UNBROKEN RUN, and
            # resumes at the top of the next.
            if not _on_ladder(line, axis, body_x0):
                break
            rows.append(line)
    if not rows:
        return NOTHING

    # ---- the ladder -----------------------------------------------------
    fences = [i for i, l in enumerate(rows) if _is_fence(l, axis)]
    if len(fences) < _MIN_FENCES:
        return NOTHING
    zones: list[list] = []
    start = 0
    for at in fences:
        zones.append(rows[start:at])
        start = at + 1
    zones.append(rows[start:])

    # ---- the engraved masthead ------------------------------------------
    masthead = zones[0]
    if not masthead or len(masthead) > _MASTHEAD_ROWS:
        return NOTHING
    faces = {l.font for l in masthead}
    if len(faces) != 1:
        return NOTHING                    # one display face over both rows
    body_faces = {l.font for l in rows[len(masthead) + 1:]
                  if abs((l.size or 0) - body_size) < 0.5}
    if not body_faces or faces & body_faces:
        return NOTHING                    # the masthead face is the body's
    if (masthead[0].size or 0) < _MASTHEAD_RATIO * body_size:
        return NOTHING                    # …and it is not set as a display

    # ---- the zones, in the order the ladder fixes ------------------------
    # A CASE is a docket and the caption zones under it. The clerk divides
    # the caption's two stacks with a hyphen rule on 22 records and with a
    # full fence on five; where it is a fence the caption arrives as two
    # zones, so a case takes ONE OR MORE consecutive caption zones.
    plan: list[tuple[str, list]] = [("court", masthead)]
    i = 1
    cases: list[list[list]] = []
    while i + 1 < len(zones) and _is_docket_zone(zones[i]) \
            and _is_caption_zone(zones[i + 1], axis):
        plan.append(("docket", zones[i]))
        i += 1
        case: list[list] = []
        while i < len(zones) and _is_caption_zone(zones[i], axis):
            plan.append(("caption", zones[i]))
            case.append(zones[i])
            i += 1
        cases.append(case)
    if not cases or i + 1 >= len(zones):
        return NOTHING
    origin = zones[i]
    if (not origin or _is_docket_zone(origin)
            or _is_caption_zone(origin, axis) or _is_dates_zone(origin)):
        return NOTHING                    # the origin is what is left here
    plan.append(("lower-court", origin))
    i += 1
    if not _is_dates_zone(zones[i]):
        return NOTHING
    plan.append(("date", zones[i]))
    i += 1
    if i < len(zones) and _is_roster_zone(zones[i], body_x0):
        plan.append(("panel", zones[i]))
        i += 1
    if i >= len(zones):
        return NOTHING                    # no fence closed the last zone

    # ---- emit, in the page's own order ----------------------------------
    crit: dict = {"headmatter_style": STYLE_TYPED_LADDER}
    items: list = []
    consumed: set[int] = set()
    subrules = {l.id for l in rows if _is_subrule(l, axis)}
    banner_rows: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    panel_rows: list[str] = []
    dockets: list[str] = []
    dates: dict = {}

    def emit(line, role: str):
        pm = pages[line.page]
        align = line_alignment(line, pm.width, geom,
                               banner_center_min_size=body_size + 2.0)
        rel = 0.0
        if align == "L" and line.x0 > body_x0 + 12:
            rel = min(line.x0 - body_x0, (pm.width or width) * 0.6)
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), italic=_is_status(line, axis),
            rel=rel, role=role))
        consumed.add(line.id)

    def fence(line):
        items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                            typed=True, span="full"))
        consumed.add(line.id)

    for n, (role, zone) in enumerate(plan):
        for line in zone:
            if line.id in subrules:
                # THE DIVIDER renders where the page types it — a reader
                # that claims the region inherits the court's own marks.
                fence(line)
                continue
            emit(line, role)
            text = _norm(line.plain)
            if role == "court":
                banner_rows.append(text)
            elif role == "docket":
                dockets.append(text.rstrip("."))
            elif role == "caption":
                caption_rows.append(text)
            elif role == "lower-court":
                origin_rows.append(text)
            elif role == "panel":
                panel_rows.append(text)
            elif role == "date":
                got = _labelled_date(text)
                if got:
                    dates[got[0]] = got[1]
                mm = _FLAG.match(text)
                if mm:
                    crit.setdefault(
                        "publication_status",
                        "unpublished" if mm.group(1) else "published")
        # THE FENCE THAT CLOSES THE ZONE, at the index the ladder found it.
        if n < len(fences):
            fence(rows[fences[n]])

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if dockets:
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit["other_dockets"] = dockets[1:]
    if caption_rows:
        crit["caption"] = caption_rows
    # THE FIRST CASE names the record. Its caption is one or more zones,
    # each of which the divider may split again; the appeal's parties are
    # the stack holding the pivot.
    segments: list[list] = []
    for zone in cases[0]:
        current: list = []
        for line in zone:
            if line.id in subrules:
                segments.append(current)
                current = []
                continue
            current.append(line)
        segments.append(current)
    sides = _sides(_party_stack([s for s in segments if s]), axis)
    if sides:
        crit["parties"] = list(sides)
        crit["case_name"] = f"{sides[0]} v. {sides[1]}"
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
    for label, value in dates.items():
        if label in ("decided", "filed", "amended", "entered"):
            crit.setdefault("decision_date", value)
        elif label in ("submitted", "submitted_on_briefs", "resubmitted",
                       "argued_and_submitted", "argued", "reargued"):
            crit.setdefault("submitted", value)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": [], "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
