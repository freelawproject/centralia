"""Tennessee Court of Appeals ('tennctapp').

Everything unique to tennctapp lives here. It imports core, never another
court file, and no other court file imports it.

THE PROFILE. tennctapp's ``CourtProfile`` stays in ``courts/__init__.py``
beside ``_TENN_GRAMMAR``, the byline grammar it shares with the Supreme
Court and the Court of Criminal Appeals. Shared data by reference is the
established pattern; the profile is fetched here, not re-registered.

THE CONTRACT — the same one the Supreme Court sets, and the same name:
``typed sandwich``. The court fences exactly one thing, its own docket
number, which stands alone in a band nothing else shares. Above the band is
the case's identity; below it the court's own front matter, down to the row
where the writing begins.

    07/15/2026                             the clerk's stamp — furniture,
                                           and the only release date printed
    IN THE COURT OF APPEALS OF TENNESSEE   the banner, 15.1pt, centred
    AT JACKSON                             …and where the Court sat
    April 21, 2026 Session                 the sitting: argued / on briefs
    AHA MECHANICAL CONTRACTORS, LLC v. …   the caption, BOLD
    Appeal from the Chancery Court for …   the origin, bold
    No. CH-21-1403-1  Melanie Taylor …     …its docket and its judge, ONE
                                           row set as two cells
    ______________________________         the fence, ON THE AXIS…
    No. W2025-01107-COA-R3-CV              …around THIS court's docket…
    ______________________________         …and one under it
    This appeal requires us to determine…  the summary
    Tenn. R. App. P. 3 Appeal as of Right; the disposition, BOLD
    STEVEN W. MARONEY, J., delivered the … the authorship announcement
    Scott A. Frick, Memphis, Tennessee, …  the appearances
    OPINION                                …and the writing begins

ONE FORMAT, 42 of 42. Every record sets the fence PAIR and nothing else:
TYPED as underscores at 227.3pt on 35 records, DRAWN as a filled rect at
216.0pt on seven. No record in the corpus prints one fence, three fences,
or none.

THE AXIS IS THE TYPE BLOCK'S, NOT THE PAGE'S. ``in_re_jaden_h`` sets its
whole text block to a 432pt measure (72 → 504) on the same 612pt sheet, so
its fences are centred at 287.9 — 18.1pt left of the page axis, which a
page-axis test rejects outright. Measured against ``(body_x0 + the type
block's right rail) / 2`` every fence in the corpus lands within 0.8pt.
That is also what disqualifies the footnote separator, which is 144pt wide
and struck 162pt LEFT of the axis at the foot of the page: the axis takes
it first, the measure takes it again.

WHAT STANDS ABOVE THE BAND IS THREE BLOCKS, ALWAYS. The court sets its
front matter at a 15pt leading and stands each block off at 2x that, and
above the fence the sequence never varies: the court's own name, its
division and its sitting; then the caption; then the origin. So the
CAPTION/ORIGIN boundary is a block boundary, not a wording test — which
matters, because 'BOARD OF EDUCATION' (aha, the caption's second row) and
'Appeal from the Chancery Court' (the origin's first) are both bold rows
full of court words, and only their position tells them apart. The last
block above the band is the origin; what lies between the court block and
it is the caption.

A SIZE STEP WOULD HAVE BEEN THE OBVIOUS TEST AND IT IS WRONG. 41 records
set the caption a step over the body (13.9 against 13.0) and the origin at
the body size — and ``michael_tomlin`` sets banner, caption and origin all
at 13.0. The block boundary holds on all 42.

WHERE THE READER STOPS: the 'OPINION' banner, on all 42 records. This
court's byline is an ANNOUNCEMENT ('…, J., delivered the opinion of the
court, in which … joined.') and the appearances print BELOW it, so the
writing does not start at the byline. Core already knows this — ``assemble``
moves everything between an ``accept_delivered`` byline and that banner back
to the headmatter — and the reader does the same job IN PLACE, so those rows
come back tagged instead of merely relocated. The byline row itself is
stepped over, never claimed: core builds the author from it, and a claim
would leave the writing unsigned.

THE BYLINE IS FOUND STRUCTURALLY, NOT BY THE GRAMMAR. An ALL-CAPS name
followed by a delivery verb and 'the opinion' is the announcement whether
or not ``_TENN_GRAMMAR`` can parse the row, and the reader must step over
it either way — otherwise the nine records signed by a SECTION presiding
judge would have their byline tagged as prose and their appearances read
as summary.

KNOWN GAP, NOT A LAYOUT FINDING — and it is core's, not this court's. Nine
of the 42 are signed 'J. STEVEN STAFFORD, P.J., W.S., delivered …' /
'JOHN W. MCCLARTY, P.J., E.S., …' — the presiding judge of a SECTION of
this court, whose section designator ``_TENN_GRAMMAR`` declares in
``title_suffixes``. ``BylineParser.parse`` normalizes tight punctuation
before matching ('E.S.' -> 'E. S.'), but ``title_suffixes`` is compared
against the TIGHT form, so the spread designator is never stripped, the
delivery verb is never reached, and those nine writings assemble unsigned.
The fix is data, one line in ``courts/__init__.py``, and it is reported
rather than applied here.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..resolve.bylines import BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import get_profile

# The profile is registered in courts/__init__.py beside _TENN_GRAMMAR,
# which tenn and tenncrimapp reference by the same name.
TENNCTAPP = get_profile("tennctapp")

STYLE_RULED = "typed sandwich"          # 42 of 42

# ---- tennctapp's declared facts (measured over the corpus, not tuned) ----
# THE FENCE MEASURE. 84 fences over 42 records, in two families and no
# others: 70 typed underscore rules at 227.3pt and 14 drawn rects at
# 216.0pt. The window is set wide enough to survive a re-setting, and it
# is the AXIS that does the discriminating.
_FENCE_MEASURE = (150.0, 300.0)
# …ON THE TYPE BLOCK'S AXIS, to within 0.8pt on every record in the
# corpus. Measured against the PAGE axis in_re_jaden_h misses by 18.1pt.
_FENCE_AXIS = 6.0
# A DRAWN fence and a TYPED one may both be present on one record; a rect
# within this of a typed rule's top is that rule inked, not a second fence.
_FENCE_SAME = 16.0
# THE BLOCK STAND-OFF. Front matter runs at a 15pt leading and stands the
# next block off at 2.0x it; a runover is 1.0x. 1.6x separates them, and
# it is what makes the caption/origin boundary readable.
_BLOCK_GAP = 1.6
# THE BANNER: 15.1pt over a 13.0pt body on 41 records and 13.0 flat on
# michael_tomlin. Either way it is the top row of page 1.
_BANNER_LEAD = 3                        # how many rows the banner may take
# THE WRITING'S OWN BANNER is set out from the rail: 'OPINION' at x0=277
# and 'MEMORANDUM OPINION' at x0=222 against a 72pt body rail. A row at
# the rail is prose, whatever it says.
_BANNER_INSET = 60.0
# THE NOTES ARE A STEP SMALLER: 11.0pt against a 13.0pt body. A caption
# footnote prints at the FOOT of the page the reader is walking, so the
# step is what keeps it out of the block — the note zone is core's.
_NOTE_STEP = 1.4
# THE CLERK'S STAMP sits in the right margin: a 9pt sans date on every
# record, and on in_re_othella_s a struck 'FILED' block with 6.4pt
# 'Clerk of the / Appellate Courts' beside it. Nothing the court sets in
# its headmatter starts this far right.
_STAMP_RAIL = 0.72
# HOW FAR THE BLOCK MAY RUN: the appearances wrap onto page 2 on ten
# records; nothing in the corpus needs a third sheet.
_MAX_PAGES = 3

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# THIS COURT'S OWN DOCKET, the only number it sets inside the band:
# 'No. W2025-01107-COA-R3-CV', 'No. E2026-00981-COA-T10B-CV'.
_DOCKET = re.compile(
    r"^Nos?\.\s*([A-Z]\d{4}-\d{3,6}-COA-[A-Z0-9-]+)", re.I)
# THE COURT BELOW gives its own number, and prints its judge beside it on
# the same visual row ('No. CH-21-1403-1  Melanie Taylor Jefferson,
# Chancellor').
_LOWER_NO = re.compile(r"^Nos?\.\s*(.+)$", re.I)
_BENCH = ("judge", "judges", "chancellor", "commissioner",
          "special judge", "senior judge", "magistrate")
# THE SITTING. Tennessee dates the hearing, never the release — the
# release date is the clerk's stamp, which is furniture.
_SITTING = ("session", "assigned on briefs", "heard at", "submitted on",
            "argued")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+)\.?\s*(\d{1,2}),?\s*(\d{4})")
# THE RELEASE DATE is the one date the court does NOT set in type: the
# clerk strikes it into the top-right margin as '07/15/2026'.
_STAMP_DATE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
# THE AUTHORSHIP ANNOUNCEMENT, read as a LABEL: an ALL-CAPS name, then a
# delivery verb over THE opinion. The verbs are core's own closed set; the
# ' the opinion' tail is what survives a page that sets the row with no
# spaces at all ('ANDY D.BENNETT,J.,delivered the opinion of the Court').
_DELIVERS = ("delivered", "filed", "authored", "announced", "wrote")
_ANNOUNCES = re.compile(
    r"\b(?:" + "|".join(_DELIVERS) + r")\s+the\s+opinion\b", re.I)
# THE PAPER'S OWN NAME, printed alone and centred where the court disposes
# of a case without a titled opinion. A closed vocabulary of labels.
_TITLE_HEADS = ("ORDER", "OPINION", "JUDGMENT", "PER CURIAM",
                "MEMORANDUM OPINION")
# THE ORIGIN opens on what an APPEAL is called, never on the name of any
# particular court. Used only to confirm the last block above the band is
# the origin — the boundary itself is geometric.
_ORIGIN_OPENERS = ("appeal", "direct appeal", "an appeal", "on appeal",
                   "appeal by permission", "appeal as of right",
                   "interlocutory appeal", "petition")
# THE DISPOSITION. The court closes its front matter with the rule it
# decided under and what it did, above the byline. It is BOLD on all 42
# records and the summary above it never is, so weight carries the test;
# the inset is the second mark and is a real STAND-OFF, not a nudge —
# jayesh_patel centres its disposition at x0=73.7, 1.7pt in from the body
# rail, and anything shorter than a stand-off would read that as prose.
_DISPOSITION_INSET = 40.0
_DISPOSITION_CUES = ("tenn. r. app. p.", "tenn. code ann.",
                     "tenn. sup. ct. r.", "tenn. r. civ. p.",
                     "tenn. r. juv. p.", "appeal as of right",
                     "appeal by permission", "extraordinary appeal",
                     "interlocutory appeal", "direct appeal",
                     "accelerated interlocutory appeal")
# REPRESENTATION is a closed role vocabulary. Every appearance this court
# prints closes on one of these; a party or firm NAME is never read. The
# marks are tested against the row with its spaces removed as well as with
# them, because the extractor loses a space often enough that a literal
# match misses ('for theappellees, Alexandria and Mark B.').
_COUNSEL_MARKS = ("for the appell", "for appell", "for the petition",
                  "for petition", "for the respond", "for respond",
                  "for the amic", "for amic", "for the plaintiff",
                  "for the defendant", "for the state of", "pro se",
                  "on brief", "attorney general and reporter",
                  "assistant attorney general", "solicitor general",
                  "no appearance", "guardian ad litem")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _tight(text: str) -> str:
    return _norm(text).upper().replace(" ", "")


def _is_banner(text: str) -> bool:
    """The court names itself on the top row of every paper it prints, then
    names the city it sat in underneath.

    Read WITHOUT the spaces, and as a CONTAINMENT: the extractor loses a
    space often, and jo_kelly_stephenson loses the opening 'I' outright
    ('N THE COURT OF APPEALS OF TENNESSEE'). The court's own name is the
    same name either way."""
    flat = _norm(text).upper().rstrip(".")
    tight = flat.replace(" ", "")
    if "THECOURTOFAPPEALSOFTENNESSEE" in tight:
        return True
    return flat.startswith("AT ") and len(flat) <= 24


def _sitting_value(text: str) -> str | None:
    """'April 21, 2026 Session' / 'Assigned on Briefs July 1, 2026' — the
    day the Court took the case up, which is the only date the page sets in
    type. Returns the date as printed, or None."""
    flat = _norm(text)
    low = flat.lower()
    if not any(cue in low for cue in _SITTING):
        return None
    mm = _DATE.search(flat)
    if mm is None or mm.group(1).lower().rstrip(".") not in _MONTHS:
        return None
    return f"{mm.group(1)} {mm.group(2)}, {mm.group(3)}"


def _is_origin_opener(text: str) -> bool:
    low = _norm(text).lower()
    return low.startswith(_ORIGIN_OPENERS)


def _title_label(text: str) -> str | None:
    """A centred all-caps row under the fence names the paper."""
    flat = _norm(text).rstrip(".:")
    letters = [c for c in flat if c.isalpha()]
    if not letters or not all(c.isupper() for c in letters):
        return None
    if len(flat) > 60 or not flat.startswith(_TITLE_HEADS):
        return None
    return flat


def _is_announcement(text: str) -> bool:
    """'STEVEN W. MARONEY, J., delivered the opinion of the court, in which
    … joined.' — an ALL-CAPS name, then a delivery verb over THE opinion."""
    flat = _norm(text)
    head = flat.split(",", 1)[0]
    letters = [c for c in head if c.isalpha()]
    if not letters or not all(c.isupper() for c in letters):
        return False
    return _ANNOUNCES.search(flat) is not None


