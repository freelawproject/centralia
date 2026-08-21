"""United States Air Force Court of Criminal Appeals ('afcca').

The second of the service-CCA family in this engine (nmcca was the first,
and its file is the reference for the family's reading). afcca reviews
courts-martial under Article 66, UCMJ; every one of the 32 corpus records
is `United States v. <airman>` except one writ petition (`In re Chantay P.
WHITE`), every panel is a panel of `Appellate Military Judges`, and the
court below is the `United States Air Force Trial Judiciary`.

**afcca PRINTS TWO PAPERS AND THEY SHARE NOTHING BUT THE MASTHEAD.** The
corpus splits 15 / 17 and the split is COMPLEMENTARY AND TOTAL — measured
over all 32 page ones, no record draws both and none draws neither:

    style              records   ')' column on p1   typed axis fences on p1
    fenced stack          15            0                   4, 5 or 6
    parenthetical box     17          8, 9 or 10                  0

That is the dispatch. Not the title, not the wording, not the page count:
the ORDER paper stacks a `)` rail down the middle of its caption and types
no rule anywhere, and the OPINION paper types underscore rules on the page
axis and sets no rail. The old engine's shared military base folds a `)`
rail into EVERY CCA headmatter (`_military.py`:
`_fold_rail_caption(d["summary"], ")")`) — measured on nmcca that fold
finds nothing at all, and measured here it finds the right thing on 17
records and nothing on the other 15. The fold is afcca/acca ORDER paper.
It is inherited here as a CONTRACT WITH A LANDMARK, never as a blind fold.

    ┌── STYLE A: the fenced centred stack (15 records) ─────────────────┐
    │              UNITED STATES AIR FORCE          the masthead, 14pt  │
    │             COURT OF CRIMINAL APPEALS         bold, over 11pt body│
    │             ________________________          FENCE 1             │
    │                  No. ACM 40809                the DOCKET          │
    │             ________________________          FENCE 2             │
    │                  UNITED STATES                (bold: party)       │
    │                    Appellee                   (ital: status)      │
    │                       v.                      the pivot           │
    │                 Joshua D. ALLEN               (bold: party)       │
    │   Airman First Class (E-3), U.S. Air Force, Appellant             │
    │                                               (roman: rate)       │
    │             ________________________          FENCE 3             │
    │  Appeal from the United States Air Force Trial Judiciary          │
    │               Decided 25 June 2026            the date            │
    │             ________________________          FENCE 4             │
    │  Military Judge: Tiny L. Bowman (scheduling order); …             │
    │  Sentence: Sentence adjudged 11 December 2024 by GCM convened …   │
    │  For Appellant: Captain Joyclin N. Webster, USAF; …               │
    │  For Appellee: Major Heather R. Bezold, USAF; …                   │
    │  Before DOUGLAS, MCCALL, and KUBLER, Appellate Military Judges.   │
    │  Senior Judge DOUGLAS delivered the opinion of the court, in …    │
    │             ________________________          FENCE 5             │
    │      This is an unpublished opinion and, as such, does not        │
    │      serve as precedent under AFCCA Rule of Practice and          │
    │      Procedure 30.4.                          the publication stmt│
    │             ________________________          FENCE 6             │
    │  DOUGLAS, Senior Judge:                       (the paper begins)  │
    └───────────────────────────────────────────────────────────────────┘

    ┌── STYLE B: the parenthetical box (17 records) ────────────────────┐
    │              UNITED STATES AIR FORCE          the masthead        │
    │             COURT OF CRIMINAL APPEALS                             │
    │   UNITED STATES        )        No. ACM 40816   the DOCKET        │
    │           Appellee     )                                          │
    │                        )                                          │
    │           v.           )                                          │
    │                        )        ORDER          what the paper is  │
    │   Bradley M. BYINGTON  )                                          │
    │   Major (O-4)          )                                          │
    │   U.S. Air Force       )                                          │
    │           Appellant    )        Panel 1        who sat            │
    │                                                                   │
    │  On 9 June 2026, Appellant submitted …        (the paper begins)  │
    └───────────────────────────────────────────────────────────────────┘

STYLE A — WHAT THE FENCE IS AND WHY IT IS THE PARSER. The court types its
rules as a run of underscores set as text, never a vector, dead on the page
axis. Measured over every underscore row on all 32 page ones (83 rows):
72 are 132.0pt wide, 9 are 144.0 and 2 are 143.5, and ALL 83 have their
midpoint within 2.5pt of 306.0 on a 612pt page. So the AXIS is the test and
the measure is payload — ca5's rule holding in the easy direction. The
fence count varies (6 on ten records, 5 on three, 4 on two, with the
remainder of the ladder spilling onto page 2), so the dispatch is never an
ordinal: it is the first fence PAIR on page 1 with a DOCKET row between
them, under a masthead. All three hold on all 15; a record missing any of
them is not this contract and the reader returns NOTHING.

The zones then fall out of the fences without a single wording test: the
docket between fences 1 and 2, the caption stack between 2 and 3, and
everything below fence 3 read as a labelled ladder whose runs are each
bounded by their own rail, exactly as nmcca's are.

WEIGHT AND SLOPE READ THE CAPTION, on all 15 without exception: **bold** is
a party (`UNITED STATES`, `Joshua D. ALLEN`) and the pivot and the docket;
*italic* is the party STATUS (`Appellee`, and the `Appellant` that closes
the rate row); roman is the appellant's RATE AND SERVICE (`Airman First
Class (E-3), U.S. Air Force,`). So `parties` is built from the bold rows
either side of the pivot and no party name is read by wording.

STYLE B — THE RAIL IS THE PARSER, ca6's rule applied to a different glyph.
The `)` column stands at x0 = 324-326 on all 17 records (a stack of 8, 9 or
10 glyphs; the fenced records' largest `)` column is TWO, so the floor of 6
has four glyphs of headroom on both sides). Left of it are the parties;
right of it, at x0 = 360 invariantly, are the docket, what the paper calls
itself (`ORDER`, on all 17) and which panel sat (`Panel 1`, `Panel 2`,
`Special Panel`). Column membership is decided by which side of the drawn
column a glyph sits on, never by what the row says.

THE ORDER CAPTION IS ALL BOLD, SO POSITION READS IT, NOT WEIGHT. Every
left-column row on the order paper is 12pt bold — party, rank, service and
status alike — so the weight test that reads style A is useless here. What
the page does distinguish is the RAIL OF THE COLUMN ITSELF: the party's
name, rank and service stand at the column's own rail (x0 = 108) and the
STATUS labels are indented from it (`Appellee`, `v.`, `Appellant` at
x0 = 189.1 on all 15 v.-captioned orders). So the pivot is the indented row
that reads `v.`, and each party is the FIRST row at the column rail on its
side of the pivot — the same convention style A prints, where the name row
comes first and the rate follows it. in_re_white has no pivot at all (`In
re Chantay P. WHITE`, a writ petition) and yields a single party, which is
what the page states.

THE MASTHEAD IS THE COURT NAMING ITSELF and it is read by TYPE, not by its
words: exactly two rows above everything else on page 1, set at 14.0pt
against an 11.0pt body and bold, on all 32 records (64 rows, no exceptions
and nothing else on the page at that size). They take the `court` role and
`criteria.court` is the two joined. nmcca could not do this because nmcca
prints no masthead at all — only a seal, which is 30 bare curves and yields
no text.

THE DOCKET IS THE DOCKET AND THERE IS NO CITATION. `No. ACM 40809`,
`No. ACM S32814` (a special court-martial), `No. ACM 24057 (rem)` (on
remand), `No. ACM 40682 (f rev)` (further review), and the writ docket
`Misc. Dkt. No. 2026-04`. The parenthesized posture suffix is kept in
`other_dockets` so the printed form is not lost. This court assigns no
public-domain citation and `criteria.citation` stays None on all 32 — the
same trap nmcca records, an `ACM`-prefixed number that looks like a neutral
cite and is a docket.

TWO ROWS CARRY A FOOTNOTE MARKER GLUED TO THEIR TAIL. `Appeal from the
United States Air Force Trial Judiciary1` and `Decided 18 June 20262` —
the origin and the date, on the five records that hang a note off them.
The printed row keeps its marker (that is what the page says); the
criteria value drops the trailing digits, because no origin and no date
ends in one.

WHERE EACH BLOCK ENDS. Style A ends at the first byline — `PER CURIAM:`,
`DOUGLAS, Senior Judge:`, `RAMÍREZ, Judge:` — at the body rail, present on
all 15. Style B has no byline at all: the order closes `FOR THE COURT` over
the Chief Commissioner or the Clerk, who is not the author, so the block
ends where the rail's own column ends and the body opens on the first
paragraph below it.

TWO THINGS INSIDE THE SPAN ARE NOT THE BLOCK. The RUNNING HEAD on a
continuation sheet (`United States v. Cunningham, No. ACM 40746`) — style
A's ladder reaches page 2 on 5 of the 15 records, and the head is set at
BODY size, so core's recurrence test cannot always see it; where core has
not tagged it this reader takes it by the measured band and records it
`Dropped`. And the FOOTNOTE ZONE: the court draws its separator as a RECT
144.0pt wide at the page's left text rail, invariant on all 58 occurrences
in the corpus, and rows at or below it belong to the note, which core's
`FootnoteZones` has already routed.
"""

