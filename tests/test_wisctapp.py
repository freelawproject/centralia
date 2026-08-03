from centralia.audit import audit_coverage


def test_masthead_rows_can_split_between_headmatter_and_removed_notice(extract):
    doc = extract(
        "wisctapp",
        "adams_outdoor_advertising_limited_partnership_v._city_of_madison.pdf",
    )

    summary = " ".join(
        str(row.get("html", "")) if isinstance(row, dict) else str(row)
        for row in doc.summary
    )
    assert "DATED AND FILED" in summary
    assert "Samuel A. Christensen" in summary
    notice = next(
        row
        for row in doc.dropped
        if "This opinion is subject to further editing" in row
    )
    assert "petition to review an adverse decision" in notice

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]
    assert any("DATED AND FILED" in text for _page, text in result.dropped)
