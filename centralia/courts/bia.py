"""Board of Immigration Appeals ('bia').

NOT A COURT — an administrative tribunal inside the Department of Justice.
Everything unique to it lives here; it imports core, never another court
file, and no other court file imports it.

WHAT THE PAPER IS. All 32 records in this corpus are the same publication:
a PRECEDENT DECISION as the Board's own reporter sets it, `I&N Dec.`. It is
not the single-member removal order the phrase 'Board of Immigration
Appeals' usually calls to mind — there is no `IN REMOVAL PROCEEDINGS`
posture, no `File: A### ### ###` line, no Immigration Court city, and no
alien registration number anywhere in the 32 records (searched: zero hits).
The published reporter prints none of that. What it prints is a masthead,
a matter name, a date, the agency's three-line name, the reporter's
summary of the holding, the appearances, the panel, and then the writing:

    ┌──────────────────────────────────────────────────────────────────┐
    │ Cite as 29 I&N Dec. 723 (BIA 2026)      Interim Decision #4211   │ 11pt, y=70
    │                                                                  │  (furniture)
    │        Matter of Rasheen Stefan BEST, Respondent                 │ 14pt BOLD
    │              Decided by Board May 7, 2026¹                       │ 13pt centred
    │                                                                  │
    │                 U.S. Department of Justice                       │ 13pt centred
    │           Executive Office for Immigration Review                │  — the agency
    │              Board of Immigration Appeals                        │    naming itself
    │                                                                  │
    │ The Immigration Judge erred in granting a waiver of …            │ 11pt at the
    │ status in discretion because the respondent's equities …         │ body rail —
    │                                                                  │ the reporter's
    │ FOR THE RESPONDENT:  Raymond Sykes, Esquire, New York, New York  │ summary,
    │ FOR THE DEPARTMENT OF HOMELAND SECURITY:  Joanne M. Reed, …      │ then counsel,
    │ Chief Counsel                                                    │ then the panel
    │ BEFORE:  Board Panel:  GORMAN, Deputy Chief Appellate …          │
    │ VOLKERT, Appellate Immigration Judge; MCCLOSKEY, Temporary …     │
    │                                                                  │
    │ MCCLOSKEY, Temporary Appellate Immigration Judge:                │ the writing
    └──────────────────────────────────────────────────────────────────┘

THE COVER SEPARATES BY TYPE SIZE, and that is what this reader walks. On a
612x792 page with a 108pt body rail the Board sets exactly three sizes above
the byline, and each size means one thing:

  14.0 bold, centred   the MATTER — one row, or two when two matters are
                       decided together (orozco_becerra: 32 of 32 records
                       set the matter at 14pt bold and nothing else at 14pt)
  13.0 centred         the date row, then the agency's three-row name. The
                       date is always the FIRST of that run and the agency
                       name the rest; no wording decides which is which.
  11.0 at the rail     the reporter's summary, the appearances, the panel

The 13pt BODY type is the same size as the agency name and is told apart by
POSITION: the banner is centred on the page axis, the body sits at the rail
or its 126pt paragraph indent. The walk never reaches it anyway — it stops
at the byline.

THE LANDMARK IS THE AGENCY NAMING ITSELF, not the matter title. `Matter of`
is wording and would be the obvious thing to key on; the tribunal's own
three-row name is what this publication always prints and what tells this
paper apart from an Attorney General decision or a Ninth Circuit slip that
happens to quote a matter name. No banner, no claim: the reader returns
NOTHING and core's shared walk has the record (the ca6 rule).

WITHIN THE 11pt BAND two printed labels split it, and both are closed
vocabularies of ROLE, never of name: `FOR THE …:` opens the appearances and
`BEFORE:` opens the panel. Each band then runs to the next landmark, so a
continuation row with no landmark of its own ('Chief Counsel',
'Massachusetts', 'Immigration Judges.') belongs to the band it is inside —
the ca4 reading. Four records set `BEFORE:` as three same-row pieces
(shentu, t-d-e, santiago-santiago, orozco_becerra) because pdfio split the
row at its wide label gaps, so rows are grouped by BASELINE before anything
is matched.

THE READER STOPS AT THE BYLINE and never claims it. Counted over the corpus
there is exactly one byline per record, all 32 on page 1, all ending in ':'
— every other row of that shape ('MCCLOSKEY, Temporary Appellate Immigration
Judge.') is a wrapped tail INSIDE the `BEFORE:` band and is claimed as panel
before it can be mistaken for one. There is not one separate writing in the
corpus.

THE RUNNING HEAD IS FURNITURE AND STAYS FURNITURE. Core drops both slugs and
the folio; this reader reads their VALUES without consuming them, so they
are recorded as Dropped exactly once and the two facts they carry are kept.
`citation` takes the reporter cite. `docket_number` takes the Interim
Decision number, and the choice is declared rather than assumed: the A-number
that would be this case's docket is not printed in the published reporter, and
the Interim Decision serial is the only identifier the Board puts on the
paper — it is how the decision is cited before the bound volume exists.

WHAT THIS FILE DOES NOT DO. The byline grammar is core's, driven by the
titles declared on this court's CourtProfile below; without them core's
default (`Justice`) matched nothing and 31 of 32 authored decisions typed as
`order`. The footnotes, the paragraphing and the section headings are core's.
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
# THE BENCH TITLES THIS BODY PRINTS. The Board renamed its members in 2025:
# every byline in the corpus reads '<SURNAME>, <office> Appellate Immigration
# Judge:'. The older 'Board Member' forms are declared beside them because
# they are the same grammar and the reporter's back volumes are full of them.
# Longest first — the title alternation is ordered, and core's own prefix
# group knows 'Chief'/'Acting'/'Senior' but not 'Deputy Chief' or 'Temporary'.
_BIA_TITLES = (
    "Deputy Chief Appellate Immigration Judge",
    "Temporary Appellate Immigration Judge",
    "Chief Appellate Immigration Judge",
    "Deputy Appellate Immigration Judge",
    "Appellate Immigration Judge",
    "Temporary Board Member",
    "Acting Board Member",
    "Board Member",
    "Chairman",
    "Vice Chairman",
)

PROFILE = register(CourtProfile(
    "bia", "Board of Immigration Appeals",
    byline=BylineGrammar(style="prose", titles=_BIA_TITLES),
    rollout="migrated",
))

# ---------------------------------------------------------------------------
# the cover
# ---------------------------------------------------------------------------
_AXIS_TOL = 30.0            # how far a centred row may sit off the page axis
_SIZE_TOL = 0.6
_MATTER_SIZE = 14.0         # the matter, set bold
_BANNER_SIZE = 13.0         # the date and the agency's name, centred
_BAND_SIZE = 11.0           # summary, appearances, panel — at the rail
# WHERE THE SUMMARY BREAKS INTO PARAGRAPHS. The band is wrapped prose, so its
# rows are lines, not paragraphs, and emitting one row per line chopped a
# single sentence into three ('The Immigration Judge erred in granting a
# waiver of inadmissibility and adjustment of' / 'status in discretion
# because …' / 'lengthy criminal history …'). Two signals say where a real
# paragraph starts, and across all 32 records they NEVER disagree:
#
#   the leading      a continuation follows its predecessor at a gap of -0.1
#                    to 1.0pt; a new point sits 11.0-12.0pt lower, which is a
#                    blank line at this leading. The band between is empty, so
#                    the threshold sits in the middle of it.
#   the numbering    a new point opens '(1)', '(2)' … flush at the rail and
#                    hangs its continuations at 121.7. Single-holding records
#                    print no number at all (best, arana_castillo), which is
#                    why the gap is read too and not the numbering alone.
_SUMMARY_BREAK_GAP = 5.0
_SUMMARY_POINT = re.compile(r"^\(\d+\)")

# The agency naming itself: the landmark this reader dispatches on.
_AGENCY = ("board of immigration appeals",
           "executive office for immigration review")
_AGENCY_ROW = re.compile(
    r"^(?:U\.?S\.?\s+)?(?:Department of Justice"
    r"|Executive Office for Immigration Review"
    r"|Board of Immigration Appeals)$", re.I)

_DECIDED = re.compile(
    r"^(?:Decided|Reconsidered|Amended|Corrected|Argued)\b", re.I)
_DATE = re.compile(
    r"((?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s*\d{4})")
# The appearances. The label names the ROLE appeared for, and the corpus
# prints five of them; the pattern is the shape 'FOR THE <role>:', never a
# roll of party names.
_COUNSEL = re.compile(r"^FOR\s+(?:THE\s+)?[A-Z][A-Z '&,.\-]{2,60}:", re.I)
_PANEL = re.compile(r"^BEFORE\b", re.I)
_PANEL_LABEL = re.compile(r"^BEFORE\s*:?\s*(?:Board\s+(?:Panel|En\s+Banc)"
                          r"\s*:?\s*)?", re.I)
# A SURNAME on the roster is an ALL-CAPS token; the offices beside it are
# title case ('Deputy Chief Appellate Immigration Judge') and the label
# words are stripped first. Read by CASE, never against a roll of judges —
# the Board seats temporary members and its bench changes every term.
_ROSTER_NAME = re.compile(r"\b[A-Z][A-Z’'\-]{1,}\b")
_NOT_A_NAME = frozenset({"BOARD", "PANEL", "BEFORE", "EN", "BANC", "AND",
                         "THE", "OF", "IMMIGRATION", "APPEALS", "JUDGE",
                         "JUDGES", "MEMBER", "MEMBERS", "US", "U", "S"})
# The byline that opens the writing. The STOP, not the parse: core's grammar
# reads it, driven by _BIA_TITLES above.
_BYLINE = re.compile(
    r"^(?:[A-Z][A-Za-z’'\-]+(?:\s+[A-Z][A-Za-z’'\-]+)?,\s*"
    r"(?:[A-Z][a-z]+\s+){0,3}(?:Appellate\s+Immigration\s+Judge"
    r"|Board\s+Member|Chairman)|PER\s+CURIAM)\s*:$")
# The party STATUS the matter name closes on — a finite role vocabulary.
_STATUS_TAIL = re.compile(
    r",\s*(?:Respondents?|Applicants?|Petitioners?|Appellants?|Beneficiar(?:y|ies)"
    r"|Employer|Alien)\s*$", re.I)

_CITE_AS = re.compile(r"^Cite as\s+(.+?)\s*$", re.I)
_INTERIM = re.compile(r"^(Interim Decision\s*#?\s*\d+)\s*$", re.I)
_TOP_BAND = 110.0           # where the running head lives on a 792pt page


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _rows(pm, finder) -> list[list]:
    """The page's inked rows, furniture removed, grouped by BASELINE. Four
    records set `BEFORE:  Board Panel:  MALPHRUS, …` as three pieces because
    pdfio split the row at its label gaps; ungrouped, two of those pieces
    carry no landmark and fall out of the band."""
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

    def emit(self, group: list, role: str, centre: bool = False,
             stacked: bool = False) -> None:
        """``stacked``: the group is several BASELINES of one paragraph, not
        several horizontal pieces of one row, so it orders by baseline first.
        Sorting a stacked group by x0 alone reads a hanging indent backwards —
        bia's numbered summary points open '(1)' at the 108pt rail and hang
        their continuations at 121.7, so every wrapped line would sort ahead
        of the sentence it continues."""
        parts = sorted(group, key=(lambda l: (l.top, l.x0)) if stacked
                       else (lambda l: l.x0))
        if not parts:
            return
        text = ""
        for part in parts:
            piece = line_markup(part)
            text = (text.rstrip() + " " + piece.lstrip()) if text.strip() \
                else piece
        first = parts[0]
        self.items.append(m.HmLine(
            text=text, prov=m.Prov(first.page, tuple(p.id for p in parts)),
            align=m.Align.CENTER if centre else m.Align.LEFT,
            x0=first.x0, size=first.size or 0.0,
            bold=all(bool(p.all_bold) for p in parts), role=role))
        self.consumed.update(p.id for p in parts)

    def result(self) -> dict:
        return {"criteria": self.crit, "items": self.items, "attorneys": [],
                "dropped": self.dropped, "consumed": self.consumed,
                "anchor_ids": [], "doc_type_final": None}


def _size_is(group, want: float) -> bool:
    sizes = [l.size for l in group if l.size]
    return bool(sizes) and abs(max(sizes) - want) <= _SIZE_TOL


def _centred(group, width: float) -> bool:
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return abs((x0 + x1) / 2 - width / 2) <= _AXIS_TOL


def _read_running_head(pm, crit: dict) -> None:
    """The two slugs the reporter prints across the head of every page. They
    are furniture — core drops them and this reader does NOT consume them —
    but each carries a fact, and reading a value is not claiming a row."""
    for line in pm.lines:
        if line.top > _TOP_BAND:
            break
        flat = _norm(line.plain)
        cite = _CITE_AS.match(flat)
        if cite:
            crit.setdefault("citation", _norm(cite.group(1)))
            continue
        interim = _INTERIM.match(flat)
        if interim:
            # The Board's own serial for the decision. See the module note:
            # the published reporter prints no A-number, and this is the
            # only identifier on the paper.
            crit.setdefault("docket_number", _norm(interim.group(1)))


def _roster(text: str) -> list[str]:
    """Who sat, from the roster as printed. The offices are title case and
    the label words are stripped first, so what is left in capitals is the
    surnames."""
    body = _PANEL_LABEL.sub("", _norm(text))
    seen: list[str] = []
    for tok in _ROSTER_NAME.findall(body):
        if tok in _NOT_A_NAME or len(tok) < 2:
            continue
        if tok not in seen:
            seen.append(tok)
    return seen


@decider("headmatter.read", court="bia")
def read_headmatter_bia(model, geom, **_):
    """Walk the reporter's cover by type size, or return NOTHING."""
    if not model.pages:
        return NOTHING
    pm = model.pages[0]
    body_x0 = geom.body_x0 if geom and geom.body_x0 else 108.0
    body_size = geom.body_size if geom and geom.body_size else 13.0
    finder = FurnitureFinder(model, body_x0, body_size)
    rows = _rows(pm, finder)
    if not rows:
        return NOTHING

    # ---- the landmark: the agency naming itself --------------------------
    flats = [_norm(" ".join(l.plain for l in g)) for g in rows]
    banner_at = [i for i, t in enumerate(flats[:14])
                 if t.lower() in _AGENCY and _centred(rows[i], pm.width)]
    if len(banner_at) < 2:
        return NOTHING

    ctx = _Ctx()
    _read_running_head(pm, ctx.crit)

    matter_rows: list[str] = []
    panel_rows: list[str] = []
    counsel_rows: list[str] = []
    band = "matter"
    banner_done = max(banner_at)

    # The summary's rows are held until the paragraph they belong to is whole.
    para: list = []

    def flush_summary() -> None:
        if para:
            ctx.emit(list(para), "summary", stacked=True)
            para.clear()

    for i, group in enumerate(rows):
        text = flats[i]
        if not text:
            continue

        # THE PANEL BAND runs from `BEFORE:` to the byline, and its wrapped
        # tail carries no landmark of its own.
        if band == "panel":
            if _BYLINE.match(text):
                break                       # the writing begins
            panel_rows.append(text)
            ctx.emit(group, "panel")
            continue
        if _PANEL.match(text):
            flush_summary()
            band = "panel"
            panel_rows.append(text)
            ctx.emit(group, "panel")
            continue

        # THE APPEARANCES run from the first `FOR THE …:` to the panel.
        if _COUNSEL.match(text):
            flush_summary()
            band = "counsel"
            counsel_rows.append(text)
            ctx.emit(group, "counsel")
            continue
        if band == "counsel":
            counsel_rows.append(text)
            ctx.emit(group, "counsel")
            continue

        # ---- above the appearances, the SIZE says what a row is ----------
        if i <= banner_done:
            if _size_is(group, _MATTER_SIZE) and band == "matter":
                matter_rows.append(text)
                ctx.emit(group, "caption", centre=_centred(group, pm.width))
                continue
            if _size_is(group, _BANNER_SIZE):
                band = "banner"
                if _AGENCY_ROW.match(text):
                    if text.lower() == "board of immigration appeals":
                        ctx.crit.setdefault("court", text)
                    ctx.emit(group, "court", centre=True)
                else:
                    # The one row between the matter and the agency's name:
                    # the date the Board decided it.
                    got = _DATE.search(text)
                    if got:
                        ctx.crit.setdefault("decision_date", got.group(1))
                    ctx.emit(group, "date", centre=_centred(group, pm.width))
                continue
            # A row at no position this paper uses is left to core.
            continue

        # Below the agency's name and above the appearances: the reporter's
        # SUMMARY, set at the band size and at the rail.
        #
        # `summary`, NOT `headnotes` (the user, 2026-08-21). The two roles are
        # different things and model.py draws the line: headnotes are the
        # reporter's SUBJECT list, a summary is a précis somebody actually
        # wrote. What this paper prints is prose that states the holding —
        # 'The Immigration Judge erred in granting a waiver of inadmissibility
        # … because the respondent's equities were outweighed by his serious
        # and lengthy criminal history' (best) — numbered '(1)', '(2)' when
        # the decision holds more than one thing. Sentences about THIS case,
        # never a list of topics. Contrast mass, which prints the subject list
        # proper ('Pretrial Detention. Robbery.') and is tagged headnotes.
        if _size_is(group, _BAND_SIZE):
            top = min(l.top for l in group)
            if para:
                gap = top - max(l.bottom for l in para)
                if gap >= _SUMMARY_BREAK_GAP or _SUMMARY_POINT.match(text):
                    flush_summary()
            para.extend(group)
            continue
        if _BYLINE.match(text):
            flush_summary()
            break
        flush_summary()
        continue

    flush_summary()

    if not matter_rows or not panel_rows:
        return NOTHING          # not this cover: leave the record to core

    # ---- the criteria ----------------------------------------------------
    # A 'Matter of' caption HAS NO ADVERSITY, so `parties` — which renders
    # ' v. '.join(...) — is left empty on purpose. The printed rows and the
    # normalized name are both kept; neither substitutes for the other.
    ctx.crit["caption"] = list(matter_rows)
    ctx.crit["case_name"] = "; ".join(
        _STATUS_TAIL.sub("", r).rstrip(",") for r in matter_rows)
    panel_line = _norm(" ".join(panel_rows))
    ctx.crit["panel_line"] = panel_line
    ctx.crit["judges"] = _PANEL_LABEL.sub("", panel_line).strip()
    bench = _roster(panel_line)
    if bench:
        ctx.crit["panel"] = bench
    if counsel_rows:
        ctx.crit["attorneys"] = _norm(" ".join(counsel_rows))[:4000]
    ctx.crit["headmatter_style"] = "reporter-cover"
    return ctx.result()


