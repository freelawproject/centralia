"""United States Court of Appeals for the Armed Forces ('armfor').

THE APEX MILITARY COURT, NOT A SERVICE CCA. armfor sits above acca, afcca,
nmcca and uscgcoca and reviews their decisions under Article 67, UCMJ; its
five civilian judges are appointed for fifteen-year terms and it is the one
Article I court in this family that publishes a REPORTER-STYLE slip. So the
sibling reader `courts/nmcca.py` is a cousin, not a template, and only two
of its findings survive contact with this paper: that the court types its
rules as a run of underscores on the page axis, and that counsel printed in
the headmatter stays in the headmatter. Everything else differs — there is
no seal, no `Before`, no roster of `Appellate Military Judges`, no trial
recital, no publication statement, and the docket is a two-part term number
rather than a nine-digit year-serial.

    ┌──────────────────────────────────────────────────────────────────┐
    │ This opinion is subject to revision before publication.  NOTICE  │
    │                                                                  │
    │            UNITED STATES COURT OF APPEALS       THE MASTHEAD     │
    │                 FOR THE ARMED FORCES            (bold, centred)  │
    │                  _______________                FENCE 1          │
    │                   UNITED STATES                 (bold: party)    │
    │                      Appellee                   (roman: status)  │
    │                         v.                      the pivot        │
    │              Daytron Abdullah, Sergeant         (bold: party)    │
    │            United States Army, Appellant        (roman: service) │
    │                    No. 25-0070                  the DOCKET       │
    │              Crim. App. No. 20230223            the CCA's number │
    │      Argued December 9, 2025—Decided June 12, 2026   the dates   │
    │        Military Judge: Jacqueline L. Emanuel    who tried it     │
    │  For Appellant: Captain Andrew W. Moore (argued);                │
    │    Colonel Philip M. Staten, …                  the appearances  │
    │  For Appellee: Captain Meghan E. Moore (argued); …               │
    │  Judge JOHNSON delivered the opinion of the Court, in which      │
    │    Judge SPARKS and Senior Judge EFFRON joined. Chief Judge      │
    │    OHLSON filed a separate opinion concurring in the judgment,   │
    │    in which Judge HARDY joined. …               the ANNOUNCEMENT │
    │                  _______________                FENCE 2          │
    └──────────────────────────────────────────────────────────────────┘
    (page 2)  Judge JOHNSON delivered the opinion of the Court.

WHICH DIVIDER SHAPE THIS IS: **NONE.** Like nmcca and for the same reason —
the caption is a SINGLE CENTRED STACK. Measured over all 32 records, every
caption row's midpoint is within 2.6pt of the 306.0 axis and the widest of
them (jacinto's rate line, 178.0-434.0) runs straight across where a rail
would have to stand. There is no `)` column, no drawn vertical, no box rail.
The old engine's shared military base folds a `)` rail into every CCA
headmatter (`_military.py`: `_fold_rail_caption(d["summary"], ")")`) — the
trap recorded at docs/core-patch-queue.md ~1690 — but armfor never inherited
from that base even in v1 (it descends from `_reversedjustice`), and the
measurement confirms the fold would invent a rail here too: page 1 contains
ZERO `)` glyphs standing as a column on all 32 records.

THE FENCE IS INVARIANT AND THE FENCE IS THE FOOT. The court types
`_______________` — fifteen underscores — as text, never as a vector. All 63
occurrences in the corpus are 90.0pt wide except rocha's closing one (82.7),
and 61 of 63 have their midpoint at EXACTLY 306.0 with the other two 1.56pt
off (moore, moore_1). Not one is off the axis. So the axis is the test and
the measure is payload, and the LAST fence before the body is where the
cover ends.

THE DISPATCH IS THE MASTHEAD, NOT THE FENCE PAIR, and this is the one place
armfor's cover departs from nmcca's in a way that matters. nmcca can key on
the first fence PAIR because it always types two; armfor normally types two
as well (one under the masthead, one closing the cover) but
**washington_1 types only the closing one** — its cover runs straight from
`FOR THE ARMED FORCES` into `UNITED STATES` with no rule between. Keyed on
the pair, that record would be declined; keyed on the masthead, it reads
like the other 31 and the opening fence is payload. So the contract is:

  * the court NAMES ITSELF on page 1 in two centred bold rows,
    `UNITED STATES COURT OF APPEALS` / `FOR THE ARMED FORCES` — 32 of 32,
    the only thing on the cover that identifies the tribunal;
  * at least one typed axis fence stands between the masthead and the body;
  * the body opens at the page's own left rail below that fence.

Any record missing any of the three is not this contract and the reader
returns NOTHING.

WHERE THE COVER ENDS IS A GEOMETRIC QUESTION AND MUST BE. The obvious foot —
the first byline — is unusable here, because **the announcement is set in
the byline's own words**: `Judge JOHNSON delivered the opinion of the
Court,` opens the cover's last paragraph and `Judge JOHNSON delivered the
opinion of the Court.` opens the opinion two rows later, at the SAME rail
(162.0) in the SAME face and size. Nothing but position tells them apart.
The old engine solved it with a y-coordinate on page 1 (`_cover_close_top`);
this reader uses the structure instead — the cover is what stands between
the masthead and the LAST typed axis fence above the first BODY-RAIL row.
Measured over all 32: nothing inside the cover ever sits at the body rail
(the appearances are indented 18pt to 162.0 and the caption is centred), and
the body's runover lines always do (144.0). The two never overlap, so the
boundary is exact and no wording is read to find it. On 26 records the
closing fence is on page 1; on deremer, deremer_1, ellis, ellis_1 and
zackery it is on page 2, after the appearances spill over.

THE LADDER BELOW THE CAPTION IS A SET OF PARAGRAPHS, AND THE PAGE SEPARATES
THEM. Every block in the lower half of the cover — the dates, the trial
judges, each appearance, the announcement — is one paragraph set solid at
the court's leading (15.0pt, 14.0 on rocha's 11pt cover) with a BLANK LINE
between blocks. Measured over all 32 records: within a block the row-to-row
step is 1.00x the leading and between blocks it is 2.00x, with nothing in
between anywhere in the corpus. So a block boundary is a step above 1.5x and
the block's FIRST row names the whole block. That is what keeps
`Judge HARDY, and Judge JOHNSON joined.` — the third row of zackery's
appearance block, which parses as a byline standing alone — inside the block
it belongs to: ca4's lesson, that the band is the unit of meaning and not
the row, arriving here as leading rather than as a fence.

WHAT THE FOUR BLOCK OPENERS ARE, all closed forms:

  * THE DATES. `Argued December 9, 2025—Decided June 12, 2026` (28
    records), `Argued January 28, 2026—July 23, 2026` (deremer — no
    `Decided` label) and `November 18, 2025—April 13, 2026` (washington —
    neither label). So the labels are optional and the invariant is the
    DATE PAIR joined by an em dash. `submitted` takes the argued date and
    `decision_date` the second; ellis prints `July 28, 2028`, a typo for
    2026 that ellis_1 corrects, and the reader records what the page says.
  * WHO TRIED IT. `Military Judge:` (18) / `Military Judges:` (14), the
    names following on that row and its wraps. Note this row is the ONE
    place the cover states anything about the proceeding below; armfor
    never names the Court of Criminal Appeals it is reviewing, so
    `lower_court` stays None and only `lower_court_docket` is filled.
  * THE APPEARANCES. `For Appellant:` / `For Appellee:` (30 records each),
    `For United States:` and `For Staff Sergeant Zackery J. Askins:`
    (zackery, a consolidated cross-appeal where neither side is simply
    'the appellant'), and the amicus forms — `Amicus Curiae:`,
    `Amici Curiae for Appellee:`, `Amicus Curiae for Appellant:`,
    `Amicus Curiae in Support of Appellee:`, `Amicus Curiae for Staff
    Sergeant Zackery J. Askins:`. jacinto sets a label so long it WRAPS
    (`Amicus Curiae on Behalf of E.B. and in Support of` / `Appellee:
    Peter Coote, Esq. (on brief).`), which is why the opener test is the
    leading word and not the colon.
  * THE ANNOUNCEMENT. `(Chief |Senior )?Judge SURNAME (delivered|
    announced) …` — 30 records; jacinto is per curiam and prints none, and
    ellis/ellis_1 print theirs at the top of page 2. It states the whole
    lineup of writings and joins, sometimes part by part (`Judge SPARKS
    delivered the opinion of the Court, in which Chief Judge OHLSON joined
    with respect to Parts I., II.A., and III., …` — bass, twelve rows).
    It is a ROSTER, not an opinion start, and reading it as one is what
    cost the old engine a bespoke pass. Here it is simply inside the claim.

THE ANNOUNCEMENT IS WHERE THE PANEL COMES FROM, because armfor prints no
roster. There is no `Before` line and no bench designation on this cover —
the only place the judges are named is the announcement, so `panel` is read
off it by the BENCH vocabulary (`Judge`, `Chief Judge`, `Senior Judge`)
followed by an ALL-CAPS surname, in printed order and deduplicated. Nothing
is read by wording: `OHLSON`, `SPARKS`, `MAGGS`, `HARDY`, `JOHNSON` and
`EFFRON` are found because they are capitalised surnames behind a bench
word, exactly as ca2's roster is.

THE DOCKET IS TWO NUMBERS AND THEY ARE DIFFERENT FACTS. `No. 25-0070` is
this court's own docket — term year and serial — and `Crim. App. No.
20230223` is the number the SERVICE COURT below gave the case. The second
goes to `lower_court_docket` ('this case, downstairs') and never to
`other_dockets` ('another case, alongside'), which is what the model's own
comment asks for. zackery is the corpus's only consolidated record: it sets
TWO complete caption stacks (`No. 26-0002`, the appeal, and `No. 26-0014`,
the cross-appeal) over one shared `Crim. App. No. 20230303`, and its running
head prints both — `United States v. Askins, Nos. 26-0002/AR & 26-0014/AR`.
The first is `docket_number` and the second `other_dockets`. Note also that
the `/AR`, `/AF`, `/MC`, `/NA` suffix the running head appends is the
SERVICE, not part of the number, and the cover never prints it.

WHAT IS DROPPED IS THE NOTICE AND ONLY THE NOTICE. `This opinion is subject
to revision before publication.` stands italic at the very top of page 1 on
all 32 records, above the masthead. It is boilerplate about the slip's
provisional state — the court's one notice proper — and it is recorded as
`Dropped` kind 'notice'. It is NOT a publication status: it says the
opinion WILL be published once revised, so `publication_status` is left
unset rather than being read backwards into 'unpublished'.

THE RUNNING HEAD AND THE FOLIO ARE CORE'S, and unlike nmcca this court makes
that easy: armfor slips run 8-30 pages, the head is set at 11.0pt against a
12.0pt body, and both of its rows repeat on every sheet, so
`FurnitureFinder` tags all of them (`United States v. Abdullah, No.
25-0070/AR` / `Opinion of the Court`, and on the separate-writing sheets
`Chief Judge OHLSON, with whom Judge HARDY joins,` / `Judge HARDY,
concurring in the judgment`). The reader skips every row core has already
tagged and never consumes one; the two head rows on the continuation sheets
that carry the cover's tail (5 records) are core's drops, not this reader's.

WHY THE PROFILE DECLARES `reversed` AND WHAT IT COSTS TO GET IT WRONG.
armfor signs title-first with an all-caps surname — `Judge JOHNSON delivered
the opinion of the Court.`, `Chief Judge OHLSON, dissenting.`, `Judge HARDY,
with whom Judge JOHNSON joins, con-` / `curring in the judgment.` — and
`PER CURIAM.` on jacinto. Core's `reversed` grammar matches on
`text.startswith(title + " ")`, so the titles are declared in the printed
case (`Judge`, not `JUDGE`); the all-caps surname is what keeps body prose
that merely mentions a judge ('the military judge') from parsing. Before
this port armfor had no profile at all, and the result was total: **32 of 32
records came back with ZERO writings, the whole document typed `order` and
the entire cover swallowed into it as block 0.**
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

STYLE_MASTHEAD = "armfor masthead ladder"

# ---- armfor's declared facts (measured over all 32 records) -------------
# THE FENCE. A typed run of underscores centred on the page axis. All 63 in
# the corpus: 90.0pt wide (62) or 82.7 (rocha's closing rule), midpoint at
# 306.0 (61) or 1.56pt off it (moore, moore_1). The axis is the test.
_FENCE_TEXT = re.compile(r"^_{4,}$")
_AXIS_TOL = 4.0
# THE MASTHEAD — the court naming itself, and the landmark this contract is
# dispatched on. Two centred bold rows, always in this order, on all 32.
_MAST1 = re.compile(r"^UNITED STATES COURT OF APPEALS$")
_MAST2 = re.compile(r"^FOR THE ARMED FORCES$")
_COURT_NAME = "United States Court of Appeals for the Armed Forces"
# THE STANDING NOTICE, italic above the masthead on all 32.
_NOTICE = re.compile(r"^This opinion is subject to revision before "
                     r"publication\.?$", re.I)
# THE DOCKET: 'No. 25-0070' — term year and serial. zackery prints two.
_DOCKET = re.compile(r"^Nos?\.\s*(\d{2}-\d{3,4})\.?$")
# THE NUMBER THE COURT BELOW GAVE IT: 'Crim. App. No. 20230223' (Army/Navy
# year-serial), 'Crim. App. No. 40434' (Air Force five-digit),
# 'Crim. App. No. 22072'. The label is the invariant, not the shape.
_CCA_NO = re.compile(r"^(?:Crim\.?\s*App\.?|C\.?C\.?A\.?)\s*Nos?\.\s*(.+?)\.?$",
                     re.I)
# THE PIVOT.
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# THE PARTY STATUS — a closed role vocabulary, set roman on this cover
# (nmcca sets the same words italic). Used only to tell the status row from
# the party row where weight cannot: 'United States Army, Appellant' is one
# roman row carrying the service AND the status.
_STATUS = re.compile(r"\b(Appellants?|Appellees?|Petitioners?|Respondents?"
                     r"|Cross-Appellants?|Cross-Appellees?)\b")
# THE DATES. A pair of dates joined by an em dash, the labels optional:
# 28 records print both ('Argued …—Decided …'), deremer prints only
# 'Argued', washington prints neither.
_DATEPAIR = re.compile(
    r"^(?:(Argued|Reargued|Submitted)\s+)?"
    r"([A-Z][a-z]+\s+\d{1,2},\s*\d{4})\s*[—–-]\s*"
    r"(?:(?:Decided|Filed)\s+)?"
    r"([A-Z][a-z]+\s+\d{1,2},\s*\d{4})\.?$")
_DATEONE = re.compile(r"^(?:Decided|Filed|Argued|Submitted):?\s+"
                      r"([A-Z][a-z]+\s+\d{1,2},\s*\d{4})\.?$")
# WHO TRIED IT.
_MILJUDGE = re.compile(r"^Military Judges?:", re.I)
# THE APPEARANCE OPENER. The colon cannot be the test — jacinto wraps its
# label onto a second row ('Amicus Curiae on Behalf of E.B. and in Support
# of' / 'Appellee: Peter Coote, Esq. (on brief).') — so the LEADING WORDS
# are, and they are a closed set: the court labels an appearance either
# 'For <party>:' or '<Amicus|Amici> Curiae …:'.
_FOR = re.compile(r"^(?:For\s+[A-Z]|Amicus\s+Curiae\b|Amici\s+Curiae\b)")
# THE ANNOUNCEMENT of the writings: a bench word, an ALL-CAPS surname and a
# filing verb. Never matched below the cover's closing fence, so the
# identically-worded byline on the next page cannot reach it.
_ANNOUNCE = re.compile(
    r"^(?:Chief\s+|Senior\s+|Acting\s+)?Judge\s+[A-Z][A-Z'’\-]+\b"
    r".*\b(?:delivered|announced|filed|wrote)\b")
# THE BENCH VOCABULARY that reads the panel out of the announcement.
_BENCH_NAME = re.compile(
    r"\b(?:Chief\s+|Senior\s+|Acting\s+)?Judge\s+([A-Z][A-Z'’\-]{1,}[A-Za-z]*)")
# A BLOCK BOUNDARY is a vertical step above 1.5x the cover's own leading.
# Measured over all 32: within a block the step is 1.00x and between blocks
# 2.00x, with nothing in between anywhere in the corpus.
_BLOCK_GAP = 1.5
# The cover never runs past page 2; the fence bounds it anyway.
_MAX_PAGES = 4


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---- the profile -------------------------------------------------------
# BYLINE FORMS, all 63 in the corpus:
#   'Judge JOHNSON delivered the opinion of the Court.'      the majority
#   'Judge SPARKS announced the judgment of the Court.'      a plurality
#   'Chief Judge OHLSON, dissenting.'                        a separate writing
#   'Judge MAGGS, concurring in part and in the judgment.'
#   'Chief Judge OHLSON, with whom Judge HARDY joins,' / 'concurring in the
#                                                          judgment.'   (wrap)
#   'Judge HARDY, with whom Judge JOHNSON joins, con-' / 'curring in the
#                                                        judgment.' (wrap, and
#                                                        broken MID-WORD)
#   'PER CURIAM.'                                            jacinto
# Declared `reversed` with the titles in the case the court PRINTS them —
# core matches `text.startswith(title + " ")` and 'JUDGE' would match none of
# the 63. `accept_delivered` is not needed: 'delivered' and 'announced' are
# both already in core's `_DELIVER_VERBS`.
register(CourtProfile(
    "armfor",
    "United States Court of Appeals for the Armed Forces",
    byline=BylineGrammar(
        style="reversed",
        rev_titles=("Judge", "Chief Judge", "Senior Judge", "Acting Judge")),
    # The body opens its paragraphs 18pt in from the measure's rail (144 ->
    # 162) and sets its block quotations at 180. Twice this value must fall
    # between the two, so 14.0.
    para_indent_min=14.0,
    rollout="migrated",
))


@decider("headmatter.read", court="armfor")
def read_headmatter_armfor(model, geom, **_):
    """Read the masthead ladder of an armed-forces slip, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 144.0)
    finder = FurnitureFinder(model, body_x0, body_size)
    width = model.pages[0].width
    axis = width / 2

    # ---- the rows the cover may contain ---------------------------------
    # Furniture is neither claimed nor consumed: core has already tagged
    # every running head and folio on this paper (both head rows repeat on
    # every sheet at 11.0pt against a 12.0pt body), and a reader that took
    # them would report them twice.
    rows: list[list] = []
    for pm in model.pages[:_MAX_PAGES]:
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
        rows.extend(groups[k] for k in order)
    if len(rows) < 8:
        return NOTHING
    txt = [_norm(" ".join(l.plain for l in g)) for g in rows]

    def _x0(i: int) -> float:
        return min(l.x0 for l in rows[i])

    def _mid(i: int) -> float:
        g = rows[i]
        return (min(l.x0 for l in g) + max(l.x1 for l in g)) / 2

    def _centred(i: int) -> bool:
        return abs(_mid(i) - axis) <= 8.0

    # ---- the dispatch: the masthead, then a fence, then the body rail ---
    mast = None
    for i in range(len(rows) - 1):
        if rows[i][0].page != 1:
            break
        if _MAST1.match(txt[i]) and _MAST2.match(txt[i + 1]):
            mast = i
            break
    if mast is None:
        return NOTHING
    fences = [i for i in range(len(rows))
              if _FENCE_TEXT.match(txt[i].replace(" ", ""))
              and abs(_mid(i) - axis) <= _AXIS_TOL]
    # THE FOOT. The body's own left rail — 144.0 on a 612pt page — is where
    # the opinion's runover lines stand and nothing on the cover ever does:
    # the appearances are indented to 162.0 and the caption is centred. So
    # the first full-measure row AT the rail opens the paper, and the last
    # typed axis fence above it closes the cover.
    body = next((i for i in range(mast, len(rows))
                 if abs(_x0(i) - body_x0) <= 2.0
                 and (max(l.x1 for l in rows[i]) - _x0(i)) > 0.45 * width),
                None)
    if body is None:
        return NOTHING
    close = [i for i in fences if mast < i < body]
    if not close:
        return NOTHING
    stop = close[-1] + 1

    kinds: list[str | None] = [None] * stop
    for i in fences:
        if i < stop:
            kinds[i] = "#fence"
    kinds[mast] = kinds[mast + 1] = "court"
    for i in range(mast):
        if _NOTICE.match(txt[i]):
            kinds[i] = "#notice"

    # ---- the caption: the centred stack under the masthead --------------
    # It runs from the masthead to the first LADDER opener. Inside it the
    # only distinctions that matter are the two numbers.
    def _opens_ladder(i: int) -> bool:
        t = txt[i]
        return bool(_DATEPAIR.match(t) or _DATEONE.match(t)
                    or _MILJUDGE.match(t) or _FOR.match(t)
                    or _ANNOUNCE.match(t))

    cap_end = next((i for i in range(mast + 2, stop)
                    if kinds[i] is None and _opens_ladder(i)), stop)
    for i in range(mast + 2, cap_end):
        if kinds[i] is not None:
            continue
        if _DOCKET.match(txt[i]):
            kinds[i] = "docket"
        elif _CCA_NO.match(txt[i]):
            kinds[i] = "lower-docket"
        else:
            kinds[i] = "caption"

    # ---- the ladder: paragraphs, each named by its first row ------------
    # A block boundary is a vertical step above 1.5x the cover's leading.
    # The block's OPENER names the whole block, which is what keeps
    # zackery's 'Judge HARDY, and Judge JOHNSON joined.' — the third row of
    # an appearance block, a byline standing alone — inside its own block.
    lead = _leading(rows, cap_end, stop)
    state: str | None = None
    rail: float | None = None
    for i in range(cap_end, stop):
        if kinds[i] is not None:
            state = rail = None
            continue
        turned = rows[i][0].page != rows[i - 1][0].page
        if state is not None and not turned and not _new_block(rows, i, lead):
            kinds[i] = state
            continue
        t = txt[i]
        if _DATEPAIR.match(t) or _DATEONE.match(t):
            kinds[i], state, rail = "date", "date", _x0(i)
        elif _MILJUDGE.match(t):
            kinds[i], state, rail = "lower-court", "lower-court", _x0(i)
        elif _FOR.match(t):
            kinds[i], state, rail = "counsel", "counsel", _x0(i)
        elif _ANNOUNCE.match(t):
            kinds[i], state, rail = "panel", "panel", _x0(i)
        # ---- THE SHEET TURNED MID-BLOCK -------------------------------
        # A block that runs onto page 2 does not have to reopen with its
        # own label, so the page turn cannot be a block boundary on its
        # own. Five records carry the cover onto a second sheet and they
        # split two ways: deremer, deremer_1, ellis and ellis_1 open page 2
        # with a real label ('Amicus Curiae: Sean J. Kealy, Esq., Boston';
        # 'Judge HARDY delivered the opinion of the Court, in'), and
        # ZACKERY DOES NOT — its page 2 opens 'Lieutenant Colonel Kyle C.
        # Sprague, Major Andrew', the fourth name in an appearance that
        # began on page 1. So the labels are tested FIRST and the
        # continuation is what is left, bounded by the block's own RAIL.
        #
        # The order matters and cannot be reversed. Eight records set a row
        # INSIDE the announcement that parses as a label standing alone
        # ('Judge JOHNSON joined. Judge HARDY filed a' — hennessy, moore,
        # moore_1, serjak, rosariomartinez, ellis, ellis_1; 'Judge MAGGS
        # filed a separate opinion, concurring' — bass), and every one of
        # them is mid-block on its own page. Testing openers first
        # everywhere would cut each announcement into two.
        elif (turned and state is not None and rail is not None
                and abs(_x0(i) - rail) <= 2.0):
            kinds[i] = state
        else:
            # An unnamed block. Left unclaimed rather than guessed: core's
            # shared walk renders it and `hm-unread` counts it, which is the
            # honest report. Fires on nothing in this corpus.
            state = rail = None

    # ---- emit ------------------------------------------------------------
    ctx = _Ctx()
    caption_rows: list[str] = []
    counsel: list[str] = []
    judges_below: list[str] = []
    announce: list[str] = []
    dockets: list[str] = []
    cca: list[str] = []
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
        if kind == "court":
            ctx.emit(pieces, "court", centre=True)
            continue
        if kind == "caption":
            caption_rows.append(txt[i])
            ctx.emit(pieces, "caption", centre=True)
            continue
        if kind == "docket":
            dockets.append(_DOCKET.match(txt[i]).group(1))
            ctx.emit(pieces, "docket", centre=True)
            continue
        if kind == "lower-docket":
            cca.append(_norm(txt[i]))
            ctx.emit(pieces, "lower-court", centre=True)
            continue
        if kind == "date":
            ctx.emit(pieces, "date", centre=_centred(i))
            continue
        if kind == "lower-court":
            judges_below.append(txt[i])
            ctx.emit(pieces, "lower-court", centre=_centred(i))
            continue
        if kind == "counsel":
            counsel.append(txt[i])
            ctx.emit(pieces, "counsel", centre=False)
            continue
        if kind == "panel":
            announce.append(txt[i])
            ctx.emit(pieces, "panel", centre=False)
            continue

    # ---- criteria, populated BEFORE anything is gated on them ------------
    for i in range(stop):
        if kinds[i] != "date":
            continue
        got = _DATEPAIR.match(txt[i])
        if got:
            if got.group(1):
                ctx.crit.setdefault("submitted", _norm(got.group(2)))
            ctx.crit.setdefault("decision_date", _norm(got.group(3)))
        else:
            one = _DATEONE.match(txt[i])
            if one:
                ctx.crit.setdefault("decision_date", _norm(one.group(1)))
        break
    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if dockets[1:]:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if cca:
        # 'this case, downstairs' — the number the service court gave it,
        # never `other_dockets`, which is 'another case, alongside'.
        ctx.crit.setdefault("lower_court_docket", cca)
    if judges_below:
        got = " ".join(judges_below)
        ctx.crit.setdefault("lower_court_judge",
                            _norm(got.split(":", 1)[1] if ":" in got else got))
    if caption_rows:
        ctx.crit.setdefault("caption", caption_rows[:40])
    sides = _sides(txt, rows, kinds, mast + 2, cap_end)
    if sides:
        ctx.crit.setdefault("parties", sides)
        ctx.crit.setdefault("case_name", " v. ".join(sides))
    if announce:
        # THE ANNOUNCEMENT IS THE ONLY PLACE THE BENCH IS NAMED on this
        # cover — armfor prints no 'Before' roster — so the panel is read
        # off it by the bench vocabulary and the all-caps surname, in
        # printed order, deduplicated.
        line = " ".join(announce)
        ctx.crit.setdefault("panel_line", line[:2000])
        ctx.crit.setdefault("judges", line[:2000])
        names: list[str] = []
        for got in _BENCH_NAME.finditer(line):
            name = got.group(1).rstrip(",.")
            if name not in names:
                names.append(name)
        if names:
            ctx.crit.setdefault("panel", names)
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE; its text is copied
    # into criteria.attorneys, which core fills only from a MOVED block
    # (core-patch-queue item 41).
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    # THE COURT NAMES ITSELF in the masthead, so `court` is what the page
    # prints and not what the registry says.
    ctx.crit.setdefault("court", _COURT_NAME)
    ctx.crit.setdefault("headmatter_style", STYLE_MASTHEAD)
    return ctx.result()


