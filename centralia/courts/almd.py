"""United States District Court for the Middle District of Alabama ('almd').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, shared with
the other district corpora. almd is the second court read off it, and the
first witness for the GLYPH RAIL family (33 of the 89 district corpora).

Facts measured on this corpus are declared below; everything else is the
shared default.
"""

from __future__ import annotations

from ..districts import EcfPaper, read_ecf
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import decider
from . import register

ALMD = register(CourtProfile(
    "almd", "United States District Court for the Middle District of Alabama",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

PAPER = EcfPaper()


@decider("headmatter.read", court="almd")
def read_headmatter_almd(model, geom, **kw):
    """Read almd's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
