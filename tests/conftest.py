"""Shared test fixtures.

Tests run against the local PDF corpora under ``assets/<court>/`` (gitignored),
so a test is skipped if its asset isn't present rather than failing.
"""

from pathlib import Path

import pytest

from centralia import get_extractor

ASSETS = Path(__file__).resolve().parent.parent / "assets"


@pytest.fixture
def extract():
    def _extract(court: str, filename: str):
        path = ASSETS / court / filename
        if not path.exists():
            pytest.skip(f"missing asset: {path}")
        return get_extractor(court).extract(str(path))

    return _extract
