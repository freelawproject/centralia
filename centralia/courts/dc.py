"""District of Columbia Court of Appeals ('dc').

Everything unique to dc lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py.

THE CONTRACT — the court fronts every paper with a FOUR-LINE REPORTER'S
NOTICE at the rail, names itself on the page axis, and then prints one of
TWO papers. Which one it is, is decided by WHERE THE DOCKET ROW STANDS: on
the axis it is a slip opinion, at the body rail it is a bar-discipline
order. Measured over all 30 records the split is exact — the five `in re`
discipline orders print `No. 26-BG-0060` at x0=72.0 and the other 25 print
`No. 24-CO-0716` centred at x0≈258; `in_re_meta_platforms` is an `in re`
mandamus OPINION and its docket is centred with the rest, so the wording of
the caption would have misrouted it and the geometry does not.

    ┌──────────────────────────────────────────────────────────────────┐
    │ Notice: This opinion is subject to formal revision before …      │  the
    │ and Maryland Reporters. Users are requested to notify …          │  four
    │ any formal errors so that corrections may be made before …      │  rows
    │ to press.                                                        │
    │                                                                  │
    │        DISTRICT OF COLUMBIA COURT OF APPEALS       the masthead   │
    │                  No. 24-CO-0716                    the docket     │
    │              HENRY O. ALLEN, APPELLANT,            the caption:   │
    │                        V.                          CAPS either    │
    │              UNITED STATES, APPELLEE.              side of V.     │
    │             Appeal from the Superior Court          the origin    │
    │               of the District of Columbia           (mixed case)  │
    │                   (2002-FEL-006601)                 its number    │
    │               (J. Michael Ryan, Judge)              its judge     │
    │ (Argued November 20, 2025          Decided July 30, 2026)  dates  │
    │     Paul Maneri, Public Defender Service, with whom …    counsel  │
    │ Wang, Public Defender Service, were on the briefs, for appellant. │
    │     Before DEAHL, HOWARD, and SHANKER, Associate Judges.  panel   │
    │     Opinion for the court by Associate Judge DEAHL.      author   │
    │     DEAHL, Associate Judge: Henry Allen was convicted …  writing  │
    └──────────────────────────────────────────────────────────────────┘

THE CASE IS SET IN CAPS, THE PAPER IS NOT. The caption band runs from the
docket row to the first row whose letters are not all upper case: every
party row on all 25 opinions is CAPS (`et al.` is the one lower-case token
the court sets inside one, and the pivot is `V.` on 24 records and `v.` on
samaddar_dds), and every origin recital is sentence case (`Appeal from the
Superior Court`, `On Petition for Review of an Order of the District of
Columbia`, `On Petition for a Writ of Mandamus to the`). So the band break
is measured off the type, and no origin wording is matched.

THE DATES ARE ONE ROW SET IN TWO POSITIONS — `(Argued November 20, 2025` at
the rail and `Decided July 30, 2026)` flush right, the same `top` on all 25
opinions, and the parentheses only close on the second piece. Read as a
single row, which is what the paper prints. `Argued` / `Submitted` /
`Argued en banc` all occur (d.w. en banc), and the decided date may carry a
footnote mark (`Decided March 12, 2026*)` on alston).

THE COUNSEL BLOCK OPENS ON THE 36pt INDENT and runs back to the rail
(108.0 over 72.0 on every record); an entry is an indented row plus its
rail continuations, so `criteria.attorneys` can be grouped without reading
any of the words.

WHAT FLOWS IS JOINED, WHAT IS CENTRED IS SET AS PRINTED. An element that
runs to its column's right edge and returns to the RAIL is one thing the
page wrapped — a counsel entry, the roster, an announcement, the bar
order's membership recital — and it is emitted as ONE line with every line
id in its prov (a hyphen at the break welds, as core's own `_join` does:
d.w. breaks 'BLACKBURNE-RIGSBY' across two rows). An element the court
CENTRED — the caption rows, the origin recital — is balanced line by line
on the axis, so the court chose that break and the render reproduces it.

TWO PIECES ON ONE ROW ARE TWO THINGS unless the punctuation says otherwise.
Over all 30 records exactly two kinds of row carry two pieces: the slip's
dates row, where the left piece opens a parenthesis only the right piece
closes (one element, all 25), and the bar order's apparatus row, where the
left column stands at the rail and the right column starts at 324.0 or
360.0 (two elements, all 5 — 'Bar Registration No. 888283858' and 'DDN:
2025-D156' are a bar number and a disciplinary docket number, not one row).

THE PANEL IS THE COURT'S OWN WORD — `Before …` on a slip, `BEFORE: …` on an
order — and it runs to the row that ends its sentence (`… and GLICKMAN,`
/ `Senior Judge.`).

AFTER THE PANEL, dc ANNOUNCES its writings before signing them (`Opinion
for the court by Associate Judge DEAHL.`, `Dissenting opinion by Senior
Judge THOMPSON at page 49.`, `Opinion concurring in the judgment by
Associate Judge MCLEESE at page 28.`). Those rows are the court naming its
authors, so they are `author`, not `title` — the paper never names itself
on a slip. Nothing is passed to core as an announced author: dc also SIGNS
every writing, and a byline always outranks an announcement.

THE BYLINE ENDS THE READER (`DEAHL, Associate Judge:` / `PER CURIAM:`), and
the block may cross onto page 2 to reach it — carruth and d.w. end page 1
on the panel, in_re_meta prints its panel on page 2.

    ┌──────────────────────────────────────────────────────────────────┐
    │        DISTRICT OF COLUMBIA COURT OF APPEALS       the masthead   │
    │ No. 24-BG-1045                                     the docket,    │
    │ IN RE MARC S. ALPERT,                              AT THE RAIL    │
    │             Respondent.                                           │
    │ A Suspended Member of the Bar of the               the bar        │
    │ District of Columbia Court of Appeals              apparatus      │
    │ Bar Registration No. 196386      DDN: 2024-D175                   │
    │ BEFORE: Deahl and Howard, Associate Judges, and …   the panel     │
    │                  O R D E R                          the TITLE     │
    │              (FILED – July 23, 2026)                the date      │
    │     On consideration of the certified copy of …     the writing   │
    └──────────────────────────────────────────────────────────────────┘

ON THE BAR ORDER THE PAPER NAMES ITSELF. `O R D E R` — letter-spaced, on
the axis — is `title`, and it is reported as the claim's anchor so core can
release it if the order's body has nothing else to open on. The filed date
closes the block; everything under it is the order. The apparatus band
between the caption and the panel is `case-info` — the membership recital,
`Bar Registration No.`, `DDN:`/`BDN:` identify the matter without being
this court's docket, its date or a party name. Inside the band a row
opening with one of those printed LABELS starts a new element; anything
else at the rail continues the recital above it (in_re_mcneal wraps the
recital past the DDN row, so the run cannot be counted).

WHAT IS LEFT UNCLAIMED, deliberately: the page-1 footnote zone under the
144pt drawn rule at the rail (alston, bloomberg, jones), which is core's
work, and the `argued` date, which has no declared criterion to hold it.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# THE MASTHEAD, printed identically on all 30 records at 14.0pt on the page
# axis. It is the dispatch landmark; the notice above it is 4 rows on all 30
# but is never counted — a fifth would shift every ordinal.
_MASTHEAD = re.compile(r"^DISTRICT OF COLUMBIA COURT OF APPEALS$")
_MAST_SEARCH_ROWS = 12          # 4 notice rows measured; 12 is slack, not a
#                                 measurement of anything the court prints.
_AXIS_TOL = 12.0                # 'No. 24-CO-0716' centres 306.0±1.0 on the
#                                 25 opinions; 'Respondent.' centres at 215.
# A CENTRED ROW IS A SHORT ROW (nh's lesson): the dates row runs 72.0-539.4
# and its mid-point is on the axis, so the width cap is what keeps it from
# reading as centred apparatus.
_CENTRED_WIDTH_MAX = 0.72
# The counsel indent: 108.0 against a 72.0 rail on every one of the 30.
_INDENT_MIN = 18.0
# THE HEAD-MARGIN STAMP'S TWO GUARDS. Page 1 establishes the type block (its
# topmost row stands at 75.35 on all 30 records); a row on a later page
# standing above that line is outside the measure. It must also STAND OFF
# from the page's first row of text by more than 1.5x that page's own
# leading (29.6pt against a 16.1pt lead on the two records that print one)
# and reach no more than half the measure (95.7pt of 468.0).
_STAMP_STANDOFF = 1.5
_STAMP_WIDTH_MAX = 0.5

# 'No. 24-CO-0716' / 'Nos. 18-CF-0686 & 25-CO-0349' (minor) / 'No. 26-BG-0060'
_DOCKET = re.compile(r"^Nos?\.\s+(\S.*)$")
# The pivot, 'V.' on 24 records and 'v.' on samaddar_dds — the one caption
# row whose letters are not upper case.
_PIVOT = re.compile(r"^v\.?$", re.I)
# 'et al.' is the only lower-case token the court sets inside a CAPS caption
# row ('MITSUBISHI ELECTRIC AND ELECTRONICS USA, INC., et al., APPELLEES.').
_ET_AL = re.compile(r"\bet\s+al\.?", re.I)
# Party STATUS is a closed vocabulary; party NAMES are never read by wording.
# Case-insensitive because the two papers set it differently: a slip prints
# 'APPELLANT,' in the caption's caps, a bar order prints 'Respondent.' on its
# own row in sentence case.
_STATUS = re.compile(
    r",?\s*(?:APPELLANTS?|APPELLEES?|PETITIONERS?|RESPONDENTS?"
    r"|INTERVENORS?|AMICUS CURIAE)\.?,?$", re.I)
# The dates row, read as the single row the court prints in two positions.
_DATE_ROW = re.compile(r"^\((?:Argued|Submitted|Reargued|FILED)\b")
_DECIDED = re.compile(r"\bDecided\s+([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
_SUBMITTED = re.compile(r"\bSubmitted(?:\s+en\s+banc)?"
                        r"\s+([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
# '(FILED – July 23, 2026)' / '(FILED—July 16, 2026)' — the en dash, the em
# dash and the hyphen all occur across the five orders.
_FILED = re.compile(r"^\(FILED\s*[–—-]\s*(.+?)\)$")
# The court's own convening word, and the roster's bench titles.
_PANEL_OPEN = re.compile(r"^(?:Before\b|BEFORE:)")
_BENCH = re.compile(r"^(?:Chief|Senior|Associate)?\s*(?:Judges?|Justices?)$",
                    re.I)
# dc announces each writing and its author above the first byline.
_ANNOUNCE = re.compile(
    r"^(?:Opinion|Dissenting opinion|Concurring opinion|Separate opinion"
    r"|Statement)\b")
# The byline: 'DEAHL, Associate Judge: Henry Allen was convicted…' /
# 'BLACKBURNE-RIGSBY, Chief Judge: …' / 'PER CURIAM: Petitioner…' — measured
# on all 30 records' first writing. THE COLON AND THE PROSE AFTER IT ARE
# REQUIRED: a roster's second row is 'GLICKMAN, Senior Judge.', which every
# name-then-title test takes for a byline, and it ended the reader one row
# early on caesar, minor and perry — the stranded roster row then opened a
# phantom empty writing authored by GLICKMAN.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Z’'.\-]+(?:\s+[A-Z][A-Z’'.\-]+)*,\s+"
    r"(?:Chief|Senior|Associate)\s+Judges?|PER CURIAM):\s+\S")
# 'O R D E R' — the bar order's own name for itself, letter-spaced.
_TITLE = re.compile(r"^(?:[A-Z]\s){2,}[A-Z]$")
# The respondent's status row on a bar order, and the matter's identifiers.
_RESPONDENT = re.compile(r"^(?:Respondent|Petitioner|Applicant)\.?$", re.I)
_IN_RE = re.compile(r"^IN RE\b")
# The identifier labels a bar order prints in its apparatus band. A closed
# vocabulary of LABELS (never of names), and it is what tells a new element
# from a wrap inside the band's left column.
_ID_LABEL = re.compile(r"^(?:Bar Registration No|Bar No|DDN|BDN)\b", re.I)
# A wrap that broke on a hyphen — the mark may sit inside the row's markup
# ('…BLACKBURNE-</em>').
_WRAP_HYPHEN = re.compile(r"-(?:</(?:em|strong|u)>)*\s*$")


def _norm(text: str) -> str:
    return " ".join(text.split())


def _is_caps(text: str) -> bool:
    """A caption row: every letter upper case, `et al.` excepted."""
    letters = [c for c in _ET_AL.sub("", text) if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _party(rows: list[str]) -> str:
    """One side of the pivot, with its STATUS label removed. THE FULL STOP
    STAYS: stripping it takes the abbreviation with it — 'D.W., APPELLANT,'
    came out 'D.W' and 'et al.' came out 'et al'. The status pattern already
    eats the one period that belongs to the label."""
    return _STATUS.sub("", " ".join(rows).strip()).strip().strip(",").strip()


def _panel_names(text: str) -> list[str]:
    """The roster's names, with the bench titles dropped."""
    body = re.sub(r"^(?:Before|BEFORE:?)\s*", "", text).strip().rstrip(".")
    out = []
    for part in re.split(r",|\band\b", body):
        part = part.strip(" .")
        if part and not _BENCH.match(part):
            out.append(part)
    return out




