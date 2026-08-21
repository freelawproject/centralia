"""Utah Court of Appeals ('utahctapp').

Everything unique to utahctapp lives here. It imports core, never another
court file, and no other court file imports it. Same publisher as the Utah
Supreme Court, so the CONTRACT is the same shape as `utah.py`'s — but every
measurement in it is different, and they are re-measured below rather than
inherited.

THE CONTRACT — 'fenced cover' (30 of 30 records). The court sets its whole
front matter as ONE COLUMN on the page axis and FENCES every section with a
72.0pt ORNAMENT centred on that axis. The cover opens on a 324.0pt rule
under the public-domain citation, and from there the ornaments name the
sections by standing between them:

    2026 UT App 110                              the public-domain citation
    ─────────── 324.0pt, x0=144.0 ───────────    …the cover OPENS
    THE UTAH COURT OF APPEALS                    14pt — the masthead
    ──── 72pt, on the axis ────
    STATE OF UTAH,                               the caption: a party…
    Appellee,                                    …its status…
    v.                                           …the pivot…
    HEATH WADE ANDERSON,                         …the other side…
    Appellant.
    ──── 72pt, on the axis ────
    Opinion                                      what the paper calls itself
    No. 20240323-CA                              …this court's own docket…
    Filed July 23, 2026                          …and the day it was filed
    ──── 72pt, on the axis ────
    Eighth District Court, Duchesne Department    the court below…
    The Honorable Samuel P. Chiara                …who tried it…
    No. 211800371                                 …and its own number
    ──── 72pt, on the axis ────
    Lyla Mahmoud, Debra M. Nelson, Benjamin       the appearances, each entry
    Miller, and Wendy M. Brown, Attorneys         CLOSED BY ITS OWN ROLE
    for Appellant                                 PHRASE
    ──── 72pt, on the axis ────
    JUDGE MICHELE M. CHRISTIANSEN FORSTER         who wrote and who joined —
    authored this Opinion, in which JUDGES        the authorship summary
    RYAN M. HARRIS and JOHN D. LUTHY concurred.
    ──── 72pt, on the axis ────
    CHRISTIANSEN FORSTER, Judge:                  …and the writing starts

THE DIVIDER, MEASURED: **there is none, and none is invented.** Over the
whole corpus — 30 records, 650 pages — pdfio reads **0 vertical rules**.
The caption is a single centred column; nothing stands beside it, so no
second column is built and no x0 threshold is pressed into service as a
rail. This is the `iowactapp`/`nmctapp`/`nmcca` branch of the divider
taxonomy: genuinely one column. What DOES parse the page is the horizontal
ornament, and it is read by ITS MEASURE AND ITS RAIL.

THREE DRAWN-RULE POPULATIONS ON A COVER PAGE, and all three are told apart
by measure and rail, never by position or by medium:

    72.0pt, x0=270.0, on the axis      the section fence — 183 on the 30
                                       cover pages, width 72.0 ± 0.0, axis
                                       offset 0.0 on 180 of them and 0.8pt
                                       on the other 3 (x0=269.2, one fence
                                       on each of the three 'in re' covers)
    324.0pt, x0=144.0, on the axis     the rule that OPENS the cover — one
                                       per record, top=82.7 on all 30
    345.6pt, x0=133.2, AT THE BODY     the footnote separator — 9 covers
    RAIL, the page's full measure      set a note on page 1

Note that the separator is WIDER than the opening rule, so measure alone
takes both: the opener starts 10.8pt INSIDE the body rail and the separator
starts exactly ON it. Rail first, measure second (ca5's lesson, arrived at
from the other side).

A BAND IS THE UNIT OF MEANING, NOT A ROW (ca4's lesson). Each fenced band
is asked ONCE what section it is, from a landmark of its own:

    masthead      a row set at 14.0pt — the only type above the 12.0pt body
    caption       a free-standing pivot row, a party STATUS row, or the
                  'IN THE MATTER OF …' / 'IN THE INTEREST OF …' style the
                  court gives a case with no adversary
    docket        'No. 20240323-CA' — this court's own closed docket form,
                  eight digits and the '-CA' suffix. THE SUFFIX IS THE
                  WHOLE POINT: the court below numbers its case with bare
                  digits ('No. 211800371'), and conflating the two is the
                  error that cost `ill` its corpus
    dates         a row opening on a date leader (all 30 print 'Filed')
    below         'The Honorable …' or 'Commissioner …', a tribunal name,
                  and the trial court's own number
    counsel       the ROLE PHRASE 'Attorney(s) for <status>' — 30 of 30
                  records close every appearance with one, so the band is
                  read FROM THAT PHRASE and never from wording heuristics
                  about names. This is where utahctapp differs from utah:
                  the Supreme Court prints a standing 'Attorneys:' LABEL
                  and the Court of Appeals prints none at all
    panel         'authored', which this court uses for the authorship
                  summary and NEVER for a byline

BAND ORDER IS NOT ASSUMED. 27 covers set six fences; the three 'in re'
covers set seven, splitting the caption into a CASE-TITLE band above the
party band. Each band answers for itself, so an absent, repeated or split
band costs nothing.

THE READER STOPS AT THE LAST FENCE, and that is a structural bound rather
than a guess: on all 30 records the final ornament stands immediately above
the byline. The trailing region is read only as far as its first byline, so
a cover that carried its summary past the last fence would still be read.

THE BYLINE GRAMMAR THIS COURT ACTUALLY PRINTS IS DECLARED HERE, because
`get_profile("utahctapp").byline` names a different one and the difference
is load-bearing. The court signs `LUTHY, Judge:` /
`HARRIS, Judge (concurring in part …):` — name first, title after the comma,
which is the `prose` style. The registered profile says
`style="abbrev", titles=("Justice",), also_reversed=True`, under which:

  * the real byline does not parse AT ALL — `LUTHY, Judge:` -> None on all
    30 records;
  * the AUTHORSHIP SUMMARY does — 'JUDGE MICHELE M. CHRISTIANSEN FORSTER
    authored this Opinion, in which' parses as a reversed byline, which is
    why core alone signed every majority with the summary row and left
    `CHRISTIANSEN FORSTER, Judge:` sitting in the prose;
  * `state_v._shay`'s concurrence (`HARRIS, Judge (concurring in part and
    concurring in the result):`, page 15) is invisible, so that record
    reads as one writing where the paper prints two.

So the reader's own byline test uses the grammar declared in this file —
utah's discriminator by another route: there the verb 'authored' had to
separate the summary from a byline the parser could read, here the parser
simply cannot mistake them. The profile patch is queued, not applied.

THE ANNOUNCED AUTHOR is reported through core's own `announced_author`
seam. The cover ANNOUNCES its author; the writing SIGNS itself; the
signature outranks the announcement, and core enforces that precedence
already (`pipeline.py:1916` — it signs the lead writing from an
announcement only where the writing prints no byline of its own).

FURNITURE AND FOOTNOTES THE READER INHERITS BUT DOES NOT TAKE. Page 1
carries no running head; continuation pages carry a three-piece footer
('20240323-CA · 2 · 2026 UT App 110') left to core's furniture sweep. Nine
covers set their own footnotes below the drawn separator, and everything
below it on that page is the footnote zone, which core's zone reader
already handles — the reader takes none of it.

NO FENCE, NO CLAIM. A record that does not open on a 324pt rule with at
least four ornaments beneath it is not this paper; a band whose section
cannot be named, or a row above the opening rule that is neither the
citation nor a title, refuses the whole record. Core's shared walk is a
better answer than a misread one.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider

STYLE_COVER = "fenced cover"

# ---- utahctapp's declared facts (measured over the 30-record corpus) -----
# THE ORNAMENT FENCE: 72.0pt wide on every one of the 183 page-1 fences,
# centred on the page axis to 0.0 on 180 of them and to 0.8pt on the other
# three (x0=270.0 throughout, except one fence on each 'in re' cover at
# x0=269.2). Nothing else on the page is 72pt wide.
_FENCE = (68.0, 76.0)
_FENCE_AXIS = 8.0
# THE RULE THAT OPENS THE COVER: 324.0pt at x0=144.0, top=82.7, one per
# record. It is NARROWER than the footnote separator (345.6pt), so the rail
# decides first — the opener stands 10.8pt inside the body rail.
_OPENING = (300.0, 336.0)
# HOW MANY FENCES A COVER SETS: six on 27 records, seven on the three that
# set a case-title band above the parties.
_MIN_FENCES = 4
# THE MASTHEAD is 14.0pt against a 12.0pt body — the only type above it.
_MASTHEAD_SIZE = 13.0
# THE FOOTNOTE SEPARATOR is drawn AT the body rail in the page's own
# measure (345.6pt = 478.8 - 133.2 on all nine covers that set one).
_SEP_FRAC = 0.92
_RAIL_TOL = 6.0
# The cover is one centred column; every row on it is centred on the page
# axis, including the full-measure summary rows (x0=134.0, x1=477.8,
# mid=305.9 against an axis of 306.0).
_AXIS_TOL = 6.0
# THE COVER never runs past page 2 — the byline is on page 1 on all 30.
_MAX_PAGES = 2

# ---- the closed vocabularies this court prints ---------------------------
# THIS COURT'S OWN DOCKET: eight digits and the '-CA' suffix that names the
# Court of Appeals. The suffix is what tells it from the trial court's own
# number, which is bare digits in the very next band.
_OWN_DOCKET = re.compile(
    r"^Nos?\.\s*\d{6,10}-CA(?:\s*(?:,|and)\s*\d{6,10}-CA)*\.?$", re.I)
_OWN_DOCKET_NUM = re.compile(r"\d{6,10}-CA", re.I)
# …and the number the court BELOW gave the case: 'No.' and bare digits.
_BELOW_DOCKET = re.compile(r"^Nos?\.\s*[\w.\-]+(?:\s*,\s*[\w.\-]+)*\.?$", re.I)
_DIGITS = re.compile(r"\d[\w.\-]*")
# WHAT THE PAPER CALLS ITSELF. A closed set; all 30 records print 'Opinion'.
_TITLES = ("opinion", "amended opinion", "corrected opinion",
           "per curiam opinion", "opinion on remand", "memorandum decision",
           "amended memorandum decision", "order", "per curiam",
           "opinion and order", "supplemental opinion")
# THE DAYS THE COURT RECORDS. A finite set of leaders, each naming a step in
# the case's own progress — never a party and never a court.
_DATE_LEADERS = ("filed", "heard", "submitted", "argued", "decided",
                 "considered", "amended", "reheard", "resubmitted",
                 "reargued", "supplemental briefing received")
_FILED = "filed"
_SUBMITTED = ("heard", "submitted", "argued", "reargued", "considered")
# WHO TRIED IT BELOW — this court's honorifics for a trial judge and for a
# domestic-relations commissioner (schmidt sets both).
_BENCH_OFFICERS = ("the honorable", "honorable", "commissioner",
                   "judge pro tempore")
# WHAT A TRIBUNAL IS CALLED. A closed set of institution words; never a
# court NAME, which is open.
_TRIBUNAL_WORDS = ("court", "commission", "board", "division", "bar",
                   "committee", "agency", "office", "tribunal", "council",
                   "department")
# THE APPEARANCES' OWN ROLE PHRASE, and the only landmark the counsel band
# has: this court prints no 'Attorneys:' label. Matched on the band's rows
# JOINED, because the phrase splits across a line break on one record
# ('… Attorneys' / 'for Appellee').
_COUNSEL_ROLE = re.compile(
    r"\battorneys?\s+for\s+(?:appellant|appellee|petitioner|respondent|"
    r"plaintiff|defendant|intervenor|amicus|amici|cross-|the\s)", re.I)
# …and the other appearance forms the court uses for a party with no fee
# counsel. A closed vocabulary; nothing here is a name.
_COUNSEL_OTHER = ("guardian ad litem", "attorney general",
                  "self-represented", "pro se", "amicus curiae",
                  "attorney for", "attorneys for")
# THE AUTHORSHIP SUMMARY'S VERB — this court's alone, and never a byline's.
_AUTHORED = "authored"
_ROSTER_CUES = ("authored", "concurred", "joined", "participate",
                "dissent", "sat")
# WHO DID NOT SIT. Past this cue the summary stops naming the panel.
_ABSENCE_CUES = ("recus", "does not participate", "did not participate",
                 "became a member", "retirement", "retired",
                 "sat in his place", "sat in her place")
# BENCH TITLES, longest first — a finite role vocabulary (ca2's lesson:
# without it a roster yields a judge called 'and').
_BENCH_TITLES = ("PRESIDING JUDGES", "PRESIDING JUDGE", "SENIOR JUDGES",
                 "SENIOR JUDGE", "CHIEF JUDGE", "JUDGES", "JUDGE",
                 "JUSTICES", "JUSTICE")
_BENCH_RE = re.compile("|".join(_BENCH_TITLES))
# THE PUBLIC-DOMAIN CITATION this court assigns its own opinion. The series
# is 'UT App'; the Supreme Court's is 'UT'. This is NOT a docket.
_CITATION = re.compile(r"^(?:19|20)\d\d\s+UT\s+App\s+\d+$")
# A party's STATUS closes its side of the caption, including the compound
# forms a cross-appeal prints ('Appellees and Cross-appellants').
_STATUS_WORDS = ("appellant", "appellee", "petitioner", "respondent",
                 "plaintiff", "defendant", "intervenor", "movant",
                 "cross-appellant", "cross-appellee", "cross-petitioner",
                 "cross-respondent", "real party in interest",
                 "self-represented", "amicus", "amici")
_PIVOT = re.compile(r"^v\.?$", re.I)
# A case with no adversary names itself instead. Structural phrases, not
# names — a court states a matter this way or it states two parties.
_CASE_TITLE_LEADS = ("in the matter of", "in re", "in the interest of")
_CASE_TITLE_MARKS = ("in the matter of", "in the interest of",
                     "in the estate of", "in the guardianship of")
# FOOTNOTE MARKS. Utah's Supreme Court hangs stars off a caption row; the
# Court of Appeals hangs BODY-SIZE DIGITS ('MOUNTAIN WEST TOWING, ET AL.,1',
# 'Attorneys for Appellant, assisted by law student … Anderson1'). Stars
# include the PRIVATE-USE glyph the foundry substitutes, so any mark test
# strips it too. Stripped only from what is PARSED — never from what is
# rendered, where the mark stays a footnote reference.
_STARS = "*∗†‡§ "
# A trailing mark digit follows a letter or a closing punctuation mark; a
# year never does ('Filed July 23, 2026' — the digits follow a space).
_MARK_DIGIT = re.compile(r"(?<=[A-Za-z,.;:)])\d{1,2}$")

# THE BYLINE GRAMMAR THIS COURT PRINTS, declared here because the
# registered profile names another one (see the module docstring). Reversed
# forms are OFF deliberately: with them on, the authorship summary parses as
# a byline and the reader would stop on the panel band.
_BYLINE = BylineGrammar(
    style="prose",
    titles=("Judge", "Presiding Judge", "Senior Judge", "Chief Judge"))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _bare(text: str) -> str:
    """The row without the footnote mark the court hung on it."""
    flat = _norm(text).strip(_STARS).strip()
    return _MARK_DIGIT.sub("", flat).strip()


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


def _is_fence(rule, width: float) -> bool:
    """A DRAWN section fence: this court's one ornament measure, on the axis."""
    return (_FENCE[0] <= rule.width <= _FENCE[1]
            and abs((rule.x0 + rule.x1) / 2 - width / 2) <= _FENCE_AXIS)


