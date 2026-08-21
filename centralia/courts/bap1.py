"""Bankruptcy Appellate Panel of the First Circuit ('bap1').

Everything unique to bap1 lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'centred ladder'. bap1 sets ONE paper, a cover sheet whose
every zone the clerk fences with a TYPED RULE — a row of underscores and
nothing else, centred on the sheet's axis — and whose every row is centred
on that same axis. 32 of 32 records, no exceptions:

    FOR PUBLICATION                        the publication flag: the one
                                             display row OFF the axis
    UNITED STATES BANKRUPTCY APPELLATE PANEL   the masthead, 16pt against
    FOR THE FIRST CIRCUIT                        a 12pt body
    _______________________________        a TYPED fence
    BAP NO. MB 24-012                      the panel's own docket
    _______________________________
    Bankruptcy Case No. 24-10550-JEB       the case appealed FROM — and an
    Adversary Proceeding No. 23-00050-ESL    adversary number where there
    _______________________________          is one
    STEVEN T. CARRIGAN, SR.,               the bankruptcy court's caption:
         Debtor.                             names, then a STATUS row
    _______________________________
    STEVEN T. CARRIGAN, SR.,               the APPEAL's caption, with the
         Appellant,                          pivot where there are two
    v.                                       sides
    WELLS FARGO BANK, N.A.,
         Appellee.
    _______________________________
    Appeal from the United States Bankruptcy Court    the origin — named by
    for the District of Massachusetts                   POSITION, and the
    (Hon. Janet E. Bostwick, U.S. Bankruptcy Judge)     trial judge in the
    _______________________________                     court's own paren
    Before                                 the roster
    Godoy, Cary, and González,
    United States Bankruptcy Appellate Panel Judges.
    _______________________________
    David G. Baker, Esq., on brief for Appellant.     the appearances
    _______________________________
    February 18, 2025                      the date, alone
    _______________________________        …and the fence that CLOSES the
    Godoy, U.S. Bankruptcy Appellate Panel Judge.       block: the byline
                                                        opens below it

Because a bankruptcy panel sits BETWEEN a bankruptcy court and a circuit,
its cover states two dockets and two captions: the panel's own BAP number
over the bankruptcy case number, and the bankruptcy court's style ('…,
Debtor.') over the appeal's ('…, Appellant, v. …, Appellee.'). A
CONSOLIDATED record repeats the pair — banco_popular runs two bankruptcy
cases and four captions before its single origin, kittery_point runs two
BAP dockets — and states the origin, the roster, the counsel and the date
ONCE at the end.

The zones are found by POSITION on the ladder, exactly as ca8's are, and
the only things read are FORMS and closed role vocabularies:

  * a ZONE is what stands between two typed fences;
  * the MASTHEAD is the zone above the first fence, and every row in it is
    set at DISPLAY size (>= body + 2pt). That is the dispatch: a record
    whose first zone is ordinary body-size text is not this paper;
  * a DOCKET zone is one whose every row states a number ('No.'/'Nos.'
    plus a token carrying a digit) — the label is never enumerated, so
    'BAP NO.', 'Bankruptcy Case No.' and 'Adversary Proceeding No.' all
    read alike, and a parenthetical aside the clerk hangs off one
    ('(Consolidated)') rides with it;
  * a CAPTION zone is one holding a STATUS row — a row every word of which
    is a party-role word ('Debtor.', 'Alleged Debtor.', 'Appellants,',
    'Defendants-Appellees.'). Statuses are a finite role vocabulary; party
    NAMES are never read;
  * the DATE is the last zone that is a single row stating a month, a day
    and a year, and that a fence closes. The COUNSEL zone is the one before
    it and the ROSTER the one before that — checked, not found, against the
    opener the court prints and an unparenthesized bench title;
  * the ORIGIN is what is left between the last caption and the roster,
    which is how 'Appeal from…', 'Appeals from…' and a record that prints
    no origin at all (5 of 32) all read without an opener vocabulary.

The claim ENDS at the fence that closes the date. Three records hang a
caption footnote in the foot of the cover page ('1 The Honorable Brian K.
Tester presided over the bankruptcy case…'), and one prints its byline
there (madge_casper); all of them stand below that fence and none of them
is touched.

A record that does not draw this ladder is not bap1's paper and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

The reader claims HEADMATTER ONLY. The counsel block the court sets inside
the cover STAYS inside it — its text is copied into `attorneys`, never
lifted out — and the writings, their footnotes and their paragraphs are
core's.
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
# `_bap` loop bap1 used to sit in, so nothing about its bylines changes by
# being moved here.
BAP1 = register(CourtProfile(
    "bap1", "Bankruptcy Appellate Panel of the First Circuit",
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

STYLE_CENTRED_LADDER = "centred ladder"

# ---- bap1's declared facts (measured over the corpus, not tuned) --------
# THE FENCE: a row of underscores and nothing else. The clerk types 31, 32,
# 33 and 53 of them; four is the floor.
_FENCE = re.compile(r"^_{4,}$")
# THE SHEET'S AXIS is taken from the fences the sheet itself types, and the
# ladder is only this paper if that axis is the page's. Measured: every
# fence on all 32 records centres at 306.0 on a 612pt sheet.
_AXIS_OF_PAGE = 30.0
# A ROW is on the ladder when its own midpoint is on that axis. Measured:
# the widest cover rows (a justified counsel entry filling the measure) sit
# at 305.9-306.1, so 8pt is many times the observed spread.
_ROW_AXIS_TOL = 8.0
# THE DISPLAY SIZE the masthead and the flag are set in — 15.5pt and 16pt
# against a 12pt body. Two points clears the body and everything in it.
_DISPLAY_OVER_BODY = 2.0
# How far the ladder may run. A consolidated cover reaches its date on page
# 2 (banco_popular, kittery_point); four pages is far more than any needs.
_MAX_PAGES = 4
# The RIGHT MARGIN, mirror of the body rail: where the flag is set.
_MARGIN_TOL = 4.0
# The ladder cannot be shorter than its own zones: masthead | BAP docket |
# case number | debtor | parties | roster | counsel | date needs seven
# fences to fence them (the origin is optional).
_MIN_FENCES = 7

# A DOCKET is a FORM, never a wording: a number label and a token carrying
# a digit. 'BAP NO. MB 24-012', 'BAP NOS. PR 23-033 and PR 24-002',
# 'Bankruptcy Case No. 16-01148', 'Adversary Proceeding No. 17-04055-EDK'.
_NUMBER_LABEL = re.compile(r"\bNos?\.", re.I)
_DOCKET_MAX = 80
# A parenthetical aside INSIDE the docket zone — milk_industry states two
# bankruptcy cases and then '(Consolidated)'. It rides with the numbers it
# annotates; it is not itself one.
_ASIDE_MAX = 24
# PARTY STATUS: a finite role vocabulary. A row every word of which is one
# of these is the status of the party above it, whatever that party is
# called. Nothing here names a party, a court or a lawyer.
_STATUS_WORDS = {
    "alleged", "debtor", "debtors", "appellant", "appellants", "appellee",
    "appellees", "plaintiff", "plaintiffs", "defendant", "defendants",
    "petitioner", "petitioners", "respondent", "respondents", "cross",
    "intervenor", "intervenors", "trustee", "trustees", "movant", "movants",
    "creditor", "creditors", "party", "parties", "interest", "amicus",
    "amici", "curiae", "and", "in", "pro", "se", "possession",
}
_STATUS_MAX = 60
# THE PIVOT, as bap1 sets it: alone on a centred row.
_PIVOT = ("v.", "vs.", "v", "vs")
# THE ROSTER OPENER the court prints, and the BENCH words that confirm it.
# The roster is FOUND by its position on the ladder; these two only check
# that the zone found is the one meant.
_ROSTER_OPENER = "before"
_BENCH_WORDS = ("judge", "judges", "justice", "justices")
_SUFFIXES = ("JR", "SR", "II", "III", "IV")
# THE DATE, alone on its row: a month, a day and a year.
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"^(?:%s)\s+\d{1,2},\s*\d{4}$" % "|".join(_MONTHS), re.I)
# THE PUBLICATION FLAG: a two-form closed vocabulary the cover states in
# display type, flush right. Which ROW it is on is decided by geometry.
_UNPUBLISHED = "not for publication"
_PUBLISHED = "for publication"
# …and RIGHT STAYS RIGHT. The flag is set flush to the sheet's right
# margin — the mirror of the body rail — while every other cover row is
# centred. Measured: x1 runs 539.9-540.1 against a 612pt sheet on a 72pt
# rail, so 4pt covers the whole corpus. The shared alignment test reads it
# 'L' (its x0 falls just short of the 0.6 mark) and renders it as a 279pt
# indent instead, which is the ca5/mcnutt failure exactly.
# THE HONORIFIC the origin's parenthetical may carry before the trial
# judge's name. A closed courtesy vocabulary, never a name test.
_HONORIFICS = ("hon.", "honorable", "the honorable")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _unmarked(line) -> str:
    """The row's text with any FOOTNOTE REFERENCE dropped.

    The printed form keeps the mark — `caption` reproduces the row as the
    page sets it. The PARSED form must not: three records hang a note off
    the origin's parenthetical ('(Hon. Brian K. Tester, U.S. Bankruptcy
    Judge)1'), and no judge is called 'Judge)1'."""
    markup = line_markup(line)
    markup = re.sub(r"<footnotemark>.*?</footnotemark>", "", markup)
    flat = re.sub(r"<[^>]+>", "", markup)
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'")):
        flat = flat.replace(ent, ch)
    return _norm(flat)


