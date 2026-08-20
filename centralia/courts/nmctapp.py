"""Court of Appeals of the State of New Mexico ('nmctapp').

Everything unique to nmctapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT — ONE LADDER, THREE PAPERS. The Court of Appeals prints the
same block its Supreme Court does: a ladder of identifiers at the body rail,
one group per appeal, closed by the paper naming ITSELF on the page axis.
Nothing is fenced. The three drawn verticals on the slip paper are the
pleading gutter rails and the right page border, not a caption divider —
**there is no divider on this court's caption at all**, in any of its three
papers, so the reading is va's and not ca6's or illappct's: the only
measurement that separates the caption's cells is where a row starts, and
here even that is degenerate, because both cells stand at the SAME rail.
The block is one column, in the page's order.

    ┌───────────────────────────────────────────────────────────────┐
    │ The slip opinion is the first version of an opinion released  │
    │ by the Clerk of the Court of Appeals.  Once an opinion is     │
    │ selected for publication … Rule 23-112 NMRA, authenticated    │
    │ and formally published.                    the clerk's notice │
    │                                                               │
    │   IN THE COURT OF APPEALS OF THE STATE OF NEW MEXICO          │
    │                                              the masthead     │
    │ Opinion Number: __________   the PUBLIC-DOMAIN CITATION slot  │
    │ Filing Date: July 8, 2025                  the filing date    │
    │ No. A-1-CA-41014                                the DOCKET    │
    │                                                               │
    │ PETER B. KOMIS and DORINDA                                    │
    │ HOPPER-KOMIS,                                                 │
    │      Plaintiffs-Appellants,                   the caption     │
    │ v.                                                            │
    │ FARMERS INSURANCE COMPANY,                                    │
    │      Defendant-Appellee.                                      │
    │ APPEAL FROM THE DISTRICT COURT OF SANTA FE COUNTY             │
    │                                               the origin…     │
    │ Bryan Biedscheid, District Court Judge     …and its judge     │
    │                                                               │
    │ Jones, Snead, Wertheim & Clifford, P.A.                       │
    │ Jerry Todd Wertheim                       the appearances     │
    │ Santa Fe, NM                              (each CLOSES on     │
    │ for Appellant Peter B. Komis               'for …' or         │
    │ …                                          'Pro Se …')        │
    │                     OPINION                    the title      │
    │ BOSSON, Justice, retired, sitting by designation.             │
    │                                        (the paper begins)     │
    └───────────────────────────────────────────────────────────────┘

THE THREE PAPERS, measured over all 21 records. They differ in their
FURNITURE and in what the paper calls itself; below the fourth rung they
are identical, which is why the reader dispatches on the MASTHEAD and never
on an ordinal — the notice moves every row beneath it by three, four or
five, and on the published paper by none at all.

  * SLIP (13 records). Line-numbered pleading stationery — a `1`-`28`
    column at x0 50-65 behind two drawn gutter rails at x 65.9/67.3, which
    core's `FurnitureFinder` already tags `gutter`; a 14pt measure; the
    Clerk's slip notice above the masthead, set at 9, 11, 12 or 14pt in
    three or five rows depending on the template; `Opinion Number:` printed
    EMPTY (`__________`, `:__________` with no space, or nothing at all on
    state_v._schmidt), because Rule 23-112 NMRA assigns the citation only
    once the Court selects the opinion for publication; and `OPINION` on
    the axis. Its headmatter runs to page 4 (n.m._auto._dealers_assoc).
  * MEMORANDUM (7 records). A 12pt measure, no line numbers, a five-row
    non-publication notice ('This decision … was not selected for
    publication in the New Mexico Appellate Reports'), NO `Opinion Number`
    rung and NO `Filing Date` rung — the ladder is masthead, docket, and
    nothing else — and `MEMORANDUM OPINION` on the axis. Its appearances
    close on 'Pro Se Appellant' as often as on 'for Appellant'.
  * PUBLISHED (1 record, apache_corp). No notice of any kind, no line
    numbers, a 12pt measure, and the citation slot FILLED:
    `Opinion Number: 2024-NMCA-080`.

THE PUBLIC-DOMAIN CITATION IS NOT THE DOCKET. `2024-NMCA-080` is the
vendor-neutral citation the Court assigns under Rule 23-112 NMRA — `NMCA`
is this court's own series, as `NMSC` is the Supreme Court's — and it takes
`criteria.citation` and the `citation` role. The docket is a separate rung,
always `No. A-1-CA-NNNNN`, and it takes `docket_number`. Conflating them
cost ill its whole corpus (commit 03e8652): the neutral cite wore the
`docket` role, every cover printed two dockets, and `citation` stayed empty
on all 50 files. Here the two are never confusable by shape, and the reader
keeps them apart by RUNG, not by shape.

THE COMPILATION COMMISSION'S SIGNING STAMP IS AN ANNOTATION, NOT TEXT.
The authenticated paper carries the Commission's UELMA signature —
'Office of the Director / New Mexico Compilation Commission / 2024.12.17 /
16:09:16' — drawn in a `/Widget` annotation over the head of page 1. It is
furniture, and its timestamp must never reach `decision_date`; the filing
date the court itself prints ('Filing Date: June 17, 2024') is the
decision date. MEASURED: of the 21 records exactly one carries the widget
(apache_corp, the published paper — the only one the Commission has
authenticated), pdfminer returns ZERO characters for it, and page 1's first
text row is the masthead at top 75.8. So there is nothing in the stream to
drop and no row to guard: the stamp cannot reach any criterion because it
never becomes a line. This is recorded because the coverage machinery knows
the family ('UELMA signature-annotation boilerplate (invisible to
pdfminer)', docs/review-backlog.md) and a later extractor that DOES render
annotations would put four rows above the masthead — where this reader
already drops everything it does not recognize as a notice, as `stamp`.

THE NOTICES ARE FURNITURE. Both of them — the Clerk's slip warning and the
non-publication warning — are standing boilerplate above the masthead,
recorded as `Dropped`, never tinted. Because the non-publication notice is
the only place the memorandum paper states its status, dropping it would
LOSE that fact, so the reader states it itself: `publication_status =
'unpublished'` where that notice stands, and 'published' where the Court
has filled the citation slot (the slip notice says in terms that the
citation is assigned when the opinion 'is selected for publication'). On a
slip the reader states nothing, because the page states nothing.

HOW THE CAPTION IS BOUNDED. Exactly nm's problem and exactly nm's answer:
caption rows and appearance rows stand at the SAME rail (72.0) in the SAME
type and no rule is drawn between them. Two closed vocabularies bound it —
its last row is a party STATUS label, and its first is found by walking
back from that label to the rung above. The status label is indented to
108.0 on the memorandum paper and FLUSH at the rail on the slip paper
(the leading space in ' Petitioner-Appellant.' is the whole indent), so the
INDENT cannot be the test. `Protestant-Appellant,` (apache) and
`Plaintiff/Counterdefendant-Appellee,` (prince) are in the vocabulary;
party NAMES and firm names never are.

Below the status label the caption may carry the MATTER appealed — a run
opening 'IN THE MATTER OF' and closing where the origin begins
(n.m._auto._dealers_assoc p2: 'IN THE MATTER OF PETITION TO AMEND EXISTING
REGULATIONS 20.2.91 NMAC …'). It reads as `case-info`. On
in_re_petition_for_expungement the same words open the caption INSTEAD of a
party name, so the run is only ever looked for BELOW a status label.

WHY THE CLAIM RUNS EDGE TO EDGE. Every row from the masthead through the
paper's own name is claimed — court, citation, date, docket, caption,
case-info, lower-court, counsel, title — with no hole, because a row left
unclaimed inside the span lets core open a writing there and the bisection
invariant (pipeline.py) then pulls the block into it. That is not
hypothetical here: before this reader existed,
n.m._auto._dealers_assoc rendered FOUR headmatter rows and filed its
caption, its origin and its 38 appearance rows inside the majority.
Measured over all 21 records this classification leaves ZERO rows in the
span unnamed.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# WHERE THE PROFILE LIVES. Every other ported court moved its CourtProfile
# into its own file; nmctapp's still stands in `courts/__init__.py:374`
# because that file is owned by another agent for the length of this port
# and `register` refuses a duplicate id. Two measured facts belong on it
# and are NOT yet declared — both concern the BODY, not this block, so the
# reader is complete without them:
#
#   * `para_indent_min=24.0`. The rail is 72.0, a paragraph opens 36pt in
#     at 108.0, and a quotation is set out at 144.0 or 180.0
#     (state_v._romanis-beltran body pages: 649 rows at 72, 139 at 108, 12
#     at 144, 56 at 180). Twice this value is the block-quotation fence, so
#     it must fall strictly between 36 and 72; at the 12.0 default the
#     fence is 24pt and every ordinary paragraph opener is inside it.
#   * `titles=(… "Justice", "Chief Justice")` beside the shared
#     `_JUDGE_PROSE` list. Retired Supreme Court justices sit here by
#     designation and sign as such: 'BOSSON, Justice, retired, sitting by
#     designation.' (komis), 'BUSTAMANTE, Judge, retired, sitting by
#     designation.' (apache).

STYLE_SLIP = "nmctapp slip ladder"
STYLE_MEMORANDUM = "nmctapp memorandum ladder"
STYLE_PUBLISHED = "nmctapp published ladder"

# ---- nmctapp's declared facts (measured over all 21 records) ------------
# THE DISPATCH. Centred on the page axis on all 21: x0 95.5-516.7 against
# the slip paper's 14pt measure (mid 306.1), 127.3-484.7 against the 12pt
# memorandum and published papers (mid 306.0), on a 612pt page.
_MASTHEAD = re.compile(r"^IN THE COURT OF APPEALS OF THE STATE OF NEW MEXICO$",
                       re.I)
# THE FOOT. 'OPINION' at x0 275.3-336.8 (mid 306.05) and 'MEMORANDUM
# OPINION' at 233.7-378.4 (mid 306.05) — both dead on the axis. The other
# names are admitted because this court also files decisions and orders;
# none appears in this corpus.
_TITLE = re.compile(r"^(?:MEMORANDUM OPINION|MEMORANDUM DECISION"
                    r"|OPINION AND ORDER|OPINION|DECISION|ORDER)$")
_AXIS_TOL = 14.0
# The block never runs past page 4 (n.m._auto._dealers_assoc, four party
# groups and 38 appearance rows; the median record ends on page 1).
_MAX_PAGES = 6
# THE NOTICES, by their opening words — the only two the court prints, both
# above the masthead, both standing boilerplate.
_SLIP_NOTICE = re.compile(r"^The slip opinion is the first version", re.I)
_NOPUB_NOTICE = re.compile(r"^This decision of the New Mexico Court of "
                           r"Appeals was not selected for publication", re.I)
# THE PUBLIC-DOMAIN CITATION SLOT. Filled on the published paper
# ('Opinion Number: 2024-NMCA-080'), empty on every slip — as
# '__________' (11 records), ':__________' with no space after the colon
# (silva, fulton), or with nothing at all after the colon (schmidt).
_CITE = re.compile(r"^Opinion Number:\s*(.*)$", re.I)
# What a FILLED slot looks like: the Court's own series, 'YYYY-NMCA-NNN'.
_CITE_VALUE = re.compile(r"^\d{4}-NMCA-\d+[A-Za-z]?$")
_DATE = re.compile(r"^Filing Date:\s*(.*)$", re.I)
# THE DOCKET — the Court of Appeals' own number, 'A-1-CA-41014' on all 21.
# Never the citation: that rung says 'Opinion Number:' and this one 'No.'
_DOCKET = re.compile(r"^Nos?\.\s*(A-1-CA-\d[\dA-Za-z,;\s-]*)$", re.I)
# WHERE THE APPEAL CAME FROM. Measured wordings: 'APPEAL FROM THE DISTRICT
# COURT OF <COUNTY> COUNTY' (17), 'APPEAL FROM THE ADMINISTRATIVE HEARINGS
# OFFICE' (apache), 'APPEAL FROM ENVIRONMENTAL IMPROVEMENT BOARD and' +
# 'THE ALBUQUERQUE BERNALILLO AIR QUALITY CONTROL BOARD' (n.m._auto, the
# only wrapped one). The wording is payload; the stem is the landmark.
_ORIGIN = re.compile(
    r"^(?:APPEAL FROM|APPEALS FROM|ORIGINAL PROCEEDING|CERTIORARI TO"
    r"|ON CERTIORARI|ON APPEAL FROM|CERTIFICATION FROM|DIRECT APPEAL"
    r"|PETITION FOR)\b")
# WHO TRIED IT, printed directly under the origin: 'Emilio Chavez, District
# Court Judge', 'Brian VanDenzen, Chief Hearing Officer', 'Felicia Orth,
# Administrative Hearing Officer'.
_JUDGE = re.compile(
    r",\s*(?:[A-Z][a-z]+\s+)*(?:Judges?|Justices?|Hearing Officers?"
    r"|Commissioners?)$")
# AN APPEARANCE BLOCK CLOSES ON ITS ATTRIBUTION: 'for Appellant',
# 'for Appellee State of New Mexico', 'for Intervenor-Appellee Coalition
# for Clean Affordable Energy', 'for Amicus Curiae N.M. Department of
# Justice and' — or, on the memorandum paper where a party appears for
# itself, 'Pro Se Appellant' / 'Pro Se Appellee'.
_FOR = re.compile(r"^(?:for\s+\S|Pro\s+Se\b)", re.I)
# THE MATTER APPEALED, under the parties.
_MATTER = re.compile(r"^In (?:the Matter of|the Application|re)\b", re.I)
_CASE_NO = re.compile(r"Case No\.\s*\S+$", re.I)
# PARTY STATUS — a closed vocabulary, and the caption's last row. Never a
# party NAME and never a firm name: those are open vocabularies.
# 'Protestant' is here for apache ('Protestant-Appellant,'), the taxpayer's
# name for itself before the Administrative Hearings Office.
_STATUS = re.compile(
    r"^(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|Appellants?"
    r"|Appellees?|Intervenors?|Relators?|Claimants?|Movants?|Protestants?"
    r"|Cross-\w+|Real Part(?:y|ies) in Interest|Amic(?:us|i) Curiae"
    r"|Worker|Employer|Insurer|Child|Children|Mother|Father"
    r"|(?:Necessary|Nominal|Indispensable) Part(?:y|ies)[\w-]*)"
    r"[A-Za-z\s,/&'’-]*[,.]$")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_JOINER = re.compile(r"^and$", re.I)
# A row set in the origin's capitals — no lower-case letter anywhere in it.
_ALLCAPS = re.compile(r"^[^a-z]*[A-Z][^a-z]*$")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="nmctapp")
def read_headmatter_nmctapp(model, geom, **_):
    """Read the New Mexico Court of Appeals' ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    # geom is None on the shortest records (prince_v._de_los_santos, two
    # pages), so both measurements fall back to the court's printed values.
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    width = model.pages[0].width

    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 6:
        return NOTHING
    txt = [_norm(" ".join(l.plain for l in g)) for g in rows]

    def _centred(i: int) -> bool:
        g = rows[i]
        mid = (min(l.x0 for l in g) + max(l.x1 for l in g)) / 2
        return abs(mid - width / 2) <= _AXIS_TOL

    # THE DISPATCH: the masthead, wherever the notice above it happens to
    # end (three, four or five rows, or none on the published paper).
    mast = next((i for i in range(min(16, len(rows)))
                 if _MASTHEAD.match(txt[i]) and _centred(i)), None)
    if mast is None:
        return NOTHING
    # THE FOOT: the paper's own name on the axis. Without it we do not know
    # where the block ends, and a claim of unknown extent is worse than none.
    title = next((i for i in range(mast + 1, len(rows))
                  if _TITLE.match(txt[i]) and _centred(i)), None)
    if title is None:
        return NOTHING

    kinds: list[str | None] = [None] * len(rows)
    # ABOVE THE MASTHEAD: a notice RUN, and above the run whatever else the
    # page put there. The run OPENS on one of the two notices' first words
    # and closes at the masthead; anything above the opener is not the
    # court's boilerplate and is dropped as a `stamp` (today that region is
    # always empty — see the Compilation Commission note above — but a
    # reader that claims a region inherits its furniture, and this is where
    # a rendered signature annotation would land).
    notice_at = next((i for i in range(mast)
                      if _SLIP_NOTICE.match(txt[i])
                      or _NOPUB_NOTICE.match(txt[i])), None)
    notice_kind = None
    if notice_at is not None:
        notice_kind = (STYLE_MEMORANDUM if _NOPUB_NOTICE.match(txt[notice_at])
                       else STYLE_SLIP)
    for i in range(mast):
        kinds[i] = ("#notice" if notice_at is not None and i >= notice_at
                    else "#stamp")
    kinds[mast] = "court"
    kinds[title] = "title"
    # ---- pass 1: the rungs that name themselves -------------------------
    for i in range(mast + 1, title):
        t = txt[i]
        if _CITE.match(t):
            kinds[i] = "citation"
        elif _DATE.match(t):
            kinds[i] = "date"
        elif _DOCKET.match(t):
            kinds[i] = "docket"
        elif _ORIGIN.match(t):
            kinds[i] = "lower-court"
            # THE ORIGIN WRAPS, and its second row carries no landmark of
            # its own: 'APPEAL FROM ENVIRONMENTAL IMPROVEMENT BOARD and' /
            # 'THE ALBUQUERQUE BERNALILLO AIR QUALITY CONTROL BOARD'. The
            # wrap is set in the origin's CAPS, which nothing printed below
            # the origin uses — the judge, the firms and the cities are all
            # mixed case.
            j = i + 1
            while j < title and kinds[j] is None and _ALLCAPS.match(txt[j]) \
                    and not _DOCKET.match(txt[j]) \
                    and not _ORIGIN.match(txt[j]):
                kinds[j] = "lower-court"
                j += 1
        elif _FOR.match(t):
            kinds[i] = "counsel"
    # ---- pass 2: the captions, bounded by their status labels ------------
    # Each caption is the run ending at the LAST status label reachable
    # without crossing a pass-1 landmark, and beginning at the first row
    # above its first status label that no landmark separates from it.
    caps: list[tuple[int, int]] = []
    i = mast + 1
    while i < title:
        if kinds[i] is None and _STATUS.match(txt[i]):
            last = i
            j = i + 1
            while j < title and kinds[j] is None:
                if _STATUS.match(txt[j]):
                    last = j
                j += 1
            first = i
            while first - 1 > mast and kinds[first - 1] is None:
                first -= 1
            caps.append((first, last))
            i = last + 1
        else:
            i += 1
    for first, last in caps:
        for k in range(first, last + 1):
            kinds[k] = "caption"
        # THE MATTER APPEALED, under the parties: opens 'IN THE MATTER OF'
        # and closes on its own 'Case No. …' row where it prints one, and
        # otherwise where the origin begins.
        j, inside = last + 1, False
        while j < title and kinds[j] is None:
            if _MATTER.match(txt[j]):
                inside = True
            if not inside:
                break
            kinds[j] = "case-info"
            if _CASE_NO.search(txt[j]):
                inside = False
            j += 1
    # ---- pass 3: the judge under the origin, then the appearances --------
    for i in range(mast + 1, title):
        if kinds[i] != "lower-court":
            continue
        j = i + 1
        while j < title and kinds[j] is None and _JUDGE.search(txt[j]):
            kinds[j] = "lower-court"
            j += 1
    # BELOW A CAPTION AND ABOVE THE NEXT ONE the paper prints only the
    # origin, its judge and the appearances — the first two named
    # themselves in pass 1, so what is left is an appearance row (a firm, a
    # lawyer, a city, or the continuation of an attribution that wrapped:
    # 'for Intervenors-Appellees Southwest Energy Efficiency Project,' runs
    # over six rows on n.m._auto._dealers_assoc p3). Above the FIRST
    # caption nothing is left to name, and a row there is left for core
    # rather than guessed at.
    first_cap_end = caps[0][1] if caps else None
    for i in range(mast + 1, title):
        if kinds[i] is None and first_cap_end is not None \
                and i > first_cap_end:
            kinds[i] = "counsel"

    if not caps:
        return NOTHING

    # ---- emit -----------------------------------------------------------
    ctx = _Ctx()
    counsel: list[str] = []
    caption_rows: list[str] = []
    lower: list[str] = []
    dockets: list[str] = []
    lower_dockets: list[str] = []
    citation = ""
    for i in range(0, title + 1):
        kind = kinds[i]
        pieces = rows[i]
        if kind is None:
            continue
        if kind in ("#notice", "#stamp"):
            ctx.drop(pieces, "notice" if kind == "#notice" else "stamp")
            continue
        if kind == "court":
            ctx.crit.setdefault("court", txt[i])
            ctx.emit(pieces, "court", centre=True)
            continue
        if kind == "title":
            ctx.crit.setdefault("title", txt[i])
            ctx.emit(pieces, "title", centre=True)
            ctx.anchor.update(l.id for l in pieces)
            continue
        if kind == "citation":
            # THE PUBLIC-DOMAIN CITATION, and only where the Court has
            # filled the slot: '__________' is a blank, not a value.
            value = _norm(_CITE.match(txt[i]).group(1)).strip("_ ")
            if _CITE_VALUE.match(value):
                citation = value
                ctx.crit.setdefault("citation", value)
            ctx.emit(pieces, "citation", centre=False)
            continue
        if kind == "date":
            value = _norm(_DATE.match(txt[i]).group(1))
            if value:
                ctx.crit.setdefault("decision_date", value)
            ctx.emit(pieces, "date", centre=False)
            continue
        if kind == "docket":
            dockets.append(_norm(_DOCKET.match(txt[i]).group(1)))
            ctx.emit(pieces, "docket", centre=False)
            continue
        if kind == "lower-court":
            lower.append(txt[i])
            if _JUDGE.search(txt[i]):
                ctx.crit.setdefault("lower_court_judge", txt[i])
            else:
                ctx.crit.setdefault("lower_court", txt[i])
            ctx.emit(pieces, "lower-court", centre=False)
            continue
        if kind == "case-info":
            found = _CASE_NO.search(txt[i])
            if found and _norm(found.group(0)) not in lower_dockets:
                lower_dockets.append(_norm(found.group(0)))
            ctx.emit(pieces, "case-info", centre=False)
            continue
        if kind == "caption":
            caption_rows.append(txt[i])
            ctx.emit(pieces, "caption", centre=False)
            continue
        if kind == "counsel":
            counsel.append(txt[i])
            ctx.emit(pieces, "counsel", centre=False)
            continue

    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if len(dockets) > 1:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if lower_dockets:
        ctx.crit.setdefault("lower_court_docket", lower_dockets)
    if lower:
        ctx.crit.setdefault("history", " ".join(lower)[:2000])
    # THE PRINTED FORM BESIDE THE PARSED FORM: the caption rows verbatim,
    # and the case name built from the party names either side of the pivot
    # in the FIRST group.
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    sides = _sides(txt, caps[0])
    if sides:
        ctx.crit.setdefault("parties", sides)
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    else:
        # A MATTER HAS NO PIVOT. 'IN THE MATTER OF PETITION FOR EXPUNGEMENT
        # FOR C.T.,' is the whole caption above a single status label, so
        # the name is the party rows joined — there is no second side to
        # find and none is invented.
        only = _single(txt, caps[0])
        if only:
            ctx.crit.setdefault("parties", [only])
            ctx.crit.setdefault("case_name", only)
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE; its text is copied
    # into criteria.attorneys, which core fills only from a moved block
    # (core-patch-queue item 41).
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    # WHAT THE PAPER IS, and what the notice we just dropped said about it.
    # THE NOTICE IS THE ONLY PLACE THE MEMORANDUM PAPER STATES ITS STATUS,
    # so claiming it as furniture would lose that fact unless the reader
    # states it back.
    style = notice_kind or STYLE_PUBLISHED
    if style == STYLE_MEMORANDUM:
        ctx.crit.setdefault("publication_status", "unpublished")
    elif style == STYLE_PUBLISHED and citation:
        # The slip notice states the rule in terms: the vendor-neutral
        # citation is assigned 'once an opinion is selected for publication
        # by the Court'. A filled slot IS that selection.
        ctx.crit.setdefault("publication_status", "published")
    ctx.crit.setdefault("headmatter_style", style)
    return ctx.result()