def _is_opening(rule, width: float, rail: float) -> bool:
    """The rule that OPENS the cover: 324pt, on the axis, and standing INSIDE
    the body rail — which is what tells it from the wider footnote separator
    drawn AT that rail."""
    return (_OPENING[0] <= rule.width <= _OPENING[1]
            and abs((rule.x0 + rule.x1) / 2 - width / 2) <= _FENCE_AXIS
            and rule.x0 > rail + _RAIL_TOL)


def _is_separator(rule, measure: float, rail: float) -> bool:
    """The footnote separator: the page's own measure, AT the body rail."""
    return (rule.width >= measure * _SEP_FRAC
            and rule.x0 <= rail + _RAIL_TOL)


def _is_own_docket(text: str) -> bool:
    return bool(_OWN_DOCKET.match(_bare(text)))


def _is_below_docket(text: str) -> bool:
    flat = _bare(text)
    return bool(_BELOW_DOCKET.match(flat)) and not _is_own_docket(flat)


def _is_title(text: str) -> bool:
    return _bare(text).lower().rstrip(".") in _TITLES


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


def _is_counsel_text(joined: str) -> bool:
    low = joined.lower()
    return bool(_COUNSEL_ROLE.search(low)) or any(
        cue in low for cue in _COUNSEL_OTHER)


