"""Corpus-wide tests.

Two tiers:
  * SMOKE — every court that has assets must extract without crashing and
    return a well-formed document. This guarantees every court "has output".
  * STRICT — registered (tuned) courts must also satisfy content invariants
    (authored opinions have a body, opinion docs yield opinions) and high line
    coverage. Unregistered courts fall back to the generic extractor and are
    only smoke-tested until a dedicated extractor is built for them.

A small sample per court keeps the run tractable; raise the SAMPLE_* knobs to
widen coverage.
"""

from pathlib import Path

import pytest

from centralia import get_extractor
from centralia.audit import audit_coverage
from centralia.models import DocType
from centralia.registry import EXTRACTORS

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SMOKE_PER_COURT = 2
STRICT_PER_COURT = 5

_AUTHORED = {DocType.OPINION}  # types that should carry opinions


def _all_courts():
    if not ASSETS.exists():
        return []
    return sorted(
        d.name for d in ASSETS.iterdir() if d.is_dir() and any(d.glob("*.pdf"))
    )


def _sample(courts, n):
    out = []
    for court in courts:
        for f in sorted((ASSETS / court).glob("*.pdf"))[:n]:
            out.append((court, f.name))
    return out


SMOKE = _sample(_all_courts(), SMOKE_PER_COURT)
STRICT = _sample([c for c in EXTRACTORS if (ASSETS / c).exists()], STRICT_PER_COURT)


@pytest.mark.parametrize(
    "court,filename", SMOKE, ids=[f"{c}:{f[:36]}" for c, f in SMOKE]
)
def test_smoke(court, filename):
    """Every court extracts without error into a well-formed document."""
    doc = get_extractor(court).extract(str(ASSETS / court / filename))
    assert doc.doc_type in DocType.ALL
    assert isinstance(doc.opinions, list)


@pytest.mark.parametrize(
    "court,filename", STRICT, ids=[f"{c}:{f[:36]}" for c, f in STRICT]
)
def test_invariants(court, filename):
    """Registered courts: opinions are well-formed and opinion docs parse."""
    doc = get_extractor(court).extract(str(ASSETS / court / filename))
    for op in doc.opinions:
        if op.type != DocType.ORDER:  # orders may be authorless/per curiam
            assert op.author.strip(), f"empty author: {court}/{filename}"
        assert op.blocks, f"opinion with no blocks: {court}/{filename}"
    if doc.doc_type in _AUTHORED:
        assert doc.opinions, f"opinion doc, no opinions: {court}/{filename}"


@pytest.mark.parametrize(
    "court,filename", STRICT, ids=[f"{c}:{f[:36]}" for c, f in STRICT]
)
def test_completeness(court, filename):
    """Registered courts: most source lines are accounted for somewhere."""
    path = ASSETS / court / filename
    doc = get_extractor(court).extract(str(path))
    r = audit_coverage(doc, str(path))
    if r.total == 0:
        pytest.skip("no extractable text")
    pct = r.covered / r.total
    assert pct >= 0.85, (
        f"{court}/{filename}: {pct:.0%} accounted for; missing e.g. "
        f"{[m[1][:50] for m in r.missing[:3]]}"
    )
