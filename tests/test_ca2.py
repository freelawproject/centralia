"""CA2 (Second Circuit) — document-style identification.

CA2 documents come in distinct styles, and each style dictates how it must be
extracted, so the first job is to identify the style reliably. Two independent
axes:

  * summary-order vs opinion — a summary order opens with the convening recital
    'At a stated term of the United States Court of Appeals …' under a centered
    'SUMMARY ORDER' heading and a 'PRESENT: <judges>' panel; an opinion carries
    a normal '<NAME>, Circuit Judge:' byline.
  * numbered paper or not — a left-margin sequential line-number gutter.

``document_style`` returns one of: opinion / opinion_numbered / summary_order /
summary_order_numbered. These tests pin the four exemplars (one per style) and
assert every corpus file resolves to a known style.

Assets are gitignored, so tests skip cleanly when a PDF is absent.
"""

from pathlib import Path

import pdfplumber
import pytest

from centralia import get_extractor

COURT = "ca2"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / COURT
_EXTRACTOR = get_extractor(COURT)
_STYLES = {"opinion", "opinion_numbered", "summary_order", "summary_order_numbered"}
_CACHE: dict = {}


def _style(stem: str) -> str:
    p = ASSETS / f"{stem}.pdf"
    if not p.exists():
        pytest.skip(f"missing asset: {p}")
    if stem not in _CACHE:
        with pdfplumber.open(str(p)) as pdf:
            _CACHE[stem] = _EXTRACTOR.document_style(pdf.pages[0])
    return _CACHE[stem]


_DOC_CACHE: dict = {}


def _doc(stem: str):
    p = ASSETS / f"{stem}.pdf"
    if not p.exists():
        pytest.skip(f"missing asset: {p}")
    if stem not in _DOC_CACHE:
        _DOC_CACHE[stem] = _EXTRACTOR.extract(str(p))
    return _DOC_CACHE[stem]


def _stems():
    if not ASSETS.exists():
        return []
    return sorted(p.stem for p in ASSETS.glob("*.pdf"))


def _summary_stems():
    out = []
    for stem in _stems():
        try:
            if _style(stem).startswith("summary_order"):
                out.append(stem)
        except Exception:
            pass
    return out


_OPENERS = (
    "appeal from",
    "appeals from",
    "cross-appeal from",
    "petition for review",
    "petitions for review",
    "on appeal from",
    "on petition for review",
    "following disposition",
    "upon due consideration",
    "on consideration",
)


@pytest.mark.parametrize(
    "stem,style",
    [
        # one exemplar per style
        ("adidas_america_inc._v._thom_browne_inc.", "opinion"),
        ("alsonidar_v._mullin", "summary_order"),
        ("alvarenga_vides_v._blanche", "summary_order_numbered"),
        ("campbell_v._broome_county", "opinion_numbered"),
    ],
)
def test_document_style(stem, style):
    assert _style(stem) == style


@pytest.mark.parametrize("stem", _stems())
def test_style_is_known(stem):
    """Every ca2 document resolves to one of the four recognized styles."""
    assert _style(stem) in _STYLES


# ------------------------------------------------------- summary-order extraction
# havlish is a consolidated multi-docket order whose operative opener doesn't
# land on a segment boundary — a known hard case, tracked separately.
_SUMMARY_HARD = {"havlish_v._taliban_aliganga_v._taliban"}


@pytest.mark.parametrize("stem", _summary_stems())
def test_summary_order_is_per_curiam_body(stem):
    """A summary order yields a single PER CURIAM opinion whose body opens with
    the order's operative language (not the headmatter recital/panel/counsel)."""
    if stem in _SUMMARY_HARD:
        pytest.xfail("consolidated order: opener not on a segment boundary")
    doc = _doc(stem)
    assert doc.opinions, f"{stem}: no opinion extracted"
    op = doc.opinions[0]
    assert op.author == "PER CURIAM", f"{stem}: author={op.author!r}"
    assert op.blocks, f"{stem}: no body blocks"
    first = op.blocks[0].text.lower().lstrip()
    # strip any leading inline tag (e.g. <strong>UPON DUE CONSIDERATION</strong>)
    while first.startswith("<"):
        first = first[first.find(">") + 1 :].lstrip()
    assert first.startswith(_OPENERS), f"{stem}: body opens {first[:40]!r}"


@pytest.mark.parametrize(
    "stem,opener",
    [
        ("alsonidar_v._mullin", "appeal from"),
        ("quito_v._blanche", "upon due consideration"),
        ("alvarenga_vides_v._blanche", "upon due consideration"),
    ],
)
def test_summary_order_body_opener(stem, opener):
    doc = _doc(stem)
    assert doc.opinions and doc.opinions[0].author == "PER CURIAM"
    first = doc.opinions[0].blocks[0].text.lower().lstrip()
    while first.startswith("<"):
        first = first[first.find(">") + 1 :].lstrip()
    assert first.startswith(opener), f"{stem}: {first[:40]!r}"
