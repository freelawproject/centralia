"""Supreme Court of Minnesota ('minn').

Everything unique to minn lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — Minnesota sets ONE type size and separates its bands with
TYPED RULES. The whole paper is 13pt: masthead, caption, counsel, syllabus
and opinion alike, so the type says nothing here. What the court does
instead is print a row of underscores between bands, and set three things
out in a right-hand column.

    ┌────────────────────────────────────────────────────────────────────┐
    │                     STATE OF MINNESOTA          the masthead pair  │
    │                     IN SUPREME COURT                               │
    │                        A24-1702                 the docket         │
    │ Carver County                       Moore, III, J.   below | author│
    │ Adrian Dominic Riley,                                              │
    │            Appellant,                           the caption        │
    │ vs.                                                                │
    │ State of Minnesota,        Filed: October 22, 2025                 │
    │                            Office of Appellate Courts              │
    │        Respondent.                                                 │
    │              ________________________           a TYPED rule       │
    │ Adrian Dominic Riley …, for appellant.          the appearances    │
    │ Keith Ellison, Attorney General, …, for respondent.                │
    │              ________________________           a TYPED rule       │
    │                    S Y L L A B U S              letterspaced       │
    │ 1.  The district court erred in concluding …     the syllabus      │
    └────────────────────────────────────────────────────────────────────┘

THE RIGHT-HAND COLUMN IS A COLUMN, not a caption. Three different things
stand out there and each is read by its own landmark, never by position:
the AUTHOR ('Moore, III, J.' / 'Per Curiam' — Minnesota announces its
author in the block rather than signing), the release ('Filed: …'), and the
clerk's office ('Office of Appellate Courts'). The left column beside them
carries the county the case came from, or 'Original Jurisdiction'.

THE SYLLABUS IS THE COURT'S OWN. Minnesota prints numbered points of law
under a letterspaced 'S Y L L A B U S' heading — the same thing Kansas
prints, and it takes the same role. It is NOT `headnotes`: headnotes are the
Reporter's subject list, and the Reporter does not write these.

A HEADING THAT NAMES A SECTION belongs to that section, so 'S Y L L A B U S'
is read as `syllabus` and not as `title` — `title` is what the paper calls
itself.

THE TYPED RULES ARE NOT COUNTED. A record with a dissent prints a further
pair, and one with no syllabus prints only one; both read, because the walk
is driven by the landmark each row carries and the rules are only rendered
where the page draws them.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

_MASTHEAD = "state of minnesota"
_COURT_ROW = re.compile(r"^IN (?:SUPREME COURT|COURT OF APPEALS)$", re.I)
_AXIS_TOL = 8.0
_MAX_PAGES = 3

# 'A24-1702' / 'A24-1702, A24-1703'
_DOCKET = re.compile(r"^A\d{2}-\d{3,4}(?:\s*,\s*A\d{2}-\d{3,4})*$")
# A TYPED RULE: the court draws its band edges with underscores.
_TYPED_RULE = re.compile(r"^_{6,}$")
_SYLLABUS_HEAD = re.compile(r"^S\s*Y\s*L\s*L\s*A\s*B\s*U\s*S$", re.I)
_OPINION_HEAD = re.compile(r"^O\s*P\s*I\s*N\s*I\s*O\s*N$", re.I)
# The right-hand column's three tenants, each by its own landmark.
_FILED = re.compile(r"^(?:Filed|Refiled|Amended):", re.I)
_CLERK = re.compile(r"^Office of Appellate Courts$", re.I)
# THE FOURTH TENANT OF THE RIGHT COLUMN: the justice who did not sit. Measured
# on 13 of the 50 records, at x0 406.1 beside the author and the filed date
# ('Took no part, Hennesy, J.', 'Took no part, Gaïtas, J.', 'Took no part,
# Hudson, C.J.'). Unclaimed it is not merely untagged — core opened a WRITING
# on it, so alvin_glay_trustee_for_the_next_of_kin_of_unity_mcgill rendered a
# one-block 'majority' whose whole body was that line, standing ahead of the
# real opinion. It is `panel`: it names the bench, by saying who is absent
# from it.
_RECUSED = re.compile(
    r"^(?:Took no part|Did not participate|Took no part in the consideration"
    r"|Recused)\b", re.I)
_AUTHOR = re.compile(
    r"^(?:Per Curiam|[A-Z][A-Za-z'’\-]+(?:,\s*(?:III|Jr\.|Sr\.|II))?"
    r",\s*(?:C\.\s*J\.|J\.))$")
# The left column beside them.
_ORIGIN = re.compile(
    r"^(?:.*\bCounty\b.*|Original Jurisdiction|Court of Appeals"
    r"|Workers'? Compensation Court of Appeals|Tax Court"
    r"|Office of Lawyers Professional Responsibility)$", re.I)
# The caption's own furniture.
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PARTY_ROLE = re.compile(
    r"^(?:Appellant|Appellee|Respondent|Petitioner|Relator|Cross-Appellant"
    r"|Cross-Respondent|Plaintiff|Defendant|Intervenor)s?[,.]?$", re.I)
# The appearances name themselves in their last words.
_COUNSEL = re.compile(
    r"for (?:appellant|appellee|respondent|petitioner|relator|amicus"
    r"|plaintiff|defendant|intervenor)", re.I)
_PRO_SE = re.compile(r"\bpro se\b", re.I)
_SYL_NUM = re.compile(r"^\d+\.$")
_RIGHT_COL_MIN = 0.48          # of the measure


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`, which the render labels 'argued/submitted'.
# Written under the wrong names they were attached to the object by setattr
# and never serialized — read as read, reported as nothing.


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="minn")
def read_headmatter_minn(model, geom, **_):
    """Read Minnesota's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE BLOCK IS NOT ONE PAGE. Minnesota's syllabus is numbered and runs
    # as long as it needs to: `adrian_dominic_riley` sets point 1 on page 1
    # and point 2 with its 'Affirmed.' on page 2, and reading page 1 alone
    # left point 2 in the stream, where core opened a PHANTOM WRITING on it
    # ('2. Although the district court erred…' / 'Affirmed.') ahead of the
    # real opinion. The walk spans pages and stops where the paper names
    # itself, at the centred 'O P I N I O N'.
    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 5:
        return NOTHING
    # THE DISPATCH: the masthead pair, centred, at the head of the page.
    head = [_norm(" ".join(l.plain for l in g)) for g in rows[:2]]
    if len(head) < 2 or head[0].lower() != _MASTHEAD \
            or not _COURT_ROW.match(head[1]):
        return NOTHING

    ctx = _Ctx()
    band = "caption"          # caption | counsel | syllabus
    caption: list[str] = []
    for group in rows:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        first = pieces[0]
        centred = abs((first.x0 + max(l.x1 for l in pieces)) / 2
                      - page1.width / 2) <= _AXIS_TOL

        if _TYPED_RULE.match(text):
            ctx.rule(first.page, tuple(p.id for p in pieces), typed=True)
            continue
        if text.lower() == _MASTHEAD or _COURT_ROW.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _DOCKET.match(text):
            _dk = [t.strip() for t in text.split(",") if t.strip()]
            ctx.crit.setdefault("docket_number", _dk[0])
            if _dk[1:]:
                ctx.crit.setdefault("other_dockets", _dk[1:])
            ctx.emit(pieces, "docket")
            continue
        if _SYLLABUS_HEAD.match(text):
            band = "syllabus"
            ctx.emit(pieces, "syllabus")
            continue
        if _OPINION_HEAD.match(text):
            # THE PAPER NAMES ITSELF, and that row ends the block: what
            # follows it is the writing.
            ctx.emit(pieces, "title")
            break
        if band == "syllabus":
            # 'Affirmed.' / 'Reversed and remanded.' closes the syllabus —
            # it is the syllabus's own last line, printed on its indent.
            ctx.emit(pieces, "syllabus", centre=False)
            continue

        # A ROW SET IN TWO COLUMNS is read one piece at a time — the page
        # put 'State of Minnesota,' and 'Filed: October 22, 2025' on one
        # line and they are not one element.
        placed = False
        for piece in pieces:
            one = _norm(piece.plain)
            if not one:
                continue
            right = piece.x0 >= page1.width * _RIGHT_COL_MIN
            if right and _FILED.match(one):
                ctx.crit.setdefault("decision_date", one.split(":", 1)[1].strip())
                ctx.emit([piece], "date", centre=False)
                placed = True
                continue
            if right and _CLERK.match(one):
                ctx.emit([piece], "case-info", centre=False)
                placed = True
                continue
            if right and _RECUSED.match(one):
                ctx.emit([piece], "panel", centre=False)
                placed = True
                continue
            if right and _AUTHOR.match(one):
                ctx.crit.setdefault("author_line", one)
                ctx.emit([piece], "author", centre=False)
                placed = True
                continue
            if not right and _ORIGIN.match(one) and band == "caption" \
                    and not caption:
                ctx.crit.setdefault("lower_court", one)
                ctx.emit([piece], "lower-court", centre=False)
                placed = True
                continue
            if _COUNSEL.search(one) or _PRO_SE.search(one) or band == "counsel":
                band = "counsel"
                ctx.emit([piece], "counsel", centre=False)
                placed = True
                continue
            if band == "caption" and (_PIVOT.match(one) or _PARTY_ROLE.match(one)
                                      or not right):
                if not _PIVOT.match(one) and not _PARTY_ROLE.match(one):
                    caption.append(one)
                ctx.emit([piece], "caption", centre=(centred and len(pieces) == 1))
                placed = True
                continue
        if not placed:
            # A ROW THIS PAPER DOES NOT PRINT is left to core rather than
            # tinted with a role that would be a guess.
            continue

    if not ctx.crit.get("docket_number"):
        return NOTHING
    if caption:
        ctx.crit.setdefault("parties", caption[:6])
    return ctx.result()


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

    def rule(self, page: int, ids: tuple = (), typed: bool = False) -> None:
        self.items.append(m.Rule(prov=m.Prov(page, ids), typed=typed,
                                 span="center" if typed else "full"))
        self.consumed.update(ids)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
