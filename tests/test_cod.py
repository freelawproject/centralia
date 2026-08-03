from pathlib import Path

import pytest

from centralia.audit import audit_coverage
from centralia.registry import get_extractor
from centralia.render import render_casebody, render_html


ASSETS = Path(__file__).resolve().parent.parent / "assets" / "cod"


def _extract(name: str):
    path = ASSETS / name
    if not path.exists():
        pytest.skip(f"missing asset: {path}")
    extractor = get_extractor("cod")
    return path, extractor, extractor.extract(str(path))


def test_lewandowski_cross_page_footnotes_are_complete():
    path, extractor, doc = _extract("gov.uscourts.cod.226382.273.0.pdf")
    assert len(doc.opinions) == 1

    opinion = doc.opinions[0]
    footnotes = {
        fn.label: " ".join(text for _kind, text in fn.paragraphs)
        for fn in opinion.footnotes
    }
    assert list(footnotes) == ["1", "2", "3", "4"]

    # Footnotes 3 and 4 each continue below an unlabeled separator on the next
    # physical page.  Their complete final sentences and citations stay with
    # the note instead of becoming indented body paragraphs.
    assert "A plaintiff’s pro se status does not entitle him" in footnotes["3"]
    assert "Montoya v. Chao" in footnotes["3"]
    assert "unfavorable to that party may tip the balance at trial" in footnotes["4"]
    assert footnotes["4"].endswith(
        "Fed. R. Civ. P. 37 advisory committee note."
    )

    body = " ".join(block.text for block in opinion.blocks)
    assert "A plaintiff’s pro se status does not entitle him" not in body
    assert "unfavorable to that party may tip the balance at trial" not in body
    assert "Fed. R. Civ. P. 37 advisory committee note." not in body

    casebody = render_casebody(doc)
    html = render_html(doc)
    assert "unfavorable to that party may tip the balance at trial" in casebody
    assert "unfavorable to that party may tip the balance at trial" in html

    coverage = audit_coverage(doc, str(path), extractor)
    assert coverage.ok, coverage.missing[:5]


def test_bonfil_rivera_conclusion_preserves_numbered_order_items():
    path, extractor, doc = _extract("gov.uscourts.cod.253935.22.0.pdf")
    blocks = doc.opinions[0].blocks

    conclusion = next(i for i, block in enumerate(blocks) if "CONCLUSION" in block.text)
    tail = blocks[conclusion:]
    assert [block.kind for block in tail[:7]] == [
        "heading",
        "p",
        "ordered-list-item",
        "ordered-list-item",
        "ordered-list-item",
        "p",
        "p",
    ]

    items = [block.text for block in tail if block.kind == "ordered-list-item"]
    assert len(items) == 3
    assert items[0].startswith("1) Petitioner’s Motion to Enforce")
    assert items[0].endswith("is <strong>GRANTED</strong>;")
    assert items[1].startswith("2) Respondents <strong>SHALL RELEASE")
    assert items[2].startswith("3) On or before July 30, 2026")
    assert tail[5].text == "Dated: July 23, 2026"
    assert tail[6].text == "BY THE COURT:"

    casebody = render_casebody(doc)
    assert '<list type="ordered">' in casebody
    assert casebody.count("<item>") == 3

    coverage = audit_coverage(doc, str(path), extractor)
    assert coverage.ok, coverage.missing[:5]
