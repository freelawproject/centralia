"""Supreme Court of Illinois ('ill').

Everything unique to ill lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Illinois publishes TWO papers for every decision, and the
page tells them apart before a word is read.

    'ruled cover' (47 of 50) — the opinion slip. A 12pt BOLD
    public-domain citation, a 16pt BOLD four-row masthead, and then a
    DRAWN RULE: 144.7pt wide, centred 5.0pt right of the page axis, at
    top 305 of 792. Measured over the corpus the rule is invariant to
    the tenth of a point and appears on every cover and on nothing else.
    It is the fence that closes the masthead and opens the case:

        2026 IL 130930                    12pt bold, on the axis
        IN THE                            \
        SUPREME COURT                      >  16pt bold masthead,
        OF                                /   four rows, on the axis
        THE STATE OF ILLINOIS            /
        ───────────────                   the FENCE — 144.7pt, axis+5
        (Docket No. 130930)               the docket
        THE PEOPLE OF THE STATE OF …      the caption, wrapped
        CORWYN BROWN, Appellee.           …to as many rows as it needs
        Opinion filed January 28, 2026.   the release date
        CHIEF JUSTICE NEVILLE delivered…  …and the writing starts

    ABOVE THE FENCE THE COVER IS INVARIANT: five rows, one 12pt bold
    and four 16pt bold, on all 47 covers. BELOW IT the court centres
    every row on the page axis (measured: 182 of 184 rows at offset
    0.0/-0.1; the two others are caption rows long enough to fill the
    measure). So the cover DECLARES its alignment rather than inferring
    it per row — a full-measure party list is still a centred caption
    row, and read per row it renders as a flush-left paragraph.

    THE SAME MEASURE OFF THE AXIS IS SOMETHING ELSE. One cover draws a
    144.0pt rule at top 648 — the footnote separator, 162pt left of the
    axis. Width alone takes it; the axis takes neither it nor anything
    else on the page.

    'case summary' (3 of 50) — the one-page synopsis the court releases
    beside each opinion (people_v._butler is the summary; butler_1 is
    the 29-page opinion). No citation, no typed masthead, no fence and
    no line above body size; the court's SEAL is set as a 67x67pt raster
    on the axis in the page's top band, and under it the same docket,
    caption and release date, then a named byline and two paragraphs of
    prose ABOUT the decision.

        [seal]                            67x67pt image, on the axis
        (Docket No. 130988)
        THE PEOPLE OF THE STATE OF …      the caption
        SIDNEY BUTLER, Appellant.
        Opinion filed November 20, 2025.
        Justice Overstreet delivered …    …and the synopsis follows

THE DISPATCH is one question about page 1: is ill's fence drawn on it?
Fence — the cover. No fence, no row above body size, and an axis-centred
image in the top band — the summary. Neither, and the record is not one
of these papers: the reader returns NOTHING and core's shared walk has it.

WHERE THE READER STOPS. At the first byline, which on this court is
prose ('CHIEF JUSTICE NEVILLE delivered the judgment of the court, with
opinion.' / 'PER CURIAM'). Everything under it — the concurrence roster,
the recusals, the announcements of separate writings, the 'OPINION'
heading — is the writing's, and the reader does not take it. It is READ
for the panel and left exactly where the page put it.

WHY THE BYLINE GRAMMAR STRIPS A PARAGRAPH MARKER. ill numbers its
paragraphs with a hanging pilcrow, and it numbers the SEPARATE WRITINGS'
bylines too: '¶ 63      JUSTICE OVERSTREET, specially concurring:' is one
visual row, the marker at x=62.6 and the byline at the body rail. Without
`strip_para_marker` every special concurrence, dissent and partial
dissent in the corpus is invisible and the document assembles as a single
majority.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import register

ILL = register(CourtProfile(
    "ill", "Supreme Court of Illinois",
    # 'JUSTICE ROCHFORD delivered the judgment of the court, with opinion.'
    # / 'Justice Overstreet delivered …' (the summary sheet sets the same
    # byline in title case) / 'JUSTICE O'BRIEN, dissenting:'.
    byline=BylineGrammar(style="reversed", strip_para_marker=True,
                         rev_titles=("JUSTICE", "CHIEF JUSTICE")),
))

STYLE_COVER = "ruled cover"
STYLE_SUMMARY = "case summary"

# ---- ill's declared facts (measured over the 50-record corpus) -----------
# THE FENCE. 47 covers, 47 rules: 144.7pt wide on every one, centred 5.0pt
# right of the page axis on every one, at top 305.2 on every one. The only
# other rule anywhere on a page 1 is a footnote separator at the same
# measure and 162pt off the axis.
_FENCE_MEASURE = (140.0, 150.0)
_FENCE_AXIS = (5.0, 3.0)          # (offset from the page axis, tolerance)
# THE MASTHEAD is 16pt over a 12pt body; nothing else on the cover leaves
# body size, and the summary sheet has no row above it at all.
_MASTHEAD_SIZE = 14.0
# THE COVER CENTRES EVERY ROW on the page axis — declared, not tested per
# row: a caption row long enough to fill the measure reads flush-left to a
# shared alignment test and renders as an indent instead. The tolerance
# below is used only where something OTHER than a text row has to be found
# on the axis (the summary sheet's seal).
_AXIS_TOL = 12.0
# THE SEAL on the summary sheet: 67.35pt square, top 72 of 792 (9%), and
# centred on the axis to a tenth of a point.
_SEAL_MIN = 40.0
_SEAL_BAND = 0.25
# HOW FAR THE BLOCK MAY RUN. Both papers print the whole of it on page 1.
_MAX_PAGES = 1

# 'Opinion filed November 20, 2025.' — the release row, and the only row
# the court dates. A closed leader, never a court or party name.
_FILED_LEAD = "opinion filed"
# '(Docket No. 130930)' / '(Docket No. 130596, 130597 cons.)' /
# '(Docket Nos. 131026, 131032)' — every form the court prints. The row is
# read as the SEQUENCE of dockets it names: a consolidation is companion
# appeals, not one number with a comma in it.
_DOCKET_LEADS = ("docket no.", "docket nos.")
# PARTY STATUS is a finite role vocabulary; a party NAME is never read by
# wording. Illinois prints the status after the name, comma-separated, and
# COMPOUNDS the trial and appellate roles with a hyphen on a supervisory
# petition ('Petitioner-Appellant', 'Respondents-Appellees'). So the label
# is read as a compound of role words rather than enumerated whole —
# enumerating it missed both halves of stewart's caption.
_ROLES = frozenset((
    "appellant", "appellants", "appellee", "appellees",
    "petitioner", "petitioners", "respondent", "respondents",
    "plaintiff", "plaintiffs", "defendant", "defendants",
    "intervenor", "intervenors", "movant", "movants",
    "counterplaintiff", "counterplaintiffs",
    "counterdefendant", "counterdefendants"))
# The modifiers a compound role may carry, and nothing else.
_ROLE_MODS = frozenset(("cross", "counter", "third", "party"))
# BENCH TITLES — the closed vocabulary that opens a name run in the
# court's own roster prose. Longest first so 'Chief Justice' wins.
_BENCH = ("Chief Justices", "Chief Justice", "Justices", "Justice")
# THE ROSTER'S VERBS. A statement naming justices ends at its verb; the
# recusal is the one statement whose names are NOT on the panel.
_RECUSED = "took no part"


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# the visual row — pdfio splits a row at its column gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline.

    ill hangs its paragraph marker in a column of its own ('¶ 63' at
    x=62.6 beside the row's text at x=108), so a row can reach the reader
    in pieces. Nothing in the headmatter is set that way, but the reader
    walks to the first byline and the byline itself may be.
    """

    __slots__ = ("pieces", "page", "top", "x0", "x1", "size", "bold", "text")

    def __init__(self, pieces: list):
        self.pieces = sorted(pieces, key=lambda l: l.x0)
        first = self.pieces[0]
        self.page = first.page
        self.top = min(p.top for p in self.pieces)
        self.x0 = min(p.x0 for p in self.pieces)
        self.x1 = max(p.x1 for p in self.pieces)
        self.size = max((p.size or 0.0) for p in self.pieces)
        self.bold = all(bool(p.all_bold) for p in self.pieces)
        self.text = _norm(" ".join(p.plain for p in self.pieces))

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


