"""Supreme Court of New Jersey ('nj').

THE CONTRACT — one paper, printed 46 times out of 50: the FENCED LADDER.

New Jersey publishes a merits opinion in two halves. The Clerk's SYLLABUS
comes first — its own pages, headed 'SYLLABUS', ending in the joinder
('CHIEF JUSTICE RABNER and JUSTICES … join in JUSTICE WAINER APTER's
opinion.  JUSTICE NORIEGA filed a dissent.') — and only THEN does the
opinion's own cover page open, with the court naming itself and the
headmatter set as a ladder of bands, each closed by a DRAWN RULE running
the full measure (467.5pt at the body rail, x0=72 on a 612pt page):

    SUPREME COURT OF NEW JERSEY            the banner, centred…
    A-12 September Term 2024               …the term line…
    089603                                 …and the docket
    ───────────────────────────────────    a FENCE, full measure
    Fred Krug,                             the caption: a party…
         Appellant-Appellant,              …its status…
    v.                                     …the pivot…
    New Jersey State Parole Board,
         Respondent-Respondent.
    ───────────────────────────────────
    On certification to the Superior       the origin, always
    Court, Appellate Division.             opening on 'On …'
    ───────────────────────────────────
    Argued              Decided            THE DATE GRID — two
    February 3, 2025    August 11, 2025    COLUMNS, label over value
    ───────────────────────────────────
    Kevin S. Finckenauer, Assistant …      the appearances, at their
    argued the cause for appellant …       own rail (x0=144)
    ───────────────────────────────────
    JUSTICE WAINER APTER delivered the opinion of the Court.
    ───────────────────────────────────    …and the writing starts

THE FENCE IS THE BAND MARK; THE BAND'S FIRST ROW NAMES THE BAND. Band
ORDINALS decide nothing: a consolidated release fences each of its four
captions separately (russell_forde_hornor sets four, over three pages;
darryl_nieves two), so the ladder runs 6, 7 or 8 fences. What a band IS is
read from its opening row — the banner text, an origin opening on 'On',
a two-column date grid, the counsel rail, a byline — never from its index.

EVERY BAND DECLARES ITS OWN ALIGNMENT, because measuring one across the
headmatter gets it wrong. The banner, the caption and the origin are centred
on the page axis (measured: every row's midpoint within 0.5pt of 305.9 on a
612pt page). The counsel band and the date grid are flush LEFT to their own
rails — the appearances at x0=144.0 on all 46 records, each date column at
its own label edge. A justified counsel line spans 144-485 and reads as
CENTRED to a page-wide test, which is the ca5 defect: 12 of the 23 rows in
one appearance block rendered centred and the block came apart.

THE DATE GRID IS THE ROW THIS COURT LOSES. It is a 2x2 label/value grid,
not four rows: 'Argued' over 'February 3, 2025' in the LEFT column,
'Decided' over 'August 11, 2025' in the RIGHT one. Read row-wise it prints
two labels with no values, which is the `split-label` defect on 31 of the
50 records. Read COLUMN-WISE — by the x midpoint against the page axis,
never by the wording, because the same grid is labelled 'Decided by Order'
/ 'Opinion Filed' on the emergent applications — each column is one cell:
label, value, one row, one criterion.

WHERE THE SYLLABUS ENDS. It ends where this ladder begins, and not one row
earlier: the joinder and the dissent summary at the foot of the syllabus
are the Clerk's, not the Court's, and they parse as bylines ('JUSTICE
NORIEGA, dissenting, expresses the view that…'). Core already routes a
labelled syllabus page to the syllabus section; claiming the cover is what
stops assembly from opening a phantom writing inside it, because a claimed
headmatter anchors the first writing at the first segment BELOW the front
matter. The reader never touches a syllabus page and never claims one row
of one.

THE SECOND CONTRACT — the RAILED ORDER (3 records). A motion order carries
no syllabus and no fence. It sets its masthead in the page's RIGHT HALF and
its caption in two columns divided by a STACKED ':' — the same shape ca6
draws with box-drawing glyphs and with a stacked ')', and it is read the
same way: by the rail, never by the wording.

    FILED, Clerk of the Supreme Court, 23 Oct 2025, 090357   (a stamp)
                          SUPREME COURT OF NEW JERSEY    the masthead,
                          M-1149 September Term 2024     off the axis
                                    090357
    In the Matter of            :                        ABOVE the rail
    Wilfredo Benitez,           :                        is the masthead;
                                :     O R D E R          LEFT of it the
    A Judge of the Municipal Court :                     parties, RIGHT
                                                         of it the paper's
    Pending before the Court is an application by …      name; BELOW it
                                                         the writing.

The rail is three ':' glyphs stacked at x=280.9 to the tenth of a point,
and the last of them is fused into its own caption row — shed from the cell
it fell into, exactly as ca6 sheds its corners.

THE THIRD CONTRACT — the MOTION FORM (1 record, `state_v._paul_j._caneiro`).
Appellate Division stationery, filed into this corpus. It names itself and
then TYPES its rules: a run of hyphens centred on the page axis under the
paper's name, and a second one under the writing's heading. The two typed
rules fence the form, and inside it the page prints a LABEL GRID in two
columns:

    ORDER ON MOTION                        the paper names itself…
    ---------------                        …over a TYPED rule on the axis
                    SUPERIOR COURT OF NEW JERSEY     the right column is
                    APPELLATE DIVISION               the court and the
                    DOCKET NO.: AM-000582-24T5       numbers and the bench
    STATE OF NEW JERSEY   MOTION NO.: M-006354-24
    V                     BEFORE:        PART L      the left column is
    PAUL J. CANEIRO       JUDGES:        LISA ROSE   the caption
                                         KAY WALCOTT-HENDERSON
    MOTION FILED: 07/14/2025   BY: STATE OF NEW JERSEY
    ANSWER        07/24/2025   BY: PAUL J. CANERIO   A LABEL MAY WRAP:
    FILED:                                           'ANSWER' / 'FILED:'
    SUBMITTED TO COURT: July 31, 2025                is ONE label

    ORDER                                  the writing's own heading,
    -----                                  under the second typed rule
    THIS MATTER HAVING BEEN DULY PRESENTED TO THE COURT …

A LABEL WITH NO VALUE IS NEVER A CELL. 'FILED:' stands alone on its row
because the label 'ANSWER FILED:' wrapped; read as a row it prints a label
and nothing else, which is the same defect the date grid produces on the
ladder. It is folded into the cell above it.

A record that matches none of the three gets NOTHING.
"""

