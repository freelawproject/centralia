"""United States District Court, District of Oregon ('ord').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads NONE of a five-record sample. This
court's paper has not been read yet — the registration is here so the
court is wired and measurable, not because it is done.

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

ORD = register(CourtProfile(
    "ord", "United States District Court, District of Oregon",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # A district judge signs in the reversed form — the name over the office
    # ('EMILY C. MARKS' / 'UNITED STATES DISTRICT JUDGE').
    # …AND IT ALSO SIGNS IN PROSE, which is the only form this court's
    # records actually print at the head of the writing: 'CLARKE, United
    # States Magistrate Judge.' Measured over all 36 of ord's records, EIGHT
    # sign that way and NOT ONE signs in the reversed form declared here —
    # so the magistrate's own byline was body prose, the writing opened on
    # it with no author, and an unsigned head types 'order' however the
    # paper is titled ('OPINION AND ORDER'). The reversed form is kept: it
    # costs nothing, and the conformed '/s/' sign-off the other records
    # carry is read elsewhere.
    byline=BylineGrammar(style="reversed",
                         also_prose=True,
                         titles=("United States District Judge",
                                 "United States Magistrate Judge",
                                 "Senior United States District Judge",
                                 "Chief United States District Judge"),
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="ord")
def read_headmatter_ord(model, geom, **kw):
    """Read ord's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
