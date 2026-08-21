"""Tribunal Supremo de Puerto Rico ('prsupreme').

Everything unique to prsupreme lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py; this module adds the reader only, so
importing it can never raise a duplicate profile.

THE CONTRACT — a Spanish-language cover on a LEGAL sheet (612 x 1008 on all
31 records; nothing here may be measured against a letter page), fenced by
TWO DRAWN RULES that divide it into three bands, and every record in the
corpus draws exactly two:

    ┌─ page 1, 612 x 1008 ────────────────────────────────────────────┐
    │             EN EL TRIBUNAL SUPREMO DE PUERTO RICO      the COURT │
    │ ─────────────────────────────────────────────────────  rule 1    │
    │  El Pueblo de Puerto Rico                                       │
    │             Recurrido              2026 TSPR 39       THE CAPTION│
    │                 v.                 218 DPR ___        two columns│
    │  Davis Ponce Feliciano                                          │
    │            Peticionario                                         │
    │ ─────────────────────────────────────────────────────  rule 2    │
    │ Número del Caso:  CC-2025-0573                        the DOCKET │
    │ Fecha:  16 de abril de 2026                           the DATE   │
    │ Tribunal de Apelaciones: Panel VIII                   the ORIGIN │
    │ Representante legal de la parte peticionaria:         ┐          │
    │      Sociedad para Asistencia Legal                   │ COUNSEL  │
    │      Lcda. Celimar Gracia Marín                       ┘          │
    │ Oficina del Procurador General:                       ┐ COUNSEL  │
    │      Hon. Omar Andino Figueroa / Procurador General   ┘          │
    │ Materia: Procedimiento Criminal – No procede la …     the SUBJECT│
    │ Este documento está sujeto a los cambios y correcciones … NOTICE │
    └─────────────────────────────────────────────────────────────────┘

THE RULES ARE THE STRUCTURE. Above the first: the court naming itself, on
all 31. Between them: the caption, set in two columns over an undrawn
gutter — the parties on the left, the court's own citations on the right.
Below the second: a list of LABELLED FIELDS, each label at the body rail
with its value beside it or indented underneath.

A FIELD IS ITS LABEL PLUS EVERYTHING UNTIL THE NEXT LABEL, and that is the
whole reading of the third band. Nothing is keyed to a row ordinal, because
the values wrap and the wraps sit at BOTH indents: counsel's names are
indented 40pt under their office, while `Materia`'s sentence wraps back to
the rail, which is exactly where a label would be. Only the label
vocabulary tells them apart:

    Número del Caso            31/31   ->  docket
    Fecha                      31/31   ->  date
    Materia                    30/31   ->  the subject, as headnotes
    Tribunal de Apelaciones    17/31   ->  the court below
    Representante(s) legal(es) / Abogad[oa] / Oficina / Registradora
                                       ->  counsel, whoever appeared

THE APPEARANCE LABELS ARE NOT ONE PHRASE. The corpus prints eleven forms of
them, agreeing in gender and number with the party they act for
('Representante legal de la parte peticionaria', 'Representantes legales de
la parte recurrida', 'Representante legal del promovido', 'Abogada de la
parte recurrida'), and two offices that appear in their own name ('Oficina
del Procurador General', 'Oficina de Inspección de Notarías'), and one
official ('Registradora de la Propiedad'). The pattern matches the OPENING
NOUN and lets the agreement fall where it will; spelled out as a list, the
next inflection the court prints would fall through to no field at all.

TWO CITATIONS, ONE RECORDED. The right column carries the court's own
public-domain cite ('2026 TSPR 39') over the bound-volume placeholder ('218
DPR ___'). The placeholder is printed on all 31 and assigned on none, and a
blank is not a cite — so `citation` takes the TSPR form and the DPR row is
rendered where the page prints it and recorded nowhere.

WHAT THIS READER DOES NOT TOUCH. The closing notice ('Este documento está
sujeto a los cambios y correcciones del proceso de compilación y publicación
oficial …') is the court's distribution disclaimer, not its words on the
case: `Dropped(kind="notice")`. Everything from page 2 on — the opinion, its
byline, its footnotes — is core's.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider

STYLE_COVER = "ruled Spanish cover"

# ---- prsupreme's declared facts (measured over all 31 records) -----------
# THE SHEET: legal, on all 31. A letter-sized filing is not this cover.
_SHEET = (612.0, 1008.0)
_SHEET_TOL = 8.0
# THE DISPATCH: the court naming itself above the first rule, on all 31.
_MASTHEAD = re.compile(r"^EN\s+EL\s+TRIBUNAL\s+SUPREMO\s+DE\s+PUERTO\s+RICO$",
                       re.I)
# THE FENCE: two drawn rules, full measure at the rail, on all 31 records
# and never a third.
_RULES = 2
# WHERE THE CAPTION'S GUTTER FALLS. The right column opens at 388-408pt on a
# 612pt sheet and the left never reaches 340. A share of the sheet, not a
# fixed rail.
_GUTTER = 0.55
# THE COURT'S OWN CITE, and the bound-volume placeholder beside it.
_TSPR = re.compile(r"^\d{4}\s+TSPR\s+\d+$", re.I)
# THE LABELLED FIELDS of the third band. Four structural ones, named; the
# appearances matched by their opening noun — see the module docstring.
_F_DOCKET = re.compile(r"^N[úu]mero\s+del\s+Caso:\s*(?P<v>.*)$", re.I)
_F_DATE = re.compile(r"^Fecha:\s*(?P<v>.*)$", re.I)
_F_ORIGIN = re.compile(r"^Tribunal\s+de\s+Apelaciones:\s*(?P<v>.*)$", re.I)
_F_SUBJECT = re.compile(r"^Materia:\s*(?P<v>.*)$", re.I)
_F_COUNSEL = re.compile(r"^(?:Representantes?\s+legal(?:es)?|Abogad[oa]s?"
                        r"|Oficina|Registrador[ao]|Procurador[ao]?)\b"
                        r"[^:]{0,60}:\s*(?P<v>.*)$", re.I)
# THE CLOSING NOTICE, by its opening words.
_NOTICE = re.compile(r"^Este\s+documento\s+est[áa]\s+sujeto\b", re.I)
# A PARTY'S STATUS, as this court labels it — the row that closes a party's
# name rather than naming another party.
_STATUS = re.compile(r"^(?:Peticionari[oa]s?|Recurrid[oa]s?|Promovid[oa]s?"
                     r"|Querellad[oa]s?|Demandant[e]s?|Demandad[oa]s?"
                     r"|Apelant[e]s?|Apelad[oa]s?|Interventor[ae]s?"
                     r"|Solicitante|Notari[oa])\b", re.I)
_PIVOT = re.compile(r"^v\.?$", re.I)


@decider("headmatter.read", court="prsupreme")
def read_headmatter_prsupreme(model, geom, **_):
    """Read the ruled Spanish cover on page 1, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    if (abs(pm.width - _SHEET[0]) > _SHEET_TOL
            or abs(pm.height - _SHEET[1]) > _SHEET_TOL):
        return NOTHING
    if len(pm.h_rules) != _RULES:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 68.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = _rows(pm, finder)
    if len(rows) < 6:
        return NOTHING
    top, bottom = sorted(r.top for r in pm.h_rules)
    head = [g for g in rows if g[0].top < top]
    band = [g for g in rows if top < g[0].top < bottom]
    tail = [g for g in rows if g[0].top > bottom]
    if not (head and band and tail):
        return NOTHING
    if not any(_MASTHEAD.match(_norm(_text(g))) for g in head):
        return NOTHING

    ctx = _Ctx()
    # ---- above the first rule: the court naming itself -------------------
    for group in head:
        text = _norm(_text(group))
        if not _MASTHEAD.match(text):
            return NOTHING      # something stands above the caption
        ctx.emit(group, "court")
        ctx.crit["court"] = text

    # ---- between the rules: the caption, in two columns -----------------
    mid = pm.width * _GUTTER
    left: list = []
    right: list = []
    cap_rows: list[str] = []
    for group in band:
        l_cells = [l for l in group if l.x0 < mid]
        r_cells = [l for l in group if l.x0 >= mid]
        left.append(_cells(l_cells, "caption") if l_cells else _blank(pm))
        # THE RIGHT COLUMN CARRIES NOTHING BUT CITATIONS on all 31 records —
        # the court's own TSPR cite over the DPR volume placeholder.
        right.append(_cells(r_cells, "citation") if r_cells else _blank(pm))
        cap_rows.extend(_norm(c.plain) for c in l_cells)
        for cell in r_cells:
            if _TSPR.match(_norm(cell.plain)):
                ctx.crit.setdefault("citation", _norm(cell.plain))
        ctx.consumed.update(l.id for l in group)
    if not cap_rows:
        return NOTHING
    ctx.items.append(m.CaptionBlock(
        left=left, right=right, rail=None,
        prov=m.Prov(pm.number, tuple(l.id for g in band for l in g))))

    # ---- below the second rule: the labelled fields ---------------------
    if not _fields(ctx, tail):
        return NOTHING

    ctx.crit["caption"] = cap_rows
    _parties(ctx, cap_rows)
    ctx.crit["headmatter_style"] = STYLE_COVER
    return ctx.result()


