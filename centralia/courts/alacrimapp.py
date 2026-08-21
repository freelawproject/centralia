"""Court of Criminal Appeals of Alabama ('alacrimapp').

Everything unique to alacrimapp lives here. It imports core, never another
court file, and no other court file imports it.

THE FAMILY. This court sets on the SAME two Alabama appellate templates the
Supreme Court sets on (see courts/ala.py), and the contracts are named the
same so the family reads as one:

    'fenced cover' (28 of 30) — the opinion slip. The masthead sits a
    quarter to a third of the way down the page (top 194-248 on a 792pt
    page) at 22pt, under the reporter's four-row revision notice; the
    docket stands between a TYPED underscore fence PAIR, 175.0-175.2pt
    wide and centred on the page axis to 0.0. Every row from the sitting
    down is centred, and the caption block is set BOLD — the only roman
    rows in the corpus are the paper naming itself:

        Rel: May 1, 2026                       the release stamp (dropped)
        Notice: This opinion is subject …      the reporter's notice (dropped)
        Alabama Court of Criminal Appeals      22pt, a third of the way down
        OCTOBER TERM, 2025-2026                the sitting
        _________________________              a fence ON THE AXIS…
        CR-2025-0003                           …around the docket…
        _________________________              …and one under it
        Antonio Deandre Hawkins                the caption: a party…
        v.                                     …the pivot…
        State of Alabama                       …and the other side
        Appeal from Jefferson Circuit Court    the origin
        (CC-06-1430.62)                        and its docket
        On Return to Remand                    the paper, ROMAN (optional)
        PER CURIAM.                            …and the writing starts

    'engraved certificate' (2 of 30) — the clerk's paper. A 20pt masthead
    pinned in the PAGE'S TOP BAND (top 76.5 of 792 — under 10% down), the
    release date centred under it, the docket at the body rail, and the
    caption as one justified paragraph at that same rail. Nothing is
    fenced. The clerk's centred heading — 'NOTICE' here, 'CERTIFICATE OF
    JUDGMENT' on ala — is the WRITING's, and the reader stops at it
    without claiming it:

        ALABAMA COURT OF CRIMINAL APPEALS      20pt, in the top band
        January 9, 2026                        the date, on the page axis
        CR-2025-0113                           the docket, at the rail
        Dolphus Atchison v. State of Alabama   the caption paragraph,
        (Appeal from Madison Circuit Court:    at the rail, wrapped
        CC-23-1756)
        NOTICE                                 …and the writing starts

THE DISPATCH is one question about page 1: is there a row set above 18pt,
and if so WHERE. In the top tenth it is the clerk's paper; further down,
with a fence pair beneath it, the opinion slip; a record answering
neither is not one of these papers and gets NOTHING.

WHY THE DATE IS NOT READ BY SIZE. ala's certificate sets its release date
at 16pt; this court sets it at 12pt — the same size as its body — and the
two clerk's papers are single sheets on which `geometry.measure` returns
nothing at all. The date is therefore read by POSITION: the centred rows
between the masthead and the rail-set docket. Same reason the cover reads
its pre-masthead band by position rather than by size (a two-page slip
measures its body at the notice's 9pt).
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.evidence import NOTHING, decider
from . import PROFILES, register

# The profile belongs beside the reader. Registration is guarded because
# the registry may still carry the table entry this file supersedes.
_PROFILE = CourtProfile(
    "alacrimapp", "Court of Criminal Appeals of Alabama",
    # 'COLE, Judge.' / 'WINDOM, Presiding Judge.' / 'PER CURIAM.'
    byline=BylineGrammar(style="prose", titles=("Judge", "Presiding Judge")),
)
ALACRIMAPP = PROFILES.get("alacrimapp") or register(_PROFILE)

STYLE_CERT = "engraved certificate"
STYLE_COVER = "fenced cover"

# ---- alacrimapp's declared facts (measured over its 30 records) ----------
# THE MASTHEAD. 20pt on the clerk's paper, 22pt on all 28 covers. The
# cover's body is 14pt; the clerk's paper's is 12pt.
_MASTHEAD_SIZE = 18.0
# WHERE THE MASTHEAD STANDS names the paper: the clerk's paper pins it at
# top 76.5 on a 792pt page (9.7%); the cover sets it at 194-248 (24-31%).
_TOP_BAND = 0.15
# THE COVER'S DOCKET FENCE: two typed underscore rules per record, 175.0
# or 175.2pt wide, centred on the page axis to 0.0.
_FENCE_MEASURE = (165.0, 186.0)
_FENCE_AXIS = 6.0
# THE COVER CENTRES EVERY ROW on the page axis.
_AXIS_TOL = 4.0
# HOW FAR THE BLOCK MAY RUN. Every cover in the corpus signs on page 1;
# the bound is generous so a consolidation that carried its fence pairs
# over a page break would still be read.
_MAX_PAGES = 12
# A row is AT THE RAIL when it starts on the body's left edge.
_RAIL_TOL = 1.5

_TYPED_RULE = re.compile(r"^_{6,}$")
# 'CR-2025-0113' — this court's own docket, and only this court's.
_DOCKET = re.compile(r"^CR[-‑]\d{4}[-‑]\d{3,5}$")
# 'CC-06-1430.62' / 'JU-24-372.01' / 'DC-15-3187' / 'CC-92-25.69' — the
# number the court BELOW gave the case, in every form this court prints.
_LOWER_DOCKET = re.compile(
    r"\b[A-Z]{2,4}[-‑]\d{2,4}(?:[-‑]\d{1,6})?(?:\.\d{2})?\b")
# 'Rel: May 1, 2026' — the release stamp, furniture on the cover.
_REL = "rel:"
# The sitting: 'OCTOBER TERM, 2025-2026'. A closed structural form — the
# word TERM over a year — never a court or party name.
_TERM = re.compile(r"^[A-Z]+\s+TERM,?\s+\d{4}(?:\s*[-‑]\s*\d{4})?\.?$")
# THE ORIGIN LEADERS: a closed vocabulary of the ways a court states where
# a case came from. Never a court NAME.
_ORIGIN_LEADERS = ("appeal from", "appeals from", "on appeal from",
                   "certified question from", "certified questions from",
                   "on certified question from",
                   "review of", "on review from")
# THE PAPER THE PETITIONER FILED, printed in caps inside the caption.
_PETITION_LEAD = "PETITION FOR"
# 'In re' opens the case BELOW, not the origin — both are parenthesised.
_IN_RE = re.compile(r"^\(\s*in\s+re\b", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _docket_row(text: str) -> list:
    """The dockets a fenced row names, in order, or [] when it names none."""
    parts = [p for p in re.split(r"[,;]|\band\b", _norm(text).rstrip("."))
             if p.strip()]
    out = [_norm(p) for p in parts]
    return out if out and all(_DOCKET.match(t) for t in out) else []


# --------------------------------------------------------------------------
# the visual row — pdfio splits a justified line at its wide gaps
# --------------------------------------------------------------------------

class _Row:
    """One VISUAL row: every piece the page set on the same baseline."""

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

    def markup(self):
        out = ""
        for p in self.pieces:
            piece = line_markup(p)
            out = (out.rstrip() + "  " + piece.lstrip()) if out.strip() \
                else piece
        return out


def _visual_rows(model, finder, max_pages: int) -> list:
    """Content rows, furniture removed, in the page's own order."""
    rows: list = []
    for pm in model.pages[:max_pages]:
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
        # pdfio leaves `row` unset on pages it did not have to split; fall
        # back to a baseline test, which is what `row` encodes anyway.
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

