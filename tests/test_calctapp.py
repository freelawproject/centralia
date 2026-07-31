from pathlib import Path

import pytest

from centralia.audit import audit_coverage
from centralia.registry import get_extractor
from centralia.render import render_casebody, render_html


ASSETS = Path(__file__).resolve().parent.parent / "assets" / "calctapp"


def _extract(name: str):
    path = ASSETS / name
    if not path.exists():
        pytest.skip(f"missing asset: {path}")
    extractor = get_extractor("calctapp")
    return path, extractor, extractor.extract(str(path))


def test_colonial_manor_preserves_order_opinion_and_page_geometry():
    path, extractor, doc = _extract("colonial_manor_inc._v._reyes.pdf")

    assert doc.docket_number == "24APLC00316"
    assert doc.parties == ["COLONIAL MANOR, INC.,", "VILMA REYES,"]
    assert len(doc.opinions) == 2

    order, opinion = doc.opinions
    assert order.type == "order"
    assert order.author == "P. McKay, P. J."
    assert order.caption
    assert opinion.type == "majority"
    assert opinion.author == "P. McKay, P. J."
    assert doc.panel == ["Ricciardulli, J.", "Guillemet, J."]

    # The four-line replacement and the one-line replacement share the same
    # deep left inset in the PDF.  Only those passages are blockquotes.
    quotes = [b.text for b in order.blocks if b.kind == "blockquote"]
    assert len(quotes) == 2
    assert quotes[0].startswith("It is the lessor’s burden to allege and prove")
    assert quotes[1] == "(SMRCCA, art. XVIII, § 1806, subd. (f))."

    # Hanging continuations remain attached to their numbered paragraphs.
    paragraphs = [b.text for b in order.blocks if b.kind == "p"]
    item_two = next(t for t in paragraphs if t.startswith("2. On page 4"))
    item_three = next(t for t in paragraphs if t.startswith("3. On page 5"))
    assert item_two.endswith("between the words “Reyes” and “who”.")
    assert "numbering of the subsequent footnotes shall be readjusted" in item_three

    # The final signature line is content.  The tiny lower-left compositor
    # mark and the caption's trailing rail glyph are not body paragraphs.
    body_texts = [b.text.strip() for op in doc.opinions for b in op.blocks]
    assert any("Ricciardulli, J. Guillemet, J." in t for t in body_texts)
    assert "jl" in doc.dropped
    assert "jl" not in body_texts
    assert ")" not in body_texts
    assert '<div class="dropline">jl</div>' in render_html(doc)

    # The attached order has folio 2; the opinion then restarts at 1 and runs
    # through 13.  Every printed opinion folio must survive in the output.
    casebody = render_casebody(doc)
    for folio in range(1, 14):
        assert f'<pagenumber value="{folio}"' in casebody

    coverage = audit_coverage(doc, str(path), extractor)
    assert coverage.ok, coverage.missing[:5]
    assert not doc.residual


def test_mata_statutory_items_are_geometry_based_blockquotes():
    _path, _extractor, doc = _extract(
        "mata_v._digital_recognition_network_inc..pdf"
    )
    blocks = [b for op in doc.opinions for b in op.blocks]
    quotes = [b.text for b in blocks if b.kind == "blockquote"]

    assert len(quotes) == 7
    assert quotes[0].startswith("“(A) The authorized purposes")
    assert quotes[-1].startswith("“(G) The length of time ALPR information")
    assert not any("Third and last" in text for text in quotes)
    assert any(
        b.kind == "p" and b.text.startswith("Third and last") for b in blocks
    )
