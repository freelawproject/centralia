"""Supreme Court of Indiana ('ind').

THE CONTRACT — one paper, printed 50 times out of 50: the RULED COVER.

Indiana engraves its name at the head of every slip and then FENCES the
cover with full-measure rules drawn at the body rail. Everything above the
first fence is the court and the caption; the band under it states what the
case IS and where it came from; the band under the second fence states who
wrote the opinion and who joined. The writing opens on the byline at the
rail below:

    IN THE                                    12pt, on the page axis
    Indiana Supreme Court                     30pt — the masthead
    Supreme Court Case No. 25S-PL-141         12pt — THIS court's docket
    Indiana Land Trust #3082 and Omar and     16pt — a party…
    Haitham Abuzir as Trustees
        Appellants (plaintiffs below)         12pt italic — its status
    –v–                                       13pt — the pivot
    Hammond Redevelopment Commission et al.   16pt — the other party
        Appellees (defendants below)
    ─────────────────────────────────────     A FENCE: 395.5pt at the rail
    Argued: September 4, 2025 | Decided: …    11pt — the label grid
    Appeal from the Lake Superior Court,      …the origin…
    No. 45D11-2401-PL-1                       …its number…
    The Honorable Bruce D. Parent, Judge      …and who tried it
    On Petition to Transfer from the Indiana Court of Appeals,
    No. 24A-PL-1284                           …the route here
    ─────────────────────────────────────     the second fence
    Opinion by Justice Goff                   11pt BOLD — the announced author
    Chief Justice Rush and Justices Massa, Slaughter, and Molter concur.
    Goff, Justice.                            …and the writing starts

THE DISPATCH is a single question about page 1: does the court engrave its
name there — one row set at 30pt over a 12pt body, on the page axis, in the
top half — and does the cover draw at least one full-measure fence at the
body rail on page 1 or page 2? Over the 50-record corpus that test agrees
with the paper on every one; a record that answers no is not this cover and
gets NOTHING.

THE BANDS ARE NOT COUNTED — THE LANDMARKS NAME THEM. The fence between the
caption and the case-info band is SUPPRESSED where a page turn already does
its work (baldwin's 20-party caption fills page 1 and the case-info band
opens page 2 with no fence above it), so a reader that numbered the bands
would read that record's case info as its author band. Each band is entered
on its own landmark instead:

* the CASE-INFO band opens on the court's own date grid ('Argued: … |
  Decided: …', 'Decided: …') or on an ORIGIN LEADER — a closed vocabulary
  of the ways this court states where a case came from, never a court NAME;
* the AUTHOR band opens on the authorship leader ('Opinion by …', 'Per
  Curiam Opinion'), which is also the only BOLD row on the cover;
* everything before either is the caption.

Inside the case-info band the court sets 17.0pt between the rows of ONE
statement and 23.0pt between statements, so a row that names nothing itself
('Indiana's Rules of Procedure for Original Actions') is read as the wrap it
is rather than as a new fact.

THE TRAILING ROSTER is claimed as a second region. Indiana prints its
appearances BELOW the writings, and it is the only place in the document
where 10pt type stands at the body rail: a heading at 10.0pt naming the
party represented, over entries at 11.0pt, against a 12.0pt body. Two
records set that roster in TWO COLUMNS (waggoner's 56-party medical-review
caption, yerano), and the columns are read as columns — each page's roster
is emitted left column then right, by the x0 the rows themselves cluster on,
never by the order the rows happen to sit in down the page. The roster is
rendered as endmatter, one row per printed row, every row tagged.

WHY IT IS CLAIMED HERE AND NOT BY ``counsel_after_writings``. That path
harvests the last 12 assembled blocks of the last writing and needs its
marks in the closing span of an entry; Indiana's rosters run to 48 rows
(edgerock, 10 headings), the heading and the names are separate blocks, and
five records set the roster BEFORE a separate writing (baldwin's roster
closes the majority slip on pages 15-16 and Justice Goff's opinion follows
on page 17), which is not a trailing window at all. Claimed here, the whole
roster is subtracted before assembly and cannot be mistaken for the closing
paragraph of an opinion.

WHAT THE READER DOES NOT TOUCH. The per-page footer ('Indiana Supreme Court
| Case No. 25S-PL-141 | February 24, 2026' over 'Page 3 of 11') is core's
furniture. The pre-certification notice one record prints above the masthead
('Pursuant to Indiana Appellate Rule 65(E), …') is recorded as a Dropped
notice. Footnotes are core's: the reader stops at the top of the separator
Indiana rules at 144.0pt, which is the only measure it ever rules one at.

FIXED 2026-08-21 — THE FENCE IS NO LONGER READ AS A SEPARATOR. Core's
footnote chain used to take a cover FENCE for a footnote separator on 15 of
the 50 records: the fence is full measure at the body rail with 11pt
case-info type under it, which is 'a rule over smaller text', and it escaped
on the other 35 only because the fence there falls above core's caption-page
floor. Those records lost the whole lower cover — the argued/decided row,
the appeal-from lines, the 'Opinion by' announcement, the bench line — into
a phantom '?' footnote before this reader ran. The fix is the declared
measure this docstring always asked for: the profile now carries
`FootnoteConfig(sep_measure=(140.0, 148.0))`, and core vetoes any rule
outside a declared measure in every rule-based step of the chain. Measured
over all 50 records: phantom notes 15 -> 0, claimed headmatter rows 715 ->
839, and the writing footnotes are UNCHANGED at 154 — no real note was won
or lost by the veto.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..resolve.bylines import BylineParser
from ..resolve.footnotes import FootnoteZones, line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, Trace, decider

STYLE_COVER = "ruled cover"

# ---- ind's declared facts (measured over all 50 records) -----------------
# THE MASTHEAD: 'Indiana Supreme Court' at 30.0pt on every cover, over a
# 12.0pt body. Nothing else in the corpus is set above 18pt.
_MASTHEAD_SIZE = 24.0
# THE FENCE: 104 rules over the corpus at 395.5-396.2pt, every one starting
# at the body rail (x0 = 108.0). The court's OTHER rule is the footnote
# separator, 129 of them at 144.0pt — the two measures do not overlap and
# nothing between them is ever drawn.
_FENCE_MEASURE = (380.0, 410.0)
_FENCE_RAIL = 3.0
_SEP_MEASURE = (140.0, 148.0)
# HOW FAR THE COVER MAY RUN. baldwin's 20-party caption fills page 1 and
# closes on page 2; nothing in the corpus needs a third.
_MAX_PAGES = 2
# THE RAIL. Every cover row is centred and none starts left of x0 = 114.9;
# the byline that ends the reader sits at the rail (108.0) like the body.
_RAIL = 2.0
# PARTY NAMES are set at 16.0pt, their statuses at 11-12pt, the pivot at
# 13.0pt. One step above the body is the whole test.
_PARTY_SIZE = 15.0
# THE CASE-INFO BAND's own leading: 17.0pt inside one statement, 23.0pt
# between statements (measured on all 50 covers; elzey's stacked trial-court
# numbers run tighter still at 14.9pt).
_INFO_WRAP = 20.0
# THE TRAILING ROSTER: headings at 10.0pt, entries at 11.0pt, against a
# 12.0pt body. Two records set it in two columns, whose rails stand 198-216pt
# apart; a wrapped heading stays inside 6pt of its own rail.
_ROSTER_HEAD = 10.0
_ROSTER_ENTRY = 11.0
_ROSTER_SIZE_TOL = 0.25
_ROSTER_COLUMN = 6.0
# The notice one record prints ABOVE the masthead, at 10.0pt.
_NOTICE_MAX_SIZE = 10.5

# THE MASTHEAD'S OWN ROWS. Read letters-only: two records letterspace the
# first row ('I N   T H E'), and one letterspaces it with non-breaking
# spaces, so no test on the printed string can be shared between them.
_MASTHEAD_TOP = "INTHE"
_MASTHEAD_NAME = "INDIANASUPREMECOURT"
# THIS COURT'S OWN DOCKET, announced by its printed leader: 'Supreme Court
# Case No. 25S-PL-141'. The number the court BELOW gave the case is printed
# in the case-info band and is never read from here.
_DOCKET_LEAD = re.compile(r"^supreme\s+court\s+case\s+nos?\.\s*", re.I)
# THE DATE GRID. Indiana labels both dates on one row and separates them
# with a pipe; a record with no argument prints only the second.
_DATE_LABEL = re.compile(
    r"\b(argued|reargued|submitted|decided)\s*:\s*"
    r"([A-Z][a-z]+\.?\s+\d{1,2},\s*\d{4})", re.I)
# THE ORIGIN LEADERS: a closed vocabulary of the ways this court states
# where a case came from, and the proceedings it opens in its own right.
# Never a court NAME.
_ORIGIN_LEADERS = (
    "appeal from", "direct appeal from", "on appeal from",
    "on petition to transfer from", "on petition for review from",
    "on transfer from", "petition for writ of mandamus",
    "petition for writ of prohibition", "original action",
    "certified question from", "on certified question from",
    "review of", "on review from",
)
# WHO TRIED IT, as the origin says. 'The Honorable X, Judge' below, and the
# 'Hon. X, … Special Masters' a judicial-discipline record appoints.
_JUDGE_LEAD = re.compile(r"^(the\s+honorable|hon\.)\b", re.I)
_MASTERS = re.compile(r"^(special\s+masters?|masters?)\.?$", re.I)
# THE NUMBER THE COURT BELOW GAVE THE CASE, in every form ind prints:
# '45D11-2401-PL-1', '24A-PL-1284', '21T-TA-44', '02D06-2111-MR-20'.
_LOWER_DOCKET = re.compile(
    r"\b\d{1,3}[A-Z]{0,2}\d{0,2}[-‑]\d{2,4}[-‑][A-Z]{1,3}[-‑]\d{1,6}\b"
    r"|\b\d{2}[A-Z][-‑][A-Z]{2}[-‑]\d{1,6}\b")
_NUMBER_LEAD = re.compile(r"^(nos?\.|trial\s+court\s+case\s+nos?\.)", re.I)
# THE AUTHORSHIP LEADER — how the cover announces who wrote it. Both forms
# are set BOLD, and they are the only bold rows on any cover.
_AUTHOR_LEAD = re.compile(r"^(opinion\s+by\b|per\s+curiam\s+opinion\b)", re.I)
# BENCH TITLES, a closed role vocabulary, longest first.
_BENCH = ("Chief Justice", "Justices", "Justice")
# THE PIVOT the caption turns on: '–v–' as printed, and the plain forms.
_PIVOT = re.compile(r"^[-–—]*\s*vs?\.?\s*[-–—]*$", re.I)
# A JOINDER between two party groups on the same side of the pivot.
_JOINER = re.compile(r"^and$", re.I)
# The roster's own heading: a representation LABEL, which is a closed
# vocabulary. Read letters-only — the roster's font kerns its capitals apart
# ('ATTORNEY FOR A PP E L L AN T') on 9 records.
_ROSTER_HEAD_WORD = ("ATTORNEY", "ATTORNEYS")


def _norm(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def _letters(text: str) -> str:
    return "".join(c for c in text if c.isalpha()).upper()


# --------------------------------------------------------------------------
# the page's own marks
# --------------------------------------------------------------------------

def _fences(pm, body_x0: float) -> list[float]:
    """The tops of the cover fences this page draws, in page order."""
    return sorted(r.top for r in pm.h_rules
                  if _FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]
                  and abs(r.x0 - body_x0) <= _FENCE_RAIL)


def _footnote_cuts(model, geom) -> dict:
    """Where CORE put each page's footnote zone.

    Indiana rules its own separator at 144.0pt and at no other measure, so
    the page itself would answer this in one line (``r.width`` in
    ``_SEP_MEASURE``, as ariz does). It is asked of core instead because on
    this court the two answers DISAGREE: core's chain takes a cover FENCE
    for a separator on 14 of the 50 records (see the module docstring), and
    on those pages the lower cover has already been lifted into a footnote
    before this reader runs. A reader that claimed it anyway would place
    the same rows twice — once tagged in the block, once again in the
    phantom note — and duplicating a document's own text is worse than
    leaving part of it for core. Bounded here, the claim stays total over
    the stream this reader actually receives, and the day core's chain
    stops taking the fence the bound lifts by itself.

    Verified over all 50 records and every page: this reconstruction
    reproduces the pipeline's own zone decision exactly."""
    from . import get_profile
    profile = get_profile("ind")
    parser = BylineParser(profile.byline)
    zones = FootnoteZones(model, geom, profile.footnotes, "ind", Trace(),
                          is_byline=lambda t: bool(parser.parse(t)))
    cuts: dict = {}
    prev = False
    for pm in model.pages:
        value = zones.page_zone(pm, prev).value
        cuts[pm.number] = float("inf") if value is None else value
        prev = value is not None
    return cuts


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its wide gaps
# --------------------------------------------------------------------------

