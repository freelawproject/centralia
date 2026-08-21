"""Florida's District Courts of Appeal ('fladistctapp').

Five separate courts publish under this id, and over the 42-record corpus
they set FOUR mastheads on TWO papers. The First, Second and Sixth districts
share one contract and one walk; the Fourth sets a second paper that fences
nothing, and it has its own. Nothing here is dispatched on the district's
name.

THE CONTRACT — 'fenced sandwich' (41 of 42). A two-row masthead set a step
above the body, over zones each closed by a rule CENTRED ON THE PAGE AXIS in
one invariant measure. The rule is TYPED on 40 records and DRAWN on one, and
both are the same fence: the measure and the axis name it, never the glyph.

    SIXTH DISTRICT COURT OF APPEAL        the masthead, 18pt over a 14pt body
    STATE OF FLORIDA
    _____________________________         a fence ON THE AXIS…
    Case No. 6D2025-0031                  …around this court's docket…
    Lower Tribunal No. 2011-CF-019792     …and the tribunal's own number
    _____________________________
    ALISON TORRES,                        the caption: a party…
         Appellant,                       …its status…
    v.                                    …the pivot
    STATE OF FLORIDA,
         Appellee.
    _____________________________         the LAST fence closes the caption
    Appeal pursuant to Fla. R. App. P. …  …and below it stands the origin,
    Margaret O. Steinbeck, Judge.
    July 14, 2026                         the release date,
    ON JOINT STIPULATION FOR DISMISSAL    the paper's own name when it has
    PER CURIAM.                           one, and the writing starts

The five districts differ only in what they hang on that frame:

  * the SIXTH types its fence at 202.9pt and centres every row of the block;
  * the FIRST types the same fence at 188.4pt and sets its caption and its
    origin FLUSH LEFT at the body rail;
  * the SECOND DRAWS the 188.4pt rule, and fences only twice — its docket
    stands inside the caption's zone and its appearance roster below the
    origin, before the byline.

Nothing above is read by zone ORDINAL, which is why one walk takes all
three: above the last fence a row is the masthead (it is set above the body
size), this court's docket (a closed form, '6D2025-0031'), the tribunal's
number (its own label) or the caption (what is left, and the zone is closed
by a fence so it cannot run away). Below the last fence stands one block that
every district prints and `_read_below` reads for all of them: the origin,
the release date (a closed form), any labelled datum, any roster, and the
paper's own name (BOLD, CAPS, on the axis). That region ends at the first
byline, at the paper's own name — the row an unsigned order anchors its
writing on — or at the first paragraph that is none of those things.

THE SECOND CONTRACT — 'unfenced fourth' (1 of 42). The FOURTH district
fences nothing at all, and its landmark is the BRACKET: alone among the five
it sets its release date in square brackets on the page axis, and that row
is the hinge of the page.

    DISTRICT COURT OF APPEAL OF THE STATE OF FLORIDA   the masthead, 14pt
    FOURTH DISTRICT                                    over a 12pt body
    JEFFERY LEE CAIN,                    the caption opens at the first BOLD
         Appellant,                      row — the Fourth sets its party
    v.                                   names bold and nothing above is
    STATE OF FLORIDA,
         Appellee.
    No. 4D2025-3573                      the docket, in the same closed form
    [July 31, 2026]                      THE BRACKET — the hinge
    Appeal from the Circuit Court …      and below it the same block again
    Daniel Eisinger, Public Defender …
    ON CONFESSION OF ERROR
    PER CURIAM.

ONE EXEMPLAR. That contract rests on a single record, so it is gated on
three landmarks at once — the bracketed date on the axis, this court's
docket in its closed form, and a bold caption over a pivot. A record missing
any of them, or one that fences exactly ONCE, gets NOTHING: core's shared
walk places those rows unidentified, which is a smaller error than forcing
them through a contract they are not.

THE ENDMATTER. Florida closes its slips BELOW the writings with the
appearance roster and a standing finality stamp ('NOT FINAL UNTIL TIME
EXPIRES TO FILE MOTION FOR REHEARING / AND DISPOSITION THEREOF IF TIMELY
FILED'). That is not the opinion and core was reading it as the opinion's
last paragraphs. It is claimed as a SECOND region, walked BACKWARD from the
document's tail over paragraphs that are a notice, a fence, or an appearance
— an appearance being a paragraph set at the body RAIL (every body paragraph
of every district is indented from it) that carries a representation phrase.
The walk stops at the first paragraph that is none of those, and never
crosses above the last byline. The roster returns in the reader's
``attorneys`` channel, which the pipeline feeds to the `endmatter` section;
the stamp is recorded as `Dropped`.
"""

