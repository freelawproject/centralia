"""United States Court of Appeals for the Fifth Circuit ('ca5').

Everything unique to ca5 lives here. It imports core, never another court
file, and no other court file imports it.

ca5 prints ONE layout, and its zone marks are RULES THE COURT TYPES:

    Case: 25-30016  Document: 52-1  Page: 1 …    the ECF strip (furniture)
    United States Court of Appeals               the banner, Old English 24pt
    for the Fifth Circuit
                                    FILED        the clerk's stamp, Arial,
                                April 13, 2026   pinned right of the measure
                                Lyle W. Cayce
                                Clerk
        ____________                             a SHORT typed rule
        No. 25-30016                             the docket
        ____________                             …and its closing rule
    Albert K. Alexander,                         the caption: parties…
                            Plaintiff—Appellant, …their status, flush right
                versus                           …the pivot
    Dwayne Arceneaux; Jeff Hebert; …
                          Defendants—Appellees.
        ______________________________           a LONG typed rule
    Appeal from the United States District Court the origin…
    for the Western District of Louisiana        …its forum…
    USDC No. 6:11-CV-1749                        …and its docket
        ______________________________
    ON REMAND FROM                               the posture recital (rare)
    THE SUPREME COURT OF THE UNITED STATES
    Before Clement, Douglas, and Ramirez, Circuit Judges.      the roster
    Edith Brown Clement, Circuit Judge:          the byline — the reader stops

STYLE 'typed sandwich' — every section of the headmatter is SANDWICHED
between a pair of rules centred on the page axis, and the rule's MEASURE
names the section it opens:

  * the SHORT rule (90-106pt over the corpus) brackets the DOCKET;
  * the LONG rule (234-252pt) brackets the ORIGIN.

Both are set on the page axis, and that is what separates a fence from the
two other rules ca5 types on the same page:

  * the FOOTNOTE SEPARATOR — 165pt at the body rail, 80pt off the axis;
  * the CONSOLIDATION DIVIDER — the LONG measure set flush at the rail,
    dividing two captions that share one docket band (united_states_v.
    _state_of_texas, texas_medical_association_v._hhs).

Width alone would take both; the axis takes neither. Two records of 102
DRAW their fences as strokes instead of typing them, at the very same two
measures (busby_v._guerrero) — so both kinds are collected, and a drawn
rule whose ends coincide with a text row's is an UNDERLINE, not a fence
(olivier_v._city_of_brandon_ms underlines its posture recital).

That makes the BAND the unit of meaning, exactly as on ca4: a band is asked
once what section it is, and each band is identified by its OWN landmark,
not by its position — a consolidated record repeats docket-then-caption for
every appeal and states the origin, the recital and the roster once, at the
end, for all of them.

ca5 PRINTS NO APPEARANCES IN ITS HEADMATTER. Its bands are the court's
name, the dockets, the caption, the origin, the roster — then the author and
the opinion. There is no counsel band, so there is nothing here for a
counsel reader to find, and anything it DID claim would be something else
wearing an appearance's clothes.

The reader claims HEADMATTER ONLY: it stops when the roster closes (or at
the first byline), and everything below — the writings, their footnotes,
their paragraphs — is core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import FurnitureFinder
from ..pdfio.rules import is_typed_rule
from . import register

CA5 = register(CourtProfile(
    "ca5", "United States Court of Appeals for the Fifth Circuit",
    # ca5 signs its bylines in TITLECASE ('Jerry E. Smith, Circuit Judge:');
    # its roster is the single 'Before …' line, so titlecase is safe here.
    # …and its en banc majority names its joiners and closes on a PERIOD
    # ('Jerry E. Smith, Circuit Judge, joined by Elrod, Chief Judge, and
    # Jones, …, Circuit Judges.'), where ca2's twin closes on a colon.
    byline=BylineGrammar(style="prose", allow_titlecase_name=True,
                         joined_by_period=True,
                         titles=("Circuit Judge", "Judge", "District Judge",
                                 "Justice", "Chief Judge")),
))

STYLE_TYPED_SANDWICH = "typed sandwich"

# ---- ca5's declared facts (measured over all 102 records, not tuned) ------
# THE FENCES. Two measures, each invariant to a couple of points across the
# corpus; the window is deliberately narrow, because the rules ca5 types
# that are NOT fences share one of these measures exactly.
_FENCE_SHORT = (86.0, 118.0)          # measured 90.0 – 105.8
_FENCE_LONG = (225.0, 262.0)          # measured 234.0 – 251.2
# How far a fence's midpoint may sit off the page axis. The footnote
# separator (165pt at x0=144) and the consolidation divider (the long
# measure at x0=108) are both ~80pt off it.
_FENCE_AXIS = 8.0
# THE CLERK'S STAMP. ca5 sets its whole slip in Equity, with an Old English
# banner; the electronic filing stamp the clerk's office overlays is Arial
# and is pinned to the RIGHT of the text measure (x0 421-517 over the
# corpus, against a 108pt rail and a 504pt right edge). Either test alone
# misfires — a right-flush status row ('Plaintiff—Appellant,') sits at
# x0=376-403, and the court's own type is never Arial — so both are
# required, and the stamp's own date is read out before it is dropped.
_STAMP_FACES = ("arial", "helvetica")
_STAMP_MIN_X0 = 400.0
# The body rail, and the measured right edge of the caption's measure.
_RAIL = 108.0
# How many pages the headmatter may run to. The longest in the corpus is
# nathan_v._alamo_heights_isd, whose caption alone fills page 1 and half of
# page 2; four is slack, and the LANDMARKS stop the reader, not the count.
_MAX_PAGES = 4

_DOCKET_ROW = re.compile(
    r"^Nos?\.\s*\d{2}-\d{3,5}"
    r"(?:\s*[,;&]\s*(?:and\s+)?(?:No\.\s*)?\d{2}-\d{3,5})*\.?$", re.I)
# The lower tribunal's own docket, as the origin band states it.
_LOWER_DOCKET = re.compile(
    r"^(?:USDC|Agency|Civil Action|Tax Court|BIA|Case)\s+Nos?\.\s*\S", re.I)
# The connective a consolidated record prints between two dockets. A closed
# vocabulary of one phrase — it may sit in the docket band (moreau) or at
# the foot of the caption that precedes the next docket (plaquemines), and
# it belongs to the docket either way.
_CONSOLIDATED = ("consolidated with", "c/w")
# The calendar ca5 names under the docket on its unsigned dispositions.
_CALENDAR = re.compile(r"^(?:Summary|Non-Argument|Oral Argument)\s+Calendar\.?$",
                       re.I)

# ORIGIN OPENERS — how ca5 names the tribunal it is reviewing. A closed
# vocabulary of the court's own openers, never a test on the court's NAME.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "cross-appeals from", "petition for review", "petitions for review",
    "on petition for review", "on petitions for review", "on remand from",
    "review of", "on review of", "appeal of", "appeals of",
    "petition for writ", "on petition for writ", "petition for a writ",
    "on petition for a writ", "application for certificate",
    "application for leave", "on application for", "on writ of",
    "motion for", "consolidated appeals from", "direct appeal from",
)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "debtor", "debtors", "intervenor",
    "intervenors", "intervenor plaintiffs", "amicus", "amici", "movant",
    "movants", "applicant", "applicants", "claimant", "claimants",
)
_STATUS_GLUE = ("and", "supporting", "the", "third", "party", "pro", "se",
                "cross", "in", "interest", "of", "plaintiffs", "defendants")
_BENCH_WORDS = ("judge", "judges", "justice", "justices")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _plain(text: str) -> str:
    """The row without its inline markup — what a criterion records."""
    return _norm(re.sub(r"<[^>]+>", "", text or ""))


def _is_banner(text: str) -> bool:
    low = _plain(text).lower().rstrip(".")
    return low in ("united states court of appeals",
                   "for the fifth circuit",
                   "united states court of appeals for the fifth circuit")


def _is_origin(text: str) -> bool:
    return _plain(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _is_docket(text: str) -> bool:
    flat = _plain(text)
    return bool(_DOCKET_ROW.match(flat)) or flat.lower() in _CONSOLIDATED \
        or bool(_CALENDAR.match(flat))


def _is_caps(text: str) -> bool:
    letters = [c for c in _plain(text) if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _roster_closed(text: str) -> bool:
    """The roster ends on a BENCH WORD followed by a full stop.

    'Before Jones and Engelhardt, Circuit Judges, and Summerhays,' /
    'District Judge.*' is one roster over two rows, and the designation
    footnote mark rides on its last word."""
    flat = _plain(text)
    bare = flat.rstrip().rstrip("*†‡0123456789").rstrip()
    return (any(w in flat.lower() for w in _BENCH_WORDS)
            and bare.endswith("."))


def _stamp_face(line) -> bool:
    """The row is set in the clerk's typeface, not the court's."""
    faces: dict[str, int] = {}
    for c in line.chars:
        if not (c.get("text") or "").strip():
            continue
        name = (c.get("fontname") or "").lower()
        faces[name] = faces.get(name, 0) + 1
    if not faces:
        return False
    dominant = max(faces, key=lambda k: faces[k])
    return any(f in dominant for f in _STAMP_FACES)


def _fences(model) -> dict:
    """Where each page sandwiches its sections: {page: [(top, line_or_None)]}.

    A fence is a rule of one of ca5's two measures set on the page axis. It
    may be TYPED (100 records) or DRAWN (2); a drawn rule whose ends
    coincide with a text row's is that row's UNDERLINE and is not a fence.
    """
    out: dict = {}
    for pm in model.pages:
        mid = (pm.width or 612.0) / 2
        found: list = []
        text_edges = [(l.x0, l.x1, l.top) for l in pm.lines if l.plain.strip()]
        for line in pm.lines:
            flat = line.plain.strip()
            if not flat or not is_typed_rule(flat):
                continue
            if _fence_measure(line.x0, line.x1, mid):
                found.append((line.top, line))
        for r in pm.h_rules:
            if not _fence_measure(r.x0, r.x1, mid):
                continue
            if any(abs(x0 - r.x0) <= 3 and abs(x1 - r.x1) <= 3
                   and -4 <= r.top - top <= 16 for x0, x1, top in text_edges):
                continue                     # an underline, not a fence
            found.append((r.top, None))
        if found:
            out[pm.number] = sorted(found, key=lambda f: f[0])
    return out


def _fence_measure(x0: float, x1: float, mid: float) -> bool:
    width = x1 - x0
    if abs((x0 + x1) / 2 - mid) > _FENCE_AXIS:
        return False
    return (_FENCE_SHORT[0] <= width <= _FENCE_SHORT[1]
            or _FENCE_LONG[0] <= width <= _FENCE_LONG[1])


def _panel_names(text: str) -> list:
    """The judges named in a 'Before …' roster.

    Split on the punctuation the court itself uses and keep the fragments
    that are not TITLES — a closed bench vocabulary, never a case test.
    A visiting judge's designation clause names nobody."""
    flat = _plain(text)
    for opener in ("before:", "before"):
        if flat.lower().startswith(opener):
            flat = flat[len(opener):]
            break
    at = flat.lower().find("sitting by")
    if at > 0:
        flat = flat[:at].rstrip(" ,")
    names: list = []
    for chunk in flat.replace(";", ",").split(","):
        piece = chunk.strip().strip(".*†‡: ").strip()
        if not piece:
            continue
        if any(w.strip(".") in _BENCH_WORDS for w in piece.lower().split()):
            continue
        for part in piece.replace(" and ", "|").split("|"):
            name = part.strip().strip(".*†‡: ").strip()
            if name.lower().startswith("and "):
                name = name[4:].strip()
            if not name or not any(c.isalpha() for c in name):
                continue
            # A generational SUFFIX is part of the judge's name, not another
            # judge ('James E. Graves, Jr.').
            if names and name.rstrip(".").upper() in ("JR", "SR", "II",
                                                      "III", "IV"):
                names[-1] = f"{names[-1]}, {name}"
                continue
            names.append(name)
    return names