# --------------------------------------------------------------------------
# the forms and the role vocabularies
# --------------------------------------------------------------------------

def _is_fence(text: str) -> bool:
    return bool(_FENCE.match(_norm(text)))


def _is_docket(text: str) -> bool:
    flat = _norm(text)
    if not flat or len(flat) > _DOCKET_MAX or not _NUMBER_LABEL.search(flat):
        return False
    return any(any(c.isdigit() for c in w) for w in flat.split())


def _is_aside(text: str) -> bool:
    flat = _norm(text)
    return (flat.startswith("(") and flat.endswith(")")
            and len(flat) <= _ASIDE_MAX)


def _is_status(text: str) -> bool:
    flat = _norm(text).rstrip(".,;:").strip()
    if not flat or len(flat) > _STATUS_MAX:
        return False
    words = [w.strip(".,;:") for w in re.split(r"[\s\-/]+", flat.lower())]
    words = [w for w in words if w]
    return bool(words) and all(w in _STATUS_WORDS for w in words)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in [p.rstrip(".") for p in _PIVOT]


def _is_date(text: str) -> bool:
    return bool(_DATE.match(_norm(text)))


def _flag_status(text: str) -> str | None:
    low = _norm(text).lower().strip(" .*†‡")
    if low.startswith(_UNPUBLISHED):
        return "unpublished"
    if low.startswith(_PUBLISHED):
        return "published"
    return None


