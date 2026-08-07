"""United States Court of Appeals for the Federal Circuit."""

from __future__ import annotations

import html
import re

from ._circuit import FederalCircuitBase

_TAG = re.compile(r"<[^>]+>")


class FederalCircuit(FederalCircuitBase):
    court_id = "cafc"
    court_label = "United States Court of Appeals for the Federal Circuit."
    circuit_phrase = "federal circuit"

    # Headmatter criteria: typed rules; docket printed BARE ('2025-1317') after the caption.
    parse_criteria_enabled = True
    body_baseline_x0 = 144.0
    gap_tight_max = 10.0
    gap_single_max = 14.0
    gap_double_max = 22.0

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        kept = []
        for item in doc.summary:
            raw = item.get("html", "") if isinstance(item, dict) else item
            plain = html.unescape(_TAG.sub("", str(raw)))
            normalized = " ".join(plain.split())
            if normalized in {
                "NOTE: This disposition is nonprecedential.",
                "NOTE: This order is nonprecedential.",
            }:
                # This is publication-status furniture, not authored text.
                # Keep it visible in Removed to preserve source fidelity.
                doc.dropped.append(normalized)
                continue
            kept.append(item)
        doc.summary = kept
        return doc

    def find_footnote_separator(self, page):
        return self._sep_at(page, 160, 175)

    # cafc sets its ATTORNEY NAMES IN SMALL CAPS, which lowers a row's dominant
    # font size below the prose around it — 'lotte, NC; DEEPRO MUKERJEE, LANCE
    # SODERSTROM, New' measures 9.5pt against its neighbours' 12pt. Every
    # consumer that treats a size change as a structural boundary then cuts the
    # row out of its paragraph, and the counsel block came apart mid-word
    # ('… JITENDRA MALIK, Char-' / 'lotte, NC; …'). The orphaned tail rows were
    # then swept into whatever criteria field was still open, which is how a
    # counsel roll became the document title and how the prior history came back
    # with an attorney's address welded onto the trial judge.
    #
    # Small caps are a TYPEFACE choice, not a change of structure, so the row
    # reports the size of its full-size text instead. Identified by the smaller
    # glyphs being uppercase throughout while the larger size is present on the
    # same row — which is what small caps is and what a genuine size change
    # (a 14pt party over its 12pt qualifier) is not.
    def line_meta(self, line):
        size, font, bold = super().line_meta(line)
        chars = [c for c in (line.get("chars") or ()) if (c.get("text") or "").strip()]
        if not chars:
            return size, font, bold
        sizes = {round(c.get("size", 0), 1) for c in chars}
        if len(sizes) < 2:
            return size, font, bold
        full = max(sizes)
        if size >= full:
            return size, font, bold
        letters = [
            c.get("text", "")
            for c in chars
            if round(c.get("size", 0), 1) < full and c.get("text", "").isalpha()
        ]
        if letters and all(ch.isupper() for ch in letters):
            return full, font, bold
        return size, font, bold