def _is_disposition(text: str) -> bool:
    low = _norm(text).lower()
    return any(cue in low for cue in _DISPOSITION_CUES)


def _is_counsel(text: str) -> bool:
    low = _norm(text).lower()
    tight = low.replace(" ", "")
    return any(mk in low or mk.replace(" ", "") in tight
               for mk in _COUNSEL_MARKS)


# --------------------------------------------------------------------------
# the band — tennctapp's one section mark, and the dispatch
# --------------------------------------------------------------------------

def _type_axis(pm, geom) -> float:
    """The axis the court centres on: the middle of its own TYPE BLOCK.

    Not the page's — in_re_jaden_h sets a 432pt measure on a 612pt sheet
    and every fence on it is 18.1pt left of the page axis. The right rail
    is the furthest any full-measure row reaches."""
    rail = max((l.x1 for l in pm.lines
                if abs(l.x0 - geom.body_x0) < 2.0), default=None)
    if rail is None:
        return pm.width / 2
    return (geom.body_x0 + rail) / 2


def _typed_fences(pm, axis: float) -> list:
    """The typed underscore rules this page sets on its axis, in order."""
    out = []
    for line in pm.lines:
        if not _TYPED_RULE.match(_norm(line.plain)):
            continue
        width = line.x1 - line.x0
        if not (_FENCE_MEASURE[0] <= width <= _FENCE_MEASURE[1]):
            continue
        if abs((line.x0 + line.x1) / 2 - axis) > _FENCE_AXIS:
            continue
        out.append(line)
    return sorted(out, key=lambda l: l.top)


