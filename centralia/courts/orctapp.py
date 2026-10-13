"""Oregon Court of Appeals ('orctapp').

Everything unique to orctapp lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — orctapp is not a slip opinion either. All 42 records are pages
of the OREGON REPORTS ADVANCE SHEETS, the same bound half-measure volume its
Supreme Court is printed in (see or.py, which reads the same paper for a
different court and shares nothing with this file but the physics):

    ┌──────────────────────────────────────────────────────────────────┐
    │ No. 398          May 13, 2026                409  the page head  │
    ├────────────────── DRAWN RULE, top 49.1 ──────────────────────────┤
    │              IN THE COURT OF APPEALS OF THE      the masthead    │
    │                   STATE OF OREGON                                │
    │                                                                  │
    │                  CITY OF EUGENE,                                 │
    │                Plaintiff-Respondent,             the caption,    │
    │                        v.                        centred on the  │
    │              Hamid Michael HEJAZI,               block's own     │
    │               Defendant-Appellant.               axis            │
    │              Lane County Circuit Court                           │
    │               24CR16542, 24CR57085;              the numbers     │
    │      A184491 (Control), A184509, A186553         below, then this│
    │                                                  court's own     │
    │   Jay A. McAlpin, Judge.                         the judge below │
    │   Argued and submitted April 15, 2026.           the dates       │
    │   Kyle Krohn, Deputy Public Defender, argued the cause for       │
    │ appellant. …                                     counsel         │
    │   Before Tookey, Presiding Judge, Kamins, Judge, and             │
    │ Jacquot, Judge.                                  who sat         │
    │   TOOKEY, P. J.                                  the writing     │
    └──────────────────────────────────────────────────────────────────┘

---- orctapp's declared facts (measured over all 42 records) ---------------

THE DRAWN RULE IS THE PAGE'S OWN MEASURE, and it is the only reliable way to
find the axis. Measured over EVERY page of every record: 342 rules on 342
pages, all at top 49.1, all 301.5pt wide, x0 alternating 49.5 and 45.0 as the
binding margin changes side each leaf. No page lacks it. So each page's own
rule states its RAIL (the rule's x0), its AXIS (x0 + 150.75) and the foot of
its PAGE HEAD (everything above it). Page width / 2 is the WRONG axis on this
paper — the type block is offset by the binding margin — and used as one it
reads every caption row as an indent; and a rail read off page 1 and applied
to page 2 is 4.5pt wrong, which is a third of the ladder's own indent.

CENTRED IS A MEASURED FACT AND IT DELIMITS THE CAPTION, with the same catch
or.py records: a JUSTIFIED WRAP fills the measure exactly, so its mid-point
sits on the axis too and width is what separates them. The caption band is
therefore the maximal run of rows within ±4pt of the axis AND under 295pt
wide, opening at the masthead; nothing below that run is read as caption.

THE NUMBERS COME IN TWO SERIES ON ONE ROW. This court's own docket is an
A-number, and the reporter prints the court below's number first, separated
by a semicolon: '24JU05821; A188495 (Control), A188260'. Read as one field
the trial number displaced the appellate one, so the semicolon splits them —
the A-numbers are `docket_number` plus `other_dockets`, and what stands
before the semicolon is `lower_court_docket`. '(Control)' marks the lead
appeal and is kept with the number it labels.

…EXCEPT WHERE THEY DO NOT FIT ON ONE. Three records wrap the two series over
two rows, the first closing on the reporter's own semicolon ('24CR16542,
24CR57085;' over 'A184491 (Control), A184509, A186553' on hejazi; dean and
klaus the same way). Read as separate rows the opener is not numbers at all
by the A-number test, and it was filed as a PARTY: 'CITY OF EUGENE v. Hamid
Michael HEJAZI v. 24CR16542, 24CR57085;', with the trial numbers lost. The
semicolon is what joins them.

THE ORIGIN IS WHERE IT STANDS, NOT WHAT IT SAYS. The court, board or agency
the case came from is the caption row directly above the numbers — unless
that row is a party label or the pivot, which is how lorengel says it came
from no court at all. Named instead by a VOCABULARY of tribunals it took
party names with it on 9 of the 42 records: 'DEPARTMENT OF HUMAN SERVICES,'
on the seven dependency appeals, 'BOARD OF PAROLE AND POST-PRISON
SUPERVISION,' on lorengel, 'and Department of Forestry,' on jewel — each of
them a party to the case, each tinted `lower-court` in the block and locked
into `criteria.lower_court` ahead of the real origin printed two rows below
it. Position also reads the origin the vocabulary could not: on
dept._of_human_services_v._c._a._w. the reporter set 'Columbia County
Circuit' and left the word 'Court' off.

A PARTY IS A GROUP OF ROWS, NOT A ROW. The reporter sets the party's name,
then its office and institution beneath it, then the label ('Corey FHUERE,' /
'Superintendent,' / 'Oregon State Penitentiary,' / 'Defendant-Respondent.')
— one party, four rows — and the label, the pivot and the connector each
close the group, as or.py reads the same volume. Listed row by row instead,
`criteria.parties` reported 'a Child.', 'and', 'fka Emma J. Berry' and
'Superintendent' as parties of the case.

THE LADDER IS READ RUNG BY RUNG, each by its own landmark, because their
order is not stable — 'Before …' prints below the counsel on this court's
records, where its Supreme Court prints 'En Banc' above the origin:

  lower-judge  'Jay A. McAlpin, Judge.' — a short rung closing on the title,
               spelled out. It is the judge BELOW, so it is `lower-court`: a
               `panel` tint here would say this court sat as one judge.
  date         'Argued and submitted April 15, 2026.' -> `submitted`
  panel        'Before Tookey, Presiding Judge, …' -> `judges` + `panel`
  posture      'On respondents’ petition for reconsideration filed May 13,
               2026. …' — how the case got back here, which is
               `procedural-history` and not a court below (dean)
  counsel      everything else in the ladder, which the reporter sets as
               PROSE paragraphs inside the block rather than as a roster

AND A RUNG IS NAMED BY ITS OPENER ALONE. The ladder is TWO POSITIONS and
nothing else — measured over all 42 records, 248 rows stand at rail + 15.0
and 198 at rail + 0.0, with no third position anywhere in the corpus — so an
opener is 15pt in, a wrap is at the rail, and the role decided from the
opener is never revised, because a wrap says nothing about what its rung is.
Given a landmark of its own a wrap claimed two rungs it had no part in:
'argued the case for respondents. Also on the brief were Dan' opened a `date`
on jewel, the date vocabulary having matched 'argued' in the middle of a
counsel sentence, and 'filed the brief for respondent Department of Human
Services.' opened a `lower-court` on dept._of_human_services_v._c._a._w. and
put itself into `criteria.history` as the court the case came from.

THE PAGE HEAD IS THE REPORTER'S, NOT THE COURT'S, ON EVERY PAGE. On page 1
it is a folio, the FILING DATE and the advance sheet's own serial ('No. 398'),
three pieces on one printed row above the rule; from page 2 on it is the
running head. Core knows the folio and cannot know the rest, which is content
by every test it has, and the running head has to REPEAT before the furniture
pass will key it — which this one does not do in ONE form: the rectos carry
the cite and the versos the short case name, with the author's own row
between them on a published opinion, so a 4-page record prints each form
once. Read only over the three pages this reader walks, and dropped only on
page 1, the head stood in the OPINION BODY on 17 of the 42 records: 'State v.
Lonergan the property, including by sorting through any recyclable …', 'Cite
as 352 Or App 7 (2026) of Aranda, the state concedes …'. The rule the page
draws says exactly where the head ends, so it is taken on every page, dropped
as the head it is where core has not already dropped it, and the filing date
harvested into `criteria.decision_date`.

THE CITE AND THE SHORT NAME COME OUT OF THE RUNNING HEAD, the only place the
volume prints them — rectos read 'Cite as 349 Or App 409 (2026)' where the
opinion is published and 'Nonprecedential Memo Op: 352 Or App 84 (2026)'
where it is not, versos 'City of Eugene v. Hejazi'. Both are furniture and
neither gets a row, but '349 Or App 409' is Oregon's public-domain citation
for this court and goes to `criteria.citation`, the short form to
`criteria.short_case_name`. THE SHORT NAME IS THE PIECE AT THE RIGHT MARGIN
that is not a folio: a verso head is three pieces on a published opinion —
the folio at the rail, the AUTHOR in the middle and the short name flush
right ('2' / 'EGAN, J.' / 'State v. Gudino-Macias') — so the first non-folio
piece is the author's name, not the case's. Naming the piece by a ' v. ' in
it instead missed the ones that carry none ('Kagel and Berry', 'Fial and
Fial').

THE BYLINE ENDS THE READER. It is set in the abbreviated form the profile
declares ('EGAN, J.', 'AOYAGI, P. J.', 'LAGESEN, C. J.', 'WALTERS, S. J.',
'PER CURIAM'), and 37 records sign on page 1 against 3 on page 2, so the walk
is bounded at three pages. Nothing at or below the byline is claimed — that
row is the anchor core opens the writing on. The grammar has to be UNICODE
and it has to know the SENIOR JUDGE: 'PAGÁN, J.' is as much a surname in caps
as 'TOOKEY' is, and an ASCII character class threw it out along with
'WALTERS, S. J.'. Both walks then ran past the signature onto page 2, swept
its running head into the counsel block, left no disposition statement, and
cost the record its writing — santoro and state_v._pleasure both typed
`order` with no author. The profile's own abbreviations carry 'S. J.' for the
same reason, and they say Judge where the default says Justice: this court
sits Judges, and its Supreme Court on the other half of the volume sits
Justices.

THE 8pt APPARATUS IS CORE'S. Under the ladder the reporter types a rule 58.5pt
wide (22 of them across the corpus) and sets the origin's detail beneath it in
8pt. That is a footnote, it lives in core's footnote zone, and the zone is
subtracted from the stream before this reader runs.

THE CRITERIA FIELD NAMES ARE THE MODEL'S — `docket_number` plus
`other_dockets`, the numbers from below in `lower_court_docket`, an argued
date in `submitted`. Written under any other name they are attached by
setattr and never serialized: read as read, reported as nothing.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

STYLE = "advance sheet"

# ---------------------------------------------------------------------------
# The paper, measured over all 42 records of /assets/orctapp.
# ---------------------------------------------------------------------------
# EVERY PAGE DRAWS THE RULE: 342 pages of 342, top 49.1 on the nose, every
# one 301.5pt wide, x0 alternating 49.5 and 45.0 as the binding margin
# changes side each leaf. No page without one, so the frame below is a
# measured fact of the page and never an inference from the type.
_RULE_TOP = 49.1
_RULE_TOP_TOL = 2.5
_MEASURE = 301.5
_AXIS_FROM_RAIL = _MEASURE / 2          # 150.75
_AXIS_TOL = 4.0
# A justified wrap is the measure on the nose and shares the axis; a genuinely
# centred row never fills it.
_CENTRED_WIDTH_MAX = 295.0
# THE LADDER IS TWO POSITIONS AND NOTHING ELSE. Measured over all 42 records:
# 248 rows stand at rail + 15.0 and 198 at rail + 0.0, and there is no third
# position anywhere in the corpus. So an opener is 15pt in, a wrap is at the
# rail, and half of 15 separates them with room to spare either way.
_INDENT = 15.0
# THE DISPOSITION STATEMENT'S OWN INDENT. Below the byline the reporter sets
# one short statement of what the court did, opening 15pt in from the page's
# rail and wrapping back to it — the same ladder fact, and the same 15pt
# or.py measured on the Supreme Court's half of the very same volume.
_SUMMARY_INDENT = _INDENT
# The paper is 11pt (2,288 rows). The reporter's apparatus is 8pt (84) and its
# block quotations 10pt (42); nothing the block prints is under 11pt.
_BODY_SIZE_MIN = 10.5
# 37 records sign on page 1, 3 on page 2.
_MAX_PAGES = 3

_MASTHEAD_1 = re.compile(r"^IN THE COURT OF APPEALS OF THE$", re.I)
_MASTHEAD_2 = re.compile(r"^STATE OF OREGON$", re.I)

_HEAD_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+\d{4}$")
# THE HEAD'S OWN CITE, printed on the rectos from page 2 on. A published
# opinion heads them 'Cite as 349 Or App 409 (2026)'; a nonprecedential
# memorandum heads them 'Nonprecedential Memo Op: 352 Or App 84 (2026)', and
# read only in the first form the memoranda kept no citation at all.
_CITE_AS = re.compile(
    r"^(?:Cite as|Nonprecedential Memo Op:)\s+(\d+\s+Or\s+App\s+\d+)"
    r"\s*\(\d{4}\)\.?$", re.I)
# The folio, which is the one head piece core already knows.
# The folio, which is the one head piece core already knows. Some pages set
# it with a space inside it ('6 92', '62 4'), which is one number and not two.
_FOLIO = re.compile(r"^\d[\d\s]{0,4}$")
# …and where the short name is long enough to fill the measure the folio
# shares its row: '726 Santoro v. Eagle Crest Estate Homesite Owners Assn.'
_FOLIO_PREFIX = re.compile(r"^\d{1,4}\s+(?=\D)")
# The advance sheet's own serial for this opinion, on page 1 only. Not a
# docket, and there is no criteria field for it; it is dropped as the head
# piece it is.
_HEAD_SERIAL = re.compile(r"^No\.\s*\d+$", re.I)

# A CASE NUMBER: this court's own A-number, or the number a court below gave
# the case — '24CR16542', 'C101495DRD', '25CC04070', '2201795', '24JU05821'.
# One token, no spaces, at least one digit, and '(Control)' where the
# reporter marks the lead appeal.
_CASE_NUMBER = re.compile(r"^[A-Za-z0-9]*\d[A-Za-z0-9]*"
                          r"(?:\s*\(Control\))?$")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_CONNECTOR = re.compile(r"^and$", re.I)
# A FURTHER PARTY, joined to the one above by the reporter's 'and'.
_ALSO_PARTY = re.compile(r"^and\s+\S", re.I)
# The party's position, printed on its own row under the name. A closed set:
# this is every label the 42 records print.
_PARTY_WORD = (r"Plaintiffs?|Defendants?|Petitioners?|Respondents?"
               r"|Appellants?|Appellees?|Relators?|Movants?|Intervenors?"
               r"|Claimants?|Adverse\s+Party")
_PARTY_STATUS = re.compile(
    rf"^(?:(?:{_PARTY_WORD})|Third-Party\s+(?:{_PARTY_WORD}))"
    rf"(?:\s*-\s*(?:{_PARTY_WORD}))?\s*[,.;]?$", re.I)
# The judge BELOW: a short row that closes on the title, spelled out.
_LOWER_JUDGE = re.compile(
    r",\s*(?:Judge|Senior Judge|Judge pro tempore|Magistrate"
    r"|Administrative Law Judge)\.", re.I)
_DATES = re.compile(
    r"^(?:Argued and submitted|Submitted|Argued|Resubmitted|On the record"
    r"|On record|Reargued)\b", re.I)
# THE DATED POSTURE, which this court prints where it reconsiders its own
# decision: 'On respondents’ petition for reconsideration filed May 13, 2026.
# Precedential opinion filed April 29, 2026. Dean v. Multnomah County, 349 Or
# App 10, 590 P3d 546.' No counsel rung in the corpus opens with 'On'.
_POSTURE = re.compile(r"^On\b", re.I)
_PANEL = re.compile(r"^Before\b|^En Banc\b", re.I)
_BENCH_WORD = re.compile(
    r"^(?:Chief\s+)?(?:Judges?|Justices?)$|^Senior\s+Judges?$"
    r"|^Presiding\s+Judges?$|^Judges?\s+pro\s+tempore$|^pro\s+tempore$",
    re.I)
# THE BYLINE IS THE SURNAME IN CAPS OVER AN ABBREVIATED TITLE, and the
# profile's grammar is not a fine enough sieve for this page: 'Rebecca D.
# Guptill, Judge.' — the judge BELOW, printed two rungs above — parses as a
# byline under it, so the walk ended on the trial judge and read her as the
# author of the opinion (leckenby), while the rungs left behind became a
# phantom `order` writing on 10 records. The reporter sets the author's
# surname in caps over an abbreviated title and the judge below in mixed case
# over a spelled one; CASE is the difference, and the case test has to be
# UNICODE — 'PAGÁN, J.' is as much a surname in caps as 'TOOKEY' is, and an
# ASCII class threw it out along with 'WALTERS, S. J.', whose Senior-Judge
# title the abbreviations did not list. Both walks then ran past the
# signature into page 2, swept its running head into the counsel block, left
# no disposition statement, and cost the record its writing: santoro and
# state_v._pleasure both typed `order` with no author.
_BYLINE = re.compile(
    r"^(?P<name>[^\d,]{2,30}),\s*"
    r"(?:C\.\s*J\.|P\.\s*J\.|S\.\s*J\.|V\.\s*C\.\s*J\.|J\.|JJ\.)$")
_PER_CURIAM = re.compile(r"^PER CURIAM\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_byline(text: str) -> bool:
    """The author's row: a surname with no lower case, over an abbreviation."""
    if _PER_CURIAM.match(text):
        return True
    hit = _BYLINE.match(text)
    if not hit:
        return False
    name = hit.group("name")
    return bool(name.strip()) and not any(c.islower() for c in name)


