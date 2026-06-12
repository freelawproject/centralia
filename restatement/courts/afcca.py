"""United States Air Force Court of Criminal Appeals. ('afcca') — on the shared military CCA base."""

from __future__ import annotations

from ._military import MilitaryCCA


class AirForceCCA(MilitaryCCA):
    court_id = "afcca"
    court_label = "United States Air Force Court of Criminal Appeals."