def _drawn_fences(pm, typed: list, axis: float) -> list:
    """…and the ones it STROKES instead. A rect sitting on a typed rule is
    that rule inked, not a second fence. The footnote separator is 144pt
    wide and 162pt off the axis, so both tests refuse it."""
    tops = [l.top for l in typed]
    out = []
    for r in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - axis) > _FENCE_AXIS:
            continue
        if any(abs(r.top - t) <= _FENCE_SAME for t in tops):
            continue
        out.append(r.top)
    return sorted(out)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="tennctapp")
def read_headmatter_tennctapp(model, geom, **_):
    """Read tennctapp's banded headmatter, or NOTHING."""
    if not model.pages or geom is None:
        return NOTHING
    page1 = model.pages[0]
    finder = FurnitureFinder(model, geom.body_x0, geom.body_size)
    page_w = page1.width
    rows: list = []
    stamped: list = []
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            # THE NOTES ARE A STEP SMALLER and they are core's, wherever
            # they fall: a caption footnote prints at the FOOT of the page
            # the reader is walking.
            if (line.size or 0) < geom.body_size - _NOTE_STEP:
                continue
            # THE CLERK'S STAMP, struck into the right margin — taken here
            # and not in the walk, because on in_re_othella_s its 'FILED'
            # stands ABOVE the banner and would otherwise be read as one.
            if line.page == 1 and line.x0 >= page_w * _STAMP_RAIL:
                stamped.append(line)
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for l in rows[:_BANNER_LEAD]):
        return NOTHING                    # the court names itself first

    axis = _type_axis(page1, geom)
    typed = _typed_fences(page1, axis)
    drawn = _drawn_fences(page1, typed, axis)
    marks = sorted([l.top for l in typed] + list(drawn))
    if len(marks) < 2:
        return NOTHING                    # not this paper; core's walk reads it
    return _read(model, geom, rows, stamped,
                 (marks[0], marks[-1], typed, drawn))


