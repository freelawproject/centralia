"""Supreme Court of the State of Nevada ('nev').

Everything unique to nev lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py, and it declares `byline=BylineGrammar(style="abbrev",
strip_by_the_court=True)` — Nevada signs 'By the Court, BELL, J.:', and that
row is where this reader stops.

THE CONTRACT — Nevada's advance sheets are SCANNED slip opinions. The paper
sets the Reporter's advance cite over its own masthead, then a two-column
band with the parties on the left and NOTHING BUT THE CLERK on the right,
then a double-leaded band saying where the case came from and what the court
did, then the appearances single-leaded at the rail, then the bench, the
paper's own name, and the signature.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                              142 Nev., Advance Opinion 33    cite   │
    │            IN THE SUPREME COURT OF THE STATE OF NEVADA    masthead  │
    │                                                                     │
    │ TYLER DANIEL CARTER,                    │  No. 89594     the docket │
    │        Appellant,                       │  ┌───────────┐            │
    │ vs.                                     │  │  F I L E D│  the CLERK │
    │ THE STATE OF NEVADA,                    │  │ MAY 14 2026│ — dropped │
    │        Respondent.                      │  │ BY  DEPUTY │           │
    │                                         │  └─ CLERK ───┘            │
    │      Appeal from a judgment of conviction, pursuant to a jury        │
    │ verdict, of reckless driving … Eighth Judicial District Court,       │
    │ Clark County; Jennifer Schwartz, Judge.                 the origin  │
    │      Affirmed in part, reversed in part, and remanded.  disposition │
    │                                                                     │
    │ Hayes Wakayama Juan and Dale A. Hayes, Jr., … Las                   │
    │ Vegas,                                                  the         │
    │ for Appellant.                                          appearances │
    │ Aaron D. Ford, Attorney General, Carson City; …                     │
    │ for Respondent.                                                     │
    │                                                                     │
    │ BEFORE THE SUPREME COURT, PICKERING, PARRAGUIRRE, and   the bench   │
    │ BELL, JJ.                                                           │
    │                     OPINION                             the title   │
    │ By the Court, BELL, J.:                                 the writing │
    │  SUPREME                                                            │
    │  COURT OF   (0) 1947A                              the seal, 5pt    │
    │  NEVADA                                                             │
    └─────────────────────────────────────────────────────────────────────┘

MEASURED over the 33 of 50 records that carry a text layer (the other 17
scan to zero lines and this reader answers NOTHING on them):

THE PAGE. 607-612pt wide, 792 tall. `geom.body_x0` measures the rail at
106-108 on every one of the 33; the caption sits 0-8pt right of it, the
'and' between respondents and real parties 15-21pt right of it, and the
origin/disposition paragraphs open 70-73pt right of it. So a row 40pt right
of the rail is a PARAGRAPH OPENER and nothing else is.

THE GUTTER IS REAL AND WIDE. In the caption band the left column's ink ends
by x1=367.5 (planned_parenthood, singh) and the right column's begins at
x0=411.5 (richt) — measured across all 32 opinion records. 0.63 of the
measure falls inside that gutter with 18pt of clearance either side.

THE RIGHT COLUMN HOLDS ONE THING THE COURT WROTE: its docket. Everything
else standing there is the clerk's rubber stamp — 'FILED' at 22-32pt, the
date, 'BY', 'DEPUTY CLERK', a scanned signature, and whatever the OCR made
of them ('A- BRO', 'CkEFCEPUTY CLERK', '1 9? -lA. BRg ; i'). It is dropped
as a stamp, by POSITION, never by wording: no wording survives this scan.

WHY NO decision_date. The stamp date is the only date the paper prints, and
the OCR of it is not a date — 'JAN 29 202', 'MAY 1 it 2026', 'EALIP •R E0N
9• 2026', 'MAR 2 6 2026'. Parsing that would be inventing a fact, so the
stamp goes to `dropped` whole and the criterion is left unset.

THE LEADING NAMES THE BAND. Below the caption the court double-leads what it
says about the case — 23.0-24.1pt between the origin recital's own lines,
and the same between the recital and the disposition — and single-leads the
appearances at 15.0-16.5pt. The step from the disposition to the first
appearance is 38.8-54.7pt on all 32 records. So inside the origin band a
rail row within 26pt of the row above CONTINUES the paragraph, and a rail
row further down has left the band.

THE ORIGIN BAND IS BOUNDED, AND ITS FIRST PARAGRAPH IS THE ORIGIN. Between
the caption and the appearances every record prints exactly two indented
paragraphs: where the case came from ('Appeal from …', 'Original petition
for a writ of mandamus …', 'Consolidated appeals from …', 'Certified
question under NRAP 5 …', 'Jurisdictional prescreening of an appeal …')
and then what the court did ('Affirmed.', 'Petition denied.', 'Question
answered.', 'Reversed and remanded.'). The band decides, not the words —
the FIRST paragraph is the origin, every later one is the disposition — so
the OCR that turned 'Affirmed' into 'Affirrned' and 'reversed' into
'reuersed' costs nothing.

THE BENCH NAMES ITSELF ('BEFORE THE SUPREME COURT, …'), and its second line
is a wrap at the rail 15-16pt below. 'EN BANC.' yields no panel names; a
three-judge row yields three.

THE GATE IS THE SHAPE: the masthead, the signature, a caption and an origin
recital. Not the docket — robinson_maurice_v._state_criminal's 'No. 89xxx'
went under the clerk's stamp in the scan, and gating on it cost that record
its whole block for an OCR failure.

THE BYLINE ENDS THE READER — 'By the Court, STIGLICH, J.:' — and it is left
UNCLAIMED so that core opens the writing on it. The claim is otherwise
TOTAL from the first row to that one: every row above it is an item or a
Dropped, because a hole inside the claim lets core open a writing there and
the bisection invariant then empties the headmatter into it.

WHAT IS NOT CLAIMED. `engle_julie_v._dist._ct._state_criminal_2` is a
PARTY'S filing (a 'NOTICE OF SERVICE OF WRIT AND OPINION AND RETURN' with
an e-filing stamp, a typed rule closing the caption, and no bench, title or
byline). It prints the masthead and nothing else this contract describes,
so the reader answers NOTHING rather than forcing it through.

THE SEAL IS FURNITURE. Every page carries 'SUPREME COURT OF NEVADA' and a
form number ('(0) 1947A') in 4.5-8pt at the foot; page 1's real ink reaches
713.1 at the deepest (in_re_estate_of_ulvang's 'Pro Se.', 12.5pt), so the
foot is taken by SIZE inside the bottom band, never by the band alone.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder, is_folio_text

# THE MASTHEAD, spelled through the scan: 'SUPREME COTJRT', 'SUPREME
# COLTRT', 'SUPPEME COVRT' all occur, and lennar drops the leading 'IN'.
# The two words that survive every scan are 'THE' and 'NEVADA'.
_COURT_NAME = "IN THE SUPREME COURT OF THE STATE OF NEVADA"
_MASTHEAD = re.compile(
    r"^(?:IN\s+)?THE\s+SU\S+\s+CO\S+\s+OF\s+THE\s+STATE\s+OF\s+NEVADA\.?$",
    re.I)
# The Reporter's advance cite, printed above the masthead: '142 Nev.,
# Advance Opinion 33'. The trailing number is the advance-opinion number and
# the OCR loses it as often as not ('LOS', 'oR', '.: C‘', '°WS)').
_CITE = re.compile(
    r"^(1\d\d)\s*Nev[.,]{0,2}\s*Advan\S*\s*Opini\S*\s*(\d{1,3})?\b", re.I)
# 'No. 89594' / 'No, 89238' — the court's own number, in the right column.
_DOCKET = re.compile(r"^No[.,]?\s*(\d{4,6})\b", re.I)
# 'BEFORE THE SUPREME COURT, EN BANC.' / '…, PICKERING, PARRAGUIRRE, and'
_BENCH = re.compile(r"^BEFORE\s+THE\s+SU\S+\s+CO\S+[,.;:]?\s*(.*)$", re.I)
# Words that stand in the bench line without naming a justice.
_NOT_A_NAME = {"EN", "BANC", "J", "JJ", "C.J", "CJ", "THE", "AND", "COURT",
               "SUPREME", "CHIEF", "JUSTICE", "JUSTICES"}
# 'OPINION' — what the paper calls itself. Scanned as 'OPINIO?V'.
_TITLE = re.compile(r"^OPINI\S{0,4}\.?$", re.I)
# 'By the Court, BELL, J.:' — the signature, and the end of the block.
_BYLINE = re.compile(r"^By\s+the\s+Co\S+\b|^PER\s+CURIAM", re.I)
# THE FILED PAPER'S OWN MARKS (the second contract, below).
# The caption closes on a TYPED RULE the form draws with underscores and
# ends with a solidus — '______________________________________/'. It is the
# only thing on the sheet that says where the caption stops, there being no
# origin recital under it.
_TYPED_CLOSER = re.compile(r"^_{6,}\s*/?\s*$")
# THE CLERK'S E-FILING STAMP, in the right column above the docket. Four
# rows, and none of them is anything this court wrote.
_EFILED = re.compile(
    r"^Electronically\s+Filed\b|^Clerk\s+of\s+(?:the\s+)?Supreme\s+Court\b"
    r"|^\w{3}\s+\d{1,2}\s+\d{4}\s+\d{1,2}:\d{2}\s*[AP]M\b", re.I)
# WHAT THE FILER CALLS THE PAPER: a centred all-caps row above the text.
_FILED_TITLE = re.compile(
    r"^(?:NOTICE|MOTION|PETITION|RETURN|RESPONSE|REPLY|STIPULATION)\b[A-Z ,.'()/-]*$")

# A row 40pt right of the measured rail opens a paragraph. Measured: the
# origin/disposition indent runs 70-73pt over the rail; the deepest caption
# row ('and', between the respondents and the real party) is 21pt over it.
_INDENT_MIN = 40.0
# The gutter between the caption and the clerk: left ink ends by 0.60 of the
# measure, right ink begins at 0.67 (x1=367.5 / x0=411.5 on a 612pt page).
_RIGHT_COL = 0.63
# Double-leaded band (23.0-24.1pt) vs the step to the appearances
# (38.8-54.7pt), measured on all 32 opinion records.
_ORIGIN_LEAD_MAX = 26.0
# The bench's wrap sits 15.0-16.5pt below its first line.
_WRAP_LEAD_MAX = 20.0
# The seal and the form number are 4.5-8.0pt; nothing the court prints on
# these pages falls below 12.0pt.
_FOOT_SIZE_MAX = 9.5
_FOOT_BAND = 0.88
# The masthead stands in the first rows — under the cite, and under the OCR
# speck in_re_estate_of_ulvang scanned above it.
_MASTHEAD_ROWS = 5
_MAX_PAGES = 3
# THE TITLE BEGINS ON THE AXIS — it is not centred on it. Measured on all
# 32 records that print it, 'OPINION' opens at x0 299.7-306.0 against a page
# axis of 303.5 (607pt paper) or 306.0 (612pt), and runs 61pt right of that,
# so its MID-POINT stands 27pt off the axis and a mid-point test finds no
# title at all — which is what it did on the first pass (0 of 32 tagged).
# The masthead scans the same way (x0 151-163 over a 514 right edge).
_AXIS_X0_TOL = 8.0
# FurnitureFinder.kind's CORNER-STAMP rule (resolve/furniture.py:384-401)
# calls
# any short row in the top 19% of the page a stamp when its type is 2pt
# under the measured body size — which on singh_v._dist._ct._singh_civil_1
# deletes the counsel row 'for Petitioners.' (page 2, top 98.4, x0 106.3,
# 12.0pt against a measured 14.5). Reported, not patched: this reader honours
# only the finder's REPEAT-measured verdicts and does its own stamp work by
# column.
_FURNITURE_KINDS = ("folio", "running-head", "running-foot", "gutter")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="nev")
def read_headmatter_nev(model, geom, **_):
    """Read Nevada's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 107.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 8:
        return NOTHING
    texts = [_norm(" ".join(l.plain for l in g)) for g in rows]
    # THE DISPATCH: the masthead, wherever the cite above it happens to end.
    mast = next((i for i, t in enumerate(texts[:_MASTHEAD_ROWS])
                 if _MASTHEAD.match(t)), None)
    if mast is None:
        return NOTHING
    # AND THE SIGNATURE, which is what bounds the walk. A paper that prints
    # the masthead and never signs is not this contract (a party's notice of
    # service, filed under the same caption) and is left to core.
    if not any(_BYLINE.match(t) for t in texts[mast + 1:]):
        return _read_filed_paper(rows, texts, mast, page1, body_x0)

    ctx = _Ctx()
    caption: list[str] = []
    parties: list[str] = []
    origin: list[str] = []
    disposition: list[str] = []
    counsel: list[str] = []
    bench: list[str] = []
    dockets: list[str] = []
    band = "head"           # head | caption | origin | counsel | bench
    origin_paras = 0
    origin_role = "lower-court"
    prev_top: float | None = None
    prev_page: int | None = None

    for group, text in zip(rows, texts):
        pieces = sorted(group, key=lambda l: l.x0)
        if not text:
            continue
        first = pieces[0]
        page_no = first.page
        pm = model.pages[page_no - 1] if page_no <= len(model.pages) else page1
        width, height = pm.width, pm.height
        on_axis = abs(first.x0 - width / 2) <= _AXIS_X0_TOL
        indented = first.x0 - body_x0 >= _INDENT_MIN
        same_page = prev_page == page_no
        lead = (first.top - prev_top) if (same_page and prev_top is not None) \
            else None

        # ---- THE SIGNATURE ENDS THE READER -----------------------------
        if band != "head" and _BYLINE.match(text):
            break

        # ---- THE FOOT: the seal and the form number, by SIZE ------------
        if first.top >= height * _FOOT_BAND \
                and ((first.size or 0.0) <= _FOOT_SIZE_MAX
                     or is_folio_text(text)):
            ctx.drop(pieces, "running-foot")
            continue
        kind = finder.kind(pm, first)
        if kind in _FURNITURE_KINDS:
            ctx.drop(pieces, kind)
            continue

        # ---- THE RIGHT COLUMN: the docket, then the clerk --------------
        if first.x0 >= width * _RIGHT_COL:
            docket = _DOCKET.match(text)
            if docket:
                dockets.append(docket.group(1))
                ctx.emit(pieces, "docket", centre=False)
            else:
                ctx.drop(pieces, "stamp")
            continue

        # ---- ABOVE THE MASTHEAD: the Reporter's cite, and scan specks ---
        if band == "head":
            if _MASTHEAD.match(text):
                # criteria.court only where the scan spelled it — a court
                # named 'THE SUPREME COTJRT' is worse than no value.
                if text.upper() == _COURT_NAME:
                    ctx.crit.setdefault("court", text)
                ctx.emit(pieces, "court")
                band = "caption"
                prev_top, prev_page = first.top, page_no
                continue
            cite = _CITE.match(text)
            if cite:
                # The printed tail is dropped where the scan lost it; the
                # volume and the advance number are what the cite states.
                value = f"{cite.group(1)} Nev., Advance Opinion"
                if cite.group(2):
                    value = f"{value} {cite.group(2)}"
                ctx.crit.setdefault("citation", value)
                ctx.emit(pieces, "citation", centre=False)
            else:
                ctx.drop(pieces, "stamp")
            prev_top, prev_page = first.top, page_no
            continue

        # ---- THE BENCH, and the paper's own name ------------------------
        benched = _BENCH.match(text)
        if benched:
            band = "bench"
            bench.append(text)
            ctx.emit(pieces, "panel", centre=False)
            prev_top, prev_page = first.top, page_no
            continue
        if band == "bench" and not on_axis and lead is not None \
                and lead <= _WRAP_LEAD_MAX:
            bench.append(text)
            ctx.emit(pieces, "panel", centre=False)
            prev_top, prev_page = first.top, page_no
            continue
        if on_axis and _TITLE.match(text):
            if text.upper() == "OPINION":
                ctx.crit.setdefault("title", "OPINION")
            ctx.emit(pieces, "title")
            band = "bench"
            prev_top, prev_page = first.top, page_no
            continue

        # A paragraph opening on the indent once the appearances have been
        # printed is the writing's own prose, not this block. Each state is
        # bounded; the byline is the ordinary end, this is the backstop.
        #
        # IT MUST STAND LAST. The title is itself indented (x0 ~302), and so
        # is the clerk's scrawl in page 1's bottom-right corner — where the
        # signature falls on page 2, that corner is INSIDE the claimed span
        # and is neither small type nor a folio ('7.A.-i3g9y' at 18.6pt,
        # 'To- kli-E0' at 29pt, '2b- cA552' at 32pt). Tested before the
        # right-column rule it ended the walk 100pt short and the scrawl
        # became a PHANTOM WRITING on 8 of the 32 records.
        if band in ("counsel", "bench") and indented:
            break

        # ---- THE CAPTION: the left column above the first indent -------
        if band == "caption":
            if not indented:
                caption.append(text)
                # THE PARTY NAMES ARE THE CAPS ROWS. Nevada sets every party
                # in full capitals and every status in caps-and-lower
                # ('Appellant,', 'Real Party in Interest.'), so the case is
                # the discriminator and no wording is read. It also survives
                # the scan's OVERPRINT: the pivot is struck through the
                # status on 9 records ('Avsp.pellant,' is 'Appellant,' with
                # 'vs.' over it, 'vPse.titioners,' is 'Petitioners,'), which
                # no status vocabulary can match — but which is never caps.
                if text.upper() == text:
                    parties.append(text)
                ctx.emit(pieces, "caption", centre=False)
                prev_top, prev_page = first.top, page_no
                continue
            band = "origin"

        # ---- THE ORIGIN BAND: two double-leaded paragraphs -------------
        if band == "origin":
            if indented:
                origin_paras += 1
                origin_role = "lower-court" if origin_paras == 1 \
                    else "disposition"
            elif lead is None or lead > _ORIGIN_LEAD_MAX:
                band = "counsel"
            if band == "origin":
                (origin if origin_role == "lower-court"
                 else disposition).append(text)
                ctx.emit(pieces, origin_role, centre=False)
                prev_top, prev_page = first.top, page_no
                continue

        # ---- THE APPEARANCES, single-leaded at the rail -----------------
        if band == "counsel":
            counsel.append(text)
            ctx.emit(pieces, "counsel", centre=False)
            prev_top, prev_page = first.top, page_no
            continue

        # A ROW AT NO POSITION THIS PAPER USES is left to core rather than
        # tinted with a role that would be a guess.
        prev_top, prev_page = first.top, page_no

    # THE SHAPE IS THE GATE, not any one value. Requiring a docket cost
    # robinson_maurice_v._state_criminal its whole block: the scan lost the
    # 'No. 89xxx' row under the clerk's stamp, and the record is otherwise
    # this contract line for line. The masthead, the signature, the caption
    # and the origin recital are the four things every one of the 32 prints.
    if not caption or not origin_paras:
        return NOTHING
    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if len(dockets) > 1:
            # Consolidated appeals print a caption and a number each
            # (el_cortez: 87236 and 88370; rosenbrook: 84452 and 85175).
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if caption:
        ctx.crit.setdefault("caption", caption)
    if parties:
        ctx.crit.setdefault("parties", parties[:8])
    if origin:
        ctx.crit.setdefault("history", " ".join(origin)[:2000])
        below = _COURT_BELOW.search(" ".join(origin))
        if below:
            ctx.crit.setdefault("lower_court", _norm(below.group(1)))
        judged = _JUDGE_BELOW.search(" ".join(origin))
        if judged:
            ctx.crit.setdefault("lower_court_judge", _norm(judged.group(1)))
    if disposition:
        ctx.crit.setdefault("disposition", " ".join(disposition)[:400])
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    if bench:
        line = " ".join(bench)
        ctx.crit.setdefault("panel_line", line)
        names = _panel_names(line)
        if names:
            ctx.crit.setdefault("panel", names)
    return ctx.result()


