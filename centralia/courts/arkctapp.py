"""Arkansas Court of Appeals ('arkctapp').

Everything unique to arkctapp lives here. It imports core, never another
court file, and no other court file imports it.

THE CONTRACT — 'open caption box'. The Court of Appeals prints on the
Supreme Court of Arkansas's paper: it DRAWS the caption's column divider,
closes it with one rule across the whole measure, and draws nothing over
its head. That upside-down T is the entire zone system, on all 42
records:

    Cite as 2026 Ark. App. 344                  the reporter citation
    ARKANSAS COURT OF APPEALS                   the masthead, 18pt bold
    DIVISION IV                                 which division sat
    No. CR-25-665                               the court's own docket
                             │ Opinion Delivered: May 20, 2026
    AARON BARR               │                  ← the divider, drawn
              APPELLANT      │ APPEAL FROM THE CLAY
    V.                       │ COUNTY CIRCUIT COURT,
                             │ EASTERN DISTRICT
    STATE OF ARKANSAS        │ [NO. 11PCR-18-70]
              APPELLEE       │ HONORABLE PAMELA
                             │ HONEYCUTT, JUDGE
                             │
                             │ AFFIRMED; MOTION TO WITHDRAW GRANTED
    ─────────────────────────────────────────   the foot rule, full measure
    MIKE MURPHY, Judge                          ← the reader stops

    What stands ABOVE the divider is the masthead band; LEFT of it, the
    parties; RIGHT of it, the court's statements about the case; BELOW
    the foot rule, the writings. Column membership is decided by which
    side of the drawn line a row sits on — never by what the row says.
    All 42 records draw it, at x/width 0.495-0.522, with a foot rule
    0.77-0.93 of the measure standing on the divider's own foot; not one
    draws a head rule, which is what makes this an open T rather than
    core's 'i-beam' or 'backwards-c'.

    The RIGHT COLUMN is a stack of STATEMENTS, not of rows: each one may
    wrap over as many rows as the column is narrow. A statement ends
    where the next one opens, and each opens either on a word from a
    closed vocabulary ('Opinion Delivered', 'APPEAL FROM', '[NO.',
    'HONORABLE', 'MOTION') or, for the one statement that carries no
    opener — what the court DID — on a stand-off of more than one and a
    half lines. Measured over the corpus: a wrap sits 15.6pt under its
    own first row and the smallest stand-off before a disposition is
    26.7pt.

WHAT THIS COURT SETS THAT ITS SUPREME COURT DOES NOT.

  * A DIVISION ROW ('DIVISION IV', 'DIVISIONS III & IV') stands between
    the masthead and the docket on every record — the panel that sat,
    named the way this court names it. It is kept as `panel_line`.

  * THE STATUS IS SET ON THE PARTY'S OWN ROW as often as under it, and
    the two are one extracted row ('BRODERICK PODOLAK APPELLANT'). On
    one record the overlay actually collides — 'EMILY GRACE
    BRINLEYA PPELLANT' — so the split cannot be geometric: the pieces
    overlap. A trailing status is taken off by the closed ROLE
    vocabulary, matched over the row's letters with the spacing ignored,
    and only ever off the END of a row. The printed row still renders as
    the page set it; only `parties` sees the split.

  * THE DOCKET LABEL MAY FALL INSIDE THE BOX. One record sets the
    number bare in the masthead band ('CV-25-460') and leaves its 9pt
    'No.' label stranded in the caption's left column. The label is
    still the label: it renders where the page put it and is not read
    as a party.

  * THE DELIVERY DATE RUNS ONTO ITS LABEL ('Opinion DeliveredMay 20,
    2026' — the field is set without its trailing space on 20 of the 42
    records). The date is therefore read out of the REMAINDER of the
    statement its label opens, never out of the whole row: a month name
    welded to a word is no month name at all.

A record that draws no divider is not this paper and gets NOTHING:
core's shared walk places those rows unidentified, which is a smaller
error than a confident misreading.

WHAT THE READER DOES NOT TOUCH. arkctapp prints its appearances BELOW
the writings ('Wilkinson Law Firm, by: Bryan Altman, for appellant.' /
'One brief only.'). The reader stops at the caption's foot rule and
never reaches into a writing.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..geometry import line_alignment
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import find_date, looks_like_docket

# arkctapp's CourtProfile is registered in `courts/__init__.py` (shared
# file); this module owns the reader only.
STYLE_BOX = "open caption box"

# ---- arkctapp's declared facts (measured over the corpus, not tuned) -----
# THE DIVIDER is a drawn vertical — pdfio reports the two edges of a thin
# filled rect, 1.4pt apart. It stands at 0.495-0.522 of the measure on all
# 42 records and is as tall as the caption (147pt at the shortest).
_DIVIDER_MIN_H = 40.0
_DIVIDER_BAND = (0.42, 0.62)
# THE FOOT RULE closes the box: 468.0-571.7pt on a 612pt sheet (0.765 to
# 0.934 of the measure), its top on the divider's own foot.
_FOOT_MIN_W = 0.60
_FOOT_JOIN = 8.0
# A HEAD RULE would make this a different box. This court never draws one,
# and a record that does is not this contract.
_HEAD_JOIN = 8.0
# THE MASTHEAD is set 18pt over a 13pt body — the only enlarged row on
# the page.
_MASTHEAD_MIN_SIZE = 16.0
# HOW A RIGHT-COLUMN STATEMENT ENDS. A wrap sits one leading (15.6pt at
# 13pt type) under its own first row; the stand-off before a new
# statement is 26.7pt at the tightest. 1.6 type sizes = 20.8pt separates
# them with room on both sides.
_WRAP_GAP = 1.6
# ONE VISUAL ROW. The two columns are set on independent baselines and
# the party's own status is set on a third: over the corpus a pair the
# page sets level is staggered by up to 3.6pt, while the tightest
# leading INSIDE either column is 11.6pt. 4pt separates them.
_ROW_TOL = 4.0

# THE COURT NAMES ITSELF in one row, on every paper it prints.
_MASTHEAD = "arkansas court of appeals"
# THE REPORTER CITATION the clerk stamps at the head of page 1 ('Cite as
# 2026 Ark. App. 344'). It is not a running head — pages 2+ carry none.
_CITE_OPENER = "cite as"
# THE COURT'S OWN DOCKET, in the series it prints: CR (criminal), CV
# (civil), E (employment security). One record drops the 'No.' label off
# the front of it and leaves the label behind in the caption.
_DOCKET = re.compile(r"^(?:Nos?\.\s*)?[A-Z]{1,2}-\d{2}-\d{1,5}\.?$", re.I)
_DOCKET_LABEL = re.compile(r"^Nos?\.?$", re.I)
# WHICH DIVISION SAT. The court sits in numbered divisions and says so
# under its own name, alone or in pairs ('DIVISIONS III & IV').
_DIVISION = re.compile(
    r"^DIVISIONS?\s+[IVX]+(?:\s*(?:&|AND|,)\s*[IVX]+)*$", re.I)
# WHEN THE COURT HANDED THE CASE DOWN, labelled in the right column's
# first cell. The label is the landmark; the value is read out of what
# follows it — the field is set without its trailing space on half the
# corpus ('Opinion DeliveredMay 20, 2026').
_DELIVERED = "opinion delivered"
# HOW THIS COURT NAMES THE TRIBUNAL IT REVIEWS. Openers only — what
# follows is that tribunal's own name, which is never read by wording.
_ORIGIN_OPENERS = (
    "appeal from", "appeals from", "on appeal from", "cross-appeal from",
    "pro se appeal from", "pro se appeals from", "pro se motion",
    "petition for", "on petition for", "certified question",
    "on certification from", "original action",
)
# THE NUMBER THE CASE CARRIES BELOW, always in the court's own brackets.
_LOWER_DOCKET = "["
# WHO TRIED IT. 'HONORABLE PAMELA HONEYCUTT, JUDGE'.
_JUDGE_OPENER = "honorable"
# A MOTION decided alongside the appeal, stated in the same column.
_MOTION_OPENER = "motion"

# WHERE A STATEMENT REALLY ENDS. A ';' does NOT end one here: this court
# joins the clauses of a single disposition with it ('AFFIRMED; MOTION TO
# WITHDRAW GRANTED;' / 'REMANDED TO CORRECT SENTENCING ORDER'), and read
# as an ending the disposition came back as two.
_TERMINATORS = (".", "]")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. Inside the drawn box the left column holds nothing else — the
# masthead stands above the divider — so a row that is not a status and
# not the pivot is a party, whatever it says. (Core's shared party reader
# vetoes rows carrying court words or 'attorney general', which here
# deletes 'DIRECTOR, DIVISION OF WORKFORCE SERVICES' and 'LESLIE
# RUTLEDGE, ARKANSAS ATTORNEY GENERAL' out of two parties' own names.)
_STATUS_WORDS = frozenset((
    "appellant", "appellants", "appellee", "appellees", "petitioner",
    "petitioners", "respondent", "respondents", "intervenor", "intervenors",
    "plaintiff", "plaintiffs", "defendant", "defendants", "movant",
    "movants", "amicus", "amici", "separate", "cross", "third", "party",
    "parties", "real", "interest", "and", "the", "in", "of", "pro", "se",
))
# THE SAME VOCABULARY AS A ROW'S TAIL — the labels only, never the
# connectives, because a tail is stripped off a party's own name and
# 'IN THE MATTER OF THE' ends in two of the connectives.
_STATUS_TAILS = tuple(sorted((
    "APPELLANT", "APPELLANTS", "APPELLEE", "APPELLEES",
    "CROSS-APPELLANT", "CROSS-APPELLANTS", "CROSS-APPELLEE",
    "CROSS-APPELLEES", "PETITIONER", "PETITIONERS", "RESPONDENT",
    "RESPONDENTS", "INTERVENOR", "INTERVENORS", "DEFENDANT", "DEFENDANTS",
    "PLAINTIFF", "PLAINTIFFS", "MOVANT", "MOVANTS",
), key=len, reverse=True))
# THE PIVOT, as this court sets it.
_PIVOTS = ("v", "vs")
# THE NUMBER THE CASE CARRIES BELOW, in the brackets the court always
# sets it in — stated on its own row, or run onto the end of the origin.
_BRACKET = re.compile(r"\[\s*NOS?\.?\s*([^\]]+?)\s*\]", re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _closed(text: str) -> bool:
    """Does this statement END here?

    The period after an INITIAL closes nothing — the court breaks the
    trial judge's name at one ('HONORABLE JOHNNIE A.' / 'COPELAND,
    JUDGE'), and read as a full stop the wrap opens a new statement and
    the judge's surname is published as part of the disposition."""
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


