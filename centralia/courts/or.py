"""Supreme Court of the State of Oregon ('or').

Everything unique to or lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

WHY THIS FILE IS IMPORTED THE LONG WAY. The court id is 'or', and `or` is a
Python keyword: `or.py` is a perfectly legal FILENAME but `from . import or`
is a syntax error. So the file keeps the name every other court file has —
`centralia/courts/<court>.py`, the convention the porting docs state — and
courts/__init__.py reaches it with `importlib.import_module` instead, in a
loop over ("del", "or"). Delaware ('del') has the same problem and the same
answer, and its docstring says so too. THERE IS NO `from . import or` LINE
TO ADD; adding one breaks the package.

THE CONTRACT — Oregon is not a slip opinion. All 50 records are pages of the
OREGON REPORTS ADVANCE SHEETS: a 396pt half-measure reporter page whose
every leaf is ruled under its running head, with a 301.5pt type block whose
rail alternates 45.0 / 49.5 with the binding margin. The reporter sets the
block in exactly two positions — CENTRED ON THE TYPE BLOCK'S OWN AXIS above,
a LADDER at the rail below — and the axis is where the reader's work is:

    ┌──────────────────────────────────────────────────────────────────┐
    │ 618          December 24, 2025            No. 54   the page head │
    ├────────────────── DRAWN RULE, top 49.1 ──────────────────────────┤
    │              IN THE SUPREME COURT OF THE           the masthead  │
    │                   STATE OF OREGON                                │
    │                                                                  │
    │                THOMAS GOLDEN ALLEN,                              │
    │                     Plaintiff,                     the caption,  │
    │                        v.                          centred on    │
    │                Charlotte THRASHER,                 the block's   │
    │                   Superintendent,                  own axis      │
    │                    Coffee Creek                                  │
    │                 Correctional Facility,                           │
    │                     Defendant.                                   │
    │                   (SC S072466)                     the dockets   │
    │                                                                  │
    │   En Banc                                          the bench     │
    │   Original proceeding in habeas corpus.            the origin    │
    │   Argued and submitted December 18, 2025.          the dates     │
    │   Thaddeus August Betz, Oregon Justice Resource Center,          │
    │ Portland, argued the cause and filed the petition, …  counsel    │
    │   Paul L. Smith, Deputy Solicitor General, Salem, argued …       │
    │   GARRETT, J.                                      the writing   │
    └──────────────────────────────────────────────────────────────────┘

THE DRAWN RULE IS THE PAGE'S OWN MEASURE. Every page of every record draws
exactly one rule at top 49.1, running the full type measure: x0 45.0 x1
346.5 on a verso and 49.5 / 351.0 on a recto, 301.5pt either way, measured
over 135 pages of the 50 records. So the rule gives the reader three facts
it never has to guess — the RAIL (its x0), the AXIS (x0 + 150.75) and the
foot of the PAGE HEAD (everything above it). Page width / 2 is the wrong
axis here and reads every caption row as an indent: the type block is offset
from the paper's centre by the binding margin, which changes side every leaf.

CENTRED IS A MEASURED FACT, AND IT DELIMITS THE CAPTION. A row's offset from
the axis is `(x0 + x1) / 2 - axis`, and over all 50 records every masthead,
caption and docket row lands within ±1.5pt of it while nothing else in the
block comes within 7pt. One catch, and it is the same one nh had: a JUSTIFIED
WRAP fills the measure exactly, so its mid-point is the axis too — a counsel
continuation is 'centred' by that test alone. Ink WIDTH separates them; the
widest centred row over the corpus is 284.0pt of the 301.5pt measure, and a
justified wrap is 301.5pt on the nose. So the caption band is the maximal run
of rows within ±4pt of the axis AND under 295pt wide, starting at the
masthead, and no row below that run is ever read as caption. Read this way
the run partitions all 50 records exactly: no ladder row leaks in, and
Progressive's 274.9pt party row — which stands at dx 13.3, two points off the
ladder's own 15pt indent — stays in the caption where it belongs.

THE LADDER IS READ RUNG BY RUNG, NOT IN ORDER. Below the caption every row
stands at the rail (a wrap) or 15.0pt in (an opener), and the rungs are
these, each by its own landmark, because their ORDER is not stable — 'En
Banc' prints above the origin, while 'Before Flynn, Chief Justice, …' prints
BELOW the counsel, immediately above the byline (measured: 38 records set
'En Banc' before the origin, 9 set a 'Before …' roster after the counsel,
and state_v._mcgee sets one where the other would be):

  panel        'En Banc' | 'Before <roster>, Justices.'
  lower-court  'On review from the Court of Appeals.' (23) | 'On review of
               the decision of a trial panel of the Disciplinary Board.' (5)
               | 'On appeal from an order of the … Circuit Court …' (1)
  case-info    'Original proceeding in habeas corpus.' (7) | 'Original
               proceeding in mandamus.' (4) — an original proceeding names
               NO court below, so tinting it `lower-court` would be a claim
               the paper does not make; it is the case's posture, which is
               what `case-info` is for.
  date         'Argued and submitted <date>.' (29) | 'Submitted on the
               record <date>.' (5) | any rung carrying 'considered and under
               advisement on' (8) — on those records the reporter prints the
               posture and BOTH dates as one sentence ('On petition for
               review filed August 12, 2025;* considered and under advisement
               on October 7, 2025.') and prints no separate date rung at all.
               A row carries one role; the dates are what that sentence is
               mostly made of, and its posture is still recovered into
               `criteria.history`.
  counsel      everything else in the ladder, including 'No appearance
               contra.' (4)

THE PAGE HEAD IS THE REPORTER'S, NOT THE COURT'S — and on page 1 it is not
the same head that repeats. Above the rule the advance sheet prints three
pieces on one row: the folio, the FILING DATE, and the advance sheet's own
serial ('No. 54'). Core already knows the folio; it cannot know the other
two, which are content by every test it has, so they render as the first two
untagged rows of the block. They are dropped here as the page head they are,
and the date is harvested into `criteria.decision_date` — it is the date the
opinion was filed (three records share 'December 24, 2025' and carry Nos.
54, 55 and 56).

THE CITE AND THE SHORT NAME COME OUT OF THE RUNNING HEAD, which is the only
place the advance sheet prints them: the recto heads read 'Cite as 374 Or 618
(2025)' and the versos read 'Allen v. Thrasher'. Both are furniture and
neither gets a row — a role would say the block prints something it does not
— but '374 Or 618' is Oregon's public-domain citation and it goes into
`criteria.citation`, the short form into `criteria.short_case_name`.

THE BYLINE ENDS THE READER, and on this paper the byline is printed TWICE.
The reporter sets the author over a one-paragraph statement of what the court
did ('GARRETT, J.' / 'It is hereby ordered that plaintiff immediately be
discharged …'), and the opinion proper then opens on the next page with the
same byline. The reader stops at the FIRST of them and claims nothing below
it, which is what leaves core the anchor it opens the writing on. Measured:
38 records sign on page 1 and 12 on page 2, so the walk is bounded at three
pages.

THE 8pt APPARATUS IS CORE'S. Below the last ladder rung the reporter types a
short underscore and sets the origin's detail in 8pt ('* On appeal from
Jackson County Circuit Court, Timothy Barnack, Judge. 328 Or App 452 …').
That is a footnote and it sits in core's footnote zone, which is subtracted
from the segment stream before this reader runs — so passing over it leaves
no hole in the claim, and claiming it would take a note off the headmatter.

THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
has no `docket` field and no `argued` field: the docket is `docket_number` (a
string) plus `other_dockets` (the rest), the numbers the courts BELOW gave
the case are `lower_court_docket`, and an argued date belongs in
`submitted`, which the render labels 'argued/submitted'. Written under the
wrong names they are attached to the object by setattr and never serialized
— read as read, reported as nothing.

KNOWN, REPORTED, NOT PATCHED HERE. On kulongoski__paden_v._rayfield the
byline 'PER CURIAM' stands on page 2 at 19% of the page height, and the same
words head every page after it, so core's running-head rule
(`resolve/furniture.py`, the `frac <= 0.22 and key in self.top_keys` test)
drops the one byline the document has and no writing can open on it. That
record had 0 opinions before this reader and still has 0 after; the claim is
withdrawn whole by core's own no-writing guard, which is the right outcome
for a reader and the wrong outcome for the record.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup

# ---------------------------------------------------------------------------
# The paper, measured over all 50 records of /assets/or.
# ---------------------------------------------------------------------------
# The page-head rule: exactly one per page, top 49.1, x0 45.0/49.5, always
# 301.5pt wide. Measured on 135 pages (pages 1-3 of every record).
_RULE_TOP = 49.1
_RULE_TOP_TOL = 2.5
_MEASURE = 301.5
_AXIS_FROM_RAIL = _MEASURE / 2          # 150.75
# A CENTRED ROW IS A SHORT ROW ON THE AXIS. Every masthead/caption/docket row
# is within 1.5pt of the axis; the nearest thing that is not is a counsel
# opener at 7.5pt. A justified wrap fills the measure exactly and so shares
# the axis — the widest genuinely centred row is 284.0pt
# (state_v._mcgee's '(CA A178091 (Control), A178092, A177818) (SC S072315)').
_AXIS_TOL = 4.0
_CENTRED_WIDTH_MAX = 295.0
# The ladder: an opener stands 15.0pt in from the rail, a wrap at the rail.
# Oregon's BODY indent is 42.0pt, so a row that far in has left the block.
_INDENT = 15.0
_LADDER_X_MAX = 22.0
# The paper is 11pt. The reporter's footnote apparatus is 8pt and its block
# quotations 10pt; nothing the block itself prints is under 11pt.
_BODY_SIZE_MIN = 10.5
# 38 records sign on page 1, 12 on page 2. Nothing needs a fourth page.
_MAX_PAGES = 3
# Two vertical steps in the block are a real blank band, not leading: 28.0pt
# under the masthead and 26.0pt under the last docket row (allen). Every
# other step is 11.9-18.0pt, which is the ladder's own 6pt element space.
_GAP_MIN = 22.0
# Pieces the page set on ONE row: only the page head does this (folio, date
# and serial, 82pt apart on allen). A justified line never leaves that much.
_SAME_ROW_SPLIT = 20.0

_MASTHEAD_1 = re.compile(r"^IN THE SUPREME COURT OF THE$", re.I)
_MASTHEAD_2 = re.compile(r"^STATE OF OREGON$", re.I)

# The page head's two content pieces. 'No. 54' is the advance sheet's serial
# number for this opinion, not a docket; the date is the filing date.
_HEAD_DATE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
_HEAD_SERIAL = re.compile(r"^No\.\s*\d{1,4}$")
_FOLIO = re.compile(r"^\d{1,4}$|^\d\s\d{2}$")   # '1 52' — a broken folio

# The running heads, which are the only place the advance sheet prints
# Oregon's public-domain citation and the case's short name.
_CITE_HEAD = re.compile(r"^Cite as\s+(\d+\s+Or\s+\d+)\s*\(\d{4}\)$", re.I)

# THE DOCKETS are one or more parenthesised groups and nothing else, centred
# under the caption: '(SC S072466)', '(CC 20CV10350) (CA A174313) (SC
# S070647)', '(SC S072772 (Control); S072776)', '(OSB 23111) (SC S071643)',
# and on two records split over two rows. 'SC' is this court, 'CC' the
# circuit court, 'CA' the Court of Appeals, 'OSB' the Oregon State Bar.
_DOCKET_ROW = re.compile(r"^\((?:[^()]|\([^()]*\))*\)"
                         r"(?:\s*\((?:[^()]|\([^()]*\))*\))*$")
_DOCKET_TOKEN = re.compile(r"\b(?:SC|CC|CA|OSB|TC|OTC)\b|^\(S\d{5,}")
_DOCKET_GROUP = re.compile(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)")
_DOCKET_COURT = re.compile(r"^(SC|CC|CA|OSB|TC|OTC)\b\s*(.*)$")

# The caption's own closed vocabularies: the pivot, the connector, the party
# STATUS labels, and the apparatus rows that open lower case ('a foreign
# corporation,', 'aka Michael Farnham, …', 'dba Eagle Fire,', 'et al,').
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_CONNECTOR = re.compile(r"^and$", re.I)
# The STATUS labels are a closed set, and this is all of them the 50 records
# print: 'Petitioner on Review,', 'Plaintiff-Adverse Party,', 'Plaintiffs
# -Respondents,' (the paper's own stray space), 'Defendant-Relator.',
# 'Third-Party Plaintiff,', 'Respondents on Review,' …
_PARTY_WORD = (r"Plaintiffs?|Defendants?|Petitioners?|Respondents?"
               r"|Appellants?|Appellees?|Relators?|Movants?|Intervenors?"
               r"|Claimants?")
_STATUS = re.compile(
    rf"^(?:(?:{_PARTY_WORD})|Third-Party\s+(?:{_PARTY_WORD}))"
    rf"(?:\s*-\s*(?:Adverse\s+Party|{_PARTY_WORD}))?"
    r"(?:\s+(?:on\s+Review|Below))?\s*[,.;]?$", re.I)

# The bench. 'En Banc' is the whole rung; a 'Before …' roster runs to
# 'Justices.' and carries titles this vocabulary knows how to drop.
_PANEL_EN_BANC = re.compile(r"^(?:En|In)\s+Banc\.?$", re.I)
_PANEL_BEFORE = re.compile(r"^Before\b", re.I)
_BENCH_WORD = re.compile(
    r"^(?:Chief\s+)?(?:Justices?|Judges?)$|^Senior\s+Judges?$"
    r"|^Justices?\s+pro\s+tempore$|^Judges?\s+pro\s+tempore$"
    r"|^pro\s+tempore$", re.I)

# THE ORIGIN — a tribunal below, named. Closed set, measured over the corpus.
_ORIGIN_BELOW = re.compile(
    r"^On\s+(?:review\s+from|review\s+of\s+the\s+decision|appeal\s+from"
    r"|certified\s+|automatic\s+and\s+direct\s+review|direct\s+review"
    r"|remand\s+from)", re.I)
# …and an ORIGINAL PROCEEDING, which names no court below at all.
_ORIGIN_HERE = re.compile(r"^Original\s+proceeding\b", re.I)
# THE DATED POSTURE. Eight records print no 'Argued and submitted' rung at
# all: instead the reporter states how the case got here and BOTH of its
# dates in one sentence, and 'filed' or 'considered and under advisement on'
# may fall on the second or third line of it — so the rung is recognized
# from its OPENER, which is every 'On …' rung the tribunal patterns above
# did not already take. Measured openers: 'On petition for review filed
# August 12, 2025;*', 'On petition for writ of mandamus filed January 16,
# 2026;', 'On petitions to review ballot title filed on January 30,', 'On
# respondent on review’s petition for reconsideration'. No counsel entry
# opens with 'On' — every one of them opens with a person's name.
_POSTURE_DATED = re.compile(r"^(?:On|Upon)\b", re.I)

# THE DATES. 'Argued and submitted …' / 'Submitted on the record …' are their
# own rungs; the eight records that print none of those state the posture and
# both dates in one sentence hinged on 'considered and under advisement on'.
_DATE_RUNG = re.compile(
    r"^(?:Argued\s+and\s+submitted|Reargued\s+and\s+resubmitted"
    r"|Submitted\s+on\s+the\s+record|Submitted\s+on\s+briefs"
    r"|Argued|Reargued|Submitted)\b", re.I)
_ADVISEMENT = re.compile(r"considered\s+and\s+under\s+advisement\s+on\s+"
                         r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", re.I)
_DATE_VALUE = re.compile(r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})")
_MOTION = re.compile(
    r"\b(petition\s+for\s+reconsideration|petition\s+for\s+rehearing"
    r"|petition\s+for\s+review|petitions?\s+to\s+review\s+ballot\s+title"
    r"|petition\s+for\s+(?:an\s+)?alternative\s+writ\s+of\s+mandamus"
    r"|petition\s+for\s+writ\s+of\s+mandamus)\b", re.I)

# THE BYLINE. Measured forms: 'GARRETT, J.' (11), 'PER CURIAM' (14),
# 'BUSHONG, J.' (7), 'FLYNN, C.J.' (6), 'JAMES, J.' (5), 'MASIH, J.' (3),
# 'DeHOOG, J.' (3), 'DUNCAN, J.' (1). Nothing else in the block takes that
# shape, and every one of the 50 records prints one.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z’'\-]*(?:,\s*[A-Z][A-Za-z’'\-]*)*,\s*"
    r"(?:C\.\s*J\.|JJ?\.)|PER\s+CURIAM)\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _page_frame(pm) -> tuple[float, float, float]:
    """(rail, axis, head_foot) from the page's own drawn rule."""
    for rule in pm.h_rules:
        if abs(rule.top - _RULE_TOP) <= _RULE_TOP_TOL \
                and abs((rule.x1 - rule.x0) - _MEASURE) <= 6.0:
            return rule.x0, rule.x0 + _AXIS_FROM_RAIL, rule.top
    # No rule drawn: fall back to the leftmost ink on the page, which is the
    # rail on every record measured. The reader still refuses the record if
    # the masthead is not where the frame says it should be.
    xs = [l.x0 for l in pm.lines if l.plain.strip()]
    rail = min(xs) if xs else 45.0
    return rail, rail + _AXIS_FROM_RAIL, _RULE_TOP