# THE COURT BELOW, in the three forms the origin recital prints. Each is
# closed and each carries its OWN tail: the state form runs to the county
# (and to 'Family Division' where the case is one), the two federal forms to
# their district or circuit. An open tail ('[^;.]*') is what put 'concerning
# an excess insurer's ability to claim equitable subrogation…' in
# north_river's lower_court — the state form ends at the ';' before the
# judge, and the federal forms end at no punctuation at all.
_COURT_BELOW = re.compile(
    r"((?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth"
    r"|Eleventh)\s+Judicial\.?\s+District\s+Court"
    r"(?:,\s+Family\s+Division)?(?:,\s+[A-Z][a-z]+\s+County)?"
    r"|United\s+States\s+District\s+Court"
    r"(?:\s+for\s+the\s+District\s+of\s+[A-Z][a-z]+)?"
    r"|United\s+States\s+Court\s+of\s+Appeals"
    r"(?:\s+for\s+the\s+[A-Z]\w+\s+Circuit)?)", re.I)
# '… Clark County; Jennifer Schwartz, Judge.'
_JUDGE_BELOW = re.compile(r";\s*([^;]{3,60}?),\s*(?:District\s+)?Judge\.?\s*$")


def _panel_names(line: str) -> list[str]:
    """The justices the bench line names. 'EN BANC' names none."""
    tail = _BENCH.match(line)
    if not tail:
        return []
    out: list[str] = []
    for tok in re.split(r"[,.;]|\band\b", tail.group(1)):
        word = tok.strip().strip(".,;:")
        # 'EN BANC' is ONE token — the split never breaks it — so the test
        # is on every word in the token, not on the token as a whole. Left
        # word-wise it named a justice called 'EN BANC' on the 12 en banc
        # records.
        if len(word) >= 3 and word.upper() == word \
                and re.match(r"^[A-Z][A-Z'\- ]+$", word) \
                and not all(w in _NOT_A_NAME for w in word.upper().split()):
            out.append(word)
    return out


