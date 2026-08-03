import pytest

from centralia.audit import audit_coverage


@pytest.mark.parametrize(
    ("filename", "notice"),
    [
        ("cantu_v._collins.pdf", "NOTE: This disposition is nonprecedential."),
        (
            "foras_technologies_ltd._v._bmw_of_north_america_llc.pdf",
            "NOTE: This order is nonprecedential.",
        ),
    ],
)
def test_nonprecedential_notice_is_visible_furniture(extract, filename, notice):
    doc = extract("cafc", filename)

    assert notice not in " ".join(map(str, doc.summary))
    assert notice in doc.dropped
    assert all(
        notice not in str(block.text)
        for opinion in doc.opinions
        for block in opinion.blocks
    )

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]
