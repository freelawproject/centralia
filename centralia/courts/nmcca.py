"""United States Navy-Marine Corps Court of Criminal Appeals. ('nmcca') — on the shared military CCA base."""

from __future__ import annotations

from ._military import MilitaryCCA


class NavyMarineCCA(MilitaryCCA):
    court_id = "nmcca"
    court_label = "United States Navy-Marine Corps Court of Criminal Appeals."
