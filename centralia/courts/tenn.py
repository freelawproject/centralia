"""Supreme Court of Tennessee ('tenn').

Everything unique to tenn lives here. It imports core, never another court
file, and no other court file imports it.

THE PROFILE. tenn's ``CourtProfile`` stays in ``courts/__init__.py``: its
byline grammar (``_TENN_GRAMMAR``) is shared DATA, referenced by name from
the two intermediate Tennessee courts that print the same announcement
byline. Shared data by reference is the established pattern; moving the
registration here would either duplicate the grammar or make one court file
import another. The profile is fetched, not re-registered.

THE CONTRACT. Tennessee sets ONE paper and fences ONE thing on it: its own
docket number stands alone in a band nothing else shares. Everything above
that band is the case's identity; everything below it is the court's own
front matter, down to the row where the writing begins.

    06/16/2025                             the clerk's stamp — furniture,
                                           and the only release date printed
    IN THE SUPREME COURT OF TENNESSEE      the banner, 15.1pt, centred
    AT JACKSON                             …and where the Court sat
    November 6, 2024 Session               the sitting: argued / assigned
    STATE OF TENNESSEE v. PERVIS TYRONE …  the caption, BOLD
    Appeal by Permission from the Court …  the origin, bold, centred
    Criminal Court for Shelby County       …the court below…
    Nos. 87-04408, …    Paula L. Skahan, Judge   …its docket and its judge,
                                                 ONE row set as two cells
    ______________________________         the fence, ON THE AXIS…
    No. W2022-00210-SC-R11-CD              …around THIS court's docket…
    ______________________________         …and one under it
    This case is about a court's authority…    the summary
    Tenn. R. App. P. 11 Appeal by Permission;  the disposition, BOLD
    SARAH K. CAMPBELL, J., delivered the …     the authorship announcement
    Jonathan Skrmetti, Attorney General …      the appearances
    OPINION                                    …and the writing begins

THE BAND TAKES TWO FORMS AND THEY ARE THE SAME BAND — the style name
records which the record printed:

    'typed sandwich' (46 of 50) — a PAIR of rules centred on the page axis
    to a tenth of a point, TYPED as underscores on 41 records and DRAWN as
    a filled rect on five, in one measure family (162–285pt, and 227.3pt on
    33 of them). randall_johnson_1 sets both, one on top of the other; a
    rect within 16pt of a typed rule is that rule inked, not a second
    fence.

    'panel sandwich' (3 of 50) — the Special Workers' Compensation Appeals
    Panel slip omits the rules and keeps the band: the docket row stands
    with 43–45pt of air above and below it against a 15pt leading, which is
    exactly the space the rules would have occupied (14.9 + 30.0). These
    three are scans with an OCR text layer, and their clerk's stamp leaves
    debris in the top-right margin ('Clerk of the Appellartfairts') that no
    size test can see; the reader drops anything starting past 0.72 of the
    measure and RECORDS it.

A record with neither — the one image-only scan in the corpus, which has no
text layer at all — is not this paper and gets NOTHING.

WHERE THE READER STOPS. Two landmarks, and the paper decides which it
prints. The 'OPINION' banner comes first where the court sets one: tenn's
byline is an ANNOUNCEMENT ('…, J., delivered the opinion of the Court, in
which … joined.') and the appearances print BELOW it, so the writing does
not start at the byline. Core already knows this — ``assemble`` moves
everything between an ``accept_delivered`` byline and that banner back to
the headmatter — and the reader does the same job IN PLACE, so those rows
come back tagged instead of merely relocated. The byline row itself is
stepped over, never claimed: core builds the author from it, and a claim
would leave the writing unsigned. On a separate writing there is no banner
and the opinion opens on its own signature, so the byline is the end. A
paper printing neither is an unsigned order that begins under the band, and
the reader claims at most the one row naming it.

KNOWN GAP, NOT A LAYOUT FINDING. The panel slips sign 'W. MARK WARD, SR.
J., delivered the opinion of the court…'. ``_TENN_GRAMMAR`` has no Senior
Judge title, so the shared parser declines the row and the writing comes
out unsigned. The reader still identifies the row for what it is (role
'panel'), because a wrong tag is worse than a right one late; the fix is
one line in ``courts/__init__.py`` and is reported, not applied here.
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
# which tennctapp and tenncrimapp reference by name.
TENN = get_profile("tenn")

STYLE_RULED = "typed sandwich"          # the fence pair (46 of 50)
STYLE_PANEL = "panel sandwich"          # the workers'-comp slip (3 of 50)

# ---- tenn's declared facts (measured over the corpus, not tuned) ---------
# THE FENCE MEASURE. 90 fences over 45 records: 66 at 227.3pt, 8 at 216.0
# (drawn), 4 at 210.0, and singles at 220.8 / 232.1 / 233.7 / 234.0 /
# 247.0 / 285.0 / 162.2 / 168.7 — every one of them centred on the page
# axis to within 2.6pt.
_FENCE_MEASURE = (150.0, 300.0)
_FENCE_AXIS = 12.0
# A DRAWN fence and a TYPED one may both be present on the same record
# (randall_johnson_1 sets underscores and strokes a rect under them); a
# rect within this of a typed rule's top is that rule, not a second fence.
_FENCE_SAME = 16.0
# THE WHITESPACE FENCE. Where the panel slip omits the rules the docket
# keeps its band: measured 43.4–45.2pt of clear space on both sides
# against a 15pt leading. 2.2x the leading separates it from the 1.0x
# runover and the 2.0x block gap the rest of the page uses.
_BAND_CLEAR = 2.2
# THE BANNER: 15.1pt over a 13.0pt body on the ruled paper, 14.2 over
# 12.4 on the slip. Either way it is the top row of page 1.
_BANNER_LEAD = 3                        # how many rows the banner may take
# THE WRITING'S OWN BANNER is set out from the rail: 'OPINION' at x0=277
# against a 72pt body rail. A row at the rail is prose, whatever it says.
_BANNER_INSET = 60.0
# THE NOTES ARE A STEP SMALLER: 11.0pt against a 13.0pt body. A caption
# footnote prints at the FOOT of the page the reader is walking, so the
# step is what keeps it out of the block — the note zone is core's.
_NOTE_STEP = 1.4
# THE CLERK'S STAMP sits in the right margin. On the ruled paper it is
# 9pt sans and core's furniture pass takes it; on the scanned panel slips
# it is a struck 'FILED' block whose OCR debris ('Clerk of the
# Appellartfairts') core has no size cue for. Nothing the court sets in
# its headmatter starts this far right.
_STAMP_RAIL = 0.72
# HOW FAR THE BLOCK MAY RUN: the appearances wrap onto page 2 on the long
# records (trentham prints six of them); nothing in the corpus needs to
# look past a third sheet for the 'OPINION' banner.
_MAX_PAGES = 3

_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# THIS COURT'S OWN DOCKET, the only number it sets inside the band:
# 'No. W2022-00210-SC-R11-CD', 'No. M2024-00959-SC-R10-CO', and on the
# panel slip with its mailing date welded on ('No. W2023-01733-SC-R3-WC —
# Mailed September 30, 2024').
_DOCKET = re.compile(
    r"^Nos?\.\s*([A-Z]\d{4}-\d{3,6}-SC-[A-Z0-9-]+)", re.I)
# THE COURT BELOW gives its own number, and prints its judge beside it on
# the same visual row ('No. 2021-C-1591 Angelita Dalton, Judge').
_LOWER_NO = re.compile(r"^Nos?\.\s*(.+)$", re.I)
_BENCH = ("judge", "judges", "chancellor", "commissioner",
          "special judge", "senior judge")
# THE SITTING. Tennessee dates the hearing, never the release — the
# release date is the clerk's stamp, which is furniture.
_SITTING = ("session", "assigned on briefs", "heard at", "submitted on",
            "argued")
# THE AUTHORSHIP ANNOUNCEMENT, as a LABEL. tenn's byline is a sentence
# ('X, J., delivered the opinion of the court, in which Y and Z joined.'),
# and where the shared grammar declines the name form the row is still
# that sentence and still belongs to the front matter. Recognising it
# here changes no structure — it only stops the row from being tagged
# 'summary', which it is not. The verbs are core's own closed set.
_DELIVERS = ("delivered", "filed", "authored", "announced", "wrote")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"([A-Z][a-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})")
# THE RELEASE DATE is the one date the court does NOT set in type: the
# clerk strikes it into the top-right margin as '06/16/2025'. It is
# furniture and it is dropped, but the value is still the day the opinion
# issued, and nothing else on the page says so.
_STAMP_DATE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
# THE ORIGIN. A closed vocabulary of what a court below is CALLED — never
# a test on the name of any particular court.
_ORIGIN_WORDS = ("appeal", "appellate", "court", "commission", "board",
                 "panel", "tribunal", "review", "certified", "circuit",
                 "chancery", "criminal", "juvenile", "probate", "claims",
                 "workers", "direct", "automatic", "petition")
# THE PAPER'S OWN NAME, printed alone and centred under the fence when the
# Court disposes of a case without an opinion. A closed vocabulary of
# labels — never a test on anything a row says about a case.
_TITLE_HEADS = ("ORDER", "OPINION", "JUDGMENT", "PER CURIAM")
# THE DISPOSITION. The court closes its front matter with the rule it
# decided under and what it did, above the byline: set BOLD on the ruled
# paper and merely SET IN from the body rail on the panel slip, which
# prints no bold at all. Either mark, plus the cue, identifies it.
_DISPOSITION_INSET = 40.0
_DISPOSITION_CUES = ("tenn. r. app. p.", "tenn. code ann.",
                     "tenn. sup. ct. r.", "tenn. r. civ. p.",
                     "appeal as of right", "appeal by permission",
                     "direct appeal", "automatic review")
# REPRESENTATION is a closed role vocabulary. Every appearance Tennessee
# prints closes on one of these; a party or firm NAME is never read.
_COUNSEL_MARKS = ("for the appell", "for appell", "for the petition",
                  "for petition", "for the respond", "for respond",
                  "for the amic", "for amic", "for the plaintiff",
                  "for the defendant", "for the state of", "pro se",
                  "on brief", "attorney general and reporter",
                  "assistant attorney general", "no appearance")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_banner(text: str) -> bool:
    """tenn names itself on the top row of every paper it prints, then
    names its division and the city it sat in underneath.

    Read WITHOUT the spaces: the extractor loses one often enough that a
    literal comparison misses ('IN THE SUPREME COURTOF TENNESSEE' —
    annie_jones), and the court's own name is the same name either way."""
    flat = _norm(text).upper().rstrip(".")
    tight = flat.replace(" ", "")
    if tight.startswith("INTHESUPREMECOURTOFTENNESSEE"):
        return True
    if flat.startswith("AT ") and len(flat) <= 24:
        return True
    return "APPEALSPANEL" in tight or "COMPENSATIONAPPEALS" in tight


