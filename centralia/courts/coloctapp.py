"""Colorado Court of Appeals ('coloctapp').

Everything unique to coloctapp lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py.

THE CONTRACT — coloctapp DRAWS ITS BANDS. Colorado is the rare court that
does the parser's work for it: the headmatter page carries FOUR horizontal
rules, and every band of the block sits between two of them.

    ┌────────────────────────────────────────────────────────────────────┐
    │ COLORADO COURT OF APPEALS                              2025COA71   │ the masthead
    ├──────────────────────────────────── rule 1 ────────────────────────┤
    │ Court of Appeals No. 24CA0934                                      │ the docket
    │ City and County of Denver District Court No. 22CV30453             │ the court below
    │ Honorable Mark T. Bailey, Judge                                    │ its judge
    ├──────────────────────────────────── rule 2 ────────────────────────┤
    │ 1046 Munras Properties, L.P., a California limited partnership,    │
    │ Plaintiff-Appellant,                                               │ the caption
    │ v.                                                                 │
    │ Kabod Coffee, a Colorado limited liability company; …,             │
    │ Defendants-Appellees.                                              │
    ├──────────────────────────────────── rule 3 ────────────────────────┤
    │            ORDERS AFFIRMED IN PART AND REVERSED IN PART,           │ the disposition
    │                  Division VII                                      │ who sat
    │              Opinion by JUDGE LIPINSKY                             │ who wrote
    │            Johnson and Moultrie, JJ., concur                       │ who joined
    │              Announced August 7, 2025                              │ the release
    ├──────────────────────────────────── rule 4 ────────────────────────┤
    │ CYLG, P.C., Christopher A. Young, … for Plaintiff-Appellant        │ the appearances
    └────────────────────────────────────────────────────────────────────┘

Measured over all 42 records: 41 draw exactly four rules and
`people_in_the_interest_of_n.g.` draws five. THE RULES ARE NOT COUNTED and
no role is indexed off a band ORDINAL — the fifth rule would shift every
band below it and produce a page of confident wrong roles. The rules
SEGMENT; the row's own landmark NAMES it. That is also why a record whose
page prints its bands in another order still reads.

TWO PAPERS, ONE BLOCK. A published opinion is preceded by the Reporter's
SUMMARY sheet and sets the block on page 2; an unpublished one opens with
the block on page 1. Measured: the masthead lands on page 1 on 12 records,
page 2 on 16 and page 3 on 14. THE PAGE IS FOUND BY THE LANDMARK, never by
number — dispatching on page 1 would have read the summary sheet as the
headmatter on 30 of 42 records.

THE TYPE SEPARATES BLOCK FROM BODY. The whole headmatter is set at 12pt
and the opinion at 14pt, so the block closes where the type steps UP. This
is what stops the walk; there is no byline to stop it on, because Colorado
announces its author in the block ('Opinion by JUDGE LIPINSKY') instead of
signing the opinion.

THE SUMMARY SHEET (published records only) is the Reporter's, not the
court's, and it says so: 'The summaries of the Colorado Court of Appeals
published opinions constitute no part of the opinion of the division…'.
That notice is furniture. What follows it is read — the public-domain
citation, the release date, the docket with the case name, the subject
lines, and the précis itself.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = "colorado court of appeals"
_MAX_PAGES = 5
# The block's type. Headmatter is 12pt against a 14pt body on every record
# in the corpus; the step is the boundary.
_HM_SIZE_MAX = 13.0
_AXIS_TOL = 6.0

# THE COURT'S OWN PUBLIC-DOMAIN CITE, printed bold at the right end of the
# masthead row on a published opinion and again on the summary sheet.
_CITE = re.compile(r"^\d{4}COA\d+[A-Z]*$")
# 'Court of Appeals No. 24CA0934' / 'Court of Appeals Nos. 24CA0934 & …'
_DOCKET = re.compile(r"^(?:Court of Appeals|Supreme Court)\s+Nos?\.", re.I)
# The tribunal below, and the judge who sat there. Colorado reviews district
# and county courts, the Industrial Claim Appeals Office, and a handful of
# named agencies; each prints its own number line.
_BELOW = re.compile(
    r"(District Court|County Court|Juvenile Court|Probate Court|Water Court"
    r"|Industrial Claim Appeals Office|Office of Administrative Courts"
    r"|Division of |Department of |Board of |Commission)", re.I)
_BELOW_NO = re.compile(r"^(?:DD|Case|Claim|WC|OAC|No)\.?\s*Nos?\.?\s*[\w-]", re.I)
_JUDGE_BELOW = re.compile(r"^Honorable\b|,\s*(?:Judge|Magistrate|Referee)\.?$")
# The caption's own furniture.
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PARTY_ROLE = re.compile(
    r"^(?:Plaintiff|Defendant|Petitioner|Respondent|Appellant|Appellee"
    r"|Intervenor|Movant|Cross-Appell\w+|Third-Party\s+\w+|Garnishee"
    r"|Claimant|Employer|Insurer|Guardian|Conservator|Interested Party)"
    r"[\w\s/-]*[,.]?$", re.I)
_IN_RE = re.compile(r"^(?:IN RE|In re|In the (?:Matter|Interest)|The People)", re.I)
# What the court DID, printed centred in caps above the division.
_DISPO = re.compile(
    r"\b(AFFIRMED|REVERSED|VACATED|REMANDED|DISMISSED|SET ASIDE|MODIFIED"
    r"|DISCHARGED|ANNULLED|WITHDRAWN|SUSTAINED|GRANTED|DENIED)\b")
# THE DIVISIONS ARE NUMBERED — AND ONE IS LETTERED. 41 records sit in
# 'Division I' through 'Division VII'; people_v._jenkins sits in 'Division
# A'. Read as Roman numerals only, that row matched nothing, fell past every
# branch, and was left unclaimed — whereupon it became the writing's first
# block and core's reunite repair pulled the author announcement, the roster,
# the release date and the whole appearances band in after it.
_DIVISION = re.compile(r"^Division\s+(?:[IVXLC]+|[A-Z])\.?$", re.I)
# WHAT BECAME OF AN EARLIER OPINION, stated in the release band above the
# date: 'Prior Opinion Announced August 3, 2023, Vacated in 24-5460',
# 'Prior Opinion Announced November 13, 2025, WITHDRAWN', 'Opinion
# Previously Announced as "NOT PUBLISHED PURSUANT TO C.A.R. 35(e)" on
# November 13, 2025, is now Designated for Publication'. Three records print
# one, and on all three it was the row the writing opened on.
_PRIOR = re.compile(
    r"^(?:Prior Opinion|Opinion Previously|Opinion Announced|Rehearing)\b",
    re.I)
_OPINION_BY = re.compile(r"^Opinion by\b", re.I)
_ROSTER = re.compile(r"\b(concur|dissent|specially concurr|joins?)\w*\b", re.I)
_PUBLICATION = re.compile(
    r"^(?:NOT PUBLISHED|PUBLISHED)\b|C\.A\.R\.\s*35|ANNOUNCED PURSUANT", re.I)
_ANNOUNCED = re.compile(r"^Announced\b", re.I)
# THE E-FILING SLUG the court stamps atop an unpublished block, repeating
# the docket, the short case name and the release date on one row
# ('25CA2269 GOAL Academy v ICAO 08-06-2026'). It is a filing artifact, not
# a printed band, and it is dropped rather than tinted with a role.
_SLUG = re.compile(r"^\d{2}CA\d{3,4}\s+\S.*\s+\d{2}-\d{2}-\d{4}$")

# ---- the summary sheet ----------------------------------------------------
# The Reporter's notice. It names itself in its first words on every record
# that prints one.
_NOTICE_OPEN = re.compile(r"^The summaries of the Colorado Court of Appeals",
                          re.I)
_NOTICE_WORDS = re.compile(
    r"constitute no part of the opinion|convenience of the reader"
    r"|not the official|discrepancy between the language", re.I)
_SUMMARY_HEAD = re.compile(r"^SUMMARY$")
# THE COMMA IS NOT ALWAYS THERE. 28 of the 30 sheets read 'No. 24CA0934,
# 1046 Munras Properties, L.P. v. Kabod — …' and two run the case name
# straight on ('No. 24CA1046 Castillo v. STEM — …', smith_v._terumo). With
# the comma required, `seen_docket` stayed false on those two, so the subject
# lines and the whole précis went unclaimed — and once a WRITING opened on
# them at the top of page 1, core's reunite repair pulled the opinion's own
# block on page 2 back into it, row by row: 31 read rows became 7 (the user,
# 2026-08-20: 'it has a summary and then headmatter but its not parsing it').
_SHEET_DOCKET = re.compile(r"^Nos?\.\s*\d{2}CA\d{3,4}\b\s*,?")
_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s*\d{4}$")
# A SUBJECT LINE is the Reporter's index entry, and Colorado sets it with
# em-dash separated topics ('Courts and Court Procedure — Attorney Fees;
# Contracts — Fee-shifting Provisions — Fees-on-Fees'). The précis that
# follows is prose and opens on an indent.
_SUBJECT = re.compile(r"[—–]")
# The sheet's own rail: the docket and index rows stand at it, the précis is
# indented a paragraph in from it.
_SHEET_RAIL = 72.0
# The block's own footnote: the court marks an assigned judge on the roster
# row and explains the mark at the foot of the block.
_BLOCK_NOTE = re.compile(r"^\*\s*\S")
# The opinion's own first paragraph, numbered as this court numbers them all.
_PARA_ONE = re.compile(r"^¶\s*1\b")
# A body row runs the measure; this court's measure ends at 540.
_MEASURE_MIN = 470.0
# The paragraph indent the body opens at.
_INDENT = 108.0


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="coloctapp")
def read_headmatter_coloctapp(model, geom, **_):
    """Read Colorado's drawn block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)

    # THE LANDMARK FINDS THE PAGE. Never the page number: the summary sheet
    # pushes the block to page 2 or 3 on 30 of the 42 records.
    head_pm = head_line = None
    for pm in model.pages[:_MAX_PAGES]:
        for line in pm.lines:
            if _norm(line.plain).lower() == _MASTHEAD:
                head_pm, head_line = pm, line
                break
        if head_pm is not None:
            break
    if head_pm is None:
        return NOTHING

    finder = FurnitureFinder(model, body_x0, body_size)
    ctx = _Ctx(model)

    # ---- the Reporter's summary sheet, where the record prints one -------
    for pm in model.pages[:head_pm.number - 1]:
        _read_sheet(ctx, pm, finder)

    # ---- the drawn block -------------------------------------------------
    # THE BLOCK RUNS ONTO THE NEXT PAGE on 5 of the 42 records. The masthead
    # page holds the rules and the ladder; what does not fit — the division,
    # the author announcement, the roster, the release date, the appearances
    # and the block's own footnote — is set on the page after it, and the
    # opinion then opens on '¶ 1' further down. Walked one page only, all of
    # that was read as the opinion's first paragraphs (people_v._jenkins
    # opened its majority on 'Division A'; the user, 2026-08-20: 'not parsing
    # all the headmatter putting in opinion').
    if not sorted(r.top for r in head_pm.h_rules if r.top > 50.0):
        return NOTHING
    pages = [head_pm]
    for pm in model.pages[head_pm.number:_MAX_PAGES]:
        if any(_PARA_ONE.match(_norm(" ".join(l.plain for l in g)))
               for g in _rows(pm, finder)):
            pages.append(pm)          # the block's tail, above '¶ 1'
            break
        pages.append(pm)
    rows = [(pm, g) for pm in pages for g in _rows(pm, finder)]
    if not rows:
        return NOTHING
    # The rules SEGMENT, and each page has its own: the tops are the band
    # edges and a row is in the band its top falls into. Nothing is indexed
    # off the count.
    _rules_by_page = {pm.number: sorted(r.top for r in pm.h_rules
                                        if r.top > 50.0) for pm in pages}

    def band_of(page: int, top: float) -> int:
        return sum(1 for r in _rules_by_page.get(page) or () if r > top)

    dockets: list[str] = []
    parties: list[str] = []
    below: list[str] = []
    ladder_band = None
    in_block_note = False
    in_prior = False
    last_band = None
    for head_pm_of_row, group in rows:
        text = _norm(" ".join(line.plain for line in group))
        if not text:
            continue
        first = group[0]
        # THE OPINION OPENS ON '¶ 1', and that is what closes the block —
        # measured over all 42 records, every one of them numbers its first
        # paragraph and none opens any other way (the user's call,
        # 2026-08-20: 'all opinions start with ¶ 1 i think').
        #
        # THE TYPE STEP IS NOT THE BOUNDARY, though the block is 12pt and the
        # body 14pt: the court sets rows of the block itself at body size —
        # 'Prior Opinion Announced August 3, 2023, Vacated in 24-5460'
        # (people_v._fields), 'Opinion Previously Announced as "NOT PUBLISHED
        # PURSUANT TO C.A.R. 35(e)" …' (people_in_the_interest_of_n.g.), and
        # a plain 'Division A' (people_v._jenkins). Stopping at the step left
        # the rest of the block — the division, the author announcement, the
        # roster, the release date and the appearances — to be read as the
        # opinion's first paragraphs on five records.
        if _PARA_ONE.match(text):
            break
        # …and the type step still guards a paper this contract does not
        # describe, but only where the row is BODY-SHAPED: set at body size,
        # opening at the rail or the paragraph indent, and running the
        # measure. The block's own body-size rows are none of those — they
        # are short, or centred, or both.
        if ((first.size or 0.0) > _HM_SIZE_MAX
                and first.x0 <= _INDENT + 1.0
                and max(l.x1 for l in group) >= _MEASURE_MIN):
            break
        band = band_of(head_pm_of_row.number, first.top)
        # A DRAWN RULE RENDERS WHERE THE PAGE DRAWS IT.
        if last_band is not None and band != last_band:
            ctx.rule(head_pm_of_row.number)
        last_band = band
        # CENTRED MEANS SET IN FROM THE RAIL, not 'its midpoint is near the
        # axis'. A caption row that runs the full measure has its midpoint ON
        # the axis by construction — smith_v._city_and_county_of_denver sets
        # 'Ronald G. Smith and Jasper Armstrong, in his representative
        # capacity and on' from 72.0 to 529.5, a centre of 300.8 against an
        # axis of 306.0 — so it read as centred, failed the caption's `not
        # centred` test, and was left unclaimed. A WRITING then opened on it
        # and core's reunite repair pulled the rest of the block into that
        # writing. Colorado's centred rows begin at 204-278; every row of the
        # docket ladder, the caption and the appearances begins at the rail.
        centred = (abs((first.x0 + max(l.x1 for l in group)) / 2
                       - head_pm_of_row.width / 2) <= _AXIS_TOL
                   and first.x0 > body_x0 + 12.0)

        if _SLUG.match(text):
            ctx.drop(group, "stamp")
            continue
        if text.lower() == _MASTHEAD:
            ctx.crit.setdefault("court", text)
            ctx.emit(group, "court", centre=False)
            continue
        # The cite shares the masthead's ROW, printed bold at the right end.
        if _CITE.match(text):
            ctx.crit.setdefault("citation", text)
            ctx.emit(group, "citation", centre=False)
            continue
        if _DOCKET.match(text):
            dockets.append(text)
            # THE LADDER IS A BAND, and this row names it. Everything the
            # court says about the tribunal below stands in the same band as
            # its own docket, between the first two rules.
            ladder_band = (head_pm_of_row.number, band)
            ctx.emit(group, "docket", centre=False)
            continue
        # …AND THE TEST FOR IT IS BAND-BOUND. The tribunal below is named by
        # words that occur just as readily in the CAPTION and in the
        # APPEARANCES: goal_academy_v._icao reviews the Industrial Claim
        # Appeals Office, which is also a named RESPONDENT ('Industrial Claim
        # Appeals Office of the State of Colorado and Mordecai Valdez') and
        # the subject of an appearance row ('No Appearance for Respondent
        # Industrial Claim Appeals Office'). Both were tinted `lower-court`
        # in the middle of the caption and the counsel (the user, 2026-08-20:
        # 'it marked a lower court incorrectly again in the caption and in
        # the counsel'). The rules the page draws already separate the three;
        # only the ladder's own band answers this question.
        if ladder_band == (head_pm_of_row.number, band) and (
                _JUDGE_BELOW.search(text) or _BELOW.search(text)
                or _BELOW_NO.match(text)):
            below.append(text)
            ctx.emit(group, "lower-court", centre=False)
            continue
        if _ANNOUNCED.match(text):
            ctx.crit.setdefault("decision_date", text.split(None, 1)[-1])
            in_prior = False              # the release date closes the band
            ctx.emit(group, "date")
            continue
        # WHAT BECAME OF AN EARLIER OPINION stands just above the release
        # date, and it RUNS ON: 'Opinion Previously Announced as "NOT
        # PUBLISHED PURSUANT TO C.A.R. 35(e)" on November 13, 2025, is now
        # Designated for Publication' takes two rows, and the first ends on
        # the abbreviation 'C.A.R.' — so a full stop cannot close the band.
        # The release date closes it, and the date is tested above.
        if _PRIOR.match(text) or in_prior:
            in_prior = True
            ctx.emit(group, "publication", centre=centred)
            continue
        if _PUBLICATION.match(text):
            ctx.emit(group, "publication")
            continue
        if _OPINION_BY.match(text):
            ctx.crit.setdefault("author_line", text)
            # THE COURT ANNOUNCES ITS AUTHOR AND NEVER SIGNS. 'Opinion by
            # JUDGE SCHUTZ' stands in the block, so once the block is claimed
            # there is no byline left anywhere for core to read and every one
            # of the 42 records came back with an UNAUTHORED writing. Reported
            # through core's own `announced_author`, which it applies only to
            # a lead writing that carries no byline of its own — the
            # profile's grammar already reads this form
            # ('opinion_by_headings').
            ctx.announced = text
            ctx.emit(group, "author")
            continue
        if _DIVISION.match(text):
            ctx.emit(group, "panel")
            continue
        if centred and _ROSTER.search(text):
            ctx.crit.setdefault("panel_line", text)
            ctx.emit(group, "panel")
            continue
        if centred and _DISPO.search(text) and text == text.upper():
            ctx.emit(group, "disposition")
            continue
        # THE APPEARANCES are the band BELOW THE LAST RULE, and they are the
        # only band the court sets as flowing prose — so a row there is
        # counsel whatever it says. `band_of` counts the rules still BELOW a
        # row, so the closing band is 0 and the masthead's is the highest:
        # testing it the other way round swapped the caption and the
        # appearances on every record in the corpus.
        if band == 0:
            # …EXCEPT THE BLOCK'S OWN FOOTNOTE. Colorado marks a judge
            # sitting by assignment with an asterisk on the roster row and
            # sets the note at the foot of the block, in the appearances'
            # band and with no separator above it: '*Sitting by assignment of
            # the Chief Justice under provisions of Colo. Const. art. VI, §
            # 5(3), and § 24-51-1105, C.R.S. 2025.' Claimed as an appearance
            # it read as counsel for a party (the user, 2026-08-20: 'this is
            # correctly marked as headmatter footnote but left in counsel').
            # It is left to core's footnote machinery, which already pairs it
            # with the roster's mark.
            # Once it opens it runs to the end of the band: the note is the
            # last thing the block prints. ('Ends with a period' cannot close
            # it — the first row ends on the abbreviation 'Colo. Const.
            # art.', so the continuation went back to being counsel.)
            if _BLOCK_NOTE.match(text) or in_block_note:
                # CLAIMED, not left to core. The note explains an asterisk on
                # the roster row ('Grove and Bernard*, JJ., concur'), so it
                # belongs with the panel it qualifies. Left unclaimed for
                # core's footnote pass to pair, it paired on two records and
                # on the third (mosley_v._daves) became the writing's own
                # first block instead — and once a writing opens on a row of
                # the block, the reunite repair takes the rest of the block
                # in after it. A row the page prints inside the block is the
                # block's; luck is not a reading.
                in_block_note = True
                ctx.emit(group, "panel", centre=False)
                continue
            ctx.emit(group, "counsel", centre=False)
            continue
        # THE CAPTION is what is left between the docket ladder and the
        # disposition: the parties, their roles, and the pivot.
        if _PIVOT.match(text) or _PARTY_ROLE.match(text) or _IN_RE.match(text) \
                or not centred:
            if not _PIVOT.match(text) and not _PARTY_ROLE.match(text):
                parties.append(text)
            ctx.emit(group, "caption", centre=False)
            continue
        # A ROW THIS PAPER DOES NOT PRINT is left to core rather than tinted
        # with a role that would be a guess.
        ctx.dropped_none(group)

    if not dockets:
        return NOTHING
    _dk = [d.split("Nos.", 1)[-1].split("No.", 1)[-1].strip()
           for d in dockets]
    ctx.crit["docket_number"] = _dk[0]
    if _dk[1:]:
        ctx.crit["other_dockets"] = _dk[1:]
    if parties:
        ctx.crit.setdefault("parties", parties[:6])
    if below:
        ctx.crit.setdefault("history", " ".join(below)[:2000])
    return ctx.result()