from __future__ import annotations

import re
from collections import Counter

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import PROFILES

# fladistctapp is already registered in courts/__init__.py; assigning into
# PROFILES replaces that entry instead of raising on a duplicate id.
FLADCA = CourtProfile(
    "fladistctapp", "Florida District Court of Appeal",
    # 'PER CURIAM.' / 'PRATT, J.' / 'GANNAM, J.' / 'WOZNIAK, J., concurs in
    # result only.' — an abbreviated title over an all-caps surname.
    byline=BylineGrammar(style="abbrev"),
)
PROFILES[FLADCA.court_id] = FLADCA

STYLE_FENCED = "fenced sandwich"
STYLE_UNFENCED = "unfenced fourth"

# ---- declared facts, measured over the corpus ----------------------------
# THE FENCE. 122 fences over the 41 fenced records, in two measures — 188.4pt
# (First and Second districts) and 202.8-203.2pt (Sixth) — and every one of
# them centred on the page axis to within 0.1pt.
_FENCE_MEASURE = (180.0, 212.0)
_FENCE_AXIS = 8.0
# THE PAGE AXIS. A centred row of any district lands within 9pt of it; the
# First district's flush-left origin statement is 31pt off and the Second's
# is 22pt. What settles the ones in between is the RAIL — a row standing on
# the body rail is set flush left however near the axis its midpoint falls
# ('Petition for Writ of Certiorari to the County Court for Sarasota
# County;' is 9pt off the axis and flush left at 72).
_AXIS_TOL = 12.0
# THE BODY RAIL. The Sixth sets its block at 72, the First at 108, the
# Second at 72 — and every one of them INDENTS the first line of every body
# paragraph (108 / 135.4 / 108). The rail is what tells an appearance from
# the prose above it.
_RAIL_TOL = 3.0
# THE MASTHEAD on the fenced paper is the only thing above the first fence
# and it is set above the body: 18pt over 13pt (First), 18pt over 14pt
# (Sixth), 16pt over 13pt (Second). The unfenced paper does not use this —
# the Fourth sets 'FOURTH DISTRICT' at the body's own 12pt, so its masthead
# is bounded by the caption's first BOLD row instead.
_MASTHEAD_STEP = 1.5
# HOW A PARAGRAPH ENDS. Florida sets its blocks single-spaced inside a
# paragraph and double-spaced between: 16.1 against 32.2 at 14pt, 15.6
# against 31.3 at 13pt.
_PARA_GAP = 1.6
# THE FOOTNOTE SEPARATOR: a 144pt rule at the body rail, 162pt off the axis.
# Same measure logic as everywhere — the axis takes it, not the width.
_FOOTNOTE_RULE_MAX = 0.5

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# A star row is the Fourth district's separator; the Sixth types none.
_STAR_ROW = re.compile(r"^[*•\s]+$")
# THIS COURT'S OWN DOCKET, in the two forms the districts print it:
# 'Case No. 6D2025-0031' and 'No. 1D2026-0018'.
_DOCKET = re.compile(r"^(?:Case\s+)?Nos?\.\s*(\d?D\d{4}-\d{2,6})\.?$", re.I)
# THE TRIBUNAL'S OWN NUMBER, under its own label.
_LOWER = re.compile(r"^Lower\s+Tribunal\s+Nos?\.\s*(.+?)\.?$", re.I)
_LOWER_SPLIT = re.compile(r",\s*(?:and\s+)?|\s+and\s+")
# 'July 14, 2026' bare (First / Second / Sixth) or '[July 31, 2026]' — the
# FOURTH district is the only one that brackets its release date, and the
# bracket is what names its paper.
_DATE = re.compile(r"^\[?([A-Z][a-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})\.?\]?$")
_BRACKETED = re.compile(r"^\[.+\]$")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# WHO TRIED IT, as the origin states it: one personal name and the singular
# title. The plural ('…, and Amy P. Brodersen, Judges.') names a bench and
# is left inside the origin statement rather than mis-read as one judge.
_JUDGE = re.compile(r"^([A-Z][^,]*(?:,\s*(?:Jr|Sr|II|III|IV)\.?)?),\s*Judge\.$")
# A LABELLED DATUM the origin block carries beside the appeal route ('Date of
# Accident: February 19, 2024.' on a workers' compensation appeal).
_LABELLED = re.compile(r"^[A-Z][A-Za-z .]{2,30}:\s*\S")

# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellee", "petitioner", "respondent", "complainant",
    "plaintiff", "defendant", "intervenor", "movant", "amicus", "amici",
    "applicant", "claimant", "cross-appellant", "cross-appellee",
)
# THE COURT'S STANDING STAMPS. Each district words its finality notice
# differently and every one of them is boilerplate the court prints on every
# slip — a closed vocabulary of this court's own furniture.
_NOTICE_CUES = (
    "not final until time expires",
    "disposition thereof if timely filed",
    "not final until disposition",
    "opinion subject to revision prior to official publication",
)
# REPRESENTATION is a closed role vocabulary too — the same family core
# recognizes, restricted to the phrases Florida's rosters actually end on.
_APPEARANCE_MARKS = (
    "pro se", "no appearance for", "for appell", "for the appell",
    "for petition", "for the petition", "for respond", "for the respond",
    "for plaintiff", "for the plaintiff", "for defendant",
    "for the defendant", "counsel for", "attorney for", "attorneys for",
    "on brief", "on the brief",
)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower().replace("(s)", "s")
    if not bare:
        return False
    words = [w.strip(",.;: ") for w in bare.split()]
    return all(w in _STATUS_WORDS or w.rstrip("s") in _STATUS_WORDS
               or w in ("and", "the", "cross", "etc")
               for w in words if w)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in ("v", "vs")


def _date_value(text: str) -> str | None:
    """'July 14, 2026' as the page set it, or None. The month is a closed
    vocabulary; the brackets the Fourth district types are furniture."""
    mm = _DATE.match(_norm(text))
    if mm is None or mm.group(1).lower().rstrip(".") not in _MONTHS:
        return None
    return f"{mm.group(1)} {mm.group(2)}, {mm.group(3)}"


def _is_notice(text: str) -> bool:
    low = _norm(text).lower()
    return any(cue in low for cue in _NOTICE_CUES)


def _is_appearance(text: str) -> bool:
    low = _norm(text).lower()
    return any(mark in low for mark in _APPEARANCE_MARKS)


# --------------------------------------------------------------------------
# the fence — this court's section mark, and the dispatch
# --------------------------------------------------------------------------

def _underlines(pm) -> set:
    """The tops of rules the page drew as UNDERLINES rather than fences.

    A rule whose ends coincide with the row just above it underscores that
    row; the Sixth district rules its 'ON JOINT STIPULATION…' title that
    way, at 363pt on the axis."""
    out = set()
    for r in pm.h_rules:
        for line in pm.lines:
            if not (0 < r.top - line.bottom < 14):
                continue
            if abs(line.x0 - r.x0) <= 3 and abs(line.x1 - r.x1) <= 3:
                out.add(round(r.top, 1))
    return out


def _on_axis(x0: float, x1: float, page_width: float,
             tol: float = _FENCE_AXIS) -> bool:
    return abs((x0 + x1) / 2 - page_width / 2) <= tol


def _is_fence_row(line, page_width: float) -> bool:
    """A typed underscore row IS the fence, in the measure and on the axis."""
    if not _TYPED_RULE.match(_norm(line.plain)):
        return False
    width = line.x1 - line.x0
    return (_FENCE_MEASURE[0] <= width <= _FENCE_MEASURE[1]
            and _on_axis(line.x0, line.x1, page_width))