from __future__ import annotations

import re

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import register

_BYLINE = BylineGrammar(style="reversed",
                        rev_titles=("JUSTICE", "CHIEF JUSTICE"))

NJ = register(CourtProfile(
    "nj", "Supreme Court of New Jersey",
    byline=_BYLINE,
    # The Clerk's syllabus is a published section of the release, not the
    # opinion's front matter and not the body.
    front_matter=("syllabus",),
))

STYLE_LADDER = "fenced ladder"
STYLE_RAILED = "railed order"
STYLE_FORM = "motion form"

# ---- nj's declared facts (measured over all 50 records) ------------------
# THE FENCE. Every band mark in the corpus is a drawn rect 467.5-468.2pt
# wide starting at the body rail (x0 = 71.3-72.0) on a 612pt page. The
# court's OTHER rules are narrower by a wide margin: the footnote separator
# is 144pt at the same rail, and a citation underline runs 10-150pt
# anywhere. Width alone separates them; no ratio, no page-relative fudge.
_FENCE_MIN = 400.0
_FENCE_RAIL = 8.0
# …and the court sometimes TYPES the same fence instead of drawing it.
_TYPED_FENCE = re.compile(r"^_{20,}$")
# THE COUNSEL RAIL. The appearances are the only headmatter set at x0=144
# — the caption is centred (x0 ~ 205-300) and the body sits at 72/108.
_COUNSEL_RAIL = (136.0, 152.0)
# THE LADDER NEVER REACHES THE BODY RAIL. Measured over the 46 records,
# every claimed row starts at x0 >= 143.9 on a 72pt rail — the counsel rail
# is the leftmost thing the block sets. The body's own rows start at 72 and
# 108, so a band that opens within 60pt of the rail is the writing and ends
# the reader. Without this bound the walk would read body prose as a
# caption on any record whose byline it failed to parse.
_LADDER_RAIL_MIN = 60.0
# HOW FAR THE LADDER MAY RUN, counted from the cover. russell_forde_hornor
# consolidates four appeals and carries its captions from page 5 to page 7
# and its counsel to page 8 — four pages; nothing in the corpus needs five.
_MAX_PAGES = 5
# WHERE THE COVER MAY BE. The syllabus runs 2-4 pages ahead of it.
_MAX_COVER_PAGE = 8

# THE RAILED ORDER's divider: a ':' stacked at ONE x. Two rows prove a
# column; a lone ':' is punctuation.
_RAIL_GLYPH = ":"
_RAIL_MIN_ROWS = 2
_RAIL_X_TOL = 1.5

