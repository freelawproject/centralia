import html
import re

from centralia import get_extractor
from centralia.audit import audit_coverage


def _plain(value):
    return html.unescape(re.sub(r"<[^>]+>", "", str(value)))


def test_signed_reconsideration_ruling_is_an_order(extract):
    doc = extract("cand", "gov.uscourts.cand.345583.148.0.pdf")

    assert doc.doc_type == "order"
    assert doc.opinions[0].type == "order"
    assert doc.opinions[0].author == "BETH LABSON FREEMAN"
    assert doc.signature

    extractor = get_extractor("cand")
    audited = extractor.extract(doc.source_path)
    result = audit_coverage(audited, doc.source_path, extractor=extractor)
    assert result.ok, result.missing[:5]


def test_accepted_proposed_order_keeps_real_deadline_tables(extract):
    doc = extract("cand", "gov.uscourts.cand.444034.106.0.pdf")

    assert doc.doc_type == "order"
    assert doc.opinions[0].type == "order"
    assert doc.opinions[0].author == "Araceli Martinez-Olguín"

    summary = " ".join(_plain(item) for item in doc.summary)
    assert "UNITED STATES DISTRICT COURT" in summary
    assert "Telephone:" not in summary
    assert any("submitting attorney headmatter removed" in row for row in doc.dropped)

    tables = [
        block
        for opinion in doc.opinions
        for block in opinion.blocks
        if block.kind == "table"
    ]
    assert len(tables) == 2
    first_table = " ".join(
        str(cell or "")
        for row in tables[0].payload["rows"]
        for cell in row
    )
    assert "Event" in first_table
    assert "Current Deadline" in first_table
    assert "Proposed New" in first_table
    assert "Deadline" in first_table
    assert all(footnote.label != "?" for footnote in doc.opinions[0].footnotes)
    assert not any(
        "Case No." in _plain(item) and re.search(r"-\s*\d+\s*-", _plain(item))
        for item in doc.signature
    )

    extractor = get_extractor("cand")
    audited = extractor.extract(doc.source_path)
    result = audit_coverage(audited, doc.source_path, extractor=extractor)
    assert result.ok, result.missing[:5]
