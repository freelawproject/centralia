"""Supreme Court of Arkansas ('ark').

Everything unique to ark lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'open caption box'. Arkansas DRAWS its caption's column
divider and closes it with one rule across the whole measure, and draws
nothing over its head. That upside-down T is the entire zone system:

    Cite as 2026 Ark. 44                        the reporter citation
    SUPREME COURT OF ARKANSAS                   the masthead, 18pt bold
    No. CR-24-690                               the court's own docket
                             │ Opinion Delivered: March 5, 2026
    CHRISTOPHER COY GAMBLE   │                  ← the divider, drawn
              APPELLANT      │ APPEAL FROM THE WHITE
    V.                       │ COUNTY CIRCUIT COURT [NO.
                             │ 73CR-20-604]
    STATE OF ARKANSAS        │ HONORABLE MARK PATE, JUDGE
              APPELLEE       │
                             │ AFFIRMED.
    ─────────────────────────────────────────   the foot rule, full measure
    BARBARA W. WEBB, Justice                    ← the reader stops

    What stands ABOVE the divider is the masthead band; LEFT of it, the
    parties; RIGHT of it, the court's statements about the case; BELOW
    the foot rule, the writings. Column membership is decided by which
    side of the drawn line a row sits on — never by what the row says.
    49 of the 50 records draw it, at x/width 0.50-0.52 and a foot rule
    0.77 of the measure; not one draws a head rule, which is what makes
    this an open T rather than core's 'i-beam' or 'backwards-c'.

    The RIGHT COLUMN is a stack of STATEMENTS, not of rows: each one may
    wrap over as many rows as the column is narrow. A statement ends
    where the next one opens, and each opens either on a word from a
    closed vocabulary ('Opinion Delivered', 'APPEAL FROM', 'PRO SE
    APPEAL FROM', '[NO.', 'HONORABLE', 'MOTION') or, for the one
    statement that carries no opener — what the court DID — on a
    stand-off of more than one and a half lines. Measured over the
    corpus: a wrap sits 14.7pt under its own first row and the smallest
    stand-off before a disposition is 26.7pt.

    'hand-down notice' (1 of 50) — the day the court releases nothing it
    posts the sheet that says so: one page, no divider, no rule, two
    CENTRED rows and a folio. An empty `opinions` list is the correct
    output for it, and the reader says so by declaring the type.

        NO SUPREME COURT OPINIONS TODAY
        MAY 14, 2026

A record that draws neither is not one of these papers and gets
NOTHING: core's shared walk places those rows unidentified, which is a
smaller error than a confident misreading.

WHAT THE READER DOES NOT TOUCH. ark prints its appearances BELOW the
writings ('David R. Raupp, Arkansas Public Defender Commission, for
appellant.'), on 31 of the 50 records. That roster is core's to harvest
under `counsel_after_writings`; the reader stops at the caption's foot
rule and never reaches into a writing.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import find_date, looks_like_docket

# ark's CourtProfile is registered in `courts/__init__.py` (shared file);
# this module owns the reader only.
STYLE_BOX = "open caption box"
STYLE_NOTICE = "hand-down notice"

# ---- ark's declared facts (measured over the corpus, not tuned) ----------
# THE DIVIDER is a drawn vertical — pdfio reports the two edges of a thin
# filled rect, 1.4pt apart. It stands at 0.498-0.521 of the measure on all
# 49 boxed records and is as tall as the caption (88pt at the shortest).
_DIVIDER_MIN_H = 40.0
_DIVIDER_BAND = (0.42, 0.62)
# THE FOOT RULE closes the box: 468.8pt or 473.4pt on a 612pt sheet
# (0.766 / 0.773 of the measure), its top on the divider's own foot.
_FOOT_MIN_W = 0.60
_FOOT_JOIN = 8.0
# A HEAD RULE would make this a different box. ark never draws one, and a
# record that does is not this contract.
_HEAD_JOIN = 8.0
# THE MASTHEAD is set 18pt over a 13pt body — the only enlarged row on
# the page.
_MASTHEAD_MIN_SIZE = 16.0
# HOW A RIGHT-COLUMN STATEMENT ENDS. A wrap sits one leading (14.7pt at
# 13pt type) under its own first row; the stand-off before a new
# statement is 26.7pt at the tightest. 1.6 type sizes = 20.8pt separates
# them with room on both sides.
_WRAP_GAP = 1.6
# One visual row: the two columns are set on independent baselines, so
# rows pair only where the page really put them level.
_ROW_TOL = 2.5

# THE COURT NAMES ITSELF in one row, on every paper it prints.
_MASTHEAD = "supreme court of arkansas"
# THE REPORTER CITATION the clerk stamps at the head of page 1 ('Cite as
# 2026 Ark. 44'). It is not a running head — pages 2+ carry none.
_CITE_OPENER = "cite as"
# THE COURT'S OWN DOCKET, in the three series it prints: CR (criminal),
# CV (civil), D (discipline).
_DOCKET = re.compile(r"^Nos?\.\s*[A-Z]{1,2}-\d{2}-\d{1,5}\.?$", re.I)
# WHEN THE COURT HANDED THE CASE DOWN, labelled in the right column's
# first cell. The label is the landmark; the value is read out of it.
_DELIVERED = "opinion delivered"
# HOW ark NAMES THE COURT IT REVIEWS. Openers only — what follows is the
# tribunal's own name, which is never read by wording.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "pro se appeal from", "pro se appeals from", "pro se motion",
    "petition for", "on petition for", "certified question",
    "on certification from", "original action",
)
# THE NUMBER THE CASE CARRIES BELOW, always in the court's own brackets.
_LOWER_DOCKET = "["
# WHO TRIED IT. 'HONORABLE MARK PATE, JUDGE' — and one record's trial
# judge is surnamed Honorable ('HONORABLE LATONYA / HONORABLE, JUDGE'),
# which is why an opener may not RE-open the statement it is already in.
_JUDGE_OPENER = "honorable"
# A MOTION decided alongside the appeal, stated in the same column.
_MOTION_OPENER = "motion"

_TERMINATORS = (".", ";", "]")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Inside the drawn box the left column holds nothing else — the
# masthead stands above the divider — so a row that is not a status and
# not the pivot is a party, whatever it says. (Core's shared party reader
# vetoes rows carrying court words or 'attorney general', which here
# deletes 'SUPREME COURT COMMITTEE' and 'ATTORNEY GENERAL' out of the
# middle of two parties' own names.)
_STATUS_WORDS = frozenset((
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "intervenor", "intervenors",
    "plaintiff", "plaintiffs", "defendant", "defendants", "movant",
    "movants", "amicus", "amici", "separate", "cross", "third", "party",
    "parties", "real", "interest", "and", "the", "in", "of", "pro", "se",
))
# THE PIVOT, as ark sets it.
_PIVOTS = ("v", "vs")
# THE NUMBER THE CASE CARRIES BELOW, in the brackets ark always sets it in
# — stated on its own row, or run onto the end of the origin.
_BRACKET = re.compile(r"\[\s*NOS?\.?\s*([^\]]+?)\s*\]", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _closed(text: str) -> bool:
    """Does this statement END here?

    The period after an INITIAL closes nothing — ark breaks the trial
    judge's name at one ('HONORABLE CATHLEEN V.' / 'COMPTON, JUDGE'), and
    read as a full stop the wrap opened a new statement and the judge's
    surname was published as part of the disposition."""
    flat = _norm(text)
    if not flat.endswith(_TERMINATORS):
        return False
    if flat.endswith("."):
        last = flat.rstrip(".").split()[-1] if flat.rstrip(".").split() else ""
        if len(last.strip("(),;")) <= 1:
            return False
    return True


def _strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup or "")


def _is_masthead(text: str) -> bool:
    return _norm(text).lower().rstrip(".") == _MASTHEAD


def _is_citation(text: str) -> bool:
    return _norm(text).lower().startswith(_CITE_OPENER)


def _is_status(text: str) -> bool:
    words = [w for w in _norm(text).lower().rstrip(",.;: ")
             .replace("-", " ").replace("/", " ").replace(",", " ").split()]
    return bool(words) and all(w in _STATUS_WORDS for w in words)


def _is_pivot(text: str) -> bool:
    return _norm(text).lower().rstrip(".,") in _PIVOTS


def _sides(rows: list[str]) -> list[str]:
    """The party sides, bounded structurally: a side runs to its STATUS
    row, the pivot separates the two, and a bare 'AND' row joins one
    party group to the next ('… APPELLEES' / 'AND' / '… INTERVENOR-
    APPELLEE')."""
    sides: list[str] = []
    cur: list[str] = []

    def close():
        if cur:
            sides.append(_norm(" ".join(cur)).rstrip(",; "))
            cur.clear()

    for row in rows:
        flat = _norm(row)
        if not flat:
            continue
        if _is_pivot(flat) or _is_status(flat):
            close()
            continue
        cur.append(flat)
    close()
    return sides


# --------------------------------------------------------------------------
# the box — ark's zone system, and the dispatch
# --------------------------------------------------------------------------

def _box(pm) -> dict | None:
    """The caption box this page draws, or None.

    An open T: a vertical divider near the page's middle, a full-measure
    rule at its foot, and nothing across its head."""
    verticals = [v for v in pm.v_rules
                 if v.height >= _DIVIDER_MIN_H
                 and _DIVIDER_BAND[0] <= v.x / pm.width <= _DIVIDER_BAND[1]]
    if not verticals:
        return None
    top = min(v.top for v in verticals)
    bottom = max(v.bottom for v in verticals)
    mid = (min(v.x for v in verticals) + max(v.x for v in verticals)) / 2
    wide = [r for r in pm.h_rules if r.width >= pm.width * _FOOT_MIN_W]
    foot = next((r for r in wide if abs(r.top - bottom) <= _FOOT_JOIN), None)
    if foot is None:
        return None
    if any(abs(r.top - top) <= _HEAD_JOIN for r in wide):
        return None                       # a closed box is a different paper
    return {"x": mid, "top": top, "bottom": bottom, "foot": foot.top}


def _side(line, mid: float, want: str):
    """The part of ``line`` lying on one side of the divider, or None.

    Whether pdfio already broke a row at the vertical is an accident of
    how the split fell; the drawn line decides, glyph by glyph."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    return _replace(line, chars=keep,
                    x0=min(c["x0"] for c in keep),
                    x1=max(c.get("x1", c["x0"]) for c in keep))


def _align(line, pm, geom, body_size: float) -> m.Align:
    return m.Align(line_alignment(line, pm.width, geom,
                                  banner_center_min_size=body_size + 2.0))


# --------------------------------------------------------------------------
# the right column — a stack of STATEMENTS, not of rows
# --------------------------------------------------------------------------

def _opener(text: str) -> str | None:
    """Which statement this cell OPENS, or None (it continues one)."""
    flat = _norm(text)
    low = flat.lower()
    if low.startswith(_DELIVERED):
        return "date"
    if low.startswith(_ORIGIN_OPENERS):
        return "origin"
    if flat.startswith(_LOWER_DOCKET):
        return "lower-docket"
    if low.startswith(_JUDGE_OPENER):
        return "judge"
    if low.startswith(_MOTION_OPENER):
        return "motion"
    return None


def _statements(cells: list) -> list:
    """The right column's stack, split into the statements the page sets.

    ``cells`` is [(line, flat_text)] in page order. A cell opens a new
    statement when it carries an opener the current statement is not
    already made of, or when it stands off from the row above by more
    than a wrap's leading; otherwise it continues what is open."""
    out: list = []                       # [ {kind, rows:[line], text:str} ]
    prev = None
    for line, flat in cells:
        kind = _opener(flat)
        size = line.size or 13.0
        gap = (line.top - prev.top) if prev is not None else 1e9
        prev = line
        if out and kind is not None and kind == out[-1]["kind"]:
            kind = None                  # 'HONORABLE, JUDGE' under
                                         # 'HONORABLE LATONYA' is a wrap
        # AN UNCLOSED BRACKET IS AN OPEN STATEMENT. ark breaks the number
        # below across the column ('COUNTY CIRCUIT COURT [NO.' /
        # '73CR-20-604]'), and the '.' the label ends on is not the end of
        # a sentence — read as one, the docket became a disposition.
        held = out and out[-1]["text"].count("[") > out[-1]["text"].count("]")
        if held:
            kind = None
        if kind is None and out and gap <= _WRAP_GAP * size \
                and (held or not _closed(out[-1]["text"])):
            out[-1]["rows"].append(line)
            out[-1]["text"] = f'{out[-1]["text"]} {flat}'.strip()
            continue
        out.append({"kind": kind or "label", "rows": [line], "text": flat})
    return out


# the role each statement renders under — the block renders WHOLE, so the
# way to show how it was read is to mark the rows in place
# `label` is the court's DISPOSITION — it already sets
# crit["disposition"], and only the ROW said "title". The user,
# 2026-08-19: "AFFIRMED is not a title its a disposition ... its the
# bottom right item in the headmatter often".
_ROLE = {"date": "date", "origin": "lower-court", "lower-docket": "lower-court",
         "judge": "lower-court", "motion": "title", "label": "disposition"}


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="ark")
def read_headmatter_ark(model, geom, **_):
    """Read ark's open-caption-box headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    box = _box(page1)
    if box is not None:
        return _read_box(model, geom, page1, box)
    if any(_box(pm) for pm in model.pages):
        return NOTHING                    # a box the reader cannot bound
    return _read_notice(model, geom, page1)


def _read_box(model, geom, pm, box):
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = [l for l in pm.lines
            if l.plain.strip() and l.top <= box["foot"] + 2
            and not finder.kind(pm, l)]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not rows:
        return NOTHING

    crit: dict = {"headmatter_style": STYLE_BOX}
    items: list = []
    consumed: set[int] = set()

    def emit(line, role: str):
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(pm.number, (line.id,)),
            align=_align(line, pm, geom, body_size), x0=line.x0,
            size=line.size or 0.0, bold=bool(line.all_bold), role=role))
        consumed.add(line.id)

    # --- the masthead band: what stands above the divider -----------------
    head = [l for l in rows if l.top < box["top"] - 2]
    band = [l for l in rows if l.top >= box["top"] - 2]
    for line in head:
        text = _norm(line.plain)
        if _is_citation(text):
            # THE COURT'S OWN PUBLIC-DOMAIN CITE ('Cite as 2026 Ark. App.
            # 340') — not the court naming itself. The user, 2026-08-19.
            crit.setdefault("citation", re.sub(r"^cite\s+as\s+", "", text,
                                               flags=re.I).rstrip("."))
            emit(line, "citation")
        elif _is_masthead(text) or (line.size or 0) >= _MASTHEAD_MIN_SIZE:
            if not _is_masthead(text):
                return NOTHING            # enlarged type that is not ark's
            crit.setdefault("court", text)
            emit(line, "court")
        elif _DOCKET.match(text) and looks_like_docket(text):
            docket = looks_like_docket(text)
            if "docket_number" in crit:
                crit.setdefault("other_dockets", []).append(docket)
            else:
                crit["docket_number"] = docket
            emit(line, "docket")
        else:
            return NOTHING                # a masthead row this is not
    if not band:
        return NOTHING

    # --- the caption box, column by column --------------------------------
    grid: list[list] = []
    for line in band:
        if grid and abs(grid[-1][0].top - line.top) <= _ROW_TOL:
            grid[-1].append(line)
        else:
            grid.append([line])
    mid = box["x"]
    left_cells: list = []                 # [(line, flat)]
    right_cells: list = []
    pairs: list = []                      # [(l_cells, r_cells)]
    for row in grid:
        l_cells, r_cells = [], []
        for line in row:
            for want, bucket in (("L", l_cells), ("R", r_cells)):
                part = _side(line, mid, want)
                if part is not None:
                    bucket.append(part)
        pairs.append((sorted(l_cells, key=lambda l: l.x0),
                      sorted(r_cells, key=lambda l: l.x0)))
        for cell in l_cells:
            left_cells.append((cell, _norm(cell.plain)))
        for cell in r_cells:
            right_cells.append((cell, _norm(cell.plain)))
    if not left_cells:
        return NOTHING                    # a caption with no party column

    # THE RIGHT COLUMN'S ROLES, statement by statement.
    roles: dict[int, str] = {}
    origin: list[str] = []
    lower_dockets: list[str] = []
    judge: list[str] = []
    motion: list[str] = []
    label: list[str] = []
    dates: list[str] = []
    lower_dockets_out: list[str] = []
    for stmt in _statements(right_cells):
        for line in stmt["rows"]:
            roles[id(line)] = _ROLE[stmt["kind"]]
        {"date": dates, "origin": origin, "lower-docket": lower_dockets,
         "judge": judge, "motion": motion,
         "label": label}[stmt["kind"]].append(stmt["text"])

    # --- build the block ---------------------------------------------------
    def cell(cells: list, role: str) -> m.HmLine:
        text = ""
        for part in cells:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = cells[0]
        for part in cells:
            consumed.add(part.id)
        return m.HmLine(
            text=text, prov=m.Prov(pm.number, tuple(p.id for p in cells)),
            align=_align(first, pm, geom, body_size), x0=first.x0,
            size=first.size or 0.0,
            bold=all(p.all_bold for p in cells), role=role)

    left, right = [], []
    l_role, r_role = "caption", "caption"
    for l_cells, r_cells in pairs:
        # A BLANK CELL IS SPACING INSIDE the run it stands in, not a row of
        # its own kind: given a kind of its own it breaks every run in the
        # column into one-row pieces.
        if l_cells:
            left.append(cell(l_cells, l_role))
        else:
            left.append(m.HmLine(text="", prov=m.Prov(pm.number),
                                 role=l_role))
        if r_cells:
            r_role = roles.get(id(r_cells[0]), "title")
            right.append(cell(r_cells, r_role))
        else:
            right.append(m.HmLine(text="", prov=m.Prov(pm.number),
                                  role=r_role))
    items.append(m.CaptionBlock(
        left=left, right=right, rail="|", rail_rows=len(left),
        style_id="upside-down-t",
        fp={"rail": "drawn", "rail_band": (box["top"], box["bottom"]),
            "mid_x": mid, "vmid": True, "h_bottom": "full"},
        prov=m.Prov(pm.number, tuple(sorted(l.id for l in band)))))
    # THE FOOT RULE IS DRAWN ACROSS THE WHOLE MEASURE — a reader that
    # claims the block re-emits the fences the page set, at the measure
    # the page set them.
    items.append(m.Rule(prov=m.Prov(pm.number), span="full"))

    # --- the criteria ------------------------------------------------------
    caption_rows = [_strip_tags(r.text) for r in left if _strip_tags(r.text)]
    crit["caption"] = caption_rows
    sides = _sides(caption_rows)
    if sides:
        crit["parties"] = sides
        crit["case_name"] = (f"{sides[0]} v. {sides[1]}" if len(sides) >= 2
                             else sides[0])
    for text in dates:
        value = find_date(text)
        if value:                         # one record's date is an unfilled
            crit["decision_date"] = value  # Word field: no value, no claim
            break
    for text in list(origin) + list(lower_dockets):
        for hit in _BRACKET.findall(text):
            if hit not in lower_dockets_out:
                lower_dockets_out.append(hit)
    if origin:
        # A MOTION stated on the origin's own row ('COURT; MOTION TO FILE
        # BELATED REPLY BRIEF') is a second statement the court ran on.
        head_txt = " ".join(origin)
        cut = head_txt.upper().find("; MOTION")
        if cut > 0:
            motion.insert(0, head_txt[cut + 2:])
            head_txt = head_txt[:cut]
        crit["lower_court"] = _norm(_BRACKET.sub("", head_txt)).rstrip(" ,;")
    if lower_dockets_out:
        crit["lower_court_docket"] = lower_dockets_out
    if judge:
        crit["lower_court_judge"] = " ".join(judge)
    if motion:
        crit["motion"] = " ".join(motion)
    if label:
        crit["disposition"] = " ".join(label)

    return {"criteria": crit, "items": items, "attorneys": [], "dropped": [],
            "consumed": consumed, "anchor_ids": [], "doc_type_final": None}


# --------------------------------------------------------------------------
# the hand-down notice
# --------------------------------------------------------------------------

def _read_notice(model, geom, pm):
    """The sheet the court posts on a day it releases nothing.

    One page, no drawn caption, and every content row CENTRED — an
    opinion of this court always sets prose at the body rail, so a page
    with no left-aligned row has no body to have lost, and an empty
    `opinions` list is the correct output."""
    if model.n_pages != 1:
        return NOTHING
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 13.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = [l for l in pm.lines
            if l.plain.strip() and not finder.kind(pm, l)]
    rows.sort(key=lambda l: (l.top, l.x0))
    if not (1 <= len(rows) <= 4):
        return NOTHING
    if any(_align(l, pm, geom, body_size) is not m.Align.CENTER for l in rows):
        return NOTHING

    crit: dict = {"headmatter_style": STYLE_NOTICE}
    items: list = []
    consumed: set[int] = set()
    for line in rows:
        text = _norm(line.plain)
        date = find_date(text)
        role = "date" if date else "title"
        if date:
            crit.setdefault("decision_date", date)
        else:
            crit.setdefault("title", text)
        items.append(m.HmLine(
            text=line_markup(line), prov=m.Prov(pm.number, (line.id,)),
            align=m.Align.CENTER, x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role=role))
        consumed.add(line.id)
    if "title" not in crit:
        return NOTHING
    return {"criteria": crit, "items": items, "attorneys": [], "dropped": [],
            "consumed": consumed, "anchor_ids": [],
            "doc_type_final": m.DocType.NOTICE}
