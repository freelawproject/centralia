"""Supreme Court of the United States — profile and its own decisions.

Everything unique to scotus lives here. This file registers scotus's declared
FACTS and answers the named decision points where the Court's typesetting is
the truth. It imports core; it never imports another court file, and no other
court file imports it — so nothing here can affect, or be affected by, any
other court.

What makes scotus its own case: the Court NAMES the section in the running
head of every page ('Syllabus', 'Opinion of the Court', a Justice's name for
each separate writing). Section extent is therefore READ off the page, not
inferred from prose — and the cover repeats the caption apparatus that the
opinion prints again at its own head, so the cover's copy is superfluous.
"""

from __future__ import annotations

import re

from .. import model as m
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.furniture import head_band_rows
from ..resolve.headmatter import (_hm_line, _is_banner_row, _is_origin_row,
                                  looks_like_docket)
from . import register

register(CourtProfile(
    "scotus", "Supreme Court of the United States",
    byline=BylineGrammar(style="reversed",
                         rev_titles=("JUSTICE", "CHIEF JUSTICE")),
    # The Reporter's syllabus is part of the official report.
    front_matter=("syllabus",),
    # Body 156.2, paragraph indent 167.2, block quotation 178.3 — and in the
    # syllabus, runovers 165.2 against a 174.2 indent. Quotations are set at
    # BODY size on the BODY lead, so nothing but the indent separates a
    # quotation from prose; 2x this is the fence that keeps one out of the
    # other.
    para_indent_min=8.0,
    # 'KALEY CHILES, PETITIONER v. PATTY SALAZAR, IN' / 'HER OFFICIAL
    # CAPACITY AS EXECUTIVE DIRECTOR' / 'OF THE COLORADO DEPARTMENT OF' /
    # 'REGULATORY AGENCIES, ET AL.' is ONE party statement set over four
    # lines; rendered row by row it comes out ragged, and read row by row it
    # yields no parties and half a lower court.
    caption_wraps=True,
))


def _norm(text: str) -> str:
    return " ".join(text.split())


# --------------------------------------------------------------------------
# syllabus.pages — the running head names the section
# --------------------------------------------------------------------------

@decider("syllabus.pages", court="scotus")
def syllabus_pages(model, geom, **_):
    """Pages whose head band reads 'Syllabus'.

    Every page carries two head rows at fixed tops: the folio row (case name
    or 'Cite as: …' plus the page number) and, below it, the SECTION NAME.
    The syllabus is exactly the run of pages whose section name is
    'Syllabus'; it ends at the first page naming a writing ('Opinion of the
    Court'), which is where the opinion prints its own headmatter.

    The head band is taken from core's positional measurement, not a fixed
    coordinate: `head_band_rows` learns the tops where sub-body heads repeat.
    The cover's centered 'Syllabus' TITLE sits below that band and is not a
    membership signal — it marks where the syllabus content begins, and the
    rows above it are the cover's apparatus (see `syllabus_trim`).
    """
    body = geom.body_size if geom else 11.0
    rows = head_band_rows(model, body)
    if not rows:
        # A one-page order prints no repeated head — core decides.
        return NOTHING
    return _syllabus_page_numbers(model, geom, rows) or NOTHING


# --------------------------------------------------------------------------
# syllabus.trim — the cover's caption is printed twice
# --------------------------------------------------------------------------

def _seg_text(seg) -> str:
    return _norm(" ".join(line.plain for line in seg.lines))