def _visual_rows(model, finder) -> list:
    """Page-1 content rows, furniture removed, in the page's own order."""
    rows: list = []
    for pm in model.pages[:_MAX_PAGES]:
        buckets: dict = {}
        loose: list = []
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue
            if line.row is not None:
                buckets.setdefault(line.row, []).append(line)
            else:
                loose.append(line)
        groups = list(buckets.values())
        for line in sorted(loose, key=lambda l: (l.top, l.x0)):
            for g in groups:
                if g[0].row is None and abs(g[0].top - line.top) <= 2.0:
                    g.append(line)
                    break
            else:
                groups.append([line])
        rows.extend(_Row(g) for g in groups)
    rows.sort(key=lambda r: (r.page, r.top, r.x0))
    return rows


# --------------------------------------------------------------------------
# the landmarks
# --------------------------------------------------------------------------

def _fence(page) -> object | None:
    """ill's masthead fence: a drawn rule in the court's one measure,
    centred on the page axis. A rule of the SAME measure off the axis is
    the footnote separator and is not this."""
    want, tol = _FENCE_AXIS
    for rule in page.h_rules:
        if not (_FENCE_MEASURE[0] <= rule.x1 - rule.x0 <= _FENCE_MEASURE[1]):
            continue
        off = (rule.x0 + rule.x1) / 2 - page.width / 2
        if abs(off - want) <= tol:
            return rule
    return None