# --------------------------------------------------------------------------
# the bands
# --------------------------------------------------------------------------

def _band_kind(band: list) -> str | None:
    """What section a fenced band IS, from a landmark of its own — asked once
    per band, so a caption row naming a court is still a caption and a
    counsel row naming a judge is still counsel."""
    if not band:
        return "empty"
    joined = " ".join(r.flat for r in band)
    low = joined.lower()
    first = band[0].flat
    if any(r.size >= _MASTHEAD_SIZE for r in band):
        return "masthead"
    # THE SUMMARY'S VERB FIRST: a band carrying 'authored' is the panel band
    # whatever else it looks like (utah's lesson).
    if _AUTHORED in low and any(cue in low for cue in _ROSTER_CUES):
        return "panel"
    if _is_counsel_text(joined):
        return "counsel"
    if any(_is_own_docket(r.flat) for r in band) or _is_title(first):
        return "docket"
    if _date_leader(first):
        return "dates"
    # …and the caption BEFORE the court below, so a case against a tribunal
    # cannot be read as an origin.
    if any(_PIVOT.match(r.flat) for r in band) \
            or any(_is_status(r.flat) for r in band) \
            or first.lower().startswith(_CASE_TITLE_LEADS) \
            or any(mark in low for mark in _CASE_TITLE_MARKS):
        return "caption"
    if any(o in low for o in _BENCH_OFFICERS) \
            or (any(w in low for w in _TRIBUNAL_WORDS)
                and any(_is_below_docket(r.flat) for r in band)):
        return "below"
    if any(w in low for w in _TRIBUNAL_WORDS) and len(band) <= 3:
        return "below"
    if any(cue in low for cue in _ABSENCE_CUES):
        return "panel"
    return None


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------

