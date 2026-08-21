"""Supreme Court of California ('cal').

THE CONTRACT. California sets one cover, and the cover is a STACK OF
CENTRED BANDS under an engraved masthead, closed by a run of prose at the
body rail. Nothing on the page is read by wording except three closed
forms the court owns outright — its own docket (``S`` + six digits), the
month names in its release date, and the bench titles it signs with:

    IN THE SUPREME COURT OF          the masthead: two rows at 18pt over
    CALIFORNIA                       a 13.4/13.6pt body, centred on the axis

    In re GERALD JOHN KOWALCZYK      the caption, centred
    on Habeas Corpus.

    S277910                          THIS court's docket — the hinge

    First Appellate District, …      the origin: a court row and its own
    A162977                          docket, in pairs, as many as it takes
    San Mateo County Superior Court
    21-SF-003700-A

    April 30, 2026                   the release date, centred and bare

    Chief Justice Guerrero authored  THE AUTHORSHIP SUMMARY — flush to the
    the opinion of the Court, in     body rail, one sentence per writing
    which Justices Corrigan, …       the court is about to print
    Justice Groban filed a concurring opinion, in which …
    Justice Wiley filed a concurring opinion.

THE DOCKET IS THE HINGE, and it is what makes the block readable without
reading a single court NAME. Everything at or above the LAST ``S``-docket
is caption or docket; everything between it and the date is the origin;
what follows the date is the summary. A row inside the origin whose every
token carries a digit is that tribunal's number, and one whose tokens
carry none is its name — a test on the SHAPE of a row, never on what it
says.

TWO STYLES, dispatched on what closes the centred stack:

  'authored cover' (29 of 30) — a bare release date closes it and the
      authorship summary follows at the rail. The summary may run onto
      the page after the cover, and in in_re_z.g. it stands there
      ENTIRELY; that page continues the cover only when its first row
      stands AT THE RAIL, because every writing opens its own first page
      with a CENTRED short title block instead. The geometry tells
      continuation from body without reading either.

  'court order' (1 of 30) — no date and no summary. A BOLD CENTRED label
      ('ORDER MODIFYING OPINION') closes the stack and 'THE COURT:' opens
      the writing. shear_development_co._llc staples the modification
      order in front of the reissued opinion, which prints its own full
      cover on page 3; the reader claims the FIRST cover only and leaves
      the second one to core, because it stands inside a writing.

WHY THE SUMMARY BELONGS TO THE HEADMATTER. It is the court's own table of
its writings, and each of its sentences has a byline's grammar ('Justice
Groban filed a concurring opinion, in which Justices Liu and Evans
concurred.'). Left in the stream it opened one phantom writing per
sentence and the WHOLE document — majority and every separate writing —
collected in the last of them (in_re_kowalczyk: three writings, 61 pages,
all of them in the third). Claimed here, the sentences stay printed where
the court printed them and the writings are found where the court starts
them.

WHERE THE READER STOPS. At the first byline, as every reader does. What
stands between the cover and that byline is the writing's own title block
— the short case name over the docket, the same words the court sets as
the running head of every page of the writing — and it is recorded as the
furniture it is.

WHAT THE READER DOES NOT TOUCH. The assignment notes at the foot of the
cover ('* Associate Justice of the Court of Appeal, …') are footnotes and
are left in the footnote zone. No writing is ever entered.

THE REPORTER'S DOCKET SHEET — the endmatter, claimed as a second region.
California closes every slip with the Reporter's own trailing apparatus,
and it is not the court's writing at all: a label grid of the case's
record over the appearance roster over the addresses of the counsel who
argued. It is SET APART BY TYPE AND BY MEASURE, not by its wording:

    See next page for addresses and telephone   the referral, italic,
    numbers for counsel who argued in Supreme   opens the sheet on all 30
    Court.

    Name of Opinion  Conservatorship of E.A.    the label grid, fenced by
    ____________________________________        FOUR typed rules, exactly
    Procedural Posture (see XX below)            four on every record
    Original Appeal                              the UNMARKED options are
    Original Proceeding                          set bold; the one the
    Review Granted (published)                   Reporter marked carries
    Review Granted (unpublished) XX NP opn.      'XX' and is set roman —
      filed 8/28/24 – 1st Dist., Div. 1          two cues, one geometric
    Rehearing Granted
    ____________________________________
    Opinion No. S287241                          this court's own docket
    Date Filed: July 23, 2026                    and release date
    ____________________________________
    Court: Superior                              the TRIAL court, its
    County: Contra Costa                         county and the judge who
    Judge: Frank Riebli                          tried it — nothing the
    ____________________________________         cover states
    Counsel:                                     the appearance roster
    Brian C. McComas, under appointment by …
    Counsel who argued in Supreme Court (not intended for publication
    with opinion):
    Brian C. McComas   The Law Office of …       name, firm, address, phone

THE LANDMARK IS THE TYPE STEP, over WHOLE PAGES. Measured over all 30
records: the sheet is a trailing run of complete pages on which EVERY row
is set at 12.0pt — one full step below the 13.4/13.6pt body and one step
above the 11.0pt footnote — and EVERY row sits at x0 = 108.0, the body
rail, to the tenth of a point. There is no folio on these pages and no
centred row, which is what makes the run self-delimiting: the walk goes
back from the last page while the page is uniformly that size and wholly
at the rail, and the writing's own last page stops it because it carries
body type, a centred folio, or both. The label grid corroborates
('Name of Opinion', and the four typed rules); the referral sentence
corroborates again — it opens the sheet on all 30 — but a sentence is the
weakest landmark available and it is not what the claim rests on.

WHY IT IS CLAIMED HERE AND NOT BY ``counsel_after_writings``. That path
harvests the last 12 assembled blocks of the last writing; cal's sheet is
24 to 40 blocks, so it caught only part of it, and the part it moved lay
INSIDE the surviving writing's span, so the never-bisect invariant put it
straight back — as one paragraph per printed LINE. The sheet also carries
metadata no counsel harvest can read (the trial judge, the posture, the
Reporter's own name of the opinion) and the addresses of argued counsel,
which read as a conformed signature and credited a Deputy State Solicitor
General as an author of shear_development. Claimed here, the whole sheet
is subtracted from the stream before assembly and rendered as endmatter,
one row per printed row, every row tagged.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import register

CAL = register(CourtProfile(
    "cal", "Supreme Court of California",
    # Each writing is announced by the heading that opens its own first
    # page — 'Opinion of the Court by Guerrero, C. J.' / 'Concurring
    # Opinion by Justice Groban' / 'Dissenting Opinion by Justice Yegan'.
    # The court signs at the END in the abbreviated form ('GUERRERO, C.
    # J.' over a 'We Concur:' roster), which core demotes as a signature
    # cluster rather than opening a writing on it.
    byline=BylineGrammar(style="none", opinion_by_headings=True),
    # NOT `counsel_after_writings`. The trailing roster is claimed whole by
    # this file's own endmatter reader, so there is nothing left for core's
    # 12-block harvest to find — and left on, that harvest reads the last
    # writing's closing paragraph ('…faults appellate counsel for…') as a
    # roster and re-splits it into line fragments.
))

STYLE_COVER = "authored cover"          # the opinion paper
STYLE_ORDER = "court order"             # the modification/administrative order

# ---- cal's declared facts (measured over the corpus, not tuned) ----------
# THE MASTHEAD: two rows at 18.0pt over a 13.4 or 13.6pt body, on all 30
# records. Nothing else on any cover is set above 13.6.
_MASTHEAD_SIZE = 16.0
# THE AXIS. Every row of the centred stack sits within 1pt of the page
# midpoint (measured max offset 0.4pt over 30 covers); the summary's
# justified rows can also land on it, so the axis test is applied ONLY
# inside the stack, never across the block.
_AXIS = 8.0
# THE RAIL. The summary is flush to the body's left margin (x0 = 108.0 on
# every record); the writings' title blocks are centred instead.
_RAIL = 2.0
# THE FOOTNOTE ZONE opens either on a typed rule at the rail (3 records)
# or on a marker set a clear step below the body (27 records).
_MARK_STEP = 1.5

# THIS COURT'S OWN DOCKET — the hinge the whole cover is read from.
_DOCKET = re.compile(r"^S\d{6}$")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
# 'April 30, 2026' — cal sets its release date bare and centred.
_DATE = re.compile(r"^([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})\.?$")
# 'Filed 5/13/26' — the clerk's stamp, above the masthead at 10pt.
_STAMP = re.compile(r"^Filed\s+\d{1,2}/\d{1,2}/\d{2,4}$", re.I)
_TYPED_RULE = re.compile(r"^[_\-–—]{6,}$")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = (
    "appellant", "appellee", "petitioner", "respondent", "plaintiff",
    "defendant", "objector", "conservatee", "intervener", "intervenor",
    "movant", "amicus", "amici", "applicant", "claimant", "party",
    "interest", "real",
)
# BENCH TITLES, likewise closed: what the summary calls the justices it
# names. 'Acting Chief Justice' is the form when the Chief is recused.
_BENCH = ("acting chief justice", "chief justice", "associate justice",
          "presiding justice", "justices", "justice")
# The summary's own grammar, in the two sentences the court writes.
_AUTHORED = re.compile(
    r"^(?P<title>Acting Chief Justice|Chief Justice|Justice)\s+"
    r"(?P<name>[A-Z][\w’'\-]*(?:\s+[A-Z][\w’'\-]*)?)\s+authored the opinion "
    r"of the Court(?:,\s*in which\s+(?P<joiners>.+?)\s+concurred)?\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_masthead(line) -> bool:
    return (line.size or 0) >= _MASTHEAD_SIZE


def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w.strip(",.;: ") for w in bare.split()]
    return all(w in _STATUS_WORDS or w.rstrip("s") in _STATUS_WORDS
               or w in ("and", "the", "in", "etc", "or")
               for w in words if w)


def _is_pivot(text: str) -> bool:
    return _norm(text).rstrip(".").lower() in ("v", "vs")


def _date_value(text: str) -> str | None:
    flat = _norm(text)
    mm = _DATE.match(flat)
    if mm is None or mm.group(1).lower() not in _MONTHS:
        return None
    return flat.rstrip(".")


def _numbered(text: str) -> bool:
    """A row whose every token carries a digit is a tribunal's NUMBER, and
    one whose tokens carry none is its NAME. Shape, not wording — it is
    what lets the origin be split without reading a court name."""
    toks = [t for t in _norm(text).replace(",", " ").split() if t]
    return bool(toks) and all(any(c.isdigit() for c in t) for t in toks)


# --------------------------------------------------------------------------
# the page's own bounds
# --------------------------------------------------------------------------

def _note_top(pm, body_size: float) -> float:
    """Where the cover's footnote zone opens. Below this the page carries
    the assignment notes ('* Associate Justice of the Court of Appeal, …'),
    which are footnotes and not the reader's to claim."""
    tops = [l.top for l in pm.lines
            if _TYPED_RULE.match(_norm(l.plain))
            or (l.plain.strip() and (l.size or 99) <= body_size - _MARK_STEP
                and set(_norm(l.plain)) <= set("*†‡§¶0123456789 "))]
    return min(tops) if tops else float("inf")


