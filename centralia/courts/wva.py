"""Supreme Court of Appeals of West Virginia ('wva').

Everything unique to wva lives here. It imports core, never another court
file, and no other court file imports it.

THE PAPERS. wva publishes three, and each one is named by a LANDMARK it
always prints — never by a title and never by wording about the case:

    'typed sandwich' (36 of 50) — the term slip. Every section of the
    headmatter is SANDWICHED between rules centred on the document's own
    axis, and the rule's MEASURE names the section it opens: a SHORT rule
    (72-144pt) brackets the DOCKET, a LONG one (312-396pt) brackets the
    ORIGIN. Measured over the corpus: 154 fences, 77 short (72.0-144.1pt)
    and 77 long (311.7-396.1pt), TYPED on 24 records and DRAWN on 10 —
    and two records (andrea_dale_daye, carl_ray_summerfield) set both on
    the same page:

        IN THE SUPREME COURT OF APPEALS OF WEST VIRGINIA   the masthead…
        January 2026 Term                                  …and its term
                                        FILED              the clerk's
                                        May 18, 2026       electronic stamp,
        ____________                    C. CASEY FORBES    Arial, pinned to
        No. 23-603                      SUPREME COURT …    the right corner
        ____________
        STATE OF WEST VIRGINIA,                            the caption…
             Plaintiff Below, Respondent,                  …its statuses…
        V.                                                 …the pivot…
        AUSTIN STEVENS,
             Defendant Below, Petitioner.
        ________________________________
        Appeal from the Circuit Court of Cabell County     the origin…
        The Honorable Alfred E. Ferguson, Judge            …who tried it…
        Criminal Action No. 22-F-93                        …its number
        AFFIRMED                                           the disposition
        ________________________________
        Submitted: March 4, 2026                           the dates
        Filed: May 18, 2026
        Gary A. Collias, Esq.      John B. McCuskey, Esq.  the appearances,
        Appellate Advocacy Div.    Attorney General        set in two columns
        CHIEF JUSTICE BUNN delivered the Opinion …         the reader stops

    A CONSOLIDATED record repeats the whole sandwich — docket, caption,
    origin, disposition — once per appeal, joined by a centred 'AND', and
    states one set of dates and one roster of counsel for them all
    (city_of_weirton, west_virginia_department_of_human_services, statoil).

    'separate slip' (13 of 50) — a concurrence or dissent released on its
    own. No fences and no full caption: the clerk's stamp, then THE
    WRITING'S OWN CAPTION — the docket and the case on one row, set at the
    body rail in the body's own type — and then the byline.

        No. 23-558 – State of West Virginia v. Brendan W.
        WOOTON, Justice, concurring, in part, and dissenting, in part:

    THAT ROW IS CAPTION MATTER, NOT A TITLE. It states no name for the
    paper; it states the parties, the pivot and the number — the cover the
    court gives a writing it releases alone (the user's call on
    credit_acceptance, 2026-08-19: 'the line there is more like the
    caption'). Measured over the corpus: 12 of the 13 separate slips print
    it, in 15 rows all told (three carry the case name onto a second row —
    state_ex_rel…young, …butler_1, …the_honorable), always on page 1, at the
    body rail, in the body's own type, above the byline;
    state_of_west_virginia_v._richard_william_page prints none and opens on
    its byline.

    'clerk's hand-down' (1 of 50) — a per-curiam disposition entered by
    the Court and attested by the clerk. It names the STATE, not the
    court, recites the entry, and sets its caption at the body rail with
    the pivot, the docket and the tribunal's number on ONE row:

        STATE OF WEST VIRGINIA
        On May 21, 2026, the Supreme Court of Appeals of West Virginia
        made and entered the following order:
        Raze International, Inc.,
             Petitioner
        v.) No. 23-565 (Ohio County No. CC-35-2023-C-119)
        …
        DISMISSAL ORDER                          the writing opens here

A record that is none of these gets NOTHING: core's shared walk places
those rows unidentified, which is a smaller error than a confident
misreading.

THE AXIS IS THE DOCUMENT'S, NOT THE PAGE'S. arthur_c is imposed 21pt left
of centre — masthead, fences and caption all — so a fence test against
``page.width / 2`` takes none of its four rules. The axis is learned from
the rules themselves: the centre shared by two or more of them.

THE READER ENDS AT THE BYLINE — except on a separate slip, where the
printed DOCKET is the second landmark. wva's declared grammar reads both
the forms the court signs with ('JUSTICE WOOTON delivered the Opinion of
the Court.' and 'TRUMP, Justice:'), but not the title-case form one slip
uses ('Justice Wooton, dissenting:' — credit_acceptance). Rather than
invent a byline test here, the slip reader takes the caption row on the
strength of the docket the court printed on it, and the writing below is
left exactly as core reads it.

THE CLERK'S STAMP IS FURNITURE. Both West Virginia appellate courts overlay
the title page with an electronic FILED block set in a face the document
does not otherwise use (Arial against Times New Roman) and pinned to the
top-right corner. Its rows are interleaved BETWEEN the caption's rows by
top position, so left in place they read as caption text — 'FILED C.
CreAlSeEasYe FdO aRt B3:E0S0, pC.mLE.RK OF WEST VIRGINIA STATE OF WEST
VIRGINIA, …' was this court's `parties` criterion. It is claimed here and
recorded as Dropped. On one record (randy_c._cain) the stamp's date shares
a baseline with the masthead and pdfio reads them as ONE row; there the row
is split at the typeface boundary and each half goes where it belongs.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace as _dc_replace

from .. import model as m
from ..geometry import line_alignment
from ..pdfio.rules import is_typed_rule
from ..resolve.bylines import BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import get_profile

STYLE_SANDWICH = "typed sandwich"
STYLE_SLIP = "separate slip"
STYLE_HANDDOWN = "clerk's hand-down"

# ---- wva's declared facts (measured over all 50 records, not tuned) -------
# THE FENCES. 118 of them over the corpus, in two populations that never
# meet: SHORT 72.0-144.1pt around the docket, LONG 311.7-396.1pt around the
# origin. Typed or drawn — both are the same fence.
_FENCE_SHORT = (60.0, 170.0)
_FENCE_LONG = (280.0, 420.0)
# How far a fence's midpoint may sit off the DOCUMENT's axis. Measured
# spread over the corpus: 1.7pt. The footnote separator shares the SHORT
# measure exactly on one record (statoil types both at 144pt) and is 162pt
# off the axis, at the page's left text rail — the axis takes it, the
# measure never would.
_FENCE_AXIS = 6.0
# Two rules make an axis; one rule is a footnote separator.
_AXIS_TOLERANCE = 3.0
# HOW FAR THE BLOCK MAY RUN. A two-appeal consolidation carries its second
# sandwich onto page 2 (city_of_weirton, west_virginia_department_of_human_
# services, statoil); nothing in the corpus needs a third.
_MAX_PAGES = 3
# THE CLERK'S STAMP: a top-of-page, flush-right run set in a typeface the
# document does not otherwise use. All three tests are required — the
# court's own 'Filed: May 18, 2026' row is at the top of the page too, and
# a caption's flush-right status label is flush right too.
_STAMP_TOP_FRAC = 0.40
_STAMP_RIGHT_FRAC = 0.72
# THE ZONE GAP. wva leads its headmatter at 14.8-15.0pt and separates the
# origin from the disposition — and the caption's parties from their
# statuses — by a blank line. 1.55x the page's own modal leading takes the
# double and never the single.
_ZONE_GAP_FACTOR = 1.55
# …and a WRAP is set at the type's own leading. A separate slip states its
# case on one line and carries the overflow onto the next at 15pt against a
# 13pt type; whatever follows it stands 30pt or more below.
_WRAP_GAP_FACTOR = 1.6
# THE APPEARANCES NEVER FILL THE MEASURE. Every counsel row in the corpus
# stops at least 6pt short of the document's right edge (534.1 against
# 540.1 at the widest — 'Mountain State Justice, Inc.'); the opinion's own
# justified prose reaches it to within half a point. 3pt is the bound, and
# it is a GUARD, not a parser: the reader ends at the byline, and a walk
# that never finds one withdraws its claim whole.
_MEASURE_SLACK = 3.0

# THE COURT'S OWN DOCKET, in the three forms it prints: alone inside the
# sandwich, leading a separate slip's caption row, trailing one.
_DOCKET_ANY = re.compile(r"\bNos?\.\s*(\d{2}-\d{1,5})\b", re.I)
_DOCKET_LIST = re.compile(
    r"^Nos?\.\s*\d{2}-\d{1,5}"
    r"(?:\s*(?:,|and|&)\s*(?:Nos?\.\s*)?\d{2}-\d{1,5})*\.?$", re.I)
# THE MASTHEAD, and the STATE's own name on the clerk's hand-down.
_BANNER = "in the supreme court of appeals of west virginia"
_STATE = "state of west virginia"
# 'January 2026 Term' — the sitting the slip belongs to.
_TERM = re.compile(r"^[A-Z][a-z]+\s+\d{4}\s+Term\.?$")
# 'Submitted: March 4, 2026' / 'Filed: May 18, 2026' — wva labels both.
_DATED = re.compile(r"^(Submitted|Filed|Argued|Decided|Resubmitted)"
                    r"\s*:\s*(.+)$", re.I)
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})")
# HOW wva NAMES THE TRIBUNAL IT IS REVIEWING. A closed vocabulary of the
# court's own openers, never a test on the tribunal's NAME.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "certified question from", "certified questions from",
    "original proceeding", "petition for", "petitions for",
    "on petition for", "on certified question", "review of",
    "on review of", "lawyer disciplinary proceeding",
    "judicial disciplinary proceeding", "appeal of", "certified question",
)
# The origin band names who tried it below.
_JUDGE_ROW = re.compile(r"^\(?(?:The\s+)?Honorable\b", re.I)
# …and the number the tribunal below gave the case.
_LOWER_DOCKET = re.compile(
    r"\b(?:Nos?|Case\s+Nos?|Civil\s+Action\s+Nos?|Criminal\s+Action\s+Nos?"
    r"|Action\s+Nos?|Docket\s+Nos?|Appeal\s+Nos?)\.\s*\S", re.I)
# …which the Intermediate Court's own number is sometimes printed without
# ('22-ICA-150' alone on its row — nicholas_a._ghaphery).
_BARE_DOCKET = re.compile(r"^\(?\d{2}-[A-Z]{2,6}-\d{1,5}\)?$")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. wva sets the trial posture beside the appellate one
# ('Petitioner Below, Petitioner,' / 'Petitioner below/Petitioner,').
_STATUS_WORDS = (
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "intervenor", "intervenors", "movant",
    "movants", "complainant", "complainants", "amicus", "amici",
    "applicant", "applicants", "claimant", "claimants",
)
_STATUS_GLUE = ("and", "below", "the", "cross", "pro", "se", "in", "of",
                "interest", "party", "third")
# The connective a consolidated record prints between two appeals.
_CONNECTIVE = ("and",)
# The clerk's hand-down names itself by its recital, not by its heading.
_HANDDOWN_RECITAL = "made and entered"


# --------------------------------------------------------------------------
# small readings
# --------------------------------------------------------------------------

def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _plain(text: str) -> str:
    """The row without its inline markup — what a criterion records."""
    return _norm(re.sub(r"<[^>]+>", "", text or ""))


def _family(fontname: str) -> str:
    """Typeface family, ignoring the subset tag and the style: 'BCDGEE+
    TimesNewRomanPS-ItalicMT' and 'TimesNewRomanPSMT' are one family,
    'BCDGEE+Arial-BoldMT' and 'ArialMT' are another."""
    name = (fontname or "").split("+")[-1].split(",")[0].split("-")[0]
    return name[:-2] if name.endswith("MT") else name


def _is_banner(text: str) -> bool:
    return _plain(text).lower().rstrip(".") == _BANNER


def _is_state(text: str) -> bool:
    return _plain(text).lower().rstrip(".") == _STATE


def _is_pivot(text: str) -> bool:
    return _plain(text).strip().rstrip(".)").lower() in ("v", "vs", "versus")


def _is_status(text: str) -> bool:
    bare = _plain(text).rstrip(".,; ").lower()
    if not bare or len(bare) > 70:
        return False
    words = [w.strip(".,;: ") for w in re.split(r"[\s/,—–]+", bare)
             if w.strip(".,;: ")]
    return bool(words) and all(w in _STATUS_WORDS or w in _STATUS_GLUE
                               for w in words)


def _is_origin(text: str) -> bool:
    return _plain(text).lower().lstrip("(").startswith(_ORIGIN_OPENERS)


def _date_in(text: str) -> str | None:
    for hit in _DATE.finditer(_plain(text)):
        if hit.group(1).split()[0].strip(".,").lower() in _MONTHS:
            return _norm(hit.group(1))
    return None


# --------------------------------------------------------------------------
# the fences — wva's section marks, and the dispatch
# --------------------------------------------------------------------------

def _rule_candidates(pm) -> list:
    """(top, x0, x1, line_or_None) for every rule this page sets in either
    fence measure — typed as a row of underscores or drawn as a thin rect."""
    out = []
    for line in pm.lines:
        flat = line.plain.strip()
        if flat and is_typed_rule(flat):
            out.append((line.top, line.x0, line.x1, line))
    for r in pm.h_rules:
        out.append((r.top, r.x0, r.x1, None))
    lo = min(_FENCE_SHORT[0], _FENCE_LONG[0])
    hi = max(_FENCE_SHORT[1], _FENCE_LONG[1])
    return [c for c in out if lo <= c[2] - c[1] <= hi]


def _doc_axis(pm) -> float | None:
    """The axis the document's rules share, or None when its page-1 rules
    do not agree on one. TWO RULES MAKE AN AXIS: a lone rule in a fence
    measure is a footnote separator, and it stands at the left text rail."""
    cands = _rule_candidates(pm)
    if len(cands) < 2:
        return None
    centres = sorted((x0 + x1) / 2 for _t, x0, x1, _l in cands)
    best, best_n = None, 0
    for c in centres:
        near = [d for d in centres if abs(d - c) <= _AXIS_TOLERANCE]
        if len(near) > best_n:
            best, best_n = sum(near) / len(near), len(near)
    return best if best_n >= 2 else None


def _fence_kind(x0: float, x1: float, axis: float) -> str | None:
    if abs((x0 + x1) / 2 - axis) > _FENCE_AXIS:
        return None                       # off the axis: not a section mark
    width = x1 - x0
    if _FENCE_SHORT[0] <= width <= _FENCE_SHORT[1]:
        return "short"
    if _FENCE_LONG[0] <= width <= _FENCE_LONG[1]:
        return "long"
    return None


def _fences(pm, axis: float) -> list:
    """[(top, kind, line_or_None)] in page order."""
    out = []
    text_edges = [(l.x0, l.x1, l.top) for l in pm.lines if l.plain.strip()]
    for top, x0, x1, line in _rule_candidates(pm):
        kind = _fence_kind(x0, x1, axis)
        if kind is None:
            continue
        if line is None and any(
                abs(tx0 - x0) <= 3 and abs(tx1 - x1) <= 3
                and -4 <= top - ttop <= 16 for tx0, tx1, ttop in text_edges):
            continue                      # an underline, not a fence
        out.append((top, kind, line))
    return sorted(out, key=lambda f: f[0])


def _single_lead(rows) -> float:
    """The type's own line spacing: the SMALLEST gap that this page sets
    more than once.

    Not the commonest — wva double-leads most of its headmatter, so the
    MODE is the double (30pt) on a record whose caption is airy, and a
    threshold built on it cannot see the blank line that fences the
    disposition (west_virginia_department_of_human_services set 'WRIT
    GRANTED' 29.9pt under its origin and the whole zone read as origin).
    A wrap is always set at the single, and the single is always printed
    at least twice."""
    tops = sorted({round(l.top, 1) for pg, _t, l in rows if pg == 1})
    gaps = Counter(round(b - a) for a, b in zip(tops, tops[1:])
                   if 8 <= b - a <= 60)
    twice = [g for g, n in gaps.items() if n >= 2]
    if twice:
        return float(min(twice))
    return float(min(gaps)) if gaps else 15.0


# --------------------------------------------------------------------------
# the clerk's stamp
# --------------------------------------------------------------------------

def _body_family(model) -> str:
    counts: Counter = Counter()
    for pm in model.pages:
        for line in pm.lines:
            for ch in line.chars:
                if (ch.get("text") or "").strip():
                    counts[_family(ch.get("fontname"))] += 1
    return counts.most_common(1)[0][0] if counts else ""


def _split_family(line, body: str):
    """(body_part, stamp_part) as two Lines, for a row pdfio read as one
    because the stamp shares its baseline. Either half may be None."""
    keep = [c for c in line.chars if _family(c.get("fontname")) == body]
    drop = [c for c in line.chars if _family(c.get("fontname")) != body]

    def rebuild(chars):
        inked = [c for c in chars if (c.get("text") or "").strip()]
        if not inked:
            return None
        return _dc_replace(line, chars=list(chars),
                           x0=min(c["x0"] for c in inked),
                           x1=max(c["x1"] for c in inked))
    return rebuild(keep), rebuild(drop)


class _Stamp:
    """The clerk's electronic FILED block: read, then recorded."""

    def __init__(self, model):
        self.body = _body_family(model)
        self.rows: list = []
        self.texts: list[str] = []

    def take(self, pm, line):
        """The line, with the stamp taken out of it — or None when the whole
        row is stamp."""
        fams = {_family(c.get("fontname")) for c in line.chars
                if (c.get("text") or "").strip()}
        if not fams or fams == {self.body}:
            return line
        if line.top >= pm.height * _STAMP_TOP_FRAC:
            return line
        if self.body not in fams:
            if line.x1 < pm.width * _STAMP_RIGHT_FRAC:
                return line               # a symbol glyph, not the stamp
            self.rows.append(line)
            self.texts.append(_plain(line.plain))
            return None
        # A MIXED ROW: the stamp shares the masthead's baseline and pdfio
        # read the two as one (randy_c._cain). Split at the typeface.
        body_part, stamp_part = _split_family(line, self.body)
        if stamp_part is not None and stamp_part.x1 >= pm.width * _STAMP_RIGHT_FRAC:
            self.rows.append(line)
            self.texts.append(_plain(stamp_part.plain))
            return body_part
        return line

    def record(self, crit: dict, dropped: list, consumed: set) -> None:
        if not self.rows:
            return
        text = _norm(" ".join(self.texts))
        value = _date_in(text)
        if value:
            crit.setdefault("decision_date", value)
        dropped.append(m.Dropped(
            text=text[:600],
            prov=m.Prov(self.rows[0].page, tuple(l.id for l in self.rows)),
            kind="stamp"))
        consumed.update(l.id for l in self.rows)


# --------------------------------------------------------------------------
# the walk's shared state
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom, style: str):
        self.model = model
        self.geom = geom
        self.pages = {pm.number: pm for pm in model.pages}
        self.body_x0 = geom.body_x0 if geom else 72.0
        self.body_size = geom.body_size if geom else 13.0
        self.items: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {"headmatter_style": style}

    def emit(self, line, role: str) -> None:
        pm = self.pages[line.page]
        align = line_alignment(line, pm.width, self.geom,
                               banner_center_min_size=self.body_size + 2.0)
        rel = 0.0
        if align == "L" and line.x0 > self.body_x0 + 12:
            rel = min(line.x0 - self.body_x0, pm.width * 0.6)
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role))
        self.consumed.add(line.id)

    def rule(self, page: int, line=None) -> None:
        """The fence renders where the page sets it.

        A TYPED fence is a row of its own and carries its own provenance. A
        DRAWN one has no row, so it borrows the provenance of the row above
        it — core merges a reader's items with its own leftovers BY
        POSITION, and an item with no line ids sorts to the end of the
        block (arthur_c's four drawn fences all landed under the
        appearances)."""
        if line is not None:
            prov = m.Prov(line.page, (line.id,))
            self.consumed.add(line.id)
        elif self.items:
            prov = self.items[-1].prov
        else:
            prov = m.Prov(page, ())
        self.items.append(m.Rule(prov=prov, typed=line is not None,
                                 span="full"))

    def result(self, anchor_ids=()) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": list(anchor_ids), "doc_type_final": None}


