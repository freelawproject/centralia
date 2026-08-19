"""Supreme Judicial Court of Massachusetts ('mass').

Everything unique to mass lives here. It imports core, never another court
file, and no other court file imports it.

THE PAPER. One slip, set on a 612x792 page in 12pt Courier: body rail at
x0=72, a 36pt first-line indent, and — the fact the whole reader turns on —
a HEADMATTER SET SOLID at the 13.55pt single-space leading over a BODY set
double (27.1pt). Every band boundary in the front matter is a whole number
of those single leads, so the block is read by counting leads, never by
reading words. Italic is drawn, not encoded: the reporter's italics come
back from pdfio as `<u>` runs over drawn rects, and that is how the roster
names itself (below).

THE LADDER. The court prints one ladder and omits rungs; each rung is named
by its own landmark, never by its position alone:

    NOTICE: All slip opinions and orders are subject to…   the first band,
                                                            -> Dropped
    SJC-13799                                    the docket, AT THE RAIL
    COMMONWEALTH  vs.  BRIAN DONOVAN.            the caption, ON THE AXIS
    Norfolk.        January 7, 2026. - March 31, 2026.      THE SITTING
    Present:  Budd, C.J., Gaziano, Kafker, …, JJ.           the panel
    Constitutional Law, Assistance of counsel.  Practice,…  the reporter's
        Assistance of counsel, Transfer hearing, New trial. topic block
    Indictments found and returned in the Superior Court    the history:
        Department on February 21, 2018, …                  how the case
    The cases were tried before Douglas H. Wilkins, J., …   got here
    Ruth O'Meara-Costello for the defendant.                the roster
    Meagen K. Monahan, Assistant District Attorney, for the
        Commonwealth.
    WENDLANDT, J. This case presents the question whether…  …and the
                                                            writing starts

THREE PAPERS, and ONE QUESTION ABOUT THE ROW UNDER THE CAPTION names them
(measured over the 50-record corpus, which it partitions 34/14/2 with
nothing left over):

  * 'panel slip' (34) — that row is TWO PIECES on one baseline, the county
    at the left and an argued–decided date RANGE at the right, and a
    'Present:' roster stands under it. It carries every rung above.

  * 'rescript' (14) — that row is a LONE DATE centred on the page axis, and
    no roster follows: the single-justice appeal decided per curiam. It
    carries the topic block and then the writing itself, unsigned. There is
    no history and no roster (what roster it has, it prints BELOW the
    writing, where nothing may reach in to take it).

  * 'advisory opinion' (2) — there is no such row at all: the Justices
    answer the Senate collectively, so there is neither a sitting nor a
    panel. Caption, topic block, and the submission recital ('On April 27,
    2026, the Justices submitted the following response…'), then the
    answer opens on its salutation.

    A record answering none of the three is not this paper and gets NOTHING.

HOW THE BANDS ARE TOLD APART, once the ladder is under way:

  * THE TOPIC BLOCK is the band that follows the panel (or the sitting, or
    the caption): the Reporter of Decisions' subject HEADNOTES — a list of
    topics, never a precis — and the only band in the block set with a
    HANGING indent: first row at the rail, runovers at 108.
  * A HISTORY paragraph is set the other way round, first line indented to
    108 and runovers back at the rail.
  * THE ROSTER is set the same way, and the page tells them apart by ITALIC:
    an appearance OPENS on the counsel's name in italic ('*Ruth
    O'Meara-Costello* for the defendant.'), while a history paragraph opens
    roman and italicizes only a judge's name mid-sentence ('…was heard by
    *Linda G. Sable*, J.'). Over the 34 panel slips that test agrees with
    the reporter on every band, and it never has to read a role phrase —
    which matters, because 'for the defendant' is what the history says too.
    The roster is also final: no history band ever follows one.

THE PAGE FOOT IS NOT THE END OF THE BLOCK. A caption footnote ('1 Of the
Lynn Allegaert Revocable Trust.') opens the page's note zone, and the rest
of the front matter — history, roster — resumes at the TOP OF THE NEXT
PAGE. The reader recognizes the note by its raised label, leaves the whole
zone to core's footnote pass (it belongs there, and it renders there), and
carries on overleaf.

WHAT THE READER DOES NOT TOUCH. The notes themselves; the top-right folio
on continuation pages (core's furniture); and anything at or below the
first byline. On a rescript the reader stops at the topic block, and the
per curiam writing beneath it is left exactly as the page prints it —
unsigned, because the page signs it with nothing.

TWO THINGS THIS READER CANNOT REACH, both recorded rather than hidden:
a rescript's roster, printed BELOW the writing, stays in the writing (core's
trailing-roster harvest is switched per COURT, and mass needs it per PAPER —
switched on court-wide it lifts a paragraph out of a panel-slip majority);
and on the two rescripts whose disposition falls on page 1 or 2, core reads
'Judgment affirmed.' as a doc-type heading and opens a second writing there.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import (line_markup, mark_flags,
                                opens_with_raised_label)
from ..resolve.furniture import FurnitureFinder
from . import PROFILES

# 'GAZIANO, J. Under G. L. c. 276, § 58A…' / 'BUDD, C.J. Before
# entering…' — the abbreviated title runs INLINE with the first sentence.
MASS = CourtProfile(
    "mass", "Supreme Judicial Court of Massachusetts",
    byline=BylineGrammar(style="abbrev"),
)
# The registry still carries a bare profile for mass from `courts/__init__`;
# installing ours over it keeps this file the single place mass is declared
# whether or not that line has been removed yet.
PROFILES[MASS.court_id] = MASS

STYLE_PANEL = "panel slip"
STYLE_RESCRIPT = "rescript"
STYLE_ADVISORY = "advisory opinion"

# ---- mass's declared facts (measured over the 50-record corpus) ----------
# THE SINGLE LEAD. Every front-matter row sits a whole number of these
# below the last; the body is set at twice it. Measured, not assumed — the
# reader takes the page's own smallest row gap and refuses the record if it
# is not a 12pt slip's leading.
_LEAD_RANGE = (10.0, 20.0)
# A BAND is a run of rows no more than this many single leads apart; every
# gap between two front-matter bands is 2 leads or more.
_BAND_GAP = 1.6
# HOW FAR THE BLOCK MAY RUN. The longest roster in the corpus (Meta
# Platforms: 42 rows of State attorneys general) ends on page 2; nothing
# needs a fifth page.
_MAX_PAGES = 4
# …and how many bands. Two consolidated appeals print their history twice
# (psikarakis/smith: six history bands before the roster).
_MAX_BANDS = 16
# A row is AT THE RAIL when it starts on the body's left edge.
_RAIL_TOL = 1.5
# A row is CENTRED when its middle sits on the page axis.
_AXIS_TOL = 4.0

# 'SJC-13799' — this court's docket, and only this court's.
_DOCKET = re.compile(r"^SJC[-‑]\d{4,5}$")
# The sitting. 'January 7, 2026. - March 31, 2026.' (argued, decided) on a
# panel slip; 'April 30, 2026.' alone on a rescript. Both hyphen and en
# dash occur; the court uses them interchangeably in the same term.
_DATE = re.compile(r"^([A-Z][a-z]+ \d{1,2}, \d{4})\.?$")
_RANGE = re.compile(r"^([A-Z][a-z]+ \d{1,2}, \d{4})\.\s*[-‑–—]\s*"
                    r"([A-Z][a-z]+ \d{1,2}, \d{4})\.?$")
# The roster's printed label, and the plural bench title that closes it.
_PANEL_LEAD = "Present:"
# BENCH TITLES, a closed role vocabulary: the abbreviations this court sets
# after a name in a roster. Without them 'Budd, C.J., Gaziano' reads as a
# justice called 'C.J.'.
_BENCH = ("C.J.", "J.", "JJ.")
# The caption's pivot, as this reporter sets it.
_PIVOT = re.compile(r"\s+vs\.\s+")


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its wide gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline.

    The sitting is one row set as two pieces ('Norfolk.' at x0=136.8 and
    'January 7, 2026. - March 31, 2026.' at x0=208.8); read piecewise the
    county reads as a caption row and the dates as an element of their own.
    """

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "texts", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.texts = [_norm(p.plain) for p in self.pieces]
        self.text = "  ".join(t for t in self.texts if t)

    @property
    def ids(self) -> tuple:
        return tuple(p.id for p in self.pieces)

    def markup(self) -> str:
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out

    def unmarked(self) -> str:
        """The row's text with the footnote MARKS taken out — 'LYNN
        ALLEGAERT, trustee,1 vs. …' names a trustee, not a party '1'."""
        out = []
        for p in self.pieces:
            flags = mark_flags(p)
            chars = [c for c in p.chars if (c.get("text") or "")]
            keep = "".join(
                (c.get("text") or "")
                for i, c in enumerate(chars)
                if not (i < len(flags) and flags[i]))
            out.append(_norm(keep))
        return "  ".join(t for t in out if t)

    def italic_open(self) -> bool:
        """Does the row OPEN on an italic run? This is what tells an
        appearance from a history paragraph — the reporter sets counsel's
        name in italic at the head of the entry, and sets a judge's name in
        italic only inside a sentence."""
        return self.markup().lstrip().startswith("<u>")


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows, furniture removed, in the page's own order."""
    rows: list = []
    for pm in model.pages[:max_pages]:
        buckets: dict = {}
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            buckets.setdefault(round(line.top, 0), []).append(line)
        rows.extend(_Row(v) for v in buckets.values())
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


