"""Nebraska Court of Appeals ('nebctapp').

Everything unique to nebctapp lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py (with `front_matter=('syllabus',)`); this
module adds the reader only, so importing it can never raise a duplicate
profile. neb's reader and conn's Law-Journal branch were read for their
conventions; neither is imported.

THE COURT PRINTS TWO PAPERS, and they are not variants of one layout — they
are different sheets, different type ladders and different apparatus. The
DISPATCH is the sheet, then the landmark that sheet's paper always prints.

    A  'advance-sheet volume page'   396 x 612   37 of 42 records
    B  'memorandum web opinion'      612 x 792    5 of 42 records

--------------------------------------------------------------------------
A — THE BOUND REPORTER'S PAGE
--------------------------------------------------------------------------

What the library serves is the Reporter's bound-volume page, photographed
off the advance sheets onto a HALF-LETTER sheet (396.0 x 612.0 to the point
on all 37 — never 612 wide, so nothing in this branch may be measured
against a letter page), with the library's own web header stamped over the
top of page 1.

    ┌─ page 1, 396pt wide ───────────────────────────────────────────┐
    │ Nebraska Supreme Court Online Library          5.7pt  the      │
    │ www.nebraska.gov/apps-courts-epub/             5.7pt  library's│
    │ 03/17/2026 09:07 AM CDT                        5.7pt  stamp    │
    │                    - 126 -                     8.5pt  folio    │
    │     Nebraska Court of Appeals Advance Sheets  10.5pt ┐ running │
    │            34 Nebraska Appellate Reports      10.5pt ┘ heads   │
    │              AVERY v. WHITTLE                  8.0pt  short    │
    │            Cite as 34 Neb. App. 126            8.0pt  vol cite │
    │                                                               │
    │          Justin Avery, appellant, v.          11.0pt  THE      │
    │            Amy Whittle, appellee.             11.0pt  CAPTION  │
    │                 ___ N.W.3d ___                 8.0pt  the cite │
    │     Filed March 17, 2026.  No. A-25-373.       8.0pt  filed    │
    │ 1. Divorce: Appeal and Error. In a marital …    9.0pt ┐ the     │
    │ 2. Child Custody: … An abuse of discretion …   9.0pt ┘ SYLLABUS │
    │   Appeal from the District Court for Douglas … 11.0pt  origin   │
    │   Liam K. Meehan, of Higgins Law, …           11.0pt  counsel  │
    │   Moore, Bishop, and Welch, Judges.           11.0pt  panel    │
    │   Bishop, Judge.                              11.0pt  BYLINE — │
    └───────────────────────────────────────────────────────── stop ─┘

THE WEB-LIBRARY STAMP IS NOT THE BOOK, AND ITS TIMESTAMP IS A TRAP.
'03/17/2026 09:07 AM CDT' is when the PDF was pulled from the library, not
when the court decided anything, and it must never reach
`Criteria.decision_date`. Core's FurnitureFinder already identifies all
three 5.7pt rows as `stamp` on all 37 records (verified: no 5.7pt row
survives into this reader's row list on any of them) and records them in
`Dropped`, so they are attested rather than discarded — this reader never
sees them and never reads a date from them. The filing DATE is taken from
one row and one row only, the court's own 'Filed <date>.' line.

THE TYPE LADDER SAYS WHOSE WORDS A ROW IS, measured over all 37 records:

    5.7pt   the library's web header — not the book at all
    8.0-8.5 the VOLUME apparatus: folio, short head, volume cite, the
            'Cite as' row, and the paper's own '___ N.W.3d ___' placeholder
    9.0     the SYLLABUS — the court's numbered points of law
    10.5    the running-head pair
    11.0    the COURT's own text: caption, origin, counsel, panel, opinion

THE DISPATCH is the running-head pair, in the first three non-furniture
rows of page 1 and present on all 37: 'Nebraska Court of Appeals Advance
Sheets' over '<volume> Nebraska Appellate Reports'. Core's FurnitureFinder
drops that pair on pages 2..n but NOT on page 1, because a first page's top
rows are where a caption normally lives; left unclaimed they stand one row
above the caption this reader claims, which is exactly where an unclaimed
row is most dangerous. They are dropped here as `running-head`.

'Cite as 34 Neb. App. 126' IS THE REPORTER CITATION, and it is READ, NOT
CLAIMED: core has already identified it as a running head (it repeats on
every page — 37 of 37 records print exactly one distinct 'Cite as' string)
and dropped it, so this reader only records what it says, in
`Criteria.citation`. The abbreviation is TWO WORDS, 'Neb. App.', which is
why the value is taken as the whole tail of the row rather than parsed into
volume/reporter/page. A CITATION IS NOT A DOCKET: the docket comes from the
'Filed' row and nowhere else, and the two never share a field.

THE FOLIO sits at top 51.0 of a 612pt page = 0.0833 on all 37 records, and
core identifies every one of them. This paper is therefore NOT exposed to
core-patch-queue item 20 (the 0.19/0.22 folio-band disagreement that leaks
Connecticut's reporter folio into writings); measured and reported, not
patched.

THE CLAIM MUST BE CONTIGUOUS, and here that means the SYLLABUS is claimed.
The court prints no byline above its numbered points, so a reader that took
the caption and skipped the 9pt band would leave 18-130 rows for core to
open a writing on, and the bisection invariant would then pull the whole
claim into that writing and publish an EMPTY headmatter. The walk runs
unbroken from the caption to the panel.

THE 11pt BANDS ARE PARAGRAPHS, NOT ROWS. All of them open at x0=66.0 and
wrap to the rail at 54.0 — a 12pt step, invariant on all 37 — so the
origin, each appearance and the panel are grouped by that indent and asked
ONCE what they are. Each is identified by a landmark it carries:

    origin   'Appeal from' / 'Appeals from' / 'Appeals in Nos. …' — 37 of
             37, and the FIRST paragraph only
    panel    the bench word 'Judges.'
    counsel  'for <party status>' or 'pro se'
    byline   the whole paragraph is '<Surname>, Judge.' / '<Surname>,
             Chief Judge.' / 'Per Curiam.'

THE ORIGIN IS TESTED BEFORE THE ROSTER, and that order is the whole reason
roebuck_v._north_platte_pub._sch._dist. reads correctly: its origin recital
is 'Appeal from the District Court for Lincoln County: Richard A. Birch and
Cindy R. Volkmer, Judges. Affirmed.' — two trial judges, so the recital
carries the roster's own bench word. neb can test its roster first because
'JJ.' never appears in a Nebraska Supreme Court origin; here 'Judges.'
does, so the first paragraph is offered to the origin test first.

--------------------------------------------------------------------------
B — THE MEMORANDUM WEB OPINION
--------------------------------------------------------------------------

A letter sheet (612.0 x 792.0 on all 5), 12pt throughout, no library stamp,
no reporter apparatus, no syllabus, and NO running head on continuation
pages (measured: page 2 of every one of the 5 opens with body prose).

    ┌─ page 1, 612pt wide ───────────────────────────────────────────┐
    │            IN THE NEBRASKA COURT OF APPEALS       80.6  banner │
    │                                                                │
    │       MEMORANDUM OPINION AND JUDGMENT ON APPEAL  114.6 ┐ title │
    │              (Memorandum Web Opinion)            128.4 ┘       │
    │                                                                │
    │                   STATE V. ADAMS                 162.8  the    │
    │                                                     case-name  │
    │  NOTICE: THIS OPINION IS NOT DESIGNATED FOR …    203.6 ┐ NOTICE│
    │  AND MAY NOT BE CITED EXCEPT AS PROVIDED BY …    218.6 ┘       │
    │                                                                │
    │              STATE OF NEBRASKA, APPELLEE,        259.4 ┐       │
    │                        V.                        280.4 │ CAPTION
    │              ANTHONY ADAMS, APPELLANT.           301.4 ┘       │
    │           Filed July 28, 2026.  No. A-26-066.    342.2  filed  │
    │   Appeal from the District Court for Buffalo …    384.2  origin │
    │   Jeffrey P. Ensz, of Lieske, … for appellant.   420.3  counsel│
    │   PIRTLE, WELCH, and PICCOLO, Judges.            483.3  panel  │
    │   PIRTLE, Judge.                                 504.3  BYLINE │
    └───────────────────────────────────────────────────────── stop ─┘

THE HEAD IS BANDED BY WHITESPACE, and the bands are read positionally, not
by wording. Every one of the 5 sets the same tops to the hundredth of a
point; the gaps BETWEEN bands are 34.0, 34.4 and 40.8pt while the steps
INSIDE a band are 13.8 and 15.0 — one line's leading. So a step over
`_BAND_GAP` closes a band, and the bands in order are:

    band 0  the court naming itself      -> `banner`, `Criteria.court`
    bands 1..n-1  the paper's own name   -> `title`,  `Criteria.title`
    band n  the case-name head           -> `caption`, `short_case_name`
    the NOTICE                           -> `publication`

The case-name head is the LAST band before the notice — a position, not a
wording test, which is what keeps 'MEMORANDUM OPINION AND JUDGMENT ON
APPEAL' and 'STATE V. ADAMS' apart without reading either name.

THE NOTICE CLOSES ON ITS OWN SENTENCE. It opens on the court's own label
('NOTICE:' — a label, not a name) and runs to the first row ending in a
period, which is where '§ 2-102(E).' stands. It carries a fact as well as
a role: a paper the court itself says is 'NOT DESIGNATED FOR PERMANENT
PUBLICATION' is unpublished, and core misses it (measured: all 5 come back
with `publication_status` unset without this reader).

NO NOTICE, NO CLAIM. The court also publishes a designated 'OPINION AND
JUDGMENT ON APPEAL' on this same sheet, and none is in this corpus, so
nothing here is measured against one: a record whose head band shows no
notice returns NOTHING and core's shared walk reads it.

THE PIVOT IS A ROW, NOT A REGEX. The caption is set in CAPITALS, where a
middle initial 'V.' is indistinguishable from the pivot by wording; all 5
set the pivot alone on the page axis, so the caption is split at the ROW
whose entire text is 'V.' and no case-insensitive ' v. ' search is run.

--------------------------------------------------------------------------
BOTH BRANCHES
--------------------------------------------------------------------------

WHERE THE BLOCK ENDS is the BYLINE, and the byline is NOT claimed — core
needs it to open the majority. `authorless` is not a defect and no author
is ever invented; but a paper this reader cannot walk to a byline is a
paper it does not recognize, and it returns NOTHING.

A PARAGRAPH THAT MATCHES NO LANDMARK WITHDRAWS THE WHOLE CLAIM. There is
no catch-all: parking an unrecognized row on `caption` or `case-info` would
be a confident wrong answer, and a hole in the middle of a claim is worse
than no claim at all.

THE GATE IS AFTER THE WALK, NEVER BESIDE IT. wyo shipped with its docket
gate one line above the `finish()` that populates the docket and refused
all 50 of its own correct readings; every test here runs on the finished
context, on fields the walk has already written.

THE PRINTED FORM STAYS BESIDE THE PARSED FORM. `caption` keeps the rows
verbatim and `case_name`/`parties` are built from the two sides of the
pivot; `panel_line` keeps the roster as printed and `panel` the surnames;
`lower_court` keeps the origin recital and `disposition` the sentence the
court closes it with. Wrapped statements are de-hyphenated for the parsed
form only, never in the rendered rows.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# ---- the two sheets, as declared facts -----------------------------------
# A: the Reporter's half-letter book page, 396.0 x 612.0 on all 37.
_SHEET_A_W = 396.0
# B: the memorandum web opinion, a letter sheet, 612.0 x 792.0 on all 5.
_SHEET_B_W = 612.0
_SHEET_TOL = 8.0

# ---- A: the advance-sheet volume page -----------------------------------
# THE TYPE LADDER. The court's own text is 11.0pt; the syllabus 9.0pt; the
# volume apparatus 8.0-8.5pt; the running heads 10.5pt. 10.0 separates the
# court's text from everything below it.
_A_COURT_SIZE_MIN = 10.0
# THE CAPTION IS ON THE AXIS. Every caption row in the 37 records is centred
# on the page axis to 0.01pt — the Reporter sets nothing else in that band.
_AXIS_TOL = 8.0
# THE RUNNING-HEAD PAIR is the dispatch, and page 1 sets it at 10.5pt.
_A_ADVANCE_SHEETS = "nebraska court of appeals advance sheets"
_A_VOLUME_HEAD = re.compile(r"^\d{1,4}\s+Nebraska Appellate Reports$", re.I)
# The pair is rows 0-1 on all 37; the search allows two rows of slack in
# case a record's library header is read as content rather than as a stamp.
_A_HEAD_SEARCH = 3
# THE VOLUME CITE closes the caption band. All 37 print the placeholder the
# advance sheets carry before the N.W. volume is assigned; the numbered form
# is what the same row becomes in the bound reprint, so both are read.
_A_VOL_CITE = re.compile(
    r"^(?:_{2,}|\d{1,4})\s*N\.\s?W\.\s?\d?d\.?\s*(?:_{2,}|\d{1,4})$", re.I)
# A PARAGRAPH OPENS at 66.0 and wraps to the rail at 54.0 — a 12pt step,
# invariant on all 37 records and every one of their 4-6 paragraphs.
_A_PARA_INDENT = 66.0
# The byline stands on page 1 (1 record), 2, 3 or 4. 8 pages covers it with
# margin; a record showing no byline inside it is not this paper.
_A_MAX_PAGES = 8

# ---- B: the memorandum web opinion --------------------------------------
# THE BANNER — the court naming itself, and the dispatch for this sheet.
_B_BANNER = "in the nebraska court of appeals"
# THE HEAD IS BANDED BY WHITESPACE: gaps BETWEEN bands are 34.0/34.4/40.8pt
# and steps INSIDE a band are 13.8/15.0pt on all 5. 25.0 separates them with
# margin at both ends. (Below the notice the caption's own step is 21.0, so
# this measure bounds the HEAD band only and the caption is closed by the
# 'Filed' landmark instead.)
_B_BAND_GAP = 25.0
# The head band never runs past six rows on the 5 records (banner, two title
# rows, the case-name head, two notice rows).
_B_HEAD_MAX = 10
# THE NOTICE opens on the court's own label and closes on its own sentence.
_B_NOTICE = re.compile(r"^NOTICE\b")
_B_UNPUBLISHED = re.compile(
    r"not\s+designated\s+for\s+permanent\s+publication", re.I)
# A PARAGRAPH OPENS at 108.0 and wraps to the rail at 72.0 — a 36pt step,
# invariant on all 5.
_B_PARA_INDENT = 108.0
# THE PIVOT ROW: the caption's own axis row, the whole of whose text is the
# pivot. Read as a ROW because a capitalised caption cannot distinguish a
# middle initial 'V.' from the pivot by wording.
_B_PIVOT_ROW = re.compile(r"^v\.?$", re.I)
# The byline is on page 1 on all 5; 3 pages covers it with margin.
_B_MAX_PAGES = 3

# ---- shared: the landmarks each band carries ----------------------------
_INDENT_TOL = 2.0
# THE FILING ROW carries the date AND the docket, on one line, on all 42:
# 'Filed March 17, 2026.    No. A-25-373.' / 'Filed August 4, 2026.
# Nos. A-26-030, A-26-032.'
_FILED = re.compile(
    r"^Filed\s+(?P<date>[A-Z][a-z]+\s+\d{1,2},\s*\d{4})\.\s*"
    r"Nos?\.\s*(?P<dockets>.+?)\.?$")
# THE ORIGIN's opening words: a closed vocabulary covering 42 of 42. The
# 'Appeals in Nos. … from …' form is dunham_v._dunham, four consolidated
# appeals from two different trial courts.
_ORIGIN = re.compile(
    r"^Appeals?\s+(?:from\b|in\s+Nos?\.)")
# THE PANEL's bench word, spelled out on both papers ('Moore, Bishop, and
# Welch, Judges.' / 'RIEDMANN, Chief Judge, and BISHOP and WELCH, Judges.').
# The PLURAL is what separates a roster from a byline's 'Judge.'.
_ROSTER = re.compile(r"\bJudges\.")
# BENCH WORDS, so a roster yields surnames and not a judge called 'Chief'.
# A closed vocabulary, matched with the token's trailing period removed.
_BENCH_WORD = re.compile(
    r"^(?:Retired\s+)?(?:C\.?\s?J\.?|JJ\.?|Justices?"
    r"|(?:District\s+|Chief\s+|Retired\s+|Senior\s+)?Judges?)$", re.I)
_BENCH_TAIL = re.compile(r"\s+(?:JJ|J|C\.\s?J)\.?$")
# THE APPEARANCES name themselves in their closing words.
_PARTY_STATUS = (r"appellant|appellee|cross-appellant|cross-appellee"
                 r"|plaintiff|defendant|intervenor|respondent|applicant"
                 r"|relator|petitioner|amicus|amici|guardian ad litem")
_COUNSEL = re.compile(r"\bfor\s+(?:%s)" % _PARTY_STATUS, re.I)
_PRO_SE = re.compile(r"\bpro\s+se\b", re.I)
# THE BYLINE — the writing's first row, and the reader's stop. Left
# UNCLAIMED: core opens the majority on it. Both papers spell the title, and
# B sets the surname in capitals.
_BYLINE = re.compile(
    r"^(?:Per\s+Curiam\.|[A-Z][A-Za-z’'\-]*(?:-[A-Z][A-Za-z]+)?,"
    r"\s*(?:Chief\s+|Senior\s+)?Judge\.)$")
# THE DISPOSITION sentence the court closes the origin recital with, in the
# forms the corpus prints. Anchored at a SENTENCE boundary, so the recital's
# own opening 'Appeals in Nos. …' can never be taken for the disposition's
# 'Appeals in Nos. … dismissed.' (dunham prints both).
_DISPOSITION = re.compile(
    r"(?<=\.\s)(?=(?:Affirmed|Reversed|Vacated|Dismissed|Remanded"
    # 'Appeals?\s+in\s+Nos?' ends on a WORD character deliberately: the
    # group closes on `\b`, and an alternative ending in the escaped period
    # of 'Nos.' can never satisfy it (dunham's 'Appeals in Nos. A-25-176,
    # A-25-177, and A-25-337 dismissed.' was silently skipped).
    r"|Appeals?\s+dismissed|Appeals?\s+in\s+Nos?|Judgments?"
    r"|Final\s+order|Sentences?|Cause\s+remanded)\b)")
# The trial judge, as the origin names them: ': Tressa M. Alioth, Judge.'
# and ', Lori A. Maret, Judge,' both occur, as does the capitalised
# ': KANE M. RAMSEY, Judge.' of the memorandum paper. 'Judges' is excluded
# by the word boundary — which is deliberate: roebuck's two-judge recital
# names them 'Richard A. Birch and Cindy R. Volkmer, Judges.', and half a
# name is worse than none.
_TRIAL_JUDGE = re.compile(
    r"[:,]\s*([A-Z][A-Za-z.’'\- ]+?),\s*Judge\b")
# …and the PLURAL form, where one appeal was tried by two judges:
# roebuck_v._north_platte_pub._sch._dist. names them '… for Lincoln County:
# Richard A. Birch and Cindy R. Volkmer, Judges.'. Read only where the
# recital itself uses the plural, and split on the conjunction the page
# prints — never on the roster's, which is a different paragraph.
_TRIAL_JUDGES = re.compile(
    r"[:,]\s*([A-Z][A-Za-z.’'\- ]+?\s+and\s+[A-Z][A-Za-z.’'\- ]+?),"
    r"\s*Judges\b")
# A party's STATUS LABEL, where it stands in the caption's prose. Nebraska
# prints the status after the name it belongs to, so the label is also where
# that party's name ENDS.
_STATUS_AT = re.compile(r",\s*(?:and\s+)?(?:%s)s?\b" % _PARTY_STATUS, re.I)
_PIVOT = re.compile(r",?\s+v\.\s+")
# A SENTENCE BOUNDARY INSIDE A CAPTION, which is not the same thing as a
# period: 'Alicia G. Murphy' and 'Trevor S., Jr.' both print an initial.
# TWO letters of the SAME CASE before the stop is what separates
# 'deceased. Barbara' and 'OF AGE. STATE' from 'G. Murphy' — and what keeps
# 'Jr. et al.' whole, because the following word is lower case.
_SENTENCE = re.compile(r"(?<=[a-z]{2}\.)\s+(?=[A-Z])"
                       r"|(?<=[A-Z]{2}\.)\s+(?=[A-Z])")
# The corpus prints 4 to 6 paragraphs between the caption band and the
# byline; 12 bounds a runaway walk without cutting a real one.
_MAX_PARAS = 12


# --------------------------------------------------------------------------
# text helpers
# --------------------------------------------------------------------------

def _norm(text: str) -> str:
    return " ".join(text.split())


def _dehyphenate(rows: list[str]) -> str:
    """Join wrapped rows the way the page reads them: the Reporter breaks
    'depriv-' / 'ing a litigant' across two rows, and joining those on a
    space invents a word. Used for the PARSED form only — the rendered rows
    keep exactly what the page prints."""
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


def _strip_status(name: str) -> str:
    """The party's name, which runs up to its status label. Statuses are a
    closed vocabulary; party NAMES are never read by wording."""
    out = _norm(name)
    cut = _STATUS_AT.search(out)
    if cut:
        out = out[:cut.start()]
    return out.strip().rstrip(",")


def _panel_names(line: str) -> list[str]:
    """The surnames in a roster, bench words removed."""
    out: list[str] = []
    for token in re.split(r",|\band\b", _norm(line)):
        token = token.strip(" ,").rstrip(".")
        if not token or _BENCH_WORD.match(token):
            continue
        out.append(_BENCH_TAIL.sub("", token))
    return out


def _text(group: list) -> str:
    return " ".join(l.plain for l in sorted(group, key=lambda l: l.x0))


def _centre(group: list) -> float:
    return (group[0].x0 + max(l.x1 for l in group)) / 2


def _rows(pm, finder) -> list[list]:
    """The page's content rows, furniture removed, grouped by baseline. A
    justified line split at a wide gap is two pieces on one baseline, and
    they are one row."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


