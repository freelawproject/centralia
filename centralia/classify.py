"""Triage (scan / unreadable) and document-type classification.

Triage runs before everything: a scan is a SUCCESS result — reported
separately, never a parse failure. Calibrated on the corpus: pure scans
(delctcompl) and OCR-layer scans (mesuperct, vaed) both show image_area>0.85
on essentially every page; born-digital courts show none. An OCR text layer
does not make geometry trustworthy, so it stays a scan.

Doc-type reads PROMINENT HEADINGS (centered/bold/short standalone lines high
in the document) — string-prefix cues on structure, not regex over prose.
88% of the old corpus read "opinion" including 1,797/1,977 district filings;
this taxonomy is where that gets fixed, and the census gate proves it.
"""

from __future__ import annotations

import re

from .model import DocType
from .pdfio.model import PdfModel

# Fraction of pages that must be image-covered to call the document a scan.
SCAN_PAGE_FRAC = 0.8
# A page is image-covered when images paint most of it.
SCAN_IMAGE_AREA = 0.85
# …AND how little text a page must carry before its image means anything. A
# full-page image is not proof of a scan: a CM/ECF sheet can be printed over
# a page-sized background and still carry a perfect born-digital text layer
# (ared 153173: image_area 1.00 on every page, 919 clean characters, zero CID
# glyphs). Triaged as a scan on the image alone, the document is handed back
# unparsed — no headmatter, no caption, no reader — and the flag reads
# 'scanned-source' as though the paper were unreadable. The same floor
# pipeline.py already uses to call a page image-only.
SCAN_INK_FLOOR = 120
# CID glyphs as a fraction of ink beyond which the text layer is unreadable.
CID_MAX_FRAC = 0.2

# THE STANDARD 14. A PDF may name these without embedding anything, so a
# document whose glyphs come only from this list has embedded no type of its
# own — which is what an OCR engine writes.
_BASE_14 = frozenset({
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique",
    "Helvetica-BoldOblique",
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Symbol", "ZapfDingbats",
    # THE ALIASES A VIEWER SUBSTITUTES FOR THEM, which an OCR layer names just
    # as readily and which embed nothing either. texbizct's scans are the
    # reason: may_v._ineos_usa_oil__gas is a 4-page raster covered 4/4 with
    # nothing embedded, but it names ArialMT beside the standard faces, so an
    # exact-14 test called it born-digital and it carried no banner at all
    # while its text layer mangled every paragraph mark ('<jfl', '912',
    # '<jf3' for ¶1, ¶2, ¶3). The gate that does the real work is the image
    # coverage; this list only has to admit the faces a scan can name.
    "Arial", "ArialMT", "Arial-Bold", "Arial-BoldMT", "Arial-Italic",
    "Arial-ItalicMT", "Arial-BoldItalicMT",
    "TimesNewRoman", "TimesNewRomanPSMT", "TimesNewRomanPS-BoldMT",
    "TimesNewRomanPS-ItalicMT", "TimesNewRomanPS-BoldItalicMT",
    "CourierNew", "CourierNewPSMT", "CourierNewPS-BoldMT",
    "CourierNewPS-ItalicMT", "SymbolMT", "Wingdings",
})
# THE OCR ENGINE SIGNING ITS OWN WORK. Tesseract lays an invisible
# 'GlyphLessFont' over the image it read; GdPicture embeds
# 'GDPFNTCI-GdPictureOCRFont' (texbizct/plains_pipeline, whose every other
# face is a substituted '*Times New Roman-3251'). A face whose NAME says OCR
# is the layer saying what it is, so the name is read for it — and only after
# the image-coverage gate above has already passed, which is what keeps the
# real OCR-A and OCR-B typefaces, set as ordinary text on a form, out of it.
_OCR_FONTS = frozenset({"GlyphLessFont"})


def _is_ocr_font(name: str) -> bool:
    bare = name.split("+")[-1]
    return bare in _OCR_FONTS or "ocr" in bare.lower()