def _centred(pm, group: list) -> bool:
    """Balanced on the page axis AND short. The mid-point test alone calls
    the dates row centred (72.0-539.4 centres on 305.7), so the width cap is
    what separates a display line from a full-measure one."""
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return (abs((x0 + x1) / 2 - pm.width / 2) <= _AXIS_TOL
            and (x1 - x0) <= pm.width * _CENTRED_WIDTH_MAX)


@decider("headmatter.read", court="dc")
def read_headmatter_dc(model, geom, **_):
    """Read the District of Columbia's block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 14.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    # THE BLOCK MAY CROSS ONTO PAGE 2 to reach its byline (carruth, d.w.,
    # in_re_meta). Nothing dc prints reaches a third page.
    rows: list[tuple] = []
    for pm in model.pages[:2]:
        rows.extend((pm, g) for g in _rows(pm, finder, body_x0))
    if len(rows) < 6:
        return NOTHING

    texts = [_row_text(g) for _, g in rows]
    # THE DISPATCH: the masthead, wherever the notice above it ends.
    mast = next((i for i, t in enumerate(texts[:_MAST_SEARCH_ROWS])
                 if _MASTHEAD.match(t)), None)
    if mast is None:
        return NOTHING
    # …and the docket row below it, which is what names the paper.
    dock = next((i for i in range(mast + 1, min(mast + 4, len(rows)))
                 if _DOCKET.match(texts[i])), None)
    if dock is None:
        return NOTHING
    at_rail = min(l.x0 for l in rows[dock][1]) <= body_x0 + 2.0
    style = "rail bar order" if at_rail else "axis slip"

    ctx = _Ctx()
    ctx.crit["headmatter_style"] = style
    # THE NOTICE IS EVERYTHING ABOVE THE MASTHEAD — four rail rows on all 30
    # records, the Reporter's standing warning about revision. Dropped, not
    # tinted: no part of it is the court's writing.
    for _pm, group in rows[:mast]:
        ctx.drop(group, "notice")

    pm0, mast_group = rows[mast]
    ctx.crit["court"] = texts[mast]
    ctx.emit([mast_group], "court", _centred(pm0, mast_group))
    pmd, dock_group = rows[dock]
    nums = [n.strip() for n
            in re.split(r"[,&]", _DOCKET.match(texts[dock]).group(1))
            if n.strip()]
    ctx.crit["docket_number"] = nums[0]
    if nums[1:]:
        ctx.crit["other_dockets"] = nums[1:]
    ctx.emit([dock_group], "docket", _centred(pmd, dock_group))

    reader = _read_order if style == "rail bar order" else _read_slip
    reader(rows, texts, dock, ctx, body_x0)
    # THE HEAD-MARGIN STAMP is furniture of the same class as a running
    # head, on every page the paper reaches. Recorded, never silently cut.
    for stamp in _margin_stamps(model, finder, body_x0):
        ctx.drop(stamp, "running-head")
    if not ctx.crit.get("docket_number"):
        return NOTHING
    return ctx.result()


def _read_slip(rows, texts, dock, ctx, body_x0) -> None:
    """The slip opinion: caption, origin, dates, counsel, panel, authors."""
    caption: list[str] = []
    pivot = -1
    origin: list[str] = []
    counsel: list[list[str]] = []
    pend: list[list] = []        # the element being built, row group by group
    pend_text = ""
    band = "caption"

    def flush(role: str, centre: bool = False) -> None:
        nonlocal pend, pend_text
        if pend:
            ctx.emit(pend, role, centre)
        pend, pend_text = [], ""

    for idx in range(dock + 1, len(rows)):
        pm, group = rows[idx]
        text = texts[idx]
        if not text:
            continue
        # THE BYLINE ENDS THE READER — but only where no band with an end of
        # its own is open. A roster runs to its own full stop, and its second
        # row looks exactly like a byline (ca4's lesson: the byline test
        # belongs in the trailing region, not inside a fenced band).
        if band not in ("caption", "panel") and _BYLINE.match(text):
            break

        if band == "caption":
            # THE CASE IS SET IN CAPS, THE PAPER IS NOT — the band breaks at
            # the first row whose letters are not all upper case.
            if _is_caps(text) or _PIVOT.match(text):
                if _PIVOT.match(text):
                    pivot = len(caption)
                caption.append(text)
                ctx.emit([group], "caption", _centred(pm, group))
                continue
            band = "origin"
        if _DATE_ROW.match(text):
            dec = _DECIDED.search(text)
            if dec:
                ctx.crit["decision_date"] = dec.group(1)
            sub = _SUBMITTED.search(text)
            if sub:
                ctx.crit["submitted"] = sub.group(1)
            ctx.emit([group], "date", _centred(pm, group))
            band = "counsel"
            continue
        if band == "origin":
            # The origin is CENTRED display: the court balances every line of
            # it on the axis and chose the break, so it is reproduced as set.
            origin.append(text)
            ctx.emit([group], "lower-court", _centred(pm, group))
            continue
        if _PANEL_OPEN.match(text) or band == "panel":
            # THE ROSTER CLOSES THE LAST COUNSEL ENTRY. Without this the
            # pending entry ran on into the roster and the joined element
            # came out tagged `panel` — the appearance lost, the roster
            # invisible (allen, alston, carruth, d.w.).
            if band == "counsel" and pend:
                counsel.append([pend_text])
                flush("counsel")
            pend.append(group)
            pend_text = (pend_text + " " + text).strip()
            band = "panel"
            # The roster runs to the row that ends its sentence ('… and
            # GLICKMAN,' / 'Senior Judge.').
            if pend_text.endswith("."):
                ctx.crit["panel_line"] = pend_text
                ctx.crit["panel"] = _panel_names(pend_text)
                flush("panel")
                band = "author"
            continue
        if band == "counsel":
            # AN ENTRY OPENS ON THE 36pt INDENT and flows back to the rail;
            # the wraps belong to the entry, not to rows of their own.
            if group[0].x0 - body_x0 >= _INDENT_MIN and pend:
                counsel.append([pend_text])
                flush("counsel")
            pend.append(group)
            pend_text = (pend_text + " " + text).strip()
            continue
        if band == "author":
            if _ANNOUNCE.match(text) and pend:
                flush("author")
            if _ANNOUNCE.match(text) or pend:
                pend.append(group)
                pend_text = (pend_text + " " + text).strip()
                if pend_text.endswith("."):
                    flush("author")
                continue
            break
        # A ROW IN NO BAND THIS PAPER USES ends the claim rather than being
        # tinted with a guess — stopping here keeps the claim contiguous.
        break

    if pend:
        if band == "counsel":
            counsel.append([pend_text])
        flush("counsel" if band == "counsel"
              else "panel" if band == "panel" else "author")
    if caption:
        ctx.crit["caption"] = caption
        left = _party(caption[:pivot]) if pivot > 0 else _party(caption)
        right = _party(caption[pivot + 1:]) if pivot >= 0 else ""
        ctx.crit["parties"] = [p for p in (left, right) if p]
        ctx.crit["case_name"] = f"{left} v. {right}" if right else left
    if origin:
        # The origin recital, its number and its judge, told apart by shape:
        # a bare parenthesis holding a number is the court below's docket, a
        # parenthesis naming a Judge is who tried it.
        recital, numbers, judges = [], [], []
        for row in origin:
            inner = row[1:-1].strip() if row.startswith("(") \
                and row.endswith(")") else None
            if inner is None:
                recital.append(row)
            elif re.search(r"\bJudge\b", inner):
                judges.append(inner)
            else:
                numbers.append(inner)
        if recital:
            ctx.crit["lower_court"] = " ".join(recital)
        if numbers:
            ctx.crit["lower_court_docket"] = numbers
        if judges:
            ctx.crit["lower_court_judge"] = "; ".join(judges)
    if counsel:
        ctx.crit["attorneys"] = "\n\n".join(e[0] for e in counsel)


def _read_order(rows, texts, dock, ctx, body_x0) -> None:
    """The bar-discipline order: caption, the two-column apparatus, the
    panel, the paper's own name, the filed date."""
    caption: list[str] = []
    appx: list[list] = []        # the apparatus band, row by row
    panel: list[list] = []
    panel_text = ""
    band = "caption"

    for idx in range(dock + 1, len(rows)):
        pm, group = rows[idx]
        text = texts[idx]
        if not text:
            continue
        if band == "title":
            filed = _FILED.match(text)
            if filed:
                ctx.crit["decision_date"] = _norm(filed.group(1))
                ctx.emit([group], "date", _centred(pm, group))
            break                       # the block ends on the filed date
        if band == "caption" and (_IN_RE.match(text)
                                  or _RESPONDENT.match(text)):
            caption.append(text)
            ctx.emit([group], "caption", _centred(pm, group))
            continue
        if _PANEL_OPEN.match(text) or band == "panel":
            if band != "panel":
                _emit_apparatus(ctx, appx, body_x0)
                band = "panel"
            panel.append(group)
            panel_text = (panel_text + " " + text).strip()
            if panel_text.endswith("."):
                ctx.crit["panel_line"] = panel_text
                ctx.crit["panel"] = _panel_names(panel_text)
                ctx.emit(panel, "panel", False)
                panel, band = [], "roster-done"
            continue
        if _TITLE.match(text) and _centred(pm, group):
            ctx.crit["title"] = text.replace(" ", "")
            ctx.emit([group], "title", True)
            # The order is unsigned above its body; core anchors the writing
            # on this heading, so offer it back.
            ctx.anchor.extend(p.id for p in group)
            band = "title"
            continue
        if band == "caption":
            appx.append(group)
            continue
        break

    if panel:
        ctx.emit(panel, "panel", False)
    if caption:
        ctx.crit["caption"] = caption
        ctx.crit["parties"] = [_party(caption)]
        ctx.crit["case_name"] = _party(caption)