def _rows(pm, finder, body_size: float) -> list:
    """The page's content rows above its footnote zone, in page order."""
    limit = _note_top(pm, body_size)
    out = [l for l in pm.lines
           if l.plain.strip() and l.top < limit and not finder.kind(pm, l)]
    out.sort(key=lambda l: (l.top, l.x0))
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom, body_size):
        self.model = model
        self.geom = geom
        self.body_size = body_size
        self.items: list = []
        self.attorneys: list = []
        # what the Reporter's sheet states about the TRIAL court, collected
        # over its 'Court:' / 'County:' rows and joined once at the end.
        self.origin: dict = {}
        self.consumed: set[int] = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, line, role: str, centred: bool = True):
        """One printed row, tagged for what the cover made it. A row of the
        centred stack is centred when it sits on the page axis; a summary
        row is at the rail and stays there even when its justified measure
        happens to centre on the same axis."""
        pw = self.model.pages[line.page - 1].width
        cx = (line.x0 + line.x1) / 2
        align = "C" if centred and abs(cx - pw / 2) <= _AXIS else "L"
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        self.consumed.add(line.id)

    def endmatter(self, line, role: str):
        """One printed row of the Reporter's trailing sheet. The endmatter
        is the same kind of matter as the headmatter and is rebuilt the same
        way — one row per printed row, in the page's own order, tagged for
        what the sheet made it."""
        self.attorneys.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align("L"), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), italic=bool(line.all_emphasized),
            role=role))
        self.consumed.add(line.id)

    def drop(self, line, kind: str):
        self.dropped.append(m.Dropped(text=_norm(line.plain),
                                      prov=m.Prov(line.page, (line.id,)),
                                      kind=kind))
        self.consumed.add(line.id)

    def result(self, anchor_ids=(), doc_type=None):
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": list(anchor_ids), "doc_type_final": doc_type}