@decider("syllabus.trim", court="scotus")
def syllabus_trim(segs, syl_pages, **_):
    """The cover's caption block — dropped, because the opinion reprints it.

    Under the banner the cover sets the 'Syllabus' title, the case name, the
    court appealed from and the docket-and-dates row; then the syllabus prose
    begins. The first page of each WRITING prints that same caption again,
    and prints it fuller: party status ('AHMAD ABOUAMMO, PETITIONER'), the
    docket fenced in its own rules, the decision date. Rendering both states
    the caption twice.

    The block is taken as a RUN — every row from the banner down to the
    docket-and-dates row — rather than row by row, because the rows wrap
    ('CERTIORARI TO THE UNITED STATES COURT OF APPEALS FOR' / 'THE NINTH
    CIRCUIT') and a per-row test drops one half and keeps the other. Core
    still mines the run for criteria: the argued date is printed only here.
    """
    if not syl_pages:
        return NOTHING
    cover = min(syl_pages)
    rows = [seg for seg in segs if seg.page == cover]
    banner = next((seg for seg in rows if _is_banner_row(_seg_text(seg))),
                  None)
    if banner is None:
        return NOTHING
    top = min(line.top for line in banner.lines)
    docket = next((seg for seg in rows
                   if min(line.top for line in seg.lines) > top
                   and looks_like_docket(_seg_text(seg))), None)
    if docket is None:
        return NOTHING
    bottom = max(line.top for line in docket.lines)
    drop = {id(seg) for seg in rows
            if top <= min(line.top for line in seg.lines) <= bottom}
    return drop or NOTHING


# --------------------------------------------------------------------------
# headmatter.parties — the caption is CAPS, and the pivot is its one hinge
# --------------------------------------------------------------------------
# Ported from the old engine's `_is_caption_row` / `_opens_next_party`: a
# caption row is set entirely in caps, and the single lower-case thing it
# contains is the 'v.' pivot — so removing the pivot and testing for caps
# identifies caption rows without a phrase list. A side that names itself
# CLOSES on its status ('SHAWN MONTGOMERY, PETITIONER'); a bare status row is
# the continuation of the party above it, never a new party.

_BRACKET_DATE = re.compile(r"^\[[^\]]*\d{4}\]$")

_PARTY_STATUS_END = (
    "petitioner", "petitioners", "respondent", "respondents",
    "appellant", "appellants", "appellee", "appellees",
    "applicant", "applicants", "plaintiff", "plaintiffs",
    "defendant", "defendants", "movant", "movants",
)


def _is_caption_row(text: str) -> bool:
    """Caps but for the pivot — the caption's own typesetting."""
    kept = [tok for tok in text.split()
            if tok.strip(".,").lower() not in ("v", "vs")]
    return bool(kept) and not any(c.islower() for c in " ".join(kept))


@decider("headmatter.parties", court="scotus")
def headmatter_parties(rows, **_):
    """The two sides, read off the caption rows.

    The caption WRAPS at the measure ('CISCO SYSTEMS, INC., ET AL.,
    PETITIONERS v.' / 'DOE I, ET AL.'), so no single row carries both sides
    and a row-at-a-time reader finds no pivot at all. Join the caption rows,
    split once at the pivot, and drop each side's closing status word — the
    status names the side's ROLE, not the party.
    """
    # The banner, the docket, the proceeding ('ON WRIT OF CERTIORARI…',
    # 'ON APPLICATION FOR STAY') and the bracketed date are all set in caps
    # too — caps alone is not the caption. Keep the RUN that carries the
    # pivot, and let any apparatus row end it: a consolidated cover stacks
    # one caption per docket, and the sides of the first are the case's.
    def _apparatus(t: str) -> bool:
        low = t.lower()
        return (_is_banner_row(t) or _is_origin_row(t)
                or low.startswith("on ")
                or bool(looks_like_docket(t))
                or bool(_BRACKET_DATE.match(t)))

    run: list[str] = []
    for r in rows:
        r = _norm(r)
        if not r:
            continue
        if _apparatus(r) or not _is_caption_row(r):
            if any(re.search(r"\bv[s]?\.?\b", x, re.I) for x in run):
                break
            run = []
            continue
        run.append(r)
    if not run:
        return NOTHING
    joined = _norm(" ".join(run))
    for pivot in (" v. ", " V. ", " vs. ", " v ", " V "):
        if pivot in joined:
            left, _, right = joined.partition(pivot)
            out = []
            for side in (left, right):
                words = side.strip().rstrip(",. ").split()
                while words and words[-1].strip(",.").lower() \
                        in _PARTY_STATUS_END:
                    words.pop()
                    while words and words[-1].strip(".,").upper() in (
                            "ET", "AL", "ET AL"):
                        words.pop()
                if words:
                    out.append(" ".join(words).rstrip(",. "))
            if len(out) == 2:
                return out
    return NOTHING


