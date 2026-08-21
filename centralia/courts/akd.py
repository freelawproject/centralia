"""United States District Court, District of Alaska ('akd').

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

AKD = register(CourtProfile(
    "akd", "United States District Court, District of Alaska",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # MEASURED before this file existed, and kept: akd's orders are
    # UNSIGNED — they carry a '/s/' signature and no byline at all.
    byline=BylineGrammar(style="none"),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="akd")
def read_headmatter_akd(model, geom, **kw):
    """Read akd's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
