"""Invariants, and a pin for every fix made on 2026-08-21.

The guard's signatures catch structural drift. These catch the SPECIFIC things
that were wrong and are now right — each one names the record it came from, so
a failure says which reading regressed rather than which number moved.
"""

from __future__ import annotations

import pytest

from conftest import needs_corpus  # noqa: F401

pytestmark = needs_corpus


def _read(court, stem):
    import centralia
    from centralia.settings import CORPUS_ROOT
    pdf = CORPUS_ROOT / court / f"{stem}.pdf"
    if not pdf.is_file():
        pytest.skip(f"{court}/{stem} not in this corpus")
    return centralia.read(pdf, court_id=court)


# --------------------------------------------------------------------------
# invariants that hold for every record
# --------------------------------------------------------------------------

SAMPLE = [
    ("nmariana", "in_re_commonwealth"), ("neb", "state_v._kellogg"),
    ("pacommwct", "passhe_v._plrb"), ("bia", "best"),
    ("nysurct", "matter_of_levine_calleo"), ("orctapp", "city_of_eugene_v._hejazi"),
    ("wvactapp", "gabriel_b._v._thomas_c._and_west_virginia_department_of_human_services"),
    ("njtaxct", "one_main_st_edgewater_llc_co_natl_re_v._edgewater_borough"),
    ("mont", "transparent_election_initiative_v._knudsen"),
    ("nebctapp", "avery_v._whittle"),
]


@pytest.mark.parametrize("court,stem", SAMPLE)
def test_no_content_goes_unplaced(court, stem):
    """Text on the page must reach SOMETHING — a section, a writing, or the
    Removed box. Residual content means words vanished, which is the one
    defect that cannot be seen by reading the output."""
    d = _read(court, stem)["diagnostics"]
    assert d["residual_content"] == 0, d["residual"][:3]


@pytest.mark.parametrize("court,stem", SAMPLE)
def test_a_writing_never_opens_on_its_own_heading(court, stem):
    """'MEMORANDUM OPINION', 'OPINION BY …', 'FILED: …' and a caption row are
    headmatter. A writing that opens on one has swallowed the cover."""
    import re
    bad = re.compile(r"^(MEMORANDUM\s+OPINION|OPINION\s+BY|OPINION\s*\d*\s+BY"
                     r"|FILED\s*:|CONCURRING|DISSENTING|Table of Contents"
                     r"|IN THE\b|SUPERIOR COURT\b)", re.I)
    for op in _read(court, stem)["opinions"]:
        head = " ".join(op["text"].split())[:60]
        assert not bad.match(head), f"[{op['type']}] opens on {head!r}"


@pytest.mark.parametrize("court,stem", SAMPLE)
def test_every_writing_has_content(court, stem):
    """A bodyless writing is a phantom — a byline-shaped row read as a paper."""
    for op in _read(court, stem)["opinions"]:
        assert op["text"].strip(), f"[{op['type']}] has no text at all"


# --------------------------------------------------------------------------
# the specific readings fixed on 2026-08-21
# --------------------------------------------------------------------------

def test_acca_redactions_become_glyphs():
    """A blacked-out name is drawn, not written; 31 boxes on this record."""
    r = _read("acca", "united_states_v._sergeant_tyler_a._kindschi")
    bars = sum(t.count("█") for op in r["opinions"] for t in [op["text"]])
    assert bars >= 60, f"only {bars} block glyphs; the boxes went unread"
    assert "SPC █" in " ".join(op["text"] for op in r["opinions"])


def test_nevapp_ocr_scan_is_flagged():
    """A 200dpi raster with a clean OCR layer is still a scan, and must say so
    or a consumer ingests the scanner's guesses as the court's words."""
    r = _read("nevapp", "ccmsi_v._odell")
    assert r["diagnostics"]["source_kind"] == "ocr-scan"
    assert r["status"] == "scanned"
    assert len(r["diagnostics"]["scan_pages"]) == r["diagnostics"]["n_pages"]


def test_texbizct_scan_is_flagged_despite_arialmt():
    """The font alias that hid three scans from the OCR test."""
    r = _read("texbizct", "local_marketing_v._bennett")
    assert r["diagnostics"]["source_kind"] == "ocr-scan"


