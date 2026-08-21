"""Michigan Supreme Court ('mich').

Everything unique to mich lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Michigan files TWO papers, and page 1's DRAWN FENCES name
which one. Both papers set the same letterhead — the court's name in the
upper right over the seated bench — and the fences under it are the
court's own stationery, not the document's:

    'reported slip' (49 of 50) — the Reporter's release. Page 1 carries
    THREE full-width rules across the letterhead (measured: 536.0pt at
    x0=37.9, tops 53.5 / 163.7 / 199.8 on all 49) and a 65pt section tab
    at the left margin. Exactly ONE later page carries TWO of those rules
    (564.0pt at x0=23.6, tops 58.8 / 169.0) — that page is the OPINION
    COVER, and it is the headmatter:

        Michigan Supreme Court            the letterhead, upper right…
        Lansing, Michigan
        ── fence 1 ─────────────────
        OPINION   Chief Justice:          …the section tab and the bench
                  Elizabeth T. Clement
                  Justices:  Brian K. Zahra …
        ── fence 2 ─────────────────      …and the letterhead ends here
        FILED  April 20, 2026             the release stamp, flush right
        S T A T E  O F  M I C H I G A N   the court naming itself, centred
        SUPREME COURT
        JANICE SHERMAN,                   a party, AT THE RAIL…
             Plaintiff-Appellant,         …its status, indented…
        v                    No. 167826   …the pivot, with the docket
        PROGRESSIVE MICHIGAN INSURANCE      flush right on the same row
        COMPANY,
             Defendant-Appellee,
        ──────────────── (250pt shelf)    the caption's own closing rule
        BEFORE THE ENTIRE BENCH (except HOOD, J.)      the panel
        ZAHRA, J.                         …and the writing starts

    Everything BETWEEN page 1 and that cover is the Reporter's syllabus
    (`syllabus.pages` below), which is why the reader claims the two
    letterheads and nothing in between.

    'clerk's order' (1 of 50) — a one-page disposition. NO full-width
    rule anywhere; a 30pt 'Order' tab, the date and the docket at the
    rail, the caption beside a right-hand column of case numbers, and a
    TYPED underscore rule ending in '/' closing the caption:

        Order                             the tab, 30pt at the margin
        March 25, 2026                    the date, at the rail
        169730 & (3)                      the docket
        In re ANONYMOUS JUDGE   SC: 169730      the caption, and the
        BEFORE THE JUDICIAL TENURE          numbers in a right column
        COMMISSION
        ______________________________/   the typed closing rule
        On order of the Court, …          …and the writing starts

THE DISPATCH is a single question about page 1: how many full-width
drawn rules does the letterhead fence with? Three is the reported slip,
none is the clerk's order. Over the 50-record corpus that test agrees
with the papers' own tabs on every one; a record answering neither gets
NOTHING.

WHERE EACH ZONE ENDS. The letterhead ends at its LAST fence — the rows
above it are the court's stationery (banner, tab, bench roster, and on
page 1 the Reporter of Decisions' name in the same right-hand column),
and the reader records them as `Dropped` rather than reprinting them.
The caption ends at the SHELF: a rule at the body rail, roughly two
fifths of the measure (measured 237-290pt over the corpus), drawn on the
slip and TYPED on the order and on a consolidation. The reader ends at
the first byline, always.

A SEPARATE WRITING PRINTS ITS OWN COVER. Michigan paginates every
writing on its own (the majority's folio reads 35 on the page above a
dissent whose first page reads 1), and sets a fresh cover over each one —
the court naming itself CENTRED ON THE PAGE AXIS, then the whole caption
again, then the shelf, then the byline:

    S T A T E  O F  M I C H I G A N   centred, and NO letterhead: the
    SUPREME COURT                       fences belong to the Reporter's
    PINEBROOK WARREN, LLC, …            release and the lead cover only
         Plaintiffs-Appellants,
    v                    No. 164869
    …
    ──────────────── (251.9pt shelf)
    VIVIANO, J. (dissenting).         …and the separate writing starts

That cover is a VERBATIM REPEAT of the block the lead cover already
printed, and the reader claims it as `Dropped`. It has to: the cover
opens BELOW the first byline, so assembly files it into the PRECEDING
writing, where it renders as a heading and 400 rows of body prose
(pinebrook_warren_llc_v._city_of_warren_1, pages 41-52, at the tail of
the majority). Measured over the 50-record corpus: 52 such covers on 30
records, every one closed by a byline, and NOT ONE containing a single
full-measure lower-case row — no prose is ever inside one, so the run
from the centred court row to the next byline is safe to claim whole. A
candidate page that never reaches a byline is not this shape, and then
nothing is claimed.

WHAT THE READER DOES NOT TOUCH. The Reporter's syllabus is core's
section, and its own title and 'Docket No. … Argued … Decided …' row are
read for criteria but left where the page prints them. mich prints
NO appearance of counsel anywhere in the corpus.
"""

