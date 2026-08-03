from centralia.audit import audit_coverage


def test_body_sized_slip_notice_is_removed_by_its_fixed_text(extract):
    doc = extract("nmctapp", "silva_v._city_of_albuquerque.pdf")
    needle = "The slip opinion is the first version"

    assert not any(needle in str(row) for row in doc.summary)
    assert not any(
        needle in block.text
        for opinion in doc.opinions
        for block in opinion.blocks
    )
    assert any(needle in row for row in doc.dropped)

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]
