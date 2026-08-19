"""Supreme Court of Vermont ('vt').

Everything unique to vt lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is already
registered in courts/__init__.py.

Vermont prints TWO papers, and the caption's own divider names which one.
Measured over all 50 records: 41 set the caption in two columns with nothing
but WHITESPACE between them (core's catalog: `open-range`), 9 set it with a
stacked '}' brace (`gathering-brace`). Nothing is decided by wording.

PAPER A — THE OPEN RANGE (41 records: 32_intervale, state_v._andy_lagore, …)

    ┌──────────────────────────────────────────────────────────────────┐
    │ NOTICE: This opinion is subject to motions for reargument …      │ furniture
    │ … of any errors in order that corrections may be made before     │ (5 rows,
    │ this opinion goes to press.                                      │  dropped)
    │                       2026 VT 9                    the cite      │
    │                     No. 25-AP-248                  the docket    │
    │ 32 Intervale, LLC et al.       │ Supreme Court     ← the court   │
    │                                │ On Appeal from                  │
    │ v.                             │ Superior Court,   ← the origin  │
    │                                │ Environmental Division          │
    │ City of Burlington             │ February Term, 2026 ← the term  │
    │ Joseph S. McLean, J.                       the judge below       │
    │ Liam L. Murphy … for Plaintiffs-Appellants.  the appearances      │
    │     Rachel L. Seelig … for Defendant-Appellee.                   │
    │ PRESENT: Reiber, C.J., Eaton, Waples and Drescher, JJ., and …    │
    │     Specially Assigned                     the panel             │
    │        ¶ 1.  EATON, J. Seventeen Burlington property owners …    │ the paper
    └──────────────────────────────────────────────────────────────────┘

    There is no drawn or typed divider anywhere on the page (`h_rules` on
    page 1 is empty or holds only footnote separators). The two columns are
    a WHITESPACE GUTTER: the left cell sits at the body rail (72.0, the
    pivot 'v.' one step in at 87.0) and the right cell starts at a shared
    edge measured at 373.1 on 88 rows and 367.8 on 4 — never between. That
    shared right edge IS the divider, and column membership is decided by
    it, never by what a row says.

    THE BAND'S BOUNDS ARE LANDMARKS, NOT ORDINALS. It OPENS on the first row
    carrying a right-column piece and CLOSES on the first row below that
    matches the BENCH VOCABULARY at the rail — a closed vocabulary
    ('…, J.' / '…, J. (Ret.)' / '…, Chair' / '…, Acting Chair' /
    '…, Commissioner' / '…, Appellate Officer'), which is what the origin
    judge's line is and what no counsel row in the corpus is. Closing on
    the TERM row instead loses a party-name wrap set below it, which three
    records print (agency_of_transportation '(R.L. Vallee, Inc. & Crystal
    Clear Hospitality, LLC)', ciara_kilburn 'Access Media, Inc.',
    garret_hirchak 'Hirchak Brothers LLC, and Hirchak Group LLC').

PAPER B — THE GATHERING BRACE (9 records: the entry orders)

    ┌──────────────────────────────────────────────────────────────────┐
    │ NOTICE: This entry order is subject to motions for reargument …  │ furniture
    │                     ENTRY ORDER                    the title     │
    │                      2025 VT 11                    the cite      │
    │            SUPREME COURT CASE NO. 25-AP-048        the docket    │
    │                  FEBRUARY TERM, 2025               the term      │
    │ State of Vermont          } APPEALED FROM:                       │
    │                           }                                      │
    │ v.                        } Superior Court, Chittenden Unit,     │
    │                           } Criminal Division                    │
    │                           } CASE NO. 24-CR-08894                 │
    │ Aaliyah Johnson           }                                      │
    │                             Trial Judge: David R. Fenster        │
    │        In the above-entitled cause, the Clerk will enter:        │ the paper
    └──────────────────────────────────────────────────────────────────┘

    The '}' column is the parser. Measured x0: 312.4 on 51 glyphs (the seven
    printed on the Reporter's notice paper), 287.8/288.0 on 3 (in_re_shawn_t.
    _tao) and 295.6 on 3 (state_v._jason_robinson). Cells are split GLYPH BY
    GLYPH at that edge, because whether pdfio broke the visual row at the
    brace was an accident of the gap: aaliyah_johnson sets 'State of Vermont'
    / '}' / 'APPEALED FROM:' as three runs, jason_robinson welds the brace
    onto its right cell ('} APPEALED FROM:'), and tao welds the WHOLE row
    ('In re Shawn T. Tao (Office of Disciplinary } Original Jurisdiction').

    Two of the nine (in_re_shawn_t._tao, state_v._jason_robinson) are printed
    on the clerk's LETTERHEAD instead of the Reporter's notice paper —
    'VERMONT SUPREME COURT' over the Montpelier address, with 'Case No.' set
    flush right on the masthead row. The address rows and the e-filing stamp
    are dropped; the masthead is the court and the flush-right number is the
    docket. Neither of those two prints a public-domain cite.

    THE BAND CLOSES ON THE RECITAL. 'In the above-entitled cause, the Clerk
    will enter:' is the order's own opening sentence, not headmatter, and it
    is DELIBERATELY LEFT UNCLAIMED — it is what core opens the order writing
    on. All 9 records print it.

WHAT THE PARAGRAPH MARKS DO. vt numbers with '¶ 1.' set as its own run at
x0=108 with the text of the paragraph at 144 — NOT the bracket form '[¶4]'
that core's note in resolve/assemble.py ascribes to it. 48 of the 50 open
their first paragraph that way on page 1; in_re_shawn_t._tao and
state_v._jason_robinson number nothing. The reader ends above the first
such row and never reaches into the writing.

THE CRITERIA FIELD NAMES ARE THE MODEL'S. `Criteria` (centralia/model.py)
has no `docket` field and no `argued` field: the docket is `docket_number`
(a string) plus `other_dockets` (the rest), and the term the case was heard
in belongs in `submitted`. Written under an undeclared name they are
attached by setattr and never serialize.
"""