def _is_status(text: str) -> bool:
    """A row that names a party's ROLE rather than a party.

    ca5 sets the em dash between the two roles ('Plaintiff—Appellant,',
    'Defendants—Appellants/Cross-Appellees,'), so the dash and the slash are
    separators, not letters."""
    bare = _plain(text).rstrip(".,; ").lower()
    if not bare or len(bare) > 80:
        return False
    words = [w.strip(".,;: ") for w in
             re.split(r"[\s—–/-]+", bare) if w.strip(".,;: ")]
    return bool(words) and all(w in _STATUS_WORDS or w in _STATUS_GLUE
                               for w in words)


def _sides(caption_rows: list, one_sided: bool = False):
    """The two party names either side of the pivot.

    Built from the party NAMES, never by joining the caption wholesale — the
    status labels and the pivot are apparatus, not names."""
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in caption_rows:
        flat = _plain(row)
        bare = flat.strip().rstrip(".,").lower()
        if bare in ("v", "vs", "versus"):
            side = right
            seen_pivot = True
            continue
        if bare in _CONSOLIDATED or _CALENDAR.match(flat) \
                or _DOCKET_ROW.match(flat):
            continue
        if _is_status(flat):
            continue
        if bare.startswith(("versus ", "v. ", "vs. ")):
            side = right
            seen_pivot = True
            flat = flat.split(None, 1)[1]
        side.append(flat)
    if one_sided:
        return _plain(" ".join(left + right)).rstrip(",. ") or None
    if not (left and right and seen_pivot):
        return None
    return (_plain(" ".join(left)).rstrip(",. "),
            _plain(" ".join(right)).rstrip(",. "))


