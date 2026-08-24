"""Wisconsin Court of Appeals ('wisctapp').

Everything unique to wisctapp lives here. It imports core, never another
court file, and no other court file imports it — not even `wis.py`, whose
approach this file copies and whose code it does not touch. Its CourtProfile
is already registered in courts/__init__.py; this module only binds the
reader.

WHICH SHAPE IS THIS? A DRAWN MARK, and a HORIZONTAL one. Counted over all
30 records, every page: **VERTICAL RULES CORPUS-WIDE = 0**. The only rules
these pages draw are

    443.00 / 443.72pt at x0 98.06 or 103.46   the SLIP FENCE PAIR — one
                                              above the caption, one below
    468.07pt          at x0 72.02             the COVER FENCE, 4 per cover
    144.02pt          at x0 108.02            the footnote separator
                                              (measured on lowell x2)

The measure alone separates all three (72.4% / 76.5% / 23.5% of a 612pt
sheet). No typed `)` or `:` column either — no row anywhere in the 30
records consists of rail glyphs alone. So the taxonomy entry for wisctapp is
the scctapp one: A DRAWN HORIZONTAL FENCE, NO VERTICALS ANYWHERE — with two
qualifications that are themselves measurements:

  * THE CAPTION IS ONE COLUMN and no second column is invented (the
    iowactapp / nmctapp / scctapp ruling). Its parties stand at a single
    rail — x0 = 103.6 or 108.9, exactly, on every party row of every record
    — and the party statuses are INDENTED from it, not set beside it.
  * THE MASTHEAD IS TWO COLUMNS with NOTHING DRAWN BETWEEN THEM (the va /
    calctapp shape). The gutter is measured, not assumed: over the 30
    records the left column's rightmost ink reaches x1 = 302.9 and the right
    column's leftmost ink starts at x0 = 311.7 — an 8.8pt band no glyph
    crosses. Taken by the ROW'S OWN x0 the clearance is far wider: the
    left column's largest x0 is 191.0 and the right column's smallest is
    311.7, so the page axis (306.0) sits inside a 120.7pt band and `x0 <
    width/2` splits the columns on every row of every record.

THE PAPER, and there are two of them.

FORMAT 1 — THE FILED SLIP (27 of 30 records; the 3 published ones print it
too, behind their cover). Page 1, whole:

    ┌──────────────────────────────────────────────────────────────────┐
    │                                              2026 WI App 35      │  the citation, flush
    │        COURT OF APPEALS            NOTICE                        │  right, 4 records
    │           DECISION          This opinion is subject to further   │
    │        DATED AND FILED      editing.  If published, the official │  the CLERK'S STAMP,
    │         May 27, 2026        version will appear in the bound     │  centred in the LEFT
    │      Samuel A. Christensen  volume of the Official Reports.      │  column …
    │     Clerk of Court of Appeals   A party may file with the …      │
    │                                                 …RULE 809.62.    │  … and the standing
    │                                        Cir. Ct. No.  2021CV360   │  publication NOTICE
    │  Appeal No.   2024AP2425                                         │  in the right, which
    │  STATE OF WISCONSIN            IN COURT OF APPEALS               │  is boilerplate and
    │                                    DISTRICT II                   │  is Dropped
    │  ──────────────────────────────────────────────────────────────  │  FENCE
    │  BURT J. STEFFES,                                                │  the CAPTION band:
    │        PLAINTIFF-APPELLANT,                                      │  names at the rail,
    │     V.                                                           │  statuses indented,
    │  FOND DU LAC REGIONAL CLINIC, S.C. AND FOND DU LAC REGIONAL      │  the pivot half as
    │  CLINIC, S.C. RETIREMENT PLAN C/O KATE M. COLE, PLAN             │  far in
    │  ADMINISTRATOR,                                                  │
    │        DEFENDANTS-RESPONDENTS.                                   │
    │  ──────────────────────────────────────────────────────────────  │  FENCE
    │      APPEAL from an order of the circuit court for Fond du Lac   │  the ORIGIN, one
    │  County: TRICIA L. WALKER, Judge.  Reversed and cause remanded.  │  statement
    │      Before Neubauer, P.J., Gundrum, and Grogan, JJ.             │  the PANEL
    │      Per curiam opinions may not be cited …  RULE 809.23(3).     │  the 809.23(3) notice
    │      ¶1  GUNDRUM, J.   Dermatologist Burt J. Steffes appeals …   │  …and the writing
    └──────────────────────────────────────────────────────────────────┘

FORMAT 2 — THE PUBLISHED COVER (3 records: benjean_f._lara,
katina_papanastasiou, state_v._latres_christopher_robinson). A reporter
cover sheet is bound AHEAD of the slip, so the slip masthead lands on page 2
or 3 and the headmatter spans every page up to it. The cover is a
LABEL/VALUE GRID fenced by four 468.07pt rules:

                                                   2026 WI App 23   citation
                    COURT OF APPEALS OF WISCONSIN                   court
                         PUBLISHED OPINION                          the paper's name
    Case No.:        2024AP1685                                     docket
    ─────────────────────────────────────────────────────────────── FENCE
                                       †Petition for Review filed
    Complete Title of Case:
              STATE OF WISCONSIN EX REL. BENJEAN F. LARA,           the same caption
                        PETITIONER-APPELLANT,                       grammar as the slip
    ─────────────────────────────────────────────────────────────── FENCE
    Opinion Filed:   March 18, 2026                                 dates
    Oral Argument:   November 5, 2025
    ─────────────────────────────────────────────────────────────── FENCE
    JUDGES:          White, C.J., Colón, P.J., and Geenen, J.       the panel
    Concurred:
    Dissented:
    ─────────────────────────────────────────────────────────────── FENCE
    Appellant
    ATTORNEYS:       On behalf of the petitioner-appellant, …        COUNSEL, to the end
                                                                    of the cover pages

    The grid's two rails are measured: labels at x0 = 77.4, values at
    x0 = 190.4, the caption at 148.3-148.6. A label and its value share a
    baseline, so they are read as ONE row.

WHAT THE CAPTION BAND HOLDS, and how it is told apart. This court sets its
whole caption BOLD, so wis's roman/italic test does not transfer — the
INDENT does, and it is exact. Measured against each band's own rail over all
30 records, with no other value occurring anywhere:

    d =  0.0                a PARTY NAME (and every wrap of one)
    d = 26.4  or  72.0      a PARTY STATUS  ('PLAINTIFF-APPELLANT,')
    d = 13.2  or  36.0      the PIVOT — exactly half the status indent, and
                            its whole text is 'V.'

Two indent templates (26.4/13.2 on 22 records, 72.0/36.0 on 8), so the
statuses are found by 'indented from the rail', never by a value. A status
is therefore never read from a vocabulary of statuses, which matters:
'INVOLUNTARY-PLAINTIFF' (lizbeth_hernandez_ramirez), 'THIRD-PARTY
DEFENDANT-APPELLANT' (lowell x2), 'PLAINTIFF-CO-APPELLANT' (herbal_aspect)
and 'INTERVENOR' (jennifer_munnik) all occur.

THE BAND'S OWN LEADING SEPARATES ITS ELEMENTS, exactly 2:1. Inside an
element (a wrapped party name) the step is 14.9-15.0pt; between elements it
is 29.9-30.0pt. Stated as a fraction of the band's own LARGEST step, because
every caption prints at least one 30pt step (the pivot always stands alone)
while a caption with no wrapped name has no 15pt step at all — an anchor on
the smallest step would then declare the whole band one element.

THE MATTER TITLE IS A RAIL ELEMENT WITH NO STATUS UNDER IT.
county_of_trempealeau opens 'IN THE MATTER OF THE REFUSAL OF LAYNE PERRY
STENBERG:' at the rail, then 'COUNTY OF TREMPEALEAU,' at the rail with
'PLAINTIFF-RESPONDENT,' indented under it. Read as a party the case name
became 'IN THE MATTER OF … STENBERG: COUNTY OF TREMPEALEAU v. …'. A party
group always prints its status; a matter title never does. Same rule wis
needed for its 15 disciplinary records, restated in indent terms.

THE TAIL IS A STACK OF PARAGRAPHS, and their own leading names them. Below
the second fence the step inside a paragraph is 24.0pt and between
paragraphs 36.0pt on all 30 records; each paragraph is indented 72pt on its
first line. In order: the ORIGIN (opens on the route word), the PANEL (opens
on 'Before'), and on the records that print it the RULE 809.23(3) notice —
11pt where the body is 13pt, and BOLD, which is what tells it from a
FOOTNOTE set at the same 11pt and not bold (lowell x2, tamra_schott). The
reader ends there; the '¶1' that follows is the writing's and is not touched.

THE PANEL MAY BE ON THE NEXT PAGE. lowell x2 fill page 1 with the origin and
a footnote and print 'Before Gundrum, Grogan, and Lazar, JJ.' at the top of
page 2, under the running head. Both records are read whole; the claim
simply continues onto the following page's first paragraph. A record with no
panel paragraph in either place is not this contract and is declined.

WHAT THE DISPOSITION IS: THE ITALIC RUN. The origin's closing sentence is
set in italic and the judge's name before it is not — 'TRICIA L. WALKER,
Judge.  *Reversed and cause remanded*.' — on all 30 records, the closing
period sometimes left roman and once carrying a footnote mark ('.1', lowell
x2). So `disposition` is read off the TYPEFACE and never off a vocabulary of
dispositions; 'Orders affirmed; order reversed and cause remanded for
further proceedings' (lizbeth_hernandez_ramirez) would defeat one.

THIS COURT NAMES ITSELF IN TEXT, so `criteria.court` is SET — unlike wis,
which prints its name only as a 364x34pt blackletter graphic. wisctapp
prints no images at all (0 across the corpus): the slip stamp types 'COURT
OF APPEALS' at 14pt and the cover types 'COURT OF APPEALS OF WISCONSIN' at
16pt. The value is whichever of those the record prints, VERBATIM and
unjoined — 'STATE OF WISCONSIN' and 'DISTRICT IV' are separate printed rows
of the same banner and welding the three into one string would be an
invention, so they are tagged `court` in the block and left there. (See the
final report: `Criteria` has no division field for 'DISTRICT IV'.)

CITATION IS NOT THE DOCKET, and this court prints both — the trap that cost
`ill` its whole corpus (commit 03e8652):

    'Appeal No.  2024AP2425'   -> role `docket`,   `docket_number`
    'Case No.:   2024AP1685'   -> role `docket`,   `docket_number`  (cover)
    'Cir. Ct. No.  2021CV360'  -> role `docket`,   `lower_court_docket`
    '2026 WI App 35'           -> role `citation`, `citation`

`citation` IS ALSO THE ONLY PUBLICATION SIGNAL THIS READER TRUSTS, and it is
read from the HEADMATTER ROW ONLY. Item 24 of the core queue is exactly the
error in the other direction, and this corpus is full of the bait:

  * 27 of the 30 records cite an OLDER 'WI App' volume in their BODY text,
    so a citation scan reports the wrong volume on 27 records;
  * 4 records — two of them PUBLISHED — cite 'RULE 809.23(3)' in a footnote
    or an argument, so a text search for the notice reports the wrong status
    on those two;
  * and the RULE 809.23(3) notice that IS printed in the headmatter is a
    standing citability caution on the per curiam FORM, not this paper's
    status: state_v._gustin_j._king prints it above the writing and
    'Recommended for publication in the official reports.' below it.

So `published` is written on the 4 records whose HEADMATTER prints a
'20xx WI App n' cite or a 'PUBLISHED OPINION' cover, and `publication_status`
is left UNSET on the other 26 — which is what their own masthead notice
says ('If published, the official version will appear in the bound volume of
the Official Reports'). The 27 'Recommended for publication in the official
reports.' rows this court prints at the FOOT of its writing are the real
answer for the rest, and no headmatter reader can reach them: they are
inside an assembled writing and there is no `endmatter.read` seam (queue
item 39). Reported, not guessed at.

AUTHORLESS IS NOT A DEFECT (the user's ruling, 2026-08-19). state_v._gustin_
j._king opens '¶1 PER CURIAM.' and no author is invented for it.

CORE ITEMS CLOSED HERE, NOT PATCHED (notes/core-patch-queue.md):

  item 41  `criteria.attorneys` is unreachable for a reader that keeps
           counsel in the headmatter. Closed the way seven courts have now
           closed it: the counsel rows stay where the cover prints them and
           this reader writes `crit["attorneys"]` itself.
  item 22  not reachable — this court prints NO images on any page of any
           record, so there is no masthead graphic to plant in a writing.
  item 24  not reachable once the status is read from the headmatter row,
           as above. Reported, not patched.
  item 6   not reachable — the running head ('No.  2024AP4') and the folio
           are recognized by core's own FurnitureFinder on every
           continuation page of all 30 records, checked and not assumed, and
           this reader skips whatever that finder claims rather than
           matching wording.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import find_date

STYLE_SLIP = "wisctapp filed slip"
STYLE_COVER = "wisctapp published cover"

# ---- wisctapp's declared facts (measured over all 30 records) ------------

# THE SLIP FENCE PAIR. 443.00pt and 443.72pt, x0 98.06 or 103.46, exactly
# two per slip page on all 30 records. 72.4% of a 612pt sheet.
_SLIP_FENCE = (440.0, 447.0)
# THE COVER FENCE. 468.07pt at x0 72.02, exactly four on the cover's first
# page of all 3 published records. 76.5% of the sheet.
_COVER_FENCE = (466.0, 470.0)
_COVER_FENCE_COUNT = 4
# The footnote separator is 144.02pt and is excluded by either gate.

# THE MASTHEAD GUTTER. Nothing is drawn in it. By the row's own x0 the left
# column's largest value is 191.0 and the right column's smallest is 311.7,
# so the page axis splits them with 115pt of clearance on the left and 5.7pt
# on the right; by INK the gutter is 302.9 -> 311.7.
_AXIS_SPLIT = 0.5
# THE PRINTED LINE, across both columns. Two columns do not share a baseline
# exactly: 'Appeal No.  2024AP2425' and the 'Cir. Ct. No.  2021CV360' beside
# it are set 0.62-0.79pt apart on all 30 records (the right column is a
# smaller type), and 'STATE OF WISCONSIN' / 'IN COURT OF APPEALS' are set at
# 0.0. The smallest gap between two rows in the SAME column, notice
# excluded, is 9.12pt. So rows within 4.0pt are ONE printed line and the
# left column is read first — otherwise the headmatter emits the circuit
# court's number one row above the appeal number it stands beside, which is
# not the order the page reads in.
_LINE_BAND = 4.0

# THE CAPTION RAIL, and the two indent templates measured off it:
#   status 26.4 / pivot 13.2   (22 records)
#   status 72.0 / pivot 36.0   ( 8 records)
# A row is AT the rail within 2pt (every party row measures 0.0) and
# INDENTED beyond 8pt (the smallest indent printed is 13.2).
_RAIL_TOL = 2.0
_INDENT_MIN = 8.0
# THE CAPTION'S ELEMENT BREAK. Inside an element 14.9-15.0pt, between
# elements 29.9-30.0pt — a clean 2:1. Anchored on the band's LARGEST step
# because every caption prints a 30pt one and a caption without a wrapped
# name prints no 15pt one at all. Measured ratios: 0.497-0.502 inside,
# 0.997-1.000 between.
_ELEMENT_BREAK = 0.70

# THE TAIL'S PARAGRAPH BREAK. Inside a paragraph 24.0pt, between paragraphs
# 36.0pt, on all 30 records; 30.0 sits 6pt clear of both.
_PARA_BREAK = 30.0

# THE ROUTE WORD the origin statement opens on: 'APPEAL from a judgment of
# …', 'APPEAL from orders of …'. A closed vocabulary of appellate ROUTES,
# never a read of a court name.
_ROUTE = re.compile(r"^(?:APPEALS?|CERTIFICATION|PETITION|ORDER)\b")
# 'Before Neubauer, P.J., Gundrum, and Grogan, JJ.' — the panel paragraph's
# own opener, printed on all 30 records.
_PANEL_OPEN = re.compile(r"^Before\b")
# THE BENCH TITLES this court abbreviates with. A closed role vocabulary, so
# a roster yields three judges and not a judge called 'and'.
_BENCH = re.compile(r"^(?:C\.J\.|P\.J\.|JJ\.|J\.|Reserve\s+J\.)$")
# '(Reserve )Judge.' closes the trial judge's name inside the origin.
_TRIAL_JUDGE = re.compile(
    r":\s*(?P<name>.+?),\s*(?:Reserve\s+|Chief\s+)?Judge\.")
# 'circuit court for Fond du Lac County' / 'circuit court for La Crosse
# County' — bounded by the court's own label words, so the county reads as
# printed however it is spelled.
_COURT_BELOW = re.compile(r"((?:circuit|municipal)\s+court\s+for\s+.+?\s+County)",
                          re.I)

# THE COURT NAMING ITSELF, in text, on the two papers.
_COURT_SLIP = re.compile(r"^COURT OF APPEALS$")
_COURT_COVER = re.compile(r"^COURT OF APPEALS OF WISCONSIN$")
# The stamp's own legend, and the paper's own name.
_TITLE_SLIP = re.compile(r"^DECISION$")
_STAMP_DATE_LABEL = re.compile(r"^DATED AND FILED$")
_BANNER_STATE = re.compile(r"^STATE OF WISCONSIN$")
_BANNER_COURT = re.compile(r"^IN COURT OF APPEALS$")
_BANNER_DISTRICT = re.compile(r"^DISTRICT\s+[IVX]+$")
# 'PUBLISHED OPINION' — the cover's own name for the paper AND its
# publication flag.
_COVER_TITLE = re.compile(r"^PUBLISHED OPINION$")

# THE NUMBERS. 'Appeal No.  2024AP2425' / 'Appeal Nos. …' / 'Case No.:
# 2024AP1685'; the token itself is year + 'AP' + serial + an optional
# suffix ('-CR', '-CRNM', '-FT', '-NM').
_APPEAL_LABEL = re.compile(r"^Appeal\s+Nos?\.", re.I)
_CASE_LABEL = re.compile(r"^Case\s+Nos?\.:?", re.I)
_CIRCUIT_LABEL = re.compile(r"^Cir\.\s*Ct\.\s*Nos?\.", re.I)
_APPEAL_NO = re.compile(r"\b\d{4}AP\d{1,5}(?:-[A-Z]{2,4})?\b")
_CIRCUIT_NO = re.compile(r"\b\d{4}[A-Z]{2}\d{1,6}\b")
# THE PUBLIC-DOMAIN CITE. The appellate series is 'WI App' — never 'WI',
# which is the Supreme Court's ('2025 WI 23').
_CITE = re.compile(r"^\d{4}\s+WI\s+App\s+\d{1,4}$")

# THE STANDING PUBLICATION NOTICE, in the masthead's right column. It is a
# RUN, and its own leading closes it: the right-half rows set below the body
# size, broken wherever the page leaves a bigger step than the run's own.
# Measured over all 30 records — inside the run the step is 8.4-21.6pt (the
# 21.6 being its 'NOTICE' heading down to its first line, which is why the
# heading comes with the run instead of being hunted separately); the gaps
# that bound it are 33.7-42.7pt below (down to 'Cir. Ct. No.') and 43.9-45.8
# above (up to the citation row). 27.0 sits 5.4pt clear of both.
#
# The rail is NOT the anchor: the run's first line hangs 29.5pt left of the
# other five on 26 records ('  This opinion is subject to further editing.'
# begins with a space), so a modal-rail test drops it and the claim is not
# total. Three rows deep is the minimum, which the citation row's singleton
# run and the 'Cir. Ct. No.' row never reach.
_NOTICE_MIN_ROWS = 3
_NOTICE_RUN_BREAK = 27.0

# THE RULE 809.23(3) NOTICE in the tail: 11pt where the body is 13pt, and
# BOLD, which separates it from a footnote set at the same size.
# (state_v._gustin_j._king is the one record in this corpus that prints it.)

# THE COVER GRID'S RAILS: labels at 77.4, values at 190.4, sub-labels
# ('Concurred:', 'Dissented:') at 113.4, the caption at 148.3-148.6.
_COVER_LABEL = re.compile(
    r"^(Case Nos?\.:?|Complete Title of Case:|Opinion Filed:"
    r"|Submitted on Briefs:|Oral Argument:|JUDGES:|Concurred:|Dissented:"
    r"|Appellant|Respondent|Petitioner|Appellants|Respondents"
    r"|ATTORNEYS:|Petition for Review filed)")
_COVER_DATE_LABEL = re.compile(
    r"^(Opinion Filed:|Submitted on Briefs:|Oral Argument:)\s*(.*)$")
_COVER_JUDGES = re.compile(r"^JUDGES:\s*(.*)$")
_COVER_SIDE = re.compile(
    r"^(Appellant|Respondent|Petitioner|Appellants|Respondents"
    r"|Petitioners|Cross-Appellant|Cross-Respondent|Guardian ad Litem)$")
_COVER_ATTY = re.compile(r"^ATTORNEYS:")
_COVER_REVIEW = re.compile(r"^†?\s*Petition for Review filed")


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row — the pieces the page set on one baseline, in one column
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row. pdfio splits a line at its widest gaps, and this court
    needs the split BOTH ways: the masthead's two columns arrive on shared
    baselines and must stay apart, while the cover grid's label and value
    also share a baseline and must come back together. So a row is the
    pieces on one baseline THAT LIE ON THE SAME SIDE OF THE PAGE AXIS —
    which is the same 120.7pt gutter that names the masthead's columns."""

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold",
                 "italic_text", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))
        self.italic_text = _norm("".join(
            (c.get("text") or "") for p in self.pieces for c in p.chars
            if any(s in (c.get("fontname") or "")
                   for s in ("Italic", "Oblique"))))

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    @property
    def centre(self) -> float:
        return (self.x0 + self.x1) / 2

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _rows(pm, finder, lo: float | None = None,
          hi: float | None = None) -> list:
    """The page's content rows between two tops, in the page's own order.

    Whatever core's FurnitureFinder claims — the 'No.  2024AP4' running head
    and the folio, on every continuation page of all 30 records — is skipped
    rather than claimed, so a Dropped this reader does not own is not
    duplicated as an item."""
    axis = pm.width * _AXIS_SPLIT
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        if lo is not None and line.top <= lo:
            continue
        if hi is not None and line.top >= hi:
            continue
        key = (round(line.top, 1), line.x0 >= axis)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    out = [_Row(groups[k]) for k in order]
    # …then put the page's own reading order back: within one printed line,
    # the left column first.
    band = 0
    start = None
    keyed = []
    for row in out:
        if start is None or row.top - start > _LINE_BAND:
            band += 1
            start = row.top
        keyed.append((band, row.x0 >= axis, row))
    keyed.sort(key=lambda t: (t[0], t[1]))
    return [t[2] for t in keyed]


