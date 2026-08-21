"""indctapp — Court of Appeals of Indiana.

A COPY OF ind.py, not an import of it: court files may not import each
other, so a family that prints the same paper is ported by copying the
reader and rebinding the id. Indiana sets its Supreme Court and its Court of
Appeals from the same stationery — the engraved name over a RULED COVER, the
same 395.5pt fence at the same rail, the same case-info band under it, the
same authorship leader over the same roster of joiners, and the same
trailing appearances below the writings.

If the two courts ever diverge further, THIS file changes and ind.py does
not.

WHAT IS MEASURED DIFFERENT HERE, over all 42 records against ind's 50:

  * THE NAME. 'IN THE' at 14pt over 'Court of Appeals of Indiana' at 30pt on
    every record — where ind engraves 'Indiana Supreme Court'. The size is
    the landmark, not the words, and 30pt is well clear of the 24pt floor
    the dispatch keeps.
  * THE DOCKET IS IN THE CASE-INFO BAND, not above the caption, and it is
    printed on TWO ROWS — a label and its number:

        Court of Appeals Case No.
        24A-CR-2415

    ind sets 'Supreme Court Case No. 25S-PL-141' on one row above the
    parties. So the docket is read where this court prints it, by its own
    label, and the bare number under a label row belongs to it.
  * THE COURT BELOW numbers its case the same way, on two rows:

        Trial Court Cause No.
        30C01-2402-F5-000196

    39 of the 42 records print one; the three that do not are original
    actions.
  * THE PAPER NAMES ITSELF IN THE AUTHOR LEADER. 41 records lead 'Opinion by
    Judge Felix' / 'Opinion by Chief Judge Tavitas'; one leads 'Memorandum
    Decision by Judge May', which is this court's unpublished form. Both are
    the same landmark and both are read.
  * THE FENCES. 79 fences over the 42 records — 395.5pt at x0 108.2, the
    identical measure and rail ind draws, two per cover: one closing the
    caption and one closing the case-info band. Five records draw only one.
    THE FENCES ARE NOT COUNTED, exactly as in ind: each band is entered on
    its own landmark, so a cover that fences once still reads.
  * 39 of the 42 sign the writing under the author band ('Felix, Judge.',
    'Tavitas, Chief Judge.') and 39 print the trailing appearances roster.
    Both are ind's own shapes and are handled by the code copied with them.

    Above the masthead this court draws a 22.3pt mark (a stroked glyph, on
    29 records) which is neither a fence nor a separator: it is well under
    the fence measure and is left where it is.
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
# THE MASTHEAD: 'Court of Appeals of Indiana' at 30.0pt on every cover, over
# a 13.0pt body. Nothing else in the corpus is set above 18pt.
_MASTHEAD_SIZE = 24.0
# THE FENCE: 79 rules over the 42 records, every one 395.5-395.6pt wide and
# every one starting at x0 108.2-108.3.
#
# THE RAIL IS DECLARED, NOT MEASURED — the one place this reader must differ
# from ind.py's. ind draws its fence ON its body rail (108.0 against a
# measured body_x0 of 108.0), so testing the fence against the measured rail
# is exact there. This court sets the same fence at the same 108.2 but its
# measured body rail comes back 86.0 — its cover is centred matter and its
# body opens at 72.0, and the measurer averages them. Tested against that,
# the fence stood 22pt off its own rail, no cover dispatched, and all 42
# records fell through to core's shared ladder: 20 rows, none tagged, and
# 'IN THE' fused onto the head of `parties`.
_FENCE_MEASURE = (380.0, 410.0)
_FENCE_X0 = 108.25
_FENCE_RAIL = 2.0
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
# THE TRAILING ROSTER's own two sizes, measured on this court: a heading at
# 13.0pt naming the party represented ('ATTORNEY FOR APPELLANT') over entries
# at 12.0pt, against a 13.0pt body — where ind sets 10.0 over 11.0 against
# 12.0. The step is the same one type size; the absolute sizes are not, and
# left as ind's no roster was found on any of the 39 records that print one.
# The head's own measure: the longest in the corpus is 'ATTORNEY FOR
# APPELLEE/CROSS-APPELLANT' at 37 characters.
_ROSTER_HEAD_MAX = 60
_ROSTER_HEAD = 13.0
_ROSTER_ENTRY = 12.0
_ROSTER_SIZE_TOL = 0.25
_ROSTER_COLUMN = 6.0
# The notice one record prints ABOVE the masthead, at 10.0pt.
_NOTICE_MAX_SIZE = 10.5

# THE MASTHEAD'S OWN ROWS. Read letters-only: two records letterspace the
# first row ('I N   T H E'), and one letterspaces it with non-breaking
# spaces, so no test on the printed string can be shared between them.
_MASTHEAD_TOP = "INTHE"
_MASTHEAD_NAME = "COURTOFAPPEALSOFINDIANA"
# THIS COURT'S OWN DOCKET, announced by its printed leader: 'Supreme Court
# Case No. 25S-PL-141'. The number the court BELOW gave the case is printed
# in the case-info band and is never read from here.
# THE DOCKET'S OWN LABEL, and it stands ALONE on its row: the number is set
# under it. `\s*$` is what says so — read without the anchor the label would
# swallow a one-row form this court does not print.
_DOCKET_LEAD = re.compile(
    r"^court\s+of\s+appeals\s+case\s+nos?\.\s*", re.I)
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
# THE BARE DATE the case-info band opens on, and the bare NUMBER that stands
# under a label row ('24A-CR-2415', '30C01-2402-F5-000196', '25A-PL-3120').
_BARE_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s*\d{4}\.?$", re.I)
_BARE_NUMBER = re.compile(r"^[0-9][0-9A-Za-z]*(?:[-‑][0-9A-Za-z]+){1,4}$")
_LOWER_DOCKET = re.compile(
    r"\b\d{1,3}[A-Z]{0,2}\d{0,2}[-‑]\d{2,4}[-‑][A-Z]{1,3}[-‑]\d{1,6}\b"
    r"|\b\d{2}[A-Z][-‑][A-Z]{2}[-‑]\d{1,6}\b")
_NUMBER_LEAD = re.compile(
    r"^(nos?\.|trial\s+court\s+(?:case|cause)\s+nos?\.)", re.I)
# THE AUTHORSHIP LEADER — how the cover announces who wrote it. Both forms
# are set BOLD, and they are the only bold rows on any cover.
# 'Opinion by Judge Felix' on 41 records and 'Memorandum Decision by Judge
# May' on one — this court's unpublished form. Both name the author.
_AUTHOR_LEAD = re.compile(
    r"^(opinion\s+by\b|memorandum\s+decision\s+by\b"
    r"|per\s+curiam\s+(?:opinion|memorandum\s+decision)\b)", re.I)
# BENCH TITLES, a closed role vocabulary, longest first.
_BENCH = ("Chief Judge", "Judges", "Judge", "Senior Judge")
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
                  and abs(r.x0 - _FENCE_X0) <= _FENCE_RAIL)


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
    """[('argued', 'September 4, 2025'), ('decided', 'February 24, 2026')].

    THIS COURT PRINTS ONE BARE DATE and no labels: 'August 7, 2026', on the
    axis, as the first row under the caption's fence — 42 records out of 42.
    ind labels its dates ('Argued: … | Decided: …'), so the labelled form is
    kept for the family and the bare row is read as the decision date. It is
    what opens the case-info band; unread, the band never opened at all and
    the date, the docket label and the docket NUMBER were tinted `caption`
    (the user, 2026-08-20: 'this is date and docket').
    """
    flat = _norm(text)
    hits = [(mm.group(1).lower(), _norm(mm.group(2)).rstrip("."))
            for mm in _DATE_LABEL.finditer(flat)]
    if hits:
        return hits
    if _BARE_DATE.match(flat):
        return [("decided", flat.rstrip("."))]
    return []


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
            # THE STOP WORDS ARE THIS COURT'S OWN TITLES. Left as ind's, the
            # roster 'Chief Judge Tavitas and Judge Bradford concur.' ran
            # 'Judge' into the seat list as a surname and lost Bradford.
            if bare in ("Judge", "Judges", "Chief", "Senior"):
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


@decider("headmatter.read", court="indctapp")
def read_headmatter_indctapp(model, geom, **_):
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
    pending: str | None = None        # a label row awaiting its number
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
                # THE LABEL AND ITS NUMBER ARE TWO ROWS. This court sets
                # 'Court of Appeals Case No.' and 'Trial Court Cause No.' on
                # rows of their own and the number under each, so the number
                # is read as the continuation of the label above it — which
                # is the same wrap rule the band already keeps, used here to
                # fill the criteria the pair states.
                if role == "docket" and _DOCKET_LEAD.match(text):
                    pending = "docket"
                elif role == "lower-court" and _NUMBER_LEAD.match(text):
                    pending = "below"
                elif pending and _BARE_NUMBER.match(text):
                    if pending == "docket":
                        ctx.crit.setdefault("docket_number", text)
                    else:
                        ctx.crit.setdefault(
                            "lower_court_docket", []).append(text)
                    pending = None
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
    if _DOCKET_LEAD.match(_norm(text)):
        return "docket"
    # A BARE NUMBER BELONGS TO THE LABEL ABOVE IT, and only the label knows
    # which number it is: '24A-CR-2415' under 'Court of Appeals Case No.' is
    # this court's own docket, '30C01-2402-F5-000196' under 'Trial Court
    # Cause No.' is the court below's. Answered here it read as the court
    # below's every time, because the lower-docket pattern matches both
    # shapes. Left to the band's own wrap rule, each takes the role of the
    # row it continues.
    if _BARE_NUMBER.match(_norm(text)):
        return None
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
        # …AND NEVER THIS COURT'S OWN DOCKET. The two numbers are the same
        # shape ('24A-CR-2415' and '30C01-2402-F5-000196' both match), and
        # only the label above each says which is which — so a number this
        # cover already recorded as the docket is not the court below's.
        if role != "docket":
            for number in _LOWER_DOCKET.findall(flat):
                if number != ctx.crit.get("docket_number") \
                        and number not in numbers:
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

def _is_roster_head(flat: str) -> bool:
    """THE HEAD IS A LABEL, NOT A SENTENCE -- short, capitalised, and opening
    on the representation word ('ATTORNEYS FOR APPELLEE'). ind can tell a
    head from the body by size alone (10pt against a 12pt body); this court
    sets both at 13.0pt, so the shape has to say it."""
    return (_letters(flat).startswith(_ROSTER_HEAD_WORD)
            and len(flat) <= _ROSTER_HEAD_MAX
            and flat == flat.upper())


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
        flat = _norm(" ".join(l.plain for l in group))
        # THE HEAD IS A LABEL, NOT A SENTENCE — short and set in caps
        # ('ATTORNEY FOR APPELLANT', 'ATTORNEYS FOR APPELLEE'). ind can tell
        # the two apart by size alone, because its roster head is 10pt
        # against a 12pt body; here the head is 13.0pt and so is the body, so
        # the shape has to say it. Without that, the first row on the page
        # whose letters open on 'ATTORNEY' was a line of the opinion —
        # 'Attorneys and appellate counsel. P-C.R. 1(4)(g). Regardless …' —
        # and the roster went unclaimed on 7 of the 40 records that print
        # one.
        if _is_roster_head(flat):
            start = i
            break
    if start is None:
        return
    run: list[list] = []
    for group in rows[start:]:
        size = round(group[0].size or 0.0, 1)
        if abs(size - _ROSTER_HEAD) <= _ROSTER_SIZE_TOL:
            # AT HEAD SIZE, ONLY A HEAD BELONGS TO THE ROSTER. This court
            # sets its roster heads in the BODY's own 13.0pt, so 'a row at
            # head size' cannot mean 'a row of the roster' -- tested that
            # way, the run opened on 'ATTORNEYS FOR APPELLANTS' and never
            # closed, swallowing the separate concurrence that follows the
            # roster (garvin_street's four pages of it) into the counsel
            # section. Only the LABEL continues the run; any other row at
            # body type closes it, the byline included.
            if _is_roster_head(_norm(" ".join(l.plain for l in group))):
                run.append(group)
                continue
            break
        if abs(size - _ROSTER_ENTRY) <= _ROSTER_SIZE_TOL:
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
