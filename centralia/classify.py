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
# CID glyphs as a fraction of ink beyond which the text layer is unreadable.
CID_MAX_FRAC = 0.2


def triage(model: PdfModel) -> str | None:
    """'scan' | 'unreadable' | None (proceed)."""
    if not model.pages:
        return "unreadable"
    img_pages = sum(1 for p in model.pages if p.image_area > SCAN_IMAGE_AREA)
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