def _single_lead(rows: list) -> float | None:
    """The page's SINGLE-SPACE leading: the smallest gap between two rows
    of the caption page. The notice alone sets seven rows at it."""
    gaps = sorted(round(b.top - a.top, 1)
                  for a, b in zip(rows, rows[1:])
                  if b.page == a.page and b.top - a.top > 6.0)
    if not gaps:
        return None
    lead = gaps[0]
    return lead if _LEAD_RANGE[0] <= lead <= _LEAD_RANGE[1] else None


def _bands(rows: list, lead: float) -> list:
    """Rows grouped into bands: a blank line (2 leads) opens a new one."""
    out: list = []
    for row in rows:
        if out and out[-1][-1].page == row.page \
                and row.top - out[-1][-1].top <= lead * _BAND_GAP:
            out[-1].append(row)
        else:
            out.append([row])
    return out


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _is_notice(band: list) -> bool:
    return band[0].text.lower().startswith("notice:")


def _is_docket(row: _Row, body_x0: float) -> bool:
    return bool(_DOCKET.match(row.text)) and row.x0 <= body_x0 + _RAIL_TOL


def _sitting(row: _Row) -> tuple | None:
    """(argued, decided) for a panel slip's sitting row, (None, decided)
    for a rescript's lone date, or None."""
    tail = row.texts[-1]
    mo = _RANGE.match(tail)
    if mo:
        return (mo.group(1), mo.group(2))
    mo = _DATE.match(tail)
    if mo:
        return (None, mo.group(1))
    return None


