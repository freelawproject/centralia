"""United States Tax Court ('tax').

Everything unique to the Tax Court lives here. It imports core, never
another court file, and no other court file imports it.

The court prints ONE cover, and it is the most regular in the corpus:

    United States Tax Court          the banner, 20pt, on the page axis
    REVIEWED                         a printing flag (rare: REVIEWED,
                                     CORRECTED) — set BETWEEN banner and cite
    167 T.C. No. 6                   the SERIES CITATION the court cites
                                     itself by ('T.C. Memo. 2026-41',
                                     'T.C. Summary Opinion 2026-5')
    HBM HOLDINGS COMPANY,            the caption: party…
                Petitioner           …its status…
                    v.               …the pivot…
    COMMISSIONER OF INTERNAL REVENUE, …and the Commissioner, always
                Respondent
              ——————               a FENCE
    Docket Nos. 19735-23, 3881-24.   the docket, at the rail…
                Filed July 27, 2026. …and the filing date, flush right,
                                     on the SAME baseline
              ——————               …and the fence that closes it
    P is the parent of a consolidated group. …   the SYLLABUS (reported
    Held: DRE is a predecessor to P …            opinions only), inset 36pt
              ——————               …and the fence that closes IT
    David D. Aughtry, … for petitioner.   the appearances, at the rail
    Laura L. Bates, … for respondent.
    OPINION                          the paper's name — the WRITING's, not
    JENKINS, Judge: Both parties …   the headmatter's. The reader stops here.

STYLE 'axis fences' — the court types a rule of ONE measure, 60pt, centred
on the page axis, and it uses that rule for every zone mark on the cover.
Two of them always bracket the docket band; a third closes the syllabus
where there is one. The rule is typed with underscores on some printings
and with em dashes on others (both forms occur inside a single record —
charmaine_a._gray opens the band with '__________' and closes it with
'—————'), so the GLYPH says nothing and the MEASURE and the AXIS say
everything.

Three zones are read by position between the fences, not by wording:

  * ABOVE the first fence — the banner, then anything before the series
    citation is a printing flag, then the caption;
  * BETWEEN the first two fences — the docket and the filing date;
  * BELOW the second fence — the SYLLABUS if the band opens inset from the
    rail (144pt against a 108pt rail), otherwise the APPEARANCES, which are
    set AT the rail. A syllabus is closed by its own fence and the
    appearances follow it.

The appearances end at the first row that leaves the rail: the court's own
name for the paper ('MEMORANDUM OPINION', 'SUMMARY OPINION', 'OPINION',
'MEMORANDUM FINDINGS OF FACT AND OPINION') is centred, and it is the
WRITING's opening heading — the reader reads it into `title` and leaves the
row in the stream, because it is the only thing the writing can anchor on.

THE SERIES DESIGNATION IS A CITATION, NOT A DOCKET. 'T.C. Memo. 2026-41' is
how the court cites this opinion; 'Docket No. 18451-23L' is the case's
number in this court. They are recorded as `citation` and `docket_number`
respectively (ill was fixed for exactly this confusion).

FURNITURE: the clerk stamps 'Served 05/19/26' at the foot of page 1, in
14pt bold on the page axis, below every other row on the page. It is not
repeated, so the shared furniture pass never sees it, and left behind it
renders as a heading in the middle of the opinion (bryan_edward_menge) or
inside the headmatter (hbm_holdings_company). It is claimed and recorded.

A page-1 FOOTNOTE (the consolidation note the 'ET AL.' caption carries) is
set two points smaller than the body and is already lifted by the shared
footnote pass; the reader steps over anything below the body size rather
than claiming it twice.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar, BylineParser
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import FurnitureFinder
from ..pdfio.rules import is_typed_rule
from . import register

TAX = register(CourtProfile(
    "tax", "United States Tax Court",
    # The court signs 'KERRIGAN, Judge:' — a CAPS surname, a spelled title
    # and a COLON, with the opinion's first sentence running on from it.
    # Its trial bench sits under four designations, and all four have to be
    # declared: without them 'PANUTHOS, Special Trial Judge:' parses as
    # nothing and a signed opinion is typed 'order'.
    byline=BylineGrammar(style="prose",
                         titles=("Judge", "Chief Judge",
                                 "Special Trial Judge",
                                 "Chief Special Trial Judge",
                                 "Senior Judge")),
))

STYLE_AXIS_FENCES = "axis fences"

# ---- the court's declared facts (measured over all 32 records) -----------
# THE FENCE. One measure, 60.0pt on every record, centred on the page axis
# (x0=276, x1=336 on a 612pt page). The window is generous on either side
# because the court has no other axis rule to confuse it with.
_FENCE_WIDTH = (44.0, 80.0)
_FENCE_AXIS = 8.0
# The body rail and the syllabus's own measure. The syllabus is inset 36pt
# from the rail on both sides (144–468 against 108–504) and indents its
# first line another 36pt; the appearances are set AT the rail.
_RAIL = 108.0
_SYLLABUS_INSET = 36.0
# How far off the page axis a centred cover row may sit. Every caption row,
# the banner, the citation and the printing flag are centred to within a
# point of the axis; the shared alignment test reads the widest of them
# (BIG APPLE TOMPKINS REALTY LLC …, 368pt of a 396pt measure) as justified
# prose and left-aligns it.
_CENTRE_TOL = 8.0
# The clerk's service stamp: 14pt bold, on the axis, in the bottom band.
_STAMP_BAND = 0.90                     # of the page height (747.5 of 792)
# How many pages the cover may run to. The longest (peter_f._mcdougall_donor,
# two captions and a nine-paragraph syllabus) fills two; four is slack, and
# the fences stop the reader, not the count.
_MAX_PAGES = 4

# THE SERIES CITATION, in the court's three forms. Anchored on 'T.C.',
# which is the court's own abbreviation of itself and not a case word.
_CITATION = re.compile(
    r"^(?:\d{1,3}\s+T\.\s?C\.\s+No\.\s+\d+"
    r"|T\.\s?C\.\s+Memo\.\s+\d{4}-\d+"
    r"|T\.\s?C\.\s+Summary\s+Opinion\s+\d{4}-\d+)\.?$", re.I)
# The docket band. The court numbers its cases NNNNN-YY with an optional
# letter suffix naming the proceeding (L lien/levy, S small case,
# W whistleblower, P passport, X, R, D).
_DOCKET_NO = re.compile(r"\b(\d{1,5}-\d{2}[A-Z]?)\b")
_DOCKET_HEAD = re.compile(r"^Docket\s+Nos?\.", re.I)
_FILED = re.compile(r"^\s*Filed\s+(.+?)\s*\.?$", re.I)
# THE REPORTER'S STAR PAGE. Every page after the first opens with '[*14]'.
# Where the page opens with prose the marker leads that line and is part of
# it; where it opens with a syllabus paragraph it stands alone in the left
# margin, a whole column clear of the text, and it is pagination, not the
# court's words.
_STAR_PAGE = re.compile(r"^\[\*\d+\]$")
# PARTY STATUS is a closed role vocabulary; a party NAME is never read by
# wording. The court prints exactly these five.
_STATUS = ("petitioner", "petitioners", "petitioner(s)",
           "respondent", "respondents")
_PIVOT = ("v.", "v", "vs.", "versus")
# How an appearance closes. A closed vocabulary of the court's own four
# tails — every appearance in the corpus ends on one of them.
_APPEARANCE_TAIL = re.compile(
    r"(?:pro\s+se|pro\s+sese|for\s+(?:the\s+)?"
    r"(?:petitioner|petitioners|petitioner\(s\)|respondent|respondents|"
    r"amicus\s+curiae|intervenor|intervenors))\s*\.$", re.I)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _plain(text: str) -> str:
    return _norm(re.sub(r"<[^>]+>", "", text or ""))


def _bare(text: str) -> str:
    """The row's text without a trailing footnote mark or punctuation."""
    return _plain(text).rstrip(".,;: ").rstrip("*†‡0123456789").rstrip(".,;: ")


