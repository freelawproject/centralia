"""CA11 (Eleventh Circuit) regression lock-in.

ca11 sets opinions in a NARROW DanteMTPro column (left margin x0≈126) and, on
pages 2+, prints a running header below the bates stamp that names the current
opinion and resets its page count:

    24-13309 Opinion of the Court 3   /   3 Opinion of the Court 24-13309
    25-14065 LAGOA, J., Dissenting 1  /   2 ABUDU, J., Concurring 25-11375

That header is the opinion map: a change of name marks a new opinion (judge +
kind), so detection keys on it rather than on bylines (ca11 bylines aren't bold
and wrap across lines). These tests pin:

  * ``_running_header_name`` parses the header (both orderings) and REJECTS body
    citations like '(Gorsuch, J., concurring)' — the loose version exploded
    ismael_perez into a dozen phantom opinions;
  * multi-opinion detection (incl. a concurrence by the SAME judge as the
    majority — northfield);
  * the running header never lands in the body;
  * the narrow single-spaced column is read as paragraphs, not blockquotes;
  * every source line is accounted for.

Assets are gitignored, so tests skip cleanly when a PDF is absent.
"""

from pathlib import Path

import pytest

from centralia import get_extractor
from centralia.audit import audit_coverage

COURT = "ca11"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / COURT

_EXTRACTOR = get_extractor(COURT)
_CACHE: dict = {}


def _extract(stem: str):
    p = ASSETS / f"{stem}.pdf"
    if not p.exists():
        pytest.skip(f"missing asset: {p}")
    if stem not in _CACHE:
        _CACHE[stem] = _EXTRACTOR.extract(str(p))
    return _CACHE[stem]


def _stems():
    if not ASSETS.exists():
        return []
    return sorted(p.stem for p in ASSETS.glob("*.pdf"))


# --------------------------------------------------- running-header parser
@pytest.mark.parametrize(
    "line,expected",
    [
        ("25-11375 Opinion of the Court 3", "Opinion of the Court"),
        ("3 Opinion of the Court 25-11375", "Opinion of the Court"),
        ("25-14065 LAGOA, J., Dissenting 1", "LAGOA, J., Dissenting"),
        ("2 ABUDU, J., Concurring 25-11375", "ABUDU, J., Concurring"),
        ("10 Opinion of the Court 24-11946", "Opinion of the Court"),
    ],
)
def test_running_header_parses(line, expected):
    assert _EXTRACTOR._running_header_name(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        # body citations / prose that mention concur/dissent — NOT headers
        "U.S. at 747 (Gorsuch, J., concurring)",
        "Our dissenting colleague suggests that our reading is wrong.",
        "519 U.S. 357, 366 (Kennedy, J., dissenting)",
        "the Court explained, see id., that the dissenting view fails",
        "We describe the background of this appeal in two parts.",
    ],
)
def test_running_header_rejects_body(line):
    assert _EXTRACTOR._running_header_name(line) is None


# --------------------------------------------------------- opinion structure
@pytest.mark.parametrize(
    "stem,types,authors",
    [
        # majority + a concurrence by the SAME judge
        (
            "northfield_insurance_company_v._north_brook_industries_inc.",
            ["majority", "concurrence"],
            ["TJOFLAT", "TJOFLAT"],
        ),
        # majority + one concurrence (must NOT split into two)
        (
            "associated_builders_and_contractors_florida_first_coast_chapter_v._general",
            ["majority", "concurrence"],
            ["WILLIAM PRYOR", "ABUDU"],
        ),
        # majority + a single dissent (was 12 phantom opinions before the fix)
        (
            "ismael_perez_v._assistant_field_office_director_krome_north_service",
            ["majority", "dissent"],
            ["MARCUS", "LAGOA"],
        ),
        # single opinion
        ("abigail_marbut_v._matthew_phillips", ["majority"], ["WILLIAM PRYOR"]),
    ],
)
def test_opinions(stem, types, authors):
    doc = _extract(stem)
    assert [op.type for op in doc.opinions] == types, (
        f"{stem}: {[op.author for op in doc.opinions]}"
    )
    for op, name in zip(doc.opinions, authors):
        assert op.author.upper().startswith(name.upper()), f"{stem}: {op.author!r}"