def _centred(row: _Row, width: float, body_x0: float) -> bool:
    return (abs((row.x0 + row.x1) / 2 - width / 2) <= _AXIS_TOL
            and row.x0 > body_x0 + _RAIL_TOL)


def _hanging(band: list, body_x0: float) -> bool:
    """The topic block's shape: first row at the rail (or centred alone),
    runovers indented. A history paragraph is the exact inverse."""
    if len(band) == 1:
        return True
    return (band[0].x0 <= body_x0 + _RAIL_TOL
            and all(r.x0 > body_x0 + _RAIL_TOL for r in band[1:]))


def _paragraph(band: list, body_x0: float) -> bool:
    return (len(band) >= 2 and band[0].x0 > body_x0 + _RAIL_TOL
            and any(r.x0 <= body_x0 + _RAIL_TOL for r in band[1:]))


# --------------------------------------------------------------------------
# the caption's own grammar
# --------------------------------------------------------------------------


def _tidy(text: str) -> str:
    """A party name's own closing stop is part of the NAME.

    Stripping `.` off the tail turns an initials-only party into a typo —
    'V.B.' became 'V.B' (massappct), and mass prints two of its own:
    'R.D. v. COMMONWEALTH' and 'S.W. v. COMMONWEALTH' read 'R.D' and 'S.W'.
    Found by massappct's porter while transplanting this file, which fixed it
    in its own copy and flagged it here rather than editing a court the user
    had approved. Two closed vocabularies keep the stop: a single-letter
    initial at a word boundary, and the entity suffixes."""
    flat = text.rstrip(",; ")
    if not flat.endswith("."):
        return flat
    tail = flat[:-1].rsplit(None, 1)[-1] if flat[:-1].split() else ""
    if re.fullmatch(r"(?:[A-Z]\.)*[A-Z]", tail):
        return flat                      # 'V.B.' / 'R.D.' / 'B.W.R.T.'
    if tail.upper().rstrip(".") in (
            "INC", "LLC", "LLP", "CO", "CORP", "LTD", "ASSN", "BROS",
            "N.A", "P.C", "L.P"):
        return flat                      # 'SKECHERS USA, INC.'
    return flat[:-1]