def _visual_rows(pm, finder, cut: float) -> list[list]:
    """One entry per printed row, its same-baseline pieces together, in the
    page's own order; furniture and the footnote zone removed."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or line.top >= cut:
            continue
        if finder.kind(pm, line):
            continue
        key = line.row if line.row is not None else round(line.top)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


# --------------------------------------------------------------------------
# what the rows say
# --------------------------------------------------------------------------

def _is_masthead_top(text: str) -> bool:
    return _letters(text) == _MASTHEAD_TOP


def _is_masthead_name(text: str) -> bool:
    return _letters(text) == _MASTHEAD_NAME


def _docket_value(text: str) -> str | None:
    flat = _norm(text)
    if not _DOCKET_LEAD.match(flat):
        return None
    return _DOCKET_LEAD.sub("", flat).strip().rstrip(".") or None


def _dates(text: str) -> list[tuple[str, str]]:
    """[('argued', 'September 4, 2025'), ('decided', 'February 24, 2026')]."""
    return [(mm.group(1).lower(), _norm(mm.group(2)).rstrip("."))
            for mm in _DATE_LABEL.finditer(_norm(text))]


def _is_origin(text: str) -> bool:
    low = _norm(text).lower()
    return any(low.startswith(lead) for lead in _ORIGIN_LEADERS)


def _is_number_row(text: str) -> bool:
    flat = _norm(text)
    return bool(_NUMBER_LEAD.match(flat) or _LOWER_DOCKET.search(flat))


def _is_judge(text: str) -> bool:
    flat = _norm(text)
    return bool(_JUDGE_LEAD.match(flat) or _MASTERS.match(flat))


def _panel_names(text: str) -> list[str]:
    """The justices a roster row names, read off the BENCH TITLES it prints
    and never off the wording between them. 'Chief Justice Rush and Justices
    Massa, Slaughter, and Goff concur.' names four."""
    words = _norm(text).replace(",", " , ").split()
    out: list[str] = []
    i = 0
    while i < len(words):
        title = None
        for cand in _BENCH:
            parts = cand.split()
            if [w.rstrip(",") for w in words[i:i + len(parts)]] == parts:
                title = cand
                i += len(parts)
                break
        if title is None:
            i += 1
            continue
        while i < len(words):
            word = words[i]
            if word in (",", "and", "&"):
                i += 1
                continue
            bare = word.strip(".,;:")
            if not bare or not bare[:1].isupper():
                break
            if bare in ("Justice", "Justices", "Chief"):
                break
            if bare not in out:
                out.append(bare)
            i += 1
            # one surname per title unless the court printed a list
            if i < len(words) and words[i] not in (",", "and", "&"):
                break
    return out


