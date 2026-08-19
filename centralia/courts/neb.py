"""Nebraska Supreme Court ('neb').

Everything unique to neb lives here. It imports core, never another court
file, and no other court file imports it. Its CourtProfile is registered in
courts/__init__.py (with `front_matter=('syllabus',)`); this module adds the
reader only, so importing it can never raise a duplicate profile.

THE CONTRACT — Nebraska does not publish a slip. What the library serves is
the REPORTER'S BOUND-VOLUME PAGE, photographed off the advance sheets, on a
HALF-LETTER sheet (396 x 612 on all 50 records — never 612 wide, so nothing
here may be measured against a letter page), with the library's own web
header stamped over the top of page 1.

    ┌─ page 1, 396pt wide ───────────────────────────────────────────┐
    │ Nebraska Supreme Court Online Library          5.7pt  the      │
    │ www.nebraska.gov/apps-courts-epub/             5.7pt  library's│
    │ 05/15/2026 08:12 AM CDT                        5.7pt  stamp    │
    │                    - 409 -                     8.5pt  folio    │
    │        Nebraska Supreme Court Advance Sheets  10.5pt ┐ running │
    │                 321 Nebraska Reports         10.5pt ┘ heads    │
    │            AMERICAN EXCH. BANK v. TOPP         8.0pt  short    │
    │               Cite as 321 Neb. 409             8.0pt  vol cite │
    │                                                               │
    │        American Exchange Bank, appellee, v.   11.0pt  THE      │
    │      Luke G. Topp and Ria N. Topp, appellants. 11.0pt  CAPTION │
    │                 ___ N.W.3d ___                 8.0pt  the cite │
    │        Filed May 15, 2026. No. S-25-290.       8.0pt  filed    │
    │ 1. Summary Judgment: Appeal and Error. An …    9.0pt ┐ the     │
    │ 2. ____: ____. An appellate court will …      9.0pt ┘ SYLLABUS │
    │   Appeal from the District Court for Johnson … 11.0pt  origin   │
    │   Sarah E. Cavanagh …, for appellants.        11.0pt  counsel  │
    │   Funke, C.J., Cassel, … and Vaughn, JJ.      11.0pt  panel    │
    │   Bergevin, J.                                11.0pt  BYLINE — │
    └───────────────────────────────────────────────────────── stop ─┘

THE TYPE LADDER SAYS WHOSE WORDS A ROW IS, and it has four rungs, every one
of them measured over all 50 records:

    5.7pt   the library's web header — not the book at all
    8.0-8.5 the VOLUME apparatus: folio, running heads, the volume cite
    9.0     the SYLLABUS — the court's numbered points of law (2,289 rows)
    10.5    the running heads 'Nebraska Supreme Court Advance Sheets' and
            '<vol> Nebraska Reports'
    11.0    the COURT's own text: caption, origin, counsel, panel, opinion

Nothing here is keyed to a page number or a row ordinal. The DISPATCH is
the running-head pair, found in the first three non-furniture rows of page
1 and present on all 50 records: 'Nebraska Supreme Court Advance Sheets'
over '<volume> Nebraska Reports'. Every role below is anchored to that
landmark or to the one before it.

THE PAGE-1 RUNNING HEADS ARE THIS READER'S TO DROP. Core's FurnitureFinder
identifies the folio, the library stamp and the 8pt heads on every page and
the 10.5pt pair on pages 2..n — but NOT the 10.5pt pair on page 1, because
a first page's top rows are where a caption normally lives. Left unclaimed
they stand immediately above the caption this reader claims, one row from
the top of the block, which is exactly where an unclaimed row is most
dangerous. They are dropped as `running-head`.

THE CLAIM MUST BE CONTIGUOUS, and here that means the SYLLABUS is claimed.
Nebraska prints no byline above its numbered points, so a reader that took
the caption and skipped the 9pt band would leave 14-184 rows for core to
open a writing on, and the bisection invariant (pipeline.py:2055) would
then pull the whole claim into that writing and publish an EMPTY
headmatter. So the walk runs unbroken from the caption to the panel, and
the numbered points take the `syllabus` role — NOT `headnotes`. Headnotes
are the Reporter's subject list; these are the court's own statements of
law, printed under no heading at all (there is no 'SYLLABUS' row on any of
the 50, which is also why core's front-matter page inference never fires).

WHERE THE BLOCK ENDS is the BYLINE, and the byline is NOT claimed — core
needs it to open the majority. Measured on all 50: the last four or five
11pt paragraphs before the opinion are, in order, the ORIGIN, two to three
COUNSEL paragraphs, the PANEL (absent only on martinez_v._jensen, a
single-justice special proceeding), and then 'Bergevin, J.' / 'Funke, C.J.'
/ 'Per Curiam.' — the writing's own first row. The reader stops there. If
no byline is found within 8 pages it returns NOTHING rather than guess.

THE 11pt BANDS ARE PARAGRAPHS, NOT ROWS. All of them open at x0=66.0 and
wrap to the rail at 54.0, so the origin, each appearance, the panel and the
byline are grouped by that indent and asked ONCE what they are — which is
what keeps 'Riedmann, Chief Judge, and Bishop and Welch, Judges,' (the
Court of Appeals bench, inside the origin recital) from reading as a panel,
and 'Michael T. Hilgers, Attorney General, …' from reading as a byline.
Each paragraph is identified by a landmark it carries, never by its
position in the run:

    origin   'Appeal from' (34) / 'Appeals from' (6) / 'Petition for
             further review' (6) / 'Original action' (3) / 'Special
             proceeding' (1) — 50 of 50, the first paragraph only
    panel    the bench word 'JJ.' — a closed vocabulary, and no
             appearance in the corpus contains it
    counsel  'for <party status>' or 'pro se'
    byline   the whole paragraph is 'Per Curiam.' or '<Surname>, J.' /
             '<Surname>, C.J.'

A PARAGRAPH THAT MATCHES NONE OF THEM WITHDRAWS THE WHOLE CLAIM. There is
no catch-all: parking an unrecognized row on `caption` or `case-info` would
be a confident wrong answer, and a hole in the middle of the claim is worse
than no claim at all.

THE PRINTED FORM STAYS BESIDE THE PARSED FORM. `caption` keeps the rows
verbatim and `case_name`/`parties` are built from the two sides of the
pivot; `panel_line` keeps the roster as printed and `panel` the surnames;
`lower_court` keeps the origin recital and `disposition` the sentence the
court closes it with. Wrapped statements are de-hyphenated for the parsed
form only ('Vacated and remanded with direc-' / 'tions to dismiss.'), never
in the rendered rows.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder

# ---- neb's declared facts (measured over all 50 records) -----------------
# THE SHEET. A half-letter page, 396.0 x 612.0 to the point on all 50. The
# width is part of the dispatch: nothing in this file may assume 612.
_SHEET_W = 396.0
_SHEET_TOL = 8.0
# THE TYPE LADDER. The court's own text is 11.0pt; the syllabus 9.0pt (all
# 2,289 rows in the corpus); the volume apparatus 8.0-8.5pt; the running
# heads 10.5pt. 10.0 separates the court's text from everything below it.
_COURT_SIZE_MIN = 10.0
# THE CAPTION IS ON THE AXIS. All 151 caption rows in the corpus are centred
# on the page axis to 0.0pt — the Reporter sets nothing else in that band —
# so a row off the axis inside it means this is not the paper measured here.
_AXIS_TOL = 8.0
# THE RUNNING-HEAD PAIR is the dispatch, and page 1 sets it at 10.5pt.
_ADVANCE_SHEETS = "nebraska supreme court advance sheets"
_VOLUME_HEAD = re.compile(r"^\d{1,4}\s+Nebraska Reports$", re.I)
# The pair never stands lower than the third non-furniture row of page 1
# (it is rows 0-1 on all 50; the search allows for the library stamp being
# read as content on a record whose header differs).
_HEAD_SEARCH = 3
# THE VOLUME CITE closes the caption band. All 50 print the placeholder the
# advance sheets carry before the N.W. volume is assigned; the numbered form
# is what the same row becomes in the bound reprint, so both are read.
_VOL_CITE = re.compile(
    r"^(?:_{2,}|\d{1,4})\s*N\.\s?W\.\s?\d?d\.?\s*(?:_{2,}|\d{1,4})$", re.I)
# THE FILING ROW carries the date AND the docket, on one line, on all 50:
# 'Filed May 15, 2026. No. S-25-290.' / 'Filed February 6, 2026. Nos.
# S-25-064, S-25-065.' / 'Nos. S-25-096 through S-25-099.'
_FILED = re.compile(
    r"^Filed\s+(?P<date>[A-Z][a-z]+\s+\d{1,2},\s*\d{4})\.\s*"
    r"Nos?\.\s*(?P<dockets>.+?)\.?$")
# A PARAGRAPH OPENS at 66.0 and wraps to the rail at 54.0 — a 12pt step,
# invariant on all 50 records and every one of the 4-5 paragraphs.
_PARA_INDENT = 66.0
_INDENT_TOL = 2.0
# THE ORIGIN's opening words: a closed vocabulary covering 50 of 50.
_ORIGIN = re.compile(
    r"^(?:Appeals?\s+from\b|Petition\s+for\s+further\s+review\b"
    r"|Original\s+action\b|Special\s+proceeding\b)")
# THE PANEL's bench word. 'JJ.' appears in every roster in the corpus
# (including 'Funke, C.J., Cassel, Stacy, and Papik, JJ., and Heavican,
# Retired C.J., and Martinez, District Judge.') and in no appearance.
_ROSTER = re.compile(r"\bJJ\.")
# BENCH WORDS, so a roster yields surnames and not a judge called 'District'.
# A closed vocabulary, matched with the token's trailing period already
# removed so 'District Judge.' and 'JJ.' both land here.
_BENCH_WORD = re.compile(
    r"^(?:Retired\s+)?(?:C\.?\s?J\.?|JJ\.?|D\.?\s?J\.?|Justices?"
    r"|(?:District\s+|Chief\s+|Retired\s+)?Judges?)$", re.I)
# 'Bergevin, and Vaughn JJ.' — in_re_estate_of_meyers sets the last surname
# and its bench word with no comma between them.
_BENCH_TAIL = re.compile(r"\s+(?:JJ|J|C\.\s?J|D\.\s?J)\.?$")
# THE APPEARANCES name themselves in their closing words.
_PARTY_STATUS = (r"appellant|appellee|cross-appellant|cross-appellee"
                 r"|plaintiff|defendant|intervenor|respondent|applicant"
                 r"|relator|petitioner|amicus|amici")
_COUNSEL = re.compile(r"\bfor\s+(?:%s)" % _PARTY_STATUS, re.I)
_PRO_SE = re.compile(r"\bpro\s+se\b", re.I)
# THE BYLINE — the writing's first row, and the reader's stop. It is left
# UNCLAIMED: core opens the majority on it.
_BYLINE = re.compile(
    r"^(?:Per\s+Curiam\.|[A-Z][A-Za-z’'\-]*(?:-[A-Z][A-Za-z]+)?,"
    r"\s*(?:C\.\s?J\.|J\.))$")
# THE DISPOSITION sentence the court closes the origin recital with, in the
# forms the corpus prints. Found at a sentence boundary, so the paragraph's
# own opening 'Appeal from …' can never be taken for 'Appeal dismissed.'
_DISPOSITION = re.compile(
    r"(?<=\.\s)(?=(?:Affirmed|Reversed|Vacated|Dismissed|Remanded"
    r"|Appeals?\s+dismissed|Judgments?|Final\s+order|Sentences?"
    r"|Cause\s+remanded)\b)")
# The trial judge, as the origin names them: ': Ricky A. Schreiner, Judge.'
# and ', Ricky A. Schreiner, Judge,' both occur. 'Judges' is excluded by the
# word boundary, which is what keeps the Court of Appeals bench out.
_TRIAL_JUDGE = re.compile(
    r"[:,]\s*([A-Z][A-Za-z.’'\- ]+?),\s*Judge\b")
# A party's STATUS LABEL, where it stands in the caption's prose. Nebraska
# prints the status after the name it belongs to, so the label is also where
# that party's name ENDS — 'Robert B. Evnen, in his official capacity as
# Nebraska Secretary of State, appellee, and the Nebraska Republican Party,
# intervenor.' names the appellee up to the first label.
_STATUS_AT = re.compile(r",\s*(?:and\s+)?(?:%s)s?\b" % _PARTY_STATUS, re.I)
_PIVOT = re.compile(r",?\s+v\.\s+")
# A SENTENCE BOUNDARY INSIDE A CAPTION, which is not the same thing as a
# period: 'Carol J. Goldie' and 'Luke G. Topp' both print an initial. Two
# lower-case letters before the stop is what separates 'deceased. Barbara'
# from 'J. Goldie'.
_SENTENCE = re.compile(r"(?<=[a-z]{2}\.)\s+(?=[A-Z])")
# THE BLOCK'S REACH. The byline stands on page 1 (1 record), 2 (32), 3 (16)
# or 6 (state_v._lopez, whose syllabus runs 184 rows). 8 pages covers it
# with margin; a record that shows no byline inside it is not this paper.
_MAX_PAGES = 8
# The corpus prints 4 or 5 paragraphs between the syllabus and the byline.
_MAX_PARAS = 12


def _norm(text: str) -> str:
    return " ".join(text.split())


def _dehyphenate(rows: list[str]) -> str:
    """Join wrapped rows the way the page reads them: Nebraska breaks
    'direc-' / 'tions to dismiss.' across two rows of the origin recital,
    and joining those on a space invents a word. Used for the PARSED form
    only — the rendered rows keep exactly what the page prints."""
    out = ""
    for row in rows:
        piece = _norm(row)
        if not out:
            out = piece
        elif out.endswith("-"):
            out = out[:-1] + piece
        else:
            out = out + " " + piece
    return out


def _strip_status(name: str) -> str:
    """The party's name, which runs up to its status label. Statuses are a
    closed vocabulary; party NAMES are never read by wording."""
    out = _norm(name)
    cut = _STATUS_AT.search(out)
    if cut:
        out = out[:cut.start()]
    return out.strip().rstrip(",")


def _panel_names(line: str) -> list[str]:
    """The surnames in a roster, bench words removed."""
    out: list[str] = []
    for token in re.split(r",|\band\b", _norm(line)):
        token = token.strip(" ,").rstrip(".")
        if not token or _BENCH_WORD.match(token):
            continue
        out.append(_BENCH_TAIL.sub("", token))
    return out


@decider("headmatter.read", court="neb")
def read_headmatter_neb(model, geom, **_):
    """Read Nebraska's bound-volume block, or NOTHING."""
    if not model.pages:
        return NOTHING
    page1 = model.pages[0]
    # THE SHEET IS PART OF THE DISPATCH — this contract is a half-letter
    # book page, and a letter-sized filing is not it.
    if abs(page1.width - _SHEET_W) > _SHEET_TOL:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 11.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 54.0)
    finder = FurnitureFinder(model, body_x0, body_size)

    rows = [g for pm in model.pages[:_MAX_PAGES] for g in _rows(pm, finder)]
    if len(rows) < 6:
        return NOTHING

    # ---- the dispatch: the running-head pair, near the top of page 1 -----
    head = None
    for idx in range(min(_HEAD_SEARCH, len(rows) - 1)):
        if rows[idx][0].page != 1:
            break
        if _norm(_text(rows[idx])).lower() != _ADVANCE_SHEETS:
            continue
        if _VOLUME_HEAD.match(_norm(_text(rows[idx + 1]))):
            head = idx
            break
    if head is None:
        return NOTHING

    ctx = _Ctx()
    # Everything from the top of the page down to and including the pair is
    # the volume's own furniture. Core drops it on pages 2..n but not here,
    # and an unclaimed row one step above the caption is what opens a
    # phantom writing over the whole block.
    for idx in range(head + 2):
        ctx.drop(rows[idx], "running-head")

    # ---- the caption: 11pt, centred on the page axis, 2-6 rows ----------
    # It closes at the VOLUME CITE, which is the landmark below it — never
    # at a row count. Measured: all 151 caption rows in the corpus are
    # 11.0pt and centred on the axis to 0.0pt.
    cap_rows: list[str] = []
    idx = head + 2
    while idx < len(rows) and not _VOL_CITE.match(_norm(_text(rows[idx]))):
        group = rows[idx]
        if (group[0].size or 0.0) < _COURT_SIZE_MIN:
            return NOTHING          # something stands in the caption band
        centre = (group[0].x0 + max(l.x1 for l in group)) / 2
        if abs(centre - page1.width / 2) > _AXIS_TOL:
            return NOTHING          # …and it is not set on the axis
        cap_rows.append(_text(group))
        ctx.emit(group, "caption")
        idx += 1
    if not cap_rows or idx >= len(rows):
        return NOTHING

    # ---- the volume cite ------------------------------------------------
    # The row is nothing but a reporter citation for this opinion, so it
    # takes `citation`. The value is not recorded: all 50 print the blank
    # placeholder the advance sheets carry, and a blank is not a cite.
    ctx.emit(rows[idx], "citation")
    idx += 1

    # ---- the filing row: the date AND the docket, on one line -----------
    filed = _FILED.match(_norm(_text(rows[idx])))
    if not filed:
        return NOTHING
    # ONE ROW, TWO FACTS. The row is the paper's filing line — that is what
    # it calls itself — so it renders as `date`, and the docket it carries
    # is recorded in the criteria rather than tinted onto a second role the
    # page does not print.
    ctx.emit(rows[idx], "date")
    ctx.crit["decision_date"] = _norm(filed.group("date"))
    # 'S-25-064, S-25-065' / 'S-25-096 through S-25-099' — a range prints
    # only its endpoints, so only its endpoints are recorded.
    dockets = [t.strip() for t in
               re.split(r",|\bthrough\b", filed.group("dockets"))
               if t.strip()]
    if dockets:
        ctx.crit["docket_number"] = dockets[0]
        if dockets[1:]:
            ctx.crit["other_dockets"] = dockets[1:]
    idx += 1

    # ---- the syllabus: every row below the court's type size ------------
    # The court's own numbered points of law, under no heading. Claimed in
    # place, tagged `syllabus`, and NOT lifted into a section: the
    # headmatter renders whole and in the page's order.
    while idx < len(rows) and (rows[idx][0].size or 0.0) < _COURT_SIZE_MIN:
        ctx.emit(rows[idx], "syllabus", centre=False)
        idx += 1

    # ---- the 11pt paragraphs, each asked once what it is ----------------
    paras: list[tuple[list, list[str]]] = []
    while idx < len(rows) and len(paras) <= _MAX_PARAS:
        group = rows[idx]
        first = group[0]
        if (first.size or 0.0) < _COURT_SIZE_MIN:
            return NOTHING          # the 9pt band is closed; nothing reopens it
        if first.x0 >= _PARA_INDENT - _INDENT_TOL:
            paras.append(([group], [_text(group)]))
        elif paras:
            paras[-1][0].append(group)
            paras[-1][1].append(_text(group))
        else:
            return NOTHING          # a wrap with nothing to wrap onto
        # A paragraph is only decidable once it is whole, so the walk looks
        # one row ahead: the paragraph closes at the next row that opens at
        # the indent, or at the end of the block.
        idx += 1
        nxt = rows[idx] if idx < len(rows) else None
        if nxt is not None and nxt[0].x0 < _PARA_INDENT - _INDENT_TOL \
                and (nxt[0].size or 0.0) >= _COURT_SIZE_MIN:
            continue
        groups, texts = paras[-1]
        text = _dehyphenate(texts)
        if _BYLINE.match(text):
            # THE PAPER'S OWN WRITING STARTS HERE. The byline is left in the
            # stream: core opens the majority on it.
            paras.pop()
            break
        if _ROSTER.search(text):
            ctx.crit.setdefault("panel_line", text)
            ctx.crit.setdefault("panel", _panel_names(text))
            for g in groups:
                ctx.emit(g, "panel", centre=False)
            continue
        if len(paras) == 1 and _ORIGIN.match(text):
            _origin(ctx, text)
            for g in groups:
                ctx.emit(g, "lower-court", centre=False)
            continue
        if _COUNSEL.search(text) or _PRO_SE.search(text):
            ctx.counsel.append(text)
            for g in groups:
                ctx.emit(g, "counsel", centre=False)
            continue
        # NO CATCH-ALL. An unidentified paragraph inside the block would
        # either be mis-tinted or leave a hole in the claim, and both are
        # worse than handing the record back to core whole.
        return NOTHING
    else:
        return NOTHING              # ran out of block without finding a byline

    if not ctx.crit.get("lower_court") or not ctx.crit.get("decision_date"):
        return NOTHING
    ctx.crit["caption"] = [_norm(r) for r in cap_rows]
    _caption(ctx, cap_rows)
    if ctx.counsel:
        ctx.crit["attorneys"] = " ".join(ctx.counsel)
    # The layout contract, named for the landmark it always prints.
    ctx.crit["headmatter_style"] = "advance-sheet volume page"
    short = _short_case_name(page1, finder)
    if short:
        ctx.crit["short_case_name"] = short
    return ctx.result()


