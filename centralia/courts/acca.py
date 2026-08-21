"""United States Army Court of Criminal Appeals ('acca').

The Army's Article 66 court, second of the service-CCA family in this engine
after `nmcca`. Every one of the 32 corpus records is captioned `United States
v. <servicemember>`, the panel is a panel of `Appellate Military Judges`, and
the case comes up from a court-martial convened by an Army headquarters. The
family resemblance to nmcca stops at the vocabulary: the two courts set
COMPLETELY different paper, and this file inherits nothing from that one.

    ┌──────────────────────────────────────────────────────────────────┐
    │                     CORRECTED COPY            a stamp (antepara)  │
    │ UNITED STATES ARMY COURT OF CRIMINAL APPEALS                      │
    │  ⟵ 16pt BOLD, the full text measure ⟶       THE MASTHEAD          │
    │                        Before                                     │
    │              MORRIS, JUETTEN, and MURDOUGH    the roster  10.5pt  │
    │                Appellate Military Judges      the bench           │
    │                                                                   │
    │                 UNITED STATES, Appellee       the caption 12pt    │
    │                           v.                                      │
    │                  Captain ALEX H. BEAN                             │
    │              United States Army, Appellant                        │
    │                                                                   │
    │                    ARMY 20240529              THE DOCKET          │
    │                                                                   │
    │ Headquarters, U.S. Army Center for Initial Military Training …    │
    │        Adam S. Kazin and Pamela L. Jones, Military Judges         │
    │      Colonel Catherine L. Brantley, Special Trial Counsel         │
    │                                          the court below          │
    │ For Appellant: Captain Emily R. Ittner, JA; …    the appearances, │
    │ brief); … Esquire (on reply brief).            AT THE BODY RAIL   │
    │ For Appellee: Colonel Richard E. Gorini, JA; …                    │
    │                     19 March 2026             the date            │
    │            ───────────────────────────        RULE (title measure)│
    │                  MEMORANDUM OPINION           the title  10.5pt   │
    │            ───────────────────────────        RULE (title measure)│
    │ This opinion is issued as an unpublished opinion and, as such,    │
    │ does not serve as precedent.              the publication status  │
    │ MURDOUGH, Judge:                          (the paper begins)      │
    └──────────────────────────────────────────────────────────────────┘

WHICH DIVIDER SHAPE THIS IS: **NONE, AND NO FENCE EITHER.** There is no
caption column divider — no drawn rail, no box, no typed `)` or `:` column —
and unlike nmcca there is no typed underscore fence anywhere on the sheet.
The cover is a SINGLE CENTRED LADDER hung under an engraved masthead, its
zones separated by nothing but white space. So no `CaptionBlock` is emitted
and no second column is invented.

**THIS IS THE `_fold_rail_caption(d["summary"], ")")` TRAP, AND IT IS REAL
HERE TOO.** The old engine's shared military base folds a `)`-railed caption
into EVERY service CCA's headmatter, and the nmcca port already measured that
fold as wrong for nmcca (core-patch-queue, 'nmcca: what the SERVICE-CCA family
will need, and one trap'). Measured again on acca: over the 22 records with a
readable cover, page 1 contains ZERO `)` glyphs standing as a caption column —
the only parentheses on the sheet are inside counsel entries (`(on brief)`)
and military-judge stages (`(arraignment & motions)`), all mid-row. The old
base's own comment says the rail belongs to acca/afcca ORDER paper; there is
no order paper in this corpus, and inheriting the fold would invent a rail on
every record.

THE DISPATCH IS THE MASTHEAD, AND IT IS GEOMETRY, NOT WORDING. The court
engraves its name across the head of page 1 in the largest type on the sheet
and runs it the whole text measure: 16.0pt on 20 records and 16.5pt on two
(santaella, erb), against a 12.0–12.5pt body, and 456–464pt wide on a
612–618pt page. So the test is 'the row nearest the top of page 1 set at
>=1.20x the body size and spanning >=0.70 of the page width', and the court's
own name is read off it as `criteria.court` rather than matched against. No
record has a second row that meets it: the next largest type on any cover is
the 13.0pt `v.` of ayuso, at 9.6pt wide. A record with no such row is not this
contract and the reader returns NOTHING.

TYPE SIZE SEPARATES THE PANEL FROM THE CAPTION, AND NOTHING ELSE HAS TO. The
ladder's two upper zones are both centred stacks of short rows, and the only
thing that tells them apart is the SIZE the court sets them at. Measured over
all 22 covers, the two populations are disjoint with a 1.5pt empty band
between them:

  * the panel band — `Before`, the roster, `Appellate Military Judges` — runs
    8.0 to 10.5pt (ayuso sets its `Before` at 8.0);
  * the caption band — the parties, the pivot, the service line — runs 12.0
    to 13.0pt.

So the caption is the run of rows immediately above the docket set at
`body_size - 1.0` or larger, and the panel is what is left above it. No row
is read by wording to find either. (The TITLE is small type too — 10.0 to
10.5 — which is exactly why it is placed by POSITION, below the date, and not
by size.)

THE DOCKET IS `ARMY 20240529` AND THE OCR BREAKS IT. Six records reach us as
a scan whose text layer splits the number — `ARMY 2024041 7`, `ARMY 2024053
8` — so the printed row is kept verbatim in the block and the internal spaces
are closed only in `criteria.docket_number`. This court assigns no
public-domain citation, so `criteria.citation` stays None on all 32; the
`ARMY` prefix is the docket wearing the service's name, the same trap nmcca
recorded for `NMCCA No.`.

THE COURT BELOW IS A HEADQUARTERS, NOT A COURT. Article 66 review reaches
this court from a court-martial convened by a command, and the origin band
names the command (`Headquarters, U.S. Army Center for Initial Military
Training and Fort Eustis`), then who tried it (`Adam S. Kazin and Pamela L.
Jones, Military Judges`, with the stage in parentheses where two or more
sat), then the legal adviser (`Colonel Catherine L. Brantley, Special Trial
Counsel` / `Staff Judge Advocate`). All three are `lower-court` rows; only
the first two are parsed, into `lower_court` and `lower_court_judge`. The
adviser is neither the tribunal nor its judge and is left as printed.

THE APPEARANCES ARE THE ONLY LEFT-ALIGNED RUN ON THE SHEET, AND THAT IS THE
BOUND. `For Appellant:` (22 of 22) and `For Appellee:` (22 of 22) open at the
body rail and wrap to it; every other row in the ladder is centred on the
page axis. The run therefore ends where the rail ends — at the date, which is
centred — and no wording test closes it. Counsel printed inside the
headmatter STAYS there; its text is copied into `criteria.attorneys`
(core-patch-queue item 41, closed here as the other ports close it). Two
records print `For Appellee: No brief filed.` / `Pursuant to A.C.C.A. Rule
17.4, no response filed.` — an appearance row that names no lawyer, and still
an appearance row.

THE TITLE IS BRACKETED BY A RULE PAIR CUT TO ITS OWN MEASURE. 21 of the 22
covers draw a horizontal rule above the title and (on 20 of them) another
below it, and each rule is the TITLE's width, not a section fence: `DECISION`
runs 279.9–332.3 and its rules are 276.6 wide 59.4; `MEMORANDUM OPINION ON
REMAND ON RECONSIDERATION` runs 143.0–471.3 and its rules are 140.0 wide
334.0. That is ca5's underline test in the general form — a rule whose ends
coincide with the row beside it is decoration, not structure — so the pair is
NOT used to find anything. It is re-emitted where the page draws it, because
a reader that claims the block inherits the block's furniture. alfaro draws
no pair at all and sets its title BOLD instead; bean's lower rule is lost in
the scan. Neither is a defect and neither changes the reading.

WHAT THE PAPER CALLS ITSELF, in the corpus's own words: `MEMORANDUM OPINION`
(8), `SUMMARY DISPOSITION` (6), `OPINION OF THE COURT` (1), `DECISION` (1),
and five records that qualify one of those with the posture — `ON REMAND`,
`ON RECONSIDERATION`, `UPON RECONSIDERATION`, `ON REMAND ON RECONSIDERATION`,
`AND ACTION / ON PETITION FOR NEW TRIAL` (the only two-row title). Every one
of them is an OPINION of this court signed by a named judge or per curiam;
there is no order paper here, and the reader states that in `doc_type_final`
rather than letting a `SUMMARY DISPOSITION` heading type eight records
`order` (which is what happened before this file existed, against v1's
`opinion` on every one of them).

THE PUBLICATION STATEMENT IS A STATUS, NOT A NOTICE, SO IT IS NOT DROPPED.
`This opinion is issued as an unpublished opinion and, as such, does not
serve as precedent.` stands on 18 of the 22 covers, set at 10pt bold-italic
across the measure under the title. The four that omit it are the four that
are precedential — varlaro and alfaro (`OPINION OF THE COURT` / `… ON
RECONSIDERATION`), hudgens and aranzamendi — and the status is recorded only
where the statement stands. Nothing on this cover is standing boilerplate, so
this reader records NO `Dropped` notice at all; the one non-ladder row in the
corpus, antepara's `CORRECTED COPY` stamp, is the reissue marker and keeps a
`banner` row of its own.

WHERE THE BLOCK ENDS. At the first byline, which on all 22 covers stands on
page 1 at the body rail: `MURDOUGH, Judge:`, `POND, Senior Judge:`,
`Per Curiam:`. The search starts BELOW the date, so the origin band's
`… , Military Judges` and the counsel block's `For Appellant:` — both
colon-or-comma shaped — can never be mistaken for one. A record whose cover
we cannot see the end of is declined whole.

TEN OF THE 32 RECORDS HAVE NO COVER TO READ. Eight are image-only from end to
end (0 text lines in the whole PDF: wilcoxson, lowe, chillura, goines, feil,
martin, reese, jones) and two lose page 1 alone to the scanner (prajapati,
williams-clark_1). The reader returns NOTHING on all ten; the old engine
refused 13 of the corpus outright as non-born-digital, so this is the smaller
refusal, not the larger one.
"""