@decider("headmatter.read", court="cal")
def read_headmatter_cal(model, geom, **_):
    """Read cal's cover, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = geom.body_size if geom else 13.4
    body_x0 = geom.body_x0 if geom else 108.0
    finder = FurnitureFinder(model, body_x0, body_size)
    page1 = model.pages[0]
    rows = _rows(page1, finder, body_size)
    if not rows:
        return NOTHING

    ctx = _Ctx(model, geom, body_size)

    # THE MASTHEAD opens the cover. The clerk's file stamp may stand above
    # it; that is stationery and is recorded as such.
    i = 0
    while i < len(rows) and _STAMP.match(_norm(rows[i].plain)):
        ctx.drop(rows[i], "stamp")
        i += 1
    banner: list = []
    while i < len(rows) and _is_masthead(rows[i]):
        banner.append(rows[i])
        i += 1
    if len(banner) < 2:
        return NOTHING                    # not this court's cover
    for line in banner:
        ctx.emit(line, "court")
    # AS THE PAGE PRINTS IT — the masthead is two rows and one name.
    ctx.crit["court"] = _norm(" ".join(l.plain for l in banner))

    stack = rows[i:]
    if not stack:
        return NOTHING

    # THE DISPATCH: what closes the centred stack. A bare release date
    # opens the authorship summary; a bold centred label opens an order.
    date_i = next((k for k, l in enumerate(stack)
                   if _date_value(l.plain) is not None), None)
    title_i = next((k for k, l in enumerate(stack)
                    if l.all_bold and abs((l.x0 + l.x1) / 2
                                          - page1.width / 2) <= _AXIS), None)
    if date_i is not None and (title_i is None or title_i > date_i):
        end = date_i
        style = STYLE_COVER
    elif title_i is not None:
        end = title_i
        style = STYLE_ORDER
    else:
        return NOTHING

    if not _read_stack(ctx, stack[:end]):
        return NOTHING
    ctx.crit["headmatter_style"] = style

    if style is STYLE_ORDER:
        line = stack[end]
        ctx.crit["title"] = _norm(line.plain)
        ctx.emit(line, "title")
        _read_sheet(ctx, body_size, body_x0)
        return ctx.result(anchor_ids=[line.id])

    date_line = stack[end]
    ctx.crit["decision_date"] = _date_value(date_line.plain)
    ctx.emit(date_line, "date")
    last_page = _read_summary(ctx, stack[end + 1:], finder, body_x0,
                              date_line.page)
    _title_block(ctx, last_page, body_size)
    # THE REPORTER'S SHEET closes the paper, whichever cover opened it. It is
    # read LAST because it is a second region, not a continuation of the
    # first: the cover walk ends at the first byline and this one begins at
    # the back of the document and walks forward to the last page.
    _read_sheet(ctx, body_size, body_x0)
    return ctx.result(doc_type=m.DocType.OPINION)


def _read_stack(ctx: _Ctx, stack: list) -> bool:
    """Caption, docket and origin — split at the LAST S-docket."""
    hinge = None
    for k, line in enumerate(stack):
        if _DOCKET.match(_norm(line.plain)):
            hinge = k
    if hinge is None:
        return False                      # no docket, no cover

    caption: list = []
    dockets: list = []
    for line in stack[:hinge + 1]:
        text = _norm(line.plain)
        if _DOCKET.match(text):
            dockets.append(text)
            ctx.emit(line, "docket")
        else:
            caption.append(line)
            ctx.emit(line, "caption")
    names: list = []
    numbers: list = []
    for line in stack[hinge + 1:]:
        text = _norm(line.plain)
        ctx.emit(line, "lower-court")
        (numbers if _numbered(text) else names).append(text)

    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    if names:
        ctx.crit["lower_court"] = "; ".join(names)
    if numbers:
        ctx.crit["lower_court_docket"] = [
            t.strip() for row in numbers for t in row.split(",") if t.strip()]
    if caption:
        ctx.crit["caption"] = [_norm(l.plain) for l in caption]
        _name(ctx, caption)
    return True


def _name(ctx: _Ctx, rows: list) -> None:
    """The case name, built from the party names either side of the pivot
    — never by joining the caption wholesale.

    THE PARTY BLOCK IS A BAND. A consolidated cover stacks a case TITLE
    ('In re Z.G. et al., / Persons Coming Under the Juvenile Court Law.')
    over the parties and a second case under them, each band set off by a
    gap of two lines against the caption's own single-line pitch. The band
    that carries the pivot is the one that names the case; joined
    wholesale, in_re_z.g. read 'In re Z.G. et al., Persons Coming Under
    the Juvenile Court Law. SAN BERNARDINO … v. A.G., In re A.G. on Habeas
    Corpus.'"""
    band = _pivot_band(rows)
    left, right, seen = [], [], False
    for line in band:
        text = _norm(line.plain)
        if _is_pivot(text):
            seen = True
            continue
        if _is_status(text):
            # THE RESPONDENT'S OWN STATUS CLOSES THE NAME. Everything under
            # it is another party to the same appeal (sunflower's real
            # party in interest, j.o.'s conservator), not the respondent.
            if seen:
                break
            continue
        (right if seen else left).append(text)
    if seen and left and right:
        a = _norm(" ".join(left)).rstrip(", ")
        b = _norm(" ".join(right)).rstrip(", ")
        ctx.crit["parties"] = [a, b]
        ctx.crit["case_name"] = f"{a} v. {b}"
        return
    one = _norm(" ".join(_norm(l.plain) for l in rows
                         if not _is_status(_norm(l.plain)))).rstrip(", ")
    if one:
        ctx.crit["parties"] = [one]
        ctx.crit["case_name"] = one


