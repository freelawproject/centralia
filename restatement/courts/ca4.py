"""United States Court of Appeals for the Fourth Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class FourthCircuit(FederalCircuitBase):
    court_id = "ca4"
    court_label = "United States Court of Appeals for the Fourth Circuit."
    circuit_phrase = "fourth circuit"
    gap_tight_max = 12.0
    gap_single_max = 20.0
    gap_double_max = 36.0
    page2_header_cutoff = 30.0