def _head_rule(pm):
    """The rule this page draws under its head, or None."""
    for rule in sorted(getattr(pm, "h_rules", []), key=lambda r: r.top):
        if abs(rule.top - _RULE_TOP) <= _RULE_TOP_TOL \
                and abs((rule.x1 - rule.x0) - _MEASURE) <= 6.0:
            return rule
    return None


@decider("headmatter.read", court="orctapp")
def read_headmatter_orctapp(model, geom, **_):
    """Read the advance sheet's block for this court, or NOTHING."""
    if not model.pages:
        return NOTHING

    # THE RULE STATES THE RAIL AND THE AXIS, page by page — the binding
    # margin changes side each leaf, so a rail read off page 1 and applied to
    # page 2 is 4.5pt wrong, which is a third of the ladder's own indent.
    frames: dict[int, tuple[float, float, float]] = {}
    for pm in model.pages:
        rule = _head_rule(pm)
        if rule is not None:
            frames[pm.number] = (rule.x0, rule.x0 + _AXIS_FROM_RAIL, rule.top)
    if 1 not in frames:
        return NOTHING
    rail, axis, head_foot = frames[1]

    rows = _rows(model, _MAX_PAGES)
    if len(rows) < 6:
        return NOTHING
    # `_rows` deliberately keeps every printed line — this reader finds its
    # bearings from the drawn rule, not from core's furniture guess. It asks
    # core what the page's furniture is only to avoid reporting a removal
    # twice, and to bound the disposition statement by the foot of its page.
    finder = FurnitureFinder(model,
                             geom.body_x0 if geom and geom.body_x0 else rail,
                             geom.body_size if geom and geom.body_size
                             else _BODY_SIZE_MIN)
    ctx = _Ctx()

    # ---- the page head, above the rule, on EVERY page --------------------
    # THE PAGE HEAD IS THE REPORTER'S, NOT THE COURT'S, and it is above the
    # rule on all 342 pages, not just the three this reader walks. Left to
    # core it has to REPEAT to be keyed as furniture, and this head does not
    # repeat in one form: the rectos carry the cite and the versos the short
    # case name (with the author's own row between them on a published
    # opinion), so a 4-page record prints each form once. Seventeen of the 42
    # records had a head standing in the opinion body as a result — 'State v.
    # Lonergan the property, including by sorting through any recyclable …',
    # 'Cite as 352 Or App 7 (2026) of Aranda, the state concedes …'. The rule
    # the page draws says exactly where the head ends, so the head is taken
    # here and dropped as the head it is.
    #
    # ONLY WHAT THE READER CAN NAME. Standing above the rule is not on its own
    # enough, because a page's type does not always stay where the page put
    # it: pdfio's substitute-font pass lifts a displaced run to the nearest
    # row that has a hole for it, and on five pages it lifted the SECTION
    # HEADING into the head band — '666 The Parties’ Arguments' (jewel), '62 4
    # Danger to Self' (state_v._e._r.), '756 Warrant' (klaus). Swept up with
    # the head those headings would be removed from the record outright, so a
    # head-band row is claimed only when this reader can say which head piece
    # it is: the folio, the cite, page 1's filing date or serial, or the
    # short name at the right margin. Anything else above the rule is left
    # exactly where it was, for core to judge.
    for pm in model.pages:
        frame = frames.get(pm.number)
        if frame is None:
            continue
        _prail, _, foot = frame
        right = _prail + _MEASURE
        for line in sorted(pm.lines, key=lambda l: l.x0):
            if line.top >= foot or not line.plain.strip():
                continue
            one = _norm(line.plain)
            named = False
            if pm.number == 1 and _HEAD_DATE.match(one):
                ctx.crit.setdefault("decision_date", one)
                named = True
            elif pm.number == 1 and _HEAD_SERIAL.match(one):
                named = True
            elif _FOLIO.match(one):
                named = True
            elif _CITE_AS.match(one):
                ctx.crit.setdefault(
                    "citation", _norm(_CITE_AS.match(one).group(1)))
                named = True
            elif pm.number > 1 and abs(line.x1 - right) <= 4.0:
                # THE SHORT NAME IS THE PIECE AT THE RIGHT MARGIN. A verso
                # head is three pieces — the folio at the rail, the AUTHOR in
                # the middle and the short name flush right ('2' / 'EGAN, J.'
                # / 'State v. Gudino-Macias') — so taking the first non-folio
                # piece reads the author as the case. Naming the piece by a
                # ' v. ' in it misses the ones that carry none: 'Kagel and
                # Berry', 'Fial and Fial'. Where the name fills the measure
                # the folio has no gap to stand in and shares the row, so it
                # is taken off the front.
                ctx.crit.setdefault(
                    "short_case_name", _FOLIO_PREFIX.sub("", one))
                named = True
            if not named:
                continue
            # A ROW THE FURNITURE PASS ALREADY REMOVED IS NOT REMOVED TWICE.
            if not finder.kind(pm, line):
                ctx.dropped.append(m.Dropped(
                    text=one, prov=m.Prov(pm.number, (line.id,)),
                    kind="running-head"))
            ctx.consumed.add(line.id)

    def centred(pieces) -> bool:
        page = pieces[0].page
        _, page_axis, _ = frames.get(page, (rail, axis, head_foot))
        x0 = min(l.x0 for l in pieces)
        x1 = max(l.x1 for l in pieces)
        if abs((x0 + x1) / 2 - page_axis) > _AXIS_TOL:
            return False
        if (x1 - x0) <= _CENTRED_WIDTH_MAX:
            return True
        # A CENTRED ROW CAN FILL THE MEASURE. Width alone tells a centred row
        # from a justified wrap only while no caption row happens to be the
        # measure wide — and 'BOARD OF PAROLE AND POST-PRISON SUPERVISION,'
        # is 301.5pt on the nose, the measure exactly. Thrown out by width it
        # closed the caption band before the docket row and the whole claim
        # collapsed (lorengel returned NOTHING). The reporter sets party
        # names in CAPS and counsel in mixed case, so case decides where
        # width cannot.
        text = _norm(" ".join(l.plain for l in pieces))
        letters = [c for c in text if c.isalpha()]
        return bool(letters) and not any(c.islower() for c in letters)

    # THE DISPATCH: the two masthead rows, centred on the axis, below the
    # rule. Never an ordinal — the head above the rule is one printed row on
    # some records and two on others.
    mast = None
    for idx, group in enumerate(rows[:8]):
        text = _norm(" ".join(l.plain for l in group))
        if _MASTHEAD_1.match(text) and centred(sorted(group,
                                                      key=lambda l: l.x0)):
            nxt = _norm(" ".join(l.plain for l in rows[idx + 1])) \
                if idx + 1 < len(rows) else ""
            if _MASTHEAD_2.match(nxt):
                mast = idx
                break
    if mast is None:
        return NOTHING

    # ---- the nonprecedential notice, BELOW the rule and above the masthead
    # 10 of the 42 records print it, always three rows and always the same
    # sentence: 'This is a nonprecedential memorandum opinion pursuant to
    # ORAP 10.30 and may not be cited except as provided in ORAP 10.30(1).'
    # It stands between the page head and the masthead, so neither the head
    # loop nor the caption walk saw it — and left in the stream those three
    # rows opened a PHANTOM `order` writing whose author core then scavenged
    # from the trial judge's row ('Rebecca D. Guptill, Judge.' on leckenby).
    # It is the court saying whether this may be cited, which is what
    # `publication` is.
    notice = [g for g in rows[:mast]
              if g[0].page == 1 and g[0].top > head_foot]
    if notice:
        ctx.crit.setdefault("publication_status", "unpublished")
        for group in notice:
            ctx.emit(group, "publication")

    # ---- the walk, from the masthead down to the byline -------------------
    # THE BYLINE ENDS THE READER and is never claimed: that row is the anchor
    # core opens the writing on, and the only place this paper names the
    # author.
    walk: list[tuple[list, str]] = []
    signed_at: tuple[int, float] | None = None
    for group in rows[mast:]:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text or (pieces[0].size or 0.0) < _BODY_SIZE_MIN:
            continue
        if pieces[0].id in ctx.consumed:      # the page head, already taken
            continue
        if _is_byline(text):
            signed_at = (pieces[0].page, pieces[0].top)
            break
        walk.append((pieces, text))

    # THE CAPTION BAND IS ONE RUN AND NEVER RESUMES: the maximal run of rows
    # on the axis, opening at the masthead. A row off the axis, or too wide
    # for it, has left the caption for good.
    band = 0
    while band < len(walk) and centred(walk[band][0]):
        band += 1
    caption, ladder = walk[:band], walk[band:]

    _read_caption(ctx, caption)
    _read_ladder(ctx, caption, ladder, frames, rail)

    if not ctx.crit.get("docket_number"):
        return NOTHING

    # THE REPORTER'S DISPOSITION STATEMENT IS NOT THE OPINION. The byline
    # stands over a short statement of what the court did — 'Reversed.',
    # 'Vacated and remanded.', 'In Case No. 24CR16542, general judgment of
    # dismissal reversed and remanded. …' — and then the page ends and the
    # opinion PROPER opens on the next leaf. Read as the writing's opening it
    # made 40 of the 42 records begin with their own outcome. This is the
    # same fact or.py records for the Supreme Court's half of the same
    # advance-sheet volume, and the user asked for it here (2026-08-21).
    #
    # MEASURED over all 42: 39 sign, and the rows below the signature on its
    # own page number 1 on 32 records, 2 on 6 and 3 on 1 — never more. That
    # bound is tighter than or's 3-8 because this court states its outcome in
    # a sentence and its Supreme Court states it in a paragraph. Nothing
    # below the signature's own page is touched.
    #
    # THE SUMMARY IS A FLOW SECTION — `sections.py` declares it "flow", so it
    # carries PARAGRAPHS and not rows; HmLine rows put there take the
    # renderer down (`_render_blocks: HmLine`). The statement wraps, so it is
    # rebuilt on the reporter's own indent.
    if signed_at is not None:
        _pg, _top = signed_at
        _page = model.pages[_pg - 1]
        _tail = [l for l in sorted(_page.lines, key=lambda l: (l.top, l.x0))
                 if l.top > _top + 1.0 and l.plain.strip()
                 and l.id not in ctx.consumed
                 and not finder.kind(_page, l)
                 and not (l.size and l.size < _BODY_SIZE_MIN)]
        if _tail:
            _rail = min(l.x0 for l in _tail)
            _paras: list[list] = []
            for _line in _tail:
                if not _paras or _line.x0 > _rail + _SUMMARY_INDENT / 2:
                    _paras.append([_line])
                else:
                    _paras[-1].append(_line)
            for _run in _paras:
                ctx.summary.append(m.Paragraph(
                    text=" ".join(_norm(l.plain) for l in _run),
                    prov=m.Prov(_run[0].page, tuple(l.id for l in _run))))
                ctx.consumed.update(l.id for l in _run)
    ctx.crit["headmatter_style"] = STYLE
    return ctx.result()


