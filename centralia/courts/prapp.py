"""Tribunal de Apelaciones de Puerto Rico ('prapp').

Everything unique to prapp lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py; this module adds the reader only, so importing it can
never raise a duplicate profile.

THE CONTRACT — a Spanish-language BOXED cover on a legal sheet (612 x 1008
on all 42 records), and the box is really drawn: two vertical rules for its
sides running the height of the page, two more for the caption's columns,
and horizontal rules closing the caption band and the page foot.

    ┌─ page 1, 612 x 1008 ───────────────────────────────────────────┐
    │ ┌──────────────────────────────────────────────────────────┐   │
    │ │            Estado Libre Asociado de Puerto Rico          │   │
    │ │               TRIBUNAL DE APELACIONES                    │   │
    │ │                     PANEL IX                             │   │
    │ ├───────────────────────┬──────────┬───────────────────────┤   │
    │ │ ADA IRIS TORRES       │          │ APELACIÓN             │   │
    │ │ SABATER               │          │ procedente del        │   │
    │ │        Apelante       │          │ Tribunal de Primera   │   │
    │ │           v.          │TA2026AP00409 Instancia, Sala …   │   │
    │ │ JULITA COLÓN BÁEZ     │          │ Caso número:          │   │
    │ │        Apelada        │          │ PO2021CV02172         │   │
    │ │                       │          │ Sobre: Nulidad de …   │   │
    │ ├───────────────────────┴──────────┴───────────────────────┤   │
    │ │ Panel integrado por su presidenta, la juez Brignoni …    │   │
    │ │ Aldebol Mora, Juez Ponente                               │   │
    │ │                   S E N T E N C I A            <- core's │   │
    │ └──────────────────────────────────────────────────────────┘   │
    └────────────────────────────────────────────────────────────────┘

THE CAPTION IS THREE COLUMNS, NOT TWO, and the page draws both dividers:
two vertical rules at 251-292pt and 364-400pt, spanning only the caption
band. The first column holds the parties and their statuses, the SECOND
holds nothing but this court's own docket ('TA2026AP00409'), and the third
holds the appeal's origin — the tribunal below, its case number, and the
subject ('Sobre: …'). The band is found from the rules, never from a row
count: 39 records draw the two dividers once and 3 draw each of them twice,
1pt apart, which is a doubled stroke and not four columns.

`CaptionBlock` models TWO stacks, so the second and third columns are
rendered as one right-hand stack in the page's own order. That is a
reproduction choice, and it is the honest one available: the alternative is
to drop a divider the page actually draws, or to interleave the docket into
a party's name. What the columns MEAN is not lost — the docket, the origin,
the lower court's case number and the subject are each read off their own
cell into criteria.

BELOW THE BAND THE COURT SIGNS ITS BENCH, in two rows that are one sentence
and one name:

    Panel integrado por su presidenta, la juez Brignoni Mártir, el juez
    Salgado Schwarz y la juez Aldebol Mora.          41/42   -> panel
    Aldebol Mora, Juez Ponente                      38/42   -> author

THE ROSTER WRAPS, AND ITS WRAPS LOOK LIKE NOTHING ELSE. 51 rows in the
corpus are continuations of that sentence, and read as rows in their own
right they are unidentifiable — 'Adorno.', 'y la Jueza Prats Palerm.',
'Cordero.'. They belong to the roster that opened above them, so a row that
follows a panel row and is not the paper's title continues it. One record
also prints an administrative-order footnote there ('Mediante Orden
Administrativa OATA-2026-063 … se designó al Hon. Juan A. Robles Adorno en
sustitución de …'), which is the court explaining its own composition: the
same fact, the same role.

WHERE THE READER STOPS. At the paper naming itself — 'SENTENCIA' on 33
records, 'RESOLUCIÓN' on 8, some of them letter-spaced ('S E N T E N C I A',
and 'S E N T E N C IA' on two). That row is LEFT IN THE STREAM: it is the
doc-type heading an unsigned writing opens on, and claiming it would leave
the judgment with nothing to begin at.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider

STYLE_COVER = "boxed Spanish cover"

# ---- prapp's declared facts (measured over all 42 records) ---------------
_SHEET = (612.0, 1008.0)
_SHEET_TOL = 8.0
# THE DISPATCH: the court naming itself in the box's head, on all 42.
# THE HEAD OF THE BOX names the court in up to four rows, and the corpus
# prints each of them more than one way: 'TRIBUNAL DE APELACIONES' (41) and
# 'EN EL TRIBUNAL DE APELACIONES' (1); the Commonwealth in capitals (19) and
# in caps-and-lower (23); and 2 records name the whole judicial branch
# ('TRIBUNAL GENERAL DE JUSTICIA') above the court itself. All of it is the
# court naming itself, and a reader that admitted only the commonest form
# refused 3 records outright.
_COURT = re.compile(r"^(?:EN\s+EL\s+)?TRIBUNAL\s+DE\s+APELACIONES$", re.I)
_STATE = re.compile(r"^(?:ESTADO\s+LIBRE\s+ASOCIADO\s+DE\s+PUERTO\s+RICO"
                    r"|TRIBUNAL\s+GENERAL\s+DE\s+JUSTICIA)$", re.I)
# WHICH PANEL SAT. 'PANEL IX', 'PANEL ESPECIAL', and — where the text layer
# breaks — 'PANEL ES PECIAL' and 'A NEL ESPECIAL', the second having lost the
# P that would open it.
_PANEL_ID = re.compile(r"^(?:P\s?A\s?N\s?EL|A\s?NEL)\b", re.I)
# THE CAPTION'S DIVIDERS: vertical rules that span the band and nothing
# else. A doubled stroke 1pt from its twin is the same divider.
_DIV_MIN_H = 40.0
_DIV_BAND = (0.3, 0.8)
_DIV_SAME = 2.0
# THE BENCH, below the band.
_ROSTER = re.compile(r"^Panel\s+", re.I)
_PONENTE = re.compile(r"Ponente", re.I)
_ADMIN = re.compile(r"^\d?\s*Mediante\s+Orden\s+Administrativa\b", re.I)
# THE PAPER NAMING ITSELF — the reader's stop. Letter-spaced on 7 records,
# so every internal space is optional.
_TITLE = re.compile(r"^(?:S\s?E\s?N\s?T\s?E\s?N\s?C\s?I\s?A"
                    r"|R\s?E\s?S\s?O\s?L\s?U\s?C\s?I\s?[ÓO]\s?N"
                    r"|O\s?P\s?I\s?N\s?I\s?[ÓO]\s?N)\.?$", re.I)
# THE RIGHT-HAND CELLS, each naming the fact it carries.
# THIS COURT'S OWN DOCKET, in both forms the corpus prints: the current
# 'TA2026AP00409' and the older 'KLAN201700365' — one of which is set with a
# space inside it ('KLAN20 2401032'), so the number is matched in parts.
_THIS_DOCKET = re.compile(r"^[A-Z]{2,4}\s?\d{2,4}\s?[A-Z]{0,2}\s?\d{3,8}$")
_LOWER_DOCKET = re.compile(r"^Caso\s+n[úu]mero:?\s*(?P<v>.*)$", re.I)
_ORIGIN = re.compile(r"^(?:APELACI[ÓO]N|CERTIORARI|REVISI[ÓO]N"
                     r"|MANDAMUS|H[ÁA]BEAS)\b", re.I)
_SUBJECT = re.compile(r"^Sobre:?\s*(?P<v>.*)$", re.I)
# A PARTY'S STATUS, as this court labels it.
_STATUS = re.compile(r"^(?:Apelantes?|Apelad[oa]s?|Peticionari[oa]s?"
                     r"|Recurrid[oa]s?|Demandant[e]s?|Demandad[oa]s?"
                     r"|Promovent[e]s?|Promovid[oa]s?|Interventor[ae]s?"
                     r"|Querellant[e]s?|Querellad[oa]s?)\b", re.I)
_PIVOT = re.compile(r"^v\.?$", re.I)


@decider("headmatter.read", court="prapp")
def read_headmatter_prapp(model, geom, **_):
    """Read the boxed Spanish cover on page 1, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    if (abs(pm.width - _SHEET[0]) > _SHEET_TOL
            or abs(pm.height - _SHEET[1]) > _SHEET_TOL):
        return NOTHING
    divs = _dividers(pm)
    if not divs:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 102.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(pm, finder)
    if len(rows) < 6:
        return NOTHING
    band_top = min(v.top for v in divs)
    band_bot = max(v.bottom for v in divs)
    head = [g for g in rows if g[0].bottom <= band_top]
    band = [g for g in rows if band_top < g[0].top < band_bot]
    tail = [g for g in rows if g[0].top >= band_bot]
    if not (head and band and tail):
        return NOTHING
    if not any(_COURT.match(_norm(_text(g))) for g in head):
        return NOTHING

    ctx = _Ctx()
    # ---- the box's head: the court, and which panel sat -----------------
    for group in head:
        text = _norm(_text(group))
        if _PANEL_ID.match(text):
            ctx.emit(group, "panel")
            ctx.crit.setdefault("panel_line", text)
        elif _COURT.match(text) or _STATE.match(text):
            ctx.emit(group, "court")
            if _COURT.match(text):
                ctx.crit["court"] = text
        else:
            return NOTHING      # something stands in the box's head

    # ---- the caption band: three columns, two stacks -------------------
    if not _caption(ctx, pm, band, divs):
        return NOTHING

    # ---- below the band: the bench, down to the paper's own title -------
    roster: list[str] = []
    for group in tail:
        text = _norm(_text(group))
        if _TITLE.match(text):
            break               # left in the stream: core opens on it
        if _PONENTE.search(text):
            # WHO WROTE IT. 'Aldebol Mora, Juez Ponente' — the court names
            # its writer here and nowhere else on the cover.
            ctx.emit(group, "author", centre=False)
            ctx.crit.setdefault("judges", _norm(
                re.sub(r",?\s*Juez[a]?\s+Ponente\.?$", "", text, flags=re.I)))
            continue
        if _ROSTER.match(text) or _ADMIN.match(text) or roster:
            # The roster, and every row that continues it — see the module
            # docstring on the 51 wrap rows.
            ctx.emit(group, "panel", centre=False)
            roster.append(text)
            continue
        return NOTHING          # no catch-all inside the block
    if roster:
        ctx.crit["panel_line"] = _norm(" ".join(roster))
    ctx.crit["headmatter_style"] = STYLE_COVER
    return ctx.result()


