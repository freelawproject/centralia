"""Supreme Court of Utah ('utah').

Everything unique to utah lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'fenced cover' (50 of 50 records). Utah sets its whole
front matter as ONE COLUMN on the page axis and FENCES every section with
a 90.0pt ORNAMENT centred on that axis. The cover opens on a
full-measure rule under the neutral citation, and from there the
ornaments name the sections by standing between them:

    This opinion is subject to revision before final   10pt italic — the
    publication in the Pacific Reporter                reporter's notice
    2025 UT 48                                         the neutral citation
    ─────────────── full measure ───────────────       …the cover OPENS
    IN THE                                             9.5pt
    SUPREME COURT OF THE STATE OF UTAH                 16pt — the masthead
    ──── 90pt, on the axis ────
    STATE OF UTAH,                                     the caption: a party…
    Appellee,                                          …its status…
    v.                                                 …the pivot…
    CHRISTOFFER ALAN HARRIS,                           …the other side…
    Appellant.
    ──── 90pt, on the axis ────
    No. 20250138                                       the docket…
    Heard July 16, 2025                                …and the two days
    Filed October 30, 2025                             the court records
    ──── 90pt, on the axis ────
    On Direct Appeal                                   how the case got here
    ──── 90pt, on the axis ────
    First District Court, Logan                        the court below…
    The Honorable Brian G. Cannell                     …who tried it…
    No. 231101518                                      …and its number
    ──── 90pt, on the axis ────
    Attorneys:                                         the appearances,
    David Drake, Midvale, for appellant                under their own label
    ──── 90pt, on the axis ────
    JUSTICE HAGEN authored the opinion of the Court,    who wrote and who
    in which JUSTICE PETERSEN … joined.                 joined — and who
    Due to his pending retirement, … PEARCE            did not sit
    does not participate herein; … BLANCH sat.
    ──── 90pt, on the axis ────
    JUSTICE HAGEN, opinion of the Court:               …and the writing
                                                        starts

THE ORNAMENT IS THE PARSER. Measured over the corpus, utah draws 337
horizontal rules on its cover pages and they fall into exactly two
populations: 50 full-measure rules (373.4pt, one per record, the one that
opens the cover) and the rest at 90.0pt ± 0.0, centred on the page axis to
the point. Nothing else on the page is 90pt wide. Where the type foundry
ran out of ornament the court TYPES the same fence instead — one record
sets a row of underscores 90.0pt wide at the same x0=261 — so the fence is
read by ITS MEASURE AND ITS AXIS, never by whether it was drawn or typed.

A BAND IS THE UNIT OF MEANING, NOT A ROW (ca4's lesson). Each fenced band
is asked ONCE what section it is, from a landmark of its own:

    masthead      a row set at 16pt — the only type above the 12pt body
    caption       a free-standing pivot row, a party STATUS row, or the
                  'In the Matter of …' style the court gives a case with
                  no adversary
    docket        'No. 20250138' — this court's own eight-digit docket
    dates         a row opening on a date leader (Heard/Filed/Submitted/
                  Argued/Amended/Supplemental Briefing Received)
    posture       a row opening on 'On ' — how the case reached the court
    below         'The Honorable …', a tribunal name, and its own number
    counsel       the printed label 'Attorneys' — every one of the 50
                  records prints it, so the band is read FROM THE LABEL
                  and never from wording heuristics about names
    panel         'authored', which utah uses for the authorship summary
                  and NEVER for a byline

BAND ORDER IS NOT ASSUMED. Six records omit the court below; two split
the docket and the dates into fences of their own; two set a case-title
band above the caption; one consolidates two captions in one band behind
a typed divider. Each band answers for itself, so an absent or repeated
band costs nothing.

THE READER STOPS AT THE FIRST BYLINE, and utah makes that decision
delicate: 'JUSTICE HAGEN authored the opinion of the Court, in which'
PARSES as a byline under this court's own grammar, and that is what put
the authorship summary inside the majority on every record core read
alone. The verb is the discriminator, and it is the court's own: the
summary says 'authored', the writing signs itself 'JUSTICE HAGEN,
opinion of the Court:'. So the byline test runs per BAND, and a band
carrying 'authored' is the panel band whatever else it looks like.

FURNITURE AND FOOTNOTES THE READER INHERITS BUT DOES NOT TAKE. The cover
runs onto page 2 on 13 records, so it inherits that page's running head
('BARRANI v. SALT LAKE CITY' over 'Opinion of the Court') and its folio —
both left to core's furniture sweep. And utah sets its cover's own
footnotes on the cover: a TYPED separator at the body rail, in the page's
full measure, and everything below it on that page is the footnote zone,
which core's zone finder already reads. Three typed-rule populations, and
all three are told apart by measure and rail, never by position:

    348pt at x0=132 (the rail)      the footnote separator — 101 of them
    282–288pt at x0=162, on axis    a caption's own divider — 4
    90pt at x0=261, on axis         the section fence — 1

The reporter's two-row notice is recorded as `Dropped`; nothing else
leaves the block.

NO FENCE, NO CLAIM. A record that does not open on a full-measure rule
with at least four ornaments beneath it is not this paper, and a band
whose section cannot be named refuses the whole record — core's shared
walk is a better answer than a misread one.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import get_profile

STYLE_COVER = "fenced cover"

# ---- utah's declared facts (measured over the 50-record corpus) ----------
# THE ORNAMENT FENCE: 90.0pt wide on every one of the 286 section fences,
# centred on the page axis to 0.0 (x0=261.0 on a 612pt page; 260.9 and
# 265.1 on one record each). Drawn as a rect or a curve, and typed as a row
# of underscores on one record — the measure and the axis decide, not the
# medium.
_ORNAMENT = (85.0, 95.0)
_ORNAMENT_AXIS = 10.0
# THE RULE THAT OPENS THE COVER: 373.4pt, x0=124.2 — wider than the body's
# own measure, and the only rule on the page that is.
_OPENING_MEASURE = 300.0
# HOW MANY FENCES A COVER SETS: 5 to 8 ornaments; the masthead, the
# caption, the docket and the posture are fenced on all 50.
_MIN_ORNAMENTS = 4
# THE MASTHEAD is 16.0pt against a 12.0pt body — the only type above it.
_MASTHEAD_SIZE = 15.0
# THE COVER runs onto page 2 on 13 records and never onto a third.
_MAX_PAGES = 3
# Centred on the page axis; a row that reaches the body rail is a wrap the
# page set flush left (ala's rule, and utah's counsel entries need it).
_AXIS_TOL = 6.0
_RAIL_TOL = 8.0
# THE FOOTNOTE SEPARATOR is typed at the body rail in the page's own
# measure; a CAPTION DIVIDER is typed on the axis at four fifths of it.
# Measured: separators 342–348pt at x0=130–135, dividers 282–288pt at
# x0=162–165 — the two populations do not come near touching.
_SEP_FRAC = 0.90
_TYPED_RULE = re.compile(r"^_{4,}$")

# ---- the closed vocabularies utah prints --------------------------------
# THIS COURT'S OWN DOCKET: eight digits, the year and a sequence
# ('No. 20250138'). A consolidation lists them on one row, and a second
# row may carry more ('Nos. 20250639, 20250932').
_DOCKET_ROW = re.compile(r"^Nos?\.\s*\d{6,10}(?:\s*,\s*\d{6,10})*\.?$")
_DOCKET_NUM = re.compile(r"\d{6,10}")
# THE DAYS THE COURT RECORDS. A finite set of leaders, each naming a step
# in the case's own progress — never a party or a court.
_DATE_LEADERS = ("heard", "filed", "submitted", "argued", "amended",
                 "reheard", "resubmitted", "decided", "considered",
                 "supplemental briefing received", "reargued")
# The day the court FILED the opinion is the decision date; the day it
# HEARD or took the case SUBMITTED is the submission.
_FILED = "filed"
_SUBMITTED = ("heard", "submitted", "argued", "reargued", "considered")
# HOW THE CASE REACHED THIS COURT, always stated as a prepositional phrase
# opening on 'On' ('On Direct Appeal', 'On Certiorari to the Utah Court of
# Appeals', 'On Petition for Extraordinary Relief', 'On Certification from
# the Court of Appeals', 'On Appeal of Interlocutory Order', 'On Petition
# for Review of …'). A wrap of it, and the 'and' joining two postures on a
# consolidated cover, continue the band.
_POSTURE_LEAD = "on "
# WHO TRIED IT BELOW — the court's own honorific.
_HONORABLE = "the honorable"
# WHAT A TRIBUNAL IS CALLED. A closed set of institution words; never a
# court NAME, which is open.
_TRIBUNAL_WORDS = ("court", "commission", "board", "division", "bar",
                   "committee", "agency", "office", "tribunal", "council")
# THE APPEARANCES' OWN LABEL. Printed on all 50 records, sometimes with a
# footnote mark ('Attorneys∗:', 'Attorneys*').
_COUNSEL_LABEL = re.compile(r"^attorneys?\b")
# THE AUTHORSHIP SUMMARY'S VERB — utah's alone, and never a byline's.
_AUTHORED = "authored"
# …and the summary's other shapes, for a band that names only who sat.
_ROSTER_CUES = ("authored", "joined.", "participate herein",
                "became a member of the court")
# WHO DID NOT SIT. Past this cue the summary stops naming the panel and
# starts explaining an absence, so the roster is read only above it.
_ABSENCE_CUES = ("recus", "does not participate", "did not participate",
                 "became a member", "retirement", "retired", " sat.",
                 "sat in his place", "sat in her place")
# BENCH TITLES, longest first — a finite role vocabulary (the ca2 lesson:
# without it a roster yields a judge called 'and').
_BENCH_TITLES = ("COURT OF APPEALS JUDGE", "DISTRICT COURT JUDGE",
                 "ASSOCIATE CHIEF JUSTICE", "VICE CHIEF JUSTICE",
                 "CHIEF JUSTICE", "PRESIDING JUDGE", "SENIOR JUDGE",
                 "JUSTICE", "JUDGE")
_BENCH_RE = re.compile("|".join(re.escape(t) for t in _BENCH_TITLES))
# THE NEUTRAL CITATION utah assigns its own opinion.
_CITATION = re.compile(r"^(?:19|20)\d\d\s+UT\s+\d+$")
# A party's STATUS closes its side of the caption. Utah's forms, including
# the compound ones a cross-appeal prints.
_STATUS_WORDS = ("appellant", "appellee", "petitioner", "respondent",
                 "plaintiff", "defendant", "intervenor", "movant",
                 "cross-appellant", "cross-appellee", "cross-petitioner",
                 "cross-respondent", "real party in interest",
                 "self-represented", "amicus", "amici")
_PIVOT = re.compile(r"^v\.?$", re.I)
# A case with no adversary names itself instead ('In the Matter of the
# Estate of BEVERLY MARIE DAVIES', 'STATE OF UTAH, in the interest of
# B.G.,').
_CASE_TITLE_LEADS = ("in the matter of", "in re", "in the interest of")
# …and the same phrases where the row opens on the petitioning body
# instead ('STATE OF UTAH, in the interest of B.G.,'). Structural phrases,
# not names — a court states a matter this way or it states two parties.
_CASE_TITLE_MARKS = ("in the matter of", "in the interest of",
                     "in the estate of")
# Footnote marks utah hangs off a caption row, a status or its counsel
# label. Stripped before a row is read, never from what is rendered.
_MARKS = "*∗†‡§ "


def _norm(text: str) -> str:
    return " ".join(text.split())


def _bare(text: str) -> str:
    """The row without the footnote mark the court hung on it."""
    return _norm(text).strip(_MARKS).strip()


# --------------------------------------------------------------------------
# the visual row
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def flat(self) -> str:
        return _bare(self.text)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _page_rows(pm, finder) -> list:
    """The page's content rows, furniture removed, in the page's order."""
    buckets: dict = {}
    loose: list = []
    for line in pm.lines:
        if not line.plain.strip():
            continue
        if finder.kind(pm, line):
            continue
        if line.row is not None:
            buckets.setdefault(line.row, []).append(line)
        else:
            loose.append(line)
    groups = list(buckets.values())
    for line in sorted(loose, key=lambda l: (l.top, l.x0)):
        for g in groups:
            if g[0].row is None and abs(g[0].top - line.top) <= 2.0:
                g.append(line)
                break
        else:
            groups.append([line])
    return sorted((_Row(g) for g in groups), key=lambda r: (r.top, r.x0))


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _on_axis(x0: float, x1: float, width: float) -> bool:
    return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL


def _is_ornament_rule(rule, width: float) -> bool:
    """A DRAWN section fence: utah's one ornament measure, on the axis."""
    return (_ORNAMENT[0] <= rule.width <= _ORNAMENT[1]
            and abs((rule.x0 + rule.x1) / 2 - width / 2) <= _ORNAMENT_AXIS)