def _drawn_fences(pm) -> list:
    """The tops of the fences this page DRAWS, in page order."""
    skip = _underlines(pm)
    out = []
    for r in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if not _on_axis(r.x0, r.x1, pm.width):
            continue
        if round(r.top, 1) in skip:
            continue
        out.append(r.top)
    return sorted(out)


def _footnote_top(pm, rail: float) -> float | None:
    """Where this page rules off its footnotes, or None. The separator is at
    the body RAIL and far off the axis; the fence is on the axis. Width
    alone would take both."""
    tops = [r.top for r in pm.h_rules
            if abs(r.x0 - rail) <= 6.0
            and r.width <= _FOOTNOTE_RULE_MAX * pm.width
            and not _on_axis(r.x0, r.x1, pm.width, 40.0)]
    return min(tops) if tops else None


# --------------------------------------------------------------------------
# the document's own measurements
# --------------------------------------------------------------------------

def _facts(model, geom) -> tuple[float, float]:
    """(rail, body size). `measure` returns None on a one-page per curiam —
    too few full-measure rows to be sure — and these records are mostly one
    page, so the rail and the size are taken from the document's own modal
    row when it does."""
    if geom is not None and geom.body_size:
        return geom.body_x0, geom.body_size
    xs: Counter = Counter()
    ss: Counter = Counter()
    for pm in model.pages:
        for line in pm.lines:
            text = _norm(line.plain)
            if not text or _TYPED_RULE.match(text):
                continue
            xs[round(line.x0)] += 1
            ss[round(line.size or 0.0, 1)] += 1
    rail = float(xs.most_common(1)[0][0]) if xs else 72.0
    size = float(ss.most_common(1)[0][0]) if ss else 13.0
    return rail, size


def _is_separator(line) -> bool:
    text = _norm(line.plain)
    return bool(_TYPED_RULE.match(text) or _STAR_ROW.match(text))


def _paragraphs(rows: list, size: float) -> list:
    """Rows grouped the way the page sets them: single-spaced inside a
    paragraph, double-spaced between — and A SECTION MARK IS ITS OWN
    PARAGRAPH however tightly the page sets it. The First district leaves
    only a single lead between its finality stamp and the rule under it, so
    a purely metric grouping folded the court's fence into the notice's own
    text."""
    out: list[list] = []
    prev = None
    for line in rows:
        # SAME-ROW PIECES ARE ONE ROW. The Fourth district's '* * *' comes
        # back as three lines at one top, and a mark that splits paragraphs
        # would otherwise make three of them.
        same_row = prev is not None and abs(line.top - prev.top) <= 1.0
        if (prev is None or line.page != prev.page
                or line.top - prev.top > _PARA_GAP * size
                or (not same_row
                    and (_is_separator(line) or _is_separator(prev)))):
            out.append([])
        out[-1].append(line)
        prev = line
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom, rail, size):
        self.model = model
        self.geom = geom
        self.rail = rail
        self.size = size
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.attorneys: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def at_rail(self, line) -> bool:
        return abs(line.x0 - self.rail) <= _RAIL_TOL

    def centred(self, line) -> bool:
        """On the axis AND off the rail. A row the page set flush left is
        flush left even where its measure happens to straddle the axis."""
        return (not self.at_rail(line)
                and _on_axis(line.x0, line.x1, self.pages[line.page].width,
                             _AXIS_TOL))

    def _row(self, line, role: str):
        return m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align("C" if self.centred(line) else "L"),
            x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), italic=bool(line.all_emphasized),
            role=role)

    def emit(self, line, role: str):
        self.items.append(self._row(line, role))
        self.consumed.add(line.id)

    def endmatter(self, line, role: str):
        """One printed row of the trailing roster — the same kind of matter
        as the headmatter, rebuilt the same way, in the page's own order."""
        self.attorneys.append(self._row(line, role))
        self.consumed.add(line.id)

    def rule(self, page: int, line=None):
        prov = m.Prov(page, (line.id,) if line is not None else ())
        self.items.append(m.Rule(prov=prov, typed=line is not None,
                                 span="center"))
        if line is not None:
            self.consumed.add(line.id)

    def drop(self, lines, kind: str):
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(l.plain for l in lines))[:1200],
            prov=m.Prov(lines[0].page, tuple(l.id for l in lines)),
            kind=kind))
        self.consumed.update(l.id for l in lines)

    def result(self, anchor_ids=()):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys, "dropped": self.dropped,
                "consumed": self.consumed, "anchor_ids": list(anchor_ids),
                "doc_type_final": None}


