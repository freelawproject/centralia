import pytest

from centralia.audit import _matches, audit_coverage


@pytest.mark.parametrize(
    ("court", "filename", "placed_text", "old_residual"),
    (
        (
            "ctd",
            "gov.uscourts.ctd.152154.212.0.pdf",
            "NANCY NAVARRETTA, in her official",
            "NANCY NAVARRETTA, in her official)",
        ),
        (
            "miwd",
            "gov.uscourts.miwd.121585.5.0.pdf",
            "-v-",
            "-v- )",
        ),
        (
            "miwd",
            "gov.uscourts.miwd.87803.121.0.pdf",
            "-v-",
            "-v- )",
        ),
        (
            "mad",
            "gov.uscourts.mad.286196.21.0.pdf",
            "ABIRA MEDICAL LABORATORES, LLC,",
            "ABIRA MEDICAL LABORATORES, LLC,)",
        ),
    ),
)
def test_fused_parenthetical_caption_rail_is_not_unplaced_content(
    extract, court, filename, placed_text, old_residual
):
    doc = extract(court, filename)

    assert placed_text in str(doc.summary)
    assert not any(
        old_residual in item.get("text", "") for item in doc.residual
    )

    result = audit_coverage(doc, doc.source_path)
    assert not any(page == 1 for page, _text in result.missing)


def test_trailing_parenthesis_in_caption_content_remains_significant():
    # The first ')' is a rail; the last closes Rule 26(f) and must not be
    # discarded merely because the line has more closes than opens overall.
    raw = ") ORDER FOR RULE 26(f)"
    output_missing_the_final_parenthesis = ")orderforrule26(f"

    assert not _matches(raw, output_missing_the_final_parenthesis)
