from html import unescape

from centralia.audit import audit_coverage


def _all_text(doc):
    html = " ".join(
        block.text
        for opinion in doc.opinions
        for block in opinion.blocks
        if block.kind != "table"
    )
    out = []
    inside = False
    for char in html:
        if char == "<":
            inside = True
        elif char == ">":
            inside = False
        elif not inside:
            out.append(char)
    return unescape("".join(out))


def test_standing_order_keeps_page_top_continuations_and_structure(extract):
    doc = extract("cacd", "gov.uscourts.cacd.1028586.10.0.pdf")
    text = _all_text(doc)

    assert doc.doc_type == "order"
    assert doc.opinions[0].type == "order"
    assert doc.opinions[0].author == "KENLY KIYA KATO"
    assert "UNITED STATES DISTRICT COURT" not in doc.opinions[0].blocks[0].text
    assert "PLEASE READ THIS ORDER CAREFULLY" in doc.opinions[0].blocks[0].text
    assert "UNLESS OTHERWISE ORDERED BY THE COURT" in text
    assert "those designations are identified" in text
    assert "The Court thanks the parties" in text
    assert not any("those designations are identified" in row for row in doc.dropped)
    assert any(block.kind == "heading" for block in doc.opinions[0].blocks)
    assert any(block.kind == "table" for block in doc.opinions[0].blocks)

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]


def test_civil_minutes_keeps_bottom_line_and_drops_repeated_form_head(extract):
    doc = extract("cacd", "gov.uscourts.cacd.999943.5.0.pdf")
    text = _all_text(doc)

    assert doc.doc_type == "order"
    assert doc.opinions[0].type == "order"
    assert doc.opinions[0].author == "Sheri Pym"
    assert "Boerckel, 526 U.S. 838" in text
    assert not any("Boerckel, 526 U.S. 838" in row for row in doc.dropped)
    assert text.count("CIVIL MINUTES - GENERAL") == 0
    assert any("CIVIL MINUTES - GENERAL" in row for row in doc.dropped)

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]
