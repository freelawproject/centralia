"""Louisiana Court of Appeal ('lactapp').

Everything unique to lactapp lives here. It imports core, never another
court file, and no other court file imports it — not `la.py`, whose Supreme
Court prints a Clerk's news-release sheet this court has no equivalent of.
Its CourtProfile is registered in courts/__init__.py.

THE COURT PRINTS TWO PAPERS, and one of them is a PHOTOGRAPH. Counted over
all 42 records:

    typeset judgments of the SECOND CIRCUIT          30
    single-sheet writ actions, scanned               12

The twelve are a full-bleed raster on one sheet (`image_area` 1.00, body
type measured at 5.5-8.2pt where it is measured at all) — the First
Circuit's writ dispositions, photographed. core's own scan test answers for
them and this reader declines them, which is why the dispatch below is the
DIVIDER and not the court's name: the scans carry the name too.

THE DIVIDER IS THE STRUCTURE, AND THE COURT TYPES IT. Every one of the 30
judgments sets '* * * * *' on a row of its own, FOUR TIMES, and the four
fence the block into five sections. Measured over all 120 of them the row's
ink runs 299.6-348.5 and its centre is 323.93-324.07 — so the divider does
two jobs at once, and the second one is the reason this file is short:

    IT MARKS THE AXIS THE TWO COLUMNS STRADDLE. The block is set on its own
    axis, (108 + 540) / 2 = 324, and NOT on the page's (306). No rule is
    drawn anywhere — `v_rules` and `h_rules` are 0 on every page of every
    record — so the gutter is white space, and the court's own typed row is
    the only thing on the sheet that measures where it runs.

    ┌───────────────────────────────────────────────────────────────────┐
    │                              Judgment rendered April 22, 2026.    │ 1
    │                              Application for rehearing may be     │
    │                              filed within the delay allowed by    │
    │                              Art. 2166, La. C.C.P.                │
    │                        No. 56,796-CA                              │
    │                       COURT OF APPEAL                             │
    │                       SECOND CIRCUIT                              │
    │                      STATE OF LOUISIANA                           │
    │                          * * * * *                                │
    │  ALICE CLARK                      Plaintiff-Appellant             │ 2
    │                    versus                                         │
    │  ST. FRANCIS MEDICAL                Defendant-Appellee            │
    │  CENTER, INC.                                                     │
    │                          * * * * *                                │
    │                       Appealed from the                           │ 3
    │            Fourth Judicial District Court for the                 │
    │                Parish of Ouachita, Louisiana                      │
    │                  Trial Court No. 2019-2615                        │
    │         Honorable Frederick Douglass Jones, Judge                 │
    │                          * * * * *                                │
    │  LAW OFFICE OF                       Counsel for                  │ 4
    │  ANTHONY J. BRUSCATO                 Appellant                    │
    │  By: Anthony J. Bruscato                                          │
    │                          * * * * *                                │
    │            Before PITMAN, COX, and HUNTER, JJ.                    │ 5
    └───────────────────────────────────────────────────────────────────┘

    1 the court's date and its rehearing notice, the docket, the court
    2 the caption, in two columns: the parties left, their postures right
    3 where the case came from, on the axis
    4 the appearances, in two columns: the firm left, who it appears for
    5 who sat

SECTION 1 IS EIGHT ROWS ON 29 OF THE 30, and section 3 is five on 28 — this
paper does not vary. What varies is the wording, and none of it is
load-bearing: the rehearing notice cites Art. 2166 on the 22 civil records
and Art. 922 on the 8 criminal ones; the origin opens 'Appealed from the'
on 29 and 'On Application for Writs from the' on one; the tribunal below is
a numbered district court on 26, a city court on one, and the Office of
Workers' Compensation on two — which sign their judge on two rows with no
'Honorable' at all ('Christopher T. Lee' / 'Workers' Compensation Judge (Ad
Hoc)').

WHICH COLUMN A CELL IS IN IS NOT WHICH SIDE OF THE AXIS IT ENDS ON. Eight
of the appearances' firm names are long enough to run PAST the axis from
the left rail ('PETTIETTE, ARMAND, DUNKELMAN, / HUDSON, POTTS & BERNSTEIN,
LLP' reaches 363.5), and three captions set a single party's name the same
way. Read by 'does the ink cross 324' they would each have become a
full-width row and broken the column. So a full-width row is one CENTRED on
the axis and alone on its printed row — which the pivot ('versus', 27
records), the docket, the court's three rows, the origin and the panel all
are, and which no cell in the corpus is: the widest left cell centres at
235.8 and the leftmost right cell at 366.5.

WHAT THIS FILE DOES NOT DO. It reads the block above the writing and
nothing else: the byline ('HUNTER, J.' at the rail of page 2), the separate
writings, the footnotes and the closing disposition are core's, and are
configured on the profile in courts/__init__.py.
"""