# --------------------------------------------------------------------------
# headmatter.read — the writing's own cover, row by row
# --------------------------------------------------------------------------
#
# Every separate writing opens on a fresh page and reprints the same seven
# things in the same order:
#
#     Cite as: 608 U. S. ____ (2026)      1   the running head and the folio
#     Opinion of the Court                    …and the SECTION NAME
#     NOTICE: This opinion is subject to …    the publisher's notice, 7pt
#     SUPREME COURT OF THE UNITED STATES      the banner, 15pt
#     _________________                       a typed rule, 6pt
#     No. 25–5146                             the docket, fenced by rules
#     _________________
#     AHMAD ABOUAMMO, PETITIONER v.           the caption, 11pt, WRAPPING
#     UNITED STATES
#     ON WRIT OF CERTIORARI TO THE UNITED …   where it came from, 9pt
#     APPEALS FOR THE NINTH CIRCUIT
#     [June 11, 2026]                         the decision date, in brackets
#     JUSTICE KAGAN delivered the opinion …   the byline — the writing begins
#
# The document's headmatter is the FIRST such cover; the covers below it
# belong to the writings they open and are never reached, because the run
# ends at the first row that is not apparatus.
#
# WRAP OR NEW ELEMENT IS MEASURABLE, and the measurement is the same one
# core makes for `caption_wraps`: a runover follows its first line by about
# 1.22x the type size, while the next element stands off by ~1.9x. Rows are
# merged on that fact rather than on wording, which is why 'KALEY CHILES,
# PETITIONER v. PATTY SALAZAR, IN' / 'HER OFFICIAL CAPACITY AS EXECUTIVE
# DIRECTOR' / 'OF THE COLORADO DEPARTMENT OF' / 'REGULATORY AGENCIES, ET
# AL.' comes back as one party statement and not four ragged rows.
_WRAP_LEAD = 1.5          # x the type size — above this a new element opens

# The typed rules the Court fences its docket with are underscores, printed
# at 6pt. They are furniture with a shape, not text.
_TYPED_RULE = re.compile(r"^[_\u2014\u2013-]{3,}$")

# The proceeding under review, in the forms the Court prints it: a merits
# opinion says 'ON WRIT OF CERTIORARI TO …', an order 'ON APPLICATION FOR
# STAY', a syllabus cover 'CERTIORARI TO …'. This is a CLOSED vocabulary of
# openers, never a court-name test.
_ORIGIN_OPENERS = ("on writ of certiorari", "on petition for", "on appeal",
                   "on appeals", "on application", "on motion",
                   "on writs of certiorari", "certiorari to", "appeal from",
                   "appeals from", "on request for", "on the application")


def _welds(head: str, tail: str, vocab: set) -> bool:
    """Does the hyphen at the end of ``head`` close a word broken at the
    measure? Only the document's own word list can say."""
    from ..audit import strip_tags, unescape_xml
    left = unescape_xml(strip_tags(head)).rstrip()[:-1]
    right = unescape_xml(strip_tags(tail)).lstrip()
    a = "".join(c for c in reversed(left) if c.isalpha() or c in "\u2019'")
    b = right.split()[0] if right.split() else ""
    b = b.strip("\u201c\u201d\"'\u2019\u2018()[]{}.,;:!?")
    if not a or not b:
        return False
    left_word = "".join(reversed(a))
    if (left_word + b).lower() in vocab:
        return True                      # printed unbroken somewhere
    # …and where the document says nothing either way, the CAPTION's own
    # setting decides: it is one statement broken at the measure, so a
    # hyphen at the end of a row is a break unless the document prints that
    # compound WITH its hyphen ('natural-born' survives; 'DE-' / 'PARTMENT'
    # does not, and this short per curiam never prints 'department' again).
    return f"{left_word}-{b}".lower() not in vocab


def _is_origin_opener(text: str) -> bool:
    low = text.lower()
    return any(low.startswith(o) for o in _ORIGIN_OPENERS)