from __future__ import annotations

import re

from .. import model as m
from ..courts import register
from ..profile import CourtProfile
from ..resolve.bylines import DEFAULT_ABBREV, BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

STYLE_FENCED = "afcca fenced centred stack"
STYLE_BOX = "afcca parenthetical box"

# ---- afcca's declared facts (measured over all 32 records) ---------------
# THE FENCE. A typed run of underscores centred on the page axis. All 83 on
# the corpus's page ones: 132.0pt (72), 144.0 (9), 143.5 (2), every midpoint
# within 2.5pt of 306.0. The axis is the test; the measure is payload.
_FENCE_TEXT = re.compile(r"^_{6,}$")
_AXIS_TOL = 5.0
# CENTRED ON THE AXIS, for a text row: the caption, the origin, the date and
# the publication statement all sit within 4pt of the axis, and the nearest
# thing that is not centred is the ladder at the body rail, 198pt away.
_CENTRED_TOL = 8.0
# THE MASTHEAD: two rows at 14.0pt over an 11.0pt body, bold, above
# everything. Declared as a MARGIN over the body size, not as 14.
_MASTHEAD_OVER = 2.0
# THE RAIL of style B: a ')' column. 8-10 glyphs on the 17 order records,
# never more than 2 on the 15 opinion records.
_RAIL_GLYPH = ")"
_RAIL_FLOOR = 6
_RAIL_WINDOW = 4.0
# THE COLUMN IS A CONTIGUOUS RUN, and the run is what ends it. The box sets
# one rail glyph per printed row — 15.0pt on 16 records, 16.8 on monroe, with
# a single row (byington's rank line) whose glyph the court simply left out,
# for a 30.0pt step. Below the box a `)` that closes ordinary text can land in
# the same column by accident (in_re_white's '(UCMJ)' on the body's sixth
# line, 111.8pt under the caption's last rail row), and left in the stack it
# stretched the box's band over six paragraphs of the order. So the column
# ends at the first vertical step of more than three of its own rows: 45.0 is
# 15pt clear of the widest real step and 66pt clear of the nearest stray.
_RAIL_GAP = 45.0
# THE RIGHT COLUMN of the parenthetical box stands at x0 = 360.1 on all 17.
# Not used to split (the rail does that) — declared because the box's own
# geometry is the record of what was read.
#
# THE DOCKET: 'No. ACM 40809', 'No. ACM S32814', 'No. ACM 24057 (rem)',
# 'No. ACM 40682 (f rev)', 'Misc. Dkt. No. 2026-04'. Never a citation.
_DOCKET = re.compile(
    r"^(?:Misc\.\s*Dkt\.\s*)?Nos?\.\s*(?:ACM\s+)?"
    r"([A-Z]?[\d][\w\-]*)\s*(\([^)]*\))?\.?$")
