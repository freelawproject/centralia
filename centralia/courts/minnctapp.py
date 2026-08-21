"""Minnesota Court of Appeals ('minnctapp').

Everything unique to minnctapp lives here. It imports core, never another
court file, and no other court file imports it. Its CourtProfile is
registered in courts/__init__.py.

THE PAPER IS NOT ITS SIBLING'S. minn (the Supreme Court) sets three things
out in a RIGHT-HAND COLUMN — the author, 'Filed: …', 'Office of Appellate
Courts' — and fences its bands with TYPED UNDERSCORE RULES. The Court of
Appeals prints neither: over all 30 records there is not one underscore rule
and not one right-hand column. Everything above the appearances stands on the
PAGE AXIS, and the band is named by whether it is set BOLD.

    ┌────────────────────────────────────────────────────────────────────┐
    │                  STATE OF MINNESOTA          bold, on the axis     │
    │                  IN COURT OF APPEALS         the masthead PAIR     │
    │                       A25-1408               bold — the docket     │
    │                  State of Minnesota,                               │
    │                     Respondent,                                    │
    │                          vs.                 the caption, roman,   │
    │                Alexander Steven Jonas,       on the axis           │
    │                      Appellant.                                    │
    │                 Filed April 20, 2026         ─┐                    │
    │        Reversed and remanded; motion denied   │ THE BOLD RELEASE   │
    │                    Reyes, Judge              ─┘ (date/disp/author) │
    │               Anoka County District Court     the origin, roman    │
    │                 File No. 02-CR-22-21          on the axis          │
    │ Keith Ellison, Attorney General, …; and       the appearances, at  │
    │ Cathryn Middlebrook, … (for appellant)        the BODY RAIL        │
    │     Considered and decided by Reyes, Presiding Judge; Harris,       │
    │ Judge; and Jesson, Judge.*                    the roster, INDENTED │
    │                     SYLLABUS                  bold, on the axis    │
    │     When the court of appeals reverses a conviction and remands …   │
    │                     OPINION                   the paper NAMES      │
    └────────────────────────────────────────────────────────────────────┘

THE LANDMARKS, measured over all 30 records (25 distinct papers; five are
printed twice under two stems):

  masthead pair 'STATE OF MINNESOTA' / 'IN COURT OF APPEALS'   30 of 30
  a bold 'A\\d\\d-\\d{3,4}' docket                              30 of 30
  a bold row opening 'Filed '                                  30 of 30
  a bold row ending ', Judge' / ', Chief Judge'                30 of 30
  a roster opening 'Considered and decided by'                 30 of 30
  a bold 'SYLLABUS'                                            30 of 30
  a bold row ENDING in 'OPINION'                               30 of 30

BOLD IS THE BAND MARK, AND THE AXIS IS THE COLUMN. The court sets the
masthead, the docket, the release and the section headings bold and centred;
the caption and the origin roman and centred; the appearances at the body
rail. Nothing here is read by wording except the four landmarks above, each
of which is a phrase the court prints on every paper.

THE RELEASE IS ONE BAND OF THREE THINGS, and each is taken by its own test,
never by its position: the row that opens 'Filed ' is the date, a row that
ends in a BENCH WORD is an author, and whatever else the band holds is the
disposition. state_of_minnesota_v._todd_jeremy_thompson prints a FOURTH row
there — 'Concurring specially, Wheelock, Judge' — because Minnesota
announces a separate writing in the block rather than waiting for its byline;
that is an author row too, and reading the band by position would have made
it the disposition. wilmington_trust_…_v._700_hennepin runs its disposition
over TWO rows ('Reversed and remanded; motion to supplement denied' / 'and
motion to dismiss granted in part'), so the disposition is a RUN, not a row.

THE ROSTER IS INDENTED AND ITS WRAP IS NOT. 'Considered and decided by …'
starts at 100.8–108.0 and wraps back to the body rail at 72.0, which is also
where the appearances start — so the roster cannot be told from counsel by
column alone, and the phrase opens it while its own sentence closes it (the
merged text ends in a period, after 26 of 30 records wrap it onto a second
line).

THE SYLLABUS IS THE COURT'S OWN and takes the `syllabus` role, the same as
minn's and Kansas's. It is NOT `headnotes`: headnotes are the Reporter's
subject list, and the Reporter does not write these.
minnesota_nurses_association_v._mcleod_county numbers its points, and pdfio
splits '1.' from its text at the column gap — the row is read whole, so the
number stays with the point it numbers.

THE BLOCK SPANS PAGES. texa_tonka_shopping_center and wilmington_trust have
captions long enough to push the roster, the syllabus and 'OPINION' onto page
2; reading page 1 alone would have left the roster in the stream, where a row
naming three judges is exactly what opens a phantom writing.

THE PAPER NAMES ITSELF LAST, and that row ends the block. 29 of 30 print
'OPINION'; in_re_washington_county_…_v._erik_lawrence_bader prints 'SPECIAL
TERM OPINION'. The test is a bold row on the axis whose text ENDS in
'OPINION' — and if pages 1–3 hold no such row this is not this paper and the
reader returns NOTHING rather than guess where the writing starts.

PUBLICATION: all 30 print a SYLLABUS and none prints the nonprecedential
notice, so all 30 are `published`. The syllabus is the positive landmark —
Minnesota prints one only on a precedential opinion — and the notice, which
this corpus does not exercise, is tagged `publication` where it appears
rather than left as an unread row.
"""

