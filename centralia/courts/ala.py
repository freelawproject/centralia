"""Supreme Court of Alabama ('ala').

Everything unique to ala lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT. Alabama prints THREE papers, and each one is named by where
it sets its masthead and how it fences its docket. No word on the page
decides which:

    'engraved certificate' (270 of 467) — the clerk's certificate of
    judgment and its mandamus-order twin. A 20pt masthead pinned in the
    PAGE'S TOP BAND (top 40.5 of 792 — 5% down), a 16pt release date
    centred under it, the docket at the body rail, and the caption set as
    one JUSTIFIED PARAGRAPH at that same rail. Nothing is fenced:

        IN THE SUPREME COURT OF ALABAMA        20pt, in the top band
        July 11, 2025                          16pt, on the page axis
        SC-2024-0534                           the docket, at the rail
        Bradley C. Lewis v. Lily T. Ojano-     the caption paragraph,
        Bracco; … (Appeal from Jefferson       at the rail, wrapped and
        Circuit Court: CV-17-900540).          justified
        CERTIFICATE OF JUDGMENT                …and the writing starts

    THE CAPTION ENDS WHERE THE PAGE LEAVES THE RAIL. The clerk's heading
    ('CERTIFICATE OF JUDGMENT' on 262 records, 'ORDER' on 8) is centred,
    and it is the writing's, not the headmatter's — the reader stops
    there without claiming it.

    'fenced cover' (136 of 467) — the opinion slip. The masthead moves
    DOWN the page (top 256–270, a third of the way) and is set 22–25pt
    under the reporter's notice; the docket stands between a TYPED
    underscore fence PAIR, 175.0–175.2pt wide and centred on the page
    axis to the point (measured: 385 of 388 fences at offset 0.0). The
    pair REPEATS once per consolidated case:

        SUPREME COURT OF ALABAMA               22pt, mid-page
        OCTOBER TERM, 2025-2026                the sitting
        _________________________              a fence ON THE AXIS…
        SC-2024-0810                           …around the docket…
        _________________________              …and one under it
        790 Montclair, LLC                     the caption: a party…
        v.                                     …the pivot…
        Birmingham Metro, LLC; …               …and the other side
        Appeal from Jefferson Circuit Court    the origin
        (CV-23-903446)                         and its docket
        SELLERS, Justice.                      …and the writing starts

    EVERY ROW ON THIS COVER IS CENTRED ON THE PAGE AXIS — measured over
    the 136 covers, all but a handful of block rows sit at offset 0.0 and
    the rest at 2.0. A party list long enough to fill the measure is
    still a centred caption row, so the cover declares its alignment
    rather than inferring it per row. It also sets the whole block in
    BOLD; the only three roman rows in the corpus are the paper naming
    itself ('On Rehearing Ex Mero Motu').

    A 15-way mandamus consolidation carries its fence pairs and captions
    to PAGE 11; the reader is bounded at 12 and stops at the byline.

    'judicial-department list' (61 of 467) — the release list for a
    no-opinion affirmance. NO masthead above body size at all: the court
    names itself in three body-size rows on the axis, then sets the
    docket and the caption paragraph at the rail, exactly as the
    certificate does.

        STATE OF ALABAMA -- JUDICIAL DEPARTMENT
        THE SUPREME COURT
        OCTOBER TERM, 2024-2025
        SC-2024-0548                           the docket, at the rail
        1 Oak Grand, LLC v. Richard L. …       the caption paragraph
        McCOOL, Justice.                       …and the writing starts

THE DISPATCH is a single question about page 1: is there a row set above
18pt, and if so WHERE. In the top tenth it is the certificate; further
down, with a fence pair beneath it, the cover; no such row at all, the
list. Over 467 records that test agrees with the papers' own wording on
every one. A record that answers none of the three is not one of these
papers and gets NOTHING.

WHAT THE READER DOES NOT TOUCH. The 'Rel: <date>' release stamp and the
four-row reporter's notice are core's furniture and core's notice drop;
the reader reads the release date off the stamp but claims neither. ala
prints NO appearance of counsel anywhere in the corpus.
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

ALA = register(CourtProfile(
    "ala", "Supreme Court of Alabama",
    # 'McCOOL, Justice.' / 'STEWART, Chief Justice.' / 'PER CURIAM.'
    byline=BylineGrammar(style="prose", titles=("Justice",)),
))

STYLE_CERT = "engraved certificate"
STYLE_COVER = "fenced cover"
STYLE_LIST = "judicial-department list"

# ---- ala's declared facts (measured over the 467-record corpus) ----------
# THE MASTHEAD. 20pt on the certificate, 22pt (126) or 25pt (10) on the
# cover, absent from the list. The body is 14pt everywhere.
_MASTHEAD_SIZE = 18.0
# WHERE THE MASTHEAD STANDS names the paper: the certificate pins it at
# top 40.5 on a 792pt page (5%); the cover sets it at 256–270 (32–34%).
_TOP_BAND = 0.10
# THE CERTIFICATE'S RELEASE DATE is the only other row above body size.
_DATE_SIZE = 15.5
# THE COVER'S DOCKET FENCE: 388 typed underscore rules over the corpus,
# 387 of them 175.0–175.2pt wide and 385 centred on the page axis to 0.0.
_FENCE_MEASURE = (165.0, 186.0)
_FENCE_AXIS = 6.0
# THE COVER CENTRES EVERY ROW on the page axis (offset 0.0 on all but a
# handful, 2.0 on those).
_AXIS_TOL = 4.0
# HOW FAR THE BLOCK MAY RUN. The 15-way Methodist Church mandamus
# consolidation carries its caption to page 11; nothing needs a twelfth.
_MAX_PAGES = 12
# A row is AT THE RAIL when it starts on the body's left edge; the
# certificate and the list set their captions there and nothing else.
_RAIL_TOL = 1.5

_TYPED_RULE = re.compile(r"^_{6,}$")
# 'SC-2024-0548' — this court's own docket, and only this court's. Two
# appeals consolidated under ONE fence pair are printed as a list
# ('SC-2025-0346 and SC-2025-0357'), so the row is read as the sequence of
# dockets it names rather than as a single token.
_DOCKET = re.compile(r"^SC[-‑]\d{4}[-‑]\d{3,5}$")
# 'CV-17-900540' / 'CC-18-4334.60' / 'CL-2024-0668' / 'ASB-2023-1719' —
# the number a court BELOW gave the case, in every form ala prints.
_LOWER_DOCKET = re.compile(
    r"\b[A-Z]{2,4}[-‑]\d{2,4}(?:[-‑]\d{1,6})?(?:\.\d{2})?\b"
    # …and the FEDERAL district number a certified question comes with
    # ('7:23-cv-00692-ACA' / '1:22-cv-01165-RDP').
    r"|\b\d{1,2}:\d{2}[-‑][a-z]{2}[-‑]\d{3,6}(?:[-‑][A-Z]{2,4})?\b")
# 'Rel: June 13, 2025' — the release stamp, which core drops as furniture.
_REL = "rel:"
# The sitting, printed on the cover and on the list: 'OCTOBER TERM,
# 2025-2026' / 'SPECIAL TERM, 2025'. A closed structural form — the word
# TERM over a year — never a court or party name.
_TERM = re.compile(r"^[A-Z]+\s+TERM,?\s+\d{4}(?:\s*[-‑]\s*\d{4})?\.?$")
# THE ORIGIN LEADERS: a closed vocabulary of the ways a court states where
# a case came from. Never a court NAME.
_ORIGIN_LEADERS = ("appeal from", "appeals from", "on appeal from",
                   "certified question from", "certified questions from",
                   "on certified question from",
                   "review of", "on review from")
# THE PAPER THE PETITIONER FILED, printed in caps inside the caption:
# 'PETITION FOR WRIT OF CERTIORARI TO THE COURT OF CRIMINAL APPEALS'.
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
    """One VISUAL row: every piece the page set on the same baseline.

    ala justifies its caption paragraph, and pdfplumber breaks a justified
    row at the widest gaps ('Ex parte Donald Vester Robbins, Jr.' at
    x0=72 | 'PETITION FOR WRIT OF' at x0=342). Read piecewise, the second
    piece leaves the rail and ends the caption three rows early.
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
    """The cover's docket fence: a typed underscore rule in ala's one
    measure, centred on the page axis."""
    if not _TYPED_RULE.match(row.text.replace(" ", "")):
        return False
    if not (_FENCE_MEASURE[0] <= row.x1 - row.x0 <= _FENCE_MEASURE[1]):
        return False
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _FENCE_AXIS