def _rows(pm, finder) -> list[list]:
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    out: list[list] = []
    for k in order:
        row = groups[k]
        # A ROW WHOSE PIECES STAND APART is two elements the page set on one
        # line — a caption row and the docket or the clerk's stamp beside it
        # ('GREGORY BURNS, | No. 89998'; 'Respondents, | CHÝ Di | CLERK').
        # Every multi-piece row on page 1 is that, over all 32 records.
        if len(row) > 1:
            out.extend([piece] for piece in row)
        else:
            out.append(row)
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

    def cell(self, parts: list, role: str, page: int):
        parts = sorted(parts, key=lambda l: l.x0)
        if not parts:
            return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                            role=role)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def box(self, rows: list) -> None:
        """The caption, as the clerk's form sets it: two columns paired by
        the printed row, over the whitespace gutter documented above."""
        left, right = [], []
        ids: set[int] = set()
        for pg, l_cells, r_cells in rows:
            left.append(self.cell(l_cells, "caption", pg))
            right.append(self.cell(r_cells, "docket" if r_cells
                                   else "caption", pg))
            ids.update(c.id for c in l_cells + r_cells)
        while left and not (left[-1].text or "").strip() \
                and not (right[-1].text or "").strip():
            left.pop()
            right.pop()
        if not left:
            return
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=len(left),
            style_id="open-gutter", fp={"rail": None},
            prov=m.Prov(rows[0][0], tuple(sorted(ids)))))
        self.consumed.update(ids)

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


