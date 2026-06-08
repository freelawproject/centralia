"""United States Court of Appeals for the Ninth Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class NinthCircuit(FederalCircuitBase):
    court_id = "ca9"
    court_label = "United States Court of Appeals for the Ninth Circuit."
    circuit_phrase = "ninth circuit"
    body_baseline_x0 = 54.0
    gap_tight_max = 10.0
    gap_single_max = 12.0
    gap_double_max = 22.0

    def find_footnote_separator(self, page):
        return self._sep_at(page, 50, 60)

    def skip_headmatter_segment(self, seg) -> bool:
        if seg and (seg[0].get("text") or "").strip().upper() in (
            "FOR PUBLICATION",
            "NOT FOR PUBLICATION",
        ):
            return True
        return super().skip_headmatter_segment(seg)