from __future__ import annotations

import re

from .. import model as m
from ..resolve.evidence import NOTHING, Trace, decider
from ..resolve.footnotes import FootnoteZones, line_markup
from ..resolve.furniture import FurnitureFinder
from ..resolve.headmatter import roster_names

_MASTHEAD = "state of minnesota"
_COURT_ROW = re.compile(r"^IN COURT OF APPEALS$", re.I)
_AXIS_TOL = 8.0
_RAIL_TOL = 3.0
_MAX_PAGES = 3

# 'A25-1408' — one per row; in_the_marriage_of_sarah_nicole_smith prints two
# rows (A25-0258 over A25-0616), which is a consolidation, not a wrap.
_DOCKET = re.compile(r"^A\d{2}-\d{3,4}(?:\s*,\s*A\d{2}-\d{3,4})*$")
_SYLLABUS_HEAD = re.compile(r"^S\s*Y\s*L\s*L\s*A\s*B\s*U\s*S$", re.I)
# THE PAPER'S OWN NAME: 'OPINION' on 29 records, 'SPECIAL TERM OPINION' on
# in_re_washington_county. Matched at the END so a qualifier in front of it
# still names the paper.
_OPINION_HEAD = re.compile(
    r"^(?:[A-Z][A-Z ]*\s)?O\s*P\s*I\s*N\s*I\s*O\s*N$", re.I)
# THE RELEASE BAND's three tenants.
_FILED = re.compile(r"^(?:Filed|Refiled|Amended)\b", re.I)
# A BENCH WORD ENDS AN AUTHOR ROW. Closed vocabulary, and the only thing
# separating 'Smith, Tracy M., Judge' (a judge whose given name the court
# prints to tell two Smiths apart) from a disposition. 'Concurring
# specially, Wheelock, Judge' is an author row by the same test.
_AUTHOR = re.compile(
    r",\s*(?:Chief|Presiding|Senior|Acting)?\s*Judge\.?$", re.I)
# THE ORIGIN, by its own landmark rather than by any list of tribunals.
_FILE_NO = re.compile(r"^File\s+Nos?\.\s*(.+)$", re.I)
# THE ROSTER opens with a phrase the court prints on every paper.
_ROSTER = re.compile(r"^Considered and decided by\s+(.*)$", re.I)
# The roster's own titles, which core's `_ROSTER_TITLE` does not carry
# ('Presiding Judge' is not in it), stripped before the names are split.
_ROSTER_TITLE = re.compile(
    r",\s*(?:Chief|Presiding|Senior|Acting)?\s*Judges?\.?$", re.I)
