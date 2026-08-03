import pytest

from centralia.audit import _is_filing_stamp, audit_coverage
from centralia.ecosystem_audit import _headmatter_boundary_signals
from centralia.models import Block, DocType, ExtractedDocument, Opinion
from centralia.registry import get_extractor
from centralia.render.casebody import render_casebody
from centralia.render.html import render_html


@pytest.mark.parametrize(
    ("court", "filename"),
    [
        ("almd", "gov.uscourts.almd.83289.89.0.pdf"),
        ("cadc", "alon_refining_krotz_springs_inc._v._epa.pdf"),
        ("uscfc", "jeffers_v._secretary_of_health_and_human_services.pdf"),
        ("ca2", "cunha_v._freden.pdf"),
        ("or", "state_v._de_witt_simons.pdf"),
        ("wis", "state_v._k._r._c..pdf"),
        ("texcrimapp", "barber_grady_jack_v._the_state_of_texas.pdf"),
        ("texcrimapp", "cuevas_victor_hugo_v._the_state_of_texas.pdf"),
        ("texcrimapp", "lambert_jason_curtis_v._the_state_of_texas.pdf"),
        ("texcrimapp", "lewis_howard_wayne_v._the_state_of_texas.pdf"),
        ("texcrimapp", "mcdonald_amanda_v._the_state_of_texas.pdf"),
        ("texcrimapp", "montgomery_beecher_v._the_state_of_texas.pdf"),
        ("texcrimapp", "wenzel_michael_justice.pdf"),
        ("pacommwct", "the_salvation_army_v._wayne_county_commissioners.pdf"),
        ("wash", "a_better_richland_v._chilton.pdf"),
        ("ctd", "gov.uscourts.ctd.162105.43.0.pdf"),
        ("delch", "ashok_mayya_v._edward_lee.pdf"),
        ("idaho", "johnson_v._srm-double_l_llc.pdf"),
        ("idaho", "medical_recovery_services_llc_v._wood.pdf"),
        (
            "iowa",
            "melinda_williams_v._kenneth_j._hartman_m.d._and_davenport_surgical_group.pdf",
        ),
    ],
)
def test_repaired_content_is_fully_placed(extract, court, filename):
    doc = extract(court, filename)

    assert not [
        item
        for item in doc.residual
        if isinstance(item, dict) and item.get("kind") == "content"
    ]


def test_microscopic_word_field_code_is_not_rendered(extract):
    doc = extract("arwd", "gov.uscourts.arwd.74562.17.0.pdf")
    extractor = get_extractor("arwd")
    text = " ".join(block.text for op in doc.opinions for block in op.blocks)

    assert "0F<footnotemark>" not in text
    assert not audit_coverage(doc, doc.source_path, extractor=extractor).missing


def test_tenth_circuit_publication_banner_is_furniture():
    assert _is_filing_stamp("PUBLISH Tenth Circuit")


@pytest.mark.parametrize(
    ("court", "filename"),
    [
        ("cacd", "gov.uscourts.cacd.972521.25.0.pdf"),
        ("calctapp", "marriage_of_g.e.__i.d..pdf"),
        ("calctapp", "people_v._tyus.pdf"),
        ("md", "cutchember_v._state.pdf"),
        ("md", "mayor__city_cncl._of_balt._v._b.p._p.l.c..pdf"),
        ("nvd", "gov.uscourts.nvd.171970.12.0.pdf"),
        (
            "prapp",
            "consejo_de_titulares_del_condominio_villas_de_paseosol_v._"
            "luis_gilberto_cabrera_medina_carmelina_álvarez_giboyeaux_socie.pdf",
        ),
        (
            "prapp",
            "mwi_corporation_mwi_corporation_mwi_corporation_v._tetrad_"
            "enterprises_limited_liability_company_luis_hernández_rivera_al.pdf",
        ),
        ("tned", "gov.uscourts.tned.114244.32.0.pdf"),
        ("wawd", "gov.uscourts.wawd.356328.16.0.pdf"),
    ],
)
def test_final_source_line_repairs_are_audited(extract, court, filename):
    doc = extract(court, filename)
    extractor = get_extractor(court)

    assert not audit_coverage(
        doc, doc.source_path, extractor=extractor
    ).missing


