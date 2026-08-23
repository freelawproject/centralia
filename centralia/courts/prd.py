"""United States District Court, District of Puerto Rico ('prd').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED on this corpus (10 records): the shared reader reads nine of them
with the default facts, and refuses one — see the notes. This file declares the court and its signing
form and nothing else — the expected shape of a district court file.

A TERRITORIAL DISTRICT IS A FEDERAL DISTRICT COURT. Guam, Puerto Rico and the
Virgin Islands each have an Article IV district court that files on CM/ECF
exactly as the fifty states' districts do; the territory's OWN courts
(`virginislands`, `prapp`, `prsupreme`) are a different corpus entirely.

Nothing is inherited: this file imports core and never another court file,
and no other court file imports it.
"""

from __future__ import annotations

from ..districts import EcfPaper, read_ecf
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import decider
from . import register

PRD = register(CourtProfile(
    "prd", "United States District Court, District of Puerto Rico",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # MEASURED: 2 of the 10 records print a byline-shaped row and 5 sign over the
    # office, so the reversed signing form is what this court uses.
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge",
                                     "Judge of the District Court")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="prd")
def read_headmatter_prd(model, geom, **kw):
    """Read prd's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
