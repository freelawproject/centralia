"""The public entry point's contract.

This is what a downstream consumer depends on, so it is pinned here: the keys
that exist, the shapes behind them, that the payload survives JSON, and that
a path, bytes and a file object are the SAME read. Most of it needs a real
document; the shape assertions that do not are kept corpus-free on purpose.
"""

from __future__ import annotations

import dataclasses as dc
import io
import json

import pytest

import centralia
from conftest import needs_corpus  # noqa: F401

TOP_KEYS = {"status", "court_id", "form", "versions", "cluster", "opinions",
            "headmatter", "endmatter", "sections", "removed", "diagnostics",
            "html", "review_html", "casebody", "warnings"}

# The two role-bearing blocks share a shape.
HM_KEYS = {"rows", "by_role", "html", "text", "untinted"}

CLUSTER_KEYS = {
    "court_id", "court", "case_name", "case_name_short", "citation",
    "docket_number", "other_dockets", "date_filed", "date_filed_iso",
    "date_argued", "date_argued_iso", "date_submitted", "date_submitted_iso",
    "date_reargued", "date_reargued_iso", "submitted_split",
    "precedential_status", "judges", "panel", "author", "attorneys",
    "syllabus", "summary", "headnotes",
    "parties", "cases", "caption", "disposition", "history", "lower_court",
    "lower_court_docket", "lower_court_judge", "title", "panel_line",
    "motion", "headmatter_style", "n_pages", "doc_type",
}

DIAG_KEYS = {
    "status", "rollout", "source_kind", "n_pages", "scan_pages", "text_missing_pages",
    "cid_pages", "residual", "residual_content", "removed_counts", "redactions",
    "opinion_count", "unbylined_opinions", "footnote_count",
    "headmatter_rows", "headmatter_untinted", "dates_unparsed", "warnings",
    "is_form",
}


def test_documented_names_are_importable():
    """The docstring used to promise `from centralia import extract` while the
    module exported nothing at all. It must never do that again."""
    for name in ("read", "extract", "render_html", "render_opinion",
                 "render_body", "render_casebody", "opinion_text",
                 "to_iso", "all_iso", "Document", "Criteria", "Meta",
                 "__version__"):
        assert hasattr(centralia, name), f"centralia.{name} is missing"
    assert set(centralia.__all__) <= set(dir(centralia))


def test_rejects_text_input():
    """A released court id, so the court check (which runs first) passes and
    the input-type check is the one under test."""
    from centralia.released import RELEASED
    court = sorted(RELEASED)[0]
    with pytest.raises(TypeError):
        centralia.read(io.StringIO("not a pdf"), court_id=court)


@needs_corpus
def test_returns_the_documented_keys(sample_pdf):
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    assert set(r) == TOP_KEYS
    assert set(r["cluster"]) == CLUSTER_KEYS
    assert set(r["diagnostics"]) == DIAG_KEYS
    assert r["status"] in ("valid", "review", "scanned", "failed")


@needs_corpus
def test_every_criteria_field_is_exposed(sample_pdf):
    """`cluster` must name EVERY field `Criteria` carries. Two — `panel_line`
    and `motion` — were dropped in silence until the user asked where the
    split-off pieces went; the whole headmatter block went the same way. A
    field added to the model and forgotten here is invisible to every
    consumer, so this fails rather than letting that happen again."""
    from centralia.model import Criteria
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    exposed = set(r["cluster"])
    # The few deliberate renamings, model name -> API name.
    renamed = {"decision_date": "date_filed",
               "short_case_name": "case_name_short",
               "publication_status": "precedential_status",
               "submitted": "date_submitted"}
    missing = [f.name for f in dc.fields(Criteria)
               if f.name not in exposed and renamed.get(f.name) not in exposed]
    assert not missing, f"Criteria fields absent from cluster: {missing}"


@needs_corpus
def test_headmatter_and_endmatter_are_role_bearing_blocks(sample_pdf):
    """Both are 'hm'-styled sections — rows carrying the role each was read
    as. Flattened to strings the roles are lost, and the roles are the product
    of a court port."""
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    for name in ("headmatter", "endmatter"):
        block = r[name]
        assert set(block) >= HM_KEYS, f"{name}: {sorted(block)}"
        for row in block["rows"]:
            assert set(row) == {"role", "text", "html", "page"}
            assert "<" not in row["text"], f"markup leaked into {name} text"
    assert "footnotes" in r["headmatter"]


@needs_corpus
def test_the_body_render_drops_no_section(sample_doc):
    """`render_body` skipped every 'hm'-styled section in silence, so the
    cover and the appearances vanished from the body HTML. It now raises on an
    unknown style instead of falling through."""
    from centralia.render import render_body, render_headmatter
    body = render_body(sample_doc)
    hm = render_headmatter(sample_doc)
    if hm.strip():
        assert hm in body, "the headmatter is missing from the body render"


@needs_corpus
def test_payload_survives_json(sample_pdf):
    """A consumer serializes this. Enums and dataclasses must already be
    plain, with no `default=` crutch."""
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    json.dumps(r)          # no default= on purpose


@needs_corpus
def test_payload_holds_no_enums_or_dataclasses(sample_pdf):
    """JSON-safety is NOT the same test. `DocType` is a StrEnum, so it
    serialises as a string while the value a caller receives is still an enum
    — `json.dumps` passed and the leak went unseen until the user printed a
    cluster and got `<DocType.ORDER: 'order'>`. Assert the TYPE."""
    import enum
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    bad: list[str] = []

    def walk(node, path):
        if isinstance(node, enum.Enum):
            bad.append(f"{path}: {node!r}")
        elif dc.is_dataclass(node) and not isinstance(node, type):
            bad.append(f"{path}: {type(node).__name__} dataclass")
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, (list, tuple)):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(r, "read()")
    assert not bad, "\n".join(bad)