# THE MOTION FORM's rules are TYPED — a run of hyphens centred on the page
# axis. Four is the shortest the form sets ('-----' under 'ORDER').
_DASH_RULE = re.compile(r"^-{4,}$")
_AXIS = 24.0
# THE FORM'S COLUMN DIVIDER. Measured on the record: every left-column
# piece starts at 36.0-154.5 and every right-column piece at 283.9-383.4.
_FORM_GUTTER = 260.0
# The form's LABELS, as a closed vocabulary, with what each one states.
_FORM_LABELS = {
    "docket no": "docket", "motion no": "docket",
    "before": "panel", "judges": "panel",
    "motion filed": "date", "answer filed": "date",
    "submitted to court": "date", "by": "date",
}

_BANNER = "supreme court of new jersey"
# THE DOCKET, printed in two forms the court states in two rows. The
# CALENDAR line — 'A-12 September Term 2024' / 'A-48/49 September Term
# 2024' / 'S-73/74 September Term 2025' — names the appeal, and the way
# this court is cited folds it to 'A-12-24'; the bare six-digit row under
# it is the Clerk's own file number. Both are recorded; the calendar
# number is the docket, because the term is not one (a docket carrying the
# word 'Term' is exactly what `docket-suspect` is looking for).
_TERM = re.compile(r"^([A-Z]-[\d/]+)\s+\w+\s+Term\s+(\d{2})(\d{2})\.?$")
_CLERK_NO = re.compile(r"^\d{6}(?:\s+and\s+\d{6})*$")
# The origin band states where the case came from and, where the court
# below published, what it held. The citation is history, not the court.
_REPORTED = re.compile(r",?\s+whose opinion is\b", re.I)
# THE ORIGIN always opens on 'On': 'On certification to the Superior
# Court,' / 'On appeal from and certification to the' / 'On an Emergent
# Application' / 'On Emergent Applications'.
_ORIGIN = re.compile(r"^On\s+[a-z]", re.I)
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording.
_STATUS_WORDS = {
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "plaintiff", "plaintiffs",
    "defendant", "defendants", "intervenor", "intervenors", "movant",
    "movants", "amicus", "amici", "curiae", "applicant", "applicants",
    "claimant", "claimants", "complainant", "cross", "third", "party",
    "counterclaimant", "counterdefendant", "and", "the", "et", "al",
    "in", "interest", "real", "parties", "a", "an", "of",
}
_PIVOT = re.compile(r"^v\.?$", re.I)
# THE DATE GRID's labels, as the court prints them. A closed vocabulary of
# EVENT words, used only to file the value under the right criterion —
# the COLUMN, not the word, is what pairs a label with its value.
_HEARD = ("argued", "reargued", "submitted", "resubmitted")
_DECIDED = ("decided", "filed", "opinion filed", "decided by order")
_MONTHS = ("january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december")
_DATE = re.compile(r"^[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}\.?$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _join(rows: list) -> str:
    """Join caption rows the way the page reads them. A row ending in a
    hyphen is a WORD broken at its OWN hyphen ('PK-12 All-' / 'Purpose
    Regional School District') — the hyphen stays, the space does not. This
    court does not soft-hyphenate a caption; the only broken rows in the
    corpus break at a hyphen the name already carries."""
    out = ""
    for row in rows:
        row = _norm(row)
        if not row:
            continue
        out = row if not out else (out + row if out.endswith("-")
                                   else out + " " + row)
    return out


def _is_banner(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _BANNER


def _is_status(text: str) -> bool:
    bare = _norm(text).rstrip(".,;: ").lower()
    if not bare:
        return False
    words = [w for w in re.split(r"[\s/,-]+", bare) if w]
    return bool(words) and all(w.strip(".") in _STATUS_WORDS for w in words)


def _is_date(text: str) -> bool:
    t = _norm(text)
    return bool(_DATE.match(t)) and t.split()[0].lower().rstrip(".") in _MONTHS


def _fences(pm) -> list[float]:
    """The tops of the band marks this page draws, in page order."""
    return sorted(r.top for r in pm.h_rules
                  if r.width >= _FENCE_MIN and abs(r.x0 - 72.0) <= _FENCE_RAIL)


def _is_typed_fence(group, body_x0: float) -> bool:
    """A fence this court TYPED instead of drawing: a run of underscores at
    the body rail, to the full measure. The rulemaking consolidation divides
    its two captions that way and draws nothing between them — read as a
    row, 64 underscores become a caption row."""
    if len(group) != 1:
        return False
    line = group[0]
    return (bool(_TYPED_FENCE.match(_norm(line.plain)))
            and abs(line.x0 - body_x0) <= _FENCE_RAIL + 4.0
            and (line.x1 - line.x0) >= _FENCE_MIN)


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="nj")
def read_headmatter_nj(model, geom, **_):
    """Read New Jersey's fenced ladder, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    finder = FurnitureFinder(model, body_x0, body_size)
    pages = {pm.number: pm for pm in model.pages}

    def rows_of(pm) -> list[list]:
        """The page's visual ROWS, same-row pieces kept together — the date
        grid and a justified counsel line both arrive split at their gaps."""
        groups: dict = {}
        order: list = []
        for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
            if not line.plain.strip() or finder.kind(pm, line):
                continue
            key = line.row if line.row is not None else round(line.top)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(line)
        return [sorted(groups[k], key=lambda l: l.x0) for k in order]

    # THE DISPATCH: a page that names the court at its head. Which paper it
    # is then follows from what that page DRAWS — a full-measure fence
    # (the ladder) or a stacked ':' rail (the order). Nothing is matched
    # against a case's own wording.
    cover = None
    for pm in model.pages[:_MAX_COVER_PAGE]:
        rows = rows_of(pm)
        if rows and _is_banner(" ".join(l.plain for l in rows[0])):
            cover = pm
            break
    if cover is None:
        return _read_form(model, geom, model.pages[0], rows_of)
    if not _fences(cover):
        return _read_railed(model, geom, cover, rows_of)

    # THE STREAM: rows and fences from the cover page on, in page order.
    stream: list = []
    for pm in model.pages[cover.number - 1:cover.number - 1 + _MAX_PAGES]:
        for group in rows_of(pm):
            typed = _is_typed_fence(group, body_x0)
            stream.append((pm.number, group[0].top, 0 if typed else 1,
                           group))
        for top in _fences(pm):
            stream.append((pm.number, top, 0, None))
    stream.sort(key=lambda t: (t[0], t[1], t[2]))

    # THE BANDS: a fence closes one and opens the next. Each band remembers
    # the fence that OPENED it — a typed one is a line of the page and
    # carries its own provenance, a drawn one carries none.
    bands: list[list] = [[]]
    opened_by: dict = {}
    for _page, _top, kind, group in stream:
        if kind == 0:
            bands.append([])
            opened_by[len(bands) - 1] = group
        else:
            bands[-1].append(group)

    ctx = _Ctx(model, geom, pages, body_size)
    parser = BylineParser(_BYLINE)
    caption: list[str] = []
    dockets: list[str] = []
    origin: list[str] = []
    counsel: list[str] = []
    pending_fence = False
    saw_caption = saw_dates = False

    for index, band in enumerate(bands):
        pending_fence = pending_fence or index > 0
        if not band:
            continue
        head = _norm(" ".join(l.plain for l in band[0]))
        # THE BYLINE ENDS THE READER — always, and before the fence above
        # it is emitted, because that fence closes the block.
        if parser.parse(head) is not None:
            break
        if band[0][0].x0 < body_x0 + _LADDER_RAIL_MIN:
            break                 # the body rail: a writing, not a band
        if pending_fence:
            ctx.rule(band[0][0].page, typed=bool(opened_by.get(index)),
                     lines=opened_by.get(index))
            pending_fence = False

        if _is_banner(head):
            _banner_band(ctx, band, dockets, align="C")
            continue
        if _ORIGIN.match(head):
            for group in band:
                origin.append(_norm(" ".join(l.plain for l in group)))
                ctx.emit(group, "lower-court", align="C")
            continue
        if _is_grid(band):
            _date_band(ctx, band)
            saw_dates = True
            continue
        if _COUNSEL_RAIL[0] <= band[0][0].x0 <= _COUNSEL_RAIL[1]:
            for group in band:
                counsel.append(_norm(" ".join(l.plain for l in group)))
                ctx.emit(group, "counsel", align="L")
            continue
        # WHAT IS LEFT IS A CAPTION. A consolidated release fences one per
        # case, and each is read the same way.
        if not all(len(g) == 1 for g in band):
            return NOTHING       # a two-column band this contract has no
        for group in band:       # place for — leave the record to core
            caption.append(_norm(" ".join(l.plain for l in group)))
            ctx.emit(group, "caption", align="C")
        saw_caption = True

    if not (saw_caption and saw_dates and dockets):
        return NOTHING           # not the ladder this contract names

    ctx.crit["headmatter_style"] = STYLE_LADDER
    ctx.crit["court"] = "Supreme Court of New Jersey"
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    _name(ctx, caption)
    if origin:
        whole = _norm(" ".join(origin)).rstrip(". ")
        mm = _REPORTED.search(whole)
        court = whole[:mm.start()] if mm else whole
        ctx.crit["lower_court"] = court.rstrip(", ") + "."
        if mm:
            told = whole[mm.start():].lstrip(", ").rstrip(". ")
            ctx.crit["history"] = told + "."
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    return ctx.result()


# --------------------------------------------------------------------------
# the motion form
# --------------------------------------------------------------------------

def _typed_rule(group, width: float) -> bool:
    """A run of hyphens centred on the page axis — the form's own rule."""
    if len(group) != 1:
        return False
    text = _norm(group[0].plain)
    return (bool(_DASH_RULE.match(text))
            and abs((group[0].x0 + group[0].x1) / 2 - width / 2) <= _AXIS)


def _label(text: str):
    """('docket', 'AM-000582-24T5') for a labelled cell, else None. The
    label vocabulary is closed; the VALUE is never read by wording."""
    head, sep, tail = text.partition(":")
    if not sep:
        return None
    kind = _FORM_LABELS.get(_norm(head).lower().rstrip(". "))
    return None if kind is None else (kind, _norm(tail))


def _read_form(model, geom, page, rows_of):
    """The MOTION FORM: a label grid fenced by two TYPED rules on the axis."""
    body_size = geom.body_size if geom else 14.0
    pages = {pm.number: pm for pm in model.pages}
    width = page.width
    # A LABEL MAY WRAP. 'ANSWER' over 'FILED:' is ONE label with ONE value,
    # and the tail goes back where the label is, not after its value.
    rows: list[list] = []
    for group in rows_of(page):
        text = _norm(" ".join(l.plain for l in group))
        if (len(group) == 1 and rows and group[0].x0 < _FORM_GUTTER
                and text.endswith(":") and _label(text) is None):
            host = [pt for pt in rows[-1] if pt.x0 < _FORM_GUTTER]
            if host and ":" not in _norm(host[0].plain):
                rows[-1].insert(rows[-1].index(host[0]) + 1, group[0])
                continue
        rows.append(list(group))
    # THE DISPATCH: the paper names itself over a typed rule, and types a
    # second one lower down to open the writing. Two rules, or nothing.
    marks = [i for i, g in enumerate(rows) if _typed_rule(g, width)]
    if len(marks) < 2 or marks[0] != 1:
        return NOTHING
    # THE SECOND TYPED RULE UNDERLINES THE WRITING'S OWN HEADING, so the
    # axis-centred row above it is the writing's, not the form's — the
    # reader stops short of it without claiming it.
    end = marks[1]
    if end and _norm(" ".join(l.plain for l in rows[end - 1])) \
            and abs(sum((l.x0 + l.x1) / 2 for l in rows[end - 1])
                    / len(rows[end - 1]) - width / 2) <= _AXIS:
        end -= 1

    ctx = _Ctx(model, geom, pages, body_size)
    court: list[str] = []
    caption: list[str] = []
    panel_line: list[str] = []
    dockets: list[str] = []
    seen_label = {"L": False, "R": False}
    prev_cell: dict = {}

    for index, group in enumerate(rows[:end]):
        if index == 0:                       # the paper's own name
            ctx.crit["title"] = _norm(" ".join(l.plain for l in group))
            ctx.emit(group, "title")
            continue
        if index == marks[0]:
            ctx.rule(group[0].page, span="center", typed=True, lines=group)
            continue
        cells = {"L": [p for p in group if p.x0 < _FORM_GUTTER],
                 "R": [p for p in group if p.x0 >= _FORM_GUTTER]}
        for side in ("L", "R"):
            parts = cells[side]
            if not parts:
                continue
            text = _norm(" ".join(p.plain for p in parts))
            found = _label(text)
            # A LABEL WITH NO VALUE IS THE TAIL OF THE LABEL ABOVE IT.
            if (len(parts) == 1 and text.endswith(":")
                    and found is None and side in prev_cell):
                ctx.remerge(prev_cell[side], parts, text)
                continue
            if found is not None:
                seen_label[side] = True
                kind, value = found
                if kind == "docket" and value:
                    dockets.append(value)
                elif kind == "panel":
                    panel_line.append(text)
                elif kind == "date" and value and _is_date(value):
                    ctx.crit["submitted"] = value
                role = kind
            elif seen_label[side]:
                role = "panel" if side == "R" else "date"
                if side == "R":
                    panel_line.append(text)
            else:
                role = "court" if side == "R" else "caption"
                (court if side == "R" else caption).append(text)
            ctx.emit(parts, role, ordered=True, align="L")
            prev_cell[side] = ctx.items[-1]

    if not (caption and dockets):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_FORM
    if court:
        ctx.crit["court"] = _norm(", ".join(court))
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = caption
    _name(ctx, caption)
    if panel_line:
        line = _norm(" ".join(panel_line))
        ctx.crit["panel_line"] = line
        ctx.crit["panel"] = _form_panel(panel_line)
    return ctx.result()


def _form_panel(rows: list[str]) -> list[str]:
    """The bench, from the form's 'JUDGES:' cell and the rows under it. The
    LABEL is the closed vocabulary; a name is what stands after it."""
    out: list[str] = []
    taking = False
    for row in rows:
        head, sep, tail = row.partition(":")
        if sep:
            taking = _norm(head).lower().rstrip(". ") == "judges"
            row = tail
        if taking and _norm(row):
            out.append(_norm(row))
    return out


# --------------------------------------------------------------------------
# the railed order
# --------------------------------------------------------------------------

def _piece(line, keep: list):
    """``line`` restricted to ``keep`` — one side of the rail."""
    from dataclasses import replace as _replace
    inked = [c for c in keep if (c.get("text") or "").strip()]
    if not inked:
        return None
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in inked),
                    x1=max(c.get("x1", c["x0"]) for c in inked))