def _is_banner(text: str) -> bool:
    return _plain(text).lower().rstrip(".") == "united states tax court"


def _is_status(text: str) -> bool:
    return _bare(text).lower() in _STATUS


def _is_pivot(text: str) -> bool:
    return _plain(text).strip().lower().rstrip(".") in ("v", "vs", "versus")


def _fences(model) -> dict:
    """{page: [tops]} — where the court types its 60pt axis rule."""
    out: dict = {}
    for pm in model.pages:
        axis = (pm.width or 612.0) / 2
        tops = []
        for line in pm.lines:
            flat = line.plain.strip()
            if not flat or not is_typed_rule(flat):
                continue
            if abs((line.x0 + line.x1) / 2 - axis) > _FENCE_AXIS:
                continue
            if not (_FENCE_WIDTH[0] <= line.x1 - line.x0 <= _FENCE_WIDTH[1]):
                continue
            tops.append(line.top)
        if tops:
            out[pm.number] = sorted(tops)
    return out


# A FOOTNOTE MARK ON A CAPTION ROW rides on the row's own punctuation
# ('BEVELED EDGE INSURANCE COMPANY, INC., ET AL.,1'). Only a digit that
# FOLLOWS a stop is a mark — a party name may itself end in a number
# ('SOUTH FULTON PARKWAY 58, LLC, SOUTH FULTON 58').
_CAPTION_MARK = re.compile(r"(?<=[.,])\d{1,2}$")