def _emit_apparatus(ctx, groups: list, body_x0: float) -> None:
    """THE APPARATUS BAND IS TWO COLUMNS, and column membership is an x0
    question, never a wording one. On all five orders the left column stands
    at the rail (x0 = 72.0 exactly) and the right column starts at 324.0 or
    360.0 — past the left column's widest row (327.5 on in_re_correa). The
    left column FLOWS: 'A Suspended Member of the Bar of the' / 'District of
    Columbia Court of Appeals' is one sentence the column wrapped, and split
    into two rows its second half reads as a stray masthead. It is joined,
    and a row opening with one of the identifier labels the court prints
    ('Bar Registration No.', 'DDN:', 'BDN:') starts an element of its own.
    The right column's rows are each their own identifier."""
    runs: list[list] = []
    cur: list[list] = []
    right: list[list] = []
    for group in groups:
        left = [p for p in group if p.x0 <= body_x0 + 4.0]
        far = [p for p in group if p.x0 > body_x0 + 4.0]
        if left:
            head = _norm(" ".join(p.plain for p in left))
            if _ID_LABEL.match(head) or not cur:
                if cur:
                    runs.append(cur)
                cur = [left]
            else:
                cur.append(left)
        if far:
            right.append([far])
    if cur:
        runs.append(cur)
    for run in runs + right:
        ctx.emit(run, "case-info", False)