def _body_fonts(page) -> set:
    """The faces the PAGE'S OWN TYPE is set in — the e-filing overlay left out.

    `ocr_text_layer` asks whose type the glyphs are, and answers it from the
    page's whole font set. But CM/ECF stamps its header onto the sheet AT
    FILING, in its own embedded face, over whatever was filed: every page of
    ctd/170255.73.0 is a 300dpi JPEG with a Helvetica OCR layer under a
    'QOSDJF+LiberationSans' stamp row, and that one subsetted face — the
    clerk's, not the document's — declared all 36 pages born-digital. So a
    scanned pro-se filing was read as ordinary paper: its OCR's own damage
    ('rathcr' for 'rather', a case-lookup screenshot OCR'd to
    'c FgT.C\r21.80S$t€ CA3CADE FUIIOIIIG') was graded as OUR parse defect
    (joins x66, hyph x5, grade D) and the geometry was trusted (the user,
    2026-08-23).

    The stamp is excluded by what it SAYS, not by where it sits, and its whole
    visual row goes with it: pdfio splits the overlay at its column gaps, and
    a piece like 'Document 73' names too few fields to be recognised alone.
    """
    from .resolve.furniture import _looks_like_efiling_stamp
    lines = list(page.lines)
    stamped = {l.row for l in lines if l.row is not None
               and _looks_like_efiling_stamp(" ".join((l.plain or "").split()))}
    # …AND THE PAGE ID BELOW IT IS THE STAMP'S OWN. CM/ECF sets its Pageid
    # on a SECOND row, not as a split piece of the first, so the row test
    # above does not reach it: oknd/…66486.56.0 stamps 'Case
    # 4:23-cv-00290-JDR-CDL  Document 56  Filed…' and a bare '31' beneath
    # it, both in 'KRSWRU+LiberationSans'. The numeral kept the clerk's
    # embedded face in the page's own font set, and one subsetted face is
    # what this module reads as born-digital — so 31 rastered pages whose
    # OCR renders the masthead 'mniteis States? ®igtrict Court' were never
    # called a scan (the user, 2026-08-25: 'shouldnt this one be identifed
    # as a non digitla document').
    stamp_faces = {c.get("fontname") for l in lines
                   if _looks_like_efiling_stamp(" ".join((l.plain or "").split()))
                   for c in (l.chars or ()) if c.get("fontname")}
    out: set = set()
    for line in lines:
        t = " ".join((line.plain or "").split())
        if not t:
            continue
        if _looks_like_efiling_stamp(t) or (line.row is not None
                                            and line.row in stamped):
            continue
        if stamp_faces and t.isdigit() and len(t) <= 6:
            _f = {c.get("fontname") for c in (line.chars or ())
                  if c.get("fontname")}
            if _f and _f <= stamp_faces:
                continue
        for c in line.chars or ():
            f = c.get("fontname")
            if f:
                out.add(f)
    # A PAGE THAT IS NOTHING BUT ITS STAMP still has to answer the question,
    # and the only faces it has are the ones it was asked about.
    return out or {f for f in page.fonts if f}