def _origin(ctx, text: str) -> None:
    """Split the origin recital from the disposition it closes on, and name
    the judge it names. The two are separate facts printed as one paragraph,
    and the paragraph itself renders whole as `lower-court`."""
    cut = _DISPOSITION.search(text)
    recital = text[:cut.start()].strip() if cut else text
    ctx.crit["lower_court"] = recital
    if cut:
        ctx.crit["disposition"] = text[cut.start():].strip()
    judges = [_norm(j) for j in _TRIAL_JUDGE.findall(recital)]
    if judges:
        ctx.crit["lower_court_judge"] = "; ".join(judges)


def _caption(ctx, cap_rows: list[str]) -> None:
    """The two sides of the pivot, with their statuses stripped.

    Nebraska sets its caption as running prose, so a consolidated record
    prints two or three sentences with a pivot in each ('In re Estate of
    Paul A. Knapp, deceased.' over 'Barbara Knapp, appellant, v. Lance
    Knapp, …, appellee.'). Where the printed caption holds exactly ONE
    pivot the parties are read off it; where it holds none or several,
    nothing is invented — the verbatim rows are already recorded."""
    whole = _dehyphenate(cap_rows)
    parts = _PIVOT.split(whole)
    if len(parts) != 2:
        return
    # A pivot's own sentence is the one it stands in: the 'In re Estate of
    # …, deceased.' that opens a probate caption is a separate sentence and
    # not a party.
    left = _strip_status(_SENTENCE.split(parts[0])[-1])
    right = _strip_status(_SENTENCE.split(parts[1])[0])
    if not left or not right:
        return
    ctx.crit["parties"] = [left, right]
    ctx.crit["case_name"] = f"{left} v. {right}"


