"""United States Coast Guard Court of Criminal Appeals. ('uscgcoca') — on the shared military CCA base."""

from __future__ import annotations

from ._military import MilitaryCCA


class CoastGuardCCA(MilitaryCCA):
    court_id = "uscgcoca"
    court_label = "United States Coast Guard Court of Criminal Appeals."