def test_armfor_wrapped_roster_does_not_create_empty_opinion(extract):
    doc = extract("armfor", "united_states_v._ellis.pdf")
    extractor = get_extractor("armfor")

    assert [(op.type, op.author) for op in doc.opinions] == [
        ("majority", "Judge HARDY delivered the opinion of the Court."),
        ("concurrence", "Judge MAGGS, concurring in part and in the judgment."),
    ]
    assert all(op.blocks for op in doc.opinions)
    assert "Judge JOHNSON joined" in doc.summary[-1]["html"]
    assert not audit_coverage(
        doc, doc.source_path, extractor=extractor
    ).missing


@pytest.mark.parametrize(
    ("court", "filename", "expected_tables", "shape"),
    [
        ("delch", "in_re_swervepay_acquisition_llc.pdf", 1, (20, 4)),
        ("iowa", "donald_lee_wyldes_jr._v._state_of_iowa.pdf", 2, (4, 3)),
        (
            "njtaxct",
            "paula_forshee_v._city_of_east_orange_prospect_castle_llc_v._city_of_east.pdf",
            2,
            (6, 6),
        ),
        (
            "olc",
            "harmonizing_the_professional_responsibility_and_work_opportunity.pdf",
            1,
            (10, 4),
        ),
    ],
)
def test_repaired_tables_are_structured_and_complete(
    extract, court, filename, expected_tables, shape
):
    doc = extract(court, filename)
    tables = [
        block.payload.get("rows") or []
        for opinion in doc.opinions
        for block in opinion.blocks
        if block.kind == "table"
    ]

    assert len(tables) == expected_tables
    assert (len(tables[-1]), len(tables[-1][0])) == shape
    assert not [item for item in doc.residual if item.get("kind") == "content"]


def test_delaware_chancery_body_is_not_headmatter(extract):
    doc = extract("delch", "in_re_swervepay_acquisition_llc.pdf")

    assert len(doc.opinions) == 1
    assert doc.opinions[0].author == "McCORMICK, C."
    assert len(doc.opinions[0].blocks) > 250
    assert not _headmatter_boundary_signals(doc)


@pytest.mark.parametrize(
    ("court", "filename", "author_fragment"),
    [
        ("arizctapp", "david_stone_v._pima_county.pdf", "O’NEIL"),
        ("bap6", "in_re_haffey.pdf", "PRESTON"),
        ("kyctapp", "jessica_saner_v._commonwealth_of_kentucky_cabinet_for_health_and_family.pdf", "JONES"),
        ("la", "in_re_judge_donald_chick_foret_twenty-fourth_judicial_district_court.pdf", "Guidry"),
        ("mass", "commonwealth_v._phan.pdf", "PER CURIAM"),
        ("massappct", "in_the_matter_of_the_estate_of_jasiul.pdf", "BLAKE"),
        ("mdag", "108oag108.pdf", "Anthony G. Brown"),
        ("mdctspecapp", "carroll_v._state.pdf", "Eyler"),
        ("me", "in_re_catherine_r._connors.pdf", "DOW"),
        ("minn", "state_of_minnesota_v._jennifer_lynn_nagle.pdf", "McKEIG"),
        ("sc", "in_the_matter_of_the_care_and_treatment_of_andy_eugene_hyman.pdf", "KITTREDGE"),
        ("wyo", "the_state_of_wyoming_v._dixon_dean_cole.pdf", "COOLEY"),
        ("acca", "united_states_v._specialist_jaimin_p._prajapati.pdf", ""),
        ("afcca", "united_states_v._penninga.pdf", "RAMÍREZ"),
        ("bia", "lopez_rico.pdf", "RADICS"),
        ("idahoctapp", "tracy_allen_an_individual_v._james_allison_and_annette_allison_husband.pdf", "LORELLO"),
        ("me", "opinion_of_the_justices_ranked-choice_voting.pdf", "THE JUSTICES"),
        ("mo", "prosecuting_attorney_21st_judicial_circuit_ex_rel._marcellus_williams.pdf", "Fischer"),
        ("mont", "transparent_election_initiative_v._knudsen.pdf", "Shea"),
        ("ohioctapp", "in_re_s.w..pdf", "DINGUS"),
        ("prapp", "bosch_international_inc._v._junta_de_directores_su_presidente_marisol.pdf", "Robles Adorno"),
        ("tenncrimapp", "state_of_tennessee_v._johnny_mack_powell.pdf", "WEDEMEYER"),
        ("wva", "credit_acceptance_corporation_v._kenneth_e._stanley_and_kerry_j._stanley.pdf", "Wooton"),
    ],
)
def test_repaired_opinion_body_is_not_left_in_headmatter(
    extract, court, filename, author_fragment
):
    doc = extract(court, filename)

    assert doc.opinions
    assert any(opinion.blocks for opinion in doc.opinions)
    assert author_fragment in doc.opinions[0].author
    assert not _headmatter_boundary_signals(doc)