def _typed_kind(row: _Row, width: float, measure: float,
                rail: float) -> str | None:
    """What a TYPED rule is, by its measure and where it starts: the cover's
    section fence, a caption's own divider, or the footnote separator."""
    if not _TYPED_RULE.match(row.text.replace(" ", "")):
        return None
    span = row.x1 - row.x0
    if span >= measure * _SEP_FRAC and row.x0 <= rail + _RAIL_TOL:
        return "separator"
    if _ORNAMENT[0] <= span <= _ORNAMENT[1] \
            and abs((row.x0 + row.x1) / 2 - width / 2) <= _ORNAMENT_AXIS:
        return "fence"
    return "divider"


def _is_docket(text: str) -> bool:
    return bool(_DOCKET_ROW.match(_bare(text)))


def _date_leader(text: str) -> str | None:
    low = _bare(text).lower()
    for lead in _DATE_LEADERS:
        if low.startswith(lead + " "):
            return lead
    return None


def _is_status(text: str) -> bool:
    low = _bare(text).lower().rstrip(".,;")
    if not low or len(low) > 70:
        return False
    words = [w for w in low.replace("/", " ").replace(",", " ").split()
             if w not in ("and", "the", "of", "in", "a")]
    if not words:
        return False
    hits = sum(1 for w in words
               if any(w.rstrip("s").startswith(s.split()[0])
                      for s in _STATUS_WORDS))
    return hits >= max(1, len(words) - 3)