def _is_fence(row: _Row, page_width: float) -> bool:
    """The cover's docket fence: a typed underscore rule in this court's one
    measure, centred on the page axis."""
    if not _TYPED_RULE.match(row.text.replace(" ", "")):
        return False
    if not (_FENCE_MEASURE[0] <= row.x1 - row.x0 <= _FENCE_MEASURE[1]):
        return False
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _FENCE_AXIS


def _on_axis(row: _Row, page_width: float) -> bool:
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _AXIS_TOL


def _release_date(model) -> str | None:
    """'Rel: May 1, 2026' -> 'May 1, 2026'. The stamp is furniture; the date
    printed on it is still the day the court released the paper."""
    page1 = model.pages[0]
    for line in page1.lines:
        flat = _norm(line.plain)
        if flat[:len(_REL)].lower() == _REL and line.top < page1.height * 0.2:
            rest = flat[len(_REL):].strip()
            if rest:
                return rest
    return None


def _lower_dockets(text: str) -> list:
    return [_norm(t) for t in _LOWER_DOCKET.findall(text)]


# --------------------------------------------------------------------------
# the caption's own grammar — shared by both papers
# --------------------------------------------------------------------------

def _split_parens(text: str) -> list:
    """Top-level segments: ('T', prose) and ('P', '(…)') in page order."""
    segs: list = []
    depth = 0
    buf = ""
    for ch in text:
        if ch == "(":
            if depth == 0 and buf.strip():
                segs.append(("T", buf.strip()))
                buf = ""
            depth += 1
            buf += ch
        elif ch == ")":
            if depth:
                depth -= 1
            buf += ch
            if depth == 0:
                segs.append(("P", buf.strip()))
                buf = ""
        else:
            buf += ch
    if buf.strip():
        segs.append(("T", buf.strip()))
    return segs