def _read_railed(model, geom, cover, rows_of):
    """The RAILED ORDER: masthead ABOVE the rail, parties LEFT of it, the
    paper's own name RIGHT of it, and the Court's prose BELOW it."""
    body_size = geom.body_size if geom else 14.0
    pages = {pm.number: pm for pm in model.pages}
    rows = rows_of(cover)

    # THE RAIL. Every ':' glyph on the page, bucketed by x; the bucket the
    # court stacked is the divider. A lone ':' is punctuation.
    buckets: dict = {}
    for group in rows:
        for part in group:
            for c in part.chars:
                if (c.get("text") or "").strip() == _RAIL_GLYPH:
                    buckets.setdefault(round(c["x0"] / _RAIL_X_TOL),
                                       []).append((c["x0"], part))
    stack = max(buckets.values(), key=len) if buckets else []
    if len({id(p) for _, p in stack}) < _RAIL_MIN_ROWS:
        return NOTHING
    mid = sum(x for x, _ in stack) / len(stack)
    rail_ids = {id(p) for _, p in stack}
    band_top = min(p.top for _, p in stack) - 2.0
    band_bot = max(p.bottom for _, p in stack) + 2.0

    ctx = _Ctx(model, geom, pages, body_size)
    dockets: list[str] = []
    band_ids: list[int] = []
    left: list = []
    right: list = []
    cap_rows: list[str] = []
    title: str | None = None
    for group in rows:
        top = group[0].top
        if top < band_top:                       # ABOVE the rail: masthead
            _banner_band(ctx, [group], dockets)
            continue
        if top > band_bot:                       # BELOW it: the writing
            break
        # INSIDE the band: the rail decides the column, never the wording.
        cell_l: list = []
        cell_r: list = []
        # THE RAIL'S OWN GLYPHS ARE PLACED BY THE BLOCK, not by a cell —
        # the CaptionBlock carries them as its `rail`. A row that holds
        # nothing else is still consumed, or the ':' comes back as the
        # opening of the writing.
        band_ids.extend(l.id for l in group)
        ctx.consumed.update(l.id for l in group)
        for part in group:
            keep_l = [c for c in part.chars
                      if c["x0"] < mid - _RAIL_X_TOL
                      or not (c.get("text") or "").strip()]
            keep_r = [c for c in part.chars if c["x0"] > mid + _RAIL_X_TOL]
            if id(part) in rail_ids:
                keep_l = [c for c in keep_l
                          if (c.get("text") or "").strip() != _RAIL_GLYPH]
                keep_r = [c for c in keep_r
                          if (c.get("text") or "").strip() != _RAIL_GLYPH]
            for keep, cell in ((keep_l, cell_l), (keep_r, cell_r)):
                piece = _piece(part, keep)
                if piece is not None:
                    cell.append(piece)
        left.append(ctx.cell(cell_l, "caption", group))
        right.append(ctx.cell(cell_r, "title", group))
        if cell_l:
            cap_rows.append(_norm(" ".join(p.plain for p in cell_l)))
        if cell_r and title is None:
            title = _norm(" ".join(p.plain for p in cell_r))
    while left and right and not (left[-1].text or right[-1].text):
        left.pop()
        right.pop()
    if not any(r.text for r in left):
        return NOTHING
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=_RAIL_GLYPH, rail_rows=len(left),
        fp={"rail": _RAIL_GLYPH, "rail_band": (band_top, band_bot),
            "mid_x": mid},
        prov=m.Prov(cover.number, tuple(sorted(band_ids)))))
    if not dockets:
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_RAILED
    ctx.crit["court"] = "Supreme Court of New Jersey"
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = cap_rows
    _name(ctx, cap_rows)
    if title:
        # 'O R D E R' — the court letter-spaces the paper's own name.
        ctx.crit["title"] = re.sub(r"(?<=\b\w) (?=\w\b)", "", title)
    return ctx.result()


