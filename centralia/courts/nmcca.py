"""United States Navy-Marine Corps Court of Criminal Appeals ('nmcca').

**THIS IS NOT A NEW MEXICO COURT.** The id sits between `nm` and `nmctapp`
in the registry and the resemblance ends there: `nmcca` is the Navy-Marine
Corps Court of Criminal Appeals, an Article I military appellate court that
reviews courts-martial under Article 66, UCMJ. Every one of the 32 corpus
records is captioned `United States v. <servicemember>`, every panel is a
panel of `Appellate Military Judges`, and the court below is the `United
States Navy-Marine Corps Trial Judiciary`. Nothing about nm's or nmctapp's
paper applies, and this file inherits from neither — it imports core only.
It is the FIRST of the service-CCA family in this engine; acca, afcca,
uscgcoca and armfor come later, and the contract below is written so they
can be held to it or measured against it.

    ┌──────────────────────────────────────────────────────────────────┐
    │ This opinion is subject to administrative correction before      │
    │ final disposition.                          the standing notice  │
    │                                                                  │
    │                   ⟨ the court's SEAL — curves, no text ⟩          │
    │                                                                  │
    │                          Before                                  │
    │                DALY, GROSS, and de GROOT           the panel     │
    │                 Appellate Military Judges                        │
    │                _________________________     FENCE 1            │
    │                      UNITED STATES              (bold: party)    │
    │                        Appellee                 (ital: status)   │
    │                           v.                    the pivot        │
    │                   Mason W. WILLIAMS             (bold: party)    │
    │      Hospital Corpsman Third Class (E-4), U.S. Navy             │
    │                                                 (roman: rate)   │
    │                        Appellant                (ital: status)   │
    │                     No. 202400478               the DOCKET      │
    │                _________________________     FENCE 2            │
    │                 Decided: 13 July 2026           the date         │
    │  Appeal from the United States Navy-Marine Corps Trial Judiciary │
    │                     Military Judges:                             │
    │                Derrick A. Poteet (arraignment)  the court below  │
    │                  Stephen F. Keane (trial)                        │
    │  Sentence adjudged 17 June 2021 by a special court-martial …     │
    │  Judgment: reduction to E-1.               the TRIAL RECITAL    │
    │                    For Appellant:                                │
    │              Major Colin P. Norton, USMC        the appearances  │
    │                    For Appellee:                                 │
    │        Lieutenant Stephanie N. Fisher, JAGC, USN                 │
    │  Chief Judge DALY delivered the opinion of the Court, in which   │
    │  Senior Judge HARRELL and Judge KORN joined.   the attribution   │
    │                _________________________     FENCE 3            │
    │      This opinion does not serve as binding precedent but        │
    │           may be cited as persuasive authority under             │
    │           NMCCA Rule of Appellate Procedure 30.2.                │
    │                                          the PUBLICATION statement│
    │                _________________________     FENCE 4            │
    │  PER CURIAM:                            (the paper begins)       │
    └──────────────────────────────────────────────────────────────────┘

WHICH DIVIDER SHAPE THIS IS: **NONE.** There is no caption column divider
on an nmcca slip — no drawn rule, no box rail, no typed `)` or `:` column,
and no measurable x0 threshold, because the caption is a SINGLE CENTRED
STACK. All seven caption rows are centred on the page axis, and the widest
of them (the rate line) runs from 156.0 to 456.1 straight across where a
rail would have to stand. So no `CaptionBlock` is emitted and no second
column is invented — the iowactapp / ohioctapp / nmctapp answer, arrived at
by measurement rather than by analogy. This also contradicts the OLD
engine's shared military base, which folds a `)` rail into every CCA
headmatter (`_military.py`: `_fold_rail_caption(d["summary"], ")")`);
MEASURED over all 32 records page 1 contains ZERO `)` glyphs standing as a
column. That fold is acca/afcca ORDER paper, not nmcca opinion paper, and
inheriting it here would have invented a rail the page does not draw.

WHAT THE PAGE DOES DRAW IS A FENCE, AND THE FENCE IS THE PARSER. The court
types its rules — a run of underscores set as text, never a vector — in ONE
invariant measure, dead on the page axis. Measured over every underscore
row in all 32 records (128 rows): 127 are 137.5pt wide and one is 126.5pt
(salazar types 23 underscores instead of 25), and ALL 128 have their
midpoint within 0.1pt of 306.0 on a 612pt page. Not one is off the axis, so
the axis is the test and the measure is only the payload — ca5's lesson
('the same measure OFF the axis means something else entirely'), holding in
the easy direction here.

THE DISPATCH IS THE FIRST FENCE PAIR, NOT A TITLE — the paper has no title.
nmcca prints no masthead and no `OPINION` label: the only thing that names
the court on the cover is the SEAL, which is drawn as 30 bare curves and
yields no text at all. So `criteria.court` and `criteria.title` are left
EMPTY, because the page states neither, and inventing them from the
registry label would be reading the profile instead of the paper. What the
page does state, structurally, is: two typed axis fences on page 1, with
`Appellate Military Judges` above the first (the court's own bench
designation — a closed BENCH vocabulary, the one landmark every service CCA
prints) and the docket row immediately above the second. All three hold on
all 32; any record missing any of them is not this contract and the reader
returns NOTHING.

THE NEAREST COUSIN ALREADY IN THE ENGINE IS bap1, NOT ANY STATE COURT.
bap1's 'centred ladder' is the same family — a cover whose every row is
centred on the sheet's axis and whose zones are fenced by a typed row of
underscores on that axis — and the difference between the two is the only
interesting thing about nmcca's version: bap1 fences EVERY zone on all 32 of
its records, so its reader can read the fences as a complete partition,
while nmcca fences the caption always and everything below it sometimes. So
the dispatch here cannot be 'the Nth fence'; it is the first PAIR.

THE FENCE COUNT IS NOT FIXED, SO IT IS NEVER COUNTED. Below the caption
sandwich the court fences some sections and not others: 29 records type
four fences (the pair around the caption, the pair around the publication
statement), zavala types five (its attribution recital gets a fence of its
own), and perez types two (its publication statement is fenced on neither
side). A reader that keyed on 'the third rule' would misread three records;
this one keys on the first PAIR and reads every later fence as furniture it
re-emits in place.

WEIGHT AND SLOPE READ THE CAPTION, NOT WORDING. Inside the sandwich the
typeface does the whole job, on all 32 records without exception:

  * **BOLD** is a party — `UNITED STATES`, `Mason W. WILLIAMS` — and the
    pivot `v.`, and the docket `No. 202400478`;
  * *ITALIC* is a party STATUS — `Appellee`, `Appellant` — the same closed
    role vocabulary every court prints, set in slope here;
  * roman is the appellant's RATE AND SERVICE — `Hospital Corpsman Third
    Class (E-4), U.S. Navy`, `Private (E-1), U.S. Marine Corps`. It is part
    of the party's designation and never part of the name.

So `parties` is built from the BOLD rows either side of the pivot and
`case_name` from those two, and no party name is ever read by wording.

THE DOCKET IS THE DOCKET AND THERE IS NO CITATION. nmcca numbers its cases
`No. 202400478` — a nine-digit docket whose first four digits are the term
year — and prints it as the caption's last row, in bold, above the second
fence. The running head on every continuation sheet repeats it as `United
States v. Beckman, NMCCA No. 202500258`, and that `NMCCA No.` is the
DOCKET wearing the court's initials, NOT a public-domain citation: this
court assigns no vendor-neutral cite, so `criteria.citation` stays None on
all 32. Conflating the two cost ill its whole corpus (commit 03e8652) and
the trap here is the mirror image — an `NMCCA`-prefixed number that LOOKS
like a neutral cite and is not one. The running head is furniture in any
case and this reader never touches it (core's `FurnitureFinder` tags both
its rows `running-head` on every sheet).

ONE DOCKET WEARS A REVIEW-TYPE SUFFIX. suarez prints `No. 202300049 (f
rev)` — further review, the case returning after remand from the Court of
Appeals for the Armed Forces — and states the posture in an italic recital
under the origin: 'upon further review following remand from / the United
States Court of Appeals for the Armed Forces'. `docket_number` takes the
NUMBER (`202300049`, which is what the running head prints and what CAAF
docketed), and the posture goes to `history` beside the trial recital,
where it belongs. The parenthesized suffix is kept in `other_dockets` so
the printed form is not lost.

THE TRIAL RECITAL IS THE CASE'S HISTORY. Every record sets a justified
prose paragraph naming the court-martial, the place, its composition and
the sentence in the Entry of Judgment: 'Sentence adjudged 28 December 2025
by a general court-martial tried at Marine Corps Recruit Depot Parris
Island, South Carolina, consisting of a military judge sitting alone.
Sentence in the Entry of Judgment: confinement for 15 years, …' (31
records; perez opens 'Findings announced 5 November 2024 …' because its
findings and sentence came from differently composed courts). It reads as
`case-info` and its text goes to `criteria.history`. It is BOUNDED BY ITS
OWN RAIL: the recital is the only left-aligned run in the block, set at
126.0 on the 486-measure template and 108.0 on the wider 504-measure one
(cardoso, fisk), and its wraps stand at that same x0 to within a point,
while every row above and below it is centred. So the run ends where the
rail ends — no wording test closes it.

THE APPEARANCES ARE LABELLED AND THE LABEL CLOSES THEM. `For Appellant:`
(32) and `For Appellee:` (16) are centred roman labels; the counsel under
each are centred ITALIC rows ('Major Colin P. Norton, USMC', 'Lieutenant
Commander Alaric A. Piette, JAGC, USN', 'Kimberly D. Barnes, Esq.',
'Major Mary Claire Finnen, USMC (argued)'). Counsel printed inside the
headmatter STAYS there; its text is copied into `criteria.attorneys`, which
core fills only from a MOVED block — core-patch-queue item 41, closed here
inside the court file as five other ports have closed it.

THE ATTRIBUTION RECITAL IS THE PANEL SPEAKING, NOT A BYLINE. 13 records
print 'Chief Judge DALY delivered the opinion of the Court, in which Senior
Judge HARRELL and Judge KORN joined.' — at the recital's own rail, above
the publication statement and above the signing byline. It reads as `panel`
and it is NOT reported as an announced author, because the paper signs
itself two rows further down ('DALY, Chief Judge:') and a printed byline
always outranks an announcement. The other 19 records are per curiam and
print no recital at all; `authorless` would be no defect here either way
(the user's ruling, 2026-08-19) — but in fact every record signs.

THE PUBLICATION STATEMENT IS A STATUS, NOT A NOTICE, SO IT IS NOT DROPPED.
Set bold and centred between fences, in two wordings: 'This opinion does
not serve as binding precedent but may be cited as persuasive authority
under NMCCA Rule of Appellate Procedure 30.2.' (13 records, three rows) and
'This opinion does not serve as binding precedent under NMCCA Rule of
Appellate Procedure 30.2(a).' (19 records, two rows) — fisk brackets the
longer form. Both say the paper is not binding precedent, so
`publication_status = 'unpublished'`, and the rows keep the `publication`
role in place rather than being lifted out. What IS recorded as `Dropped`
is the standing italic head 'This opinion is subject to administrative
correction before final disposition.' — 27 of the 32 records, at the top of
page 1 above the seal, standing boilerplate about the paper's provisional
state and the court's only notice proper.

ONE MORE STAMP EXISTS AND THIS READER NEVER SEES IT. mcgrath_1 is the
corrected reissue of mcgrath under the SAME docket (202500115), and it
prints the reason at the foot of page 1 in centred italic: '18 May 2026:
Administrative Correction to reflect correct composition of Appellate
Judges who decided Appellant's case.' It sits BELOW the footnote separator,
so core's `FootnoteZones` has already taken it and it arrives glued to the
end of footnote 1 — which is exactly what v1 does with it too. The
`_CORRECTION` guard below therefore fires on NOTHING in this corpus; it is
declared for the reissue that prints the stamp above the separator, and it
is recorded here as firing on nothing rather than left to look like a
reading that works.

WHERE THE BLOCK ENDS, AND WHAT IT MUST NOT SWALLOW. The reader ends at the
first byline, which on all 32 records stands on page 2 at the body rail. Two
things inside the span are NOT the block and are left alone:

  * the RUNNING HEAD on every continuation sheet. The block runs through it
    on 17 of the 32 records — every record whose block reaches page 2 at
    all — and core cannot always see it, because core identifies furniture
    by RECURRENCE and this head is set at BODY size: on a 2-page slip it
    prints exactly once, below the >=2-sheet floor, and on williams the
    second row changes wording at page 5 ('Modified Entry of Judgment') so
    neither variant clears the floor either. Where core does tag it this
    reader skips it; where core does not, the reader takes it by the
    MEASURED BAND and records it as `Dropped` kind 'running-head' (31 rows
    over the corpus). The old engine needed a court-specific 70pt head band
    for exactly this;
  * the FOOTNOTE ZONE. Page 1 carries a footnote on 14 records — a credit
    for pretrial confinement hung off the trial recital — and the court
    draws its separator as a RECT 144.0pt wide at the page's left text
    rail, invariant on all 200 occurrences in the corpus. Rows at or below
    that rect are the note's, not the block's; core's `FootnoteZones` has
    already routed them and this reader must not consume them, or the note
    would render twice.
"""