# THE DATE. 'Decided 25 June 2026', 'Decided 18 June 20262' (a footnote
# marker glued to the year — the capture stops at the four-digit year).
_DATE = re.compile(r"^Decided:?\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})")
# WHERE THE APPEAL CAME FROM. 'Appeal from the United States Air Force Trial
# Judiciary' (12) and 'On Remand from the United States Court of Appeals for
# the Armed Forces' (3, two of which wrap after 'On Remand from'). The other
# openings are admitted because Article 66 review also reaches this court on
# the Judge Advocate General's certificate and on writ-appeal.
_ORIGIN = re.compile(
    r"^(?:Appeal from|Appeals from|On Remand from|Review of"
    r"|Certificate for Review|On (?:further )?review"
    r"|Writ[- ]Appeal Petition)\b")
# WHO TRIED IT, and WHAT THE COURT-MARTIAL DID. Both are labels the court
# sets in italic at the body rail with the value running on after the colon.
_MILJUDGE = re.compile(r"^Military Judges?:")
_SENTENCE = re.compile(r"^(?:Sentence|Findings|Findings and [Ss]entence):")
# THE APPEARANCE LABEL. 'For Appellant:' / 'For Appellee:' and the two
# law-school amicus rosters reese prints ('Amicus Curiae for Appellant:').
_FOR = re.compile(r"^(?:Amicus Curiae for|For)\s+[A-Z][A-Za-z .\-]*:")
# THE ROSTER. 'Before DOUGLAS, MCCALL, and KUBLER, Appellate Military
# Judges.' — the bench designation is set italic and may wrap to its own row.
_BEFORE = re.compile(r"^Before\s+[A-Z]")
_BENCH = re.compile(r"Appellate Military\s*$|^Judges\.$|"
                    r"Appellate Military Judges\.?$")
# THE ATTRIBUTION RECITAL: the panel saying who wrote, above the byline that
# signs. 11 of the 15; the other four are per curiam and print none.
_ATTRIB = re.compile(r"\bdelivered the opinion of the court\b")
# THE PUBLICATION STATEMENT, set bold and centred between fences 5 and 6.
# One wording on all 15, over two rows.
_PUBSTMT = re.compile(r"^This is an? (?:un)?published opinion\b")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# THE PARTY STATUS, a closed role vocabulary — used only to tell a status
# row from a party row where the page's own geometry cannot (in_re_white
# sets 'Petitioner' on the same printed row as the rank).
_STATUS = re.compile(
    r"^(?:Appellee|Appellant|Petitioner|Respondent|Cross-Appell(?:ee|ant)"
    r"|Plaintiff|Defendant|Amicus Curiae)[,.]?$", re.I)
