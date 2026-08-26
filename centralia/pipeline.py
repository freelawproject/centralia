"""The fixed pipeline. Eleven stages, one order, no overrides:

  load > triage > measure > classify > furniture > footnotes > segments
  > headmatter > body > finalize > emit

Fresh state per document; every decision in the trace. Courts appear only as
the CourtProfile handed to the resolvers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import geometry
from . import model as m
from .classify import classify_doc_type, triage
from .courts import get_profile
from .pdfio import build_pdf
from .resolve.assemble import assemble
from .resolve.bylines import BylineParser
from .resolve.captions import classify_page
from .resolve.evidence import Trace
from .resolve.footnotes import FootnoteZones
import collections as _collections
import os as _os_env
import re as _re

# A CASE CITATION inside a publication-status sentence means the sentence is
# about ANOTHER decision: a reporter or database cite, a docket number, a
# star-page. Length is NOT the discriminator — ca5 states its own status in
# 70 characters ('* This opinion is not designated for publication. See 5th
# Cir. R. 47.5.') and that one is TRUE, while mich's Reporter syllabus
# recites the court BELOW's unpublished opinion and tagged 17 of 50
# published slips wrongly.
_STATUS_CITES_ANOTHER = _re.compile(
    r"\b(?:wl|lexis)\b|\bno\.\s*\d|\bf\.\s?(?:supp|app)|"
    r"\b\d+\s+[a-z]\.\s?[a-z]?\.?\s?\d|\bat\s+\*\d")

from .resolve.evidence import NOTHING, court_decides
from .resolve.furniture import FurnitureFinder
from .resolve.headmatter import read_headmatter, _hm_line
from .resolve.segments import Segmenter
from .styles import pick as pick_style

PIPELINE_VERSION = "0.0.3"

# Warnings that describe the SOURCE PDF rather than the parse. These can
# never be fixed by better extraction, so they route a file to 'scanned'
# instead of 'review' and keep the defect worklist honest.
SOURCE_WARNINGS = (
    "scan with OCR text layer",
    "image-only page",
    "text missing from",
    # A PAGE-IMAGE DOCUMENT IS THE SAME COMPLAINT AS THE REST OF THIS LIST.
    # Left out, the stub a pure scan returns read as a PARSE failure: 7 of
    # nevapp's 31 records -- every one of them a bilevel raster with no text
    # layer at all -- graded D on 'no-opinions' plus a parse warning, as
    # though a reader could be written for them.
    "non-born-digital",
    # An unmapped-CID font is unreadable by every extractor, so it routes
    # with the scans wherever a warning list is consulted.
    "text layer unreadable",
)

# A FOLIO IS NOT A SIGNATURE ROW. The page number closes the sheet
# below the signing block ("5", "Page 116 of 116", "- 3 -"), and it is
# not dropped yet where the signature lift runs, so it broke the walk
# on its first row.
_FOLIO_ROW = _re.compile(
    r"^(?:[-–—\s]*\d{1,4}[-–—\s]*|Page\s+\d{1,4}\s+of\s+\d{1,4}\.?)$",
    _re.IGNORECASE)

# THE CONFORMED SLASH, WHEREVER THE ROW PUTS IT. A judge signs on the slash
# alone; a lawyer types the form the pleading rule gives them, which opens
# with the word that introduces it: 'By: /s/ Yonatan Even'
# (cand/364265.1716.0). Tested with `startswith`, that row was not a signing
# row at all — so it BROKE the signing run in half, the half that carried the
# slash was thrown away, and the whole end matter (firm, roster, 'Attorneys
# for Plaintiff and Counter-defendant EPIC GAMES, INC.') stayed in the body
# as 14 one-line paragraphs. Nothing then claimed the signature, and with no
# signature there was nothing for the filing test below to read.
_CONFORMED = _re.compile(r"(?:^|[\s:(\[])/s/")



# WHO SIGNED, AND AS WHAT. A court signs an office; a party's lawyer signs
# for a client, and says so.
# WHAT OPENS A BLOCK ON ITS OWN: the paragraph mark a court numbers with, and
# the outline label it sections with. Neither is ever a runover.
_PARA_OPENER = __import__("re").compile(
    r"^(?:\u00b6|\u00a7|\*)|^(?:[IVXLC]{1,5}|[0-9]{1,2}|[A-Z])\s*[.)]\s+\S")
# A bare paragraph number, the mark lost to OCR: digits then a capitalised
# word, never a citation's reporter volume.
_NUM_OPENER = __import__("re").compile(r"^[0-9]{1,3}\s+[A-Z]")
# The dot leaders and the page number that CLOSE a table-of-contents entry.
_TOC_TAIL = __import__("re").compile(
    r"(?:\.[  ]?){6,}\s*[0-9IVXivx]+(?:\s*[-\u2013\u2014]\s*[0-9IVXivx]+)?\.?$")
_re_tags = __import__("re").compile(r"<[^>]+>")

_FILING_FLAG = "a party's filing, not the court's writing"
_re_filing_appearance = __import__("re").compile(
    r"\b(?:attorneys?|counsel)\s+for\b|\bon\s+behalf\s+of\b"
    r"|\bpro\s+se\b(?:\s+(?:plaintiff|defendant|petitioner))")
# THE ROSTER A PARTY'S PAPER CLOSES WITH. Contact details -- an e-mail, a
# telephone, a firm's form of organisation -- are what a lawyer's end matter
# carries and what a court's signature never does. Two of them standing with
# an appearance row is the evidence that the block IS an appearance block and
# not a sentence of prose that mentions counsel.
_re_roster_row = _re.compile(
    r"[\w.+-]+@[\w-]+\.[\w.]+"
    r"|^(?:tel|telephone|fax|facsimile|phone)\b\s*[:.]"
    r"|\b(?:LLP|LLC|PLLC|P\.\s?C\.|A\.?P\.?C\.?)\b", _re.I)
# AN APPEARANCE ROW, NOT A SENTENCE ABOUT ONE. A district order says 'counsel
# for plaintiff filed a motion' in prose all the time; an appearance block
# says nothing but who it appeared for, and stops.
# THE DATE A COURT PUTS ON ITS PAPER WHEN THE HEADMATTER NEVER DID. A
# district signs above its own name and dates the signature: 'Dated: August
# 6, 2026', a bare 'August 18, 2026' at the rail, or the ordinal recital
# 'SO ORDERED, this 17th day of August, 2026'. Measured on mad, where 21 of
# 27 records carry their ONLY date there and came back with none at all (the
# user, 2026-08-24: 'gotta fix tese MAD ones'), and on msnd/52361.17.0, whose
# one-page judgment states its date the ordinal way.
_MONTHS = ("january|february|march|april|may|june|july|august|september"
           "|october|november|december")
_re_signed_date = _re.compile(
    rf"\b(?:dated?\s*:?\s*)?({_MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})\b", _re.I)
_re_ordinal_date = _re.compile(
    rf"\bthis\s+(\d{{1,2}})(?:st|nd|rd|th)\s+day\s+of\s+({_MONTHS}),?\s+(\d{{4}})\b",
    _re.I)


# THE ROW THAT SAYS THE DATE IS THE PAPER'S OWN.
_re_dated_row = _re.compile(
    r"\bdated\b|\bdone\s+and\s+ordered\b|\bso\s+ordered\b"
    r"|\bentered\s+this\b|\bsigned\s+this\b|\bthis\s+\d{1,2}(?:st|nd|rd|th)"
    r"\s+day\s+of\b", _re.I)


# THE REVISION STAMP a judgment FORM carries at the head of every sheet —
# '(Rev. 11/25)'. The form NUMBER beside it cannot be read on its own: a
# district prefixes the AO's number with its own ('GAS245B' — gasd), sets a
# pen glyph in front of it ('✎AO 245D' — iand), or prints none at all, and a
# pattern loose enough for those also matches a bare docket standing in the
# same band ('EDCR20-00019-KK-1' — cacd/…770740.1371.0, which is not a form
# code at all). The revision is what no opinion carries.
# THE SEPARATOR IN THE REVISION IS NOT ALWAYS A SLASH. A subset font that
# lost its ToUnicode map hands the '/' back as an escape, so the stamp reads
# '(Rev. 11(cid:18)25)' — nced/…208700.202.0's AO 245C, which named no form
# at all against a pattern that insisted on the character. '(Rev.' is the
# distinctive part; whatever stands between the two numbers is not.
# …AND THE DISTRICT STAMPS ITS OWN INITIALS INSIDE THE PARENTHESIS. A court
# that amends the AO's sheet says so where the revision stands — casd prints
# '(CASD Rev. 1/19)' on AO 245D and '(CASDRev. 08/14)', no space at all, on
# AO 245B. Insisting on 'Rev' immediately after the bracket read neither as a
# form (the user, 2026-08-25, four times over: 'this is a form … why cnat we
# tag them?'), and both are judgments filled in on a pre-printed sheet.
_AO_REV = _re.compile(
    r"\(\s*(?:[A-Za-z]{2,6}\s*)?Rev\.?\s*\d{1,2}\D{1,12}\d{2,4}\s*\)", _re.I)
# …AND A COURT'S OWN MINUTE TEMPLATE NAMES ITSELF IN ITS HEADING AND AGAIN
# IN ITS FOOTER. cacd heads every one 'CIVIL MINUTES – GENERAL' over a grid
# of labelled fields (Case No. | Date | Title, Deputy Clerk, Court Reporter,
# Proceedings:). Measured over 2,099 records: three carry the phrase, all of
# them that form.
_MINUTES = _re.compile(r"\b(?:CIVIL|CRIMINAL)\s+MINUTES\b", _re.I)
_AO_FORM = _re.compile(r"^[^A-Za-z0-9]{0,3}AO\s*\d{1,3}[A-Z]?\b", _re.I)
# A FORM THAT PRINTS NO REVISION STILL PRINTS ITS NUMBER, and the AO is not
# the only body that issues one. The probation office's violation petition
# heads waed/…95832.132.0 with 'PROB 12C' — no revision, no title, nothing
# else on the row — so a test that keys on the revision stamp cannot see it
# at all. Read ONLY where the code opens the row in the head band, which is
# where a form prints its own name and where no court's prose begins: the
# two records that merely MENTION a form (mnd/…226579.5.0's 'return a
# Marshal Service Form (Form USM 285)', sdd/…85997.7.0's 'submit an AO 239
# Application') say so mid-sentence at 55% of the sheet.
# 'JS' IS DELIBERATELY ABSENT. cacd stamps 'JS-3' and 'JS-6' on ordinary
# minute orders as a case-status code, not a form number, and no record in
# the corpus heads a sheet with a JS form at all.
_SERIES_FORM = _re.compile(
    r"^[^A-Za-z0-9]{0,3}"
    r"(?P<code>(?:AO|CJA|PROB|EOIR|USM)[\s.-]?\d{1,3}\s?[A-Z]?)\b", _re.I)


# A DISTRICT'S PREFIX IS GLUED TO THE NUMBER, never a word beside it. gasd
# issues the AO's judgment as 'GAS245B', which is why the prefix is allowed
# at all — but spelled with a gap it also reached backwards across the space
# into the e-filing stamp printed on the same band, and the form came out
# named after the stamp: 'DOCUMENT AO 245B' (nysd/…624127.124.0), 'SDNY AO
# 245B' (…627069.131.0), 'OF AO 245B' (waed/…98410.132.0).
# …AND THE AO ISSUES ONE SHEET FOR TWO FORMS. iand/…69000.105.0 heads
# 'AO 245 B&C', the judgment and the amended judgment on one template.
_AO_NAME = _re.compile(
    r"([A-Z]{0,4}AO\s*\d{1,3}(?:\s?[A-Z](?:&[A-Z])?)?"
    r"|[A-Z]{2,4}\d{2,3}[A-Z]?)", _re.I)


# THE INSTRUCTIONS A FORM PRINTS UNDER ITS BLANKS — '(Name of Counsel)',
# '(Last 4 digits)', 'MONTH DAY YEAR'. A district that uses its own template
# rather than the AO's prints no form number and no revision, so nothing in
# the head declares it: cacd/…770740.1371.0 and …770761.1367.0 are judgment
# forms headed only 'United States District Court' and a 'JS-3' code. What
# they DO print is a caption for every blank, which no court sets in its own
# prose. Measured over 1,749 records: two or more such cells appear on the
# cacd form and on nothing else at all.
_FORM_INSTR = _re.compile(
    r"^\((?:name|last|month|day|year|type|print|check|if|specify|date|city"
    r"|state|signature|title|attach|list)\b[^)]{0,44}\)$", _re.I)
_FORM_LEGEND = _re.compile(r"^(?:MONTH\s+DAY\s+YEAR"
                           r"|DATE\s+OF\s+(?:BIRTH|ENTRY))$", _re.I)
_FORM_INSTR_MIN = 2


def _prints_form_instructions(model) -> bool:
    """Does the paper caption its own blanks? See `_FORM_INSTR`."""
    n = 0
    for pm in model.pages[:2]:
        for line in pm.lines:
            flat = " ".join(line.plain.split())
            if _FORM_INSTR.match(flat) or _FORM_LEGEND.match(flat):
                n += 1
                if n >= _FORM_INSTR_MIN:
                    return True
    return False


# A FONT THE OCR ENGINE INVENTED. A born-digital PDF embeds a subset of a
# real face and reuses it — 'ABCDEF+TimesNewRomanPSMT' on every page. An OCR
# engine has no font to embed: it synthesizes one per page and names it after
# the face it guessed, with an arbitrary id — '*Times New Roman-3206' on page
# one, '*Times New Roman-4021' on page two. txsd/…2092603.7.0 reads that way
# on all four sheets and was reported born-digital, so its footnotes came
# back wrong with nothing to say why (the user, 2026-08-25: 'we need to do
# better about identifying ocr scans so we can flag that … we need to know
# that'). Measured over 1,166 records: four carry such a name, every one of
# them a scan with a page image under the text.
_OCR_FONT = _re.compile(r"^\*.+-\d{2,6}$")


def _ocr_synthesized(model) -> bool:
    """Was this text layer SYNTHESIZED by an OCR engine? See `_OCR_FONT`."""
    for pm in model.pages[:3]:
        for line in pm.lines:
            for c in (line.chars or ()):
                name = str(c.get("fontname") or "").split("+")[-1]
                if _OCR_FONT.match(name):
                    return True
    return False


def _names_ao_form(model) -> str:
    """WHICH form the paper says it is, or ''. See `Meta.form`."""
    for pm in model.pages[:1]:
        band = [l for l in pm.lines
                if l.plain.strip() and l.top <= pm.height * 0.12]
        joined = " ".join(" ".join(l.plain.split()) for l in band)
        if not _AO_REV.search(joined):
            continue
        # The code stands immediately before the revision it is issued under.
        head = joined[:_AO_REV.search(joined).start()]
        m = None
        for m in _AO_NAME.finditer(head):
            pass
        if m:
            return " ".join(m.group(1).split()).upper()
        return "form"
    # …AND THE CODE ALONE, where the sheet stamps no revision. See
    # `_SERIES_FORM`: the head band and the row's own opening are the whole
    # test, because the number is all such a sheet prints.
    for pm in model.pages[:1]:
        for line in pm.lines:
            if not line.plain.strip() or line.top > pm.height * 0.12:
                continue
            hit = _SERIES_FORM.match(" ".join(line.plain.split()))
            if hit:
                return " ".join(hit.group("code").split()).upper()
    for pm in model.pages[:1]:
        if _MINUTES.search(" ".join(l.plain for l in pm.lines)):
            return "minutes"
    return "form" if _prints_form_instructions(model) else ""


def _states_ao_form(model) -> bool:
    """Does the paper print an Administrative Office FORM NUMBER at its head?

    The AO issues the judgment, the summons and the warrant as numbered
    forms, and each sheet carries its number and revision ('AO 245B (Rev.
    11/25) Judgment in a Criminal Case'). A court's own writing never does.
    Read on the first sheet only, above the caption, where the number sits.
    """
    for pm in model.pages[:1]:
        band = [l for l in pm.lines
                if l.plain.strip() and l.top <= pm.height * 0.12]
        if _AO_REV.search(" ".join(l.plain for l in band)):
            return True
        for line in band:
            if _AO_FORM.match(" ".join(line.plain.split())):
                return True
    return False


def _signed_date(text: str) -> str | None:
    """The date a signing block states, in the form the readers publish."""
    m = _re_ordinal_date.search(text)
    if m:
        return f"{m.group(2).title()} {int(m.group(1))}, {m.group(3)}"
    m = _re_signed_date.search(text)
    if m:
        return f"{m.group(1).title()} {int(m.group(2))}, {m.group(3)}"
    return None


# WHAT ONLY A COURT SAYS. A disposition is the court speaking, and it
# outranks a party's appearance printed on the same page.
_re_ordering = _re.compile(
    r"\b(?:so\s+ordered|it\s+is\s+(?:hereby\s+)?ordered"
    r"|signed\s+this|entered\s+this)\b", _re.I)
_re_appearance_row = _re.compile(
    r"^(?:attorneys?|counsel)\s+(?:for|on\s+behalf\s+of)\b", _re.I)

# WHAT A PARTY'S SIGNATURE CARRIES AND A COURT'S NEVER DOES.
_re_counsel_apparatus = __import__("re").compile(
    r"\brespectfully\s+submitted\b|\bby:\s*/s/|\bcertificate\s+of\s+service\b"
    r"|\b(?:sbn|bar\s+no\.?|state\s+bar)\b|\besq\.|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")

# …and what the paper calls itself — but ONLY where the name belongs to a
# party and to nobody else. Measured over 90 records, a broad pleading
# vocabulary called five court writings filings: 'memorandum' is what olc
# titles its opinions and what ca9 titles an unpublished disposition, and
# 'motion', 'brief', 'response' and 'objections' all appear in the names
# courts give their own orders. What is left is a name no court signs.
_re_pleading = __import__("re").compile(
    r"^(?:(?:first|second|third|fourth|amended|verified|joint|corrected|"
    r"supplemental|proposed)\s+)*"
    r"(?:complaint|answer|counterclaim|cross-?claim|"
    r"notice\s+of\s+(?:appeal|removal))\b",
    __import__("re").I)


def _px(image) -> int:
    """How many pixels the source object actually carries. `srcsize` is the
    image's own resolution, which is what tells a photograph from the frame
    it was pasted inside."""
    src = image.get("srcsize") if hasattr(image, "get") else None
    if src and len(src) == 2:
        return int(src[0]) * int(src[1])
    return 0


# HOW LITTLE TEXT A FULL-SHEET RASTER MAY CARRY before its words are taken
# to be in the picture rather than in the text layer. Measured on nysd: an
# endorsed FORM fills 4.3% of the sheet, endorsed LETTERS whose text is all
# present fill 19.5% and 33%, and a page of prose about half.
_RASTER_TEXT_COVER = 0.12


def _text_cover(pm) -> float:
    """What fraction of the sheet the page's own text lines cover."""
    if not pm.width or not pm.height:
        return 1.0
    area = sum(max(0.0, l.x1 - l.x0) * max(0.0, l.bottom - l.top)
               for l in pm.lines if l.plain.strip())
    return area / (pm.width * pm.height)


def _page_list(pages: list[int]) -> str:
    """'p 4', 'pp 4, 11', 'pp 4-6, 11' — contiguous runs collapsed, the rest
    named. A warning that names its pages has to name the RIGHT ones."""
    runs: list[list[int]] = []
    for n in sorted(pages):
        if runs and n == runs[-1][-1] + 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    parts = [str(r[0]) if len(r) == 1 else f"{r[0]}-{r[-1]}" for r in runs]
    return ("p " if len(pages) == 1 else "pp ") + ", ".join(parts)


def _column_order(lines: list) -> list:
    """Re-read a TWO-COLUMN block in column order. Guam sets counsel as
    parallel columns ('Appearing for Plaintiff-Appellee:' left, 'Appearing
    for Defendant-Appellant:' right) that row-wise reading interleaves,
    attributing lawyers to the wrong party. Evidence required: every visual
    row splits into exactly two pieces, each column's left edge is
    consistent, and the columns never overlap. Anything less reads in the
    original order."""
    if len(lines) < 4:
        return lines
    xs = sorted(l.x0 for l in lines)
    gap, idx = max((b - a, i) for i, (a, b) in enumerate(zip(xs, xs[1:])))
    if gap < 40:
        return lines
    split_x = (xs[idx] + xs[idx + 1]) / 2
    left = [l for l in lines if l.x0 < split_x]
    right = [l for l in lines if l.x0 >= split_x]
    if len(left) < 2 or len(right) < 2:
        return lines
    if max(l.x0 for l in left) - min(l.x0 for l in left) > 14:
        return lines
    if max(l.x0 for l in right) - min(l.x0 for l in right) > 14:
        return lines
    if max(l.x1 for l in left) - 2 > min(l.x0 for l in right):
        return lines
    return (sorted(left, key=lambda l: (l.page, l.top))
            + sorted(right, key=lambda l: (l.page, l.top)))


@dataclass
class ExtractionResult:
    document: m.Document
    trace: Trace
    # valid   — fully accounted, nothing to look at
    # scanned — parsed, but the SOURCE is a scan (nothing to fix here)
    # review  — the parse left something unplaced or warned
    # failed  — no usable output
    status: str = "valid"
    versions: dict = field(default_factory=lambda: {"pipeline": PIPELINE_VERSION})


# A FILING STAMP IN THE COURT'S OWN FORM: 'Filed 7/20/26'. Prose cannot
# match it, which is what lets the length bound below be waived.
_FILED_STAMP = _re.compile(r"^Filed\s+\d{1,2}/\d{1,2}/\d{2,4}\b", _re.I)
# THE ECF PAGE OVERLAY IS NOT A COVER STAMP. Every page of a federal
# district filing carries the same one-row stamp, and it opens on the same
# word a cover stamp does: 'Filed 07/06/26     Page 4 of 5 PageID #: 926'.
# Counted as a filing stamp it made the strict test true on EVERY page,
# which widened the banner window to eight rows, and eight rows down an
# opinion some sentence carries two court words — so arwd/75862 was cut in
# two at page 4 and rendered as two writings. What tells the overlay from a
# cover is that the overlay NAMES ITS OWN PAGE: a stamp reading 'Page 4 of
# 5' is that page's furniture, whatever else stands beside it.
# 'of M' IS OPTIONAL. waed's stamp wraps its own total onto the next line
# ('… PageID.1504     Page 19' / '19'), so the row never says 'of 19' at all.
# What identifies the overlay is the page it NAMES, not the total.
_PAGE_OF = _re.compile(r"\bPage\s+(\d+)(?:\s+of\s+\d+)?\b", _re.I)


def _is_page_overlay(text: str, page_number: int) -> bool:
    for mm in _PAGE_OF.finditer(text):
        if int(mm.group(1)) == page_number:
            return True
    return False


def _stamp_row(pm, line) -> str:
    """The line's whole VISUAL ROW. The ECF stamp is one typed row, but pdfio
    splits it at its column gaps, and half a stamp does not look like one:
    waed's pieces are 'Case 2:26-cv-00160-TOR', 'ECF No. 7',
    'filed 07/06/26', 'PageID.29     Page 9 of 9'. Read piece by piece, the
    third IS a filing stamp and the fourth is where the page number lives —
    so every page of every waed record looked like a fresh cover, and
    waed/114266 was cut at page 19 and rendered with its own signature block
    inside the caption."""
    if line.row is None:
        return line.plain.strip()
    return " ".join(l.plain.strip() for l in pm.lines
                    if l.row == line.row).strip()


