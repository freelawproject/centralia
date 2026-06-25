"""Nevada Court of Appeals.

Same byline form as the Nevada Supreme Court (nev.py): 'By the Court,
WESTBROOK, J.:' — the tag is stripped and the abbreviated-title colon form
follows. Inherits the nev handling; only the identity differs. Half the
corpus is flatbed scans (no text layer) that honestly yield nothing.
"""

from __future__ import annotations

from .nev import NevadaSupreme


class NevadaCourtOfAppeals(NevadaSupreme):
    court_id = "nevapp"
    court_label = "Nevada Court of Appeals."