# A BAND BREAK inside the caption: cal sets the caption on a 20pt pitch
# and holds two lines between bands. 1.6x the document's own leading takes
# the break and never a wrap.
_BAND_GAP = 1.6


def _pivot_band(rows: list) -> list:
    """The caption band that carries the pivot, or the whole caption."""
    if not rows:
        return rows
    lead = min((b.top - a.top for a, b in zip(rows, rows[1:])
                if b.page == a.page and b.top > a.top), default=20.0)
    bands: list[list] = [[rows[0]]]
    for prev, line in zip(rows, rows[1:]):
        if line.page != prev.page or line.top - prev.top > lead * _BAND_GAP:
            bands.append([])
        bands[-1].append(line)
    for band in bands:
        if any(_is_pivot(_norm(l.plain)) for l in band):
            return band
    return rows


# --------------------------------------------------------------------------
# the authorship summary
# --------------------------------------------------------------------------

def _read_summary(ctx: _Ctx, tail: list, finder, body_x0: float,
                  date_page: int) -> int:
    """The court's own table of the writings it is about to print.

    It is bounded on both sides: it opens under the release date and it
    ends at the last row standing AT THE RAIL. A row that leaves the rail
    is not the summary — on this cover nothing else follows it, so the
    walk simply stops and leaves that row to core. Returns the page the
    cover closed on."""
    lines: list = []
    for line in tail:                     # the rest of the cover's page
        if abs(line.x0 - body_x0) > _RAIL:
            break
        lines.append(line)
    # THE SUMMARY MAY RUN ONTO THE NEXT PAGE, and that page continues it
    # only when its first row stands at the rail — a writing opens its own
    # page with a centred title block instead. in_re_z.g. prints NO summary
    # row on the cover at all and the whole of it on the page after, so the
    # continuation is tried whether or not the cover carried one.
    if date_page < len(ctx.model.pages):
        nxt = _rows(ctx.model.pages[date_page], finder, ctx.body_size)
        if nxt and abs(nxt[0].x0 - body_x0) <= _RAIL:
            for line in nxt:
                if abs(line.x0 - body_x0) > _RAIL:
                    break
                lines.append(line)
    for line in lines:
        ctx.emit(line, "summary", centred=False)
    if not lines:
        return date_page
    text = _norm(" ".join(l.plain for l in lines))
    # THE PRINTED FORM BESIDE THE PARSED ONE: the sentence that names who
    # wrote and who joined, as the court set it.
    first = text.split(". ")[0].strip()
    ctx.crit["panel_line"] = first if first.endswith(".") else first + "."
    panel = _panel(text)
    if panel:
        ctx.crit["panel"] = panel
        ctx.crit["judges"] = ", ".join(panel)
    return lines[-1].page