from __future__ import annotations

import re

from .. import model as m
from ..courts import register
from ..profile import CourtProfile
from ..resolve.bylines import DEFAULT_ABBREV, BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

STYLE_FENCED = "nmcca fenced centred stack"

# ---- nmcca's declared facts (measured over all 32 records) --------------
# THE FENCE. A typed run of underscores, centred on the page axis. All 128
# in the corpus: width 137.5 (127) or 126.5 (salazar), midpoint within
# 0.1pt of the axis. The axis is the test; the measure is payload.
_FENCE_TEXT = re.compile(r"^_{6,}$")
_AXIS_TOL = 4.0
# CENTRED ON THE AXIS, for a TEXT row. Measured over all 822 rows this
# reader emits: every centred row — caption, counsel, date, docket, origin,
# publication — sits within 1.6pt of 306.0, and the nearest off-axis row
# (the trial recital's first line) is 157.2pt off. So the test has 155pt of
# headroom and nothing is being tuned; 6.0 is generous by two decimal
# orders and still cannot reach a left-aligned run.
_CENTRED_TOL = 6.0
# THE BENCH DESIGNATION — the landmark that names this contract. Every
# service CCA seats a panel of appellate military judges and says so.
_BENCH = re.compile(r"^Appellate Military Judges$", re.I)
_BEFORE = re.compile(r"^Before$", re.I)
# THE DOCKET: 'No. 202400478', 'No. 202300049 (f rev)'. Nine digits, the
# first four the term year. Never a citation — this court assigns none.
_DOCKET = re.compile(r"^Nos?\.\s*(\d{6,})\s*(\([^)]*\))?\.?$", re.I)
_DATE = re.compile(r"^Decided:\s*(.+?)\.?$", re.I)
# WHERE THE APPEAL CAME FROM. All 32: 'Appeal from the United States
# Navy-Marine Corps Trial Judiciary'. The other openings are admitted
# because Article 66 review also reaches the court on the Judge Advocate
# General's certificate and on writ-appeal; none appears in this corpus.
_ORIGIN = re.compile(
    r"^(?:Appeal from|Appeals from|Review of|Certificate for Review"
    r"|On (?:further )?review|Writ[- ]Appeal Petition)\b", re.I)