def ocr_text_layer(model: PdfModel) -> bool:
    """True when the paper is a SCAN and its text is an OCR layer over it.

    This is a different question from `triage`, which asks whether a document
    can be read at all, and it is asked separately because the answers must
    not share a consequence: a 'scan' verdict can REFUSE a document
    (pipeline.py, max ink < 250), and a born-digital page printed over a
    page-sized background must never be refused.

    A FULL-PAGE IMAGE IS NOT PROOF OF A SCAN and text volume cannot settle it
    either — nevapp/ccmsi_v._odell is a bilevel 200dpi raster on all 10 pages
    carrying 761-1,680 OCR characters each, so it clears every ink floor in
    this module and was reported as ordinary born-digital paper, geometry and
    all (the user, 2026-08-21). What settles it is WHOSE TYPE THE GLYPHS ARE.
    Measured over the corpus, the two families separate with nothing in
    between:

        a scan's OCR layer     names only the standard 14 (mesuperct, nevapp)
                               or Tesseract's GlyphLessFont (virginislands)
                               and embeds nothing
        born-digital paper     embeds at least one subsetted face —
                               'KJYOFE+LiberationSans' (ared 153173, the
                               CM/ECF sheet over a background that this
                               module's SCAN_INK_FLOOR comment was written
                               for), 'BCDEEE+TimesNewRomanPSMT' (lactapp)

    The test is per DOCUMENT, not per court: lactapp prints both kinds.
    """
    if not model.pages:
        return False
    # PAGE BY PAGE, NOT DOCUMENT-WIDE. A hybrid sheet is common: five rastered
    # pages with an OCR layer and a born-digital certificate appended.
    # tenn/brad_wigdor is exactly that — pages 1-5 are full rasters typed in
    # nothing but Helvetica and Times-Roman, page 6 is real type in
    # 'CIDFont+F1'. Unioned, that one embedded subset declared all six pages
    # born-digital and the scan went unflagged (guard regression, 2026-08-21).
    ocr_pages = 0
    for page in model.pages:
        if page.image_area <= SCAN_IMAGE_AREA:
            continue
        fonts = _body_fonts(page)
        if not fonts:
            continue        # an image with no text at all: `triage` owns it
        # WHAT MATTERS IS THAT NOTHING IS EMBEDDED, which is what this
        # function's own docstring says: born-digital paper embeds at least
        # one subsetted face. Naming the standard 14 was one way to embed
        # nothing, not the only one — oknd's OCR layer names 'Century',
        # which is neither subsetted nor base-14, and the page went
        # uncounted. A sheet wholly covered by a raster whose type embeds
        # nothing is a scan, whatever the substituted face is called.
        if any(_is_ocr_font(f) for f in fonts) or all(
                "+" not in f for f in fonts):
            ocr_pages += 1
    # NO DOCUMENT-WIDE OVERRIDE. An OCR face on ONE page does not make the
    # document a scan: nced 205280.57 is a born-digital CM/ECF filing —
    # 'UNHHVC+LiberationSans' embedded on all eight pages — carrying a
    # 'HiddenHorzOCR' overlay on page 5 alone, presumably a scanned exhibit.
    # Tested document-wide on the font name it read as a scan, which would
    # have gated a real filing out of ingestion. The PAGE COUNT is the gate,
    # and the per-page test above already counts an OCR-font page as one.
    return ocr_pages / model.n_pages >= SCAN_PAGE_FRAC


def triage(model: PdfModel) -> str | None:
    """'scan' | 'unreadable' | None (proceed)."""
    if not model.pages:
        return "unreadable"
    img_pages = sum(1 for p in model.pages
                    if p.image_area > SCAN_IMAGE_AREA
                    and p.ink_chars < SCAN_INK_FLOOR)
    if img_pages / model.n_pages >= SCAN_PAGE_FRAC:
        return "scan"
    ink = sum(p.ink_chars for p in model.pages)
    cid = sum(p.cid_chars for p in model.pages)
    if ink == 0:
        return "scan"
    if cid / ink > CID_MAX_FRAC:
        return "unreadable"
    return None


