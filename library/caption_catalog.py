"""A hand-built catalog of distinct case-caption LINE styles, transcribed from a
survey of ~100 real opinions.

The fascination here is how courts *draw* the caption — the divider down the
middle (a vertical rule, a column of close-parens, colons, section signs, square
brackets, asterisks, a curly brace…), the horizontal rules and boxes, the
blackletter mastheads, the slashes and dots that close it off. Each entry records
the structural tells as facet tags, a short write-up of what's weird, the parsing
signal it gives us, and a faithful ASCII recreation. Grouped by column count.
Rendered at /captions; the long-term point is to mine these tells for parsing.

Facets (one value or a few space-separated; em-dash = none):
  columns  one-column | two-column | three-column
  divider  none | pipe | | parens ) | colon : | section § | bracket ] |
           asterisk * | double-pipe || | brace } | box edge | slash /
  rules    none | underline | single-line | double-line | bold-line | rule-bands
  box      any of  top bottom left right
  spacing  single | double
  name     bold caps plain smallcaps blackletter
  status   italic indent centered flush-right
  banner   caps letter-spaced centered blackletter
  glyphs   § seal asterisks filing-stamp x-caps dots
  extras   docket · term/clerk · appeal-from · trial-judge · panel · notice
"""

from __future__ import annotations

FACETS = [
    "columns", "divider", "rules", "box", "spacing",
    "name", "status", "banner", "glyphs", "extras",
]


def _S(**kw):
    return kw


