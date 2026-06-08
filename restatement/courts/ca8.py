"""United States Court of Appeals for the Eighth Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class EighthCircuit(FederalCircuitBase):
    court_id = "ca8"
    court_label = "United States Court of Appeals for the Eighth Circuit."
    circuit_phrase = "eighth circuit"
    gap_tight_max = 10.0
    gap_single_max = 17.0
    gap_double_max = 28.0
