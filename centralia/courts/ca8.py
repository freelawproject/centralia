"""United States Court of Appeals for the Eighth Circuit ('ca8').

Everything unique to ca8 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'engraved ladder'. ca8 sets ONE paper, and it states its
own structure twice over in ink, without a word having to be read:

  * the MASTHEAD is ENGRAVED — both rows are set in a blackletter display
    face (`OldEnglishTextMT`) that occurs nowhere else in the document, the
    first at 21pt against a 14pt body. 103 of 103 records, no exceptions;
  * every zone below it is FENCED by a TYPED RULE — a row of underscores
    and nothing else, centred on the page axis (measured centre 306.0 on a
    612pt page, spread 306-308 over 619 rules). The zones come in a fixed
    order and each is closed by the fence under it:

        United States Court of Appeals        the engraved masthead
        For the Eighth Circuit
        ___________________________           a TYPED fence
        No. 24-2914                           the docket
        ___________________________
        Abigail Farella, …                    the caption: names, then a
             Plaintiffs - Appellees              STATUS row set in ITALIC
        v.                                      and indented to its own
        Benton County District Court, Div. 4    column
             Defendant
        ------------------------------        a DASHED rule: the amici
        Quattrone Center for the Fair …         stand below it, inside the
             Amicus Curiae                      same fenced zone
        ____________
        Appeal from United States District Court   the origin — named by
        for the Western District of Arkansas         its POSITION, never
        ____________                                 by its wording
        Submitted: January 15, 2026           the dates
        Filed: May 18, 2026
        [Unpublished]                         the publication flag, if any
        ____________
        Before GRUENDER, SHEPHERD, and GRASZ, Circuit Judges.   the roster,
        ____________                          alone at the BODY RAIL
        SHEPHERD, Circuit Judge.  Abigail …   the first byline

    A consolidated record repeats DOCKET-then-CAPTION and states the origin
    ONCE, below the last of them (minnesota_telecom_alliance runs sixteen
    petitions over seventeen pages before its roster).

Three measurements do all of the work and none of them reads a word:

  * a ZONE is what stands between two typed fences;
  * a STATUS row is ITALIC. Every italic-bearing row in every ca8
    headmatter is a party status ('Plaintiff - Appellee', 'Amici on Behalf
    of Respondent', 'Intervenors') and nothing else is italic anywhere in
    the block — so a zone holding an italic row is a CAPTION, and one that
    does not is the docket, the origin, the dates or the roster;
  * the ROSTER is the one zone set at the BODY RAIL. Every other row in
    the block is centred on the page axis, or (a status row) indented to
    the status column.

The origin is therefore read WITHOUT an opener vocabulary: it is the zone
between the last caption and the dates, whether the court writes 'Appeal
from United States District Court', 'Petition for Review of an Order of
the / Board of Immigration Appeals', or simply 'United States Tax Court'.

A record that does not draw this ladder is not ca8's paper and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

The reader claims HEADMATTER ONLY. It ends at the fence that closes the
roster; the byline under it, the writings, their footnotes and a caption
footnote printed below the last fence are all core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# The circuits' shared byline grammar, copied VERBATIM out of the
# `_CIRCUIT_GRAMMAR` loop ca8 used to sit in, so nothing about its bylines
# changes by being moved here.
CA8 = register(CourtProfile(
    "ca8", "United States Court of Appeals for the Eighth Circuit",
    byline=BylineGrammar(
        style="prose",
        # 'J.' covers the circuits' short form on separate writings.
        titles=("Circuit Judge", "Judge", "District Judge", "Justice",
                "Chief Judge", "Circuit Justice", "J.")),
))

STYLE_ENGRAVED_LADDER = "engraved ladder"

# ---- ca8's declared facts (measured over the corpus, not tuned) ----------
# THE FENCE: a row of underscores and nothing else. Four is the floor; the
# court types 11, 12, 27, 30 and 31 of them and every one is a fence.
_FENCE = re.compile(r"^_{4,}$")
# THE AMICI RULE: the same rule typed in HYPHENS instead. It divides the
# amici from the parties INSIDE one fenced caption zone (9 records), so it
# is drawn where the page types it but it does not close a zone.
_SUBRULE = re.compile(r"^[-–—]{4,}$")
# A fence is CENTRED ON THE PAGE AXIS. Measured: 619 of 619 rules sit at
# 306-308 on a 612pt page, so 20pt is four times the observed spread and
# still nowhere near a rule set to one side.
_AXIS_TOL = 20.0
# A ROW is centred when its own midpoint is on that axis. Everything in
# this block is except the italic status rows (their own column) and the
# roster (the body rail).
_ROW_AXIS_TOL = 8.0
# THE ENGRAVED MASTHEAD: one display face over both rows, the first at
# 1.5x the body. 1.3 is the floor; nothing else in the document comes
# near it.
_MASTHEAD_RATIO = 1.3
_MASTHEAD_ROWS = 4
# THE STATUS COLUMN: a status row is italic. 'Defendant' + a roman 's',
# and 'Trustee - Appellee' with a roman tail, are the loosest the corpus
# sets, so two fifths of the inked glyphs is the floor.
_ITALIC_MIN = 0.4
# THE BODY RAIL is where the roster is set, and only the roster.
_RAIL_TOL = 3.0
# How far the ladder may run. minnesota_telecom_alliance consolidates
# sixteen petitions and reaches its roster on page 18.
_MAX_PAGES = 24
# The ladder cannot be shorter than its own zones: masthead | docket |
# caption | origin | dates | roster needs five fences to fence them.
_MIN_FENCES = 5

# A DOCKET is a FORM, never a wording. 'No. 24-2914', 'Nos. 24-3265/3296'.
_DOCKET_TAIL = r"(?:[/,;]\s*(?:\d{2}-)?\d{2,5})*"
_DOCKET = re.compile(r"^Nos?\.\s*\d{2}-\d{3,5}" + _DOCKET_TAIL + r"\.?$",
                     re.I)
# THE PUBLICATION FLAG, bracketed on its own row: '[Published]',
# '[Unpublished]'.
_FLAG = re.compile(r"^\[\s*(Un)?published\s*\]$", re.I)
# THE DATE LABELS ca8 prints. It sets one label per centred row and has
# never printed another over this corpus, but the family's forms are kept
# so a record that argues a case still reads.
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
# the court. Which rows ARE statuses is decided by the italic, not here.
_AMICUS_WORDS = ("amicus", "amici", "intervenor", "intervenors")
# THE PIVOT, as ca8 sets it: alone on a centred row.
_PIVOT = ("v.", "vs.", "v", "vs")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _unmarked(line) -> str:
    """The row's text with any FOOTNOTE REFERENCE dropped.

    The printed form keeps the mark — `caption` reproduces the row as the
    page sets it. The PARSED form must not: ca8 hangs a substitution note
    off the respondent's name ('Todd Blanche,1 Acting Attorney General of
    the United States'), and a party is not called '1'."""
    markup = line_markup(line)
    markup = re.sub(r"<footnotemark>.*?</footnotemark>", "", markup)
    flat = re.sub(r"<[^>]+>", "", markup)
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'")):
        flat = flat.replace(ent, ch)
    return _norm(flat)


