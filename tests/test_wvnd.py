from centralia import get_extractor
from centralia.audit import audit_coverage


def _page_one_content_residuals(doc):
    return [
        item
        for item in doc.residual
        if item.get("page") == 1 and item.get("kind") == "content"
    ]


def test_rule_bounded_title_is_placed_before_completeness_sweep(extract):
    doc = extract("wvnd", "gov.uscourts.wvnd.63703.37.0.pdf")

    assert doc.opinions[0].blocks[0].kind == "heading"
    assert "ORDER GRANTING IN PART AND DENYING IN PART" in (
        doc.opinions[0].blocks[0].text
    )
    assert not _page_one_content_residuals(doc)

    extractor = get_extractor("wvnd")
    result = audit_coverage(doc, doc.source_path, extractor=extractor)
    assert result.ok, result.missing[:5]


def test_dual_caption_uses_rule_beneath_real_document_title(extract):
    doc = extract("wvnd", "gov.uscourts.wvnd.39456.69.0.pdf")

    summary = str(doc.summary)
    assert "CRIMINAL NO. 1:16-CR-61" in summary
    assert "CIVIL NO. 1:25-CV-70" in summary
    assert "Respondent." in summary
    assert "MEMORANDUM OPINION AND ORDER ADOPTING" in (
        doc.opinions[0].blocks[0].text
    )
    assert not _page_one_content_residuals(doc)

    extractor = get_extractor("wvnd")
    result = audit_coverage(doc, doc.source_path, extractor=extractor)
    assert result.ok, result.missing[:5]
