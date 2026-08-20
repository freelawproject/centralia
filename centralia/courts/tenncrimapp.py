"""Tennessee Court of Criminal Appeals ('tenncrimapp').

Everything unique to tenncrimapp lives here. It imports core, never another
court file, and no other court file imports it.

THE PROFILE. tenncrimapp's ``CourtProfile`` stays in ``courts/__init__.py``
beside ``_TENN_GRAMMAR``, the byline grammar it shares with the Supreme
Court and the Court of Appeals. Shared data by reference is the established
pattern; the profile is fetched here, not re-registered. The grammar needed
nothing: over the 42 records this court prints 40 announcement bylines and
``BylineParser`` reads 39 of them (the fortieth is a typo on the page, see
KNOWN GAP below); the other two records are unsigned ORDERS.

THE CONTRACT — the same one the Supreme Court and the Court of Appeals set,
and the same name: ``typed sandwich``. The court fences exactly one thing,
its own docket number, which stands alone in a band nothing else shares.
Above the band is the case's identity; below it the court's own front
matter, down to the row where the writing begins.

    07/02/2026                             the clerk's stamp — furniture,
                                           and the only release date printed
    IN THE COURT OF CRIMINAL APPEALS OF …  the banner, 15.1pt
    AT JACKSON                             …and where the Court sat
    Assigned on Briefs at Knoxville June … the sitting: argued / on briefs
    STATE OF TENNESSEE v. KEITH ANDREW …   the caption, BOLD
    Appeal from the Circuit Court for …    the origin, bold
    No. 21-26    Joseph T. Howell, Judge   …its docket and its judge, ONE
                                           row set as two cells
    ______________________________         the fence, ON THE AXIS…
    No. W2025-01176-CCA-R3-CD              …around THIS court's docket…
    ______________________________         …and one under it
    The Defendant, Keith Andrew Baggett, … the summary
    Tenn. R. App. P. 3 Appeal as of Right; the disposition, BOLD
    ROBERT H. MONTGOMERY, JR., J., deliv…  the authorship announcement
    Jeremy Epperson, District Public Def…  the appearances
    OPINION                                …and the writing begins

ONE FORMAT, 42 of 42, and the band is a PAIR on every record: two marks on
the type block's axis, exactly one row between them, and that row is this
court's own docket. Measured: 33 records TYPE the pair as underscore rules
at 227.2–227.4pt; 9 STROKE it as filled rects, in four measures —
216.2 (powell, smotherman), 216.5 (collins, norton), 147.8 (baggett,
jenkins) and 144.0 (chantler, burrow, gordon). No record prints one fence,
three fences, or none.

THE DRAWN MEASURE REACHES DOWN TO 144pt, WHICH IS THE FOOTNOTE SEPARATOR'S
MEASURE TOO — so the axis has to do the discriminating, not the width. The
separator is struck 162pt LEFT of the axis at the foot of the page
(cartwright, roach, teresa_kay_nolan and eight others); every fence in the
corpus lands within 1.1pt of the axis. Because the window had to open to
144, ONE MORE test is needed that tennctapp did not need: a rect whose two
ends coincide with the row printed just above it is an UNDERLINE, not a
fence. ``bryiant_c._overton`` strokes 203.3pt at x=204.2–407.5 dead on the
axis, under a bold section head set at exactly x=204.2–407.5 — inside the
window, on the axis, and 325pt below the real band. Take it and the band
runs from the docket to the middle of the opinion.

THE AXIS IS THE TYPE BLOCK'S, NOT THE PAGE'S — inherited from the sibling
courts and it costs nothing here (all 42 set a 468pt measure on a 612pt
sheet, so the two coincide to 0.5pt), but the fence pair is centred on what
the court set, and that is the thing to measure against.

WHAT STANDS ABOVE THE BAND IS THREE BLOCKS, ALWAYS. The court runs its
front matter at a 15pt leading and stands each block off at 2.0x that, and
above the fence the sequence never varies: the court's own name and where
it sat; then the caption; then the origin. So the CAPTION/ORIGIN boundary
is a block boundary, not a wording test.

AND THE ORIGIN DOES NOT ALWAYS SAY 'APPEAL'. 40 of 42 open the origin with
'Appeal from the Circuit Court for …' / 'Appeal from the Judgment of the
Circuit Court for …' (wendricks), which is what tennctapp confirms its
origin block by. The two ORDERS name the court below with no recital at all
— 'Criminal Court for Shelby County' (annesha_jackson), 'Circuit Court for
Hickman County' (rediker). What all 42 do print in that block is the number
the court below gave the case, so the CONFIRMATION is a docket row, not an
appeal word: an opener OR a 'No. …' row, and the block is the last one
above the band either way.

THE SITTING IS NOT ALWAYS PRINTED. 40 records date the hearing ('May 6,
2026 Session', 'Assigned on Briefs June 23, 2026 at Knoxville', 'November12,
2025 Session' with the space lost); the two ORDERS print no date at all
except the clerk's stamp. The banner block simply ends and the caption
begins — which is why the block boundary, not the row count, is the test.

WHERE THE READER STOPS: the writing's own banner, on all 42 records —
'OPINION' on 40, 'ORDER' on the two unsigned ones. It is set out 203–211pt
from the body rail every time, and 14 of the 42 print it on PAGE 2 with the
appearances running over onto that sheet, so the reader walks two pages.
This court's byline is an ANNOUNCEMENT ('…, J., delivered the opinion of
the court, in which … joined.') and the appearances print BELOW it, so the
writing does not start at the byline. Core already knows this — ``assemble``
moves everything between an ``accept_delivered`` byline and that banner back
to the headmatter — and the reader does the same job IN PLACE, so those rows
come back tagged instead of merely relocated. The byline row itself is
stepped over, never claimed: core builds the author from it, and a claim
would leave the writing unsigned.

THE BYLINE IS FOUND STRUCTURALLY, NOT BY THE GRAMMAR. An ALL-CAPS name
followed by a delivery verb and 'the opinion' is the announcement whether
or not ``_TENN_GRAMMAR`` can parse the row, and the reader must step over
it either way.

THE DISPOSITION IS SET IN FROM THE RAIL, AND WEIGHT IS NOT ENOUGH. 38 of
the 40 opinions set it BOLD, which is what tennctapp keys on; ``j.p._burrow``
and ``victor_gordon`` set their whole page 1 roman — caption, origin and
disposition alike — at x0=77.8, 5.8pt in from a 72.0 rail. tennctapp's
40pt stand-off reads that as prose. The measured separation here is the
PARAGRAPH INDENT: every disposition in the corpus sits at 76.3–201.4 and
not one at the indent, while the summary sets its opener AT the indent
(36.0pt on all 42) and its wraps at the rail. So the test is 'off the rail
and off the indent', with the rule cue carrying the rest.

REPORTED, NOT WORKED AROUND — a core placement, measured here because
this court's byline always wraps. The announcement runs two printed rows
on 40 of 42 records. Core builds the byline from the FIRST row and welds
the wrap on only where the first row breaks MID-WORD ('…in which JILL BART'
/ 'AYERSandMATTHEW J.WILSON, JJ., joined.' — collins). Where it breaks at
a word boundary ('…in which ROBERT H.' / 'MONTGOMERY,JR., and STEVEN
W.SWORD, JJ., joined.' — roach) the continuation is left in the headmatter
with nothing claiming it: 12 of the 40 signed records (roach, pickle,
phillips, both starnes, skidmore, moten, gambill, golden, burnette,
jenkins, smith), one row each, and the same 12 rows are orphaned with this
reader popped. The reader deliberately does NOT claim them — the roster
tail belongs to the byline sentence, and claiming it would take the roster
out of collins' author string and leave it truncated mid-word.

KNOWN GAP, NOT A LAYOUT FINDING, and it is the page's, not core's.
``state_of_tennessee_v._johnny_mack_powell`` signs 'ROBERT W. WEDEMEYER,
PJ., delivered the opinion of the Court…' — the abbreviation is set without
its first period, so no title in the grammar matches and that writing
assembles unsigned. The reader still finds the row structurally and steps
over it, so the appearances beneath it are read as appearances and not as
summary; only the author is lost, and it is lost to a typo in the PDF.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..resolve.bylines import BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import roster_names
from ..resolve.evidence import NOTHING, decider
from . import get_profile

# The profile is registered in courts/__init__.py beside _TENN_GRAMMAR,
# which tenn and tennctapp reference by the same name. Nothing about it
# needed changing for this court.
TENNCRIMAPP = get_profile("tenncrimapp")

STYLE_RULED = "typed sandwich"          # 42 of 42

# ---- tenncrimapp's declared facts (measured over the corpus, not tuned) ---
# THE FENCE MEASURE. 84 fences over 42 records: 66 typed underscore rules
# at 227.2–227.4pt and 18 drawn rects in four measures, 144.0 to 216.5.
# The window has to open to 144 for chantler/burrow/gordon, which is the
# footnote separator's measure as well — so it is the AXIS that does the
# discriminating, and the underline test below that finishes the job.
_FENCE_MEASURE = (140.0, 300.0)
# …ON THE TYPE BLOCK'S AXIS, to within 1.1pt on every record in the corpus.
_FENCE_AXIS = 6.0
# A DRAWN fence and a TYPED one may both be present on one record; a rect
# within this of a typed rule's top is that rule inked, not a second fence.
_FENCE_SAME = 16.0
# A RECT WHOSE ENDS COINCIDE WITH THE ROW ABOVE IT IS AN UNDERLINE.
# bryiant_c._overton strokes 203.3pt on the axis under a bold section head
# set to the same 204.2–407.5 measure; inside the window and on the axis,
# and 325pt below the real band.
_UNDERLINE_DROP = 15.0                  # how far under a row a rule may sit
_UNDERLINE_ENDS = 3.0                   # …and how closely its ends must agree
# THE BLOCK STAND-OFF. Front matter runs at a 15pt leading (16pt on box,
# lumley, poole) and stands the next block off at 2.0x it; a runover is
# 1.0x. 1.6x separates them, and it is what makes the caption/origin
# boundary readable.
_BLOCK_GAP = 1.6
# THE BANNER: 15.0–15.1pt over a 12.8–13.0pt body, and always the top row
# of page 1 under the clerk's stamp.
_BANNER_LEAD = 3                        # how many rows the banner may take
# THE WRITING'S OWN BANNER is set far out from the rail: 'OPINION' and
# 'ORDER' land 203.3–210.5pt in on all 42 records. A row at the rail is
# prose, whatever it says.
_BANNER_INSET = 60.0
# THE NOTES ARE A STEP SMALLER: 11.0pt against a 12.8–13.0pt body. A caption
# footnote prints at the FOOT of the page the reader is walking (price sets
# two of them), so the step is what keeps it out of the block — the note
# zone is core's.
_NOTE_STEP = 1.4
# THE CLERK'S STAMP sits in the right margin: a 9pt sans date at x0=534.5
# on all 42 records. Nothing the court sets in its headmatter starts this
# far right.
_STAMP_RAIL = 0.72
# HOW FAR THE BLOCK MAY RUN: the appearances wrap onto page 2 on 14 records
# and the banner with them; nothing in the corpus needs a third sheet.
_MAX_PAGES = 2

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# THIS COURT'S OWN DOCKET, the only number it sets inside the band:
# 'No. W2025-01176-CCA-R3-CD', 'No. E2025-00035-CCA-R3-CD',
# 'No. M2025-01058-CCA-R3-PC'. Matches the in-band row on 42 of 42.
_DOCKET = re.compile(
    r"^Nos?\.\s*([A-Z]\d{4}-\d{3,6}-CCA-[A-Z0-9-]+)", re.I)
# THE COURT BELOW gives its own number, and prints its judge beside it on
# the same visual row ('No. 21-26    Joseph T. Howell, Judge').
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
# clerk strikes it into the top-right margin as '07/02/2026'.
_STAMP_DATE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
# THE AUTHORSHIP ANNOUNCEMENT, read as a LABEL: an ALL-CAPS name, then a
# delivery verb over THE opinion. The verbs are core's own closed set; the
# ' the opinion' tail is what survives a row the page set with no spaces
# ('STEVEN W.SWORD,J.,delivered the opinion of the court, in whichROBERT L…').
_DELIVERS = ("delivered", "filed", "authored", "announced", "wrote")
_ANNOUNCES = re.compile(
    r"\b(?:" + "|".join(_DELIVERS) + r")\s+the\s+opinion\b", re.I)
# THE JOINED ROSTER, which the announcement carries in its own sentence:
# '…, in which TIMOTHY L. EASTER and STEVEN W. SWORD, JJ., joined.'
_JOINED = re.compile(r"\bin\s+which\b(.*?)\bjoin", re.I | re.S)
# THE PAPER'S OWN NAME, printed alone and centred where the court disposes
# of a case without a titled opinion. A closed vocabulary of labels.
_TITLE_HEADS = ("ORDER", "OPINION", "JUDGMENT", "PER CURIAM",
                "MEMORANDUM OPINION")
# THE ORIGIN opens on what an APPEAL is called, never on the name of any
# particular court — 40 of 42. The other two name the court below outright,
# and are confirmed by the lower-court docket row instead.
_ORIGIN_OPENERS = ("appeal", "direct appeal", "an appeal", "on appeal",
                   "appeal by permission", "appeal as of right",
                   "interlocutory appeal", "petition")
# THE DISPOSITION. The court closes its front matter with the rule it
# decided under and what it did, above the byline. Set in from the rail on
# all 40 that print one (76.3 to 201.4 against a 72.0 rail) and never at
# the paragraph indent, which is where the summary sets its opener.
_PARA_INDENT = 36.0                     # 108.0 against a 72.0 rail, all 42
_INDENT_SLOP = 3.0
_DISPOSITION_CUES = ("tenn. r. app. p.", "tenn r. app. p.",
                     "tenn. code ann.", "tenn. sup. ct. r.",
                     "tenn. r. crim. p.", "tenn. r. civ. p.",
                     "appeal as of right", "appeal by permission",
                     "extraordinary appeal", "interlocutory appeal",
                     "direct appeal", "accelerated interlocutory appeal")
# REPRESENTATION is a closed role vocabulary. Every appearance this court
# prints closes on one of these; a party or firm NAME is never read. The
# marks are tested against the row with its spaces removed as well as with
# them, because the extractor loses a space often enough that a literal
# match misses ('for the appellant,Hunter Jay Chantler').
_COUNSEL_MARKS = ("for the appell", "for appell", "for the petition",
                  "for petition", "for the respond", "for respond",
                  "for the amic", "for amic", "for the plaintiff",
                  "for the defendant", "for the state of", "pro se",
                  "on brief", "attorney general and reporter",
                  "assistant attorney general", "solicitor general",
                  "district public defender", "assistant public defender",
                  "district attorney general", "no appearance",
                  "guardian ad litem")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _tight(text: str) -> str:
    return _norm(text).upper().replace(" ", "")


def _is_banner(text: str) -> bool:
    """The court names itself on the top row of every paper it prints, then
    names the city it sat in underneath.

    Read WITHOUT the spaces, and as a CONTAINMENT on 'COURT OF CRIMINAL
    APPEALS' alone: the extractor loses a space often, and
    ``justin_james_cruger_wendricks`` prints the masthead short — 'IN THE
    COURT OF CRIMINAL APPEALS', with no 'OF TENNESSEE' after it."""
    flat = _norm(text).upper().rstrip(".")
    tight = flat.replace(" ", "")
    if "COURTOFCRIMINALAPPEALS" in tight:
        return True
    # 'AT JACKSON', 'AT NASHVILLE', 'AT KNOXVILLE' — and 'AT JACKSON1'
    # where a footnote mark is welded to it (cartwright, cohens).
    return flat.startswith("AT ") and len(flat) <= 24