@decider("headmatter.read", court="fladistctapp")
def read_headmatter_fladistctapp(model, geom, **_):
    """Read the fenced sandwich and its trailing roster, or NOTHING."""
    if not model.pages:
        return NOTHING
    rail, size = _facts(model, geom)
    finder = FurnitureFinder(model, rail, size)
    page1 = model.pages[0]
    parser = BylineParser(FLADCA.byline)

    rows = [l for l in page1.lines
            if l.plain.strip() and not finder.kind(page1, l)]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not rows:
        return NOTHING

    # THE FENCE IS THE DISPATCH. A record fencing fewer than twice above its
    # first byline is not this paper (the Fourth district fences not at all).
    byline_top = next((l.top for l in rows
                       if parser.parse(_norm(l.plain)) is not None), None)
    cut = byline_top if byline_top is not None else 1e9
    fences = [(l.top, l) for l in rows
              if _is_fence_row(l, page1.width) and l.top < cut]
    fences += [(t, None) for t in _drawn_fences(page1) if t < cut]
    fences.sort(key=lambda f: f[0])
    ctx = _Ctx(model, geom, rail, size)
    if len(fences) >= 2:
        read = _read_fenced(ctx, page1, rows, fences, cut, parser, size)
    elif not fences:
        read = _read_unfenced(ctx, rows, cut, size)
    else:
        read = NOTHING            # one fence is neither paper
    if read is NOTHING:
        return NOTHING
    _read_endmatter(ctx, finder, parser)
    return ctx.result(ctx.crit.pop("_anchors", []))


def _read_fenced(ctx: _Ctx, page1, rows, fences, cut, parser, size):
    last_fence = fences[-1][0]
    fence_ids = {l.id for _t, l in fences if l is not None}
    anchors: list[int] = []

    # ---- above the last fence: masthead, dockets, caption ---------------
    stream: list = [(l.top, l) for l in rows if l.top <= last_fence]
    stream += [(t, None) for t, l in fences if l is None]
    stream.sort(key=lambda s: (s[0], 0 if s[1] is None else 1))

    masthead: list[str] = []
    caption: list[str] = []
    dockets: list[str] = []
    lower_nos: list[str] = []
    seen_fence = False
    for _top, line in stream:
        if line is None:                       # a DRAWN fence
            ctx.rule(page1.number)
            seen_fence = True
            continue
        if line.id in fence_ids:
            ctx.rule(page1.number, line)
            seen_fence = True
            continue
        text = _norm(line.plain)
        if not seen_fence:
            # THE MASTHEAD is what stands above the first fence, and it is
            # the only thing on the page set above the body size.
            if (line.size or 0.0) < size + _MASTHEAD_STEP:
                return NOTHING
            masthead.append(text)
            ctx.emit(line, "court")
            continue
        mm = _DOCKET.match(text)
        if mm:
            dockets.append(text.rstrip("."))
            ctx.emit(line, "docket")
            continue
        mm = _LOWER.match(text)
        if mm:
            lower_nos.extend(p for p in _LOWER_SPLIT.split(mm.group(1)) if p)
            ctx.emit(line, "lower-court")
            continue
        caption.append(text)
        ctx.emit(line, "caption")
    # THE BAR FOR CLAIMING: the fences must have held this court's docket
    # and a caption with a pivot in it.
    if not masthead or not dockets:
        return NOTHING
    if not any(_is_pivot(t) for t in caption):
        return NOTHING

    # ---- below the last fence: origin, date, the paper's own name -------
    _read_below(ctx, [l for l in rows if last_fence < l.top < cut], size,
                anchors)

    ctx.crit["headmatter_style"] = STYLE_FENCED
    ctx.crit["court"] = " ".join(masthead)
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    if lower_nos:
        ctx.crit["lower_court_docket"] = lower_nos
    ctx.crit["caption"] = caption
    _name(ctx, caption)
    if anchors:
        ctx.crit["_anchors"] = anchors
    return True


