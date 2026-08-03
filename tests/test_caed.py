import re

from centralia.audit import audit_coverage


def test_joint_arbitration_notice_is_a_party_filing(extract):
    doc = extract("caed", "gov.uscourts.caed.477764.17.0.pdf")

    assert doc.doc_type == "filing"
    assert all(not opinion.author for opinion in doc.opinions)
    assert any("/s/ Jihad Smaili" in block.text for block in doc.opinions[0].blocks)

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]


def test_stipulated_dismissal_is_a_party_filing_with_visible_footer(extract):
    doc = extract("caed", "gov.uscourts.caed.489415.13.0.pdf")

    assert doc.doc_type == "filing"
    assert all(not opinion.author for opinion in doc.opinions)
    assert any(
        "By: /s/ Carol B. Lewis"
        in " ".join(re.sub(r"<[^>]+>", "", block.text).split())
        for block in doc.opinions[0].blocks
    )
    assert any("ATTORNEYSATLAW" in row.replace(" ", "") for row in doc.dropped)
    assert any("WITHOUT PREJUDICE" in row for row in doc.dropped)

    result = audit_coverage(doc, doc.source_path)
    assert result.ok, result.missing[:5]