@decider("headmatter.read", court="or")
def read_headmatter_or(model, geom, **_):
    """Read Oregon's advance-sheet block, or NOTHING."""
    if not model.pages:
        return NOTHING

    pages = model.pages[:_MAX_PAGES]
    rows: list[tuple] = []          # (page, rail, axis, [lines])
    for pm in pages:
        rail, axis, head_foot = _page_frame(pm)
        for group in _rows(pm):
            rows.append((pm, rail, axis, head_foot, group))
    if len(rows) < 8:
        return NOTHING

    # THE DISPATCH: the two-row masthead, below page 1's rule. Never an
    # ordinal — the page head is three pieces on one row and pdfio orders
    # them by x0, so the masthead's index moves with the binding margin.
    mast = None
    for idx, (pm, rail, axis, head_foot, group) in enumerate(rows[:8]):
        if pm.number != 1 or group[0].top <= head_foot:
            continue
        if _MASTHEAD_1.match(_norm(" ".join(l.plain for l in group))):
            mast = idx
            break
    if mast is None:
        return NOTHING

    ctx = _Ctx()
    # THE RUNNING HEADS, read across EVERY page and never claimed: they are
    # the only place the advance sheet prints Oregon's public-domain cite and
    # the case's short name, and they are furniture wherever they stand. The
    # pre-pass is separate from the walk because the walk stops at the byline
    # — 38 records sign on page 1, so their cite (which the reporter sets on
    # the rectos from page 2 on) is below where the walk ever reaches.
    # A VERSO HEAD IS THREE PIECES — the folio at the rail, the AUTHOR in the
    # middle and the short case name flush right ('620' / 'GARRETT, J.' /
    # 'Allen v. Thrasher'); a recto head is two — the cite at the rail and the
    # folio flush right. So the short name is the piece at the RIGHT MARGIN
    # that is not a folio, and taking the first non-folio piece instead read
    # the author's name as the case's on 21 records.
    for pm in model.pages:
        rail, _, head_foot = _page_frame(pm)
        right = rail + _MEASURE
        for line in pm.lines:
            if line.top > head_foot:
                continue
            head = _norm(line.plain)
            if not head:
                continue
            cite = _CITE_HEAD.match(head)
            if cite:
                ctx.crit.setdefault("citation", _norm(cite.group(1)))
            elif (pm.number > 1 and abs(line.x1 - right) <= 4.0
                    and not _FOLIO.match(head)):
                ctx.crit.setdefault("short_case_name", head)

    caption_rows: list[str] = []     # the printed caption, verbatim
    party_rows: list[str] = []       # one entry per party GROUP
    party_heads: list[str] = []      # each group's FIRST row — the name
    party_buf: list[str] = []        # the group being read
    pivot_at: int | None = None      # index into party_rows
    dockets: list[str] = []          # this court's numbers, in printed order
    lower_dockets: list[str] = []    # the numbers the courts below gave it
    rungs: list[list] = []           # [role, whole printed text] per rung
    band = "head"                    # head | caption | ladder
    prev_top: float | None = None
    prev_page: int | None = None

    def _flush_party() -> None:
        """A PARTY GROUP IS THE ROWS DOWN TO ITS STATUS LABEL. Oregon sets
        the party's name, then its office and institution beneath it, then
        the label ('Charlotte THRASHER,' / 'Superintendent,' / 'Coffee
        Creek' / 'Correctional Facility,' / 'Defendant.') — one party, five
        rows. The label, the pivot and the connector each close the group."""
        if party_buf:
            party_rows.append(_norm(" ".join(party_buf)))
            party_heads.append(party_buf[0])
            party_buf.clear()

    for idx, (pm, rail, axis, head_foot, group) in enumerate(rows):
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        x1 = max(l.x1 for l in pieces)
        width = x1 - first.x0
        dx = first.x0 - rail
        centred = (abs((first.x0 + x1) / 2 - axis) <= _AXIS_TOL
                   and width <= _CENTRED_WIDTH_MAX)

        # THE PAGE HEAD, by the rule the page draws under it. On page 1 it is
        # the advance sheet's own dateline and serial, which core cannot know
        # and leaves as the first two rows of the block; on later pages it is
        # the running head, which core already drops (and which the pre-pass
        # above has read for the cite and the short name).
        if first.top <= head_foot:
            if pm.number == 1:
                if _HEAD_DATE.match(text):
                    ctx.crit.setdefault("decision_date", text)
                ctx.drop(pieces, "running-head")
            continue

        # THE 8pt APPARATUS is core's footnote zone; passing over it leaves
        # no hole, because the zone is subtracted before this reader runs.
        if first.size and first.size < _BODY_SIZE_MIN:
            continue

        # THE BYLINE ENDS THE READER, wherever it stands (dx 15.0 on 49
        # records, 0.0 on state_v._ayon-urbano). It is never on the axis, so
        # a caption row shaped like one cannot end the reader early.
        if idx > mast and not centred and _BYLINE.match(text):
            break
        # A ROW AT THE BODY INDENT has left the block.
        if not centred and dx > _LADDER_X_MAX:
            break

        # The paper's own blank bands, kept as rhythm.
        if prev_top is not None and prev_page == pm.number \
                and first.top - prev_top >= _GAP_MIN:
            ctx.gap()
        prev_top, prev_page = first.top, pm.number

        if band == "head":
            if idx == mast or (idx == mast + 1 and _MASTHEAD_2.match(text)):
                ctx.crit["court"] = _norm(
                    (ctx.crit.get("court", "") + " " + text))
                ctx.emit(pieces, "court", centre=True)
                if idx > mast:
                    band = "caption"
                continue
            band = "caption"

        # ---- the caption band: the run of rows on the block's axis --------
        if band == "caption":
            if centred:
                if _DOCKET_ROW.match(text) and _DOCKET_TOKEN.search(text):
                    _read_dockets(text, dockets, lower_dockets)
                    ctx.emit(pieces, "docket", centre=True)
                    continue
                caption_rows.append(text)
                if _PIVOT.match(text):
                    _flush_party()
                    if pivot_at is None:
                        pivot_at = len(party_rows)
                elif _STATUS.match(text) or _CONNECTOR.match(text):
                    _flush_party()
                else:
                    party_buf.append(text)
                    # A row that ends its own SENTENCE closes the group:
                    # 'In the Matter of T. A. G., II,' / 'a Child.' is the
                    # child's case, and the agency named beneath it is a
                    # different party.
                    if text.endswith("."):
                        _flush_party()
                ctx.emit(pieces, "caption", centre=True)
                continue
            _flush_party()
            band = "ladder"

        # ---- the ladder: rung by rung, each by its own landmark ----------
        # A rung OPENS on the 15pt indent and CONTINUES at the rail. Its role
        # is decided from the opener alone and never revised, because a wrap
        # says nothing about what its rung is: 'and under advisement on
        # October 7, 2025.' and 'the cause and filed the response …' are the
        # same shape. The rung's whole text is kept and parsed once it closes.
        if dx >= _INDENT - 5.0 or not rungs:
            role = "counsel"
            if _PANEL_EN_BANC.match(text) or _PANEL_BEFORE.match(text):
                role = "panel"
            elif _ORIGIN_BELOW.match(text):
                role = "lower-court"
            elif _ORIGIN_HERE.match(text):
                role = "case-info"
            elif _DATE_RUNG.match(text) or _POSTURE_DATED.match(text):
                role = "date"
            rungs.append([role, text])
        else:
            rungs[-1][1] = _norm(rungs[-1][1] + " " + text)
        ctx.emit(pieces, rungs[-1][0], centre=False, rel=dx)

    # A CLAIM THAT NEVER LEFT THE MASTHEAD IS NOT A READING.
    _flush_party()
    if band != "ladder" or not ctx.items:
        return NOTHING

    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if dockets[1:]:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if lower_dockets:
        ctx.crit.setdefault("lower_court_docket", lower_dockets)
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows)
    if party_rows:
        ctx.crit.setdefault("parties", party_rows)
        name = _case_name(party_heads, pivot_at)
        if name:
            ctx.crit.setdefault("case_name", name)

    # ---- the rungs, parsed once each is whole ----------------------------
    counsel = [t for role, t in rungs if role == "counsel"]
    below = [t for role, t in rungs if role in ("lower-court", "case-info")]
    for role, text in rungs:
        if role == "panel":
            ctx.crit.setdefault("panel_line", text)
            # 'En Banc' is not a roster: it says the whole court sat, and
            # naming it as a judge would be a name nobody printed.
            names = [] if _PANEL_EN_BANC.match(text) else _panel_names(text)
            if names:
                ctx.crit.setdefault("panel", names)
        elif role == "date":
            _read_dates(text, ctx.crit)
            # A dated rung that also states the posture ('On petition for
            # review filed …') says where the case came from; the origin is
            # recovered even though the row's one role went to the dates.
            if _POSTURE_DATED.match(text):
                below.append(text)
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
        _lower = [t for t in below if _ORIGIN_BELOW.match(t)]
        if _lower:
            ctx.crit.setdefault("lower_court", _lower[0])
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    ctx.crit.setdefault("headmatter_style", "advance-sheet")
    return ctx.result()


