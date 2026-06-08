"""Golden expectations for representative documents, one per court / doc shape.

As we confirm how each court's document *types* should parse (full opinion,
per curiam, order, no-opinion decision, multi-opinion with concurrence /
dissent, ...), we add a verified case here. Each case pins the doc_type and the
(opinion type, author surname-prefix) of every opinion, so a parsing
regression shows up immediately.

Author is matched on the text before the first comma (the name), since the
stored author also carries the title/kind (e.g. 'RHONDA K. WOOD, Justice,
concurring.').
"""

import pytest

# (court, filename, expected doc_type, [(opinion_type, author_name), ...])
CASES = [
    # Arkansas — full opinion with a concurrence and a dissent (3 authored).
    (
        "ark",
        "state_of_arkansas_v._luis_ramirez_1.pdf",
        "opinion",
        [
            ("majority", "NICHOLAS J. BRONNI"),
            ("concurrence", "RHONDA K. WOOD"),
            ("dissent", "KAREN R. BAKER"),
        ],
    ),
    # Federal circuits — period byline form.
    (
        "ca1",
        "american_federation_of_govt_employees_local_2305_v._united_states.pdf",
        "opinion",
        [("majority", "BARRON")],
    ),
    # Per curiam.
    (
        "ca1",
        "arocho-rodriguez_v._roldan-concepcion.pdf",
        "opinion",
        [("majority", "PER CURIAM.")],
    ),
    # Colon byline form + mixed-case name.
    (
        "ca5",
        "alexander_v._arceneaux.pdf",
        "opinion",
        [("majority", "Edith Brown Clement")],
    ),
    # Colon byline form, all-caps name.
    (
        "cadc",
        "alon_refining_krotz_springs_inc._v._epa.pdf",
        "opinion",
        [("majority", "PAN")],
    ),
    # --- State supreme courts ---
    # New Mexico — pleading-paper line numbers dropped; 'WE CONCUR:' signature
    # roster folded out (would otherwise add 4 phantom opinions).
    (
        "nm",
        "city_of_las_cruces_v._n.m._pub._regul._commn.pdf",
        "opinion",
        [("majority", "THOMSON")],
    ),
    # Montana — reversed prose byline ('Justice X delivered the Opinion ...').
    (
        "mont",
        "bmk_enterprises_v._bailey.pdf",
        "opinion",
        [("majority", "Justice Beth Baker delivered the Opinion of the Court.")],
    ),
    # Missouri — trial judge ('The Honorable ..., Judge') excluded; the real
    # author is a 'Judge' of this court.
    (
        "mo",
        "cedric_dewayne_mack_appellant_vs._state_of_missouri_respondent..pdf",
        "opinion",
        [("majority", "Ginger K. Gooch")],
    ),
    # North Carolina — standard bold all-caps byline.
    (
        "nc",
        "bradley_home_v._n.c._dept_of_health__hum._servs..pdf",
        "opinion",
        [("majority", "DIETZ")],
    ),
    # Minnesota — majority + a separately-authored concurrence.
    (
        "minn",
        "cindy_ludwig_v._dakota_county_self-insured_by_sfm_risk_solutions_relator.pdf",
        "opinion",
        [("majority", "HENNESY"), ("concurrence", "MCKEIG")],
    ),
    # Iowa — title-case byline.
    (
        "iowa",
        "kevin_koeller_v._cardinal_logistics_management_corporation_and_ace_american.pdf",
        "opinion",
        [("majority", "Mansfield")],
    ),
    # Louisiana — legal-size page (margin raised); abbreviated-title byline in a
    # subset bold font ('WEIMER, Chief Justice*'); the GUIDRY dissent is signed
    # in-body with its disposition clause.
    (
        "la",
        "consolidated_with_2025-c-00868_beverly_alexander_rise_st._james_inclusive.pdf",
        "opinion",
        [("majority", "WEIMER"), ("dissent", "GUIDRY")],
    ),
    # Wyoming — trial judge from 'Appeal from ...' excluded.
    (
        "wyo",
        "andrew_atkinson_v._the_state_of_wyoming.pdf",
        "opinion",
        [("majority", "FENN")],
    ),
    # Massachusetts — inline abbreviated byline; publication NOTICE dropped,
    # reporter topic-headnotes routed to syllabus.
    (
        "mass",
        "banevicius_v._barnstable.pdf",
        "opinion",
        [("majority", "GAZIANO")],
    ),
    # Massachusetts single-justice order — no byline, body after the headnotes.
    (
        "mass",
        "smith_v._commonwealth.pdf",
        "opinion",
        [("majority", "PER CURIAM")],
    ),
    # Hawaiʻi ICA — author from the 'OPINION OF THE COURT BY <NAME>' heading, not
    # a counsel/trial-judge line (the bug the restricted author search fixes).
    (
        "hawapp",
        "deutsche_bank_national_trust_company_v._mendonza.pdf",
        "opinion",
        [("majority", "OPINION OF THE COURT BY HIRAOKA")],
    ),
    # Virginia COA — author announced as '[PUBLISHED ]OPINION BY / JUDGE NAME'
    # after the caption; ALL-CAPS 'JUDGE' distinguishes it from the panel/trial.
    ("vactapp", "daquan_hinton_v._commonwealth_of_virginia.pdf", "opinion",
     [("majority", "JUDGE RANDOLPH A. BEALES")]),
    # Kentucky COA — inline 'NAME, JUDGE:' colon byline after the BEFORE: panel.
    ("kyctapp",
     "723_vape_inc._v._allyson_taylor_in_her_official_capacity_as_commissioner.pdf",
     "opinion", [("majority", "MCNEILL")]),
    # Oregon — abbreviated-title byline; disposition summary + opinion merged.
    ("or", "state_v._miller.pdf", "opinion", [("majority", "BUSHONG")]),
    # Missouri — author signed at the end as ALL-CAPS 'NAME, JUDGE' (case-
    # insensitive title); Court of Appeals end-signature via signature fallback.
    ("mo",
     "catharine_sue_carter_as_personal_representative_of_the_estate_of_david.pdf",
     "opinion", [("majority", "KELLY C. BRONIEC")]),
    ("moctapp",
     "daniel_brothers_appellant_v._edward_james_becker_respondent..pdf",
     "opinion", [("majority", "JAMES M. DOWD")]),
    # Nebraska — Advance Sheets reporter format: running header dropped, numbered
    # syllabus routed to the syllabus field, title-case abbreviated byline.
    ("neb", "hastreiter_v._foltz_bros..pdf", "opinion", [("majority", "Papik")]),
    # Nebraska Court of Appeals — same reporter format, spelled-out Judge title.
    ("nebctapp", "dunham_v._dunham.pdf", "opinion", [("majority", "Bishop")]),
    # Michigan Court of Appeals — author restricted to the 'Before:' panel, so a
    # parenthetical SCOTUS citation ('(ALITO, J., concurring)') is not a byline.
    (
        "michctapp",
        "general_motors_llc_v._alphons_iacobelli.pdf",
        "opinion",
        [("majority", "MURRAY")],
    ),
    # North Dakota — bold Title-Case name-first byline on the second page; the
    # trial judge ('Honorable ..., Judge.') in the appeal-from block is excluded;
    # [¶N]-numbered body.
    (
        "nd",
        "state_v._romanyshyn.pdf",
        "opinion",
        [("majority", "Bahr")],
    ),
    # West Virginia — bold all-caps colon byline.
    (
        "wva",
        "danny_j._dobbins_and_jackie_l._dobbins_v._west_virginia_national_auto.pdf",
        "opinion",
        # Reversed-justice verb byline; the author string is the full announcement
        # phrase, as for tex/nj (see ReversedJusticeSupreme).
        [("majority", "JUSTICE TRUMP delivered the Opinion of the Court.")],
    ),
    # WV clerk's disposition — bold centered 'DISMISSAL ORDER' header, no byline,
    # red-ruled page → per curiam.
    (
        "wva",
        "raze_international_inc._v._wheeling_hospital_inc._city_of_wheeling_and.pdf",
        "opinion",
        [("majority", "PER CURIAM")],
    ),
    # Oregon — narrow reporter page; per curiam dispositions.
    (
        "or",
        "in_re_ashton.pdf",
        "opinion",
        # Oregon signs the disposition summary and the opinion separately; the
        # same-author pair is merged into one writing.
        [("majority", "PER CURIAM")],
    ),
    # WV Intermediate Court — signed opinion, reversed byline with the JUDGE
    # title (shares WestVirginiaStyle + the reversed-title base with the SJC).
    (
        "wvactapp",
        "chandra_t._v._robert_m..pdf",
        "opinion",
        [("majority", "CHIEF JUDGE GREEAR delivered the Opinion of the Court.")],
    ),
    # WV Intermediate Court — per-curiam 'MEMORANDUM DECISION' (Rule 21), no
    # byline, bold centered header opens the body.
    (
        "wvactapp",
        "brandon_carter_v._seven_rivers_design_build_llc.pdf",
        "opinion",
        [("majority", "PER CURIAM")],
    ),
    # Puerto Rico Court of Appeals — Spanish 'NAME, Juez[a] Ponente' byline;
    # legal-size pages, single-spaced block quotes kept in the body.
    (
        "prapp",
        "andr-s_antonio_torres_matos_y_otros_v._geovannie_morales_cintr-n.pdf",
        "opinion",
        [("majority", "Cintrón Cintrón")],
    ),
    # Puerto Rico — no ponente (pro-se 'por derecho propio' review) -> per curiam
    # panel decision opening at the centered 'SENTENCIA' header.
    (
        "prapp",
        "omar_osvaldo_ruiz_figueroa_v._departamento_de_correcci-n_y_rehabilitaci-n.pdf",
        "opinion",
        [("majority", "PER CURIAM")],
    ),
    # --- Abbreviated-title state supreme courts ('NAME, J.') ---
    # Massachusetts — inline byline, not bold.
    ("mass", "banevicius_v._barnstable.pdf", "opinion", [("majority", "GAZIANO")]),
    # Massachusetts Appeals Court — shares the SJC slip front matter (NOTICE
    # dropped, reporter headnotes -> syllabus) via MassachusettsStyle; 'Judge'
    # title byline + a concurrence.
    ("massappct", "commonwealth_v._milan.pdf", "opinion", [("majority", "MEADE")]),
    (
        "massappct",
        "lester_v._old_republic_title_insurance_company.pdf",
        "opinion",
        [("majority", "D'ANGELO"), ("concurrence", "WOOD")],
    ),
    # Ohio — bold byline; non-bold authorship summary excluded.
    ("ohio", "in_re_p.m.s..pdf", "opinion", [("majority", "BRUNNER")]),
    # Michigan — non-bold standalone byline after 'BEFORE THE ENTIRE BENCH';
    # the caption-box bottom rule no longer chops the byline + body.
    ("mich", "carlonda_naishe_swoope_v._citizens_insurance_co_of_the_midwest.pdf",
     "opinion", [("majority", "BOLDEN")]),
    # Michigan — majority + a (concurring) opinion; COA panel roster excluded.
    (
        "mich",
        "in_re_barberespinoza_minors.pdf",
        "opinion",
        [("majority", "CAVANAGH"), ("concurrence", "BOLDEN")],
    ),
    # Michigan — majority + three separate writings (a 'per curiam opinion'
    # prose line in the syllabus is not mistaken for a per-curiam byline).
    (
        "mich",
        "people_of_michigan_v._michael_georgie_carson.pdf",
        "opinion",
        [
            ("majority", "CAVANAGH"),
            ("concurrence-in-result", "ZAHRA"),
            ("concurrence-in-result", "BERNSTEIN"),
            ("concurring-in-part-and-dissenting-in-part", "BOLDEN"),
        ],
    ),
    # Michigan clerk's order — no byline, opens 'On order of the Court' → per
    # curiam; doc_type stays 'order'.
    (
        "mich",
        "placeholder_case_name.pdf",
        "order",
        [("majority", "PER CURIAM")],
    ),
    # Washington — em-dash inline byline, accented surnames.
    ("wash", "in_re_recall_of_hobbs.pdf", "opinion", [("majority", "MUNGIA")]),
    # --- Reversed-title state supreme courts ('JUSTICE NAME <verb>') ---
    # New Jersey — 'delivered the opinion'; the syllabus 'writing for ...'
    # heading is treated as headmatter, not a duplicate opinion.
    (
        "nj",
        "a-47-24_state_v._gerald_w._butler.pdf",
        "opinion",
        [("majority", "JUSTICE NORIEGA delivered the opinion of the Court.")],
    ),
    # Texas — 'delivered the opinion of the Court.'.
    (
        "tex",
        "angela_kate_whittenburg_wang_v._john_burkhart_whittenburg.pdf",
        "opinion",
        [("majority", "JUSTICE BUSBY delivered the opinion of the Court.")],
    ),
    # Pennsylvania — 'JUSTICE NAME DECIDED: <date>'.
    (
        "pa",
        "commonwealth_v._foster_j._aplt..pdf",
        "opinion",
        [("majority", "JUSTICE DOUGHERTY DECIDED: MAY 19")],
    ),
    # --- Wave 2 state supreme courts ---
    # Connecticut — abbreviated-title inline byline; a 'Mc' surname (exercises
    # the Mc/Mac byline-name rule).
    ("conn", "state_v._baez.pdf", "opinion", [("majority", "McDONALD")]),
    # Maine — standalone abbreviated-title byline.
    (
        "me",
        "amelia_johnson_v._michael_osseyran.pdf",
        "opinion",
        [("majority", "LIPEZ")],
    ),
    # New Hampshire — standalone byline below an underlined counsel block
    # (exercises the footnote-separator underline exclusion).
    (
        "nh",
        "appeal_of_pittsfield_sch._dist..pdf",
        "opinion",
        [("majority", "MACDONALD")],
    ),
    # Kansas — colon byline inline; a 'STEGALL, J., joins the foregoing ...'
    # joinder is NOT a separate opinion (single majority). SYLLABUS BY THE COURT
    # is lifted into the syllabus field.
    ("kan", "savage_v._timsah.pdf", "opinion", [("majority", "WALSH")]),
    # Kansas — an order: no byline, so the body opens at the centered all-caps
    # title ('ORDER'), authored per curiam; doc_type = order.
    ("kan", "in_re_janoski.pdf", "order", [("majority", "PER CURIAM")]),
    # Kansas Court of Appeals — same front matter (SYLLABUS BY THE COURT ->
    # syllabus); indented 'NAME, J.:' byline.
    ("kanctapp", "creative_planning_v._greco.pdf", "opinion", [("majority", "HURST")]),
    # South Carolina — reversed-title colon byline, bold.
    (
        "sc",
        "alexis_jones_v._progressive_northern_insurance_company.pdf",
        "opinion",
        [("majority", "JUSTICE JAMES:")],
    ),
    # Utah — reversed-title body byline 'JUSTICE NAME, opinion of the Court:';
    # the title-page 'authored ...' summary is left as headmatter (no
    # double-count).
    ("utah", "deer_valley_v._olson.pdf", "opinion", [("majority", "JUSTICE PETERSEN")]),
    # Utah Court of Appeals — same shape: the 'JUDGE X authored ... in which ...'
    # summary stays headmatter; the colon byline 'NAME, Judge:' starts the body.
    ("utahctapp", "hasemeyer_v._lefevre.pdf", "opinion", [("majority", "TENNEY")]),
    # utahctapp — a separate writing the old parser swallowed: majority + a
    # 'NAME, Judge (concurring ...)' concurrence now split out.
    (
        "utahctapp",
        "state_v._shay.pdf",
        "opinion",
        [("majority", "CHRISTIANSEN FORSTER"), ("concurrence", "HARRIS")],
    ),
    # Kentucky — 'OPINION OF THE COURT BY JUSTICE <NAME>' heading byline.
    (
        "ky",
        "commonwealth_of_kentucky_v._russell_t._amboree.pdf",
        "opinion",
        # Lead opinion + an in-body separate writing ('NICKELL, J., DISSENTING:').
        [("majority", "OPINION OF THE COURT BY JUSTICE CONLEY"), ("dissent", "NICKELL")],
    ),
    # Tennessee — prose authorship byline 'NAME, J., delivered the opinion ...'
    # with a kerned small-caps name (exercises plain-text byline parsing).
    (
        "tenn",
        "berkeley_research_group_llc_v._southern_advanced_materials_llc.pdf",
        "opinion",
        [("majority", "DWIGHT E. TARWATER")],
    ),
    # Nevada — 'By the Court, NAME, J.:'; the tag is kept in the byline text.
    (
        "nev",
        "carter_tyler_v._state_criminal.pdf",
        "opinion",
        [("majority", "By the Court")],
    ),
    # Rhode Island — reversed-title prose byline with a two-word surname.
    (
        "ri",
        "el_bebe_day_care_center_inc._v._rhode_island_department_of_elementary_and.pdf",
        "opinion",
        [("majority", "Justice Lynch Prata")],
    ),
    # Mississippi — name-first 'NAME, JUSTICE, FOR THE COURT:' + a separately
    # authored 'concurring in part and dissenting in part' writing.
    (
        "miss",
        "brooke_shantelle_denison_v._mississippi_organ_recovery_agency_inc..pdf",
        "opinion",
        [
            ("majority", "SULLIVAN"),
            ("concurring-in-part-and-dissenting-in-part", "GRIFFIS"),
        ],
    ),
    # Mississippi Court of Appeals — same 'NAME, J., FOR THE COURT:' family with
    # Judge titles; a compound surname ('LASSITTER, ST. PÉ, J.') is rejoined.
    (
        "missctapp",
        "frederick_d._small_aka_frederick_small_v._mississippi_department_of.pdf",
        "opinion",
        [("majority", "LASSITTER")],
    ),
    # missctapp — majority + a separately authored dissent.
    (
        "missctapp",
        "jack_rehm_v._robinson_property_group_llc_dba_horseshoe_tunica_and_the.pdf",
        "opinion",
        [("majority", "CARLTON"), ("dissent", "WESTBROOKS")],
    ),
    # Texas Court of Criminal Appeals — announcement byline 'NAME, J., delivered
    # the opinion of the Court ...'; one opinion per PDF (later announcements name
    # separately-filed writings).
    (
        "texcrimapp",
        "young_martin_v._the_state_of_texas.pdf",
        "opinion",
        [("majority", "PARKER")],
    ),
    # texcrimapp — a separately-filed dissent ('Schenck, P.J., filed a dissenting
    # opinion ...'), title-case surname; caption-divider footnote fix exposes it.
    (
        "texcrimapp",
        "barber_grady_jack_v._the_state_of_texas.pdf",
        "opinion",
        [("dissent", "Schenck")],
    ),
    # texcrimapp — 'Per curiam.' (capitalized, not all-caps).
    (
        "texcrimapp",
        "pearson_kameron.pdf",
        "opinion",
        [("majority", "PER CURIAM")],
    ),
    # DC Court of Appeals — name-first 'NAME, Associate/Senior Judge:' colon
    # byline + a dissent (confirmed by the 'Dissenting opinion by ...'
    # announcement).
    (
        "dc",
        "district_of_columbia_metropolitan_police_dept_v._district_of_columbia.pdf",
        "opinion",
        [("majority", "THOMPSON"), ("dissent", "BECKWITH")],
    ),
    # --- Wave 3 state supreme courts ---
    # Vermont — paragraph-numbered byline '¶ N. NAME, J.' (majority + a
    # separately authored, separately numbered dissent).
    (
        "vt",
        "state_v._kent_eaton.pdf",
        "opinion",
        [("majority", "¶ 1. WAPLES"), ("dissent", "¶ 30. COHEN")],
    ),
    # Wisconsin — '¶1 NAME, J.' majority keyed to the paragraph marker + a
    # self-contained 'NAME, J., dissenting.' separate writing; the per-page
    # 'JUSTICE X, dissenting' running header is NOT a phantom opinion.
    (
        "wis",
        "heather_gudex_v._franklin_collection_service_inc._1.pdf",
        "opinion",
        [("majority", "¶1 BRIAN K. HAGEDORN"), ("dissent", "SUSAN M. CRAWFORD")],
    ),
    # Maryland — caption byline 'Opinion by NAME, C.J.'; a bare 'Fader, C.J.'
    # coram listing is NOT an opinion start.
    (
        "md",
        "engage_armament_v._montgomery_cnty..pdf",
        "opinion",
        [("majority", "Opinion by Fader")],
    ),
    # Nebraska — advance-sheet authoring judge 'NAME, J.' (title-case) after
    # the panel roster; majority + dissent.
    (
        "neb",
        "american_exch._bank_v._topp.pdf",
        "opinion",
        [("majority", "Bergevin"), ("dissent", "Papik")],
    ),
    # Virginia — caption-embedded author on the record-number row; the
    # 'v. Record No.' lead is kept as body, author is the 'JUSTICE NAME' tail.
    (
        "va",
        "blow_v._commonwealth.pdf",
        "opinion",
        [("majority", "JUSTICE JUNIUS P. FULTON")],
    ),
    # --- U.S. district courts (single ruling, author from the signature
    # block / opening byline; whole ruling is one opinion) ---
    # N.D. Illinois — signature block 'Honorable Edmond E. Chang / U.S.D.J.'.
    (
        "ilnd",
        "gov.uscourts.ilnd.425533.111.0.pdf",
        "opinion",
        [("majority", "Honorable Edmond E. Chang")],
    ),
    # S.D.N.Y. — all-caps signature 'ANDREW E. KRAUSE / U.S. Magistrate Judge'.
    (
        "nysd",
        "gov.uscourts.nysd.477585.89.0.pdf",
        "opinion",
        [("majority", "ANDREW E. KRAUSE")],
    ),
    # E.D. Pa. — opening byline 'Rufe, J.' (no signature block).
    ("paed", "gov.uscourts.paed.596645.31.0.pdf", "opinion", [("majority", "Rufe")]),
    # N.D. Ga. — signature 'THOMAS W. THRASH, JR. / United States District Judge'.
    (
        "gand",
        "gov.uscourts.gand.313856.131.0.pdf",
        "opinion",
        [("majority", "THOMAS W. THRASH")],
    ),
]


@pytest.mark.parametrize(
    "court,filename,doc_type,opinions",
    CASES,
    ids=[f"{c}:{f}" for c, f, _dt, _ops in CASES],
)
def test_document(extract, court, filename, doc_type, opinions):
    doc = extract(court, filename)
    assert doc.doc_type == doc_type
    got = [(op.type, op.author.split(",")[0].strip()) for op in doc.opinions]
    assert got == opinions