# --------------------------------------------------------------------------
# the bands
# --------------------------------------------------------------------------

def _band_kind(band: list) -> str | None:
    """What section a fenced band IS, from a landmark of its own — asked
    once per band, so a roster row that parses as a byline still belongs to
    the roster and a caption row naming a court is still a caption."""
    if not band:
        return "empty"
    joined = " ".join(r.flat for r in band).lower()
    first = band[0].flat
    if any(r.size >= _MASTHEAD_SIZE for r in band):
        return "masthead"
    if _COUNSEL_LABEL.match(first.lower()):
        return "counsel"
    if any(cue in joined for cue in _ROSTER_CUES) and _AUTHORED in joined:
        return "panel"
    if _is_docket(first):
        return "docket"
    if _date_leader(first):
        return "dates"
    if first.lower().startswith(_POSTURE_LEAD):
        return "posture"
    if any(_PIVOT.match(r.flat) for r in band) \
            or any(_is_status(r.flat) for r in band) \
            or first.lower().startswith(_CASE_TITLE_LEADS) \
            or any(mark in joined for mark in _CASE_TITLE_MARKS):
        return "caption"
    if _HONORABLE in joined or (
            any(w in joined for w in _TRIBUNAL_WORDS)
            and any(_is_docket(r.flat) for r in band)):
        return "below"
    if any(w in joined for w in _TRIBUNAL_WORDS) and len(band) <= 3:
        return "below"
    # A band that names only who did NOT sit is still the panel's.
    if any(cue in joined for cue in _ABSENCE_CUES):
        return "panel"
    return None


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------