def _margin_stamps(model, finder, body_x0: float) -> list[list]:
    """THE DOCKET THE COURT STAMPS IN EVERY LATER PAGE'S HEAD MARGIN.

    The bar order repeats its docket above the type block of every page
    after the first — 'No. 26-BG-0060' at top 61.2 where page 1's own
    topmost row stands at 75.35. It is stationery in exactly the sense a
    running head is, and core cannot see it: the stamp is set at BODY SIZE
    (14.0) at the rail, so no reduced-type test reaches it, and on a
    two-page order its top-band count can never clear core's repeat floor
    of 0.4 x n_pages, because page 1 prints the same docket at top 183.8 —
    below the 0.22 band core learns heads in. Left in the stream it becomes
    a segment of its own between two halves of one sentence and renders as
    a heading inside the prose ('... during the' / 'No. 26-BG-0060' /
    'period of suspension ...' — kester, alpert).

    Read by POSITION, never by the docket's text: the row stands ABOVE the
    measure page 1 establishes, stands OFF from the page's first text row
    by more than that page's own leading, and is short. Measured over all
    30 records those three tests take exactly the two stamps and nothing
    else — every other row above the measure on a later page is the folio
    core already drops.
    """
    pm0 = model.pages[0]
    live0 = [l for l in pm0.lines
             if l.plain.strip() and not finder.kind(pm0, l)]
    if not live0:
        return []
    measure_top = min(l.top for l in live0)
    out: list[list] = []
    for pm in model.pages[1:]:
        live = [l for l in pm.lines
                if l.plain.strip() and not finder.kind(pm, l)]
        tops = sorted({round(l.top, 0) for l in live})
        # THE PAGE'S OWN LEADING, measured on the page: the stand-off is a
        # ratio against it, so a court resetting its leading needs no edit.
        gaps = [b - a for a, b in zip(tops, tops[1:]) if b - a > 2.0]
        lead = min(gaps) if gaps else 0.0
        for key in tops:
            if key >= measure_top - 3.0:
                break               # inside the measure: this is the text
            below = [t for t in tops if t > key + 2.0]
            if not lead or not below:
                continue
            if below[0] - key <= lead * _STAMP_STANDOFF:
                continue            # flush with the text block, so content
            row = [l for l in live if abs(l.top - key) <= 1.5]
            width = max(l.x1 for l in row) - min(l.x0 for l in row)
            if width > (pm.width - 2 * body_x0) * _STAMP_WIDTH_MAX:
                continue
            out.append(sorted(row, key=lambda l: l.x0))
    return out


