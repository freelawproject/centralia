"""United States Court of Appeals for the Seventh Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class SeventhCircuit(FederalCircuitBase):
    court_id = "ca7"
    court_label = "United States Court of Appeals for the Seventh Circuit."
    circuit_phrase = "seventh circuit"
    body_baseline_x0 = 144.0
    gap_tight_max = 10.0
    gap_single_max = 14.0
    gap_double_max = 24.0

    def find_footnote_separator(self, page):
        return self._sep_at(page, 140, 150)
