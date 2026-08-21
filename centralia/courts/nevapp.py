"""Nevada Court of Appeals ('nevapp').

THE SAME PAPER AS ITS SUPREME COURT, printed by the same clerk on the same
form, with three words changed. nev.py is the reference; this file is that
contract with the appellate masthead, the appellate bench line, the '-COA'
docket suffix, and the '(0) 1947B' form number instead of '1947A'.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                              140 Nev., Advance Opinion 21    cite   │
    │       IN THE COURT OF APPEALS OF THE STATE OF NEVADA     masthead   │
    │ KIM A. JUDD,                            │  No. 85734-COA  docket    │
    │        Appellant,                       │  ┌───────────┐            │
    │ vs.                                     │  │  F I L E D│  the CLERK │
    │ THE STATE OF NEVADA,                    │  │ MAR 28 20 │  — dropped │
    │        Respondent.                      │  └─ DEPUTY ──┘            │
    │      Appeal from a judgment of conviction … Seventh Judicial         │
    │ District Court, Lincoln County; Gary Fairman, Judge.     the origin │
    │      Affirmed in part, reversed in part, and remanded.  disposition │
    │ Katschke Law, LLC, and Franklin J. Katschke, Panaca,                │
    │ for Appellant.                                          appearances │
    │ BEFORE THE COURT OF APPEALS, GIBBONS, C.J., and BULLA and  bench    │
    │ WESTBROOK, JJ.                                                      │
    │                     OPINION                             the title   │
    │ By the Court, BULLA, J.:                                the writing │
    │  COURT OF APPEALS                                                   │
    │  OF          (0) 1947B                             the seal, 5pt    │
    │  NEVADA                                                             │
    └─────────────────────────────────────────────────────────────────────┘

MEASURED over all 31 records. 7 of them scan to ZERO lines and this reader
answers NOTHING (austin_joseph_v._state_criminal, bernstein_v._morris_civil,
chadwick_v._state, hall_kenya_..._cw_90152, in_re_guardianship_...,
johnson_v._bennett_child_custody, willson_v._first_jud._dist._ct._1) — each
is the image half of a pair whose '_1' twin carries the text. The remaining
24 print the masthead in the first three rows and sign 'By the Court, …',
and every one of them is this contract.

THE PAGE. 607-612pt wide. `geom.body_x0` measures the rail at 106-116; the
caption sits 0-8pt right of it and the origin/disposition paragraphs open
70-73pt right of it, so a row 40pt right of the rail is a PARAGRAPH OPENER
and nothing else is (same measure as nev).

THE RIGHT COLUMN HOLDS ONE THING THE COURT WROTE: 'No. 85734-COA'. The rest
standing there is the clerk's stamp, scanned to nothing readable ('MED',
"'NLED", 'FILE', 'F13 1 3 ai25', 'pqq bC'), and it is dropped BY POSITION.
No decision_date is set: the stamp date is the only date printed and the OCR
of it is not a date ('FEB 2 6 2026', 'JAN 30 2025', 'MAR 28 20').

THE BENCH SURVIVES THE SCAN ONLY LOOSELY — 'BEFORE TH E COURT O F APPEALS,
I3ULLA, C.J., and GIBBONS and' (ccmsi) — so its pattern tolerates broken
words. One record (in_re_guardianship_..._child_custody_1) loses the bench
row entirely to the scan; the bench is therefore not part of the gate.

THE GATE IS THE SHAPE: masthead + signature + a caption + an origin
recital. Not the docket, and not the title — willson_v._first_jud._dist.
_ct._2 prints no readable 'OPINION' row.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder, is_folio_text

_COURT_NAME = "IN THE COURT OF APPEALS OF THE STATE OF NEVADA"
# The masthead, spelled through the scan. Every record prints the words
# 'OF THE STATE OF NEVADA'; the court's own name is what the OCR mangles.
_MASTHEAD = re.compile(
    r"^(?:IN\s+)?TH\s?E\s+CO\S*\s?\S*\s+O\s?F?\s+APPE\S+\s+O\s?F\s+THE\s+"
    r"STATE\s+O\s?F\s+NEVADA\.?$", re.I)
# '140 Nev., Advance Opinion 21' — the trailing number is lost as often as
# not ('c21', 'Ia.', 'CO&', '$ 1-1', '(S2'), so it is only carried when it
# scans as digits.
_CITE = re.compile(
    r"^(1\d\d)\s*Nev[.,]{0,2}\s*Advan\S*\s*Opini\S*\s*(\d{1,3})?\b", re.I)
# 'No. 85734-COA' / 'No, 86567-COA' / 'No. 871.30-COA' (OCR dot inside the
# number). The '-COA' suffix is what the Court of Appeals prints and it is
# what tells this row from the clerk's scrawl beside it.
_DOCKET = re.compile(r"^No[.,]?\s*([\d.,]{4,8}\s*-\s*C\s?O\s?A)\b", re.I)
# 'BEFORE THE COURT OF APPEALS, GIBBONS, C.J., and BULLA and'
_BENCH = re.compile(
    r"^BEFORE\s+TH\s?E\s+CO\S*\s?\S*\s+O\s?F?\s+APPE\S+[,.;:]?\s*(.*)$",
    re.I)
_NOT_A_NAME = {"EN", "BANC", "J", "JJ", "C.J", "CJ", "CA", "C.A", "THE",
               "AND", "COURT", "APPEALS", "CHIEF", "JUDGE", "JUDGES"}
_TITLE = re.compile(r"^OPINI\S{0,4}\.?$", re.I)
_BYLINE = re.compile(r"^By\s+the\s+Co\S+\b|^PER\s+CURIAM", re.I)

_INDENT_MIN = 40.0
_RIGHT_COL = 0.63
_ORIGIN_LEAD_MAX = 26.0
_WRAP_LEAD_MAX = 20.0
_FOOT_SIZE_MAX = 9.5
_FOOT_BAND = 0.88
_MASTHEAD_ROWS = 5
_MAX_PAGES = 3
_AXIS_X0_TOL = 8.0
_FURNITURE_KINDS = ("folio", "running-head", "running-foot", "gutter")


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="nevapp")
def read_headmatter_nevapp(model, geom, **_):
    """Read the Court of Appeals' block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 12.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 108.0)
    page1 = model.pages[0]
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm)]
    if len(rows) < 8:
        return NOTHING
    texts = [_norm(" ".join(l.plain for l in g)) for g in rows]
    mast = next((i for i, t in enumerate(texts[:_MASTHEAD_ROWS])
                 if _MASTHEAD.match(t)), None)
    if mast is None:
        return NOTHING
    if not any(_BYLINE.match(t) for t in texts[mast + 1:]):
        return NOTHING

    ctx = _Ctx()
    caption: list[str] = []
    # THE CAPTION'S TWO COLUMNS, buffered until the band closes: the left
    # rows in the order the page prints them, and the right column keyed by
    # the baseline it shares with one of them.
    box_left: list = []
    box_right: dict = {}
    parties: list[str] = []
    origin: list[str] = []
    disposition: list[str] = []
    counsel: list[str] = []
    bench: list[str] = []
    dockets: list[str] = []
    band = "head"
    origin_paras = 0
    origin_role = "lower-court"
    prev_top: float | None = None
    prev_page: int | None = None

    for group, text in zip(rows, texts):
        pieces = sorted(group, key=lambda l: l.x0)
        if not text:
            continue
        first = pieces[0]
        page_no = first.page
        pm = model.pages[page_no - 1] if page_no <= len(model.pages) else page1
        width, height = pm.width, pm.height
        on_axis = abs(first.x0 - width / 2) <= _AXIS_X0_TOL
        indented = first.x0 - body_x0 >= _INDENT_MIN
        same_page = prev_page == page_no
        lead = (first.top - prev_top) if (same_page and prev_top is not None) \
            else None

        # ---- THE SIGNATURE ENDS THE READER -----------------------------
        if band != "head" and _BYLINE.match(text):
            break

        # ---- THE FOOT: the seal and '(0) 1947B', by SIZE ----------------
        if first.top >= height * _FOOT_BAND \
                and ((first.size or 0.0) <= _FOOT_SIZE_MAX
                     or is_folio_text(text)):
            ctx.drop(pieces, "running-foot")
            continue
        kind = finder.kind(pm, first)
        if kind in _FURNITURE_KINDS:
            ctx.drop(pieces, kind)
            continue

        # ---- THE RIGHT COLUMN: the docket, then the clerk ---------------
        if first.x0 >= width * _RIGHT_COL:
            docket = _DOCKET.match(text)
            if docket:
                dockets.append(_norm(docket.group(1)).replace(" ", ""))
                # IN THE CAPTION BAND it is the box's right column and is
                # paired with the party row it is printed beside; anywhere
                # else it stands on its own.
                if band == "caption":
                    box_right.setdefault(round(first.top, 1), []).extend(
                        pieces)
                else:
                    ctx.emit(pieces, "docket", centre=False)
            else:
                ctx.drop(pieces, "stamp")
            continue

        # ---- ABOVE THE MASTHEAD: the Reporter's cite, and scan specks ---
        if band == "head":
            if _MASTHEAD.match(text):
                if text.upper() == _COURT_NAME:
                    ctx.crit.setdefault("court", text)
                ctx.emit(pieces, "court")
                band = "caption"
                prev_top, prev_page = first.top, page_no
                continue
            cite = _CITE.match(text)
            if cite:
                value = f"{cite.group(1)} Nev., Advance Opinion"
                if cite.group(2):
                    value = f"{value} {cite.group(2)}"
                ctx.crit.setdefault("citation", value)
                ctx.emit(pieces, "citation", centre=False)
            else:
                ctx.drop(pieces, "stamp")
            prev_top, prev_page = first.top, page_no
            continue

        # ---- THE BENCH, and the paper's own name ------------------------
        benched = _BENCH.match(text)
        if benched:
            band = "bench"
            bench.append(text)
            ctx.emit(pieces, "panel", centre=False)
            prev_top, prev_page = first.top, page_no
            continue
        if band == "bench" and not on_axis and lead is not None \
                and lead <= _WRAP_LEAD_MAX:
            bench.append(text)
            ctx.emit(pieces, "panel", centre=False)
            prev_top, prev_page = first.top, page_no
            continue
        if on_axis and _TITLE.match(text):
            if text.upper() == "OPINION":
                ctx.crit.setdefault("title", "OPINION")
            ctx.emit(pieces, "title")
            band = "bench"
            prev_top, prev_page = first.top, page_no
            continue

        # The backstop: a paragraph opening on the indent once the
        # appearances are printed is the writing's prose. It stands LAST
        # for the reason nev records — the title and the clerk's scrawl are
        # both indented.
        if band in ("counsel", "bench") and indented:
            break

        # ---- THE CAPTION: the left column above the first indent --------
        if band == "caption":
            if not indented:
                caption.append(text)
                # Parties are the CAPS rows; statuses are caps-and-lower,
                # and survive the overprint ('Avsp.pellant,').
                if text.upper() == text:
                    parties.append(text)
                box_left.append((page_no, round(first.top, 1), pieces))
                prev_top, prev_page = first.top, page_no
                continue
            band = "origin"

        # ---- THE ORIGIN BAND: two double-leaded paragraphs --------------
        if band == "origin":
            if indented:
                origin_paras += 1
                origin_role = "lower-court" if origin_paras == 1 \
                    else "disposition"
            elif lead is None or lead > _ORIGIN_LEAD_MAX:
                band = "counsel"
            if band == "origin":
                (origin if origin_role == "lower-court"
                 else disposition).append(text)
                ctx.emit(pieces, origin_role, centre=False)
                prev_top, prev_page = first.top, page_no
                continue

        # ---- THE APPEARANCES, single-leaded at the rail -----------------
        if band == "counsel":
            counsel.append(text)
            ctx.emit(pieces, "counsel", centre=False)
            prev_top, prev_page = first.top, page_no
            continue

        prev_top, prev_page = first.top, page_no

    if box_left:
        ctx.box([(pg, pieces, box_right.get(top, []))
                 for pg, top, pieces in box_left])
    if not caption or not origin_paras:
        return NOTHING
    if dockets:
        ctx.crit.setdefault("docket_number", dockets[0])
        if len(dockets) > 1:
            ctx.crit.setdefault("other_dockets", dockets[1:])
    if caption:
        ctx.crit.setdefault("caption", caption)
    if parties:
        ctx.crit.setdefault("parties", parties[:8])
    if origin:
        joined = " ".join(origin)
        ctx.crit.setdefault("history", joined[:2000])
        below = _COURT_BELOW.search(joined)
        if below:
            ctx.crit.setdefault("lower_court", _norm(below.group(1)))
        judged = _JUDGE_BELOW.search(joined)
        if judged:
            ctx.crit.setdefault("lower_court_judge", _norm(judged.group(1)))
    if disposition:
        ctx.crit.setdefault("disposition", " ".join(disposition)[:400])
    if counsel:
        ctx.crit.setdefault("attorneys", " ".join(counsel)[:2000])
    if bench:
        line = " ".join(bench)
        ctx.crit.setdefault("panel_line", line)
        names = _panel_names(line)
        if names:
            ctx.crit.setdefault("panel", names)
    return ctx.result()


