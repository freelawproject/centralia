from pathlib import Path
from collections import Counter

from centralia.audit import audit_coverage
from centralia.registry import get_extractor


ASSETS = Path(__file__).resolve().parent.parent / "assets" / "ca3"


def test_bps_direct_keeps_top_continuations_and_counsel():
    path = ASSETS / "bps_direct_llc_v..pdf"
    extractor = get_extractor("ca3")
    doc = extractor.extract(str(path))
    result = audit_coverage(doc, str(path), extractor=extractor)

    assert result.ok
    assert not doc.residual
    assert any("Counsel for Appellees" in str(item) for item in doc.trailer)


def test_kalshiex_preserves_restarted_dissent_footnotes():
    """The dissent restarts its footnote numbering at 1, so the document holds
    two runs of low labels. All 78 must survive — and land on the writing that
    printed them, not pooled onto one merged opinion."""
    path = ASSETS / "kalshiex_llc_v._mary_jo_flaherty.pdf"
    extractor = get_extractor("ca3")
    doc = extractor.extract(str(path))
    result = audit_coverage(doc, str(path), extractor=extractor)

    assert result.ok
    assert not doc.residual
    assert [op.type for op in doc.opinions] == ["majority", "dissent"]
    assert sum(len(op.footnotes) for op in doc.opinions) == 78
    for op in doc.opinions:
        labels = [fn.label for fn in op.footnotes]
        assert labels == [str(i) for i in range(1, len(labels) + 1)]
        assert max(Counter(labels).values()) == 1


def test_counsel_addendum_between_opinions_is_ending_matter():
    """CA3 prints the counsel appearances AFTER the opinion they belong to —
    here between the majority's disposition and the dissent's byline. They are
    ending matter, and the writing that follows them is a separate opinion."""
    path = ASSETS / "kalshiex_llc_v._mary_jo_flaherty.pdf"
    extractor = get_extractor("ca3")
    doc = extractor.extract(str(path))
    trailer = [str(item) for item in doc.trailer]

    # The first appearance group is printed ABOVE its 'Counsel for' caption, so
    # the caption alone does not bound the block.
    assert trailer[0] == "Matthew J. Platkin"
    assert any("Counsel for Appellants" in line for line in trailer)
    assert any("Counsel for Appellee" in line for line in trailer)
    # ... and none of it is left glued to the majority's closing paragraph.
    assert "Platkin" not in doc.opinions[0].blocks[-1].text
    assert doc.opinions[0].blocks[-1].text.rstrip().endswith("We will affirm.")


def test_jabar_evans_accepts_uppercase_byline_and_ruleless_footnotes():
    path = ASSETS / "united_states_v._jabar_evans.pdf"
    extractor = get_extractor("ca3")
    doc = extractor.extract(str(path))
    result = audit_coverage(doc, str(path), extractor=extractor)

    assert result.ok
    assert doc.doc_type == "opinion"
    assert doc.opinions[0].author == "RESTREPO, CIRCUIT JUDGE"
    assert [fn.label for fn in doc.opinions[0].footnotes] == [
        str(i) for i in range(1, 10)
    ]