def _panel(text: str) -> list:
    """Who sat, from the summary's first sentence. The bench titles are a
    closed vocabulary; the names are whatever stands after them."""
    # THE ASSIGNMENT MARKER IS NOT A LETTER. The court sets it tight
    # against the name it qualifies and sometimes against the word after
    # it too ('Boulware Eurie*concurred.' — ventura), so it is opened out
    # before the sentence is read.
    first = _norm(re.sub(r"[*\u2020\u2021]+", " ", text.split(". ")[0]))
    mm = _AUTHORED.match(first + ("." if not first.endswith(".") else ""))
    if mm is None:
        return []
    out = [mm.group("name").strip()]
    joiners = mm.group("joiners") or ""
    for chunk in re.split(r",| and ", joiners):
        part = _norm(chunk)
        low = part.lower()
        for title in _BENCH:
            if low.startswith(title + " "):
                part = part[len(title):].strip()
                break
        part = _norm(part).rstrip(".,")
        if part and part[0].isupper() and part.lower() not in ("the", "court"):
            out.append(part)
    return out


# --------------------------------------------------------------------------
# the writing's own title block
# --------------------------------------------------------------------------

# HOW FAR OFF THE BLOCK'S OWN AXIS a title row may sit. Measured against
# the BYLINE's centre, not the page's: people_v._sanmiguel sets the whole
# writing page 18pt right of the sheet's middle, and a page-axis test read
# its title block as off-centre.
_TITLE_AXIS = 10.0