# The caption's own furniture.
_PIVOT = re.compile(r"^(?:v\.?|vs\.?|and)$", re.I)
_PARTY_ROLE = re.compile(
    r"^(?:Appellant|Appellee|Respondent|Petitioner|Relator|Cross-Appellant"
    r"|Cross-Respondent|Plaintiff|Defendant|Intervenor)s?[,.]?$", re.I)
# …and the same vocabulary printed INSIDE a party row ('Mathew Paul Crow,
# petitioner,' / 'In re Washington County, Petitioner,').
_TRAILING_ROLE = re.compile(
    r",\s*(?:appellant|appellee|respondent|petitioner|relator|plaintiff"
    r"|defendant|intervenor)s?\s*[,.]?$", re.I)
# THE NONPRECEDENTIAL NOTICE. 0 of the 30 records print it — the corpus is
# all published opinions — but it is this court's other paper, and an
# unclaimed notice row is an unread row.
_NONPRECEDENTIAL = re.compile(
    r"nonprecedential|not precedential|Minn\. R\. Civ\. App\. P\. 136\.01",
    re.I)


def _norm(text: str) -> str:
    return " ".join(text.split())


@decider("headmatter.read", court="minnctapp")
def read_headmatter_minnctapp(model, geom, **_):
    """Read the Court of Appeals' block, or NOTHING."""
    if not model.pages:
        return NOTHING
    body_size = (geom.body_size if geom and geom.body_size else 13.0)
    body_x0 = (geom.body_x0 if geom and geom.body_x0 else 72.0)
    axis = model.pages[0].width / 2
    finder = FurnitureFinder(model, body_x0, body_size)
    cuts = _footnote_cuts(model, geom)

    rows = [g for pm in model.pages[:_MAX_PAGES]
            for g in _rows(pm, finder, cuts.get(pm.number, float("inf")))]
    if len(rows) < 8:
        return NOTHING

    # THE DISPATCH: the masthead PAIR, bold, on the axis, at the head of the
    # page. Nothing else in this court's paper prints those two rows.
    head = [_norm(" ".join(l.plain for l in g)) for g in rows[:2]]
    if len(head) < 2 or head[0].lower() != _MASTHEAD \
            or not _COURT_ROW.match(head[1]):
        return NOTHING

    # THE BLOCK ENDS WHERE THE PAPER NAMES ITSELF, and the reader will not
    # claim a line until it knows where that is. Found first, so the walk is
    # bounded by a printed row rather than by a page count.
    last = None
    for i, group in enumerate(rows):
        text = _norm(" ".join(l.plain for l in sorted(group, key=lambda l: l.x0)))
        if _OPINION_HEAD.match(text) and _bold(group) and _on_axis(group, axis):
            last = i
            break
    if last is None:
        return NOTHING

    ctx = _Ctx()
    band = "caption"       # caption | release | origin | counsel | syllabus
    caption: list[str] = []
    parties: list[str] = []
    disposition: list[str] = []
    counsel: list[str] = []
    roster: list[str] = []
    roster_ids: list = []
    pivot_at: int | None = None

    for group in rows[:last + 1]:
        pieces = sorted(group, key=lambda l: l.x0)
        text = _norm(" ".join(l.plain for l in pieces))
        if not text:
            continue
        bold = _bold(pieces)
        centred = _on_axis(pieces, axis)
        rail = abs(pieces[0].x0 - body_x0) <= _RAIL_TOL

        # --- the roster RUN closes on its own sentence -------------------
        if band == "roster":
            roster.append(text)
            roster_ids.extend(pieces)
            if text.rstrip().endswith((".", ".*", ".∗")):
                band = "post-roster"
            continue

        if _OPINION_HEAD.match(text) and bold and centred:
            ctx.crit.setdefault("title", text)
            ctx.emit(pieces, "title")
            break
        if text.lower() == _MASTHEAD or _COURT_ROW.match(text):
            ctx.crit.setdefault("court", text)
            ctx.emit(pieces, "court")
            continue
        if _NONPRECEDENTIAL.search(text):
            ctx.crit["publication_status"] = "unpublished"
            ctx.emit(pieces, "publication")
            continue
        if _DOCKET.match(text) and bold:
            for n, dk in enumerate(t.strip() for t in text.split(",")):
                if not dk:
                    continue
                if not ctx.crit.get("docket_number") and n == 0 \
                        and "docket_number" not in ctx.crit:
                    ctx.crit["docket_number"] = dk
                else:
                    ctx.crit.setdefault("other_dockets", []).append(dk)
            ctx.emit(pieces, "docket")
            continue
        if _SYLLABUS_HEAD.match(text) and bold and centred:
            # A HEADING THAT NAMES A SECTION belongs to that section.
            band = "syllabus"
            ctx.crit.setdefault("publication_status", "published")
            ctx.emit(pieces, "syllabus")
            continue
        if band == "syllabus":
            ctx.emit(pieces, "syllabus", centre=False)
            continue
        mr = _ROSTER.match(text)
        if mr:
            band = "roster"
            roster.append(text)
            roster_ids.extend(pieces)
            if text.rstrip().endswith((".", ".*", ".∗")):
                band = "post-roster"
            continue

        # --- the bold RELEASE band --------------------------------------
        if bold and centred and _FILED.match(text):
            band = "release"
            ctx.crit.setdefault(
                "decision_date",
                _norm(re.sub(r"^(?:Filed|Refiled|Amended)\b:?\s*", "", text,
                             flags=re.I)))
            ctx.emit(pieces, "date")
            continue
        if band == "release" and bold and centred:
            if _AUTHOR.search(text):
                ctx.emit(pieces, "author")
            else:
                disposition.append(text)
                ctx.emit(pieces, "disposition")
            continue

        # --- the roman ORIGIN band, on the axis ------------------------
        if band in ("release", "origin") and centred and not rail:
            band = "origin"
            mf = _FILE_NO.match(text)
            if mf:
                ctx.crit.setdefault("lower_court_docket", []).extend(
                    p.strip() for p in mf.group(1).split(",") if p.strip())
            else:
                ctx.crit.setdefault("lower_court", text)
            ctx.emit(pieces, "lower-court", centre=False)
            continue

        # --- the APPEARANCES, at the body rail --------------------------
        if band in ("origin", "counsel", "post-roster") and rail:
            band = "counsel"
            counsel.append(text)
            ctx.emit(pieces, "counsel", centre=False)
            continue

        # --- the CAPTION, roman, on the axis ----------------------------
        if band == "caption":
            caption.append(text)
            if _PIVOT.match(text):
                if text.lower() != "and" and pivot_at is None:
                    pivot_at = len(parties)
            elif not _PARTY_ROLE.match(text):
                parties.append(_norm(_TRAILING_ROLE.sub("", text).strip(" ,")))
            ctx.emit(pieces, "caption", centre=(centred and len(pieces) == 1))
            continue

        # A ROW THIS PAPER DOES NOT PRINT is left to core rather than
        # tinted with a role that would be a guess.
        return NOTHING

    # A CLAIM MUST BE TOTAL, and the roster is the one run held back for
    # merging — place it, printed form and parsed form together.
    if roster:
        printed = _norm(" ".join(roster))
        ctx.emit(roster_ids, "panel", centre=False, text=printed)
        ctx.crit["panel_line"] = printed
        said = _ROSTER.match(printed)
        if said:
            ctx.crit["judges"] = _norm(said.group(1))
            ctx.crit["panel"] = _panel(said.group(1))

    if not ctx.crit.get("docket_number") or not roster:
        return NOTHING
    if caption:
        ctx.crit["caption"] = caption
    if parties:
        ctx.crit["parties"] = parties
        if pivot_at is not None and 0 < pivot_at < len(parties):
            ctx.crit["case_name"] = \
                f"{parties[pivot_at - 1]} v. {parties[pivot_at]}"
        else:
            ctx.crit["case_name"] = _norm(" ".join(parties))
    if disposition:
        ctx.crit["disposition"] = _norm(" ".join(disposition))
    if counsel:
        ctx.crit["attorneys"] = _norm(" ".join(counsel))[:4000]
    ctx.crit["headmatter_style"] = "bold-band axis"
    return ctx.result()