def _petition_split(text: str) -> tuple:
    """('Ex parte K.M.', 'PETITION FOR WRIT OF CERTIORARI …') — the parties,
    and the paper they filed. The title is found by its printed LEADER,
    never by 'this looks like capitals': a petitioner initialled 'M.C.' is
    capitals too, and this court initials most of its juvenile appellants."""
    i = text.find(_PETITION_LEAD)
    if i < 0:
        return text.strip(), None
    return text[:i].strip(), _norm(text[i:]).rstrip(".,;")


def _sides(text: str) -> tuple | None:
    """The two party names either side of the caption's pivot. The pivot is
    a free-standing 'v.', so an abbreviation inside a name cannot be it."""
    parts = re.split(r"(?<=[\s\w.,;)])\s+v\.?\s+", text, maxsplit=1)
    if len(parts) != 2:
        return None
    left, right = _norm(parts[0]).rstrip(",; "), _norm(parts[1]).rstrip(",; ")
    return (left, right) if left and right else None


def _name_from(ctx, parties_text: str) -> None:
    sides = _sides(parties_text)
    if sides:
        ctx.crit["parties"] = list(sides)
        ctx.crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    elif parties_text:
        ctx.crit["parties"] = [parties_text]
        ctx.crit["case_name"] = parties_text


def _record_origin(ctx, printed: str) -> None:
    """The origin as the page prints it, plus the numbers inside it."""
    flat = _norm(printed)
    if not flat:
        return
    prev = ctx.crit.get("lower_court")
    ctx.crit["lower_court"] = f"{prev} {flat}" if prev else flat
    for dk in _lower_dockets(flat):
        if dk not in ctx.crit.setdefault("lower_court_docket", []):
            ctx.crit["lower_court_docket"].append(dk)


def _read_caption_paragraph(ctx, text: str) -> None:
    """The clerk's paper's caption: one justified paragraph.

        <parties> [PETITION FOR …] [(In re: <case below>)] (<origin>).

    Each bracketed part is optional and each is read from its own printed
    mark — the petition's leader, 'In re', the parenthesis."""
    segs = _split_parens(text.rstrip().rstrip(".").rstrip())
    if not segs:
        return
    lead = segs[0][1] if segs[0][0] == "T" else ""
    parties_text, petition = _petition_split(lead)
    if petition:
        ctx.crit["history"] = petition
    _name_from(ctx, parties_text)
    for kind, seg in segs[1:]:
        if kind != "P":
            # An unbalanced parenthesis: the tail belongs to the group
            # before it.
            _record_origin(ctx, seg)
            continue
        if _IN_RE.match(seg):
            continue                      # the case below, not the origin
        inner = seg.strip()
        if inner.startswith("("):
            inner = inner[1:]
        if inner.endswith(")"):
            inner = inner[:-1]
        _record_origin(ctx, inner)