from __future__ import annotations

import re
from collections import defaultdict

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import roster_names

# ---- the divider, and the axis it marks ------------------------------------

# The court's typed divider: stars and spaces, nothing else. Five stars on
# every one of the 120 rows, but the count is not required — a row that is
# punctuation and whitespace, in body type, on its own, is the divider.
_STAR = re.compile(r"^[*\s]{5,}$")
_STARS_WANTED = 4
# The block's own axis, and how close to it a row must centre to be one of
# the court's full-width rows. Measured: the divider centres at 324.0 on
# every record; the pivot at 324.1; the widest LEFT cell in the corpus
# centres at 235.8 and the leftmost RIGHT cell at 366.5, so a 12pt window
# has 88pt of clear air either side of it.
_AXIS_TOL = 12.0
# A cell's own side, once it is not full-width: which side of the axis its
# ink CENTRES on. Not which side it ends on — see the docstring.
_MAX_PAGES = 2              # 4 of the 30 close the block on page 2

# ---- what each row of the block says --------------------------------------

_RENDERED = re.compile(r"^Judgment\s+rendered\s+(.+?)\.?\s*$", re.I)
# The court's standing notice that the judgment is not yet final. It is the
# court's own row, printed on all 30 — not a publication flag and not
# something to remove — so it is read as `case-info`, which is what the
# render calls caption apparatus that has no role of its own.
_NOTICE = re.compile(r"^(?:Application\s+for\s+rehearing|within\s+the\s+delay"
                     r"|La\.\s*C\.\s*(?:Cr\.\s*)?C\.\s*P\.)", re.I)
_DOCKET = re.compile(r"^No\.\s*(\S.*?)\s*$", re.I)
_CONSOLIDATED = re.compile(r"^\(?Consolidated\s+Cases?\)?\.?$", re.I)
_COURT_ROWS = ("court of appeal", "second circuit", "first circuit",
               "third circuit", "fourth circuit", "fifth circuit",
               "state of louisiana")
_PIVOT = re.compile(r"^versus$", re.I)
# THE PARTY'S STATUS, printed beside the party it belongs to. The whole
# vocabulary over the 30 records: Plaintiff, Defendant, Appellant, Appellee,
# Respondent, Applicant, and their plurals, joined by a hyphen the page
# sometimes spaces off ('Defendants -Applicants'). A closed list, because
# the court's is closed.
_STATUS_WORDS = frozenset((
    "plaintiff", "plaintiffs", "defendant", "defendants", "appellant",
    "appellants", "appellee", "appellees", "respondent", "respondents",
    "applicant", "applicants", "relator", "relators", "petitioner",
    "petitioners", "intervenor", "intervenors", "and"))


def _is_status(text: str) -> bool:
    """Is this cell a status label and nothing else?"""
    toks = [t for t in re.split(r"[-–—/,\s]+", text.strip()) if t]
    return (bool(toks)
            and all(t.lower().rstrip(".") in _STATUS_WORDS for t in toks))


# The origin's opener. 'Appealed from the' on 29 records; one is a writ
# application, and that posture is the only one worth recording as history
# — see `_read_origin`.
_ORIGIN_OPEN = re.compile(r"^(?:Appealed|On\s+Application\s+for\s+Writs?"
                          r"|On\s+(?:Remand|Appeal)|Appeal)\b.*\bfrom\s+the$",
                          re.I)
_TRIAL_NO = re.compile(r"^Trial\s+Court\s+Nos?\.?\s*(.+?)\.?\s*$", re.I)
# The judge below, three ways the corpus prints them: 'Honorable X, Judge',
# 'Honorable X, Judge, Pro Tempore', and — the two workers' compensation
# records — a bare name over its own bench line.
_TRIAL_JUDGE = re.compile(r"^(?:Honorable|Hon\.)\s+(.+?)\s*$", re.I)
_BENCH_LINE = re.compile(r"^(?:Workers.{0,3}\s*Compensation\s+Judge"
                         r"|Judge(?:\s*,\s*Pro\s+Tempore)?)\b.*$", re.I)