def _sitting_value(text: str) -> str | None:
    """'May 6, 2026 Session' / 'Assigned on Briefs at Knoxville June 23,
    2026' — the day the Court took the case up, which is the only date the
    page sets in type. Returns the date as printed, or None."""
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
    """'ROBERT H. MONTGOMERY, JR., J., delivered the opinion of the court,
    in which … joined.' — an ALL-CAPS name, then a delivery verb over THE
    opinion."""
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
# the band — tenncrimapp's one section mark, and the dispatch
# --------------------------------------------------------------------------

def _type_axis(pm, geom) -> float:
    """The axis the court centres on: the middle of its own TYPE BLOCK.
    The right rail is the furthest any full-measure row reaches."""
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


def _underlines(pm, rule) -> bool:
    """A rule whose two ends coincide with the row just above it is that
    row's UNDERLINE, not a fence (overton's section head)."""
    for line in pm.lines:
        if not (0 < rule.top - line.top <= _UNDERLINE_DROP):
            continue
        if (abs(line.x0 - rule.x0) <= _UNDERLINE_ENDS
                and abs(line.x1 - rule.x1) <= _UNDERLINE_ENDS):
            return True
    return False


def _drawn_fences(pm, typed: list, axis: float) -> list:
    """…and the ones it STROKES instead. A rect sitting on a typed rule is
    that rule inked; the footnote separator is 162pt off the axis; a rect
    ruled under its own row is an underline. All three are refused."""
    tops = [l.top for l in typed]
    out = []
    for r in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - axis) > _FENCE_AXIS:
            continue
        if any(abs(r.top - t) <= _FENCE_SAME for t in tops):
            continue
        if _underlines(pm, r):
            continue
        out.append(r.top)
    return sorted(out)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="tenncrimapp")