@decider("headmatter.read", court="ca5")
def read_headmatter_ca5(model, geom, **_):
    """Read ca5's typed-sandwich headmatter, or NOTHING.

    NOTHING is returned for anything that is not the contract above: core's
    shared walk places those rows unidentified, which is a smaller error
    than a confident misreading."""
    if not model.pages:
        return NOTHING
    fences = _fences(model)
    if len(fences.get(1, ())) < 2:
        return NOTHING                     # not the typed-sandwich contract

    from ..resolve.footnotes import line_markup

    finder = FurnitureFinder(model, geom.body_x0 if geom else _RAIL,
                             geom.body_size if geom else 13.0)
    parser = BylineParser(CA5.byline)
    pages_by_no = {pm.number: pm for pm in model.pages}

    # ---- the rows, in page order, minus the page's furniture -------------
    rows: list = []                        # (page, top, line)
    stamp_lines: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            # FURNITURE the page carries into the region: the CM/ECF strip
            # ('Case: 25-30016  Document: 52-1  Page: 1 …'), the running
            # head and the foot folio. Core measures and records those; the
            # reader steps over them rather than claiming them twice.
            if finder.kind(pm, line):
                continue
            # THE CLERK'S FILING STAMP is the court's furniture, not the
            # court's words: it is set in the clerk's own face and pinned
            # right of the measure. Claimed here so it is RECORDED — core
            # does not recognize it, and left behind it renders inside the
            # caption, interleaved with the docket by top position.
            if (pm.number == 1 and line.x0 >= _STAMP_MIN_X0
                    and _stamp_face(line)):
                stamp_lines.append(line)
                continue
            rows.append((pm.number, line.top, line))
    rows.sort(key=lambda r: (r[0], r[1]))
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for _, _, l in rows[:5]):
        return NOTHING                     # ca5 always names itself first

    # ---- bands, and the fences that close them --------------------------
    def band_of(page: int, top: float) -> tuple:
        return (page, sum(1 for t, _ in fences.get(page, ()) if t < top))

    bands: list = []                       # [(key, [lines])]
    for page, top, line in rows:
        key = band_of(page, top)
        if bands and bands[-1][0] == key:
            bands[-1][1].append(line)
        else:
            bands.append((key, [line]))

    # ---- what each band IS, by its own landmark -------------------------
    kinds: list = []
    seen_docket = seen_origin = False
    for _key, blines in bands:
        head = next((_plain(l.plain) for l in blines
                     if not is_typed_rule(l.plain.strip())), "")
        if seen_origin:
            # CA5 STATES ITS ORIGIN ONCE, for the whole record however many
            # appeals it consolidates — so everything below the origin's
            # closing fence is the tail. Tested BEFORE the origin openers,
            # because the posture recital that opens the tail is worded like
            # one ('ON REMAND FROM' / 'THE SUPREME COURT OF THE UNITED
            # STATES'), and read as a second origin it left the record with
            # no roster and no claim at all.
            kind = "tail"
        elif _is_origin(head) and not _is_caps(head):
            # …and the second guard on the same collision: ca5 sets its
            # origin in title case and its recital in caps.
            kind = "lower-court"
            seen_origin = True
        elif _is_docket(head):
            # A NEW DOCKET OPENS A NEW APPEAL, and the appeal starts with
            # its caption; a consolidated ca5 record repeats
            # docket-then-caption before stating one origin for them all.
            kind = "docket"
            seen_docket = True
        elif seen_docket:
            # EVERYTHING BETWEEN THE DOCKET AND THE ORIGIN IS THE CAPTION —
            # not only the rows that look like parties. The pivot says
            # nothing for itself and a wrapped respondent list looks like
            # prose; ca5 puts nothing else in that span.
            kind = "caption"
        else:
            kind = "court"
        kinds.append(kind)
    if "caption" not in kinds and "docket" not in kinds:
        return NOTHING
    if "tail" not in kinds:
        return NOTHING                     # no roster: not this contract

    # ---- emit ------------------------------------------------------------
    crit: dict = {"headmatter_style": STYLE_TYPED_SANDWICH}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    banner_rows: list[str] = []
    caption_rows: list[str] = []
    cases: list = []                       # one per docket band
    origin_rows: list[str] = []
    lower_dockets: list[str] = []
    recital_rows: list[str] = []
    roster_rows: list[str] = []
    stop = False

    # THE CAPTION'S OWN RIGHT RAIL, measured INSIDE the caption band and
    # nowhere else. Every ca5 caption row that leaves the body rail is a
    # STATUS label set flush right to this rail — all thirteen of them over
    # the corpus, and none of them is an indent. The shared alignment test
    # reads a row starting left of 0.6 of the page as left-aligned, and a
    # long status label ('Defendants—Appellants/Cross-Appellees.' at x0=295)
    # then rendered as a 187pt indent instead of a flush right.
    cap_x1 = max((l.x1 for (_k, bl), kd in zip(bands, kinds) if kd == "caption"
                  for l in bl if not is_typed_rule(l.plain.strip())),
                 default=0.0)

    def emit(line, role: str):
        pm = pages_by_no[line.page]
        align = line_alignment(line, pm.width, geom,
                               banner_center_min_size=(geom.body_size + 2.0)
                               if geom else None)
        if (role == "caption" and align == "L" and line.x0 > _RAIL + 24
                and cap_x1 and line.x1 >= cap_x1 - 3.0):
            align = "R"
        items.append(m.HmLine(
            text=_norm(line_markup(line)), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    last_key = None
    roster_open = False
    for (key, blines), kind in zip(bands, kinds):
        if stop:
            break
        # THE FENCE ITSELF RENDERS. A reader that claims the region
        # inherits the page's furniture — but a fence is not furniture, it
        # is the court's own section mark. A TYPED fence is a line of its
        # own and is emitted where it stands (below); a DRAWN one has no
        # line, so it borrows the provenance of the row above it and is
        # emitted at the boundary it closes. Band index IS fence index —
        # crossing from band b to band b' crosses fences b … b'-1.
        first = 0 if last_key is None or key[0] != last_key[0] else last_key[1]
        page_fences = fences.get(key[0], ())
        for i in range(first, min(key[1], len(page_fences))):
            if page_fences[i][1] is None and items:
                items.append(m.Rule(prov=items[-1].prov, span="full"))
        last_key = key

        for line in blines:
            flat = _plain(line.plain)
            # A TYPED RULE IS NEVER CONTENT. A fence renders as the court's
            # own section mark; so does the CONSOLIDATION DIVIDER inside a
            # caption, which is the same rule set flush at the rail.
            if is_typed_rule(line.plain.strip()):
                consumed.add(line.id)
                items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                    typed=True, span="full"))
                continue
            if kind == "court":
                if _is_banner(flat):
                    banner_rows.append(flat)
                    emit(line, "court")
                else:
                    # 'REVISED' over the banner — what the court calls this
                    # printing of the paper.
                    crit.setdefault("title", flat)
                    emit(line, "title")
                continue
            if kind == "docket":
                _record_docket(crit, cases, flat)
                emit(line, "docket")
                continue
            if kind == "caption":
                if flat.lower() in _CONSOLIDATED or _DOCKET_ROW.match(flat):
                    # The connective and a docket that opens a consolidated
                    # appeal belong to the DOCKET wherever the page sets
                    # them (plaquemines prints 'consolidated with' at the
                    # foot of the first caption).
                    _record_docket(crit, cases, flat)
                    emit(line, "docket")
                    continue
                caption_rows.append(flat)
                if cases:
                    cases[-1]["caption"].append(flat)
                emit(line, "caption")
                continue
            if kind == "lower-court":
                origin_rows.append(flat)
                if _LOWER_DOCKET.match(flat):
                    lower_dockets.append(flat)
                emit(line, "lower-court")
                continue
            # ---- the trailing band: recital, roster, then the writing ----
            if roster_open:
                # A roster wraps as many rows as the measure takes and ends
                # on a bench word with a full stop. The row after it is the
                # BYLINE, and the reader has no business below it.
                roster_rows.append(flat)
                emit(line, "panel")
                if _roster_closed(flat):
                    roster_open = False
                    stop = True
                continue
            low = flat.lower()
            if low.startswith("before") and len(flat) < 300:
                roster_rows.append(flat)
                emit(line, "panel")
                roster_open = not _roster_closed(flat)
                stop = not roster_open
                continue
            # THE POSTURE RECITAL: what brought the case back here, set in
            # caps between the origin and the roster ('ON REMAND FROM' /
            # 'THE SUPREME COURT OF THE UNITED STATES', 'ON PETITION FOR
            # REHEARING'). It is history, not the paper's name — reading it
            # as a title is what typed three signed opinions as orders.
            if _is_caps(flat) and len(flat) <= 60 and not parser.parse(flat):
                recital_rows.append(flat)
                emit(line, "title")
                continue
            stop = True                     # anything else is the writing
            break

    if not roster_rows:
        return NOTHING                      # the roster is the contract's end

    # ---- criteria --------------------------------------------------------
    if banner_rows:
        crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        # THE PARTIES ARE THE LEAD CASE'S. A consolidated record prints one
        # caption per appeal; joining them all yields a case name that names
        # four sides and belongs to none of them.
        lead = next((c["caption"] for c in cases if c["caption"]),
                    caption_rows)
        sides = _sides(lead)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        else:
            # A MANDAMUS PETITION HAS ONE SIDE ('In re Google, L.L.C.,' /
            # 'Petitioner.'). One party is still the parties.
            one = _sides(lead, one_sided=True)
            if one:
                crit["parties"] = [one]
                crit["case_name"] = one
    if origin_rows:
        crit["lower_court"] = _norm(" ".join(origin_rows))
    for docket in lower_dockets:
        crit.setdefault("other_dockets", []).append(docket)
    if recital_rows:
        crit["history"] = _norm(" ".join(recital_rows))
    if roster_rows:
        printed = _norm(" ".join(roster_rows))
        crit["panel_line"] = printed
        roster = printed
        if roster.lower().startswith("before"):
            roster = roster[len("before"):].lstrip(": ")
        crit["judges"] = roster
        names = _panel_names(printed)
        if names:
            crit["panel"] = names

    # ---- the clerk's stamp: read, then recorded --------------------------
    if stamp_lines:
        stamp_lines.sort(key=lambda l: l.top)
        text = _norm(" ".join(_plain(l.plain) for l in stamp_lines))
        for hit in _DATE.finditer(text):
            if hit.group(1).split()[0].strip(".,").lower() in _MONTHS:
                crit.setdefault("decision_date", _norm(hit.group(1)))
                break
        dropped.append(m.Dropped(
            text=text[:600],
            prov=m.Prov(stamp_lines[0].page,
                        tuple(l.id for l in stamp_lines)), kind="stamp"))
        consumed.update(l.id for l in stamp_lines)

    # A POSTURE RECITAL IS NOT A DOCUMENT TITLE. 'ON PETITION FOR REHEARING'
    # is the only heading-shaped row these signed opinions print, and the
    # shared classifier reads it as an order's name. Where the reader saw
    # the recital AND the row it stopped on is a byline, the paper is the
    # opinion the byline signs.
    doc_type_final = None
    if recital_rows:
        # ``rows`` is in page order and everything above the stop is
        # claimed, so the first unclaimed row IS the row that ended the
        # reader — the byline, where there is one.
        nxt = next((l for _p, _t, l in rows if l.id not in consumed), None)
        if nxt is not None and parser.parse(_plain(nxt.plain)):
            doc_type_final = m.DocType.OPINION

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed, "anchor_ids": [],
            "doc_type_final": doc_type_final}


def _record_docket(crit: dict, cases: list, flat: str) -> None:
    if _CALENDAR.match(flat) or flat.lower() in _CONSOLIDATED:
        return
    cases.append({"docket": flat, "caption": []})
    if not crit.get("docket_number"):
        crit["docket_number"] = flat
    else:
        crit.setdefault("other_dockets", []).append(flat)