def _on_axis(row: _Row, page_width: float) -> bool:
    return abs((row.x0 + row.x1) / 2 - page_width / 2) <= _AXIS_TOL


def _release_date(model) -> str | None:
    """'Rel: June 13, 2025' -> 'June 13, 2025'. The stamp is core's to drop;
    the date on it is still the day the court released the paper."""
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
# the caption's own grammar — shared by all three papers
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
    """('Ex parte K.M.', 'PETITION FOR WRIT OF CERTIORARI TO THE COURT OF
    CIVIL APPEALS') — the parties, and the paper they filed. The title is
    found by its printed LEADER, never by 'this looks like capitals': a
    petitioner initialled 'K.M.' is capitals too."""
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
    """The origin, split into the TRIBUNALS and their NUMBERS.

    Alabama's certiorari cover states the whole route below in one
    parenthesis, one tribunal per semicolon and each naming its own number
    after a colon:

        (Mobile Circuit Court: CC-19-3497; Criminal Appeals: CR-2024-0009)
        (DeKalb Juvenile Court: JU-21-146.02; Civil Appeals: CL-2025-0050)

    Recorded whole, `lower_court` carried both courts AND both dockets in
    one string while `lower_court_docket` held the same numbers again — so
    the field could not answer 'which court' without re-parsing it. The
    colon is the court's own separator, so each side goes where it belongs:
    the tribunal to `lower_court`, its number to `lower_court_docket`
    (which already deduplicates). A group with no colon is a court that
    states no number and is recorded as printed."""
    flat = _norm(printed)
    if not flat:
        return
    courts: list[str] = []
    for group in flat.split(";"):
        group = group.strip()
        if not group:
            continue
        court, sep, number = group.partition(":")
        court = court.strip().rstrip(",")
        if sep and _lower_dockets(number):
            if court:
                courts.append(court)
        else:
            courts.append(group)      # states no number of its own
    prev = ctx.crit.get("lower_court")
    joined = "; ".join(courts)
    if joined:
        ctx.crit["lower_court"] = f"{prev}; {joined}" if prev else joined
    for dk in _lower_dockets(flat):
        if dk not in ctx.crit.setdefault("lower_court_docket", []):
            ctx.crit["lower_court_docket"].append(dk)