# Heading vocabulary -> DocType, most specific first. Matching is done on a
# whitespace-collapsed uppercase key so letter-spaced headings ('O R D E R')
# and wrapped two-line headings both resolve.
_HEADINGS: tuple[tuple[str, DocType], ...] = (
    ("CERTIFICATE OF JUDGMENT", DocType.CERTIFICATE),
    ("ERRATA SHEET", DocType.NOTICE),
    ("ERRATA", DocType.NOTICE),
    ("NOTICE OF PASSING", DocType.NOTICE),   # haw bar-exam notices
    ("SENTENCIA", DocType.OPINION),          # pr appellate judgment
    ("RESOLUCIÓN", DocType.ORDER),
    ("RESOLUCION", DocType.ORDER),
    ("REPORT AND RECOMMENDATION", DocType.RR),
    ("REPORT & RECOMMENDATION", DocType.RR),
    ("FINDINGS AND RECOMMENDATION", DocType.RR),
    ("MEMORANDUM OPINION", DocType.OPINION),
    ("OPINION AND ORDER", DocType.OPINION),
    ("OPINION & ORDER", DocType.OPINION),
    ("MEMORANDUM DECISION", DocType.OPINION),
    ("MEMORANDUM AND ORDER", DocType.ORDER),
    ("MEMORANDUM & ORDER", DocType.ORDER),
    ("MEMORANDUM ORDER", DocType.ORDER),
    ("OPINION UNDER SEAL", DocType.NOTICE),   # sealed placeholder: no body
    ("OPINION", DocType.OPINION),
    ("SLIP OPINION", DocType.OPINION),
    ("CERTIFIED FOR PUBLICATION", DocType.OPINION),
    # ca9's unpublished disposition: an unsigned 'MEMORANDUM*' cover heading.
    ("MEMORANDUM", DocType.OPINION),
    ("SUMMARY ORDER", DocType.ORDER),
    # ca3 heads its rehearing disposition with the petition it answers.
    ("SUR PETITION FOR REHEARING", DocType.ORDER),
    ("SUR PETITION FOR PANEL REHEARING", DocType.ORDER),
    ("ON PETITION FOR REHEARING", DocType.ORDER),
    ("FINAL JUDGMENT", DocType.JUDGMENT),
    ("JUDGMENT IN A CIVIL", DocType.JUDGMENT),
    # ca10's unsigned disposition IS the court's writing (its own note
    # says 'this order and judgment is not binding precedent'), unlike a
    # clerk's bare JUDGMENT form.
    ("ORDER AND JUDGMENT", DocType.ORDER),
    ("JUDGMENT", DocType.JUDGMENT),
    ("NOTICE", DocType.NOTICE),
    ("ORDER", DocType.ORDER),
    ("DECISION", DocType.OPINION),
)


def _collapse(text: str) -> str:
    """Uppercase, single-spaced; letter-spaced runs ('O R D E R') collapsed.
    A letter-spaced PHRASE keeps its word gaps ('M E M O R A N D U M   O P
    I N I O N' — the wide run between words is the boundary)."""
    t = " ".join(text.split()).upper()
    parts = t.split(" ")
    if len(parts) >= 4 and all(len(p) == 1 for p in parts):
        words = re.split(r"\s{2,}", text.strip().upper())
        if len(words) > 1 and all(
                w and all(len(c) == 1 for c in w.split()) for w in words):
            return " ".join("".join(w.split()) for w in words)
        return "".join(parts)
    return t


def _heading_candidates(model: PdfModel, geom) -> list[str]:
    """Prominent short lines from the first two pages: centered, bold,
    caption-column, or larger than body — the places a court states what the
    document IS. Prose never qualifies (headings stop short of the measure)."""
    from .geometry import line_alignment

    out = []
    for pm in model.pages[:2]:
        for line in pm.lines:
            text = line.plain.strip()
            if not text or len(text) > 70:
                continue
            letters = [c for c in text if c.isalpha()]
            if not letters or not all(c.isupper() for c in letters):
                # Title-case headings exist ('Memorandum Decision'); accept
                # when bold or oversized, else require all-caps.
                if not (line.bold or (geom and line.size >= geom.body_size + 1)):
                    continue
            # A full-measure line is prose — unless every glyph is bold: a
            # long-titled order ('ORDER ON MOTIONS TO AMEND AND SUPPLEMENT
            # COMPLAINT') legitimately fills the measure.
            wide = geom and line.width >= 0.82 * geom.column
            if wide and not line.all_bold:
                continue
            align = line_alignment(line, pm.width, geom)
            prominent = (align == "C" or line.bold or line.col == "R"
                         or (geom and line.size >= geom.body_size + 1))
            if prominent:
                out.append(_collapse(text))
    return out


# Leading modifiers a heading may carry without changing what it names.
_MODIFIERS = ("AMENDED", "CORRECTED", "REVISED", "SECOND", "SUBSTITUTE",
              "SUPPLEMENTAL", "PUBLISHED", "UNPUBLISHED", "[PROPOSED]",
              "PROPOSED")