def _title_block(ctx: _Ctx, last_page: int, body_size: float) -> None:
    """The rows the court prints ABOVE the first byline, on the writing's
    own first page: the short case name and the docket, repeated from the
    cover. The reader ends at the first byline, and everything between the
    cover and that byline is this block — the same words the court sets as
    the running head of every page of the writing, which is what it is
    recorded as.

    Measured over the corpus: the block is 2 or 3 rows on all 30 records,
    always centred on the byline's own axis, and it always CLOSES ON THE
    DOCKET. Anything else standing there is not this block and nothing is
    claimed."""
    if last_page >= len(ctx.model.pages):
        return
    pm = ctx.model.pages[last_page]       # the page after the cover's last
    rows = [l for l in pm.lines
            if l.plain.strip() and l.top < _note_top(pm, body_size)]
    rows.sort(key=lambda l: (l.top, l.x0))
    parser = BylineParser(CAL.byline)
    at = next((k for k, l in enumerate(rows)
               if parser.parse(_norm(l.plain)) is not None), None)
    if at is None or not (0 < at <= 4):
        return
    head = rows[:at]
    axis = (rows[at].x0 + rows[at].x1) / 2
    if not _DOCKET.match(_norm(head[-1].plain)):
        return                            # the block always closes on the docket
    if any(abs((l.x0 + l.x1) / 2 - axis) > _TITLE_AXIS for l in head):
        return
    for line in head:
        ctx.drop(line, "running-head")


# --------------------------------------------------------------------------
# the Reporter's docket sheet — the endmatter
# --------------------------------------------------------------------------

# THE TYPE STEP. Measured on all 30 records: the sheet is set at 12.0pt
# against a 13.4 or 13.6pt body — one full step down — and every row of a
# sheet page shares that one size. The window is stated as a range below
# the body rather than as the number 12.0 so it survives a body change, and
# it deliberately EXCLUDES the 11.0pt footnote type (13.4 - 11.0 = 2.4).
_SHEET_STEP = (1.0, 2.0)
# ONE SIZE PER PAGE, to the tenth of a point.
_SHEET_SIZE_TOL = 0.3
# EVERY ROW AT THE BODY RAIL. Measured x0 = 108.0 for all 4,900-odd sheet
# rows in the corpus — one value, no exceptions. It is this that stops the
# backward walk on the writing's last page, whose folio is centred.
_SHEET_RAIL = 0.5
# THE SHEET'S OWN LEADING (14.4pt at 12.0pt type) and the gap that opens a
# new band inside it — a roster entry against its neighbour's wraps.
_SHEET_PITCH = 14.4
_SHEET_BAND = 1.5