from __future__ import annotations

import re

from .. import model as m
from ..model import DocType
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

MICH = register(CourtProfile(
    "mich", "Michigan Supreme Court",
    # 'ZAHRA, J.' / 'CLEMENT, C.J. (dissenting).' / 'WELCH, J.'
    byline=BylineGrammar(style="abbrev"),
    # The Reporter's syllabus is part of the official report.
    front_matter=("syllabus",),
))

STYLE_SLIP = "reported slip"
STYLE_ORDER = "clerk's order"

# ---- mich's declared facts (measured over the 50-record corpus) ----------
# THE LETTERHEAD FENCE: a drawn rule across the WHOLE sheet. 536.0pt on the
# syllabus title page (x0=37.9), 564.0pt on the opinion cover (x0=23.6);
# the body measure is 468pt, so nothing in the text block reaches this.
_FENCE_WIDTH = 500.0
# …and it is stationery, so it is always in the page's top third.
_FENCE_BAND = 0.35
# HOW MANY FENCES NAME THE PAPER: three on the reported slip's page 1, two
# on its opinion cover, none anywhere on the clerk's order.
_SLIP_PAGE1_FENCES = 3
_COVER_FENCES = 2
# THE SECTION TAB ('Syllabus' / 'OPINION' / 'Order') is set far above body
# size at the left margin, inside the letterhead band.
_TAB_SIZE = 20.0
_TAB_X1 = 60.0
# THE BENCH ROSTER stands in the letterhead's right-hand column. On page 1
# the Reporter of Decisions' name sits in the same column BELOW the second
# fence, so the column claim runs to the third.
_ROSTER_X0 = 300.0
# THE CAPTION'S SHELF: a rule at the body rail about two fifths of the
# measure (237.3-289.5pt over the corpus), drawn on the slip and TYPED on
# a consolidation and on the clerk's order.
_SHELF = (210.0, 320.0)
_SHELF_RAIL = 110.0
# A row is AT THE RAIL when it starts on the caption's own left edge.
_RAIL_TOL = 6.0
# HOW FAR THE COVER MAY RUN. pinebrook_warren repeats its caption once per
# consolidated docket and carries it from page 6 to page 17.
_MAX_COVER_PAGES = 14
# HOW FAR A SEPARATE WRITING'S REPRINTED COVER MAY RUN. Those same nine
# consolidated dockets carry the dissent's cover of
# pinebrook_warren_llc_v._city_of_warren_1 from page 41 to page 52 — 12
# pages, the corpus maximum (the other 51 reprints run one page, two on
# c-spine_orthopedics and parie_wallace). Two pages of headroom, and the
# run must still CLOSE ON A BYLINE before anything is claimed.
_REPRINT_PAGES = 14
# THE PAGE AXIS. The court's name is the one row Michigan centres, on the
# lead cover and on every reprint alike; the tolerance is the one the lead
# walk already uses (measured: 'S T A T E  O F  M I C H I G A N' spans
# 218.3-393.6 on a 612pt sheet, centre 305.95 against the axis at 306.0).
_AXIS_TOL = 12.0
# HOW FAR THE COVER MAY BE FROM PAGE 1. philip_m_ohalloran's syllabus runs
# eight pages before the opinion's own cover.
_MAX_SYLLABUS_PAGES = 20