# --------------------------------------------------------------------------
# the bands
# --------------------------------------------------------------------------

def _banner_band(ctx, band, dockets: list[str], align=None) -> None:
    """The masthead band: the court, the term line, the Clerk's number.
    A consolidated release prints two term lines and two numbers. The LADDER
    centres this band on the page axis; the ORDER sets it in the page's
    right half, where the measured alignment is the fact."""
    for group in band:
        text = _norm(" ".join(l.plain for l in group))
        if _TERM.match(text):
            mm = _TERM.match(text)
            dockets.append(f"{mm.group(1)}-{mm.group(3)}")
            ctx.emit(group, "docket", align=align)
        elif _CLERK_NO.match(text):
            dockets.append(text.rstrip("."))
            ctx.emit(group, "docket", align=align)
        else:
            ctx.emit(group, "court", align=align)


def _is_grid(band) -> bool:
    """A LABEL/VALUE GRID: a band whose rows arrive SPLIT at a column gap
    and whose pieces include a bare date. The geometry decides which band
    this is; the label wording only files the value afterwards, and the
    court prints three different label pairs over the same grid."""
    if not band or not any(len(g) >= 2 for g in band):
        return False
    return any(_is_date(_norm(" ".join(l.plain for l in [p])))
               for g in band for p in g)


