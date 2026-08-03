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