from __future__ import annotations

import re
from dataclasses import replace as _replace

from .. import model as m
from ..resolve.captions import classify_page
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup

# ---- vt's declared facts (measured over all 50 records, not tuned) -------

# Page 1 carries the whole block on every record; nothing spills to page 2.
_MAX_PAGES = 1

# The public-domain cite, centred: '2026 VT 9' … '2026 VT 16'. Measured
# centred at x0 271.6-280.0 on a 612pt page; 48 records print one (the two
# letterhead entry orders do not).
_CITE = re.compile(r"^\d{4}\s*VT\s*\d+[A-Z]?$", re.I)
# The slip's docket, centred: 'No. 25-AP-248', 'Nos. 25-AP-114 & 25-AP-134'.
_DOCKET_SLIP = re.compile(r"^Nos?\.\s*(\S.*)$")
# The entry order's docket, centred: 'SUPREME COURT CASE NO. 25-AP-048'.
_DOCKET_ORDER = re.compile(r"^SUPREME COURT CASE NOS?\.\s*(\S.*)$", re.I)
# 'Case No.' flush right on the letterhead masthead row (tao, jason_robinson).
_CASE_NO_LABEL = re.compile(r"^Case Nos?\.$", re.I)
_DOCKET_BARE = re.compile(r"^\d{2}-AP-\d{3}$")
# The term the case was heard in. Title case in the right column of paper A
# ('February Term, 2026'), full caps and centred on paper B ('MARCH TERM,
# 2025'). All 50 records print exactly one.
_TERM = re.compile(r"^([A-Z][A-Za-z]+)\s+TERM,\s*(\d{4})$", re.I)
# What paper B calls itself.
_ENTRY_ORDER = re.compile(r"^ENTRY ORDER$", re.I)
# The order's own first sentence — the row the reader stops above.
_RECITAL = re.compile(r"^In the above-entitled cause", re.I)
# The Reporter's slip-cover notice: 5 rows at the body rail, opening
# 'NOTICE: This opinion|entry order is subject to' and closing on 'goes to
# press.' One record prints a stray glyph before it (in_re_o.r.g.,
# 'FNOTICE:'), so the opener is matched with one optional leading character.
_NOTICE_OPEN = re.compile(r"^.?NOTICE:\s*This\s+(?:opinion|entry order)\s+is"
                          r"\s+subject\s+to", re.I)