# ---------------------------------------------------------------------------
# the caption band
# ---------------------------------------------------------------------------

def _read_caption(ctx, caption: list[tuple[list, str]]) -> None:
    """The masthead, the parties, the origin and the numbers.

    THE ORIGIN IS WHERE IT STANDS, NOT WHAT IT SAYS. The court, board or
    agency the case came from is the row directly above the numbers, and
    named instead by a vocabulary of tribunals it took party names with it on
    9 of the 42 records: 'DEPARTMENT OF HUMAN SERVICES,' on the seven
    dependency appeals, 'BOARD OF PAROLE AND POST-PRISON SUPERVISION,' on
    lorengel, 'and Department of Forestry,' on jewel — each of them a party
    to the case and each locked into `criteria.lower_court` ahead of the real
    origin printed two rows below it. Position also reads the origin the
    vocabulary could not: the reporter set 'Columbia County Circuit' on
    dept._of_human_services_v._c._a._w. and left the word 'Court' off.
    """
    blocks = _number_blocks(caption)
    in_block = {i for start, end in blocks for i in range(start, end)}
    origins = set()
    for start, _end in blocks:
        if start == 0:
            continue
        _pieces, above = caption[start - 1]
        if start - 1 in in_block or _PIVOT.match(above) \
                or _CONNECTOR.match(above) or _PARTY_STATUS.match(above):
            continue
        origins.add(start - 1)

    party_rows: list[str] = []
    party_buf: list[str] = []

    def flush() -> None:
        """A PARTY GROUP IS THE ROWS DOWN TO ITS LABEL. The reporter sets the
        party's name, then its office and institution beneath it, then the
        label ('Corey FHUERE,' / 'Superintendent,' / 'Oregon State
        Penitentiary,' / 'Defendant-Respondent.') — one party, four rows.
        Listed row by row instead, `parties` reported 'a Child.', 'and',
        'fka Emma J. Berry' and 'Superintendent' as parties of the case."""
        if party_buf:
            party_rows.append(_norm(" ".join(party_buf)).rstrip(",;"))
            party_buf.clear()

    for idx, (pieces, text) in enumerate(caption):
        if _MASTHEAD_1.match(text) or _MASTHEAD_2.match(text):
            ctx.crit.setdefault("court", "Court of Appeals of the State "
                                         "of Oregon")
            ctx.emit(pieces, "court")
            continue
        if idx in in_block:
            for start, end in blocks:
                if start == idx:
                    _read_numbers(ctx, " ".join(t for _p, t
                                                in caption[start:end]))
            ctx.emit(pieces, "docket")
            continue
        if idx in origins:
            flush()
            ctx.crit.setdefault("lower_court", text.rstrip(",;"))
            ctx.below.append(text)
            ctx.emit(pieces, "lower-court")
            continue
        if _PIVOT.match(text) or _PARTY_STATUS.match(text) \
                or _CONNECTOR.match(text):
            flush()
            ctx.emit(pieces, "caption")
            continue
        if _ALSO_PARTY.match(text):
            flush()
        party_buf.append(text)
        # A ROW THAT ENDS ITS OWN SENTENCE closes the group: 'In the Matter
        # of C. V.,' / 'a Child.' is the child's case, and the agency named
        # beneath it is a different party. So does the reporter's own
        # SEMICOLON, which is how it separates co-defendants sharing one
        # label: 'Kacey KC,' / 'Oregon State Forester;' / 'Mike Wilson, State
        # Forest Division Chief;' / 'and Department of Forestry,' /
        # 'Defendants-Respondents.' is three parties, not one.
        if text.endswith(".") or text.endswith(";"):
            flush()
        ctx.emit(pieces, "caption")
    flush()
    if party_rows:
        ctx.crit.setdefault("parties", party_rows[:8])