def _leading(rows: list, lo: int, hi: int) -> float:
    """The cover's own line leading, measured inside its ladder: the MODE of
    the row-to-row step. 15.0 on the 12pt template, 14.0 on rocha's 11pt
    one. Never a constant — the two templates differ."""
    steps: dict = {}
    for i in range(lo + 1, hi):
        if rows[i][0].page != rows[i - 1][0].page:
            continue
        step = round(rows[i][0].top - rows[i - 1][0].top, 1)
        if step > 0:
            steps[step] = steps.get(step, 0) + 1
    if not steps:
        return 15.0
    return min(steps, key=lambda s: (-steps[s], s))


def _new_block(rows: list, i: int, lead: float) -> bool:
    """True where the page put a BLANK LINE above this row — a step above
    1.5x the cover's leading. Same sheet only; a page turn is a different
    question and the walk asks it separately."""
    if i == 0 or rows[i][0].page != rows[i - 1][0].page:
        return True
    return (rows[i][0].top - rows[i - 1][0].top) > lead * _BLOCK_GAP


def _sides(txt: list[str], rows: list, kinds: list, lo: int,
           hi: int) -> list[str]:
    """The parties either side of the pivot, read by WEIGHT: the bold rows
    are the names, the roman rows are the service and the status. armfor
    sets the pivot bold too, and both numbers, so only rows already typed
    `caption` are eligible — that is what keeps 'No. 25-0070' out of the
    appellant's name.

    THE SECOND STACK IS A SECOND CASE. zackery consolidates an appeal and a
    cross-appeal and prints TWO complete caption stacks under one masthead,
    so the right-hand party must be bounded by the FIRST number below the
    pivot and not by the end of the caption band — unbounded it read
    'Zackery J. ASKINS, Staff Sergeant No. 26-0002 UNITED STATES Zackery J.
    ASKINS, Staff Sergeant No. 26-0014'. The number is the boundary because
    the court sets it as the last row of every stack, on all 32 records.
    """
    pivot = next((i for i in range(lo, hi) if _PIVOT.match(txt[i])), None)
    if pivot is None:
        return []
    end = next((i for i in range(pivot + 1, hi)
                if kinds[i] in ("docket", "lower-docket")), hi)
    out = []
    for a, b in ((lo, pivot), (pivot + 1, end)):
        names = [txt[i] for i in range(a, b)
                 if kinds[i] == "caption" and all(l.all_bold for l in rows[i])]
        joined = " ".join(names).strip().rstrip(",;")
        if joined:
            out.append(joined)
    return out if len(out) == 2 else []


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