def read_headmatter_tenncrimapp(model, geom, **_):
    """Read tenncrimapp's banded headmatter, or NOTHING."""
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
            # the reader is walking (price sets two).
            if (line.size or 0) < geom.body_size - _NOTE_STEP:
                continue
            # THE CLERK'S STAMP, struck into the right margin.
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
    # THE BAND IS A PAIR on all 42 records. Anything else is not this paper
    # and core's shared walk reads it better than a forced contract would.
    if len(marks) != 2:
        return NOTHING
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
        17064' beside 'Bruce I. Griffey, Judge') — one item, and every line
        id it was built from."""
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
    wide column gap (chantler's 'No. 17064' / 'Bruce I. Griffey,Judge'), and
    half an origin row is not an origin row."""
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

    A block may WRAP THE SHEET — chantler's appearances break mid-entry and
    finish at the top of page 2. The torn edge is the page's last row ending
    mid-clause under a continuation that opens the next page."""
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
    parser = BylineParser(TENNCRIMAPP.byline)
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

    # THE ORIGIN IS THE LAST BLOCK ABOVE THE BAND. Three blocks stand there
    # on every record — the court's name and sitting, the caption, the
    # origin — and only position separates the last two. Confirmed, not
    # decided: by the appeal recital on 40 records, and by the lower court's
    # own docket number on annesha_jackson and rediker, which print the
    # court below with no recital at all.
    above = [i for i, r in enumerate(vrows)
             if (r[0].page, r[0].top) < (1, band_top)]
    origin_at = None
    if above:
        cand = block_start[above[-1]]
        block = [_norm(" ".join(x.plain for x in vrows[k]))
                 for k in range(cand, block_at[cand][0])]
        if cand > 0 and (_is_origin_opener(block[0])
                         or any(_LOWER_NO.match(b) for b in block)):
            origin_at = cand
    if origin_at is None:
        return NOTHING            # no origin block: not this paper

    below = [r for r in vrows
             if (r[0].page, r[0].top) > (1, band_bottom)]

    # WHERE THE HEADMATTER ENDS: the writing's own banner, which all 42
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
    # powell's is set 'PJ.' and the shared grammar declines it; the reader
    # must still step over the block rather than read the appearances under
    # it as summary.
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
                    ctx.row(row, "banner")
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
            end, whole = block_at.get(idx, (idx + 1, text))
            _panel(ctx, whole)
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
        if _set_out(line, geom) and (_is_disposition(text) or dispositions):
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


def _set_out(line, geom) -> bool:
    """THE DISPOSITION IS SET IN FROM THE RAIL AND NEVER AT THE PARAGRAPH
    INDENT. 38 of the 40 set it bold; j.p._burrow and victor_gordon set
    their whole page 1 roman at x0=77.8 against a 72.0 rail, so weight
    alone reads those two as prose. The summary opens AT the indent (36.0pt
    on all 42) and wraps to the rail; no disposition in the corpus sits at
    either."""
    if line.all_bold:
        return True
    off = line.x0 - geom.body_x0
    return off > _INDENT_SLOP and abs(off - _PARA_INDENT) > _INDENT_SLOP


def _is_writing_banner(row: list, geom) -> bool:
    """The name the court sets over the writing itself — the same closed
    set core uses to find where an announcement byline's opinion begins.

    The word alone does not make the banner: a summary can break so that
    its last row is 'Opinion.' AT THE BODY RAIL. The banner is SET OUT —
    203.3 to 210.5pt in from the rail on all 42 — and the row carries
    nothing else. A footnote mark may be welded to it, so the trailing mark
    comes off before the comparison."""
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
    """'No. 21-26  Joseph T. Howell, Judge' -> the one number. The judge is
    recorded on his own, so the row is cut at the first piece that carries
    no digit."""
    out: list[str] = []
    for row in rows:
        for piece in row.split(","):
            token = piece.strip().split()[0].rstrip(",;.") \
                if piece.split() else ""
            if token and any(c.isdigit() for c in token):
                out.append(token)
    return out


def _panel(ctx: _Ctx, announcement: str) -> None:
    """The bench, from the announcement the author signs.

    The printed form is the announcement itself; the parsed form is the
    author plus the judges its 'in which … joined' clause names. Both are
    facts and one does not substitute for the other. ``roster_names`` is
    core's splitter — the titles ('J.', 'P.J.', 'JJ.') come off there and a
    generational suffix stays with its name, so 'ROBERT H. MONTGOMERY, JR.'
    is one judge and not two."""
    printed = _norm(announcement)
    ctx.crit.setdefault("panel_line", printed)
    author = _ANNOUNCES.split(printed)[0] if _ANNOUNCES.search(printed) \
        else printed
    names = roster_names(author)
    joined = _JOINED.search(printed)
    if joined:
        names += roster_names(_norm(joined.group(1)))
    seen: list[str] = []
    for name in names:
        if name and name not in seen:
            seen.append(name)
    if seen:
        ctx.crit["panel"] = seen
        ctx.crit["judges"] = ", ".join(seen)


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
