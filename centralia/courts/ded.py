"""United States District Court, District of Delaware ('ded').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads 60% of a five-record sample with
the default facts. The rest are UNREAD and this file is not finished:
what they are has not been measured yet.

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

DED = register(CourtProfile(
    "ded", "United States District Court, District of Delaware",
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


@decider("headmatter.read", court="ded")
def read_headmatter_ded(model, geom, **kw):
    """Read ded's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