# A typed rule: six or more underscores, optionally closed by the pleading
# slash Michigan's clerk types at the end of an order's caption.
_TYPED_RULE = re.compile(r"^_{6,}/?$")
# 'No. 167826' / 'Nos. 165537-8' / 'Nos. 164869, 164870' — the docket as
# this court prints it, in the caption's right-hand column. A closed
# structural form: the word No/Nos over digits, never a name.
_DOCKET = re.compile(r"^Nos?\.\s*(.+)$")
# 'SC: 169730' / 'RFI: 2026-26948' — the clerk's order sets its numbers as
# a labelled pair instead.
_LABELLED_DOCKET = re.compile(r"^(?:[A-Z]{2,4}):\s*[\dA-Za-z-]+$")
# The pivot: a bare 'v' at the rail on its own row. Michigan sets no period.
_PIVOT = re.compile(r"^v\.?$")
# The release stamp the cover prints under its letterhead.
_FILED = "filed"
# 'BEFORE THE ENTIRE BENCH (except HOOD, J.)' — the panel, stated as a
# structural form (the word BEFORE over the bench), never a roster.
_PANEL = re.compile(r"^BEFORE\s+THE\s+ENTIRE\s+BENCH\b", re.I)
# 'BEFORE THE JUDICIAL TENURE COMMISSION' — the FORUM an order's matter
# came from, printed inside the caption. A closed leader, never a name.
_FORUM = "before the"
# THE LETTERHEAD IS SET FLUSH TO THE SHEET, outside the text block: its
# rows reach within a few points of the paper's right edge (582.5 of 612)
# while the widest body row stops at 540. That column is what bounds it on
# the clerk's order, which fences with nothing.
_MARGIN_TOL = 40.0
# A roster name in the letterhead column: 'Elizabeth T. Clement'. pdfio
# interleaves two columns that share a baseline on some pages
# ('CMhieef gJuasntic Ke: . Cavanagh'), and an interior capital is what
# gives that away — a real name has none.
_ROSTER_NAME = re.compile(
    r"^[A-Z][a-z’']+(?:\s+[A-Z]\.)?(?:\s+[A-Z][a-z’'-]+)+,?$")
# The bench TITLES the letterhead sets over the names — a finite role
# vocabulary, printed with the colon on the slip and without it on the order.
_BENCH_LABELS = frozenset(("chief justice", "justices", "justice",
                           "reporter of decisions"))


def _norm(text: str) -> str:
    return " ".join(text.split())


def _untrack(text: str) -> str:
    """'S T A T E  O F  M I C H I G A N' -> 'STATE OF MICHIGAN'. Michigan
    tracks out the court's name on the cover; the wide gaps are the word
    breaks, so closing up the single glyphs reads the same row, not a
    different one. The printed form is kept on the row itself."""
    out = []
    for chunk in re.split(r"\s{2,}", text.strip()):
        parts = chunk.split()
        out.append("".join(parts) if parts and all(len(p) == 1 for p in parts)
                   else chunk)
    return " ".join(w for w in out if w)


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _fences(pm) -> list:
    """The letterhead's full-width rules, top first."""
    return sorted((r for r in pm.h_rules
                   if r.width >= _FENCE_WIDTH
                   and r.top < pm.height * _FENCE_BAND),
                  key=lambda r: r.top)


def _is_shelf(rule, rail: float) -> bool:
    """The caption's own closing rule: at the rail, two fifths of the
    measure. A letterhead fence is four times as long and starts outside
    the text block; a footnote separator is 144.0pt and shorter still."""
    return (_SHELF[0] <= rule.width <= _SHELF[1]
            and rule.x0 <= rail + _SHELF_RAIL)


def _typed_shelf(text: str) -> bool:
    return bool(_TYPED_RULE.match(text.replace(" ", "")))