def _join_rows(rows: list[str]) -> str:
    """A party name the page hyphenated across two rows is one name."""
    out = ""
    for row in rows:
        piece = _norm(row)
        if not out:
            out = piece
        elif out.endswith("-"):
            out = out[:-1] + piece
        else:
            out = out + " " + piece
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model, geom, pages, body_size):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.items: list = []
        self.attorneys: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}

    def _row(self, group: list):
        parts = sorted(group, key=lambda l: l.x0)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return parts, text

    def emit(self, group: list, role: str) -> None:
        parts, text = self._row(group)
        first = parts[0]
        pm = self.pages[first.page]
        align = line_alignment(first, pm.width, self.geom,
                               banner_center_min_size=self.body_size + 2.0)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts),
            italic=all(bool(p.all_emphasized) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def endmatter(self, group: list, role: str) -> None:
        """One printed row of the trailing roster, rendered the way the
        headmatter is rendered — the court just set it after the writings."""
        parts, text = self._row(group)
        first = parts[0]
        self.attorneys.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align("L"), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts),
            italic=all(bool(p.all_emphasized) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts, _ = self._row(group)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts)),
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int) -> None:
        # A FENCE RENDERS WHERE THE PAGE DRAWS IT. Core re-sorts the block by
        # the source position of each item's provenance, so a rule carrying
        # none sorts to the end; it takes the prov of the row above it and
        # stays put.
        prev = next((i for i in reversed(self.items)
                     if isinstance(i, m.HmLine)), None)
        self.items.append(m.Rule(
            prov=prev.prov if prev is not None else m.Prov(page),
            span="full"))

    def result(self):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys, "dropped": self.dropped,
                "consumed": self.consumed, "anchor_ids": [],
                "doc_type_final": None}


