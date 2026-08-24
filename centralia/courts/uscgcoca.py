"""United States Coast Guard Court of Criminal Appeals ('uscgcoca').

The fourth service CCA to reach this engine, after `nmcca`. It is an
Article I military appellate court reviewing Coast Guard courts-martial
under Article 66, UCMJ; every panel is a panel of `Appellate Military
Judges` and the court below is a general, special or summary
court-martial. That much it shares with nmcca — and NOTHING ELSE ABOUT
THE PAPER IS THE SAME, so this file inherits from nmcca no more than
nmcca inherited from a state court. nmcca fences its cover with typed
underscore rules on the page axis; uscgcoca types no rule at all on 29 of
its 32 records and DRAWS one, vertically, on the other three.

TWO CONTRACTS, AND THE PAGE DECLARES WHICH BY DRAWING OR NOT DRAWING A
RULE. Measured over all 32 records, with no exception and no overlap:

  * **`uscgcoca banner cover`** — 29 records. Page 1 opens on a single
    BOLD banner row spanning 117.4-494.4 (`UNITED STATES COAST GUARD
    COURT OF CRIMINAL APPEALS`) and the page draws ZERO vertical rules.
  * **`uscgcoca ruled two-column order`** — 3 records (in_re_a.h.,
    in_re_tucker, reese_v._united_states). Page 1 opens on a TWO-row
    centred masthead (`IN THE UNITED STATES COAST GUARD` /`COURT OF
    CRIMINAL APPEALS`) and draws EXACTLY ONE vertical rule, at x =
    292.0/292.0/292.5 on a 612pt page, running 113.4-292.9, 113.4-279.0
    and 109.2-274.9.

The vertical-rule count is the dispatch — ca6's rule, that the divider IS
the parser, holding in its cleanest form: 1 rule -> two columns, 0 rules
-> one centred stack. Nothing is matched against the flag beside it, and
a record that draws neither shape returns NOTHING.

    ┌───────────── THE BANNER COVER (29) ──────────────────────────────┐
    │ UNITED STATES COAST GUARD COURT OF CRIMINAL APPEALS   the BANNER │
    │                    UNITED STATES               a party           │
    │                          v.                    the pivot         │
    │                   Mario A. ANGEL               a party           │
    │       Yeoman Third Class (E-4), U.S. Coast Guard   the RATE      │
    │                     CGCMG 0373        the COURT-MARTIAL number   │
    │                   Docket No. 1467     THIS court's docket        │
    │                  13 December 2019              the date          │
    │ General court-martial tried on 16 October 2018.   the RECITAL    │
    │    Military Judge:            CDR Paul R. Casey, USCG            │
    │    Appellate Defense Counsel: LCDR Salomee G. Briggs, USCG       │
    │    Appellate Government Counsel: LCDR Stephen Miros, USCG        │
    │                            ↑ the LABEL GRID, two rails           │
    │                        BEFORE                                    │
    │           MCCLELLAND, BRUBAKER & MOORADIAN     the roster        │
    │                Appellate Military Judges       the BENCH         │
    │ Per curiam:                            (the paper begins)        │
    └──────────────────────────────────────────────────────────────────┘

THE COVER IS A COVER OF COUNSEL, WHICH IS WHY IT LOOKS LIKE NOTHING ELSE
IN THIS ENGINE. The observation in `notes/review-backlog.md` is exact: the
whole middle of page 1 is an appearance roster, and it is set as a LABEL
GRID — a left rail of labels at body_x0 + 36 and a right rail of values
just left of the page axis. 168 grid rows over the corpus. A grid has a
wrap's geometry and means something else (the ca2/scotus lesson), so the
run is never closed by leading; it is closed by the AXIS.

  * every grid row is OFF the axis: the value column runs 297.0-306.1 at
    its left edge and out to 536.3 at its right, so the nearest grid row's
    midpoint is 353.2 — 47pt off 306.0;
  * every row above and below the grid is ON the axis to within 1.6pt.

So the grid ends at the first CENTRED row, which is always `BEFORE`, and
no wording test closes it. The same axis test opens it from the other
side: the caption stack above is centred, and the trial recital between
them is the only run at the BODY RAIL.

THE LABELS ARE A CLOSED APPARATUS VOCABULARY AND THE VALUES ARE NEVER
READ. Eight labels appear: `Military Judge:` / `Military Judges:` (who
tried it — the court below's judge, not an appearance) and six ending
`Counsel:` — `Appellate Defense`, `Appellate Government`, `Civilian
Defense`, `Special Victims`, `Special Victims'`, `Appellate Special
Victims'`. A label's own row carries its first value and every following
OFF-AXIS row continues it, so `LCDR Sierra B. Whitaker-Davis, USCG` is
filed under the defence and not under the government four rows later.
livingstone sets `Appellate Special Victims' Counsel: LCDR Elizabeth A.
Hutton, USCG` as ONE unsplit line — the label and its value are told
apart at the colon, not by pdfio's column split, so both forms read.

TWO NUMBERS, AND ONLY ONE OF THEM IS THIS COURT'S DOCKET. The caption
prints the CONVENING AUTHORITY's court-martial number above the court's
own docket — `CGCMG 0373`, `CGCMSP 24980`, and since 2025 the bare form
`25-001(66)` / `25-007(62)` naming the Article. The running head on every
continuation sheet settles which is which: `United States v. Mario A.
ANGEL, No. 1467 (C.G.Ct.Crim.App. 2019)` prints 1467, the `Docket No.`
value. So `docket_number` takes the `Docket No.` and the court-martial
number goes to `lower_court_docket`, where the number the court BELOW
gave the case belongs. Read the other way round — which is what core does
today on all 29 — the docket is `CGCMG 0373` and the real one is filed as
a companion appeal.

WEIGHT DOES NOT READ THIS CAPTION, BECAUSE THE WHOLE STACK IS BOLD. On
nmcca bold was the party and roman the rate; here the banner, both
parties, the pivot, the rate, both numbers and the date are ALL bold and
only the bench designation is roman. So the caption is read by two closed
role vocabularies instead:

  * PARTY STATUS — `Appellant`, `Appellee`, `Petitioner`, `Respondent`,
    `Real Party in Interest`. Finite, and the same list every court prints.
  * the SERVICE and the PAY GRADE — `U.S. Coast Guard`, `(E-4)`, `(O-3)`.
    A row carrying either is the party's rate and service, never its name.

A party BLOCK runs from a name row to the next status row or the pivot,
and the block's first row that is neither status nor designation is the
NAME. That reads `Mario A. ANGEL` off a two-row block and `Daniel Rankin`
off a four-row one, and it never reads a rate as a person.

    ┌────── THE RULED TWO-COLUMN ORDER (3) ────────────────────────────┐
    │              IN THE UNITED STATES COAST GUARD      the masthead  │
    │                 COURT OF CRIMINAL APPEALS                        │
    │  In re A.H.,             │  28 August 2019            the date   │
    │     Petitioner           │                                       │
    │                          │ PETITION FOR EXTRAORDINARY            │
    │  United States,          │ RELIEF AND STAY, FILED    the PAPER   │
    │     Real Party in Interest│ 23 AUGUST 2019           under review│
    │  Daniel Rankin,          │ MISC. DOCKET NO. 002-19    the docket │
    │  Aviation Maintenance …  │                                       │
    │  Third Class (E-4)       │ ORDER                     the TITLE   │
    │  U.S. Coast Guard,       │                                       │
    │     Real Party in Interest│ BEFORE MCCLELLAND, BRUCE &  the panel│
    │                          │ BRUBAKER                              │
    │                       ↑ the DRAWN vertical rule at x=292         │
    └──────────────────────────────────────────────────────────────────┘

The rule's own band is the block: its top (113.4/113.4/109.2) stands one
leading below the masthead's last row and its bottom
(292.9/279.0/274.9) one leading above the byline or the first body
paragraph. Column membership is decided by which side of the DRAWN LINE a
glyph's midpoint falls, never by wording, and the right column's rows are
named by the same closed vocabularies as the banner cover's: a date, the
paper under review, a `MISC. DOCKET NO.`, the court's own name for the
paper (`ORDER`, which the court UNDERLINES — `line_markup` carries the
underline through), and a `BEFORE` roster wrapped over two rows.

WHERE THE READER STOPS. On the banner cover, at the first byline at the
body rail — all 29 print one on page 1. On the ruled order, at the drawn
rule's own bottom: in_re_tucker signs nothing at all, and a claim whose
end depended on a byline would have run into its opinion.

THE COURT'S BYLINE DIALECT, AND THE ONE NAME CORE CANNOT READ. All 34
signings in the corpus (32 lead + livingstone's and steen's separate
writings): `Per curiam:` (6, title-case), `BRUBAKER, Judge:` (16),
`MCCLELLAND, Chief Judge:` (9), `JUDGE, Judge:` (1) and `BRUCE, Judge
(concurring in part and dissenting in part):` (2). Unprofiled, core's
default grammar reads only the per curiams, so 25 of 32 records came back
typed `order` with no author and livingstone and steen lost their
concurrences entirely. `JUDGE, Judge:` still does not parse and cannot be
fixed from a court file — see the core defect reported with this port:
this court seats a judge whose SURNAME is Judge (the roster prints
`MCCLELLAND, JUDGE & BRUBAKER`), and `bylines.py:516` rejects any name
that is a bench word.
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

STYLE_BANNER = "uscgcoca banner cover"
STYLE_RULED = "uscgcoca ruled two-column order"

# ---- uscgcoca's declared facts (measured over all 32 records) -----------
# THE BANNER. One bold row, spanning 117.4-494.4 on a 612pt page, opening
# page 1 on 29 of 32 records. It is the court naming itself.
_BANNER = re.compile(
    r"^IN THE UNITED STATES COAST GUARD COURT OF CRIMINAL APPEALS$"
    r"|^UNITED STATES COAST GUARD COURT OF CRIMINAL APPEALS$", re.I)
# THE MASTHEAD of the ruled order, set over two centred rows.
_MASTHEAD = (re.compile(r"^IN THE UNITED STATES COAST GUARD$", re.I),
             re.compile(r"^COURT OF CRIMINAL APPEALS$", re.I))
# CENTRED ON THE AXIS. Every caption, banner, panel and masthead row in
# the corpus sits within 1.6pt of 306.0; the nearest grid row is 47pt off
# and the nearest recital row 88pt. 6.0 is generous by an order and still
# cannot reach either.
_CENTRED_TOL = 6.0
# THE BENCH DESIGNATION — the landmark every service CCA prints, and the
# one this contract shares with nmcca.
_BENCH = re.compile(r"^Appellate Military Judges$", re.I)
_BEFORE = re.compile(r"^BEFORE\b", re.I)
# THIS COURT'S DOCKET: 'Docket No. 1467', 'Docket No.  001-62-20',
# 'Misc. Docket No. 001-25', 'MISC. DOCKET NO. 002-19'.
_DOCKET = re.compile(r"^(?:Misc\.\s*)?Docket\s+No\.\s*(.+?)[.,]?$", re.I)
# THE CONVENING AUTHORITY'S COURT-MARTIAL NUMBER, above it: 'CGCMG 0373'
# (general), 'CGCMSP 24980' (special), and the 2025 form '25-001(66)'
# naming the UCMJ Article under which the case is docketed.
_CM_NUMBER = re.compile(r"^(?:CGCM[A-Z]*\s*\d+|\d{2}-\d{3}\(\d+\))$")
# THE DATE, as the court sets it: '13 December 2019', '01 June 2020'.
_DATE = re.compile(r"^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$")
# PARTY STATUS — the finite role vocabulary, roman here where nmcca sets
# it italic.
_STATUS = re.compile(
    r"^(?:Appellant|Appellee|Petitioner|Respondent|Real Party in Interest"
    r"|Intervenor|Amicus Curiae|Movant|Cross-Appellant|Cross-Appellee)"
    r"s?[,.]?$", re.I)
# THE SERVICE AND THE PAY GRADE. A caption row carrying either belongs to
# the party's designation and never to its name.
_SERVICE = re.compile(
    r"\bU\.\s?S\.\s+(?:Coast Guard|Navy|Marine Corps|Army|Air Force"
    r"|Space Force)\b|\bUSCG\b", re.I)
_PAYGRADE = re.compile(r"\((?:E|O|W)-\d\)")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
# THE COURT BELOW. The three kinds of court-martial the UCMJ knows, and
# the only openings the recital takes on 25 of the 29 covers that print
# one; the rest state the posture instead ('Review of Petition for
# Extraordinary Relief …', 'Referred to trial on …', 'Sentenced on …').
_COURT_MARTIAL = re.compile(
    r"^(General|Special|Summary)\s+[Cc]ourt-[Mm]artial\b")
# THE LABEL GRID. Its LEFT rail stands at body_x0 + 36 (108.0 on 28 of the
# 29 covers, 108.1 on weiser's slightly wider template).
_GRID_RAIL = (30.0, 42.0)
_JUDGE_LABEL = re.compile(r"^Military Judges?:", re.I)
_COUNSEL_LABEL = re.compile(r"^[A-Z][A-Za-z’'.\- ]*Counsel:", re.I)
# THE PAPER UNDER REVIEW, named in the ruled order's right column.
_PAPER = re.compile(r"^(?:PETITION|WRIT|APPEAL|MOTION|APPLICATION)\b", re.I)
# The court's own name for the ruled paper, underlined in the right column.
_TITLE = re.compile(r"^(?:ORDER|OPINION|JUDGMENT|DECISION)$")
# THE COURT'S SIGNING FORMS. The stop, and nothing below it is touched.
_BYLINE = re.compile(
    r"^(?:PER CURIAM\b|Per curiam\b"
    r"|[A-Z][A-Za-z'’\-]+,\s*(?:Chief |Senior |Acting )?(?:Judge|J\.))")
# Page 1 holds the whole block on all 32; the stop bounds it anyway.
_MAX_PAGES = 1


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---- the profile -------------------------------------------------------
register(CourtProfile(
    "uscgcoca",
    "United States Coast Guard Court of Criminal Appeals",
    # THE DIALECT. Spelled military titles, colon-terminated, plus the
    # abbreviated 'J.' mapped to Judge rather than Justice — this court
    # seats no justices. Without it 25 of 32 records typed `order` with no
    # author and two lost a separate writing (v1diff, before/after).
    byline=BylineGrammar(
        style="prose",
        titles=("Judge", "Chief Judge", "Senior Judge",
                "Appellate Military Judge"),
        also_abbrev=True,
        abbrev_titles=(("J.", "Judge"), *DEFAULT_ABBREV)),
    # The body sets its measure at 72 and opens each paragraph at 108 — a
    # 36pt indent, three times the 12.0 default, and block quotations at
    # 108/144 within the measure. 20.0 puts the quotation fence at 40 so
    # the ordinary opener stays outside it.
    para_indent_min=20.0,
    rollout="migrated",
))


@decider("headmatter.read", court="uscgcoca")
def read_headmatter_uscgcoca(model, geom, **_):
    """Read a Coast Guard CCA cover — banner or ruled — or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    pm = model.pages[0]
    axis = pm.width / 2
    finder = FurnitureFinder(model, body_x0, body_size)

    rows: list[list] = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        if rows and abs(rows[-1][0].top - line.top) <= 2.0:
            rows[-1].append(line)
        else:
            rows.append([line])
    if len(rows) < 8:
        return NOTHING
    txt = [_norm(" ".join(l.plain for l in sorted(g, key=lambda l: l.x0)))
           for g in rows]

    # ---- the dispatch: does the page DRAW a caption divider? ------------
    vrules = [v for v in (pm.v_rules or [])
              if (v.bottom - v.top) > body_size * 3]
    if len(vrules) == 1:
        return _ruled(rows, txt, vrules[0], pm, axis, body_x0)
    if vrules:
        return NOTHING
    return _banner(rows, txt, axis)