def _panel(roster: str) -> list[str]:
    """The judges the roster names, one per entry.

    THE SEMICOLON IS THE COURT'S DELIMITER, not the comma: 'Ede, Presiding
    Judge; Smith, Tracy M., Judge; and Cochran, Judge.' is three judges, and
    the commas inside an entry separate a judge from his TITLE and (where
    the court has two Smiths) his surname from his given name. Core's
    `roster_names` splits on commas and 'and', so handed the whole row it
    returns 'Presiding Judge; Harris' as a judge — the semicolon split is
    done here and each entry then goes to core's splitter, which is what
    drops the titles it knows and keeps a generational suffix attached.
    """
    out: list[str] = []
    for entry in roster.split(";"):
        entry = _ROSTER_TITLE.sub("", entry.strip().removeprefix("and ").strip())
        entry = entry.strip(" ,.")
        if not entry:
            continue
        # The semicolon already separated the judges, so whatever core's
        # splitter finds inside ONE entry is one judge's printed name.
        got = roster_names(entry)
        out.append(", ".join(got) if got else entry)
    return out


def _bold(group: list) -> bool:
    return all(bool(l.all_bold) for l in group)


def _on_axis(group: list, axis: float) -> bool:
    x0 = min(l.x0 for l in group)
    x1 = max(l.x1 for l in group)
    return abs((x0 + x1) / 2 - axis) <= _AXIS_TOL