def _caption_sides(rows: list) -> list:
    """The party names either side of the caption's own pivot row.

    The caption is stacked — a party, its status, the pivot, the other
    party, its status — so the sides are read from the ROWS, never by
    splitting a joined string (which yields 'STATE OF UTAH, Appellee, HEATH
    WADE ANDERSON'). A status row closes a side; a bare 'and' row joins
    another party to the side it is on; a case-title row names the matter
    rather than a party and belongs to neither side.
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

    Read from the BENCH TITLE and the ALL-CAPS tokens that follow it — the
    only all-caps words the court sets in this band ('authored', 'in which',
    'and', 'concurred' are all lower case). A PLURAL title covers a LIST, so
    'and' and a trailing comma separate one name from the next: without that
    'JUDGES RYAN M. HARRIS and JOHN D. LUTHY concurred.' yields one judge
    and drops the other. Stops at the first ABSENCE cue, past which the
    sentence names who did NOT sit.
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

    def _push(toks: list) -> None:
        name = _norm(" ".join(toks)).rstrip(",.;")
        if name and name not in names:
            names.append(name)

    for match in _BENCH_RE.finditer(head):
        toks: list = []
        for tok in head[match.end():].split():
            stem = tok.strip(",.;:()")
            if stem and stem.isupper() and any(c.isalpha() for c in stem):
                toks.append(tok.strip(",;:()"))
                if tok.endswith((",", ";")):
                    _push(toks)
                    toks = []
                continue
            if stem.lower() == "and" and toks:
                _push(toks)
                toks = []
                continue
            break
        _push(toks)
    return names


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
        self.announced: str | None = None
        # The MATTER a case with no adversary is captioned by, held until
        # every band has spoken: the parties, where the cover states any,
        # name the case (the ca2 rule — build the name from the party names
        # either side of the pivot), and the matter names it otherwise.
        self.matter: str | None = None

    def emit(self, row: _Row, role: str, align: str | None = None) -> None:
        pm = self.pages[row.page]
        if align is None:
            align = "C" if _on_axis(row.x0, row.x1, pm.width) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def fence(self, page: int) -> None:
        self.items.append(m.Rule(prov=m.Prov(page), typed=False,
                                 span="center"))

    def opening(self, page: int) -> None:
        self.items.append(m.Rule(prov=m.Prov(page), typed=False, span="full"))

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
        out = {"criteria": self.crit, "items": self.items, "attorneys": [],
               "dropped": self.dropped, "consumed": self.consumed,
               "anchor_ids": [], "doc_type_final": None}
        if self.announced:
            out["announced_author"] = self.announced
        return out


def _cover_events(model, finder, body_x0):
    """The cover's own stream: ('open'|'fence'|'row', …) in page order, with
    each page's footnote zone and its furniture left behind.

    Returns (events, opened) — `opened` is False when page 1 draws no
    opening rule, which is utahctapp declining the record.
    """
    events: list = []
    opened = False
    for pm in model.pages[:_MAX_PAGES]:
        rows = _page_rows(pm, finder)
        if not rows:
            continue
        measure = max(r.x1 - r.x0 for r in rows)
        # THE RAIL IS THE DOCUMENT'S, NOT THE PAGE'S. Read as this page's
        # own minimum x0 it happens to come out right on all 30 records —
        # but only because the opinion always OPENS on the cover page, so a
        # body-rail row is always present. On a cover with no prose under
        # the byline the rail would rise to the caption's own indent and the
        # 324pt opening rule would pass the separator's rail test.
        rail = min(body_x0, min((r.x0 for r in rows), default=body_x0))
        # WHERE THIS PAGE'S FOOTNOTE ZONE STARTS: the drawn separator at the
        # rail, in the page's own measure. Everything at or below it belongs
        # to core's zone reader, and the reader takes none of it. The rule
        # that OPENS the cover is excluded by name, not by measure — the
        # separator is the WIDER of the two and only the rail tells them
        # apart.
        zone_top = min((r.top for r in pm.h_rules
                        if _is_separator(r, measure, rail)
                        and not (pm.number == 1
                                 and _is_opening(r, pm.width, rail))),
                       default=None)
        page_events: list = []
        for rule in pm.h_rules:
            if zone_top is not None and rule.top >= zone_top:
                continue
            if pm.number == 1 and _is_opening(rule, pm.width, rail):
                opened = True
                page_events.append((rule.top, "open", None))
            elif _is_fence(rule, pm.width):
                page_events.append((rule.top, "fence", None))
        for row in rows:
            if zone_top is not None and row.top >= zone_top:
                continue
            page_events.append((row.top, "row", row))
        page_events.sort(key=lambda e: (e[0], e[1] != "open"))
        events.extend((pm.number, kind, payload)
                      for _, kind, payload in page_events)
    return events, opened


def _is_writing_byline(row: _Row, parser) -> bool:
    """Does this row SIGN a writing?

    The court signs `LUTHY, Judge:`; it ANNOUNCES with 'JUDGE JOHN D. LUTHY
    authored this Opinion, in which'. Under the grammar declared in this
    file the announcement cannot parse, and the verb test is kept as a belt
    against a grammar change.
    """
    if _AUTHORED in row.text.lower():
        return False
    return parser.parse(_norm(row.text)) is not None


@decider("headmatter.read", court="utahctapp")
def read_headmatter_utahctapp(model, geom, **_):
    """Read utahctapp's fenced cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 133.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    events, opened = _cover_events(model, finder, body_x0)
    if not opened:
        return NOTHING            # no opening rule: not this paper

    # THE COVER OPENS ON THE 324pt RULE. Above it stands the public-domain
    # citation, and on a paper that names itself, its own name.
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
    if fences < _MIN_FENCES:
        return NOTHING            # not enough of the cover is fenced

    parser = BylineParser(_BYLINE)

    # Split the stream into fenced bands. A band runs from one ornament to
    # the next; the last band is the trailing region below the final fence,
    # which on all 30 records opens on the byline.
    bands: list = [[]]
    fence_pages: list = [None]
    for page, kind, payload in rest:
        if kind == "fence":
            bands.append([])
            fence_pages.append(page)
            continue
        bands[-1].append(payload)

    # …and read each band for what it is. THE READER ENDS AT THE FIRST
    # BYLINE, inside a band as well as at its head.
    plan: list = []
    for band in bands:
        cut = len(band)
        for index, row in enumerate(band):
            if _is_writing_byline(row, parser):
                cut = index
                break
        rows = band[:cut]
        kind = _band_kind(rows)
        if kind is None:
            return NOTHING        # a band we cannot name refuses the record
        plan.append((kind, rows))
        if cut < len(band):
            break                 # the writing starts here
    while plan and plan[-1][0] == "empty":
        plan.pop()
    if not plan:
        return NOTHING

    ctx = _Ctx(model, geom, body_x0, body_size)
    if not _read_head(ctx, head):
        return NOTHING            # a head row we cannot name is not this paper
    # A READER THAT CLAIMS THE BLOCK RE-EMITS ITS RULES — the opener
    # included; core draws them only on rows a reader left behind.
    ctx.opening(open_page)
    for index, (kind, band) in enumerate(plan):
        if fence_pages[index] is not None:
            ctx.fence(fence_pages[index])
        _READERS[kind](ctx, band)
    # …and the fence that CLOSES the block: the ornament between the last
    # band the reader read and the writing that follows it.
    if len(plan) < len(fence_pages) and fence_pages[len(plan)] is not None:
        ctx.fence(fence_pages[len(plan)])

    # …and only now, every band having spoken, does the matter get to name
    # the case. A cover that states parties names itself by them.
    if ctx.matter and "case_name" not in ctx.crit:
        ctx.crit["case_name"] = ctx.matter

    # POPULATE BEFORE GATING (wyo's lesson): the cover states both, and the
    # test runs after every band has had its say.
    if not (ctx.crit.get("court") and ctx.crit.get("docket_number")):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_COVER
    return ctx.result()