from __future__ import annotations

import re

from .. import model as m
from ..courts import register
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

STYLE_LADDER = "acca engraved masthead over a centred ladder"

# ---- acca's declared facts (measured over the 22 readable covers) --------
# THE MASTHEAD. 16.0pt on 20 records, 16.5pt on santaella and erb, against a
# 12.0-12.5pt body; 456-464pt wide on a 612-618pt sheet. The next largest
# type on any cover is a 13.0pt `v.` 9.6pt wide, so neither test is tuned.
_MASTHEAD_SIZE = 1.20      # x the body size
_MASTHEAD_MEASURE = 0.70   # x the page width
# …and it stands in the top eighth of the sheet, above or below at most one
# stamp row (antepara's `CORRECTED COPY`).
_MASTHEAD_BAND = 0.16
# THE PANEL/CAPTION SIZE SPLIT. Panel rows 8.0-10.5, caption rows 12.0-13.0;
# `body - 1.0` is 11.0 or 11.5 and falls inside the 1.5pt empty band on every
# record, with >=0.5pt of clearance on both sides.
_CAPTION_MIN_DROP = 1.0
# CENTRED ON THE PAGE AXIS. Every ladder row but the appearances is; the
# appearances are declared LEFT by their zone, never by this test, because a
# justified full-measure counsel line centres by midpoint too.
_CENTRED_TOL = 9.0
# THE DOCKET: `ARMY 20240529`. Nine characters, the first four the term year.
# The OCR splits the number on six records (`ARMY 2024041 7`), so spaces are
# admitted inside it and closed only in the parsed value. Never a citation —
# this court assigns none.
_DOCKET = re.compile(r"^ARMY\s+(\d[\d ]{5,})\.?$", re.I)
# THE BENCH DESIGNATION — the landmark every service CCA prints. The OCR
# reads it `Appellant Military Judges` on thomas and ingram.
_BENCH = re.compile(r"^Appell(?:ate|ant)\s+Military\s+Judges\b", re.I)
# `Before` opens the panel band; alfaro's whole-court sitting says so on the
# same row (`Before the Court Sitting En Banc`).
_BEFORE = re.compile(r"^Before\b", re.I)
# WHERE THE CASE CAME FROM: the convening command. 22 of 22.
_ORIGIN = re.compile(r"^Headquarters\b", re.I)
# WHO TRIED IT. One judge on 13 records, two or more with the stage in
# parentheses on 9 (`Jessica Conn, Military Judge (arraignment & motions)`).
_MILJUDGE = re.compile(r",\s*Military Judges?\b", re.I)
# THE APPEARANCE LABEL, at the body rail. Both forms on all 22.
_FOR = re.compile(r"^For\s+Appell(?:ant|ee)s?\b", re.I)
# THE DATE, centred, in the court's day-month-year form. antepara hangs a
# footnote mark off it (`15 January 20261`).
_DATE = re.compile(r"^(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})\d*\.?$")
# THE PUBLICATION STATEMENT, 18 of 22 (munn drops the closing period).
_PUBSTMT = re.compile(r"^\[?This opinion is issued as an unpublished", re.I)
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# PARTY STATUS — the closed role vocabulary, printed after the party's name
# on the caption's outer rows.
_STATUS = re.compile(
    r",\s*(Appellee|Appellant|Petitioner|Respondent|Cross-Appellee"
    r"|Cross-Appellant|Real Party in Interest)s?\.?$", re.I)
