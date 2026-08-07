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
    "ca1": [
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
    ],
    "ca4": [
        # The ordinary format: every section in its own ruled band.
        "american_acceptance_corporation_of_sc_v._john_gietz",
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
    "ca5": [
        # The caption must not reach across the origin to take the title.
        "battieste_v._united_states",
        # Two dockets, each with its own caption: two cases.
        "busby_v._guerrero",
        # Two dockets under one caption: ONE case. Plus the clerk's stamp.
        "naoise_ryan_v._united_states",
        # An origin stated over two bands, the first half left dangling.
        "olivier_v._city_of_brandon_ms",
        # The origin runs onto the caption's last row; en banc roster.
        "united_states_v._state_of_texas",
    ],
    "ca6": [
        # The disposition line ('CLAY, J., delivered the opinion ...').
        "david_smith_v._cynthia_davis",
        # 'Case No.' as a docket, and the banner printed BELOW it.
        "isidro_ramos-ramos_v._todd_blanche",
        "united_states_v._jerry_baker",
    ],
    "ca7": [
        # The order form: roster one judge per row, letter-spaced 'O R D E R',
        # two-column caption held by whitespace alone.
        "close_armstrong_llc_v",
        # The ordinary format, for contrast.
        "derek_hundley_v._dee_dee_brookhart",
        "ana_bernal_v._kohls_corporation",
    ],
    "ca8": [
        # White-filled letters used as spacers in the headmatter.
        "kyle_hane_v._city_of_cedar_rapids",
        "permanent_general_assurance_corp",
        # Two dockets, one origin stated below the last of them.
        "united_states_v._bailey_belt",
        # Sixteen consolidated petitions sharing one origin.
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
        # A date that had merged into the banner row above it.
        "comanche_nation_v._ware",
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
        # The trial court's own docket, set on a row under the appeal's.
        "timothy_petrozzi_v._muriel_bowser",
        # The order form: parties in ORDINARY TITLE CASE, bounded by the
        # filing date above and the roster below; the agency's order above it.
        "anthropic_pbc_v",
        # A published opinion: counsel in the band between the origin and the
        # roster, and 'Opinion for the Court filed by ...' as the disposition.
        "in_re_donald_trump",
        # The origin and the appearances with no wall between them.
        "inova_health_care_services_v",
        # The ordinary caps caption, for contrast.
        "np_red_rock_llc_v._nlrb",
    ],
    "ca9": [
        # Two-column caption: parties left, docket/agency numbers/label right.
        "alfredo_silva-palomares_v",
        # A caption that runs over the page; a lower docket split by a hyphen.
        "crain_walnut_shelling_lp_v",
        # 'D.C. No.' over its number on the next row.
        "county_of_san_bernardino_v",
        # A footnote marker on the roster's bench word.
        "andasol_servellon_v._blanche",
        # Origin, dates and roster all on ONE row.
        "edirisinghe_v._blanche",
        # Two consolidated appeals, each with its own origin.
        "eugene_doerr_v._david_shinn",
    ],
}