def _rows(model, stamp: _Stamp, finder: FurnitureFinder, pages: int) -> list:
    """The content rows of the first ``pages`` pages, in page order, with
    the page's furniture and the clerk's stamp taken out."""
    out: list = []
    for pm in model.pages[:pages]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue                  # core measures and records these
            kept = stamp.take(pm, line)
            if kept is None:
                continue
            out.append((pm.number, line.top, kept))
    out.sort(key=lambda r: (r[0], r[1]))
    return out


# --------------------------------------------------------------------------
# the dispatch
# --------------------------------------------------------------------------

@decider("headmatter.read", court="wva")
def read_headmatter_wva(model, geom, **_):
    """Read wva's headmatter by the landmark the paper prints, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    parser = BylineParser(get_profile("wva").byline)
    stamp = _Stamp(model)
    finder = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                             geom.body_size if geom else 13.0)

    axis = _doc_axis(page1)
    if axis is not None and len(_fences(page1, axis)) >= 2:
        return _read_sandwich(model, geom, axis, stamp, finder, parser)
    rows = _rows(model, stamp, finder, 1)
    if not rows:
        return NOTHING
    head = _plain(rows[0][2].plain)
    # A SEPARATE SLIP IS THE CLERK'S STAMP OVER THE WRITING'S OWN CAPTION.
    # Either the first content row states the case and its docket at the
    # body rail, or the writing starts straight away and this slip prints no
    # cover at all (state_of_west_virginia_v._richard_william_page).
    if stamp.rows and (_is_slip_caption(rows[0][2], geom)
                       or any(parser.parse(_plain(l.plain))
                              for _p, _t, l in rows[:3])):
        return _read_slip(model, geom, rows, stamp, parser)
    if _is_state(head) and any(_HANDDOWN_RECITAL in _plain(l.plain).lower()
                               for _p, _t, l in rows[:4]):
        return _read_handdown(model, geom, rows, stamp)
    return NOTHING


# --------------------------------------------------------------------------
# the term slip: the typed sandwich
# --------------------------------------------------------------------------

def _read_sandwich(model, geom, axis, stamp, finder, parser):
    ctx = _Ctx(model, geom, STYLE_SANDWICH)
    content = _rows(model, stamp, finder, _MAX_PAGES)
    gap = _single_lead(content) * _ZONE_GAP_FACTOR

    # THE STREAM the walk reads: content rows and DRAWN fences, merged by
    # where the page prints each. A typed fence is already a row.
    stream: list = []
    for page, top, line in content:
        stream.append((page, top, "line", line))
    typed_ids = set()
    for pm in model.pages[:_MAX_PAGES]:
        for top, kind, line in _fences(pm, axis):
            stream.append((pm.number, top, kind, line))
            if line is not None:
                typed_ids.add(line.id)
    stream = [s for s in stream
              if not (s[2] == "line" and s[3].id in typed_ids)]
    stream.sort(key=lambda s: (s[0], s[1]))

    dockets: list[str] = []
    caption: list[str] = []
    groups: list[list[str]] = [[]]
    origin: list[str] = []
    lower_dockets: list[str] = []
    judges: list[str] = []
    disposition: list[str] = []
    counsel: list[str] = []
    submitted: list[str] = []
    banner_rows: list[str] = []
    state = "masthead"
    last_origin_top: float | None = None
    prev_lower_docket = False
    signed = False

    for page, top, kind, line in stream:
        if kind in ("short", "long"):
            ctx.rule(page, line)
            if kind == "short":
                state = "docket" if state != "docket" else "caption"
            else:
                state = "tail" if state in ("origin", "disposition") \
                    else "origin"
            continue
        text = _plain(line.plain)
        if not text:
            continue
        # A BYLINE ENDS THE READER, always and everywhere.
        if parser.parse(text) is not None:
            signed = True
            break
        if state == "masthead":
            # The masthead is the court's nameplate and the term it sat in.
            if not (_is_banner(text) or _TERM.match(text)):
                return NOTHING            # not the paper this contract names
            if _is_banner(text):
                banner_rows.append(text)
            ctx.emit(line, "court")
            continue
        if state == "docket":
            if not _DOCKET_LIST.match(text):
                return NOTHING            # the sandwich holds a docket
            if groups[-1]:
                groups.append([])         # a new appeal, a new caption
            dockets.extend(_DOCKET_ANY.findall(text))
            ctx.emit(line, "docket")
            continue
        if state == "caption":
            # THE ORIGIN OPENS ITS OWN ZONE WHEREVER IT STANDS. Most
            # records fence it; in_re_p.f. sets it straight under the
            # caption with no opening rule, and a walk that waited for the
            # fence read three origin rows as parties.
            if _is_origin(text):
                state = "origin"
            else:
                caption.append(text)
                groups[-1].append(text)
                ctx.emit(line, "caption")
                continue
        if state == "origin":
            # THE DISPOSITION IS FENCED BY A BLANK LINE, not by its words:
            # 'ORIGINAL PROCEEDING IN PROHIBITION' and 'WRIT GRANTED' are
            # both all-caps, both short, and only the second is a
            # disposition. wva leaves one blank line between them.
            if last_origin_top is not None and top - last_origin_top >= gap:
                state = "disposition"
            else:
                last_origin_top = top
                if _JUDGE_ROW.match(text):
                    judges.append(text)
                elif (_LOWER_DOCKET.search(text) or _BARE_DOCKET.match(text)
                      or (prev_lower_docket and not _is_origin(text))):
                    lower_dockets.append(text)
                    prev_lower_docket = True
                    ctx.emit(line, "lower-court")
                    continue
                else:
                    origin.append(text)
                prev_lower_docket = False
                ctx.emit(line, "lower-court")
                continue
        if state == "disposition":
            disposition.append(text)
            ctx.emit(line, "disposition")
            continue
        # ---- the tail: the dates, the appearances, then the writing -----
        dated = _DATED.match(text)
        if dated and not counsel:
            label = dated.group(1).lower()
            value = _date_in(dated.group(2)) or _norm(dated.group(2))
            printed = f"{dated.group(1)}: {value}"
            if label == "filed":
                ctx.crit.setdefault("decision_date", value)
            elif printed not in submitted:
                submitted.append(printed)
            ctx.emit(line, "date")
            continue
        # A CONSOLIDATED record joins its appeals with a centred 'AND' and
        # opens the next sandwich with the next docket — which statoil sets
        # ABOVE its short fence rather than between a pair.
        if text.lower().rstrip(".") in _CONNECTIVE and not counsel:
            ctx.emit(line, "docket")
            continue
        if _DOCKET_LIST.match(text) and not counsel:
            if groups[-1]:
                groups.append([])
            dockets.extend(_DOCKET_ANY.findall(text))
            ctx.emit(line, "docket")
            state = "docket"
            continue
        # THE APPEARANCES, set in two columns.
        if geom and line.x1 >= geom.right_x1 - _MEASURE_SLACK:
            break
        counsel.append(text)
        ctx.emit(line, "counsel")

    if not dockets or not signed:
        return NOTHING
    if not caption and not origin:
        return NOTHING

    ctx.crit["docket_number"] = f"No. {dockets[0]}"
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = [f"No. {d}" for d in dockets[1:]]
    if banner_rows:
        ctx.crit["court"] = _norm(" ".join(banner_rows))
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, groups[0] or caption)
    if origin:
        ctx.crit["lower_court"] = _norm(" ".join(origin))
    if judges:
        ctx.crit["lower_court_judge"] = _norm(" ".join(judges))
    if lower_dockets:
        ctx.crit["lower_court_docket"] = lower_dockets
    if disposition:
        ctx.crit["disposition"] = _norm(" ".join(disposition))
    if submitted:
        ctx.crit["submitted"] = _norm(" ".join(submitted))
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    stamp.record(ctx.crit, ctx.dropped, ctx.consumed)
    return ctx.result()


def _name(ctx: _Ctx, rows: list) -> None:
    """The lead case's name, built from the party names either side of the
    pivot — never by joining the caption wholesale."""
    sides = _sides(rows)
    if sides:
        ctx.crit["parties"] = list(sides)
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
        return
    one = _sides(rows, one_sided=True)
    if one:
        ctx.crit["parties"] = [one]
        ctx.crit["case_name"] = one


def _sides(rows: list, one_sided: bool = False):
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in rows:
        flat = _plain(row)
        if not flat:
            continue
        if _is_pivot(flat):
            side, seen_pivot = right, True
            continue
        if _is_status(flat):
            continue
        side.append(flat)
    # A TRAILING COMMA IS THE CAPTION'S PUNCTUATION; a trailing PERIOD may
    # be the party's own ('COROTOMAN, INC.', 'IN RE F.B.'), so only the
    # comma comes off.
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the separate slip
# --------------------------------------------------------------------------

def _is_slip_caption(line, geom) -> bool:
    """The slip's own caption row: this court's docket, set at the body rail.

    'No. 23-558 - State of West Virginia v. Brendan W.' and 'State of West
    Virginia v. Tina Frymyer, No. 23-513' are the two forms; the docket is
    what identifies the row, never the name beside it."""
    rail = geom.body_x0 if geom else 72.0
    return (abs(line.x0 - rail) <= 6
            and _DOCKET_ANY.search(_plain(line.plain)) is not None)


def _read_slip(model, geom, rows, stamp, parser):
    """A concurrence or dissent released on its own: the clerk's stamp, the
    writing's own caption — the docket and the case, in at most two rows —
    then the writing.

    THE CAPTION ROW IS TAGGED `caption`, NOT `title`. wva reprints no full
    caption on a separate slip; this one row IS the cover, and what it
    carries is the parties, the pivot and the number. It was read as a
    `title` until 2026-08-19, which said the paper called itself
    'No. 24-305 - Credit Acceptance Corporation v. …' — and rendered it in
    the tint the court's own nameplate uses. Nothing on this paper names
    the paper, so no row here is a title."""
    ctx = _Ctx(model, geom, STYLE_SLIP)
    caption: list[str] = []
    signed = False
    prev: tuple = ()
    for page, top, line in rows[:4]:
        text = _plain(line.plain)
        if parser.parse(text) is not None:
            signed = True
            break                          # the writing starts here
        if not caption:
            # THE CAPTION ROW STANDS AT THE BODY RAIL. Nothing else on this
            # paper does. Measured on the 12 slips that print it: x0 is the
            # document's own rail (72.0 on eleven of them, 75.6 on
            # …the_honorable, which indents its cover 3.6pt), the type is the
            # body's own (13.0 on eleven, 12.0 on …honorable_james_young),
            # and the row always stands on page 1 above the byline
            # (credit_acceptance: top 108.9 against the byline's 143.8).
            if abs(line.x0 - ctx.body_x0) > 6:
                return NOTHING
        else:
            # A WRAP follows at the type's own leading and stays inside the
            # measure; it may hang indented (the_honorable sets its second
            # row 69pt in) or return to the rail (butler). Anything set
            # further down the page is the writing, not the caption.
            if page != prev[0] or top - prev[1] > \
                    (line.size or ctx.body_size) * _WRAP_GAP_FACTOR:
                break
            if not (ctx.body_x0 - 6 <= line.x0 <= ctx.body_x0 + 108):
                break
        caption.append(text)
        ctx.emit(line, "caption")
        prev = (page, top)
    if not (signed or caption):
        return NOTHING
    printed = _norm(" ".join(caption))
    # A COVER THE COURT DID NOT NUMBER IS NOT THIS PAPER'S COVER. Where the
    # byline names the writing the reader has its landmark; where it does not
    # (credit_acceptance signs 'Justice Wooton, dissenting:', which this
    # court's declared grammar does not read), the printed docket is the
    # only thing that says this paper is one of wva's.
    if caption and not signed and not _DOCKET_ANY.search(printed):
        return NOTHING
    if printed:
        hit = _DOCKET_ANY.search(printed)
        if hit:
            ctx.crit["docket_number"] = f"No. {hit.group(1)}"
        name = _DOCKET_ANY.sub("", printed).strip(" ,–—-")
        if name:
            ctx.crit["case_name"] = name
            ctx.crit["caption"] = [printed]
            # THE PIVOT IS PRINTED, so the two sides are read off it — the
            # slip states its case on one line and the court's own ' v. '
            # is the only thing that divides it.
            pivot = re.search(r"\s+vs?\.\s+", name)
            if pivot:
                ctx.crit["parties"] = [name[:pivot.start()].strip(" ,"),
                                       name[pivot.end():].strip(" ,")]
            else:
                ctx.crit["parties"] = [name]
    stamp.record(ctx.crit, ctx.dropped, ctx.consumed)
    if not ctx.items and not ctx.dropped:
        return NOTHING
    return ctx.result()


# --------------------------------------------------------------------------
# the clerk's hand-down
# --------------------------------------------------------------------------

def _read_handdown(model, geom, rows, stamp):
    """A per-curiam disposition the Court entered and the clerk attests.
    The reader stops at the bold centred heading the writing opens on."""
    ctx = _Ctx(model, geom, STYLE_HANDDOWN)
    caption: list[str] = []
    state = "court"
    for page, _top, line in rows:
        if page != 1:
            break
        text = _plain(line.plain)
        if state == "court":
            ctx.crit.setdefault("court", text)
            ctx.emit(line, "court")
            state = "recital"
            continue
        if state == "recital":
            ctx.emit(line, "summary")
            if _HANDDOWN_RECITAL in text.lower() or text.endswith(":"):
                value = _date_in(text)
                if value:
                    ctx.crit.setdefault("decision_date", value)
                if text.endswith(":"):
                    state = "caption"
            continue
        # THE PIVOT ROW CARRIES THE DOCKETS. wva sets 'v.)' and both
        # numbers — this court's and the tribunal's — on one row.
        if line.all_bold or line.x0 > ctx.body_x0 + 24:
            break                          # the disposition heading: the
            #                                writing opens on it
        numbers = _DOCKET_ANY.findall(text)
        if numbers:
            ctx.crit.setdefault("docket_number", f"No. {numbers[0]}")
            inner = re.search(r"\(([^)]*No\.[^)]*)\)", text)
            if inner:
                ctx.crit.setdefault("lower_court_docket",
                                    [_norm(inner.group(1))])
            ctx.emit(line, "docket")
            caption.append(text)
            continue
        caption.append(text)
        ctx.emit(line, "caption")
    if not caption:
        return NOTHING
    # A CLAIM MUST BE TOTAL: this paper carries no clerk's stamp in the
    # corpus, but a row taken out of the stream is recorded either way.
    stamp.record(ctx.crit, ctx.dropped, ctx.consumed)
    ctx.crit["caption"] = caption
    _name(ctx, [re.sub(r"\).*$", "", r) if _is_pivot(re.sub(r"\).*$", "", r))
                else r for r in caption])
    return ctx.result()
