from pathlib import Path

import pytest

from centralia.audit import audit_coverage
from centralia.registry import get_extractor


ASSETS = Path(__file__).resolve().parent.parent / "assets" / "txed"


def _extract(name):
    path = ASSETS / name
    if not path.exists():
        pytest.skip(f"missing asset: {path}")
    extractor = get_extractor("txed")
    return extractor, extractor.extract(str(path))


def test_narrow_txed_template_is_not_all_blockquotes():
    extractor, doc = _extract("gov.uscourts.txed.243348.10.0.pdf")
    blocks = [b for op in doc.opinions for b in op.blocks]

    assert extractor._txed_narrow_layout is True
    assert blocks
    assert not any(b.kind == "blockquote" for b in blocks)
    assert blocks[1].text.startswith("Petitioner, a former Wood County Jail")


def test_docket_control_order_starts_before_schedule():
    _extractor, doc = _extract("gov.uscourts.txed.243659.20.0.pdf")
    blocks = [b for op in doc.opinions for b in op.blocks]
    table_text = " ".join(
        str(cell or "")
        for block in blocks
        if block.kind == "table"
        for row in block.payload.get("rows", [])
        for cell in row
    )

    assert blocks[0].text == "<strong>DOCKET CONTROL ORDER</strong>"
    assert len([block for block in blocks if block.kind == "table"]) == 4
    assert "Defendant to disclose final invalidity theories" in table_text
    assert not any(
        item.get("kind") == "content" for item in doc.residual
    )


@pytest.mark.parametrize("name", [p.name for p in sorted(ASSETS.glob("*.pdf"))])
def test_txed_source_coverage(name):
    extractor, doc = _extract(name)
    audit = audit_coverage(doc, str(ASSETS / name), extractor)

    assert audit.ok, audit.missing[:5]
