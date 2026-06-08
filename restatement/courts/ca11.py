"""United States Court of Appeals for the Eleventh Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class EleventhCircuit(FederalCircuitBase):
    court_id = "ca11"
    court_label = "United States Court of Appeals for the Eleventh Circuit."
    circuit_phrase = "eleventh circuit"
