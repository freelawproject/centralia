"""The headmatter-criteria snapshots — NOT yet an assertion, and why.

`tests/fixtures/criteria.json` holds 48 snapshots across 11 courts, one per
printed FORMAT, chosen and explained in `tests/criteria_manifest.py`. It is
real ground truth and it should be a test.

It is not one yet because the snapshots are V1-SHAPED. They were ported from
the old repo and name their fields the way that engine did:

    date_filed   panel_line   lower_judge   prior_history   counsel   cases[]

while this engine's `Criteria` names them:

    decision_date   panel_line   lower_court_judge   history   attorneys
    parties / caption / case_name

Some pairs are obvious; others are not, and `cases[]` is a list of per-case
dicts with no counterpart at all — this engine keeps one criteria object per
document and puts consolidated captions in `caption`/`other_dockets`. Writing
that mapping by eye would either fail 48 tests for no reason or, worse, pass
by comparing the wrong fields.

So this file does the one honest thing available: it asserts the fixtures are
INTACT and reports the mapping gap, so the work is visible rather than
forgotten. Deciding the mapping is a task, not a guess — see the printout
under `-s`.
"""

from __future__ import annotations

import dataclasses as dc
import json
from pathlib import Path

import pytest

from conftest import needs_corpus  # noqa: F401

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _snapshots() -> dict:
    with open(FIXTURES / "criteria.json") as fh:
        return json.load(fh)


def test_the_snapshots_are_intact():
    """They are ground truth; losing them silently would cost real work."""
    snaps = _snapshots()
    assert len(snaps) >= 48, f"only {len(snaps)} criteria snapshots"
    assert len({k.split('/')[0] for k in snaps}) >= 11


def test_the_manifest_covers_every_snapshot_court():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from criteria_manifest import MANIFEST
    snap_courts = {k.split("/")[0] for k in _snapshots()}
    missing = snap_courts - set(MANIFEST)
    assert not missing, f"snapshots with no manifest entry: {sorted(missing)}"


def test_report_the_v1_to_v2_field_gap(capsys):
    """Names the fields that still need a mapping decision. Always passes —
    its job is to keep the gap visible, not to fail the build."""
    from centralia.model import Criteria
    v2 = {f.name for f in dc.fields(Criteria)}
    v1: set[str] = set()
    for snap in _snapshots().values():
        v1 |= set(snap)
        for case in snap.get("cases") or ():
            v1 |= {f"cases[].{k}" for k in case}
    unmapped = sorted(f for f in v1 if f not in v2)
    with capsys.disabled():
        if unmapped:
            print("\n  criteria.json fields with no v2 counterpart yet:")
            for f in unmapped:
                print(f"    {f}")
            print("  -> decide the mapping, then turn this file into "
                  "a real comparison.")
    assert True