def _dividers(pm) -> list:
    """The caption's own vertical rules, doubled strokes collapsed."""
    lo, hi = _DIV_BAND
    mids = sorted((v for v in pm.v_rules
                   if v.height >= _DIV_MIN_H
                   and pm.width * lo < v.x < pm.width * hi),
                  key=lambda v: v.x)
    out: list = []
    for v in mids:
        if out and abs(v.x - out[-1].x) <= _DIV_SAME:
            continue            # the same divider, drawn twice
        out.append(v)
    return out


def _caption(ctx, pm, band: list, divs: list) -> bool:
    """The band's rows, split at the FIRST drawn divider: the parties on the
    left, everything the form stacks beside them on the right."""
    cut = divs[0].x
    left: list = []
    right: list = []
    cap_rows: list[str] = []
    for group in band:
        l_cells = [l for l in group if l.x0 < cut]
        r_cells = [l for l in group if l.x0 >= cut]
        left.append(_cells(l_cells, "caption") if l_cells else _blank(pm))
        right.append(_cells(r_cells, _right_role(r_cells)) if r_cells
                     else _blank(pm))
        cap_rows.extend(_norm(c.plain) for c in l_cells)
        for cell in r_cells:
            _right_cell(ctx, _norm(cell.plain))
        ctx.consumed.update(l.id for l in group)
    if not cap_rows:
        return False
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=None,
        prov=m.Prov(pm.number, tuple(l.id for g in band for l in g))))
    ctx.crit["caption"] = cap_rows
    names = [r.rstrip(",") for r in cap_rows
             if r and not (_STATUS.match(r) or _PIVOT.match(r))]
    if names:
        ctx.crit["parties"] = names
        if len(names) >= 2:
            ctx.crit["case_name"] = f"{names[0]} v. {names[1]}"
    return True