# What each printed part of the caption paragraph IS. The petition names the
# paper; '(In re: …)' names the case below; the last parenthesis is the route
# below. Roles, so the block reads as the four things the court set.
_PART_ROLE = {"parties": "caption", "petition": "title",
              "below": "case-info", "origin": "lower-court"}


def _read_caption_paragraph(ctx, text: str, rows: list | None = None) -> None:
    """The certificate's and the list's caption: one justified paragraph.

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
    # …and lay the parts out, one per line, where the caller handed us the
    # rows they came from (see _Ctx.part).
    if rows:
        if parties_text:
            ctx.part(rows, _norm(parties_text), _PART_ROLE["parties"])
        if petition:
            ctx.part(rows, _norm(petition), _PART_ROLE["petition"])
    for kind, seg in segs[1:]:
        if kind != "P":
            # The court's own unbalanced parenthesis (three records set
            # '))' or drop a ')'): the tail belongs to the group before it.
            _record_origin(ctx, seg)
            continue
        if _IN_RE.match(seg):
            # THE CASE BELOW is the other half of what this paper is about,
            # and discarding it lost the only statement of it on the page:
            # 'Ex parte Alvin Ray Allen' names the petitioner, and only
            # '(In re: Alvin Ray Allen v. State of Alabama)' names the case
            # the certiorari petition concerns. Kept beside the petition's
            # own title, which is what the court prints it next to.
            below = _norm(seg).strip("()")
            if below:
                prev = ctx.crit.get("history")
                ctx.crit["history"] = (f"{prev} ({below})" if prev
                                       else f"({below})")
                if rows:
                    ctx.part(rows, f"({below})", _PART_ROLE["below"])
            continue
        inner = seg.strip()
        if inner.startswith("("):
            inner = inner[1:]
        if inner.endswith(")"):
            inner = inner[:-1]
        _record_origin(ctx, inner)
        if rows and _norm(inner):
            ctx.part(rows, f"({_norm(inner)})", _PART_ROLE["origin"])


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

class _Ctx:
    """What the three walks share: the page models and the emit buffer."""

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

    def part(self, rows: list, text: str, role: str) -> None:
        """One PART of a justified caption paragraph, on a line of its own.

        Alabama sets its certiorari caption as one justified block —
        petitioner, the petition's title, the case below, then the route
        below, each closing on its own printed mark. Rendered as the page
        wraps it, a single line carries the end of the case name AND the
        start of the origin, so every row could only be tagged `caption`
        and the parts the court plainly distinguishes were invisible. The
        user asked for them on separate lines (2026-08-19).

        The page's ORDER is preserved and no text is added or dropped; what
        changes is where the line breaks fall. Provenance is the set of rows
        the part spans, which is approximate where a part opens mid-row —
        the claim stays total because every row's ids are still placed."""
        ids = tuple(i for r in rows for i in r.ids)
        first = rows[0]
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, ids),
            align=m.Align("L"), x0=first.x0, size=first.size,
            bold=first.bold, role=role))
        self.consumed.update(ids)

    def rule(self, row: _Row) -> None:
        self.items.append(m.Rule(prov=m.Prov(row.page, row.ids),
                                 typed=True, span="center"))
        self.consumed.update(row.ids)

    def result(self):
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