# ---------------------------------------------------------------------------
# writing.covers — where a Board Member writing separately opens
# ---------------------------------------------------------------------------
# THE BOARD DOES NOT SIGN A SEPARATE WRITING WITH A BYLINE; it heads it with
# a TITLE that names both the paper and its author, at the body rail and in
# the body's own type:
#
#     CONCURING OPINION:  Hugh G. Mullane, Appellate Immigration Judge
#
# No byline test can reach that. Core's prose grammar wants an ALL-CAPS
# surname; this heading sets the author's full name in title case behind a
# colon, and the court even prints the title misspelled. One record in the 32
# carries one (`r-a-n`), and the page announces it TWICE — once in the
# `BEFORE:` band on page 1 ('Concurring Opinion:  MULLANE, Appellate
# Immigration Judge.', which is the roster stating who wrote separately and
# stays in the headmatter) and once at the head of the writing itself on page
# 7. Left to core the concurrence merged into the majority, as it did in v1:
# 4 paragraphs of a Board Member's own reasoning filed under another judge's
# name.
#
# The heading STAYS IN the writing — it is that paper's own title, not
# apparatus — so nothing is dropped. The kind is the word the court printed;
# `normalize_opinion_type` reads it, and 'concuring' contains 'concur'.
_SEPARATE = re.compile(
    r"^(?P<kind>CONCUR\w*|DISSENT\w*|SEPARATE)\s+OPINION\s*:", re.I)


@decider("writing.covers", court="bia")
def writing_covers_bia(model=None, **_):
    """The heading a separately-writing Board Member opens on, or NOTHING."""
    if model is None or len(model.pages) < 2:
        return NOTHING
    starts: dict[int, str] = {}
    for pm in model.pages[1:]:
        for line in pm.lines:
            got = _SEPARATE.match(_norm(line.plain))
            if got:
                starts[line.id] = got.group("kind").lower()
    if not starts:
        return NOTHING
    return {"starts": starts, "drop": []}
