"""Which documents the headmatter-criteria snapshot covers, and why.

One entry per FORMAT, not per file. Every stem below is a shape the court
actually prints and that cost real work to read correctly — the consolidated
records, the orders, the two-column captions, the courts that state their
origin once for a whole record. A court's ordinary format is represented too,
so a change that only breaks the common case cannot pass.

Stems are matched as prefixes against ``assets/<court>/``, so a file can be
renamed without breaking the manifest.
"""

MANIFEST = {
    "bap1": [
        # --- STYLE 'centred ladder': a cover sheet whose every zone the
        # First Circuit's panel clerk fences with a typed underscore rule on
        # the sheet's axis, and whose every row is centred on that axis. The
        # zones are read by POSITION; the only things read are FORMS (a
        # number, a date) and closed role vocabularies (party status, bench).
        # THE ORDINARY COVER, and the one-sided appeal: 'Appellant.' with no
        # pivot at all, so the record states a caption but no parties.
        "steven_carrigan_sr._v.",
        # NO ORIGIN ZONE (5 of 32): the roster follows the caption directly,
        # which is why the origin is what is LEFT and may be nothing.
        "ginger_sirikanjanachai_v._commonwealth_of_massachusetts",
        # CONSOLIDATED bankruptcy cases: two case numbers and four captions
        # under one BAP docket, one origin/roster/counsel/date below them —
        # and an EMPTY zone where the clerk types the closing fence at the
        # foot of page 1 and the opening one at the head of page 2.
        "banco_popular_de_puerto_rico_v._manuel_babilonia_santiago",
        # CONSOLIDATED THE OTHER WAY: two BAP dockets, each with its own
        # bankruptcy case and captions, plus an adversary proceeding number.
        "kittery_point_partners_llc_v._bayview_loan_servicing_llc",
        # THE CAPTION THAT FILLS THE SHEET — 26 appellee rows carry it over
        # the page break and only four fences are typed on page 1, which is
        # why the axis is measured over the whole cover, not page 1 alone.
        "charles_muszynski_v._roberto_roman_valentin",
        # A PARENTHETICAL ASIDE inside the docket zone ('(Consolidated)'),
        # and a roster that prints its opener inline with the names
        # ('Before Harwood, Cary, and Fagone,').
        "milk_industry_regulatory_v._rosa_dairy_farm",
        # A CHIEF JUDGE roster split over two rows and joined by a semicolon
        # ('Fagone, Chief …Judge;' / 'and Panos and Bacher, …Judges.'), with
        # a caption footnote printed BELOW the fence that closes the block.
        "ernesto_irizarry_santiago_v._firstbank_puerto_rico",
        # THE ORIGIN'S PARENTHETICAL CARRYING A FOOTNOTE MARK — '(Hon. Brian
        # K. Tester, U.S. Bankruptcy Judge)1' — so the parsed judge is read
        # off the unmarked row while the printed row keeps its mark.
        "jose_mendez_albarran_v._carmen_socorro_rivera",
        # THE BYLINE PRINTED IN THE FOOT OF THE COVER PAGE, under the closing
        # fence: the claim ends at that fence and never reaches the writing.
        "madge_casper_v._kimberley_osullivan",
        # The flag set at 15.5pt rather than 16, and party groups running to
        # five rows each with semicolons between them.
        "caroline_ortega_berrios_v._david_torres_reyes",
    ],
    "bap10": [
        # --- STYLE 'railed ladder': the Tenth Circuit's own stationery set
        # for a bankruptcy panel. A DRAWN vertical rule at x=310.9 brackets
        # the caption and splits its two columns; every zone below it is
        # FENCED on the page axis, and a zone is read by what stands in it.
        # THE ORDINARY UNPUBLISHED PAPER: typed fences, the panel's docket
        # over the bankruptcy court's numbers and the chapter, the origin
        # centred, 'Submitted on the briefs.' at the body rail, the roster.
        "douglas_gould_v._kt_weaver",
        # THE PUBLISHED SLIP: 'PUBLISH' over the banner, an UNLABELLED
        # appearance block between the origin and the roster — and a fence
        # the drawn rail cuts in two, which is only a fence when the whole
        # visual ROW is measured against the axis.
        "michael_roberts_sr._v._harvey_sender_chapter_7_trustee",
        # FENCES THE PAGE DRAWS (252pt rules on the axis) instead of typing,
        # mixed with a typed one over the caption.
        "glencove_holdings_llc_v._steven_bloom",
        # A 470.9pt DRAWN fence in the masthead, and a rule in the party
        # column that is an UNDERLINE of the row above it, not a fence.
        "cory_markham_v._auto_cycle_exchange_services_inc",
        # ONE ZONE, TWO LANDMARKS: the origin and the submission statement
        # with no fence between them, split at the alignment change. Also
        # the paper with NO roster at all — 'PER CURIAM:' straight in.
        "zachary_rusk_v._derek_beutler",
        # THE ROSTER CLOSED BY THE BYLINE rather than by a fence, its own
        # line ending in a comma ('… Bankruptcy Judges,' / 'PER CURIAM.').
        "sean_brewer_v._indiana_department_of_natural_resources",
        # CONSOLIDATED: two appeals in one box divided by a row of dashes
        # typed in the party column, two BAP dockets, and a caption that
        # fills page 1 so the rest of the ladder resumes on page 2.
        "trak-1_technology_inc._v._patrick_malloy_iii",
        # TWO BAP DOCKETS on one appeal and a cross-appeal, with the status
        # label wrapping across rows ('Plaintiff - Appellee - Cross-' /
        # 'Appellant,').
        "mcclave_state_bank_v._jay_stum",
        # The sheet set at a different scale (fences 181.5pt, banner at
        # x=177.5), whose CM/ECF strip and clerk's stamp the extractor
        # returns interleaved as one line, and whose byline is fenced.
        "lafaver_fiberglass_corporation_v._hampton_harold_price",
    ],
    "bap8": [
        # --- STYLE 'typed ladder': the Eighth Circuit clerk's blackletter
        # masthead over zones each fenced by a typed underscore rule on the
        # SHEET'S OWN axis, with the bankruptcy case's style ('In re: …')
        # divided from the appeal's parties by a rule inside the caption.
        # The ordinary cover: hyphen divider, the whole ladder on one page,
        # and a status row whose italic covers only part of it ('Acting
        # U.S. Trustee - Appellee').
        "anthony_lincoln_v._james_snyder",
        # THE STATUS ROWS SET ROMAN. ca8 identifies its caption by the
        # italic its statuses are set in; this clerk does not set them
        # consistently, so the caption is found by the COLUMN instead.
        "hartford_accident_and_indemnity_company_v._capital_credit_union",
        # The divider typed as a FULL underscore fence, so the caption
        # arrives as two fenced zones instead of one split by a subrule.
        "machele_l._goetz_v._victor_f._weber",
        # THE SHEET OFF THE PAGE AXIS: the whole cover set 6.5pt left of
        # centre and its roster 4pt left of the body rail, which is why the
        # axis is measured off the fences rather than assumed.
        "timothy_davies_v._diana_s._daugherty",
        # CONSOLIDATED: two dockets, two captions, one origin stated below
        # the last of them, and a caption that runs over the page break.
        "madison_resource_funding_corp._v._jerry_marsh",
        # The '[Published]' flag inside the date zone, and the ROSTER on
        # page 2 because the cover filled the sheet.
        "richard_berkshire_v._lauren_goodman",
        # THREE PARTIES STACKED on one side (two debtors and the trustee),
        # and a roster that wraps to a second row.
        "farm_credit_services_v._steven_l._swackhammer",
        # The banner's second row set at 12pt instead of 14pt, over a party
        # name that runs the full measure and stays centred on the axis.
        "state_of_north_dakota_v._susan_bala",
    ],
    "ca2": [
        # The stated-term order: rule-fenced caption, gutter counsel.
        "brooks_v._bright_horizons",
        # An EN BANC DENIAL — the same skeleton with no 'SUMMARY ORDER'
        # title, so the style is identified by its recital.
        "carroll_v._trump",
        # A stated-term order that draws NO typed rules at all, and sets a
        # two-column caption beside its docket.
        "in_re_rosellini",
        # The ladder: party rows mixed-case by design, counsel on page 3.
        "powell_v._ocwen_fin._corp.",
        # NUMBERED PAPER — a line-number gutter down the margin, typed
        # rules, rows flush left, and a caption footnote.
        "campbell_v._broome_county",
        # The tribunal stacked ABOVE the banner (BIA / NAC / A-numbers),
        # which is the only statement of origin a summary order prints.
        "suhel_ahmed_v._blanche",
        # Consolidated: stacked captions, counsel opening on the attorney's
        # name rather than a party label.
        "havlish_v._taliban_aliganga_v._taliban",
        # The notice set in the SAME type size as the banner and recital.
        "cicchiello_v._warden",
        # Counsel whose label column is also the body's own measure.
        "alsonidar_v._mullin",
    ],
    "ca4": [
        # The style is RULED BANDS: every section fenced by a drawn 108pt
        # rule centred on the page axis, sitting between rows. The band, not
        # the row, is the unit of meaning.
        "american_acceptance_corporation_of_sc_v._john_gietz",
        # Counsel with no ARGUED:/ON BRIEF: label at all — identified only
        # by being the band after the court's tail.
        "amer_rizvi_v._loudoun_county_school_board",
        # An immigration petition: 'On Petition for Review …' as the origin.
        "tho_huynh_v._todd_blanche",
        # Consolidated, with a PER-CASE origin and headmatter over 3 pages.
        "jonathan_r._v._patrick_morrisey",
        # A one-sided mandamus caption ('In re: …' / 'Petitioner.').
        "in_re_express_scripts_inc.",
        # A date band with a bare label and no value ('Decided:' alone) —
        # what the page says, and the surviving split-label flag.
        "kenneth_mcpherson_v._robert_patton",
        # An OFF-AXIS fence: the same 108pt rule set 18pt left.
        "winnebago_tribe_of_nebraska_v._united_states_department_of_the_army",
        # A visiting judge's byline ('David J. NOVAK'); the disposition opens
        # with words an origin line opens with.
        "rhino_energy_llc_v._dowcp",
        # Three consolidated petitions, no rules between the tail sections.
        "trokon_diahn_v._todd_blanche_1",
        # An amici roll ruled off INSIDE the caption.
        "bobby_goddard_v._michael_burnett",
        # No 'ARGUED:'/'ON BRIEF:' opener — so no counsel is recorded at all.
        "richard_harrold_v._lewis_hagen",
        # The notice that must NOT be swallowed into the appearances.
        "rock_spring_plaza_ii_llc",
    ],
    "ca1": [
        # The whitespace-zoned cover: no rules at all, zones separated by a
        # 27pt stand-off against a 13.6pt leading.
        "beckwith_v._frey",
        # An ERRATA SHEET — banner, docket, caption, title, amendments. No
        # origin, no panel, no counsel, no date, and no body expected.
        "rana_v._blanche",
        # An ORDER OF COURT: titled, dated 'Entered:', and carrying NO
        # counsel at all — the court's own order text follows the panel.
        "state_of_california_v._mullin",
        # A JUDGMENT that closes with the clerk's attest and a cc: list.
        "african_communities_together_v._mullin",
        # A stapled record whose second half opens mid-sentence — the file
        # that proved a body sentence can fake a document boundary.
        "united_states_v._ortiz-rodriguez",
        # An unsigned PER CURIAM: no byline for the reader to stop at.
        "arocho-rodriguez_v._roldan-concepcion",
        # The filing date standing alone under the counsel block.
        "vernaliz_perez_v._fema",
        # The family archetype: bracketed trial judge, counsel below the
        # roster, and a dissent.
        "adames-garcia_v._divris",
        # A byline BROKEN between the name and the office ('LYNCH,' /
        # 'Circuit Judge. After Christian Joel …').
        "united_states_v._andino-arroyo",
        # A footnote whose continuation opens on a wrapped citation
        # ('…Fed. R. App. P.' / '43(c)(2), Acting Attorney General …').
        "guzman_v._blanche",
        # The family archetype: bracketed trial judge, counsel below the roster.
        "cortes-ramos_v._martin-morales",
    ],
    "ca3": [
        # '[ARGUED]' inside an appearance; a date value that ends at its year.
        "united_states_v._christopher_miller",
        # The filing date and the first appearance share one row.
        "corey_kendig_v._nicholas_stolar",
        # Counsel identified BACKWARDS from its trailing label.
        "united_states_v._jerome_brown_1",
        # The roster shares the submission row; dates trail the bench word.
        "artem_v._gelis",
        # The origin runs onto the caption's last row.
        "united_states_v._jerome_brown",
        # THE WIDE MEASURE (x0=72): the LAR submission rule over its own date
        # row, an agency origin (Board / agency number / immigration judge),
        # and a starred roster whose note sits under the title.
        "arefin_chowdhury_v._attorney_general_united_states_of_america",
        # THE BOUND MEASURE (x0=144): two-row banner, the compact origin
        # ('Appeal from the U.S. District Court, D.N.J.' / 'Judge …, No. …'),
        # a roster that wraps, both sitting dates on one row.
        "kalshiex_llc_v._mary_jo_flaherty",
        # A FRONT COUNSEL ROSTER that runs across the page break, with
        # '[ARGUED]' set as its own column piece on the entry's own row.
        "united_states_v._nicole_schuster",
        # CONSOLIDATED: a second cover (its own docket + caption) on page 2,
        # and a counsel block over five pages read by ITS OWN COLUMNS — the
        # rail for the appearances, an indent for the justified labels.
        "whittaker_clark__daniels_v.",
        # THE EN BANC ORDER: two stacked captions, the origin reduced to a
        # bare district docket, the title above a four-row roster.
        "adolph_michelin_v._warden_moshannon_valley_correctional_center",
        # The 'Present:' roster order, whose district docket is stated only
        # in parentheses under the caption.
        "mahmoud_khalil_v._president_united_states_of_america",
        # THE CLERK'S ORDER: no roster, no dates — a title over the order's
        # own text, which the cover must not read as a date row.
        "josue_sanchez_v._attorney_general_united_states_of_america",
        # The MOTIONS-CALENDAR cover: an 'ALD-169' clerk code above the
        # banner and a two-row summary-action submission statement.
        "christopher_mbewe_v._superintendent_mahanoy_sci",
        # The TRAILING roster — ca3 is the one court that prints its
        # appearances below the writings (`counsel_after_writings`).
        "international_brotherhood_of_electrical_workers_lo_v._energy_harbor",
    ],
    "ca5": [
        # --- STYLE 'typed sandwich': every section is sandwiched between a
        # pair of rules centred on the page axis, and the rule's MEASURE
        # names the section — SHORT (90-106pt) for the docket, LONG
        # (234-252pt) for the origin. The band is the unit of meaning.
        #
        # The archetype: banner, fenced docket, caption, fenced origin,
        # roster, byline.
        "alexander_v._arceneaux",
        # The unsigned per-curiam form: 'Summary Calendar' shares the
        # docket band with the docket.
        "united_states_v._abron",
        # Two dockets in ONE band, joined by 'consolidated with'; the
        # roster wraps to a second row carrying the designation mark.
        "moreau_v._white",
        # Two dockets, each with its own caption: a short-fenced docket
        # NESTED inside the caption, and the headmatter running to page 2.
        "plaquemines_parish_v._bp_america_prod",
        # The fences DRAWN as strokes instead of typed, at the same two
        # measures — plus a second appeal fenced with typed rules.
        "busby_v._guerrero",
        # Drawn rules that are UNDERLINES, not fences (their ends coincide
        # with the row above); the 'ON REMAND FROM' posture recital, whose
        # wording collides with an origin opener.
        "olivier_v._city_of_brandon_ms",
        # The posture recital that the shared classifier read as an order's
        # title ('ON PETITION FOR REHEARING') over a signed opinion.
        "battieste_v._united_states",
        # 'REVISED' above the banner; two dockets under one caption (ONE
        # case); the clerk's stamp interleaved with the docket band.
        "naoise_ryan_v._united_states",
        # Status labels so long they start left of the page's 0.6 mark —
        # flush RIGHT to the caption's own rail, never an indent.
        "mcnutt_v._us_dept_of_justice",
        # The CONSOLIDATION DIVIDER: the long measure set flush at the rail
        # inside the caption, which is not a fence; en banc roster.
        "texas_medical_association_v._hhs",
        # A one-sided caption ('In re Google, L.L.C.,' / 'Petitioner.').
        "in_re_google",
        # No clerk's stamp at all, so no decision date is printed.
        "state_of_louisiana_v._fda",
        # A caption that fills page 1 and half of page 2.
        "nathan_v._alamo_heights_isd",
        # The origin fenced on page 2; the majority's 'joined by' byline.
        "united_states_v._state_of_texas",
    ],
    "ca6": [
        # --- STYLE 'paren-rail slip' (unpublished): a stacked ')' is the
        # caption's divider and the whole zone system; no rules at all.
        # The disposition line ('CLAY, J., delivered the opinion ...').
        "david_smith_v._cynthia_davis",
        # 'Case No.' as a docket, and the banner printed BELOW it.
        "isidro_ramos-ramos_v._todd_blanche",
        "united_states_v._jerry_baker",
        # A rail whose right column is one cell narrower — the OPINION
        # label sits past the origin column, not beside it.
        "darin_newson_v._nyx_llc",
        # --- STYLE 'ruled slip' (published): a box-drawn caption under a
        # 110pt drawn rule, with typed '________' fences below it.
        # The ordinary format: docket in the caption's right cell, the
        # origin, both dates, the roster, COUNSEL, then OPINION.
        "alexandre_ansari_v._moises_jimenez",
        # A DATE LABEL WITH NO VALUE ('Decided and Filed:' alone), which
        # used to end the walk one row above the roster.
        "demond_liles_v._v._michael_fisher",
        # Consolidated: two origin bands separated by a typed rule, and a
        # disposition whose continuation reads as a byline.
        "juan_sanchez_alvarez_v._markwayne_mullin",
        # A caption row set as ONE run across the rail
        # ('Plaintiffs-Appellees/Cross-Appellants, > Nos. 25-5385/5400').
        "joseph_fischer_v._karen_thomas",
        # An EN BANC DENIAL: the rehearing posture above the origin, and an
        # unsigned ORDER whose fence must be left standing as its anchor.
        "nathan_roberts_v._progressive_preferred_ins._co.",
        # Two pages only, so the running head never repeats for core to
        # measure — the court's own head band is what removes it.
        "texas_assn_of_bus._v._fcc",
    ],
    "ca7": [
        # --- STYLE 'typed rules': every section fenced by twenty underscores
        # 120pt wide on the page axis; the origin band set a step SMALLER
        # than the body; the roster below the last fence, bounded by the
        # court's own full stop.
        # The ordinary format: docket, caption, origin, dates, roster.
        "united_states_v._mona_ghosh",
        "derek_hundley_v._dee_dee_brookhart",
        "ana_bernal_v._kohls_corporation",
        # Consolidated: TWO caption bands under ONE docket row.
        "united_states_v._terry_ferguson",
        # A FULL-MEASURE typed rule used as a divider INSIDE the caption,
        # and the headmatter running onto page 2 under a running head.
        "bad_river_band_of_lake_superior_tribe_of_chippewa",
        # The docket row separated by a comma AND an ampersand together
        # ('Nos. 23-2434, 23-2450, 23-2479, & 23-2652').
        "united_states_v._warren_griffin",
        # A ONE-SIDED caption ('IN RE: …' / 'APPEALS OF: …') over a
        # bankruptcy origin that states two lower dockets.
        "city_of_chicago_v._ahmed_alayah",
        # In chambers: NO roster below the last fence, and an origin that
        # is a motion — no lower docket, no trial judge.
        "sidney_upchurch_v._united_states",
        # A non-district forum ('Appeal from the United States Tax Court.').
        "hyatt_hotels_corporation__subsidiaries_v._cir",
        # --- STYLE 'order form': the courthouse letterhead. No rules at
        # all; roster ONE JUDGE PER ROW under a bare 'Before'; a two-column
        # caption held by whitespace alone; letter-spaced 'O R D E R'.
        "close_armstrong_llc_v",
        # …and the NONPRECEDENTIAL DISPOSITION variant: the publication
        # flag, its citation notice dropped, three labelled date rows.
        "paul_smith_v._pamela_hart",
    ],
    "ca8": [
        # --- STYLE 'engraved ladder': a blackletter masthead over zones
        # each fenced by a typed underscore rule on the page axis.
        # The ordinary format: docket, caption, 'Appeal from …', both
        # dates, roster — the whole ladder on one page.
        "angela_kendall_v._zoltek_corporation",
        # The unpublished per curiam: the same ladder with a bracketed
        # '[Unpublished]' flag inside the date zone.
        "ana_ponce-lopez_v._todd_blanche",
        # An origin with NO opener at all ('United States Tax Court'),
        # which is why the origin is read by POSITION; and '[Published]'.
        "boechler_p.c._v._cir",
        # The AMICI RULE: a dashed rule dividing the friends of the court
        # from the parties INSIDE one fenced caption zone, plus a ladder
        # that runs over a page break.
        "abigail_farella_v._district_judge_a.j._anglin",
        # The amici in a fenced zone of their own, below a dashed rule.
        "leticia_roberts_v._tony_thompson",
        # A CAPTION FOOTNOTE set in the foot of page 1 while the date zone
        # the ladder is holding open resumes on page 2.
        "rustico_lacsina_v._todd_blanche",
        # White-filled letters used as spacers in the headmatter.
        "kyle_hane_v._city_of_cedar_rapids",
        "permanent_general_assurance_corp",
        # Two dockets, one origin stated below the last of them.
        "united_states_v._bailey_belt",
        # Sixteen consolidated petitions sharing one origin, with the
        # roster seventeen pages down.
        "minnesota_telecom_alliance_v._fcc",
    ],
    "ca10": [
        # The lower court's docket, its court abbreviation and the document's
        # own title were all being read into the case name.
        "johnson_v._rankins",
        "lunsford_v._green",
        "national_association_for_gun_rights_v",
        # The e-file stamp overlaps the banner; a footnote sequence with a gap
        # in it (19 of 1-22) that the audit reported as a clean extraction.
        "morphew_v._chaffee_county_colorado",
        # A caption whose parties run past the foot of page 1 and carry the
        # drawn rail onto page 2 — one box, two pages. Its date had also
        # merged into the banner row above it.
        "comanche_nation_v._ware",
        # THE UNPUBLISHED ORDER, the court's commonest paper: fence, caption
        # box, fence, the paper's own name, fence, roster, fence, and then
        # prose with no byline at all.
        "belcher_v._quick",
        # THE PUBLISHED SLIP: the same ladder with an origin band and an
        # UNLABELLED appearance block between the caption and the roster,
        # and a byline fenced under it.
        "church_of_jesus_christ_of_latter-day_saints_v._national_union_fire",
        # A published slip whose caption fills page 1 outright, so the whole
        # rest of the ladder — origin, counsel, roster, byline — is on p2.
        "citizens_for_constitutional_integrity_v._united_states",
        # Two consolidated appeals inside ONE box, divided by a row of
        # em-dashes the court types in the party column.
        "aaebo-akhan_v._connell",
        # Two consolidated appeals as TWO DRAWN BOXES on one page, fenced
        # apart, with the page-1 footnote zone splitting the ladder so the
        # appearances resume at the top of page 2.
        "united_states_v._tew",
        # THE OFF-AXIS RAIL: the party column is set wider and the drawn
        # divider moves with it (x=347.3 against the usual 310.9).
        "new_mexico_cattle_growers_association_v._united_states_forest",
        # A published slip that states NO origin and NO appearances:
        # fence, caption, fence, roster, fence, byline.
        "united_states_v._doe",
        # An EN BANC rehearing order — the full court's roster over three
        # rows, and an unsigned disposition under it.
        "united_states_v._watkins",
        # TWO STAPLED DOCUMENTS: an errata order and, behind it, the
        # corrected opinion with a cover of its own.
        "wildcat_coal_v._pacific_minerals",
    ],
    "ca11": [
        # The family archetype: 'FOR PUBLICATION' lifted off the caption, the
        # docket fenced in rules, the BIA origin, an all-caps roster.
        "alma_hernandez-rebollar_v",
        # Two cases heard together, each with its own docket and caption.
        "ismael_perez_v",
        # Caption whitespace and per-line alignment.
        "byron_chemaly_v._eddie_lampert",
        # A page with no text layer at all — the warning is correct, and the
        # record must still come out well-formed.
        "roger_tejon_v._zeus_networks_llc",
        # The one record that yields no criteria; locked so that if it starts
        # yielding some, we find out deliberately rather than by accident.
        "brandon_fulton_v._fulton_county_board",
    ],
    "cadc": [
        # FORMAT 'typed-rule order': the underscore run typed on the docket
        # row is the divider; the trial court's own number sits flush right
        # under it, and the caption is set at the left rail in title case.
        "timothy_petrozzi_v._muriel_bowser",
        # …the same order sheet reviewing an AGENCY: the order under review
        # ('DOD-03/03/2026 Order') stands where the trial number would, and
        # no origin statement is printed at all.
        "anthropic_pbc_v",
        # FORMAT 'fenced bands', argued opinion: the drawn 36pt axis fence
        # between sections, counsel in the band under the origin, and
        # 'Opinion for the Court filed by …' as the disposition.
        "adele_ruppe_v._marco_rubio",
        # …the same fence over a CONSOLIDATED record: a docket roll that
        # wraps four rows and three dispositions under one roster.
        "in_re_donald_trump",
        # The origin and the appearances with no wall between them.
        "inova_health_care_services_v",
        # FORMAT 'fenced bands', judgment: docket and September Term on one
        # printed row at 18pt, the caption at the left rail in caps, and
        # 'J U D G M E N T' left unclaimed as the unsigned writing's anchor.
        "np_red_rock_llc_v._nlrb",
        # A consolidated order sheet whose headmatter runs three pages, each
        # reprinting the banner and docket row as a running head.
        "patsy_widakuswara_v._kari_lake",
        # The record that draws NEITHER divider — the NLRB's own two-column
        # proposed judgment. The reader must return NOTHING for it.
        "vermont_information_processing_inc",
    ],
    "ca9": [
        # --- STYLE 'ruled caption box'. ca9 DRAWS the caption's column
        # divider — a vertical rule with a horizontal across its head and
        # another across its foot — and those three strokes are the whole
        # zone system on both of the court's papers.
        # THE MEMORANDUM (letter paper, 14pt): the clerk's filing stamp in
        # a column of its own, the agency numbers stacked one per
        # petitioner, and an unsigned disposition running straight in.
        "alfredo_silva-palomares_v",
        # THE PUBLISHED SLIP (reporter measure, 12pt): the staff summary
        # and the appearances stand between the roster and the opinion —
        # the summary is core's section, the appearances are headmatter.
        "3pak_llc_v._city_of_seattle",
        # A caption that runs over the page: a SECOND box on page 2 with
        # the parties alone in it; a lower docket split by a hyphen.
        "crain_walnut_shelling_lp_v",
        # …and one that fills eight pages, with boxes on every one.
        "state_of_colorado_v._meta_platforms_inc.",
        # 'D.C. No.' over its number on the next row.
        "county_of_san_bernardino_v",
        # The box drawn as a FILLED PATH: pdfio collects the horizontals
        # and drops the vertical, so the divider is read off the rules'
        # own right end — which is where the vertical stands elsewhere.
        "mercer_global_advisors_inc._v._hewitt",
        # The fully-boxed order form: rules the full measure and a TWIN
        # divider, two verticals between the same two horizontals.
        "michael_ray_hogan_v._jeremy_bean",
        # A three-row label in the right column ('ORDER AND / AMENDED /
        # OPINION') and 'Order;' among the who-wrote-what descriptors.
        "united_states_v._tekola",
        # A date band split by the PAGE BREAK: the date on page 1, the
        # place it was submitted at on page 2.
        "williams_v._legacy_health",
        # A published ORDER on letter paper: the district and its division
        # printed under the lower docket.
        "dickinson_v._trump",
        # Consolidated: two boxes on one page, agency numbers under an
        # 'EPA Nos.' label.
        "yurok_tribe_v._usepa",
        # The agency's NAME wrapping under its own number.
        "committee_for_a_better_arvin_v",
        # A footnote marker on the roster's bench word.
        "andasol_servellon_v._blanche",
        # The immigration memorandum: origin, dates and roster in three
        # bands under the box, body prose straight after.
        "edirisinghe_v._blanche",
        # Two consolidated appeals, each with its own origin.
        "eugene_doerr_v._david_shinn",
    ],
    "cafc": [
        # The style is TYPED FENCE BANDS: a 132pt run of underscores typed
        # between every section of the cover. The ordinary merits opinion —
        # banner, caption, bare docket, origin, date, appearances, and the
        # roster standing under the last fence.
        "a.l.m._holding_company_v._zydex_industries_private_ltd.",
        # A MOTIONS ORDER: 'ON MOTION' fenced above and below (so it is the
        # paper's name), 'O R D E R' under the last fence (so it is the
        # writing's heading and is left standing). Two pages, so core cannot
        # measure the running head by repetition.
        "bradley_v._united_states",
        # A RULE 36 JUDGMENT: 'JUDGMENT' fenced, the appearances fenced
        # closed, and the clerk's judgment form below the last fence left
        # entirely to the writings.
        "burns_v._dhs",
        # A NONPRECEDENTIAL disposition: the 'NOTE: … nonprecedential'
        # stamp dropped as a notice and read as the publication status; a
        # one-line pro-se appearance.
        "cantu_v._collins",
        # A one-page MANDAMUS order: a one-sided caption ('IN RE UNITED
        # STATES, / Petitioner'), no dates, no appearances, no roster.
        "in_re_us",
        # An ERRATA sheet: the date band ABOVE the caption, 'Appeal No.
        # 2025-1081' as the docket, and the publication flag printed as a
        # row of its own ('Nonprecedential Opinion').
        "guttenberg_v._dhs",
        # CONSOLIDATED: two captions divided by the court's typed dash row
        # (200pt, dashes — not the 132pt underscore fence), the cover
        # running onto page 2.
        "bissell_inc._v._itc",
        # An appeal consolidated with a mandamus petition, where the dash
        # divider stands INSIDE the origin band: two dockets, two origins,
        # and the lead appeal's is the document's.
        "in_re_byrd",
        # An EN BANC DENIAL: the appearances left unfenced under the last
        # fence (identified by the small caps cafc sets a name in), an
        # 11-judge roster wrapping three rows with a footnote mark on the
        # last, and a second full cover on page 4 the reader must not reach.
        "range_of_motion_products_llc_v._armaid_company_inc.",
        # A roster that wraps to a visiting judge whose row parses as a
        # byline ('FREEMAN, District Judge.†') — the wrap ends on the
        # leading and the mark, not on the punctuation.
        "davis_v._collins",
        # A caption of forty exporters that fills page 1 by itself, so the
        # cover's remaining fences are all on page 2.
        "fusong_jinlong_wooden_group_co._ltd._v._united_states",
        # The appearances running past the page break, with their closing
        # fence on page 2.
        "apple_inc._v._itc",
        # A SCANNED cover: page 1 carries no text at all, so the reader
        # returns NOTHING and core reads the document.
        "hepler_v._collins",
    ],
    "scotus": [
        # A merits cover with the Reporter's syllabus printed ABOVE it: the
        # writing's own cover is what the reader claims, not page 1.
        "abouammo_v._united_states",
        # An order cover closing on a dated docket row, with 'PER CURIAM.'
        # printed below — caps, like a party, and not a caption row.
        "klein_v._martin",
        # A consolidated stay cover, dockets fenced by rules.
        "danco_laboratories_llc_v._louisiana",
        # A cert denial: the Court's unsigned disposition, then a dissent.
        "alabama_v._powell",
        # A consolidated cover, stacked captions and docket cells, no
        # bracketed date.
        "allen_v._caster",
        # A bracketed date followed by 'PER CURIAM.'
        "allen_v._milligan",
        # A three-row caption wrap carrying an escaped ampersand.
        "m__k_employee_solutions_inc._v._trustees_of_iam_nat._pension",
        # The multi-writing merits opinion.
        "trump_v._slaughter",
    ],
    "fla": [
        # --- STYLE 'engraved cover': a 37pt masthead over a docket fenced
        # above and below by an 84pt rule centred on the page axis.
        # The plain form: one fence pair, one caption, an unsigned
        # 'PER CURIAM.' byline, and the roster printed after the writing.
        "andrew_richard_lukehart_v._state_of_florida",
        # FOUR fence pairs — one per consolidated case — with the fourth
        # caption carried onto page 2 and four dockets to state.
        "state_attorneys_for_the_second_seventh_and_ninth_judicial_circuits",
        # The paper's own name under the date ('CORRECTED OPINION'), over a
        # 163pt rule that is an UNDERLINE, not a fence: same axis, same
        # page, and its ends coincide with the row above it.
        "marcus_roland_maye_v._state_of_florida",
        # The one record whose fences are DRAWN (98.1pt lines) instead of
        # typed, and whose caption is one-sided ('IN RE: AMENDMENTS TO …').
        "in_re_amendments_to_rules_regulating_the_florida_bar_and_rules_of",
        # --- STYLE 'docket sheet': the clerk's disposition sheet — a 32pt
        # masthead, a weekday release row, a two-column caption, and one
        # drawn 473pt rule fencing the block off from the ruling.
        # The full form, with a lower-tribunal column beside the docket.
        "the_florida_bar_v._kenneth_chesebro",
        # A sheet whose right column holds the docket and nothing else, so
        # the column ends at its own last cell instead of padding out.
        "walter_javier_arrazola_mendivil_v._the_florida_bar",
    ],
    "ala": [
        # --- STYLE 'engraved certificate' (270 of 467): a 20pt masthead
        # pinned in the page's TOP BAND, a 16pt release date, and the
        # docket and caption set as a justified paragraph at the body rail.
        # The caption ends where the page leaves that rail.
        # THE ORDINARY CERTIFICATE: a direct appeal, one origin
        # parenthetical, and a wrapped caption at the rail.
        "safeway_insurance_company_of_alabama_inc._v._tara_abner_as_personal",
        # The same paper headed 'ORDER' instead of 'CERTIFICATE OF
        # JUDGMENT' (8 records) — the heading is the WRITING's either way,
        # which is why the reader stops at the rail and not at a word.
        "ex_parte_akamai_technologies_inc._petition_for_writ_of_mandamus",
        # A CERTIORARI PETITION: the petition title, the '(In re: …)' case
        # below, and TWO courts in the origin — and a caption row pdfio
        # splits at its justification gap ('Ex parte Donald Vester
        # Robbins, Jr.' | 'PETITION FOR WRIT OF'), which the reader must
        # read as one visual row or the caption ends three rows early.
        "ex_parte_donald_vester_robbins_jr._petition_for_writ_of_certiorari",
        # --- STYLE 'fenced cover' (136 of 467): a 22pt masthead set a
        # third of the way down the page under the reporter's notice, and
        # a docket standing between a TYPED 175pt underscore fence pair
        # centred on the page axis. Every row is centred on that axis.
        # THE ORDINARY COVER: one fence pair, a pivoted caption, an
        # 'Appeal from …' origin and its docket parenthetical.
        "790_montclair_llc_v._the_station_at_crestline_heights_llc_valley",
        # FIFTEEN fence pairs — the Methodist Church mandamus
        # consolidation — carrying captions to PAGE 11, which is why the
        # walk is bounded at 12 and the origin is recorded for the LEAD
        # case only.
        "in_re_armstrong_methodist_church_v._alabama-west_florida_conference",
        # A CERTIFIED QUESTION from a federal district court: the origin
        # statement WRAPS across three rows and carries a federal docket
        # ('7:23-cv-00692-ACA'), so an origin read row-by-row folded its
        # middle line into the party names.
        "the_new_york_times_company_v._kai_spears_certified_question",
        # THE PAPER NAMING ITSELF on the cover ('On Rehearing Ex Mero
        # Motu') — the one ROMAN row in a caption block the court sets
        # entirely in bold.
        "teresa_williams_and_barneys_childcare_and_learning_center_inc._dba",
        # TWO dockets inside ONE fence pair ('SC-2025-0346 and
        # SC-2025-0357'), so the fenced row is read as the list it is.
        "tara_grall_v._william_grall_and_g-team_p.c.",
        # --- STYLE 'judicial-department list' (61 of 467): the no-opinion
        # release list. No masthead above body size at all — three
        # body-size rows on the axis, then the docket and caption at the
        # rail. THE ORDINARY LIST, with a docket broken across the measure
        # ('… Circuit Court: CV-' / '24-900114') that must close up.
        "1_oak_grand_llc_v._richard_l._crawford_iii_lana_d._crawford",
        # A LIST that names itself under the caption ('On Rehearing Ex
        # Mero Motu') — the one row on this paper that leaves the rail.
        "olaf_lieb_tina_lieb_jennifer_m._holton_36081_rentals_llc_and_eeztec",
    ],
}