def _seal(page) -> object | None:
    """The summary sheet's masthead is a raster: a square image on the page
    axis, in the top quarter, above every line of text."""
    first_text = min((l.top for l in page.lines if l.plain.strip()),
                     default=page.height)
    for im in (page.images or []):
        if im.x1 - im.x0 < _SEAL_MIN or im.bottom - im.top < _SEAL_MIN:
            continue
        if im.top > page.height * _SEAL_BAND or im.bottom > first_text:
            continue
        if abs((im.x0 + im.x1) / 2 - page.width / 2) <= _AXIS_TOL:
            return im
    return None


def _dockets(text: str) -> list:
    """The dockets a '(Docket No. …)' row names, in order, or []."""
    flat = _norm(text)
    if not (flat.startswith("(") and flat.endswith(")")):
        return []
    inner = flat[1:-1].strip()
    low = inner.lower()
    lead = next((d for d in _DOCKET_LEADS if low.startswith(d)), None)
    if lead is None:
        return []
    rest = inner[len(lead):].strip().rstrip(".")
    # '130596, 130597 cons.' — the consolidation tag closes the row.
    if rest.lower().endswith(" cons"):
        rest = rest[:-5].strip()
    out = [p.strip() for p in rest.split(",") if p.strip()]
    if not out or not all(p.replace("-", "").isalnum() for p in out):
        return []
    return out


# --------------------------------------------------------------------------
# the caption's grammar
# --------------------------------------------------------------------------

def _outer(text: str) -> str:
    """The caption without a trailing top-level parenthetical. Illinois
    prints a consolidated third-party action inside one ('MELISSA ANDREWS
    v. CARBON ON 26th, LLC, et al. (Martin Produce, Inc., Appellee, v.
    Jack Tuchten …, Appellants).') and it carries a pivot of its own."""
    flat = _norm(text).rstrip(".")
    if not flat.endswith(")"):
        return flat
    depth = 0
    for i in range(len(flat) - 1, -1, -1):
        if flat[i] == ")":
            depth += 1
        elif flat[i] == "(":
            depth -= 1
            if depth == 0:
                return flat[:i].strip().rstrip(",") or flat
    return flat


def _is_role(tag: str) -> bool:
    """Is this comma-separated tail a party STATUS label? A compound
    ('Respondents-Appellees') is one when every part of it is a role word or
    one of the modifiers a role compounds with."""
    parts = [p for p in tag.split("-") if p]
    return bool(parts) and all(p in _ROLES or p in _ROLE_MODS for p in parts)


def _strip_role(side: str) -> str:
    """A party name with its STATUS labels taken off the tail. Roles are a
    closed vocabulary; the name itself is never matched against words."""
    out = _norm(side).strip().strip(".,").strip()
    changed = True
    while changed and out:
        changed = False
        head, sep, tail = out.rpartition(",")
        if not sep:
            break
        tag = tail.strip().strip(".,").lower()
        if _is_role(tag) or tag == "et al":
            out, changed = head.strip().strip(",").strip(), True
    return out