def _fields(ctx, tail: list) -> bool:
    """The third band: each label opens a field that owns every row until the
    next label. Returns False where a row belongs to no field — a hole in the
    claim is worse than handing the record back."""
    role = None
    value: list[str] = []
    counsel: list[str] = []
    seen = set()

    def close():
        if role is None:
            return
        text = _norm(" ".join(value))
        if role == "docket" and text:
            ctx.crit.setdefault("docket_number", text)
        elif role == "date" and text:
            ctx.crit.setdefault("decision_date", text)
        elif role == "lower-court" and text:
            ctx.crit.setdefault("lower_court", text)
        # `Materia` IS RENDERED AND TAGGED, AND RECORDED NOWHERE. It is the
        # Reporter's subject line plus the holding it summarises, and
        # `Criteria` has no field for that: filed under `history` it would
        # claim the case's PRIOR HISTORY, which is a different fact and a
        # wrong one. The tagged row on the page is the fact.

        elif role == "counsel" and text:
            counsel.append(text)

    for group in tail:
        text = _norm(_text(group))
        opened = None
        for pattern, name in ((_F_DOCKET, "docket"), (_F_DATE, "date"),
                              (_F_ORIGIN, "lower-court"),
                              (_F_SUBJECT, "headnotes"),
                              (_F_COUNSEL, "counsel")):
            hit = pattern.match(text)
            if hit:
                opened = (name, hit.group("v"))
                break
        if _NOTICE.match(text):
            close()
            role, value = None, []
            ctx.drop(group, "notice")
            continue
        if opened:
            close()
            role, value = opened[0], [opened[1]]
            seen.add(role)
            ctx.emit(group, role, centre=False)
            continue
        if role is None:
            # A row before any label, or after the notice opened: on this
            # cover the notice is last, so this is the notice WRAPPING.
            if ctx.dropped and ctx.dropped[-1].kind == "notice":
                ctx.drop(group, "notice")
                continue
            return False
        value.append(text)
        ctx.emit(group, role, centre=False)
    close()
    if not {"docket", "date"} <= seen:
        return False
    if counsel:
        ctx.crit["attorneys"] = " ".join(counsel)
    return True


def _parties(ctx, cap_rows: list[str]) -> None:
    """The caption's party names: the left column's rows that are neither a
    status label nor the pivot. 'Ex Parte:' and 'In re:' captions name one
    party and no pivot, and nothing is invented from them."""
    names = [r.rstrip(",") for r in cap_rows
             if r and not (_STATUS.match(r) or _PIVOT.match(r))]
    if not names:
        return
    ctx.crit["parties"] = names
    if len(names) >= 2:
        ctx.crit["case_name"] = f"{names[0]} v. {names[1]}"


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
