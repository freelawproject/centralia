"""The Supreme Court, State of Wyoming ('wyo').

Everything unique to wyo lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is already
registered in courts/__init__.py — this module only binds the reader.

THE CONTRACT — 'RULED RAIL'. Wyoming stacks four centred identifiers, then
sets the caption in TWO COLUMNS SPLIT BY A DRAWN VERTICAL RULE, then either
a labelled ladder (origin, appearances, bench) or a single ORDER title, and
closes the block with the Reporter's revision notice inside a DOUBLE-RULED
BOX. Measured on aaron_r._maki_v._the_state_of_wyoming (612pt page, 13pt
body, body rail x0=72.0):

    ┌────────────────────────────────────────────────────────────────────┐
    │        THE SUPREME COURT, STATE OF WYOMING     masthead 14pt,      │
    │                                                centre 306.0        │
    │                     2026 WY 32                 the public-domain   │
    │                                                cite, centre 306.0  │
    │                              OCTOBER TERM, A.D. 2025   the term    │
    │                                    March 9, 2026       the date    │
    │                              ───────────────────  DRAWN h_rule     │
    │                                                   top 182.4,       │
    │                                                   x 355.8–540.1    │
    │ AARON R. MAKI,                    │                                │
    │     Appellant                     │  ← DRAWN v_rule x=341.2,       │
    │     (Defendant),                  │    top 197.9 → bottom 362.3    │
    │ v.                                │  S-25-0166   the docket, RIGHT │
    │ THE STATE OF WYOMING,             │              of the rail       │
    │     Appellee                      │                                │
    │     (Plaintiff).                  │                                │
    │                                                                    │
    │       Appeal from the District Court of Campbell County   origin,  │
    │        The Honorable Matthew F.G. Castano, Judge          centred  │
    │                                                                    │
    │ Representing Appellant:                          label at the rail │
    │    Donna D. Domonkos of Domonkos Law Office…     entry at 108.0    │
    │ Representing Appellee:                                             │
    │    Keith G. Kautz, Attorney General; …                             │
    │                                                                    │
    │ Before BOOMGAARDEN, C.J., and GRAY, FENN, JAROSH, and HILL, JJ.    │
    │ ╔════════════════════════════════════════════════════════════════╗ │
    │ ║ NOTICE: This opinion is subject to formal revision before …    ║ │
    │ ╚════════════════════════════════════════════════════════════════╝ │
    └────────────────────────────────────────────────────────────────────┘

THE DIVIDER IS THE PARSER. Every one of the 50 records draws exactly one
vertical rule in the caption band — measured x 296.5–341.8 (296.5, 301.0,
323.0, 340.6, 341.2, 341.8 are the values seen) — and the notice box's own
verticals stand at 60.7/65.2 and 545.4/549.8, outside the text measure, so
the gate `200 < x < 470` takes the rail and nothing else. Which side of that
rule a row sits on decides whether it is a party or the docket; nothing is
inferred from the wording. NO RAIL, NO CLAIM: the reader returns NOTHING.

THE RAIL ALSO BOUNDS THE CAPTION. Its top and bottom are the band; the
origin ladder begins below `rail.bottom`. On the long consolidated captions
the rail runs to the foot of the page and RESUMES on the next
(wyoming_fall_creek: page 1 x=296.5 top 197.9–706.6, page 2 top 72.0–221.5;
nicolette_and_travis_leck: pages 1 and 2, with the appearances finishing on
page 3), so the walk is per page and follows the rail wherever it goes.

A DRAWN RULE INSIDE THE BAND IS A CONSOLIDATION DIVIDER, not a fence:
memorial_hospital draws one at top 428.1 (x 72–531) between its two
appeals, wyoming_fall_creek at 526.7 (x 67–527). The caption is split there
into two blocks with the rule between them, which is what the page shows.

THE NOTICE IS FURNITURE, AND IT IS FOUND BY ITS TYPE. Measured across the
corpus the court sets the block at 12.5–13pt and the notice at 10 or 11pt;
`in_the_interest_of_ag` prints a 12.5pt counsel entry, so the small-type
gate is 12.0. The notice opens 'NOTICE:' and runs to the end of its box.

THE ASTERISK NOTE IS THE APPEARANCES' OWN FOOTNOTE. Four records print an
11pt line explaining a substitution of counsel ('*An Order Substituting
Patricia L. Bennett for Brandon Booth was entered on…'), and its mark is
printed inside a counsel entry ('State Public Defender;*'). It is read as
`counsel` — the block it annotates — wherever the compositor put it, which
on susanne_jacqueline_mayeux is BELOW the bench roster, not above it.

THE ORDERS PRINT A TITLE WHERE THE LADDER WOULD BE. Seven records (the
three Board of Professional Responsibility suspensions and four Anders
affirmances) set a 14–15pt centred heading immediately under the caption
('ORDER OF THREE-YEAR SUSPENSION', 'ORDER AFFIRMING THE DISTRICT COURT'S
JUDGMENT AND SENTENCE' — two rows on jodie_leroy_wood) and no origin, no
appearances, no bench and no notice. That row is `title`: it is what the
paper calls itself. Its line ids go to `anchor_ids` so that core can hand
it back if the claim would otherwise leave the record with no writing.

THE BLOCK ENDS AT THE FIRST BYLINE — 'FENN, Justice.',
'BOOMGAARDEN, Chief Justice.', 'WESTBY, District Judge.' at the body rail —
or at '[¶1]' on the orders, which sign nothing. Measured: the byline stands
on page 2 (37 records), 3 (7), 4 (2, leck) or page 1 (the orders); nothing
the court prints stands between the notice box and it.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# The two papers this contract prints, named for the landmark each carries
# where the other carries nothing.
STYLE_LADDER = "ruled rail, ladder below"
STYLE_ORDER = "ruled rail, order title"

# 'THE SUPREME COURT, STATE OF WYOMING' (24 records, 14pt) and
# 'IN THE SUPREME COURT, STATE OF WYOMING' (26 records, 14 or 16pt).
_MASTHEAD = re.compile(r"^(?:IN\s+)?THE SUPREME COURT,\s*STATE OF WYOMING$",
                       re.I)
# '2026 WY 32' — the court's own public-domain citation, on all 50 records.
_CITE = re.compile(r"^\d{4}\s+WY\s+\d+[A-Z]?$", re.I)
_MONTH = (r"January|February|March|April|May|June|July|August|September"
          r"|October|November|December")
# 'OCTOBER TERM, A.D. 2025' / 'April Term, A.D. 2026' — both cases printed.
_TERM = re.compile(r"^(?:%s)\s+TERM,\s*A\.?\s*D\.?\s*,?\s*\d{4}$" % _MONTH,
                   re.I)
# 'March 9, 2026' — the decision date, flushed into the right-hand stack.
_DATE = re.compile(r"^(?:%s)\s+\d{1,2},\s*\d{4}$" % _MONTH, re.I)
# 'S-25-0166' / 'D-26-0002' / 'S-25-0134, S-25-0170' (consolidated).
_DOCKET = re.compile(r"^[A-Z]-\d{2}-\d{4}(?:\s*,\s*[A-Z]-\d{2}-\d{4})*$")
# PARTY STATUS is a closed vocabulary; a party NAME is never read by wording.
# Case is no help here — 'ANDREA K. SMERSKI f/k/a Andrea' / 'K. Lemon,' is a
# name in two cases and 'Appellant' is a status in one.
_STATUS = re.compile(
    r"^\(?(?:Appellants?|Appellees?|Plaintiffs?|Defendants?|Petitioners?"
    r"|Respondents?|Intervenors?|Movants?|Relators?|Cross-Appellants?"
    r"|Cross-Appellees?|Intervenor-Defendants?|Intervenor-Plaintiffs?"
    r"|Third-Party (?:Plaintiffs?|Defendants?))"
    r"[A-Za-z\s,/()\-.]*$", re.I)
_PIVOT = re.compile(r"^(?:v\.?|vs\.?|and)$", re.I)
# The bench roster, at the body rail below the appearances.
_PANEL_OPEN = re.compile(r"^Before\s+[A-Z]", re.I)
# A roster that has not closed continues on the next row: measured, the
# open forms end in ',' or 'and' ('…and EAMES,' / '…JJ, and') and the
# continuation is the title alone ('D.J.' / 'ROBINSON, DJ.').
_PANEL_OPEN_END = re.compile(r"(?:,|\band)$", re.I)
# Surnames in the roster. The bench TITLES are one or two letters with stops
# ('C.J.', 'JJ.', 'D.J.', 'DJ.') and never match a 3+ letter all-caps run.
_PANEL_NAME = re.compile(r"\b[A-Z][A-Z'’\-]{2,}\b")
_PANEL_NOT_NAME = {"BEFORE", "AND", "JJ", "DJ"}
# An appearances label stands at the rail and ends in a colon; the entries
# stand a step in. Both forms are printed: 'Representing Appellant:' and
# 'Guardian ad Litem:' / 'Amicus Curiae Juvenile Law Center:'.
_COUNSEL_LABEL = re.compile(r":$")
_NOTICE_OPEN = re.compile(r"^NOTICE:", re.I)
# The appearances' own footnote, printed at 11pt with its mark.
_STAR_NOTE = re.compile(r"^\*")
# 'FENN, Justice.' / 'BOOMGAARDEN, Chief Justice.' / 'WESTBY, District
# Judge.' — and 'Hill, Justice.' on sabrina_kaylee_sunshine_stone, which
# sets the surname in title case, so the test is case-insensitive. It is
# only ever run at the body rail, which is what keeps the centred origin
# row 'The Honorable F. Scott Peasley, Judge' out of it.
_BYLINE = re.compile(
    r"^(?:PER CURIAM\.?"
    r"|[A-Z][A-Za-z'’\-]+(?:\s+[A-Z][A-Za-z'’\-]+)*,\s*"
    r"(?:Chief\s+)?(?:Justice|District Judge|J\.|C\.J\.)\.?)$", re.I)
_PARA = re.compile(r"^\[¶\s*\d+\]")

# The caption rail, and only it: measured x 296.5–341.8 over 50 records,
# against the notice box's verticals at 60.7/65.2 and 545.4/549.8.
_RAIL_X_MIN, _RAIL_X_MAX = 200.0, 470.0
_RAIL_MIN_HEIGHT = 30.0
_BAND_PAD_TOP, _BAND_PAD_BOTTOM = 6.0, 8.0
# A rule counts as the band's own edge (rather than a consolidation divider)
# when it coincides with the rail's head or foot.
_EDGE_TOL = 14.0
# Measured: the court sets this block at 12.5–13pt, the notice at 10–11pt.
_SMALL_MAX = 12.0
# A CENTRED ROW IS A SHORT ROW (nh's lesson): a counsel entry running
# 108.0–540.0 has its mid-point 18pt right of the page axis, but the width
# guard is what keeps a shorter one out of the origin ladder.
_AXIS_TOL = 12.0
_CENTRED_WIDTH_MAX = 0.72
# The appearances' entries stand at 108.0 against a 72.0 rail.
_INDENT_MIN = 20.0
_MAX_PAGES = 5


# THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
# has no `docket` field and no `argued` field: the docket is
# `docket_number` (a string) plus `other_dockets` (the rest), and an argued
# date belongs in `submitted`. Written under any other name they are
# attached to the object by setattr and never serialize.


def _norm(text: str) -> str:
    return " ".join(text.split())


def _rail(pm):
    """The caption's drawn divider on this page, or None."""
    rails = [v for v in (pm.v_rules or [])
             if _RAIL_X_MIN < v.x < _RAIL_X_MAX
             and (v.bottom - v.top) >= _RAIL_MIN_HEIGHT]
    if not rails:
        return None
    return max(rails, key=lambda v: v.bottom - v.top)