def _number_blocks(caption: list[tuple[list, str]]) -> list[tuple[int, int]]:
    """The runs of rows that carry case numbers and nothing else.

    THE NUMBERS COME IN TWO SERIES ON ONE ROW — the court below's first, then
    a semicolon, then this court's A-numbers — EXCEPT where they do not fit
    on one. Three records wrap them ('24CR16542, 24CR57085;' over 'A184491
    (Control), A184509, A186553' on hejazi, and dean and klaus the same way),
    and read as separate rows the first was filed as a PARTY: 'CITY OF EUGENE
    v. Hamid Michael HEJAZI v. 24CR16542, 24CR57085;'. The row that opens the
    wrap closes on the reporter's own semicolon, which is what joins them.
    """
    out: list[tuple[int, int]] = []
    idx = 0
    while idx < len(caption):
        if not _numbers_row(caption[idx][1]):
            idx += 1
            continue
        end = idx + 1
        while end < len(caption) and caption[end - 1][1].rstrip().endswith(";") \
                and _numbers_row(caption[end][1]):
            end += 1
        out.append((idx, end))
        idx = end
    return out


def _numbers_row(text: str) -> bool:
    """Is this centred row case numbers and nothing else?"""
    tokens = [t.strip(" .") for t in re.split(r"[;,]", text) if t.strip(" .")]
    return bool(tokens) and all(_CASE_NUMBER.match(t) for t in tokens)