@decider("headmatter.read", court="ind")
def read_headmatter_ind(model, geom, **_):
    """Read Indiana's ruled cover and its trailing roster, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 108.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    # THE DISPATCH: the court engraves its name on page 1, and the cover
    # draws at least one full-measure fence at the rail over pages 1-2.
    cuts = _footnote_cuts(model, geom)
    cover_rows: list[list] = []
    for pm in model.pages[:_MAX_PAGES]:
        cover_rows.extend(_visual_rows(pm, finder, cuts[pm.number]))
    if not cover_rows:
        return NOTHING
    masthead = next(
        (g for g in cover_rows
         if g[0].page == 1 and (g[0].size or 0) >= _MASTHEAD_SIZE
         and g[0].top < page1.height * 0.5
         and _is_masthead_name(" ".join(l.plain for l in g))), None)
    if masthead is None:
        return NOTHING
    if not any(_fences(pm, body_x0) for pm in model.pages[:_MAX_PAGES]):
        return NOTHING

    ctx = _Ctx(model, geom, pages, body_size)
    ctx.crit["headmatter_style"] = STYLE_COVER
    _read_cover(ctx, cover_rows, masthead, body_x0, body_size)
    _read_roster(ctx, model, finder, cuts)
    return ctx.result()


# ---- the cover ------------------------------------------------------------

def _read_cover(ctx: _Ctx, rows: list, masthead: list, body_x0: float,
                body_size: float) -> None:
    """Walk the cover in the page's own order, fences included."""
    stream: list = []
    for group in rows:
        stream.append((group[0].page, group[0].top, 1, group))
    for pno in sorted({g[0].page for g in rows}):
        for top in _fences(ctx.pages[pno], body_x0):
            stream.append((pno, top, 0, None))
    stream.sort(key=lambda t: (t[0], t[1], t[2]))

    state = "court"
    caption: list[list] = []          # party/status/pivot rows, in order
    info: list[tuple[str, str]] = []  # (role, text) of the case-info band
    panel_rows: list[str] = []
    prev_info_top: float | None = None
    prev_info_role: str | None = None
    prev_page: int | None = None

    for page, top, kind, group in stream:
        if kind == 0:
            ctx.rule(page)
            continue
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        # THE READER ENDS AT THE BYLINE — the first row set at the BODY RAIL
        # at body size or above. Every cover row is centred and none starts
        # within 6pt of that rail.
        if (abs(group[0].x0 - body_x0) <= _RAIL
                and (group[0].size or 0) >= body_size - 0.5):
            break

        if state == "court":
            if group is masthead:
                ctx.crit["court"] = text
                ctx.emit(group, "court")
                continue
            if group[0].top < masthead[0].top:
                # above the masthead: the pre-certification notice
                if (group[0].size or 0) <= _NOTICE_MAX_SIZE:
                    ctx.drop(group, "notice")
                else:
                    ctx.emit(group, "court")
                continue
            if _is_masthead_top(text):
                ctx.emit(group, "court")
                continue
            docket = _docket_value(text)
            if docket is not None:
                ctx.crit["docket_number"] = docket
                ctx.emit(group, "docket")
                continue
            state = "caption"

        if state == "caption":
            if _AUTHOR_LEAD.match(text):
                state = "author"
            elif _dates(text) or _is_origin(text):
                state = "info"
            else:
                caption.append(group)
                ctx.emit(group, "caption")
                continue

        if state == "info":
            if _AUTHOR_LEAD.match(text):
                state = "author"
            else:
                role = _info_role(text)
                if (role is None and prev_info_role is not None
                        and prev_page == page and prev_info_top is not None
                        and 0 < top - prev_info_top <= _INFO_WRAP):
                    role = prev_info_role   # a wrap of the row above
                for label, value in _dates(text):
                    key = ("decision_date" if label == "decided"
                           else "submitted")
                    ctx.crit.setdefault(key, value)
                info.append(((role or "case-info"), text))
                ctx.emit(group, role or "case-info")
                prev_info_role = role
                prev_info_top, prev_page = top, page
                continue

        if state == "author":
            if _AUTHOR_LEAD.match(text) and "author" not in ctx.crit:
                ctx.crit["judges"] = _norm(
                    re.sub(r"^opinion\s+by\s+", "", text, flags=re.I)
                    .rstrip("."))
                ctx.crit["author"] = True
                ctx.emit(group, "author")
                panel_rows.append(text)
                continue
            panel_rows.append(text)
            ctx.emit(group, "panel")
            continue

    ctx.crit.pop("author", None)
    _caption_criteria(ctx, caption)
    _info_criteria(ctx, info)
    if panel_rows:
        ctx.crit["panel_line"] = " ".join(panel_rows)
        names: list[str] = []
        for row in panel_rows:
            for name in _panel_names(row):
                if name not in names:
                    names.append(name)
        if names:
            ctx.crit["panel"] = names