# ------------------------------------------------------------------------
# the banner cover
# ------------------------------------------------------------------------

def _banner(rows, txt, axis):
    def mid(i: int) -> float:
        g = rows[i]
        return (min(l.x0 for l in g) + max(l.x1 for l in g)) / 2

    def centred(i: int) -> bool:
        return abs(mid(i) - axis) <= _CENTRED_TOL

    if not (_BANNER.match(txt[0]) and centred(0)):
        return NOTHING
    # ---- the landmarks, in the order the cover sets them ---------------
    # THE LABEL GRID'S OWN RAIL IS THE RULER, AND IT IS MEASURED OFF THIS
    # PAGE. `geom.body_x0` cannot serve: on a two-page slip whose commonest
    # paragraph rail is the INDENT rather than the measure it comes back
    # 108.0 (galliano), and every offset taken from it then names the wrong
    # zone — that record filed its whole recital and its trial judge as
    # counsel and its counsel as panel. So the rail is taken from the first
    # row the court LABELS, and everything is measured against that:
    # measured over all 29 covers the rail is 108.0 (28) or 108.1 (weiser),
    # the caption never comes left of 126.5 and the recital never right of
    # 77.4 — 18.4pt of clearance on one side and 30.6pt on the other.
    grid0 = next((i for i in range(1, len(rows))
                  if _JUDGE_LABEL.match(_norm(rows[i][0].plain))
                  or _COUNSEL_LABEL.match(_norm(rows[i][0].plain))), None)
    panel0 = next((i for i in range(1, len(rows)) if _BEFORE.match(txt[i])),
                  None)
    bench = next((i for i in range(len(rows)) if _BENCH.match(txt[i])), None)
    # The bench designation is the landmark this contract shares with every
    # service CCA; the grid is what makes it a Coast Guard cover. Without
    # both, this is not the contract and core's shared walk reads it better.
    if bench is None or grid0 is None or not (grid0 < bench):
        return NOTHING
    if panel0 is None or not (grid0 < panel0 <= bench):
        panel0 = bench
    rail = rows[grid0][0].x0

    # THE FOOT: the first byline at the recital rail, below the bench. Where
    # the paper signs nothing the bench designation closes the block — a
    # bound the page states either way, never an unbounded run.
    stop = None
    for i in range(bench + 1, len(rows)):
        if _BYLINE.match(txt[i]) and rows[i][0].x0 < rail - 8.0:
            stop = i
            break
    if stop is None:
        stop = bench + 1

    kinds: list[str | None] = [None] * stop
    kinds[0] = "court"
    for i in range(1, stop):
        x0 = rows[i][0].x0
        if i >= panel0:
            kinds[i] = "panel"
        elif i >= grid0:
            if abs(x0 - rail) <= 3.0:
                kinds[i] = "lower-court" \
                    if _JUDGE_LABEL.match(_norm(rows[i][0].plain)) \
                    else "counsel"
            else:
                # AN OFF-RAIL ROW INSIDE THE GRID CONTINUES THE LABEL ABOVE
                # IT — the value column stands at 297.0-306.1 and a name
                # four rows below its label still belongs to it.
                kinds[i] = next((k for k in reversed(kinds[:i])
                                 if k in ("counsel", "lower-court")),
                                "counsel")
        elif x0 > rail + 4.0:
            kinds[i] = _caption_kind(txt[i])
        else:
            # THE RECITAL IS A RUN AND ITS WRAP IS NOT A SECOND FACT.
            # 'General Court-Martial convened by Commander, Coast Guard
            # Pacific Area. Tried at …' / '…California, on 24 February - 3
            # March 2020.' is one statement of where the case was tried, so
            # the run keeps the kind its OPENING row states.
            prev = next((k for k in reversed(kinds[:i])
                         if k in ("recital-lc", "recital-ci")), None)
            kinds[i] = prev or ("recital-lc" if _COURT_MARTIAL.match(txt[i])
                                else "recital-ci")

    # ---- emit ----------------------------------------------------------
    ctx = _Ctx()
    cap: list[int] = []
    grid: list[tuple[str, str, str]] = []   # role, label, value
    recital: list[str] = []
    dockets: list[str] = []
    cm_numbers: list[str] = []
    date: str | None = None
    for i in range(stop):
        kind = kinds[i]
        if kind is None:
            continue
        if kind == "court":
            ctx.crit.setdefault("court", txt[i])
            ctx.emit(rows[i], "court", centre=True)
            continue
        if kind in ("caption", "docket", "case-info-num", "date"):
            if kind == "docket":
                dockets.append(_DOCKET.match(txt[i]).group(1))
            elif kind == "case-info-num":
                cm_numbers.append(txt[i])
            elif kind == "date":
                date = date or txt[i]
            else:
                cap.append(i)
            ctx.emit(rows[i], "date" if kind == "date" else
                     ("docket" if kind in ("docket", "case-info-num")
                      else "caption"), centre=True)
            continue
        if kind in ("recital-lc", "recital-ci"):
            recital.append(txt[i])
            ctx.emit(rows[i],
                     "lower-court" if kind == "recital-lc" else "case-info",
                     centre=False)
            continue
        if kind in ("counsel", "lower-court"):
            label, value = _grid_cell(rows[i])
            grid.append((kind, label or "", value))
            ctx.emit(rows[i], kind, centre=False)
            continue
        if kind == "panel":
            ctx.emit(rows[i], "panel", centre=True)
            continue

    _fill(ctx, txt, rows, cap, grid, recital, dockets, cm_numbers, date,
          [i for i in range(stop) if kinds[i] == "panel"])
    ctx.crit.setdefault("headmatter_style", STYLE_BANNER)
    return ctx.result()