def _sides(text: str) -> tuple | None:
    """The two party names either side of the caption's pivot. The pivot is
    a free-standing 'v.', so an abbreviation inside a name cannot be it."""
    parts = re.split(r"(?<=[\s\w.,;)’])\s+v\.\s+", text, maxsplit=1)
    if len(parts) != 2:
        return None
    left, right = _strip_role(parts[0]), _strip_role(parts[1])
    return (left, right) if left and right else None


# --------------------------------------------------------------------------
# the roster — read, never claimed
# --------------------------------------------------------------------------

def _bench_names(text: str) -> list:
    """Every judicial surname a roster statement names, in order.

    'Chief Justice Theis and Justices Neville, Overstreet, Holder White,
    Rochford, and O'Brien concurred in the judgment and opinion.' ->
    six names. The run opens on a BENCH TITLE and closes on the first
    lower-case word that is not a connector — which is always the
    statement's verb ('concurred', 'dissented', 'took'). Two-word
    surnames ('Holder White') survive because the run is split on its
    commas, not on its spaces.
    """
    names: list = []
    toks = _norm(text).split()
    i = 0
    while i < len(toks):
        title = None
        for t in _BENCH:
            n = len(t.split())
            got = [w.strip(",.").upper() for w in toks[i:i + n]]
            if got == t.upper().split():
                title, i = t, i + n
                break
        if title is None:
            i += 1
            continue
        run: list = []
        while i < len(toks):
            tok = toks[i]
            bare = tok.strip(",.:;")
            if bare.lower() == "and":
                run.append(tok)
                i += 1
                continue
            if not bare or not bare[:1].isupper():
                break
            run.append(tok)
            i += 1
            if tok.endswith((".", ":", ";")):
                break
        raw = " ".join(run)
        for part in re.split(r",|\band\b", raw):
            nm = part.strip().strip(".,:;").strip()
            if nm and nm[:1].isupper():
                names.append(nm)
    return names


def _read_roster(rows: list, body_x0: float, parser) -> tuple:
    """(panel_line, panel) from the court's own statements under the byline.

    The rows are NOT claimed: they sit inside the writing, and nothing is
    ever taken out of an assembled writing. A statement opens at the
    court's first-line indent (x=126) and runs over at the body rail
    (x=108), so the block is grouped by geometry rather than by sentence.
    """
    stmts: list = []
    for row in rows:
        if not stmts:
            if parser.parse(row.text) is None:
                continue
            stmts.append([row])            # the byline opens the block
            continue
        if row.bold or row.text.startswith("¶"):
            break                          # the 'OPINION' heading / the body
        if row.x0 > body_x0 + 6.0:
            stmts.append([row])
        else:
            stmts[-1].append(row)
    if not stmts:
        return None, []
    texts = [_norm(" ".join(r.text for r in s)) for s in stmts]
    panel: list = []
    for text in texts:
        if _RECUSED in text.lower():
            continue
        for nm in _bench_names(text):
            if nm not in panel:
                panel.append(nm)
    line = " ".join(texts[1:]) or None
    return line, panel


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    def __init__(self, rows, body_x0):
        self.rows = rows
        self.body_x0 = body_x0
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align: str = "C") -> None:
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


def _read_case(ctx: _Ctx, rows: list) -> bool:
    """The docket / caption / date block both papers share. Returns False
    when the block is not the shape the court prints."""
    docket: list = []
    caption: list = []
    dated = False
    for row in rows:
        if not docket:
            found = _dockets(row.text)
            if not found:
                return False               # the block opens on its docket
            docket = found
            ctx.emit(row, "docket")
            continue
        if row.text.lower().startswith(_FILED_LEAD):
            ctx.crit["decision_date"] = _norm(row.text)[len(_FILED_LEAD):] \
                .strip().rstrip(".")
            ctx.emit(row, "date")
            dated = True
            break
        caption.append(row.text)
        ctx.emit(row, "caption")
    if not (docket and caption and dated):
        return False
    ctx.crit["docket_number"] = docket[0]
    if len(docket) > 1:
        ctx.crit["other_dockets"] = docket[1:]
    ctx.crit["caption"] = caption
    flat = _norm(" ".join(caption))
    sides = _sides(_outer(flat))
    if sides:
        ctx.crit["parties"] = list(sides)
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    else:
        # 'In re MARRIAGE OF … and …' — a caption with no pivot is one
        # party, and inventing a second from the conjunction would name a
        # respondent the page does not.
        ctx.crit["parties"] = [_norm(flat.rstrip("."))]
        ctx.crit["case_name"] = _norm(flat.rstrip("."))
    return True