def _read_numbers(ctx, text: str) -> None:
    """'24JU05821; A188495 (Control), A188260' — the trial number, then this
    court's. Read as one field the trial number displaced the appeal."""
    lower, sep, appellate = _norm(text).rpartition(";")
    if not sep:
        lower, appellate = "", text
    a_nums = [t.strip(" .") for t in appellate.split(",") if t.strip(" .")]
    if a_nums:
        if not ctx.crit.get("docket_number"):
            ctx.crit["docket_number"] = a_nums[0]
            if a_nums[1:]:
                ctx.crit["other_dockets"] = a_nums[1:]
        else:
            ctx.crit.setdefault("other_dockets", []).extend(a_nums)
    for one in (t.strip(" .") for t in lower.split(",") if t.strip(" .")):
        ctx.crit.setdefault("lower_court_docket", []).append(one)


# ---------------------------------------------------------------------------
# the ladder
# ---------------------------------------------------------------------------

def _read_ladder(ctx, caption, ladder, frames, rail) -> None:
    """The rungs below the caption, each read from its OPENER alone.

    A RUNG OPENS ON THE 15pt INDENT AND CONTINUES AT THE RAIL, and its role
    is decided from the opener and never revised — because a wrap says
    nothing about what its rung is. Given a role of its own, a wrap claimed
    two rungs it had no part in: 'argued the case for respondents. Also on
    the brief were Dan' opened a `date` on jewel (the reporter's date
    vocabulary matched 'argued' in the middle of a counsel sentence), and
    'filed the brief for respondent Department of Human Services.' opened a
    `lower-court` on dept._of_human_services_v._c._a._w. and put itself in
    `criteria.history` as the court the case came from.
    """
    rungs: list[list] = []          # [role, whole text, [rows]]
    for pieces, text in ladder:
        page_rail = frames.get(pieces[0].page, (rail, 0.0, 0.0))[0]
        dx = pieces[0].x0 - page_rail
        if dx >= _INDENT / 2 or not rungs:
            role = "counsel"
            if _PANEL.match(text):
                role = "panel"
            elif _POSTURE.match(text):
                role = "procedural-history"
            elif _DATES.match(text):
                role = "date"
            elif _LOWER_JUDGE.search(text):
                role = "lower-court"
            rungs.append([role, text, [pieces]])
        else:
            rungs[-1][1] = _norm(rungs[-1][1] + " " + text)
            rungs[-1][2].append(pieces)
        if rungs[-1][0] == "counsel":
            ctx.attorney(pieces)
        else:
            ctx.emit(pieces, rungs[-1][0], centre=False)

    panel = [t for role, t, _ in rungs if role == "panel"]
    if panel:
        line = _norm(" ".join(panel))
        ctx.crit.setdefault(
            # THE ROSTER'S FOOTNOTE MARK IS NOT PART OF A NAME. Nine records
            # hang one off the last judge ('Before Lagesen, Chief Judge, and
            # Egan, Judge.*') and the note it points at is the two-judge
            # department; the mark belongs to the apparatus, not the bench.
            "judges", re.sub(r"[*†‡]+\s*$", "",
                             re.sub(r"^Before\s+", "", line,
                                    flags=re.I).strip()).strip(" ."))
        names = _panel_names(line)
        if names:
            ctx.crit.setdefault("panel", names)
    for role, text, _rows_ in rungs:
        if role == "date":
            ctx.crit.setdefault("submitted", text.rstrip("."))
        elif role in ("lower-court", "procedural-history"):
            ctx.below.append(text)
    if ctx.below:
        # A CONSOLIDATED RECORD CAPTIONS EACH CASE IN ITS OWN COMPARTMENT and
        # names the same circuit court over each of them, so the origin is
        # printed twice and `history` read it twice ('Multnomah County Circuit
        # Court Multnomah County Circuit Court Morgan Wren Long, Judge.').
        # One court, said once.
        seen: list[str] = []
        for one in ctx.below:
            if one not in seen:
                seen.append(one)
        ctx.crit.setdefault("history", " ".join(seen)[:2000])