def _caption_sides(rows: list) -> list:
    """The party names either side of the caption's own pivot row.

    Utah stacks its caption — a party, its status, the pivot, the other
    party, its status — so the sides are read from the ROWS, never by
    splitting a joined string (which yields 'STATE OF UTAH, Appellee,
    CHRISTOFFER ALAN HARRIS'). A status row closes a side; a bare 'and'
    row joins another party to the side it is on; a case-title row names
    the matter rather than a party and belongs to neither side.
    """
    sides: list = [[]]
    for text in rows:
        flat = _bare(text)
        low = flat.lower().rstrip(".,;")
        if _PIVOT.match(flat):
            sides.append([])
            continue
        if _is_status(flat) or low in ("and", "and,") \
                or low.startswith(_CASE_TITLE_LEADS) \
                or any(mark in low for mark in _CASE_TITLE_MARKS):
            continue
        sides[-1].append(flat.rstrip(",;"))
    out = [_norm(" ".join(s)).rstrip(",; ") for s in sides]
    return [s for s in out if s]


def _case_title(rows: list) -> str | None:
    for text in rows:
        flat = _bare(text)
        low = flat.lower()
        if low.startswith(_CASE_TITLE_LEADS) \
                or any(mark in low for mark in _CASE_TITLE_MARKS):
            return flat.rstrip(",")
    return None