class _Ctx:
    """The emit buffer, shared by the walk's three zones."""

    def __init__(self, model, geom, pages):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.items: list = []
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}

    def row(self, cells: list, role: str):
        """A visual ROW, which the page may have set as two cells ('No.
        CT-003613-18' beside 'Gina Higgins, Judge') — one item, and every
        line id it was built from."""
        parts = sorted(cells, key=lambda l: l.x0)
        pm = self.pages[parts[0].page]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        align = line_alignment(parts[0], pm.width, self.geom,
                               banner_center_min_size=self.geom.body_size + 2.0)
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(p.all_bold for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, cells: list, kind: str):
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(c.plain for c in cells))[:120],
            prov=m.Prov(cells[0].page, tuple(c.id for c in cells)),
            kind=kind))
        self.consumed.update(c.id for c in cells)

    def rule(self, page: int, line=None):
        prov = m.Prov(page, (line.id,) if line is not None else ())
        self.items.append(m.Rule(prov=prov, typed=line is not None,
                                 span="center"))
        if line is not None:
            self.consumed.add(line.id)

    def result(self, anchor_ids=()):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": list(anchor_ids), "doc_type_final": None}


def _visual_rows(lines: list) -> list:
    """Lines the page set on ONE baseline, grouped: pdfio splits a row at a
    wide column gap, and half an origin row is not an origin row."""
    out: list[list] = []
    for line in sorted(lines, key=lambda l: (l.page, l.top, l.x0)):
        if (out and out[-1][0].page == line.page
                and abs(out[-1][0].top - line.top) <= 3):
            out[-1].append(line)
        else:
            out.append([line])
    return out


