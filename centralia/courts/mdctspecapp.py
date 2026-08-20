"""Appellate Court of Maryland ('mdctspecapp'), formerly the Court of Special
Appeals.

Everything unique to mdctspecapp lives here. It imports core, never another
court file, and no other court file imports it. It is the SAME PUBLISHER as
`md` — the Maryland Judiciary's reporter sets both courts' slips on one press
— so the anatomy below is md's cover read again for this court's own name,
its own publication flag and the two structures md never prints (a docket
band BELOW a caption, and a byline band naming five writings). Nothing is
shared in code: md's reader is read, not imported.

WHAT THE DIVIDER IS, MEASURED. **A full-measure HORIZONTAL FENCE, off the
page axis, inside a caption column of its own — and there is no vertical
divider anywhere in this corpus.** Counted over all 30 records and all
1,144 pages: `v_rules` = 0. Not one. So this is neither ca6's drawn rail nor
pa's typed `:` column nor illappct's typed `)`; and it is not va's measured
x0 threshold either, because the page DOES draw (or type) its dividers — it
just draws them across the band instead of down the gutter. The nearest
measured sibling is scctapp ('DRAWN but HORIZONTAL: band fences on the page
axis, zero vertical rules corpus-wide'), with one difference that matters:

    mdctspecapp's fences are NOT on the page axis. They are centred at
    411.5–414.8 on a 612pt page whose axis is 306 — 106 to 109pt right of
    it — because the whole caption is set in a column of its own on the
    page's right half. On the one record the press shifted (mayor_city:
    every row 5.4pt right, column axis 433.3) the fence moves with the
    column, which is what proves the fence belongs to the column and not
    to the page.

THE FENCE'S MEASURE is invariant and it comes in both hands:

    TYPED, as a row of underscores  — 246.9-247.1pt, 122 fences on 29 records
    DRAWN, as a rect                — 252.0pt,         4 fences on 1 record
                                      (sudler_trotter, which types 2 more)

…and the three SHORT rects on every cover (67.2 / 165.7 / 95.0pt) are not
fences at all: their ends coincide with the row above them to a tenth of a
point, which is the general test for an UNDERLINE. They underline the
masthead — the publication flag and the two rows of the court's own name.

    Circuit Court for Washington County   10-13pt at the PAGE's rail: the
    Case No. C-21-CR-22-000291            court below and its number

                          REPORTED       underlined: the publication flag
                  IN THE APPELLATE COURT  underlined: the court, row 1
                        OF MARYLAND       underlined: the court, row 2
                          No. 1818        the docket
                    September Term, 2024  the sitting
              ______________________      a FENCE, 247pt, centre 414
                      BERQUAN CARROLL     the caption…
                             v.           …its printed pivot…
                     STATE OF MARYLAND    …and the other side
              ______________________      a FENCE
              Shaw,                       the roster: a LEFT-ALIGNED STACK
              Zic,                          — the page's own pivot
              Eyler, Deborah S.,
                 (Senior Judge, Specially Assigned),
                             JJ.
              ______________________      a FENCE
              Opinion by Eyler, Deborah S., J.   the byline — the WRITING's,
              ______________________              never claimed
              Filed: July 8, 2026         the day it was filed

THE BANDS ARE NOT AT FIXED INDICES, and the band — never the row — is the
unit of meaning. Four fences on 25 records, five on 4, six on sudler_trotter
(4 drawn + 2 typed), and thomas_v._state types two with NOTHING between
them. A band is named by what it holds:

  - the ROSTER band is the one whose rows form a LEFT-ALIGNED STACK (three
    or more rows sharing one x0 to 1.5pt). There is exactly one per cover
    and it is the page's pivot: above it, masthead-or-docket bands and the
    caption; the band below it is the byline; anything below that is the
    filing date and the reporter's non-participation note. The note bands
    ALSO stack (3-4 rows on x0=288), which is why the FIRST stack wins.
  - a HEAD band is one every row of which is a closed structural form: the
    publication flag, the court's own name, a docket, a sitting, or one of
    the two sitting labels the court prints ('IN BANC', 'CONSOLIDATED
    CASES').
  - everything else above the roster is CAPTION.

TWO STRUCTURES md DOES NOT PRINT, and both are the reason this file exists
rather than a `court=` line added to md's decider:

  - A DOCKET BAND BELOW A CAPTION. sudler_trotter consolidates two appeals
    and sets each docket over its own parties, in the combined form
    'No. 157, September Term, 2024' — docket and sitting on ONE row. md's
    reader latches `caption_open` on the first caption band and reads every
    later head band as caption, which would file 'No. 1399, September Term,
    2024' as a party. Here the FORM decides each band, at every depth.
  - A BYLINE BAND NAMING FIVE WRITINGS. hicks_v._state sits in banc and
    lists 'Opinion by Graeff, J.' / 'Joint Concurring Opinion by Berger,
    Friedman, and Shaw, JJ.' / three more concurrences. md passes over only
    the FIRST unit of that band; every unit here is tested, so none of the
    five is claimed away from its writing.

CITATION IS NOT DOCKET, and this court prints both kinds of number in
three distinct roles, kept distinct:

    'No. 1818' / 'Nos. 1187 & 2058'        -> criteria.docket_number, and
    'No. 157, September Term, 2024'           any second one to
                                              criteria.other_dockets
    'September Term, 2024'                 -> the SITTING (role `date`)
    'Case No. C-21-CR-22-000291'           -> criteria.lower_court_docket
    'Estate No. W108771'                      (role `lower-court`) — the
    'Case Nos. C-23-CR-23-000157,'            number the court BELOW gave
       'C-23-CR-24-000068'                    the case, wrap included

No record in this corpus prints a public-domain citation, so
`criteria.citation` is left alone rather than guessed at.

WHAT THE READER DOES NOT TOUCH. The byline ('Opinion by Ripken, J.') is the
WRITING's: the reader stops short of every byline-shaped unit in the byline
band and lets assembly anchor on it exactly as it does for any other court.
mdctspecapp prints no appearance of counsel anywhere in the corpus, and — the
finding this port was asked for — NO '/s/' SIGNATURE BAND either: zero
occurrences over 30 records and 1,144 pages, against 10 over the first 12
records of md alone. md's signature-band epic is md's alone (its per curiam
attorney-grievance orders); the `signature` seam is not this court's problem,
so nothing is returned under that key.

THE REPORTER'S HEADNOTE PAGES come BEFORE the cover — one on 24 records, two
on 4, three on 2, never none. An attribution line (which the reporter wraps,
and whose continuation row 'Ripken, J.' looks exactly like a byline), then
an optional 'HEADNOTES' label, then BOLD topical headings each over a roman
précis. They stay in the headmatter — the block renders WHOLE — marked
`case-info`, `headnotes` and `summary`.

THE COVER IS THE FIRST ONE. hicks_v._state repeats the whole cover before
each separate writing (pp. 54, 89, 111, 126, fences 214.5pt because the
column is set narrower there). Those rows stand BETWEEN writings, not in the
headmatter, and lifting them into a block that renders at the top of the
document would move them off the page they are printed on — so only the
document's own cover is claimed.

CORE DEFECTS THIS READER RAN INTO AND DID NOT PATCH (reported, not fixed):

  1. `resolve/bylines.BylineParser` with `style="abbrev"` cannot read the
     reporter's INVERTED FULL-NAME byline, 'Opinion by Eyler, Deborah S.,
     J.' (carroll_v._state). The v1 engine read it — old md.py's `_md_author`
     had a branch for exactly this shape. Unread, the row stays in the stream
     and becomes the writing's first PARAGRAPH, and the lead opinion comes
     back authorless.
  2. The same parser cannot read a JOINT byline, 'Joint Concurring Opinion by
     Berger, Friedman, and Shaw, JJ.' (hicks_v._state), nor one WRAPPED over
     two rows ('Concurring Opinion by Berger, J.,' / 'Friedman, J., and
     Shaw, J.', hicks p. 54). v1 finds 6 writings in hicks; we find 1. Both
     with and without this reader — it is an assembly gap, not a reading one.
  3. `classify.classify_doc_type` takes its heading candidates from the front
     of the document, and on this press the front of the document is the
     REPORTER'S TOPICAL HEADNOTES. 'PLEA - REVIEWABLE AFTER FINAL JUDGMENT'
     typed malvo_v._state a `judgment` — a type for which an empty body is
     CORRECT output. Six of 30 records were mistyped before this reader
     declared `doc_type_final`.
  4. `criteria.judges` is reachable only through a LABELLED roster
     ('Before:', 'Panel:', 'Present:'). This court fences a bare stack, so
     the criterion was empty on all 30. Closed here, in the court's own file,
     exactly as core-patch queue item 41 says six courts closed
     `criteria.attorneys`.
"""