@pytest.mark.parametrize(
    "stem,opinions",
    [
        # (type, author-prefix, footnote-count) per opinion — five diverse
        # multi-opinion ca11 cases pinned exactly.
        (
            "byron_chemaly_v._eddie_lampert",
            [("majority", "JORDAN", 6), ("dissent", "HULL", 0)],
        ),
        (
            "friends_of_the_everglades_inc._v._secretary_of_the_u.s._department_of",
            [("majority", "WILLIAM PRYOR", 0), ("dissent", "ABUDU", 3)],
        ),
        (
            "l.w._v._commissioner_of_the_georgia_department_of_communit",
            [("majority", "BRASHER", 1), ("concurrence", "GRANT", 2)],
        ),
        (
            "roger_tejon_v._zeus_networks_llc",
            [("majority", "KIDD", 1), ("dissent", "BRANCH", 4)],
        ),
        (
            "the_lane_construction_corporation_v._skanska_usa_civil_southeast_inc.",
            [("majority", "TJOFLAT", 26), ("concurrence", "NEWSOM", 0)],
        ),
    ],
)
def test_five_pdfs(stem, opinions):
    """Exact opinion structure (type, author, footnote count) for five
    representative ca11 documents."""
    doc = _extract(stem)
    assert [op.type for op in doc.opinions] == [o[0] for o in opinions], (
        f"{stem}: {[(op.type, op.author) for op in doc.opinions]}"
    )
    for op, (typ, author, fn) in zip(doc.opinions, opinions):
        assert op.author.upper().startswith(author.upper()), f"{stem}: {op.author!r}"
        assert len(op.footnotes) == fn, (
            f"{stem}: {op.author!r} has {len(op.footnotes)} footnotes, want {fn}"
        )


def test_northfield_footnotes():
    """The footnote separator sits at the narrow column (x0≈126), not x0≈72 —
    miss that and footnotes vanish into the body. northfield carries 7 in the
    majority and 2 in the concurrence."""
    doc = _extract("northfield_insurance_company_v._north_brook_industries_inc.")
    counts = [len(op.footnotes) for op in doc.opinions]
    assert counts == [7, 2], counts


@pytest.mark.parametrize("stem", _stems())
def test_footnote_markers_have_footnotes(stem):
    """If the body cites footnote markers, the footnotes must be captured (not
    left in the body for want of the separator)."""
    doc = _extract(stem)
    markers = sum(
        b.text.count("<footnotemark") for op in doc.opinions for b in op.blocks
    )
    captured = sum(len(op.footnotes) for op in doc.opinions) + len(
        doc.headmatter_footnotes
    )
    if markers >= 2:
        assert captured >= 1, f"{stem}: {markers} markers but 0 footnotes captured"


# ----------------------------------------------------------- corpus invariants
@pytest.mark.parametrize("stem", _stems())
def test_no_running_header_in_body(stem):
    doc = _extract(stem)
    for op in doc.opinions:
        for b in op.blocks:
            assert _EXTRACTOR._running_header_name(b.text) is None, (
                f"{stem}: running header leaked into body: {b.text[:60]!r}"
            )


@pytest.mark.parametrize("stem", _stems())
def test_not_over_blockquoted(stem):
    """The narrow single-spaced column must read as paragraphs; blockquotes are
    the exception, not the rule (they were ~70% of blocks before the retune)."""
    doc = _extract(stem)
    p = sum(b.kind == "p" for op in doc.opinions for b in op.blocks)
    bq = sum(b.kind == "blockquote" for op in doc.opinions for b in op.blocks)
    if p + bq < 10:
        pytest.skip("too few body blocks to judge")
    assert bq <= p, f"{stem}: {bq} blockquote vs {p} paragraph blocks"


@pytest.mark.parametrize("stem", _stems())
def test_audit_complete(stem):
    doc = _extract(stem)
    r = audit_coverage(doc, str(ASSETS / f"{stem}.pdf"), extractor=_EXTRACTOR)
    assert not r.missing, f"{stem}: {len(r.missing)} missing e.g. {r.missing[:3]}"