def _is_docket_cell(text: str) -> bool:
    """The court's own docket, or the bare label the overlay strands in
    the caption's left column ('No.')."""
    flat = _norm(text)
    return bool(_DOCKET_LABEL.match(flat) or _DOCKET.match(flat))


def _drop_status_tail(text: str) -> tuple[str, bool]:
    """``text`` with the party STATUS taken off its end.

    The court sets the status flush right on the party's own row as often
    as under it, and the two arrive as one extracted row. On one record
    the two overlays collide mid-glyph ('EMILY GRACE BRINLEYA PPELLANT'),
    so the split cannot be geometric — the pieces overlap. Match the
    closed role vocabulary over the row's LETTERS with the spacing
    ignored, and cut the original where that match begins."""
    flat = _norm(text)
    probe = flat.rstrip(",;: ")
    squeezed = re.sub(r"\s+", "", probe).upper()
    for tail in _STATUS_TAILS:
        if not squeezed.endswith(tail) or len(squeezed) <= len(tail):
            continue
        keep = len(squeezed) - len(tail)
        seen = 0
        for i, ch in enumerate(probe):
            if seen == keep:
                return probe[:i].rstrip(",;:/ "), True
            if not ch.isspace():
                seen += 1
        return probe, True
    # NOTHING WAS TAKEN OFF, so nothing is trimmed either: the ';' a
    # party row wraps on belongs to the party list it is part of.
    return flat, False


