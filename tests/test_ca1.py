"""CA1 (First Circuit) regression lock-in.

Pins the behaviors tuned while working ca1 so later changes can't silently
regress them:

  * Byline detection is the leading BOLD run + byline form — it finds the
    majority AND concurrence/dissent bylines, rejects the regular-weight panel
    roster ('Gelpí, Circuit Judge.') and bold dispositions ('So ordered.').
  * The headmatter runs through the centered date: a one-per-line panel judge
    is not mistaken for the author, and a counsel-underline rule is not
    mistaken for a footnote separator (which had spawned a phantom headmatter
    footnote and cut the caption short). A real page-1 caption footnote ('*')
    is still kept.
  * '- N -' page footers are dropped from body, blockquotes, and footnotes —
    not left inline ('… obtained . . .. - 8 -' / '… a federally - 4 -').
  * Every source line is accounted for (audit), with no real content stranded
    in residual.

Assets are gitignored, so each test skips cleanly when its PDF is absent; the
corpus-parametrized tests collect nothing when the ca1 corpus is missing.
"""

from pathlib import Path
import re

import pytest

from centralia import get_extractor
from centralia.audit import audit_coverage

COURT = "ca1"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / COURT

# A standalone '- N -' page footer (dash, 1-3 digits, dash). The digit guards
# keep it off citation ranges ('534-535') and years ('2020-2021').
_PAGENO = re.compile(r"(?<!\d)-\s?\d{1,3}\s?-(?!\d)")

_EXTRACTOR = get_extractor(COURT)
_CACHE: dict = {}


def _extract(stem: str):
    """Extract a ca1 PDF by stem (cached); skip if the asset is absent."""
    p = ASSETS / f"{stem}.pdf"
    if not p.exists():
        pytest.skip(f"missing asset: {p}")
    if stem not in _CACHE:
        _CACHE[stem] = _EXTRACTOR.extract(str(p))
    return _CACHE[stem]


def _ca1_stems():
    if not ASSETS.exists():
        return []
    return sorted(p.stem for p in ASSETS.glob("*.pdf"))


def _summary_text(doc) -> str:
    return " ".join(str(s) for s in doc.summary)


def _all_footnotes(doc):
    yield from doc.headmatter_footnotes
    for op in doc.opinions:
        yield from op.footnotes


# --------------------------------------------------------------------- bylines
@pytest.mark.parametrize(
    "stem,types,authors",
    [
        # multi-opinion: majority + a separate dissent/concurrence
        (
            "sec_v._sargent",
            ["majority", "concurring-in-part-and-dissenting-in-part"],
            ["KAYATTA", "BARRON"],
        ),
        (
            "cortes-ramos_v._martin-morales",
            ["majority", "dissent"],
            ["THOMPSON", "BARRON"],
        ),
        # single-opinion
        ("st._john_v._campbell", ["majority"], ["RIKELMAN"]),
        ("buckley_v._blanche", ["majority"], ["AFRAME"]),
        ("united_states_v._calderin-pascual", ["majority"], ["BARRON"]),
    ],
)
def test_opinion_bylines(stem, types, authors):
    doc = _extract(stem)
    assert [op.type for op in doc.opinions] == types, (
        f"{stem}: {[op.author for op in doc.opinions]}"
    )
    for op, name in zip(doc.opinions, authors):
        assert op.author.upper().startswith(name), f"{stem}: {op.author!r}"


def test_per_curiam_detected():
    """A court-authored 'PER CURIAM' start is still recognized."""
    doc = _extract("arocho-rodriguez_v._roldan-concepcion")
    assert doc.opinions
    assert doc.opinions[0].author.upper().startswith("PER CURIAM")


def test_calderin_headmatter_runs_through_date():
    """The one-per-line panel ('Gelpí, Circuit Judge.') must not be taken for
    the author (the real byline is BARRON on a later page); the headmatter then
    keeps the counsel block and the centered decision date."""
    doc = _extract("united_states_v._calderin-pascual")
    assert doc.opinions[0].author.upper().startswith("BARRON")
    summ = _summary_text(doc)
    assert "April 3, 2026" in summ          # runs through the date
    assert "George T. Pallas" in summ       # counsel block retained
    assert "Gelpí" in summ                   # panel judge stays in headmatter


# ----------------------------------------------------------------- headmatter
def test_st_john_no_phantom_footnote():
    """A counsel-name underline rule must not be read as a footnote separator
    (which had swept the counsel tail + date into a bogus headmatter footnote)."""
    doc = _extract("st._john_v._campbell")
    assert len(doc.headmatter_footnotes) == 0
    assert "April 29, 2026" in _summary_text(doc)


def test_buckley_keeps_caption_footnote():
    """A genuine page-1 caption footnote ('*' Rule 43(c) substitution) is kept
    as a headmatter footnote — the width-matched separator still registers."""
    doc = _extract("buckley_v._blanche")
    assert "*" in [fn.label for fn in doc.headmatter_footnotes]


@pytest.mark.parametrize(
    "stem", ["buckley_v._blanche", "st._john_v._campbell", "sec_v._sargent"]
)
def test_caption_banner_present(stem):
    """The 'United States Court of Appeals' banner is rendered in the styled
    headmatter, not absorbed into a metadata field."""
    assert "United States Court of Appeals" in _summary_text(_extract(stem))


# -------------------------------------------------------- page-number footers
@pytest.mark.parametrize("stem", _ca1_stems())
def test_no_page_footer_in_body(stem):
    doc = _extract(stem)
    for op in doc.opinions:
        for b in op.blocks:
            assert not _PAGENO.search(b.text), (
                f"{stem}: '- N -' footer leaked into body: {b.text[:90]!r}"
            )


@pytest.mark.parametrize("stem", _ca1_stems())
def test_no_page_footer_in_footnotes(stem):
    doc = _extract(stem)
    for fn in _all_footnotes(doc):
        for _tag, txt in fn.paragraphs:
            tail = txt.rstrip()
            assert not re.search(r"(?<!\d)-\s?\d{1,3}\s?-$", tail), (
                f"{stem}: footer leaked into footnote [{fn.label}]: {tail[-50:]!r}"
            )


# ---------------------------------------------------------------- completeness
@pytest.mark.parametrize("stem", _ca1_stems())
def test_audit_complete(stem):
    """Every source line is accounted for, and nothing real is stranded in the
    residual safety net (page-number furniture is fine)."""
    doc = _extract(stem)
    p = str(ASSETS / f"{stem}.pdf")
    r = audit_coverage(doc, p, extractor=_EXTRACTOR)
    assert not r.missing, f"{stem}: {len(r.missing)} missing e.g. {r.missing[:3]}"
    residual_content = [
        x for x in (doc.residual or []) if x.get("kind") != "furniture"
    ]
    assert not residual_content, f"{stem}: residual content {residual_content[:3]}"