def _panel_names(line: str) -> list[str]:
    """The roster's names, with the bench titles dropped.

    'Before Tookey, Presiding Judge, Kamins, Judge, and Jacquot, Judge.' —
    the titles are a closed vocabulary and the names are what is left."""
    body = re.sub(r"^Before\s+", "", line, flags=re.I)
    body = re.sub(r"[*†‡]+\s*$", "", body.strip()).rstrip(".")
    out: list[str] = []
    for piece in re.split(r",|\band\b", body):
        piece = _norm(piece).rstrip(".").strip()
        if not piece or _BENCH_WORD.match(piece):
            continue
        if re.match(r"^(?:Chief|Senior|Presiding|pro|tempore)$", piece, re.I):
            continue
        out.append(piece)
    return out


# ---------------------------------------------------------------------------
# rows, and the emit buffer
# ---------------------------------------------------------------------------

def _rows(model, max_pages: int) -> list[list]:
    """Printed rows, in reading order, over the pages the block may reach.

    Rows are keyed on the page AND the baseline: two pages share a top, and
    keyed on the top alone page 2's head joined page 1's.
    """
    groups: dict = {}
    order: list = []
    for pm in model.pages[:max_pages]:
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip():
                continue
            key = (pm.number, round(line.top, 1))
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
    return [groups[k] for k in order]


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.attorneys: list = []
        self.summary: list = []
        self.below: list[str] = []

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

    def attorney(self, group: list) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.attorneys.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role="counsel"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items,
                "attorneys": self.attorneys, "summary": self.summary,
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