def _cover_page(model) -> int | None:
    """The opinion cover: the one later page whose letterhead fences twice."""
    for pm in model.pages[1:_MAX_SYLLABUS_PAGES]:
        if len(_fences(pm)) == _COVER_FENCES:
            return pm.number
    return None


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """What both walks share: the page models and the emit buffer."""

    def __init__(self, model, geom, finder):
        self.model = model
        self.geom = geom
        self.finder = finder
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def lines(self, page_no: int) -> list:
        """Content lines of one page, furniture left for core to drop."""
        pm = self.pages[page_no]
        return [l for l in sorted(pm.lines, key=lambda l: (l.top, l.x0))
                if l.plain.strip() and not self.finder.kind(pm, l)]

    def emit(self, line, role: str, align: str = "L",
             rel: float = 0.0) -> None:
        self.items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role))
        self.consumed.add(line.id)

    def rule(self, page_no: int, ids=(), typed: bool = False) -> None:
        # A DRAWN rule has no line of its own, and the block is re-sorted
        # into the page's order by line id — so a rule the page drew borrows
        # the prov of the row it follows and the stable sort keeps it there.
        prov = m.Prov(page_no, tuple(ids))
        if not ids and self.items:
            prov = self.items[-1].prov
        self.items.append(m.Rule(prov=prov, typed=typed, span="left"))
        self.consumed.update(ids)

    def drop(self, lines: list, kind: str) -> None:
        if not lines:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(_norm(l.plain) for l in lines)[:1200],
            prov=m.Prov(lines[0].page, tuple(l.id for l in lines)),
            kind=kind))
        self.consumed.update(l.id for l in lines)

    def result(self, doc_type=None):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": doc_type}


def _claim_letterhead(ctx: _Ctx, page_no: int) -> list:
    """The court's stationery: everything above the letterhead's LAST fence,
    plus what stands in its right-hand column between the second fence and
    the third. Recorded as `Dropped`, never reprinted — it is the same on
    every sheet the court files."""
    pm = ctx.pages[page_no]
    fences = _fences(pm)
    if len(fences) < 2:
        return []
    band = fences[1].top
    tail = fences[2].top if len(fences) > 2 else band
    head = [l for l in ctx.lines(page_no)
            if l.top < band
            or (band <= l.top < tail and l.x0 >= _ROSTER_X0)]
    ctx.drop(head, "letterhead")
    return head


def _roster_panel(lines: list, below: float = 0.0) -> list:
    """The seated bench, read off the letterhead's right-hand column BELOW
    its first fence — the court's own name stands above that rule and reads
    as a title-case name too. A row pdfio interleaved with its neighbour
    ('CMhieef gJuasntic Ke: . Cavanagh') is skipped, not repaired: an
    interior capital is what gives the collision away."""
    out: list = []
    for line in lines:
        if line.x0 < _ROSTER_X0 or line.top < below or line.all_bold:
            continue                      # the court's own name is BOLD
        name = _norm(line.plain).rstrip(",")
        if name.rstrip(":").lower() in _BENCH_LABELS:
            continue                      # the title over the names
        if _ROSTER_NAME.match(name) and name not in out:
            out.append(name)
    return out


# --------------------------------------------------------------------------
# the caption's own grammar — shared by both papers
# --------------------------------------------------------------------------

def _record_docket(ctx: _Ctx, printed: str) -> None:
    hit = _DOCKET.match(printed)
    value = _norm(hit.group(1)) if hit else _norm(printed)
    for part in re.split(r"\s*(?:,|\band\b|&)\s*", value):
        part = part.strip(" .")
        # '169730 & (3)' — the clerk files the motion's own sequence beside
        # the docket; only the number the court gave the case is one.
        if not part or not re.fullmatch(r"[\dA-Za-z][\dA-Za-z-]*", part):
            continue
        if ctx.crit.get("docket_number") is None:
            ctx.crit["docket_number"] = part
        elif part != ctx.crit["docket_number"]:
            ctx.crit.setdefault("other_dockets", []).append(part)


