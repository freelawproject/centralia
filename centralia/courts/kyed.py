"""United States District Court for the Eastern District of Kentucky ('kyed').

Everything unique to kyed lives here. It imports core, never another court
file, and no other court file imports it.

THE CONTRACT — 'the ECF pleading order', which is `centralia.districts.ecf`
and is shared with the other 88 district corpora. kyed was the court it was
read off: its 25 records are three templates, and they are the SAME PAPER with
three different caption dividers (glyph rail 7, drawn rail 6, flush-right
status 12). The paper, the walk and the vocabularies are documented there.

kyed measures no differently from the shared defaults — every number in
`EcfPaper` was taken off these 25 records — so this file declares the court
and nothing else. THAT IS THE EXPECTED SHAPE of a district court file: in the
old engine 56 of 89 districts needed no more than a label. A number belongs
here only when kyed's own pages disagree with the default.
"""

from __future__ import annotations

from ..districts import EcfPaper, read_ecf
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import decider
from . import register

KYED = register(CourtProfile(
    "kyed", "United States District Court for the Eastern District of Kentucky",
    # District judges sign in the reversed form where they sign at all
    # ('RICHARD L. BOURGEOIS, JR. / UNITED STATES MAGISTRATE JUDGE'). No
    # record in this corpus does; the grammar is declared so that one which
    # does is read rather than missed.
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

# kyed's declared facts: the shared measurements, unchanged. The district's
# own line carries a typo on part of the corpus ('EASTEN DISTRICT OF
# KENTUCKY'), which is why the masthead is recognised on 'DISTRICT COURT'
# alone — the shared default, and the reason it is the default.
PAPER = EcfPaper()


@decider("headmatter.read", court="kyed")
def read_headmatter_kyed(model, geom, **kw):
    """Read kyed's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
