from pathlib import Path

from centralia.registry import get_extractor


ASSETS = Path(__file__).parents[1] / "assets" / "ala"


def test_full_page_footnote_continuation_is_retained():
    """Footnote 10 starts on page 52, occupies all of page 53, and ends on 54."""
    pdf = (
        ASSETS
        / "in_re_gold_hill_methodist_church_v._alabama-west_florida_conference_of_the.pdf"
    )
    doc = get_extractor("ala").extract(str(pdf))

    footnote = next(
        fn
        for opinion in doc.opinions
        for fn in opinion.footnotes
        if fn.label == "10"
    )
    text = " ".join(text for _kind, text in footnote.paragraphs)

    assert "passage in <u>Jones v. Wolf</u>" in text
    assert "neutral-principles method" in text
    assert "constitutional documents of churches" in text
    assert not [
        item
        for item in doc.residual
        if item.get("kind") == "content" and item.get("page") == 53
    ]


def test_fused_footnote_labels_do_not_produce_residual_content():
    """PDF text extraction fuses Alabama's raised labels to the first word."""
    pdf = ASSETS / "leonard_l._hixon_v._premier_medical_group_inc..pdf"
    doc = get_extractor("ala").extract(str(pdf))

    assert not [
        item for item in doc.residual if item.get("kind") == "content"
    ]


def test_math_font_hyphens_do_not_split_numbered_blockquotes():
    pdf = (
        ASSETS
        / "ex_parte_b.t._roberts_in_his_capacity_as_a_member_of_the_auburn_university.pdf"
    )
    doc = get_extractor("ala").extract(str(pdf))
    blocks = [block for opinion in doc.opinions for block in opinion.blocks]

    paragraph_191 = next(block for block in blocks if '"191.' in block.text)
    paragraph_192 = next(block for block in blocks if '"192.' in block.text)

    assert paragraph_191.kind == "blockquote"
    assert "four‐year period" in paragraph_191.text
    assert "personnel file maintained would not" in paragraph_191.text
    assert paragraph_191.text.endswith("future at Auburn University.")
    assert paragraph_192.kind == "blockquote"
    assert "Maxwell‐Evans knew or should" in paragraph_192.text
    assert paragraph_192.text.endswith('personal records."')
    assert not [
        item for item in doc.residual if item.get("kind") == "content"
    ]


def test_citation_docket_is_not_dropped_as_running_header():
    pdf = (
        ASSETS
        / "ex_parte_city_of_birmingham_petition_for_writ_of_mandamus_civil_in_re.pdf"
    )
    doc = get_extractor("ala").extract(str(pdf))
    body = " ".join(
        block.text for opinion in doc.opinions for block in opinion.blocks
    )

    assert (
        "<u>Ex parte City of Orange Beach</u>, "
        "[Ms. SC-2024-0526, Apr. 4, 2025] ___ So. 3d ___, ___ (Ala. 2025)."
        in body
    )
    assert not [
        item for item in doc.residual if item.get("kind") == "content"
    ]


def test_indented_case_number_opener_is_not_a_running_header():
    names = (
        "highland_rim_investments_llc_and_monique_dollonne_v._kindra_cooper.pdf",
        "highland_rim_investments_llc_v._kindra_cooper.pdf",
    )
    opener = "In case number SC-2025-0599, Highland Rim Investments, LLC,"

    for name in names:
        doc = get_extractor("ala").extract(str(ASSETS / name))
        body = " ".join(
            block.text for opinion in doc.opinions for block in opinion.blocks
        )
        assert opener in body
        assert not [
            item for item in doc.residual if item.get("kind") == "content"
        ]


def test_docket_citations_inside_later_opinions_are_not_headers():
    names = (
        "russell_a._collins_and_stacey_d._collins_v._west_alabama_bank__trust.pdf",
        "russell_a._collins_and_stacey_d._collins_v._west_alabama_bank__trust_1.pdf",
    )
    for name in names:
        doc = get_extractor("ala").extract(str(ASSETS / name))
        body = " ".join(
            block.text for opinion in doc.opinions for block in opinion.blocks
        )
        assert "[Ms. SC-2023-0904, Nov. 22, 2024]" in body
        assert "dissent in case no. SC-2024-0275." in body
        assert not [
            item for item in doc.residual if item.get("kind") == "content"
        ]


def test_standalone_footnote_label_is_returned():
    pdf = (
        ASSETS
        / "traveka_stanley_reginald_burrell_charlie_gray_jermaine_pringle_and.pdf"
    )
    doc = get_extractor("ala").extract(str(pdf))
    labels = {
        footnote.label
        for opinion in doc.opinions
        for footnote in opinion.footnotes
    }

    assert "12" in labels
    assert not [
        item for item in doc.residual if item.get("kind") == "content"
    ]