# ---- the bands, one reader each -----------------------------------------

def _read_head(ctx: _Ctx, rows: list) -> bool:
    """Above the opening rule: the public-domain citation, and on a paper
    that names itself there, its own name. A row that is neither is not
    this cover."""
    for row in rows:
        flat = row.flat
        if _CITATION.match(flat):
            ctx.crit["citation"] = flat
            ctx.emit(row, "citation", "C")
            continue
        if _is_title(flat) or (flat.upper() == flat
                               and any(c.isalpha() for c in flat)):
            ctx.crit.setdefault("title", flat.rstrip("."))
            ctx.emit(row, "title", "C")
            continue
        return False
    return True


def _read_masthead(ctx: _Ctx, band: list) -> None:
    for row in band:
        ctx.emit(row, "court", "C")
        if row.size >= _MASTHEAD_SIZE or "court" not in ctx.crit:
            ctx.crit["court"] = row.flat


def _read_caption(ctx: _Ctx, band: list) -> None:
    """A caption band: either the MATTER the case is about, or the PARTIES.

    The three 'in re' covers fence the two separately, and the distinction
    decides what the band contributes. A band that states the matter and
    carries no pivot names NO PARTY — reading its rows as parties gave
    matthews a litigant called 'DAVID HAROLD MATTHEWS' (the ward) and m.m.
    one called 'A PERSON UNDER EIGHTEEN YEARS OF AGE.' The matter title
    spans the band's rows, so it is the rows JOINED, not the first of them.
    """
    texts = [r.flat for r in band]
    for row in band:
        ctx.emit(row, "caption", "C")
    caption = ctx.crit.setdefault("caption", [])
    caption.extend(texts)
    has_pivot = any(_PIVOT.match(t) for t in texts)
    if _case_title(texts) and not has_pivot:
        title = _norm(" ".join(texts)).rstrip(",")
        ctx.matter = f"{ctx.matter} {title}" if ctx.matter else title
        return
    sides = _caption_sides(texts)
    parties = ctx.crit.setdefault("parties", [])
    for side in sides:
        if side not in parties:
            parties.append(side)
    if len(sides) >= 2 and "case_name" not in ctx.crit:
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"


