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

    def _byline_split(self, line):
        """CA4 opinion bylines are ALL-CAPS ('GREGORY, Chief Judge:', 'PATRICIA
        TOLLIVER GILES, District Judge:'). A title-case name is the trial judge
        named in the lower-court history line ('... at Columbia. Mary G. Lewis,
        District Judge.'), which must stay in the headmatter, not open the
        opinion. So a byline whose name carries any lowercase letter is rejected
        (PER CURIAM / BY THE COURT pass through)."""
        r = super()._byline_split(line)
        if r is None:
            return None
        up = r[0].upper()
        if up.startswith(("PER CURIAM", "BY THE COURT")):
            return r
        name = r[0].split(",", 1)[0]
        letters = [c for c in name if c.isalpha()]
        if letters and not all(c.isupper() for c in letters):
            return None
        return r