@decider("headmatter.read", court="ala")
def read_headmatter_ala(model, geom, **_):
    """Read one of ala's three papers, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 14.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _visual_rows(model, finder, _MAX_PAGES)
    if not rows:
        return NOTHING
    ctx = _Ctx(model, geom, rows, body_x0, body_size)

    p1 = [r for r in rows if r.page == 1]
    big = [r for r in p1 if r.size >= _MASTHEAD_SIZE]
    fences = [r for r in p1 if _is_fence(r, page1.width)]
    # THE MASTHEAD'S POSITION NAMES THE PAPER.
    if big and big[0].top < _TOP_BAND * page1.height:
        return _read_certificate(ctx, big[0])
    if big and len(fences) >= 2:
        return _read_cover(ctx, big[0])
    if not big:
        return _read_list(ctx)
    return NOTHING


# ---- the engraved certificate -------------------------------------------

def _read_certificate(ctx: _Ctx, masthead: _Row):
    parser = BylineParser(ALA.byline)
    date = None
    docket = None
    caption: list = []
    caption_rows: list = []
    ended = False
    for row in ctx.rows:
        if row.page != 1 or row.top < masthead.top:
            continue
        if row is masthead:
            ctx.crit["court"] = row.text
            ctx.emit(row, "court", "C")
            continue
        if docket is None and row.size >= _DATE_SIZE:
            if date is not None:
                return NOTHING
            date = row.text.rstrip(".")
            ctx.emit(row, "date", "C")
            continue
        if docket is None:
            found = _docket_row(row.text)
            if not found:
                return NOTHING            # the docket always follows the date
            docket = found
            ctx.emit(row, "docket", "L")
            continue
        # THE CAPTION ENDS WHERE THE PAGE LEAVES THE RAIL — the clerk's
        # centred heading is the WRITING's, and the reader does not take it.
        if row.x0 > ctx.body_x0 + _RAIL_TOL or parser.parse(row.text):
            ended = True
            break
        caption.append(row.text)
        caption_rows.append(row)
    if not (ended and docket and caption):
        return NOTHING
    ctx.crit["headmatter_style"] = STYLE_CERT
    ctx.crit["docket_number"] = docket[0]
    if len(docket) > 1:
        ctx.crit["other_dockets"] = docket[1:]
    if date:
        ctx.crit["decision_date"] = date
    ctx.crit["caption"] = caption
    _read_caption_paragraph(ctx, _join_wrapped(caption), caption_rows)
    return ctx.result()


def _join_wrapped(rows: list) -> str:
    """The caption paragraph as one string. A row that ENDS on a hyphen
    broke a docket across the measure ('… Circuit Court: CV-' / '24-900114')
    and must close up, or the number reads as two."""
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


# ---- the judicial-department list ---------------------------------------

def _read_list(ctx: _Ctx):
    parser = BylineParser(ALA.byline)
    page1 = ctx.model.pages[0]
    docket = None
    caption: list = []
    caption_rows: list = []
    head: list = []
    signed = False
    for row in ctx.rows:
        if row.page != 1:
            break
        if parser.parse(row.text):
            signed = True
            break
        if docket is None:
            found = _docket_row(row.text)
            if found:
                docket = found
                ctx.emit(row, "docket", "L")
                continue
            if not _on_axis(row, page1.width):
                return NOTHING            # the masthead band is on the axis
            head.append(row)
            continue
        if row.x0 <= ctx.body_x0 + _RAIL_TOL:
            caption.append(row.text)
            caption_rows.append(row)
            continue
        # A CENTRED ROW AFTER THE CAPTION is the paper naming itself
        # ('On Rehearing Ex Mero Motu').
        ctx.crit.setdefault("title", row.text.rstrip("."))
        ctx.emit(row, "title", "C")
    if not (signed and docket and caption and head):
        return NOTHING
    # THE MASTHEAD BAND: the court names itself, then names its sitting.
    for i, row in enumerate(head):
        if i == len(head) - 1 and _TERM.match(row.text.upper()):
            ctx.emit(row, "date", "C")
        else:
            ctx.emit(row, "court", "C")
            ctx.crit["court"] = row.text
    ctx.crit["headmatter_style"] = STYLE_LIST
    ctx.crit["docket_number"] = docket[0]
    if len(docket) > 1:
        ctx.crit["other_dockets"] = docket[1:]
    date = _release_date(ctx.model)
    if date:
        ctx.crit["decision_date"] = date
    ctx.crit["caption"] = caption
    _read_caption_paragraph(ctx, _join_wrapped(caption), caption_rows)
    return ctx.result()


# ---- the fenced cover ----------------------------------------------------

def _read_cover(ctx: _Ctx, masthead: _Row):
    parser = BylineParser(ALA.byline)
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
            # position says so — not size. (A two-page opinion measures its
            # BODY at the notice's 10pt, so a size test dropped the claim on
            # exactly the records where core's own stamp test also failed.)
            # Core's notice peel runs only on rows the reader left behind,
            # and left behind alone the notice assembled as an authorless
            # writing on 132 covers.
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
        # is the paper naming itself — 'On Rehearing Ex Mero Motu', 'On
        # Application for Rehearing', 'After Remand from the Supreme Court
        # of the United States'. Measured: exactly three roman rows in the
        # 136 covers, and all three are that.
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
        # AN ORIGIN STATEMENT WRAPS. 'Certified Questions from the United
        # States District Court' / 'for the Northern District of Alabama' /
        # '(Case No. 7:23-cv-00692-ACA)' is one statement in three rows;
        # read row by row, its middle line joined the party names. Once the
        # origin opens it runs to the fence that opens the next case, or to
        # the byline.
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
            # petition title once per case, and merged they read four times
            # over.
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
    for kind, band in (("stamp", [r for r in notice
                                  if r.text[:len(_REL)].lower() == _REL]),
                       ("notice", [r for r in notice
                                   if r.text[:len(_REL)].lower() != _REL])):
        if not band:
            continue
        ctx.dropped.append(m.Dropped(
            text=" ".join(r.text for r in band)[:1200],
            prov=m.Prov(band[0].page,
                        tuple(i for r in band for i in r.ids)),
            kind=kind))
        for r in band:
            ctx.consumed.update(r.ids)
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
    parenthesised ('(In re: City of Huntsville' / 'v.' / 'John Sandifer)')
    and carries a pivot of its own; the parenthesis opens it, and nothing
    from there on names a party to THIS case ('Ex parte John Sandifer (In
    re: City of Huntsville v. John Sandifer)')."""
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