# The grid's labels — a closed vocabulary the Reporter owns, and the only
# wording this reader tests. Anything unlabelled is recorded verbatim.
_ENDM_NAME = re.compile(r"^Name of Opinion\s+(.+)$")
_ENDM_OPNO = re.compile(r"^Opinion Nos?\.\s+(.+)$")
_ENDM_FILED = re.compile(r"^Date Filed:\s*(.+)$")
_ENDM_COURT = re.compile(r"^(Court|County):\s*(.*)$")
# 'Judge', 'Judges' and 'Commissioner' — 27 / 1 / 2 of the 30 records.
_ENDM_JUDGE = re.compile(r"^(?:Judges?|Commissioner)s?:\s*(.*)$")
# The roster's own two headings — 'Counsel:' opens the appearances and
# 'Counsel who argued in Supreme Court…' opens the addresses. Anchored, not
# a prefix test: a roster CONTINUATION row also opens on the word
# ('Counsel, Nina Dong and Andrea L. Russi, Deputy County Counsel, for').
_ENDM_COUNSEL = re.compile(r"^Counsel:$|^Counsel who argued in Supreme Court\b")
_ENDM_ARGUED = "counsel who argued in supreme court"


def _sheet_pages(model, body_size: float, body_x0: float) -> list:
    """The trailing run of pages the Reporter's sheet occupies, or [].

    THE MEASURE, not the sentence. Walk back from the last page while the
    page is set ENTIRELY in one size a full step below the body and its
    every row stands at the body rail. The writing's own last page fails
    both tests at once — it carries body type and a centred folio — so the
    run delimits itself without any wording being read.

    Page 1 is never part of it: the cover is this court's, not the
    Reporter's, and a document that is nothing but a sheet is not this
    contract."""
    lo, hi = body_size - _SHEET_STEP[1], body_size - _SHEET_STEP[0]
    first = None
    for k in range(len(model.pages) - 1, 0, -1):
        rows = [l for l in model.pages[k].lines if l.plain.strip()]
        if not rows:
            continue
        sizes = [l.size or 0.0 for l in rows]
        if (max(sizes) - min(sizes) <= _SHEET_SIZE_TOL
                and lo <= min(sizes) <= hi
                and all(abs(l.x0 - body_x0) <= _SHEET_RAIL for l in rows)):
            first = k
        else:
            break
    if first is None:
        return []
    return [model.pages[k] for k in range(first, len(model.pages))]


