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
        # CA5 page-1 right-column 'FILED <date> / Clerk' stamp.  It overlaps
        # the centered Old English court banner in X, so an x>=440 crop cuts
        # the final ``ls`` off ``Appeals`` and can attach ``Clerk`` to the
        # first party.  The stamp is consistently Arial; the authored slip
        # caption uses OldEnglish/Equity faces.  Filter on that structural font
        # distinction and preserve the complete banner underneath.
        if (
            obj.get("page_number", 1) == 1
            and obj.get("top", 0) <= 220
            and "arial" in (obj.get("fontname") or "").lower()
        ):
            return None
        return super().filter_margins(obj)

    def find_footnote_separator(self, page):
        return self._sep_at(page, 100, 150)