def _name_from(ctx: _Ctx, left: list, right: list) -> None:
    """The case name, built from the party names either side of the pivot —
    never by joining caption rows wholesale (the status labels stand between
    them and would read as parties)."""
    a = _norm(" ".join(left)).rstrip(",; ")
    b = _norm(" ".join(right)).rstrip(",; ")
    if a and b:
        ctx.crit["parties"] = [a, b]
        ctx.crit["case_name"] = f"{a} v {b}"
    elif a:
        ctx.crit["parties"] = [a]
        ctx.crit["case_name"] = a


class _Parties:
    """The LEAD case's parties, gathered as the caption prints them.

    A party name wraps over as many rail rows as it needs and is closed by
    the STATUS label indented under it ('Plaintiff-Appellant,'); the pivot
    row turns the collection over to the other side; and once the second
    side has closed, the document is named. That last rule is what a
    consolidation needs: pinebrook_warren restates the whole caption once
    for each of its nine dockets, and without it the case name read nine
    times over.
    """

    def __init__(self):
        self.left: list = []
        self.right: list = []
        self._side = self.left
        self._pivot = False
        self._done = False

    def party(self, text: str) -> None:
        if not self._done:
            self._side.append(text)

    def status(self) -> None:
        if self._pivot and self.right:
            self._done = True

    def pivot(self) -> None:
        if not self._done:
            self._pivot = True
            self._side = self.right


# --------------------------------------------------------------------------
# the cover a separate writing prints over itself
# --------------------------------------------------------------------------

def _reprint_block(ctx: _Ctx, page_no: int, banner: str,
                   parser: BylineParser) -> list:
    """The reprinted cover that OPENS on ``page_no``, or [].

    Two facts identify it and both are the page's own geometry: the first
    content row of the page is CENTRED ON THE AXIS and is the very row the
    lead cover printed as the court naming itself (compared against what
    THIS document printed, never against a wording list), and the run
    closes at the next BYLINE — the same landmark that ends the lead walk.

    A run that reaches `_REPRINT_PAGES` without a byline is NOT this shape
    and returns nothing: better to leave the rows to core than to drop
    prose. Measured on the corpus: 52 blocks, all 52 closed by a byline,
    none holding a full-measure lower-case row.
    """
    rows = ctx.lines(page_no)
    if not rows:
        return []
    pm = ctx.pages[page_no]
    head = rows[0]
    if abs((head.x0 + head.x1) / 2 - pm.width / 2) > _AXIS_TOL:
        return []
    # the tracked-out row is the same row closed up — 'S T A T E  O F …'
    if _untrack(head.plain).strip().upper() != banner:
        return []
    block: list = []
    last = min(page_no + _REPRINT_PAGES, len(ctx.model.pages))
    for page in range(page_no, last + 1):
        for line in ctx.lines(page):
            if parser.parse(_norm(line.plain)) is not None:
                return block          # the writing starts HERE, not above
            block.append(line)
    return []


def _drop_reprints(ctx: _Ctx, after: int, court: list,
                   parser: BylineParser) -> None:
    """Claim every reprinted cover below the lead byline.

    Recorded as `Dropped(kind="superfluous")`, the kind core already uses
    for cover apparatus a court prints twice — the rows are a verbatim
    repeat of the caption that renders whole at the head of the document,
    so nothing court-written is lost, and core still mines a superfluous
    drop for criteria. One `Dropped` PER PAGE, because a `Dropped` carries
    one page in its prov and its text preview is capped at 1200 characters
    — pinebrook_warren's 12-page dissent cover would lose most of its
    attestation as a single record.

    The claim is subtractive and happens BEFORE assembly, so this is not
    the reader reaching into a writing: these rows never enter one.
    """
    if not court:
        return
    banner = court[0].strip().upper()
    page_no = after + 1
    while page_no <= len(ctx.model.pages):
        block = _reprint_block(ctx, page_no, banner, parser)
        if not block:
            page_no += 1
            continue
        for page in sorted({l.page for l in block}):
            ctx.drop([l for l in block if l.page == page], "superfluous")
        page_no = max(l.page for l in block) + 1


