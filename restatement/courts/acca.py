"""United States Army Court of Criminal Appeals. ('acca') — on the shared military CCA base."""

from __future__ import annotations

from ._military import MilitaryCCA


class ArmyCCA(MilitaryCCA):
    court_id = "acca"
    court_label = "United States Army Court of Criminal Appeals."