def _strip_modifiers(cand: str) -> str:
    words = cand.split(" ")
    while words and words[0] in _MODIFIERS:
        words = words[1:]
    # A footnote mark on the heading belongs to the heading ('MEMORANDUM*').
    return " ".join(words).rstrip("*†‡∗⁎﹡＊ ")


# Type words that may also CLOSE a heading ('SCREENING ORDER', 'PROTECTIVE
# ORDER', 'MEMORANDUM OPINION' already matches by prefix). Kept to the three
# that name what the document IS.
_SUFFIX_KEYS = ("ORDER", "OPINION", "JUDGMENT")


def _matches(cand: str, key: str) -> bool:
    """The heading NAMES the type: equals the key, starts with it as a phrase
    ('ORDER GRANTING…'), or — for the core type words — ends with it
    ('SCREENING ORDER'). Substring matches are how 'DEFAULT JUDGMENT AND
    FINAL DECREE' inside a case-description line misclassified a Montana
    opinion — anchored only."""
    c = _strip_modifiers(cand)
    if c == key or c.startswith(key + " ") or c.startswith(key + ":"):
        return True
    return key in _SUFFIX_KEYS and c.endswith(" " + key) and len(c) <= 40


def heading_doc_type(text: str) -> DocType | None:
    """The DocType a single heading line names, if any (shared by the
    classifier and the assembly's unsigned-order anchor)."""
    cand = _collapse(text)
    for key, dt in _HEADINGS:
        if _matches(cand, key):
            return dt
    return None


def classify_doc_type(model: PdfModel, geom) -> tuple[DocType, str | None]:
    """(doc_type, matched heading or None). UNKNOWN when no heading speaks —
    later stages (byline found, /s/ signature) may refine."""
    cands = _heading_candidates(model, geom)
    # A CAPTION'S RAIL GLYPH IS NOT PART OF THE HEADING. Where a chambers
    # divides its caption columns with ')' and sets the paper's name in the
    # right one, the glyph arrives welded to the front of the row: gasd/
    # …127345.13.0 offers ') JUDGMENT IN A CRIMINAL CASE', which matches no
    # heading at all, so the record classified UNKNOWN and the fallback below
    # made it an ORDER — an AO judgment FORM read as the court's own writing.
    # The stripped form is offered ALONGSIDE the row, never instead of it, so
    # a heading that really opens on punctuation is still matched as it reads.
    _bare = [c.lstrip(")]:*§}|( ").strip() for c in cands]
    cands = cands + [b for b in _bare if b and b not in cands]
    joined = ["  ".join(cands[i:i + 2]) for i in range(len(cands) - 1)]  # wraps
    for key, dt in _HEADINGS:
        for cand in (*cands, *joined):
            if _matches(cand, key):
                # 'NOTICE: Motions for reconsideration must be…' is a slip
                # cover's boilerplate over a signed opinion (gactapp), not a
                # notice document — the bare heading alone classifies.
                if key == "NOTICE" and len(" ".join(cand.split())) > 12:
                    continue
                if "[PROPOSED]" in cand or cand.startswith("PROPOSED "):
                    return DocType.HYBRID, cand
                return dt, cand
    # No heading — an ANNOUNCED order ('The Court of Appeals hereby passes
    # the following order:' — gactapp prints no banner at all).
    for pm in model.pages[:2]:
        for line in pm.lines:
            low = " ".join(line.plain.split()).lower()
            if "hereby passes the following order" in low \
                    or "hereby enters the following order" in low \
                    or "it is ordered by the court" in low \
                    or "this matter comes before the court" in low \
                    or low.startswith("upon a petition for review"):
                # 'This matter comes before the Court upon a petition…' /
                # 'UPON A PETITION FOR REVIEW UNDER CODE § 8.01-626' — va's
                # unsigned full-court orders open on the formula, no
                # heading, no byline.
                return DocType.ORDER, line.plain.strip()[:60]
    return DocType.UNKNOWN, None