# THE APPELLATE POSTURE is set ITALIC and centred under the origin — 'upon
# further review following remand from / the United States Court of Appeals
# for the Armed Forces' (suarez, the one record returning after a CAAF
# remand). It carries no landmark of its own on either row, so slope and
# the axis identify it and no wording is matched.
# WHO TRIED IT. 26 records print one military judge, 6 print two or more
# with the stage in parentheses ('Derrick A. Poteet (arraignment)').
_MILJUDGE = re.compile(r"^Military Judges?:$", re.I)
# THE TRIAL RECITAL — the court-martial, its place, its composition and the
# sentence in the Entry of Judgment. 31 open 'Sentence adjudged', perez
# opens 'Findings announced' (findings by members, sentence by the judge).
_RECITAL = re.compile(r"^(?:Sentence adjudged|Findings announced"
                      r"|Sentence approved|Findings and sentence)\b", re.I)
# THE APPEARANCE LABEL. 'For Appellant:' (32), 'For Appellee:' (16).
_FOR = re.compile(r"^For\s+[A-Z][A-Za-z .\-]*:$")
# THE ATTRIBUTION RECITAL. 13 records; the other 19 are per curiam.
_ATTRIB = re.compile(
    r"^(?:(?:Chief|Senior|Acting)\s+)?Judge\s+\S+.*\bdelivered the opinion\b"
    r"|\bdelivered the opinion of the Court\b")
