"""The regression guard as a test suite.

739 sentinels across 111 courts are pinned in ``tests/fixtures/guard.json`` —
the structural signature of every file this project ever fixed. `harness/guard`
has always been able to check them; nothing ran it automatically, so a change
to one court could silently break another. This is that check, wired.

The signatures are computed ONCE per session, in parallel, and each sentinel
then asserts against its pin. That keeps the whole suite near the harness's own
runtime while still failing per file, so a break names the record.

    pytest tests/test_guard.py                     # every sentinel
    pytest tests/test_guard.py --court ca9         # one court
    pytest tests/test_guard.py -k nmariana

Re-pinning is deliberately NOT possible from here — it is a decision, not a
test outcome. Use `python -m harness.cli guard --bless` once the new state is
verified.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from conftest import HAVE_CORPUS, needs_corpus  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PINS_PATH = REPO_ROOT / "tests" / "fixtures" / "guard.json"


def _pins() -> dict:
    if not PINS_PATH.is_file():
        return {}
    with open(PINS_PATH) as fh:
        return json.load(fh)


PINS = _pins()
KEYS = sorted(PINS)


def _sig_one(key: str) -> tuple[str, dict]:
    from harness.guard import signature
    court, _, stem = key.partition("/")
    return key, signature(court, stem)


@pytest.fixture(scope="session")
def signatures(only_courts) -> dict:
    """Every sentinel's CURRENT signature, computed in one parallel pass."""
    keys = [k for k in KEYS
            if not only_courts or k.split("/")[0] in only_courts]
    if not keys:
        return {}
    with ProcessPoolExecutor() as pool:
        return dict(pool.map(_sig_one, keys, chunksize=4))


@needs_corpus
def test_pins_exist():
    """A guard with no pins protects nothing — fail loudly rather than pass."""
    assert PINS, f"no sentinels pinned in {PINS_PATH}"
    assert len(PINS) > 500, f"only {len(PINS)} sentinels pinned"


@needs_corpus
@pytest.mark.parametrize("key", KEYS)
def test_sentinel(key, signatures, only_courts):
    if only_courts and key.split("/")[0] not in only_courts:
        pytest.skip("not in --court selection")
    got = signatures.get(key)
    if got is None:
        pytest.skip("signature not computed in this selection")
    from harness.guard import _compare
    diffs = _compare(PINS[key], got)
    assert not diffs, "\n".join([f"{key}:"] + [f"  {d}" for d in diffs])


if not HAVE_CORPUS:      # keep collection honest when there is no corpus
    def test_guard_needs_the_corpus():
        pytest.skip("corpus not present; guard cannot run")
