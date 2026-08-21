"""Merit Systems Protection Board ('mspb').

NOT A COURT. The Board is the appellate tribunal of the federal civil
service: an employee ('the appellant') appeals a personnel action to a
regional office, an administrative judge issues an INITIAL DECISION, and the
Board decides the petition for review of it. So the caption is
appellant-against-employing-agency, the bench is the Board's confirmed
members, and the paper is an ORDER — the Board reserves 'Opinion and Order'
for its precedential decisions, and says so in the footnote it prints on
every cover of this corpus.

ONE PAPER, PRINTED THE SAME WAY 32 TIMES OUT OF 32:

    ┌──────────────────────────────────────────────────────────────────┐
    │              UNITED STATES OF AMERICA                            │  the banner,
    │            MERIT SYSTEMS PROTECTION BOARD                        │  two bold rows
    │                                                                  │
    │  BINTA CONTEH,                    DOCKET NUMBER                  │  the CAPTION,
    │            Appellant,             DA-0432-25-0030-I-1            │  two columns
    │        v.                                                        │  over a
    │  DEPARTMENT OF THE TREASURY,      DATE:  August 6, 2026          │  whitespace
    │            Agency.                                               │  gutter
    │                                                                  │
    │        THIS FINAL ORDER IS NONPRECEDENTIAL¹                      │  publication
    │                                                                  │
    │    Binta Conteh , Houston, Texas, pro se.                        │  the
    │    Jason C. Green , Esquire, and Bridgette M. Gibson , Esquire,  │  APPEARANCES
    │      Dallas, Texas, for the agency.                              │
    │                                                                  │
    │                      BEFORE                                      │  the bench
    │            Henry J. Kerner, Vice Chairman                        │
    │            James J. Woodruff II, Member                          │
    │                                                                  │
    │                   FINAL ORDER                                    │  ← the reader
    │  The appellant has filed a petition for review …                 │    STOPS here
    └──────────────────────────────────────────────────────────────────┘

THE LANDMARK IS THE BANNER, not any title: 'UNITED STATES OF AMERICA' over
'MERIT SYSTEMS PROTECTION BOARD', both bold and centred on the page axis, the
first two inked rows of page 1 in all 32 records. No banner, no claim.

THE CAPTION IS TWO COLUMNS OVER A WHITESPACE GUTTER, and both columns are
read by POSITION. Measured over all 32 covers, the left column sets its rows
at exactly four offsets from the caption's OWN rail — and at no fifth:

      +0.0pt   64 rows   a party NAME opens here
     +18.0pt   14 rows   …and WRAPS here ('DEPARTMENT OF VETERANS ' /
                          'AFFAIRS,')
     +72.0pt   32 rows   the PIVOT, 'v.' — one per record
    +108.0pt   64 rows   the STATUS label, 'Appellant,' / 'Agency.'

and the right column sets all 96 of its rows (32 x 3: the label 'DOCKET
NUMBER', the number, and 'DATE:  …') at +252.9pt from that same rail. The
caption's rail is measured INSIDE the caption band and nowhere else: three
records set the caption at x0 77.5 while every other band on the same page
stays at 72.1/108.1, so a rail taken across the headmatter would misread
them by 5.4pt and file every status row as a name.

THE BAND EDGES ARE WHITESPACE. Inside the caption the largest leading is
30.0pt; the stand-off from its last row to whatever follows is never less
than 39.4pt. 35pt separates the two with room to spare, and the same
whitespace is what closes the caption whether the next band is the
publication notice, the appearances, or 'BEFORE'.

THE APPEARANCES HAVE THEIR OWN RAIL, and it is ABSOLUTE, not relative to the
caption's: all 76 entry rows open at x0 108.1 and all 16 runover rows at
122.5, in every record including the three whose caption is shifted. An
entry is one row plus its runovers ('Jason C. Green , Esquire, and Bridgette
M. Gibson , Esquire,' / 'Dallas, Texas, for the agency.'), and the block ends
at the first row outside those two columns — which is 'BEFORE', centred.

THE PUBLICATION FLAG IS A ROW OF ITS OWN, set 16pt bold where the page's
body is 13pt: 'THIS FINAL ORDER IS NONPRECEDENTIAL¹' (20) or 'THIS ORDER IS
NONPRECEDENTIAL¹' (6). Six records print no flag at all — they are the
single-member orders the Board issues when it has no quorum, and they state
their non-precedence in the body instead ('This decision shall not be
considered as precedent by the Board in any other case. 5 C.F.R.
§ 1200.3(e).'). That sentence is body prose and this reader does not go
looking for it: where the cover prints no flag, `publication_status` is left
unset rather than inferred.

THE BENCH IS 'BEFORE' AND THE CENTRED ROWS UNDER IT — 58 of them over the
corpus, one or two per record (Kerner 27, Woodruff 31; a recusal leaves one
member sitting alone and there is then no quorum to disturb the initial
decision). The office is a closed three-word vocabulary — Chairman, Vice
Chairman, Member — and the name is whatever precedes it; no roll of members
is consulted, because the Board's composition changes with the Senate.

THE READER STOPS AT THE TITLE and does not take it. 'FINAL ORDER' (20),
'ORDER' (8), 'REMAND ORDER' (4) is the first bold row below the bench, and
it is where the writing opens: core anchors the Board's order on it, types
the paper from it, and reads the body beneath. Its text is copied into
`criteria.title` — reading a row is not claiming it — and the row itself is
left in the stream.

WHAT THIS FILE DOES NOT DO. The Board signs nothing: there is no judicial
byline anywhere in this corpus, and the paper closes on the clerk's
conformed sign-off ('FOR THE BOARD: / ____ / Gina K. Grippando / Clerk of
the Board / Washington, D.C.'). The profile therefore declares
`style="none"` — the default grammar looks for 'Justice' and would find
nothing, but it would also be a claim this Board never makes. The
NOTICE OF APPEAL RIGHTS the Board prints before that sign-off is CONTENT,
not furniture: it is a section of the order, addressed to the appellant,
carrying its own footnote, and it sits ABOVE the signature rather than after
it. Nothing here touches it.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# --------------------------------------------------------------------------
# the profile
# --------------------------------------------------------------------------
# ONE WRITING PER PAPER. The Board decides as a body; a member who disagrees
# does not sign a dissent in these orders, and nothing in the corpus prints a
# second writing. Declared so a bold section heading inside the order cannot
# be mistaken for the start of one.
register(CourtProfile(
    "mspb", "Merit Systems Protection Board",
    byline=BylineGrammar(style="none"),
    single_writing=True,
    rollout="migrated",
))


# --------------------------------------------------------------------------
# the measured facts of this cover
# --------------------------------------------------------------------------
_BANNER_1 = re.compile(r"^UNITED STATES OF AMERICA$", re.I)
_BANNER_2 = re.compile(r"^MERIT SYSTEMS PROTECTION BOARD$", re.I)
# The four positions the left column of the caption uses, as offsets from the
# caption's own rail, and the one the right column uses. Nothing else appears
# at any other offset in 210 measured caption rows.
_NAME, _WRAP, _PIVOT_X, _STATUS = 0.0, 18.0, 72.0, 108.0
_LEFT_POS = (_NAME, _WRAP, _PIVOT_X, _STATUS)
_RIGHT_POS = 252.9
_POS_TOL = 3.0
# The whitespace band edge: <=30.0pt inside the caption, >=39.4pt out of it.
_CAPTION_STANDOFF = 35.0
# The appearances' own rail and its runover, absolute on the page.
_COUNSEL_X = 108.1
_COUNSEL_RUNOVER = 122.5
_RAIL_TOL = 4.0
# The publication flag is set 16pt against a 13pt body.
_FLAG_SIZE = 15.0
_BEFORE = re.compile(r"^BEFORE\b", re.I)
# The Board's three offices. A closed vocabulary; the names are not.
_OFFICE = re.compile(r",\s*((?:Vice\s+)?Chair(?:man|woman|person)|Member)"
                     r"\s*$", re.I)
_DATE = re.compile(r"^DATE\s*:?\s*(.+)$", re.I)
_DOCKET_LABEL = re.compile(r"^DOCKET\s+NUMBERS?$", re.I)
# 'DA-0432-25-0030-I-1' — office code / case type / year / sequence / stage.
# Two covers mistype the stage letter as a digit ('...-1-1'), which is why
# the tail is not spelled out.
_DOCKET_NO = re.compile(r"^[A-Z]{2}-[A-Z0-9]{3,5}-\d{2}-\d{4}-[A-Z0-9]-\d+$")
_PIVOT = re.compile(r"^v\.?$", re.I)
# The flag carries its footnote mark on the same word — 'NONPRECEDENTIAL1'
# — and a digit is a word character, so a closing \\b matches nothing here.
_NONPRECEDENTIAL = re.compile(r"\bNONPRECEDENTIAL", re.I)
_AXIS_TOL = 26.0


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _flat(text: str) -> str:
    """The row's words with the markup stripped — for reading, never for
    publishing."""
    return _norm(re.sub(r"<[^>]+>", "", text or ""))


def _rows(pm, finder) -> list[tuple[float, list]]:
    """The page's inked rows, furniture removed, grouped by baseline."""
    groups: dict[float, list] = {}
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        groups.setdefault(round(line.top, 1), []).append(line)
    return [(t, sorted(groups[t], key=lambda l: l.x0)) for t in sorted(groups)]


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the gutter, or None. Split
    CHAR BY CHAR: whether pdfio broke the row at its column gap is an
    accident of how wide the gap happened to be (the ca6 reading)."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep, x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _text(parts: list) -> str:
    out = ""
    for part in parts:
        piece = line_markup(part)
        out = (out.rstrip() + " " + piece.lstrip()) if out.strip() else piece
    return out


