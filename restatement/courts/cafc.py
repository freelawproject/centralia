"""United States Court of Appeals for the Federal Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class FederalCircuit(FederalCircuitBase):
    court_id = "cafc"
    court_label = "United States Court of Appeals for the Federal Circuit."
    circuit_phrase = "federal circuit"
    body_baseline_x0 = 144.0
    gap_tight_max = 10.0
    gap_single_max = 14.0
    gap_double_max = 22.0

    def find_footnote_separator(self, page):
        return self._sep_at(page, 160, 175)
