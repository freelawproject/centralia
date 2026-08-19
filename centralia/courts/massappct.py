"""Massachusetts Appeals Court ('massappct').

A TRANSPLANT of `courts/mass.py`. The Reporter of Decisions sets the Appeals
Court's slips on the same press as the Supreme Judicial Court's — the same
612x792 page in 12pt Courier, the same body rail at x0=72, the same 36pt
first-line indent, and the same load-bearing fact: the FRONT MATTER IS SET
SOLID at the 13.55pt single lead while the body is set DOUBLE at 27.1pt, and
every band boundary is a whole number of single leads. The block is read by
counting leads, never by reading words. Italic is drawn, not encoded: pdfio
returns the reporter's italics as `<u>` runs over drawn rects, and that is
how the roster names itself (below).

TWO PAPERS, and the 42-record corpus partitions 30/12 with nothing left over.
Each is named by a landmark it always prints, never by its position alone.

THE PANEL SLIP (30). mass's ladder with two extra rungs — the court's own
name set beside the docket, and the docket restated on the axis under the
caption:

    NOTICE: All slip opinions and orders are subject to…    the first band,
                                                             -> Dropped
    24-P-647              Appeals Court    the docket AT THE RAIL and the
                                          court naming itself beside it, one
                                          baseline, TWO PIECES
    COMMONWEALTH  vs.  ROBERT ALBERT.     the caption, ON THE AXIS
    No. 24-P-647.                         the docket again, ON THE AXIS
    Bristol.     February 6, 2026. – July 1, 2026.        THE SITTING
    Present:  Sacks, Hodgens, & Toone, JJ.               the panel
    Rape.  Child Abuse.  Indecent Assault and Battery.…  the reporter's
        Statute.  Evidence, First complaint, Motive.…    topic block
    Indictments found and returned in the Superior Court  the history:
        Department on January 23, 2020.                  how the case got
    The cases were tried before Renee P. Dupuis, J.      here
    James P. McKenna for the defendant.                  the roster
    Rachel J. Eisenhaure, Assistant District Attorney, for the
        Commonwealth.
    TOONE, J.  After a Superior Court jury trial, the…   …and the writing
                                                          starts

THE RULE 23.0 MEMORANDUM (12). The court's summary decision, and a different
paper entirely — a TYPED COVER set DOUBLE, with no sitting, no panel band, no
topic block, no history and no roster, closing on the name the paper gives
itself. It is signed by the clerk BELOW the writing ('By the Court (Singh,
Hershfang & Wood, JJ.), … Clerk / Entered: July 27, 2026.'), where nothing
may reach in to take it:

    NOTICE: Summary decisions issued by the Appeals Court pursuant to
        M.A.C. Rule 23.0, as appearing in…                 -> Dropped
    COMMONWEALTH OF MASSACHUSETTS      the court naming itself, ON THE AXIS
    APPEALS COURT
                     25-P-284          the docket, RIGHT OF THE AXIS
    COMMONWEALTH                       the caption, ON THE AXIS, its pivot
    vs.                                on a row of its own
    NANCY WHITE.
    MEMORANDUM AND ORDER PURSUANT TO RULE 23.0     what the paper calls
                                                    itself -> the anchor
    Following a bench trial, the defendant was convicted…  the writing, at
                                                    the 36pt indent

    A record answering neither is not this paper and gets NOTHING.

HOW THE TWO ARE TOLD APART, and it is one question about the FIRST ROW UNDER
THE NOTICE: on a panel slip it is the docket AT THE RAIL; on a rule 23.0
memorandum it is the court's name ON THE PAGE AXIS, and the docket comes two
rows later set RIGHT of that axis. Nothing is matched against the words
'MEMORANDUM AND ORDER' to make the choice, and over the corpus the two
geometries co-occur on 30 records and on 12 and never on the same one.

WHERE THE RULE 23.0 COVER ENDS: at the BODY'S FIRST-LINE INDENT. Every row of
the cover is set on or right of the axis (the one exception being a party
name long enough to fill the measure, which centres on the axis anyway);
the writing opens 36pt in from the rail, and no cover row ever does. So the
cover is the run of rows between the notice and the first row at that indent,
its LAST row is the paper's own title, and the run is total.

HOW THE PANEL SLIP'S LOWER BANDS ARE TOLD APART, inherited unchanged from
mass:

  * THE TOPIC BLOCK is the band under the panel: the Reporter of Decisions'
    subject HEADNOTES — a list of topics, never a precis — and the only band
    in the block set with a HANGING indent: first row at the rail, runovers
    at 108. Tagged `headnotes`, not `summary`, and NOT lifted into a
    Syllabus section the way the old engine lifts it: the page prints it
    here, so it renders here.
  * A HISTORY paragraph is set the other way round, first line indented to
    108 and runovers back at the rail.
  * THE ROSTER is set the same way, and the page tells them apart by ITALIC:
    an appearance OPENS on counsel's name in italic ('*James P. McKenna* for
    the defendant.'), while a history paragraph opens roman and italicizes
    only a judge's name mid-sentence ('…were tried before *Renee P.
    Dupuis*, J.'). It never has to read a role phrase — which matters,
    because 'for the defendant' is what the history says too.

THE PAGE FOOT IS NOT THE END OF THE BLOCK. A caption footnote ('1 A
pseudonym.') opens the page's note zone, and the rest of the front matter
resumes at the TOP OF THE NEXT PAGE — nine of the thirty slips carry their
byline overleaf. The reader recognizes the note by its raised label, leaves
the whole zone to core's footnote pass (it belongs there, and it renders
there), and carries on.

WHAT THE READER DOES NOT TOUCH. The notes themselves; the folio on
continuation pages (core's furniture); the clerk's signature block and
`Entered:` line under a rule 23.0 memorandum; and anything at or below the
first byline.

WHAT THIS COURT DOES NOT PRINT, measured: none of the 42 records is mass's
`rescript` (a lone decided date, no roster) or its `advisory opinion` (no
sitting at all), so neither branch is carried here — a record shaped like
one would get NOTHING rather than be forced through the panel-slip contract.
And the bench: mass sits Justices, this court sits Judges, but the reporter
abbreviates both the same way ('TOONE, J.', 'BLAKE, C.J.', '…, JJ.'), so the
byline grammar is `abbrev` for both and the roster's closed bench vocabulary
is identical.
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

# 'TOONE, J.  After a Superior Court jury trial…' / 'BLAKE, C.J.  In this
# appeal…' — the abbreviated title runs INLINE with the first sentence, the
# same grammar mass's reporter uses. The Appeals Court sits JUDGES where the
# Supreme Judicial Court sits JUSTICES, but the reporter abbreviates both to
# 'J.' / 'C.J.' / 'JJ.', so nothing in the grammar changes.
MASSAPPCT = CourtProfile(
    "massappct", "Massachusetts Appeals Court",
    byline=BylineGrammar(style="abbrev"),
)
# The registry still carries a bare profile for massappct from
# `courts/__init__`; installing ours OVER it (rather than calling `register`,
# which raises on a duplicate) keeps this file the single place massappct is
# declared whether or not that line has been removed yet.
PROFILES[MASSAPPCT.court_id] = MASSAPPCT

STYLE_PANEL = "panel slip"
STYLE_RULE23 = "rule 23.0 memorandum"

# ---- massappct's declared facts (measured over the 42-record corpus) ------
# THE SINGLE LEAD. Every front-matter row of a panel slip sits a whole number
# of these below the last; the body is set at twice it. Measured, not
# assumed — the reader takes the page's own smallest row gap and refuses the
# record if it is not a 12pt slip's leading. (The rule 23.0 cover is set
# double throughout, and there the notice's own 11.3pt leading supplies it.)
_LEAD_RANGE = (10.0, 20.0)
# A BAND is a run of rows no more than this many single leads apart; every
# gap between two front-matter bands is 2 leads or more.
_BAND_GAP = 1.6
# HOW FAR THE BLOCK MAY RUN. Nine slips finish their roster on page 2;
# nothing needs a fifth page.
_MAX_PAGES = 4
# …and how many bands, for a consolidated appeal printing its history twice.
_MAX_BANDS = 16
# A row is AT THE RAIL when it starts on the body's left edge.
_RAIL_TOL = 1.5
# A row is CENTRED when its middle sits on the page axis.
_AXIS_TOL = 4.0
# THE BODY'S FIRST-LINE INDENT, off the rail. This is what closes the rule
# 23.0 cover, and it is a fact of the reporter's typesetting: 36pt on both
# Massachusetts papers.
_PARA_INDENT = 36.0

# '24-P-647' — this court's docket, and only this court's. mass's is
# 'SJC-13799'; the panel numeral is the Appeals Court's own.
_DOCKET = re.compile(r"^\d{2}[-‑]P[-‑]\d{2,5}$")
# The docket restated on the axis under the caption, as the reporter labels
# it. 'No.' is a label, not a name — a closed vocabulary of one.
_NO_ROW = re.compile(r"^Nos?\.\s+\d{2}[-‑]P[-‑]\d{2,5}\.?$")
# The sitting. 'February 6, 2026. – July 1, 2026.' (argued, decided). Both
# hyphen and en dash occur; the reporter uses them interchangeably in the
# same term.
_DATE = re.compile(r"^([A-Z][a-z]+ \d{1,2}, \d{4})\.?$")
_RANGE = re.compile(r"^([A-Z][a-z]+ \d{1,2}, \d{4})\.\s*[-‑–—]\s*"
                    r"([A-Z][a-z]+ \d{1,2}, \d{4})\.?$")
# The roster's printed label.
_PANEL_LEAD = "Present:"
# BENCH TITLES, a closed role vocabulary: the abbreviations this reporter
# sets after a name in a roster. Without them 'Blake, C.J., Vuono' reads as
# a judge called 'C.J.'.
_BENCH = ("C.J.", "J.", "JJ.")
# The caption's pivot, as this reporter sets it. On a panel slip it runs
# inline; on a rule 23.0 cover it stands on a row of its own.
_PIVOT = re.compile(r"\s+vs\.\s+")


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its wide gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline.

    Two rungs of the panel slip are one row set as two pieces — the docket
    ('24-P-647' at x0=72 and 'Appeals Court' at x0=288.1) and the sitting
    ('Bristol.' at x0=140.4 and 'February 6, 2026. – July 1, 2026.' at
    x0=212.4). Read piecewise the county reads as a caption row and the
    dates as an element of their own.
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
        """The row's text with the footnote MARKS taken out — 'GERARD
        FONTANA & another1 vs. CITY OF BOSTON.' names another party, not a
        party '1'."""
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
    """The page's SINGLE-SPACE leading: the smallest gap between two rows of
    the caption page. On a panel slip the notice alone sets seven rows at
    it; on a rule 23.0 cover the notice sets ten at its own 11.3pt."""
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
    """The panel slip's head rung: the docket AT THE RAIL. The court's own
    name shares the baseline as a second piece, so the test is on the FIRST
    piece — mass, whose docket stands alone, could test the whole row."""
    return bool(_DOCKET.match(row.texts[0])) and row.x0 <= body_x0 + _RAIL_TOL


def _sitting(row: _Row) -> tuple | None:
    """(argued, decided) for the sitting row's date range, (None, decided)
    for a lone date, or None."""
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


def _on_axis(row: _Row, width: float) -> bool:
    """Centred on the page axis, WITHOUT the off-rail proviso: a party name
    long enough to fill the measure ('DIRECTOR OF THE DEPARTMENT OF
    UNEMPLOYMENT ASSISTANCE & another.1', x0=73.2) is still set on the axis,
    and on the rule 23.0 cover that row must not read as body prose."""
    return abs((row.x0 + row.x1) / 2 - width / 2) <= _AXIS_TOL


def _at_indent(row: _Row, body_x0: float) -> bool:
    """The body's first-line indent — what closes the rule 23.0 cover."""
    return abs(row.x0 - (body_x0 + _PARA_INDENT)) <= _RAIL_TOL


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

# A PARTY NAME'S OWN LAST CHARACTER MAY BE A PERIOD. The reporter closes a
# caption with a full stop, so the stop comes off — but not when the last
# thing printed is an INITIAL, and this court's juvenile and 209A captions
# are nothing but initials ('V.B. vs. B.W.R.T.', 'S.B. vs. L.M.', 'IN THE
# MATTER OF A.H.'). A single letter standing at a word boundary before the
# final stop is an abbreviation and the stop is part of the name.
# …and a CORPORATE FORM abbreviates the same way ('SKECHERS USA, INC.',
# 'AVALONBAY COMMUNITIES, INC.'). Two closed vocabularies, then: the
# single-letter initial and the entity suffix this reporter sets.
_ABBREV_END = re.compile(
    r"\b(?:[A-Z]|INC|LLC|LLP|CO|CORP|LTD|ASSN|BROS|N\.A|P\.C|L\.P)\.$")


def _tidy(text: str) -> str:
    out = _norm(text).rstrip(",; ")
    while out.endswith(".") and not _ABBREV_END.search(out):
        out = out[:-1].rstrip(",; ")
    return out


def _name_from(crit: dict, rows: list) -> None:
    """The parties either side of the caption's pivot.

    A consolidated slip prints one caption and says so ('ADOPTION OF COLTON
    (and a consolidated case1).'), but the reporter can also set two, one
    per appeal, and the pivot then appears once in each. Joined wholesale
    that reads as one enormous party, so the rows are grouped at each new
    pivot and the name is built from the FIRST case; the others stand in
    `caption`, verbatim.
    """
    groups: list = [[]]
    for text in rows:
        if _PIVOT.search(text) and any(_PIVOT.search(t) for t in groups[-1]):
            groups.append([])
        groups[-1].append(text)
    lead = " ".join(groups[0])
    parts = _PIVOT.split(lead, maxsplit=1)
    if len(parts) == 2:
        left = _tidy(parts[0])
        right = _tidy(parts[1])
        if left and right:
            crit["parties"] = [left, right]
            crit["case_name"] = f"{left} v. {right}"
            return
    flat = _tidy(lead)
    if flat:
        crit["parties"] = [flat]
        crit["case_name"] = flat


def _panel_names(roster: str) -> list:
    """['Sacks', 'Hodgens', 'Toone'] — the roster read by its own bench
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

    # WHICH RUNGS THE REPORTER CENTRES. The caption, the restated docket, the
    # sitting and the panel are set on the page axis; the rail docket, the
    # history and the roster are set at the rail with a 36pt first-line
    # indent, and a wrapped roster row that happens to end near the right
    # margin ('Rachel J. Eisenhaure, Assistant District Attorney, for the')
    # centres to the point under an axis test alone. The topic block is
    # centred only when the reporter sets it on ONE row.
    _MAY_CENTRE = ("caption", "date", "panel", "headnotes", "title", "court")

    def emit(self, row: _Row, role: str, alone: bool = False,
             centre: bool = True, keep_x: bool = False) -> None:
        pm = self.pages[row.page]
        ok = (centre and role in self._MAY_CENTRE
              and _centred(row, pm.width, self.body_x0))
        if ok and role == "headnotes":
            measure = ((self.geom.right_x1 - self.geom.body_x0)
                       if self.geom else pm.width - 2 * self.body_x0)
            ok = alone and (row.x1 - row.x0) <= 0.95 * measure
        align = m.Align.CENTER if ok else m.Align.LEFT
        # A ROW THE PAGE SETS NEITHER AT THE RAIL NOR ON THE AXIS keeps its
        # own offset: the rule 23.0 docket stands alone at x0=360 on a
        # 612pt page, and rendered flush left it reads as a rail row, which
        # is not where the paper puts it.
        rel = (row.x0 - self.body_x0) if (keep_x and not ok) else 0.0
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=align, x0=row.x0, size=row.size, rel=rel, role=role))
        self.consumed.update(row.ids)

    def emit_piece(self, row: _Row, piece, role: str,
                   align: m.Align = m.Align.LEFT) -> None:
        """One PIECE of a visual row, tagged on its own. The docket row sets
        two things on one baseline — the number at the rail and the court
        naming itself beside it — and one role cannot be true of both."""
        self.items.append(m.HmLine(
            text=line_markup(piece).strip(),
            prov=m.Prov(row.page, (piece.id,)),
            align=align, x0=piece.x0, size=piece.size or 0.0, role=role))
        self.consumed.add(piece.id)

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
                "anchor_ids": self.anchor, "doc_type_final": None}


@decider("headmatter.read", court="massappct")
def read_headmatter_massappct(model, geom, **_):
    """Read one of massappct's two papers, or NOTHING."""
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
    width = model.pages[0].width

    ctx = _Ctx(model, geom, body_x0)
    # Every row carries the band it belongs to, because the head of the
    # ladder is read by ROW and its tail by BAND: mass sets one slip's
    # caption only ONE lead under the docket, so those two rungs can share a
    # band and a band-level walk loses the record entirely.
    flat: list = []
    band_of: list = []
    for bi, band in enumerate(bands):
        for row in band:
            flat.append(row)
            band_of.append(bi)

    i = 0
    # THE NOTICE is the page's first band, and it is the reporter's, not the
    # court's: recorded as removed, never rendered. Both papers open on one,
    # and they are different notices — the slip's citation warning and the
    # rule 23.0 precedential disclaimer.
    if _is_notice(bands[0]):
        ctx.drop(bands[0], "notice")
        i = len(bands[0])
    if i >= len(flat):
        return NOTHING

    # THE FIRST ROW UNDER THE NOTICE NAMES THE PAPER: the docket at the rail
    # on a panel slip, the court's own name on the axis on a rule 23.0
    # memorandum.
    if _is_docket(flat[i], body_x0):
        return _read_panel_slip_head(ctx, bands, band_of, flat, i, width)
    if _on_axis(flat[i], width) and not _DOCKET.match(flat[i].texts[0]):
        return _read_rule23(ctx, flat, i, width, body_x0)
    return NOTHING


# --------------------------------------------------------------------------
# the rule 23.0 memorandum — a typed cover, set double
# --------------------------------------------------------------------------

def _read_rule23(ctx: _Ctx, flat: list, i: int, width: float,
                 body_x0: float):
    """The cover is the run from the notice to the body's first-line indent.

    Inside it the docket is the one row set OFF the axis (right of it), the
    rows above the docket are the court naming itself, the rows between the
    docket and the last row are the caption, and the LAST row is what the
    paper calls itself. Nothing is read by wording, and the run is total.
    """
    cover: list = []
    for j in range(i, min(i + 12, len(flat))):
        row = flat[j]
        if row.page != 1 or _at_indent(row, body_x0):
            break
        cover.append(row)
    # masthead (>=1) + docket + caption (>=1) + title. Twelve records, and
    # the run measures five rows (a one-party caption) or seven.
    if not 4 <= len(cover) <= 8:
        return NOTHING
    dk = [k for k, r in enumerate(cover)
          if _DOCKET.match(r.texts[0]) and not _on_axis(r, width)]
    if len(dk) != 1 or not 1 <= dk[0] <= len(cover) - 3:
        return NOTHING
    d = dk[0]
    if not _on_axis(cover[-1], width):
        return NOTHING

    for row in cover[:d]:
        ctx.emit(row, "court")
    ctx.emit(cover[d], "docket", centre=False, keep_x=True)
    caption = cover[d + 1:-1]
    for row in caption:
        ctx.emit(row, "caption")
    title = cover[-1]
    ctx.emit(title, "title")
    # THE ANCHOR. An unsigned writing has nothing to open on but the name
    # the paper gives itself; claimed here, core may hand this one row back
    # to the stream rather than let the document lose its opinion.
    ctx.anchor.extend(title.ids)

    ctx.crit["headmatter_style"] = STYLE_RULE23
    ctx.crit["docket_number"] = cover[d].texts[0]
    ctx.crit["caption"] = [r.text for r in caption]
    ctx.crit["title"] = title.text
    _name_from(ctx.crit, [r.unmarked() for r in caption])
    return ctx.result()


# --------------------------------------------------------------------------
# the panel slip — mass's ladder, two rungs longer
# --------------------------------------------------------------------------

def _read_panel_slip_head(ctx: _Ctx, bands: list, band_of: list, flat: list,
                          i: int, width: float):
    body_x0 = ctx.body_x0
    # THE DOCKET ROW: the number at the rail, and the court naming itself on
    # the same baseline. One role cannot be true of both, so the row is
    # emitted piecewise.
    head = flat[i]
    docket = head.texts[0]
    ctx.emit_piece(head, head.pieces[0], "docket")
    for piece in head.pieces[1:]:
        if _norm(piece.plain):
            ctx.emit_piece(head, piece, "court", m.Align.RIGHT)
    i += 1

    # THE RUNGS BELOW, each found by its own landmark and required in order:
    # the restated docket on the axis, the sitting, the panel.
    no_i = sit_i = pres_i = None
    for j in range(i, len(flat)):
        if flat[j].page != 1:
            break
        if no_i is None and _NO_ROW.match(flat[j].text) \
                and _on_axis(flat[j], width):
            no_i = j
        elif no_i is not None and sit_i is None and _sitting(flat[j]):
            sit_i = j
        elif flat[j].text.startswith(_PANEL_LEAD):
            pres_i = j
            break
    if no_i is None or sit_i is None or pres_i is None:
        return NOTHING
    if not (i < no_i and no_i + 1 == sit_i and sit_i + 1 == pres_i):
        return NOTHING

    # THE CAPTION: every row between the docket and the restated docket.
    caption = flat[i:no_i]
    if len(caption) > 4:
        return NOTHING
    for row in caption:
        ctx.emit(row, "caption")

    ctx.emit(flat[no_i], "docket")
    # THE SITTING: the county the case came from and the days the court heard
    # and decided it, on one baseline.
    argued, decided = _sitting(flat[sit_i])
    ctx.emit(flat[sit_i], "date")
    if argued:
        ctx.crit["submitted"] = argued
    ctx.crit["decision_date"] = decided

    # THE PANEL, its label and the judges who sat.
    panel = bands[band_of[pres_i]]
    if panel[0] is not flat[pres_i]:
        return NOTHING
    roster = " ".join(r.text for r in panel)
    for row in panel:
        ctx.emit(row, "panel")
    ctx.crit["panel_line"] = roster
    ctx.crit["judges"] = _norm(roster[len(_PANEL_LEAD):])
    ctx.crit["panel"] = _panel_names(roster)

    b = band_of[pres_i] + 1
    # THE TOPIC BLOCK — the reporter's subject headings, hanging-indented.
    # Tagged `headnotes`, NOT `summary` and NOT lifted into a Syllabus: it is
    # the Reporter of Decisions' list of SUBJECTS, and a summary is a precis
    # of the case. What the render puts in the margin beside it is the only
    # thing that changes.
    if b < len(bands) and _hanging(bands[b], body_x0) \
            and not _paragraph(bands[b], body_x0):
        for row in bands[b]:
            ctx.emit(row, "headnotes", alone=len(bands[b]) == 1)
            ctx.anchor.extend(row.ids)
        b += 1

    ctx.crit["headmatter_style"] = STYLE_PANEL
    ctx.crit["docket_number"] = docket
    ctx.crit["caption"] = [r.text for r in caption]
    _name_from(ctx.crit, [r.unmarked() for r in caption])
    return _read_panel_slip_tail(ctx, bands, b)


def _read_panel_slip_tail(ctx: _Ctx, bands: list, b: int):
    """History bands, then the roster, then the byline ends the block."""
    parser = BylineParser(MASSAPPCT.byline)
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
        # A CAPTION FOOTNOTE opens the page's note zone: the block resumes at
        # the top of the next page and the notes stay with core.
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
