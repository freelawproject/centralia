"""United States District Court, District of Colorado ('cod').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads every sampled record of this
corpus with the default facts, so this file declares the court and
nothing else — the expected shape of a district court file.

Facts this court measures differently from the shared defaults are declared
below. Nothing is inherited: this file imports core and never another court
file, and no other court file imports it.
"""

from __future__ import annotations

from ..districts import EcfPaper, read_ecf
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import decider
from . import register

COD = register(CourtProfile(
    "cod", "United States District Court, District of Colorado",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # A district judge signs in the reversed form — the name over the office
    # ('EMILY C. MARKS' / 'UNITED STATES DISTRICT JUDGE').
    #
    # …AND THIS COURT ALSO ANNOUNCES THE JUDGE IN ITS MASTHEAD, in the same
    # reversed order but with the office SHORT and the name in titlecase:
    # 'District Judge S. Kato Crews', 'Magistrate Judge N. Reid Neureiter'.
    # 18 of the 22 records print such a row and all 22 reached the end of the
    # pipeline with no author on the lead writing, because the declared
    # titles all begin 'United States' and the declared name had to be
    # capitals. Both forms are the same grammar; only the spellings differ.
    byline=BylineGrammar(style="reversed",
                         allow_titlecase_name=True,
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge",
                                     "Chief District Judge",
                                     "Senior District Judge",
                                     "District Judge",
                                     "Magistrate Judge",
                                     "Chief Judge",
                                     "Judge")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="cod")
def read_headmatter_cod(model, geom, **kw):
    """Read cod's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