def _read_sheet(ctx: _Ctx, body_size: float, body_x0: float) -> None:
    """Claim the Reporter's sheet and render it as endmatter.

    The sheet is a LABEL GRID over a roster, and the grid's own labels are
    what name each band. Every row is emitted — the four typed rules
    included, because they are what the page draws the bands with — so the
    claim is total: nothing is taken out of the document that is not put
    back somewhere a reader can see it."""
    pages = _sheet_pages(ctx.model, body_size, body_x0)
    if not pages:
        return
    rows = [l for pm in pages
            for l in sorted((x for x in pm.lines if x.plain.strip()),
                            key=lambda x: (x.top, x.x0))]
    texts = [_norm(l.plain) for l in rows]
    # CORROBORATION, and the bar for claiming at all: the grid names itself
    # ('Name of Opinion') and fences itself (typed rules). A trailing run of
    # small type that does neither is not this sheet and is left alone.
    if not any(_ENDM_NAME.match(t) for t in texts):
        return
    if sum(1 for t in texts if _TYPED_RULE.match(t)) < 2:
        return

    # THE FIRST FENCED BAND HOLDS EXACTLY ONE ITEM — the Reporter's name of
    # the opinion — so a row standing between that label and the rule below
    # it is the name's own WRAP and nothing else can be ('Name of Opinion
    # Shear Development Company, LLC v. California' / 'Coastal Commission';
    # 5 of the 30 wrap). The band is what makes this safe: one pitch below a
    # row means a wrap here and a NEW OPTION inside the posture band, so the
    # fence has to be read before the pitch.
    wrap: set[int] = set()
    at = next((k for k, t in enumerate(texts) if _ENDM_NAME.match(t)), None)
    if at is not None:
        for k in range(at + 1, len(texts)):
            if _TYPED_RULE.match(texts[k]):
                break
            wrap.add(k)

    roster: list[list[str]] = []          # the appearance entries, banded
    state = "grid"
    prev = None
    for at_k, (line, text) in enumerate(zip(rows, texts)):
        gap_break = (prev is None or line.page != prev.page
                     or line.top - prev.top > _SHEET_PITCH * _SHEET_BAND)
        prev = line
        if at_k in wrap:
            ctx.endmatter(line, "title")
            ctx.crit["short_case_name"] = _norm(
                f"{ctx.crit.get('short_case_name', '')} {text}")
            continue
        if _TYPED_RULE.match(text):
            # the band fence, re-emitted where the page typed it
            ctx.endmatter(line, "case-info")
            continue
        if state != "counsel" and _ENDM_COUNSEL.match(text):
            state = "counsel"
        if state == "counsel":
            ctx.endmatter(line, "counsel")
            low = text.lower()
            if _ENDM_ARGUED in low:
                state = "argued"          # addresses, not appearances
            elif not text.rstrip().endswith(":"):
                if gap_break or not roster:
                    roster.append([])
                roster[-1].append(text)
            continue
        if state == "argued":
            ctx.endmatter(line, "counsel")
            continue
        _grid_row(ctx, line, text)
    _sheet_criteria(ctx, roster)


def _grid_row(ctx: _Ctx, line, text: str) -> None:
    """One row of the label grid, tagged by the label that opens it."""
    mo = _ENDM_NAME.match(text)
    if mo:
        ctx.endmatter(line, "title")
        # THE REPORTER'S OWN NAME OF THE OPINION — the same words the court
        # sets as the running head of every page ('CONSERVATORSHIP OF E.A.').
        # Recorded beside the parsed case name, never over it.
        ctx.crit.setdefault("short_case_name", _norm(mo.group(1)))
        return
    mo = _ENDM_OPNO.match(text)
    if mo:
        ctx.endmatter(line, "docket")
        ctx.crit.setdefault("docket_number", _norm(mo.group(1)))
        return
    mo = _ENDM_FILED.match(text)
    if mo:
        ctx.endmatter(line, "date")
        val = _date_value(mo.group(1))
        if val:
            ctx.crit.setdefault("decision_date", val)
        return
    mo = _ENDM_JUDGE.match(text)
    if mo:
        ctx.endmatter(line, "lower-court")
        # WHO TRIED IT. The cover never says; the sheet always does.
        if _norm(mo.group(1)):
            ctx.crit.setdefault("lower_court_judge", _norm(mo.group(1)))
        return
    mo = _ENDM_COURT.match(text)
    if mo:
        ctx.endmatter(line, "lower-court")
        ctx.origin[mo.group(1).lower()] = _norm(mo.group(2))
        return
    # THE REFERRAL and the POSTURE BAND. The five options and the one the
    # Reporter marked ('Review Granted (unpublished) XX NP opn. filed
    # 8/28/24 – 1st Dist., Div. 1' — the marked row carries 'XX' and is set
    # roman where the four it did not mark are set bold) are recorded
    # verbatim in the rows, which is as far as this reader may take them:
    # the posture is not a declared criteria field, and an undeclared key
    # attaches silently and never serializes.
    ctx.endmatter(line, "case-info")


def _sheet_criteria(ctx: _Ctx, roster: list) -> None:
    """What the sheet states that the cover does not.

    Only where the cover left the field empty: the cover's origin is the
    fuller form ('First Appellate District, Division One; Contra Costa
    County Superior Court') and the sheet's is the shorter, and a good
    value is never overwritten with a worse one."""
    origin = ctx.origin
    if origin.get("county") and origin.get("court"):
        ctx.crit.setdefault(
            "lower_court",
            f"{origin['county']} County {origin['court']} Court")
    if roster:
        ctx.crit.setdefault("attorneys",
                            " ".join(" ".join(e) for e in roster)[:2000])
