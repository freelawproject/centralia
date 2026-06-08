"""United States Court of Appeals for the District of Columbia Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class DCCircuit(FederalCircuitBase):
    court_id = "cadc"
    court_label = (
        "United States Court of Appeals for the District of " "Columbia Circuit."
    )
    circuit_phrase = "district of columbia circuit"
    body_baseline_x0 = 156.0
    gap_tight_max = 10.0
    gap_single_max = 12.0
    gap_double_max = 22.0

    def find_footnote_separator(self, page):
        return self._sep_at(page, 150, 165)