from __future__ import annotations

import re

from .. import model as m
from ..pdfio.model import Line
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.headmatter import find_date
from . import get_profile

# mdctspecapp's profile is registered in `courts/__init__.py`; this file adds
# only the reader, so importing it can never raise a duplicate registration.
# It is read for the assertion, not for a grammar: this reader tests the
# byline's printed FORM and never parses a name (see the byline note below).
assert get_profile("mdctspecapp") is not None

STYLE_COVER = "column fences"

# ---- declared facts, measured over the 30-record corpus ------------------
# THE FENCE. Typed 246.9-247.1 on 122 fences over 29 records; drawn 252.0 on
# the 4 of sudler_trotter. The masthead UNDERLINES are 67.2 / 165.7 / 95.0
# and are never in this band.
_FENCE_MEASURE = (244.0, 254.0)
# …and it stands OFF THE PAGE AXIS, because the column does: 106-127pt.
_OFF_AXIS_MIN = 60.0
# The fences of one cover agree on their centre to 3.3pt (a typed rule's ends
# fall where the last underscore's ink does, which wanders by ~2.5pt).
_AXIS_SPREAD = 12.0
# HOW FAR FORWARD THE COVER MAY BE: three headnote pages is the corpus
# maximum (mayor_city, wittwer). Eight leaves room and still refuses to call
# a repeated mid-document cover the document's own.
_MAX_HEAD_PAGES = 8
# THE COLUMN'S OWN LEFT EDGE is the fence's x0; nothing in the column starts
# left of it, and the origin block starts 216pt further left again.
_COL_SLACK = 60.0
# THE ROSTER IS A STACK: three or more rows sharing one left edge.
_STACK_TOL = 1.5
_STACK_MIN = 3
# An UNDERLINE's ends coincide with the row above it (0.1pt on this press;
# 2.0 is the shared tolerance every ruled court uses).
_UNDERLINE_TOL = 2.0
_UNDERLINE_DROP = 16.0

