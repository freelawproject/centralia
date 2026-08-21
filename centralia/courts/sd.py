"""Supreme Court of South Dakota ('sd').

Everything unique to sd lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py (byline style 'prose'; titles Justice / Chief Justice /
Retired Justice).

THE CONTRACT — 'asterisk ladder'. South Dakota flushes a clerk's docket line
and its own public-domain citation to the left rail, centers a three-row
masthead under them, and then runs FIVE zones down the page in a fixed
order. On 37 of 50 records each zone is fenced by a centered '* * * *'; on
the other 13 the same zones stand in the same order with nothing between
them but a wider band of air. THE ORDER AND THE COLUMNS ARE THE CONTRACT —
the fences are decoration, which is why this reader never counts them.

    ┌────────────────────────────────────────────────────────────────────┐
    │ #30970-a-PJD                                    docket (+ clerk's  │
    │ 2026 S.D. 12                                    code) then the cite│
    │                  IN THE SUPREME COURT                              │
    │                       OF THE                    the masthead       │
    │               STATE OF SOUTH DAKOTA                                │
    │                      * * * *                                       │
    │ GROVES LAW OFFICE,           │ Plaintiffs and Appellants,          │
    │            v.                │                    the caption:     │
    │ GOODSELL & OVIATT, LLP,      │ Defendant and Appellee.   two cols  │
    │                      * * * *                                       │
    │            APPEAL FROM THE CIRCUIT COURT OF                        │
    │              THE SEVENTH JUDICIAL CIRCUIT       where it came from  │
    │            PENNINGTON COUNTY, SOUTH DAKOTA                         │
    │                      * * * *                                       │
    │              THE HONORABLE STACY L. WICKRE      who tried it        │
    │                        Judge                                       │
    │                      * * * *                                       │
    │ JOHN K. NOONEY               │                                     │
    │ Nooney & Solay, LLP          │                  the appearances     │
    │ Rapid City, South Dakota     │ Attorneys for plaintiffs and        │
    │                              │ appellants.                         │
    │                      * * * *                                       │
    │                              │ ARGUED                              │
    │                              │ MARCH 19, 2026    the dates         │
    │                              │ OPINION FILED 05/06/26              │
    └────────────────────────────────────────────────────────────────────┘

THE COLUMNS ARE EXACT AND THEY ARE THE PARSER. Measured on all 50 records:
the page is 612pt, the left rail is x0 = 72.0, the second column's rail is
x0 = 360.0 on EVERY row that leaves the left column (min 360.0, max 360.0 —
not a tolerance, an invariant), and the pivot 'v.' sits alone at x0 = 108.0
on every record that prints one. The left column's ink never passes
x1 = 344.9, so the gutter is the band 345–360 and a row that crosses it is
either axis-centered (masthead, origin, judge, an in-re caption) or is not
this paper.

WHAT EACH ZONE IS READ BY — a landmark, never an ordinal:

  docket   row 1 at the rail, '#30970-a-PJD' / '#30787, #30788-r-JMK' /
           '#30954, #30955, #30956, #30957, #30958, #30959' (six on
           state_v._ware). All 50 records open with one.
  citation row 2 at the rail, '2026 S.D. 12'. All 50, and BOLD on all 50 —
           the only bold row on the page. It is the court's own
           public-domain cite, so it takes `criteria.citation`; putting it
           in `docket_number` would displace a real value.
  court    the three centered rows 'IN THE SUPREME COURT' / 'OF THE' /
           'STATE OF SOUTH DAKOTA', on all 50. The caption band opens
           where the third of them ends — not at a row number, because the
           masthead starts at top=82.9 on most records and at 140.6 on
           advisory_opinion.
  caption  everything between the masthead and the origin landmark. Two
           forms, both just 'caption' rows: party v. party in the two
           columns, and a centered in-re block ('IN THE MATTER OF THE
           PETITION OF SIGRID KRISTIANE NIELSEN…', 'THE PEOPLE OF THE
           STATE OF SOUTH DAKOTA / IN THE INTEREST OF / J.A.D., III…').
  lower    'APPEAL FROM THE CIRCUIT COURT OF' (49 records) opens it, then
  court    centered continuations ('THE SEVENTH JUDICIAL CIRCUIT',
           'PENNINGTON COUNTY, SOUTH DAKOTA'), then 'THE HONORABLE …' and
           a bare 'Judge' / 'Retired Judge' (49 records).
  case-info 'ORIGINAL PROCEEDING' (advisory_opinion) sits in the origin
           zone but names no court below, so it is case-info, not
           lower-court, and that record has no judge row at all.
  counsel  opens at the FIRST row back at the left rail once the origin
           zone has been entered, and runs to the end of the claim. Each
           entry is a left-column run (counsel, firm, city) beside a
           right-column phrase naming who they appeared for.
  date     the right column's own label/value ladder: 'ARGUED' (25) or
           'CONSIDERED ON BRIEFS' (25), optionally 'REASSIGNED' (2, both
           state_v._huante), each followed by a spelled date, then
           'OPINION FILED 05/06/26' — one on every one of the 50.

THE DATES ARE NOT THE LAST ZONE. On sleep_v._steele the whole counsel block
is pushed to page 2 and the dates print above it on page 1; on
culhane_v._thovson and state_v._spry the dates print at the foot of page 1
and the counsel block RESUMES on page 2 under a fence. So the walk cannot
close on the dates, and the bands are not a strict sequence — every row is
identified by its own landmark and column, with band state used only where a
column alone is ambiguous (a left-rail row is a party name in the caption
zone and an attorney below the origin zone; a right-column row is a party
status above the origin and a representation phrase below it).

WHERE THE CLAIM ENDS. Four stops, in this order of appearance:

  * the byline — 'DEVANEY, Justice', 'JENSEN, Chief Justice',
    'KERN, Retired Justice', 'SALTER, Justice (on reassignment).';
  * a paragraph mark — South Dakota numbers its paragraphs '[¶1.]' and
    prints the mark AT the body rail (x0 72.0–111.4) with the paragraph's
    first line beside it at x0 = 144.0, same row. pdfio welds the two into
    one line, so core's `_is_para_mark` sees '[¶1.] Sigrid Nielsen…' and
    opens the paragraph correctly. The number is NOT in the margin and
    nothing in core needs changing for it;
  * 'Table of Contents' — save_centennial_valley prints a dotted-leader
    contents page between the headmatter and the opinion. Its rows are
    claimed but deliberately left UNTAGGED: `HmLine.role` has no honest
    role for a contents list, and stopping on it instead costs a writing
    (see the walk);
  * a page above the first that carries the RUNNING HEAD. sd prints the
    short docket ('#31120') in the top band only on the opinion's pages —
    the pages that still carry headmatter print no head at all
    (culhane p2 opens with a fence at top 39.6, sleep p2 with counsel at
    68.4). advisory_opinion is why this stop is needed: its page 2 carries
    the running head and then a centered all-caps restatement of the
    Governor's question, axis-centered and no wider than that record's own
    caption, so no geometric test separates the two. It is left to core.

THE CLAIM IS CONTIGUOUS by construction: every row from the docket to the
last claimed row is either emitted, or emitted as the typed rule it draws
('* * * *' and the full-measure '- - - -' that divides state_v._spry's two
consolidated captions), or recorded as furniture by FurnitureFinder. The
walk breaks out of BOTH loops at the first stop, so it cannot leave a hole
and let the bisection invariant pull the block into a writing.

WHAT IS READ AND NOT RECORDED. The docket line's tail is the clerk's:
'-a-', '-r-', '-aff in pt & rev in pt-', '-aff in pt, vacate in pt, & rem-',
'-vacate & dismiss-' followed by the author's initials (PJD, SPM, JMK, SRJ,
MES, RG). It states the disposition and the author in an abbreviation table
that is not printed anywhere on the paper, so expanding 'a' to 'affirmed'
would be a decode and not a reading; the tail is stripped off the docket
numbers and no `disposition` is claimed from it. The row itself is emitted
verbatim, so nothing is lost from the render.

THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
has no `docket` field and no `argued` field: the docket is `docket_number`
(a string) plus `other_dockets` (the rest), and an argued or on-briefs date
belongs in `submitted`. Written under any other name they would be attached
by setattr and never serialized.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# --- the measured page ----------------------------------------------------
# 612pt paper on all 50 records; the axis is 306.
_AXIS_TOL = 14.0
# The second column's rail. Measured across all 50 records and both of the
# pages a record's headmatter can occupy: every row that leaves the left
# column starts at x0 = 360.0 exactly (min 360.0, max 360.0).
# x0 = 360.0; the test is the GUTTER between the columns, 345–360, which the
# left column's ink never enters on any of the 50 records.
_GUTTER = 350.0
# The left rail is 72.0; a firm-name wrap is set one indent in at 88.7/88.8
# ('& Simmons, L.L.P.', 'Hinrichs & Tysdal, LLP').
_RAIL_TOL = 20.0
# Headmatter is confined to the first two pages: the longest counsel block
# in the corpus (culhane_v._thovson) ends at top 183.8 of page 2.
_MAX_PAGES = 2

# '#31355' / '#30970-a-PJD' / '#30787, #30788-r-JMK' / six numbers on
# state_v._ware. Group 1 is the numbers; anything after the following '-' is
# the clerk's disposition code and the author's initials.
_DOCKET = re.compile(r"^(#\d{4,6}(?:\s*,\s*#\d{4,6})*)(?:-.*)?$")
# '2026 S.D. 12' — the court's own public-domain cite, bold on all 50.
_CITE = re.compile(r"^\d{4}\s+S\.\s?D\.\s+\d+[A-Z]?$")
_MASTHEAD = ("IN THE SUPREME COURT", "OF THE", "STATE OF SOUTH DAKOTA")
# The centered fence, measured x0 289.0-323.0 on the axis, 183 rows in all.
_FENCE = re.compile(r"^\*(?:\s+\*)+$")
# state_v._spry divides its two consolidated captions with a full-measure
# typed dash rule, x0 72.0-537.8.
_DASH_RULE = re.compile(r"^-(?:\s+-)+$")
# 'APPEAL FROM THE CIRCUIT COURT OF' on 49 records; the 50th is
# 'ORIGINAL PROCEEDING' (advisory_opinion), which names no court below.
_APPEAL_FROM = re.compile(r"^APPEAL FROM\b|^CERTIFICATION FROM\b", re.I)
_ORIGINAL = re.compile(r"^ORIGINAL PROCEEDING\b|^ORIGINAL ACTION\b", re.I)
_HONORABLE = re.compile(r"^THE HONORABLE\b", re.I)
# The origin zone's own continuations, and there are only these two forms in
# the whole corpus: the circuit and the county, both naming the court system
# and neither ever saying anything else. Bounding the zone to them matters —
# left open ('band == origin and centered'), the rule swallowed
# advisory_opinion's centered restatement of the Governor's question on page
# 2 and tinted three rows of it 'lower court'.
_ORIGIN_CONT = re.compile(
    r"^THE [A-Z]+ JUDICIAL CIRCUIT$|^[A-Z][A-Z’' ]* COUNTY, SOUTH DAKOTA$")
# The bare title row beneath the trial judge's name: 'Judge' on 47 records,
# 'Retired Judge' on 2.
_JUDGE_TITLE = re.compile(
    r"^(?:Retired|Acting|Presiding|Circuit|Senior)?\s*Judges?$", re.I)
# The right column's date ladder. 'ARGUED' 25, 'CONSIDERED ON BRIEFS' 25,
# 'REASSIGNED' 2 — each on its own row above a spelled date.
_DATE_LABEL = re.compile(
    r"^(ARGUED|REARGUED|CONSIDERED ON BRIEFS|SUBMITTED ON BRIEFS"
    r"|SUBMITTED|RESUBMITTED|REASSIGNED)$")
_DATE_VALUE = re.compile(r"^[A-Z][A-Za-z]+\s+\d{1,2},\s+\d{4}$")
_FILED = re.compile(r"^OPINION FILED\s+(\S+)$")
# ARGUED and CONSIDERED ON BRIEFS both answer 'when was it submitted'; the
# model has no `argued` field and the render labels `submitted`
# 'argued/submitted'. REASSIGNED is procedural history, not a submission.
_SUBMITTED_LABELS = {"ARGUED", "REARGUED", "CONSIDERED ON BRIEFS",
                     "SUBMITTED ON BRIEFS", "SUBMITTED", "RESUBMITTED"}
# The byline, which ends the claim. Measured forms: 'DEVANEY, Justice',
# 'JENSEN, Chief Justice', 'KERN, Retired Justice', 'MYREN, Justice',
# 'GUSINSKY, Justice', 'SALTER, Justice (on reassignment).'
_BYLINE = re.compile(
    r"^[A-Z][A-Z’'.\-]+(?:\s+[A-Z][A-Z’'.\-]+)*,\s+"
    r"(?:Chief\s+|Retired\s+|Acting\s+)?Justices?\b")
_PARA = re.compile(r"^\[?\s*¶")
# save_centennial_valley's own contents page, between block and opinion.
_TOC = re.compile(r"^Table of Contents$", re.I)
# The running head: the short docket alone in the top band. It marks the
# opinion's pages — a page still carrying headmatter prints none.
_RUNNING_HEAD = re.compile(r"^#\d{4,6}(?:\s*,\s*#\d{4,6})*$")
_HEAD_BAND = 60.0
# The pivot, alone at x0 = 108.0 on every record that prints one.
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="sd")
def read_headmatter_sd(model, geom, **_):
    """Read South Dakota's asterisk ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    width = model.pages[0].width or 612.0

    # THE DISPATCH: the three-row masthead, wherever the docket line above
    # it happens to leave it. Never an ordinal — the masthead's top runs
    # 82.9 on most records and 140.6 on advisory_opinion, and the docket
    # line is one row on 49 records.
    first = _rows(model.pages[0], finder)
    mast = [i for i, g in enumerate(first[:8])
            if _norm(" ".join(l.plain for l in g)) in _MASTHEAD]
    if len(mast) != 3 or mast != list(range(mast[0], mast[0] + 3)):
        return NOTHING
    if not _DOCKET.match(_norm(" ".join(l.plain for l in first[0]))):
        return NOTHING

    ctx = _Ctx()
    band = "ident"              # ident | caption | origin | counsel
    label: str | None = None    # the date label awaiting its value
    left_run: list[str] = []    # caption rows in the left column, in order
    right_run: list[str] = []   # caption rows in the second column
    centre_run: list[str] = []  # a centered in-re caption
    below: list[str] = []       # the origin zone, as printed
    judge: list[str] = []
    counsel: list[str] = []
    printed: list[str] = []     # every caption row, as printed
    pivot_at: int | None = None
    lead_case = True            # inside the FIRST of consolidated captions
    stop = False

    for page in model.pages[:_MAX_PAGES]:
        rows = first if page is model.pages[0] else _rows(page, finder)
        # A page above the first that prints the running head is the
        # opinion's page, whatever else it carries.
        if page is not model.pages[0] and _has_running_head(page):
            break
        for group in rows:
            pieces = sorted(group, key=lambda l: l.x0)
            text = _norm(" ".join(l.plain for l in pieces))
            if not text:
                continue
            lead = pieces[0]
            x1 = max(l.x1 for l in pieces)
            single = len(pieces) == 1
            centred = (single
                       and abs((lead.x0 + x1) / 2 - width / 2) <= _AXIS_TOL)
            at_rail = abs(lead.x0 - body_x0) <= _RAIL_TOL
            in_col2 = lead.x0 >= _GUTTER

            # --- the stops -----------------------------------------------
            if _PARA.match(text) or (band not in ("ident", "contents")
                                     and at_rail and _BYLINE.match(text)):
                stop = True
                break
            # THE CONTENTS PAGE IS CLAIMED BUT NOT IDENTIFIED. There is no
            # honest role for a table of contents in `HmLine.role`, so its
            # rows are emitted UNTAGGED — which reports truthfully as
            # unread rather than tinting them with a role that would be a
            # guess. They are CLAIMED rather than stopped on, because
            # stopping here costs a writing: its first entry
            # 'JENSEN, Chief Justice ……… 1' is byline-shaped, so core opens
            # a second, unauthored `order` on it (measured: 74 writings
            # across the corpus instead of 73). Claimed, the same
            # byline-shaped row still opens the majority a page early and
            # the bisection invariant pulls these rows into it — which is
            # exactly what core did before this reader existed, so the
            # writings are unchanged.
            if _TOC.match(text):
                band = "contents"
            if band == "contents":
                ctx.emit(pieces, "", centre=False)
                continue

            # --- what the page DRAWS between the zones -------------------
            if _FENCE.match(text):
                ctx.rule(lead.page, tuple(p.id for p in pieces), "center")
                continue
            if _DASH_RULE.match(text):
                # state_v._spry stacks TWO captions and divides them with
                # this rule. Only the first names the lead case (#30787, the
                # docket the record is filed under), so the parsed name is
                # built from that one; joined across the rule it read
                # 'STATE OF SOUTH DAKOTA, RICHARD SPRY, STATE OF SOUTH
                # DAKOTA v. SUSAN SPRY'. `caption` keeps every printed row.
                lead_case = False
                ctx.rule(lead.page, tuple(p.id for p in pieces), "full")
                continue

            # --- the identifiers, wherever they print --------------------
            docket = _DOCKET.match(text)
            if docket and (band == "ident" or centred):
                # advisory_opinion repeats '#31355' centered inside the
                # caption zone; the rail copy above the masthead is the one
                # that sets the criteria.
                numbers = [t.strip() for t in docket.group(1).split(",")
                           if t.strip()]
                ctx.crit.setdefault("docket_number", numbers[0])
                if numbers[1:]:
                    ctx.crit.setdefault("other_dockets", numbers[1:])
                ctx.emit(pieces, "docket", centre=centred)
                continue
            if band == "ident" and _CITE.match(text):
                ctx.crit.setdefault("citation", text)
                ctx.emit(pieces, "citation", centre=False)
                continue
            if band == "ident" and text in _MASTHEAD:
                ctx.crit.setdefault("court", "Supreme Court of the State of "
                                             "South Dakota")
                ctx.emit(pieces, "court")
                if text == _MASTHEAD[-1]:
                    band = "caption"
                continue

            # --- the dates, which are not the last zone ------------------
            if in_col2 and _DATE_LABEL.match(text):
                label = text
                ctx.emit(pieces, "date", centre=False)
                continue
            if in_col2 and label and _DATE_VALUE.match(text):
                if label in _SUBMITTED_LABELS:
                    ctx.crit.setdefault("submitted", text)
                else:
                    ctx.crit.setdefault(
                        "history", f"{label.title()} {text}")
                label = None
                ctx.emit(pieces, "date", centre=False)
                continue
            filed = _FILED.match(text)
            if in_col2 and filed:
                ctx.crit.setdefault("decision_date", filed.group(1))
                label = None
                ctx.emit(pieces, "date", centre=False)
                continue

            # --- where it came from, and who tried it --------------------
            if band in ("ident", "caption") and _APPEAL_FROM.match(text):
                band = "origin"
                below.append(text)
                ctx.emit(pieces, "lower-court", centre=centred)
                continue
            if band in ("ident", "caption") and _ORIGINAL.match(text):
                # No court below: this record came here first.
                band = "origin"
                ctx.emit(pieces, "case-info", centre=centred)
                continue
            if band == "origin" and _HONORABLE.match(text):
                judge.append(text)
                ctx.emit(pieces, "lower-court", centre=centred)
                continue
            if band == "origin" and judge and centred \
                    and _JUDGE_TITLE.match(text):
                judge.append(text)
                ctx.emit(pieces, "lower-court", centre=centred)
                continue
            if band == "origin" and not judge and centred \
                    and _ORIGIN_CONT.match(text):
                # 'THE SEVENTH JUDICIAL CIRCUIT' / 'PENNINGTON COUNTY,
                # SOUTH DAKOTA' — the origin's own continuations.
                below.append(text)
                ctx.emit(pieces, "lower-court", centre=True)
                continue

            # --- the appearances ------------------------------------------
            # The counsel band opens at the first row back at the left rail
            # once the origin zone has been entered, and it uses exactly the
            # two columns the caption used.
            if band == "origin" and at_rail:
                band = "counsel"
            if band == "counsel" and (at_rail or in_col2) and x1 <= width:
                counsel.append(text)
                ctx.emit(pieces, "counsel", centre=False)
                continue

            # --- the caption ---------------------------------------------
            if band == "caption":
                if _PIVOT.match(text) and single:
                    if lead_case:
                        pivot_at = len(left_run)
                    ctx.emit(pieces, "caption", centre=False)
                    continue
                for part in pieces:
                    piece = _norm(part.plain)
                    if not piece:
                        continue
                    printed.append(piece)
                    if not lead_case:
                        continue
                    if part.x0 >= _GUTTER:
                        right_run.append(piece)
                    elif centred:
                        centre_run.append(piece)
                    else:
                        left_run.append(piece)
                ctx.emit(pieces, "caption", centre=centred)
                continue

            # A ROW AT NO POSITION THIS PAPER USES is left to core rather
            # than tinted with a role that would be a guess.
            continue
        if stop:
            break

    if not ctx.crit.get("docket_number") or not ctx.crit.get("citation"):
        return NOTHING
    # THE PRINTED FORM BESIDE THE PARSED FORM.
    if printed:
        ctx.crit.setdefault("caption", printed)
    if pivot_at is not None and left_run:
        # Built from the party names either side of the pivot, never by
        # joining caption rows wholesale.
        lhs = _norm(" ".join(left_run[:pivot_at])).rstrip(",")
        rhs = _norm(" ".join(left_run[pivot_at:])).rstrip(",.")
        if lhs and rhs:
            ctx.crit.setdefault("case_name", f"{lhs} v. {rhs}")
            ctx.crit.setdefault("parties", [lhs, rhs])
    elif centre_run:
        ctx.crit.setdefault("case_name",
                            _norm(" ".join(centre_run)).rstrip("."))
    if below:
        # The recital names an ACTION ('APPEAL FROM …'); the field wants the
        # court, so the opening phrase comes off and the rest stands as the
        # origin printed it.
        ctx.crit.setdefault(
            "lower_court",
            re.sub(r"^(?:APPEAL|CERTIFICATION) FROM\s+", "",
                   _norm(" ".join(below))))
    if judge:
        # 'THE HONORABLE MICHELLE K. COMER' over a bare 'Judge'.
        ctx.crit.setdefault("lower_court_judge", ", ".join(judge))
    if counsel:
        ctx.crit.setdefault("attorneys", "\n".join(counsel))
    ctx.crit.setdefault("headmatter_style", "asterisk-ladder")
    return ctx.result()


def _has_running_head(pm) -> bool:
    """The short docket alone in the top band — sd prints it only on the
    opinion's pages, never on a page still carrying headmatter.

    Measured on the page's RAW lines, not on `_rows`: FurnitureFinder has
    already removed the running head by then, so the filtered rows of
    advisory_opinion's page 2 open with the Governor's question and the page
    reads as headmatter that is still running.
    """
    for line in pm.lines:
        if line.top > _HEAD_BAND:
            continue
        if _RUNNING_HEAD.match(_norm(line.plain)):
            return True
    return False


def _rows(pm, finder) -> list[list]:
    """The page's visual rows, furniture already removed. Same-top pieces
    stay together: sd sets a party name and its status, or an appearance and
    who it was for, on ONE row in two columns."""
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
        self.crit: dict = {}

    def emit(self, group: list, role: str, centre: bool = True) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        lead = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(lead.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=lead.x0, size=lead.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int, ids: tuple = (), span: str = "center") -> None:
        self.items.append(m.Rule(prov=m.Prov(page, ids), typed=True,
                                 span=span))
        self.consumed.update(ids)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
