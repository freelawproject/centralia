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
_DIVISION = re.compile(r"^Division\s+[IVXLC]+\.?$", re.I)
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
_SHEET_DOCKET = re.compile(r"^Nos?\.\s*\d{2}CA\d{3,4}\s*,")
_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s*\d{4}$")
# A SUBJECT LINE is the Reporter's index entry, and Colorado sets it with
# em-dash separated topics ('Courts and Court Procedure — Attorney Fees;
# Contracts — Fee-shifting Provisions — Fees-on-Fees'). The précis that
# follows is prose and opens on an indent.
_SUBJECT = re.compile(r"[—–]")


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
    rows = _rows(head_pm, finder)
    if not rows:
        return NOTHING
    # The rules SEGMENT. Their tops are the band edges; a row is in the band
    # its top falls into. Nothing is indexed off the count.
    rules = sorted(r.top for r in head_pm.h_rules if r.top > 50.0)
    if not rules:
        return NOTHING

    def band_of(top: float) -> int:
        return sum(1 for r in rules if r > top)

    dockets: list[str] = []
    parties: list[str] = []
    below: list[str] = []
    last_band = None
    for group in rows:
        text = _norm(" ".join(line.plain for line in group))
        if not text:
            continue
        first = group[0]
        # THE TYPE CLOSES THE BLOCK. The body steps up to 14pt.
        if (first.size or 0.0) > _HM_SIZE_MAX:
            break
        band = band_of(first.top)
        # A DRAWN RULE RENDERS WHERE THE PAGE DRAWS IT.
        if last_band is not None and band != last_band:
            ctx.rule(head_pm.number)
        last_band = band
        centred = abs((first.x0 + max(l.x1 for l in group)) / 2
                      - head_pm.width / 2) <= _AXIS_TOL

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
            ctx.emit(group, "docket", centre=False)
            continue
        if _JUDGE_BELOW.search(text) or _BELOW.search(text) \
                or _BELOW_NO.match(text):
            below.append(text)
            ctx.emit(group, "lower-court", centre=False)
            continue
        if _ANNOUNCED.match(text):
            ctx.crit.setdefault("decision_date", text.split(None, 1)[-1])
            ctx.emit(group, "date")
            continue
        if _PUBLICATION.match(text):
            ctx.emit(group, "publication")
            continue
        if _OPINION_BY.match(text):
            ctx.crit.setdefault("author_line", text)
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
    ctx.crit["docket"] = [d.split("Nos.", 1)[-1].split("No.", 1)[-1].strip()
                          for d in dockets]
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


def _read_sheet(ctx, pm, finder) -> None:
    """The Reporter's SUMMARY sheet: its notice is furniture, the rest is
    read. The notice is named by its own opening words, and the précis by
    the fact that it is prose set below the subject lines."""
    rows = _rows(pm, finder)
    in_notice = False
    seen_docket = False
    in_precis = False
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
            seen_docket = True
            ctx.emit(group, "docket", centre=False)
            continue
        # THE SUBJECT LINES are the Reporter's index entry and stand between
        # the docket row and the précis; the précis opens on an indent and
        # is prose.
        if not in_precis and seen_docket and _SUBJECT.search(text):
            ctx.emit(group, "headnotes", centre=False)
            continue
        if seen_docket:
            in_precis = True
            ctx.emit(group, "summary", centre=False)
            continue
        ctx.dropped_none(group)


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self, model):
        self.model = model
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
                "anchor_ids": [], "doc_type_final": None}