def _rows(pm, finder, band):
    """Rows in page order. A row STRADDLING THE RAIL is two elements the
    page set on one line — the pivot and the docket beside it — so rows
    inside the caption band are split into their pieces and everything
    else stays joined."""
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
    out: list[list] = []
    for k in order:
        row = groups[k]
        if band and len(row) > 1 and band[0] <= k <= band[1]:
            out.extend([piece] for piece in row)
        else:
            out.append(row)
    return out


@decider("headmatter.read", court="wyo")
def read_headmatter_wyo(model, geom, **_):
    """Read Wyoming's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE DISPATCH IS THE RAIL, and the masthead confirms the paper. No rail
    # on page 1 means this is not the contract and the record is left whole.
    page1 = model.pages[0]
    rail1 = _rail(page1)
    if rail1 is None:
        return NOTHING
    head = [_norm(" ".join(l.plain for l in g))
            for g in _rows(page1, finder, None)[:4]]
    if not any(_MASTHEAD.match(t) for t in head):
        return NOTHING

    ctx = _Ctx()
    walk = _Walk(ctx, body_x0, body_size)
    for pm in model.pages[:_MAX_PAGES]:
        if walk.done:
            break
        if not walk.page(pm, finder):
            break
    walk.flush()

    # THE CRITERIA ARE BUILT BEFORE THEY ARE GATED. `finish()` is what reads
    # the walk's collected dockets into `docket_number`, so asking for it
    # first would refuse every record the walk had just read correctly.
    walk.finish()
    if not ctx.crit.get("docket_number"):
        return NOTHING
    return ctx.result(walk.anchor)


class _Walk:
    """The classifier. One band at a time, each bounded by its own end."""

    def __init__(self, ctx, body_x0: float, body_size: float):
        self.ctx = ctx
        self.body_x0 = body_x0
        self.body_size = body_size
        self.done = False
        self.band = "ident"        # ident | caption | ladder | counsel | panel
        self.seen_caption = False
        self.in_notice = False
        self.panel_open = False
        self.anchor: list[int] = []
        # the pending caption column stacks, flushed at a divider or below
        # the rail
        self.left: list = []
        self.right: list = []
        self.cap_ids: list[int] = []
        self.cap_page = 1
        self.rail_glyph = "|"
        # the printed forms, kept beside the parsed ones
        self.cap_rows: list[str] = []
        self.dockets: list[str] = []
        self.origin: list[str] = []
        self.counsel: list[str] = []
        self.panel_line: str | None = None
        self.title: str | None = None

    # -- the walk -------------------------------------------------------
    def page(self, pm, finder) -> bool:
        """Read one page. False when the block did not reach this page."""
        rail = _rail(pm)
        band = ((rail.top - _BAND_PAD_TOP, rail.bottom + _BAND_PAD_BOTTOM)
                if rail else None)
        rows = _rows(pm, finder, band)
        if not rows:
            return not self.seen_caption or self.band != "ident"
        # The page's DRAWN rules, merged into the row stream by position so
        # the block keeps the page's order. A reader that claims the region
        # inherits its furniture — core draws no fence on a claimed row.
        stream: list = []
        for r in (pm.h_rules or []):
            if self._rule_is_notice_box(pm, r):
                continue
            stream.append((r.top, 1, r))
        for row in rows:
            stream.append((min(l.top for l in row), 0, row))
        stream.sort(key=lambda t: (t[0], t[1]))

        touched = False
        for _top, kind, item in stream:
            if self.done:
                break
            if kind == 1:
                self._rule(pm, band, item)
                continue
            if band and band[0] <= _top <= band[1]:
                self._caption(pm, rail, item)
                touched = True
                continue
            self.flush()
            if not self._row(pm, item):
                self.done = True
                break
            touched = True
        return touched or self.done

    def _rule_is_notice_box(self, pm, r) -> bool:
        """The revision notice's double border, which goes with the notice."""
        box = [v for v in (pm.v_rules or []) if v.x < self.body_x0 - 4.0]
        return any(v.top - 8.0 <= r.top <= v.bottom + 8.0 for v in box)

    def _rule(self, pm, band, r) -> None:
        if band and band[0] <= r.top <= band[1] \
                and abs(r.top - band[0]) > _EDGE_TOL \
                and abs(r.top - band[1]) > _EDGE_TOL:
            # A CONSOLIDATION DIVIDER inside the caption: close the block,
            # draw the rule, open the next.
            self.flush()
            self.ctx.rule(pm.number, span="full")
            return
        self.flush()
        span = "right" if r.x0 > pm.width / 2 - 20.0 else "full"
        self.ctx.rule(pm.number, span=span)

    # -- the caption ----------------------------------------------------
    def _caption(self, pm, rail, group) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in parts))
        if not text:
            return
        self.seen_caption = True
        self.band = "caption"
        self.cap_page = pm.number
        mid = (parts[0].x0 + max(l.x1 for l in parts)) / 2
        cell = self.ctx.cell(parts, "docket" if mid > rail.x else "caption")
        self.cap_ids.extend(p.id for p in parts)
        if mid > rail.x:
            self.right.append(cell)
            self.dockets.append(text)
        else:
            self.left.append(cell)
            self.cap_rows.append(text)

    def flush(self) -> None:
        """Close the pending caption block."""
        if not self.left and not self.right:
            return
        self.ctx.caption(self.cap_page, self.left, self.right,
                         self.rail_glyph, self.cap_ids)
        self.left, self.right, self.cap_ids = [], [], []

    # -- everything below the rail --------------------------------------
    def _row(self, pm, group) -> bool:
        """Place one row. False ends the claim — a row this paper does not
        print is never tinted with a role that would be a guess."""
        parts = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in parts))
        if not text:
            return True
        first = parts[0]
        size = first.size or 0.0
        x1 = max(l.x1 for l in parts)
        at_rail = abs(first.x0 - self.body_x0) <= 4.0
        centred = (abs((first.x0 + x1) / 2 - pm.width / 2) <= _AXIS_TOL
                   and (x1 - first.x0) <= pm.width * _CENTRED_WIDTH_MAX)

        if at_rail and (_PARA.match(text) or _BYLINE.match(text)):
            return False                        # the paper begins
        # ---- the four centred identifiers -------------------------------
        if _MASTHEAD.match(text):
            self.ctx.crit.setdefault("court", text)
            self.ctx.emit(parts, "court")
            return True
        if _CITE.match(text):
            self.ctx.crit.setdefault("citation", text)
            self.ctx.emit(parts, "citation")
            return True
        if _TERM.match(text):
            self.ctx.emit(parts, "court", align=m.Align.RIGHT)
            return True
        if _DATE.match(text) and not self.seen_caption:
            self.ctx.crit.setdefault("decision_date", text)
            self.ctx.emit(parts, "date", align=m.Align.RIGHT)
            return True
        # ---- the small type: the notice, and the appearances' footnote ---
        if size and size < _SMALL_MAX:
            if self.in_notice or _NOTICE_OPEN.match(text):
                self.in_notice = True
                self.ctx.drop(parts, "notice")
                return True
            if _STAR_NOTE.match(text):
                self.counsel.append(text)
                self.ctx.emit(parts, "counsel", align=m.Align.LEFT)
                return True
            return False
        self.in_notice = False
        # ---- the bench roster, before the counsel band can claim it -----
        if _PANEL_OPEN.match(text) and at_rail:
            self.band = "panel"
            self.panel_line = text
            self.panel_open = bool(_PANEL_OPEN_END.search(text))
            self.ctx.emit(parts, "panel", align=m.Align.LEFT)
            return True
        if self.band == "panel" and self.panel_open and at_rail:
            self.panel_line = f"{self.panel_line} {text}"
            self.panel_open = bool(_PANEL_OPEN_END.search(text))
            self.ctx.emit(parts, "panel", align=m.Align.LEFT)
            return True
        # ---- what the paper calls itself --------------------------------
        if self.seen_caption and centred and size >= self.body_size + 0.75 \
                and self.band in ("caption", "title"):
            self.band = "title"
            self.title = f"{self.title} {text}" if self.title else text
            self.anchor.extend(p.id for p in parts)
            self.ctx.emit(parts, "title")
            return True
        # ---- the origin, centred between the caption and the ladder -----
        if centred and self.band in ("caption", "ladder"):
            self.band = "ladder"
            self.origin.append(text)
            self.ctx.emit(parts, "lower-court")
            return True
        # ---- the appearances: a label at the rail, entries a step in ----
        if self.band == "counsel" and first.x0 >= self.body_x0 - 1.0:
            self.counsel.append(text)
            self.ctx.emit(parts, "counsel", align=m.Align.LEFT)
            return True
        if first.x0 >= self.body_x0 + _INDENT_MIN \
                or (at_rail and _COUNSEL_LABEL.search(text)):
            self.band = "counsel"
            self.counsel.append(text)
            self.ctx.emit(parts, "counsel", align=m.Align.LEFT)
            return True
        return False

    # -- the parsed forms ------------------------------------------------
    def finish(self) -> None:
        crit = self.ctx.crit
        crit["headmatter_style"] = (STYLE_ORDER if self.title
                                    else STYLE_LADDER)
        if self.cap_rows:
            crit.setdefault("caption", self.cap_rows[:40])
        names = _party_names(self.cap_rows)
        if names:
            crit.setdefault("parties", names[:8])
        pivot = _case_name(self.cap_rows)
        if pivot:
            crit.setdefault("case_name", pivot)
        if self.dockets:
            flat = [t.strip() for d in self.dockets
                    for t in d.split(",") if t.strip()]
            crit.setdefault("docket_number", flat[0])
            if flat[1:]:
                crit.setdefault("other_dockets", flat[1:])
        if self.origin:
            crit.setdefault("lower_court", self.origin[0])
            judge = next((t for t in self.origin
                          if re.match(r"^The Honorable\b", t, re.I)), None)
            if judge:
                crit.setdefault("lower_court_judge", judge)
            if len(self.origin) > 1:
                crit.setdefault("history", " ".join(self.origin)[:2000])
        if self.counsel:
            crit.setdefault("attorneys", " ".join(self.counsel)[:4000])
        if self.panel_line:
            crit.setdefault("panel_line", self.panel_line)
            seat = [t for t in _PANEL_NAME.findall(self.panel_line)
                    if t.upper() not in _PANEL_NOT_NAME]
            if seat:
                crit.setdefault("panel", seat)
                crit.setdefault("judges", ", ".join(seat))
        if self.title:
            crit.setdefault("title", self.title)


