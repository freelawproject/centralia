"""Shared base for the Alabama U.S. district courts (almd / alnd / alsd).

The caption facsimile they relied on now lives in ``DistrictBase`` (shared by
all districts), so this is just a thin grouping marker — kept so the Alabama
courts stay a named family and have a place for any future Alabama-only tuning.
"""

from __future__ import annotations

from ._district import DistrictBase


class AlabamaDistrictBase(DistrictBase):
    pass