# --------------------------------------------------------------------------
# the reported slip
# --------------------------------------------------------------------------

def _read_slip(ctx: _Ctx, cover: int):
    parser = BylineParser(MICH.byline)
    # PAGE 1's letterhead is stationery on a page core routes to the
    # syllabus; unclaimed it interleaves with the Reporter's notice.
    _claim_letterhead(ctx, 1)
    head = _claim_letterhead(ctx, cover)
    fences = _fences(ctx.pages[cover])
    panel = _roster_panel(head, below=fences[0].top)

    rail = None
    court: list = []
    caption: list = []
    parties = _Parties()
    signed = False
    signed_page = 0
    band = fences[1].top
    for page_no in range(cover, min(cover + _MAX_COVER_PAGES,
                                    len(ctx.model.pages)) + 1):
        pm = ctx.pages[page_no]
        rules = [r for r in pm.h_rules if page_no > cover or r.top > band]
        for line in ctx.lines(page_no):
            if page_no == cover and line.top < band:
                continue
            text = _norm(line.plain)
            # THE SHELF the page drew above this row closes a caption group.
            for r in [x for x in rules if x.top < line.top
                      and _is_shelf(x, rail if rail is not None else 0.0)]:
                ctx.rule(page_no)
                rules.remove(r)
            if parser.parse(text) is not None:
                signed = True
                signed_page = page_no
                break
            if _PANEL.match(text):
                ctx.crit["panel_line"] = text
                ctx.emit(line, "panel")
                continue
            if _typed_shelf(text):
                ctx.rule(page_no, (line.id,), typed=True)
                continue
            if text.lower().startswith(_FILED):
                ctx.crit["decision_date"] = _norm(
                    text[len(_FILED):]).lstrip(": ")
                ctx.emit(line, "date", "R")
                continue
            if rail is None:
                # THE COURT NAMES ITSELF above the caption, centred; the
                # caption's rail is the first row to leave the page axis.
                if abs((line.x0 + line.x1) / 2 - pm.width / 2) <= 12.0:
                    # the tracked-out row keeps its OWN spacing: the wide
                    # gaps are its word breaks and _norm would close them.
                    court.append(_untrack(line.plain))
                    ctx.emit(line, "court", "C")
                    continue
                rail = line.x0
            # THE DOCKET shares the pivot's row, flush right.
            if _DOCKET.match(text) and line.x0 > rail + 100:
                _record_docket(ctx, text)
                ctx.emit(line, "docket", "R")
                continue
            caption.append(text)
            if line.x0 > rail + _RAIL_TOL:
                # A STATUS LABEL is indented from the caption's own rail.
                ctx.emit(line, "caption", "L", rel=line.x0 - rail)
                parties.status()
                continue
            ctx.emit(line, "caption", "L")
            if _PIVOT.match(text):
                parties.pivot()
                continue
            parties.party(text)
        else:
            continue
        break
    if not (signed and rail is not None and caption):
        return NOTHING
    # EVERY SEPARATE WRITING BELOW re-prints this same cover; those rows are
    # claimed too, or they read as body prose at the tail of the writing
    # above them.
    _drop_reprints(ctx, signed_page, court, parser)
    ctx.crit["headmatter_style"] = STYLE_SLIP
    if court:
        ctx.crit["court"] = " ".join(court)
    ctx.crit["caption"] = caption
    if panel:
        ctx.crit["panel"] = panel
    _name_from(ctx, parties.left, parties.right)
    return ctx.result()


# --------------------------------------------------------------------------
# the clerk's order
# --------------------------------------------------------------------------