def _is_fence(line, width: float) -> bool:
    return bool(_FENCE.match(_norm(line.plain))
                and abs((line.x0 + line.x1) / 2 - width / 2) <= _AXIS_TOL)


def _is_subrule(line, width: float) -> bool:
    return bool(_SUBRULE.match(_norm(line.plain))
                and abs((line.x0 + line.x1) / 2 - width / 2) <= _AXIS_TOL)


def _italic_share(line) -> float:
    """How much of the row's ink is set in an italic face."""
    inked = [c for c in line.chars if (c.get("text") or "").strip()]
    if not inked:
        return 0.0
    ital = sum(1 for c in inked
               if any(s in (c.get("fontname") or "")
                      for s in ("Italic", "Oblique")))
    return ital / len(inked)


def _is_status(line) -> bool:
    return _italic_share(line) >= _ITALIC_MIN


def _is_docket(text: str) -> bool:
    return bool(_DOCKET.match(_norm(text)))


def _labelled_date(text: str) -> tuple[str, str] | None:
    """('submitted', 'January 15, 2026') — the label the row opens with and
    the date it states, sliced out of the row in the form the page set it."""
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


def _at_rail(line, body_x0: float) -> bool:
    return abs(line.x0 - body_x0) <= _RAIL_TOL


def _on_ladder(line, width: float, body_x0: float) -> bool:
    """Is ``line`` set the way the ladder sets its rows?

    Three positions and no others, over all 103 records: ON THE PAGE AXIS
    (the masthead, the fences, the docket, the caption's names, the origin,
    the dates), IN THE STATUS COLUMN (italic, indented right of centre), or
    AT THE BODY RAIL (the roster).

    A row set anywhere else is not the ladder's. That is how the caption
    FOOTNOTE ca8 prints in the foot of a caption page is kept out of the
    zone the ladder is holding open across the page break — rustico_lacsina
    sets '1Acting Attorney General Todd Blanche is automatically
    substituted as' at the paragraph indent and runs it to the measure, so
    its midpoint is 18pt right of the axis while every caption row that
    reaches the same measure is symmetric about it."""
    if abs((line.x0 + line.x1) / 2 - width / 2) <= _ROW_AXIS_TOL:
        return True
    return _is_status(line) or _at_rail(line, body_x0)