def _row_text(group: list) -> str:
    """The row as it reads, left to right. Sorting a row by `top` reverses
    it where the pieces differ in the fourth decimal — alston's dates row is
    413.4919 on the right against 413.4976 on the left, and read in that
    order it matched no landmark and eight rows came out `lower-court`."""
    return _norm(" ".join(l.plain for l in sorted(group, key=lambda l: l.x0)))


def _rows(pm, finder, body_x0: float) -> list[list]:
    """The page's visual rows, furniture removed, and nothing below the
    footnote separator — the 144pt rule the court draws at the rail on
    alston, bloomberg and jones fences a page-1 note zone that is core's
    work, not the block's."""
    fence = min((r.top for r in pm.h_rules
                 if r.x0 <= body_x0 + 2.0 and (r.x1 - r.x0) < 300.0),
                default=None)
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        if fence is not None and line.top > fence:
            continue
        key = round(line.top, 0)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [sorted(groups[k], key=lambda l: l.x0) for k in order]


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.anchor: list[int] = []
        self.crit: dict = {}

    def emit(self, groups: list, role: str, centre: bool = True) -> None:
        """One ELEMENT — a row, or a row and its wraps — as one styled line,
        with every line id it came from kept in its prov."""
        parts = [l for g in groups for l in sorted(g, key=lambda l: l.x0)]
        if not parts:
            return
        first = parts[0]
        text = ""
        for part in parts:
            piece = line_markup(part)
            if not text.strip():
                text = piece
            elif _WRAP_HYPHEN.search(text):
                # A LINE-BREAK HYPHEN NEVER EARNS A SPACE (core's own rule in
                # resolve/assemble._join): d.w. breaks 'BLACKBURNE-RIGSBY'
                # across the announcement's two rows, and a space made it
                # 'BLACKBURNE- RIGSBY'.
                text = text.rstrip() + piece.lstrip()
            else:
                text = text.rstrip() + " " + piece.lstrip()
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

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
                "anchor_ids": self.anchor, "doc_type_final": None}