def _date_row(ctx: _Ctx, row: _Row) -> None:
    lead = _date_leader(row.flat)
    value = _norm(row.flat[len(lead):]).strip(" .,")
    if lead == _FILED and "decision_date" not in ctx.crit:
        ctx.crit["decision_date"] = value
    elif lead in _SUBMITTED and "submitted" not in ctx.crit:
        ctx.crit["submitted"] = value
    ctx.emit(row, "date", "C")


def _read_docket(ctx: _Ctx, band: list) -> None:
    """The band that carries what the paper calls itself, this court's own
    docket, and the day it was filed."""
    for row in band:
        flat = row.flat
        if _is_own_docket(flat):
            for num in _OWN_DOCKET_NUM.findall(flat):
                if "docket_number" not in ctx.crit:
                    ctx.crit["docket_number"] = num
                elif num not in ctx.crit.setdefault("other_dockets", []):
                    ctx.crit["other_dockets"].append(num)
            ctx.emit(row, "docket", "C")
            continue
        if _date_leader(flat):
            _date_row(ctx, row)
            continue
        if _is_title(flat):
            ctx.crit.setdefault("title", flat.rstrip("."))
            ctx.emit(row, "title", "C")
            continue
        ctx.emit(row, "docket", "C")


def _read_dates(ctx: _Ctx, band: list) -> None:
    for row in band:
        if _date_leader(row.flat):
            _date_row(ctx, row)
        else:
            ctx.emit(row, "date", "C")