_NOTICE_CLOSE = re.compile(r"goes to press\.\s*$", re.I)
# The asterisk key the letterhead prints instead of the notice
# (state_v._jason_robinson), 2 rows.
_ASTERISK_NOTE = re.compile(r"^Note:\s*In the case title, an asterisk", re.I)
_ASTERISK_CLOSE = re.compile(r"cross-appellant\.\s*$", re.I)
# The clerk's letterhead, below its masthead: street, city, telephone, url.
# ('802-828-47 74' carries an internal space in tao.)
_LETTERHEAD = re.compile(r"^(?:\d+\s+State Street$|Montpelier VT\b"
                         r"|\d{3}-\d{3}-[\d ]+$|www\.)", re.I)
_MASTHEAD = re.compile(r"^VERMONT SUPREME COURT$")
# tao's e-filing stamp, printed in the top 25pt at the extreme left edge.
_EFILE_TOP_MAX = 25.0
_EFILE_X_MAX = 12.0
_FILED_STAMP = re.compile(r"^Filed:\s*([A-Z][a-z]+)\s*(\d{1,2}),\s*(\d{4})$")

# THE BENCH VOCABULARY — what the line naming the judge below ends with.
# Measured across the 41 open-range records: '…, J.', '…, J. (Ret.)',
# '…, J. (motion to suppress)', '…, Chair', '…, Acting Chair',
# '…, Commissioner', '…, Appellate Officer'. No counsel row in the corpus
# matches it (checked: 0 false hits over every appearance row).
_BENCH = re.compile(
    r",\s*(?:J\.|JJ\.|Judge|Chief Judge|Chair|Acting Chair|Commissioner"
    r"|Appellate Officer|Hearing Officer|Supr\.\s*J\.)(?:\s|\(|;|$)")
# Paper B's right column labels the origin outright.
_APPEALED_FROM = re.compile(r"^(?:APPEALED FROM:?|Original Jurisdiction)$",
                            re.I)
_CASE_NO_BELOW = re.compile(r"^CASE NOS?\.\s*(\S.*)$", re.I)
_TRIAL_JUDGE = re.compile(r"^Trial Judge:\s*(\S.*)$", re.I)
# Paper A's right column heads its origin with the posture.
_ON_APPEAL = re.compile(r"^On Appeal from$", re.I)
_PRESENT = re.compile(r"^PRESENT:\s*(.*)$")
_PIVOT = re.compile(r"^v\.?$|^vs\.?$", re.I)
_PARA = re.compile(r"^\[?\s*¶+\s*\d+\s*[.)\]]?(?:\s|$)")
# A caption row that is wholly parenthetical names an appearance status, not
# a party ('(Carolyn Bates et al., Appellants)') — kept in the printed rows
# and out of the parsed party names.
_PARENTHETICAL = re.compile(r"^\(.*\)$")

# The step from the rail that makes a row a CONTINUATION of the entry above
# it. Measured: counsel wraps at 78.0 and 81.0, the judge-below wrap at
# 78.0, the panel's 'Specially Assigned' at 135.0, against a rail of 72.0.
_INDENT_MIN = 3.0
# The right column's own edge, measured: 367.8-373.2, i.e. never below
# 0.58 of a 612pt measure and never crossed by a left-column row.
_RIGHT_MIN_FRAC = 0.55
_RIGHT_TOL = 4.0
# A whitespace gutter is only a caption divider where a STACK stands on it.
# Measured minimum over the 41 records: 4 rows (court, posture, one origin
# row, term).
_RIGHT_MIN_ROWS = 3

STYLE_OPEN_RANGE = "open-range slip"
STYLE_BRACE = "gathering-brace entry order"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _row_text(row: list) -> str:
    return _norm(" ".join(l.plain for l in row))


