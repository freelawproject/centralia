from centralia.audit import audit_coverage
from centralia.render import render_html


def test_shabazz_uses_shallow_indent_paragraphs_and_headings(extract):
    doc = extract("ind", "ajaylan_m_shabazz_v._state_of_indiana.pdf")
    blocks = doc.opinions[0].blocks

    paragraphs = [block for block in blocks if block.kind == "p"]
    headings = [block.text for block in blocks if block.kind == "heading"]
    assert len(paragraphs) >= 30
    assert any("Facts and Procedural History" in text for text in headings)
    assert any("Standard of Review" in text for text in headings)
    first_issue = next(text for text in headings if "I. The trial court" in text)
    second_issue = next(text for text in headings if "II. The error" in text)
    assert "Jones to testify virtually" in first_issue
    assert "was harmless" in second_issue
    assert any("Conclusion" in text for text in headings)
    assert not any("\xa0" in str(block.text or "") for block in blocks)
    html = render_html(doc)
    assert "\xa0" not in html

    indented = [
        block
        for block in paragraphs
        if block.payload.get("first_line_indent") is not None
    ]
    assert len(indented) >= 25
    assert {block.payload["first_line_indent"] for block in indented} == {14.4}
    assert 'style="text-indent:14.4pt"' in html
    assert not any(
        block.payload.get("first_line_indent")
        for block in blocks
        if block.kind in ("heading", "blockquote")
    )

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]


def test_indiana_keeps_non_dominant_nbsp_usage(extract):
    doc = extract("ind", "yerano_martinez_v._jeffrey_smith.pdf")

    assert any(
        "\xa0" in str(block.text or "")
        for opinion in doc.opinions
        for block in opinion.blocks
    )
    indents = {
        block.payload.get("first_line_indent")
        for opinion in doc.opinions
        for block in opinion.blocks
        if block.payload.get("first_line_indent")
    }
    assert {14.4, 18.0} <= indents
    html = render_html(doc)
    assert 'style="text-indent:14.4pt"' in html
    assert 'style="text-indent:18.0pt"' in html