def _info_role(text: str) -> str | None:
    """What the case-info band's row IS, by the leader the court printed."""
    if _dates(text):
        return "date"
    if _is_origin(text):
        return "lower-court"
    if _is_judge(text):
        return "lower-court"
    if _is_number_row(text):
        return "lower-court"
    return None


def _caption_criteria(ctx: _Ctx, caption: list) -> None:
    """The case's name, built from the party names either side of the pivot
    — never by joining the caption wholesale."""
    if not caption:
        return
    rows = [_norm(" ".join(l.plain for l in g)) for g in caption]
    ctx.crit["caption"] = rows
    sides: list[list[list[str]]] = [[], []]
    side = 0
    group: list[str] = []
    for g, text in zip(caption, rows):
        if _PIVOT.match(text):
            if group:
                sides[side].append(group)
                group = []
            side = 1
            continue
        if _JOINER.match(text):
            if group:
                sides[side].append(group)
                group = []
            continue
        if (g[0].size or 0) >= _PARTY_SIZE:
            group.append(text)
        elif group:                     # a status closes its party group
            sides[side].append(group)
            group = []
    if group:
        sides[side].append(group)
    names = [_join_rows(g[0]).rstrip(",;: ") if g else None for g in sides]
    if names[0] and names[1]:
        ctx.crit["parties"] = [names[0], names[1]]
        ctx.crit["case_name"] = f"{names[0]} v. {names[1]}"
    elif names[0]:
        ctx.crit["parties"] = [names[0]]
        ctx.crit["case_name"] = names[0]