# The footnote separator this court draws: a RECT two inches wide at the
# page's left text rail. Invariant on all 58 occurrences in the corpus.
_SEP_WIDTH = (138.0, 152.0)
# THE RUNNING-HEAD BAND on a continuation sheet. Measured over EVERY
# continuation sheet in the corpus (144 sheets, every row above 90pt): the
# head prints at 38-40 (140 rows) with one variant at 51 (4 rows), and the
# first body row never rises above 74. Nothing at all lands between. So 0.08
# of a 792pt page (63.4) sits in the middle of that gap, 12pt clear of the
# highest head and 11pt clear of the lowest body row.
_HEAD_BAND = 0.08
# The ladder never runs past page 2; the byline stop bounds it anyway.
_MAX_PAGES = 3


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---- the profile ---------------------------------------------------------
# BYLINE FORMS, all 15 in the corpus:
#   'PER CURIAM:'              4 records
#   'DOUGLAS, Senior Judge:'   the prose form, spelled title
#   'RAMÍREZ, Judge:'          an ACCENTED surname (mabida, penninga)
#   'GRUEN, Senior Judge:' / 'KEARLEY, Judge:' / 'MCCALL, Judge:' /
#   'KUBLER, Judge:' / 'MORGAN, Judge:'
# The 17 orders sign 'FOR THE COURT' over the Chief Commissioner or the
# Clerk of the Court, who is apparatus and never an author.
register(CourtProfile(
    "afcca",
    "United States Air Force Court of Criminal Appeals",
    byline=BylineGrammar(
        style="prose",
        titles=("Judge", "Chief Judge", "Senior Judge",
                "Appellate Military Judge"),
        also_abbrev=True,
        abbrev_titles=(("J.", "Judge"), *DEFAULT_ABBREV)),
    # The body opens its paragraphs 18pt in from the 108pt measure rail
    # (108 -> 126 on every record) and sets its block quotations at 144.
    # Twice this value must fall between the two, so 14.0.
    para_indent_min=14.0,
    rollout="migrated",
))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="afcca")
def read_headmatter_afcca(model, geom, **_):
    """Read an Air Force CCA cover — the fenced stack or the parenthetical
    box — or NOTHING.

    NOTHING is returned for anything that is neither contract: core's shared
    walk places those rows unidentified, which is a smaller error than a
    confident misreading."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 108.0)
    page1 = model.pages[0]
    axis = page1.width / 2

    # THE DISPATCH, decided on page 1 by geometry alone and nothing else.
    rail = _rail(page1)
    fences1 = _fences(page1, axis)
    if rail is not None and not fences1:
        return _read_box(model, geom, body_size, body_x0, rail)
    if fences1 and rail is None:
        return _read_fenced(model, geom, body_size, body_x0)
    # A page that draws both, or neither, is not one of these contracts.
    return NOTHING


def _fences(pm, axis: float) -> list:
    """The typed axis fences on ``pm``, in page order."""
    return [l for l in sorted(pm.lines, key=lambda l: l.top)
            if _FENCE_TEXT.match(l.plain.replace(" ", ""))
            and abs((l.x0 + l.x1) / 2 - axis) <= _AXIS_TOL]


def _rail(pm) -> dict | None:
    """The parenthetical box's ')' column, or None.

    Read exactly as ca6 reads its rail: the most common x0 among the page's
    ')' glyphs, kept only when enough of them stack there. A ')' that closes
    real text is not in the column and cannot reach the floor."""
    from collections import Counter

    paren = [c for l in pm.lines for c in l.chars
             if (c.get("text") or "") == _RAIL_GLYPH]
    if len(paren) < _RAIL_FLOOR:
        return None
    x, _n = Counter(round(c["x0"]) for c in paren).most_common(1)[0]
    stack = [c for c in paren if abs(c["x0"] - x) < _RAIL_WINDOW]
    tops = sorted({round(c["top"], 1) for c in stack})
    if not tops:
        return None
    runs: list[list[float]] = [[tops[0]]]
    for t in tops[1:]:
        if t - runs[-1][-1] > _RAIL_GAP:
            runs.append([])
        runs[-1].append(t)
    band = max(runs, key=len)
    stack = [c for c in stack
             if band[0] - 0.5 <= round(c["top"], 1) <= band[-1] + 0.5]
    if len(stack) < _RAIL_FLOOR:
        return None
    return {"x": float(x), "glyph": _RAIL_GLYPH,
            "top": min(c["top"] for c in stack),
            "bottom": max(c["bottom"] for c in stack)}


def _rows(model, finder, body_x0: float, pages: int) -> list[list]:
    """The visual rows this block may contain.

    Furniture core already tagged and the footnote zone (below the court's
    own 144pt separator rect) are neither claimed nor consumed: core has
    routed both, and a reader that took them would print them twice."""
    out: list[list] = []
    for pm in model.pages[:pages]:
        cut = _footnote_cut(pm, body_x0)
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip() or finder.kind(pm, line):
                continue
            if cut is not None and line.top >= cut:
                continue
            key = round(line.top, 1)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        out.extend(groups[k] for k in order)
    return out


def _footnote_cut(pm, body_x0: float) -> float | None:
    """The top of this page's footnote zone: a RECT two inches wide at the
    page's left text rail. Invariant on all 58 occurrences in the corpus."""
    tops = [r.top for r in pm.h_rules
            if r.source == "rect"
            and _SEP_WIDTH[0] <= r.width <= _SEP_WIDTH[1]
            and abs(r.x0 - body_x0) <= 24.0
            and r.top > pm.height * 0.30]
    return min(tops) if tops else None