STYLES = [
    # ============================================================ ONE COLUMN
    _S(
        id="blackletter-centerfold", name="The Blackletter Centerfold",
        columns="one-column",
        summary="an engraved Old-English masthead over a centered party stack, parties joined by a centered –v–",
        courts="Indiana Supreme Court (also Texas, 7th Cir., 8th Cir. BAP use blackletter)",
        tags={"columns": "one-column", "divider": "none", "rules": "single-line",
              "spacing": "double", "name": "plain", "status": "italic centered",
              "banner": "blackletter centered", "glyphs": "filing-stamp",
              "extras": "docket · argued/decided"},
        desc="An ornate <b>blackletter</b> masthead (“𝔴𝐸𝐸…” Old English) crowns a fully "
        "centered caption: party names large, roles in small italic, and a "
        "centered <code>–v–</code> token instead of a gutter <code>v.</code> A faint rule "
        "divides the parties from a centered <code>Argued … | Decided …</code> line whose "
        "two dates are split by a lone pipe.",
        signal="No columns, no party-status margins — everything is centered; the "
        "<code>–v–</code> glyph (em-dashes hugging a v) is the party split, and a single "
        "rule ends the caption.",
        ascii=r"""
                    I N   T H E
           Indiana Supreme Court     (blackletter)

            Supreme Court Case No. 25S-CR-303

                  Carlos T. Ortiz,
                 Appellant-Defendant,

                        –v–

                  State of Indiana,
                  Appellee-Plaintiff.
   ---------------------------------------------
       Argued: January 22, 2026 | Decided: May 19, 2026
""",
    ),
    _S(
        id="triple-band", name="The Triple Band",
        columns="one-column",
        summary="three full-width rules; the docket number rides in its own banded slot",
        courts="Iowa Supreme Court",
        tags={"columns": "one-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "bold centered", "status": "centered",
              "banner": "centered", "glyphs": "—", "extras": "docket · submitted/filed"},
        desc="Three full-width horizontal rules slice the headmatter into bands: "
        "the docket <code>No.</code> sits sandwiched in its own slot between rules one and "
        "two, the submitted/filed dates ride below, and the party stack (bold "
        "names, roman <code>vs.</code>) lives between rules two and three.",
        signal="Equal full-width rules at regular intervals = banded fields; the "
        "docket is the line boxed between the first two.",
        ascii=r"""
              In the Iowa Supreme Court
   ----------------------------------------------
                    No. 24-1879
   ----------------------------------------------
        Submitted April 15, 2026 - Filed May 15, 2026

                 Javonte Hines-Miller,
                       Appellee,
                         vs.
                    Ashlea Teter,
                      Appellant.
   ----------------------------------------------
   On review from the Iowa Court of Appeals.
""",
    ),
    _S(
        id="underscore-ladder", name="The Underscore Ladder",
        columns="one-column",
        summary="short centered underscores rung between every metadata block",
        courts="Supreme Court of South Carolina",
        tags={"columns": "one-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "plain", "status": "centered",
              "banner": "centered", "glyphs": "—",
              "extras": "docket · appeal-from · disposition"},
        desc="A ladder of short, centered underscore rules separates each block in "
        "turn — caption, then <code>ON WRIT OF CERTIORARI…</code>, then <code>Appeal from…</code>, "
        "then <code>Opinion No.…</code>, then a one-word centered disposition "
        "(<code>REVERSED</code>) — each rung fenced above and below by its own little rule.",
        signal="Repeated short centered rules are section separators, not the "
        "caption end; the bold one-word line near the bottom is the disposition.",
        ascii=r"""
        Aretha Price, Respondent,
        v.
        Progressive Northern Insurance Company, Petitioner.
        Appellate Case No. 2025-000943
                   _________
        ON WRIT OF CERTIORARI TO THE COURT OF APPEALS
                   _________
              Appeal from Chester County
                   _________
                 Opinion No. 28325
                   _________
                    REVERSED
                   _________
""",
    ),
    _S(
        id="double-rule-banner", name="The Double-Rule Banner",
        columns="one-column",
        summary="blackletter masthead with == double-rule bands around docket and provenance",
        courts="Supreme Court of Texas",
        tags={"columns": "one-column", "divider": "none", "rules": "double-line",
              "spacing": "double", "name": "plain", "status": "italic centered",
              "banner": "blackletter centered", "glyphs": "—",
              "extras": "docket · petition-from · argued"},
        desc="The civil high court pairs an Old-English <b>blackletter</b> masthead with "
        "<b>double horizontal rules</b> (<code>===</code>) that band the docket and the "
        "<code>On Petition for Review…</code> provenance. Party roles are italic; the whole "
        "thing is centered.",
        signal="Blackletter + paired double rules; docket is the line between the "
        "first pair, provenance between the second.",
        ascii=r"""
              Supreme Court of Texas    (blackletter)
                    ===========
                     No. 25-0350
                    ===========
           Angela Kate Whittenburg Wang, et al.,
                      Petitioners,
                          v.
            John Burkhart Whittenburg, et al.,
                      Respondents
                    ===========
              On Petition for Review from the
          Court of Appeals for the Seventh District
                    ===========
                Argued February 12, 2026
""",
    ),
    _S(
        id="sealed-double-rule", name="The Sealed Double-Rule",
        columns="one-column",
        summary="a court seal up top and == bands around every element",
        courts="Texas Court of Criminal Appeals (habeas / WR- docket)",
        tags={"columns": "one-column", "divider": "none", "rules": "double-line",
              "spacing": "single", "name": "bold caps centered", "status": "centered",
              "banner": "caps centered", "glyphs": "seal",
              "extras": "docket · application-from · per curiam"},
        desc="A habeas matter styled <code>EX PARTE NAME, Applicant</code>, centered, with an "
        "engraved <b>court seal</b> on top and <b>double rules</b> banding the docket and the "
        "<code>ON APPLICATION FOR A WRIT OF HABEAS CORPUS…</code> block. Even <code>O P I N I O N</code> "
        "is letter-spaced.",
        signal="Centered, column-less, double-ruled bands → an original proceeding "
        "(no appellant/appellee); the seal is furniture.",
        ascii=r"""
                       (CCA seal)
              IN THE COURT OF CRIMINAL APPEALS
                        OF TEXAS
                  ====================
                  NO. WR-97,593-01
                  ====================
            EX PARTE GEORGE GLYNN BANTA , Applicant
                  ====================
          ON APPLICATION FOR A WRIT OF HABEAS CORPUS
          CAUSE NO. 20-11-14200 (1) IN THE 435TH ...
                  ====================
          Per curiam.
                       O P I N I O N
""",
    ),
    _S(
        id="citation-crown", name="The Citation Crown",
        columns="one-column",
        summary="a vendor-neutral cite over a heavy rule crowns small-caps parties",
        courts="Supreme Court of Utah",
        tags={"columns": "one-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "smallcaps", "status": "italic centered",
              "banner": "smallcaps centered", "glyphs": "—",
              "extras": "neutral-cite · docket · heard/filed"},
        desc="The vendor-neutral citation (<code>2026 UT 7</code>) sits alone above a single "
        "<b>heavy full-width rule</b> that crowns the page; below it, a small-caps banner, "
        "small-caps party names, and thin centered rules separating each lower "
        "block (docket, heard/filed dates, <code>On Direct Appeal</code>).",
        signal="A medium-weight cite over one heavy rule = the crown; small-caps "
        "throughout; thin rules band the lower fields.",
        ascii=r"""
                    2026 UT 7
   ==============================================
                     IN THE
        SUPREME COURT OF THE STATE OF UTAH
                  ------------
   WAYNE ASTON and VALLEY FORGE IMPACT PARK ... ,
                    Appellants,
                       v.
   CHRONICLE-PROGRESS LLC, ... and MATT WARD,
                    Appellees.
                  ------------
                   No. 20241202
              Heard Dec. 12, 2025 / Filed Apr. 2, 2026*
""",
    ),
    _S(
        id="consolidated-centerline", name="The Consolidated Centerline",
        columns="one-column",
        summary="centered bold stack joined by VS. and a C/W consolidation marker",
        courts="Supreme Court of Louisiana",
        tags={"columns": "one-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "bold caps centered", "status": "centered",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · writ-from · consolidation"},
        desc="Everything centered and bold: the parties joined by <code>VS.</code>, and — the "
        "tell — a centered <code>C/W</code> (“consolidated with”) marker stitching a second "
        "caption underneath the first. A roman <code>On Writ of Certiorari…</code> line "
        "closes it.",
        signal="A centered <code>C/W</code> between two captions = consolidated cases on one "
        "page; no rules or dividers at all.",
        ascii=r"""
              SUPREME COURT OF LOUISIANA
                   No. 2025-C-00551

      BRUCE A. O'KREPKI, INDEPENDENT EXECUTOR
       OF THE SUCCESSION OF RICHARD E. O'KREPKI
                        VS.
           PENELOPE BRODTMANN O'KREPKI
                        C/W
          SUCCESSION OF RICHARD E. O'KREPKI

  On Writ of Certiorari to the Court of Appeal, Fifth Circuit
""",
    ),
    _S(
        id="record-ledger", name="The Record Ledger",
        columns="one-column",
        summary="a bold-italic party block above a tabbed label:value docket sheet",
        courts="Supreme Court of Mississippi",
        tags={"columns": "one-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "bold caps", "status": "—",
              "banner": "centered", "glyphs": "—",
              "extras": "docket · trial-court record table"},
        desc="The whole party block is set in <b>bold italic</b> caps; below it the opinion "
        "opens not with prose but with a <b>tabbed ledger</b> of the trial-court record — "
        "<code>DATE OF JUDGMENT:</code>, <code>TRIAL JUDGE:</code>, <code>COURT FROM WHICH APPEALED:</code> — each "
        "label flush left with its value at a fixed tab stop.",
        signal="A label:value table (DATE OF JUDGMENT, etc.) right under the parties "
        "is headmatter, not the opinion; the <code>-SCT</code>/<code>-COA</code> docket suffix flags the court.",
        ascii=r"""
                  NO. 2024-CA-00644-SCT

  BROOKE SHANTELLE DENISON
  v.
  MISSISSIPPI ORGAN RECOVERY AGENCY, INC.,
  SHIRLEY SCHLESSINGER, M.D., AND ...

  DATE OF JUDGMENT:            05/03/2024
  TRIAL JUDGE:                 HON. ...
  COURT FROM WHICH APPEALED:   ...
""",
    ),
    _S(
        id="bare-centerfold", name="The Bare Centerfold",
        columns="one-column",
        summary="purely centered type, no rules or dividers at all",
        courts="Supreme Court of Oregon · South Carolina (consolidated)",
        tags={"columns": "one-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "caps", "status": "italic centered",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · en banc"},
        desc="The minimalist: a fully centered caption held together by nothing but "
        "indentation and whitespace — no rule, no box, no divider glyph. Surnames in "
        "caps, <code>Respondent.</code> italic, parenthetical dockets, an <code>En Banc</code> line.",
        signal="No line-art whatsoever; rely on centering + the <code>v.</code>/<code>In re</code> token "
        "and an <code>En Banc</code> or panel line to bound the caption.",
        ascii=r"""
          IN THE SUPREME COURT OF THE
                STATE OF OREGON

          In re Complaint as to the Conduct of
                  Derek J. ASHTON,
                   OSB No. 871552,
                    Respondent.
              (OSB 2202) (SC S071535)

En Banc
""",
    ),
    _S(
        id="in-the-matter-order", name="The In-the-Matter Order",
        columns="one-column",
        summary="a one-party recital and a centered ORDER, no rules",
        courts="Kansas · (disciplinary & clerk's orders generally)",
        tags={"columns": "one-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "caps", "status": "italic centered",
              "banner": "caps centered", "glyphs": "—", "extras": "docket"},
        desc="With no opposing party the caption collapses to <code>In the Matter of NAME,</code> / "
        "italic <code>Respondent.</code>, then a centered all-caps document type (<code>ORDER</code>). "
        "No rules anywhere.",
        signal="A centered all-caps type word after a one-party recital and no "
        "byline → a per-curiam order; the type line opens the body.",
        ascii=r"""
     IN THE SUPREME COURT OF THE STATE OF KANSAS

                    No. 124,955

       In the Matter of JASON MICHAEL JANOSKI,
                     Respondent.

                       ORDER

      On March 11, 2025, the court reinstated ...
""",
    ),
    _S(
        id="seal-crowned", name="The Seal-Crowned Slip",
        columns="one-column",
        summary="full-color seals flanking a blackletter banner, with an e-filed stamp",
        courts="Supreme Court of the CNMI (Northern Mariana Islands)",
        tags={"columns": "one-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "smallcaps", "status": "italic centered",
              "banner": "blackletter centered", "glyphs": "seal filing-stamp",
              "extras": "docket · neutral-cite · panel"},
        desc="A round full-color court seal sits center-top above a blackletter "
        "banner, a second seal + an <code>E-FILED</code> clerk stamp rides the top-right "
        "corner, and a vendor-neutral <code>Cite as: 2026 MP 1</code> anchors the lower band. "
        "<code>AND</code> joins a third party.",
        signal="Two seals + an e-filed corner stamp + <code>Cite as: 2026 MP N</code>; centered "
        "small-caps parties with <code>AND</code>-joined applicants.",
        ascii=r"""
       (seal)                  (seal) E-FILED
                          CNMI SUPREME COURT
                  IN THE
              Supreme Court     (blackletter)
                  OF THE
   Commonwealth of the Northern Mariana Islands
            -----------------------
   ANAKS OCEAN VIEW HILL ... ASSN, LTD.,
              Petitioner-Appellant,
                      v.
            PERRY INOS JR., ET AL.,
              Respondent-Appellees,
                     AND
            ATKINS KROLL SAIPAN, INC.,
              Applicant-Appellee.
""",
    ),
    _S(
        id="letterspaced-order", name="The Letter-Spaced Order",
        columns="one-column",
        summary="a book-typeset centered caption closing on a letter-spaced O R D E R",
        courts="federal district courts (centered variant, e.g. E.D. Tex.)",
        tags={"columns": "one-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "bold centered", "status": "italic centered",
              "banner": "caps centered", "glyphs": "—", "extras": "docket"},
        desc="A few districts abandon the boxed pleading caption for a clean, "
        "book-typeset centered one: bold party names, italic roles, a short rule "
        "under the docket and another under the parties, closing on a "
        "letter-spaced <code>O R D E R</code>.",
        signal="Centered + tiny decorative rules + letter-spaced heading = the "
        "typeset district variant; no pleading gutter to find.",
        ascii=r"""
              UNITED STATES DISTRICT COURT
              EASTERN DISTRICT OF TEXAS
                  No. 6:26-cv-00048
                     ----------
               Phillip James Emerson, Jr.,
                       Petitioner,
                          v.
                F. Duncan Thomas et al.,
                      Respondents.
                     ----------
                     O R D E R
""",
    ),

    # ============================================================ TWO COLUMN
    _S(
        id="old-faithful", name="Old Faithful",
        columns="two-column",
        summary="one vertical rule, one half horizontal rule that flips up to meet it",
        courts="federal district courts · many state trial & appellate courts",
        tags={"columns": "two-column", "divider": "pipe |", "rules": "single-line",
              "box": "right + bottom-left", "spacing": "double", "name": "caps",
              "status": "indent", "banner": "caps centered", "glyphs": "—",
              "extras": "docket"},
        desc="The baseline everyone starts from: a single <b>vertical rule</b> splits the "
        "page, parties left and docket right, closed by a <b>half-width horizontal "
        "rule</b> under the parties that runs into the vertical and <b>flips up</b> at the "
        "corner (<code>┘</code>).",
        signal="One vertical rule = the column split; the bottom-left corner rule "
        "ends the caption; author is in a later byline/signature, not the box.",
        ascii=r"""
                  UNITED STATES DISTRICT COURT
                EASTERN DISTRICT OF CALIFORNIA

   JANE DOE,                          │
                                      │
              Plaintiff,              │   No. 2:24-cv-01234
                                      │
        v.                            │   ORDER
                                      │
   ACME CORPORATION,                  │
              Defendant.              │
   ------------------------------------┘
""",
    ),
    _S(
        id="parenthetical-box", name="The Parenthetical Box",
        columns="two-column",
        summary="a column of close-parens ) stands in for the vertical rule",
        courts="Idaho Supreme Court · Maine Superior · Washington Supreme · many districts",
        tags={"columns": "two-column", "divider": "parens )", "rules": "underline",
              "spacing": "double", "name": "bold caps", "status": "italic indent",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · term/clerk · appeal-from"},
        desc="The single most common variant: instead of a drawn rule, a tidy "
        "<b>column of <code>)</code></b> runs down the middle, parties left, metadata right "
        "(sitting term, <code>Opinion Filed:</code>, the Clerk, or a docket). One underline "
        "marks the end. Federal districts use the same rail with a <code>Case No.</code> right.",
        signal="A run of <code>)</code> glyphs at a fixed x is the divider — left is parties, "
        "right is metadata, never parties.",
        ascii=r"""
              IN THE SUPREME COURT OF THE STATE OF IDAHO
                          Docket No. 51595

   STATE OF IDAHO,                    )
        Plaintiff-Appellant,          )   Boise, January 2026 Term
   v.                                 )   Opinion Filed: May 7, 2026
   GANNON MANUELITO,                  )   Melanie Gagnepain, Clerk
        Defendant-Respondent.         )
   ___________________________________)
""",
    ),
    _S(
        id="banded-bracket", name="The Banded Bracket",
        columns="two-column",
        summary="a )-divider, but horizontal rules band the banner and close the caption",
        courts="Appellate Court of Illinois (all districts)",
        tags={"columns": "two-column", "divider": "parens )", "rules": "single-line",
              "spacing": "double", "name": "bold caps", "status": "indent",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · appeal-from · trial-judge"},
        desc="Illinois takes the <code>)</code> rail and frames the masthead in <b>horizontal "
        "rules</b> — above and below the <code>APPELLATE COURT OF ILLINOIS / … DISTRICT</code> banner, "
        "and one closing the caption. Right column is provenance + the "
        "<code>Honorable …, Judge presiding.</code> Juvenile cases wrap the party block in literal parentheses.",
        signal="Same <code>)</code> split; the banding rules bracket the banner, so the "
        "caption is the band between the second and third rule.",
        ascii=r"""
   ----------------------------------------------------------
                  APPELLATE COURT OF ILLINOIS
                        FIRST DISTRICT
   ----------------------------------------------------------
   THE PEOPLE OF THE STATE OF ILLINOIS,    )   Appeal from the
         Plaintiff-Appellee,               )   Circuit Court of
   v.                                      )   Cook County.
   QUINTON GATES,                          )   No. 17 CR 09924
         Defendant-Appellant.              )   Honorable ...
   ----------------------------------------------------------
   JUSTICE HYMAN delivered the judgment of the court...
""",
    ),
    _S(
        id="colon-rail", name="The Colon Rail",
        columns="two-column",
        summary="a vertical ladder of colons : divides parties from docket",
        courts="Ohio Cts. of Appeals · Pennsylvania Supreme · many districts · CIT",
        tags={"columns": "two-column", "divider": "colon :", "rules": "none",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · trial-court · disposition"},
        desc="A tall stack of <b>colons</b> <code>:</code> (one per line) is the divider. Ohio pairs it "
        "with a centered row of spaced dots (<code>. . . . .</code>) to close the caption; "
        "Pennsylvania fills the right side with a long prose <code>Appeal from the Order…</code> "
        "recital and a bold justice roster above.",
        signal="A column of <code>:</code> at a fixed x = the split; an Ohio dotted row or a "
        "PA prose recital follows in the right column.",
        ascii=r"""
              IN THE COURT OF APPEALS OF OHIO
                SECOND APPELLATE DISTRICT
   DAVID DODD                  :
        Appellee               :   C.A. No. 2025-CA-42
   v.                          :   Trial Court Case No. 2023CVG1581
   CYNTHIA PRESTON             :   (Civil Appeal from Municipal Court)
        Appellant              :   FINAL JUDGMENT ENTRY & OPINION
                 . . . . . . . . . .
""",
    ),
    _S(
        id="section-rail", name="The Section-Sign Rail",
        columns="two-column",
        summary="a vertical ladder of section signs § (very Texas)",
        courts="Texas courts — Business Court, district courts (E.D./N.D. Tex.)",
        tags={"columns": "two-column", "divider": "section §", "rules": "double-line",
              "spacing": "double", "name": "caps", "status": "italic indent",
              "banner": "caps centered", "glyphs": "§ seal",
              "extras": "docket · disposition"},
        desc="The unmistakable Texas tell: a column of <b><code>§</code> section signs</b> runs down "
        "the middle. The Business Court adds the state seal and <b>double rules</b> "
        "sandwiching the opinion title; federal Texas districts use the same <code>§</code> "
        "rail with a plain <code>CIVIL ACTION NO.</code> on the right.",
        signal="A column of <code>§</code> glyphs is the divider — Texas, almost always; right "
        "side holds the cause/civil-action number.",
        ascii=r"""
                  THE BUSINESS COURT OF TEXAS
                      ELEVENTH DIVISION
   ASPIRE COMMERCIAL, LLC      §
        Plaintiff,             §
   v.                          §   Cause No. 26-BC11B-0040
   CHRISTOPHER STEPHENSON and  §
   BES.AI, LLC,                §
        Defendants.            §
   ============================================
        MEMORANDUM OPINION AND ORDER ...
   ============================================
""",
    ),
    _S(
        id="bracket-rail", name="The Square-Bracket Rail",
        columns="two-column",
        summary="a vertical ladder of right-brackets ] as the divider",
        courts="U.S. District Court, N.D. Alabama",
        tags={"columns": "two-column", "divider": "bracket ]", "rules": "underline",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps centered", "glyphs": "—", "extras": "docket"},
        desc="Northern Alabama's signature: the gutter is a column of <b>right square "
        "brackets <code>]</code></b>, one per line, with the docket nestled against them and a "
        "bold underlined <code>MEMORANDUM OPINION</code> below.",
        signal="A column of <code>]</code> glyphs = the N.D. Ala. divider (Movant/Respondent "
        "habeas labels common).",
        ascii=r"""
        IN THE UNITED STATES DISTRICT COURT
       FOR THE NORTHERN DISTRICT OF ALABAMA
                 SOUTHERN DIVISION

   DEMONTAYE LAMAR JONES,          ]
        Movant,                    ]
   v.                              ]   Case No.: 2:24-cv-8021-ACA
   UNITED STATES OF AMERICA,       ]
        Respondent.                ]
                MEMORANDUM OPINION
""",
    ),
    _S(
        id="asterisk-rail", name="The Asterisk Rail",
        columns="two-column",
        summary="a vertical column of single asterisks * as the divider",
        courts="Supreme Court of Maryland · U.S. District Court, D. Md.",
        tags={"columns": "two-column", "divider": "asterisk *", "rules": "none",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps", "glyphs": "asterisks", "extras": "docket"},
        desc="Maryland runs a column of <b>free-standing asterisks <code>*</code></b> down the "
        "centerline. The Supreme Court even splits its own name across the right "
        "column opposite the asterisks; the district court pairs the vertical "
        "rail with a long spaced-asterisk horizontal rule below.",
        signal="A column of lone <code>*</code> glyphs = Maryland; watch for the court name "
        "stacked in the right column rather than a top banner.",
        ascii=r"""
                              *      IN THE
     IN THE MATTER OF THE     *      SUPREME COURT
   APPLICATION OF MERRY       *      OF MARYLAND
   LYNN ALBERT LYMN TO        *
   RESIGN FROM THE            *      AG No. 59
   PRACTICE OF LAW IN MD      *      September Term, 2025
                              *
                       ORDER
""",
    ),
    _S(
        id="twin-rail", name="The Twin Rail",
        columns="two-column",
        summary="a doubled, heavy vertical rule ||",
        courts="U.S. District Court, N.D. Iowa",
        tags={"columns": "two-column", "divider": "double-pipe ||", "rules": "single-line",
              "spacing": "double", "name": "caps", "status": "centered",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · disposition"},
        desc="Northern Iowa thickens the divider into a <b>twin vertical rule <code>||</code></b> "
        "running the full height of the caption; the right column stacks the "
        "docket over a centered bold disposition title. Bankruptcy variants band "
        "three consolidated captions with horizontal rules across the twin rail.",
        signal="A doubled vertical bar = N.D. Iowa; horizontal cross-rules mark "
        "stacked consolidated captions.",
        ascii=r"""
        IN THE UNITED STATES DISTRICT COURT
        FOR THE NORTHERN DISTRICT OF IOWA
                WESTERN DIVISION
   MARVIN LYNN HILDRETH, JR.,     ║   No. C23-4010-LTS
        Plaintiff,                ║
   vs.                            ║   MEMORANDUM OPINION
   CHAD SHEEHAN, et al.,          ║   AND ORDER ...
        Defendants.               ║
""",
    ),
    _S(
        id="gathering-brace", name="The Gathering Brace",
        columns="two-column",
        summary="a big curly brace } gathers the party block and points to one docket",
        courts="U.S. Courts of Appeals, 6th Cir. · 6th Cir. BAP",
        tags={"columns": "two-column", "divider": "brace }", "rules": "single-line",
              "spacing": "double", "name": "smallcaps", "status": "italic",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · file-name · appeal-from · panel"},
        desc="The Sixth Circuit's flourish: a single large <b>curly brace <code>}</code></b> embraces "
        "the entire party block and points at the lone docket number, like a "
        "hand-drawn bracket. Small-caps party names; a <code>File Name: 26a0120p.06</code> "
        "publication code rides above the banner.",
        signal="A tall <code>}</code> brace spanning the parties → 6th Cir.; the docket sits at "
        "its apex; <code>File Name:</code> code = published.",
        ascii=r"""
                File Name: 26a0120p.06
              UNITED STATES COURT OF APPEALS
                  FOR THE SIXTH CIRCUIT
                     -----------
   ALEXANDER ROSS,                      ⎫
              Plaintiff-Appellant,      ⎬
   v.                                   ⎬   No. 25-1802
   ROBINSON, HOOVER & FUDGE, PLLC,      ⎬
              Defendant-Appellee.       ⎭
""",
    ),
    _S(
        id="full-box", name="The Full Box",
        columns="two-column",
        summary="a real rectangle drawn around the party block, docket outside",
        courts="U.S. Bankruptcy Appellate Panels · Court of Int'l Trade · EDNY · D. Conn. · N.D. Okla.",
        tags={"columns": "two-column", "divider": "box edge", "rules": "single-line",
              "box": "top bottom left right", "spacing": "single", "name": "caps",
              "status": "indent", "banner": "caps centered", "glyphs": "filing-stamp",
              "extras": "docket · appeal-from · panel"},
        desc="The whole party block is fenced in a <b>drawn rectangle</b> — all four edges — "
        "often with an <b>internal horizontal rule</b> splitting an <code>In re: … Debtors.</code> "
        "sub-caption from the <code>… v. … Appellees.</code> one. The docket and disposition "
        "(<code>MEMORANDUM</code>) sit <i>outside</i> the box on the right. The CIT stacks two such "
        "boxes for consolidated cases.",
        signal="A closed rectangle: parties inside, metadata outside — split on the "
        "box's right edge; treat the inner rule as a sub-caption boundary, not a footnote rule.",
        ascii=r"""
   NOT FOR PUBLICATION                      JAN 28 2026
            UNITED STATES BANKRUPTCY APPELLATE PANEL
                     OF THE NINTH CIRCUIT
   ┌----------------------------------┐
   | In re:                           |   BAP No. CC-25-1109-CNS
   | ALEXANDER VON NEITSCH et ux.,    |
   |              Debtors.            |   Bk. No. 2:25-bk-11999-DS
   |----------------------------------|
   | ALEXANDER VON NEITSCH et ux.,    |
   |              Appellants,         |
   | v.                               |   MEMORANDUM*
   | DANIEL E. NAYSAN, D.D.S. et al., |
   |              Appellees.          |
   └----------------------------------┘
""",
    ),
    _S(
        id="double-ruled-box", name="The Double-Ruled Box",
        columns="two-column",
        summary="a party box whose top and bottom edges are double rules ==",
        courts="U.S. District Court, D.D.C.",
        tags={"columns": "two-column", "divider": "box edge", "rules": "double-line",
              "box": "top bottom left right", "spacing": "single", "name": "bold caps",
              "status": "indent", "banner": "caps centered", "glyphs": "—",
              "extras": "docket"},
        desc="D.C.'s district court draws the party box with <b>double horizontal rules</b> "
        "(<code>==</code>) top and bottom and single verticals on the sides, bold party names "
        "inside, docket outside on the right.",
        signal="A box whose top/bottom edges are doubled (and sides single) = "
        "D.D.C.; docket floats outside the right edge.",
        ascii=r"""
              UNITED STATES DISTRICT COURT
             FOR THE DISTRICT OF COLUMBIA
   ╔================================╗
   ║ UNITED STATES OF AMERICA,      ║
   ║       Plaintiff,               ║
   ║    v.                          ║   No. 20-cr-248-CKK-ZMF
   ║ HERBERT BENDER,                ║
   ║       Defendant.               ║
   ╚================================╝
            REPORT AND RECOMMENDATION
""",
    ),
    _S(
        id="l-frame", name="The L-Frame",
        columns="two-column",
        summary="a vertical rule + a bottom rule only — an open L-shaped bracket",
        courts="Washington Cts. of Appeals · N.C. Business Court",
        tags={"columns": "two-column", "divider": "box edge", "rules": "single-line",
              "box": "left bottom", "spacing": "double", "name": "caps",
              "status": "indent", "banner": "caps centered", "glyphs": "—",
              "extras": "docket · disposition"},
        desc="Half a box: a vertical rule plus a bottom rule meet at a corner, "
        "framing the parties on two sides only (no top, no right edge) — an "
        "<b>L-shaped bracket</b>. Washington stacks three consolidated captions with "
        "internal rules; North Carolina's Business Court heads the box with "
        "<code>STATE OF NORTH CAROLINA / WAKE COUNTY</code>.",
        signal="A vertical + bottom rule with open top/right = the L-frame; "
        "internal horizontal rules separate consolidated sub-captions.",
        ascii=r"""
        IN THE COURT OF APPEALS OF THE STATE OF WASHINGTON
   MICHAEL SALVO,             │   No. 87146-3-I
        Appellant,            │   DIVISION ONE
   v.                         │
   WASHINGTON CRIMINAL JUSTICE│   ORDER GRANTING
   TRAINING COMMISSION et al.,│   MOTION TO PUBLISH
        Respondents.          │
   ---------------------------┘
""",
    ),
    _S(
        id="double-box", name="The Double Box",
        columns="two-column",
        summary="parties and docket each enclosed in their own drawn box",
        courts="E.D.N.Y. and other federal districts",
        tags={"columns": "two-column", "divider": "box edge", "rules": "single-line",
              "box": "two adjacent boxes", "spacing": "single", "name": "plain",
              "status": "indent", "banner": "caps centered", "glyphs": "—",
              "extras": "docket"},
        desc="The caption is drawn as <b>two adjacent boxes</b> sharing the middle "
        "rule: parties in the left box, docket and judge initials in the right. "
        "Verticals at both content edges AND the middle, closed top and bottom.",
        signal="Three tall verticals (left edge, middle, right edge) joined by top "
        "and bottom rules = two boxes; the middle vertical is the column split.",
        ascii=r"""
                  UNITED STATES DISTRICT COURT
                 EASTERN DISTRICT OF NEW YORK
   ┌─────────────────────────────────┬──────────────────┐
   │ Bank of America, NA.,           │                  │
   │                  Plaintiffs,    │  2:26-cv-733     │
   │        -v-                      │  (NJC) (ST)      │
   │ Henry R. Terry,                 │                  │
   │                  Defendant.     │                  │
   └─────────────────────────────────┴──────────────────┘
""",
    ),
    _S(
        id="x-capped-box", name="The X-Capped Pleading Box",
        columns="two-column",
        summary="hyphen rules whose ends are capped with an X, over a colon rail",
        courts="N.Y. trial courts · D. Conn. · N.J. Tax Court",
        tags={"columns": "two-column", "divider": "colon :", "rules": "single-line",
              "box": "top bottom", "spacing": "double", "name": "caps",
              "status": "indent", "banner": "caps", "glyphs": "x-caps",
              "extras": "docket · disposition"},
        desc="The classic New York pleading caption: rows of hyphens whose right "
        "ends terminate in a capital <b><code>X</code></b> (<code>--------X</code>) fence the party block top "
        "and bottom, with a <b>colon rail</b> down the middle and <code>-against-</code> instead of "
        "<code>v.</code> Connecticut and the N.J. Tax Court borrow it.",
        signal="A <code>------X</code> terminator top and bottom = NY-style; <code>-against-</code> is the "
        "party split, docket on the right.",
        ascii=r"""
   CIVIL COURT OF THE CITY OF NEW YORK
   COUNTY OF KINGS: HOUSING PART B
   ------------------------------------X
   SURUJNARIN DHANSINGH,               :
              Petitioner,              :   Index No. L&T 324270-25
        -against-                      :   DECISION/ORDER
   JACOB HAGER, et al.,                :
              Respondents.             :
   ------------------------------------X
""",
    ),
    _S(
        id="florida-slash", name="The Florida Slash",
        columns="two-column",
        summary="the closing rule terminates in a forward slash /",
        courts="U.S. District Court, M.D. Fla. (and Florida state practice)",
        tags={"columns": "two-column", "divider": "none", "rules": "single-line",
              "box": "bottom", "spacing": "double", "name": "bold caps",
              "status": "indent", "banner": "caps centered", "glyphs": "slash",
              "extras": "docket"},
        desc="No vertical divider at all — the tell is the <b>closing rule that ends in a "
        "forward slash</b> (<code>______/</code>) under the party block, a Florida-pleading "
        "signature. The docket floats at the right with no rail. Some divisions "
        "draw the closing rule heavy.",
        signal="A bottom rule ending in <code>/</code> = Florida style; the docket is "
        "right-aligned with no divider glyph.",
        ascii=r"""
              UNITED STATES DISTRICT COURT
               MIDDLE DISTRICT OF FLORIDA
                   ORLANDO DIVISION
   KERIEKAN PALMER,
        Plaintiff,
   v.                              Case No: 6:24-cv-0989-PGB-NWH
   CITY OF DAYTONA BEACH et al.,
        Defendants.
   ___________________________/
                    ORDER
""",
    ),
    _S(
        id="pleading-slash", name="The Pleading Slash",
        columns="two-column",
        summary="a full-width underscore rule ending in a slash, e-filing stamp at right",
        courts="Supreme Court of Nevada",
        tags={"columns": "two-column", "divider": "none", "rules": "single-line",
              "box": "bottom", "spacing": "single", "name": "caps",
              "status": "indent", "banner": "caps centered", "glyphs": "filing-stamp slash",
              "extras": "docket · e-filed"},
        desc="Nevada closes its caption with a long <b>underscore rule that flips into a "
        "<code>/</code></b> at the right end (the pleading slash), and floats a plain electronic "
        "filing stamp (<code>Electronically Filed … Clerk of Supreme Court</code>) in the right "
        "column with the docket midway down.",
        signal="An <code>_______/</code> caption-closer + an <code>Electronically Filed</code> stamp = "
        "Nevada; docket sits mid-right, not on top.",
        ascii=r"""
      IN THE SUPREME COURT OF THE STATE OF NEVADA
   JULIE ENGLE,                    Electronically Filed
        Petitioner,                Apr 24 2026 04:04 PM
   vs.                             Elizabeth A. Brown
   THE SECOND JUDICIAL DISTRICT    Clerk of Supreme Court
   COURT ... ; THE HONORABLE
   DAVID HARDY,
        Respondents,
   and THE STATE OF NEVADA,        No. 89183
        Real Party In Interest.
   _______________________________/
""",
    ),
    _S(
        id="rule-sandwich", name="The Rule Sandwich",
        columns="two-column",
        summary="paired short rules sandwich the cite and the docket separately",
        courts="Supreme Court of North Dakota",
        tags={"columns": "two-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "plain", "status": "flush-right",
              "banner": "caps centered", "glyphs": "—",
              "extras": "neutral-cite · docket · appeal-from"},
        desc="North Dakota stacks <b>two separate rule-sandwiches</b>: one pair hugging the "
        "neutral cite (<code>2026 ND 72</code>), a second pair lower hugging the docket "
        "(<code>No. 20250337</code>). Party names are left, their statuses flush-right opposite.",
        signal="Two short centered rule-pairs (cite then docket) with right-flush "
        "status labels = North Dakota.",
        ascii=r"""
            IN THE SUPREME COURT
            STATE OF NORTH DAKOTA
              ________________
                 2026 ND 72
              ________________
   Jarrod Jashawn Adams,          Petitioner and Appellant
              v.
   State of North Dakota,         Respondent and Appellee
              ________________
                No. 20250337
              ________________
""",
    ),
    _S(
        id="starbreak", name="The Starbreak",
        columns="two-column",
        summary="rows of spaced asterisks * * * * band the caption into zones",
        courts="La. Cts. of Appeal · South Dakota Supreme · Ohio (Wood Cty.) · E.D. Ky.",
        tags={"columns": "two-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "caps", "status": "flush-right",
              "banner": "caps centered", "glyphs": "asterisks",
              "extras": "appeal-from · trial-judge · counsel"},
        desc="Instead of rules, rows of <b>spaced asterisks</b> (<code>* * * * *</code>) band the "
        "headmatter into zones — banner, parties, provenance, counsel. Louisiana "
        "uses <code>versus</code>; South Dakota right-flushes the statuses; Ohio brackets the "
        "counsel block; federal E.D. Ky. closes the caption with <code>*** *** *** ***</code>.",
        signal="Horizontal rows of asterisks are section dividers (not the caption "
        "end); content between them is one zone each.",
        ascii=r"""
                 IN THE SUPREME COURT
                  STATE OF SOUTH DAKOTA
                       * * * *
   SEAMUS CULHANE, TURBAK LAW
   OFFICE, P.C., et al.,          Plaintiffs and Appellees,
       v.
   BILL THOVSON,                  Defendant and Appellant.
                       * * * *
            APPEAL FROM THE CIRCUIT COURT ...
                       * * * *
""",
    ),
    _S(
        id="numbered-gutter", name="The Numbered Gutter",
        columns="two-column",
        summary="line numbers down a ruled gutter, the whole caption inside the rule",
        courts="Supreme Court of New Mexico · (California-style pleading paper)",
        tags={"columns": "two-column", "divider": "pipe |", "rules": "single-line",
              "box": "left", "spacing": "single", "name": "caps", "status": "indent",
              "banner": "caps", "glyphs": "—",
              "extras": "docket · slip-disclaimer · appeal-from"},
        desc="Pleading-paper styling: a column of <b>line numbers (1–22)</b> runs down a "
        "left gutter behind a single vertical rule, and the entire caption — court "
        "name, docket, parties — is stacked single-column to its right. New Mexico "
        "tops it with an italic slip-opinion disclaimer.",
        signal="A numbered left gutter + one vertical rule → strip the gutter "
        "numbers as furniture (don't confuse them with body numerals).",
        ascii=r"""
       The slip opinion is the first version of an opinion ...
    1 |  IN THE SUPREME COURT OF THE STATE OF NEW MEXICO
    2 |  Filing Date: May 11, 2026
    3 |  NO. S-1-SC-40636
    4 |  CITY OF LAS CRUCES,
    5 |       Appellant,
    6 |  v.
    7 |  NEW MEXICO PUBLIC REGULATION COMMISSION,
    8 |       Appellee, ...
""",
    ),
    _S(
        id="inline-docket", name="The Inline Docket",
        columns="two-column",
        summary="the docket rides inside the v. line; a right-justified author block",
        courts="Supreme Court of Virginia",
        tags={"columns": "two-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "caps", "status": "—",
              "banner": "caps", "glyphs": "—",
              "extras": "docket · author-block · panel"},
        desc="Virginia tucks the <b>record number inside the <code>v.</code> line</b> itself "
        "(<code>v. Record No. 250365</code>) rather than a right column, opens with a "
        "<code>PRESENT: All the Justices</code> panel line, and right-justifies an author block "
        "(<code>OPINION BY / JUSTICE … / date</code>).",
        signal="<code>v. Record No. …</code> on one line = Virginia; the author is the "
        "right-justified <code>OPINION BY JUSTICE …</code> block, not a byline below.",
        ascii=r"""
   PRESENT:  All the Justices

   DEMEATRIC EUGENE BLOW
                                       OPINION BY
   v.  Record No. 250365        JUSTICE JUNIUS P. FULTON, III
                                      APRIL 16, 2026
   COMMONWEALTH OF VIRGINIA

           FROM THE COURT OF APPEALS OF VIRGINIA
""",
    ),
    _S(
        id="status-flush", name="The Flush-Right Status",
        columns="two-column",
        summary="party names left, status labels pinned to the right margin, provenance centered",
        courts="Supreme Court of Kentucky & Ky. Ct. of Appeals · E.D. Ark.",
        tags={"columns": "two-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "caps", "status": "flush-right",
              "banner": "—", "glyphs": "—",
              "extras": "docket · on-review-from · disposition"},
        desc="A three-zone alignment with no glyphs: party names flush <b>left</b>, status "
        "labels (<code>APPELLANT</code>/<code>APPELLEE</code>) flush <b>right</b>, and a centered provenance "
        "block (<code>ON REVIEW FROM …</code>) floating between them on the <code>V.</code> line. Kentucky "
        "ends on an underlined disposition (<code>AFFIRMING</code>) and an asterisk flourish.",
        signal="Status words hard against the right margin with a centered "
        "provenance between the parties → Kentucky; author is <code>OPINION … BY JUSTICE …</code>.",
        ascii=r"""
                    2024-SC-0449-DG
   COMMONWEALTH OF KENTUCKY                      APPELLANT
                 ON REVIEW FROM COURT OF APPEALS
   V.                  NO. 2023-CA-0769
                    HENDERSON CIRCUIT COURT
   RUSSELL T. AMBOREE                             APPELLEE

          OPINION OF THE COURT BY JUSTICE CONLEY
                       AFFIRMING
""",
    ),
    _S(
        id="typed-sandwich", name="The Typewriter Sandwich",
        columns="two-column",
        summary="caption sandwiched between two typed dash rules, each closed with an 'x'",
        courts="E.D.N.Y. · S.D.N.Y. (and the other New York districts)",
        tags={"columns": "two-column", "divider": "none", "rules": "typed",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps left", "glyphs": "- and x",
              "extras": "docket · doc-title right · judge byline below"},
        desc="Nothing is drawn. The caption is closed above and below by a rule "
        "<i>typed</i> as a run of hyphens and terminated with a lowercase "
        "<code>x</code> — the typewriter-era stand-in for the corner of a box, which the "
        "New York districts kept when they moved to Word. The court banner sits "
        "flush left above the top rule; the doc-type title and docket ride the right "
        "of the caption; and a judge byline (<code>NAME, United States District Judge:</code>) "
        "opens the ruling immediately below the bottom rule.",
        signal="A line of hyphens ending in <code>x</code>, twice, with the parties between "
        "them. The <code>x</code> is furniture, not text — the rules render as dividers. If a "
        "<code>:</code> column also runs down the middle it is The Colon Rail instead.",
        ascii=r"""
   UNITED STATES DISTRICT COURT
   EASTERN DISTRICT OF NEW YORK
   ------------------------------------x
   JERMAINE DUNBAR,

                     Plaintiff,          MEMORANDUM & ORDER

              -against-                  22-CV-222 (EK)

   ANTHONY J. ANNUCCI,

                     Defendant.
   ------------------------------------x
   ERIC KOMITEE, United States District Judge:
""",
    ),
    _S(
        id="open-range", name="The Open Range",
        columns="two-column",
        summary="parties left, docket right, held together by whitespace alone",
        courts="W.D.N.C. (occasional) · scattered districts",
        tags={"columns": "two-column", "divider": "none", "rules": "none",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · centered heading follows"},
        desc="No line-art, no glyph rail, no flush-right pinning — just party names "
        "at the left margin, role lines indented beneath them, and the docket number "
        "floated right of mid-page on the <code>v.</code> line. The opinion usually opens with "
        "a centered bold ALL-CAPS heading right below.",
        signal="Two columns with nothing holding them apart but whitespace; the "
        "docket rides the <code>v.</code> line past mid-page. If status words were pinned at the "
        "right margin instead, it would be The Flush-Right Status.",
        ascii=r"""
            IN THE UNITED STATES DISTRICT COURT
         FOR THE WESTERN DISTRICT OF NORTH CAROLINA

   NAYJA JOHNSON,

             Plaintiff,

   v.                    CIVIL ACTION NO. 3:24-cv-00334-TEJ

   ERIC TILLMAN, et al.,

             Defendants.

               MEMORANDUM OPINION AND ORDER
""",
    ),
    _S(
        id="boxed-notice", name="The Boxed Publication Notice",
        columns="two-column",
        summary="a small drawn box quarantines an APPROVED FOR PUBLICATION stamp",
        courts="Superior Court of New Jersey, Appellate Division",
        tags={"columns": "two-column", "divider": "none", "rules": "single-line",
              "box": "top bottom left right", "spacing": "double", "name": "caps",
              "status": "indent", "banner": "caps", "glyphs": "—",
              "extras": "docket · submitted/decided"},
        desc="New Jersey leaves the caption rule-light but draws a tidy little "
        "<b>rectangle around an <code>APPROVED FOR PUBLICATION</code></b> notice floating in the right "
        "column, with a short underscore rule closing the party block on the left.",
        signal="A small 4-edge box containing only <code>APPROVED FOR PUBLICATION</code> = NJ "
        "App. Div.; it's a stamp, not part of the caption columns.",
        ascii=r"""
                          SUPERIOR COURT OF NEW JERSEY
                          APPELLATE DIVISION
                          DOCKET NO.  A-2974-24
   DELLA M. BOURNES,
        Plaintiff-Respondent,
                              ┌------------------------┐
   v.                         | APPROVED FOR PUBLICATION|
                              |      April 30, 2026     |
   SHAWN J. HARRIS,           |   APPELLATE DIVISION    |
        Defendant-Appellant.  └------------------------┘
   ___________________________
""",
    ),
    _S(
        id="michigan-masthead", name="The Letter-Spaced Masthead",
        columns="two-column",
        summary="a tracked-out S T A T E  O F  banner; docket floats opposite a bare v",
        courts="Michigan Supreme Court",
        tags={"columns": "two-column", "divider": "none", "rules": "single-line",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "letter-spaced centered", "glyphs": "filing-stamp",
              "extras": "docket · justice-roster"},
        desc="Michigan tracks out its banner into <code>S T A T E   O F   M I C H I G A N</code>, "
        "uses a bare single-letter <code>v</code> (no period) as the versus token, floats the "
        "docket in a right column opposite it, and closes with one rule before "
        "<code>BEFORE THE ENTIRE BENCH</code>. A justice roster + <code>FILED</code> stamp form a separate masthead.",
        signal="A letter-spaced state-name banner + bare <code>v</code> + right-floated docket "
        "→ Michigan; the roster/FILED block above is page furniture.",
        ascii=r"""
              S T A T E   O F   M I C H I G A N
                       SUPREME COURT
   CARLONDA NAISHE SWOOPE,
           Plaintiff-Appellant,
   v                                        No. 166790
   CITIZENS INSURANCE COMPANY OF THE MIDWEST,
              Defendant-Appellee.
   -------------------------------------------
   BEFORE THE ENTIRE BENCH
""",
    ),

    _S(
        id="dashed-realignment", name="The Dashed Realignment",
        columns="two-column",
        summary="a vertical rule, plus a dashed in-column rule that breaks off realigned parties",
        courts="U.S. Courts of Appeals — 10th Cir. · D.C. Cir.",
        tags={"columns": "two-column", "divider": "pipe |", "rules": "single-line",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps centered", "glyphs": "—",
              "extras": "docket · intervenor-break · panel"},
        desc="Same single vertical rule as Old Faithful, but with a <b>dashed horizontal "
        "rule</b> (<code>- - - - -</code>) <i>inside</i> the party column that splits off a realigned "
        "group — intervenors, a consolidated case — from the main parties. The "
        "D.C. Circuit uses the dashes to fence Appellee from Intervenors and from "
        "a <code>Consolidated with …</code> line; a clerk name rides the top-right corner.",
        signal="A dashed (not solid) in-column rule = a party-group break, not the "
        "caption end; everything below it is a separate realignment/intervenor block.",
        ascii=r"""
                                  Christopher M. Wolpert
              FOR THE TENTH CIRCUIT    Clerk of Court
   ---------------------------------------------------
   CITIZENS FOR CONSTITUTIONAL    │
   INTEGRITY; et al.,             │
        Plaintiffs - Appellants,  │       No. 25-1006
   v.                             │
   THE OFFICE OF SURFACE MINING   │
   ... et al.,                    │
        Defendants - Appellees.   │
   - - - - - - - - - - - - - - -  │
   GCC ENERGY, LLC,               │
        Intervenor - Appellee.    │
""",
    ),
    _S(
        id="mixed-rail", name="The Mixed Rail",
        columns="two-column",
        summary="one divider glyph down the side, a different glyph row to close it",
        courts="U.S. District Court, E.D. Ky. (and kin)",
        tags={"columns": "two-column", "divider": "parens )", "rules": "rule-bands",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps centered", "glyphs": "asterisks",
              "extras": "docket · disposition"},
        desc="Some courts mix their punctuation: a <code>)</code> rail runs down the side as the "
        "column divider, then a <b>row of grouped asterisks</b> (<code>*** *** *** ***</code>) — a "
        "different glyph entirely — closes the caption off before the body. One "
        "tell for the gutter, another for the bottom.",
        signal="When the vertical divider glyph and the horizontal closer glyph "
        "differ, treat them independently — the rail splits columns, the asterisk row ends the caption.",
        ascii=r"""
            UNITED STATES DISTRICT COURT
            EASTERN DISTRICT OF KENTUCKY
                  at Covington
   CELLMARK, INC.,            )
        Plaintiff,            )  Civil Action No. 2:24-cv-00181-SCM
   v.                         )
   ROBERT WEBSTER, et al.,    )    MEMORANDUM OPINION
        Defendants.           )         AND ORDER
              ***   ***   ***   ***
""",
    ),

    _S(
        id="termed-masthead", name="The Termed Masthead",
        columns="two-column",
        summary="a vertical rule, a neutral cite up top, and a sitting-term + date stacked over a short right rule",
        courts="Supreme Court of Wyoming",
        tags={"columns": "two-column", "divider": "pipe |", "rules": "rule-bands",
              "spacing": "double", "name": "caps", "status": "indent",
              "banner": "caps centered", "glyphs": "—",
              "extras": "neutral-cite · term · docket · appeal-from"},
        desc="Wyoming hangs a vendor-neutral cite (<code>2026 WY 51</code>) under the banner, then "
        "stacks the sitting term and decision date (<code>APRIL TERM, A.D. 2026 / May 6, 2026</code>) "
        "over a <b>short right-hand rule</b>, with a single vertical rule down to a lone "
        "docket. Each appellate status also carries its <b>parenthetical trial role</b> "
        "(<code>Appellant / (Defendant)</code>).",
        signal="Neutral cite + a term/date block over a short rule on the right + "
        "parenthetical <code>(Defendant)</code>/<code>(Plaintiff)</code> roles = Wyoming.",
        ascii=r"""
            THE SUPREME COURT, STATE OF WYOMING
                       2026 WY 51
                              APRIL TERM, A.D. 2026
                                  May 6, 2026
                              -----------------
   ANDREW ATKINSON,              │
   Appellant                     │
   (Defendant),                  │       S-25-0216
   v.                            │
   THE STATE OF WYOMING,         │
   Appellee                      │
   (Plaintiff).                  │
        Appeal from the District Court of Goshen County
""",
    ),

    _S(
        id="right-hand-rules", name="The Right-Hand Rules",
        columns="two-column",
        summary="short rules pushed to the right margin, bracketing the cite and the appeal-from",
        courts="Supreme Court of Montana",
        tags={"columns": "two-column", "divider": "none", "rules": "rule-bands",
              "spacing": "double", "name": "caps", "status": "centered",
              "banner": "caps centered", "glyphs": "—",
              "extras": "neutral-cite · appeal-from"},
        desc="Montana's quirk: the bracketing rules are <b>short and pushed to the right "
        "margin</b> — “lines on the wrong side” — one over the neutral cite "
        "(<code>2026 MT 162</code>), one under the party block above a tabbed "
        "<code>APPEAL FROM:</code> block. No vertical divider; the parties sit centered-left.",
        signal="Short rules hugging the RIGHT margin (not centered or full-width) + "
        "a neutral <code>20xx MT n</code> cite = Montana.",
        ascii=r"""
                              2026 MT 162
                          -----------------
   BMK ENTERPRISES, INC.,
            Plaintiff and Appellant,
       v.
   BAILEY ENTERPRISES OF MONTANA, LLC, et al.,
            Defendants and Appellees.
                          -----------------
   APPEAL FROM:  District Court of the Eighteenth Judicial
                 District, ... Gallatin, Cause No. DV-22-254
""",
    ),
    _S(
        id="red-letter-date", name="The Red-Letter Date",
        columns="two-column",
        summary="a )-rail and seal, with the opinion-issued date printed in red",
        courts="Supreme Court of Missouri (en banc)",
        tags={"columns": "two-column", "divider": "parens )", "rules": "none",
              "spacing": "double", "name": "caps", "status": "centered",
              "banner": "caps centered", "glyphs": "seal",
              "extras": "docket · appeal-from · color"},
        desc="Missouri runs a <code>)</code> rail under a centered seal and <code>SUPREME COURT OF "
        "MISSOURI / en banc</code> banner — but the tell is <b>color</b>: the "
        "<code>Opinion issued July 22, 2025</code> line is printed in <b>red italic</b>, the only "
        "splash of color in the whole corpus.",
        signal="A red-inked <code>Opinion issued …</code> date (a non-black fill on the chars) "
        "next to a <code>)</code> rail and an <code>en banc</code> line = Missouri.",
        ascii=r"""
                       (seal)
              SUPREME COURT OF MISSOURI
                       en banc
   C.S.,                          )   Opinion issued July 22, 2025
        Appellant,                )       (printed in red)
   v.                             )   No. SC100944
   MISSOURI STATE HIGHWAY PATROL  )
   ... ; LAFAYETTE PROSECUTING    )
   ATTORNEY,                      )
        Respondents.              )
   APPEAL FROM THE CIRCUIT COURT OF LAFAYETTE COUNTY
""",
    ),
    _S(
        id="horizontal-frame", name="The Horizontal Frame",
        columns="two-column",
        summary="no vertical rail — two full-width rules frame the caption, county set off right",
        courts="New York State Supreme Court (trial term)",
        tags={"columns": "two-column", "divider": "none", "rules": "rule-bands",
              "box": "top bottom", "spacing": "double", "name": "caps",
              "status": "indent", "banner": "caps", "glyphs": "—",
              "extras": "index-no · rji · disposition"},
        desc="New York's trial-term style frames the caption between two <b>full-width "
        "horizontal rules</b> with <b>no vertical rail at all</b> — parties left, "
        "<code>DECISION AND ORDER</code> + <code>Index No.</code> floating in the right gutter. The "
        "<code>COUNTY OF …</code> is set off to the right of <code>SUPREME COURT</code> in the banner.",
        signal="Two full-width rules and a whitespace gutter (no <code>)</code>/<code>:</code>/rule) with "
        "<code>Index No.</code> on the right = NY trial term; <code>vs.</code>/<code>-against-</code> splits the parties.",
        ascii=r"""
   STATE OF NEW YORK
   SUPREME COURT              COUNTY OF ONTARIO
   __________________________________________
   PNC BANK, NATIONAL ASSOCIATION,
                       Plaintiff,
                                    DECISION AND ORDER
          vs.                         (Motions # 2 and 3)
                                    Index No. 139717-2024
   CHRISTOPHER GRIFFITH ... ET. AL.,
                       Defendants.
   __________________________________________
""",
    ),
    _S(
        id="keyed-author", name="The Keyed Author",
        columns="two-column",
        summary="the authoring justice is keyed to the top-right corner of the caption",
        courts="Minnesota Supreme Court / Court of Appeals",
        tags={"columns": "two-column", "divider": "none", "rules": "underline",
              "spacing": "double", "name": "plain", "status": "centered",
              "banner": "—", "glyphs": "—",
              "extras": "docket · county · author · filed"},
        desc="Minnesota skips a banner and keys the <b>authoring justice to the top-right</b> "
        "(<code>Thissen, J.</code>) on the same line as the county of origin, with "
        "<code>Filed: …</code> and <code>Office of Appellate Courts</code> below it. A short centered "
        "underscore rule divides the caption from the counsel line.",
        signal="A lone justice surname keyed top-right (<code>Name, J.</code>) opposite a county "
        "line, no banner = Minnesota; that's the author, not a party.",
        ascii=r"""
                          A23-1274
   Ramsey County                              Thissen, J.

   Andrew Vernard Glover,
                     Appellant,
   vs.                                  Filed: April 1, 2026
                                        Office of Appellate Courts
   State of Minnesota,
                     Respondent.
                   ________________
""",
    ),

    # ========================================================== THREE COLUMN
    _S(
        id="three-cell-ledger", name="The Three-Cell Ledger",
        columns="three-column",
        summary="a full ruled table: parties | a docket channel | court-of-origin",
        courts="Puerto Rico — Tribunal de Apelaciones / Tribunal Supremo",
        tags={"columns": "three-column", "divider": "box edge", "rules": "single-line",
              "box": "top bottom left right", "spacing": "double", "name": "bold caps",
              "status": "centered", "banner": "caps centered", "glyphs": "—",
              "extras": "docket · court-of-origin · panel"},
        desc="Puerto Rico draws a genuine <b>three-cell table</b>: the parties "
        "(<i>Recurrido</i>/<i>Peticionario</i>) in the left cell, a narrow center channel "
        "holding just the docket (vertically centered), and the court of origin "
        "(<code>procedente del Tribunal de Primera Instancia…</code>, <code>Sobre:</code> the subject) in "
        "the right cell — all in Spanish, the whole thing boxed.",
        signal="Three boxed columns with the docket isolated in a middle channel "
        "→ Puerto Rico; split on the two interior verticals, Spanish role labels.",
        ascii=r"""
   ┌----------------------┬-----------┬----------------------┐
   |   ESTADO LIBRE ASOCIADO DE PUERTO RICO                       |
   |        TRIBUNAL DE APELACIONES - PANEL II                    |
   |----------------------┼-----------┼----------------------|
   | ANDRES ANTONIO        |           | CERTIORARI           |
   | TORRES MATOS y otros  |           | procedente del       |
   |     Recurrido         |TA2026CE003| Tribunal de Primera  |
   |     v.                |           | Instancia, Sala ...  |
   | GEOVANNIE MORALES     |           | Civil Num.:          |
   | CINTRON               |           | CR2021CV00297        |
   |     Peticionario      |           | Sobre: Servidumbre   |
   └----------------------┴-----------┴----------------------┘
""",
    ),
]

# Strip the leading newline each ascii block starts with.
for _s in STYLES:
    _s["ascii"] = _s["ascii"].strip("\n")