def _info_criteria(ctx: _Ctx, info: list) -> None:
    """What the case-info band states: the origin, its number, who tried it,
    and the route by which the case reached this court."""
    origin: list[str] = []
    judges: list[str] = []
    history: list[str] = []
    numbers: list[str] = []
    in_history = False
    for role, text in info:
        flat = _norm(text).rstrip(",")
        if role == "lower-court" and _is_origin(flat):
            in_history = flat.lower().startswith(
                ("on petition to transfer", "on transfer",
                 "on petition for review"))
            (history if in_history else origin).append(flat)
            continue
        if role == "lower-court" and _is_judge(flat):
            judges.append(flat)
            continue
        if role == "lower-court":
            (history if in_history else origin).append(flat)
        for number in _LOWER_DOCKET.findall(flat):
            if number not in numbers:
                numbers.append(number)
    if origin:
        ctx.crit["lower_court"] = "; ".join(origin)
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)
    if history:
        ctx.crit["history"] = " ".join(history)
    if numbers:
        ctx.crit["lower_court_docket"] = numbers


# ---- the trailing roster --------------------------------------------------

def _read_roster(ctx: _Ctx, model, finder, cuts: dict) -> None:
    """Claim the appearance roster Indiana prints below its writings.

    It is the only place in the document where 10pt type stands at the body
    rail. The run opens on a 10pt heading naming the party represented and
    closes at the next BODY-SIZED row — a separate writing's byline, or the
    end of the document. Rows smaller than the roster's own type (the
    footnote zone, the page footer) neither belong to it nor close it."""
    rows: list[list] = []
    for pm in model.pages:
        rows.extend(_visual_rows(pm, finder, cuts[pm.number]))
    start = None
    for i, group in enumerate(rows):
        size = round(group[0].size or 0.0, 1)
        if abs(size - _ROSTER_HEAD) > _ROSTER_SIZE_TOL:
            continue
        if _letters(" ".join(l.plain for l in group)).startswith(
                _ROSTER_HEAD_WORD):
            start = i
            break
    if start is None:
        return
    run: list[list] = []
    for group in rows[start:]:
        size = round(group[0].size or 0.0, 1)
        if (abs(size - _ROSTER_HEAD) <= _ROSTER_SIZE_TOL
                or abs(size - _ROSTER_ENTRY) <= _ROSTER_SIZE_TOL):
            run.append(group)
            continue
        if size < _ROSTER_HEAD - _ROSTER_SIZE_TOL:
            continue                    # a footnote below the roster
        break                           # body type: the roster is closed
    if not run:
        return
    # THE COLUMNS ARE READ AS COLUMNS. Two records set the roster in two,
    # and the rails the rows themselves cluster on are what separates them.
    for pno in sorted({g[0].page for g in run}):
        page_rows = [g for g in run if g[0].page == pno]
        rails: list[float] = []
        for group in page_rows:
            x0 = group[0].x0
            if not any(abs(x0 - r) <= _ROSTER_COLUMN for r in rails):
                rails.append(x0)
        rails.sort()
        for rail in rails:
            for group in page_rows:
                if abs(group[0].x0 - rail) <= _ROSTER_COLUMN:
                    ctx.endmatter(group, "counsel")