def _footnote_cuts(model, geom) -> dict:
    """Where core will put each page's footnote zone.

    The '∗ Retired judge of the Minnesota Court of Appeals, serving by
    appointment…' note stands at the FOOT of the caption page, below the
    syllabus, on 9 of the 30 records — inside the span this reader walks. It
    is a footnote, core reads it as one, and a reader that swept it into the
    syllabus would both mistag it and break the mark that calls it.
    Reconstructed from the profile exactly as the pipeline does at stage 6."""
    from . import get_profile
    from ..resolve.bylines import BylineParser
    profile = get_profile("minnctapp")
    parser = BylineParser(profile.byline)
    zones = FootnoteZones(model, geom, profile.footnotes, "minnctapp",
                          Trace(), is_byline=lambda t: bool(parser.parse(t)))
    cuts: dict = {}
    prev = False
    for pm in model.pages:
        value = zones.page_zone(pm, prev).value
        cuts[pm.number] = float("inf") if value is None else value
        prev = value is not None
    return cuts


def _rows(pm, finder, cut: float) -> list[list]:
    """One entry per printed row, its same-baseline pieces together, in the
    page's own order; furniture and the footnote zone removed."""
    groups: dict = {}
    order: list = []
    for line in sorted(pm.lines, key=lambda l: (l.top, l.x0)):
        if not line.plain.strip() or line.top >= cut:
            continue
        if finder.kind(pm, line):
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

    def emit(self, group: list, role: str, centre: bool = True,
             text: str | None = None) -> None:
        parts = sorted(group, key=lambda l: (l.page, l.top, l.x0))
        if not parts:
            return
        first = parts[0]
        if text is None:
            text = ""
            for part in parts:
                piece = line_markup(part)
                text = (text.rstrip() + " " + piece.lstrip()) \
                    if text.strip() else piece
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