# --------------------------------------------------------------------------
# STYLE A — the fenced centred stack
# --------------------------------------------------------------------------

def _read_fenced(model, geom, body_size: float, body_x0: float):
    finder = FurnitureFinder(model, body_x0, body_size)
    axis = model.pages[0].width / 2
    rows = _rows(model, finder, body_x0, _MAX_PAGES)
    if len(rows) < 10:
        return NOTHING
    txt = [_norm(" ".join(l.plain for l in g)) for g in rows]

    def _mid(i: int) -> float:
        g = rows[i]
        return (min(l.x0 for l in g) + max(l.x1 for l in g)) / 2

    def _centred(i: int) -> bool:
        return abs(_mid(i) - axis) <= _CENTRED_TOL

    fences = [i for i in range(len(rows))
              if _FENCE_TEXT.match(txt[i].replace(" ", ""))
              and abs(_mid(i) - axis) <= _AXIS_TOL]
    p1 = [i for i in fences if rows[i][0].page == 1]
    if len(p1) < 3:
        return NOTHING
    f1, f2, f3 = p1[0], p1[1], p1[2]
    # …with the masthead above the first fence and the DOCKET between the
    # first pair. Both required; neither is a wording test.
    mast = [i for i in range(f1)
            if (rows[i][0].size or 0) >= body_size + _MASTHEAD_OVER
            and all(l.all_bold for l in rows[i]) and _centred(i)]
    if len(mast) != f1 or not mast:
        return NOTHING
    dockets_at = [i for i in range(f1 + 1, f2) if _DOCKET.match(txt[i])]
    if len(dockets_at) != f2 - f1 - 1 or not dockets_at:
        return NOTHING
    # THE FOOT: the first byline. A claim of unknown extent is worse than
    # none, so a record whose paper we cannot see the end of is declined.
    stop = _first_byline(txt, rows, body_x0)
    if stop is None or stop <= f3:
        return NOTHING

    kinds: list[str | None] = [None] * len(rows)
    for i in fences:
        if i < stop:
            kinds[i] = "#fence"
    # THE RUNNING HEAD WHERE RECURRENCE CANNOT SEE IT. The ladder reaches
    # page 2 on 6 of the 15 records and the head is set at BODY size, so
    # neither the small-type band nor the size test reaches it; on a 2- or
    # 3-page slip it may print too few times to clear core's floor. The band