# THE BANNER IS THE LARGEST TYPE ON THE PAGE — 15pt against an 11pt body,
# and nothing else on the cover comes near it. Core's worded test counts
# COURT WORDS, which on this cover also describes the notice's own address
# line ('pio@supremecourt.gov, of any typographical or other formal errors.')
# and the origin's runover ('APPEALS FOR THE NINTH CIRCUIT'); starting the
# walk on either of those read the notice as the masthead. Geometry decides.
_BANNER_OVER_BODY = 2.5           # points the masthead stands above the body


def _is_slip_banner(line, geom) -> bool:
    body = (geom.body_size if geom else 11.0) or 11.0
    text = _norm(line.plain)
    return ((line.size or 0.0) >= body + _BANNER_OVER_BODY
            and bool(text) and not any(c.islower() for c in text))


# 'No. 25–848. Decided June 15, 2026' states the docket AND the date in one
# row; the docket is what stands before the date label.
_DOCKET_HEAD = re.compile(r"\s+(?=(?:Argued|Reargued|Submitted|Decided|"
                          r"Filed)\b)")


def _docket_head(text: str) -> str:
    head = _DOCKET_HEAD.split(text, 1)[0].strip()
    # 'No. 25–848.' closes on the sentence period, 'No. 162, Orig.' on an
    # abbreviation — only the first is punctuation to drop.
    if head.endswith(".") and head[:-1].strip()[-1:].isdigit():
        head = head[:-1].strip()
    return head


# The head band is where the running head prints; the section name sits on
# the row under it. A page that turns a footnote may push that row down a
# line (chiles sets it at 152.1 where its neighbours set it at 139.2), which
# is below the repeated band core measures but plainly still the top of the
# page. The band gives the usual row; the TOP FIFTH of the page gives the
# rest, and no section name is ever set below it.
_TOP_BAND = 0.22          # of the page height


def _syllabus_page_numbers(model, geom, rows=None) -> set:
    """The pages whose head names the section 'Syllabus'.

    The same measurement `syllabus.pages` makes, factored out because the
    reader runs BEFORE core computes the syllabus span — and the reader must
    not touch those pages: their cover is the syllabus's, and `syllabus.trim`
    already answers for it.
    """
    if rows is None:
        rows = head_band_rows(model, geom.body_size if geom else 11.0)
    pages = set()
    for pm in model.pages:
        band = (pm.height or 792.0) * _TOP_BAND
        for line in pm.lines:
            if (round(line.top) in rows or line.top <= band) \
                    and _norm(line.plain).lower().rstrip(" :") == "syllabus":
                pages.add(pm.number)
                break
    return pages


