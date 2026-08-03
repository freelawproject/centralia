from centralia.audit import audit_coverage


def test_advisory_opinion_has_an_opinion_body(extract):
    doc = extract("sd", "advisory_opinion.pdf")

    assert doc.doc_type == "opinion"
    assert len(doc.opinions) == 1
    assert doc.opinions[0].author == ""
    assert doc.opinions[0].blocks[0].kind == "heading"
    assert "AN OPINION REQUESTED BY HIS EXCELLENCY" in doc.opinions[0].blocks[0].text
    assert "§ 5 OF THE SOUTH DAKOTA CONSTITUTION" in doc.opinions[0].blocks[0].text

    paragraphs = [
        block.text for block in doc.opinions[0].blocks if block.kind == "p"
    ]
    assert any(text.startswith("[¶1.]") for text in paragraphs)
    assert any(text.startswith("[¶24.]") for text in paragraphs)

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]


def test_gustafson_running_docket_and_paragraph_geometry(extract):
    doc = extract("sd", "dept_of_transportation_v._gustafson.pdf")

    assert "#30723" in doc.dropped
    assert all(
        "#30723" not in block.text
        for opinion in doc.opinions
        for block in opinion.blocks
    )

    majority = doc.opinions[0]
    numbered = [
        block.text for block in majority.blocks if block.text.startswith("[¶")
    ]
    assert "[¶1.]" in majority.blocks[0].text
    assert numbered[0].startswith("[¶2.]")
    assert any(text.startswith("[¶26.]") for text in numbered)
    assert any(text.startswith("[¶61.]") for text in numbered)

    dissent = doc.opinions[1]
    assert dissent.blocks[-1].kind == "p"
    assert dissent.blocks[-1].text == "[¶72.]  MYREN, Justice, joins this writing."


def test_gustafson_wrapped_issue_titles_are_single_headings(extract):
    doc = extract("sd", "dept_of_transportation_v._gustafson.pdf")
    headings = [
        block.text for block in doc.opinions[0].blocks if block.kind == "heading"
    ]

    first = next(text for text in headings if "1. Whether the Gustafsons" in text)
    second = next(text for text in headings if "2. Whether the Gustafsons" in text)
    assert "access to 41st Street as abutting landowners" in first
    assert "compensation for a substantial impairment of" in second
    assert "access.</em></strong>" in second

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]