# --------------------------------------------------------------------------
# the zones — what stands between two fences, and what each one is
# --------------------------------------------------------------------------

def _is_docket_zone(zone: list) -> bool:
    return bool(zone) and all(_is_docket(l.plain) for l in zone)


def _is_caption_zone(zone: list) -> bool:
    """A caption states a party's STATUS, and ca8 sets every status in
    italic. Nothing else in the block is italic at all, so one italic row
    identifies the zone whatever the parties are called."""
    return any(_is_status(l) for l in zone)


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
    """The roster is the one zone ca8 sets at the BODY RAIL; every other
    row in the block is centred on the page axis or indented to the status
    column."""
    return bool(zone) and all(_at_rail(l, body_x0) for l in zone)


def _panel_names(text: str) -> list:
    """The judges a roster names.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    'Before COLLOTON, Chief Judge, ARNOLD and GRASZ, Circuit Judges.' names
    three judges and two offices."""
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
        for part in piece.replace(" and ", "|").split("|"):
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


def _sides(zone: list, subrules: set) -> tuple[str, str] | None:
    """The two party names either side of the caption's pivot.

    Built from the party NAMES, never by joining the caption wholesale: the
    status rows are apparatus, and the amici and intervenors below them are
    not what the case is called. A group runs from wherever the last one
    ended to the ITALIC row that names its status; the pivot moves the
    groups from one side to the other."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    names: list[str] = []
    for line in zone:
        if line.id in subrules:
            # BELOW THE AMICI RULE the zone is friends of the court.
            break
        text = _unmarked(line)
        if not text:
            continue
        if _is_status(line):
            words = text.lower().replace("-", " ").replace("(s)", "").split()
            if names and not any(w in _AMICUS_WORDS for w in words):
                side.append(" ".join(names))
            names = []
            continue
        if text.rstrip(".").lower() in [p.rstrip(".") for p in _PIVOT]:
            side = right
            seen_pivot = True
            names = []
            continue
        names.append(text)
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ca8")
def read_headmatter_ca8(model, geom, **_):
    """Read ca8's engraved-ladder headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    width = model.pages[0].width or 612.0
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0

    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}
    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        page_rows: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: ca8's foot folio
            # ('-2-'), which falls in the middle of a consolidated caption.
            # Core measures and records those; the reader steps over them
            # rather than claiming them twice.
            if finder.kind(pm, line):
                continue
            # THE LADDER RUNS DOWN EACH PAGE IN ONE UNBROKEN RUN. The first
            # row set off the ladder's three positions ends its occupancy of
            # this page — the body below it, and the caption note some pages
            # carry in the foot. The ladder resumes at the top of the next.
            if not _on_ladder(line, pm.width or width, body_x0):
                break
            page_rows.append(line)
        rows.extend(page_rows)
    if not rows:
        return NOTHING

    # ---- the ladder -----------------------------------------------------
    fences = [i for i, l in enumerate(rows) if _is_fence(l, width)]
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
    plan: list[tuple[str, list]] = [("court", masthead)]
    i = 1
    cases = 0
    while i + 1 < len(zones) and _is_docket_zone(zones[i]) \
            and _is_caption_zone(zones[i + 1]):
        plan.append(("docket", zones[i]))
        plan.append(("caption", zones[i + 1]))
        cases += 1
        i += 2
    if not cases or i + 1 >= len(zones):
        return NOTHING
    origin = zones[i]
    if (not origin or _is_docket_zone(origin) or _is_caption_zone(origin)
            or _is_dates_zone(origin)):
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
    crit: dict = {"headmatter_style": STYLE_ENGRAVED_LADDER}
    items: list = []
    consumed: set[int] = set()
    subrules = {l.id for l in rows if _is_subrule(l, width)}
    banner_rows: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    panel_rows: list[str] = []
    dockets: list[str] = []
    dates: dict = {}
    first_caption: list | None = None

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
            bold=bool(line.all_bold), italic=_is_status(line),
            rel=rel, role=role))
        consumed.add(line.id)

    def fence(line, typed: bool = True):
        items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                            typed=typed, span="full"))
        consumed.add(line.id)

    for n, (role, zone) in enumerate(plan):
        for line in zone:
            if line.id in subrules:
                # THE AMICI RULE renders where the page types it — a reader
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
        if role == "caption" and first_caption is None:
            first_caption = zone
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
    if first_caption:
        sides = _sides(first_caption, subrules)
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