@decider("headmatter.read", court="scotus")
def read_headmatter_scotus(model, geom, **_):
    """The first writing's cover, read as the apparatus it is.

    The claim is deliberately NARROW: it begins at the banner and ends at the
    first row that is not one of the things the cover prints. Everything
    above the banner — the running head, the folio, the publisher's notice —
    is left to core, which already measures and drops it, and a row this
    reader does not recognize is left to core's shared walk rather than
    guessed at. A claim that is not total is not a claim.
    """
    if not model.pages:
        return NOTHING
    syl = _syllabus_page_numbers(model, geom)
    cover = None
    for pm in model.pages:
        if pm.number in syl:
            continue
        if any(_is_slip_banner(l, geom) for l in pm.lines):
            cover = pm
            break
    if cover is None:
        return NOTHING

    lines = sorted((l for l in cover.lines if l.plain.strip()),
                   key=lambda l: (l.top, l.x0))
    start = next((i for i, l in enumerate(lines)
                  if _is_slip_banner(l, geom)), None)
    if start is None:
        return NOTHING

    from ..geometry import learn_vocabulary
    vocab = learn_vocabulary(model)

    crit: dict = {"headmatter_style": "slip-cover"}
    items: list = []
    consumed: set = set()
    dropped: list = []
    # the row a runover may still join, and what it was read as
    last: tuple | None = None       # (Line, HmLine, role)

    def _emit(line, role: str):
        item = _hm_line(line, cover, geom, indent_rel=True)
        item.role = role
        items.append(item)
        consumed.add(line.id)
        return item

    def _wraps(line, role: str) -> bool:
        """Is this row the runover of the row above it? The court's own
        measure decides — same type size, and no further below it than 1.5x
        that size. A statement set over THREE rows measures each gap from
        the row it actually follows, so the comparison advances with every
        merge; measured from the first row throughout, the third row of
        'ON PETITION FOR A WRIT OF CERTIORARI BEFORE JUDGMENT' / 'TO THE
        UNITED STATES COURT OF APPEALS FOR THE' / 'ELEVENTH CIRCUIT' stands
        2.4x out and reads as a new element.
        A gap of ZERO is the same visual row split at a wide space (a
        consolidated caption sets its docket cell beside the pivot).
        """
        if last is None or last[2] != role:
            return False
        prev = last[0]
        return (abs((line.size or 0.0) - (prev.size or 0.0)) <= 0.4
                and 0 <= line.top - prev.top
                <= _WRAP_LEAD * (line.size or 11.0))

    def _merge(line, item):
        """A runover merges its TEXT and its PROVENANCE both — a line whose
        id is dropped from the row it joined is consumed and unplaced, and
        comes back as residual content.

        A row broken ON A HYPHEN is one word split at the measure ('ALABAMA
        DE-' / 'PARTMENT OF CORRECTIONS'), and the DOCUMENT'S OWN VOCABULARY
        proves it: 'department' is printed unbroken elsewhere, while a real
        compound ('natural-born') is printed WITH its hyphen. Welding without
        that proof would make 'ANTI-' / 'TERRORISM' into one word.
        """
        from ..resolve.footnotes import line_markup
        add = line_markup(line).strip()
        if add:
            head = item.text.rstrip()
            if head.endswith("-") and _welds(head, add, vocab):
                item.text = head[:-1] + add
            else:
                item.text = head + " " + add
        item.prov = m.Prov(cover.number,
                           tuple(item.prov.line_ids) + (line.id,))
        consumed.add(line.id)

    # A READER THAT CLAIMS A REGION INHERITS ITS FURNITURE. Above the
    # banner the cover prints only apparatus — the running head naming the
    # section, the folio beside it, the slip stamp and the Reporter's
    # notice — and every one of those rows is recorded as Dropped rather
    # than passed over: a row left in the stream here is the first thing
    # above the writing, and assembly reads it as the writing's opening.
    body = (geom.body_size if geom else 11.0) or 11.0
    top_band = (cover.height or 792.0) * _TOP_BAND
    for line in lines[:start]:
        text = _norm(line.plain)
        if not text:
            continue
        if line.top <= top_band:
            kind = "folio" if text.strip(" .[]-").isdigit() else "running-head"
        elif (line.size or body) < body - 1.0:
            kind = "notice"
        else:
            kind = "superfluous"
        dropped.append(m.Dropped(text=text,
                                 prov=m.Prov(cover.number, (line.id,)),
                                 kind=kind))
        consumed.add(line.id)

    for line in lines[start:]:
        text = _norm(line.plain)
        if not text:
            continue

        if _TYPED_RULE.match(text):
            items.append(m.Rule(prov=m.Prov(cover.number, (line.id,)),
                                typed=True, span="center"))
            consumed.add(line.id)
            last = None
            continue

        if _is_slip_banner(line, geom):
            last = (line, _emit(line, "court"), "court")
            continue

        # THE DOCKET stands alone between its rules ('No. 25–5146'), and on
        # an order the Court runs the decision date into it ('No. 25–848.
        # Decided June 15, 2026') — the only place that record states it.
        if looks_like_docket(text) and len(text) < 90:
            if not crit.get("docket_number"):
                crit["docket_number"] = _docket_head(text)
            else:
                crit.setdefault("other_dockets", []).append(
                    _docket_head(text))
            _mine_dates(crit, text)
            _emit(line, "docket")
            # A DOCKET ROW THAT STATES THE DATE CLOSES THE COVER, exactly as
            # the bracketed date does on a merits cover — an order runs the
            # two together ('No. 25–51. Decided January 26, 2026') and there
            # is no other closing row. What follows is the writing: 'PER
            # CURIAM.' is set in caps like a party, and read on as one more
            # caption row it took the per curiam's own byline into the
            # headmatter and left the opinion unsigned.
            if _DATE_IN_ROW.search(text):
                break
            last = (line, items[-1], "docket")
            continue

        # THE DECISION DATE CLOSES THE COVER. What the Court prints next is
        # its writing — the byline, or for an unsigned order 'PER CURIAM.'
        # and the disposition. 'PER CURIAM.' is set in caps like a party and
        # was read as one more caption row, which put the writing's own
        # opener in the headmatter.
        if _BRACKET_DATE.match(text):
            if not crit.get("decision_date"):
                crit["decision_date"] = text.strip("[]").strip()
            _emit(line, "date")
            break

        if _is_origin_opener(text) or _is_origin_row(text):
            if _wraps(line, "lower-court"):
                _merge(line, last[1])
                last = (line, last[1], "lower-court")
                continue
            last = (line, _emit(line, "lower-court"), "lower-court")
            continue

        # A BARE PIVOT is the ordinary multi-row caption — the Court stacks
        # 'WES ALLEN, ALABAMA SECRETARY OF STATE,' / 'ET AL.' / '25–243  v.'
        # / 'MARCUS CASTER, ET AL.' and the hinge row carries no party at
        # all. Read as 'not a caption' it ended the cover mid-caption.
        _pivot = text.rstrip(".").strip().lower() in ("v", "vs")
        if _pivot or _is_caption_row(text):
            if _wraps(line, "caption"):
                _merge(line, last[1])
                last = (line, last[1], "caption")
                continue
            # …and a caption's OWN runover may open with a lower-case word
            # only in the origin, never here: a caps row that follows the
            # origin at wrap distance is the origin's continuation.
            if _wraps(line, "lower-court"):
                _merge(line, last[1])
                last = (line, last[1], "lower-court")
                continue
            last = (line, _emit(line, "caption"), "caption")
            continue

        # Anything else ends the cover: the byline, or the Court's own
        # unsigned disposition. Neither is headmatter, and the reader never
        # reaches into a writing.
        break

    # THE ROWS AS THEY WERE READ ARE THE ONE SOURCE. A runover merges into
    # the row it continues, hyphen and all, so a second bookkeeping list of
    # strings drifts from what the render shows the moment a wrap is welded
    # ('ALABAMA DE-' / 'PARTMENT' welded in the row and split in the
    # criteria). The criteria are read back off the items.
    # …and back to PLAIN TEXT first: the markup escapes what the page prints
    # ('M & K EMPLOYEE SOLUTIONS' becomes 'M &amp; K …'), and 'amp' is
    # lower-case, so the caps test that identifies a caption row rejected
    # the row on its own escaping and the case came back with no parties.
    from ..audit import strip_tags as _st
    from ..audit import unescape_xml as _ux

    def _plain(it) -> str:
        return _norm(_ux(_st(it.text)))

    printed = [(getattr(it, "role", ""), _plain(it)) for it in items
               if getattr(it, "text", None)]
    banner_rows = [t for r, t in printed if r == "court"]
    caption_rows = [t for r, t in printed if r == "caption"]
    origin_rows = [t for r, t in printed if r == "lower-court"]
    if not (banner_rows and (caption_rows or crit.get("docket_number"))):
        return NOTHING
    crit["court"] = _norm(" ".join(banner_rows))
    if caption_rows:
        crit["caption"] = caption_rows
        # The WHOLE printed run goes to the party reader, apparatus and all:
        # a consolidated cover stacks one caption per docket, and it is the
        # docket and the 'ON APPLICATION FOR STAY' between them that say
        # where one case ends and the next begins.
        # THE DOCKET CELL SHARES THE PIVOT'S ROW. A consolidated cover sets
        # each case's number in the left column, level with its 'v.'
        # ('FEDERAL COMMUNICATIONS COMMISSION, ET AL., PETITIONERS' |
        # '25–406' | 'v.' | 'AT&T, INC.'), and the row rebuilds with the
        # number run into the first party's name. It is apparatus, not part
        # of anyone's name — dropped for the party read, kept in the row.
        sides = headmatter_parties(
            rows=[_CAPTION_CELL.sub(" ", t) if r == "caption" else t
                  for r, t in printed])
        if sides is not NOTHING:
            crit["parties"] = list(sides)
            crit["case_name"] = " v. ".join(sides)
    if origin_rows:
        # A consolidated cover states the proceeding once PER CASE ('ON
        # APPLICATION FOR STAY' three times over three dockets); joined they
        # read as one absurd lower court. The case's own is the first.
        crit["lower_court"] = origin_rows[0]
    return {"criteria": crit, "items": items, "attorneys": [],
            "summary": [], "dropped": dropped, "consumed": consumed,
            "anchor_ids": set(), "doc_type_final": None}