def _name_from(crit: dict, rows: list) -> None:
    """The parties either side of the caption's pivot.

    A consolidated slip prints TWO captions, one per appeal
    ('COMMONWEALTH vs. STEFANOS PSIKARAKIS.' over 'COMMONWEALTH vs.
    MAURICE SMITH.'), and the pivot appears once in each. Joined wholesale
    that reads as a party called 'STEFANOS PSIKARAKIS. COMMONWEALTH vs.
    MAURICE SMITH', so the rows are grouped at each new pivot and the name
    is built from the FIRST case; the others stand in `caption`, verbatim,
    beside their own dockets.
    """
    groups: list = [[]]
    for text in rows:
        if _PIVOT.search(text) and any(_PIVOT.search(t) for t in groups[-1]):
            groups.append([])
        groups[-1].append(text)
    lead = " ".join(groups[0])
    parts = _PIVOT.split(lead, maxsplit=1)
    if len(parts) == 2:
        left = _tidy(_norm(parts[0]))
        right = _tidy(_norm(parts[1]))
        if left and right:
            crit["parties"] = [left, right]
            crit["case_name"] = f"{left} v. {right}"
            return
    flat = _tidy(_norm(lead))
    if flat:
        crit["parties"] = [flat]
        crit["case_name"] = flat


def _panel_names(roster: str) -> list:
    """['Budd, C.J.', 'Gaziano', …] — the roster read by its own bench
    vocabulary. A title abbreviation belongs to the name before it; the
    closing plural ('JJ.') belongs to all of them and names nobody."""
    body = roster[len(_PANEL_LEAD):] if roster.startswith(_PANEL_LEAD) \
        else roster
    out: list = []
    for tok in re.split(r",|&", body):
        tok = _norm(tok).strip(". ")
        if not tok:
            continue
        dotted = tok if tok.endswith(".") else tok + "."
        if dotted in _BENCH:
            if dotted != "JJ." and out:
                out[-1] = f"{out[-1]}, {dotted}"
            continue
        out.append(tok)
    return out