# THE SIGNING FORMS. `MURDOUGH, Judge:`, `POND, Senior Judge:`,
# `Per Curiam:`. The surname is a single token before the comma, which is
# what keeps `Adam S. Kazin and Pamela L. Jones, Military Judges` and
# `Colonel Catherine L. Brantley, Staff Judge Advocate` out.
_BYLINE = re.compile(
    r"^(?:PER CURIAM\b|Per Curiam\b"
    r"|[A-Z][A-Za-z'’\-]+,\s*(?:Chief |Senior |Acting )?(?:Judge|J\.)\b)")
# A DRAWN RULE THIS READER RE-EMITS: the title's own bracket. Anything under
# 40pt on these scans is an inked artefact (a stray 6-13pt mark appears on
# five covers) and is not a rule.
_RULE_MIN_WIDTH = 40.0
# THE LADDER NEVER LEAVES PAGE 1. Measured on all 22 covers: the byline that
# closes the block stands on page 1, at tops 458-548 against a 792-796pt
# sheet, so this reader opens no page 2 and cannot run through a running
# head. (nmcca's block reaches page 2 on 17 of its 32 and needed a measured
# head band for exactly that; acca does not.)


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---- the profile ---------------------------------------------------------
# BYLINE FORMS, all 22 in the corpus:
#   'MURDOUGH, Judge:' / 'WILLIAMS, Judge:' / 'STEELE, Judge:'   14 records
#   'POND, Senior Judge:' / 'MORRIS, Senior Judge:'               6 records
#   'Per Curiam:'                                                 2 records
# The spelled, colon-terminated title is the only form this court sets, so
# `prose` is declared alone: `also_reversed` would let the origin band's
# 'Colonel … , Staff Judge Advocate' shape reach the byline parser, and
# `also_abbrev` has nothing to match. Before this profile existed the court
# ran on the generic grammar and NOT ONE of the 20 named bylines parsed —
# every signed opinion came back authorless and eight of them typed `order`.
register(CourtProfile(
    "acca",
    "United States Army Court of Criminal Appeals",
    byline=BylineGrammar(
        style="prose",
        titles=("Judge", "Senior Judge", "Chief Judge",
                "Appellate Military Judge")),
    rollout="migrated",
))