def _read_below(ctx: _Ctx, band: list) -> None:
    """The court below, who tried it, and its own number."""
    courts: list = []
    for row in band:
        flat = row.flat
        low = flat.lower()
        officer = next((o for o in _BENCH_OFFICERS if low.startswith(o)), None)
        if officer:
            judge = _norm(flat[len(officer):]).strip(" .,")
            if officer == "commissioner":
                judge = f"Commissioner {judge}"
            prev = ctx.crit.get("lower_court_judge")
            ctx.crit["lower_court_judge"] = (f"{prev}; {judge}" if prev
                                             else judge)
        elif _is_below_docket(flat):
            for num in _DIGITS.findall(flat):
                if num not in ctx.crit.setdefault("lower_court_docket", []):
                    ctx.crit["lower_court_docket"].append(num)
        else:
            courts.append(flat.rstrip(","))
        ctx.emit(row, "lower-court", "C")
    if courts:
        prev = ctx.crit.get("lower_court")
        joined = "; ".join(courts)
        ctx.crit["lower_court"] = f"{prev}; {joined}" if prev else joined


def _read_counsel(ctx: _Ctx, band: list) -> None:
    """The appearances, read from their ROLE PHRASE and left where the page
    put them — only their text is copied into criteria.

    That copy closes core-patch-queue item 41 inside this file: a reader
    that obeys the invariant ('counsel printed inside the headmatter STAYS
    there') reaches neither of the two sources `pipeline.py:1862-1870`
    copies from, so the appearances would be read perfectly and stated
    nowhere machine-readable.
    """
    for row in band:
        ctx.emit(row, "counsel")
    text = _norm(" ".join(r.flat for r in band))
    if text:
        prev = ctx.crit.get("attorneys")
        ctx.crit["attorneys"] = f"{prev} {text}" if prev else text


def _read_panel(ctx: _Ctx, band: list) -> None:
    """The authorship summary: who wrote and who joined.

    Kept beside the parsed form — `panel_line` is what the page printed,
    `panel` is the bench it names, and neither substitutes for the other.
    The first row is also reported to core as the ANNOUNCED author, which
    core uses only where the writing prints no byline of its own.
    """
    printed = _norm(" ".join(r.flat for r in band))
    prev = ctx.crit.get("panel_line")
    ctx.crit["panel_line"] = f"{prev} {printed}" if prev else printed
    panel = ctx.crit.setdefault("panel", [])
    for name in _roster(printed):
        if name not in panel:
            panel.append(name)
    if ctx.announced is None and _AUTHORED in printed.lower():
        ctx.announced = printed
    for row in band:
        ctx.emit(row, "panel")


def _read_empty(ctx: _Ctx, band: list) -> None:
    return None


_READERS = {
    "masthead": _read_masthead,
    "caption": _read_caption,
    "docket": _read_docket,
    "dates": _read_dates,
    "below": _read_below,
    "counsel": _read_counsel,
    "panel": _read_panel,
    "empty": _read_empty,
}