def _fences(pm, gate) -> list:
    return sorted((r for r in (pm.h_rules or [])
                   if gate[0] <= r.width <= gate[1]), key=lambda r: r.top)


def _paragraphs(rows: list, limit: float) -> list:
    """Split a stack of rows where the page leaves a step bigger than
    ``limit``."""
    if not rows:
        return []
    out = [[rows[0]]]
    for prev, row in zip(rows, rows[1:]):
        if row.top - prev.top > limit:
            out.append([row])
        else:
            out[-1].append(row)
    return out


def _elements(rows: list) -> list:
    """The caption band's elements, split on its own largest step."""
    if len(rows) < 2:
        return [list(rows)]
    steps = [b.top - a.top for a, b in zip(rows, rows[1:])]
    limit = _ELEMENT_BREAK * max(steps)
    out = [[rows[0]]]
    for row, step in zip(rows[1:], steps):
        if step > limit:
            out.append([row])
        else:
            out[-1].append(row)
    return out


def _panel_names(text: str) -> list:
    """The judges a roster names. The bench titles are a closed vocabulary,
    so 'Before White, C.J., Colón, P.J., and Geenen, J.' is three people and
    none of them is called 'and'."""
    flat = re.sub(r"^(?:Before|JUDGES:)\s*", "", _norm(text)).rstrip(". ")
    out: list[str] = []
    for part in flat.split(","):
        name = re.sub(r"^and\s+", "", part.strip()).strip()
        if not name or _BENCH.match(name + ("" if name.endswith(".") else ".")):
            continue
        if _BENCH.match(name):
            continue
        out.append(name)
    return out


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:

    def __init__(self, page_width: float, body_x0: float):
        self.page_width = page_width
        self.body_x0 = body_x0
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.counsel: list[str] = []

    def row(self, row: _Row, role: str, align: str = "L") -> None:
        if align == "C":
            rel = round(row.centre - self.page_width / 2, 1)
        else:
            rel = round(row.x0 - self.body_x0, 1)
            if abs(rel) <= _RAIL_TOL:
                rel = 0.0
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, italic=bool(row.italic_text), rel=rel, role=role))
        self.consumed.update(row.ids)

    def drop(self, rows: list, kind: str) -> None:
        if not rows:
            return
        text = _norm(" ".join(r.text for r in rows))
        ids = tuple(i for r in rows for i in r.ids)
        self.dropped.append(m.Dropped(text=text,
                                      prov=m.Prov(rows[0].page, ids),
                                      kind=kind))
        self.consumed.update(ids)

    def rule(self, page: int) -> None:
        self.items.append(m.Rule(prov=m.Prov(page), span="full"))

    def once(self, key: str, value) -> None:
        if value and not self.crit.get(key):
            self.crit[key] = value

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="wisctapp")
def read_headmatter_wisctapp(model, geom, **_):
    """Read wisctapp's filed slip (with or without its reporter cover), or
    NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 108.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE SLIP PAGE IS THE ONE THAT DRAWS THE FENCE PAIR. It is page 1 on 27
    # records and page 2 or 3 on the 3 that bind a reporter cover ahead of
    # it. No fence pair, no claim.
    slip = None
    for pm in model.pages:
        if len(_fences(pm, _SLIP_FENCE)) == 2:
            slip = pm
            break
    if slip is None:
        return NOTHING
    covers = [pm for pm in model.pages if pm.number < slip.number]
    if covers and len(_fences(covers[0], _COVER_FENCE)) != _COVER_FENCE_COUNT:
        return NOTHING

    ctx = _Ctx(slip.width, body_x0)
    if covers and not _read_cover(ctx, covers, finder, body_size):
        return NOTHING
    if not _read_slip(ctx, slip, model, finder, body_size):
        return NOTHING

    # POPULATE BEFORE GATING. wyo shipped its `docket_number` gate one line
    # above the call that fills it and refused 50 correctly-read records.
    if not ctx.crit.get("docket_number") or not ctx.crit.get("caption"):
        return NOTHING
    if ctx.counsel:
        # ITEM 41, closed in the file that owns the reading.
        ctx.crit["attorneys"] = _norm(" ".join(ctx.counsel))[:4000]
    ctx.crit["headmatter_style"] = STYLE_COVER if covers else STYLE_SLIP
    return ctx.result()


# ---- the filed slip ------------------------------------------------------

def _read_slip(ctx, pm, model, finder, body_size: float) -> bool:
    fences = _fences(pm, _SLIP_FENCE)
    head = _rows(pm, finder, hi=fences[0].top)
    band = _rows(pm, finder, lo=fences[0].top, hi=fences[1].top)
    if not head or not band:
        return False
    if not _read_masthead(ctx, pm, head, body_size):
        return False
    ctx.rule(pm.number)
    if not _read_caption(ctx, band):
        return False
    ctx.rule(pm.number)
    return _read_tail(ctx, pm, model, finder, fences[1].top, body_size)


def _notice_rows(rows: list, page_width: float, body_size: float) -> list:
    """The standing publication notice — the right column's own small-print
    COLUMN, found by its rail and never by its wording."""
    axis = page_width * _AXIS_SPLIT
    small = [r for r in rows if r.x0 >= axis and r.size < body_size]
    for run in _paragraphs(small, _NOTICE_RUN_BREAK):
        if len(run) >= _NOTICE_MIN_ROWS:
            return run
    return []


def _read_masthead(ctx, pm, head: list, body_size: float) -> bool:
    """The slip's two-column masthead. Every row lands in a named part or
    the claim is withdrawn."""
    axis = pm.width * _AXIS_SPLIT
    notice = _notice_rows(head, pm.width, body_size)
    ctx.drop(notice, "notice")
    stamp = [r for r in head
             if r not in notice and r.x0 < axis]
    # THE STAMP'S CENTRE, measured: its rows are centred at 202-204 in the
    # left column, and the rows that stand at the caption rail
    # ('Appeal No.', 'STATE OF WISCONSIN') are not.
    for row in head:
        if row in notice:
            continue
        text = row.text
        if _CITE.match(text):
            ctx.once("citation", text)
            ctx.crit["publication_status"] = "published"
            ctx.row(row, "citation", "C")
        elif _COURT_SLIP.match(text):
            ctx.once("court", text)
            ctx.row(row, "court", "C")
        elif _TITLE_SLIP.match(text):
            ctx.once("title", text)
            ctx.row(row, "title", "C")
        elif _STAMP_DATE_LABEL.match(text):
            ctx.row(row, "date", "C")
        elif row.x0 < axis and find_date(text) and len(text) < 30:
            ctx.once("decision_date", find_date(text))
            ctx.row(row, "date", "C")
        elif _APPEAL_LABEL.match(text):
            found = _APPEAL_NO.findall(text)
            if not found:
                return False
            ctx.once("docket_number", found[0])
            if len(found) > 1:
                ctx.crit.setdefault("other_dockets", []).extend(found[1:])
            ctx.row(row, "docket", "C")
        elif _CIRCUIT_LABEL.match(text):
            found = _CIRCUIT_NO.findall(text)
            if found:
                ctx.crit.setdefault("lower_court_docket", []).extend(
                    n for n in found
                    if n not in ctx.crit.get("lower_court_docket", []))
            ctx.row(row, "docket", "C")
        elif (_BANNER_STATE.match(text) or _BANNER_COURT.match(text)
                or _BANNER_DISTRICT.match(text)):
            ctx.row(row, "court", "C")
        elif row.x0 < axis and row.size < body_size:
            # THE CLERK'S ATTESTATION — the two 8pt rows of the stamp, its
            # name and its office. Read by size and column, not by name.
            ctx.row(row, "case-info", "C")
        else:
            return False
    return bool(stamp)


def _read_caption(ctx, band: list) -> bool:
    """The caption band: names at the rail, statuses indented, the pivot
    half as far in."""
    rail = min(r.x0 for r in band)
    els = _elements(band)
    kinds: list[str] = []
    for el in els:
        at_rail = all(abs(r.x0 - rail) <= _RAIL_TOL for r in el)
        if at_rail:
            kinds.append("name")
        elif len(el) == 1 and el[0].text.rstrip(".").strip().upper() == "V":
            kinds.append("pivot")
        elif all(r.x0 - rail >= _INDENT_MIN for r in el):
            kinds.append("status")
        else:
            return False
    if "pivot" not in kinds:
        return False

    left: list[str] = []
    right: list[str] = []
    seen_pivot = False
    for i, (kind, el) in enumerate(zip(kinds, els)):
        nxt = kinds[i + 1] if i + 1 < len(kinds) else None
        if kind == "name" and nxt != "status":
            # A RAIL ELEMENT WITH NO STATUS UNDER IT is the matter title,
            # not a party (county_of_trempealeau).
            for row in el:
                ctx.row(row, "case-info")
            continue
        for row in el:
            ctx.row(row, "caption")
        if kind == "pivot":
            seen_pivot = True
        elif kind == "name":
            # THE TERMINAL COMMA IS THE COURT'S, THE PERIOD IS THE NAME'S.
            # Every party name in the corpus ends in a comma (its status
            # follows on the next row), so only ',;' is trimmed — stripping
            # a period as well cost 'FARMERS GROUP PROPERTY & CASUALTY INS.
            # CO.' its abbreviation, and 'AMERICAN FAMILY MUTUAL INSURANCE
            # COMPANY, S.I.' its initials.
            name = _norm(" ".join(r.text for r in el)).rstrip(",; ")
            (right if seen_pivot else left).append(name)
    ctx.crit.setdefault("caption", []).extend(r.text for r in band)
    sides = ["; ".join(left), "; ".join(right)]
    sides = [s for s in sides if s]
    if sides and not ctx.crit.get("parties"):
        ctx.crit["parties"] = sides
        ctx.crit["case_name"] = " v. ".join(sides)
    return True


def _read_tail(ctx, pm, model, finder, foot: float, body_size: float) -> bool:
    """Below the second fence: the origin, the panel, and the RULE
    809.23(3) notice where the record prints one."""
    paras = _paragraphs(_rows(pm, finder, lo=foot), _PARA_BREAK)
    if not paras or not _ROUTE.match(paras[0][0].text):
        return False
    _read_origin(ctx, paras[0])
    rest = paras[1:]
    # THE PANEL MAY BE OVERLEAF (lowell x2): page 1 ends with the origin and
    # a footnote, and 'Before …' opens page 2 under the running head.
    if not (rest and _PANEL_OPEN.match(rest[0][0].text)):
        nxt = next((p for p in model.pages if p.number == pm.number + 1), None)
        if nxt is None:
            return False
        rest = _paragraphs(_rows(nxt, finder), _PARA_BREAK)
        if not (rest and _PANEL_OPEN.match(rest[0][0].text)):
            return False
    panel = rest[0]
    for row in panel:
        ctx.row(row, "panel")
    line = _norm(" ".join(r.text for r in panel))
    ctx.crit["panel_line"] = line
    names = _panel_names(line)
    if names:
        ctx.crit["panel"] = names
        # `judges` AS WELL AS `panel`: core populated `judges` from this same
        # row before this reader existed, and it is the field the criteria
        # box surfaces (`panel` is one of the seven item-38 hides). Dropping
        # it would be a regression in machine-readable output for a row that
        # is read better than before.
        ctx.crit["judges"] = "; ".join(names)
    # THE RULE 809.23(3) NOTICE: 11pt where the body is 13pt, and BOLD —
    # which is what tells it from a footnote set at the same size.
    if len(rest) > 1:
        note = rest[1]
        if all(r.size < body_size and r.bold for r in note):
            for row in note:
                ctx.row(row, "publication")
            # …AND NOTHING IS WRITTEN TO `publication_status` FROM IT. The
            # row is a standing CITABILITY caution attached to the per
            # curiam FORM ('Per curiam opinions may not be cited …'), not a
            # statement about this paper: state_v._gustin_j._king prints it
            # in the headmatter AND 'Recommended for publication in the
            # official reports.' at the foot of its writing. Read as a
            # status it types a recommended-for-publication slip
            # `unpublished`, which is item 24's error in the other
            # direction.
    return True


def _read_origin(ctx, para: list) -> None:
    """How the case came here, the court and judge below, and what this
    court did — the disposition being the ITALIC run, on all 30 records."""
    for row in para:
        ctx.row(row, "lower-court")
    whole = _norm(" ".join(r.text for r in para))
    dispo = _norm(" ".join(r.italic_text for r in para))
    if dispo:
        dispo = dispo.rstrip(" .") + "."
        ctx.crit["disposition"] = dispo
        head = whole
        cut = whole.find(dispo.rstrip("."))
        if cut > 0:
            head = whole[:cut].strip()
        ctx.crit["history"] = _norm(head)
    else:
        ctx.crit["history"] = whole
    court = _COURT_BELOW.search(whole)
    if court:
        ctx.crit["lower_court"] = _norm(court.group(1))
    judge = _TRIAL_JUDGE.search(whole)
    if judge:
        ctx.crit["lower_court_judge"] = _norm(judge.group("name"))


# ---- the published cover -------------------------------------------------

def _read_cover(ctx, covers: list, finder, body_size: float) -> bool:
    """The reporter cover sheet: a label/value grid fenced by four rules,
    with the counsel block running to the end of the cover pages."""
    for pm in covers:
        fences = _fences(pm, _COVER_FENCE)
        if fences:
            if len(fences) != _COVER_FENCE_COUNT:
                return False
            bounds = [None] + [f.top for f in fences] + [None]
            for i in range(len(bounds) - 1):
                band = _rows(pm, finder, lo=bounds[i], hi=bounds[i + 1])
                if i:
                    ctx.rule(pm.number)
                if not _read_cover_band(ctx, band, i, body_size):
                    return False
        else:
            # a continuation page: the counsel block, and nothing else
            if not _read_cover_band(ctx, _rows(pm, finder), 4, body_size):
                return False
    return True


def _read_cover_band(ctx, band: list, index: int, body_size: float) -> bool:
    """Band 0 identity, 1 the caption, 2 the dates, 3 the panel, 4 counsel."""
    if index == 0:
        for row in band:
            text = row.text
            if _CITE.match(text):
                ctx.once("citation", text)
                ctx.crit["publication_status"] = "published"
                ctx.row(row, "citation", "C")
            elif _COURT_COVER.match(text):
                ctx.once("court", text)
                ctx.row(row, "court", "C")
            elif _COVER_TITLE.match(text):
                ctx.once("title", text)
                ctx.crit["publication_status"] = "published"
                ctx.row(row, "publication", "C")
            elif _CASE_LABEL.match(text):
                found = _APPEAL_NO.findall(text)
                if not found:
                    return False
                ctx.once("docket_number", found[0])
                if len(found) > 1:
                    ctx.crit.setdefault("other_dockets", []).extend(found[1:])
                ctx.row(row, "docket")
            else:
                return False
        return True
    if index == 1:
        caption = []
        for row in band:
            text = row.text
            if _COVER_REVIEW.search(text) or text.startswith("†"):
                ctx.row(row, "case-info", "C")
            elif text.startswith("Complete Title of Case"):
                ctx.row(row, "caption")
            else:
                caption.append(row)
        return _read_caption(ctx, caption) if caption else False
    if index == 2:
        for row in band:
            got = _COVER_DATE_LABEL.match(row.text)
            if not got:
                return False
            date = find_date(got.group(2))
            if got.group(1).startswith("Opinion Filed"):
                ctx.once("decision_date", date)
            elif date:
                ctx.once("submitted", date)
            ctx.row(row, "date")
        return True
    if index == 3:
        for row in band:
            got = _COVER_JUDGES.match(row.text)
            if got:
                ctx.crit.setdefault("panel_line", _norm(row.text))
                names = _panel_names(got.group(1))
                if names and not ctx.crit.get("panel"):
                    ctx.crit["panel"] = names
                    ctx.crit["judges"] = "; ".join(names)
            elif not row.text.startswith(("Concurred:", "Dissented:")):
                return False
            ctx.row(row, "panel")
        return True
    # band 4: the appearances, side by side with the side they act for
    for row in band:
        ctx.row(row, "counsel")
        if not _COVER_SIDE.match(row.text):
            ctx.counsel.append(row.text)
    return True