# THE PUBLICATION STATEMENT, in its two wordings (fisk brackets it).
_PUBSTMT = re.compile(r"^\[?This opinion does not serve as binding precedent",
                      re.I)
# THE STANDING NOTICE, at the very top of page 1 above the seal.
_NOTICE = re.compile(r"^This opinion is subject to administrative correction",
                     re.I)
# AN ADMINISTRATIVE CORRECTION STAMP (mcgrath_1, the corrected reissue).
_CORRECTION = re.compile(
    r"^\d{1,2} \w+ \d{4}:\s*Administrative Correction\b", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# The footnote separator this court draws: a RECT two inches wide at the
# page's left text rail. Invariant on all 200 occurrences.
_SEP_WIDTH = (138.0, 152.0)
# THE RUNNING-HEAD BAND on a continuation sheet: the head's two rows top
# out at 55.4 over all 190 sheets and the first body row never rises above
# 73.8, so 0.09 of a 792pt page (71.3) separates them with 16pt to spare on
# either side.
_HEAD_BAND = 0.09
# The block never runs past page 2; the byline stop bounds it anyway.
_MAX_PAGES = 3


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---- the profile -------------------------------------------------------
# BYLINE FORMS, all 33 in the corpus (32 lead + wenzel's dissent):
#   'PER CURIAM:'                    19 records
#   'DALY, Chief Judge:'             the prose form, spelled title
#   'KISOR, Senior Judge:' / 'GANNON, Judge:'
#   'de GROOT, Judge:'               fisk — a NOBILIARY PARTICLE (see below)
#   'de GROOT, Judge (concurring in the judgment):'   cardoso's concurrence
#   'McCOY, J. (dissenting):'        wenzel's dissent — abbreviated title
# The spelled and abbreviated forms co-occur in one document (wenzel signs
# its majority 'HARRELL, Senior Judge:' and its dissent 'McCOY, J.
# (dissenting):'), so BOTH are declared: `prose` with the military titles,
# and `also_abbrev` with 'J.' mapped to Judge rather than Justice.
register(CourtProfile(
    "nmcca",
    "United States Navy-Marine Corps Court of Criminal Appeals",
    # NO DocStyle is registered for this contract: `styles` names ids in
    # core's style registry, and a court file may not add to it. The
    # contract's name travels in `criteria.headmatter_style` instead.
    byline=BylineGrammar(
        style="prose",
        titles=("Judge", "Chief Judge", "Senior Judge",
                "Appellate Military Judge"),
        also_abbrev=True,
        abbrev_titles=(("J.", "Judge"), *DEFAULT_ABBREV)),
    # The body opens its paragraphs 18pt in from the measure's rail (108 ->
    # 126 on the 504 template, 126 -> 144 nowhere else), and sets its
    # block quotations at 144. Twice this value must fall between the two,
    # so 14.0: at the 12.0 default the quotation fence is 24pt and every
    # ordinary paragraph opener sits inside it.
    para_indent_min=14.0,
    rollout="migrated",
))


@decider("headmatter.read", court="nmcca")
def read_headmatter_nmcca(model, geom, **_):
    """Read the fenced centred stack of a Navy-Marine Corps CCA slip, or
    NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 108.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    width = model.pages[0].width
    axis = width / 2

    # ---- the rows this block may contain --------------------------------
    # Furniture (the continuation sheets' two-row running head) and the
    # footnote zone (below the court's own 144pt separator rect) are neither
    # claimed nor consumed: core has already routed both, and a reader that
    # took them would print them twice.
    rows: list[list] = []
    for pm in model.pages[:_MAX_PAGES]:
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
        rows.extend(groups[k] for k in order)
    if len(rows) < 10:
        return NOTHING
    txt = [_norm(" ".join(l.plain for l in g)) for g in rows]

    def _mid(i: int) -> float:
        g = rows[i]
        return (min(l.x0 for l in g) + max(l.x1 for l in g)) / 2

    def _centred(i: int) -> bool:
        return abs(_mid(i) - axis) <= _CENTRED_TOL

    # ---- the dispatch: the first FENCE PAIR on page 1 -------------------
    fences = [i for i in range(len(rows))
              if _FENCE_TEXT.match(txt[i].replace(" ", ""))
              and abs(_mid(i) - axis) <= _AXIS_TOL]
    p1 = [i for i in fences if rows[i][0].page == 1]
    if len(p1) < 2:
        return NOTHING
    top_fence, cap_fence = p1[0], p1[1]
    # …with the court's bench designation above it and the docket
    # immediately below the caption, both required.
    if not any(_BENCH.match(txt[i]) for i in range(top_fence)):
        return NOTHING
    if not _DOCKET.match(txt[cap_fence - 1]):
        return NOTHING
    # THE FOOT: the first byline. A claim of unknown extent is worse than
    # none, so a record whose paper we cannot see the end of is declined.
    stop = _first_byline(txt, rows, body_x0)
    if stop is None or stop <= cap_fence:
        return NOTHING

    kinds: list[str | None] = [None] * len(rows)
    for i in fences:
        if i < stop:
            kinds[i] = "#fence"
    # THE RUNNING HEAD, WHERE REPETITION CANNOT SEE IT. Core identifies
    # furniture by recurrence, and on a 2-page slip — 13 of the 32 records —
    # this court's head prints exactly ONCE, below the >=2-sheet floor. It
    # is set at BODY size besides, so neither the small-type head band nor
    # the size test reaches it, and the block runs THROUGH it whenever the
    # appearances spill onto page 2: left unclaimed it read as one more
    # centred appearance row on 13 records.
    #
    # So the reader identifies it by the DOCUMENT'S OWN DOCKET, which it has
    # just read off the caption. MEASURED over all 190 continuation sheets
    # in the corpus, without a single exception: exactly TWO rows in the top
    # band, the first carrying this case's docket ('United States v.
    # Anderson, NMCCA No. 202600020') and the second naming the writing
    # ('Opinion of the Court', 'McCoy, J. (dissenting)', 'Modified Entry of
    # Judgment'), at tops 38.8-40.3 and 51.8-55.4 against a first body row
    # never higher than 73.8 — an 18.4pt stand-off that no row in the corpus
    # falls inside. The anchor is the docket and the band is measured, so
    # neither the head's wording nor a margin constant decides anything.
    # The band is the whole test, because core may already have taken the
    # head's FIRST row and left the second: the first row's digit-stripped
    # key ('United States v. Williams, NMCCA No.') recurs and clears the
    # floor, while 'Opinion of the Court' does not once a record appends a
    # Modified Entry of Judgment under a head of its own (williams pages
    # 5-6). An anchor on the docket would then have nothing to anchor to.
    for i in range(stop):
        if kinds[i] is not None or rows[i][0].page == 1:
            continue
        if rows[i][0].top < model.pages[rows[i][0].page - 1].height * _HEAD_BAND:
            kinds[i] = "#head"

    # ---- above the first fence: the notice, then the bench --------------
    for i in range(top_fence):
        if _NOTICE.match(txt[i]):
            kinds[i] = "#notice"
        elif _BEFORE.match(txt[i]) or _BENCH.match(txt[i]):
            kinds[i] = "panel"
    # The roster stands between 'Before' and the bench designation, and it
    # is the only thing that ever does.
    _before = next((i for i in range(top_fence) if _BEFORE.match(txt[i])), None)
    _bench = next((i for i in range(top_fence) if _BENCH.match(txt[i])), None)
    if _before is not None and _bench is not None:
        for i in range(_before + 1, _bench):
            if kinds[i] is None:
                kinds[i] = "panel"

    # ---- inside the sandwich: the caption, weight and slope ------------
    for i in range(top_fence + 1, cap_fence):
        kinds[i] = "docket" if _DOCKET.match(txt[i]) else "caption"

    # ---- below the sandwich: the ladder, each run bounded by its own ----
    state: str | None = None
    rail: float | None = None
    for i in range(cap_fence + 1, stop):
        if kinds[i] is not None:
            # A FENCE OR A RUNNING HEAD ENDS THE RUN IT INTERRUPTS. The
            # fence is a section boundary by construction; the head is a
            # page turn, and an appearance block that resumes below it opens
            # with its own label (porter, mendoza, rodriguezdejesus all set
            # 'For Appellee:' as the first row of page 2).
            state = None
            continue
        t = txt[i]
        if _DATE.match(t):
            kinds[i], state = "date", None
        elif _ORIGIN.match(t):
            kinds[i], state = "origin", "origin"
        elif _MILJUDGE.match(t):
            kinds[i], state = "judge-label", "judges"
        elif _RECITAL.match(t):
            kinds[i], state, rail = "case-info", "recital", rows[i][0].x0
        elif _FOR.match(t):
            kinds[i], state = "counsel", "counsel"
        elif _ATTRIB.search(t):
            kinds[i], state, rail = "panel", "attrib", rows[i][0].x0
        elif _PUBSTMT.match(t):
            kinds[i], state = "publication", "pub"
        elif _CORRECTION.match(t):
            kinds[i], state = "#notice", "correction"
        # ---- continuations, each ended by the run's own bound ----------
        elif state == "origin" and _centred(i) and all(
                l.all_emphasized for l in rows[i]):
            # THE POSTURE RECITAL, set ITALIC under the origin and centred
            # on the axis: 'upon further review following remand from / the
            # United States Court of Appeals for the Armed Forces'. Slope
            # bounds the run — the origin itself is roman, the row that
            # normally follows it labels itself ('Military Judge:'), and the
            # only other italic rows in the ladder are the appearances,
            # which their own label opens. The wrap carries no landmark of
            # its own, so no wording test may close the run.
            kinds[i] = "posture"
        elif state == "judges" and _centred(i) and ":" not in t:
            kinds[i] = "judge"
        elif state == "recital" and rail is not None \
                and abs(rows[i][0].x0 - rail) <= 1.5:
            kinds[i] = "case-info"
        elif state == "counsel" and _centred(i):
            kinds[i] = "counsel"
        elif state == "attrib" and rail is not None \
                and abs(rows[i][0].x0 - rail) <= 18.5:
            kinds[i] = "panel"
            if t.endswith("."):
                state = None
        elif state == "pub" and _centred(i) \
                and all(l.all_emphasized for l in rows[i]):
            kinds[i] = "publication"
            if t.rstrip("]").endswith("."):
                state = None
        elif state == "correction" and _centred(i):
            kinds[i] = "#notice"
            if t.endswith("."):
                state = None
        else:
            state = None

    # ---- emit ----------------------------------------------------------
    ctx = _Ctx()
    counsel: list[str] = []
    caption_rows: list[str] = []
    lower: list[str] = []
    judges: list[str] = []
    history: list[str] = []
    dockets: list[str] = []
    suffixes: list[str] = []
    for i in range(stop):
        kind = kinds[i]
        if kind is None:
            continue
        pieces = rows[i]
        if kind == "#fence":
            ctx.rule(pieces)
            continue
        if kind == "#notice":
            ctx.drop(pieces, "notice")
            continue
        if kind == "#head":
            ctx.drop(pieces, "running-head")
            continue
        if kind == "panel":
            ctx.emit(pieces, "panel", centre=_centred(i))
            continue
        if kind == "caption":
            caption_rows.append(txt[i])
            ctx.emit(pieces, "caption", centre=True)
            continue
        if kind == "docket":
            got = _DOCKET.match(txt[i])
            dockets.append(got.group(1))
            if got.group(2):
                suffixes.append(_norm(txt[i][3:]))
            ctx.emit(pieces, "docket", centre=True)
            continue
        if kind == "date":
            ctx.crit.setdefault("decision_date", _norm(_DATE.match(txt[i]).group(1)))
            ctx.emit(pieces, "date", centre=True)
            continue
        if kind in ("origin", "posture", "judge-label", "judge"):
            # FOUR THINGS SHARE ONE ROLE AND NOT ONE MEANING. The origin is
            # the court below; the posture run is this case's own appellate
            # history; the label is apparatus; the names are who tried it.
            # They render alike because the page sets them alike, and they
            # are kept apart in criteria because they are different facts —
            # read as one, suarez filed 'the United States Court of Appeals
            # for the Armed Forces' as a military TRIAL judge.
            if kind == "origin":
                lower.append(txt[i])
            elif kind == "posture":
                history.append(txt[i])
            elif kind == "judge":
                judges.append(txt[i])
            ctx.emit(pieces, "lower-court", centre=_centred(i))
            continue
        if kind == "case-info":
            history.append(txt[i])
            ctx.emit(pieces, "case-info", centre=False)
            continue
        if kind == "counsel":
            counsel.append(txt[i])
            ctx.emit(pieces, "counsel", centre=True)
            continue
        if kind == "publication":
            ctx.emit(pieces, "publication", centre=True)
            continue

    # ---- criteria, populated BEFORE anything is gated on them ----------
    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        extra = dockets[1:] + suffixes
        if extra:
            ctx.crit.setdefault("other_dockets", extra)
    if lower:
        # 'Appeal from the United States Navy-Marine Corps Trial Judiciary'
        # — the court below, as the origin row states it.
        ctx.crit.setdefault("lower_court", lower[0])
    if judges:
        ctx.crit.setdefault("lower_court_judge", "; ".join(judges))
    if history:
        ctx.crit.setdefault("history", " ".join(history)[:2000])
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    sides = _sides(txt, rows, top_fence + 1, cap_fence)
    if sides:
        ctx.crit.setdefault("parties", sides)
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    # THE PANEL: the roster row as printed, and the surnames it names. The
    # bench designation and the attribution recital are panel rows too, but
    # only the ROSTER carries the membership.
    roster = _roster(txt, kinds, top_fence)
    if roster is not None:
        ctx.crit.setdefault("panel_line", txt[roster])
        names = _panel_names(txt[roster])
        if names:
            ctx.crit.setdefault("panel", names)
        # `judges` is the ROSTER AS PRINTED, which is core's own convention
        # for it (`resolve/headmatter.py`: raw string to `judges`, split
        # names to `panel`) — here the roster row and the bench designation
        # under it, and nothing else. The attribution recital and the bare
        # 'Before' are apparatus and belong to neither.
        bench = next((txt[i] for i in range(top_fence)
                      if _BENCH.match(txt[i])), "")
        ctx.crit.setdefault("judges", _norm(txt[roster] + " " + bench))
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE; its text is copied
    # into criteria.attorneys, which core fills only from a MOVED block
    # (core-patch-queue item 41).
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    # WHAT THE PAPER IS. Both publication wordings say the same thing: the
    # opinion is not binding precedent. There is no published twin in this
    # corpus and none is assumed — the status is stated only where the
    # statement stands.
    if any(k == "publication" for k in kinds[:stop]):
        ctx.crit.setdefault("publication_status", "unpublished")
    ctx.crit.setdefault("headmatter_style", STYLE_FENCED)
    return ctx.result()


def _footnote_cut(pm, body_x0: float) -> float | None:
    """The top of this page's footnote zone: the court draws its separator
    as a RECT two inches wide at the page's left text rail. Invariant on
    all 200 occurrences in the corpus."""
    tops = [r.top for r in pm.h_rules
            if r.source == "rect"
            and _SEP_WIDTH[0] <= r.width <= _SEP_WIDTH[1]
            and abs(r.x0 - body_x0) <= 24.0
            and r.top > pm.height * 0.30]
    return min(tops) if tops else None


def _first_byline(txt: list[str], rows: list, body_x0: float) -> int | None:
    """The row where the paper begins signing. Bounded by this court's own
    forms — the spelled title, the abbreviated 'J.' with a parenthesized
    kind, and 'PER CURIAM' — each set at the body rail. `Military Judge:`
    and `For Appellant:` share the colon terminal and neither carries a
    surname before it, so neither can match."""
    for i, t in enumerate(txt):
        if not _BYLINE.match(t):
            continue
        if rows[i][0].x0 - body_x0 > 24.0:
            continue
        return i
    return None


# The court's signing forms. `de` is admitted as a nobiliary particle
# because two of this court's judges sign 'de GROOT, Judge:' — see the
# core defect reported with this port (core's own byline grammar cannot
# read the particle, so fisk's majority and cardoso's concurrence come
# back unsigned until that patch lands).
_BYLINE = re.compile(
    r"^(?:PER CURIAM\b"
    r"|(?:de |van |von |da |del )?[A-Z][A-Za-z'’\-]+,\s*"
    r"(?:Chief |Senior |Acting )?(?:Judge|J\.)\b)")


def _sides(txt: list[str], rows: list, lo: int, hi: int) -> list[str]:
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


def _roster(txt: list[str], kinds: list, top_fence: int) -> int | None:
    """The roster row: the panel row above the first fence that is neither
    'Before' nor the bench designation."""
    for i in range(top_fence):
        if kinds[i] == "panel" and not _BEFORE.match(txt[i]) \
                and not _BENCH.match(txt[i]):
            return i
    return None


def _panel_names(line: str) -> list[str]:
    """'DALY, GROSS, and de GROOT' -> three names. The particle stays with
    its surname; the connector is not a name."""
    out = []
    for piece in re.split(r",|\band\b", line):
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

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