def _block_end(vrows: list, start: int, lead: float, pages=None) -> int:
    """One past the block opening at ``start``: this court runs a paragraph
    at 1.0x its leading and stands the next block off at 2.0x.

    A block may WRAP THE SHEET — chicago_title's appearances break after
    '…for the appellee,' and finish at the top of page 2. The torn edge is
    the page's last row ending mid-clause under a continuation that opens
    the next page."""
    j = start + 1
    while j < len(vrows):
        prev, cur = vrows[j - 1][0], vrows[j][0]
        if cur.page == prev.page:
            if cur.top - prev.top > _BLOCK_GAP * lead:
                break
            j += 1
            continue
        if cur.page != prev.page + 1 or pages is None:
            break
        tail = _norm(prev.plain)
        height = pages[cur.page].height if cur.page in pages else 792.0
        if tail.endswith((".", "!", "?", ":", ";")) or cur.top > height * 0.22:
            break
        j += 1
    return j


def _read(model, geom, rows, stamped, band):
    band_top, band_bottom, typed, drawn = band
    lead = geom.lead or 15.0
    pages = {pm.number: pm for pm in model.pages}
    ctx = _Ctx(model, geom, pages)
    parser = BylineParser(TENNCTAPP.byline)
    # THE RELEASE DATE, read off the clerk's stamp. The row itself is
    # furniture and is dropped, but the value is the only record the page
    # carries of the day the opinion issued.
    for line in model.pages[0].lines:
        if line.x0 < model.pages[0].width * _STAMP_RAIL:
            continue
        if _STAMP_DATE.match(_norm(line.plain)):
            ctx.crit.setdefault("decision_date", _norm(line.plain))
            break
    for row in _visual_rows(stamped):
        ctx.drop(row, "stamp")

    typed_ids = {l.id for l in typed}
    vrows = _visual_rows([l for l in rows if l.id not in typed_ids])
    # THE BLOCK IS THE UNIT, not the row: an appearance is one entry
    # however many lines it wraps over, and the ROLE is a property of the
    # entry. Read once, up front.
    index = {id(r[0]): i for i, r in enumerate(vrows)}
    block_at: dict = {}
    block_start: dict = {}
    _i = 0
    while _i < len(vrows):
        _j = _block_end(vrows, _i, lead, pages)
        block_at[_i] = (_j, _norm(" ".join(
            x.plain for k in range(_i, _j) for x in vrows[k])))
        for _k in range(_i, _j):
            block_start[_k] = _i
        _i = _j

    # THE ORIGIN IS THE LAST BLOCK ABOVE THE BAND. Three blocks stand
    # there on every record — the court's name and sitting, the caption,
    # the origin — and only position separates the last two: 'BOARD OF
    # EDUCATION' and 'Appeal from the Chancery Court' are both bold rows
    # full of court words. Confirmed, not decided, by the opener.
    above = [i for i, r in enumerate(vrows)
             if (r[0].page, r[0].top) < (1, band_top)]
    origin_at = None
    if above:
        cand = block_start[above[-1]]
        if cand > 0 and _is_origin_opener(_norm(
                " ".join(x.plain for x in vrows[cand]))):
            origin_at = cand
    if origin_at is None:
        return NOTHING            # no origin block: not this paper

    below = [r for r in vrows
             if (r[0].page, r[0].top) > (1, band_bottom)]

    # WHERE THE HEADMATTER ENDS: the 'OPINION' banner, which all 42
    # records print. Everything above it — summary, disposition, byline
    # announcement, appearances — is front matter. This is the same rule
    # core applies to an ``accept_delivered`` byline, applied in place so
    # the rows come back TAGGED instead of merely relocated.
    banner_at = None
    for row in below:
        if _is_writing_banner(row, geom):
            banner_at = row[0]
            break
    # THE BYLINE is found STRUCTURALLY first and by the grammar second.
    # Nine records are signed by a SECTION presiding judge, whose row the
    # shared grammar declines; the reader must still step over the block
    # rather than read the appearances under it as summary.
    byline_at = None
    for row in below:
        if banner_at is not None and (row[0].page, row[0].top) >= (
                banner_at.page, banner_at.top):
            break                         # a signature under the banner is
        text = _norm(row[0].plain)        # a sign-off, not this byline
        if _is_announcement(text) or parser.parse(text) is not None:
            byline_at = row[0]
            break
    end_at = banner_at or byline_at

    # the stream the walk reads: content rows and the fences, merged by
    # where the page prints each
    stream: list = []
    for row in vrows:
        stream.append((row[0].page, row[0].top, 1, row))
    for line in typed:
        stream.append((line.page, line.top, 0, line))
    for top in drawn:
        stream.append((1, top, 0, None))
    stream.sort(key=lambda t: (t[0], t[1], t[2]))

    caption: list[str] = []
    origin: list[str] = []
    lower_nos: list[str] = []
    dispositions: list[str] = []
    counsel: list[str] = []
    dockets: list[str] = []
    anchor_ids: list[int] = []
    state = "court"
    skip_to = None
    signed = False                        # the walk has passed the byline

    for page, top, kind, payload in stream:
        if kind == 0:
            ctx.rule(page, payload)
            continue
        row = payload
        line = row[0]
        if skip_to is not None:
            if (line.page, line.top) < skip_to:
                continue
            skip_to = None
        text = _norm(" ".join(l.plain for l in row))

        # ---- the band: this court's own docket, and nothing else -------
        if page == 1 and band_top <= top <= band_bottom:
            mm = _DOCKET.match(text)
            if mm is None:
                return NOTHING            # the band holds a docket, or nothing
            dockets.append(mm.group(1))
            ctx.row(row, "docket")
            continue

        # ---- above the band: who the parties are and where they came from
        if page == 1 and top < band_top:
            idx = index[id(line)]
            if idx >= origin_at:
                origin.append(text)
                mm = _LOWER_NO.match(text)
                if mm:
                    lower_nos.append(mm.group(1))
                ctx.row(row, "lower-court")
                continue
            if state == "court":
                if _is_banner(text):
                    ctx.crit.setdefault("court", text)
                    ctx.row(row, "court")
                    continue
                value = _sitting_value(text)
                if value is not None:
                    ctx.crit.setdefault("submitted", value)
                    ctx.row(row, "date")
                    continue
                state = "caption"
            caption.append(text)
            ctx.row(row, "caption")
            continue

        # ---- below the band: the court's own front matter --------------
        if end_at is None:
            # A PAPER THAT NAMES ITSELF AND NOTHING ELSE: claim the one
            # row (as a releasable anchor) and stop.
            label = _title_label(text)
            if label is None:
                break
            ctx.crit.setdefault("title", label)
            ctx.row(row, "title")
            anchor_ids.append(line.id)
            break
        if (line.page, line.top) >= (end_at.page, end_at.top):
            break                         # the writing starts here
        if byline_at is not None and (line.page, line.top) == (
                byline_at.page, byline_at.top):
            # THE BYLINE STAYS IN THE STREAM: core builds the author from
            # it, and a claim would leave the writing unsigned. Its own
            # block (the joined-roster tail) goes with it.
            idx = index[id(line)]
            end = block_at.get(idx, (idx + 1, ""))[0]
            ctx.crit.setdefault("panel_line", text)
            signed = True
            if end >= len(vrows):
                break
            skip_to = (vrows[end][0].page, vrows[end][0].top)
            continue
        # BELOW THE BYLINE, EVERYTHING TO THE BANNER IS THE ROSTER. That
        # is core's own rule for an announcement byline; reading these rows
        # by their marks instead misfiles a summary that happens to say
        # 'proceeding pro se', so the marks are consulted ONLY where the
        # paper printed no byline to stand below.
        idx = index[id(line)]
        end, whole = block_at.get(idx, (idx + 1, text))
        if signed or (byline_at is None and (_is_counsel(whole) or counsel)):
            entry = []
            for k in range(idx, end):
                ctx.row(vrows[k], "counsel")
                entry.append(_norm(" ".join(x.plain for x in vrows[k])))
            counsel.append(" ".join(entry))
            if end >= len(vrows):
                break
            skip_to = (vrows[end][0].page, vrows[end][0].top)
            continue
        label = _title_label(text)
        if label is not None and not dispositions and not counsel:
            ctx.crit.setdefault("title", label)
            ctx.row(row, "title")
            anchor_ids.append(line.id)
            continue
        _set_out = (line.all_bold
                    or line.x0 >= geom.body_x0 + _DISPOSITION_INSET)
        if _set_out and (_is_disposition(text) or dispositions):
            dispositions.append(text)
            ctx.row(row, "disposition")
            continue
        ctx.row(row, "summary")

    if not dockets:
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE_RULED
    ctx.crit["docket_number"] = "No. " + dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = ["No. " + d for d in dockets[1:]]
    if caption:
        ctx.crit["caption"] = caption
        _name(ctx, caption)
    if origin:
        ctx.crit["lower_court"] = "; ".join(origin)
        bench = [o for o in origin if _has_bench(o)]
        if bench:
            ctx.crit["lower_court_judge"] = bench[-1]
    if lower_nos:
        numbers = _lower_numbers(lower_nos)
        if numbers:
            ctx.crit["lower_court_docket"] = numbers
    if dispositions:
        ctx.crit["disposition"] = " ".join(dispositions)
    if counsel:
        ctx.crit["attorneys"] = " ".join(counsel)[:2000]
    return ctx.result(anchor_ids)