# is measured (heads at 38-51 against a first body row never above 74)
    # and the head is recorded as Dropped, never placed.
    for i in range(stop):
        if kinds[i] is not None or rows[i][0].page == 1:
            continue
        if rows[i][0].top < model.pages[rows[i][0].page - 1].height * _HEAD_BAND:
            kinds[i] = "#head"

    for i in mast:
        kinds[i] = "court"
    for i in dockets_at:
        kinds[i] = "docket"
    for i in range(f2 + 1, f3):
        kinds[i] = "caption"

    # ---- below the caption sandwich: the ladder, each run bounded --------
    state: str | None = None
    rail: float | None = None
    for i in range(f3 + 1, stop):
        if kinds[i] is not None:
            # A FENCE OR A RUNNING HEAD ENDS THE RUN IT INTERRUPTS: the
            # fence is a section boundary by construction, the head is a
            # page turn, and a ladder that resumes below one opens with its
            # own label (reese sets 'Amicus Curiae for Appellant:' as the
            # first row of page 2).
            state = None
            continue
        t = txt[i]
        if _DATE.match(t):
            kinds[i], state = "date", None
        elif _ORIGIN.match(t):
            kinds[i], state = "origin", "origin"
        elif _MILJUDGE.match(t):
            kinds[i], state, rail = "judge", "rail", rows[i][0].x0
        elif _SENTENCE.match(t):
            kinds[i], state, rail = "case-info", "rail", rows[i][0].x0
        elif _FOR.match(t):
            kinds[i], state, rail = "counsel", "rail", rows[i][0].x0
        elif _BEFORE.match(t):
            kinds[i], state, rail = "roster", "rail", rows[i][0].x0
        elif _ATTRIB.search(t):
            kinds[i], state, rail = "panel", "rail", rows[i][0].x0
        elif _PUBSTMT.match(t):
            kinds[i], state = "publication", "pub"
        # ---- continuations, each ended by the run's own bound -----------
        elif state == "origin" and _centred(i):
            # 'On Remand from' / 'the United States Court of Appeals for the
            # Armed Forces' — the origin's own wrap, centred on the axis
            # like the row it continues. The ladder below is at the body
            # rail and the date labels itself, so the axis bounds the run.
            kinds[i] = "origin"
        elif state == "rail" and rail is not None \
                and abs(rows[i][0].x0 - rail) <= 1.5:
            # EVERY LADDER RUN CONTINUES AT ITS OWN RAIL. The labels above
            # are tested first, so a wrap can never swallow the next entry,
            # and the byline stop bounds the last run.
            kinds[i] = kinds[i - 1] if kinds[i - 1] else "case-info"
        elif state == "pub" and _centred(i):
            kinds[i] = "publication"
        else:
            state = None

    # ---- emit -----------------------------------------------------------
    ctx = _Ctx()
    counsel: list[str] = []
    caption_rows: list[str] = []
    lower: list[str] = []
    judges: list[str] = []
    history: list[str] = []
    dockets: list[str] = []
    suffixes: list[str] = []
    court_rows: list[str] = []
    roster_rows: list[str] = []
    for i in range(stop):
        kind = kinds[i]
        if kind is None:
            continue
        pieces = rows[i]
        if kind == "#fence":
            ctx.rule(pieces)
        elif kind == "#head":
            ctx.drop(pieces, "running-head")
        elif kind == "court":
            court_rows.append(txt[i])
            ctx.emit(pieces, "court", centre=True)
        elif kind == "docket":
            got = _DOCKET.match(txt[i])
            dockets.append(_norm(got.group(1)))
            if got.group(2):
                suffixes.append(_norm(got.group(2)))
            ctx.emit(pieces, "docket", centre=True)
        elif kind == "caption":
            caption_rows.append(txt[i])
            ctx.emit(pieces, "caption", centre=True)
        elif kind == "origin":
            lower.append(_strip_marker(txt[i]))
            ctx.emit(pieces, "lower-court", centre=True)
        elif kind == "date":
            ctx.crit.setdefault("decision_date",
                                _norm(_DATE.match(txt[i]).group(1)))
            ctx.emit(pieces, "date", centre=True)
        elif kind == "judge":
            judges.append(txt[i])
            ctx.emit(pieces, "lower-court", centre=False)
        elif kind == "case-info":
            history.append(txt[i])
            ctx.emit(pieces, "case-info", centre=False)
        elif kind == "counsel":
            counsel.append(txt[i])
            ctx.emit(pieces, "counsel", centre=False)
        elif kind in ("roster", "panel"):
            if kind == "roster":
                roster_rows.append(txt[i])
            ctx.emit(pieces, "panel", centre=False)
        elif kind == "publication":
            ctx.emit(pieces, "publication", centre=True)

    # ---- criteria, populated BEFORE anything is gated on them ------------
    if court_rows:
        ctx.crit.setdefault("court", _norm(" ".join(court_rows)))
    _dockets(ctx, dockets, suffixes)
    if lower:
        ctx.crit.setdefault("lower_court", _norm(" ".join(lower)))
    if judges:
        # 'Military Judge: Joshua D. Rosen.' — the label is apparatus, the
        # names after the colon are who tried it.
        names = _norm(" ".join(judges)).split(":", 1)[-1].strip().rstrip(".")
        if names:
            ctx.crit.setdefault("lower_court_judge", names)
    if history:
        ctx.crit.setdefault("history", _norm(" ".join(history))[:2000])
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    sides = _sides_by_weight(txt, rows, f2 + 1, f3)
    _parties(ctx, sides)
    if roster_rows:
        line = _norm(" ".join(roster_rows))
        ctx.crit.setdefault("panel_line", line)
        ctx.crit.setdefault("judges", line)
        names = _panel_names(line)
        if names:
            ctx.crit.setdefault("panel", names)
    if counsel:
        # Counsel printed inside the headmatter STAYS there; its text is
        # copied into criteria.attorneys, which core fills only from a MOVED
        # block (core-patch-queue item 41).
        ctx.crit.setdefault("attorneys", _norm(" ".join(counsel))[:2000])
    if any(k == "publication" for k in kinds[:stop]):
        # One wording on all 15: 'This is an unpublished opinion and, as
        # such, does not serve as precedent under AFCCA Rule of Practice and
        # Procedure 30.4.' There is no published twin in this corpus and none
        # is assumed — the status is stated only where the statement stands.
        ctx.crit.setdefault("publication_status", "unpublished")
    ctx.crit.setdefault("headmatter_style", STYLE_FENCED)
    # NO `doc_type_final`. Eleven of these fifteen came back typed 'order'
    # before this port, and it was worth checking WHY before declaring the
    # type away: the cause was the missing PROFILE, not the missing reader.
    # With no CourtProfile registered, `get_profile('afcca')` returned the
    # default `BylineGrammar(titles=('Justice',))`, so 'DOUGLAS, Senior
    # Judge:' parsed as nothing, the writing came back authorless and core
    # typed the paper an order — while the four PER CURIAM records, which
    # need no title, typed correctly. Declaring the profile's own titles
    # fixes all eleven with the claim withdrawn, so the type is core's to
    # decide and this reader does not overrule it.
    return ctx.result()


def _strip_marker(text: str) -> str:
    """A row with a footnote marker glued to its tail, without it. Only the
    origin and the date carry one, and neither ever ends in a digit."""
    return re.sub(r"\d+$", "", text).strip()


def _first_byline(txt: list[str], rows: list, body_x0: float) -> int | None:
    """The row where the paper begins signing, at the body rail.
    'Military Judge:' and 'For Appellant:' share the colon terminal and
    neither carries a surname before it, so neither can match."""
    parser = BylineParser(BylineGrammar(
        style="prose",
        titles=("Judge", "Chief Judge", "Senior Judge",
                "Appellate Military Judge")))
    for i, t in enumerate(txt):
        if rows[i][0].x0 - body_x0 > 24.0:
            continue
        if parser.parse(t) is None:
            continue
        return i
    return None