@decider("headmatter.read", court="ill")
def read_headmatter_ill(model, geom, **_):
    """Read one of ill's two papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 108.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = [r for r in _visual_rows(model, finder) if r.page == 1]
    if not rows:
        return NOTHING
    ctx = _Ctx(rows, body_x0)
    parser = BylineParser(ILL.byline)

    fence = _fence(page1)
    if fence is not None:
        return _read_cover(ctx, page1, fence, parser)
    if _seal(page1) is not None and not any(
            r.size >= _MASTHEAD_SIZE for r in rows):
        return _read_summary(ctx)
    return NOTHING


# ---- the ruled cover -----------------------------------------------------

def _read_cover(ctx: _Ctx, page1, fence, parser):
    head = [r for r in ctx.rows if r.top < fence.top]
    body = [r for r in ctx.rows if r.top > fence.top]
    # ABOVE THE FENCE: one citation row and a four-row masthead, on every
    # cover in the corpus. Anything else is not this paper.
    if len(head) != 5 or not all(r.bold for r in head):
        return NOTHING
    if head[0].size >= _MASTHEAD_SIZE \
            or not all(r.size >= _MASTHEAD_SIZE for r in head[1:]):
        return NOTHING
    # THE READER ENDS AT THE FIRST BYLINE.
    case_rows: list = []
    tail: list = []
    for row in body:
        if tail or parser.parse(row.text) is not None:
            tail.append(row)
            continue
        case_rows.append(row)
    if not tail:
        return NOTHING

    ctx.emit(head[0], "docket")             # the public-domain citation
    for row in head[1:]:
        ctx.emit(row, "court")
    ctx.crit["court"] = _norm(" ".join(r.text for r in head[1:]))
    # THE FENCE IS DRAWN, so it owns no line of its own — and the pipeline
    # merges a court's rows with core's leftovers by the LINE IDS an item
    # carries, which sends an id-less item to the foot of the block. The
    # rule is provenanced by the masthead row it closes, which is where the
    # page draws it; the tie then holds the reader's own order.
    ctx.items.append(m.Rule(prov=m.Prov(1, head[-1].ids), span="center"))
    if not _read_case(ctx, case_rows):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_COVER
    line, panel = _read_roster(tail, ctx.body_x0, parser)
    if line:
        ctx.crit["panel_line"] = line
    if panel:
        ctx.crit["panel"] = panel
    return ctx.result()


# ---- the case summary ----------------------------------------------------

def _read_summary(ctx: _Ctx):
    """The summary sheet: docket, caption, release date, and the ONE row
    naming the author of the opinion the sheet is about.

    The sheet is prose ABOUT a decision, not the decision — the opinion
    itself is filed separately (butler is the summary; butler_1 is the
    29-page opinion). v1 read the whole sheet as headmatter and typed the
    paper a notice, which is the right answer and the one core cannot yet
    take: `_body_expected` is computed from the CLASSIFIER's doc type
    before `doc_type_final` is honoured, so a claim that leaves no writing
    is withdrawn whole. So the reader takes the four rows the two papers
    share plus the author statement, and leaves the synopsis where it is.

    THE AUTHOR STATEMENT is the row under the release date: one row at the
    body rail, short of the text measure, standing off from the prose
    below it (28pt against a 16pt leading). The prose that follows opens
    at the same rail and runs the full measure.
    """
    case_rows: list = []
    tail: list = []
    for row in ctx.rows:
        if tail or row.text.lower().startswith(_FILED_LEAD):
            tail.append(row)
            continue
        case_rows.append(row)
    if len(tail) < 3:
        return NOTHING
    if not _read_case(ctx, case_rows + tail[:1]):
        return NOTHING
    author, first_prose = tail[1], tail[2]
    # The statement stops short of the measure the prose beneath it fills.
    if author.x1 >= first_prose.x1 - 12.0:
        return NOTHING
    ctx.emit(author, "panel", "L")
    ctx.crit["judges"] = author.text.rstrip(".")
    ctx.crit["headmatter_style"] = STYLE_SUMMARY
    ctx.crit["court"] = ILL.court_label
    return ctx.result()
