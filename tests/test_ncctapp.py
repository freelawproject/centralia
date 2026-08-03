from centralia import get_extractor
from centralia.audit import audit_coverage
from centralia.render import render_casebody, render_html


def _table_text(block):
    return " ".join(
        str(cell or "")
        for row in block.payload.get("rows", [])
        for cell in row
    )


def test_ahdi_multipage_assets_table_is_complete(extract):
    doc = extract("ncctapp", "ahdi_v._ahdi.pdf")
    blocks = doc.opinions[0].blocks
    tables = [block for block in blocks if block.kind == "table"]

    assert [table.page for table in tables] == [24, 25]
    assert tables[0].payload["rows"][0] == ["ASSETS", "VALUE"]
    assert tables[0].payload["has_header"] is True
    assert "[Redacted address] (marital home)" in _table_text(tables[0])
    assert "$455,000 ($147,000)" in _table_text(tables[0])

    assert tables[1].payload["continuation"] is True
    assert tables[1].payload["has_header"] is False
    continued = _table_text(tables[1])
    for value in (
        "Grover NC Land Parcel 52937",
        "$15,000",
        "Skyla/CMCU [b]usiness [c]hecking",
        "$104,888",
        "United Auto LLC (Inventory Value)",
        "$667,849",
        "2012 Land Rover LR4 HSE LUX",
        "$12,510",
        "Cryptocurrency",
        "$4[,]209",
    ):
        assert value in continued

    assert not any(item.get("kind") == "content" for item in doc.residual)
    ordinary_text = " ".join(
        block.text or "" for block in blocks if block.kind != "table"
    )
    assert "United Auto LLC (Inventory Value)" not in ordinary_text

    html = render_html(doc)
    casebody = render_casebody(doc)
    assert '<table class="continued">' in html
    assert '<table page="25">' in casebody
    page25 = casebody.split('<table page="25">', 1)[1].split("</table>", 1)[0]
    assert "<th>Grover" not in page25
    assert "<td>Grover NC Land Parcel" in page25

    extractor = get_extractor("ncctapp")
    audited = extractor.extract(doc.source_path)
    result = audit_coverage(audited, doc.source_path, extractor=extractor)
    assert result.ok, result.missing[:5]