def _sitting_value(text: str) -> str | None:
    """'November 6, 2024 Session' / 'Assigned on Briefs June 25, 2025' —
    the day the Court took the case up, which is the only date the page
    sets. Returns the date as printed, or None."""
    flat = _norm(text)
    low = flat.lower()
    if not any(cue in low for cue in _SITTING):
        return None
    mm = _DATE.search(flat)
    if mm is None or mm.group(1).lower().rstrip(".") not in _MONTHS:
        return None
    return f"{mm.group(1)} {mm.group(2)}, {mm.group(3)}"


def _is_origin(text: str) -> bool:
    low = _norm(text).lower()
    return any(w in low for w in _ORIGIN_WORDS)


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
    """'W. MARK WARD, SR. J., delivered the opinion of the court, in which
    …joined.' — an ALL-CAPS name, an abbreviated title, a delivery verb."""
    flat = _norm(text)
    head = flat.split(",", 1)[0]
    letters = [c for c in head if c.isalpha()]
    if not letters or not all(c.isupper() for c in letters):
        return False
    low = flat.lower()
    return any(f" {v} " in low for v in _DELIVERS)


def _announced(text: str) -> str:
    return text


def _is_disposition(text: str) -> bool:
    low = _norm(text).lower()
    return any(cue in low for cue in _DISPOSITION_CUES)