# ---------------------------------------------------------------------------
# the parsed forms, kept beside the printed ones
# ---------------------------------------------------------------------------

def _read_dockets(text: str, mine: list[str], lower: list[str]) -> None:
    """'(CC 20CV10350) (CA A174313) (SC S070647)' — this court's number, the
    companion appeals consolidated into it, and the numbers the courts BELOW
    gave the case. Called once per docket row: two records print the row
    twice, and the accumulators run across both."""
    for group in _DOCKET_GROUP.findall(text):
        group = _norm(group)
        if not group:
            continue
        court = _DOCKET_COURT.match(group)
        which = court.group(1).upper() if court else "SC"
        # '(S072641)' — a bare Supreme Court number, printed under the second
        # caption of a consolidated ballot-title case.
        rest = _norm(court.group(2)) if court else group
        if which != "SC":
            lower.append(_norm(f"{which} {rest}") if rest else which)
            continue
        # 'SC S072772 (Control); S072776' — the control number and its
        # companion. '(Control)' is the reporter saying which one leads.
        for piece in re.split(r"[;,]", rest):
            piece = _norm(piece.replace("(Control)", ""))
            if piece:
                mine.append(piece)


def _read_dates(text: str, crit: dict) -> None:
    """The date the case was SUBMITTED, from a whole rung.

    'Argued and submitted December 18, 2025.' states one date. 'On petition
    for review filed August 12, 2025;* considered and under advisement on
    October 7, 2025.' states two, and the second is the submission — so the
    advisement clause wins wherever the rung carries it."""
    advised = _ADVISEMENT.search(text)
    if advised:
        crit["submitted"] = _norm(advised.group(1))
    else:
        found = _DATE_VALUE.search(text)
        if found:
            crit.setdefault("submitted", _norm(found.group(1)))
    motion = _MOTION.search(text)
    if motion:
        crit.setdefault("motion", _norm(motion.group(1)))