def _read_below(ctx: _Ctx, below: list, size: float, anchors: list) -> None:
    """What every district prints under its caption: the origin, the release
    date, any labelled datum, any roster, and the paper's own name.

    THE REGION ENDS AT THE WRITING — at the first byline (the caller's
    `cut`), at the paper's own name (the row an unsigned order anchors on),
    or at the first paragraph that is none of the things this block holds.
    Five is more than any district prints; the cap is a stop, not a reading.
    """
    origin_seen = False
    for para in _paragraphs(below, size)[:5]:
        text = _norm(" ".join(l.plain for l in para))
        if len(para) == 1 and _date_value(text) is not None:
            ctx.crit.setdefault("decision_date", _date_value(text))
            ctx.emit(para[0], "date")
            continue
        if (all(l.all_bold and ctx.centred(l) for l in para)
                and text == text.upper()):
            # the paper's own name — and the only thing an unsigned order
            # has to anchor its writing on.
            ctx.crit.setdefault("title", text)
            for line in para:
                ctx.emit(line, "title")
                anchors.append(line.id)
            break
        if _is_appearance(text) and origin_seen:
            for line in para:
                ctx.emit(line, "counsel")
            ctx.crit["attorneys"] = _norm(
                f"{ctx.crit.get('attorneys', '')} {text}")
            continue
        if origin_seen and _LABELLED.match(text):
            for line in para:
                ctx.emit(line, "case-info")
            continue
        if origin_seen:
            break                              # not this block any more
        # THE ORIGIN — the route the appeal took and who tried it.
        origin_seen = True
        judge = _JUDGE.match(_norm(para[-1].plain)) if len(para) > 1 else None
        if judge:
            ctx.crit["lower_court_judge"] = judge.group(1)
            ctx.crit["lower_court"] = _norm(
                " ".join(l.plain for l in para[:-1]))
        else:
            ctx.crit["lower_court"] = text
        for line in para:
            ctx.emit(line, "lower-court")


def _read_unfenced(ctx: _Ctx, rows: list, cut: float, size: float):
    """The FOURTH district's paper, which fences nothing.

    Its landmark is the BRACKET. Alone among the five districts the Fourth
    sets its release date in square brackets on the page axis, and that row
    is the hinge of the page: the masthead, the caption and the docket stand
    above it, the origin, the roster and the paper's own name below. The
    masthead ends where the caption starts, and the caption starts at the
    first BOLD row — the Fourth sets its party names bold and nothing above
    them is.

    ONE EXEMPLAR. This contract is drawn from a single record in the corpus
    (jeffery_lee_cain), so it is gated on three landmarks at once — the
    bracketed date, this court's docket in its closed form, and a bold
    caption over a pivot. A record missing any of them gets NOTHING.
    """
    at = next((k for k, l in enumerate(rows)
               if l.top < cut and ctx.centred(l)
               and _BRACKETED.match(_norm(l.plain))
               and _date_value(_norm(l.plain)) is not None), None)
    if at is None:
        return NOTHING

    masthead: list[str] = []
    caption: list[str] = []
    dockets: list[str] = []
    seen_party = False
    for line in rows[:at]:
        text = _norm(line.plain)
        if not seen_party and line.all_bold:
            seen_party = True
        if not seen_party:
            masthead.append(text)
            ctx.emit(line, "court")
            continue
        if _DOCKET.match(text):
            dockets.append(text.rstrip("."))
            ctx.emit(line, "docket")
            continue
        mm = _LOWER.match(text)
        if mm:
            ctx.crit.setdefault("lower_court_docket", []).extend(
                p for p in _LOWER_SPLIT.split(mm.group(1)) if p)
            ctx.emit(line, "lower-court")
            continue
        caption.append(text)
        ctx.emit(line, "caption")
    if not masthead or not dockets or not any(_is_pivot(t) for t in caption):
        return NOTHING

    date_line = rows[at]
    ctx.crit["decision_date"] = _date_value(_norm(date_line.plain))
    ctx.emit(date_line, "date")

    anchors: list[int] = []
    _read_below(ctx, [l for l in rows[at + 1:] if l.top < cut], size, anchors)

    ctx.crit["headmatter_style"] = STYLE_UNFENCED
    ctx.crit["court"] = " ".join(masthead)
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    _name(ctx, caption)
    if anchors:
        ctx.crit["_anchors"] = anchors
    return True