def _is_counsel(text: str) -> bool:
    low = _norm(text).lower()
    return any(mk in low for mk in _COUNSEL_MARKS)


# --------------------------------------------------------------------------
# the band — tenn's one section mark, and the dispatch
# --------------------------------------------------------------------------

def _typed_fences(pm) -> list:
    """The typed underscore rules this page sets on its axis, in order."""
    out = []
    for line in pm.lines:
        if not _TYPED_RULE.match(_norm(line.plain)):
            continue
        width = line.x1 - line.x0
        if not (_FENCE_MEASURE[0] <= width <= _FENCE_MEASURE[1]):
            continue
        if abs((line.x0 + line.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        out.append(line)
    return sorted(out, key=lambda l: l.top)


def _drawn_fences(pm, typed: list) -> list:
    """…and the ones it STROKES instead. A rect sitting on a typed rule is
    that rule inked, not a second fence."""
    tops = [l.top for l in typed]
    out = []
    for r in pm.h_rules:
        if not (_FENCE_MEASURE[0] <= r.width <= _FENCE_MEASURE[1]):
            continue
        if abs((r.x0 + r.x1) / 2 - pm.width / 2) > _FENCE_AXIS:
            continue
        if any(abs(r.top - t) <= _FENCE_SAME for t in tops):
            continue
        out.append(r.top)
    return sorted(out)


def _docket_band(pm, rows: list, lead: float):
    """Where page 1 fences its own docket: ``(top, bottom, typed_lines,
    drawn_tops)``, or None.

    Two ways, one band. The rules where the court draws them; the clear
    space where it does not — a docket row standing ``_BAND_CLEAR`` x the
    leading away from the row above AND the row below is in the same band
    the rules would have made."""
    typed = _typed_fences(pm)
    drawn = _drawn_fences(pm, typed)
    marks = sorted([l.top for l in typed] + list(drawn))
    if len(marks) >= 2:
        return marks[0], marks[-1], typed, drawn
    page_rows = [l for l in rows if l.page == pm.number]
    for i, line in enumerate(page_rows):
        if _DOCKET.match(_norm(line.plain)) is None:
            continue
        if i == 0 or i + 1 >= len(page_rows):
            continue
        above = line.top - page_rows[i - 1].top
        below = page_rows[i + 1].top - line.top
        if above >= _BAND_CLEAR * lead and below >= _BAND_CLEAR * lead:
            return line.top - 1.0, line.top + 1.0, [], []
    return None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="tenn")
def read_headmatter_tenn(model, geom, **_):
    """Read tenn's banded headmatter, or NOTHING."""
    if not model.pages or geom is None:
        return NOTHING                    # the image-only scan has no rows
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
            # THE CLERK'S STAMP, struck into the right margin — taken here
            # and not in the walk, because on the scanned slips it stands
            # ABOVE the banner and would otherwise be read as one. THE RAIL
            # IS ASKED FIRST, BEFORE THE NOTE STEP: the OCR of mark_gray's
            # struck FILED block breaks into three 9.7pt fragments ('Clerk
            # of th' x0=460.7, 'urts' x0=548.4, 'By' x0=482.6 — 0.75, 0.90
            # and 0.79 of a 612pt sheet) against a 12.7pt body, so the note
            # step took them first and they reached neither the rows nor the
            # stamp record. Unclaimed, core put all three in the BODY and
            # opened a writing on them.
            if line.page == 1 and line.x0 >= page_w * _STAMP_RAIL:
                stamped.append(line)
                continue
            # THE NOTES ARE A STEP SMALLER and they are core's, wherever
            # they fall: a caption footnote ('… Session Heard at Martin¹')
            # prints at the FOOT of the page the reader is walking.
            if (line.size or 0) < geom.body_size - _NOTE_STEP:
                continue
            rows.append(line)
    rows.sort(key=lambda l: (l.page, l.top, l.x0))
    if not rows:
        return NOTHING
    if not any(_is_banner(l.plain) for l in rows[:_BANNER_LEAD]):
        return NOTHING                    # tenn names itself first, always

    band = _docket_band(page1, rows, geom.lead or 15.0)
    if band is None:
        return NOTHING                    # not this paper; core's walk reads it
    return _read(model, geom, rows, stamped, band)


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
        K20171856' beside 'James A. Hamilton III, Commissioner') — one
        item, and every line id it was built from."""
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
    """One past the block opening at ``start``: tenn runs a paragraph at
    1.0x its leading and stands the next block off at 2.0x.

    A block may WRAP THE SHEET — carruthers' first appearance breaks after
    '…Durham, North Carolina; and' and finishes at the top of page 2. The
    torn edge is the page's last row ending mid-clause under a
    continuation that opens the next page."""
    j = start + 1
    while j < len(vrows):
        prev, cur = vrows[j - 1][0], vrows[j][0]
        if cur.page == prev.page:
            if cur.top - prev.top > 1.6 * lead:
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
    parser = BylineParser(TENN.byline)
    # THE RELEASE DATE, read off the clerk's stamp where the stamp is
    # legible. The row itself is furniture — core drops the 9pt one and
    # the reader drops the scanned one — but the value is the only record
    # the page carries of the day the opinion issued.
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
    # entry. Read once, up front, so a row can be asked which block it
    # opens without the walk measuring leading twice.
    index = {id(r[0]): i for i, r in enumerate(vrows)}
    block_at: dict = {}
    _i = 0
    while _i < len(vrows):
        _j = _block_end(vrows, _i, lead, pages)
        block_at[_i] = (_j, _norm(" ".join(
            x.plain for k in range(_i, _j) for x in vrows[k])))
        _i = _j
    below = [r for r in vrows
             if (r[0].page, r[0].top) > (1, band_bottom)]

    # WHERE THE HEADMATTER ENDS. Two landmarks, and the paper decides
    # which one it prints:
    #   the 'OPINION' banner — where the court sets one, the writing starts
    #     there and everything above it (summary, disposition, byline
    #     announcement, appearances) is front matter. This is the same rule
    #     core applies to an ``accept_delivered`` byline, applied in place
    #     so the rows come back TAGGED instead of merely relocated;
    #   the byline — on a separate writing there is no banner and the
    #     opinion opens on its own signature.
    # A paper printing neither is an unsigned ORDER that begins immediately
    # under the band, and the reader claims nothing below it.
    banner_at = None
    for row in below:
        if _is_writing_banner(row, geom):
            banner_at = row[0]
            break
    byline_at = None
    for row in below:
        if banner_at is not None and (row[0].page, row[0].top) >= (
                banner_at.page, banner_at.top):
            break                         # a signature under the banner is
        if parser.parse(_norm(row[0].plain)) is not None:   # a sign-off
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
    announced = False                     # …or its unparsed twin
    delivered = None                      # what the announcement announced

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
            if state == "caption":
                # THE CAPTION is what the court sets above the origin, and
                # the origin is what stands under it — same weight, but the
                # origin names a COURT and the caption names the parties.
                # A row carrying the PIVOT is a caption row however many
                # court words it happens to contain (the OCR of wade's
                # caption has the clerk's stamp welded onto its tail).
                if _is_origin(text) and not _is_pivotal(text):
                    state = "origin"
                else:
                    caption.append(text)
                    ctx.row(row, "caption")
                    continue
            origin.append(text)
            mm = _LOWER_NO.match(text)
            if mm:
                lower_nos.append(mm.group(1))
            ctx.row(row, "lower-court")
            continue

        # ---- below the band: the court's own front matter --------------
        if end_at is None:
            # AN UNSIGNED PAPER THAT NAMES ITSELF. teresa_locke sets
            # 'ORDER DISMISSING APPEAL AS MOOT' under the band and then
            # opens its own numbered sections — the name is headmatter,
            # the sections are the writing. Claim the one row (as a
            # releasable anchor) and stop.
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
            # THE ANNOUNCEMENT IS CLAIMED WHOLE, WRAP AND ALL, and the name
            # it announces is handed to core as ``announced_author`` — the
            # same contract va uses for a court that ANNOUNCES its author
            # instead of signing. Stepping over the block instead left core
            # to pick the byline out of the body stream, and core can only
            # join rows INSIDE one segment and stops at the first sentence
            # terminal, so a row of the announcement came back unclaimed on
            # four records and the shared walk appended it to the headmatter
            # with no role at all:
            #   the WRAP, where the scan's uneven leading split the two rows
            #   into different segments (lauren_taylor 560.4 -> 578.6 = 18.2pt
            #   and mark_gray 552.2 -> 568.6 = 16.4pt against a 12.4pt body)
            #   — 'and W. MARK WARD, SR. J., joined.';
            #   the SECOND SENTENCE, where the block announces a separate
            #   writing too (heather_smith, ambreia_washington_1) — core cuts
            #   at the '.' after 'joined' and leaves 'DWIGHT E. TARWATER, J.,
            #   filed a separate concurring opinion.' behind.
            # Claiming the whole block leaves core no cut to make and no
            # crumbs to drop.
            idx = index[id(line)]
            end, whole = block_at.get(idx, (idx + 1, text))
            for k in range(idx, end):
                ctx.row(vrows[k], "author")
            delivered = _announced(whole)
            signed = True
            if end >= len(vrows):
                break
            skip_to = (vrows[end][0].page, vrows[end][0].top)
            continue
        # BELOW THE BYLINE, EVERYTHING TO THE BANNER IS THE ROSTER. That is
        # core's own rule for an announcement byline, and reading these
        # rows by their marks instead misfiled a summary that happened to
        # say 'proceeding pro se' (mcnabb) — the marks are consulted ONLY
        # on the unsigned papers, which print no byline to stand below.
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
        if byline_at is None and (announced or _is_announcement(text)):
            announced = True
            ctx.crit.setdefault("panel_line", text)
            ctx.row(row, "panel")
            continue
        ctx.row(row, "summary")

    if not dockets:
        return NOTHING

    ctx.crit["headmatter_style"] = STYLE_RULED if (typed or drawn) \
        else STYLE_PANEL
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
    if byline_at is not None:
        ctx.crit["panel_line"] = _norm(byline_at.plain)
    out = ctx.result(anchor_ids)
    if delivered:
        out["announced_author"] = delivered
    return out


def _is_writing_banner(row: list, geom) -> bool:
    """The name the court sets over the writing itself — the same closed
    set core uses to find where an announcement byline's opinion begins.

    The word alone does not make the banner: coblentz's summary breaks so
    that its last row is 'Opinion.' AT THE BODY RAIL, and read as a banner
    it cut the block twenty rows early. The banner is SET OUT — centred,
    well right of the rail — and the row carries nothing else."""
    if len(row) != 1:
        return False
    line = row[0]
    if line.x0 <= geom.body_x0 + _BANNER_INSET:
        return False
    return _norm(line.plain).upper().replace(" ", "").rstrip(".") in (
        "OPINION", "ORDER", "MEMORANDUMOPINION")


def _is_pivotal(text: str) -> bool:
    low = f" {_norm(text).lower()} "
    return " v. " in low or " vs. " in low or " v " in low


def _has_bench(text: str) -> bool:
    low = _norm(text).lower().rstrip(".")
    return any(low.endswith(w) for w in _BENCH)


def _lower_numbers(rows: list) -> list:
    """'87-04408, 87-04409, 87-04410  Paula L. Skahan, Judge' -> the three
    numbers. The judge is recorded on his own, so the row is cut at the
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