def _sides(txt: list[str], span: tuple[int, int]) -> list[str]:
    """The LEAD party either side of the first caption's pivot. Each side
    runs from its first name row to its own status label — the label closes
    the party group, and everything after it is a co-party or an
    intervenor (n.m._auto._dealers_assoc sets fourteen of them)."""
    first, last = span
    pivot = next((i for i in range(first, last + 1) if _PIVOT.match(txt[i])),
                 None)
    if pivot is None:
        return []
    out = []
    for lo, hi in ((first, pivot), (pivot + 1, last + 1)):
        names = []
        for i in range(lo, hi):
            if _STATUS.match(txt[i]):
                break                    # the party group closes
            if _JOINER.match(txt[i]) or _PIVOT.match(txt[i]) \
                    or _MATTER.match(txt[i]):
                break
            names.append(txt[i])
        joined = " ".join(names).strip().rstrip(",;")
        if joined:
            out.append(joined)
    return out if len(out) == 2 else []


def _single(txt: list[str], span: tuple[int, int]) -> str:
    """The one party of a caption that prints no pivot at all."""
    first, last = span
    if any(_PIVOT.match(txt[i]) for i in range(first, last + 1)):
        return ""
    names = [txt[i] for i in range(first, last + 1)
             if not _STATUS.match(txt[i]) and not _JOINER.match(txt[i])]
    return " ".join(names).strip().rstrip(",;")


def _rows(pm, finder) -> list[list]:
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


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: set[int] = set()
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

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": sorted(self.anchor), "doc_type_final": None}