# ---- the closed vocabularies --------------------------------------------
# THE COURT NAMING ITSELF, in the forms this press sets it in — two rows on
# every record in the corpus, plus the whole-line and former-name forms the
# same reporter used before the 2022 renaming. A closed vocabulary of ONE
# court's own names, never a party and never the court below.
_COURT_ROWS = frozenset({
    "IN THE APPELLATE COURT", "OF MARYLAND",
    "IN THE APPELLATE COURT OF MARYLAND",
    "APPELLATE COURT OF MARYLAND",
    "IN THE COURT OF SPECIAL APPEALS",
    "IN THE COURT OF SPECIAL APPEALS OF MARYLAND",
    "COURT OF SPECIAL APPEALS", "COURT OF SPECIAL APPEALS OF MARYLAND",
})
# THE PUBLICATION FLAG. It is underlined exactly as the court's name is, so
# the underline cannot tell them apart — the flag is its own closed
# vocabulary and it is NOT the court naming itself (the user's ruling,
# 2026-08-19: a banner that names the court IS the court, and this one does
# not).
_PUBLICATION = {"REPORTED": "published", "UNREPORTED": "unpublished"}
# 'No. 1818' / 'Nos. 1187 & 2058' / 'No. 69' — an optional leader, the word
# No., and the numbers it names.
_DOCKET = re.compile(r"^(?:[A-Z][A-Za-z.]{0,11}\s+){0,2}Nos?\.\s*\d+[\d,&\s]*$")
# 'September Term, 2024' / 'Sept. Term, 2025' — the sitting.
_TERM = re.compile(r"^[A-Z][a-z]+\.?\s+Term,?\s+\d{4}\.?$")
# 'No. 157, September Term, 2024' — sudler_trotter sets the docket and the
# sitting on ONE row, once per consolidated appeal.
_DOCKET_TERM = re.compile(
    r"^(Nos?\.\s*\d+[\d,&\s]*?),\s*([A-Z][a-z]+\.?\s+Term,?\s+\d{4})\.?$")
# 'IN BANC' — how the bench sat, in its own band above the caption.
_SITTING = frozenset({"IN BANC", "EN BANC", "IN BANC REVIEW"})
# 'CONSOLIDATED CASES' — the reporter's own statement that this paper decides
# more than one appeal, again in a band of its own.
_CONSOLIDATED = re.compile(r"^CONSOLIDATED CASES?$")
# 'Filed: July 8, 2026' / 'Argued: January 5, 2026' — a labelled date.
_DATED = re.compile(r"^(Filed|Argued|Submitted|Decided|Reargued)\s*:?\s*(.+)$")
# 'Circuit Court for Washington County' / "Orphans' Court for Montgomery
# County' — the origin block's leader.
_ORIGIN_LEAD = ("circuit court", "district court", "orphans' court",
                "orphans’ court", "court of special appeals",
                "appellate court", "supreme court", "board of",
                "workers' compensation", "workers’ compensation")
# 'Case No. C-21-CR-22-000291' / 'Case Nos. C-23-CR-23-000157,' / 'Estate
# No. W108771' / '(Cir. Ct. No. …)' — the number a court BELOW gave the case.
_LOWER_NO = re.compile(
    r"^\(?\s*(?:Cir\.\s*Ct\.\s*)?(?:Case|Estate|Petition|Claim)\s*Nos?\.?\s*:?"
    r"\s*(.+?)\)?$", re.I)