def test_misplaced_headmatter_detector_carries_review_evidence():
    rows = [
        {
            "__hm__": True,
            "html": "I. FACTUAL BACKGROUND" if index == 0 else (
                "This is ordinary opinion prose containing enough words to "
                "demonstrate a sustained misplaced body paragraph in headmatter."
            ),
            "rel": 1.0,
            "align": "L",
            "page": 2 + index // 5,
            "top": 100.0 + index * 14,
        }
        for index in range(25)
    ]
    doc = ExtractedDocument(doc_type=DocType.OPINION, summary=rows)

    signals = _headmatter_boundary_signals(doc)

    assert signals[0]["kind"] == "body-only-in-headmatter"
    assert signals[0]["page"] == 2
    assert signals[0]["row"] == 0
    assert signals[0]["geometry"]["top"] == 100.0


def test_normal_short_headmatter_does_not_signal():
    doc = ExtractedDocument(
        doc_type=DocType.OPINION,
        summary=[
            {"__hm__": True, "html": "SUPREME COURT", "rel": 1.2, "align": "C"},
            {"__hm__": True, "html": "Decided August 1, 2026", "rel": 1.0, "align": "C"},
        ],
        opinions=[Opinion("majority", "JUDGE", [Block("p", "The opinion body.")])],
    )

    assert not _headmatter_boundary_signals(doc)


def test_exact_byline_renders_without_duplicating_normalized_author():
    doc = ExtractedDocument(
        doc_type=DocType.OPINION,
        opinions=[
            Opinion(
                "majority",
                "VERNON D. OLIVER",
                [Block("p", "Opinion text.")],
                caption=[
                    Block(
                        "p",
                        "<strong>VERNON D. OLIVER</strong>, United States District Judge:",
                        payload={"role": "byline"},
                    )
                ],
            )
        ],
    )

    html = render_html(doc)
    casebody = render_casebody(doc)

    assert "United States District Judge:" in html
    assert '<div class="author">VERNON D. OLIVER</div>' not in html
    assert '<p role="byline">' in casebody
    assert "<author>VERNON D. OLIVER</author>" in casebody


def test_reconstructed_table_renders_cells():
    doc = ExtractedDocument(
        doc_type=DocType.OPINION,
        opinions=[
            Opinion(
                "majority",
                "COURT",
                [
                    Block(
                        "table",
                        payload={
                            "rows": [["Category", "Result"], ["Parolees", "Eligible"]],
                            "has_header": True,
                        },
                    )
                ],
            )
        ],
    )

    html = render_html(doc)

    assert "<th>Category</th>" in html
    assert "<td>Parolees</td>" in html
