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

    # The Eighth prints NO running header: every continuation page opens with
    # real text at top~73-75 (and the second line at ~91-95), and the folio sits
    # in the bottom margin. The family's blanket 95pt page-2 cutoff therefore
    # deleted the first — often the first TWO — lines of every page after the
    # first, which is where nearly all of this circuit's unplaced text came from.
    page2_header_cutoff = 0.0