def _sides(cells: list[str]) -> list[str]:
    """The party sides, bounded structurally: a side runs to its STATUS —
    on its own row or on the tail of the party's — and the pivot
    separates the two."""
    sides: list[str] = []
    cur: list[str] = []

    def close():
        if cur:
            sides.append(_norm(" ".join(cur)).rstrip(",; "))
            cur.clear()

    for row in cells:
        flat = _norm(row)
        if not flat or _is_docket_cell(flat):
            continue
        if _is_pivot(flat) or _is_status(flat):
            close()
            continue
        head, statused = _drop_status_tail(flat)
        if head:
            cur.append(head)
        if statused:
            close()
    close()
    return sides


# --------------------------------------------------------------------------
# the box — arkctapp's zone system, and the dispatch
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
            kind = None                  # an opener may not RE-open the
                                         # statement it is already in
        # AN UNCLOSED BRACKET IS AN OPEN STATEMENT. The court breaks the
        # number below across the column ('COUNTY CIRCUIT COURT [NO.' /
        # '73CR-20-604]'), and the '.' the label ends on is not the end
        # of a sentence — read as one, the docket became a disposition.
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


def _mend(text: str) -> str:
    """A statement's PARSED form, mended where the column broke it.

    Two things the narrow column does to a statement and to nothing
    else: it breaks a word at a hyphen ('DISMISSED AS MOOT ON CROSS-' /
    'APPEAL'), and one record sets its disposition letter-spaced
    ('A  F  F  I  R  M  E  D'). The printed rows are untouched — this is
    the queryable form beside them."""
    flat = _norm(text)
    flat = re.sub(r"(\w)-\s+(\w)", r"\1-\2", flat)
    words = flat.split()
    if len(words) > 2 and all(len(w) == 1 and w.isalpha() for w in words):
        return "".join(words)
    return flat