def test_texbizct_margin_paragraph_mark_ends_the_cover():
    """The OCR mangles '¶' differently every time, so the walk stops on the
    mark's POSITION. Unstopped it published the opinion's first paragraph as
    title rows and began the writing mid-sentence."""
    r = _read("texbizct", "local_marketing_v._bennett")
    titles = [h["text"] for h in r["headmatter"]["rows"] if h["role"] == "title"]
    assert titles, "no title claimed"
    assert all(len(t) < 90 for t in titles), f"body prose in title: {titles}"


def test_mont_origin_recital_is_claimed_whole():
    """'APPEALFROM:' welded, and 'ORIGINAL PROCEEDING:' — both open the origin
    ladder. Unmatched, the ladder below them became a phantom writing."""
    r = _read("mont", "matter_of_s.j.c._yinc")
    assert len(r["opinions"]) == 1, [o["type"] for o in r["opinions"]]
    roles = set(r["headmatter"]["by_role"])
    assert "lower-court" in roles


def test_mont_original_proceeding_keeps_its_counsel():
    """The whole counsel block went into the majority when the origin heading
    was unmatched."""
    r = _read("mont", "transparent_election_initiative_v._knudsen")
    counsel = [h["text"] for h in r["headmatter"]["rows"] if h["role"] == "counsel"]
    assert len(counsel) >= 10, f"only {len(counsel)} counsel rows claimed"
    assert r["opinions"][0]["text"].lstrip().startswith("¶1") or \
        "Petitioners Transparent" in r["opinions"][0]["text"][:120]


def test_nebctapp_claims_its_syllabus():
    """The reader dispatched on a running-head PAIR that core now collapses to
    one row; it returned NOTHING for all 37 records while grading fine."""
    r = _read("nebctapp", "avery_v._whittle")
    syl = [h for h in r["headmatter"]["rows"] if h["role"] == "syllabus"]
    assert len(syl) >= 20, f"only {len(syl)} syllabus rows"


def test_orctapp_disposition_is_a_summary_not_the_opinion():
    r = _read("orctapp", "city_of_eugene_v._hejazi")
    assert r["sections"].get("summary"), "no summary claimed"
    assert "reversed and remanded" in " ".join(r["sections"]["summary"]["text"]).lower()
    assert not r["opinions"][0]["text"].lstrip().lower().startswith(
        ("reversed", "affirmed", "vacated", "in case no"))


def test_bia_holding_precis_is_a_summary():
    """headnotes are a subject list; this is a précis, and the roles differ."""
    r = _read("bia", "best")
    roles = set(r["headmatter"]["by_role"])
    assert "summary" in roles
    assert "headnotes" not in roles


def test_njtaxct_reporter_stamp_is_removed_but_its_fact_kept():
    r = _read("njtaxct", "one_main_st_edgewater_llc_co_natl_re_v._edgewater_borough")
    stamps = [x["text"] for x in r["removed"] if x["kind"] == "stamp"]
    assert any("blication" in s for s in stamps), stamps[:4]
    assert r["cluster"]["precedential_status"] == "published"


def test_wvactapp_pivot_stays_in_the_caption():
    r = _read("wvactapp",
              "gabriel_b._v._thomas_c._and_west_virginia_department_of_human_services")
    cap = [h["text"] for h in r["headmatter"]["rows"] if h["role"] == "caption"]
    assert "v.)" in cap or "v." in cap, cap
    dockets = [h["text"] for h in r["headmatter"]["rows"] if h["role"] == "docket"]
    assert dockets, "no docket row claimed"
    assert not dockets[0].lower().startswith("v."), dockets[0]


def test_nmariana_a_court_inside_the_fence_is_a_party():
    """On an original-jurisdiction petition the respondent IS the trial court;
    the drawn fence is what says so."""
    r = _read("nmariana", "in_re_commonwealth")
    cap = " ".join(h["text"] for h in r["headmatter"]["rows"]
                   if h["role"] == "caption")
    assert "SUPERIOR COURT" in cap
    low = " ".join(h["text"] for h in r["headmatter"]["rows"]
                   if h["role"] == "lower-court")
    assert "SUPERIOR COURT OF THE COMMONWEALTH" not in low


def test_pacommwct_announced_author_names_the_opinion():
    """This court announces its author rather than signing, so the name lives
    in the headmatter — and must still reach the writing."""
    r = _read("pacommwct", "z._leger_v._g.l._martin")
    assert r["cluster"]["author"] == "PRESIDENT JUDGE COHN JUBELIRER"
    lead = r["opinions"][0]
    assert lead["author_name"] == "COHN JUBELIRER"
    assert lead["author_title"] == "President Judge"
    assert lead["text"].lstrip().startswith("Ziaire Leger")