def _line(parts: list, role: str, align=m.Align.LEFT) -> m.HmLine:
    first = parts[0]
    return m.HmLine(
        text=_text(parts), prov=m.Prov(first.page, tuple(p.id for p in parts)),
        align=align, x0=first.x0, size=first.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def _cell(parts: list, page: int, role: str) -> m.HmLine:
    """One column's cell on one printed row — the empty one keeps its place,
    so the two columns stay in step down the page. A spacer carries the role
    of the band it sits in (the caller passes the last one read in this
    column): a blank cell is not an unread row, and tagging it with the
    column's opening role would say 'docket' under a date."""
    if not parts:
        return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                        role=role)
    return _line(parts, role)


class _Ctx:
    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}

    def emit(self, parts: list, role: str, align=m.Align.LEFT) -> None:
        if not parts:
            return
        self.items.append(_line(parts, role, align))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": self.anchor, "doc_type_final": None}


@decider("headmatter.read", court="mspb")
def read_headmatter_mspb(model, geom, **_):
    """Read the Board's cover — banner, two-column caption, publication flag,
    appearances, bench — or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    axis = pm.width / 2.0
    finder = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                             geom.body_size if geom else 12.0)
    rows = _rows(pm, finder)
    if len(rows) < 6:
        return NOTHING

    # --- the landmark ------------------------------------------------------
    if not (_BANNER_1.match(_norm(" ".join(l.plain for l in rows[0][1])))
            and _BANNER_2.match(_norm(" ".join(l.plain for l in rows[1][1])))):
        return NOTHING

    # --- the bench, and the title below it, locate every other band --------
    bench_i = next((i for i, (_t, g) in enumerate(rows)
                    if _BEFORE.match(_norm(" ".join(l.plain for l in g)))),
                   None)
    if bench_i is None or bench_i < 3:
        return NOTHING
    title_i = next((i for i in range(bench_i + 1, len(rows))
                    if all(l.all_bold for l in rows[i][1])), None)
    if title_i is None:
        return NOTHING

    # --- the caption band: opened by the right column, closed by whitespace
    right_tops = [i for i in range(2, bench_i)
                  if any(l.x0 > axis for l in rows[i][1])]
    if not right_tops:
        return NOTHING
    cap_a, cap_b = right_tops[0], right_tops[-1]
    rail = min(l.x0 for i in range(cap_a, cap_b + 1)
               for l in rows[i][1] if l.x0 < axis)
    while cap_b + 1 < bench_i:
        nxt = rows[cap_b + 1]
        if nxt[0] - rows[cap_b][0] > _CAPTION_STANDOFF:
            break
        if any(l.x0 > axis for l in nxt[1]):
            break
        if not all(any(abs(l.x0 - rail - p) <= _POS_TOL for p in _LEFT_POS)
                   for l in nxt[1]):
            break
        cap_b += 1

    ctx = _Ctx()
    ctx.crit["court"] = _norm(" ".join(l.plain for l in rows[1][1]))
    for _t, g in rows[:2]:
        ctx.emit(g, "court", m.Align.CENTER)

    # --- the caption, column by column, row by printed row -----------------
    left_cells: list[m.HmLine] = []
    right_cells: list[m.HmLine] = []
    cap_ids: set[int] = set()
    parties: list[list[str]] = [[]]
    pivot_seen = False
    caption_rows: list[str] = []
    last_right = "docket"
    for i in range(cap_a, cap_b + 1):
        _t, group = rows[i]
        l_parts, r_parts = [], []
        for line in group:
            for want, bucket in (("L", l_parts), ("R", r_parts)):
                part = _side(line, axis, want)
                if part is not None:
                    bucket.append(part)
        l_parts.sort(key=lambda l: l.x0)
        r_parts.sort(key=lambda l: l.x0)

        # LEFT: which of the four positions is this row at?
        role = "caption"
        if l_parts:
            off = l_parts[0].x0 - rail
            flat = _norm(" ".join(l.plain for l in l_parts))
            caption_rows.append(flat)
            if abs(off - _PIVOT_X) <= _POS_TOL and _PIVOT.match(flat):
                pivot_seen = True
                parties.append([])
            elif abs(off - _STATUS) <= _POS_TOL:
                pass                                    # a status label
            elif abs(off - _WRAP) <= _POS_TOL:
                if parties[-1]:
                    parties[-1].append(flat)
            elif abs(off - _NAME) <= _POS_TOL:
                if parties[-1] and not pivot_seen:
                    parties.append([])
                parties[-1].append(flat)
        # RIGHT: the label, the number, the date.
        r_role = last_right
        if r_parts:
            r_role = "docket"
            flat = _norm(" ".join(l.plain for l in r_parts))
            got = _DATE.match(flat)
            if got:
                r_role = "date"
                ctx.crit.setdefault("decision_date", _norm(got.group(1)))
            elif _DOCKET_NO.match(flat):
                ctx.crit.setdefault("docket_number", flat)
            elif not _DOCKET_LABEL.match(flat):
                r_role = "case-info"
            last_right = r_role
        left_cells.append(_cell(l_parts, pm.number, role))
        right_cells.append(_cell(r_parts, pm.number, r_role))
        cap_ids.update(l.id for l in group)
    ctx.items.append(m.CaptionBlock(
        left=left_cells, right=right_cells, rail=None,
        rail_rows=len(left_cells), style_id="open-gutter", fp={"rail": None},
        prov=m.Prov(pm.number, tuple(sorted(cap_ids)))))
    ctx.consumed.update(cap_ids)
    if caption_rows:
        ctx.crit["caption"] = caption_rows
    named = [_norm(" ".join(p)).rstrip(",; ") for p in parties if p]
    if len(named) >= 2 and pivot_seen:
        ctx.crit["parties"] = named
        ctx.crit["case_name"] = " v. ".join(named)
    elif named:
        ctx.crit["parties"] = named

    # --- the flag, the appearances, the bench ------------------------------
    counsel: list[list] = []
    for i in range(cap_b + 1, bench_i):
        _t, group = rows[i]
        flat = _norm(" ".join(l.plain for l in group))
        size = max((l.size or 0.0) for l in group)
        if size >= _FLAG_SIZE and _NONPRECEDENTIAL.search(flat):
            ctx.crit.setdefault("publication_status", "unpublished")
            centred = abs((group[0].x0 + max(l.x1 for l in group)) / 2
                          - axis) <= _AXIS_TOL
            ctx.emit(group, "publication",
                     m.Align.CENTER if centred else m.Align.LEFT)
            continue
        x0 = group[0].x0
        if abs(x0 - _COUNSEL_RUNOVER) <= _RAIL_TOL and counsel:
            counsel[-1].extend(group)               # a runover of the entry
            continue
        if abs(x0 - _COUNSEL_X) <= _RAIL_TOL:
            counsel.append(list(group))
            continue
        # A ROW AT NO POSITION THIS COVER USES is left to core rather than
        # tinted with a role that would be a guess.
        continue
    entries: list[str] = []
    for parts in counsel:
        parts.sort(key=lambda l: (l.top, l.x0))
        ctx.items.append(_line(parts, "counsel"))
        ctx.consumed.update(p.id for p in parts)
        entries.append(_flat(_text(parts)).replace(" ,", ","))
    if entries:
        ctx.crit["attorneys"] = " ".join(entries)

    ctx.emit(rows[bench_i][1], "panel", m.Align.CENTER)
    bench: list[str] = []
    for i in range(bench_i + 1, title_i):
        group = rows[i][1]
        flat = _norm(" ".join(l.plain for l in group))
        ctx.emit(group, "panel", m.Align.CENTER)
        bench.append(flat)
    if bench:
        ctx.crit["panel_line"] = "; ".join(bench)
        ctx.crit["judges"] = "; ".join(bench)
        ctx.crit["panel"] = [_OFFICE.sub("", b).strip(" ,") for b in bench]

    # THE TITLE IS READ, NOT TAKEN. It is where the writing opens, and core
    # anchors and types the paper on it; copying its text into `title` costs
    # the stream nothing.
    ctx.crit["title"] = _norm(" ".join(l.plain for l in rows[title_i][1]))
    return ctx.result()