def _attached_documents(model) -> list[tuple[int, int]]:
    """Page ranges of the documents STAPLED into one PDF. A later page
    opening with a fresh 'Filed <date>' stamp AND the court's banner is a
    new cover (calctapp staples the unmodified opinion behind its
    modification order). One range = one document."""
    from .resolve.headmatter import _is_banner_row
    cuts = [0]
    for i, pm in enumerate(model.pages):
        if i == 0:
            continue
        tops = sorted((l for l in pm.lines if l.plain.strip()),
                      key=lambda l: l.top)[:4]
        # THE WIDER BANNER WINDOW IS COUPLED TO THE STRICT STAMP. calctapp
        # sets the stamp, the 'NOT TO BE PUBLISHED' flag and a three-row
        # rule-8.1115 notice above its own name, which puts the banner on row
        # 6 — outside the four rows the stamp is looked for in. But widening
        # the window unconditionally cut ca9/dickinson_v._trump at page 34,
        # where a separate writing opens under the CLERK'S stamp and that
        # stamp's own 'U.S. COURT OF APPEALS' row reads as a banner: the
        # document split mid-writing, 459 rows of opinion became headmatter
        # and the majority lost half its blocks. So the window only opens
        # where the page carries a stamp in the court's exact form, which a
        # clerk's 'FILED' / date / 'MOLLY C. DWYER, CLERK' block does not.
        _rows = {id(l): _stamp_row(pm, l) for l in tops}
        _strict = any(_FILED_STAMP.match(_rows[id(l)])
                      and not _is_page_overlay(_rows[id(l)], pm.number)
                      for l in tops)
        has_banner = any(_is_banner_row(l.plain) for l in
                         (sorted((l for l in pm.lines if l.plain.strip()),
                                 key=lambda l: l.top)[:8] if _strict
                          else tops))
        # the filing stamp may be its own row ('FILED' over 'AUG 10 2026'
        # — ca9) or an inline 'Filed 7/30/26' (calctapp)
        # A filing STAMP IS SHORT. Without a bound, a sentence of the body
        # that merely opens on the word ('filed by [Ortiz's] probation
        # officer."  Accordingly, the District…') reads as a stamp, and
        # paired with a prose line carrying two court words — which
        # `_is_banner_row` accepts — it cuts a new stapled document out of
        # the middle of an opinion (ortiz-rodriguez split at page 9 and lost
        # its writing). calctapp's 'Filed 7/30/26' is 13 characters.
        # …OR IT NAMES ITSELF EXACTLY: 'Filed 7/20/26'. A stamp in that form
        # cannot be prose, so it needs no length bound — and it needs none,
        # because calctapp writes the case onto the stamp when it staples the
        # unmodified opinion behind its modification order ('Filed 7/20/26
        # Bates v. City of Temecula CA4/1 (unmodified opinion)', 67
        # characters against the 40 above). Without this, bates read as ONE
        # document: the order's writing ran on through the opinion's whole
        # reprinted cover and its 26 pages of body, 105 blocks under one
        # empty byline (the user's call, 2026-08-20).
        has_filed = any(
            not _is_page_overlay(_rows[id(l)], pm.number)
            and ((_rows[id(l)].lower().startswith("filed ")
                  and len(_rows[id(l)]) <= 40)
                 or _FILED_STAMP.match(_rows[id(l)])
                 or _rows[id(l)].rstrip(":").upper() == "FILED")
            for l in tops)
        if has_banner and has_filed:
            cuts.append(i)
    cuts.append(len(model.pages))
    return list(zip(cuts, cuts[1:]))


def _shift_pages(doc: m.Document, off: int) -> None:
    """Add ``off`` to every prov page — a stapled part processed with local
    numbering keeps its true PDF pages for the viewer."""
    def fix(obj):
        prov = getattr(obj, "prov", None)
        if prov is not None:
            try:
                prov.page += off
            except Exception:
                obj.prov = m.Prov(prov.page + off, prov.line_ids)
    for it in (list(doc.headmatter) + list(doc.syllabus)
               + list(doc.attorneys) + list(doc.headnotes)
               + list(doc.signature) + list(doc.trailer)
               + list(doc.dropped) + list(doc.residual)
               + list(doc.headmatter_footnotes)):
        fix(it)
        for side in ("left", "right"):
            for row in getattr(it, side, []) or []:
                fix(row)
        for b in getattr(it, "blocks", []) or []:
            fix(b)
    for op in doc.opinions:
        try:
            op.author_prov.page += off
        except Exception:
            op.author_prov = m.Prov(op.author_prov.page + off,
                                    op.author_prov.line_ids)
        for coll in (op.caption, op.blocks, op.signature, op.footnotes):
            for it in coll or []:
                fix(it)
                for b in getattr(it, "blocks", []) or []:
                    fix(b)


def extract(pdf_path: str, court_id: str) -> ExtractionResult:
    model = build_pdf(str(pdf_path))
    bounds = _attached_documents(model)
    if len(bounds) > 1:
        results = []
        for a, b in bounds:
            part = type(model)(path=model.path, pages=model.pages[a:b])
            saved = [pm.number for pm in part.pages]
            for k, pm in enumerate(part.pages, 1):
                pm.number = k
            r = _extract_model(part, court_id, pdf_path)
            for pm, n in zip(part.pages, saved):
                pm.number = n
            _shift_pages(r.document, a)
            results.append(r)
        base = results[0]
        bd = base.document
        for r in results[1:]:
            d = r.document
            bd.headmatter.extend(d.headmatter)
            bd.syllabus.extend(d.syllabus)
            bd.attorneys.extend(d.attorneys)
            bd.headnotes.extend(d.headnotes)
            bd.opinions.extend(d.opinions)
            bd.dropped.extend(d.dropped)
            bd.residual.extend(d.residual)
            bd.headmatter_footnotes.extend(d.headmatter_footnotes)
            for w in d.warnings:
                if w not in bd.warnings:
                    bd.warnings.append(w)
            for f in ("publication_status", "decision_date", "submitted",
                      "docket_number", "judges", "disposition",
                      "lower_court", "history", "attorneys"):
                if not getattr(bd.criteria, f):
                    setattr(bd.criteria, f, getattr(d.criteria, f))
            if not bd.criteria.parties:
                bd.criteria.parties = d.criteria.parties
        bd.warnings.append(
            f"{len(bounds)} stapled documents (covers at pp "
            + ", ".join(str(a + 1) for a, _ in bounds) + ")")
        if any(r.status != "valid" for r in results):
            base.status = "review"
        return base
    return _extract_model(model, court_id, pdf_path)