def _rows(pm, finder) -> list[list]:
    """The page's rows in printed order, same-row pieces rejoined. The
    masthead and the citation share a row and must not be one element, so
    pieces are grouped but each piece keeps its own x0 — the caller decides.
    """
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
    out: list[list] = []
    for key in order:
        row = groups[key]
        # THE MASTHEAD ROW IS TWO ELEMENTS. A row whose pieces stand apart
        # by more than a word space is two bands the page happened to set on
        # one line ('COLORADO COURT OF APPEALS' | '2025COA71').
        if len(row) > 1:
            out.extend([piece] for piece in row)
        else:
            out.append(row)
    return out


def _prov(group: list) -> m.Prov:
    parts = sorted(group, key=lambda l: l.x0)
    return m.Prov(parts[0].page, tuple(p.id for p in parts))


def _markup(group: list) -> str:
    text = ""
    for part in sorted(group, key=lambda l: l.x0):
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() else piece
    return text


def _read_sheet(ctx, pm, finder) -> None:
    """The Reporter's SUMMARY sheet: its notice is furniture, the rest is
    read. The notice is named by its own opening words, and the précis by
    the fact that it is prose set below the subject lines."""
    rows = _rows(pm, finder)
    in_notice = False
    # THE SHEET MAY RUN TO A SECOND PAGE, so where the précis stands is
    # remembered ACROSS the sheet's pages and not per page. elken_v._bain
    # carries its last two précis rows onto page 2; read per page, that page
    # had no docket row above them, so they went unclaimed — a WRITING opened
    # on them and core's reunite repair then pulled the opinion's own block
    # off page 3 into it, one row at a time (17 read rows became 9).
    seen_docket = ctx.sheet_docket
    in_precis = ctx.sheet_precis
    for group in rows:
        text = _norm(" ".join(l.plain for l in group))
        if not text:
            continue
        if _NOTICE_OPEN.match(text):
            in_notice = True
        if in_notice:
            ctx.drop(group, "notice")
            # The notice runs until the type steps up out of it.
            if not _NOTICE_WORDS.search(text) and not _NOTICE_OPEN.match(text) \
                    and text.endswith("."):
                in_notice = False
            continue
        if _SUMMARY_HEAD.match(text):
            # A HEADING THAT NAMES A SECTION belongs to that section, not to
            # `title` — `title` is what the PAPER calls itself.
            ctx.emit(group, "summary", centre=False)
            continue
        if _DATE.match(text):
            ctx.emit(group, "date", centre=False)
            continue
        if _CITE.match(text):
            ctx.crit.setdefault("citation", text)
            ctx.emit(group, "citation")
            continue
        if _SHEET_DOCKET.match(text):
            seen_docket = ctx.sheet_docket = True
            ctx.emit(group, "docket", centre=False)
            continue
        # THE SUBJECT LINES are the Reporter's index entry and stand between
        # the docket row and the précis; the précis opens on an indent and
        # is prose.
        # …AND THE INDEX ENTRY WRAPS. Its topics are em-dash separated, but a
        # wrap carries no dash of its own: elken sets '… — Embryos —
        # Unmarried' and then 'Parties' alone on the next row. The précis
        # opens on the paragraph INDENT and this does not, which is what
        # tells the two apart (the docstring's own rule, applied to the wrap).
        if not in_precis and seen_docket and (
                _SUBJECT.search(text)
                or (group[0].x0 <= _SHEET_RAIL + 1.0 and len(text) < 60)):
            ctx.emit(group, "headnotes", centre=False)
            continue
        if seen_docket:
            # THE PRÉCIS IS A SECTION OF ITS OWN. Emitted as headmatter rows
            # it renders inside the block, above a caption it is not part of;
            # handed over as `summary` it renders as the section the sheet
            # says it is ('SUMMARY'), which is also what keeps it out of the
            # opinion when core reunites stray rows.
            in_precis = ctx.sheet_precis = True
            ctx.summary.append(m.Paragraph(
                text=_markup(group), prov=_prov(group)))
            ctx.consumed.update(l.id for l in group)
            continue
        ctx.dropped_none(group)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model):
        self.model = model
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.summary: list = []
        self.sheet_docket = False
        self.sheet_precis = False
        self.announced: str | None = None
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

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def dropped_none(self, group: list) -> None:
        """A row no landmark named. It is NOT consumed — an untagged row
        says 'nobody read this', which is true and measurable; a row tinted
        with the nearest neighbour's role is a confident lie."""
        return None

    def rule(self, page: int) -> None:
        prev = next((i for i in reversed(self.items)
                     if isinstance(i, m.HmLine)), None)
        self.items.append(m.Rule(
            prov=prev.prov if prev is not None else m.Prov(page),
            span="full"))

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "summary": self.summary, "announced_author": self.announced,
                "anchor_ids": [], "doc_type_final": None}
