from centralia import get_extractor
from centralia.audit import audit_coverage
from centralia.render import render_casebody, render_html


def test_criminal_judgment_is_an_order_and_keeps_form_content(extract):
    doc = extract("kywd", "gov.uscourts.kywd.139760.50.0.pdf")

    assert doc.doc_type == "order"
    assert [op.type for op in doc.opinions] == ["order"]
    assert doc.signature and doc.signature[0]["__image__"]
    assert not any(block.kind == "image" for block in doc.opinions[0].blocks)
    assert not doc.opinions[0].footnotes  # signature rule is not a separator

    text = " ".join(block.text for block in doc.opinions[0].blocks)
    assert "Date of Imposition of Judgment" in text
    assert "The interest requirement is waived" in text
    assert "The interest requirement for the" in text
    assert any("USDC KYWD 245B" in line for line in doc.dropped)

    # Form columns reorder checkbox/caption tokens on a shared baseline, just
    # like a table.  The geometry-aware audit must still verify every token.
    extractor = get_extractor("kywd")
    audited = extractor.extract(doc.source_path)
    result = audit_coverage(audited, doc.source_path, extractor=extractor)
    assert result.ok, result.missing[:5]


def test_titled_order_and_widget_signature_are_recognized(extract):
    doc = extract("kywd", "gov.uscourts.kywd.143180.12.0.pdf")

    assert doc.doc_type == "order"
    assert [op.type for op in doc.opinions] == ["order"]
    assert doc.opinions[0].blocks[0].text.endswith(
        "ORDER ADOPTING REPORT AND RECOMMENDATION</strong>"
    )
    assert doc.opinions[0].blocks[1].text == (
        "<strong>AND ENTERING THE AGREED ORDER</strong>"
    )
    assert doc.signature[0]["__image__"]
    assert doc.signature[1] == "May 19, 2026"
    assert 'alt="signature"' in render_html(doc)


def test_pageid_citation_cannot_become_an_invented_list_item(extract):
    doc = extract("kywd", "gov.uscourts.kywd.143976.17.0.pdf")
    blocks = doc.opinions[0].blocks
    citation = next(block for block in blocks if "PageID.198" in block.text)

    assert citation.kind == "p"
    assert "PageID.198– 99)" in citation.text
    assert "Orozco Ortega asserts" in citation.text
    assert not any(
        block.kind == "ordered-list-item" and "Orozco Ortega asserts" in block.text
        for block in blocks
    )

    casebody = render_casebody(doc)
    assert "PageID.198– 99)" in casebody
    assert "<item>Orozco Ortega asserts" not in casebody


def test_widget_signature_is_exact_pdf_appearance_stream(extract):
    doc = extract("kywd", "gov.uscourts.kywd.141482.27.0.pdf")
    image = doc.signature[0]

    assert image["__image__"]
    assert image["src"].startswith("data:image/png;base64,")
    assert image["width"] == 240
    assert image["height"] == 90
    assert doc.signature[1] == "May 20, 2026"

    # This ordinary memorandum opinion remains an opinion; signature recovery
    # is independent of document-type classification.
    assert doc.doc_type == "opinion"


def test_kywd_regressions_have_complete_visible_text(extract):
    for filename in (
        "gov.uscourts.kywd.143180.12.0.pdf",
        "gov.uscourts.kywd.143976.17.0.pdf",
    ):
        doc = extract("kywd", filename)
        result = audit_coverage(doc, doc.source_path)
        assert result.ok, result.missing[:5]