def _name(ctx: _Ctx, rows: list) -> None:
    """The case's name, built from the party names either side of the pivot
    — never by joining the caption wholesale."""
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
    left: list = []
    right: list = []
    side = left
    seen_pivot = False
    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        if _is_pivot(flat):
            side = right
            seen_pivot = True
            continue
        if _is_status(flat):
            continue
        side.append(flat)
    if one_sided:
        return _norm(" ".join(left + right)).rstrip(", ") or None
    if not (left and right and seen_pivot):
        return None
    return (_norm(" ".join(left)).rstrip(", "),
            _norm(" ".join(right)).rstrip(", "))


# --------------------------------------------------------------------------
# the endmatter — the roster and the stamp the court prints BELOW its writings
# --------------------------------------------------------------------------

def _tail_rows(ctx: _Ctx, finder) -> list:
    """Every content row of the document, minus furniture and minus each
    page's footnote zone. The Sixth district rules its notes off at the body
    rail, and a note running to the foot of the last page would otherwise
    stand between the roster and the end of the document."""
    out: list = []
    for pm in ctx.model.pages:
        floor = _footnote_top(pm, ctx.rail)
        for line in pm.lines:
            if not line.plain.strip() or finder.kind(pm, line):
                continue
            if floor is not None and line.top >= floor:
                continue
            out.append(line)
    out.sort(key=lambda l: (l.page, l.top, l.x0))
    return out


def _read_endmatter(ctx: _Ctx, finder, parser) -> None:
    all_rows = _tail_rows(ctx, finder)
    # WHERE THE WALK MAY NOT GO. Below the last BYLINE, because the Second
    # district prints its roster INSIDE the headmatter above the signature
    # and a backward walk that crossed the byline would take a writing
    # apart; and below the last row the HEADMATTER claimed, because an
    # unsigned order (kings_roofing) has no byline at all and its writing
    # opens on the paper's own name.
    floor = (0, -1.0)
    for line in all_rows:
        at = (line.page, line.top)
        if at <= floor:
            continue
        if (line.id in ctx.consumed
                or parser.parse(_norm(line.plain)) is not None):
            floor = at
    if floor == (0, -1.0):
        return
    rows = [l for l in all_rows
            if l.id not in ctx.consumed and (l.page, l.top) > floor]
    if not rows:
        return
    paras = _paragraphs(rows, ctx.size)

    kinds: list[str] = []
    for para in paras:
        text = _norm(" ".join(l.plain for l in para))
        if _is_notice(text):
            kinds.append("notice")
        elif all(_is_separator(l) for l in para):
            kinds.append("rule")
        elif _is_appearance(text) and ctx.at_rail(para[0]):
            kinds.append("counsel")
        else:
            kinds.append("")
    at = len(paras)
    while at and kinds[at - 1]:
        at -= 1
    claim = list(zip(paras[at:], kinds[at:]))
    # A RUN OF RULES ALONE IS NOT AN ENDMATTER. Something has to be in it.
    if not any(k in ("notice", "counsel") for _p, k in claim):
        return
    for para, kind in claim:
        if kind == "counsel":
            for line in para:
                ctx.endmatter(line, "counsel")
            ctx.crit["attorneys"] = _norm(
                f"{ctx.crit.get('attorneys', '')} "
                + _norm(" ".join(l.plain for l in para)))
        else:
            ctx.drop(para, kind)