def _rows(pm) -> list[list]:
    """The page's VISUAL rows, pieces kept together and ordered left to
    right. pdfio has already tagged the runs of a row split at a column gap
    with a shared `row` id; a run it did not split is its own row."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = ("r", line.row) if line.row is not None \
            else ("t", round(line.top, 1))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _side(line, mid: float, want: str):
    """The part of ``line`` lying one side of the divider, or None. Copied
    from ca6 — a two-column caption splits GLYPH BY GLYPH at the rail,
    because whether pdfio broke the row there was an accident of the gap."""
    keep = [c for c in line.chars
            if ((c["x0"] + c.get("x1", c["x0"])) / 2 < mid) == (want == "L")]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


def _shed_brace(line, rail_x: float):
    """The line with the rail's own '}' glyphs removed, or None when the
    line WAS the rail."""
    keep = [c for c in line.chars
            if not ((c.get("text") or "") == "}"
                    and abs(c["x0"] - rail_x) < 14.0)]
    if not any((c.get("text") or "").strip() for c in keep):
        return None
    if len(keep) == len(line.chars):
        return line
    x0 = min(c["x0"] for c in keep)
    x1 = max(c.get("x1", c["x0"]) for c in keep)
    return _replace(line, chars=keep, x0=x0, x1=x1)


# --------------------------------------------------------------------------
# the decider
# --------------------------------------------------------------------------

@decider("headmatter.read", court="vt")
def read_headmatter_vt(model, geom, **_):
    """Read Vermont's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 72.0
    rows = _rows(pm)
    if len(rows) < 6:
        return NOTHING
    sig, style_id, _name = classify_page(pm)

    # DISPATCH ON THE DIVIDER. A stacked '}' is paper B; a whitespace gutter
    # with a stack standing on it is paper A; anything else is not vt's
    # paper and is left to core rather than forced through a contract.
    if sig.get("rail") == "}":
        return _read_brace(pm, rows, body_x0, style_id)
    rail = _right_rail(pm, rows)
    if rail is not None and not sig.get("vmid") and not sig.get("rail"):
        return _read_open_range(pm, rows, body_x0, rail, style_id)
    return NOTHING


def _right_rail(pm, rows: list) -> float | None:
    """The right column's own left edge, or None when no stack stands on
    the gutter. Measured 367.8-373.2 over the 41 open-range records."""
    floor = pm.width * _RIGHT_MIN_FRAC
    edges = [round(l.x0, 1) for row in rows for l in row if l.x0 >= floor]
    if len(edges) < _RIGHT_MIN_ROWS:
        return None
    edge = min(edges)
    if sum(1 for e in edges if abs(e - edge) <= _RIGHT_TOL) \
            < _RIGHT_MIN_ROWS:
        return None
    return edge


# --------------------------------------------------------------------------
# PAPER A — the open range
# --------------------------------------------------------------------------

def _read_open_range(pm, rows: list, body_x0: float, rail: float,
                     style_id):
    ctx = _Ctx()

    # ---- the landmarks, found before anything is emitted ----------------
    def right_of(row):
        return [l for l in row if l.x0 >= rail - _RIGHT_TOL]

    i_notice = _find(rows, lambda r: _NOTICE_OPEN.match(_row_text(r)))
    i_cite = _find(rows, lambda r: _CITE.match(_row_text(r)))
    i_cap0 = _find(rows, lambda r: bool(right_of(r)))
    i_para = _find(rows, lambda r: any(_PARA.match(_norm(l.plain))
                                       for l in r))
    i_present = _find(rows, lambda r: _PRESENT.match(_row_text(r)))
    if i_cap0 is None or i_present is None or i_cite is None:
        return NOTHING
    # The band closes on the bench vocabulary, never on an ordinal.
    i_judge = _find(rows, lambda r: (not right_of(r))
                    and bool(_BENCH.search(_row_text(r))), start=i_cap0 + 1)
    if i_judge is None or not (i_cite < i_cap0 < i_judge < i_present):
        return NOTHING
    if i_para is not None and i_para < i_present:
        return NOTHING
    # The panel is the PRESENT row plus its indented wrap; the block ends
    # there. Anchored on the row PRESENT was found at.
    i_end = i_present
    while i_end + 1 < len(rows) \
            and rows[i_end + 1][0].x0 > body_x0 + _INDENT_MIN \
            and not any(_PARA.match(_norm(l.plain)) for l in rows[i_end + 1]):
        i_end += 1

    # ---- the Reporter's notice, dropped ---------------------------------
    if i_notice is not None and i_notice < i_cite:
        _drop_run(ctx, rows, i_notice, i_cite, _NOTICE_CLOSE, "notice")

    # ---- the identifiers -------------------------------------------------
    for idx in range(i_cite, i_cap0):
        row = rows[idx]
        text = _row_text(row)
        if _CITE.match(text):
            ctx.crit.setdefault("citation", text)
            ctx.emit(row, "citation", centre=True)
            continue
        dk = _DOCKET_SLIP.match(text)
        if dk:
            _record_dockets(ctx, dk.group(1))
            ctx.emit(row, "docket", centre=True)
            continue
        # A ROW AT NO POSITION THIS PAPER USES is not guessed at: the claim
        # would be a mis-tag, and a mis-tag is worse than an unread row.
        return NOTHING

    # ---- the caption band, as a two-column block ------------------------
    block, left_plain, right_plain = _caption_block(
        pm, rows[i_cap0:i_judge], rail, None, style_id,
        _open_range_roles)
    if block is None:
        return NOTHING
    ctx.items.append(block)
    for row in rows[i_cap0:i_judge]:
        ctx.consumed.update(l.id for l in row)
    _record_caption(ctx, left_plain)
    origin: list[str] = []
    for text in right_plain:
        if not text or _ON_APPEAL.match(text) or _TERM.match(text):
            continue
        if len(origin) == 0 and text == "Supreme Court":
            continue                     # the deciding court, not the origin
        origin.append(text)
    if origin:
        ctx.crit.setdefault("lower_court", _norm(" ".join(origin)))
    for text in right_plain:
        if _TERM.match(text):
            ctx.crit.setdefault("submitted", text)

    # ---- the judge below, the appearances, the panel --------------------
    band = "judge"
    judge: list[str] = []
    counsel: list[str] = []
    for idx in range(i_judge, i_end + 1):
        row = rows[idx]
        text = _row_text(row)
        wrap = row[0].x0 > body_x0 + _INDENT_MIN
        if idx >= i_present or band == "panel":
            band = "panel"
            ctx.emit(row, "panel", centre=False)
            continue
        if band == "judge" and (wrap or _BENCH.search(text)):
            judge.append(text)
            ctx.emit(row, "lower-court", centre=False)
            continue
        band = "counsel"
        counsel.append(text)
        ctx.emit(row, "counsel", centre=False)
    if judge:
        ctx.crit.setdefault("lower_court_judge", _norm(" ".join(judge)))
    if counsel:
        ctx.crit.setdefault("attorneys", _norm(" ".join(counsel))[:2000])
    _record_panel(ctx, [_row_text(rows[i]) for i in range(i_present,
                                                          i_end + 1)])
    ctx.crit.setdefault("headmatter_style", STYLE_OPEN_RANGE)
    return ctx.result()


