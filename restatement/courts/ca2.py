"""United States Court of Appeals for the Second Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class SecondCircuit(FederalCircuitBase):
    court_id = "ca2"
    court_label = "United States Court of Appeals for the Second Circuit."
    circuit_phrase = "second circuit"
    body_baseline_x0 = 108.0
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 28.0