_PANEL = re.compile(r"^Before\s+(.+?)\s*$", re.I)
# HOW THE BENCH VOTED, announced under the panel row: 'STONE, J., dissents
# with written reasons.' Five of the 30 records print one or more, and they
# are the bench and not a writing — the writing they announce signs itself
# further down, in bold. See `_read_votes`.
_VOTE = re.compile(
    r"^[A-Z][A-Za-z'’\-]+,\s*(?:C\.\s?J\.|P\.\s?J\.|J\.),?\s+"
    r"(?:concurs|dissents|concurring|dissenting|joins|would)\b", re.I)
# The appearances name themselves, and this court labels every one of them
# in the right column ('Counsel for Appellant'). The left column is the
# firm; nothing here needs to recognise a roster, because the section the
# court fenced IS the roster.
_TRIBUNAL = re.compile(r"(?:Court|Office|Board|Commission|Tribunal)\b", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _ink(line) -> tuple[float, float]:
    """Where the row's INK runs, not where its box does.

    pdfio's column-gap split leaves a cell's padding on it — the second
    piece of one appearances row is '               Bennet and Bennett',
    whose box starts at 319.7 and whose first glyph is 58pt further right
    (william_frederick_bennett_v._state_farm_insurance). Measured from the
    box that cell is on the LEFT of the axis, which is the one thing it
    certainly is not."""
    xs = [(c["x0"], c["x1"]) for c in (line.chars or [])
          if (c.get("text") or "").strip()]
    if not xs:
        return (line.x0, line.x1)
    return (min(a for a, _ in xs), max(b for _, b in xs))


def _centre(pieces: list) -> float:
    spans = [_ink(p) for p in pieces]
    return (min(a for a, _ in spans) + max(b for _, b in spans)) / 2


@decider("headmatter.read", court="lactapp")
def read_headmatter_lactapp(model, geom, **_):
    """Read the Second Circuit's fenced block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 108.0
    body_size = geom.body_size if geom and geom.body_size else 14.0
    finder = FurnitureFinder(model, body_x0, body_size)

    stream = _rows(model, finder)
    sections, axis, star_ids = _fence(stream)
    if sections is None:
        return NOTHING
    # THE DISPATCH IS THE MASTHEAD INSIDE THE FENCE. Four typed dividers
    # alone would be a weak claim on a paper this reader has never seen, so
    # the court must also name itself in the section above the first one.
    head = [t for _pg, _p, t in sections[0]]
    if not any(_norm(t).lower() in _COURT_ROWS for t in head):
        return NOTHING

    ctx = _Ctx(model, axis, body_x0)
    _read_top(ctx, sections[0])
    ctx.divider(star_ids[0])
    parties = _read_caption(ctx, sections[1])
    ctx.divider(star_ids[1])
    _read_origin(ctx, sections[2])
    ctx.divider(star_ids[2])
    _read_appearances(ctx, sections[3])
    ctx.divider(star_ids[3])
    # THE PANEL CLOSES THE BLOCK, and it is the FIRST row below the last
    # divider — everything after it is the writing. Section 5 is 26 to 70
    # rows long for that reason, and only its head belongs here.
    if sections[4]:
        pg, pieces, text = sections[4][0]
        panel = _PANEL.match(text)
        if panel:
            ctx.row(pieces, "panel")
            ctx.crit["judges"] = _norm(panel.group(1))
            ctx.crit["panel_line"] = _norm(panel.group(1))
            ctx.crit["panel"] = roster_names(_norm(panel.group(1)))
            _read_votes(ctx, sections[4][1:], pg)

    if not ctx.crit.get("docket_number"):
        return NOTHING          # no docket read: the block was not read
    if parties:
        ctx.crit["parties"] = parties
        ctx.crit["case_name"] = " v. ".join(parties) if len(parties) == 2 \
            else " ".join(parties)
    return ctx.result()


# --------------------------------------------------------------------------
# the fence
# --------------------------------------------------------------------------

def _rows(model, finder) -> list:
    """One entry per printed row of the first pages: (page, pieces, text)."""
    out: list = []
    for pm in model.pages[:_MAX_PAGES]:
        groups: dict = defaultdict(list)
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            groups[round(line.top, 1)].append(line)
        for top in sorted(groups):
            pieces = sorted(groups[top], key=lambda l: l.x0)
            out.append((pm.number, pieces,
                        _norm(" ".join(p.plain for p in pieces))))
    return out


def _fence(stream: list):
    """Split the stream at the court's four typed dividers.

    Returns (sections, axis, star_ids) — five sections and the axis the
    dividers measure — or (None, None, None) where the paper is not fenced
    the way this court fences it."""
    sections: list[list] = [[]]
    axes: list[float] = []
    star_ids: list[tuple] = []
    for pg, pieces, text in stream:
        if _STAR.match(text) and len(pieces) == 1:
            if len(sections) > _STARS_WANTED:
                break               # a '***' inside the writing, not a fence
            axes.append(_centre(pieces))
            star_ids.append(tuple(p.id for p in pieces))
            sections.append([])
            continue
        sections[-1].append((pg, pieces, text))
    if len(sections) != _STARS_WANTED + 1 or not all(sections[:4]):
        return None, None, None
    return sections, sorted(axes)[len(axes) // 2], star_ids


# --------------------------------------------------------------------------
# the five sections
# --------------------------------------------------------------------------

def _read_top(ctx, rows: list) -> None:
    """The date, the rehearing notice, the docket, and the court."""
    for _pg, pieces, text in rows:
        rendered = _RENDERED.match(text)
        if rendered:
            ctx.crit.setdefault("decision_date", _norm(rendered.group(1)))
            ctx.row(pieces, "date")
            continue
        if _NOTICE.match(text):
            ctx.row(pieces, "case-info")
            continue
        if _CONSOLIDATED.match(text):
            # 'No. 56,943-CA' over 'No. 56,944-CA' over '(Consolidated
            # Cases)' — the court says why there are two numbers.
            ctx.row(pieces, "case-info")
            continue
        docket = _DOCKET.match(text)
        if docket:
            value = _norm(docket.group(1))
            if ctx.crit.get("docket_number"):
                ctx.crit.setdefault("other_dockets", []).append(value)
            else:
                ctx.crit["docket_number"] = value
            ctx.row(pieces, "docket")
            continue
        if _norm(text).lower() in _COURT_ROWS:
            ctx.court.append(_norm(text))
            ctx.row(pieces, "court")
            continue
        ctx.row(pieces, "case-info")
    if ctx.court:
        # AS PRINTED. The court sets its name in three rows of capitals and
        # `court` is 'the deciding court, as printed' — title-cased it came
        # out 'Court Of Appeal', which is a form no one wrote.
        ctx.crit["court"] = ", ".join(ctx.court)


def _read_caption(ctx, rows: list) -> list[str]:
    """The caption's two columns, and the party names in the left one.

    THE STATUS LABEL IS APPARATUS, NOT A NAME. This court prints it beside
    the party it belongs to — 'Plaintiff-Appellant', 'Defendants-Appellees',
    'Defendants -Applicants' (the stray space is the page's) — and the whole
    vocabulary over the 30 records is six words and their plurals, which is
    why `_is_status` can read a closed list rather than a guess.

    THE PIVOT IS WHAT THE NAMES ARE SPLIT AT, and it is read wherever it is
    printed rather than only on the axis: bonnie_bennett_v._pathway
    _management is a CONSOLIDATED paper and sets TWO WHOLE CAPTIONS side by
    side, each with its own docket row ('No. 56,943-CA' | 'No. 56,944-CA'),
    its own party names and its own 'versus'. Read as one caption whose
    right column is postures, its 'versus' was a left-hand CELL and never a
    full-width row, so nothing split the names and `parties` came back as a
    single 74-word string with the docket and both postures inside it."""
    left: list = []
    right: list = []
    ids: list[int] = []
    names: list[list[str]] = [[]]

    def _name(text: str) -> None:
        flat = _norm(text)
        if not flat or _is_status(flat) or _DOCKET.match(flat):
            return          # a posture, or the consolidated docket
        names[-1].append(flat)

    for _pg, pieces, text in rows:
        ids.extend(p.id for p in pieces)
        if ctx.is_full_width(pieces):
            # THE PIVOT GOES IN THE LEFT COLUMN, where the render draws the
            # caption's own stack — a `CaptionBlock` has two sides and the
            # pivot belongs to neither, and the left is where the parties
            # it separates stand.
            left.append(ctx.cell(pieces[0], "caption", "C"))
            right.append(ctx.blank(pieces[0]))
            if _PIVOT.match(text):
                names.append([])
            else:
                # A one-party caption sets its whole style on the axis
                # ('IN RE: MEDICAL REVIEW PANEL' / 'PROCEEDINGS OF STEPHEN
                # BARBER'; 'STATE OF LOUISIANA' / 'IN THE INTEREST OF' /
                # 'N.P.') — three records, and there is no pivot to split.
                _name(text)
            continue
        l_cells = [p for p in pieces if not ctx.is_right(p)]
        r_cells = [p for p in pieces if ctx.is_right(p)]
        left.append(ctx.cell(l_cells[0], "caption", "L") if l_cells
                    else ctx.blank(pieces[0]))
        right.append(ctx.cell(r_cells[0], "caption", "R") if r_cells
                     else ctx.blank(pieces[0]))
        if l_cells:
            l_text = _norm(" ".join(p.plain for p in l_cells))
            if _PIVOT.match(l_text):
                names.append([])
            else:
                _name(l_text)
    ctx.caption(rows[0][0], left, right, ids)
    return [_norm(" ".join(side)) for side in names if any(side)]


def _read_origin(ctx, rows: list) -> None:
    """Where the case came from: the posture, the tribunal, its number, and
    the judge who tried it."""
    tribunal: list[str] = []
    judge: list[str] = []
    for _pg, pieces, text in rows:
        opener = _ORIGIN_OPEN.match(text)
        if opener:
            # THE ORDINARY APPEAL IS NOT A HISTORY. 29 of the 30 open
            # 'Appealed from the', which says only that this is an appeal —
            # `history` recorded on every record would say nothing on any
            # of them. The one record that opens 'On Application for Writs
            # from the' arrived a different way, and that is worth saying.
            if not text.lower().startswith("appealed"):
                ctx.crit.setdefault("history", _norm(text))
            ctx.row(pieces, "lower-court")
            continue
        trial = _TRIAL_NO.match(text)
        if trial:
            ctx.crit.setdefault("lower_court_docket", []).extend(
                _split_trial_nos(trial.group(1)))
            ctx.row(pieces, "lower-court")
            continue
        honorific = _TRIAL_JUDGE.match(text)
        if honorific:
            judge.append(_norm(honorific.group(1)))
            ctx.row(pieces, "lower-court")
            continue
        if judge and _BENCH_LINE.match(text):
            judge.append(_norm(text))       # 'Judge, Pro Tempore' runover
            ctx.row(pieces, "lower-court")
            continue
        if _BENCH_LINE.match(text) and tribunal:
            # THE WORKERS' COMPENSATION JUDGE HAS NO HONORIFIC. Two records
            # set a bare name over its own bench line ('Christopher T. Lee'
            # / 'Workers' Compensation Judge (Ad Hoc)'), so the bench line
            # claims the row above it — which by then has been read as part
            # of the tribunal, and is taken back out of it.
            judge = ([tribunal.pop(), _norm(text)] if tribunal
                     else [_norm(text)])
            ctx.row(pieces, "lower-court")
            continue
        tribunal.append(_norm(text))
        ctx.row(pieces, "lower-court")
    if tribunal:
        ctx.crit.setdefault("lower_court", " ".join(tribunal))
    if judge:
        ctx.crit.setdefault("lower_court_judge", ", ".join(judge))


def _read_votes(ctx, rows: list, page: int) -> None:
    """The vote lines under the panel row — how the bench voted, which is not
    the same thing as a writing.

    THE WEIGHT IS THE MEASUREMENT, NOT THE WORDING.
    state_of_louisiana_v._semaj_williams prints the SAME SENTENCE twice:
    'HUNTER, J., dissenting with written reasons.' announced here in roman
    at the foot of page 1, and again in BOLD on page 12, where the dissent
    it announces actually opens. So no vocabulary can tell them apart, and
    this claims only the roman one.

    Unclaimed, these rows stood above the first byline in the document and
    each opened a writing of its own: del_pumphrey_and_linda_pumphrey came
    back with a leading authorless 'order' holding three of them (one of
    which was the concurrence's own announcement, so the concurrence went
    missing), and doneyl_taylor_v._eric_clark with one.

    The run ends at the page the panel row stands on: the writing opens on
    the next sheet, and nothing this court announces here carries over."""
    voted = False
    for pg, pieces, text in rows:
        if pg != page or all(bool(p.all_bold) for p in pieces):
            return
        if _VOTE.match(text):
            ctx.row(pieces, "panel")
            voted = True
            continue
        # A runover row carries no landmark of its own ('additional
        # reasons.' under 'HUNTER, J., dissents … and joins J. STONE,
        # with') and is set in from the rail.
        if voted and pieces[0].x0 > ctx.rail + 2.0:
            ctx.row(pieces, "panel")
            continue
        return


def _split_trial_nos(value: str) -> list[str]:
    """'626,044 and 637,280' is two numbers; '2019-CV-04012' is one."""
    return [v for v in (x.strip(" .,") for x in re.split(r"\s+and\s+|;\s*",
                                                         value)) if v]


def _read_appearances(ctx, rows: list) -> None:
    """The appearances, in the same two columns as the caption: the firm and
    its attorneys on the left, who they appear for on the right."""
    left: list = []
    right: list = []
    ids: list[int] = []
    said: list[str] = []
    for _pg, pieces, text in rows:
        ids.extend(p.id for p in pieces)
        said.append(text)
        if ctx.is_full_width(pieces):
            left.append(ctx.cell(pieces[0], "counsel", "C"))
            right.append(ctx.blank(pieces[0]))
            continue
        l_cells = [p for p in pieces if not ctx.is_right(p)]
        r_cells = [p for p in pieces if ctx.is_right(p)]
        left.append(ctx.cell(l_cells[0], "counsel", "L") if l_cells
                    else ctx.blank(pieces[0]))
        right.append(ctx.cell(r_cells[0], "counsel", "R") if r_cells
                     else ctx.blank(pieces[0]))
    ctx.caption(rows[0][0], left, right, ids, counsel=True)
    # THE ROSTER IS A CRITERION TOO. The rows are placed in their columns
    # for the eye; `attorneys` is the queryable form, and it was empty on
    # every court that read its appearances as tinted rows alone.
    ctx.crit.setdefault("attorneys", " ".join(said))


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from."""

    def __init__(self, model, axis: float, rail: float):
        self.axis = axis
        self.rail = rail
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.dropped: list = []
        self.court: list[str] = []

    # ---- the columns ------------------------------------------------------

    def is_full_width(self, pieces: list) -> bool:
        """One printed piece, centred on the block's axis — the court's own
        full-width row, never a cell. See the docstring."""
        return (len(pieces) == 1
                and abs(_centre(pieces) - self.axis) <= _AXIS_TOL)

    def is_right(self, piece) -> bool:
        a, b = _ink(piece)
        return (a + b) / 2 > self.axis

    # ---- what it places --------------------------------------------------

    def _line(self, line, role: str, align: str, trim: bool) -> m.HmLine:
        text = line_markup(line)
        return m.HmLine(
            text=text.strip() if trim else text,
            prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role)

    def row(self, pieces: list, role: str) -> None:
        """A full-width row, placed as printed."""
        first = pieces[0]
        text = ""
        for piece in pieces:
            part = line_markup(piece)
            text = (text.rstrip() + " " + part.lstrip()) if text.strip() \
                else part
        align = "C" if self.is_full_width(pieces) else "L"
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in pieces)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in pieces), role=role))
        self.consumed.update(p.id for p in pieces)

    def cell(self, line, role: str, align: str) -> m.HmLine:
        """A column cell — built, not emitted: it goes in a CaptionBlock.
        The cell's own padding is not content; the column places it."""
        self.consumed.add(line.id)
        return self._line(line, role, align, trim=True)

    def blank(self, line) -> m.HmLine:
        """The other column's place on a row only one column uses. Both
        stacks keep their rows so the pairing the page prints survives."""
        return m.HmLine(text="", prov=m.Prov(line.page, ()),
                        align=m.Align.LEFT, x0=0.0, size=0.0)

    def divider(self, ids: tuple) -> None:
        """The court's typed '* * * * *'. A `Divider` draws nothing: the row
        is a component boundary, and reproducing the stars would print the
        court's own structural mark as if it were content."""
        self.items.append(m.Divider(prov=m.Prov(
            next(iter(self.pages)), ids)))
        self.consumed.update(ids)

    def caption(self, page: int, left: list, right: list,
                ids: list, counsel: bool = False) -> None:
        # THE GUTTER IS WHITE SPACE, and `rail=None` is a measurement here:
        # this court draws no rule and types no rail glyph on any page of
        # any record (`v_rules` = 0 corpus-wide). The divider it does type
        # is what says where the gutter runs, and it is recorded in `fp` so
        # the label and the reproduction cannot disagree.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=len(left),
            style_id="whitespace-gutter",
            fp={"rail": None, "axis": round(self.axis, 1),
                "of": "counsel" if counsel else "caption"},
            prov=m.Prov(page, tuple(sorted(ids)))))

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# writing.covers — where a SEPARATE writing opens
# --------------------------------------------------------------------------
# THE COURT SETS ITS SEPARATE WRITINGS AT THE HEAD OF A FRESH PAGE, IN BOLD.
# That is the indicator, and it is the court's and not core's: over the 418
# interior pages of the 30 judgments, exactly five rows are bold, open their
# page at the body rail, and carry a KIND clause —
#
#     STEPHENS, J., concurring,
#     STONE, J., dissenting with written reasons.
#     STONE, J., dissenting.
#     HUNTER, J., dissenting.
#     HUNTER, J., dissenting with written reasons.
#
# and those five are exactly the five separate writings in the corpus. The
# other 24 bold page-openers at the rail are LEAD bylines and carry no kind
# ('ROBINSON, J.', 'PITMAN, C. J.'); everything else bold at the head of a
# page is a section heading the court centres ('DISCUSSION' at x0 281,
# 'ANALYSIS' at 289) or prose.
#
# WHY THE COURT HAS TO ANSWER THIS. core finds a writing by parsing its
# byline, and this court's terminator is not always a full stop:
# del_pumphrey_and_linda_pumphrey signs 'STEPHENS, J., concurring,' with a
# COMMA, which no byline grammar admits — an unterminated kind clause is a
# running head (ca11 sets 'BRANCH, J., Dissenting' atop every page of a
# writing), and relaxing that rule in core would be Louisiana's punctuation
# deciding a corpus-wide question. So the fact stays here: 13 pages of Judge
# Stephens' concurrence were welded onto the end of Judge Robinson's
# majority and credited to him (the user, 2026-08-20: 'STEPHENS J
# CONCURRING is bold and the start of a page … that information about new
# opinions is in the lactapp code').
#
# Nothing is DROPPED. There is no cover here — the byline is the writing's
# own first row and the prose runs on beneath it.
_SEPARATE = re.compile(
    r"^[A-Z][A-Za-z'’\-]+,\s*(?:C\.\s?J\.|P\.\s?J\.|J\.?),\s*"
    r"(?P<kind>(?:specially\s+|respectfully\s+|partially\s+)?"
    r"(?:concurring|dissenting)\b.*?)\s*[.,:]?$")
_RAIL_TOL = 6.0
_FOLIO_MAX = 4          # '2', '-2-' — a page number, never a byline


@decider("writing.covers", court="lactapp")
def writing_covers_lactapp(model=None, geom=None, **_):
    """The lines a separate writing opens on, and the kind each states."""
    if model is None or len(model.pages) < 2:
        return NOTHING
    rail = geom.body_x0 if geom and geom.body_x0 else 108.0
    starts: dict[int, str] = {}
    for pm in model.pages[1:]:
        rows = sorted((l for l in pm.lines if l.plain.strip()),
                      key=lambda l: (l.top, l.x0))
        # A FOLIO MAY HEAD THE PAGE and the byline stand under it.
        head = next((l for l in rows
                     if len(_norm(l.plain).strip(" -")) > _FOLIO_MAX
                     or not _norm(l.plain).strip(" -").isdigit()), None)
        if head is None or not head.all_bold or head.x0 > rail + _RAIL_TOL:
            continue
        said = _SEPARATE.match(_norm(head.plain))
        if said:
            starts[head.id] = _norm(said.group("kind"))
    return {"starts": starts, "drop": []} if starts else NOTHING