def _open_range_roles(kind: str, texts: list[str], index: int) -> str:
    """Which role a cell of paper A's caption carries. Anchored on what the
    column PRINTS, not on the row's ordinal: the court names itself in the
    right column's first filled cell, the term is the row that states one,
    and everything between is the origin."""
    if kind == "L":
        return "caption"
    text = texts[index]
    if _TERM.match(text):
        return "date"
    filled = [i for i, t in enumerate(texts) if t]
    if filled and index == filled[0]:
        return "court"
    return "lower-court"


# --------------------------------------------------------------------------
# PAPER B — the gathering brace
# --------------------------------------------------------------------------

def _read_brace(pm, rows: list, body_x0: float, style_id):
    ctx = _Ctx()
    rail_x = _brace_x(rows)
    if rail_x is None:
        return NOTHING

    i_notice = _find(rows, lambda r: _NOTICE_OPEN.match(_row_text(r)))
    i_note = _find(rows, lambda r: _ASTERISK_NOTE.match(_row_text(r)))
    i_title = _find(rows, lambda r: _ENTRY_ORDER.match(_row_text(r)))
    i_cap0 = _find(rows, lambda r: any("}" in (l.plain or "") for l in r))
    i_recital = _find(rows, lambda r: _RECITAL.match(_row_text(r)))
    if i_title is None or i_cap0 is None or i_recital is None:
        return NOTHING
    if not (i_title < i_cap0 < i_recital):
        return NOTHING

    # ---- the Reporter's notice / the asterisk key, dropped --------------
    if i_notice is not None and i_notice < i_title:
        _drop_run(ctx, rows, i_notice, i_title, _NOTICE_CLOSE, "notice")
    if i_note is not None and i_note < i_title:
        _drop_run(ctx, rows, i_note, i_title, _ASTERISK_CLOSE, "notice")

    # ---- the letterhead / the identifiers -------------------------------
    anchor: list[int] = []
    for idx in range(0, i_cap0):
        row = rows[idx]
        text = _row_text(row)
        if any(l.id in ctx.consumed for l in row):
            continue
        # tao's e-filing stamp, by its POSITION in the top band at the
        # extreme left edge — it states the filing date, which is a fact.
        if row[0].top < _EFILE_TOP_MAX and row[0].x0 < _EFILE_X_MAX:
            stamp = _FILED_STAMP.match(text)
            if stamp:
                ctx.crit.setdefault(
                    "decision_date",
                    f"{stamp.group(1)} {stamp.group(2)}, {stamp.group(3)}")
            ctx.drop(row, "stamp")
            continue
        if _NOTICE_OPEN.match(text) or _ASTERISK_NOTE.match(text):
            ctx.drop(row, "notice")
            continue
        if _LETTERHEAD.match(text):
            ctx.drop(row, "letterhead")
            continue
        if _ENTRY_ORDER.match(text):
            ctx.crit.setdefault("title", text)
            anchor.extend(l.id for l in row)
            ctx.emit(row, "title", centre=True)
            continue
        if _CITE.match(text):
            ctx.crit.setdefault("citation", text)
            ctx.emit(row, "citation", centre=True)
            continue
        dk = _DOCKET_ORDER.match(text)
        if dk:
            _record_dockets(ctx, dk.group(1))
            ctx.emit(row, "docket", centre=True)
            continue
        if _TERM.match(text):
            ctx.crit.setdefault("submitted", text)
            ctx.emit(row, "date", centre=True)
            continue
        # The letterhead masthead row: the court at the rail, 'Case No.' and
        # its value flush right on the SAME row.
        head = [l for l in row if _MASTHEAD.match(_norm(l.plain))]
        if head:
            ctx.emit(head, "court", centre=False)
            rest = [l for l in row if l not in head]
            if rest:
                for l in rest:
                    if _DOCKET_BARE.match(_norm(l.plain)):
                        _record_dockets(ctx, _norm(l.plain))
                ctx.emit(rest, "docket", centre=False)
            continue
        return NOTHING

    # ---- the braced caption band ----------------------------------------
    block, left_plain, right_plain = _caption_block(
        pm, rows[i_cap0:i_recital], rail_x + 4.0, "}", style_id,
        _brace_roles, rail_x=rail_x)
    if block is None:
        return NOTHING
    ctx.items.append(block)
    for row in rows[i_cap0:i_recital]:
        ctx.consumed.update(l.id for l in row)
    _record_caption(ctx, left_plain)
    origin: list[str] = []
    for text in right_plain:
        if not text:
            continue
        below = _CASE_NO_BELOW.match(text)
        if below:
            ctx.crit.setdefault("lower_court_docket", []).append(
                _norm(below.group(1)))
            continue
        tried = _TRIAL_JUDGE.match(text)
        if tried:
            ctx.crit.setdefault("lower_court_judge", _norm(tried.group(1)))
            continue
        if _APPEALED_FROM.match(text):
            continue
        origin.append(text)
    if origin:
        ctx.crit.setdefault("lower_court", _norm(" ".join(origin)))
    ctx.crit.setdefault("headmatter_style", STYLE_BRACE)
    out = ctx.result()
    out["anchor_ids"] = anchor
    return out