# --------------------------------------------------------------------------
# the roster's own grammar
# --------------------------------------------------------------------------

def _roster(text: str) -> list:
    """The bench names an authorship summary states, in order.

    Read from the BENCH TITLE and the ALL-CAPS surname that follows it —
    the only all-caps tokens utah sets in this band ('in which', 'and',
    'joined.' are all lower case). Stops at the first ABSENCE cue: past
    'Having recused themselves' the sentence names who did NOT sit, and
    those names are not the panel.
    """
    flat = _norm(text)
    low = flat.lower()
    cut = len(flat)
    for cue in _ABSENCE_CUES:
        i = low.find(cue)
        if i != -1:
            cut = min(cut, i)
    head = flat[:cut]
    names: list = []
    for match in _BENCH_RE.finditer(head):
        rest = head[match.end():].split()
        toks: list = []
        for tok in rest:
            bare = tok.strip(",.;:")
            if not bare:
                break
            initial = len(bare) == 1 and bare.isalpha()
            if bare.isupper() and (initial or bare.isalpha()):
                toks.append(tok.strip(",;:"))
                if tok.endswith((",", ";")):
                    break
            else:
                break
        name = _norm(" ".join(toks)).rstrip(",.;")
        if name and name not in names:
            names.append(name)
    return names