def _party_name(text: str) -> str:
    """A caption row as a NAME: its mark and its trailing comma removed, its
    own full stop kept ('HOUGH BECK & BAIRD, INC.')."""
    return _CAPTION_MARK.sub("", _plain(text)).rstrip(", ")


def _sides(rows: list) -> tuple | None:
    """The party names either side of the pivot, built from the NAMES only.

    A status label and the pivot are apparatus. The court prints one
    caption group per consolidated case; only the first names the parties
    of the lead case."""
    left: list = []
    right: list = []
    side = left
    seen = False
    for row in rows:
        flat = _plain(row)
        if _is_pivot(flat):
            side = right
            seen = True
            continue
        if _is_status(flat):
            continue
        side.append(_party_name(flat))
    if not (left and right and seen):
        return None
    return (_party_name(" ".join(left)), _party_name(" ".join(right)))


@decider("headmatter.read", court="tax")
def read_headmatter_tax(model, geom, **_):
    """Read the Tax Court's axis-fenced cover, or NOTHING.

    NOTHING is returned for anything that is not the contract above: core's
    shared walk places those rows unidentified, which is a smaller error
    than a confident misreading."""
    if not model.pages:
        return NOTHING
    fences = _fences(model)
    if len(fences.get(1, ())) < 2:
        return NOTHING             # no docket band: not this contract

    from ..resolve.footnotes import line_markup

    body_x0 = geom.body_x0 if geom else _RAIL
    body_size = geom.body_size if geom else 12.0
    finder = FurnitureFinder(model, body_x0, body_size)
    parser = BylineParser(TAX.byline)
    pages_by_no = {pm.number: pm for pm in model.pages}

    # ---- the rows of the cover, in page order ---------------------------
    rows: list = []                        # (page, top, line)
    stamps: list = []
    for pm in model.pages[:_MAX_PAGES]:
        height = pm.height or 792.0
        for line in pm.lines:
            if not line.plain.strip():
                continue
            if finder.kind(pm, line):
                continue                   # the folio and the running head
            # THE CLERK'S SERVICE STAMP: 14pt bold on the axis, in the
            # bottom band of the page, below the court's own last row. Not
            # repeated across pages, so the shared furniture pass never
            # sees it; claimed here so that it is RECORDED rather than read
            # as a heading inside the opinion.
            if (line.top >= height * _STAMP_BAND
                    and (line.size or 0.0) > body_size
                    and line.all_bold
                    and abs((line.x0 + line.x1) / 2
                            - (pm.width or 612.0) / 2) <= 25.0):
                stamps.append(line)
                continue
            # A NOTE IS NOT THE COVER. The consolidation footnote an
            # 'ET AL.' caption carries is set two points down and has
            # already been lifted by the shared footnote pass.
            if (line.size or 0.0) < body_size - 1.0:
                continue
            rows.append((pm.number, line.top, line))
    rows.sort(key=lambda r: (r[0], r[1]))
    if not rows:
        return NOTHING
    if not _is_banner(rows[0][2].plain):
        return NOTHING                     # the court always names itself

    # ---- emit ------------------------------------------------------------
    crit: dict = {"headmatter_style": STYLE_AXIS_FENCES}
    items: list = []
    consumed: set[int] = set()
    dropped: list = []
    caption_rows: list[str] = []
    groups: list[list[str]] = []           # one per consolidated caption
    counsel_rows: list[str] = []
    dockets: list[str] = []
    flags: list[str] = []
    saw_counsel = False
    title_line = None

    def emit(line, role: str, align: str, rel: float = 0.0):
        items.append(m.HmLine(
            text=_norm(line_markup(line)), prov=m.Prov(line.page, (line.id,)),
            align=m.Align(align), x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), rel=rel, role=role))
        consumed.add(line.id)

    def centred(line) -> bool:
        pm = pages_by_no[line.page]
        return abs((line.x0 + line.x1) / 2
                   - (pm.width or 612.0) / 2) <= _CENTRE_TOL

    # Bands are counted by the fences the row has passed. Band 0 is the
    # masthead and caption, band 1 the docket, band 2 the syllabus or the
    # appearances, band 3 the appearances after a syllabus.
    def band_of(page: int, top: float) -> int:
        n = 0
        for pg in sorted(fences):
            if pg > page:
                break
            for t in fences[pg]:
                if pg < page or t < top:
                    n += 1
        return n

    seen_citation = False
    syllabus_band = None
    stop = False
    for page, top, line in rows:
        if stop:
            break
        band = band_of(page, top)
        flat = _plain(line.plain)
        if _STAR_PAGE.match(flat):
            dropped.append(m.Dropped(text=flat,
                                     prov=m.Prov(line.page, (line.id,)),
                                     kind="folio"))
            consumed.add(line.id)
            continue
        # THE FENCE ITSELF RENDERS — it is the court's own section mark, not
        # furniture. Its line is claimed where it stands.
        if is_typed_rule(line.plain.strip()) and centred(line):
            consumed.add(line.id)
            items.append(m.Rule(prov=m.Prov(line.page, (line.id,)),
                                typed=True, span="full"))
            continue
        if band == 0:
            if _is_banner(flat):
                crit.setdefault("court", flat.rstrip("."))
                emit(line, "court", "C")
                continue
            if not seen_citation and _CITATION.match(flat):
                seen_citation = True
                crit["citation"] = flat.rstrip(".")
                emit(line, "citation", "C")
                continue
            if not seen_citation:
                # A PRINTING FLAG. Whatever the court sets between its own
                # name and its own citation is what it is saying about THIS
                # printing of the paper ('REVIEWED' — decided by the full
                # Court; 'CORRECTED'). Read by position, never by wording.
                flags.append(flat)
                emit(line, "case-info", "C")
                continue
            # THE CAPTION. Everything under the citation and above the first
            # fence is caption, whatever it looks like: the pivot says
            # nothing for itself and a wrapped party name looks like prose.
            caption_rows.append(flat)
            if not groups:
                groups.append([])
            groups[-1].append(flat)
            # A consolidated cover repeats the whole caption; the
            # respondent's status row closes each group.
            if _bare(flat).lower() in ("respondent", "respondents"):
                groups.append([])
            emit(line, "caption", "C" if centred(line) else "L")
            continue
        if band == 1:
            if _FILED.match(flat) or _plain(flat).lower().startswith("filed "):
                hit = _FILED.match(flat)
                if hit:
                    crit.setdefault("decision_date", _norm(hit.group(1)))
                emit(line, "date", "R")
                continue
            dockets.extend(_DOCKET_NO.findall(flat))
            emit(line, "docket", "L")
            continue
        # ---- band 2 and beyond: the syllabus, then the appearances -------
        if syllabus_band is None and not saw_counsel:
            # THE BAND'S OWN MEASURE NAMES IT. A syllabus is inset from the
            # rail; the appearances are set at it.
            syllabus_band = band if line.x0 >= body_x0 + _SYLLABUS_INSET / 2 \
                else -1
        if band == syllabus_band:
            # THE COURT WRITES THIS BLOCK ITSELF — a factual recital and
            # then its numbered holdings ('Held:', 'Held, further:'). That
            # is a SYLLABUS, not a reporter's headnote list and not a
            # précis somebody else wrote.
            emit(line, "syllabus", "L", rel=max(line.x0 - body_x0, 0.0))
            continue
        # THE APPEARANCES, at the rail. The band ends at the first row that
        # leaves it — the court's name for the paper, centred, which opens
        # the writing and is left in the stream for it to anchor on.
        if line.x0 <= body_x0 + 2.0:
            saw_counsel = True
            counsel_rows.append(flat)
            emit(line, "counsel", "L")
            continue
        title_line = line
        stop = True

    if not saw_counsel:
        return NOTHING                     # every cover prints appearances

    # ---- criteria --------------------------------------------------------
    if flags:
        crit["history"] = _norm(" ".join(flags))
    if caption_rows:
        crit["caption"] = caption_rows
        lead = next((g for g in groups if g), caption_rows)
        sides = _sides(lead)
        if sides:
            crit["parties"] = list(sides)
            crit["case_name"] = f"{sides[0]} v. {sides[1]}"
    if dockets:
        crit["docket_number"] = dockets[0]
        if len(dockets) > 1:
            crit["other_dockets"] = dockets[1:]
    if counsel_rows:
        crit["attorneys"] = _norm(" ".join(counsel_rows))[:2000]

    # THE PAPER'S NAME, read but NOT claimed: it is the writing's opening
    # heading and the only thing an assembly can anchor the opinion on.
    doc_type_final = None
    if title_line is not None:
        name = _plain(title_line.plain)
        if name.isupper() and len(name) <= 80:
            crit["title"] = name
            nxt = next((l for _p, _t, l in rows
                        if l.id not in consumed and l.id != title_line.id),
                       None)
            if nxt is not None and parser.parse(_plain(nxt.plain)):
                doc_type_final = m.DocType.OPINION

    # ---- the clerk's stamp: recorded, not rendered -----------------------
    for line in stamps:
        dropped.append(m.Dropped(text=_plain(line.plain),
                                 prov=m.Prov(line.page, (line.id,)),
                                 kind="stamp"))
        consumed.add(line.id)

    return {"criteria": crit, "items": items, "attorneys": [],
            "dropped": dropped, "consumed": consumed, "anchor_ids": [],
            "doc_type_final": doc_type_final}