def _judges_named(markup: str) -> list:
    """The judges a history band names: an ITALIC name followed by the
    abbreviated bench title the reporter always sets after it."""
    flat = re.sub(r"</u>\s*<u>", " ", markup)
    out: list = []
    for mo in re.finditer(r"<u>([^<]{2,70}?)</u>,\s*J\.", flat):
        name = _norm(mo.group(1)).strip(",; ")
        if name and name not in out:
            out.append(name)
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, model, geom, body_x0):
        self.model = model
        self.geom = geom
        self.body_x0 = body_x0
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}
        self.anchor: list = []
        # WHERE THIS PAPER PRINTS ITS ROSTER. A panel slip prints counsel in
        # the front matter, where it stays; a rescript prints it on the LAST
        # page, under 'Judgment affirmed.', and there it is not part of the
        # writing at all. The switch is therefore per PAPER, not per court —
        # declared for the record the reader just read.
        self.counsel_after: bool = False

    # WHICH RUNGS THE REPORTER CENTRES. The caption, the sitting and the
    # panel are set on the page axis; the docket, the history and the
    # roster are set at the rail with a 36pt first-line indent, and a
    # wrapped roster row that happens to end near the right margin
    # ('Meagen K. Monahan, Assistant District Attorney, for the') centres
    # to the point under an axis test alone. The topic block is centred
    # only when the reporter sets it on ONE row.
    _MAY_CENTRE = ("caption", "date", "panel", "headnotes")

    def emit(self, row: _Row, role: str, alone: bool = False,
             centre: bool = True) -> None:
        pm = self.pages[row.page]
        ok = (centre and role in self._MAY_CENTRE
              and _centred(row, pm.width, self.body_x0))
        if ok and role == "headnotes":
            measure = ((self.geom.right_x1 - self.geom.body_x0)
                       if self.geom else pm.width - 2 * self.body_x0)
            ok = alone and (row.x1 - row.x0) <= 0.95 * measure
        align = m.Align.CENTER if ok else m.Align.LEFT
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=align, x0=row.x0, size=row.size, role=role))
        self.consumed.update(row.ids)

    def drop(self, band: list, kind: str) -> None:
        self.dropped.append(m.Dropped(
            text=" ".join(r.text for r in band)[:1200],
            prov=m.Prov(band[0].page,
                        tuple(i for r in band for i in r.ids)),
            kind=kind))
        for row in band:
            self.consumed.update(row.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None,
                "counsel_after_writings": self.counsel_after}