# --------------------------------------------------------------------------
# THE SECOND CONTRACT — THE FILED PAPER
# --------------------------------------------------------------------------
#
#     IN THE SUPREME COURT OF THE STATE OF NEVADA        the masthead
#     JULIE ENGLE,                    │ Electronically Filed   the clerk's
#          Petitioner,                │ Apr 24 2026 04:04 PM   e-filing
#          vs.                        │ Elizabeth A. Brown     stamp —
#     THE SECOND JUDICIAL DISTRICT    │ Clerk of Supreme Court dropped
#     COURT, IN AND FOR THE           │
#     COUNTY OF WASHOE; THE           │
#     HONORABLE DAVID HARDY,          │
#          Respondents,               │
#     and,                            │ No. 89183       the docket
#     THE STATE OF NEVADA,            │
#          Real Party In Interest.    │
#     ______________________________________/   the caption's own closer
#          NOTICE OF SERVICE OF WRIT AND OPINION AND RETURN   the title
#
# A PAPER FILED IN THIS COURT, under this court's caption, by a party rather
# than by the bench: engle_julie_..._2 serves the writ and opinion issued in
# engle_julie_..._1 and attaches them as scanned exhibits. It prints the
# masthead and the court's own docket, so the caption IS readable and there
# is no reason to leave it unread — but it signs nothing, recites no origin,
# names no bench and states no disposition, so the first contract above
# rightly refuses it and this one takes it instead.
#
# THE GATE IS THE CLOSER. A typed rule of underscores ending in a solidus is
# what this form draws where the opinion draws its origin recital, and
# nothing in the 33 records of the first contract draws one. Without it a
# masthead alone would let any unsigned page through.