def _brace_x(rows: list) -> float | None:
    """The rail's own x, from the glyphs themselves. Measured 312.4 (51
    glyphs), 287.8/288.0 (3), 295.6 (3)."""
    xs = []
    for row in rows:
        for line in row:
            for ch in line.chars:
                if (ch.get("text") or "") == "}":
                    xs.append(ch["x0"])
    if len(xs) < 3:
        return None
    xs.sort()
    return xs[len(xs) // 2]


def _brace_roles(kind: str, texts: list[str], index: int) -> str:
    """Paper B's right column is the origin from top to bottom — the
    posture label, the tribunal, its case number, its judge."""
    return "caption" if kind == "L" else "lower-court"


# --------------------------------------------------------------------------
# shared: the two-column caption
# --------------------------------------------------------------------------

def _caption_block(pm, band: list, mid: float, glyph, style_id, roles,
                   rail_x: float | None = None):
    """The caption band as a CaptionBlock: cells PAIRED BY VISUAL ROW so
    the two stacks stay aligned, split at the divider glyph by glyph, the
    rail's own glyphs shed from whichever cell they fell into."""
    cells: list[tuple[list, list]] = []
    for row in band:
        left_cells, right_cells = [], []
        for line in row:
            piece = line if rail_x is None else _shed_brace(line, rail_x)
            if piece is None:
                continue                 # the line WAS the rail
            for want, bucket in (("L", left_cells), ("R", right_cells)):
                part = _side(piece, mid, want)
                if part is not None:
                    bucket.append(part)
        cells.append((left_cells, right_cells))
    # THE RAIL'S OWN RUN is not the caption's rhythm: rows that held only
    # brace glyphs are empty on both sides and render as phantom rows.
    while cells and not cells[-1][0] and not cells[-1][1]:
        cells.pop()
    cells = [c for c in cells if c[0] or c[1]]
    if not cells:
        return None, [], []

    left_plain = [_norm(" ".join(c.plain for c in lc)) for lc, _ in cells]
    right_plain = [_norm(" ".join(c.plain for c in rc)) for _, rc in cells]

    def cell(parts: list, role: str, page: int):
        if not parts:
            # An empty pad cell keeps the two stacks aligned; it carries its
            # column's role so it is not counted as a row nobody read.
            return m.HmLine(text="", prov=m.Prov(page), role=role)
        parts = sorted(parts, key=lambda l: l.x0)
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        return m.HmLine(
            text=text, prov=m.Prov(page, tuple(p.id for p in parts)),
            align=m.Align.LEFT, x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role)

    left = [cell(lc, roles("L", left_plain, i), pm.number)
            for i, (lc, _) in enumerate(cells)]
    right = [cell(rc, roles("R", right_plain, i), pm.number)
             for i, (_, rc) in enumerate(cells)]
    block = m.CaptionBlock(
        left=left, right=right, rail=glyph, rail_rows=len(left),
        style_id=style_id,
        fp={"rail": glyph, "mid_x": round(mid, 1)},
        prov=m.Prov(pm.number,
                    tuple(sorted(l.id for row in band for l in row))))
    return block, left_plain, right_plain


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def _find(rows: list, test, start: int = 0) -> int | None:
    for idx in range(start, len(rows)):
        if test(rows[idx]):
            return idx
    return None


def _drop_run(ctx, rows: list, start: int, limit: int, close, kind: str):
    """A notice is a RUN and it closes on its own sentence."""
    for idx in range(start, min(limit, len(rows))):
        row = rows[idx]
        ctx.drop(row, kind)
        if close.search(_row_text(row)):
            return


def _record_dockets(ctx, printed: str) -> None:
    parts = [p.strip().rstrip(".") for p in re.split(r",|&|\band\b", printed)
             if p.strip()]
    if not parts:
        return
    ctx.crit.setdefault("docket_number", parts[0])
    if parts[1:]:
        ctx.crit.setdefault("other_dockets", parts[1:])


def _record_caption(ctx, printed: list[str]) -> None:
    """The printed rows and the parsed names, kept side by side. The names
    are built from the parties either side of the pivot — joining the
    caption wholesale welds the status parentheticals into them."""
    rows = [t for t in printed if t]
    if not rows:
        return
    ctx.crit.setdefault("caption", rows)
    names = [t for t in rows if not _PARENTHETICAL.match(t)]
    sides: list[list[str]] = [[]]
    for text in names:
        if _PIVOT.match(text):
            sides.append([])
            continue
        # A one-row caption may set the pivot inline ('State of Vermont v.
        # Jason Robinson*' — the letterhead entry order).
        if len(sides) == 1 and re.search(r"\s+vs?\.\s+", text):
            head, _, tail = re.split(r"(\s+vs?\.\s+)", text, maxsplit=1)[:3]
            sides[0].append(head)
            sides.append([tail])
            continue
        sides[-1].append(text)
    parties = [_norm(" ".join(s)).rstrip(",").replace("*", "")
               for s in sides if s]
    parties = [p for p in parties if p]
    if not parties:
        return
    ctx.crit.setdefault("parties", parties)
    ctx.crit.setdefault("case_name", " v. ".join(parties)
                        if len(parties) == 2 else " ".join(parties))


def _record_panel(ctx, printed: list[str]) -> None:
    rows = [t for t in printed if t]
    if not rows:
        return
    line = _norm(" ".join(rows))
    ctx.crit.setdefault("panel_line", line)
    roster = _PRESENT.match(rows[0])
    if roster:
        tail = _norm(" ".join([roster.group(1)] + rows[1:]))
        if tail:
            ctx.crit.setdefault("judges", tail)


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

    def drop(self, group: list, kind: str) -> None:
        parts = sorted(group, key=lambda l: l.x0)
        if not parts:
            return
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