# …and the row it wraps onto carries nothing but another such number.
_BARE_CASE_NO = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{5,}[,;]?$")
# The pivot: a row whose whole ink is 'v.'.
_PIVOT = re.compile(r"^v\.?$", re.I)
# 'JJ.' / 'J.' — the roster's closing bench abbreviation.
_BENCH_CLOSE = re.compile(r"^J{1,2}\.$")
# THE BYLINE, as this press sets it: an optional kind, then 'Opinion by',
# then who. A STRUCTURAL form, not a name test — which matters because the
# shared BylineParser cannot read two of the three shapes printed here (the
# CORE DEFECTS note in the module docstring above), and a reader that trusted
# it would claim the document's only statement of authorship into the
# headmatter.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z]*\s+)*?(?:Opinion|Statement)\s+by\s+\S", re.I)
# The reporter's note on who took no part in the decision to report the
# opinion — set below the last fence, keyed to an asterisk, on 6 records.
_NO_PART = re.compile(r"did not participate", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------

def _rows(lines: list[Line], tol: float = 2.5) -> list[list[Line]]:
    """Lines grouped into the visual rows the page set them on."""
    out: list[list[Line]] = []
    for line in sorted(lines, key=lambda l: (l.top, l.x0)):
        if out and abs(out[-1][0].top - line.top) <= tol:
            out[-1].append(line)
        else:
            out.append([line])
    for group in out:
        group.sort(key=lambda l: l.x0)
    return out


def _row_text(group: list[Line]) -> str:
    return _norm(" ".join(l.plain for l in group))


def _row_bold(group: list[Line]) -> bool:
    """THE WEIGHT OF A ROW IS THE WEIGHT OF ITS INK, taken over the whole row
    and not Line by Line. `Line.all_bold` already lets punctuation abstain,
    but pdfio hands back the reporter's bold topical heading as seven Lines
    on one baseline — one of them the en dash alone, which HAS no
    alphanumeric glyph and so answers False. Read per Line, 'INTERSTATE
    AGREEMENT ON DETAINERS (IAD) - 180-DAY' / 'REQUIREMENT' came back as two
    units of different weight instead of one wrapped heading (2 records)."""
    seen = False
    for line in group:
        for c in line.chars:
            t = c.get("text") or ""
            if not t.strip() or not t.isalnum():
                continue
            seen = True
            if "Bold" not in (c.get("fontname") or ""):
                return False
    return seen


def _row_markup(group: list[Line]) -> str:
    out = ""
    for line in group:
        piece = line_markup(line)
        out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() else piece
    return out


def _join_markup(pieces: list[str]) -> str:
    """Wrapped rows as one statement. A row ENDING on a hyphen closed a word
    the measure broke; joined with a space it reads as an unclosed
    hyphenation."""
    out = ""
    for piece in pieces:
        piece = piece.strip()
        if not out:
            out = piece
        elif out.endswith("-") and piece[:1].islower():
            out += piece
        else:
            out += " " + piece
    return out


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

class _Fence:
    """One band divider of the caption column, drawn or typed."""

    __slots__ = ("top", "x0", "x1", "lines")

    def __init__(self, top: float, x0: float, x1: float, lines: list):
        self.top, self.x0, self.x1, self.lines = top, x0, x1, lines

    @property
    def center(self) -> float:
        return (self.x0 + self.x1) / 2


def _fences(pm) -> list[_Fence]:
    """The band dividers of this page's caption column — the TYPED underscore
    rows and the DRAWN rects both, and neither the masthead's three
    underlines nor anything centred on the page."""
    found: list[_Fence] = []
    for rule in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= rule.width <= _FENCE_MEASURE[1]):
            continue
        if abs((rule.x0 + rule.x1) / 2 - pm.width / 2) < _OFF_AXIS_MIN:
            continue
        found.append(_Fence(rule.top, rule.x0, rule.x1, []))
    for group in _rows(pm.lines):
        text = _row_text(group).replace(" ", "")
        if len(text) < 12 or set(text) != {"_"}:
            continue
        x0 = min(l.x0 for l in group)
        x1 = max(l.x1 for l in group)
        if not (_FENCE_MEASURE[0] <= x1 - x0 <= _FENCE_MEASURE[1]):
            continue
        if abs((x0 + x1) / 2 - pm.width / 2) < _OFF_AXIS_MIN:
            continue
        found.append(_Fence(group[0].top, x0, x1, list(group)))
    found.sort(key=lambda f: f.top)
    if len(found) < 3:
        return []
    # THE FENCES OF ONE COVER AGREE ON THEIR CENTRE. Anything that does not
    # belongs to some other structure.
    centers = sorted(f.center for f in found)
    axis = centers[len(centers) // 2]
    found = [f for f in found if abs(f.center - axis) <= _AXIS_SPREAD]
    return found if len(found) >= 3 else []


def _underlined(pm, group: list[Line]) -> bool:
    """A drawn rule whose ends coincide with this row is an UNDERLINE. On this
    cover only the masthead — the publication flag and the court's own name —
    carries one."""
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    foot = max(l.bottom for l in group)
    return any(abs(r.x0 - x0) <= _UNDERLINE_TOL
               and abs(r.x1 - x1) <= _UNDERLINE_TOL
               and 0 <= r.top - foot <= _UNDERLINE_DROP
               for r in pm.h_rules)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom):
        self.model = model
        self.geom = geom
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.anchors: list = []
        self.doc_type: object = None
        self.byline_seen = False

    def line(self, group: list[Line], role: str, align: str = "L",
             rel: float = 0.0, text: str | None = None) -> m.HmLine:
        first = group[0]
        return m.HmLine(
            text=text if text is not None else _row_markup(group),
            prov=m.Prov(first.page, tuple(l.id for l in group)),
            align=m.Align(align), x0=first.x0,
            size=max(l.size or 0.0 for l in group),
            bold=_row_bold(group), rel=rel, role=role)

    def emit(self, group: list[Line], role: str, align: str = "L",
             rel: float = 0.0, text: str | None = None) -> m.HmLine:
        row = self.line(group, role, align, rel, text)
        self.items.append(row)
        self.consumed.update(row.prov.line_ids)
        return row

    def fence(self, fence: _Fence, after: m.HmLine | None) -> None:
        """A FENCE RENDERS WHERE THE PAGE DREW IT.

        A TYPED fence is a row of its own, so it carries its own line ids —
        which both places it exactly and PLACES ITS TEXT: given the prov of
        another row instead, its underscores are consumed and never recorded,
        and come back as residual furniture. A DRAWN fence has no line to
        carry, and core sorts an id-less item to the position of its
        neighbour, so it borrows the prov of the row it stands under."""
        if fence.lines:
            prov = m.Prov(fence.lines[0].page,
                          tuple(l.id for l in fence.lines))
        elif after is not None:
            prov = m.Prov(after.prov.page, after.prov.line_ids)
        else:
            prov = m.Prov(self.model.pages[0].number)
        self.items.append(m.Rule(prov=prov, typed=bool(fence.lines),
                                 span="center"))
        self.consumed.update(l.id for l in fence.lines)

    def add(self, key: str, value) -> None:
        if isinstance(value, list):
            bucket = self.crit.setdefault(key, [])
            for v in value:
                if v not in bucket:
                    bucket.append(v)
        elif self.crit.get(key) is None:
            self.crit[key] = value

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchors, "doc_type_final": self.doc_type}