@needs_corpus
def test_path_bytes_and_file_are_one_read(sample_pdf):
    court = sample_pdf.parent.name
    data = sample_pdf.read_bytes()
    a = centralia.read(sample_pdf, court_id=court)
    b = centralia.read(data, court_id=court)
    c = centralia.read(io.BytesIO(data), court_id=court)
    with open(sample_pdf, "rb") as fh:
        d = centralia.read(fh, court_id=court)
    for other in (b, c, d):
        assert other["html"] == a["html"]
        assert other["cluster"] == a["cluster"]
        assert other["status"] == a["status"]


@needs_corpus
def test_leaves_no_temp_file_behind(sample_pdf):
    import tempfile
    from pathlib import Path
    before = {p.name for p in Path(tempfile.gettempdir()).glob("centralia-*")}
    centralia.read(sample_pdf.read_bytes(), court_id=sample_pdf.parent.name)
    after = {p.name for p in Path(tempfile.gettempdir()).glob("centralia-*")}
    assert after <= before


@needs_corpus
def test_every_opinion_carries_its_own_content(sample_pdf):
    """The point of returning sub-opinions: each is addressable on its own."""
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    assert r["opinions"], "a valid opinion document with no writings"
    for op in r["opinions"]:
        assert set(op) >= {"order", "type", "author", "author_name", "pages",
                           "html", "text", "footnotes"}
        assert op["type"]
        assert op["html"].strip(), f"{op['type']} rendered empty"
        assert op["text"].strip(), f"{op['type']} has no text"


@needs_corpus
@pytest.mark.parametrize("court,stem,role,least", [
    ("nebctapp", "avery_v._whittle", "syllabus", 500),
    ("bia", "best", "summary", 80),
    ("orctapp", "city_of_eugene_v._hejazi", "summary", 30),
])
def test_precis_text_is_found_wherever_the_reader_put_it(court, stem, role,
                                                         least):
    """A syllabus emitted as headmatter ROWS and one emitted as flow BLOCKS
    must both reach `cluster` — a consumer cannot be asked to know which court
    does which."""
    from centralia.settings import CORPUS_ROOT
    pdf = CORPUS_ROOT / court / f"{stem}.pdf"
    if not pdf.is_file():
        pytest.skip(f"{court}/{stem} not in this corpus")
    c = centralia.read(pdf, court_id=court, allow_pending=True)["cluster"]
    assert c[role], f"{court}: {role} is empty"
    assert len(c[role]) >= least, f"{court}: {role} only {len(c[role])} chars"


@needs_corpus
def test_opinions_carry_their_document_order(sample_pdf):
    """A dissent means nothing without the opinion it dissents from, so the
    sequence the court filed them in has to survive the trip."""
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    orders = [op["order"] for op in r["opinions"]]
    assert orders == list(range(1, len(orders) + 1)), orders


@needs_corpus
def test_body_html_carries_no_review_furniture(sample_doc):
    """`html` is for ingesting, `review_html` is for reading. The review page's
    apparatus must not leak into the one a consumer stores."""
    body = centralia.render_body(sample_doc)
    review = centralia.render_html(sample_doc)
    for marker in ('class="hm-legend"', 'class="box residual"',
                   "untinted rows were not claimed"):
        assert marker not in body, f"{marker} leaked into the body render"
    assert len(review) > len(body)


@needs_corpus
def test_dates_are_reported_both_ways(sample_pdf):
    c = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)["cluster"]
    for printed, iso in (("date_filed", "date_filed_iso"),
                         ("date_argued", "date_argued_iso"),
                         ("date_submitted", "date_submitted_iso")):
        if c[printed]:
            assert c[iso] is None or len(c[iso]) == 10, c[iso]
        else:
            assert c[iso] is None


def test_released_set_is_generated_and_sane():
    """The gate's authority. Generated from the reviewer's marks by
    `harness.cli released --write`; a court is released only when every record
    was reviewed and none marked bad."""
    from centralia.released import HELD_BACK, RELEASED
    from centralia.courts import PROFILES
    assert RELEASED, "no courts released"
    assert not (RELEASED & set(HELD_BACK)), "a court cannot be both"
    unknown = (RELEASED | set(HELD_BACK)) - set(PROFILES)
    assert not unknown, f"released/held ids with no profile: {sorted(unknown)}"
    for court, (n, seen, bad) in HELD_BACK.items():
        assert bad or seen < n, f"{court} is held back for no stated reason"


def test_an_unknown_court_id_raises():
    """It would otherwise get core's generic reader and come back `valid` but
    thin — the 'ala' for 'alacivapp' trap."""
    with pytest.raises(centralia.UnknownCourt):
        centralia.read(b"%PDF-1.4", court_id="nosuchcourt")


def test_a_held_back_court_raises_but_can_be_overridden(sample_pdf):
    from centralia.released import HELD_BACK
    if not HELD_BACK:
        pytest.skip("every court is released")
    held = sorted(HELD_BACK)[0]
    with pytest.raises(centralia.CourtNotReleased):
        centralia.read(sample_pdf, court_id=held)
    r = centralia.read(sample_pdf, court_id=held, allow_pending=True)
    assert r["diagnostics"]["rollout"] == "pending"


@needs_corpus
def test_a_released_court_reports_itself_released(sample_pdf):
    r = centralia.read(sample_pdf, court_id=sample_pdf.parent.name)
    assert r["diagnostics"]["rollout"] in ("released", "pending")