def _read_order(ctx: _Ctx):
    from ..resolve.headmatter import find_date
    pm = ctx.model.pages[0]
    rows = ctx.lines(1)
    # THE LETTERHEAD here fences with nothing, so its own COLUMN bounds it:
    # every row of it is set flush to the sheet's right edge, outside the
    # text block, and the section tab stands alone at the left margin.
    head = [l for l in rows
            if l.x1 >= pm.width - _MARGIN_TOL
            or (l.x0 < _TAB_X1 and (l.size or 0) >= _TAB_SIZE)]
    body = [l for l in rows if l not in head]
    if not body:
        return NOTHING
    rail = min(l.x0 for l in body)
    ctx.drop(head, "letterhead")
    caption: list = []
    parties = _Parties()
    forum = False
    closed = False
    for line in body:
        text = _norm(line.plain)
        if _typed_shelf(text):
            ctx.rule(1, (line.id,), typed=True)
            closed = True
            break
        # THE CLERK SETS THE CASE NUMBERS IN A COLUMN of their own, right of
        # the caption and left of the letterhead.
        if _LABELLED_DOCKET.match(text) and line.x0 > rail + 100:
            _record_docket(ctx, text.split(":", 1)[1])
            ctx.emit(line, "docket", "R")
            continue
        if not caption and ctx.crit.get("decision_date") is None \
                and find_date(text):
            ctx.crit["decision_date"] = find_date(text)
            ctx.emit(line, "date")
            continue
        if not caption and re.match(r"^[\d ()&,]+$", text):
            _record_docket(ctx, text)
            ctx.emit(line, "docket")
            continue
        # THE FORUM the matter came from, stated inside the caption and
        # wrapping over as many rows as it needs.
        if text.lower().startswith(_FORUM) or forum:
            forum = True
            prev = ctx.crit.get("lower_court")
            ctx.crit["lower_court"] = f"{prev} {text}" if prev else text
            ctx.emit(line, "lower-court", "L",
                     rel=max(0.0, line.x0 - rail))
            continue
        caption.append(text)
        ctx.emit(line, "caption", "L", rel=max(0.0, line.x0 - rail))
        if _PIVOT.match(text):
            parties.pivot()
            continue
        parties.party(text)
    if not (closed and caption):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_ORDER
    ctx.crit["caption"] = caption
    ctx.crit["court"] = MICH.court_label
    panel = _roster_panel(head)
    if panel:
        ctx.crit["panel"] = panel
    _name_from(ctx, parties.left, parties.right)
    return ctx.result(DocType.ORDER)


# --------------------------------------------------------------------------
# the deciders
# --------------------------------------------------------------------------

def _dispatch(model, geom):
    """(ctx, style, cover) for a paper this court files, or None."""
    if not model.pages:
        return None
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    ctx = _Ctx(model, geom, FurnitureFinder(model, body_x0, body_size))
    fences = len(_fences(model.pages[0]))
    if fences >= _SLIP_PAGE1_FENCES:
        cover = _cover_page(model)
        return (ctx, STYLE_SLIP, cover) if cover else None
    if fences == 0 and len(model.pages) == 1:
        return (ctx, STYLE_ORDER, None)
    return None


@decider("headmatter.read", court="mich")
def read_headmatter_mich(model, geom, **_):
    """Read one of mich's two papers, or NOTHING."""
    found = _dispatch(model, geom)
    if found is None:
        return NOTHING
    ctx, style, cover = found
    return _read_slip(ctx, cover) if style == STYLE_SLIP else _read_order(ctx)


@decider("syllabus.pages", court="mich")
def syllabus_pages_mich(model, geom, **_):
    """The Reporter's syllabus: page 1 through the page before the opinion's
    own cover.

    The pages carry no running head, so the extent is read off the two
    stationery landmarks instead — the syllabus opens on the page whose
    letterhead fences three times and ends where the letterhead fences
    twice. Core's own test closes the run at the first page whose top band
    reads like a banner, and a syllabus SENTENCE does ('… the Supreme
    Court, in lieu of granting leave to appeal, held:' carries two court
    words), which left seven pages of philip_m_ohalloran's syllabus in the
    headmatter.
    """
    if not model.pages or len(_fences(model.pages[0])) < _SLIP_PAGE1_FENCES:
        return NOTHING
    cover = _cover_page(model)
    return set(range(1, cover)) if cover else NOTHING