def _sides_by_weight(txt: list[str], rows: list, lo: int, hi: int) -> list[str]:
    """The parties either side of the pivot, read by WEIGHT: the bold rows
    are the names, the italic rows are the statuses, the roman row is the
    appellant's rate and service."""
    pivot = next((i for i in range(lo, hi) if _PIVOT.match(txt[i])), None)
    if pivot is None:
        return []
    out = []
    for a, b in ((lo, pivot), (pivot + 1, hi)):
        names = [txt[i] for i in range(a, b)
                 if all(l.all_bold for l in rows[i])
                 and not _DOCKET.match(txt[i])]
        joined = " ".join(names).strip().rstrip(",;")
        if joined:
            out.append(joined)
    return out if len(out) == 2 else []


# --------------------------------------------------------------------------
# STYLE B — the parenthetical box
# --------------------------------------------------------------------------

def _read_box(model, geom, body_size: float, body_x0: float, rail: dict):
    finder = FurnitureFinder(model, body_x0, body_size)
    pm = model.pages[0]
    axis = pm.width / 2
    rows = _rows(model, finder, body_x0, 1)
    if len(rows) < 6:
        return NOTHING

    def _mid(g) -> float:
        return (min(l.x0 for l in g) + max(l.x1 for l in g)) / 2

    # The masthead is everything above the box; the box is every row inside
    # the rail's own vertical span. Nothing below it is headmatter — the
    # order's body opens on the next paragraph and it is never claimed.
    top, bottom = rail["top"] - 2.0, rail["bottom"] + 2.0
    mast, box = [], []
    for g in rows:
        if g[0].top < top:
            mast.append(g)
        elif g[0].top <= bottom:
            box.append(g)
    if not box:
        return NOTHING
    good = [g for g in mast
            if (g[0].size or 0) >= body_size + _MASTHEAD_OVER
            and all(l.all_bold for l in g)
            and abs(_mid(g) - axis) <= _CENTRED_TOL]
    if len(good) != len(mast) or not good:
        return NOTHING

    ctx = _Ctx()
    court_rows = []
    for g in mast:
        court_rows.append(_norm(" ".join(l.plain for l in g)))
        ctx.emit(g, "court", centre=True)

    block, left_txt, right_txt = _box(box, rail, pm, ctx)
    if block is None:
        return NOTHING
    ctx.items.append(block)

    ctx.crit.setdefault("court", _norm(" ".join(court_rows)))
    # THE RIGHT COLUMN states the docket, what the paper calls itself and
    # which panel sat — in that printed order, on all 17.
    dockets, suffixes, titles, panels = [], [], [], []
    for t in right_txt:
        role = _right_role(t)
        if role == "docket":
            got = _DOCKET.match(t)
            dockets.append(_norm(got.group(1)))
            if got.group(2):
                suffixes.append(_norm(got.group(2)))
        elif role == "panel":
            panels.append(t)
        elif role == "title":
            titles.append(t)
    _dockets(ctx, dockets, suffixes)
    if titles:
        ctx.crit.setdefault("title", _norm(" ".join(titles)))
    if panels:
        ctx.crit.setdefault("panel_line", _norm(" ".join(panels)))
    caption_rows = [t for t in left_txt if t]
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    _parties(ctx, _sides_by_rail(box, rail))
    ctx.crit.setdefault("headmatter_style", STYLE_BOX)
    return ctx.result()


def _box(box: list, rail: dict, pm, ctx):
    """The parenthetical box as a CaptionBlock, paired by printed row.

    Sides split AT THE RAIL, glyph by glyph — whether pdfio broke a justified
    row at its column gap is an accident of how wide the gap happened to be,
    and a whole-line test would put a cell on the wrong side of the column."""
    mid = rail["x"]
    left, right = [], []
    left_txt, right_txt = [], []
    for g in box:
        l_cells, r_cells = [], []
        for line in g:
            shed = _shed_rail(line, rail)
            if shed is None:
                continue                      # the line WAS the rail
            lo = _side(shed, mid, "L")
            hi = _side(shed, mid, "R")
            if lo is not None:
                l_cells.append(lo)
            if hi is not None:
                r_cells.append(hi)
        rt = _norm(" ".join(c.plain for c in r_cells))
        left.append(_cell(l_cells, pm, "caption"))
        # THE RIGHT COLUMN STATES THREE DIFFERENT FACTS and they are kept
        # apart, because they are different facts: the docket, what the paper
        # calls itself, and which panel sat. Read as one role they render as
        # a second caption, which is what the old engine's fold made of them.
        right.append(_cell(r_cells, pm, _right_role(rt)))
        left_txt.append(_norm(" ".join(c.plain for c in l_cells)))
        right_txt.append(rt)
        ctx.consumed.update(l.id for l in g)
    # THE RAIL'S OWN RUN is not the caption's vertical rhythm: once the
    # glyphs are gone the rows that held nothing else are empty on BOTH
    # sides, and left standing they render as phantom blank rows.
    while left and not left_txt[-1] and not right_txt[-1]:
        left.pop(), right.pop(), left_txt.pop(), right_txt.pop()
    if not left:
        return None, [], []
    ids = tuple(sorted(l.id for g in box for l in g))
    return (m.CaptionBlock(
        left=left, right=right, rail=rail["glyph"], rail_rows=len(left),
        style_id="parenthetical-box",
        fp={"rail": rail["glyph"], "rail_band": (rail["top"], rail["bottom"]),
            "mid_x": mid},
        prov=m.Prov(pm.number, ids)), left_txt, right_txt)