@decider("headmatter.read", court="acca")
def read_headmatter_acca(model, geom, **_):
    """Read the centred ladder under an Army CCA masthead, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    pm = model.pages[0]
    if not pm.lines:
        return NOTHING          # a scanned cover: ten records in this corpus
    width, axis = pm.width, pm.width / 2

    # ---- the rows this block may contain --------------------------------
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
    rows = [groups[k] for k in order]
    if len(rows) < 10:
        return NOTHING
    txt = [_norm(" ".join(l.plain for l in g)) for g in rows]

    def _x0(i: int) -> float:
        return min(l.x0 for l in rows[i])

    def _x1(i: int) -> float:
        return max(l.x1 for l in rows[i])

    def _size(i: int) -> float:
        return max((l.size or 0.0) for l in rows[i])

    def _centred(i: int) -> bool:
        return abs((_x0(i) + _x1(i)) / 2 - axis) <= _CENTRED_TOL

    # ---- the dispatch: the engraved masthead ----------------------------
    masthead = next(
        (i for i in range(len(rows))
         if rows[i][0].top <= pm.height * _MASTHEAD_BAND
         and _size(i) >= body_size * _MASTHEAD_SIZE
         and (_x1(i) - _x0(i)) >= width * _MASTHEAD_MEASURE), None)
    if masthead is None:
        return NOTHING

    # ---- the ladder's landmarks, each required --------------------------
    dock = next((i for i in range(masthead + 1, len(rows))
                 if _DOCKET.match(txt[i])), None)
    if dock is None or dock <= masthead + 1:
        return NOTHING
    counsel_lo = next((i for i in range(dock + 1, len(rows))
                       if _FOR.match(txt[i])), None)
    if counsel_lo is None or counsel_lo <= dock + 1:
        return NOTHING          # the origin band must not be empty
    date = next((i for i in range(counsel_lo + 1, len(rows))
                 if _DATE.match(txt[i]) and _centred(i)), None)
    if date is None:
        return NOTHING
    # THE FOOT: the first byline BELOW THE DATE. A claim of unknown extent is
    # worse than none, so a cover whose end we cannot see is declined.
    stop = next((i for i in range(date + 1, len(rows))
                 if _BYLINE.match(txt[i]) and _x0(i) - body_x0 <= 24.0), None)
    if stop is None:
        return NOTHING

    # THE CAPTION BAND is the run of rows immediately above the docket set at
    # the caption's own type size; the PANEL BAND is what is left above it.
    cap_lo = dock
    while cap_lo > masthead + 1 and _size(cap_lo - 1) >= body_size - _CAPTION_MIN_DROP:
        cap_lo -= 1
    if cap_lo >= dock:
        return NOTHING
    if not any(_PIVOT.match(txt[i]) for i in range(cap_lo, dock)):
        return NOTHING          # no pivot, no caption, not this contract

    # ---- the walk: one role per row, every row in the span --------------
    kinds: list[str] = [""] * stop
    for i in range(masthead):
        kinds[i] = "banner"     # antepara's `CORRECTED COPY` reissue stamp
    kinds[masthead] = "court"
    for i in range(masthead + 1, cap_lo):
        kinds[i] = "panel"
    for i in range(cap_lo, dock):
        kinds[i] = "caption"
    kinds[dock] = "docket"
    for i in range(dock + 1, counsel_lo):
        kinds[i] = "lower-court"
    for i in range(counsel_lo, date):
        kinds[i] = "counsel"
    kinds[date] = "date"
    # BELOW THE DATE: the title, then the publication statement. Anything
    # else in this zone is a row this reader has not read, and rather than
    # guess at it the claim ENDS THERE — the rows below fall back to core's
    # shared walk, which is a smaller loss than a wrong role.
    for i in range(date + 1, stop):
        if _PUBSTMT.match(txt[i]):
            kinds[i] = "publication"
        elif txt[i] == txt[i].upper() and any(c.isalpha() for c in txt[i]):
            kinds[i] = "title"
        else:
            stop = i
            kinds = kinds[:stop]
            break
    if stop <= date:
        return NOTHING

    # ---- emit, in the page's own order ----------------------------------
    ctx = _Ctx()
    # The title's bracket rules, merged by position with the rows.
    rules = sorted((r for r in pm.h_rules
                    if r.width >= _RULE_MIN_WIDTH
                    and rows[0][0].top <= r.top < rows[stop][0].top),
                   key=lambda r: r.top)
    ri = 0
    caption_rows: list[str] = []
    counsel: list[str] = []
    panel_rows: list[int] = []
    title_rows: list[str] = []
    judges: list[str] = []
    lower: list[str] = []
    for i in range(stop):
        while ri < len(rules) and rules[ri].top < rows[i][0].top:
            ctx.rule()
            ri += 1
        kind = kinds[i]
        if kind == "caption":
            caption_rows.append(txt[i])
        elif kind == "counsel":
            counsel.append(txt[i])
        elif kind == "panel":
            panel_rows.append(i)
        elif kind == "title":
            title_rows.append(txt[i])
        elif kind == "lower-court":
            if _ORIGIN.match(txt[i]):
                lower.append(txt[i])
            elif _MILJUDGE.search(txt[i]):
                judges.append(txt[i])
        ctx.emit(rows[i], kind, centre=(kind != "counsel"))
    while ri < len(rules):
        ctx.rule()
        ri += 1

    # ---- criteria, filled BEFORE anything is gated on them --------------
    got = _DOCKET.match(txt[dock])
    ctx.crit["docket_number"] = got.group(1).replace(" ", "")
    ctx.crit["decision_date"] = _norm(_DATE.match(txt[date]).group(1))
    ctx.crit["court"] = txt[masthead]
    if title_rows:
        ctx.crit["title"] = " ".join(title_rows)
    if lower:
        ctx.crit["lower_court"] = lower[0]
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)
    if caption_rows:
        ctx.crit["caption"] = caption_rows[:40]
    sides = _sides(txt, cap_lo, dock)
    if sides:
        ctx.crit["parties"] = sides
        ctx.crit["case_name"] = " v. ".join(sides)
    # THE PANEL: the roster as printed, and the surnames it names. `Before`
    # and the bench designation are apparatus and belong to neither — the
    # roster is the panel row that is neither of them, and alfaro (sitting
    # en banc) prints none at all.
    roster = next((i for i in panel_rows
                   if not _BEFORE.match(txt[i]) and not _BENCH.match(txt[i])),
                  None)
    if roster is not None:
        ctx.crit["panel_line"] = txt[roster]
        names = _panel_names(txt[roster])
        if names:
            ctx.crit["panel"] = names
        bench = next((txt[i] for i in panel_rows if _BENCH.match(txt[i])), "")
        ctx.crit["judges"] = _norm(txt[roster] + " " + bench)
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE; its text is copied
    # into criteria.attorneys, which core fills only from a MOVED block.
    if counsel:
        ctx.crit["attorneys"] = " ".join(counsel)[:2000]
    # WHAT THE PAPER IS. The status is recorded only where the statement
    # stands; the four covers that omit it are the precedential ones and no
    # status is invented for them.
    if any(k == "publication" for k in kinds):
        ctx.crit["publication_status"] = "unpublished"
    ctx.crit["headmatter_style"] = STYLE_LADDER
    return ctx.result(_doc_type(title_rows))


def _doc_type(title_rows: list[str]):
    """What the paper calls itself. Every title in this corpus names an
    OPINION of the court — `MEMORANDUM OPINION`, `SUMMARY DISPOSITION`,
    `OPINION OF THE COURT`, `DECISION` — and every one of them is signed by a
    named judge or per curiam. Left to core the `SUMMARY DISPOSITION` heading
    typed eight records `order` against v1's `opinion` on all eight."""
    return m.DocType.OPINION if title_rows else None