def _caption_kind(text: str) -> str:
    if _DOCKET.match(text):
        return "docket"
    if _CM_NUMBER.match(text):
        return "case-info-num"
    if _DATE.match(text):
        return "date"
    return "caption"


def _grid_cell(group: list) -> tuple[str | None, str]:
    """A grid row's LABEL and its VALUE. pdfio splits most of them at the
    column gap; livingstone sets one unsplit, so the colon — not the split
    — is what tells the two apart."""
    parts = sorted(group, key=lambda l: l.x0)
    head = _norm(parts[0].plain)
    rest = _norm(" ".join(p.plain for p in parts[1:]))
    if ":" in head:
        label, _, tail = head.partition(":")
        value = _norm((tail + " " + rest).strip())
        return _norm(label) + ":", value
    return None, _norm(head + " " + rest)


# ------------------------------------------------------------------------
# the ruled two-column order
# ------------------------------------------------------------------------

def _ruled(rows, txt, vrule, pm, axis, body_x0):
    """The caption is the DRAWN RULE'S OWN BAND, and a glyph's column is
    the side of that line its midpoint falls on."""
    head = [i for i in range(len(rows)) if rows[i][0].top < vrule.top - 2.0]
    band = [i for i in range(len(rows))
            if vrule.top - 2.0 <= rows[i][0].top <= vrule.bottom + 2.0]
    if len(head) != 2 or len(band) < 5:
        return NOTHING
    if not (_MASTHEAD[0].match(txt[head[0]])
            and _MASTHEAD[1].match(txt[head[1]])):
        return NOTHING

    ctx = _Ctx()
    ctx.crit.setdefault("court", _norm(txt[head[0]] + " " + txt[head[1]]))
    for i in head:
        ctx.emit(rows[i], "court", centre=True)

    left_rows: list[m.HmLine] = []
    right_rows: list[m.HmLine] = []
    left_plain: list[str] = []
    right_plain: list[str] = []
    ids: list[int] = []
    dockets: list[str] = []
    paper: list[str] = []
    panel_rows: list[str] = []
    date: str | None = None
    title: str | None = None
    state: str | None = None
    for i in band:
        lc = [l for l in rows[i] if (l.x0 + l.x1) / 2 < vrule.x]
        rc = [l for l in rows[i] if (l.x0 + l.x1) / 2 >= vrule.x]
        lt = _norm(" ".join(l.plain for l in sorted(lc, key=lambda l: l.x0)))
        rt = _norm(" ".join(l.plain for l in sorted(rc, key=lambda l: l.x0)))
        # THE RIGHT COLUMN IS A RUN MACHINE, and the run is closed by a
        # BLANK CELL IN ITS OWN COLUMN — never by what stands opposite it
        # in the left one. `RELIEF AND STAY, FILED` continues the paper
        # under review while `United States,` is being set beside it, and
        # a bound that looked left read every continuation as a caption.
        if not rt:
            state = None
            role = "caption"
        elif _DOCKET.match(rt):
            role, state = "docket", None
            dockets.append(_DOCKET.match(rt).group(1))
        elif _DATE.match(rt):
            role, state = "date", None
            date = date or rt
        elif _TITLE.match(rt):
            role, state = "title", None
            title = title or rt
        elif _BEFORE.match(rt):
            role, state = "panel", "panel"
            panel_rows.append(rt)
        elif _PAPER.match(rt):
            role, state = "case-info", "paper"
            paper.append(rt)
        elif state == "panel":
            role = "panel"
            panel_rows.append(rt)
        elif state == "paper":
            role = "case-info"
            paper.append(rt)
        else:
            role = "caption"
        left_rows.append(_cell(lc, pm, "caption"))
        right_rows.append(_cell(rc, pm, role))
        left_plain.append(lt)
        right_plain.append(rt)
        ids.extend(l.id for l in rows[i])
    while left_rows and not left_plain[-1] and not right_plain[-1]:
        left_rows.pop(); right_rows.pop()
        left_plain.pop(); right_plain.pop()
    ctx.items.append(m.CaptionBlock(
        left=left_rows, right=right_rows, rail="|", rail_rows=len(left_rows),
        style_id=STYLE_RULED,
        fp={"rail": "drawn", "rail_band": (vrule.top, vrule.bottom),
            "mid_x": vrule.x},
        prov=m.Prov(pm.number, tuple(sorted(ids)))))
    ctx.consumed.update(ids)

    parties = _parties([t for t in left_plain if t])
    if parties:
        ctx.crit.setdefault("parties", parties)
        ctx.crit.setdefault("case_name", parties[0])
    ctx.crit.setdefault("caption", [t for t in left_plain if t][:40])
    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
    if date:
        ctx.crit.setdefault("decision_date", date)
    if title:
        ctx.crit.setdefault("title", title)
    if paper:
        ctx.crit.setdefault("history", " ".join(paper)[:2000])
    if panel_rows:
        line = _norm(" ".join(panel_rows))
        ctx.crit.setdefault("panel_line", line)
        ctx.crit.setdefault("judges", line)
        names = _panel_names(re.sub(r"^BEFORE\s+", "", line, flags=re.I))
        if names:
            ctx.crit.setdefault("panel", names)
    ctx.crit.setdefault("headmatter_style", STYLE_RULED)
    return ctx.result()


