"""United States Court of Appeals for the Fifth Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase


class FifthCircuit(FederalCircuitBase):
    court_id = "ca5"
    court_label = "United States Court of Appeals for the Fifth Circuit."
    circuit_phrase = "fifth circuit"
    body_baseline_x0 = 108.0
    gap_tight_max = 10.0
    gap_single_max = 16.0
    gap_double_max = 28.0

    def filter_margins(self, obj):
        # CA5 page-1 right-column 'FILED <date> / Clerk' stamp.
        if (
            obj.get("page_number", 1) == 1
            and obj.get("x0", 0) >= 440
            and obj.get("top", 0) <= 200
        ):
            return None
        return super().filter_margins(obj)

    def find_footnote_separator(self, page):
        return self._sep_at(page, 100, 150)