# ---- the reporter's headnote pages ---------------------------------------

def _read_headnotes(ctx: _Ctx, pages: list) -> None:
    """The page(s) the reporter sets before the cover: a wrapped attribution
    line, an optional 'HEADNOTES' label, then BOLD topical headings each over
    a roman précis. Every unit wraps over several rows and a BLANK BAND is
    the separator — so a run of consecutive rows of one weight is one row of
    the block. This is what keeps the attribution's own continuation row
    ('Ripken, J.', on 4 records) from reading as a byline."""
    # A BLANK BAND IS THE SEPARATOR, and it is measured against the page's own
    # leading: a gap of more than 1.45 leadings opens a new band.
    bands: list[list[list[Line]]] = []
    for pm in pages:
        rows = [g for g in _rows(pm.lines) if _row_text(g)]
        if not rows:
            continue
        steps = sorted(rows[i + 1][0].top - rows[i][0].top
                       for i in range(len(rows) - 1))
        step = steps[len(steps) // 2] if steps else 15.0
        prev_top = None
        for group in rows:
            if prev_top is None or group[0].top - prev_top > step * 1.45:
                bands.append([group])
            else:
                bands[-1].append(group)
            prev_top = group[0].top
    # THE FIRST BAND IS THE ATTRIBUTION, whatever weights it mixes. The
    # reporter sets it three ways across the corpus — one roman row, a roman
    # row and its wrap, or (mayor_city) a BOLD case name over a roman docket
    # and a roman byline — so a run-of-one-weight rule broke it into a
    # 'headnotes' heading plus a 'summary' on that record, publishing the
    # case's own name as a topical headnote. Inside every LATER band the
    # weight still divides the bold topical heading from its roman precis,
    # because mayor_city sets those two with no blank band between them.
    groups: list[list[list[Line]]] = []
    for index, band in enumerate(bands):
        if index == 0:
            groups.append(band)
            continue
        run: list[list[Line]] = []
        for group in band:
            if run and _row_bold(run[-1]) != _row_bold(group):
                groups.append(run)
                run = []
            run.append(group)
        if run:
            groups.append(run)
    for index, unit in enumerate(groups):
        flat = [l for g in unit for l in g]
        bold = _row_bold(flat)
        # THE ATTRIBUTION LINE opens the block: the reporter's own statement
        # of what this paper is ('<case>, No. 1818, September Term, 2024.
        # Opinion by Eyler, J. Filed July 8, 2026.'). It is caption
        # apparatus, not a headnote and not a byline.
        role = "case-info" if index == 0 and not bold else (
            "headnotes" if bold else "summary")
        ctx.items.append(m.HmLine(
            text=_join_markup([_row_markup(g) for g in unit]),
            prov=m.Prov(flat[0].page, tuple(l.id for l in flat)),
            align=m.Align("L"), x0=flat[0].x0,
            size=max(l.size or 0.0 for l in flat), bold=bold, role=role))
        ctx.consumed.update(l.id for l in flat)


# ---- the cover's own origin block ----------------------------------------

def _read_origin(ctx: _Ctx, pm, lines: list[Line]) -> None:
    """The block at the page's own rail: the court below and the number it
    gave the case. sudler_trotter WRAPS that number over two rows, so a bare
    case-number row continues the one above it."""
    last_was_number = False
    for group in _rows(lines, tol=1.5):
        text = _row_text(group)
        if not text:
            continue
        low = text.lower()
        dated = _DATED.match(text)
        if dated and find_date(dated.group(2)):
            value = find_date(dated.group(2))
            ctx.emit(group, "date")
            if dated.group(1) in ("Argued", "Submitted", "Reargued"):
                ctx.add("submitted", value)
            else:
                ctx.add("decision_date", value)
            last_was_number = False
            continue
        number = _LOWER_NO.match(text)
        if number:
            ctx.emit(group, "lower-court")
            ctx.add("lower_court_docket", [_norm(number.group(1)).rstrip(",;")])
            last_was_number = True
            continue
        if last_was_number and _BARE_CASE_NO.match(text):
            # the wrap of the row above, not a new field
            ctx.emit(group, "lower-court")
            ctx.add("lower_court_docket", [text.rstrip(",;")])
            continue
        ctx.emit(group, "lower-court")
        last_was_number = False
        if any(low.startswith(lead) for lead in _ORIGIN_LEAD):
            prev = ctx.crit.get("lower_court")
            ctx.crit["lower_court"] = f"{prev}; {text}" if prev else text


# ---- the cover -----------------------------------------------------------

def _head_form(pm, group: list[Line]) -> str | None:
    """The role of one row IF it is a closed structural form of the masthead;
    None if it is not, which is what makes its band a caption band."""
    text = _row_text(group)
    upper = text.upper()
    if upper in _PUBLICATION:
        return "publication"
    if upper in _COURT_ROWS:
        return "court"
    if _DOCKET_TERM.match(text) or _DOCKET.match(text):
        return "docket"
    if _TERM.match(text):
        return "date"
    if upper in _SITTING:
        return "panel"
    if _CONSOLIDATED.match(upper):
        return "case-info"
    # A row the press UNDERLINED is masthead by construction — but only where
    # nothing else claimed it, so a party name can never be taken for the
    # court's own name on the strength of a rule.
    if _underlined(pm, group) and upper == text and len(text) <= 40:
        return "court"
    return None


def _is_stack(band: list[list[Line]]) -> bool:
    """A ROSTER IS A STACK — three or more rows on one left edge."""
    if len(band) < _STACK_MIN:
        return False
    xs = [g[0].x0 for g in band]
    for x in xs:
        if sum(1 for other in xs if abs(other - x) <= _STACK_TOL) >= _STACK_MIN:
            return True
    return False


def _read_cover(ctx: _Ctx, pm, fences: list[_Fence]) -> bool:
    axis = sorted(f.center for f in fences)[len(fences) // 2]
    col_x0 = min(f.x0 for f in fences)
    fence_ids = {l.id for f in fences for l in f.lines}
    lines = [l for l in pm.lines if l.plain.strip() and l.id not in fence_ids]
    # THE ORIGIN BLOCK IS AT THE PAGE'S RAIL, and the split is by x0, not x1:
    # 'Circuit Court for Prince George's County' runs to x1=288.1, which is
    # PAST the column's own left edge, so an x1 test files it in the column
    # (3 records) while an x0 test never can — the column's leftmost row
    # starts exactly on the fence.
    origin = [l for l in lines if l.x0 < col_x0 - _COL_SLACK]
    column = [l for l in lines if l.x0 >= col_x0 - _COL_SLACK]

    bands: list[list[list[Line]]] = []
    edges = [f.top for f in fences]
    for group in _rows(column):
        index = sum(1 for e in edges if group[0].top > e)
        while len(bands) <= index:
            bands.append([])
        bands[index].append(group)
    if not any(bands):
        return False

    # THE ROSTER BAND IS THE PAGE'S PIVOT. The reporter's non-participation
    # note stacks too (3-4 rows on one x0, below the filing date), so the
    # FIRST stack is the roster.
    stack = next((i for i, b in enumerate(bands) if _is_stack(b)), None)
    if stack is None:
        return False

    if origin:
        _read_origin(ctx, pm, origin)

    last: m.HmLine | None = None
    for index, band in enumerate(bands):
        if index and index - 1 < len(fences):
            ctx.fence(fences[index - 1], last)
        if not band:
            continue                      # thomas_v._state types two fences
        if index == stack:                # …with nothing between them
            last = _read_roster(ctx, band, col_x0)
        elif index < stack:
            forms = [_head_form(pm, g) for g in band]
            if all(f is not None for f in forms):
                last = _read_head(ctx, band, forms, axis) or last
            else:
                last = _read_caption(ctx, band, axis) or last
        else:
            # EVERY BAND BELOW THE ROSTER, not the one at stack + 1.
            # thomas_v._state types two fences with NOTHING between them, so
            # its byline band is at stack + 2 — read by index, the byline was
            # claimed as `case-info` and the writing lost its author and its
            # type (a reported opinion came back an 'order').
            last = _read_below(ctx, band) or last
    for extra in range(len(bands) - 1, len(fences)):
        ctx.fence(fences[extra], last)
    ctx.crit["headmatter_style"] = STYLE_COVER
    return True


def _read_head(ctx: _Ctx, band, forms: list[str], axis: float):
    """One masthead band, row by row — the flag, the court, the numbers, the
    sitting. Each row is a closed form and it says its own role."""
    last = None
    for group, role in zip(band, forms):
        text = _row_text(group)
        last = ctx.emit(group, role, "C")
        if role == "publication":
            ctx.add("publication_status", _PUBLICATION[text.upper()])
        elif role == "court":
            prev = ctx.crit.get("court")
            ctx.crit["court"] = _norm(f"{prev} {text}") if prev else text
        elif role == "docket":
            combined = _DOCKET_TERM.match(text)
            number = combined.group(1) if combined else text
            # CITATION IS NOT DOCKET AND A COMPANION APPEAL IS NOT EITHER:
            # the first number is this appeal's docket, a second one is the
            # appeal consolidated into it.
            if ctx.crit.get("docket_number") is None:
                ctx.crit["docket_number"] = number
            else:
                ctx.add("other_dockets", [number])
        elif role == "panel":
            # 'IN BANC' — how the bench sat. It is the roster speaking, so it
            # opens `panel_line`; it is not a judge, so it never enters
            # `panel`.
            prev = ctx.crit.get("panel_line")
            ctx.crit["panel_line"] = _norm(f"{prev} {text}") if prev else text
    return last


def _read_roster(ctx: _Ctx, band, col_x0: float):
    """The roster, as printed and as parsed. A row opening on '(' continues
    the judge above it ('Eyler, Deborah S.,' / '(Senior Judge, Specially
    Assigned),'), and the closing 'JJ.' is a bench abbreviation, not a
    name."""
    names: list[str] = []
    printed: list[str] = []
    last = None
    for group in band:
        text = _row_text(group)
        last = ctx.emit(group, "panel", "L",
                        rel=max(0.0, group[0].x0 - col_x0))
        printed.append(text)
        # STRIP THE SEPARATOR, NOT THE ABBREVIATION. `rstrip(',. ')` takes
        # the period that MAKES the name ('Wells, C.J.' -> 'Wells, C.J',
        # 'Zarnoch, Robert A.' -> 'Zarnoch, Robert A') — 26 of 30 rosters.
        bare = text.rstrip(", ")
        if _BENCH_CLOSE.match(text):
            continue
        if text.startswith("(") and names:
            names[-1] = f"{names[-1]} {text.rstrip(',')}"
        elif bare:
            names.append(bare)
    if names:
        ctx.add("panel", names)
    if printed:
        line = " ".join(printed)
        prev = ctx.crit.get("panel_line")
        # `panel_line` is the roster AS PRINTED, and on hicks_v._state that
        # includes the band above it saying how the bench sat ('IN BANC').
        ctx.crit["panel_line"] = f"{prev} {line}" if prev else line
        # THE BENCH, AS A STRING — the roster's own rows and nothing else.
        # `criteria.judges` is filled by the shared walk only from a LABELLED
        # roster ('Before:', 'Panel:', 'Present:'); this court prints a bare
        # stack under a fence and never a label, so the criterion is
        # UNREACHABLE for it — the same shape as core-patch queue item 41
        # (`criteria.attorneys` unreachable for a reader that keeps counsel
        # in the headmatter, confirmed on six courts), and it is closed here
        # in the court's own file exactly as those six closed theirs.
        ctx.crit["judges"] = line
    return last


def _read_caption(ctx: _Ctx, band, axis: float):
    """One caption band: the party names either side of the printed pivot.
    THE BAND declares the centring, so a party row set wide of the column's
    axis is still centred and never renders as an indent."""
    last = None
    left: list[str] = []
    right: list[str] = []
    side = left
    rows: list[str] = []
    for group in band:
        text = _row_text(group)
        last = ctx.emit(group, "caption", "C")
        rows.append(text)
        if _PIVOT.match(text):
            side = right
            continue
        side.append(text)
    ctx.add("caption", rows)
    lead = _norm(" ".join(left)).rstrip(",; ")
    trail = _norm(" ".join(right)).rstrip(",; ")
    if lead and not ctx.crit.get("parties"):
        ctx.crit["parties"] = [lead, trail] if trail else [lead]
        ctx.crit["case_name"] = f"{lead} v. {trail}" if trail else lead
    return last


def _units(band: list[list[Line]]) -> list[list[list[Line]]]:
    """The band's rows grouped into the STATEMENTS they wrap into. Every
    statement this press sets below the roster is a sentence, so a row that
    does not end on a full stop is still mid-statement ('Joint Concurring
    Opinion by Berger, Friedman,' / 'and Shaw, JJ.') — EXCEPT a labelled
    date, which ends on its year and is complete ('Filed: May 1, 2026'
    followed by '*Kehoe, Stephen J. did not participate in the' welded the
    filing date onto the reporter's note on 6 records)."""
    units: list[list[list[Line]]] = []
    for group in band:
        if units:
            prior = _row_text(units[-1][-1]).rstrip()
            closed = prior.endswith(".") or bool(_DATED.match(
                _norm(" ".join(_row_text(g) for g in units[-1]))))
            if not closed:
                units[-1].append(group)
                continue
        units.append([group])
    return units


def _read_below(ctx: _Ctx, band):
    """A band below the roster: the bylines, the filing date, and — on 6
    records — the reporter's note that a judge took no part in the decision
    to report the opinion.

    THE BYLINE IS THE WRITING'S. 'Opinion by Ripken, J.' is what assembly
    anchors an opinion on, and a reader that claims it takes the document's
    only statement of who wrote it out of the writing — so EVERY byline-shaped
    unit here is passed over, in every band and not merely the first of one.
    hicks_v._state lists five bylines in one band (md's reader tests only the
    leading unit of it), and thomas_v._state prints its one byline a band
    lower than every other record because it types two fences with nothing
    between them."""
    last = None
    for unit in _units(band):
        text = _norm(" ".join(_row_text(g) for g in unit))
        if _BYLINE.match(text):
            ctx.byline_seen = True
            continue
        flat = [l for g in unit for l in g]
        dated = _DATED.match(text)
        role = "date" if dated and find_date(dated.group(2)) else (
            "panel" if _NO_PART.search(text) else "case-info")
        last = ctx.emit(flat, role, "C",
                        text=_join_markup([_row_markup(g) for g in unit]))
        if role == "date":
            value = find_date(dated.group(2)) or dated.group(2).strip()
            if dated.group(1) in ("Argued", "Submitted", "Reargued"):
                ctx.add("submitted", value)
            else:
                ctx.crit["decision_date"] = value
    return last


# --------------------------------------------------------------------------
# the dispatch
# --------------------------------------------------------------------------

@decider("headmatter.read", court="mdctspecapp")
def read_headmatter_mdctspecapp(model, geom, **_):
    """One question about the front of the document, and it is about rules the
    page sets: does a page in the first eight carry THREE OR MORE fences of
    the column's measure, off the page axis, agreeing on their centre? That
    page is the cover; the pages before it are the reporter's headnotes. A
    record answering no is not this paper and gets NOTHING."""
    if not model.pages:
        return NOTHING
    cover = None
    fences: list[_Fence] = []
    for pm in model.pages[:_MAX_HEAD_PAGES]:
        found = _fences(pm)
        if found:
            cover, fences = pm, found
            break
    if cover is None:
        return NOTHING

    ctx = _Ctx(model, geom)
    if cover.number > 1:
        _read_headnotes(ctx, model.pages[:cover.number - 1])
    if not _read_cover(ctx, cover, fences):
        return NOTHING
    # THE PAPER NAMES ITSELF BY PRINTING A BYLINE BAND. Where a band below
    # the roster holds a unit of the form '<kind> Opinion by <who>', this
    # court has issued an opinion — a landmark, not a word test. Stated,
    # because the shared classifier reads the paper's type from the first
    # heading-shaped row it finds, and on this press those rows are the
    # REPORTER'S TOPICAL HEADNOTES, printed pages before the cover:
    # 'PLEA - REVIEWABLE AFTER FINAL JUDGMENT' typed malvo_v._state a
    # `judgment` (a type for which an empty body is correct output), and a
    # cover whose byline the shared grammar cannot read left carroll_v._state
    # an `order`. Six of 30 records were mistyped this way before the reader
    # spoke. Silent where no byline band prints, so nothing is invented.
    if ctx.byline_seen:
        ctx.doc_type = m.DocType.OPINION
    if ctx.crit.get("court"):
        ctx.crit["court"] = _norm(ctx.crit["court"])
    return ctx.result()