_PANEL_CELL = re.compile(r"^(?:Special |En Banc )?Panel\b")


def _right_role(text: str) -> str:
    """What a right-hand cell of the parenthetical box states."""
    if not text:
        return "caption"
    if _DOCKET.match(text):
        return "docket"
    if _PANEL_CELL.match(text):
        return "panel"
    return "title"


def _cell(cells: list, pm, role: str) -> m.HmLine:
    if not cells:
        return m.HmLine(text="", prov=m.Prov(pm.number, ()), role=role)
    parts = sorted(cells, key=lambda l: l.x0)
    text = ""
    for p in parts:
        piece = line_markup(p)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    first = parts[0]
    return m.HmLine(
        text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _rail_chars(line, rail) -> list:
    """The chars of ``line`` that belong to the rail's own column."""
    lo, hi = rail["x"] - _RAIL_WINDOW, rail["x"] + _RAIL_WINDOW
    return [c for c in line.chars
            if (c.get("text") or "") == rail["glyph"] and lo <= c["x0"] <= hi]


def _shed_rail(line, rail):
    """``line`` with the rail's glyphs removed, or None when the line WAS the
    rail. The glyph is identified by its COLUMN, never by its character."""
    ids = {id(c) for c in _rail_chars(line, rail)}
    if not ids:
        return line
    kept = [c for c in line.chars if id(c) not in ids]
    if not any((c.get("text") or "").strip() for c in kept):
        return None
    return _replace(line, kept)


def _side(line, mid: float, want: str):
    """The part of ``line`` that lies on one side of the rail, or None."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, keep)


def _replace(line, chars: list):
    import dataclasses
    return dataclasses.replace(
        line, chars=chars,
        x0=min(c["x0"] for c in chars),
        x1=max(c.get("x1", c["x0"]) for c in chars))


def _sides_by_rail(box: list, rail: dict) -> list[str]:
    """The parties of the order caption, read by POSITION in the left column.

    Every left cell is bold here, so weight says nothing. What the page does
    distinguish is the column's own rail: the party's name, rank and service
    stand at it (x0 = 108) and the STATUS labels are indented from it
    (x0 = 189). The pivot is the indented `v.`; each party is the FIRST row
    at the rail on its side of it — the order the page prints, name before
    rate, on all 17."""
    cells: list[tuple[float, str]] = []
    for g in box:
        for line in g:
            shed = _shed_rail(line, rail)
            if shed is None:
                continue
            lo = _side(shed, rail["x"], "L")
            if lo is None:
                continue
            cells.append((lo.x0, _norm(lo.plain)))
    if not cells:
        return []
    edge = min(x for x, _t in cells)
    pivot = next((k for k, (_x, t) in enumerate(cells) if _PIVOT.match(t)),
                 None)
    def first_at_rail(seq) -> str:
        for x, t in seq:
            if abs(x - edge) <= 2.0 and not _STATUS.match(t):
                return t
        return ""
    if pivot is None:
        # A writ petition captions ONE party ('In re Chantay P. WHITE').
        one = first_at_rail(cells)
        return [one] if one else []
    left = first_at_rail(cells[:pivot])
    right = first_at_rail(cells[pivot + 1:])
    return [x for x in (left, right) if x]


# --------------------------------------------------------------------------
# shared
# --------------------------------------------------------------------------

def _dockets(ctx, dockets: list[str], suffixes: list[str]) -> None:
    if not dockets:
        return
    ctx.crit.setdefault("docket_number", dockets[0])
    extra = dockets[1:] + suffixes
    if extra:
        ctx.crit.setdefault("other_dockets", extra)


def _parties(ctx, sides: list[str]) -> None:
    if not sides:
        return
    ctx.crit.setdefault("parties", sides)
    ctx.crit.setdefault("case_name", " v. ".join(sides))


def _panel_names(line: str) -> list[str]:
    """'Before DOUGLAS, MCCALL, and KUBLER, Appellate Military Judges.' ->
    three names. The bench designation is the court's, not a member's."""
    body = re.sub(r"^Before\s+", "", line)
    body = re.split(r",?\s*Appellate Military", body)[0]
    out = []
    for piece in re.split(r",|\band\b", body):
        name = piece.strip().strip(".")
        if name and name.lower() not in ("and", ""):
            out.append(name)
    return out


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

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

    def rule(self, group: list) -> None:
        """The court TYPED this rule — re-emit it where the page set it."""
        parts = sorted(group, key=lambda l: l.x0)
        self.items.append(m.Rule(
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            span="center", typed=True))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self, doc_type=None) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": doc_type}