# A bare docket number standing immediately before the caption's pivot.
_CAPTION_CELL = re.compile(r"\s\d{2,3}[\u2013\u2014-]\d{1,4}\s+(?=[Vv]s?\.)")


_DATE_IN_ROW = re.compile(
    r"\b(Argued|Submitted|Reargued|Decided|Filed)\b[^A-Za-z0-9]{0,4}"
    r"([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})")


def _mine_dates(crit: dict, text: str) -> None:
    """An order's docket row carries the dates the cover would otherwise
    print on their own ('No. 25–848. Decided June 15, 2026')."""
    for label, value in _DATE_IN_ROW.findall(text):
        key = label.lower()
        value = _norm(value).rstrip(".")
        if key in ("decided", "filed") and not crit.get("decision_date"):
            crit["decision_date"] = value
        elif key in ("argued", "submitted", "reargued") \
                and not crit.get("submitted"):
            crit["submitted"] = value


# --------------------------------------------------------------------------
# writing.unsigned — the Court's own order IS a writing
# --------------------------------------------------------------------------

@decider("writing.unsigned", court="scotus")
def unsigned_order(segs, is_byline, syl_pages=(), **_):
    """The disposition between the caption and the first byline — by LINE.

    An order document states the Court's holding unsigned ('The petition for
    a writ of certiorari is denied.', or a full stay order) and the signed
    writings that follow dissent FROM it. That disposition is the Court's
    own writing: filed as headmatter it renders as a stack of caption rows
    and the document appears to have no majority at all.

    The caption closes on its date — '[May 14, 2026]' on a merits cover, or
    the docket-and-date row an order runs together ('No. 162, Orig. Decided
    May 26, 2026'). The run is read in LINES, not segments, because the
    segmenter may set the closing row and the disposition it introduces in
    one segment; a segment-level rule keeps them fused and the order stays
    lost. It ends at the first byline — the old engine's lesson that a
    writing hanging off an order SHARES the disposition's segment is exactly
    why the byline, and not the page, has to close the run.
    """
    # The SYLLABUS cover states the docket and both dates too ('No.
    # 25-5146. Argued March 30, 2026-Decided June 11, 2026'), and the
    # syllabus prose follows it — reading that as a disposition invents an
    # unsigned writing on every merits opinion. The Court disposes on a
    # WRITING's cover, never on a syllabus page.
    lines = [l for seg in segs if seg.page not in (syl_pages or ())
             for l in seg.lines]
    anchor = None
    for i, line in enumerate(lines):
        text = _norm(line.plain)
        low = text.lower()
        if _BRACKET_DATE.match(text) or (
                looks_like_docket(text)
                and ("decided" in low or "filed" in low)):
            anchor = i
            break
    if anchor is None:
        return NOTHING
    order: set[int] = set()
    for line in lines[anchor + 1:]:
        text = _norm(line.plain)
        if not text:
            continue
        # A masthead is CAPS as well as court-named: 'the District Court
        # may "oversee an orderly process."' carries two court words and
        # would otherwise close the order mid-sentence, dropping its second
        # half back into the headmatter.
        if is_byline(text) or (_is_banner_row(text)
                               and _is_caption_row(text)):
            break
        order.add(line.id)
    return order or NOTHING