def _short_case_name(page1, finder) -> str | None:
    """The Reporter's own short form, from the 8pt running head. Read, not
    claimed: core identifies the row as furniture and drops it, and this
    reader only keeps what it says."""
    heads = [l for l in sorted(page1.lines, key=lambda l: l.top)
             if finder.kind(page1, l) == "running-head"
             and 7.5 <= (l.size or 0.0) <= 8.6
             and not _norm(l.plain).lower().startswith("cite as")]
    return _norm(heads[0].plain) if heads else None


def _text(group: list) -> str:
    return " ".join(l.plain for l in sorted(group, key=lambda l: l.x0))


def _rows(pm, finder) -> list[list]:
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or finder.kind(pm, line):
            continue
        key = round(line.top, 1)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(line)
    return [groups[k] for k in order]


class _Ctx:
    """The emit buffer: what the walk placed, and where it came from."""

    def __init__(self):
        self.items: list = []
        self.dropped: list = []
        self.consumed: set[int] = set()
        self.crit: dict = {}
        self.counsel: list[str] = []

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
        self.dropped.append(m.Dropped(
            text=_norm(" ".join(p.plain for p in parts))[:400],
            prov=m.Prov(parts[0].page, tuple(p.id for p in parts)),
            kind=kind or "furniture"))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}
