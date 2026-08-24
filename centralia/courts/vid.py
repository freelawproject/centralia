"""United States District Court, District of the Virgin Islands ('vid').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED on this corpus (10 records): the shared reader reads all ten of them
with the default facts. This file declares the court and its signing
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

VID = register(CourtProfile(
    "vid", "United States District Court, District of the Virgin Islands",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # MEASURED: none of the 10 records prints a byline at all and 9 sign over the
    # office — this court signs, it does not byline.
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge",
                                     "Judge of the District Court")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="vid")
def read_headmatter_vid(model, geom, **kw):
    """Read vid's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
