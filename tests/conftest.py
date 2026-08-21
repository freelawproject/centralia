"""Shared fixtures. The corpus lives in the OLD repo and is referenced in
place, so every corpus-backed test SKIPS cleanly where it is absent — CI can
run the contract tests without 2.7 GB of PDFs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from centralia.settings import CORPUS_ROOT  # noqa: E402

HAVE_CORPUS = CORPUS_ROOT.is_dir()
needs_corpus = pytest.mark.skipif(
    not HAVE_CORPUS, reason=f"corpus not present at {CORPUS_ROOT}")


def pytest_addoption(parser):
    parser.addoption("--court", action="append", default=[],
                     help="limit corpus tests to these court ids")


@pytest.fixture(scope="session")
def only_courts(pytestconfig) -> set[str]:
    return set(pytestconfig.getoption("--court") or ())


@pytest.fixture(scope="session")
def sample_pdf() -> Path:
    """One born-digital record, for contract tests that need a real document."""
    if not HAVE_CORPUS:
        pytest.skip("corpus not present")
    for court, stem in (("nmariana", "in_re_commonwealth"),
                        ("neb", "state_v._kellogg"),
                        ("scotus", "abouammo_v._united_states")):
        p = CORPUS_ROOT / court / f"{stem}.pdf"
        if p.is_file():
            return p
    hits = sorted(CORPUS_ROOT.glob("*/*.pdf"))
    if not hits:
        pytest.skip("corpus directory is empty")
    return hits[0]


@pytest.fixture(scope="session")
def sample_doc(sample_pdf):
    from centralia.pipeline import extract
    return extract(str(sample_pdf), sample_pdf.parent.name).document