def _date_band(ctx, band) -> None:
    """The date grid, read COLUMN-WISE. Each column is one cell — its label
    over its value — and renders as one row, so no label is ever printed
    without the date it introduces."""
    axis = ctx.pages[band[0][0].page].width / 2
    cols: list[list] = [[], []]
    for group in band:
        for part in group:
            cols[0 if (part.x0 + part.x1) / 2 < axis else 1].append(part)
    for col in cols:
        if not col:
            continue
        col.sort(key=lambda l: (l.top, l.x0))
        label = _norm(" ".join(l.plain for l in col
                               if not _is_date(l.plain)))
        value = _norm(" ".join(l.plain for l in col if _is_date(l.plain)))
        ctx.emit(col, "date", joiner="  ", align="L")
        low = label.lower().rstrip(":. ")
        if not value:
            continue
        if any(low.startswith(w) for w in _HEARD):
            ctx.crit["submitted"] = value.rstrip(".")
        elif any(w in low for w in _DECIDED):
            ctx.crit["decision_date"] = value.rstrip(".")


def _name(ctx, rows: list[str]) -> None:
    """The case's name, built from the party names either side of the FIRST
    pivot — never by joining the caption wholesale, and never past the
    second caption of a consolidated release."""
    left: list[str] = []
    right: list[str] = []
    side = left
    seen_pivot = False
    for row in rows:
        if _PIVOT.match(row):
            if seen_pivot:
                break
            side = right
            seen_pivot = True
            continue
        if _is_status(row):
            if seen_pivot and right:
                break            # the second party's status closes the name
            continue
        side.append(row)
    # A PARTY'S OWN PERIOD IS PART OF ITS NAME. Every caption row this court
    # sets ends in a comma before its status label, so the comma is
    # apparatus and the period is not ('Allergan U.S.A., Inc.', 'C.A.L. and
    # C.T.', 'Anthony A. Boyadjis, Esq.').
    if seen_pivot and left and right:
        one = _join(left).rstrip(", ")
        two = _join(right).rstrip(", ")
        ctx.crit["parties"] = [one, two]
        ctx.crit["case_name"] = f"{one} v. {two}"
        return
    whole = _join(left + right).rstrip(", ")
    if whole:
        ctx.crit["parties"] = [whole]
        ctx.crit["case_name"] = whole