def _is_writing_byline(row: _Row, parser) -> bool:
    """Does this row SIGN a writing?

    Utah's authorship summary parses as a byline under this court's own
    grammar ('JUSTICE HAGEN authored the opinion of the Court, in which'),
    and that is what put the summary inside the majority on every record.
    The court's own verb tells the two apart: the summary says 'authored',
    the writing signs itself 'JUSTICE HAGEN, opinion of the Court:'.
    """
    text = row.text
    if _AUTHORED in text.lower():
        return False
    return parser.parse(_norm(text)) is not None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom, body_x0, body_size):
        self.model = model
        self.geom = geom
        self.body_x0 = body_x0
        self.body_size = body_size
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align: str | None = None) -> None:
        pm = self.pages[row.page]
        if align is None:
            align = "C" if (_on_axis(row.x0, row.x1, pm.width)
                            and row.x0 > self.body_x0 + _RAIL_TOL) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def fence(self, page: int, ids: tuple = ()) -> None:
        self.items.append(m.Rule(prov=m.Prov(page, ids),
                                 typed=bool(ids), span="center"))
        self.consumed.update(ids)

    def rule(self, row: _Row, span: str) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids),
                                 typed=True, span=span))
        self.consumed.update(row.ids)

    def drop(self, rows: list, kind: str) -> None:
        if not rows:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(r.text for r in rows)[:1200],
            prov=m.Prov(rows[0].page,
                        tuple(i for r in rows for i in r.ids)),
            kind=kind))
        for r in rows:
            self.consumed.update(r.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


def _cover_events(model, finder, body_x0):
    """The cover's own stream: ('rule', …) and ('row', …) in page order,
    with each page's footnote zone and its furniture left behind.

    Returns (events, opened) — `opened` is False when page 1 draws no
    full-measure rule, which is utah declining the record.
    """
    events: list = []
    opened = False
    for pm in model.pages[:_MAX_PAGES]:
        rows = _page_rows(pm, finder)
        if not rows:
            continue
        measure = max((r.x1 - r.x0) for r in rows
                      if not _TYPED_RULE.match(r.text.replace(" ", "")))
        rail = min((r.x0 for r in rows
                    if not _TYPED_RULE.match(r.text.replace(" ", ""))),
                   default=body_x0)
        # WHERE THIS PAGE'S FOOTNOTE ZONE STARTS: the typed separator at the
        # rail, in the page's own measure. Everything below it belongs to
        # core's zone reader, and the reader takes none of it.
        zone_top = None
        for row in rows:
            if _typed_kind(row, pm.width, measure, rail) == "separator":
                zone_top = row.top
                break
        page_events: list = []
        for rule in pm.h_rules:
            if zone_top is not None and rule.top >= zone_top:
                continue
            if pm.number == 1 and rule.width >= _OPENING_MEASURE:
                opened = True
                page_events.append((rule.top, "open", None))
            elif _is_ornament_rule(rule, pm.width):
                page_events.append((rule.top, "fence", None))
        for row in rows:
            if zone_top is not None and row.top >= zone_top:
                continue
            kind = _typed_kind(row, pm.width, measure, rail)
            if kind == "fence":
                page_events.append((row.top, "fence", row))
            elif kind == "divider":
                page_events.append((row.top, "divider", row))
            else:
                page_events.append((row.top, "row", row))
        page_events.sort(key=lambda e: e[0])
        events.extend((pm.number, kind, payload)
                      for _, kind, payload in page_events)
    return events, opened


@decider("headmatter.read", court="utah")
def read_headmatter_utah(model, geom, **_):
    """Read utah's fenced cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 130.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    events, opened = _cover_events(model, finder, body_x0)
    if not opened:
        return NOTHING            # no opening rule: not this paper

    # THE COVER OPENS ON THE FULL-MEASURE RULE. Above it stand the neutral
    # citation, the paper's own name where it has one, and the reporter's
    # two-row notice.
    head: list = []
    rest: list = []
    seen_open = False
    open_page = 1
    fences = 0
    for page, kind, payload in events:
        if kind == "open":
            seen_open = True
            open_page = page
            continue
        if not seen_open:
            if kind == "row":
                head.append(payload)
            continue
        if kind == "fence":
            fences += 1
        rest.append((page, kind, payload))
    if fences < _MIN_ORNAMENTS:
        return NOTHING            # not enough of the cover is fenced

    ctx = _Ctx(model, geom, body_x0, body_size)
    parser = BylineParser(get_profile("utah").byline)

    # Split the stream into fenced bands. A band runs from one ornament to
    # the next and may cross a page turn (13 records carry the appearances
    # or the roster onto page 2).
    bands: list = [[]]
    marks: list = [[]]            # the dividers and fences inside a band
    for page, kind, payload in rest:
        if kind == "fence":
            bands.append([])
            marks.append([])
            marks[-1].append(("fence", page, payload))
            continue
        if kind == "divider":
            marks[-1].append(("divider", page, payload))
            bands[-1].append(payload)
            continue
        bands[-1].append(payload)

    # …and read each band for what it is. THE READER ENDS AT THE FIRST
    # BYLINE — and inside a band as well as at its head: the final fence
    # falls above the roster on 43 records but below it on 7, where the
    # writing opens in the roster's own band after the page turn.
    plan: list = []
    for band in bands:
        cut = len(band)
        for index, row in enumerate(band):
            if _is_writing_byline(row, parser):
                cut = index
                break
        head_rows = band[:cut]
        rows = [r for r in head_rows
                if not _TYPED_RULE.match(r.text.replace(" ", ""))]
        kind = _band_kind(rows)
        if kind is None:
            return NOTHING        # a band we cannot name refuses the record
        plan.append((kind, head_rows))
        if cut < len(band):
            break                 # the writing starts here
    while plan and plan[-1][0] == "empty":
        plan.pop()
    if not plan:
        return NOTHING

    _read_head(ctx, head)
    # A READER THAT CLAIMS THE BLOCK RE-EMITS ITS FENCES — the rule that
    # opens the cover included; core draws it only on rows a reader left.
    ctx.items.append(m.Rule(prov=m.Prov(open_page), typed=False, span="full"))
    for index, (kind, band) in enumerate(plan):
        for mark, page, row in marks[index]:
            if mark == "fence":
                if row is None:
                    ctx.fence(page)
                else:
                    ctx.fence(page, row.ids)
        _READERS[kind](ctx, band)
    # …and the fence that CLOSES the block: the ornament between the last
    # band the reader read and the writing that follows it.
    if len(plan) < len(marks):
        for mark, page, row in marks[len(plan)]:
            if mark == "fence":
                ctx.fence(page, row.ids if row is not None else ())

    if not (ctx.crit.get("court") and ctx.crit.get("docket_number")):
        return NOTHING            # a cover states both
    ctx.crit["headmatter_style"] = STYLE_COVER
    return ctx.result()


# ---- the bands, one reader each -----------------------------------------

def _read_head(ctx: _Ctx, rows: list) -> None:
    """Above the opening rule: the citation, the paper's own name, and the
    reporter's notice — which is the only thing the reader removes."""
    notice: list = []
    for row in rows:
        flat = row.flat
        if _CITATION.match(flat):
            ctx.crit["citation"] = flat
            ctx.emit(row, "citation", "C")
            continue
        # THE PAPER NAMES ITSELF IN CAPS ('AMENDED OPINION'); the notice is
        # set as a sentence.
        if flat.upper() == flat and any(c.isalpha() for c in flat):
            ctx.crit.setdefault("title", flat.rstrip("."))
            ctx.emit(row, "title", "C")
            continue
        notice.append(row)
    ctx.drop(notice, "notice")


def _read_masthead(ctx: _Ctx, band: list) -> None:
    for row in band:
        ctx.emit(row, "court", "C")
        if row.size >= _MASTHEAD_SIZE:
            ctx.crit["court"] = row.flat
        elif "court" not in ctx.crit:
            ctx.crit["court"] = row.flat


def _read_caption(ctx: _Ctx, band: list) -> None:
    rows: list = []
    for row in band:
        if _TYPED_RULE.match(row.text.replace(" ", "")):
            # THE CAPTION'S OWN DIVIDER: a consolidation, or a case title
            # over the parties.
            ctx.rule(row, "center")
            continue
        rows.append(row)
        ctx.emit(row, "caption", "C")
    texts = [r.flat for r in rows]
    caption = ctx.crit.setdefault("caption", [])
    caption.extend(texts)
    sides = _caption_sides(texts)
    parties = ctx.crit.setdefault("parties", [])
    for side in sides:
        if side not in parties:
            parties.append(side)
    if len(sides) >= 2 and "case_name" not in ctx.crit:
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    title = _case_title(texts)
    if title and "case_name" not in ctx.crit and len(sides) < 2:
        ctx.crit["case_name"] = title


def _read_docket(ctx: _Ctx, band: list) -> None:
    for row in band:
        if _is_docket(row.flat):
            found = _DOCKET_NUM.findall(row.flat)
            for num in found:
                if "docket_number" not in ctx.crit:
                    ctx.crit["docket_number"] = num
                elif num not in ctx.crit.setdefault("other_dockets", []):
                    ctx.crit["other_dockets"].append(num)
            ctx.emit(row, "docket", "C")
            continue
        if _date_leader(row.flat):
            _date_row(ctx, row)
            continue
        ctx.emit(row, "docket", "C")


def _date_row(ctx: _Ctx, row: _Row) -> None:
    lead = _date_leader(row.flat)
    value = _norm(row.flat[len(lead):]).strip(" .,")
    if lead == _FILED and "decision_date" not in ctx.crit:
        ctx.crit["decision_date"] = value
    elif lead in _SUBMITTED and "submitted" not in ctx.crit:
        ctx.crit["submitted"] = value
    ctx.emit(row, "date", "C")


def _read_dates(ctx: _Ctx, band: list) -> None:
    for row in band:
        if _date_leader(row.flat):
            _date_row(ctx, row)
        else:
            ctx.emit(row, "date", "C")


def _read_posture(ctx: _Ctx, band: list) -> None:
    parts = [r.flat for r in band]
    prev = ctx.crit.get("history")
    stated = _norm(" ".join(parts)).rstrip(".")
    ctx.crit["history"] = f"{prev}; {stated}" if prev else stated
    for row in band:
        ctx.emit(row, "case-info", "C")


def _read_below(ctx: _Ctx, band: list) -> None:
    courts: list = []
    for row in band:
        flat = row.flat
        low = flat.lower()
        if low.startswith(_HONORABLE):
            judge = _norm(flat[len(_HONORABLE):]).strip(" .,")
            prev = ctx.crit.get("lower_court_judge")
            ctx.crit["lower_court_judge"] = (f"{prev}; {judge}" if prev
                                             else judge)
        elif _is_docket(flat):
            for num in _DOCKET_NUM.findall(flat) or [_bare(flat)]:
                if num not in ctx.crit.setdefault("lower_court_docket", []):
                    ctx.crit["lower_court_docket"].append(num)
        elif flat.lower().startswith("no."):
            num = _norm(flat[3:]).strip(" .,")
            if num and num not in ctx.crit.setdefault("lower_court_docket",
                                                      []):
                ctx.crit["lower_court_docket"].append(num)
        else:
            courts.append(flat.rstrip(","))
        ctx.emit(row, "lower-court", "C")
    if courts:
        prev = ctx.crit.get("lower_court")
        joined = "; ".join(courts)
        ctx.crit["lower_court"] = f"{prev}; {joined}" if prev else joined


def _read_counsel(ctx: _Ctx, band: list) -> None:
    """The appearances, read FROM THEIR LABEL and left where the page put
    them — only their text is copied into criteria."""
    entries: list = []
    for row in band:
        if not _COUNSEL_LABEL.match(row.flat.lower()):
            entries.append(row.flat)
        ctx.emit(row, "counsel")
    text = _norm(" ".join(entries))
    if text:
        prev = ctx.crit.get("attorneys")
        ctx.crit["attorneys"] = f"{prev} {text}" if prev else text


def _read_panel(ctx: _Ctx, band: list) -> None:
    """The authorship summary: who wrote, who joined, and who did not sit.

    Kept beside the parsed form — `panel_line` is what the page printed,
    `panel` is the bench it names, and neither substitutes for the other.
    """
    printed = _norm(" ".join(r.flat for r in band))
    prev = ctx.crit.get("panel_line")
    ctx.crit["panel_line"] = f"{prev} {printed}" if prev else printed
    panel = ctx.crit.setdefault("panel", [])
    for name in _roster(printed):
        if name not in panel:
            panel.append(name)
    for row in band:
        ctx.emit(row, "panel")


def _read_empty(ctx: _Ctx, band: list) -> None:
    return None


_READERS = {
    "masthead": _read_masthead,
    "caption": _read_caption,
    "docket": _read_docket,
    "dates": _read_dates,
    "posture": _read_posture,
    "below": _read_below,
    "counsel": _read_counsel,
    "panel": _read_panel,
    "empty": _read_empty,
}
