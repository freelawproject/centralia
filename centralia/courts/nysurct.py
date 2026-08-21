"""Surrogate's Court of the State of New York ('nysurct').

THE PAPER IS TWO DOCUMENTS BOUND TOGETHER, and it is the New York State Law
Reporting Bureau that binds them. Page 1 is the Bureau's own cover sheet —
born-digital, machine-set, byte-identical in layout across all five records.
Behind it, from page 2 on, is a PHOTOCOPY of the Surrogate's signed decision,
scanned and OCR'd, carrying the county clerk's rubber entry stamp in its top
right corner.

    ┌──────────────────────── page 1: the Bureau's cover ─────────────────┐
    │                     Matter of Zabar                    38.4  bold   │ caption
    │                2026 NY Slip Op 30920(U)                56.2         │ citation
    │                     March 6, 2026                      74.2         │ date
    │            Surrogate's Court, New York County          92.2         │ court
    │          Docket Number: File No. 2025-4634            110.2         │ docket
    │                 Judge: Hilary Gingold                 128.2         │ author
    │   Cases posted with a "30000" identifier, i.e., …     146.2 ┐       │
    │   … republished from various New York State and …           │ the   │ publication
    │   This opinion is uncorrected and not selected for          │ CAVEAT│
    │   official publication.                               218.2 ┘       │
    │ file:///LRB-ALB-FS1/…/NYSUR.2025-4634.NEW_YORK.001…   780.8         │ dropped
    └──────────────────────────────────────────────────────────────────────┘
    ┌──────────────── page 2: the decision, as the court signed it ───────┐
    │                                          ENTERED         ┐          │
    │  SURROGATE'S COURT OF THE STATE OF NEW YORK   MAR 6 2026 │ clerk's  │
    │  COUNTY OF NEW YORK                      DATA ENTRY DEPT │ ENTRY    │
    │                             New York County Surr's Court ┘ STAMP    │
    │  ------------------------------------------------------x  ← FENCE  │
    │  Probate Proceeding, Will of                                        │
    │                                    File No.: 2025-4634              │
    │      SAULZABAR,                                                     │
    │              Deceased.                                              │
    │  ------------------------------------------------------x  ← FENCE  │
    │  GINGOLD, S.                            ← the writing opens here    │
    └──────────────────────────────────────────────────────────────────────┘

THE DISPATCH IS THE REPORTER'S CITATION, not a title. Row two of page 1 is
always `NNNN NY Slip Op NNNNN(U)`, centred, 12.0pt, and it is the one thing
that says this record came off the Bureau's press. Five of five carry it.
Without it this reader returns NOTHING.

THE CAVEAT IS PUBLICATION STATUS, not boilerplate. 'This opinion is
uncorrected and not selected for official publication' is the Bureau stating
what this document IS — a (U) table decision, unreported. It is emitted as
`publication` rows, in place, and recorded as `publication_status =
"unpublished"`. Core's own status sweep (pipeline.py:918-942) does not know
the phrase 'not selected for official publication', so without this the
status was simply absent.

THE ESTATE MATTER HAS NO ADVERSARY. 'Probate Proceeding, Will of SAUL ZABAR,
Deceased' has no `v.`, and `criteria.parties` is rendered `" v. ".join(...)`
at render/html.py:307 — asserting an adversity that does not exist. This
reader therefore sets `caption` (the rows as printed) and `case_name` (the
Bureau's own short title, 'Matter of Zabar') and leaves `parties` empty.

THE CAPTION BAND IS FENCED BY TWO TYPED RULES — a run of hyphens closed with
an 'x' or 'X', struck on a typewriter, not drawn. All four decision pages set
exactly two, and the byline follows the second within one row. The band is
lines[0 .. second rule]; fewer than two rules and the band is not read at all
(the cover still is). The fences are re-emitted as `m.Rule(typed=True)`, the
ca4 rule: a reader that claims a block owes the page its furniture back.

A FENCE CAN BE STRUCK THROUGH A LINE OF TEXT. matter_of_donnelly's county row
comes back as `C--O--U--N---T-Y-- -O--F-- N--E--W--- -Y--O--R--K-----------`:
the typist ran the rule over the words. Rendered raw it explodes into thirty
one-character rows. Where a hyphen-dominated row still has letters left after
the hyphens come out, the residue is the row and the rule is the rule — both
are emitted, in that order.

THE CLERK'S ENTRY STAMP IS BOUNDED BY THE CAPTION'S OWN RIGHT COLUMN. The
stamp is ink at the right margin — 'ENTERED', a date, 'DATA ENTRY DEPT', "New
York County Surrogate's Court" — and OCR shreds it differently every time
('DAT A EN nw DEPT', "MAR 't4f 2026", "N~wD VAoTn, A.:. ...E,J NTSR-:Y,rr
oDgaEte'Ps CTourt"). Neither its wording nor its type size is stable: the
sizes measured run 4.6, 6.5, 6.9, 8.8, 10.0, 10.3, 11.1, 15.4, 15.9, 16.3,
16.5, 16.8, 17.2, 22.2 and 24.0pt against an 11pt body, straddling it in both
directions. What IS stable is that the stamp sits ABOVE the caption's right
column. That column opens at the first right-hand landmark the caption
prints — 'DECISION and ORDER' or 'File No.' — measured at tops 121.0, 127.2,
131.1 and 156.6 across the four; the lowest stamp row sits at 90.0, 96.6,
101.5 and 101.6. Everything right of 0.55 of the measure and above that
landmark is the stamp, recorded as `Dropped(kind="stamp")`. Nothing is
matched against the stamp's own text.

WHAT THIS FILE DOES NOT DO. It does not touch the writing: the byline row
(`GINGOLD, S.`, `MEL LA, S.:` — OCR opens gaps inside the surname and core's
abbrev grammar takes them) is left in the stream so the opinion opens on it.
It reads no counsel: this court prints none on the papers in this corpus.

MEASURED ON FIVE RECORDS, WHICH IS ALL THERE ARE. Five covers, identical.
Four decision pages, all with two fences, all with the byline one row under
the second fence, all with a right-hand entry stamp. One record
(matter_of_field) is a ten-page scan whose ONLY text layer is the cover —
pages 2-10 carry four characters each, the `[* n]` page marks. Everything
below 'five of five' or 'four of four' in this docstring is a count, not an
inference; the shape of a sixth record is an inference.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

# ---------------------------------------------------------------------------
# the profile
# ---------------------------------------------------------------------------
# A SURROGATE IS NOT A JUSTICE. The bench signs 'GINGOLD, S.' and 'MEL LA,
# S.:'; with no profile at all `get_profile()` hands back
# BylineGrammar(titles=("Justice",)) and every one of these opinions
# assembles unbylined. 'S.' is the only abbreviation this court uses.
register(CourtProfile(
    "nysurct", "Surrogate's Court of the State of New York",
    byline=BylineGrammar(style="abbrev",
                         abbrev_titles=(("S.", "Surrogate"),),
                         titles=("Surrogate",)),
    # One Surrogate, one decision: there is no panel to concur in or dissent
    # from, so a record that comes back as two writings has been split.
    single_writing=True,
    rollout="migrated",
))


# ---------------------------------------------------------------------------
# the cover (page 1)
# ---------------------------------------------------------------------------
# The dispatch: the Bureau's own citation, in the form it gives an
# unreported table decision.
_SLIP_OP = re.compile(r"^\d{4}\s+N\.?Y\.?\s+Slip\s+Op\s+\d+\s*\((?:U|u)\)$")
_COVER_DOCKET = re.compile(r"^Docket\s+Numbers?:\s*(.+)$", re.I)
_COVER_JUDGE = re.compile(r"^Judges?:\s*(.+)$", re.I)
_COVER_COURT = re.compile(r"^Surrogate'?s\s+Court\b.*$", re.I)
_MONTHS = ("January|February|March|April|May|June|July|August|September"
           "|October|November|December")
_COVER_DATE = re.compile(rf"^(?:{_MONTHS})\s+\d{{1,2}},\s+\d{{4}}$")
_CAVEAT_OPEN = re.compile(r"^Cases\s+posted\s+with\b", re.I)
_FILE_PATH = re.compile(r"^file:/", re.I)

# ---------------------------------------------------------------------------
# the decision page
# ---------------------------------------------------------------------------
_DECISION_COURT = re.compile(r"^SURROGATE'?S\s+COURT\b", re.I)
_COUNTY = re.compile(r"^COUNTY\s+OF\s+[A-Z][A-Z' ]*$", re.I)
# What the paper calls itself, printed in the caption's right column.
_PAPER_TITLE = re.compile(
    r"^(DECISION|ORDER|DECREE)(\s+AND\s+(ORDER|DECREE))?\.?$", re.I)
_FILE_NO = re.compile(r"^File\s*No\.?\s*:?\s*(.+)$", re.I)
# 'GINGOLD, S.' / 'MEL LA, S.:' / 'GINGOL D, S.' — the stop, not the parse.
_BYLINE = re.compile(r"^[A-Z][A-Z]*(?:\s+[A-Z]+)*\s*,\s*S\.\s*:?$")

# The caption's right column, as a fraction of the measure. The four
# landmarks measured sit at 0.596, 0.596, 0.650 and 0.711 of the page width;
# the leftmost caption text on those pages ends at 0.60 at the widest.
_RIGHT_FRAC = 0.55
# A typed fence: a run of hyphens, optionally closed with an 'x'. The
# shortest measured is 62 characters; 8 is a floor no caption row reaches.
_MIN_FENCE_HYPHENS = 8
_FENCE_DENSITY = 0.4


def _norm(text: str) -> str:
    return " ".join((text or "").split())


# The fence's own run — eight hyphens or more with nothing between them. A
# row struck THROUGH text has short runs (one to three) between its letters
# and this long one at the end, which is how the two are told apart without
# reading a word: everything before the LAST long run is the text.
_LONG_RUN = re.compile(rf"-{{{_MIN_FENCE_HYPHENS},}}")


def _fence(text: str) -> tuple[bool, str]:
    """Is this row a typed fence, and what text (if any) was struck through
    it? Returns (is_fence, residue)."""
    flat = _norm(text)
    hyphens = flat.count("-")
    if hyphens < _MIN_FENCE_HYPHENS or hyphens < _FENCE_DENSITY * len(flat):
        return False, ""
    runs = list(_LONG_RUN.finditer(flat))
    if not runs:
        return False, ""
    last = runs[-1]
    # Before the fence's own run: the text it was struck through, its
    # letters still spaced by the short runs. After it: the 'x' the typist
    # closes the fence with — and nothing else, in this corpus.
    residue = _norm(flat[:last.start()].replace("-", ""))
    tail = _norm(flat[last.end():].strip("xX "))
    if tail:
        residue = _norm(f"{residue} {tail}")
    return True, residue


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self) -> None:
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}

    def emit(self, line, role: str, *, align=m.Align.LEFT,
             text: str | None = None) -> None:
        self.items.append(m.HmLine(
            text=line_markup(line) if text is None else text,
            prov=m.Prov(line.page, (line.id,)), align=align,
            x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        self.consumed.add(line.id)

    def rule(self, line) -> None:
        self.items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                 span="left", typed=True))
        self.consumed.add(line.id)

    def drop(self, line, kind: str) -> None:
        self.dropped.append(m.Dropped(text=_norm(line.plain),
                                      prov=m.Prov(line.page, (line.id,)),
                                      kind=kind))
        self.consumed.add(line.id)

    def result(self, doc_type=None) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": doc_type}


def _page_lines(pm) -> list:
    return [l for l in sorted(pm.lines, key=lambda l: (l.top, l.x0))
            if l.plain.strip()]


def _read_cover(ctx: _Ctx, pm) -> bool:
    """The Bureau's cover sheet. True when its citation identified it."""
    lines = _page_lines(pm)
    if not any(_SLIP_OP.match(_norm(l.plain)) for l in lines[:4]):
        return False
    caveat = False
    for line in lines:
        text = _norm(line.plain)
        if _FILE_PATH.match(text):
            # The print footer of the web page the cover was printed from.
            ctx.drop(line, "running-foot")
            continue
        if caveat:
            ctx.emit(line, "publication", align=m.Align.CENTER)
            if text.lower().rstrip(".").endswith("publication"):
                caveat = False
            continue
        if _CAVEAT_OPEN.match(text):
            caveat = True
            ctx.crit["publication_status"] = "unpublished"
            ctx.emit(line, "publication", align=m.Align.CENTER)
            continue
        if _SLIP_OP.match(text):
            ctx.crit["citation"] = text
            ctx.emit(line, "citation", align=m.Align.CENTER)
            continue
        hit = _COVER_DOCKET.match(text)
        if hit:
            ctx.crit["docket_number"] = _norm(hit.group(1))
            ctx.emit(line, "docket", align=m.Align.CENTER)
            continue
        hit = _COVER_JUDGE.match(text)
        if hit:
            # WHO WROTE IT, announced by the reporter rather than signed.
            ctx.crit["judges"] = _norm(hit.group(1))
            ctx.emit(line, "author", align=m.Align.CENTER)
            continue
        if _COVER_DATE.match(text):
            ctx.crit["decision_date"] = text
            ctx.emit(line, "date", align=m.Align.CENTER)
            continue
        if _COVER_COURT.match(text):
            ctx.crit["court"] = text
            ctx.emit(line, "court", align=m.Align.CENTER)
            continue
        # What is left, above the citation, is the Bureau's short title —
        # 'Matter of Zabar'. It is a case NAME, and the only one this paper
        # states: the estate caption below carries no 'v.' to build one from.
        if "case_name" not in ctx.crit and not ctx.items:
            ctx.crit["case_name"] = text
            ctx.emit(line, "caption", align=m.Align.CENTER)
            continue
        ctx.emit(line, "case-info", align=m.Align.CENTER)
    return True