# The court below, in the forms the origin recital prints. Each carries its
# OWN closed tail; an open tail is what put half a recital in nev's
# lower_court.
_COURT_BELOW = re.compile(
    r"((?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth"
    r"|Eleventh)\s+Judicial\.?\s+District\s+Court"
    r"(?:,\s+Family\s+Division)?(?:,\s+[A-Z][a-z]+\s+County)?"
    r"|United\s+States\s+District\s+Court"
    r"(?:\s+for\s+the\s+District\s+of\s+[A-Z][a-z]+)?)", re.I)
_JUDGE_BELOW = re.compile(r";\s*([^;]{3,60}?),\s*(?:District\s+)?Judge\.?\s*$")


def _panel_names(line: str) -> list[str]:
    """The judges the bench line names."""
    tail = _BENCH.match(line)
    if not tail:
        return []
    out: list[str] = []
    for tok in re.split(r"[,.;]|\band\b", tail.group(1)):
        word = tok.strip().strip(".,;:")
        if len(word) >= 3 and word.upper() == word \
                and re.match(r"^[A-Z][A-Z'\- ]+$", word) \
                and not all(w in _NOT_A_NAME for w in word.upper().split()):
            out.append(word)
    return out


def _rows(pm) -> list[list]:
    """Rows by baseline, split where a row's pieces stand apart — a caption
    row and the docket or the clerk's stamp beside it."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    out: list[list] = []
    for k in order:
        row = groups[k]
        if len(row) > 1:
            out.extend([piece] for piece in row)
        else:
            out.append(row)
    return out


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

    def cell(self, parts: list, role: str, page: int):
        parts = sorted(parts, key=lambda l: l.x0)
        if not parts:
            return m.HmLine(text="", prov=m.Prov(page), align=m.Align.LEFT,
                            role=role)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        return m.HmLine(
            text=text, prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=parts[0].x0, size=parts[0].size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    def box(self, rows: list) -> None:
        """The caption, as the page sets it: two columns paired by the
        printed row, over the whitespace gutter the clerk's form leaves.

        Emitted flat, the docket stood between the first party and its own
        status row -- 'BRITT HAYES, AN INDIVIDUAL,' / 'No. 85087-COA' /
        'Appellant,' -- because page order is not reading order across a
        gutter (the user, 2026-08-21). The pairing is by BASELINE, which is
        what the form itself uses: the docket is set on the first party's
        row and nothing else in the right column survives the scan.
        """
        left, right = [], []
        ids: set[int] = set()
        for pg, l_cells, r_cells in rows:
            left.append(self.cell(l_cells, "caption", pg))
            right.append(self.cell(r_cells, "docket" if r_cells
                                   else "caption", pg))
            ids.update(c.id for c in l_cells + r_cells)
        while left and not (left[-1].text or "").strip() \
                and not (right[-1].text or "").strip():
            left.pop()
            right.pop()
        if not left:
            return
        self.items.append(m.CaptionBlock(
            left=left, right=right, rail=None, rail_rows=len(left),
            style_id="open-gutter", fp={"rail": None},
            prov=m.Prov(rows[0][0], tuple(sorted(ids)))))
        self.consumed.update(ids)

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
