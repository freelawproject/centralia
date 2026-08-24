"""United States District Court, Central District of California ('cacd').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads NONE of a five-record sample. This
court's paper has not been read yet — the registration is here so the
court is wired and measurable, not because it is done.

Facts this court measures differently from the shared defaults are declared
below. Nothing is inherited: this file imports core and never another court
file, and no other court file imports it.
"""

from __future__ import annotations

from .. import model as m
from ..districts import EcfPaper, read_ecf
from ..geometry import line_alignment
from ..pdfio.rules import is_typed_rule
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from . import register

CACD = register(CourtProfile(
    "cacd", "United States District Court, Central District of California",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # A district judge signs in the reversed form — the name over the office
    # ('EMILY C. MARKS' / 'UNITED STATES DISTRICT JUDGE').
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="cacd")
def read_headmatter_cacd(model, geom, **kw):
    """Read cacd's paper: the clerk's CIVIL MINUTES form if this is one,
    otherwise the ECF pleading order. The form is tried FIRST because it is
    the narrower contract — it requires its own banner and its closing
    'Proceedings:' field, so a pleading-paper order can never satisfy it."""
    minutes = read_civil_minutes(model, geom)
    if minutes is not NOTHING:
        return minutes
    return read_ecf(model, geom, PAPER, **kw)


# --------------------------------------------------------------------------
# THE CIVIL MINUTES FORM
# --------------------------------------------------------------------------
# A minute order is not pleading paper. cacd prints its rulings on the
# clerk's own FORM — a masthead, the banner 'CIVIL MINUTES - GENERAL', then a
# grid of labelled fields (Case No. | Date, Title, Present, the clerk and
# reporter, the appearances) closing on 'Proceedings:', under which the body
# begins. There is no caption box, no rail and no party stack, so `read_ecf`
# — which is built to find exactly those — reads none of it, and the whole
# form fell into the opinion body as prose, its two columns fused into one
# run ('Rolls Royce Paschal N/A Deputy Clerk Court Reporter' — four cells,
# one line, wrong order) while `judges`, `disposition` and the parties came
# back empty (the user, 2026-08-22).
#
# MEASURED on the 9 records of the 32-record corpus that print this form
# (1002267.10.0, 1002384.9.0, 1003312.9.0, 1003351.9.0, 1021353.23.0,
# 1024031.12.0, 1028191.10.0, 986182.17.0, 999943.5.0). The chambers vary in
# spelling, never in structure: 'Case No.' / 'Case No.:', 'Court Reporter' /
# 'Court Reporter / Recorder', 'Attorneys Present for Plaintiff:' /
# '…Plaintiffs:', a hyphen or an en dash in the banner, 'Proceedings:' set
# bold or roman with its value in a second cell. Every label is therefore
# read LETTERS-ONLY, which folds all of that away.

# The banner, letters-only: 'CIVIL MINUTES - GENERAL', '… – GENERAL'.
_MINUTES_BANNER = "civilminutes"
# The masthead this form opens on, letters-only.
_MINUTES_HEAD = "unitedstatesdistrictcourt"
# The last field. The body opens under it, and it is also the only row an
# unsigned minute order can anchor a writing on — so it is the anchor the
# pipeline may release if no body was found.
_MINUTES_FOOT = "proceedings"
# A SECOND COLUMN STARTS AT THE AXIS. The form's right-hand cells begin
# between x283 and x424 on a 612pt sheet (axis 306) — 'Deputy Clerk' is
# paired with 'Court Reporter' at 283.6, the widest reach inside the axis —
# while a value that merely runs long starts at the LEFT margin and crosses
# the axis on its way ('Proceedings:' + 'ORDER TO SHOW CAUSE AND ORDER FOR
# JOINT STATUS REPORT' at x172, midpoint 358). Where the cell STARTS
# separates them; where it ends does not. 40pt is the same reach the shared
# paper measures for a lone caption piece.
_MINUTES_AXIS_REACH = 40.0
# The form's field rules underline the row above them: a drawn horizontal
# within this of a row's foot decorates that row and is not a divider of its
# own. Measured: every field rule on these records lands 1.6-2.4pt under its
# row's baseline box.
_MINUTES_UNDERLINE = 4.0

# What each field IS, by the letters its label opens with. Order matters
# only in that 'caseno' is tested before 'date' — no label is a prefix of
# another.
_MINUTES_ROLES = (
    ("caseno", "docket"),
    ("date", "date"),
    ("title", "caption"),
    ("present", "panel"),
    ("deputyclerk", "case-info"),
    ("courtreporter", "case-info"),
    ("attorneyspresent", "counsel"),
    ("proceedings", "disposition"),
)


def _mn_letters(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalpha())


def _mn_clean(text: str) -> str:
    return " ".join(text.split())


def _mn_rows(lines: list) -> list:
    """The page's lines as VISUAL ROWS, cells left to right. A form field and
    its neighbour share a baseline; pdfio has already split them at the
    column gap, and pairing them back by row is what keeps the two columns
    aligned."""
    groups: dict = {}
    order: list = []
    for line in sorted(lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip():
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


def _mn_role(text: str) -> str:
    letters = _mn_letters(text)
    for label, role in _MINUTES_ROLES:
        if letters.startswith(label):
            return role
    return ""


def _mn_label(text: str) -> str:
    """The field label this row opens with, letters-only, or ''."""
    letters = _mn_letters(text)
    for label, _role in _MINUTES_ROLES:
        if letters.startswith(label):
            return label
    return ""


def _mn_value(text: str) -> str:
    """A field's value: what follows its label.

    THE LABEL'S OWN LETTERS ARE CONSUMED, one at a time, and a colon cannot
    mark the end of it — a district docket carries one. Split at the first
    colon, 'Case No. 2:26-cv-00331-SVW-E' reported its case number as
    '26-cv-00331-SVW-E' and dropped the division (the user, 2026-08-22).
    Punctuation between the label and its value is skipped, so 'Case No.',
    'Case No.:' and 'Date January 26, 2026' all read the same way."""
    t = _mn_clean(text)
    label = _mn_label(t)
    if not label:
        return t
    i = k = 0
    while i < len(t) and k < len(label):
        if t[i].isalpha():
            if t[i].lower() != label[k]:
                return t
            k += 1
        i += 1
    return t[i:].lstrip(" :.")


def _mn_line(line, pm, geom, role: str, cells=None):
    """One HmLine for a row (or for one side of a two-column row), carrying
    the page's own alignment and the inline bold/italic of its markup."""
    parts = cells if cells is not None else [line]
    text = ""
    for part in parts:
        piece = line_markup(part)
        text = (text.rstrip() + "  " + piece.lstrip()) if text.strip() \
            else piece
    align = {"L": m.Align.LEFT, "C": m.Align.CENTER,
             "R": m.Align.RIGHT}[line_alignment(line, pm.width, geom)]
    return m.HmLine(
        text=text, prov=m.Prov(line.page, tuple(p.id for p in parts)),
        align=align, x0=line.x0, size=line.size or 0.0,
        bold=all(bool(p.all_bold) for p in parts), role=role)


def read_civil_minutes(model, geom):
    """cacd's CIVIL MINUTES form as typed headmatter, or NOTHING.

    The claim runs from the masthead to the 'Proceedings:' row inclusive and
    no further: everything below it is the body, read by core exactly as for
    any other court. Both ends must be found — a form whose extent cannot be
    seen is declined rather than half-read.
    """
    if not model.pages or not model.pages[0].lines:
        return NOTHING
    pm = model.pages[0]
    axis = pm.width / 2
    rows = _mn_rows(pm.lines)
    flat = [_mn_letters(" ".join(l.plain for l in r)) for r in rows]

    banner = next((i for i in range(len(rows))
                   if _MINUTES_BANNER in flat[i]), None)
    if banner is None:
        return NOTHING          # not this form: the ECF paper reads it
    head = next((i for i in range(banner)
                 if flat[i].startswith(_MINUTES_HEAD)), None)
    foot = next((i for i in range(banner + 1, len(rows))
                 if flat[i].startswith(_MINUTES_FOOT)), None)
    if head is None or foot is None:
        return NOTHING
    # A TYPED RULE ABOVE THE MASTHEAD is the form's own top edge, drawn in
    # underscores (1021353.23.0 rules the full measure at y39.4). Claimed
    # here so it renders as the rule it is instead of falling to the body.
    if head and is_typed_rule(_mn_clean(" ".join(l.plain
                                                 for l in rows[head - 1]))):
        head -= 1

    # THE LAST FIELD'S VALUE WRAPS. 'Proceedings:' is set beside its value in
    # a second cell, and a value too long for the measure runs onto the row
    # below. Read as one row the disposition is cut mid-phrase ('(IN
    # CHAMBERS) ORDER TO SHOW CAUSE RE:' — the words 'SUPPLEMENTAL
    # JURISDICTION' completing it were filed as the opinion's first
    # paragraph, on 4 of the 9 records).
    #
    # THE PITCH IS THE EVIDENCE, not the column: the chambers disagree about
    # where a runover goes — 1024031.12.0 sets it under the value at x180,
    # 1028191.10.0 brings it back to the body margin at x72 — but both set it
    # at the form's own leading (17.3pt on a 13pt row), while the body below
    # stands off by a paragraph (27.0pt) and opens on a first-line indent.
    # 1.5x the type size is the same wrap rule core reads a caption with.
    tail: list = []
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 0.0
    value_x0 = max(l.x0 for l in rows[foot]) if len(rows[foot]) > 1 else None
    j, prev = foot + 1, rows[foot]
    while j < len(rows):
        row = rows[j]
        size = max((l.size or 12.0) for l in row)
        if row[0].top - prev[0].top > 1.5 * size:
            break
        # …AND IT IS NOT A PARAGRAPH OPENING. A runover stands at the value's
        # column or at the margin; the body's first row is indented past it.
        at_margin = body_x0 and min(l.x0 for l in row) <= body_x0 + 4
        in_column = value_x0 is not None \
            and min(l.x0 for l in row) >= value_x0 - 4
        if not (at_margin or in_column):
            break
        tail.extend(row)
        prev = row
        j += 1

    items: list = []
    consumed: set = set()
    crit: dict = {}
    court_rows: list = []
    judge_row = title_row = proceed_row = ""

    # The form's DRAWN rules, merged into the walk by position. A rule that
    # underlines a row decorates it (see _MINUTES_UNDERLINE); what is left
    # is a divider the form draws, and it renders where it was drawn.
    feet = [max(l.bottom for l in r) for r in rows]
    foot_bottom = max([feet[foot]] + [l.bottom for l in tail])
    fences = [r for r in pm.h_rules
              if rows[head][0].top - 12 <= r.top <= foot_bottom + 12
              and not any(abs(f - r.top) <= _MINUTES_UNDERLINE for f in feet)]
    fences.sort(key=lambda r: r.top)
    fi = 0

    pending: list = []          # the open two-column run

    def _close_columns() -> None:
        nonlocal pending
        if not pending:
            return
        # A VALUE CELL BELONGS TO ITS LABEL. The grid prints the clerk's and
        # reporter's names ABOVE their labels and the appearances BELOW
        # theirs, so a row carrying only values names nothing itself — and
        # left unread it renders as an untagged row in the middle of a read
        # block (4 of 1002267.10.0's rows). It takes the role of the labelled
        # row it belongs to: the one under it where there is one, else above.
        for _k, (_l, _r) in enumerate(pending):
            if _l.role or _r.role:
                continue
            _near = next((p for p in pending[_k + 1:] if p[0].role or p[1].role),
                         None) \
                or next((p for p in reversed(pending[:_k])
                         if p[0].role or p[1].role), None)
            if _near:
                _l.role = _r.role = _near[0].role or _near[1].role
        items.append(m.CaptionBlock(
            left=[p[0] for p in pending], right=[p[1] for p in pending],
            rail=None, rail_rows=len(pending), style_id=None, fp={},
            prov=m.Prov(pm.number, tuple(sorted(
                i for p in pending for side in p
                for i in side.prov.line_ids)))))
        pending = []

    for i in range(head, foot + 1):
        row = rows[i]
        while fi < len(fences) and fences[fi].top < row[0].top:
            _close_columns()
            items.append(m.Rule(
                prov=m.Prov(pm.number),
                span="full" if fences[fi].width > pm.width * 0.4
                else "left" if fences[fi].x1 < axis else "right"))
            fi += 1
        text = _mn_clean(" ".join(l.plain for l in row))
        if is_typed_rule(text):
            _close_columns()
            items.append(m.Rule(prov=m.Prov(pm.number, tuple(l.id for l in row)),
                                typed=True, span="full"))
            consumed.update(l.id for l in row)
            continue
        left = [l for l in row if l.x0 < axis - _MINUTES_AXIS_REACH]
        right = [l for l in row if l.x0 >= axis - _MINUTES_AXIS_REACH]
        if left and right:
            # A TWO-COLUMN FIELD ROW. Held as a pair so the columns stay
            # aligned down the form — rendered as separate rows, the clerk's
            # name and the reporter's drift apart.
            pending.append((
                _mn_line(left[0], pm, geom, _mn_role(left[0].plain), left),
                _mn_line(right[0], pm, geom, _mn_role(right[0].plain), right)))
            consumed.update(l.id for l in row)
            if _mn_role(left[0].plain) == "docket":
                crit.setdefault("docket_number", _mn_value(
                    " ".join(l.plain for l in left)))
            if _mn_role(right[0].plain) == "date":
                crit.setdefault("decision_date", _mn_value(
                    " ".join(l.plain for l in right)))
            continue
        _close_columns()
        role = _mn_role(text) or ("court" if i <= banner else "")
        if i == banner:
            role = "title"
            crit.setdefault("title", text)
        elif role == "court":
            court_rows.append(text)
        if role == "caption":
            title_row = _mn_value(text)
        elif role == "panel":
            judge_row = _mn_value(text)
        elif role == "disposition":
            proceed_row = _mn_value(_mn_clean(
                " ".join(l.plain for l in row + tail)))
        cells = row + tail if i == foot else row
        items.append(_mn_line(row[0], pm, geom, role, cells))
        consumed.update(l.id for l in cells)
    _close_columns()

    # ---- what the form says --------------------------------------------
    if court_rows:
        crit["court"] = _mn_clean(" ".join(court_rows))
    if title_row:
        # THE TITLE FIELD IS THE CASE NAME, and the form prints it whole
        # ('Alejandro Urbina v. BMO Bank National Association'). The pivot
        # splits the sides; the label is already gone.
        crit["case_name"] = title_row
        for pivot in (" v. ", " vs. ", " v ", " vs "):
            a, sep, b = title_row.partition(pivot)
            if sep and a.strip() and b.strip():
                crit["parties"] = [a.strip(), b.strip()]
                break
    if proceed_row:
        crit["disposition"] = proceed_row
    # A MINUTE ORDER IS AN ORDER. The form says so on its face — these are
    # the clerk's minutes of what the court did — and the type must be stated
    # here rather than inferred downstream: core read the paper as an
    # `opinion` the moment the 'PROCEEDINGS:' heading stopped being the
    # body's first row and became headmatter, which is exactly what this
    # reader is for.
    out = {"criteria": crit, "items": items, "attorneys": [],
           "dropped": [], "consumed": consumed,
           "anchor_ids": [l.id for l in rows[foot]],
           "doc_type_final": m.DocType.ORDER}
    if judge_row:
        # WHO PRESIDED, as the form prints it — and the NAME on its own for
        # the byline core builds. 'The Honorable PERCY ANDERSON, UNITED
        # STATES DISTRICT JUDGE' names one judge; the honorific and the
        # office are not part of it.
        crit["judges"] = judge_row
        # THE HONORIFIC IS NOT THE NAME, and it does not always arrive in one
        # piece: 999943.5.0 sets 'Present: The' beside the judge's name and
        # wraps 'Honorable' onto the row below, so cutting at the word left
        # 'The Sheri Pym'. Dropping the honorific TOKENS off the front reads
        # every spelling in the corpus — 'The Honorable', 'HONORABLE', 'Hon.'
        # — however the form breaks it.
        name = judge_row.split(",")[0]
        words = name.split()
        while words and words[0].strip(".").lower() in (
                "the", "honorable", "honourable", "hon"):
            words.pop(0)
        name = " ".join(words).strip()
        if name:
            crit["author"] = name
            crit["panel"] = [name]
            out["announced_author"] = name
    return out