def _cell(cells: list, pm, role: str) -> m.HmLine:
    if not cells:
        return m.HmLine(text="", prov=m.Prov(pm.number), role=role)
    parts = sorted(cells, key=lambda l: l.x0)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
            else piece
    first = parts[0]
    return m.HmLine(
        text=text, prov=m.Prov(pm.number, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


# ------------------------------------------------------------------------
# criteria
# ------------------------------------------------------------------------

def _fill(ctx, txt, rows, cap, grid, recital, dockets, cm_numbers, date,
          panel_idx):
    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if dockets[1:]:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    # THE NUMBER THE CONVENING AUTHORITY GAVE THE CASE — the court below's
    # own docket, not a companion appeal and not this court's number.
    if cm_numbers:
        ctx.crit.setdefault("lower_court_docket", cm_numbers)
    if date:
        ctx.crit.setdefault("decision_date", date)
    if cap:
        ctx.crit.setdefault("caption", [txt[i] for i in cap][:40])
        parties = _parties([txt[i] for i in cap])
        if parties:
            ctx.crit.setdefault("parties", parties)
            pivot = any(_PIVOT.match(txt[i]) for i in cap)
            ctx.crit.setdefault(
                "case_name",
                " v. ".join(parties[:2]) if pivot and len(parties) >= 2
                else parties[0])
    if recital:
        ctx.crit.setdefault("history", " ".join(recital)[:2000])
        first = recital[0]
        if _COURT_MARTIAL.match(first):
            ctx.crit.setdefault(
                "lower_court", _COURT_MARTIAL.match(first).group(0))
    judges = [v for k, l, v in grid if k == "lower-court" and v]
    if judges:
        ctx.crit.setdefault("lower_court_judge", "; ".join(judges))
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE; its text is copied
    # into criteria.attorneys, which core fills only from a MOVED block
    # (core-patch-queue item 41). This whole cover IS the counsel roster.
    counsel: list[str] = []
    for kind, label, value in grid:
        if kind != "counsel":
            continue
        counsel.append(f"{label} {value}".strip() if label else value)
    if counsel:
        ctx.crit.setdefault("attorneys", "; ".join(counsel)[:2000])
    # THE PANEL: 'BEFORE' is apparatus, the bench designation names the
    # bench, and only the row between them carries the membership.
    roster = next((i for i in panel_idx
                   if not _BEFORE.match(txt[i]) and not _BENCH.match(txt[i])),
                  None)
    if roster is not None:
        ctx.crit.setdefault("panel_line", txt[roster])
        names = _panel_names(txt[roster])
        if names:
            ctx.crit.setdefault("panel", names)
        bench = next((txt[i] for i in panel_idx if _BENCH.match(txt[i])), "")
        ctx.crit.setdefault("judges", _norm(txt[roster] + " " + bench))


def _parties(caption: list[str]) -> list[str]:
    """The party NAMES, read by two closed vocabularies. A block runs from
    a name row to the next STATUS row or to the pivot; the block's first
    row that is neither a status nor a rate-and-service designation is the
    name. Nothing is read by wording."""
    blocks: list[list[str]] = [[]]
    for row in caption:
        if _DOCKET.match(row) or _CM_NUMBER.match(row) or _DATE.match(row):
            continue
        if _PIVOT.match(row):
            blocks.append([])
            continue
        if _STATUS.match(row):
            blocks.append([])
            continue
        blocks[-1].append(row)
    out: list[str] = []
    for block in blocks:
        name = next((r for r in block
                     if not _SERVICE.search(r) and not _PAYGRADE.search(r)),
                    None)
        if name:
            out.append(name.strip().rstrip(",;"))
    return out


def _panel_names(line: str) -> list[str]:
    """'MCCLELLAND, BRUBAKER & MOORADIAN' -> three names."""
    out = []
    for piece in re.split(r",|&|\band\b", line):
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