def _decision_page(model):
    """The first page behind the cover that carries a text layer. None where
    the scan gave us nothing (matter_of_field: 4 characters a page)."""
    for pm in model.pages[1:]:
        if pm.ink_chars >= 120:
            return pm
    return None


def _read_caption(ctx: _Ctx, pm, finder) -> bool:
    """The decision's own caption, between its two typed fences. Returns
    False where the band cannot be fenced — and the caller then withdraws
    the WHOLE claim, cover included. 'Leave it to core' is not available
    here: a court reader's items REPLACE the headmatter whole
    (`pipeline.py:1564`), so a claim that ends at the foot of the cover does
    not leave the decision's caption where core had it — it re-classifies it
    as BODY, and the decision opens on its own caption mangled into prose."""
    lines = _page_lines(pm)
    fences = [i for i, l in enumerate(lines) if _fence(l.plain)[0]]
    if len(fences) < 2:
        return False
    band = lines[:fences[1] + 1]

    right_edge = _RIGHT_FRAC * pm.width
    landmarks = [l.top for l in band
                 if l.x0 >= right_edge
                 and (_PAPER_TITLE.match(_norm(l.plain))
                      or _FILE_NO.match(_norm(l.plain)))]
    # No right-hand landmark: the fence itself bounds the stamp.
    stamp_cut = min(landmarks) if landmarks else lines[fences[0]].top + 0.5

    caption_rows: list[str] = []
    for line in band:
        text = _norm(line.plain)
        # ALREADY RECORDED IS NOT UNREAD. Core's furniture pass runs long
        # before any court reader and has already taken the worst-shredded
        # stamp row off the stream and into `Dropped`; claiming it again
        # reports it twice (the pipeline withdraws a duplicate drop only
        # where the row came back PLACED, and a stamp never does).
        if finder.kind(pm, line):
            continue
        if _BYLINE.match(text):
            break                     # the writing begins (should not occur
                                      # inside the fences, but bound it)
        if line.x0 >= right_edge and line.top < stamp_cut:
            ctx.drop(line, "stamp")
            continue
        if not any(ch.isalnum() for ch in text):
            # Scan debris — a stray glyph pair the OCR invented.
            ctx.drop(line, "margin")
            continue
        is_fence, residue = _fence(text)
        if is_fence:
            if residue:
                # The fence was struck THROUGH a row of text.
                ctx.items.append(m.HmLine(
                    text=residue, prov=m.Prov(line.page, (line.id,)),
                    align=m.Align.LEFT, x0=line.x0, size=line.size or 0.0,
                    role="court"))
                ctx.consumed.add(line.id)
                ctx.items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                        span="left", typed=True))
            else:
                ctx.rule(line)
            continue
        if _DECISION_COURT.match(text) or _COUNTY.match(text):
            ctx.emit(line, "court")
            continue
        if _PAPER_TITLE.match(text):
            ctx.crit.setdefault("title", text)
            ctx.emit(line, "title", align=m.Align.RIGHT)
            continue
        hit = _FILE_NO.match(text)
        if hit:
            ctx.crit.setdefault("docket_number", text)
            ctx.emit(line, "docket", align=m.Align.RIGHT)
            continue
        caption_rows.append(text)
        ctx.emit(line, "caption")
    if caption_rows:
        ctx.crit["caption"] = caption_rows
    return bool(caption_rows)