def _join_wrapped(rows: list) -> str:
    """The caption paragraph as one string. A row that ENDS on a hyphen
    broke a docket across the measure ('… Madison Circuit Court: CC-23-' /
    '1756)') and must close up, or the number reads as two."""
    out = ""
    for text in rows:
        flat = _norm(text)
        if not out:
            out = flat
        elif out.endswith("-") or out.endswith("‑"):
            out += flat
        else:
            out += " " + flat
    return out


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """What the two walks share: the page models and the emit buffer."""

    def __init__(self, model, geom, rows, body_x0, body_size):
        self.model = model
        self.geom = geom
        self.rows = rows
        self.body_x0 = body_x0
        self.body_size = body_size
        self.pages = {pm.number: pm for pm in model.pages}
        self.items: list = []
        self.consumed: set = set()
        self.dropped: list = []
        self.crit: dict = {}

    def emit(self, row: _Row, role: str, align: str | None = None) -> None:
        pm = self.pages[row.page]
        if align is None:
            align = "C" if (_on_axis(row, pm.width)
                            and row.x0 > self.body_x0 + _RAIL_TOL) else "L"
        self.items.append(m.HmLine(
            text=row.markup(), prov=m.Prov(row.page, row.ids),
            align=m.Align(align), x0=row.x0, size=row.size,
            bold=row.bold, role=role))
        self.consumed.update(row.ids)

    def rule(self, row: _Row) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids),
                                 typed=True, span="center"))
        self.consumed.update(row.ids)

    def drop(self, rows: list, kind: str) -> None:
        if not rows:
            return
        self.dropped.append(m.Dropped(
            text=" ".join(r.text for r in rows)[:1200],
            prov=m.Prov(rows[0].page,
                        tuple(i for r in rows for i in r.ids)),
            kind=kind))
        for r in rows:
            self.consumed.update(r.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


@decider("headmatter.read", court="alacrimapp")
def read_headmatter_alacrimapp(model, geom, **_):
    """Read one of this court's two papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if not rows:
        return NOTHING
    ctx = _Ctx(model, geom, rows, body_x0, body_size)

    p1 = [r for r in rows if r.page == 1]
    big = [r for r in p1 if r.size >= _MASTHEAD_SIZE]
    fences = [r for r in p1 if _is_fence(r, page1.width)]
    # THE MASTHEAD'S POSITION NAMES THE PAPER.
    if big and big[0].top < _TOP_BAND * page1.height and not fences:
        return _read_certificate(ctx, big[0])
    if big and len(fences) >= 2:
        return _read_cover(ctx, big[0])
    return NOTHING


# ---- the engraved certificate -------------------------------------------

def _read_certificate(ctx: _Ctx, masthead: _Row):
    """The clerk's paper. Masthead, date, docket, caption paragraph — and
    the reader stops at the clerk's centred heading, which is the writing's.

    The date is read by POSITION, not by size: this court sets it at the
    body's own 12pt, and its clerk's papers are single sheets on which
    `geometry.measure` declines to measure anything at all."""
    parser = BylineParser(ALACRIMAPP.byline)
    page1 = ctx.model.pages[0]
    date = None
    docket = None
    caption: list = []
    ended = False
    for row in ctx.rows:
        if row.page != 1 or row.top < masthead.top:
            continue
        if row is masthead:
            ctx.crit["court"] = row.text
            ctx.emit(row, "court", "C")
            continue
        if docket is None:
            found = _docket_row(row.text)
            if found:
                docket = found
                ctx.emit(row, "docket", "L")
                continue
            # BETWEEN THE MASTHEAD AND THE DOCKET the page prints one
            # centred row and one only: the day it released the paper.
            if date is not None or not _on_axis(row, page1.width):
                return NOTHING
            date = row.text.rstrip(".")
            ctx.emit(row, "date", "C")
            continue
        # THE CAPTION ENDS WHERE THE PAGE LEAVES THE RAIL — the clerk's
        # centred heading ('NOTICE') is the WRITING's, and the reader does
        # not take it.
        if row.x0 > ctx.body_x0 + _RAIL_TOL or parser.parse(row.text):
            ended = True
            break
        caption.append(row.text)
        ctx.emit(row, "caption", "L")
    if not (ended and docket and caption):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_CERT
    ctx.crit["docket_number"] = docket[0]
    if len(docket) > 1:
        ctx.crit["other_dockets"] = docket[1:]
    if date:
        ctx.crit["decision_date"] = date
    ctx.crit["caption"] = caption
    _read_caption_paragraph(ctx, _join_wrapped(caption))
    return ctx.result()


# ---- the fenced cover ----------------------------------------------------

def _read_cover(ctx: _Ctx, masthead: _Row):
    parser = BylineParser(ALACRIMAPP.byline)
    dockets: list = []
    groups: list = []                     # caption rows, one list per case
    in_docket = False
    in_title = False
    in_origin = False
    signed = False
    started = False
    notice: list = []
    for row in ctx.rows:
        if not started:
            if row is masthead:
                started = True
                ctx.crit["court"] = row.text
                ctx.emit(row, "court", "C")
                continue
            # A READER THAT CLAIMS THE REGION INHERITS ITS FURNITURE.
            # THE COVER OPENS ON ITS MASTHEAD: everything printed above it
            # is the release stamp and the reporter's revision notice, and
            # POSITION says so — not size. A two-page slip measures its
            # body at the notice's 9pt, and on exactly those records core's
            # own stamp test fails too ('Rel: March 27, 2026' rendered as
            # the first headmatter row of william_chad_randolph).
            notice.append(row)
            continue
        pm = ctx.pages[row.page]
        if _is_fence(row, pm.width):
            ctx.rule(row)
            in_docket = not in_docket
            in_title = in_origin = False
            if not in_docket:
                groups.append([])
            continue
        if parser.parse(row.text) is not None:
            signed = True
            break
        if in_docket:
            found = _docket_row(row.text)
            if not found:
                return NOTHING            # the fence pair holds a docket
            dockets.extend(found)
            ctx.emit(row, "docket", "C")
            continue
        if not groups:
            # Above the first fence the court names its sitting.
            if _TERM.match(row.text.upper()):
                ctx.emit(row, "date", "C")
                continue
            return NOTHING
        # THE COVER SETS ITS CAPTION BLOCK IN BOLD. A ROMAN row inside it
        # is the paper naming itself — 'On Return to Remand', 'On
        # Application for Rehearing', 'After Remand from the Alabama
        # Supreme Court'. Measured: every roman row in the 28 covers is
        # one of those three.
        if not row.bold:
            ctx.crit.setdefault("title", row.text.rstrip("."))
            ctx.emit(row, "title", "C")
            in_title = in_origin = False
            continue
        low = row.text.lower()
        opens_origin = any(low.startswith(lead) for lead in _ORIGIN_LEADERS)
        if not opens_origin and row.text.startswith("(") \
                and not _IN_RE.match(row.text):
            opens_origin = bool(_lower_dockets(row.text.strip("()")))
        # AN ORIGIN STATEMENT WRAPS: 'Appeal from Jefferson Circuit Court,
        # Bessemer Division' / '(CC-20-466)' is one statement in two rows.
        # Once the origin opens it runs to the fence that opens the next
        # case, or to the byline.
        if opens_origin or in_origin:
            in_origin = True
            if len(groups) == 1:          # the lead case's origin
                _record_origin(ctx, row.text)
            else:
                for dk in _lower_dockets(row.text):
                    if dk not in ctx.crit.setdefault("lower_court_docket",
                                                     []):
                        ctx.crit["lower_court_docket"].append(dk)
            ctx.emit(row, "lower-court", "C")
            in_title = False
            continue
        if row.text.startswith(_PETITION_LEAD) or (
                in_title and row.text == row.text.upper()):
            # …of the LEAD case only: a consolidation repeats the same
            # petition title once per case.
            if len(groups) == 1:
                prev = ctx.crit.get("history")
                ctx.crit["history"] = (f"{prev} {row.text}" if prev
                                       else row.text)
            in_title = True
            ctx.emit(row, "title", "C")
            continue
        in_title = False
        groups[-1].append(row.text)
        ctx.emit(row, "caption", "C")
    if not (signed and dockets and groups and any(groups)):
        return NOTHING
    ctx.drop([r for r in notice if r.text[:len(_REL)].lower() == _REL],
             "stamp")
    ctx.drop([r for r in notice if r.text[:len(_REL)].lower() != _REL],
             "notice")
    ctx.crit["headmatter_style"] = STYLE_COVER
    ctx.crit["docket_number"] = dockets[0]
    if len(dockets) > 1:
        ctx.crit["other_dockets"] = dockets[1:]
    caption = [t for g in groups for t in g]
    ctx.crit["caption"] = caption
    lead = next((g for g in groups if g), [])
    _name_from(ctx, _cover_parties(lead))
    date = _release_date(ctx.model)
    if date:
        ctx.crit["decision_date"] = date
    return ctx.result()


def _cover_parties(rows: list) -> str:
    """The lead case's parties, built from the rows either side of the
    cover's own pivot row — never by joining the caption wholesale.

    A pivot on the cover is a row of its own ('v.'). THE CASE BELOW is
    parenthesised and carries a pivot of its own; the parenthesis opens
    it, and nothing from there on names a party to THIS case."""
    left: list = []
    right: list = []
    side = left
    for text in rows:
        flat = _norm(text)
        if flat.startswith("("):
            break
        if side is left and flat.rstrip(".").lower() == "v":
            side = right
            continue
        side.append(flat)
    if right:
        return f"{_norm(' '.join(left)).rstrip(',; ')} v. " \
               f"{_norm(' '.join(right)).rstrip(',; ')}"
    return _norm(" ".join(left)).rstrip(",; ")