def _right_role(cells: list) -> str:
    """What the second and third columns are saying on this row. The docket
    column holds one thing; the origin column opens on the writ, names the
    court below, then its case number, then the subject — a runover row keeps
    company with `lower-court`, which is what that column carries whenever it
    is naming neither a number nor the subject."""
    text = _norm(" ".join(c.plain for c in cells))
    if not text:
        return "caption"
    if _PANEL_ID.match(text):
        return "panel"
    if _THIS_DOCKET.match(text):
        return "docket"
    if _LOWER_DOCKET.match(text):
        return "case-info"
    if _SUBJECT.match(text):
        return "case-info"
    return "lower-court"


def _right_cell(ctx, text: str) -> None:
    """One cell of the caption's right-hand columns, read for what it names.
    Cells that only continue the sentence above them add nothing here — the
    rendered stack already prints them where the page does."""
    if _PANEL_ID.match(text):
        # THE PANEL ROW CAN FALL IN THE MIDDLE COLUMN. It sits at the very
        # top of the band on 9 records, inside the divider rather than above
        # it, and read as a docket it would have become one.
        ctx.crit.setdefault("panel_line", text)
        return
    if _THIS_DOCKET.match(text):
        if ctx.crit.get("docket_number"):
            ctx.crit.setdefault("other_dockets", []).append(text)
        else:
            ctx.crit["docket_number"] = text
        return
    lower = _LOWER_DOCKET.match(text)
    if lower and lower.group("v"):
        ctx.crit.setdefault("lower_court_docket", []).append(
            _norm(lower.group("v")))
        return
    if _ORIGIN.match(text):
        # 'APELACIÓN' / 'CERTIORARI' opens the origin sentence, which then
        # names the tribunal below over the next few cells. The opening word
        # is the fact worth recording — the rendered stack already prints the
        # sentence where the page sets it.
        ctx.crit.setdefault("lower_court", text)
    elif _SUBJECT.match(text):
        # 'Sobre: Nulidad de Testamento y …' — the subject, which `Criteria`
        # has no field for. Rendered and tinted, recorded nowhere, for the
        # same reason prsupreme's `Materia` is not filed under `history`.
        return


def _cells(cells: list, role: str) -> m.HmLine:
    parts = sorted(cells, key=lambda l: l.x0)
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    first = parts[0]
    return m.HmLine(
        text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
        align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _blank(pm, role: str = "caption") -> m.HmLine:
    """EVERY CELL CARRIES A ROLE, blanks included — an untagged row is one
    nothing read, and the two-column ports written before this one (ca6, pa,
    va, mdctspecapp) tag 100% of their block."""
    return m.HmLine(text="", prov=m.Prov(pm.number), role=role)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _text(group: list) -> str:
    return " ".join(l.plain for l in sorted(group, key=lambda l: l.x0))


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