def _party_names(rows: list[str]) -> list[str]:
    """The party names, built from the rows a status label does NOT close.
    Joining the caption wholesale yields 'AARON R. MAKI, Appellant
    (Defendant), THE STATE OF WYOMING…'."""
    names: list[str] = []
    run: list[str] = []
    for row in rows:
        if _PIVOT.match(row) or _STATUS.match(row):
            if run:
                names.append(_norm(" ".join(run)).rstrip(",;"))
                run = []
            continue
        run.append(row)
    if run:
        names.append(_norm(" ".join(run)).rstrip(",;"))
    return [n for n in names if n]


def _case_name(rows: list[str]) -> str | None:
    """'X v. Y', from the party names either side of the printed pivot."""
    above: list[str] = []
    below: list[str] = []
    side = above
    for row in rows:
        if re.match(r"^v\.?$|^vs\.?$", row, re.I):
            if below:
                break
            side = below
            continue
        side.append(row)
    left = _party_names(above)
    right = _party_names(below)
    if not left or not right:
        return None
    return f"{left[0]} v. {right[0]}"


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def _line(self, parts: list, role: str, align) -> m.HmLine:
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=align, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def emit(self, group: list, role: str, align=m.Align.CENTER) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.items.append(self._line(parts, role, align))
        self.consumed.update(p.id for p in parts)

    def cell(self, parts: list, role: str) -> m.HmLine:
        """A caption cell — built, not emitted: it goes in a CaptionBlock."""
        self.consumed.update(p.id for p in parts)
        return self._line(parts, role, m.Align.LEFT)

    def caption(self, page: int, left: list, right: list, rail: str,
                ids: list) -> None:
        # THE TWO STACKS ARE NOT ROW-PAIRED. The renderer flows each column
        # on its own, and in this caption the docket answers to the whole
        # block rather than to the party row it happens to sit beside, so
        # padding the short column would only add blank tinted rows.
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=rail, rail_rows=max(len(left), 1),
            fp={"rail": "drawn"}, prov=m.Prov(page, tuple(sorted(ids)))))

    def rule(self, page: int, span: str = "full") -> None:
        self.items.append(m.Rule(prov=m.Prov(page), span=span))

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self, anchor: list) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": anchor, "doc_type_final": None}
