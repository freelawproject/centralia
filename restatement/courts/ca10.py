"""United States Court of Appeals for the Tenth Circuit."""

from __future__ import annotations
from ._circuit import FederalCircuitBase


class TenthCircuit(FederalCircuitBase):
    court_id = "ca10"
    court_label = "United States Court of Appeals for the Tenth Circuit."
    circuit_phrase = "tenth circuit"

    # The clerk's e-filing stamp ('FILED / United States Court of Appeals /
    # Tenth Circuit / <clerk> / Clerk of Court') is set in 12pt bold Times; the
    # centered court banner is 13pt, so this drops the stamp and keeps the banner.
    efile_stamp_font = "TimesNewRomanPS-BoldMT"
    efile_stamp_size = 12.0
