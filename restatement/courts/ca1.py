"""United States Court of Appeals for the First Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class FirstCircuit(FederalCircuitBase):
    court_id = "ca1"
    court_label = "United States Court of Appeals for the First Circuit."
    circuit_phrase = "first circuit"
    page2_header_cutoff = 30.0  # no centered running header; body at top~72