def _is_writing_banner(row: list, geom) -> bool:
    """The name the court sets over the writing itself — the same closed
    set core uses to find where an announcement byline's opinion begins.

    The word alone does not make the banner: a summary can break so that
    its last row is 'Opinion.' AT THE BODY RAIL. The banner is SET OUT —
    centred, well right of the rail — and the row carries nothing else. A
    footnote mark may be welded to it ('MEMORANDUM OPINION1'), so the
    trailing mark comes off before the comparison."""
    if len(row) != 1:
        return False
    line = row[0]
    if line.x0 <= geom.body_x0 + _BANNER_INSET:
        return False
    flat = _tight(line.plain).rstrip(".")
    while flat and (flat[-1].isdigit() or flat[-1] in "*†‡"):
        flat = flat[:-1]
    return flat in ("OPINION", "ORDER", "MEMORANDUMOPINION")


def _has_bench(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return any(low.endswith(w) for w in _BENCH)


def _lower_numbers(rows: list) -> list:
    """'No. CH-21-1403-1  Melanie Taylor Jefferson, Chancellor' -> the one
    number. The judge is recorded on his own, so the row is cut at the
    first piece that carries no digit."""
    out: list[str] = []
    for row in rows:
        for piece in row.split(","):
            token = piece.strip().split()[0].rstrip(",;.") \
                if piece.split() else ""
            if token and any(c.isdigit() for c in token):
                out.append(token)
    return out


def _name(ctx: _Ctx, rows: list) -> None:
    """The case name, built from the party names either side of the pivot
    — never by joining the caption wholesale."""
    joined = _norm(" ".join(rows))
    for sep in (" v. ", " vs. ", " V. ", " VS. "):
        if sep in joined:
            left, right = joined.split(sep, 1)
            left, right = left.strip(" ,"), right.strip(" ,")
            ctx.crit["parties"] = [left, right]
            ctx.crit["case_name"] = f"{left} v. {right}"
            return
    ctx.crit["case_name"] = joined
