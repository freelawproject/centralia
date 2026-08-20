"""United States District Court, District of Columbia ('dcd').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED on 32 records. dcd's papers do NOT come from PACER — they
carry no CM/ECF overlay at all, which is why the corpus census that
keyed on the 'gov.uscourts.' filename missed this court entirely. The
paper underneath is the same one: a centred masthead, an undrawn
caption, and the title standing alone as the closer.

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

DCD = register(CourtProfile(
    "dcd", "United States District Court, District of Columbia",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # A district judge signs in the reversed form — the name over the office
    # ('EMILY C. MARKS' / 'UNITED STATES DISTRICT JUDGE').
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="dcd")
def read_headmatter_dcd(model, geom, **kw):
    """Read dcd's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
