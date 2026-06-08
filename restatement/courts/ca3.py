"""United States Court of Appeals for the Third Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class ThirdCircuit(FederalCircuitBase):
    court_id = "ca3"
    court_label = "United States Court of Appeals for the Third Circuit."
    circuit_phrase = "third circuit"
    gap_tight_max = 12.0
    gap_single_max = 22.0
    gap_double_max = 38.0
