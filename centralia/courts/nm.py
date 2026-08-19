"""Supreme Court of the State of New Mexico ('nm').

Everything unique to nm lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — New Mexico prints a LADDER of four identifiers, then one
group per appeal, and closes the block by naming the paper on the page axis.
Every row of it stands at the body rail; nothing is fenced, nothing is
centred except the masthead and the paper's own name.

    ┌────────────────────────────────────────────────────────────────────┐
    │ The slip opinion is the first version of an opinion released by …   │  the
    │ Supreme Court. Once an opinion is selected for publication by …     │  clerk's
    │ assigned a vendor-neutral citation by the Chief Clerk for …         │  notice
    │ 112 NMRA, authenticated and formally published. The slip opinion …  │  (slip
    │ deviations from the formal authenticated opinion.                   │  paper)
    │                                                                    │
    │         IN THE SUPREME COURT OF THE STATE OF NEW MEXICO   masthead │
    │ Opinion Number: 2025-NMSC-013                     the neutral cite │
    │ Filing Date: January 16, 2025                      the filing date │
    │ No. S-1-SC-39432                                        the docket │
    │                                                                    │
    │ SOUTHWESTERN PUBLIC                                                │
    │ SERVICE COMPANY,                                                   │
    │        Appellant,                                     the caption  │
    │ and                                                                │
    │ EL PASO ELECTRIC COMPANY,                                          │
    │        Intervenors-Appellants,                                     │
    │ v.                                                                 │
    │ NEW MEXICO PUBLIC                                                  │
    │ REGULATION COMMISSION,                                             │
    │        Appellee,                                                   │
    │ In the Matter of the Commission's                     the matter   │
    │ Adoption of Rules Pursuant to the                     appealed,    │
    │ Community Solar Act, NMPRC                            with the     │
    │ Case No. 21-00112-UT                                  number below │
    │ APPEAL FROM THE NEW MEXICO PUBLIC REGULATION COMMISSION  the origin│
    │ Nancy J. Franchini, District Judge                    …and its judge│
    │                                                                    │
    │ Peifer, Hanson, Mullins & Baker, PA                                │
    │ Charles R. Peifer                                     the          │
    │ Albuquerque, NM                                       appearances  │
    │ for Petitioners                                       (each ENDS   │
    │ Ortiz & Zamora Attorneys at Law, LLC                   in 'for …') │
    │ …                                                                  │
    │ CONSOLIDATED WITH        ── the joiner; a second group follows ──   │
    │ No. S-1-SC-39558                                                   │
    │ … caption, origin, appearances again …                             │
    │                                                                    │
    │                            OPINION                     the title   │
    │ THOMSON, Chief Justice.                            (the paper begins)│
    └────────────────────────────────────────────────────────────────────┘

TWO PAPERS, ONE CONTRACT. 23 of the 50 records are SLIP opinions: a five-row
notice from the Chief Clerk above the masthead ('The slip opinion is the
first version …'; four rows on murphy_v._oreilly, where the wrap differs),
a bare 'Opinion Number:' with no value, numbered stationery in the left
margin, and a 14pt measure. The other 27 are the PUBLISHED versions: no
notice, no line numbers, a 12pt measure, and 'Opinion Number: 2025-NMSC-013'
filled in — the court's own vendor-neutral citation, which takes the
`citation` role. Below the fourth row the two papers are identical, so the
reader dispatches on the MASTHEAD and never on an ordinal: the notice moves
every row beneath it by five.

THE NOTICE IS FURNITURE. It is the Chief Clerk's standing warning about
authentication, printed identically above the masthead on every slip record
and on no published one. Dropped, never tinted.

THE BLOCK ENDS WHERE THE PAPER NAMES ITSELF. 'OPINION' centred on the page
axis (x0 275.3 on slip paper, 280.7 on published, page centre 306.0) closes
the block on all 50 records, on pages 1 through 6. It is the `title` — what
the paper calls ITSELF — and it is offered back as `anchor_ids`, because on
an unsigned record it is also the only row a writing could open on. The
byline below it ('THOMSON, Chief Justice.') is the writing's, not the
block's, and the reader never reaches it.

HOW THE CAPTION IS BOUNDED — THE PROBLEM THIS PAPER SETS. Caption rows and
counsel rows stand at the SAME rail (72.0) in the SAME type, and the paper
draws no rule between them. Two closed vocabularies bound the caption:

  * its LAST row is a party STATUS label ('Appellant,', 'Defendants.',
    'Real Parties in Interest.', 'Necessary Party-Petitioner,') — a finite
    vocabulary, and on this paper the status label is sometimes indented to
    108.0 (the published family) and sometimes flush at the rail (the slip
    family, aragon_v._martinez), so the INDENT cannot be the test;
  * its FIRST row is found by walking back from that label to the last
    landmark above it — the docket, the joiner, the filing date, or a
    'for …' appearance-attribution row.

An appearance block always CLOSES with its attribution ('for Petitioner
Shook, Hardy & Bacon LLP'), which is what makes the walk-back terminate
even where a consolidated group prints no joiner and no docket of its own
(el_paso_elec…_1 p4: 'for Intervenor New Mexico Office of the Attorney
General' is immediately followed by 'SOUTHWESTERN PUBLIC').

Below the status label the caption may carry the MATTER appealed — a run
opening 'In the Matter of' and closing on a 'Case No. 22-00020-UT' row,
which is the number of the proceeding BELOW (5 records, 72 rows). It reads
as `case-info`: caption apparatus, not a party and not the deciding court's
own number.

CONSOLIDATION TAKES THREE FORMS, all measured on shook_v._wilson_1 (three
dockets) and sw._pub._serv…_1 (five): 'CONSOLIDATED WITH', a bare 'AND',
and nothing at all. The joiners are matched CASE-SENSITIVELY — the
caption's own joiner between co-parties is a lower-case 'and' at the rail
(sw rows 7 and 16), and folding the two would split a caption in half.

WHY THE CLAIM RUNS EDGE TO EDGE. Every row from the masthead through
'OPINION' is claimed — court, citation, date, docket, caption, case-info,
lower-court, counsel, title — with no hole in between, because a row left
unclaimed inside the span lets core open a writing there and the bisection
invariant (pipeline.py:2055) then pulls the whole block into it. Measured
over all 50 records this classification leaves ZERO rows in the span
unnamed, so the claim is contiguous by construction.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# THE DISPATCH. Centred on the axis on all 50 records (x0 104.6 on slip
# paper against a 14pt measure, 136.0 on published paper against 12pt).
_MASTHEAD = re.compile(r"^IN THE SUPREME COURT OF THE STATE OF NEW MEXICO$",
                       re.I)
# The block never runs past page 6 (sw._pub._serv…_1, five consolidated
# dockets, is the longest; the median record ends on page 2).
_MAX_PAGES = 6
_AXIS_TOL = 14.0

# 'Opinion Number: 2025-NMSC-013' — the court's own vendor-neutral cite,
# filled in on the 27 published records and printed EMPTY on the 23 slip
# records, whose citation Rule 23-112 NMRA assigns later.
_CITE = re.compile(r"^Opinion Number:\s*(.*)$", re.I)
# 'Filing Date: January 16, 2025' — on 49 of 50; state_v._revels_1 omits it.
_DATE = re.compile(r"^Filing Date:\s*(.*)$", re.I)
# 'No. S-1-SC-39432' / 'NO. S-1-SC-40671' (the slip paper shouts it). Only
# the court's OWN number: 'NMPRC Case No. 21-00112-UT' below the caption is
# the number of the proceeding appealed from and is read as case-info.
_DOCKET = re.compile(r"^Nos?\.\s*(S-1-[A-Z]{2}-\d[\d\s,-]*)$", re.I)
# THE CONSOLIDATION JOINERS. 'CONSOLIDATED WITH' names itself; the bare
# joiner is printed 'AND' on shook_v._wilson_1 and sw._pub._serv…_1 but
# lower-case 'and' on el_paso_elec…_1 row 96 — the SAME string the caption
# uses between co-parties (rows 58 and 105 of that record). So the bare
# joiner is recognized by CONTEXT, never by its case: it is the row directly
# above a docket, and the caption's own 'and' never is.
_CONSOL = re.compile(r"^CONSOLIDATED WITH$")
_CONSOL_BARE = re.compile(r"^and$", re.I)
# WHERE THE APPEAL CAME FROM. 17 distinct wordings over 97 rows, all of
# them opening on one of these stems; the wording is the payload, the stem
# is the landmark.
_ORIGIN = re.compile(
    r"^(?:APPEAL FROM|APPEALS FROM|ORIGINAL PROCEEDING|CERTIFICATION FROM"
    r"|CERTIORARI TO|ON CERTIORARI|ON APPEAL FROM|DIRECT APPEAL"
    r"|PETITION FOR)\b")
# 'Nancy J. Franchini, District Judge' / 'Cindy Leos, District Judge' —
# printed directly under the origin on the 34 records with a trial court.
_JUDGE = re.compile(r",\s*(?:[A-Z][a-z]+\s+)*Judges?$")
# An appearance block's closing attribution: 'for Petitioners', 'for Amici
# Curiae New Mexico Foundation for Open Government', 'for Necessary
# Party-Petitioner Presbyterian Health Plan, Inc.'
_FOR = re.compile(r"^for\s+\S", re.I)
# WHAT THE PAPER CALLS ITSELF, centred on the page axis.
_TITLE = re.compile(r"^(?:OPINION|ORDER|DECISION|OPINION AND ORDER)$")
# The proceeding appealed from, printed under the parties and closing on its
# own number (city_of_las_cruces, el_paso_elec x2, sw._pub._serv x2).
_MATTER = re.compile(r"^In (?:the Matter of|the Application|re)\b", re.I)
_CASE_NO = re.compile(r"Case No\.\s*\S+$", re.I)
# PARTY STATUS — a closed vocabulary, and the caption's last row. Never a
# party NAME and never a firm name: those are open vocabularies.
_STATUS = re.compile(
    r"^(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|Appellants?"
    r"|Appellees?|Intervenors?|Relators?|Claimants?|Movants?|Cross-\w+"
    r"|Real Part(?:y|ies) in Interest|Amic(?:us|i) Curiae|Worker|Employer"
    r"|Insurer|Child|Children|Mother|Father"
    r"|(?:Necessary|Nominal|Indispensable) Part(?:y|ies)[\w-]*)"
    r"[A-Za-z\s,/&'’-]*[,.]$")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_JOINER = re.compile(r"^and$", re.I)
# A row set in the origin's capitals — no lower-case letter anywhere in it.
_ALLCAPS = re.compile(r"^[^a-z]*[A-Z][^a-z]*$")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="nm")
def read_headmatter_nm(model, geom, **_):
    """Read New Mexico's block, or NOTHING."""
    if not model.pages:
        return NOTHING
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

    # THE DISPATCH: the masthead, wherever the Chief Clerk's notice above it
    # happens to end (five rows on 22 records, four on murphy, none on the
    # 27 published ones). Never an ordinal.
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
    for i in range(mast):
        kinds[i] = "#notice"
    kinds[mast] = "court"
    kinds[title] = "title"
    # ---- pass 1: the rows that name themselves ---------------------------
    for i in range(mast + 1, title):
        t = txt[i]
        if _CITE.match(t):
            kinds[i] = "citation"
        elif _DATE.match(t):
            kinds[i] = "date"
        elif _DOCKET.match(t):
            kinds[i] = "docket"
        elif _CONSOL.match(t):
            kinds[i] = "case-info"
        elif _ORIGIN.match(t):
            kinds[i] = "lower-court"
            # THE ORIGIN WRAPS, and its second row carries no landmark of
            # its own: 'APPEAL FROM THE NEW MEXICO PUBLIC REGULATION' /
            # 'COMMISSION' (city_of_las_cruces, el_paso_elec), 'ORIGINAL
            # PROCEEDING ON PETITION FOR' / 'WRIT OF SUPERINTENDING
            # CONTROL' (johnson__johnson), 'CERTIFICATION FROM THE UNITED
            # STATES DISTRICT COURT FOR THE' / 'DISTRICT OF NEW MEXICO'
            # (smith_v._aaa). The wrap is set in the origin's CAPS, which
            # nothing printed below the origin uses — the judge, the firms
            # and the cities are all mixed case.
            j = i + 1
            while j < title and kinds[j] is None and _ALLCAPS.match(txt[j]) \
                    and not _CONSOL.match(txt[j]) \
                    and not _CONSOL_BARE.match(txt[j]) \
                    and not _DOCKET.match(txt[j]) \
                    and not _ORIGIN.match(txt[j]):
                kinds[j] = "lower-court"
                j += 1
        elif _FOR.match(t):
            kinds[i] = "counsel"
    # The bare consolidation joiner, by its position above a docket.
    for i in range(mast + 1, title - 1):
        if kinds[i] is None and _CONSOL_BARE.match(txt[i]) \
                and kinds[i + 1] == "docket":
            kinds[i] = "case-info"
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
        # THE MATTER APPEALED, under the parties: opens on 'In the Matter
        # of' and closes on its own 'Case No. …' row.
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
    # lawyer, a city). Above the FIRST caption nothing is left to name, and
    # a row there would be left for core rather than guessed at.
    first_cap_end = caps[0][1] if caps else None
    for i in range(mast + 1, title):
        if kinds[i] is None and first_cap_end is not None \
                and i > first_cap_end:
            kinds[i] = "counsel"

    # ---- emit -----------------------------------------------------------
    ctx = _Ctx()
    counsel: list[str] = []
    caption_rows: list[str] = []
    lower: list[str] = []
    dockets: list[str] = []
    lower_dockets: list[str] = []
    for i in range(0, title + 1):
        kind = kinds[i]
        pieces = rows[i]
        if kind is None:
            continue
        if kind == "#notice":
            ctx.drop(pieces, "notice")
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
            value = _norm(_CITE.match(txt[i]).group(1))
            if value:
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

    if not caps:
        return NOTHING
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
    # in the FIRST group — joining the rows wholesale would read
    # 'SOUTHWESTERN PUBLIC SERVICE COMPANY, Appellant, and EL PASO …'.
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    sides = _sides(txt, caps[0])
    if sides:
        ctx.crit.setdefault("parties", sides)
        if len(sides) == 2:
            ctx.crit.setdefault("case_name", " v. ".join(sides))
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE; its text is copied
    # into criteria.attorneys, which core fills only from a moved block.
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    ctx.crit.setdefault("headmatter_style", "nm ladder")
    return ctx.result()


def _sides(txt: list[str], span: tuple[int, int]) -> list[str]:
    """The LEAD party either side of the first caption's pivot. Each side
    runs from its first name row to its own status label — the label closes
    the party group, and everything after it is a co-party, an intervenor or
    a second nested proceeding (state_ex_rel._cyfd_v._calvin_t. sets a whole
    second 'v.' inside one caption). Joining a side wholesale reads
    'CALVIN T. JR., COREY T., v. PRESBYTERIAN HEALTH PLAN, INC., …'."""
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