def _delivered_date(text: str) -> str | None:
    """The date out of the statement its LABEL opens.

    'Opinion DeliveredMay 20, 2026' — the field is set without its
    trailing space on 20 of the 42 records, and a month name welded to a
    word is no month name at all. Read the remainder, not the row."""
    flat = _norm(text)
    rest = flat[len(_DELIVERED):] if flat.lower().startswith(_DELIVERED) \
        else flat
    return find_date(rest.lstrip(" : "))


# --------------------------------------------------------------------------
# the walk
# --------------------------------------------------------------------------

@decider("headmatter.read", court="arkctapp")
def read_headmatter_arkctapp(model, geom, **_):
    """Read arkctapp's open-caption-box headmatter, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    box = _box(page1)
    if box is None:
        return NOTHING
    return _read_box(model, geom, page1, box)


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
                return NOTHING            # enlarged type that is not this
            crit.setdefault("court", text)  # court's own name
            emit(line, "court")
        elif _DIVISION.match(text):
            crit.setdefault("panel_line", text)
            emit(line, "panel")
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
        for cell_line in sorted(l_cells, key=lambda l: l.x0):
            left_cells.append((cell_line, _norm(cell_line.plain)))
        for cell_line in sorted(r_cells, key=lambda l: l.x0):
            right_cells.append((cell_line, _norm(cell_line.plain)))
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
    crit["caption"] = [_strip_tags(r.text) for r in left
                       if _strip_tags(r.text)]
    sides = _sides([flat for _, flat in left_cells])
    if sides:
        crit["parties"] = sides
        crit["case_name"] = (f"{sides[0]} v. {sides[1]}" if len(sides) >= 2
                             else sides[0])
    for text in dates:
        value = _delivered_date(text)
        if value:
            crit["decision_date"] = value
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
        crit["lower_court"] = _mend(_BRACKET.sub("", head_txt)).rstrip(" ,;")
    if lower_dockets_out:
        crit["lower_court_docket"] = lower_dockets_out
    if judge:
        crit["lower_court_judge"] = _mend(" ".join(judge))
    if motion:
        crit["motion"] = _mend(" ".join(motion))
    if label:
        crit["disposition"] = _mend(" ".join(label))

    return {"criteria": crit, "items": items, "attorneys": [], "dropped": [],
            "consumed": consumed, "anchor_ids": [], "doc_type_final": None}