def _extract_model(model, court_id: str, pdf_path) -> ExtractionResult:
    profile = get_profile(court_id)
    trace = Trace()

    for pm in model.pages:
        for quirk, detail in pm.events:
            trace.event(f"quirk.{quirk}", f"p{pm.number}: {detail}")

    meta = m.Meta(court_id=court_id, court_label=profile.court_label,
                  n_pages=model.n_pages, source_path=str(pdf_path))
    doc = m.Document(meta=meta)

    # 2 triage — a scan is a SUCCESS status, not a failure. But a scan WITH
    # a substantial text layer (OCR) holds a parseable opinion: extract it
    # and flag REVIEW — the geometry is untrusted, the words are not lost.
    verdict = triage(model)
    if verdict == "scan":
        # THE RICHEST PAGE, not the sum. A stamp-only overlay is ~50-70
        # characters PER PAGE, so a scan long enough accumulates past any
        # total-ink floor and is handed to the readers as though it held an
        # opinion: 44 records — ded's 10, mtd's 10, and one to three each
        # from 20 more district courts — came back with a document type of
        # 'unknown', no headmatter, no caption and no writing, because the
        # only text in them was the CM/ECF header repeated down the file.
        # ded/…67860.423.0 is 8 pages carrying 528 characters, 66 of them on
        # its fullest page. Measured on the single fullest page the two
        # families separate with nothing in between: every stamp-only scan
        # in the corpus tops out at 141 characters, and the lowest page of
        # any scan that really does carry a cover — delctcompl's
        # vrns_ii_llc, which renders 33 headmatter rows — carries 401.
        # 250, not 500: a one-page writ disposition's WHOLE text is ~350
        # chars (lactapp — 'writ dismissed' orders were stubbed empty), and
        # on one page the fullest page IS the whole document.
        ink = max((p.ink_chars for p in model.pages), default=0)
        if ink < 250:
            meta.doc_type = m.DocType.SCAN
            meta.source_kind = "scan"
            doc.warnings.append("non-born-digital (scan); not parsed")
            # `scanned`, NOT `valid`. A stamp-only scan yields no headmatter,
            # no writing and no text, and `valid` states the one thing the
            # status exists to state -- that the reading can be trusted --
            # about a reading that does not exist. Every OTHER source
            # complaint routes to `scanned` through SOURCE_WARNINGS below;
            # this early return was the one path that did not, so 231
            # district records (mtd 21 of 38, ded 14, cacd 13) reported clean
            # with an unread caption page, and a consumer gating on `valid`
            # was handed an empty document as a good one.
            return ExtractionResult(doc, trace, status="scanned")
        meta.source_kind = "ocr-scan"
        doc.warnings.append(
            "scan with OCR text layer; extracted, geometry untrusted")
    else:
        # A SCAN WHOSE OCR LAYER IS TOO GOOD TO TRIAGE. `triage` calls a page
        # a scan only when its image covers the sheet AND it carries almost no
        # text, so a scan that OCR'd cleanly is the one kind of scan nothing
        # reported: nevapp/ccmsi_v._odell is a bilevel 200dpi raster on all
        # ten pages with 761-1,680 characters each, and it rendered as
        # ordinary born-digital paper with no flag at all (the user,
        # 2026-08-21). The reading is good and must go on — what was missing
        # was saying whose geometry it is. `ocr_text_layer` answers that from
        # the type rather than the text volume, and it is asked HERE, outside
        # the triage verdict, so it can never reach the refusal above.
        from .classify import ocr_text_layer
        if ocr_text_layer(model):
            meta.source_kind = "ocr-scan"
            doc.warnings.append(
                "scan with OCR text layer; extracted, geometry untrusted")
    # A HYBRID document: born-digital cover + scanned appendix pages that
    # carry no text layer at all (wis reprints an order as page images).
    # Nothing text-based is lost, but the reader must know pages are
    # image-only.
    from .classify import CID_MAX_FRAC, SCAN_IMAGE_AREA
    _img_only = [pm.number for pm in model.pages
                 if pm.image_area > SCAN_IMAGE_AREA and pm.ink_chars < 120]
    # SURFACED, not just warned about. These were local and discarded; a
    # consumer needs the page numbers, not a sentence to parse. See Meta.
    meta.text_missing_pages = list(_img_only)
    meta.scan_pages = [pm.number for pm in model.pages
                       if pm.image_area > SCAN_IMAGE_AREA]
    meta.cid_pages = [pm.number for pm in model.pages
                      if pm.ink_chars and
                      pm.cid_chars / pm.ink_chars > CID_MAX_FRAC]
    # WORDS DRAWN RATHER THAN WRITTEN. A chambers that flattens its headings
    # to vector outlines leaves nothing for any text layer to hold, so the
    # words are on the page and not in the document — paed/…658030.12.0
    # draws its masthead and 'MEMORANDUM OPINION AND ORDER' that way and
    # published `valid` with no court and no title and no complaint of any
    # kind (the user, 2026-08-25: 'why dont i see … memorandum and opinion
    # order on the text output?'). Named the same way image-only pages are:
    # what the reader needs is which pages, and that the text is not here.
    # A SHEET THAT IS A PICTURE, with a note typed over it. The test above
    # asks whether a page carries almost NO text, and a memo endorsement
    # carries just enough to escape it: nysd/…611698.117.0 is form AO 154
    # filled in and flattened to a raster covering 99.5% of the sheet, with
    # the judge's 'Application GRANTED…' set underneath it. 294 characters —
    # over the 120 floor — so the record published `valid` with no
    # complaint, while the caption, the case number, the parties and both
    # attorneys were all in the picture (the user, 2026-08-25: 'this is a
    # form right').
    # COVERAGE is what separates it from a page merely printed over a
    # background image, which is common and loses nothing: measured on nysd,
    # the endorsed form's text fills 4.3% of the sheet while the endorsed
    # LETTERS beside it — whose text layers are complete — fill 19.5% and
    # 33%. A page of prose fills about half.
    _thin = [pm.number for pm in model.pages
             if pm.image_area > SCAN_IMAGE_AREA
             and pm.number not in _img_only
             and _text_cover(pm) < _RASTER_TEXT_COVER]
    if _thin and verdict != "scan":
        doc.warnings.append(
            f"{len(_thin)} page(s) ({_page_list(_thin)}): the sheet is a "
            f"page image with only a note set over it — what it says is in "
            f"the picture, not in this document")
    _outlined = [pm.number for pm in model.pages if pm.outlined_rows]
    meta.outlined_pages = list(_outlined)
    if _outlined:
        _rows = sum(pm.outlined_rows for pm in model.pages)
        doc.warnings.append(
            f"{_rows} line(s) on {len(_outlined)} page(s) "
            f"({_page_list(_outlined)}) are drawn as outlines, not text: "
            f"those words are not in this document")
    if _img_only and verdict != "scan" and len(_img_only) < model.n_pages:
        # NAME THE PAGES, AND SAY WHAT IS LOST. Printed as first-to-last the
        # note read as a RANGE — nev/engle_julie_2 carries no text on pages 4
        # and 11 and the warning said '2 image-only page(s), no text layer
        # (pp 4-11)', which states eight (the user, 2026-08-21: 'says no text
        # on pages 4-11 maybe that should be a better banner? like missing
        # pages of text'). What the reader needs to know is not that the
        # pages hold an image — it is that their TEXT IS NOT IN THIS
        # DOCUMENT, and exactly which pages those are.
        doc.warnings.append(
            f"text missing from {len(_img_only)} of {model.n_pages} page(s) "
            f"({_page_list(_img_only)}): image only, no text layer")
    if verdict == "unreadable":
        meta.doc_type = m.DocType.UNKNOWN
        doc.warnings.append("text layer unreadable (unmapped CID glyphs)")
        # A FONT WITH NO USABLE ENCODING IS A SOURCE COMPLAINT, not a parse
        # failure. The glyphs carry no Unicode mapping, so no reader can
        # recover the text: poppler returns the same mojibake pdfminer does
        # ('ÿijkSlTÿcZmY[Page' on rid/58912, where only the CM/ECF stamp --
        # set in a normal font -- survives). Reported as `failed` it sat on
        # the parse worklist as though a reader were owed, which is the very
        # thing SOURCE_WARNINGS exists to prevent; it belongs with the scans,
        # whose text is recoverable only by OCR. Measured on the 7 records in
        # the district corpora that reach here (5 rid, mnd, nced).
        return ExtractionResult(doc, trace, status="scanned")

    # 3 measure
    geom = geometry.measure(model)
    vocab = geometry.learn_vocabulary(model)
    if geom:
        trace.event("geometry", f"body_x0={geom.body_x0} right={geom.right_x1:.0f} "
                                f"lead={geom.lead} size={geom.body_size}")

    # 4 classify
    sig, cap_style, cap_name = classify_page(model.pages[0])
    doc_style = pick_style(model, sig, profile.styles)
    meta.doc_style = cap_style
    # The caption band never runs PAST an interior 'Syllabus' section
    # heading (conn sets the syllabus on the caption page and the measured
    # band swallowed its first paragraph as hmrows).
    _b0 = sig.get("band")
    if _b0:
        for _l in model.pages[0].lines:
            if " ".join(_l.plain.split()).lower() == "syllabus" \
                    and _b0[0] < _l.top < _b0[1]:
                sig["band"] = (_b0[0], _l.top - 2)
                break
    # A CAPTION BOX IS NOT A TABLE. pdfio reads a ruled grid off the drawn
    # rules alone, and a federal caption fenced in the ECF manner is exactly
    # that shape — a two-column box, parties left, docket right, ruled row
    # by row (gand/daye reads 5x2). It is headmatter, already read as
    # headmatter, so a grid overlapping the measured caption band is
    # withheld from the body reading.
    _cap_band = sig.get("band")
    _tables: dict[int, list] = {}
    for pm in model.pages:
        _keep = []
        for _g in pm.tables:
            if (pm.number == 1 and _cap_band
                    and _g.top < _cap_band[1] and _g.bottom > _cap_band[0]):
                trace.event("table.caption-box",
                            f"p{pm.number} {_g.n_rows}x{_g.n_cols} "
                            f"at y{_g.top:.0f}")
                continue
            _keep.append(_g)
        _tables[pm.number] = _keep

    doc_type, heading = classify_doc_type(model, geom)
    meta.doc_type = doc_type
    # …AND WHERE THE TEXT WAS MACHINE-READ, SAY SO. `triage` calls a scan by
    # the raster it can see; an OCR layer rich enough hides that, and the
    # record then claims a fidelity it does not have. The font names are the
    # engine's own signature — see `_ocr_synthesized`. Only ever ADDED: a
    # verdict already reached above ('scan', 'ocr-scan') stands.
    if not meta.source_kind and _ocr_synthesized(model):
        meta.source_kind = "ocr-scan"
        doc.warnings.append(
            "OCR text layer (machine-read): the words are the scanner's "
            "reading of an image, and every coordinate is its guess")
        trace.event("source", "ocr-scan by synthesized font names")
    meta.form = _names_ao_form(model)
    if meta.form:
        trace.event("form", f"the paper names itself {meta.form!r}")
    if heading:
        trace.event("doc-type", f"{doc_type} via {heading!r}")

    # 5 furniture
    ff = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                         geom.body_size if geom else 12.0)
    content_by_page: dict[int, list] = {}
    # v1 lesson: the RUNNING HEAD is read before it is dropped — ca2's
    # corner slug ('25-246-cv' / 'Perez v. Porter') is the docket and the
    # case name, stated nowhere else on a summary order.
    _slug_docket: list[str] = []
    _slug_case: list[str] = []
    _figures: list = []
    _mastheads: list = []   # page-1 seals: headmatter, not body
    _sig_imgs: list = []    # last-page signature stamps
    # STATIONERY REPEATS; A FIGURE DOES NOT. An image printed at the SAME
    # position on page after page is the court's watermark or letterhead,
    # not something the opinion refers to — ky sets its seal at 124,249,
    # 363x294pt, on all 24 pages of every record, and it passes the figure
    # test (22% of the page, clear of both margins), so all 1,448 page
    # rasters across the court were cropped and planted in the body. This
    # is the same rule the furniture pass already applies to running heads
    # and folios, stated for images: keyed on the position and size, three
    # pages or more is stationery.
    _img_key = _collections.Counter(
        (round(_i.x0), round(_i.top), round(_i.x1 - _i.x0),
         round(_i.bottom - _i.top))
        for _pm in model.pages for _i in _pm.images)
    _STATIONERY_PAGES = 3

    def _is_stationery(_i) -> bool:
        return _img_key[(round(_i.x0), round(_i.top), round(_i.x1 - _i.x0),
                         round(_i.bottom - _i.top))] >= _STATIONERY_PAGES

    # A PAGE UNDER A FULL-BLEED RASTER IS A SCAN, and nothing on it is a
    # FIGURE. tenn's `mark_gray_v._tyson_foods_inc.` carries two images per
    # page: the whole sheet at 0,0 612x792, which the stationery rule above
    # catches, and the scan's own content area at ~77,70 472x575 — 57% of the
    # page, clear of both margins, and at coordinates that shift a point or
    # two per page, so it is not stationery and it passed the figure test on
    # all 9 pages. An opinion does not print a figure over the entire sheet it
    # is printed on; where one image covers the page, every other image on
    # that page is part of the same scan.
    _FULL_BLEED = 0.9
    _scan_pages = {
        _pm.number for _pm in model.pages
        for _i in _pm.images
        if ((_i.x1 - _i.x0) * (_i.bottom - _i.top))
        >= _pm.width * _pm.height * _FULL_BLEED}

    from .resolve.headmatter import looks_like_docket as _slug_ld
    for pm in model.pages:
        keep = []
        _grids = _tables.get(pm.number) or ()
        for line in pm.lines:
            kind = ff.kind(pm, line)
            # A CELL IS NOT A STAMP. Every furniture test reads a line's
            # shape and position, and a table's cells are exactly the shape
            # furniture has — short, isolated, off the measure, at a margin.
            # njtaxct's property table lost 'Property', 'Percentage of',
            # 'Retail' and 'Class' from its header row that way (dropped as
            # stamps and a running head), and its second table lost nine
            # more cells. A line inside a DRAWN cell is the court's own
            # tabulation, whatever its shape.
            if kind is not None and any(g.holds(line) for g in _grids):
                trace.event("furniture.in-cell",
                            f"p{pm.number}: {line.plain.strip()[:40]!r} "
                            f"kept ({kind})")
                kind = None
            if kind is None:
                keep.append(line)
            else:
                if kind in ("running-head", "folio") \
                        and line.top < pm.height * 0.14:
                    _t = " ".join(line.plain.split())
                    _d = _slug_ld(_t)
                    if _d and len(_t) < 30:
                        _slug_docket.append(_d)
                    elif (" v. " in _t or _t.endswith(" v.")) \
                            and len(_t) < 70:
                        _slug_case.append(_t)
                doc.dropped.append(m.Dropped(
                    text=line.plain.strip(), prov=m.Prov(pm.number, (line.id,)),
                    kind=kind))
        content_by_page[pm.number] = keep
        if pm.rotated_text:
            doc.dropped.append(m.Dropped(text=pm.rotated_text,
                                         prov=m.Prov(pm.number), kind="rotated"))
        # Page IMAGES: a sizable image INSIDE the body region is a printed
        # FIGURE (adidas's trademark exhibits) — carried into the body as
        # a data URI. Everything else (seals, logo stamps, signature
        # graphics) is surfaced as a KNOWN removal; tiny artifacts
        # (< 20pt a side) stay silent.
        # ONE PICTURE, TWO OBJECTS. A photo pasted in through a word
        # processor arrives as a composite AND as the photograph inside it —
        # alnd/179841.412.0 carries, on each of five pages, a 264×208 outer
        # object and a 789×620 inner one inset ~15pt on every side. Both are
        # sizable, both are inside the body, so both were planted as figures
        # and every exhibit photo appeared TWICE side by side (the user,
        # 2026-08-23: 'the html is oduble rendering IMages'). Where one box
        # contains another the picture is the one with more pixels in it; the
        # other is the frame it was pasted in, and it is recorded as a
        # removal so the audit still shows what stood there.
        _nested: set = set()
        for _a in pm.images:
            for _b in pm.images:
                if _a is _b:
                    continue
                if not (_b.x0 >= _a.x0 - 1 and _b.top >= _a.top - 1
                        and _b.x1 <= _a.x1 + 1 and _b.bottom <= _a.bottom + 1):
                    continue
                _pa = _px(_a)
                _pb = _px(_b)
                _drop = _a if _pb > _pa else _b
                if id(_drop) in _nested:
                    continue
                _nested.add(id(_drop))
                doc.dropped.append(m.Dropped(
                    text=(f"graphic {_drop.x1 - _drop.x0:.0f}×"
                          f"{_drop.bottom - _drop.top:.0f}pt "
                          f"(the frame around another image)"),
                    prov=m.Prov(pm.number), kind="image",
                    bbox=(_drop.x0, _drop.top, _drop.x1, _drop.bottom)))
        for _im in pm.images:
            if id(_im) in _nested:
                continue
            _w, _h = _im.x1 - _im.x0, _im.bottom - _im.top
            # WHAT A GRAPHIC IS can be the court's own knowledge. Every test
            # below reads a graphic's role off its GEOMETRY, because geometry
            # is all core can see — but a court that knows its own stationery
            # knows the answer outright, and no accumulation of position and
            # size should outvote it. A decider answers with one of the
            # reserved words 'seal' (the headmatter's masthead device),
            # 'figure' (part of the writing) or 'signature' (the stamp a
            # writing is signed with); ANY OTHER string is a surfaced
            # removal and the string itself is the reason shown in the
            # record. NOTHING falls through to core exactly as if the court
            # file did not exist.
            # A BOX DRAWN ROUND THE TYPE IS NOT A DEVICE. An e-filed caption
            # may carry a graphic that FILLS the caption box:
            # ctd/gov.uscourts.ctd.172073.13.0 paints a 271x126pt indexed
            # fill from (77,114) to (348,240), which is exactly where 'STRIKE
            # 3 HOLDINGS, LLC,' … 'Defendant.' are typed. Every geometric
            # test below says masthead — page 1, top third, inside the
            # measure, centred — so the caption was DRAWN A SECOND TIME above
            # its own rows (the user, on this file: 'this shouldnt redraw the
            # image of hte caption please'). A court's device stands on blank
            # paper: the discriminator is the page's OWN TYPE INSIDE the box,
            # which no seal, no clerk's stamp and no figure of an opinion
            # has. Scoped off the scan pages and off anything covering half
            # the sheet, where every row of the page is 'inside' the raster
            # and the stationery rules already have the answer.
            # …AND ONLY WHERE A CAPTION CAN BE. A JUDGE'S SIGNATURE IS A
            # BOX ROUND TYPE TOO: the graphic is the handwriting, and its
            # box reaches down over the typed rule, the name and the office
            # beneath it — alnd/…190122.47.0 signs page 18 of 18 with a
            # 382x111pt stamp enclosing '____', 'HAROLD D. MOOTY III' and
            # 'UNITED STATES DISTRICT JUDGE'. Measured over the 109 corpus
            # files that keep a graphic, the unbounded test took 40 real
            # signatures with it across alnd, lawd, nhd, nmd, cod, ned, rid
            # and 6 more courts. A caption box stands where a caption
            # stands — the first sheets, in the head of the page — and the
            # signature band is the one place this test must not reach.
            # …AND ON THE FIRST SHEET ONLY. A DIGITAL SIGNATURE BLOCK is a
            # box round type too, and it stands in the head of a later page:
            # miss/…leflore encloses 'DIGITAL SIGNATURE', 'Order#: 261995',
            # 'Sig Serial: 100011970' and 'Presiding Justice' in a 415x89pt
            # box at the top of page 2, and the page-2 reach dropped it. A
            # caption box stands where the caption is — the first sheet —
            # and a caption that runs on to the second is read by the
            # carry-on walk, not by this test.
            if (pm.number == 1
                    and _im.bottom <= pm.height * 0.5
                    and pm.number not in _scan_pages
                    and _w * _h <= 0.5 * pm.width * pm.height):
                _inside = [_l for _l in pm.lines
                           if _l.plain.strip()
                           and _l.x0 >= _im.x0 - 2 and _l.x1 <= _im.x1 + 2
                           and _l.top >= _im.top - 2
                           and _l.top <= _im.bottom + 2]
                if len(_inside) >= 3:
                    # NAME WHAT IT IS, where position can tell. A graphic
                    # flush to the right edge of the head band is the
                    # clerk's stamp, not a caption box — the same
                    # discriminator the figure test states below, and
                    # vawd/…132979.41.0 draws its 'CLERK … FILED May 19,
                    # 2026 … BY: /s/ DEPUTY' stamp there in unmapped CID
                    # glyphs. Read as a masthead it was drawn at the head of
                    # the headmatter as though it were the court's seal.
                    _mid_x = (_im.x0 + _im.x1) / 2
                    _text = (f"stamp {_w:.0f}\u00d7{_h:.0f}pt "
                             "(clerk's, flush right)"
                             if _mid_x > pm.width * 0.6
                             else f"graphic {_w:.0f}\u00d7{_h:.0f}pt "
                                  f"(the box around {len(_inside)} "
                                  "typed rows)")
                    doc.dropped.append(m.Dropped(
                        text=_text,
                        prov=m.Prov(pm.number), kind="image",
                        bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))
                    continue
            _role = court_decides("image.role", court_id, trace,
                                  model=model, geom=geom, page=pm, image=_im)
            if _role is not NOTHING:
                if _role == "seal":
                    _mastheads.append(_im)
                elif _role == "signature":
                    _sig_imgs.append(_im)
                elif _role == "figure":
                    _figures.append(_im)
                else:
                    doc.dropped.append(m.Dropped(
                        text=f"graphic {_w:.0f}×{_h:.0f}pt ({_role})",
                        prov=m.Prov(pm.number), kind="image",
                        bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))
                continue
            # AN IMAGE ABOVE ALL THE TYPE IS STATIONERY, not a figure. mo
            # sets its court seal at top 72 of 792 — 9.09%, just past the
            # 0.08 guard — so it was cropped and planted INSIDE the writing,
            # and 45 of mo's 50 opinions opened with the seal (ill's summary
            # sheet does the same at 9.09%). The user, 2026-08-19: "it
            # doesn't need to go into the opinion since it's not part of it
            # … just put it at the top centered of the headmatter".
            _first_text = min((l.top for l in pm.lines if l.plain.strip()),
                              default=0.0)
            # A SEAL IS SMALL. Standing above the type is what makes a
            # graphic stationery rather than a figure, but it does not make
            # it a SEAL: a scanned source carries the whole page as one
            # raster at 0,0, and that image is above the first text row too.
            # virginislands's `3rc__company_inc._v._boynes_trucking_system`
            # had its entire first page cropped and planted at the head of
            # the headmatter. A masthead is a device the court prints at the
            # top of its stationery, so it is bounded — measured against the
            # seals actually in the corpus, no real one comes near half the
            # measure or a quarter of the page's height.
            # …AND A MASTHEAD STANDS IN THE MEASURE. An e-filing stamp is
            # also small and also above the type, but the clerk puts it in a
            # CORNER — virginislands's sits at x0=497 of 612, hard against
            # the right edge. A device the court prints as its own
            # letterhead is centred or set at the left margin, never flush
            # to the far edge, so the graphic's centre must fall in the
            # middle of the page.
            # …AND A SEAL NEED NOT STAND ABOVE THE TYPE AT ALL. 'Above the
            # first text row' is a proxy for 'in the letterhead band', and it
            # fails on a court that prints anything before its device:
            # texbizct sets the clerk's FILED stamp in the top corner and its
            # own public-domain cite ('2026 Tex. Bus. 23') centred above the
            # seal, so the seal stands at top 104 of 792 with two text rows
            # over it — not a masthead by that test, and 37 of its 42 records
            # opened the opinion with the court's seal in it. What the band
            # actually is, is the TOP THIRD of page 1: caption and letterhead
            # live there and an opinion's own figure does not.
            _imid = (_im.x0 + _im.x1) / 2
            _is_masthead = (pm.number == 1
                            and (_im.top <= _first_text
                                 or _im.bottom <= pm.height * 0.33)
                            and _w <= pm.width * 0.55
                            and _h <= pm.height * 0.25
                            and abs(_imid - pm.width / 2) <= pm.width * 0.35
                            and not _is_stationery(_im))
            # THE COURT'S DEVICE, PRINTED AGAIN, IS STILL THE DEVICE. A
            # court that repeats its seal on the second page draws the SAME
            # image at the SAME place, and two pages is one short of the
            # stationery rule's three — so the repeat fell through to the
            # figure test and 5 texbizct records carried the seal inside the
            # opinion after page 1's copy had been lifted out of it.
            # Matched to 2pt, not exactly: the same device rasterized on two
            # pages comes back 93.7x93.7 on one and 95.0x95.0 on the other.
            _same_as_seal = any(
                abs((_m.x1 - _m.x0) - _w) <= 2
                and abs((_m.bottom - _m.top) - _h) <= 2
                and abs(_m.x0 - _im.x0) <= 6
                for _m in _mastheads)
            _is_figure = (
                _w >= 60 and _h >= 40
                and not _is_masthead
                and not _same_as_seal
                and not _is_stationery(_im)
                and pm.number not in _scan_pages
                and _im.top > pm.height * 0.08
                and _im.bottom < pm.height * 0.92
                and not (pm.number == model.n_pages
                         and _im.top > pm.height * 0.55))
            if _is_masthead and _w >= 20 and _h >= 20:
                _mastheads.append(_im)
                continue
            if _same_as_seal:
                doc.dropped.append(m.Dropped(
                    text=f"seal {_w:.0f}\u00d7{_h:.0f}pt (repeated)",
                    prov=m.Prov(pm.number), kind="image",
                    bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))
                continue
            # …and the mirror at the foot of the LAST page: an image below
            # every text row there is the court's signature stamp.
            # The floor is the last row of BODY text, not the last row of
            # anything: a chambers template prints the document's own source
            # path under the stamp, which raised the floor above the
            # signature on 8 of kyed's 25 records — and on one the stamp
            # loses to its OWN date row by 3pt. Measured over 2,217 federal
            # district files, this takes signature graphics 107 -> 276:
            # 168 files gain one, none loses one, across 44 courts.
            # THE FLOOR IS THE LAST ROW OF BODY TEXT, not the last row of
            # anything. Anything the furniture pass already classifies —
            # a folio, a running foot, a stamp, a template's own source
            # path — is not body, and counting it raised the floor above
            # the signature it was supposed to find. Stated as "not
            # furniture" rather than naming any one court's habit.
            _sig_floor = max((l.top for l in pm.lines
                              if l.plain.strip()
                              and l.top < pm.height * 0.9
                              and ff.kind(pm, l) is None),
                             default=0.0)
            # …AND THE SIGNATURE MAY STAND BESIDE THE DATE, not below it.
            # nynd/141588.92.0 sets 'Dated: June 11, 2026' / 'Albany, New
            # York' at the rail and the judge's signature in the signers'
            # column beside them — the graphic's top is 2.4pt ABOVE the
            # place row's, so `_im.top > _sig_floor - 30` failed by those
            # 2.4pt. Dropped as 'seal/logo/stamp', it took the only trace of
            # the judge with it: the page types no name and no office, so
            # the record came back with NO AUTHOR and still graded A (the
            # user, 2026-08-23: 'why was scullin removed and where to').
            # What a closing block cannot do is stand in the signers' own
            # column — the date and the place are set at the rail — so this
            # second floor is measured only from the rows that could be
            # BODY, the ones that run at least half the measure, and the
            # image must be in the signers' column with none of them below
            # it. A figure the opinion discusses runs the measure itself and
            # keeps its own rows below it, so it cannot pass here.
            _prose_floor = max(
                (l.bottom for l in pm.lines
                 if l.plain.strip() and l.top < pm.height * 0.9
                 and ff.kind(pm, l) is None
                 and geom is not None
                 and l.x1 - l.x0 > geom.column * 0.5),
                default=None)
            if (pm.number == model.n_pages and _w >= 60 and _h >= 20
                    and ((_im.bottom > _sig_floor
                          and _im.top > _sig_floor - 30.0)
                         or (_prose_floor is not None
                             and _im.x0 > pm.width * 0.42
                             and _im.top > _prose_floor - 2.0))):
                _sig_imgs.append(_im)
                continue
            # A CLERK'S STAMP IS NOT A FIGURE OF THE OPINION. The masthead
            # rule above already states the discriminator — 'a device the
            # court prints as its own letterhead is centred or set at the
            # left margin, never flush to the far edge' — and its mirror
            # holds: a graphic set FLUSH RIGHT in the head band of a caption
            # page is the clerk's, not the court's argument.
            # njtaxct/g_s_realty_corp_v._brick_township_1 is the case that
            # named it: the record IS a corrected opinion, and the notice
            # bound in front of it says what was corrected — 'Page 1, to add
            # the stamp' — so the 140x53pt graphic the clerk added, sitting
            # inside the caption's own band at x0=400 of 612, was published
            # as the second block of the opinion.
            # Bounded to the caption pages and the upper half of the sheet,
            # so a figure the opinion actually discusses (that court's other
            # record prints a 468x311pt exhibit on page 6) is untouched.
            if (_is_figure and pm.number <= 2
                    and _imid > pm.width * 0.6
                    and _im.bottom <= pm.height * 0.5
                    and _h <= pm.height * 0.25):
                doc.dropped.append(m.Dropped(
                    text=f"stamp {_w:.0f}\u00d7{_h:.0f}pt (clerk's, flush right)",
                    prov=m.Prov(pm.number), kind="image",
                    bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))
                continue
            if _is_figure:
                _figures.append(_im)
            elif _w >= 20 and _h >= 20:
                _what = ("watermark/stationery" if _is_stationery(_im)
                         else "scanned page" if pm.number in _scan_pages
                         else "seal/logo/stamp")
                doc.dropped.append(m.Dropped(
                    text=f"graphic {_w:.0f}×{_h:.0f}pt ({_what})",
                    prov=m.Prov(pm.number), kind="image",
                    bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))
    # Dedupe repeated furniture for display — but keep EVERY dropped line's
    # identity: the sweep must know page 3's folio was dropped even though
    # only page 2's shows (digitless keys collapse all folios to one entry).
    all_dropped_ids = {i for d in doc.dropped for i in d.prov.line_ids}
    seen: set[tuple[str, str]] = set()
    deduped = []
    for d in doc.dropped:
        key = (d.kind, "".join(c for c in d.text if not c.isdigit()))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(d)
    doc.dropped = deduped

    # 6 footnotes — per-page zones over content lines.
    zones = FootnoteZones(
        model, geom, profile.footnotes, court_id, trace,
        is_byline=lambda t: bool(BylineParser(profile.byline).parse(t)))
    zone_tops: dict[int, float] = {}
    zone_lines_by_page: dict[int, list] = {}
    prev_had = False
    for pm in model.pages:
        decision = zones.page_zone(pm, prev_had_zone=prev_had)
        prev_had = decision.value is not None
        if decision.value is not None:
            zone_tops[pm.number] = decision.value
            keep_ids = {l.id for l in content_by_page[pm.number]}
            zone_lines_by_page[pm.number] = [
                l for l in zones._lines_below(pm, decision.value)
                if l.id in keep_ids]

    # 7 segments — content lines above the zone.
    segmenter = Segmenter(geom, model.pages[0].width,
                          is_author_line=lambda t: bool(
                              BylineParser(profile.byline).parse(t)),
                          para_indent_min=profile.para_indent_min,
                          tables=_tables)
    segments_by_page = {}
    for pm in model.pages:
        cut = zone_tops.get(pm.number)
        lines = [l for l in content_by_page[pm.number]
                 if cut is None or l.top < cut]
        segments_by_page[pm.number] = segmenter.segment_page(lines, pm.number)

    # A court whose headmatter is a LAYOUT CONTRACT reads it itself, before
    # assembly. The reader claims only headmatter lines — banner, recital,
    # roster, the rule-fenced caption, the counsel block — and everything
    # below its last landmark is untouched: writings, bylines, footnote
    # zones and paragraph splitting all run exactly as they do for any other
    # court. The claim is SUBTRACTIVE, which is also what stops a panel
    # roster from reading as a byline and opening a phantom writing.
    _court_hm = court_decides("headmatter.read", court_id, trace,
                              model=model, geom=geom)
    if _court_hm is NOTHING:
        _court_hm = None
    _segments_unclaimed = {k: list(v) for k, v in segments_by_page.items()} \
        if _court_hm else None
    if _court_hm:
        # A court that reads its own headmatter also knows what KIND of
        # paper it is — and it knows before assembly, which is where the
        # type decides how writings anchor.
        _claimed = set(_court_hm.get("consumed") or ())
        # A ROW THE COURT PLACED IS NOT A REMOVAL. The furniture pass runs
        # at stage 5, long before any court reader, so a court that rescues
        # its own apparatus from a furniture rule has to read that row off
        # `pm.lines` — and the drop recorded upstream then stands beside the
        # very row the reader placed. me's ladder sits exactly where the
        # corner-stamp rule fires, and
        # me/amelia_johnson_v._michael_osseyran listed 'Submitted' as
        # removed and rendered it as headmatter at once; ca2's corner slug,
        # calctapp's 'Filed 7/30/26', la's news-release number and kyed's
        # ECF header are all reported twice the same way.
        #
        # PLACED, not merely CLAIMED. The claim is subtractive — a reader
        # may consume a line to keep it out of the body without putting it
        # anywhere — and withdrawing the drop for one of those would make
        # the row vanish from the record entirely, which is the one outcome
        # worse than reporting it twice. Only a drop whose every line came
        # back out in a placed item is withdrawn.
        def _placed_ids(_items) -> set[int]:
            _ids: set[int] = set()
            for _it in _items or ():
                _pv = getattr(_it, "prov", None)
                if _pv is not None:
                    _ids.update(_pv.line_ids)
                # a two-column caption carries its rows one level down
                _ids |= _placed_ids(getattr(_it, "left", None))
                _ids |= _placed_ids(getattr(_it, "right", None))
            return _ids

        _placed = _placed_ids(_court_hm.get("items"))
        doc.dropped = [_d for _d in doc.dropped
                       if not (_d.prov.line_ids
                               and set(_d.prov.line_ids) <= _placed)]
        from .resolve.segments import Segment as _SegHM
        for _pg, _sgs in list(segments_by_page.items()):
            _out = []
            for _sg in _sgs:
                _keep = [l for l in _sg.lines if l.id not in _claimed]
                if _keep:
                    _out.append(_SegHM(_sg.page, _keep, _sg.kind))
            segments_by_page[_pg] = _out


    # 9 body (assembly finds the opinion boundary, which stage 8 needs).
    parser = BylineParser(profile.byline)
    # SYLLABUS PAGES: a court-issued syllabus printed BEFORE the opinion's
    # own caption page (nj's 4-page cover; mich's 'Syllabus' release pages)
    # is the syllabus, not headmatter. A page whose top third sets a
    # standalone 'SYLLABUS' heading opens the block; following pages
    # continue it until a page opens with the court's banner (the real
    # caption page).
    _syl_pages: set[int] = set()
    _syl_open = False
    from .resolve.headmatter import _is_banner_row as _ibr
    for pm in model.pages:
        top_lines = [l for l in pm.lines if l.top < pm.height * 0.4]
        # The heading must OPEN the page (first three rows) — conn sets
        # 'Syllabus' as an interior section heading under the released
        # date, which is that page's apparatus, not a cover.
        first3 = sorted((l for l in pm.lines if l.plain.strip()),
                        key=lambda l: l.top)[:3]
        _big = 3 * (geom.body_size if geom else 12.0)
        has_syl = "syllabus" in profile.front_matter and any(
            " ".join(l.plain.split()).upper() == "SYLLABUS"
            and (l in first3 or (l.size or 0) >= _big)  # mich's watermark
            for l in top_lines)
        has_banner = any(_ibr(l.plain) for l in top_lines)
        if has_syl:
            _syl_open = True
        elif _syl_open and has_banner:
            _syl_open = False
        if _syl_open:
            _syl_pages.add(pm.number)

    # A court whose pages NAME their own section decides its extent outright
    # (scotus sets 'Syllabus' / 'Opinion of the Court' in every running head):
    # the printed page outranks any inference core could make from prose.
    _court_syl = court_decides("syllabus.pages", court_id, trace,
                               model=model, geom=geom)
    if _court_syl is not NOTHING:
        _syl_pages = set(_court_syl)

    # A CLERK'S COVER SHEET names itself. ri prints 'OPINION COVER SHEET'
    # on a trailing page — a label/value grid of case metadata (Written By,
    # Justices, Source of Appeal, Attorneys), never opinion text. Merged
    # into the body it reads as a phantom tail. It is apparatus: route the
    # whole page to headmatter and keep it out of assembly.
    _COVER_TITLES = ("opinion cover sheet", "cover sheet",
                     "order cover sheet")
    _cover_pages: set[int] = set()
    for pm in model.pages:
        first3 = sorted((l for l in pm.lines if l.plain.strip()),
                        key=lambda l: l.top)[:6]
        if any(" ".join(l.plain.split()).lower() in _COVER_TITLES
               for l in first3):
            _cover_pages.add(pm.number)
    _cover_lines = {p: list(segments_by_page.get(p) or [])
                    for p in _cover_pages}
    for p in _cover_pages:
        segments_by_page[p] = []

    # A COVER PER PAPER: where the court prints one, it declares both where
    # each writing begins and which rows are the cover's own. The rows are
    # apparatus — the banner, the caption, the docket, already read once from
    # page 1 — so they are RECORDED as removed and kept out of assembly
    # entirely; the user's requirement, 2026-08-20: the standard caption
    # matter must not end up inside the extracted opinions.
    _covers = court_decides("writing.covers", court_id, trace,
                            model=model, geom=geom)
    _writing_starts: dict[int, str] = {}
    if _covers is not NOTHING and _covers:
        _writing_starts = dict(_covers.get("starts") or {})
        _drop_ids = set(_covers.get("drop") or ())
        if _drop_ids:
            from .resolve.segments import Segment as _SegCov
            for _pg, _sgs in list(segments_by_page.items()):
                _kept = []
                for _sg in _sgs:
                    _keep_lines = [l for l in _sg.lines
                                   if l.id not in _drop_ids]
                    _gone = [l for l in _sg.lines if l.id in _drop_ids]
                    if _gone:
                        doc.dropped.append(m.Dropped(
                            text=" ".join(l.plain.strip() for l in _gone)[:400],
                            prov=m.Prov(_sg.page,
                                        tuple(l.id for l in _gone)),
                            kind="cover"))
                    if _keep_lines:
                        _kept.append(_SegCov(_sg.page, _keep_lines, _sg.kind))
                segments_by_page[_pg] = _kept

    def _assemble_with(segs):
        return assemble(model, geom, segs, zones, zone_tops,
                        zone_lines_by_page, parser, vocab, trace,
                        caption_band=sig.get("band"),
                        doc_type=meta.doc_type, syl_pages=_syl_pages,
                        front_matter=profile.front_matter,
                        para_indent_min=profile.para_indent_min,
                        headmatter_claimed=bool(_court_hm),
                        writing_starts=_writing_starts,
                        tables=_tables)

    assembled = _assemble_with(segments_by_page)
    if _court_hm and not assembled.opinions:
        trace.event("court.claim_no_writing",
                    "; ".join(assembled.warnings[:3]) or "(no warning)")
    # A COURT READER MAY IMPROVE THE HEADMATTER, NEVER COST THE DOCUMENT ITS
    # WRITINGS. A claim removes lines from the stream, and on a record whose
    # body anchors on something inside the claim that leaves nothing to open
    # the writing on. Where that happens the claim is withdrawn whole and
    # core reads the document as it would have without a court file — a
    # headmatter read beautifully is worth nothing beside a lost opinion.
    # …but a document that EXPECTS no body has not lost anything by having
    # none. An errata sheet or a notice is all headmatter, and withdrawing a
    # correct reading from it threw away every row (ca1's five notice
    # records rendered with an empty headmatter).
    _body_expected = meta.doc_type not in m.NO_BODY_EXPECTED
    if (_court_hm and not assembled.opinions and _segments_unclaimed
            and _body_expected):
        # First try RELEASING THE ANCHOR the reader claimed — a doc-type
        # heading the court prints ('SUMMARY ORDER') is both a headmatter row
        # and the only thing an unsigned writing can open on. Released, the
        # headmatter loses one row; withheld, the document loses its opinion.
        _anchor = set(_court_hm.get("anchor_ids") or ())
        if _anchor:
            from .resolve.segments import Segment as _SegA
            _relaxed = {}
            for _pg, _sgs in _segments_unclaimed.items():
                _keep = []
                for _sg in _sgs:
                    _ls = [l for l in _sg.lines
                           if l.id in _anchor or l.id not in _claimed]
                    if _ls:
                        _keep.append(_SegA(_sg.page, _ls, _sg.kind))
                _relaxed[_pg] = _keep
            _try2 = _assemble_with(_relaxed)
            if _try2.opinions:
                trace.event("court.anchor_released",
                            "doc-type heading returned to the stream")
                segments_by_page.clear()
                segments_by_page.update(_relaxed)
                assembled = _try2
        _retry = _assemble_with(_segments_unclaimed) \
            if not assembled.opinions else assembled
        if not assembled.opinions and _retry.opinions:
            trace.event("court.reader_withdrawn",
                        "claim cost the document its writings")
            segments_by_page.clear()
            segments_by_page.update(_segments_unclaimed)
            assembled = _retry
            _court_hm = None
    doc.opinions = assembled.opinions
    # ONE PAPER, ONE WRITING, where the court declares it (see
    # CourtProfile.single_writing). Only writings that AGREE about their
    # author are folded: a genuine second author is left standing and
    # visible, because a fold that swallowed one would be the same content
    # loss the split is.
    if profile is not None and getattr(profile, "single_writing", False) \
            and len(doc.opinions) > 1:
        _names = {(o.author or "").strip() for o in doc.opinions}
        _names.discard("")
        if len(_names) <= 1:
            _lead = doc.opinions[0]
            for _extra in doc.opinions[1:]:
                # A FOLD MOVES THE WHOLE WRITING, NOT ONLY ITS BLOCKS. The
                # spurious writing this fold exists to absorb can hold its
                # content ANYWHERE — nywd/162352.3.0 signs its order on a
                # sheet of its own, so the tail writing opened on page 4
                # held nothing but a signature ('Dated: May 22, 2026 /
                # Rochester, New York'), and taking `.blocks` alone dropped
                # those three rows on the floor: unplaced, unrecorded, and
                # counted by the sweep below as lost content (the user,
                # 2026-08-23: 'got an f why did we lose residuals').
                #
                # The signature joins the BODY, not `_lead.signature`: the
                # district lift below prepends the rows it finds on the last
                # page, which would print the bench's name above the dateline
                # the page sets under it. In the body it keeps the page's own
                # order, at the end of the writing where it was printed.
                _lead.blocks.extend(_extra.blocks)
                _lead.blocks.extend(_extra.signature)
                _lead.footnotes.extend(_extra.footnotes)
                if not _lead.caption:
                    _lead.caption = list(_extra.caption)
                if not _lead.author and _extra.author:
                    _lead.author = _extra.author
            doc.opinions = [_lead]
    doc.dropped.extend(assembled.dropped)
    doc.headmatter_footnotes = assembled.headmatter_footnotes
    doc.warnings.extend(
        w for w in assembled.warnings
        if not (w == "no opinion start found"
                and meta.doc_type in m.NO_BODY_EXPECTED))

    # 8 headmatter — the segments before the first opinion, with two
    # section splits made at SEGMENT level:
    # - counsel: a segment naming representation ('…for the appellant',
    #   'on brief', 'Attorneys for…', 'COUNSEL OF RECORD') is the attorneys
    #   section, whatever court printed it;
    # - syllabus: a multi-line prose run set a clear step SMALLER than the
    #   body before the opinion starts (Connecticut's 8pt syllabus against
    #   an 11pt body) — measured, not configured.
    from .resolve.assemble import _segment_blocks
    # STRONG marks are representation VERBS/labels — they never occur as
    # ordinary prose. WEAK marks ('for the defendant') appear in syllabus
    # prose too, so they only vouch for SHORT blocks (nj's syllabus
    # paragraphs were classifying as counsel on 'for the defendant').
    _COUNSEL_STRONG = ("on brief", "on the brief", "attorneys for",
                       "attorney for", "counsel of record", "appearances",
                       "argued the cause", "appearing for", "pro se,",
                       ", pro se", "no appearance for",
                       "self-represented litigant")
    _COUNSEL_WEAK = ("for the appell", "for appell", "for the pet",
                     "for petition", "for the respond", "for respond",
                     "for plaintiff", "for the plaintiff", "for defendant",
                     "for the defendant", "counsel for")
    _COUNSEL_MARKS = _COUNSEL_STRONG + _COUNSEL_WEAK
    # Publisher boilerplate (Connecticut's slip cover: release-date rules,
    # modification notice, Secretary of the State copyright). A multi-line
    # run hitting TWO OR MORE cues is the notice; the one-line 'officially
    # released <date>' row hits one and survives (it carries the decision
    # date).
    _NOTICE_CUES = ("officially released", "subject to modification",
                    "advance release version", "copyrighted by the secretary",
                    "may not be reproduced", "official legal publications",
                    "in the event of discrepancies",
                    # the reporter-notice family confirmed by the notice
                    # sweep (ala/scotus/ohio/ga/mich/mass/ri/dc/alaska/wis):
                    "subject to formal revision", "reporter of decisions",
                    "advance sheet", "typographical", "formal errors",
                    "constitutes no part of the opinion", "detroit timber",
                    "superseded by the", "subject to further editing",
                    "bound volume", "readers are requested",
                    "before publication in",
                    # nj's syllabus clerk note
                    "prepared by the office of the clerk",
                    "may not summarize all portions",
                    # cal's uncertified-opinion rule
                    "prohibits courts and parties",
                    "not certified for publication",
                    # ca2's summary-order rules block
                    "do not have precedential effect",
                    "must serve a copy",
                    # fla's finality notice
                    "not final until time expires",
                    "disposition thereof if timely filed")
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE. Lifting it into a
    # section of its own leaves a hole in the block the render is supposed to
    # reproduce — the appearances vanish from where the page puts them and
    # reappear somewhere else. Their MEANING is copied into criteria instead.
    # The one exception is a court that prints its roster BELOW the writings
    # (ca3's order form); there the roster is not part of the headmatter at
    # all, and `counsel_after_writings` says so.
    _counsel_texts: list[str] = []
    hm_pages: dict[int, list] = {}
    for _cp, _csegs in _cover_lines.items():
        for _cs in _csegs:
            hm_pages.setdefault(_cp, []).extend(_cs.lines)
    history_txt: list[str] = []
    hm_mode = None
    _sum_target = None
    # bands of notice drops (page, top, bottom, x0) — a notice split across
    # segments loses its cue quorum per piece; adjacency reunites it.
    _notice_bands: list[tuple] = []
    _recital_date_found: list[str] = []
    # PUBLICATION STATUS: the cover states it outright — record it as
    # criteria (the row itself stays where the page put it).
    _PUB = ("certified for publication", "for publication",
            "to be published", "publish")
    _UNPUB = ("not to be published", "not for publication",
              "not designated for publication", "unpublished",
              "non-precedential", "do not publish",
              "not certified for publication")
    _pub_status = None
    for pm in model.pages[:2]:
        if _pub_status:
            break
        for line in pm.lines:
            low = " ".join(line.plain.split()).lower().strip(" .*†‡")
            # A STATUS IS A STATEMENT ABOUT THIS PAPER. A sentence that
            # CITES ANOTHER DECISION is about that one instead: mich's
            # Reporter syllabus recites the court below's 'unpublished per
            # curiam opinion issued on …' (17 of mich's 50 PUBLISHED slips
            # came back unpublished), idaho's majority cites 'State v.
            # Borek, No. 49021, 2022 WL 4295418', wis cites an 'unpublished
            # order at 5-10'. Length is NOT the discriminator — ca5 states
            # its own status in 70 characters ('* This opinion is not
            # designated for publication. See 5th Cir. R. 47.5.') and that
            # one is true.
            if len(low) > 200 or _STATUS_CITES_ANOTHER.search(low):
                continue
            if any(low.startswith(u) or u in low[:60] for u in _UNPUB):
                _pub_status = "unpublished"
                break
            if any(low == p0 or low.startswith(p0 + " in")
                   for p0 in _PUB) or low == "publish":
                _pub_status = "published"
                break

    # A counsel COLUMN's continuation may segment separately (guam's right
    # column runs two rows past the left, markless): a following segment
    # whose lines all sit on one of the counsel segment's column edges,
    # within a couple of leads, is the same block.
    from .resolve.segments import Segment as _SegM
    _msegs: list = []
    for seg in assembled.headmatter_segments:
        if _msegs:
            prev = _msegs[-1]
            ptext = " ".join(l.plain for l in prev.lines).lower()
            pxs = {round(p.x0) for p in prev.lines}
            if (seg.page == prev.page
                    and any(mk in ptext for mk in _COUNSEL_MARKS)
                    and seg.lines[0].top - max(p.top for p in prev.lines)
                        <= 2.2 * (geom.lead if geom else 16.0)
                    and all(any(abs(l.x0 - px) <= 3 for px in pxs)
                            for l in seg.lines)):
                _msegs[-1] = _SegM(prev.page, list(prev.lines) + list(seg.lines),
                                   prev.kind)
                continue
            # FORWARD address merge: an appearance runs on as short
            # address rows ('[ARGUED] / J. Chris White / Clark Hill /
            # 1400 Wewatta Street / Suite 550 / Denver, Colorado 80202' —
            # ca3's front roster mixes marked and unmarked rows).
            from .resolve.headmatter import find_date as _fd0
            _seg_one = " ".join(
                " ".join(l.plain.split()) for l in seg.lines).strip()
            _is_date_row = (len(seg.lines) == 1 and len(_seg_one) <= 34
                            and _fd0(_seg_one) is not None)
            ptext2 = " ".join(l.plain for l in prev.lines).lower()
            _adjacent = (not _is_date_row and seg.page == prev.page
                         and seg.lines[0].top
                             - max(p.top for p in prev.lines)
                             <= 2.5 * (geom.lead if geom else 16.0))
            # …or the block WRAPS the page: continuation opens the next
            # page's top (ca2's 'FOR RESPONDENT:' roster runs on).
            _wraps = (seg.page == prev.page + 1
                      and seg.lines[0].top
                          < model.pages[seg.page - 1].height * 0.22)
            if ((_adjacent or _wraps)
                    and (any(mk in ptext2 for mk in _COUNSEL_MARKS)
                         or "[argued]" in ptext2)
                    and all(len(l.plain.strip()) <= 55 for l in seg.lines)
                    and len(seg.lines) <= 8
                    and (any(c.isdigit() for c in " ".join(
                            l.plain for l in seg.lines))
                         or "[argued]" in " ".join(
                            l.plain for l in seg.lines).lower()
                         # an address tail may be digit-free ('…Civil
                         # Division, United / States Department of
                         # Justice, Washington, DC.')
                         or sum(l.plain.count(",") for l in seg.lines) >= 2)
                    and not any(
                        l.plain.strip().rstrip(".").isupper()
                        and len(l.plain.strip()) > 3 for l in seg.lines)):
                _msegs[-1] = _SegM(prev.page,
                                   list(prev.lines) + list(seg.lines),
                                   prev.kind)
                continue
            # BACKWARD merge: a counsel segment OPENING mid-sentence owns
            # the torn first line(s) above it — nh wraps 'Rath, Young…
            # (Adam Pignatelli on the / brief and orally), for the
            # petitioner.' and the marks all sit on the continuation. The
            # torn edge shows as the PREVIOUS line ending mid-clause — a
            # trailing INITIAL ('…Graham W.') is not a sentence terminal
            # (nh ortolano's continuation opens on a capitalized surname).
            def _open_edge(s: str) -> bool:
                if not s:
                    return False
                if not s.endswith((".", ":", ";", "”", '"', ")")):
                    return True
                return bool(len(s) >= 2 and s.endswith(".")
                            and s[-2].isupper()
                            and (len(s) == 2 or not s[-3].isalpha()))
            stext = " ".join(l.plain for l in seg.lines).lower()
            first = seg.lines[0].plain.strip()
            plast = prev.lines[-1].plain.strip()
            if (seg.page == prev.page
                    and (any(mk in stext for mk in _COUNSEL_MARKS)
                         # ANY mid-sentence opening under an open edge is
                         # the same tear (ca2 griffin's disposition
                         # paragraph split half-into-headmatter)
                         or first[:1].islower())
                    and plast and not plast.endswith((":", ";"))
                    and _open_edge(plast)
                    and len(prev.lines) <= 4
                    and seg.lines[0].top - max(p.top for p in prev.lines)
                        <= 2.2 * (geom.lead if geom else 16.0)):
                merged = _SegM(prev.page,
                               list(prev.lines) + list(seg.lines),
                               seg.kind)
                _msegs[-1] = merged
                # CHAIN back: the paragraph may wrap over SEVERAL markless
                # lines ('Upton & Hatfield… on the / memorandum of law) and
                # City of Nashua…, of / Nashua (…' — nh); keep absorbing
                # open-edged short neighbors above.
                while (len(_msegs) >= 2
                       and len(merged.lines) <= 8
                       and _msegs[-2].page == merged.page
                       and len(_msegs[-2].lines) <= 4
                       and _open_edge(
                           _msegs[-2].lines[-1].plain.strip())
                       and merged.lines[0].top
                           - max(p.top for p in _msegs[-2].lines)
                           <= 2.2 * (geom.lead if geom else 16.0)):
                    merged = _SegM(merged.page,
                                   list(_msegs[-2].lines) + list(merged.lines),
                                   merged.kind)
                    _msegs[-2:] = [merged]
                continue
        _msegs.append(seg)

    # A syllabus paragraph may OPEN on the caption page and break onto the
    # first SYLLABUS page mid-sentence (ca2 verplanck): the unterminated
    # tail before the syllabus belongs to the syllabus.
    _syl_pull: set[int] = set()
    # …and the PROSE-branch variant: a full-measure syllabus paragraph
    # opening lowercase under an open-edged paragraph half (the page break
    # tore one syllabus paragraph in two). Only where the court LABELED a
    # syllabus page — otherwise this is ordinary body prose (ca5's en banc
    # majority was pulled into a fabricated syllabus).
    for _a, _b in zip(_msegs, _msegs[1:]) if _syl_pages else ():
        if not geom or _b.page - _a.page > 1 or len(_b.lines) < 4:
            continue
        if sum(l.width for l in _b.lines) / len(_b.lines) \
                < 0.75 * geom.column:
            continue
        _bj = " ".join(l.plain.strip() for l in _b.lines).strip()
        _bfirst = _b.lines[0].plain.strip()
        _alast = _a.lines[-1].plain.strip()
        if (_bj[-1:] in '.!?”"' and _bfirst[:1].islower()
                and len(_a.lines) >= 3
                and sum(l.width for l in _a.lines) / len(_a.lines)
                    >= 0.6 * geom.column
                and _alast and not _alast.endswith(
                    (".", ":", "!", "?", "”", '"', ";"))):
            _syl_pull.add(id(_a))
    if _syl_pages:
        _P = min(_syl_pages)
        _prevsegs = [s for s in _msegs if s.page == _P - 1]
        _nextsegs = [s for s in _msegs if s.page == _P]
        if _prevsegs and _nextsegs:
            _plast = _prevsegs[-1].lines[-1].plain.strip()
            _nfirst = next((l.plain.strip() for s in _nextsegs
                            for l in s.lines if l.plain.strip()), "")
            if (_nfirst[:1].islower() and _plast
                    and not _plast.endswith(
                        (".", ":", "!", "?", '"', "”", ";"))):
                _syl_pull.add(id(_prevsegs[-1]))

    # Cover apparatus a court prints AGAIN at the head of its opinion: the
    # court names those rows, core drops them (after mining their criteria).
    _syl_drop = court_decides("syllabus.trim", court_id, trace,
                              segs=_msegs, syl_pages=_syl_pages)
    if _syl_drop is NOTHING:
        _syl_drop = set()
    # The court's own UNSIGNED writing: a disposition that stands between the
    # caption and the first byline is the Court speaking, not a caption row.
    _order_segs = court_decides("writing.unsigned", court_id, trace,
                                segs=_msegs, syl_pages=_syl_pages,
                                is_byline=lambda t: bool(parser.parse(t)))
    if _order_segs is NOTHING:
        _order_segs = set()
    _order_blocks: list = []

    for seg in _msegs:
        text = " ".join(l.plain for l in seg.lines).lower()
        plain_one = " ".join(text.split())
        # A STANDALONE publication-status banner is removed content — the
        # fact lives in criteria ('CERTIFIED FOR PUBLICATION' — calctapp).
        _one = plain_one.strip(" .*†‡")
        if len(seg.lines) <= 2 and len(_one) < 80 and (
                any(_one.startswith(u) for u in _UNPUB)
                or any(_one == p0 or _one.startswith(p0 + " in")
                       for p0 in _PUB)):
            doc.dropped.append(m.Dropped(
                text=" ".join(l.plain.strip() for l in seg.lines),
                prov=m.Prov(seg.page, tuple(l.id for l in seg.lines)),
                kind="status"))
            continue
        if len(seg.lines) >= 2 and sum(
                1 for cue in _NOTICE_CUES if cue in text) >= 2:
            doc.dropped.append(m.Dropped(
                text=" ".join(l.plain.strip() for l in seg.lines)[:1200],
                prov=m.Prov(seg.page, tuple(l.id for l in seg.lines)),
                kind="notice"))
            _notice_bands.append((seg.page,
                                  min(l.top for l in seg.lines),
                                  max(l.top for l in seg.lines),
                                  min(l.x0 for l in seg.lines)))
            continue
        if _order_segs and any(l.id in _order_segs for l in seg.lines):
            # The closing caption row and the disposition it introduces may
            # share a segment — take the order LINES and leave the rest of
            # the segment to the headmatter it belongs to.
            _olines = [l for l in seg.lines if l.id in _order_segs]
            _ohead = [l for l in seg.lines if l.id not in _order_segs]
            if _ohead:
                hm_pages.setdefault(seg.page, []).extend(_ohead)
            from .resolve.segments import Segment as _SegOrd
            _order_blocks.extend(_segment_blocks(
                _SegOrd(seg.page, _olines, "body"), segmenter, vocab))
            continue
        # A segment on a SYLLABUS page is syllabus flow, wherever its shape
        # would otherwise route it (nj cover pages rendered as 120 hmrows).
        if seg.page in _syl_pages or id(seg) in _syl_pull:
            if id(seg) in _syl_drop:
                # Dropped from the render, but still read for criteria
                # below — the cover states facts the reprint omits.
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in seg.lines),
                    prov=m.Prov(seg.page, tuple(l.id for l in seg.lines)),
                    kind="superfluous"))
                continue
            # An INSET paragraph in syllabus flow is still a paragraph —
            # the same fact conn's wholly-inset syllabus proves below; the
            # cover's first paragraph measures narrower than the rules over
            # it and the segmenter types it a quote.
            doc.syllabus.extend(
                m.Paragraph(text=b.text, prov=b.prov)
                if isinstance(b, m.Blockquote) else b
                for b in _segment_blocks(seg, segmenter, vocab,
                                         inset_flow=True))
            continue
        # The CONVENING RECITAL ('At a stated term of the United States
        # Court of Appeals…, on the 10th day of June, two thousand
        # twenty-six.') is formal apparatus carrying the DECISION DATE —
        # ca2's summary orders state it nowhere else (v1 lesson).
        if plain_one.lower().startswith("at a stated term"):
            from .resolve.headmatter import recital_date as _rd
            # The segmenter may glue the NEXT block's first line onto the
            # recital ('PRESENT: …' rode along) — the recital ends at its
            # own terminal sentence.
            _cut = len(seg.lines)
            _acc = ""
            for _i, _l in enumerate(seg.lines):
                _acc += " " + _l.plain
                if "day of" in _acc.lower() \
                        and _l.plain.strip().endswith("."):
                    _cut = _i + 1
                    break
            _head, _rest = seg.lines[:_cut], seg.lines[_cut:]
            _d = _rd(" ".join(l.plain.strip() for l in _head))
            if _d and doc.criteria.decision_date is None:
                _recital_date_found.append(_d)
            doc.dropped.append(m.Dropped(
                text=" ".join(l.plain.strip() for l in _head)[:400],
                prov=m.Prov(seg.page, tuple(l.id for l in _head)),
                kind="recital"))
            if _rest:
                hm_pages.setdefault(seg.page, []).extend(_rest)
            continue
        # 'Procedural History' (Connecticut's syllabus apparatus): the run
        # under the heading is the case's prior history.
        if plain_one.rstrip(" :") == "procedural history":
            hm_mode = "history"
            doc.syllabus.extend(_segment_blocks(seg, segmenter, vocab))
            continue
        # A STANDALONE DATE ROW is the decision date wherever the court
        # sets it — ca1 prints it under the counsel block, below a clear
        # separator; it is never an appearance. (Not while a labeled
        # section is open: its prose owns the run.)
        if hm_mode is None and len(seg.lines) == 1 and len(plain_one) <= 34:
            from .resolve.headmatter import find_date as _fd1
            _dt1 = _fd1(plain_one)
            if _dt1 and _dt1.lower() == plain_one.strip().lower():
                if doc.criteria.decision_date is None:
                    doc.criteria.decision_date = _dt1
                    _recital_date_found.append(_dt1)
                hm_pages.setdefault(seg.page, []).extend(seg.lines)
                continue
        # A 'COUNSEL' / 'APPEARANCES' SECTION HEADING is the court's own
        # signal (arizctapp prints it over the roster): everything under
        # it is attorneys until the next heading.
        if plain_one.rstrip(" :").upper() in (
                "COUNSEL", "APPEARANCES", "ATTORNEYS",
                "COUNSEL OF RECORD", "ATTORNEYS AND LAW FIRMS"):
            # The court's own COUNSEL heading stays in the headmatter with
            # the roster it heads — both are printed there.
            hm_mode = "counsel"
            _counsel_texts.append(" ".join(
                l.plain.strip() for l in seg.lines))
            hm_pages.setdefault(seg.page, []).extend(seg.lines)
            continue
        # A 'SUMMARY' / 'SYLLABUS' SECTION HEADING (ca9 sets its staff
        # summary under a bold 'SUMMARY*'): everything under it is the
        # syllabus until the next section heading.
        _band_now = sig.get("band") or (0.0, 0.0)
        _fm_kind = plain_one.rstrip(" :*†‡∗⁎﹡＊").lower()
        if (_fm_kind in profile.front_matter
                # only a heading BELOW the caption opens a section (ca9's
                # SUMMARY after the roster); scotus's page-1 'Syllabus'
                # TITLE above the caption is the cover's own apparatus.
                and (seg.page > 1 or seg.lines[0].top > _band_now[1])):
            hm_mode = "syllabus"
            # the section carries the COURT'S OWN LABEL: 'SUMMARY' is a
            # staff summary, 'SYLLABUS' the formal syllabus
            _sum_target = (doc.summary if _fm_kind == "summary"
                           else doc.syllabus)
            _sum_target.append(m.Heading(
                text=" ".join(l.plain.strip() for l in seg.lines),
                prov=m.Prov(seg.page, tuple(l.id for l in seg.lines))))
            continue
        if hm_mode == "syllabus":
            if seg.kind == "separator":
                hm_pages.setdefault(seg.page, []).extend(seg.lines)
                continue
            _letters2 = [c for c in plain_one if c.isalpha()]
            # a CAPS row closes the section only if it is a section
            # heading — a running head ('REGES V. CAUCE') is furniture
            # that survived, and a party line is not a heading
            _looks_head = (_letters2 and all(c.isupper() for c in _letters2)
                           and len(plain_one) < 60
                           and " v. " not in plain_one.lower()
                           and " v " not in plain_one.lower())
            # A section heading names what FOLLOWS: 'OPINION' (the body),
            # 'COUNSEL' (the roster). Anything else — including a caps
            # topic line inside the summary — keeps the summary open.
            _closer = plain_one.rstrip(" :*†‡∗⁎﹡＊").upper() in (
                "OPINION", "ORDER", "MEMORANDUM", "PER CURIAM",
                "OPINION OF THE COURT", "COUNSEL", "APPEARANCES")
            # A counsel mark closes the section only from a SHORT block:
            # summary prose says 'judgment for defendant' in passing.
            _counselish = (len(plain_one) <= 400
                           and any(mk in text for mk in _COUNSEL_MARKS))
            if (_closer
                    or text.startswith(("counsel", "appearances"))
                    or _counselish):
                hm_mode = None   # falls through to the counsel routing
            else:
                _sum_target.extend(
                    m.Paragraph(text=b.text, prov=b.prov)
                    if isinstance(b, m.Blockquote) else b
                    for b in _segment_blocks(seg, segmenter, vocab))
                continue
        if hm_mode == "counsel":
            if seg.kind == "separator":
                # a typed rule inside the roster is the page's own divider
                hm_pages.setdefault(seg.page, []).extend(seg.lines)
                continue
            _letters = [c for c in plain_one if c.isalpha()]
            _capsish = _letters and all(
                c.isupper() for c in _letters) and len(plain_one) < 60
            if _capsish or plain_one.lower().startswith(
                    ("before", "present")):
                hm_mode = None   # the next heading/roster ends the section
            else:
                doc.attorneys.extend(
                    _segment_blocks(seg, segmenter, vocab))
                continue
        _weak_hits = sum(1 for mark in _COUNSEL_WEAK if mark in text)
        is_counsel = (any(mark in text for mark in _COUNSEL_STRONG)
                      or (_weak_hits and len(plain_one) <= 300)
                      # TWO distinct weak marks is a roster whatever its
                      # length ('…for Plaintiffs and Appellants.' + '…for
                      # Defendant and Appellant…' — calctapp's block).
                      or _weak_hits >= 2)
        # A DISTRIBUTION line is not an appearance ('Dated: … cc: All
        # Counsel of Record' — the clerk's routing note).
        import re as _rcc
        if is_counsel and (_rcc.search(r"\bcc\s*:", text)
                           or "all counsel of record" in text):
            is_counsel = False
        # …and a brief CITATION is not an appearance (see the trailing
        # roster pass below): weak marks alone cannot carry a block whose
        # role phrase belongs to 'Brief for Respondent 26.'
        if (is_counsel and not any(mk in text for mk in _COUNSEL_STRONG)
                and _rcc.search(r"\bbriefs?\s+(?:for|of)\b|"
                                r"\breply\s+brief\b", text)):
            is_counsel = False
        if hm_mode == "history" and not is_counsel and len(plain_one) > 40:
            doc.syllabus.extend(_segment_blocks(seg, segmenter, vocab))
            from .audit import strip_tags, unescape_xml
            history_txt.append(unescape_xml(strip_tags(
                " ".join(l.plain.strip() for l in seg.lines))))
            continue
        if hm_mode == "history":
            hm_mode = None   # history mode ends at its first non-match
        if is_counsel:
            # PEEL leading history sentences off the counsel block: NJ sets
            # 'On appeal from the Superior Court…, Docket No. L-4133-23.'
            # in the same segment as 'X argued the cause for appellant…' —
            # the appeal-from line is PRIOR HISTORY, never counsel.
            _LEADS = ("on appeal from", "appeal from", "on certification",
                      "before judge")
            def _terminated(s: str) -> bool:
                # '…Tamara L.' ends on an INITIAL, not a sentence — the
                # appeal-from wrap continues ('Mosbarger, Judge.').
                if not s.endswith("."):
                    return False
                return not (len(s) >= 2 and s[-2].isupper()
                            and (len(s) == 2 or not s[-3].isalpha()))
            lines = list(seg.lines)
            peeled = []
            while lines:
                head = " ".join(lines[0].plain.split())
                if not head.lower().startswith(_LEADS) and not (
                        peeled and not _terminated(" ".join(
                            peeled[-1].plain.split()))):
                    break
                peeled.append(lines.pop(0))
            if peeled:
                hm_pages.setdefault(seg.page, []).extend(peeled)
                from .audit import strip_tags, unescape_xml
                history_txt.append(unescape_xml(strip_tags(
                    " ".join(l.plain.strip() for l in peeled))))
            # And LINE-LEVEL: a panel roster or a bare disposition inside
            # the counsel segment ('Before MCLEESE and SHANKER, Associate
            # Judges…' — dc; 'Affirmed.' — conn) is never counsel.
            _kept = []
            _roster_open = False
            # a TYPED RULE fencing the block belongs to the page's
            # furniture, not to the roster text (ca6 fences COUNSEL with
            # '________' above and below)
            from .pdfio.rules import is_typed_rule as _itr
            _rules_out = [_l for _l in lines if _itr(_l.plain.strip())]
            _no_rules = [_l for _l in lines if not _itr(_l.plain.strip())]
            if _no_rules:
                # the fence renders where the page drew it — never dropped
                hm_pages.setdefault(seg.page, []).extend(_rules_out)
                lines = _no_rules
            for _l in lines:
                _one = " ".join(_l.plain.split())
                _lw = _one.lower()
                # A roster may WRAP across rows ('Before' / 'Montecalvo,
                # Thompson, and Aframe,' / 'Circuit Judges.' — ca1): the
                # opener starts it, a judicial-title row closes it.
                if _roster_open:
                    hm_pages.setdefault(seg.page, []).append(_l)
                    if (_one.rstrip().endswith(".")
                            or _lw.rstrip(".").endswith(
                                ("judges", "justices", "judge", "justice",
                                 "jj", "j"))):
                        _roster_open = False
                    continue
                if (_lw.startswith(("before judge", "before the honorable",
                                    "before:"))
                        or (_lw.startswith("before ") and len(_one) <= 95
                            and _one.rstrip().endswith("."))):
                    hm_pages.setdefault(seg.page, []).append(_l)
                    continue
                if _lw.rstrip(":") == "before" or (
                        _lw.startswith("before ") and len(_one) <= 95
                        and not _one.rstrip().endswith(".")):
                    hm_pages.setdefault(seg.page, []).append(_l)
                    _roster_open = True
                    continue
                if _lw.rstrip(".") in ("affirmed", "reversed", "vacated",
                                       "dismissed", "dismissal affirmed",
                                       "reversed; further proceedings"):
                    history_txt.append(_one)
                    hm_pages.setdefault(seg.page, []).append(_l)
                    continue
                _kept.append(_l)
            lines = _column_order(_kept)
            if lines is not _kept:
                # Columns fired: an ADDRESS ROSTER sets one fact per line
                # ('Vincent Leon Guerrero, Esq.' / 'Attorney at Law' / …) —
                # paragraph-joining garbles it (guam); render line-per-line.
                from .resolve.footnotes import line_markup as _lm
                _counsel_texts.extend(
                    _lm(l).strip() for l in lines if _lm(l).strip())
                hm_pages.setdefault(seg.page, []).extend(lines)
            elif lines:
                from .resolve.segments import Segment as _Seg
                _counsel_texts.extend(
                    " ".join(l.plain.split()) for l in lines
                    if l.plain.strip())
                hm_pages.setdefault(seg.page, []).extend(lines)
            continue
        cap_band = sig.get("band") or (0.0, 0.0)
        in_cap_band = (seg.page == 1
                       and any(cap_band[0] - 4 <= l.top <= cap_band[1] + 4
                               for l in seg.lines))
        if (geom and len(seg.lines) >= 3 and not in_cap_band
                and all(l.size <= geom.body_size - 1.5 for l in seg.lines)
                and sum(l.width for l in seg.lines) / len(seg.lines)
                    >= 0.5 * geom.column
                # sub-body type is the evidence, but only BEFORE the body
                # begins: a labeled page, or no writing found yet
                and (seg.page in _syl_pages
                     # Where the court LABELS its syllabus pages, the label
                     # is the boundary — reduced type on an UNLABELED page is
                     # the writing's own headmatter (scotus reprints banner,
                     # docket, caption and date at the head of each writing),
                     # never a continuation of the syllabus.
                     or (not _syl_pages
                         and (not assembled.opinions
                              or seg.page <= min((o.blocks[0].prov.page
                                                  for o in assembled.opinions
                                                  if o.blocks),
                                                 default=10**6))))):
            # conn's whole syllabus is INSET, so the segmenter types its
            # headnote paragraphs as blockquotes — in sub-body syllabus
            # flow an indented paragraph is just a paragraph.
            doc.syllabus.extend(
                m.Paragraph(text=b.text, prov=b.prov)
                if isinstance(b, m.Blockquote) else b
                for b in _segment_blocks(seg, segmenter, vocab,
                                         inset_flow=True))
            continue
        # A BODY-SIZE court-written summary: a full-measure PROSE run in the
        # front matter (tenn sets its syllabus at body size between the
        # docket rules and the disposition). Prose, not caption: ≥4 lines
        # averaging ≥75% of the measure, closing on sentence punctuation.
        joined = " ".join(l.plain.strip() for l in seg.lines).strip()
        if (geom and len(seg.lines) >= 4 and not in_cap_band
                and sum(l.width for l in seg.lines) / len(seg.lines)
                    >= 0.75 * geom.column
                and joined[-1:] in ".!?”\""):
            # UNLABELED front prose is a SUMMARY only on a page the court
            # LABELED (syllabus/summary page); otherwise it is the body,
            # and inventing a section for it hides a missed opinion start
            # (ca5's en banc majority landed in a fabricated summary).
            if seg.page in _syl_pages or id(seg) in _syl_pull:
                (doc.syllabus if seg.page in _syl_pages
                 else doc.summary).extend(
                    _segment_blocks(seg, segmenter, vocab))
                continue
        hm_pages.setdefault(seg.page, []).extend(seg.lines)
    # The unsigned disposition opens the document's writings: the signed
    # opinions that follow it concur in or dissent FROM it.
    if _order_blocks:
        doc.opinions.insert(0, m.Opinion(
            type="per curiam", author="",
            author_prov=m.Prov(_order_blocks[0].prov.page),
            blocks=_order_blocks))
    # LINE-LEVEL notice peel: a notice set inside the caption band never
    # reaches the segment check above (mich's syllabus note sits between
    # masthead rows). Group hm lines by top-proximity AND shared left edge
    # (so a letterhead's right column can't be swept up), and drop any
    # multi-line group hitting two cues.
    for pg, pg_lines in hm_pages.items():
        groups: list[list] = []
        for l in sorted(pg_lines, key=lambda l: (l.top, l.x0)):
            # last COMPATIBLE group: an interleaved right-column row (the
            # letterhead beside mich's note) must not break the run.
            for g in reversed(groups):
                if (l.top - g[-1].top <= 24
                        and abs(l.x0 - g[0].x0) <= 40) or (
                        # a row-mate CONTINUATION cell ('NOTICE:' + ' This
                        # opinion is subject…' split at the label) joins its
                        # row; a distant letterhead cell (gap > 50) does not.
                        l.top - g[-1].top < 2
                        and 0 <= l.x0 - g[-1].x1 <= 50) or (
                        # a BOX centers its rows (ca10's FILED stamp):
                        # shared center axis, looser leading.
                        l.top - g[-1].top <= 34
                        and abs((l.x0 + l.x1) - (g[0].x0 + g[0].x1)) <= 40):
                    g.append(l)
                    break
            else:
                groups.append([l])
        def _is_stamp_group(g: list) -> bool:
            # A filing-stamp BLOCK: short rows only, anchored by
            # 'Electronically Filed' (haw's e-file header) or a bare
            # 'FILED' row plus a 'Clerk of Court' row (ca10's margin box).
            if len(g) < 3 or any(len(l.plain.strip()) > 48 for l in g):
                return False
            gt = " ".join(l.plain for l in g).lower()
            if "electronically filed" in gt:
                return True
            has_filed = any(l.plain.strip().rstrip(":").upper() == "FILED"
                            for l in g)
            return has_filed and "clerk of court" in gt

        held: list[list] = []
        for g in groups:
            gt = " ".join(l.plain for l in g).lower()
            cues = sum(1 for cue in _NOTICE_CUES if cue in gt)
            if _is_stamp_group(g):
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in g)[:1200],
                    prov=m.Prov(pg, tuple(l.id for l in g)),
                    kind="stamp"))
                hm_pages[pg] = [l for l in hm_pages[pg] if l not in g]
            elif len(g) >= 2 and cues >= 2:
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in g)[:1200],
                    prov=m.Prov(pg, tuple(l.id for l in g)),
                    kind="notice"))
                _notice_bands.append((pg, min(l.top for l in g),
                                      max(l.top for l in g),
                                      min(l.x0 for l in g)))
                hm_pages[pg] = [l for l in hm_pages[pg] if l not in g]
            elif len(g) >= 2 and cues >= 1:
                held.append(g)
        # A 1-cue multi-line group ABUTTING a dropped notice (same left
        # edge, within a leading or two) is the notice's other half — ri's
        # 'NOTICE: This opinion is subject to formal revision' row sits in
        # the caption segment while its tail dropped at segment level.
        for g in held:
            g_top = min(l.top for l in g)
            g_bot = max(l.top for l in g)
            g_x0 = min(l.x0 for l in g)
            if any(p == pg and abs(g_x0 - x0) <= 40
                   and (abs(g_top - bot) <= 28 or abs(top - g_bot) <= 28)
                   for p, top, bot, x0 in _notice_bands):
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in g)[:1200],
                    prov=m.Prov(pg, tuple(l.id for l in g)),
                    kind="notice"))
                hm_pages[pg] = [l for l in hm_pages[pg] if l not in g]
    span = [(pm, hm_pages[pm.number]) for pm in model.pages
            if pm.number in hm_pages]
    if _court_hm:
        # The court read its own headmatter — publish it verbatim.
        doc.headmatter = list(_court_hm.get("items") or [])
        for _k, _v in (_court_hm.get("criteria") or {}).items():
            setattr(doc.criteria, _k, _v)
        doc.attorneys.extend(_court_hm.get("attorneys") or [])
        doc.dropped.extend(_court_hm.get("dropped") or [])
        doc.summary.extend(_court_hm.get("summary") or [])
        # THE SIGNATURE BAND A COURT READ ITSELF. Declared on the model
        # and in sections.py since the section list existed, but never
        # written: every court's /s/ run was opinion body prose, so
        # md lost its signing judge and me lost five of them. A court
        # that reads the band must be able to hand it over, or the
        # choice is between deleting it and printing it twice.
        doc.signature.extend(_court_hm.get("signature") or [])
        # …and ANY HEADMATTER LINE THE READER DID NOT TAKE still gets placed
        # by the shared walk. A court reader states what it recognizes; what
        # it passes over is not thereby junk, and dropping the shared walk
        # entirely orphaned those lines into residual content (ca2's counsel
        # continuations on page 2, an immigration caption the ladder does not
        # cover). The court's CRITERIA stand — only placement is topped up.
        if span:
            _rest = read_headmatter(span, sig, cap_style, geom, trace,
                                    court_id,
                                    caption_wraps=profile.caption_wraps)
            doc.headmatter.extend(_rest.items)
    elif span:
        hm = read_headmatter(span, sig, cap_style, geom, trace, court_id,
                             caption_wraps=profile.caption_wraps)
        doc.headmatter = hm.items
        doc.criteria = hm.criteria
    if _recital_date_found and doc.criteria.decision_date is None:
        doc.criteria.decision_date = _recital_date_found[0]
    if _slug_docket and doc.criteria.docket_number is None:
        doc.criteria.docket_number = _slug_docket[0]
    if _slug_case and not doc.criteria.parties:
        _sides = [x.strip() for x in _slug_case[0].split(" v. ") if x.strip()]
        if len(_sides) == 2:
            doc.criteria.parties = _sides
    if _pub_status and doc.criteria.publication_status is None:
        doc.criteria.publication_status = _pub_status
    # Page-break tears inside the SYLLABUS flow: a continuation coming
    # back as a Blockquote (an indented rail reads as a quote) or a
    # lowercase Paragraph is the SAME paragraph (conn splits its syllabus
    # at every page turn).
    for _sec_name in ("syllabus", "summary"):
      doc_sec = getattr(doc, _sec_name)
      if doc_sec:
        from .audit import strip_tags as _st3
        _mg: list = []
        for _b in doc_sec:
            _prev_txt = (_st3(getattr(_mg[-1], "text", "") or "").rstrip()
                         if _mg and isinstance(_mg[-1], m.Paragraph) else "")
            _nxt_txt = (_st3(getattr(_b, "text", "") or "").lstrip()
                        if isinstance(_b, (m.Paragraph, m.Blockquote))
                        and getattr(_b, "text", None) else "")
            # A closing quote is terminal only if the sentence ended
            # INSIDE it: 'so ordered.”' closes, 'an “inchoate offense,”'
            # does not — the comma is the page turn's own evidence that
            # the sentence runs on (scotus tears mid-quotation).
            _end = _prev_txt[-1:]
            _terminal = (_end in '.!?:;'
                         or (_end in '"”’'
                             and _prev_txt[-2:-1] not in ',;'))
            if (_prev_txt and _nxt_txt and not _terminal
                    and _nxt_txt[:1].islower()):
                _pv = _mg[-1]
                _mg[-1] = m.Paragraph(
                    text=_pv.text.rstrip() + " " + _b.text.lstrip(),
                    prov=m.Prov(_pv.prov.page,
                                tuple(_pv.prov.line_ids)
                                + tuple(_b.prov.line_ids)))
            else:
                _mg.append(_b)
        setattr(doc, _sec_name, _mg)

    # Criteria the SYLLABUS pages carry (nj's cover holds the docket and
    # the argued/decided line; those pages bypass read_headmatter).
    if doc.syllabus or doc.summary:
        import re as _re2
        from .audit import strip_tags as _st2
        from .resolve.headmatter import date_row_value as _drv
        from .resolve.headmatter import find_date as _fd2
        from .resolve.headmatter import looks_like_docket as _ld2
        _re_syl = _re2.compile(r"\(([A-Z]{1,2}-\d{1,4}-\d{2,4})\)")
        _crit_rows = [getattr(b, "text", "") or ""
                      for b in (list(doc.syllabus) + list(doc.summary))[:60]]
        # A cover row dropped as SUPERFLUOUS still speaks: where the court
        # reprints its caption at the head of the opinion, the reprint omits
        # the argued date, which the cover states once (scotus).
        _crit_rows += [dp.text for dp in doc.dropped
                       if dp.kind == "superfluous"]
        for _row_text in _crit_rows:
            t = " ".join(_st2(_row_text).split())
            if not t:
                continue
            low = t.lower()
            # the released date may sit INSIDE a long syllabus paragraph
            # (conn joins 'Argued January 13—officially released
            # February 17, 2026*' into the flow)
            if (doc.criteria.decision_date is None
                    and "officially released" in low):
                d = _fd2(t[low.index("officially released"):][:80])
                if d:
                    doc.criteria.decision_date = d
            if len(t) > 300:
                continue
            if doc.criteria.docket_number is None:
                mm = _re_syl.search(t)
                if mm:
                    doc.criteria.docket_number = mm.group(1)
                else:
                    d0 = _ld2(t)
                    if d0:
                        doc.criteria.docket_number = d0
            if doc.criteria.decision_date is None:
                d = _drv(t) or (_fd2(t[low.index("decided"):])
                                if "decided" in low else None)
                if d:
                    doc.criteria.decision_date = d
            if doc.criteria.submitted is None and "argued" in low:
                d = _fd2(t[low.index("argued"):low.index("decided")
                           if "decided" in low else len(t)])
                if d:
                    doc.criteria.submitted = d
    # DISPOSITION marker: ca9 closes the majority with a bold standalone
    # 'REMANDED.' / 'AFFIRMED in part…' — keep it in the opinion, mark it,
    # and publish it as criteria for downstream parsing.
    _DISPO_LEADS = ("AFFIRMED", "REVERSED", "REMANDED", "VACATED",
                    "DISMISSED", "GRANTED", "DENIED", "PETITION")
    if doc.opinions:
        from .audit import strip_tags as _std
        for _op in doc.opinions:
            for _b in _op.blocks[-3:]:
                _t = _std(getattr(_b, "text", "") or "").strip()
                if (_t and len(_t) < 200
                        and _t.split()[0].rstrip(".,;").upper()
                            in _DISPO_LEADS
                        and _t.split()[0].rstrip(".,;").isupper()):
                    try:
                        _b.role = "disposition"
                    except Exception:
                        pass
                    if doc.criteria.disposition is None:
                        doc.criteria.disposition = _t
            break   # the majority only

    # A 'FILED: <date>' stamp row that opened the writing's body (its
    # row-mate byline anchored the writing) carries the DECISION DATE —
    # criteria, not prose.
    if doc.opinions and doc.opinions[0].blocks:
        from .audit import strip_tags as _st1
        from .resolve.headmatter import find_date as _fd
        import re as _re1
        _b0 = doc.opinions[0].blocks[0]
        _t0 = _st1(getattr(_b0, "text", "") or "").strip()
        if len(_t0) < 45 and _re1.match(r"^FILED\b[:\s]", _t0, _re1.I):
            _d = _fd(_t0)
            if _d:
                if doc.criteria.decision_date is None:
                    doc.criteria.decision_date = _d
                doc.dropped.append(m.Dropped(
                    text=_t0, prov=_b0.prov, kind="stamp"))
                doc.opinions[0].blocks.pop(0)

    # THE COURT'S SEAL, at the head of the headmatter where the page prints
    # it. `HmItem` already admits an ImageBlock and `render_hm_items` already
    # draws one, so this needs no new machinery — only the right destination.
    if _mastheads:
        import base64 as _mb64
        import io as _mio
        import pdfplumber as _mpp
        try:
            with _mpp.open(str(pdf_path)) as _mpdf:
                for _im in sorted(_mastheads, key=lambda i: i.top):
                    _mpg = _mpdf.pages[_im.page - 1]
                    _mcrop = _mpg.crop((max(0, _im.x0 - 2), max(0, _im.top - 2),
                                        min(_mpg.width, _im.x1 + 2),
                                        min(_mpg.height, _im.bottom + 2)))
                    _mbuf = _mio.BytesIO()
                    _mcrop.to_image(resolution=150).original.save(_mbuf, "PNG")
                    doc.headmatter.insert(0, m.ImageBlock(
                        src=("data:image/png;base64,"
                             + _mb64.b64encode(_mbuf.getvalue()).decode()),
                        prov=m.Prov(_im.page),
                        width=_im.x1 - _im.x0, height=_im.bottom - _im.top,
                        role="seal"))
        except Exception:
            # a seal is not worth failing a document over
            for _im in _mastheads:
                doc.dropped.append(m.Dropped(
                    text=(f"seal {_im.x1 - _im.x0:.0f}×"
                          f"{_im.bottom - _im.top:.0f}pt (uncropped)"),
                    prov=m.Prov(_im.page), kind="image",
                    bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))

    # CONTENT FIGURES: crop each body image from the page and place it in
    # the writing at its reading position (adidas's trademark exhibits are
    # part of the opinion; v1 carried them, so do we).
    if _figures and doc.opinions:
        import base64 as _b64
        import io as _io
        import pdfplumber as _pp
        _line_top = {l.id: l.top for pm2 in model.pages for l in pm2.lines}
        with _pp.open(str(pdf_path)) as _pdf:
            for _im in _figures:
                try:
                    _pg = _pdf.pages[_im.page - 1]
                    _crop = _pg.crop((max(0, _im.x0 - 2),
                                      max(0, _im.top - 2),
                                      min(_pg.width, _im.x1 + 2),
                                      min(_pg.height, _im.bottom + 2)))
                    _pil = _crop.to_image(resolution=150).original
                    _buf = _io.BytesIO()
                    _pil.save(_buf, "PNG")
                except Exception:
                    continue
                _src = ("data:image/png;base64,"
                        + _b64.b64encode(_buf.getvalue()).decode())
                _blk = m.ImageBlock(src=_src, prov=m.Prov(_im.page),
                                    width=_im.x1 - _im.x0,
                                    height=_im.bottom - _im.top,
                                    role="figure")
                # the writing whose blocks surround the figure's position
                _placed = False
                for _op in doc.opinions:
                    _pgs = [b.prov.page for b in _op.blocks
                            if getattr(b, "prov", None)]
                    if not _pgs or not (min(_pgs) <= _im.page <= max(_pgs)):
                        continue
                    _at = len(_op.blocks)
                    for _k, _b in enumerate(_op.blocks):
                        _bpg = getattr(_b.prov, "page", 0)
                        _bt = min((_line_top.get(i, 0)
                                   for i in getattr(_b.prov, "line_ids", ())),
                                  default=0)
                        if _bpg > _im.page or (_bpg == _im.page
                                               and _bt > _im.top):
                            _at = _k
                            break
                    _op.blocks.insert(_at, _blk)
                    _placed = True
                    break
                if not _placed:
                    doc.dropped.append(m.Dropped(
                        text=(f"figure {_im.x1 - _im.x0:.0f}×"
                              f"{_im.bottom - _im.top:.0f}pt (unplaced)"),
                        prov=m.Prov(_im.page), kind="image",
                        bbox=(_im.x0, _im.top, _im.x1, _im.bottom)))

    # THE COURT'S SIGNATURE, WHERE IT IS A PICTURE. An ECF order is signed
    # with a stamp, not with type: kyed's last page carries 293x79pt of image
    # below the body and its text layer holds no 'Signed By', no 'District
    # Judge' and no judge's name at all — 22 of its 25 records are image-only
    # (2 have text, 1 has neither). Dropped as furniture, the signature
    # disappeared from the document entirely. `Opinion.signature` and
    # `ImageBlock.role="signature-graphic"` both already exist, and the
    # renderer draws an ImageBlock, so the graphic renders where the page
    # puts it — under the writing it signs, with the date line that belongs
    # to it. Only an image standing BELOW the body's last row on the LAST
    # page qualifies: anything higher is a figure the opinion discusses.
    if doc.opinions and _sig_imgs:
        import base64 as _sb64
        import io as _sio
        import pdfplumber as _spp
        _last = doc.opinions[-1]
        # THE ATTESTATION BELONGS TO THE BLOCK IT OPENS. Where the bench
        # signs with graphics alone and types no names under them, 'WE
        # CONCUR:' is the writing's last block and the signatures follow it
        # — so the attestation reads as a dangling one-line paragraph at the
        # foot of the opinion (wash/in_re_det._of_m.e., 8 graphics).
        _sig_x0 = {l.id: l.x0 for _pm3 in model.pages for l in _pm3.lines}

        def _signer_row(_b) -> bool:
            _t = " ".join(((getattr(_b, "text", "") or "")
                           .replace("<strong>", "").replace("</strong>", "")
                           ).split())
            if _t.upper().rstrip(":.") in ("WE CONCUR", "I CONCUR",
                                          "WE DISSENT", "BY THE COURT",
                                          "FOR THE COURT"):
                return True
            if not _t or len(_t) > 60:
                return False
            # …and the typed NAME beside a graphic, set in the signers'
            # column. Only reached where this writing was signed by hand,
            # so a short right-set line here is a signer and nothing else.
            _xs = [_sig_x0[i] for i in
                   getattr(getattr(_b, "prov", None), "line_ids", ())
                   if i in _sig_x0]
            return bool(_xs) and min(_xs) > model.pages[0].width * 0.42

        while _last.blocks and _signer_row(_last.blocks[-1]):
            _last.signature.insert(0, _last.blocks.pop())
        try:
            with _spp.open(str(pdf_path)) as _spdf:
                for _im in _sig_imgs:
                    _sp = _spdf.pages[_im.page - 1]
                    _sc = _sp.crop((max(0, _im.x0 - 2), max(0, _im.top - 2),
                                    min(_sp.width, _im.x1 + 2),
                                    min(_sp.height, _im.bottom + 2)))
                    _sb = _sio.BytesIO()
                    _sc.to_image(resolution=150).original.save(_sb, "PNG")
                    _last.signature.append(m.ImageBlock(
                        src=("data:image/png;base64,"
                             + _sb64.b64encode(_sb.getvalue()).decode()),
                        prov=m.Prov(_im.page),
                        width=_im.x1 - _im.x0, height=_im.bottom - _im.top,
                        role="signature-graphic"))
        except Exception:
            for _im in _sig_imgs:
                doc.dropped.append(m.Dropped(
                    text=(f"signature graphic {_im.x1 - _im.x0:.0f}×"
                          f"{_im.bottom - _im.top:.0f}pt (uncropped)"),
                    prov=m.Prov(_im.page), kind="signature"))

    # WHERE THE COURT SAYS ITS SIGNATURE BEGINS. Most papers sign with a
    # '/s/' or a drawn line and the shared lift below finds them; a few close
    # on a DATE LINE with the names typed under it and an attestation after,
    # and nothing in the shape says where the decision stopped and the
    # signing started. A court that can point at the row says so here, and
    # everything from that row to the end of the writing is its signature —
    # the block itself, the concurrences, and the clerk's certificate.
    _sig_at = court_decides("signature.opens", court_id, trace,
                            model=model, geom=geom)
    if _sig_at is not NOTHING and _sig_at and doc.opinions:
        _sig_pos = {l.id: (pm.number, l.top)
                    for pm in model.pages for l in pm.lines}

        def _blk_at(b):
            pts = [_sig_pos[i] for i in
                   getattr(getattr(b, "prov", None), "line_ids", ())
                   if i in _sig_pos]
            return min(pts) if pts else None

        for _op in doc.opinions:
            _cut = None
            for _k, _b in enumerate(_op.blocks):
                _at = _blk_at(_b)
                if _at is not None and _at >= tuple(_sig_at):
                    _cut = _k
                    break
            if _cut is not None:
                _op.signature = _op.blocks[_cut:] + list(_op.signature)
                _op.blocks = _op.blocks[:_cut]

    # A GRAPHIC AT THE END OF A WRITING IS ITS SIGNATURE. The last-page rule
    # above cannot see the others: a court that signs EVERY writing signs the
    # lead opinion in the middle of the file, so those graphics fall to the
    # figure placement and are planted as the writing's last blocks. What
    # tells them apart is what follows them — a figure the opinion discusses
    # has text after it, and a signature has nothing. Measured on wash, whose
    # justices sign each writing by hand.
    for _op in doc.opinions:
        _moved = []
        while _op.blocks and isinstance(_op.blocks[-1], m.ImageBlock):
            _blk2 = _op.blocks.pop()
            _blk2.role = "signature-graphic"
            _moved.insert(0, _blk2)
        if _moved:
            _op.signature = _moved + list(_op.signature)

    # SIGNATURE GRAPHIC: pasuperct closes with 'Judgment Entered.' as an
    # IMAGE (prothonotary stamp + signature) over a bare typed date. The
    # image never renders; the orphan date must not read as body. Stash
    # both as a surfaced removal — the record says what stood there.
    if doc.opinions:
        import re as _re
        _last_op = doc.opinions[-1]
        while _last_op.blocks:
            _lb = _last_op.blocks[-1]
            _txt = (getattr(_lb, "text", "") or "").strip()
            if not _re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", _txt):
                break
            _pg = _lb.prov.page
            _imgs = [im for im in model.pages[_pg - 1].images
                     if (im.x1 - im.x0) >= 40 and abs(im.x1 - im.x0) < 400]
            if not _imgs:
                break
            _im = _imgs[-1]
            doc.dropped.append(m.Dropped(
                text=(f"signature graphic {_im.x1 - _im.x0:.0f}×"
                      f"{_im.bottom - _im.top:.0f}pt · dated {_txt}"),
                prov=m.Prov(_pg, tuple(_lb.prov.line_ids)),
                kind="signature"))
            _last_op.blocks.pop()

    # LEADING counsel: nd sets the roster between the byline and the ¶1
    # body — strong-marked blocks at the writing's HEAD are appearances.
    if doc.opinions:
        from .audit import strip_tags as _st0
        _first = doc.opinions[0]
        while _first.blocks:
            lw = " ".join(_st0(getattr(_first.blocks[0], "text", "")
                               or "").split()).lower()
            # …and the mark must sit in the block's CLOSING span, the same
            # rule the trailing roster uses. `_COUNSEL_STRONG` contains
            # 'pro se,', and a per curiam that opens 'Proceeding pro se,
            # Reyes-Recalde argues…' matched it on its first paragraph — so
            # the writing's opening was lifted out of the opinion and filed
            # as an appearance.
            # …and the closing span was NOT enough. ca11 opens a per curiam
            # 'Derhem, pro se on appeal, raises various arguments in support
            # of reversal.  None of them have merit, so we affirm.' — the
            # mark sits in the last 120 characters, so the writing's opening
            # was still lifted out and filed as an appearance. 'pro se'
            # describes a PARTY; every other strong mark is a representation
            # LABEL, and a roster the court prints above the body always
            # names counsel with one of those. So the leading lift does not
            # get to use it. (The TRAILING roster still may — there the row
            # is the roster, not a paragraph of the opinion.)
            _HEAD_MARKS = tuple(mk for mk in _COUNSEL_STRONG
                                if "pro se" not in mk)
            if (len(lw) <= 400
                    and any(mk in lw[-120:] for mk in _HEAD_MARKS)):
                # An appearance printed above the body is HEADMATTER, and
                # that is where it renders — not in a section of its own.
                # Its text is copied into criteria like any other counsel.
                _b0 = _first.blocks.pop(0)
                doc.headmatter.append(m.HmLine(
                    text=getattr(_b0, "text", ""), prov=_b0.prov,
                    role="counsel"))
                # The BLOCK's own text, not `lw` — `lw` is the lowercased
                # working copy the marks are matched against, and appending
                # it published every one of these appearances in lower case
                # ('kiara c. kraus-parr, grand forks, nd, for petitioner').
                _counsel_texts.append(getattr(_b0, "text", "") or lw)
            else:
                break

    # TRAILING counsel: fla/ind/ohio print the appearance roster AFTER the
    # last writing — same counsel test, different address. The roster mixes
    # marked lines with address blocks ('Indianapolis, Indiana'), so harvest
    # the WINDOW from the first strong hit to the end, not a strict walk.
    def _hm_rows(blocks):
        """The moved blocks re-read as the rows the page actually printed.
        Returns [] when provenance cannot place them, and the caller keeps
        the blocks — a roster rendered as paragraphs is worse than one
        rendered as rows, but both beat losing it."""
        _by_id = {l.id: (pm, l) for pm in model.pages for l in pm.lines}
        out = []
        for _b in blocks:
            _ids = getattr(getattr(_b, "prov", None), "line_ids", ()) or ()
            _got = [_by_id[i] for i in _ids if i in _by_id]
            if not _got:
                return []
            for _pm, _l in _got:
                _row = _hm_line(_l, _pm, geom)
                _row.role = "counsel"
                out.append(_row)
        return out

    for _last in doc.opinions:
        from .audit import strip_tags as _st
        # A TRAILING NOTICE is publisher apparatus wherever it prints. The
        # headmatter sweep never reaches it because fla sets its finality
        # notice on the LAST page, under the counsel roster. Same two-cue
        # evidence bar, applied to the tail.
        # The notice is ONE printed run that may set as several short
        # lines, each carrying a single cue ('NOT FINAL UNTIL TIME EXPIRES
        # TO FILE MOTION FOR REHEARING' / 'AND DISPOSITION THEREOF IF
        # TIMELY FILED'), so the two-cue bar is read across the run.
        # The run is exactly the trailing blocks that EACH carry a cue —
        # so it stops at the first real line above it (a counsel entry) —
        # and the run as a whole must clear the two-cue bar.
        _n = 0
        while _n < min(4, len(_last.blocks)):
            _t = _st(getattr(_last.blocks[-1 - _n], "text", "") or "")
            _tl = " ".join(_t.split()).lower()
            if len(_t) > 200 or not any(c in _tl for c in _NOTICE_CUES):
                break
            _n += 1
        if _n:
            _tail = _last.blocks[-_n:]
            _txts = [_st(getattr(b, "text", "") or "") for b in _tail]
            _joined = " ".join(" ".join(t.split()) for t in _txts).lower()
            if sum(1 for c in _NOTICE_CUES if c in _joined) >= 2:
                for _b, _t2 in zip(_tail, _txts):
                    doc.dropped.append(m.Dropped(
                        text=_t2, prov=getattr(_b, "prov", m.Prov(1)),
                        kind="notice"))
                del _last.blocks[-_n:]
        _win = _last.blocks[-12:] if profile.counsel_after_writings else []
        _lows = [" ".join(_st(getattr(b, "text", "") or "").split()).lower()
                 for b in _win]
        # 'Counsel for Appellant' and '[Argued]' count as strong HERE —
        # the trailing window is already positional evidence (ca3 lists
        # counsel after the writings in that form).
        # A counsel entry CLOSES on the party it represents (fla: '…of
        # Banker Lopez Gassler, P.A., Tampa, …, for Appellant.'). The role
        # must END the block: body prose says 'for the defendant' mid
        # sentence all the time, and matching that swept ca6's conclusion
        # paragraph and a me footnote into the attorney list.
        # The role a roster entry closes on. Matched as WHOLE WORDS: a
        # substring test on 'for the state' also matches an opinion's own
        # last sentence, 'For the stated reasons, we will affirm.', and
        # byjus_alpha published its disposition as an appearance — the
        # writing's closing line lifted out of the writing.
        _ROLE_TAIL = _re.compile(
            r"for (?:appellant|appellee|petitioner|respondent|plaintiff"
            r"|defendant|real party in interest|the state"
            r"|amicus curiae|amici curiae|amicus|amici|intervenor)s?\b")
        # A CITATION TO A PARTY'S BRIEF is an authority, never an
        # appearance: an opinion closes a paragraph 'Brief for Respondent
        # 26.' or 'Reply Brief for Petitioner 4' as often as a roster
        # closes an entry ', for Respondent.', and the role tail cannot
        # tell them apart. The citation forms are the veto — applied only
        # where the role tail is the ONLY evidence, so a real entry
        # ('…, on the briefs for appellant') still hits on its strong mark.
        import re as _rcc
        _CITE_FORM = _rcc.compile(
            r"\bbriefs?\s+(?:for|of)\b|\breply\s+brief\b"
            r"|\btr\.\s*of\s*oral\s*arg"
            # '…for Respondent 26.' — a page cite closes it, not a party
            r"|\bfor\s+(?:the\s+)?[a-z]+s?\s+\d+(?:[-–]\d+)?\s*$")
        # A CLERK'S DISTRIBUTION NOTE IS NOT AN APPEARANCE. 'Dated: March 2,
        # 2026  Amr/Cc: All counsel of record' names no one who argued
        # anything — it says who was sent a copy. Core already vetoes it
        # where counsel is routed in the headmatter; the trailing roster,
        # which only ca3 enables, never got the same veto and published the
        # note as ca3's attorneys section.
        _DISTRIB = ("cc:", "all counsel of record", "counsel of record.",
                    "/cc:", "dated:")
        # …and a note vetoed here is REMOVED, not left behind. Vetoing it
        # only stopped it being published as counsel; the block stayed in
        # the writing, where the clerk's copy list and its page numerals
        # then read as counsel-in-body and folio leaks.
        for _k, _lw in enumerate(_lows):
            if any(_d in _lw for _d in _DISTRIB) and len(_lw) <= 400:
                _b = _win[_k]
                if _b in _last.blocks:
                    doc.dropped.append(m.Dropped(
                        text=_st(getattr(_b, "text", "") or "")[:400],
                        prov=getattr(_b, "prov", m.Prov(1)),
                        kind="distribution"))
                    _last.blocks.remove(_b)
        _hits = [k for k, lw in enumerate(_lows)
                 if not any(d in lw for d in _DISTRIB)
                 # …in the entry's CLOSING span. Unbounded, 'counsel for'
                 # matched 651 characters of opinion prose — 'Wilcox faults
                 # appellate counsel for not arguing that…' — which dragged
                 # the body back into the roster and the length cap then
                 # vetoed the whole harvest. The leading lift has always
                 # confined its marks this way; this path did not.
                 and any(mk in lw[-120:] for mk in
                         _COUNSEL_STRONG + ("counsel for", "[argued]"))
                 # the role sits in the entry's CLOSING span, not mid
                 # sentence ('…, for Plaintiff and Appellants.')
                 or (_ROLE_TAIL.search(lw.rstrip(". ")[-46:])
                     and not _CITE_FORM.search(lw.rstrip(". ")))]
        if not profile.counsel_after_writings:
            _probe = _os_env.environ.get("CENTRALIA_COUNSEL_PROBE")
            if _probe:
                _plows = [" ".join(_st(getattr(b, "text", "") or "").split())
                          .lower() for b in _last.blocks[-12:]]
                _ph = [k for k, lw in enumerate(_plows)
                       if any(mk in lw for mk in
                              _COUNSEL_STRONG + ("counsel for", "[argued]"))]
                if _ph:
                    with open(_probe, "a") as _fh:
                        _fh.write(f"{court_id}\t{pdf_path}\t"
                                  f"{_plows[_ph[0]][:80]}\n")
        if _hits and (len(_win) - 1 - _hits[-1]) <= 4:
            # The roster ENDS at its last marked entry, plus any short
            # continuation rows (a firm's second address line). Running to
            # the end of the document instead swept a me footnote and a
            # ca6 conclusion paragraph in behind the counsel.
            _end = _hits[-1]
            while (_end + 1 < len(_win)
                   and len(_st(getattr(_win[_end + 1], "text", "")
                               or "")) <= 120):
                _end += 1
            _base = len(_last.blocks) - len(_win)
            _start, _stop = _base + _hits[0], _base + _end + 1
            _moved = _last.blocks[_start:_stop]
            # 600, not 400: fla sets a single 458-character appearance, and
            # one over-long entry vetoed the roster for the whole record.
            if all(len(_st(getattr(b, "text", "") or "")) <= 600
                   for b in _moved):
                del _last.blocks[_start:_stop]
                # WHERE THE PAGE PRINTS IT. A roster the court sets BELOW
                # its writings belongs after them, and `attorneys` renders
                # at order 40 — ahead of the opinions — so publishing it
                # there hoists the end of the document to the top. `trailer`
                # (order 70) is the section that keeps the page's order.
                # Its text is copied into criteria like any other counsel.
                # …AS THE PAGE PRINTS IT. The roster is a list of rows —
                # a name, a firm, an address — and assembly had welded them
                # into paragraphs ('Melissa Bayly Christopher J. Dalton
                # [Argued] Argia J. DiMarco BUCHANAN INGERSOLL & ROONEY').
                # Headmatter keeps every printed row; the endmatter is the
                # same kind of matter and is rebuilt the same way, one
                # HmLine per source line, so both read alike.
                _rows = _hm_rows(_moved)
                doc.attorneys.extend(_rows or _moved)
                _counsel_texts.extend(
                    _st(getattr(b, "text", "") or "") for b in _moved)

    if _counsel_texts and doc.criteria.attorneys is None:
        from .audit import strip_tags as _sta, unescape_xml as _uxa
        doc.criteria.attorneys = " ".join(
            _uxa(_sta(t)) for t in _counsel_texts if t.strip())[:2000]
    if doc.attorneys and doc.criteria.attorneys is None:
        from .audit import strip_tags, unescape_xml
        doc.criteria.attorneys = " ".join(
            unescape_xml(strip_tags(getattr(b, "text", "")))
            for b in doc.attorneys if getattr(b, "text", ""))[:2000]
    if history_txt and doc.criteria.history is None:
        doc.criteria.history = " ".join(history_txt)[:2000]

    # A court that read its own headmatter also knows what KIND of paper it
    # is. Applied HERE, after the writings are built: the doc-type heading
    # is what anchors an unsigned writing, so the type cannot be declared
    # before assembly without removing the anchor that finds the body. An
    # unsigned lead writing typed 'order' by that heading is the court's
    # opinion when the court says the paper is one.
    if _court_hm and _court_hm.get("doc_type_final") is not None:
        meta.doc_type = _court_hm["doc_type_final"]
        if (meta.doc_type is m.DocType.OPINION and doc.opinions
                and doc.opinions[0].type == "order"
                and not doc.opinions[0].author_name):
            doc.opinions[0].type = "majority"

    # THE PAPER'S OWN NAME TYPES ITS WRITING. A separately published
    # concurrence or dissent NAMES itself ('CONCURRING STATEMENT',
    # 'DISSENTING OPINION') and then signs itself with a bare byline carrying
    # no kind clause ('JUSTICE WECHT'), so `normalize_opinion_type(None)`
    # returned 'majority' and the writing rendered as the court's opinion:
    # pa/wentz_m._v._wentz_d._1 is a concurring statement that came out a
    # majority. Where the court names the paper a concurrence or a dissent and
    # the writing carries no kind of its own, the title is the better
    # evidence.
    #
    # Only on a paper with ONE writing. A sandwich record titles itself
    # 'OPINION' and types each writing off its own byline, which is right;
    # this is for the slip that IS the separate writing.
    _paper = (doc.criteria.title or "").strip().lower()
    if (_paper and len(doc.opinions) == 1
            and doc.opinions[0].type in ("majority", "order")
            and ("concur" in _paper or "dissent" in _paper)):
        from .resolve.bylines import normalize_opinion_type as _not
        doc.opinions[0].type = _not(_paper)

    # A court that ANNOUNCES its author in the caption instead of SIGNING the
    # writing ('OPINION BY' over 'JUSTICE JUNIUS P. FULTON, III' in va's
    # caption right column) leaves core no byline to build from: core's
    # `_opinion_by` wants the label and the name on ONE line, and the
    # headmatter renders whole so nothing may be lifted out of it. The reader
    # reports what the caption announced; core parses it with the court's own
    # grammar and signs the LEAD writing — only where the document prints no
    # byline of its own, which always outranks an announcement. 44 of va's 50
    # records came back with an unauthored writing without this.
    _ann = _court_hm.get("announced_author") if _court_hm else None
    if _ann and doc.opinions and not doc.opinions[0].author_name:
        _by = parser.parse(_ann)
        if _by is not None:
            _lead = doc.opinions[0]
            _lead.author = _ann
            _lead.author_name = _by.name
            _lead.author_title = _by.title
            # …BUT A COURT THAT PRINTS ONE WRITING HAS NO MAJORITY. Where
            # the court declares `single_writing` — a judge ruling alone, the
            # whole federal district lane and a few state trial courts — the
            # paper's own name for itself stands. An ORDER credited to the
            # judge who wrote it is still an order, and 'majority' would
            # invent a bench for it to be the majority of. The flip is for
            # the appellate case this clause was written for, where an
            # announced author IS the court speaking (va, tenn).
            # …AND A COURT THAT ANNOUNCES 'PER CURIAM' HAS NAMED THE
            # WRITING, not a judge. Flipped to 'majority' the paper lost the
            # one thing its byline actually said (texcrimapp/wenzel_1, whose
            # vote row opens 'Per curiam.').
            from .resolve.bylines import is_per_curiam as _ipc
            if _ipc(_ann.split(".")[0].upper() + "."):
                _lead.type = "per-curiam"
            elif _lead.type in ("order", "opinion") \
                    and not getattr(profile, "single_writing", False):
                _lead.type = "majority"

    # HEADMATTER KEEPS THE PAGE'S ORDER. A court reader claims some rows
    # and the shared walk places the rest; appending one set after the other
    # rearranges the block, which is exactly what the render must not do.
    # Sort by where the page prints each row — the only thing that ever
    # moves is a footnote, which is lifted deliberately.
    if _court_hm:
        _ordpos = {l.id: (pm.number, l.top)
                   for pm in model.pages for l in pm.lines}

        def _row_at(it):
            prov = getattr(it, "prov", None)
            pts = [_ordpos[i] for i in (prov.line_ids if prov else ())
                   if i in _ordpos]
            return min(pts) if pts else None

        # AN ITEM WITH NO LINE PROVENANCE KEEPS ITS PLACE. A seal is an
        # ImageBlock, not a line, and it is inserted at index 0 because that
        # is where the page prints it — but a sentinel sort key sank it to the
        # FOOT of every claimed headmatter that has one (mo 49/50, nd 50/50).
        # A drawn Rule has the same problem. So an id-less item inherits the
        # position of the row it stands beside: the one after it where there
        # is one, otherwise the one before. `sorted` is stable, so it keeps
        # the side of that neighbour it was emitted on.
        _keys = [_row_at(i) for i in doc.headmatter]
        for _k in range(len(_keys) - 2, -1, -1):
            if _keys[_k] is None:
                _keys[_k] = _keys[_k + 1]
        for _k in range(len(_keys)):
            if _keys[_k] is None:
                _keys[_k] = _keys[_k - 1] if _k else (0, -1.0)
        doc.headmatter = [doc.headmatter[i] for i in sorted(
            range(len(doc.headmatter)), key=lambda i: _keys[i])]

    # …and the mirror of the bisection rule: WHERE A READER CLAIMED THE
    # HEADMATTER, AN UNREAD ROW BELOW IT IS THE WRITING'S. The reader stops
    # at the court's own prose, so a row it did not identify that sits after
    # the last row it did — and before the first writing — is the opening of
    # that writing, left behind because assembly anchored deeper in the
    # document (hampton stranded 52 rows above its majority).
    if _court_hm and doc.opinions and doc.opinions[0].blocks:
        _pos0 = {l.id: (pm.number, l.top)
                 for pm in model.pages for l in pm.lines}

        def _at(obj):
            prov = getattr(obj, "prov", None)
            pts = [_pos0[i] for i in (prov.line_ids if prov else ())
                   if i in _pos0]
            return min(pts) if pts else None

        _tagged = [_at(i) for i in doc.headmatter if getattr(i, "role", "")]
        _tagged = [p for p in _tagged if p]
        _op0 = _at(doc.opinions[0].blocks[0])
        if _tagged and _op0:
            _last_read = max(_tagged)
            _moved, _kept = [], []
            for _it in doc.headmatter:
                _p = _at(_it)
                if (not getattr(_it, "role", "") and _p
                        and _last_read < _p < _op0
                        and not isinstance(_it, (m.Rule, m.CaptionBlock))):
                    _moved.append((_p, _it))
                else:
                    _kept.append(_it)
            if _moved:
                _moved.sort(key=lambda x: x[0])
                doc.opinions[0].blocks[:0] = [
                    m.Paragraph(text=getattr(i, "text", ""), prov=i.prov)
                    for _, i in _moved]
                doc.headmatter = _kept
                trace.event("court.body_reclaimed",
                            f"{len(_moved)} rows below the read headmatter")

    # THE AIR BETWEEN THE HEADMATTER'S OWN GROUPS. A court divides its
    # cover with blank lines as often as with rules — ca6 sets a line of air
    # above 'Decided and Filed:' and above 'Before: SILER, MOORE, …' — and a
    # reader that keeps only the rows loses the grouping the page states.
    # The pitch is the document's own: the modal gap between consecutive
    # headmatter rows (8.7pt on that record), and anything appreciably wider
    # is air the page left. Recorded in units of that pitch so a renderer can
    # honour it at any type size, and only for rows whose provenance says
    # where they stood — a two-column caption is one item and takes its air
    # as a whole.
    if doc.headmatter:
        _hm_pos = {l.id: (l.page, l.top, l.bottom)
                   for pm in model.pages for l in pm.lines}

        def _hm_span(_it):
            _ids = tuple(getattr(getattr(_it, "prov", None), "line_ids", ())
                         or ())
            _ps = [_hm_pos[i] for i in _ids if i in _hm_pos]
            if not _ps:
                return None
            return (min(_ps)[0], min(q[1] for q in _ps),
                    max(q[2] for q in _ps))

        # THE TYPE IS THE RULER, not the other gaps. Measured against the
        # median gap this found nothing at all: a cover with four spaced
        # groups has as many wide gaps as tight ones, so the median sat at
        # 12.5pt on a page whose rows are 8.7pt apart and every gap looked
        # ordinary. A row's own size does not move: consecutive rows of 12pt
        # type leave ~0.7 of a size between them, and a blank line adds a
        # whole one.
        _spans = [_hm_span(_it) for _it in doc.headmatter]
        for _i, (_a, _b) in enumerate(zip(_spans, _spans[1:]), start=1):
            _it = doc.headmatter[_i]
            if not (_a and _b) or _a[0] != _b[0] or not hasattr(
                    _it, "space_before"):
                continue
            _size = (getattr(_it, "size", 0.0)
                     or (geom.body_size if geom else 0.0) or 12.0)
            _air = ((_b[1] - _a[2]) - 0.8 * _size) / _size
            if _air >= 0.3:
                _it.space_before = round(min(_air, 3.0), 2)

    # An EMPTY WRITING is not a writing. The rescue anchor can open one at a
    # segment that turns out to hold nothing, and it renders as a phantom
    # 'order' beside the real opinion.
    # …and a note it was holding belongs to the HEADMATTER, which is where
    # the page prints it: campbell's caption note was attached to a phantom
    # writing, so the document showed an empty 'order' and no headmatter
    # footnote at all.
    _empty = [o for o in doc.opinions if not o.blocks and not o.author_name]
    for _o in _empty:
        doc.headmatter_footnotes.extend(_o.footnotes)
    doc.opinions = [o for o in doc.opinions if o.blocks or o.author_name]

    # AN ANNOUNCED AUTHOR NAMES THE PAPER IT STANDS OVER. A court that does
    # not sign its opinions says who wrote them on the cover instead — 'OPINION
    # BY / PRESIDENT JUDGE COHN JUBELIRER' — and a reader that claims that row
    # into the headmatter (which is where the page prints it) leaves the
    # writing beneath it unsigned. `Criteria.author` carries the name; this
    # gives it to the LEAD writing, which is the paper the announcement heads.
    # Only where that writing has no author of its own: a signature it really
    # printed always wins, and every later paper carries its own byline.
    if doc.criteria.author and doc.opinions:
        _lead0 = doc.opinions[0]
        if not (_lead0.author or _lead0.author_name):
            _said = doc.criteria.author
            _lead0.author = _said
            # Reuse the heading parser rather than a second grammar: the form
            # is the tail of the row it came from.
            _pb = BylineParser(profile.byline).parse(f"OPINION BY {_said}")
            if _pb is not None:
                _lead0.author_name = _pb.name
                _lead0.author_title = _pb.title
                if _pb.name == "PER CURIAM":
                    from .resolve.bylines import normalize_opinion_type as _nt2
                    _lead0.type = _nt2("per curiam")
            trace.event("criteria.author_to_lead",
                        f"announced author {_said!r} named the lead writing")

    # …and NEITHER IS A FENCE ON ITS OWN. A court that heads its opinion
    # with its own name ('OPINION OF THE COURT', 'ORDER') prints that name
    # above the byline, and where a page break falls between the two the
    # heading assembles as a writing whose whole content is the heading —
    # schuster came out [majority 'OPINION OF THE COURT'], [majority KRAUSE,
    # …]. The heading is the next writing's opening line, so give it back:
    # fold a heading-only, unbylined writing into the writing below it. A
    # fence that anchors a real unsigned writing carries that writing's
    # prose too, so it is untouched (ca6's 'ORDER' stands as it did).
    _folded = 0
    for _i in range(len(doc.opinions) - 1, -1, -1):
        _o = doc.opinions[_i]
        if _i + 1 >= len(doc.opinions):
            continue
        _nxt = doc.opinions[_i + 1]
        _heading_only = (not _o.author_name and bool(_o.blocks) and all(
            isinstance(b, m.Heading) for b in _o.blocks))
        # …OR AN UNFINISHED RECITAL. cafc's Rule 36 judgment prints
        #
        #     THIS CAUSE having been heard and considered, it is
        #     ORDERED and ADJUDGED:
        #     PER CURIAM (DYK, MAYER, and PROST, Circuit Judges).
        #     AFFIRMED.  See Fed. Cir. R. 36.
        #
        # — ONE paper whose sentence runs straight through the byline, so
        # assembly opened a writing at the recital and another at the
        # byline. The COLON is the evidence: the recital does not end, it
        # continues into the writing below.
        #
        # Deliberately narrow. 'Any short unbylined writing folds down'
        # would destroy scotus, where an unsigned disposition ('The
        # petition for a writ of certiorari is denied.') followed by a
        # dissent is genuinely two writings — that recital ENDS, and a
        # dissent never completes another writing's sentence.
        # The recital's own first row is read as the writing's byline
        # ('THIS CAUSE having been heard and considered, it is'), so the
        # test spans the author row AND the blocks. A real byline carries a
        # bench title; this one carries none, which is the second signal.
        _txt = " ".join([_st(_o.author or "")] +
                        [_st(getattr(b, "text", "") or "")
                         for b in _o.blocks]).strip()
        _recital = (len(_o.blocks) <= 4 and len(_txt) <= 300
                    and _txt.endswith(":") and not _o.author_title
                    and bool(_nxt.author_name)
                    and _nxt.type not in ("dissent", "concurrence"))
        if not (_heading_only or _recital):
            continue
        _lead = list(_o.blocks)
        if _o.author and _st(_o.author).strip():
            # …and its byline row is PROSE. Keep it, at the top, or the
            # judgment loses the sentence it opens with.
            _lead.insert(0, m.Paragraph(text=_o.author, prov=_o.author_prov))
        _nxt.blocks = _lead + list(_nxt.blocks)
        _nxt.footnotes = list(_o.footnotes) + list(_nxt.footnotes)
        del doc.opinions[_i]
        _folded += 1
    if _folded:
        trace.event("writing.fence_folded",
                    f"{_folded} heading-only writing(s) joined the writing "
                    "below")

    # AN EMPTY WRITING IS NOT A WRITING. A byline with no body under it did
    # not open anything — it SIGNED the writing above it. washctapp's stapled
    # order closes 'FOR THE COURT:' over a typed rule with 'MAXA, J.' beneath,
    # and that name, being byline-shaped, opened a third writing holding
    # nothing at all beside the order and the opinion (the user, 2026-08-21:
    # 'it has two … but im getting three'). Refusing the anchor cannot tell
    # this case from cadc's 'Per Curiam' — both are the document's only
    # byline — so the EMPTINESS is what is read, after assembly, when it is
    # known.
    _emptied = 0
    for _i in range(len(doc.opinions) - 1, -1, -1):
        _o = doc.opinions[_i]
        if _o.blocks or _o.signature or _o.footnotes:
            continue
        # …AND ONLY WHERE THERE IS A WRITING ABOVE IT TO SIGN. An empty LEAD
        # writing has signed nothing; dropping it costs the document its
        # majority and its author outright (alaska's democratic_party, whose
        # 'majority, dissent, dissent' came back as two dissents).
        if _i == 0:
            continue
        if _o.author_name and not doc.opinions[_i - 1].author_name:
            _prev = doc.opinions[_i - 1]
            _prev.author = _o.author
            _prev.author_name = _o.author_name
            _prev.author_title = _o.author_title
            _prev.author_prov = _o.author_prov
        del doc.opinions[_i]
        _emptied += 1
    if _emptied:
        trace.event("writing.empty_dropped",
                    f"{_emptied} byline(s) with no body signed the writing "
                    "above instead of opening one")

    # 9b INVARIANT — A WRITING IS NEVER BISECTED.
    #
    # Once a writing is assembled, the text between its first line and its
    # last belongs to it. Any row that some later rule filed as headmatter,
    # attorneys or front matter while sitting INSIDE that span was cut out
    # of the middle of an opinion, and that is always wrong however good the
    # rule's reason looked: callais lost the second half of a per curiam
    # order because one sentence of it ('…the District Court may "oversee an
    # orderly process."') carried two court words and read as a masthead;
    # pung lost a paragraph of a concurrence because it closed on 'Brief for
    # Respondent 26.' and read as an appearance. Both are the same defect,
    # so the repair is stated once, structurally, instead of patched at each
    # rule that can produce it.
    _pos = {l.id: (pm.number, l.top)
            for pm in model.pages for l in pm.lines}

    def _pt(obj):
        prov = getattr(obj, "prov", None)
        pts = [_pos[i] for i in (prov.line_ids if prov else ()) if i in _pos]
        return (min(pts), max(pts)) if pts else None

    _spans = []
    for _op in doc.opinions:
        _pts = [q for b in _op.blocks for q in ([_pt(b)] if _pt(b) else [])]
        if _pts:
            _spans.append((_op, min(p[0] for p in _pts),
                           max(p[1] for p in _pts)))
    if _spans:
        for _sec in ("headmatter", "attorneys", "syllabus", "summary"):
            _kept = []
            for _it in getattr(doc, _sec):
                _p = _pt(_it)
                _home = None
                if _p is not None and not isinstance(_it, (m.Rule,
                                                           m.CaptionBlock)):
                    for _op, _lo, _hi in _spans:
                        if _lo < _p[0] < _hi:
                            _home = _op
                            break
                if _home is None:
                    _kept.append(_it)
                    continue
                # put it back where the page printed it
                _blk = m.Paragraph(text=getattr(_it, "text", ""),
                                   prov=_it.prov)
                _at = len(_home.blocks)
                for _k, _b in enumerate(_home.blocks):
                    _bp = _pt(_b)
                    if _bp and _bp[0] > _p[0]:
                        _at = _k
                        break
                _home.blocks.insert(_at, _blk)
                # A repair that SUCCEEDED is not a parse complaint: recorded
                # in the trace, not in the warnings that gate the file.
                trace.event("invariant.reunited",
                            f"{_sec} row p{_p[0][0]}")
            setattr(doc, _sec, _kept)

    # THE ROW THAT NAMED THE AUTHOR IS PART OF THE DOCUMENT. A district
    # judge closes with a conformed signature — an optional 'DATED:' line,
    # '/s/ Emily C. Marks', the name in capitals, 'UNITED STATES DISTRICT
    # JUDGE' — set right of the measure below the body's last row. The
    # byline reads those rows (the author comes out right) but nothing
    # CLAIMS them, so they reached the sweep below as unaccounted content
    # and demoted the record to `review`: measured on almd, hid, caed and
    # ilcd, four courts whose readings were otherwise clean.
    #
    # Claimed here rather than in a court file because every district signs
    # this way, and only at the END of the last writing: a '/s/' anywhere
    # above the body's close belongs to a quoted document, not the bench.
    if doc.opinions:
        _sig_titles = ("judge", "justice", "magistrate", "chancellor",
                       "commissioner", "master", "referee")

        # THE SIGNERS' COLUMN starts at a third of the measure: almd sets
        # the judge's name at x0 252 on a 612pt sheet (41%), ilcd at 288
        # (47%). A body row starts at the rail (72) or its indent (108).
        _sig_rail = model.pages[-1].width * 0.33

        def _is_sig_row(line) -> bool:
            """A row in the signing block: short, and either set out in the
            signers' column or opening with the court's own signing cue.

            The NAME carries nothing to recognise it by — 'EMILY C. MARKS'
            is just a short line — so POSITION is the test, the same rail
            the graphic-signature lift above already uses. A body sentence
            starts at the measure and fails it.
            """
            t = " ".join((line.plain or "").split())
            if not t or len(t) > 70:
                return False
            low = t.lower()
            if low.startswith(("/s/", "/s ", "s/")) or _CONFORMED.search(low):
                return True
            if low.rstrip(".:").startswith(("dated", "done ")) or \
                    low.startswith(("entered ", "signed ")):
                return True
            # THE DISTRIBUTION LINE IS PART OF THE SIGNING BLOCK. The page
            # sets 'cc: counsel of record' under the judge's office, and it
            # broke the run there — so the judge's NAME, his office and the
            # cc line stayed in the body as one welded paragraph (the user,
            # 2026-08-23: 'the last line is teh judge stuff but it should be
            # on separte rows').
            if low.startswith(("cc:", "cc ", "copies to", "copies furnished",
                               "copy to", "distribution")):
                return True
            if any(w in low for w in _sig_titles):
                return True
            return line.x0 > _sig_rail

        # The dropped set is recomputed here: `all_dropped_ids` was taken
        # before the furniture passes ran, so the folio this page ends on
        # ('5', bottom of the sheet) still looked live and broke the walk on
        # its first row.
        _drop_now = {i for d in doc.dropped for i in d.prov.line_ids}
        _last_pg = model.pages[-1].number
        _tail = [l for l in model.pages[-1].lines
                 if l.plain.strip() and l.id not in _drop_now
                 and not _FOLIO_ROW.match(l.plain.strip())]
        _tail.sort(key=lambda l: (l.top, l.x0))

        # A RUN IS THE BENCH SIGNING only if it says so somewhere: the
        # conformed slash, or a judicial office. caed's magistrate types the
        # name and the office with no '/s/' at all.
        def _run_is_signature(run) -> bool:
            for line in run:
                low = " ".join((line.plain or "").split()).lower()
                if low.startswith(("/s/", "/s ", "s/")) or _CONFORMED.search(low):
                    return True
                if any(w in low for w in _sig_titles):
                    return True
            return False

        # THE SIGNATURE IS NOT ALWAYS THE LAST THING ON THE SHEET. almd
        # prints footnote 29 in the foot margin BELOW the judge's name, so a
        # walk up from the bottom hit footnote prose and stopped before ever
        # reaching the signing block. Every maximal run of signing rows on
        # the page is considered instead, and the LAST one that names an
        # office or carries the slash is the bench: footnote and body rows
        # start at the measure and bound the run on both sides.
        _runs: list = []
        _cur: list = []
        for line in _tail:
            if _is_sig_row(line):
                _cur.append(line)
                continue
            if _cur:
                _runs.append(_cur)
                _cur = []
        if _cur:
            _runs.append(_cur)
        _run = next((r for r in reversed(_runs) if _run_is_signature(r)), [])

        if _run:
            _op_sig = doc.opinions[-1]
            # A ROW ALREADY READ AS BODY IS IN THE WRONG PLACE, NOT MISSING.
            # This lift used to APPEND every row of the signing run, so where
            # a court reader (or either lift above) had already placed those
            # rows the paper was signed twice over — akd/76949.15.0 printed
            # '/s/ Sharon L. Gleason' and 'UNITED STATES DISTRICT JUDGE'
            # twice, once with the page's italics and once without (the user,
            # 2026-08-23: 'why does this list the signature twice???'), and
            # almd/81184.72.0 the same. Appending only the UNCLAIMED rows
            # cured the double but left the other half of the defect: on
            # alnd/179841.412.0 the judge's name, his title and the
            # signature graphic stayed in the BODY, so the writing ended on
            # its own signature block (the user: 'signatures are inserted
            # into and above the ending text?').
            #
            # So the run MOVES what it finds. Everything from the first
            # already-placed signing row to the end of the writing is the
            # signature — which is what `signature.opens` means where a court
            # states it — and the rows nothing claimed are created beside
            # them, each in the place the page prints it.
            def _ids(b) -> set:
                return set(getattr(getattr(b, "prov", None),
                                   "line_ids", ()) or ())

            _run_ids = {l.id for l in _run}
            _rank = {l.id: k for k, l in enumerate(_run)}

            # ONLY A TRAILING RUN OF PURE SIGNING BLOCKS MOVES. Cutting at
            # the FIRST block that merely touches the run swallowed the
            # writing: cafc/in_re_us lost all 7 of its blocks to its own
            # signature, and six other sentinels lost half their body, on
            # one-page orders where a signing row and a body paragraph share
            # a block. A block qualifies only if EVERY line in it is a
            # signing row — or if it carries no lines at all, which is what
            # a graphic is — and the walk stops at the first block that does
            # not qualify, so a body paragraph is a floor.
            _line_at = {l.id: l for pm in model.pages for l in pm.lines}
            _meas_x0 = geom.body_x0 if geom else 72.0
            _meas_x1 = ((getattr(geom, "right_x1", None) or 540.0)
                        if geom else 540.0)
            _meas = max(_meas_x1 - _meas_x0, 1.0)

            def _is_stacked(b) -> bool:
                """Rows the page STACKS, not prose it wraps.

                A paragraph runs to the measure and wraps; an appearance, an
                address or a signature is a column of short rows. ord/
                …172179.21.0 closes with 'Proposed Order submitted by:' over
                the firm, the street, the telephone, the e-mail and 'Of
                Attorneys for Plaintiff' — seven rows of 147-355pt against a
                468pt measure — and because that block is not a SIGNING row
                the tail walk stopped on it, so the judge's own signature
                above it was never claimed and rendered flush left, and the
                seven rows came back welded into one paragraph (the user,
                2026-08-25: 'why are we not putting signature on the right
                and preserving the new lines at the end where its clearly
                neeeed?').
                """
                _ls = [_line_at[i] for i in _ids(b) if i in _line_at]
                if len(_ls) < 3:
                    return False
                return all(l.x1 <= _meas_x1 - 0.15 * _meas for l in _ls)

            def _is_sig_block(b) -> bool:
                ids = _ids(b)
                if not ids:
                    return isinstance(b, m.ImageBlock)
                return ids <= _run_ids or _is_stacked(b)

            _cut = len(_op_sig.blocks)
            while _cut > 0 and _is_sig_block(_op_sig.blocks[_cut - 1]):
                _cut -= 1
            _tail = _op_sig.blocks[_cut:]
            _op_sig.blocks = _op_sig.blocks[:_cut]
            _held = {i for b in (*_tail, *_op_sig.signature) for i in _ids(b)}
            _held |= {i for _o in doc.opinions for _b in _o.blocks
                      for i in _ids(_b)}

            # ORDER IS THE PAGE'S. A moved block keeps the position of its
            # first signing row; a graphic carries no row ids at all, so it
            # keeps the place it already had, just after the block above it.
            _keyed: list = []
            _last_key = -1.0
            for b in _tail:
                _mine = [_rank[i] for i in _ids(b) if i in _rank]
                _last_key = float(min(_mine)) if _mine else _last_key + 0.5
                _keyed.append((_last_key, b))
            _new = 0
            for line in _run:
                if line.id in _held:
                    continue
                _keyed.append((float(_rank[line.id]), m.Paragraph(
                    text=line.plain.strip(),
                    prov=m.Prov(_last_pg, (line.id,)), align="right")))
                _new += 1
            _keyed.sort(key=lambda kv: kv[0])
            # ONE PRINTED ROW PER ROW. The assembler joins contiguous lines
            # into prose, so a moved block arrives with the judge's name, his
            # office and the cc line welded into one paragraph — 'ROY K.
            # ALTMAN UNITED STATES DISTRICT JUDGE cc: counsel of record'. The
            # page sets one per line and a signature block IS its rows, so a
            # moved block is rebuilt from the lines it came off.
            _line_of = {l.id: l for pm in model.pages for l in pm.lines}
            from .resolve.footnotes import line_markup as _lmk

            def _as_rows(b) -> list:
                ids = [i for i in _ids(b) if i in _line_of]
                if len(ids) <= 1 or isinstance(b, m.ImageBlock):
                    return [b]
                _ls = sorted((_line_of[i] for i in ids),
                             key=lambda l: (l.page, l.top, l.x0))
                _rows: list = []
                for _l in _ls:
                    if (_rows and _rows[-1][0].page == _l.page
                            and abs(_rows[-1][0].top - _l.top) <= 2.0):
                        _rows[-1].append(_l)
                    else:
                        _rows.append([_l])
                if len(_rows) <= 1:
                    return [b]
                # …AND EACH ROW KEEPS THE PLACE THE PAGE SET IT. Ranging the
                # whole block right moved an appearance block that the page
                # sets at the body rail out to the middle of the sheet: ord
                # signs at x0 288 of a 612pt sheet and sets 'Proposed Order
                # submitted by:' and its five rows at 72, and both belong
                # where the court put them.
                def _al(_r) -> str:
                    _x0 = min(x.x0 for x in _r)
                    return "right" if _x0 > _meas_x0 + 0.35 * _meas else ""

                return [m.Paragraph(
                    text="  ".join(_lmk(x) for x in sorted(_r,
                                                           key=lambda y: y.x0)),
                    prov=m.Prov(_r[0].page, tuple(x.id for x in _r)),
                    align=_al(_r)) for _r in _rows]

            _sig_items = [x for _k, b in _keyed for x in _as_rows(b)]
            for _i2, _b2 in enumerate(_sig_items):
                if isinstance(_b2, m.Heading):
                    _sig_items[_i2] = m.Paragraph(
                        text=_b2.text, prov=_b2.prov, align="right")
            # …AND A ROW THAT WAS ALREADY ITS OWN BLOCK KEEPS ITS PLACE TOO.
            # `_as_rows` hands back a single-line block unchanged, so a court
            # that sets each signing row as its own block never had one
            # aligned: ord/…172179.21.0 signs at x0 288 of a 612pt sheet and
            # the judge's name, the s/ line and his office all rendered flush
            # left against the body. Read off the page rather than assumed,
            # so the appearance block the same court sets at the rail below
            # it stays where it belongs.
            for _i3, _b3 in enumerate(_sig_items):
                if not isinstance(_b3, m.Paragraph) or getattr(_b3, "align", ""):
                    continue
                _ls3 = [_line_at[i] for i in _ids(_b3) if i in _line_at]
                if _ls3 and min(l.x0 for l in _ls3) > _meas_x0 + 0.35 * _meas:
                    _sig_items[_i3] = m.Paragraph(
                        text=_b3.text, prov=_b3.prov, align="right",
                        continuation=_b3.continuation, role=_b3.role)
            _op_sig.signature = _sig_items + list(_op_sig.signature)
            trace.event("signature.claimed",
                        f"{len(_tail)} moved, {_new} new, p{_last_pg}")

    # 10 finalize — residual sweep: every content line must have landed.
    placed: set[int] = set()
    for items in (doc.headmatter, doc.attorneys, doc.syllabus, doc.summary,
                  doc.headnotes, doc.signature, doc.trailer):
        for it in items:
            prov = getattr(it, "prov", None)
            if prov is not None:
                placed.update(prov.line_ids)
            if isinstance(it, m.CaptionBlock):
                for row in it.left + it.right:
                    placed.update(row.prov.line_ids)
    for op in doc.opinions:
        placed.update(op.author_prov.line_ids)
        for b in (*op.blocks, *op.signature, *op.caption):
            placed.update(getattr(b, "prov", m.Prov(1)).line_ids)
        for fn in op.footnotes:
            for b in fn.blocks:
                placed.update(b.prov.line_ids)
    for fn in doc.headmatter_footnotes:
        for b in fn.blocks:
            placed.update(b.prov.line_ids)
    placed.update(assembled.consumed_ids)
    dropped_ids = all_dropped_ids | {
        i for d in doc.dropped for i in d.prov.line_ids}
    for pm in model.pages:
        for line in pm.lines:
            if line.id in placed or line.id in dropped_ids:
                continue
            if not line.plain.strip():
                continue
            in_zone = (pm.number in zone_tops
                       and line.top > zone_tops[pm.number] - 0.5)
            kind = "furniture" if ff.kind(pm, line) else "content"
            if in_zone and kind == "content":
                continue  # zone separators/typed rules
            # A line of PURE RAIL GLYPHS carries no words: it is the
            # caption's drawn column (pasuperct sets ':' down the middle)
            # or a typed separator. Counting it as lost content sent whole
            # courts to review over punctuation.
            if kind == "content" and not any(
                    c.isalnum() for c in line.plain):
                kind = "furniture"
            doc.residual.append(m.Residual(
                text=line.plain.strip(), prov=m.Prov(pm.number, (line.id,)),
                kind=kind))

    # A PARTY'S FILING IS NOT THE COURT'S WRITING. A complaint reads like an
    # opinion to every structural test — masthead, caption, numbered
    # paragraphs, a signature — and akd/79708.1.0 came back as an `opinion`
    # with 297 blocks and an 'author' who is the plaintiff's lawyer. The
    # paper says what it is where it SIGNS: the signer states who they
    # appeared FOR ('Attorneys for Plaintiff Defenders of Wildlife'), and no
    # court signs that way; a court signs an office. The paper's own name is
    # the second route, for a filing that closes without the phrase.
    #
    # The record is still parsed and still rendered — the user, 2026-08-23:
    # 'we want to be able to recognize this as not an opinion and not ingest
    # it on the CL side but that doesnt mean we shouldnt be able to parse
    # this right here and also flag it'. `DocType.FILING` is what the flag
    # is: `NO_BODY_EXPECTED` already contains it, and the CL view refuses to
    # translate it into an opinion cluster.
    if meta.doc_type in (m.DocType.OPINION, m.DocType.ORDER,
                         m.DocType.UNKNOWN, m.DocType.HYBRID):
        from .audit import strip_tags as _stf
        # HOW A PAPER CLOSES IS WHO WROTE IT. The signature BLOCK alone was
        # too narrow: a party's counsel signs 'By: /s/ William T. Dowd' and
        # sets the firm, the street, the fax and the email under it, and
        # those rows land in the BODY rather than the signature — so
        # gud/15303.118.0, a motion in limine, came back an `opinion` (the
        # user, 2026-08-23: 'i need filings to be identified across federal
        # district courts'). The CLOSING REGION is read instead: the
        # signature, the tail of the writing, and the trailer.
        _tail_blocks = [b for _o in doc.opinions
                        for b in (*_o.blocks[-8:], *_o.signature)]
        _close = " ".join(_stf(getattr(b, "text", "") or "")
                          for b in (*_tail_blocks, *doc.trailer))
        _sig_low = " ".join(_close.split()).lower()
        _office = ("judge", "justice", "magistrate", "chancellor",
                   "referee", "commissioner", "clerk", "by the court",
                   "so ordered", "it is ordered")
        _judicial = any(w in _sig_low for w in _office)
        # THE APPARATUS OF A PARTY'S SIGNATURE, which a court prints none of:
        # no firm, no bar number, no email, no certificate of service, and it
        # never submits anything respectfully.
        _appeared_for = bool(_re_filing_appearance.search(_sig_low)
                             or _re_counsel_apparatus.search(_sig_low))
        _named_itself = bool(
            doc.criteria.title and _re_pleading.match(doc.criteria.title))
        # ...AND SOME PAPERS NEVER LET A SIGNATURE BE CLAIMED AT ALL. A
        # complaint closes with PAGES of roster: caed/492832.42.2 runs its
        # counsel over three sheets and ends, 57 pages in, on 'Counsel for
        # Plaintiff National Association of / Wholesaler-Distributors' set at
        # the RAIL -- so no signing run forms (that walk wants the signers'
        # column or the conformed slash) and `signature` stays empty. The end
        # matter is still there, in the body's last blocks, and it still says
        # the one thing no court says. Read from the closing rows on three
        # signals measured together: a row that IS an appearance rather than a
        # sentence mentioning one, the contact details a roster carries and an
        # order never does, and no judicial office among them.
        _closing = [_t for _t in (
            " ".join(_stf(getattr(b, "text", "") or "").split())
            for _o in doc.opinions[-1:]
            for b in (*[x for x in _o.blocks
                        if getattr(getattr(x, "prov", None), "page", 0)
                        >= model.pages[-1].number], *_o.signature))
            if _t]
        _appear_close = any(_re_appearance_row.match(_t) and len(_t) <= 80
                            for _t in _closing)
        _roster_rows = sum(1 for _t in _closing if _re_roster_row.search(_t))
        _closed_by_counsel = (
            _appear_close and _roster_rows >= 2
            and not any(w in _t.lower() for _t in _closing for w in _office))
        # …AND THE COURT'S OWN APPEARANCE LIST IS NOT A PARTY'S BLOCK. Both
        # routes above read an appearance and neither asks WHOSE, so a court
        # that prints its counsel of record at the foot of its opinion looked
        # exactly like a paper filed by one of them.
        #
        # THE COURT NAMES EVERYONE; A PARTY NAMES ITSELF. nmd closes its
        # opinions with a roster of every firm in the case — 'Attorneys for
        # Defendant HCSC Insurance Services Co.', '… Molina Healthcare …',
        # '… Presbyterian Health Plan …' on one record and six such rows on
        # another — while a party's paper closes on ONE appearance, its own
        # (the user, 2026-08-24: 'why does this … say its a filing?').
        #
        # AND NO PARTY WRITES 'SO ORDERED'. nysd endorses a letter-motion by
        # stamping its order beneath counsel's own block, so that page
        # carries a party's appearance AND the court's disposition; the
        # disposition is the court speaking and outranks anything above it.
        _appear_rows = sum(1 for _t in _closing
                           if _re_appearance_row.match(_t) and len(_t) <= 80)
        _court_roster = _appear_rows >= 2 or any(
            _re_ordering.search(_t) for _t in _closing)
        if not _judicial and not _court_roster and (
                _appeared_for or _named_itself or _closed_by_counsel):
            meta.doc_type = m.DocType.FILING
            doc.warnings.append(
                _FILING_FLAG + ": the signer "
                + ("states who they appeared for" if _appeared_for
                   else f"the paper names itself {doc.criteria.title!r}"
                   if _named_itself
                   else "is counsel for a party, with their own roster"))

    if meta.doc_type == m.DocType.UNKNOWN and doc.opinions:
        signed = any(op.author for op in doc.opinions)
        meta.doc_type = m.DocType.OPINION if signed else m.DocType.ORDER
    # A SIGNED writing outranks a notice classification (a slip cover's
    # 'NOTICE:' boilerplate must never validate an empty extraction).
    if meta.doc_type == m.DocType.NOTICE and any(
            op.author for op in doc.opinions):
        meta.doc_type = m.DocType.OPINION
    # A JUDGMENT heading over SUBSTANTIVE REASONING is the court's own
    # writing, not a clerk's form (ca1 heads a reasoned disposition
    # 'JUDGMENT'; ca10 heads the same thing 'ORDER AND JUDGMENT'). The
    # body itself is the evidence: a bare form has none.
    if meta.doc_type == m.DocType.JUDGMENT:
        from .audit import strip_tags as _stj
        _words = sum(len(_stj(getattr(b, "text", "") or "").split())
                     for op in doc.opinions for b in op.blocks)
        # …UNLESS THE PAPER STATES THAT IT IS A FORM. The word count reads a
        # bare form as empty, and the Administrative Office's judgment form
        # is anything but: almd/…85545.1118.0 is an AO 245B carrying the
        # count of conviction, the term, and every condition of supervision
        # — 288 rows over seven sheets — so the test reclassified it as the
        # court's own ORDER and it was graded as a writing that had no
        # opinion in it (the user, 2026-08-25: 'i think this should be
        # flagged as a form and not processed as an opinion').
        # THE FORM NUMBER IS THE PAPER'S OWN DECLARATION, printed at the head
        # of every sheet the AO issues ('AO 245B (Rev. 11/25) Judgment in a
        # Criminal Case', 'Sheet 1'), and no opinion carries one.
        if _words >= 120 and not _states_ao_form(model):
            meta.doc_type = m.DocType.ORDER

    # 10c WHERE IT STOOD. Every removal and every unclaimed row gets the box
    # its source lines occupied, so a consumer can audit the decision against
    # the page instead of taking it on trust. Done HERE, in one pass over the
    # finished lists, rather than at the 163 sites that build a `Dropped` —
    # one owner, and no site can forget it.
    _box_of = {l.id: (l.x0, l.top, l.x1, l.bottom)
               for pm in model.pages for l in pm.lines}

    def _union(ids) -> tuple | None:
        boxes = [_box_of[i] for i in ids if i in _box_of]
        if not boxes:
            return None
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    for _rec in (*doc.dropped, *doc.residual):
        if _rec.bbox is None:
            _rec.bbox = _union(_rec.prov.line_ids)

    # 10c-bis A RUNOVER IS THE ITEM STILL SPEAKING. The segmenter can cut a
    # bulleted list between an item and its own second line — measured on
    # alnd/179841.412.0, 4 of its 9 conclusion items were cut that way — and
    # the halves then read as an item and a stray paragraph beneath it. The
    # page says which is which: a block whose first line is set IN from the
    # item above it is that item continuing, not a new one.
    _x0_of = {l.id: l.x0 for pm in model.pages for l in pm.lines}
    _pos_of = {l.id: (l.page, l.top, l.bottom, l.x0)
               for pm in model.pages for l in pm.lines}

    def _first_x0(b):
        xs = [_x0_of[i] for i in getattr(getattr(b, "prov", None),
                                         "line_ids", ()) if i in _x0_of]
        return min(xs) if xs else None

    def _span(b):
        """(rail, first_x0, first(page,top), last(page,bottom)) for a block."""
        ps = [_pos_of[i] for i in getattr(getattr(b, "prov", None),
                                          "line_ids", ()) if i in _pos_of]
        if not ps:
            return None
        ps.sort(key=lambda q: (q[0], q[1]))
        return (min(q[3] for q in ps), ps[0][3],
                (ps[0][0], ps[0][1]), (ps[-1][0], ps[-1][2]))

    # A LINE AT THE RAIL UNDER AN INDENTED PARAGRAPH IS THAT PARAGRAPH. The
    # segmenter can cut a paragraph from its own last line, and a one-line
    # segment always opens a block — so a paragraph lost its closing sentence
    # to a block of its own ('… who Vandergaw was prosecuting.' / 'Id at 9.'
    # — akd/62768.505.0). The page decides: this document marks a new
    # paragraph by INDENTING it, so a row that starts at the runover edge,
    # one line-pitch below, is the paragraph continuing (the user, 2026-08-23:
    # 'we dont want every apragraph to lose its last sentence?').
    _lead = (geom.lead if geom and geom.lead else 0.0) or 14.0
    # NOT ON AN OCR'D SOURCE. This rule reads x0 to tell a runover from an
    # opener, and a scan's own warning says the geometry is untrusted — on
    # virginislands/…wrensford the OCR renders the court's paragraph marks as
    # 'qi', '{9' and '47' by turns, so neither the marks nor the measure can
    # carry the decision. The safe direction is to leave those documents
    # exactly as they were.
    _trust_geometry = not (meta.scan_pages or "scan" in (meta.source_kind or ""))
    import os as _os2
    _join_diag = _os2.environ.get("CENTRALIA_PARA_JOIN_DIAG")
    for _op in (doc.opinions if _trust_geometry else ()):
        _kept2: list = []
        for _b in _op.blocks:
            _prev = _kept2[-1] if _kept2 else None
            if (isinstance(_b, m.Paragraph) and isinstance(_prev, m.Paragraph)
                    and not getattr(_b, "role", "")
                    and not getattr(_prev, "role", "")):
                _a, _c = _span(_prev), _span(_b)
                if _a and _c:
                    _rail, _a_first, _, _a_last = _a
                    _, _c_first, _c_top, _ = _c
                    _indented = _a_first >= _rail + 8.0
                    # AT the rail, not merely left of the indent. A row set
                    # LEFT of the paragraph's own runover edge is outside its
                    # measure and belongs to something else — illappct sets
                    # its headings at 72 under paragraphs whose runovers sit
                    # at 144, and those were being swallowed.
                    _at_rail = abs(_c_first - _rail) <= 2.5
                    _adjacent = (_c_top[0] == _a_last[0]
                                 and 0 < _c_top[1] - _a_last[1] <= 1.6 * _lead)
                    # …AND THE PAGE'S OWN OPENERS ARE NEVER RUNOVERS. A
                    # court that numbers its paragraphs opens one at the rail
                    # ('¶ 12 …' — the Illinois courts), and an outline label
                    # opens a section there; joined to the paragraph above,
                    # both vanish into it.
                    _cur_flat = _re_tags.sub("", _b.text or "").lstrip()
                    _opens_itself = bool(_PARA_OPENER.match(_cur_flat))
                    # …AND A COURT THAT NUMBERS ITS PARAGRAPHS may lose the
                    # mark to OCR, leaving a bare number ('47 On May 15,
                    # 2023, Dr. Boschulte…' — virginislands). A leading
                    # number is not enough on its own: a runover can open on
                    # one ('91 Fed. Reg. 9339'). What settles it is whether
                    # the paragraph ABOVE opens on a number too — that is
                    # the document saying it numbers its paragraphs.
                    if not _opens_itself and _NUM_OPENER.match(_cur_flat):
                        _prev_flat = _re_tags.sub(
                            "", _prev.text or "").lstrip()
                        _opens_itself = bool(_NUM_OPENER.match(_prev_flat))
                    if (_indented and _at_rail and _adjacent
                            and not _opens_itself):
                        if _join_diag:
                            import re as _re3
                            _pt = _re3.sub(r"<[^>]+>", "", _prev.text)[-58:]
                            _ct = _re3.sub(r"<[^>]+>", "", _b.text or "")[:58]
                            print(f"JOIN rail={_rail:.0f} first={_a_first:.0f} "
                                  f"cur={_c_first:.0f} gap="
                                  f"{_c_top[1] - _a_last[1]:.0f}: "
                                  f"…{_pt!r} + {_ct!r}")
                        _prev.text = (_prev.text.rstrip() + " "
                                      + (_b.text or "").lstrip())
                        _prev.prov = m.Prov(
                            _prev.prov.page,
                            tuple(_prev.prov.line_ids) + tuple(_b.prov.line_ids))
                        continue
            _kept2.append(_b)
        _op.blocks = _kept2

    for _op in doc.opinions:
        _kept: list = []
        for _b in _op.blocks:
            if (_kept and isinstance(_kept[-1], m.ListItem)
                    and isinstance(_b, m.Paragraph)):
                _ax, _bx = _first_x0(_kept[-1]), _first_x0(_b)
                if _ax is not None and _bx is not None and _bx > _ax + 2.0:
                    _kept[-1].text = (_kept[-1].text.rstrip() + " "
                                      + (_b.text or "").lstrip())
                    _kept[-1].prov = m.Prov(
                        _kept[-1].prov.page,
                        tuple(_kept[-1].prov.line_ids) + tuple(
                            _b.prov.line_ids))
                    continue
            _kept.append(_b)
        _op.blocks = _kept

    # 10c-ter A TABLE-OF-CONTENTS ENTRY IS ONE ROW, however many lines the
    # page wraps it over. Only the LAST line of an entry carries the dot
    # leaders and the page number; the lines above it are the heading's own
    # text, and they are set in the same capitals a heading is — so they were
    # classified one per line and came out as three Headings, a Blockquote and
    # a stray Paragraph for two entries (gud/15303.96.0). A table of
    # AUTHORITIES reads correctly for the one reason that its entries fit on a
    # single row (the user, 2026-08-23: 'the table oc conteents fails to
    # format right but table of authorities gest it irhgt … thats an issue
    # across courts').
    #
    # Repaired here, over the finished blocks, because the mis-typing happens
    # before the leader row is ever in view: the leader row is the END of the
    # entry, and every contiguous block above it that does not end in leaders
    # and stands at the same left edge is the same entry still speaking.
    if _trust_geometry:
        for _op in doc.opinions:
            _out: list = []
            for _b in _op.blocks:
                _txt = _re_tags.sub("", getattr(_b, "text", "") or "")
                if not _TOC_TAIL.search(_txt.rstrip()):
                    _out.append(_b)
                    continue
                _run: list = []
                while _out:
                    _cand = _out[-1]
                    _ct = _re_tags.sub("", getattr(_cand, "text", "") or "")
                    if not _ct.strip() or _TOC_TAIL.search(_ct.rstrip()):
                        break
                    # PROSE IS NOT AN ENTRY'S FIRST LINE. Without this the
                    # walk-back ate the body: 'COMES NOW Plaintiff Guam
                    # Waterworks Authority, by and through Counsel, …'
                    # swallowed the entry below it. A contents entry is
                    # SHORT and set in the court's own capitals.
                    _alpha = [c for c in _ct if c.isalpha()]
                    if len(_ct.split()) > 25 or not _alpha:
                        break
                    if sum(c.isupper() for c in _alpha) < 0.8 * len(_alpha):
                        break
                    _sa, _sb = _span(_cand), _span(_run[0] if _run else _b)
                    if not (_sa and _sb):
                        break
                    # contiguous, and standing at the same left edge
                    # ADJACENT ROWS MAY OVERLAP BY THEIR GLYPH BOXES: entry
                    # III's last line bottoms at 90 while the row under it
                    # tops at 88, so a strictly positive gap rejected the
                    # very rows this pass exists to join.
                    if _sa[3][0] != _sb[2][0] or not (
                            -5.0 <= _sb[2][1] - _sa[3][1] <= 2.2 * _lead):
                        break
                    if abs(_sa[1] - _sb[1]) > 40.0:
                        break
                    _run.insert(0, _out.pop())
                if not _run:
                    _out.append(_b)
                    continue
                _text = " ".join(
                    (getattr(x, "text", "") or "").strip()
                    for x in (*_run, _b) if (getattr(x, "text", "") or "").strip())
                _ids = tuple(i for x in (*_run, _b)
                             for i in getattr(getattr(x, "prov", None),
                                              "line_ids", ()) or ())
                _out.append(m.Paragraph(
                    text=_text, prov=m.Prov(_run[0].prov.page, _ids)))
            _op.blocks = _out

    # 10d THE CASES THIS RECORD DECIDES. A court reader that read its own
    # box's compartments has already published them (the district lane);
    # this reads the grouping off the headmatter's own row order for every
    # court that has not, and says nothing where the page states one case.
    if not doc.criteria.cases:
        from .resolve.headmatter import read_consolidated_cases
        _cases = read_consolidated_cases(doc)
        if _cases:
            doc.criteria.cases = _cases
            # THE LEAD CASE NAMES THE RECORD, and the companions are what
            # `other_dockets` was already carrying — restated here so the
            # two cannot disagree.
            _extra = [c.docket_number for c in _cases[1:]
                      if c.docket_number
                      and c.docket_number != doc.criteria.docket_number]
            for _d in _extra:
                if _d not in doc.criteria.other_dockets:
                    doc.criteria.other_dockets.append(_d)

    # 11 emit
    #
    # 'review' must mean SOMETHING TO FIX. A scanned or partly image-only
    # source is a property of the PDF, not of the parse — lumping the two
    # together buried real defects under ~100 files nobody can improve, so
    # source complaints get their own status and their own worklist.
    _src = [w for w in doc.warnings
            if any(k in w for k in SOURCE_WARNINGS)]
    # THE FILING FLAG IS A CLASSIFICATION, NOT A DEFECT. Recognising a
    # party's pleading and saying so is the RIGHT outcome — `review` means
    # 'something to fix here', and there is nothing to fix.
    _parse = [w for w in doc.warnings
              if w not in _src and not w.startswith(_FILING_FLAG)]
    status = "valid"
    if any(r.kind == "content" for r in doc.residual) or _parse:
        status = "review"
    elif not doc.opinions and meta.doc_type not in m.NO_BODY_EXPECTED:
        status = "review"
    elif _src:
        status = "scanned"
    # THE SIGNING BLOCK DATES THE PAPER, where the headmatter never did.
    # Asked LAST, when `doc.criteria` is final: placed with the signature
    # lift it ran before the headmatter's own criteria were merged and
    # OVERWROTE a date the caption had already stated correctly —
    # mad/238521.179.0 went from its own 'August 11, 2026' to a 'March 12,
    # 2026' recited inside the signing block. Only the court's own signature
    # and the rows it closes on are read: a date anywhere else on the sheet
    # could be a deadline the order sets or a filing it recites.
    if not doc.criteria.decision_date and doc.opinions:
        from .audit import strip_tags as _stdate
        _last_op = doc.opinions[-1]
        # A BODY PARAGRAPH MUST ANNOUNCE THE DATE TO COUNT. Inside the
        # claimed signature a bare date is the court's own; in the body it is
        # as likely to be something the order RECITES — ded/90534.32.0 closes
        # on 'Dentsply's Motion to Dismiss, D.I. 14, is granted in part …'
        # and the paragraph names a 2020 date, which this fallback published
        # as the decision date of a 2026 opinion. So a body block is read
        # only where it says the date is the paper's: 'Dated', the recital
        # 'this 20th day of May 2026' (alsd), or an order pronounced with it.
        for _sb in _last_op.signature:
            _sd = _signed_date(" ".join(
                _stdate(getattr(_sb, "text", "") or "").split()))
            if _sd:
                doc.criteria.decision_date = _sd
                trace.event("date.from-signature", _sd)
                break
        else:
            for _sb in _last_op.blocks[-3:]:
                _t = " ".join(_stdate(getattr(_sb, "text", "") or "").split())
                if not _re_dated_row.search(_t):
                    continue
                _sd = _signed_date(_t)
                if _sd:
                    doc.criteria.decision_date = _sd
                    trace.event("date.from-closing-row", _sd)
                    break

    return ExtractionResult(doc, trace, status=status)