@decider("headmatter.read", court="mass")
def read_headmatter_mass(model, geom, **_):
    """Read one of mass's three papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    finder = FurnitureFinder(model, body_x0, geom.body_size if geom else 12.0)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if not rows:
        return NOTHING
    page1 = [r for r in rows if r.page == 1]
    lead = _single_lead(page1)
    if lead is None:
        return NOTHING
    bands = _bands(rows, lead)

    ctx = _Ctx(model, geom, body_x0)
    # Every row carries the band it belongs to, because the head of the
    # ladder is read by ROW and its tail by BAND: on a long-headnote slip
    # the court sets the caption only ONE lead under the docket
    # (commonwealth v. arias), so those two rungs share a band and a
    # band-level walk lost the record entirely.
    flat: list = []
    band_of: list = []
    for bi, band in enumerate(bands):
        for row in band:
            flat.append(row)
            band_of.append(bi)

    i = 0
    # THE NOTICE is the page's first band, and it is the reporter's, not
    # the court's: recorded as removed, never rendered.
    if _is_notice(bands[0]):
        ctx.drop(bands[0], "notice")
        i = len(bands[0])
    # THE DOCKET stands at the rail, one row per appeal.
    dockets: list = []
    while i < len(flat) and _is_docket(flat[i], body_x0):
        dockets.append(flat[i].text)
        ctx.emit(flat[i], "docket")
        i += 1
    if not dockets:
        return NOTHING

    # THE ROW UNDER THE CAPTION NAMES THE PAPER.
    sit_i = pres_i = None
    for j in range(i, len(flat)):
        if flat[j].page != 1:
            break
        if sit_i is None and _sitting(flat[j]):
            sit_i = j
        if pres_i is None and flat[j].text.startswith(_PANEL_LEAD):
            pres_i = j
            break
    if sit_i is not None and pres_i is not None and pres_i > sit_i:
        style = STYLE_PANEL
    elif sit_i is not None and pres_i is None:
        style = STYLE_RESCRIPT
    elif sit_i is None and pres_i is None:
        style = STYLE_ADVISORY
    else:
        return NOTHING

    # THE CAPTION: every row between the docket and the sitting. An
    # advisory has no sitting, and its caption is the band under the docket.
    cap_end = sit_i if sit_i is not None else next(
        (j for j in range(i, len(flat)) if band_of[j] != band_of[i]), i)
    if cap_end <= i or cap_end - i > 4:
        return NOTHING
    caption = flat[i:cap_end]
    for row in caption:
        ctx.emit(row, "caption")
    i = cap_end

    if style is not STYLE_ADVISORY:
        # THE SITTING: the county the case came from and the days the court
        # heard and decided it, on one baseline.
        argued, decided = _sitting(flat[i])
        ctx.emit(flat[i], "date")
        if argued:
            ctx.crit["submitted"] = argued
        ctx.crit["decision_date"] = decided
        i += 1

    if style is STYLE_PANEL:
        if i != pres_i:
            return NOTHING
        panel = bands[band_of[i]]
        if panel[0] is not flat[i]:
            return NOTHING
        roster = " ".join(r.text for r in panel)
        for row in panel:
            ctx.emit(row, "panel")
        ctx.crit["panel_line"] = roster
        ctx.crit["judges"] = _norm(roster[len(_PANEL_LEAD):])
        ctx.crit["panel"] = _panel_names(roster)
        i += len(panel)

    # THE TOPIC BLOCK — the reporter's subject headings, hanging-indented.
    # Tagged `headnotes`, NOT `summary`: 'Pretrial Detention. Robbery.
    # Dangerous Weapon. Statute, Construction. Moot Question.' is the
    # Reporter of Decisions' list of SUBJECTS, and a summary is a precis of
    # the case. Nothing about the band's geometry changes; what changes is
    # the name the render puts in the margin beside it.
    b = band_of[i] if i < len(flat) else len(bands)
    if i < len(flat) and bands[b][0] is flat[i] \
            and _hanging(bands[b], body_x0) \
            and not _paragraph(bands[b], body_x0):
        for row in bands[b]:
            ctx.emit(row, "headnotes", alone=len(bands[b]) == 1)
            ctx.anchor.extend(row.ids)
        b += 1

    ctx.crit["headmatter_style"] = style
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    ctx.crit["caption"] = [r.text for r in caption]
    _name_from(ctx.crit, [r.unmarked() for r in caption])

    if style is STYLE_RESCRIPT:
        # The per curiam writing opens directly under the topic block, and
        # the roster is printed BELOW it — so this paper, and only this
        # paper, asks core for the trailing-roster harvest. Switched on
        # court-wide it costs a panel-slip majority its closing paragraph
        # (allegaert: '…faults appellate counsel for…' reads as an
        # appearance), which is why the flag is reported per RECORD.
        ctx.counsel_after = True
        return ctx.result()
    if style is STYLE_ADVISORY:
        # THE SUBMISSION RECITAL: one tight band stating the day the
        # Justices answered. Below it the answer itself, set double.
        if b < len(bands) and len(bands[b]) >= 2 \
                and _paragraph(bands[b], body_x0):
            from ..resolve.headmatter import find_date as _find_date
            text = " ".join(r.text for r in bands[b])
            for row in bands[b]:
                ctx.emit(row, "date", centre=False)
            date = _find_date(text)
            if date:
                ctx.crit["decision_date"] = date
            ctx.crit["history"] = text
        return ctx.result()

    return _read_panel_slip(ctx, bands, b)


def _read_panel_slip(ctx: _Ctx, bands: list, b: int):
    """History bands, then the roster, then the byline ends the block."""
    parser = BylineParser(MASS.byline)
    history: list = []
    counsel: list = []
    judges: list = []
    in_counsel = False
    signed = False
    skip_page = None
    seen = 0
    while b < len(bands) and seen < _MAX_BANDS:
        band = [r for r in bands[b] if not (set(r.ids) <= ctx.consumed)]
        b += 1
        if not band:
            continue
        if band[0].page == skip_page:
            continue                      # the note zone runs to the foot
        seen += 1
        if parser.parse(band[0].text):
            signed = True
            break
        # A CAPTION FOOTNOTE opens the page's note zone: the block resumes
        # at the top of the next page and the notes stay with core.
        if opens_with_raised_label(band[0].pieces[0]):
            skip_page = band[0].page
            seen -= 1
            continue
        if in_counsel or band[0].italic_open():
            in_counsel = True
            for row in band:
                ctx.emit(row, "counsel")
                counsel.append(row.text)
            continue
        markup = " ".join(r.markup() for r in band)
        judges.extend(j for j in _judges_named(markup) if j not in judges)
        for row in band:
            ctx.emit(row, "lower-court")
            history.append(row.text)
    if not signed:
        # No byline where this paper always sets one: not this contract.
        return NOTHING
    if history:
        ctx.crit["history"] = _norm(" ".join(history))[:2000]
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:2000]
    return ctx.result()