def _case_name(parties: list[str], pivot_at: int | None) -> str | None:
    """'X v. Y', from the party either side of the pivot — never from the
    caption rows joined wholesale."""
    if pivot_at is None or pivot_at <= 0 or pivot_at >= len(parties):
        return None
    left = parties[0].rstrip(",;. ")
    right = parties[pivot_at].rstrip(",;. ")
    if not left or not right:
        return None
    return f"{left} v. {right}"


def _panel_names(line: str) -> list[str]:
    """The roster's names, with the bench titles dropped.

    'Before Flynn, Chief Justice, and Duncan, Garrett, DeHoog, James, and
    Masih, Justices, and Egan, Judge, Justice pro tempore.**' — the titles
    are a closed vocabulary and the names are what is left."""
    body = re.sub(r"^Before\s+", "", line, flags=re.I)
    body = re.sub(r"[*†‡]+\s*$", "", body.strip()).rstrip(".")
    out: list[str] = []
    for piece in re.split(r",|\band\b", body):
        piece = _norm(piece).rstrip(".").strip()
        if not piece or _BENCH_WORD.match(piece):
            continue
        if re.match(r"^(?:Chief|Senior|pro|tempore)$", piece, re.I):
            continue
        out.append(piece)
    return out


# ---------------------------------------------------------------------------
# rows, and the emit buffer
# ---------------------------------------------------------------------------

def _rows(pm) -> list[list]:
    """One group per printed row, EXCEPT where the page set two things far
    apart on one row — which on this paper only the page head does."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    out: list[list] = []
    for key in order:
        row = sorted(groups[key], key=lambda l: l.x0)
        chunk = [row[0]]
        for piece in row[1:]:
            if piece.x0 - chunk[-1].x1 > _SAME_ROW_SPLIT:
                out.append(chunk)
                chunk = [piece]
            else:
                chunk.append(piece)
        out.append(chunk)
    return out


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True,
             rel: float = 0.0) -> None:
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
            bold=all(bool(p.all_bold) for p in parts),
            rel=0.0 if centre else round(rel, 1), role=role))
        self.consumed.update(p.id for p in parts)

    def gap(self, lines: int = 1) -> None:
        self.items.append(m.Gap(lines=lines))

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