def _read_filed_paper(rows, texts, mast, page1, body_x0):
    """Read a party's filing on this court's caption, or NOTHING."""
    closer = next((i for i, t in enumerate(texts[mast + 1:], mast + 1)
                   if _TYPED_CLOSER.match(t)), None)
    if closer is None:
        return NOTHING
    ctx = _Ctx()
    caption: list[str] = []
    dockets: list[str] = []
    box_left: list = []
    box_right: dict = {}
    for i in range(mast, closer + 1):
        group, text = rows[i], texts[i]
        pieces = sorted(group, key=lambda l: l.x0)
        if not text:
            continue
        first = pieces[0]
        if i == mast:
            ctx.crit.setdefault("court", _COURT_NAME)
            ctx.emit(pieces, "court")
            continue
        if _TYPED_CLOSER.match(text):
            # The form's own rule, claimed so no hole is left in the block.
            ctx.drop(pieces, "rule")
            continue
        if first.x0 >= page1.width * _RIGHT_COL:
            docket = _DOCKET.match(text)
            if docket:
                dockets.append(docket.group(1))
                box_right.setdefault(round(first.top, 1), []).extend(pieces)
            else:
                ctx.drop(pieces, "stamp")     # the clerk's e-filing stamp
            continue
        caption.append(text)
        box_left.append((first.page, round(first.top, 1), pieces))
    if not box_left or not dockets:
        return NOTHING
    ctx.box([(pg, pieces, box_right.get(top, []))
             for pg, top, pieces in box_left])
    # WHAT THE FILER CALLS THE PAPER, the first centred all-caps row under
    # the closer. It is the only thing below the caption this contract reads.
    for i in range(closer + 1, min(closer + 4, len(rows))):
        text = texts[i]
        if text and _FILED_TITLE.match(text):
            ctx.crit.setdefault("title", text)
            ctx.emit(rows[i], "title")
        break
    ctx.crit["docket_number"] = dockets[0]
    if dockets[1:]:
        ctx.crit["other_dockets"] = dockets[1:]
    # THE PARTIES ARE THE CAPS ROWS, as in the first contract above: the
    # court sets a party name in capitals and its status in caps-and-lower.
    parties = [t for t in caption if t and t.upper() == t
               and not _TYPED_CLOSER.match(t)]
    if parties:
        ctx.crit.setdefault("parties", parties[:8])
    ctx.crit.setdefault("caption", [c for c in caption if c])
    ctx.crit["headmatter_style"] = "filed paper"
    return ctx.result()