def _sides(txt: list[str], lo: int, hi: int) -> list[str]:
    """The parties either side of the pivot. The caption's outer rows carry
    the party and its STATUS (`UNITED STATES, Appellee`); the inner rows
    carry the appellant's rank-and-name and, under it, the service the party
    belongs to (`United States Army, Appellant`) — a designation, never part
    of the name. So each side is its FIRST row with the status label cut
    off, and nothing is read by wording."""
    pivot = next((i for i in range(lo, hi) if _PIVOT.match(txt[i])), None)
    if pivot is None or pivot == lo or pivot + 1 >= hi:
        return []
    out = []
    for j in (lo, pivot + 1):
        name = _STATUS.sub("", txt[j]).strip().rstrip(",;")
        if not name:
            return []
        out.append(name)
    return out


def _panel_names(line: str) -> list[str]:
    """'MORRIS, JUETTEN, and MURDOUGH' -> three names. The scan hangs a
    footnote mark off the last one on two records (`ARGUELLES'`, `COOPER1`),
    and one record drops the Oxford comma (`COOPER, WILLIAMS and SCHLACK`);
    the connector is not a name."""
    out = []
    for piece in re.split(r",|\band\b", line):
        name = piece.strip().strip(".").rstrip("0123456789'’*")
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

    def rule(self) -> None:
        """The page DREW this rule — the title's own bracket. It carries no
        line ids, so core seats it beside the row it was emitted next to."""
        self.items.append(m.Rule(prov=m.Prov(1), span="center"))

    def result(self, doc_type=None) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": doc_type}