# --------------------------------------------------------------------------
# the emit buffer
# --------------------------------------------------------------------------

class _Ctx:
    """What the walk placed, and where it came from."""

    def __init__(self, model, geom, pages, body_size):
        self.model = model
        self.geom = geom
        self.pages = pages
        self.body_size = body_size
        self.items: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self._fenced: dict[int, list[float]] = {}

    def _fence_tops(self, page: int) -> list[float]:
        if page not in self._fenced:
            self._fenced[page] = _fences(self.pages[page])
        return self._fenced[page]

    def _markup(self, part) -> str:
        """A FULL-MEASURE FENCE IS NOT AN UNDERLINE. pdfio tags a char
        underlined from any hairline within 5pt below its baseline, and this
        court sets its fences exactly that close to the row above them — so
        'Appellate Division.' and every release date came back underlined.
        A rule four times the row's own width, overhanging it on both
        sides, is the band mark; strip the tag it left."""
        chars = part.chars or []
        if not any(c.get("_underline") for c in chars):
            return line_markup(part)
        base = max((c["bottom"] for c in chars), default=part.top)
        if not any(-2.5 <= top - base <= 5.0
                   for top in self._fence_tops(part.page)):
            return line_markup(part)
        clean = [dict(c) for c in chars]
        for c in clean:
            c.pop("_underline", None)
        from ..pdfio.text import inline_text
        from ..resolve.footnotes import (FOOTNOTE_LABEL_CHARS, canon_glyph,
                                         mark_flags)
        return inline_text(clean, FOOTNOTE_LABEL_CHARS, canon_glyph,
                           mark_flags(part))

    def emit(self, group: list, role: str, joiner: str = " ",
             ordered: bool = False, align: str | None = None) -> None:
        # A CELL'S PIECES MAY BE GIVEN IN COLUMN ORDER — a label that wrapped
        # sets its tail on the row BELOW its own value, and re-sorting by
        # position would print 'ANSWER 07/24/2025 FILED:'.
        parts = list(group) if ordered \
            else sorted(group, key=lambda l: (l.top, l.x0))
        first = parts[0]
        pm = self.pages[first.page]
        text = ""
        for part in parts:
            piece = self._markup(part)
            text = (text.rstrip() + joiner + piece.lstrip()) \
                if text.strip() else piece
        if align is None:
            align = line_alignment(first, pm.width, self.geom,
                                   banner_center_min_size=self.body_size + 2.0)
        # A ROW FLUSH LEFT TO ITS BAND'S OWN RAIL keeps that rail: the offset
        # from the body rail is the indent the page prints.
        rel = 0.0
        if align == "L" and self.geom:
            rel = max(0.0, min(first.x0 - self.geom.body_x0, pm.width * 0.6))
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align(align), x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), rel=rel, role=role))
        self.consumed.update(p.id for p in parts)

    def cell(self, parts: list, role: str, group: list) -> m.HmLine:
        """One CaptionBlock cell. An EMPTY cell is still a row of the block
        — the two stacks stay aligned by row, so the pair is kept."""
        if not parts:
            return m.HmLine(text="", prov=m.Prov(group[0].page), role=role)
        self.emit(parts, role)
        return self.items.pop()

    def remerge(self, row, parts: list, text: str) -> None:
        """Fold a wrapped label tail into the cell above it — the TEXT and
        the PROVENANCE both, or the tail's line comes back as residual."""
        row.text = f"{row.text} {text}".replace("  ", " ")
        row.prov = m.Prov(row.prov.page,
                          row.prov.line_ids + tuple(p.id for p in parts))
        self.consumed.update(p.id for p in parts)

    def rule(self, page: int, span: str = "full", typed: bool = False,
             lines: list | None = None) -> None:
        # A FENCE RENDERS WHERE THE PAGE DRAWS IT. Core re-sorts the block
        # by each item's provenance, so a rule carrying none sorts to the
        # end; it takes the prov of the row it stands under and a stable
        # sort keeps it there.
        # A TYPED rule IS a line of the page, so it carries its own
        # provenance; a DRAWN one has none and borrows the row above it.
        if lines:
            prov = m.Prov(lines[0].page, tuple(l.id for l in lines))
            self.consumed.update(l.id for l in lines)
        else:
            prev = next((i for i in reversed(self.items)
                         if isinstance(i, m.HmLine)), None)
            prov = prev.prov if prev is not None else m.Prov(page)
        self.items.append(m.Rule(prov=prov, span=span, typed=typed))

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": [], "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