def _has_bench_word(rows: list[str]) -> bool:
    """Does this zone name the bench OUTSIDE a parenthesis?

    The origin's last row names a bankruptcy judge too — '(Hon. Janet E.
    Bostwick, U.S. Bankruptcy Judge)' — but the court sets that inside its
    own parenthesis, and the roster never is."""
    for text in rows:
        flat = _norm(text)
        if flat.startswith("("):
            continue
        if any(w.strip(".,;:") in _BENCH_WORDS for w in flat.lower().split()):
            return True
    return False


# --------------------------------------------------------------------------
# what the zones say
# --------------------------------------------------------------------------

def _panel_names(text: str) -> list:
    """The judges a roster names.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a name test.
    'Finkle, Chief U.S. Bankruptcy Appellate Panel Judge; Panos and Katz,
    U.S. Bankruptcy Appellate Panel Judges' names three judges and two
    offices."""
    flat = _norm(text)
    if flat.lower().startswith(_ROSTER_OPENER):
        flat = flat[len(_ROSTER_OPENER):]
    names: list = []
    for chunk in flat.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*: ").strip()
        if not piece:
            continue
        if any(w in piece.lower().split() for w in _BENCH_WORDS):
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


def _sides(zone: list) -> tuple[str, str] | None:
    """The two party names either side of the appeal caption's pivot.

    Built from the party NAMES, never by joining the caption wholesale: the
    status rows are apparatus. A group runs from wherever the last one
    ended to the STATUS row that names it; the pivot moves the groups from
    one side to the other."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    names: list[str] = []
    for line in zone:
        text = _unmarked(line)
        if not text:
            continue
        if _is_status(text):
            if names:
                side.append(" ".join(names))
            names = []
            continue
        if _is_pivot(text):
            side = right
            seen_pivot = True
            names = []
            continue
        names.append(text)
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


def _origin(rows: list[str]) -> tuple[str, str | None]:
    """The court appealed from, and the judge its parenthetical names.

    The printed form and the parsed form are both facts: every row stands
    in the block where the page puts it, and what the band SAYS is read out
    beside it. The clerk sets the trial judge in a parenthesis of his own,
    with or without a courtesy title."""
    forum = [r for r in rows if not _norm(r).startswith("(")]
    judge = None
    for row in rows:
        flat = _norm(row)
        if not flat.startswith("("):
            continue
        inner = flat.strip("()").strip()
        low = inner.lower()
        for hon in _HONORIFICS:
            if low.startswith(hon):
                inner = inner[len(hon):].lstrip()
                break
        judge = inner or None
    return _norm(" ".join(forum)), judge


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="bap1")
def read_headmatter_bap1(model, geom, **_):
    """Read bap1's centred-ladder cover sheet, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    width = page1.width or 612.0
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    display_min = body_size + _DISPLAY_OVER_BODY

    # ---- THE AXIS, taken from the fences the sheet itself types ---------
    # Over the WHOLE cover, not page 1 alone: a cover whose caption fills
    # the sheet reaches its roster, counsel and date on page 2, and types
    # only four of its fences on the first (charles_muszynski).
    fence_mids = [(l.x0 + l.x1) / 2 for pm in model.pages[:_MAX_PAGES]
                  for l in pm.lines if _is_fence(l.plain)]
    if len(fence_mids) < _MIN_FENCES:
        return NOTHING
    axis = median(fence_mids)
    if abs(axis - width / 2) > _AXIS_OF_PAGE:
        return NOTHING              # a rule set to one side is not a fence

    # ---- the rows the ladder holds --------------------------------------
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}
    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        run: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region (the foot folio a
            # consolidated cover reaches). Core measures and records those;
            # the reader steps over them rather than claiming them twice.
            if finder.kind(pm, line):
                continue
            # THE LADDER RUNS DOWN EACH PAGE IN ONE UNBROKEN RUN, every row
            # on the axis. The first row set off it ends the page's
            # occupancy — the byline, and the caption footnote a cover
            # hangs in its own foot. The ladder resumes at the top of the
            # next page.
            on_axis = abs((line.x0 + line.x1) / 2 - axis) <= _ROW_AXIS_TOL
            display = (line.size or 0.0) >= display_min
            if not (on_axis or display):
                break
            run.append(line)
        rows.extend(run)
        if not run:
            break
    if not rows:
        return NOTHING

    fences = [i for i, l in enumerate(rows) if _is_fence(l.plain)]
    if len(fences) < _MIN_FENCES:
        return NOTHING
    zones: list[list] = []
    start = 0
    for at in fences:
        zones.append(rows[start:at])
        start = at + 1
    zones.append(rows[start:])

    def zt(zone: list) -> list[str]:
        return [_norm(l.plain) for l in zone]

    # ---- the masthead, and the flag beside it ---------------------------
    # THE DISPATCH: the zone above the first fence is set entirely in
    # display type. A record whose cover opens in body text is not this
    # paper, whatever it goes on to print.
    masthead = zones[0]
    if not masthead or not all((l.size or 0.0) >= display_min
                               for l in masthead):
        return NOTHING

    # ---- the date closes the ladder -------------------------------------
    date_at = None
    for j in range(len(fences)):
        if len(zones[j]) == 1 and _is_date(zones[j][0].plain):
            date_at = j
    if date_at is None:
        return NOTHING              # nothing closed by a fence states a date

    def _prev_filled(j: int) -> int:
        j -= 1
        while j > 0 and not zones[j]:
            j -= 1
        return j

    counsel_at = _prev_filled(date_at)
    roster_at = _prev_filled(counsel_at)
    if not (0 < roster_at < counsel_at < date_at):
        return NOTHING
    roster_rows = zt(zones[roster_at])
    if not (roster_rows[0].lower().startswith(_ROSTER_OPENER)
            and _has_bench_word(roster_rows)):
        return NOTHING
    if not zones[counsel_at]:
        return NOTHING

    # ---- the dockets and the captions, in the order the ladder fixes ----
    plan: list[tuple[str, int]] = []
    i = 1
    dockets = captions = 0
    while i < roster_at:
        zone = zones[i]
        if not zone:
            i += 1
            continue
        rows_t = zt(zone)
        if (any(_is_docket(t) for t in rows_t)
                and all(_is_docket(t) or _is_aside(t) for t in rows_t)):
            plan.append(("docket", i))
            dockets += 1
        elif any(_is_status(t) for t in rows_t):
            plan.append(("caption", i))
            captions += 1
        else:
            break
        i += 1
    if dockets < 1 or captions < 1:
        return NOTHING
    # THE ORIGIN IS WHAT IS LEFT between the last caption and the roster —
    # one zone, or none at all (5 of 32 records print no origin).
    origin_zones = [k for k in range(i, roster_at) if zones[k]]
    if len(origin_zones) > 1:
        return NOTHING
    for k in origin_zones:
        plan.append(("lower-court", k))
    plan.append(("panel", roster_at))
    plan.append(("counsel", counsel_at))
    plan.append(("date", date_at))
    role_of = {k: role for role, k in plan}

    # ---- emit, in the page's own order ----------------------------------
    crit: dict = {"headmatter_style": STYLE_CENTRED_LADDER}
    items: list = []
    consumed: set[int] = set()

    def emit(line, role: str):
        pm = pages[line.page]
        page_w = pm.width or width
        align = line_alignment(line, page_w, geom,
                               banner_center_min_size=display_min)
        rel = 0.0
        if abs(line.x1 - (page_w - body_x0)) <= _MARGIN_TOL \
                and abs((line.x0 + line.x1) / 2 - axis) > _ROW_AXIS_TOL:
            align = "R"
        elif align == "L" and line.x0 > body_x0 + 12:
            rel = min(line.x0 - body_x0, page_w * 0.6)
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role))
        consumed.add(line.id)

    banner_rows: list[str] = []
    caption_rows: list[str] = []
    origin_rows: list[str] = []
    counsel_rows: list[str] = []
    docket_rows: list[str] = []
    appeal_zone: list | None = None

    # THE CLAIM RUNS TO THE FENCE THAT CLOSES THE DATE, and no further: the
    # caption footnote and the byline a cover prints below it are core's.
    last = fences[date_at]
    for n, line in enumerate(rows[:last + 1]):
        if _is_fence(line.plain):
            # A READER THAT CLAIMS THE REGION INHERITS THE COURT'S OWN
            # MARKS. Core draws the fences only for rows a reader left
            # behind, so a total claim has to re-type them.
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            consumed.add(line.id)
            continue
        zone_at = next((z for z, at in enumerate(fences) if n < at),
                       len(fences))
        role = "court" if zone_at == 0 else role_of.get(zone_at, "")
        if not role:
            # An unread row inside the ladder means the plan does not
            # describe this cover; core reads the whole document instead.
            return NOTHING
        emit(line, role)
        text = _norm(line.plain)
        if role == "court":
            flag = _flag_status(text)
            if flag:
                crit.setdefault("publication_status", flag)
            else:
                banner_rows.append(text)
        elif role == "docket":
            if _is_docket(text):
                docket_rows.append(text.rstrip("."))
        elif role == "caption":
            caption_rows.append(text)
        elif role == "lower-court":
            origin_rows.append(_unmarked(line))
        elif role == "counsel":
            counsel_rows.append(text)
        elif role == "date":
            crit.setdefault("decision_date", text)

    # THE APPEAL'S caption is the one holding the pivot — the bankruptcy
    # court's style above it ('…, Debtor.') states the case being appealed
    # FROM, and joined into the parties it names the debtor twice.
    for role, at in plan:
        if role != "caption":
            continue
        if any(_is_pivot(t) for t in zt(zones[at])):
            appeal_zone = zones[at]
            break

    # ---- what the block says --------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if docket_rows:
        # THE PANEL'S NUMBER AND THE COURT BELOW'S ARE DIFFERENT FACTS. The
        # cover states both — 'BAP NO. MW 20-019' over 'Bankruptcy Case No.
        # 11-43854-CJP' (and any adversary proceeding number). The first is
        # this court's docket; the rest belong to the case appealed FROM,
        # and filing them together under `other_dockets` — which means a
        # companion APPEAL consolidated into this one — loses the
        # distinction. A consolidated record does print a second BAP
        # number, and that one IS an other docket.
        _bap = [d for d in docket_rows if d.upper().lstrip().startswith("BAP")]
        _below = [d for d in docket_rows if d not in _bap]
        crit["docket_number"] = (_bap or docket_rows)[0]
        _other = (_bap or docket_rows)[1:]
        if _other:
            crit["other_dockets"] = _other
        if _below:
            crit["lower_court_docket"] = _below
    if caption_rows:
        crit["caption"] = caption_rows
    if appeal_zone is not None:
        sides = _sides(appeal_zone)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    if origin_rows:
        forum, judge = _origin(origin_rows)
        if forum:
            crit["lower_court"] = forum
        if judge:
            crit["lower_court_judge"] = judge
    if roster_rows:
        printed = _norm(" ".join(roster_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith(_ROSTER_OPENER):
            roster = roster[len(_ROSTER_OPENER):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names
    if counsel_rows:
        # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE. Its text is
        # copied into criteria; the rows themselves are not moved.
        crit["attorneys"] = _norm(" ".join(counsel_rows))

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": [], "consumed": consumed,
            "anchor_ids": [], "doc_type_final": None}