# --------------------------------------------------------------------------
# the decider
# --------------------------------------------------------------------------

@decider("headmatter.read", court="nebctapp")
def read_headmatter_nebctapp(model, geom, **_):
    """Read one of the court's two papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    if abs(page1.width - _SHEET_A_W) <= _SHEET_TOL:
        return _read_reporter(model, geom, page1)
    if abs(page1.width - _SHEET_B_W) <= _SHEET_TOL:
        return _read_memo(model, geom, page1)
    # A sheet neither paper is set on. Core's shared walk reads it.
    return NOTHING


# --------------------------------------------------------------------------
# A — the advance-sheet volume page
# --------------------------------------------------------------------------

def _read_reporter(model, geom, page1):
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 54.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = [g for pm in model.pages[:_A_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 6:
        return NOTHING

    # ---- the dispatch: the running-head pair, near the top of page 1 -----
    head = None
    for idx in range(min(_A_HEAD_SEARCH, len(rows) - 1)):
        if rows[idx][0].page != 1:
            break
        if _norm(_text(rows[idx])).lower() != _A_ADVANCE_SHEETS:
            continue
        if _A_VOLUME_HEAD.match(_norm(_text(rows[idx + 1]))):
            head = idx
            break
    if head is None:
        return NOTHING

    ctx = _Ctx()
    # Everything from the top of the page down to and including the pair is
    # the volume's own furniture. Core drops it on pages 2..n but not here,
    # and an unclaimed row one step above the caption is what opens a
    # phantom writing over the whole block.
    for idx in range(head + 2):
        ctx.drop(rows[idx], "running-head")

    # ---- the caption: 11pt, centred on the page axis, 2-6 rows ----------
    # It closes at the VOLUME CITE, the landmark below it — never at a row
    # count. Measured: every caption row in the 37 records is 11.0pt and
    # centred on the axis to 0.01pt.
    cap_rows: list[str] = []
    idx = head + 2
    while idx < len(rows) and not _A_VOL_CITE.match(_norm(_text(rows[idx]))):
        group = rows[idx]
        if (group[0].size or 0.0) < _A_COURT_SIZE_MIN:
            return NOTHING          # something stands in the caption band
        if abs(_centre(group) - page1.width / 2) > _AXIS_TOL:
            return NOTHING          # …and it is not set on the axis
        cap_rows.append(_text(group))
        ctx.emit(group, "caption")
        idx += 1
    if not cap_rows or idx >= len(rows):
        return NOTHING

    # ---- the volume cite ------------------------------------------------
    # The row is nothing but a reporter citation for this opinion, so it
    # takes `citation`. Its VALUE is not recorded: all 37 print the blank
    # placeholder the advance sheets carry, and a blank is not a cite. The
    # cite that IS recorded is the 'Cite as' running head, below.
    ctx.emit(rows[idx], "citation")
    idx += 1

    idx = _filing_row(ctx, rows, idx)
    if idx is None:
        return NOTHING

    # ---- the syllabus: every row below the court's type size ------------
    # The court's own numbered points of law, under no heading. Claimed in
    # place, tagged `syllabus`, and NOT lifted into a section: the
    # headmatter renders whole and in the page's order.
    while idx < len(rows) and (rows[idx][0].size or 0.0) < _A_COURT_SIZE_MIN:
        ctx.emit(rows[idx], "syllabus", centre=False)
        idx += 1

    if not _paragraphs(ctx, rows, idx, _A_PARA_INDENT, _A_COURT_SIZE_MIN):
        return NOTHING

    _finish(ctx, cap_rows, "advance-sheet volume page")
    # THE REPORTER'S OWN APPARATUS, read from the rows core dropped as
    # furniture rather than claimed a second time here.
    cite = _reporter_cite(model, finder)
    if cite:
        ctx.crit["citation"] = cite
    short = _short_case_name(page1, finder)
    if short:
        ctx.crit["short_case_name"] = short
    if not _gate(ctx):
        return NOTHING
    return ctx.result()


def _reporter_cite(model, finder) -> str | None:
    """'Cite as 34 Neb. App. 126' -> '34 Neb. App. 126'. READ, not claimed:
    the row repeats on every page, core identifies it as a running head and
    records it in `Dropped`, and this reader only keeps what it says. The
    abbreviation is two words, so the whole tail is taken rather than
    parsed."""
    seen: list[str] = []
    for pm in model.pages:
        for line in pm.lines:
            text = _norm(line.plain)
            if not text.lower().startswith("cite as "):
                continue
            if finder.kind(pm, line) != "running-head":
                continue
            tail = text[len("Cite as "):].strip().rstrip(".")
            if tail and tail not in seen:
                seen.append(tail)
    # Exactly one distinct cite on all 37; more than one is not this paper's
    # apparatus and nothing is guessed from it.
    return seen[0] if len(seen) == 1 else None


def _short_case_name(page1, finder) -> str | None:
    """The Reporter's own short form, from the 8pt running head. Read, not
    claimed: core identifies the row as furniture and drops it."""
    heads = [l for l in sorted(page1.lines, key=lambda l: l.top)
             if finder.kind(page1, l) == "running-head"
             and 7.5 <= (l.size or 0.0) <= 8.6
             and not _norm(l.plain).lower().startswith("cite as")]
    return _norm(heads[0].plain) if heads else None


# --------------------------------------------------------------------------
# B — the memorandum web opinion
# --------------------------------------------------------------------------

def _read_memo(model, geom, page1):
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = [g for pm in model.pages[:_B_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 8:
        return NOTHING

    # ---- the dispatch: the court naming itself, on the axis, first row ---
    if _norm(_text(rows[0])).lower() != _B_BANNER:
        return NOTHING
    if abs(_centre(rows[0]) - page1.width / 2) > _AXIS_TOL:
        return NOTHING

    # ---- the head band, segmented by whitespace -------------------------
    # A step over `_B_BAND_GAP` closes a band. The bands are read by
    # POSITION: band 0 the court, the last band before the notice the
    # case-name head, everything between them the paper's own name.
    bands: list[list[list]] = [[rows[0]]]
    notice_at = None
    for idx in range(1, min(_B_HEAD_MAX, len(rows))):
        group = rows[idx]
        if group[0].page != 1:
            return NOTHING          # the head band never crosses the page
        if _B_NOTICE.match(_norm(_text(group))):
            notice_at = idx
            break
        prev = bands[-1][-1]
        if group[0].top - prev[0].top > _B_BAND_GAP:
            bands.append([group])
        else:
            bands[-1].append(group)
    if notice_at is None or len(bands) < 3:
        # No notice, or no case-name head above it: this is not the paper
        # measured here (the court also prints a DESIGNATED opinion on this
        # sheet, and none is in the corpus). Core's shared walk reads it.
        return NOTHING

    ctx = _Ctx()
    for group in bands[0]:
        ctx.emit(group, "banner")
    ctx.crit["court"] = _dehyphenate([_text(g) for g in bands[0]])
    title_rows: list[str] = []
    for band in bands[1:-1]:
        for group in band:
            ctx.emit(group, "title")
            title_rows.append(_text(group))
    if title_rows:
        ctx.crit["title"] = _dehyphenate(title_rows)
    # The case-name head — the last band before the notice.
    for group in bands[-1]:
        ctx.emit(group, "caption")
    ctx.crit["short_case_name"] = _dehyphenate([_text(g) for g in bands[-1]])

    # ---- the notice: a RUN, closing on its own sentence ------------------
    idx = notice_at
    notice: list[str] = []
    while idx < len(rows):
        text = _norm(_text(rows[idx]))
        ctx.emit(rows[idx], "publication")
        notice.append(text)
        idx += 1
        if text.endswith("."):
            break
    else:
        return NOTHING              # the notice never closed
    if _B_UNPUBLISHED.search(" ".join(notice)):
        # The court's own words about its own paper.
        ctx.crit["publication_status"] = "unpublished"

    # ---- the caption: centred on the axis, closing at the 'Filed' row ----
    cap_rows: list[str] = []
    cap_groups: list[list] = []
    while idx < len(rows) and not _FILED.match(_norm(_text(rows[idx]))):
        group = rows[idx]
        if group[0].page != 1:
            return NOTHING
        if abs(_centre(group) - page1.width / 2) > _AXIS_TOL:
            return NOTHING          # a row off the axis inside the caption
        cap_rows.append(_text(group))
        cap_groups.append(group)
        ctx.emit(group, "caption")
        idx += 1
    if not cap_rows or idx >= len(rows):
        return NOTHING

    idx = _filing_row(ctx, rows, idx)
    if idx is None:
        return NOTHING
    if not _paragraphs(ctx, rows, idx, _B_PARA_INDENT, 0.0):
        return NOTHING

    ctx.crit["caption"] = [_norm(r) for r in cap_rows]
    _memo_parties(ctx, cap_rows, cap_groups)
    if ctx.counsel:
        ctx.crit["attorneys"] = " ".join(ctx.counsel)
    ctx.crit["headmatter_style"] = "memorandum web opinion"
    if not _gate(ctx):
        return NOTHING
    return ctx.result()


def _memo_parties(ctx, cap_rows: list[str], cap_groups: list[list]) -> None:
    """The two sides of the pivot ROW. A capitalised caption cannot tell a
    middle initial 'V.' from the pivot by wording, and all 5 records set the
    pivot alone on the page axis, so the split is made at the row."""
    pivots = [i for i, g in enumerate(cap_groups)
              if _B_PIVOT_ROW.match(_norm(_text(g)))]
    if len(pivots) != 1:
        return
    cut = pivots[0]
    left = _strip_status(_SENTENCE.split(_dehyphenate(cap_rows[:cut]))[-1])
    right = _strip_status(_SENTENCE.split(_dehyphenate(cap_rows[cut + 1:]))[0])
    if not left or not right:
        return
    ctx.crit["parties"] = [left, right]
    ctx.crit["case_name"] = f"{left} v. {right}"


# --------------------------------------------------------------------------
# shared bands
# --------------------------------------------------------------------------

def _filing_row(ctx, rows: list[list], idx: int) -> int | None:
    """ONE ROW, TWO FACTS. The row is the paper's filing line — that is what
    it calls itself — so it renders as `date`, and the docket it carries is
    recorded in the criteria rather than tinted onto a second role the page
    does not print. A CITATION IS NOT A DOCKET and never lands here."""
    if idx >= len(rows):
        return None
    filed = _FILED.match(_norm(_text(rows[idx])))
    if not filed:
        return None
    ctx.emit(rows[idx], "date")
    ctx.crit["decision_date"] = _norm(filed.group("date"))
    # 'A-26-030, A-26-032' / 'A-25-176, A-25-177, A-25-337, A-25-338' — a
    # range prints only its endpoints, so only its endpoints are recorded.
    dockets = [t.strip() for t in
               re.split(r",|\bthrough\b", filed.group("dockets"))
               if t.strip()]
    if dockets:
        ctx.crit["docket_number"] = dockets[0]
        if dockets[1:]:
            ctx.crit["other_dockets"] = dockets[1:]
    return idx + 1


def _paragraphs(ctx, rows: list[list], idx: int, indent: float,
                size_min: float) -> bool:
    """The court's own paragraphs, each asked ONCE what it is, and each
    identified by a landmark it carries — never by its position in the run.
    Returns False (withdraw the claim) unless the walk reaches a byline."""
    paras: list[tuple[list, list[str]]] = []
    while idx < len(rows) and len(paras) <= _MAX_PARAS:
        group = rows[idx]
        first = group[0]
        if (first.size or 0.0) < size_min:
            return False            # the syllabus band is closed for good
        if first.x0 >= indent - _INDENT_TOL:
            paras.append(([group], [_text(group)]))
        elif paras:
            paras[-1][0].append(group)
            paras[-1][1].append(_text(group))
        else:
            return False            # a wrap with nothing to wrap onto
        # A paragraph is only decidable once it is whole, so the walk looks
        # one row ahead: it closes at the next row that opens at the indent,
        # or at the end of the block.
        idx += 1
        nxt = rows[idx] if idx < len(rows) else None
        if nxt is not None and nxt[0].x0 < indent - _INDENT_TOL \
                and (nxt[0].size or 0.0) >= size_min:
            continue
        groups, texts = paras[-1]
        text = _dehyphenate(texts)
        if _BYLINE.match(text):
            # THE PAPER'S OWN WRITING STARTS HERE. The byline is left in the
            # stream: core opens the majority on it.
            paras.pop()
            return True
        # THE ORIGIN IS TESTED BEFORE THE ROSTER. roebuck's recital names
        # two trial judges — '… Richard A. Birch and Cindy R. Volkmer,
        # Judges. Affirmed.' — so the recital carries the roster's own bench
        # word, and asking the roster first would file the origin as a panel.
        if len(paras) == 1 and _ORIGIN.match(text):
            _origin(ctx, text)
            for g in groups:
                ctx.emit(g, "lower-court", centre=False)
            continue
        if _ROSTER.search(text):
            ctx.crit.setdefault("panel_line", text)
            ctx.crit.setdefault("panel", _panel_names(text))
            for g in groups:
                ctx.emit(g, "panel", centre=False)
            continue
        if _COUNSEL.search(text) or _PRO_SE.search(text):
            ctx.counsel.append(text)
            for g in groups:
                ctx.emit(g, "counsel", centre=False)
            continue
        # NO CATCH-ALL. An unidentified paragraph inside the block would
        # either be mis-tinted or leave a hole in the claim, and both are
        # worse than handing the record back to core whole.
        return False
    return False                    # ran out of block without a byline


def _origin(ctx, text: str) -> None:
    """Split the origin recital from the disposition it closes on, and name
    the judge it names. The two are separate facts printed as one paragraph,
    and the paragraph itself renders whole as `lower-court`."""
    cut = _DISPOSITION.search(text)
    recital = text[:cut.start()].strip() if cut else text
    ctx.crit["lower_court"] = recital
    if cut:
        ctx.crit["disposition"] = text[cut.start():].strip()
    judges = [_norm(j) for j in _TRIAL_JUDGE.findall(recital)]
    for pair in _TRIAL_JUDGES.findall(recital):
        judges.extend(_norm(j) for j in re.split(r"\s+and\s+", pair))
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)


def _finish(ctx, cap_rows: list[str], style: str) -> None:
    ctx.crit["caption"] = [_norm(r) for r in cap_rows]
    _caption(ctx, cap_rows)
    if ctx.counsel:
        # criteria.attorneys is not reachable from a reader that keeps its
        # counsel INSIDE the headmatter (core-patch-queue item 41), so the
        # reader that read them states them.
        ctx.crit["attorneys"] = " ".join(ctx.counsel)
    # The layout contract, named for the landmark it always prints.
    ctx.crit["headmatter_style"] = style


def _caption(ctx, cap_rows: list[str]) -> None:
    """The two sides of the pivot, with their statuses stripped.

    The Reporter sets its caption as running prose, so a juvenile record
    prints two sentences with a pivot in the second ('In re Interest of
    Trevor S., Jr., et al., children under 18 years of age.' over 'State of
    Nebraska, appellee and cross-appellee, v. Trevor S., Sr., appellant,
    …'). Where the printed caption holds exactly ONE pivot the parties are
    read off it; where it holds none or several, nothing is invented — the
    verbatim rows are already recorded."""
    whole = _dehyphenate(cap_rows)
    parts = _PIVOT.split(whole)
    if len(parts) != 2:
        return
    left = _strip_status(_SENTENCE.split(parts[0])[-1])
    right = _strip_status(_SENTENCE.split(parts[1])[0])
    if not left or not right:
        return
    ctx.crit["parties"] = [left, right]
    ctx.crit["case_name"] = f"{left} v. {right}"


def _gate(ctx) -> bool:
    """THE GATE RUNS ON THE FINISHED CONTEXT. wyo shipped its docket gate one
    line above the walk that populates the docket and refused all 50 of its
    own correct readings; every field tested here has already been written
    by the walk above. Each is present on all 42 records, so a missing one
    means the walk went somewhere this reader has not measured."""
    crit = ctx.crit
    return bool(crit.get("caption") and crit.get("decision_date")
                and crit.get("docket_number") and crit.get("lower_court")
                and crit.get("panel_line") and ctx.counsel)


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.counsel: list[str] = []

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