@decider("headmatter.read", court="nysurct")
def read_headmatter_nysurct(model, geom, **_):
    """The Law Reporting Bureau's cover, and the decision's fenced caption
    behind it — or NOTHING."""
    if not model.pages:
        return NOTHING
    ctx = _Ctx()
    if not _read_cover(ctx, model.pages[0]):
        return NOTHING
    ctx.crit["headmatter_style"] = "ny-slip-op cover"
    ctx.crit["court"] = ctx.crit.get(
        "court", "Surrogate's Court of the State of New York")
    # THE SECOND PAPER IS PART OF THE CLAIM. Where the decision page has a
    # text layer its caption must be read, or the whole claim is withdrawn:
    # matter_of_donnelly types only ONE fence (its opening rule is struck
    # through 'COUNTY OF NEW YORK' and the OCR returns
    # 'C--O--U--N---T-Y-- -O--F-- N--E--W--- -Y--O--R--K---', which is not a
    # fence by density), so its caption cannot be bounded and core keeps the
    # record whole. matter_of_field has NO text layer behind the cover — 4
    # characters a page — so there is no second paper's headmatter to lose
    # and the cover claim stands alone.
    pm = _decision_page(model)
    if pm is not None:
        body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
        body_size = geom.body_size if geom and geom.body_size else 11.6
        if not _read_caption(ctx, pm,
                             FurnitureFinder(model, body_x0, body_size)):
            return NOTHING
    ctx.crit.setdefault("caption", [ctx.crit["case_name"]]
                        if ctx.crit.get("case_name") else [])
    return ctx.result()