def test_nysurct_leader_rows_stay_rows_and_keep_their_dots():
    """A leader list is prose with dots, not a table: one block per printed
    row, the dots as the page sets them, and the court's own sentence free."""
    r = _read("nysurct", "matter_of_levine_calleo")
    body = r["opinions"][0]["text"]
    assert "Petition ....." in body.replace("…", "")
    assert "<table" not in r["opinions"][0]["html"]
    assert "The following papers were read in determining petitioner" in body
    assert r["diagnostics"]["residual_content"] == 0


# --------------------------------------------------------------------------
# #41 — a court that never signs gets no signature block
# --------------------------------------------------------------------------

@pytest.mark.parametrize("stem", [
    # a separate writing opens on the last sheet: its 'Cite as:' running
    # head and its byline were repeated as a signature
    "e.m.d._sales_inc._v._carrera",
    # a footnote's first line names a judge
    "wooden_v._united_states",
    # a centred running-head pair: 'MCGIRT v. OKLAHOMA' / 'THOMAS, J., …'
    "mcgirt_v._oklahoma",
])
def test_scotus_writings_are_never_signed(stem):
    """Slip opinions are unsigned (`signatures=False`), so a signature block
    can only be a running head, byline, footnote line or figure read twice."""
    r = _read("scotus", stem)
    signed = [o["order"] for o in r["opinions"] if 'class="sig"' in o["html"]]
    assert not signed, f"signature block on writing(s) {signed}"


def test_scotus_closing_lines_stay_in_the_writing():
    """'It is so ordered.' is set right of the rail and 'JUSTICE SOTOMAYOR
    dissents.' names an office; the lift moved both out of the per curiam."""
    r = _read("scotus", "mays_v._hines")
    body = r["opinions"][0]["html"]
    assert 'class="sig"' not in body
    assert "It is so ordered." in body
    assert "JUSTICE SOTOMAYOR dissents." in body


def test_ca3_judgment_order_keeps_its_signature():
    """The default still signs: ca3 closes its judgment orders 'BY THE COURT,
    / s/ … / Circuit Judge', and that block must survive the scotus switch."""
    r = _read("ca3", "united_states_v._jerome_brown")
    last = r["opinions"][-1]["html"]
    assert 'class="sig"' in last
    assert "Restrepo" in last.split('class="sig"', 1)[1]


def test_scotus_syllabus_keeps_its_cover_page():
    """'Brief for Respondents 15' in the page-1 syllabus is a WEAK counsel mark;
    the backward merge took it as a counsel paragraph torn under the docket
    row, and the cover trim dropped the whole page as caption (#40)."""
    r = _read("scotus", "smith_v._spizzirri")
    assert r["cluster"]["syllabus"].startswith(
        "The Federal Arbitration Act (FAA) sets forth procedures")
    assert r["cluster"]["date_submitted"] == "April 22, 2024"
    assert not [d for d in r["removed"]
                if d["kind"] == "superfluous" and len(d["text"]) > 300]


# --------------------------------------------------------------------------
# #42: an order-style cover ('No. … Decided …') printed over a later writing
# --------------------------------------------------------------------------

def test_scotus_order_cover_is_removed_not_left_on_the_writing_above():
    """Wilson v. Hawaii prints a fresh cover over Justice Gorsuch's statement
    on page 8. It closes on 'No. 23–7517. Decided December 9, 2024', not on
    a bracketed date, and it used to end Justice Thomas's statement."""
    r = _read("scotus", "wilson_v._hawaii")
    thomas, gorsuch = r["opinions"][1], r["opinions"][2]

    assert " ".join(thomas["text"].split()).endswith("(opinion of THOMAS, J.).")
    assert gorsuch["text"].lstrip().startswith(
        "In December 2017, Christopher Wilson")
    assert any(d["kind"] == "cover" and "No. 23–7517" in d["text"]
               for d in r["removed"])


def test_scotus_syllabus_cover_survives_beside_an_order_cover():
    """Hewitt v. United States has both kinds of cover: the syllabus cover
    closes on 'Argued …—Decided …' and must stay (it is the only place the
    argued date is printed); the dissent's cover closes on 'Decided …' alone
    and must go."""
    r = _read("scotus", "hewitt_v._united_states")
    majority = r["opinions"][0]

    assert r["cluster"]["date_submitted"]
    assert r["cluster"]["syllabus"]
    assert "SUPREME COURT OF THE UNITED STATES" not in majority["text"][-500:]
