"""United States District Court, Northern District of Mississippi ('msnd').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads 80% of a five-record sample with
the default facts. The rest are UNREAD and this file is not finished:
what they are has not been measured yet.

Facts this court measures differently from the shared defaults are declared
below. Nothing is inherited: this file imports core and never another court
file, and no other court file imports it.
"""

from __future__ import annotations

from ..districts import EcfPaper, read_ecf
from ..districts.ecf import TITLE_OPENERS, TITLE_WORDS
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import decider
from . import register

MSND = register(CourtProfile(
    "msnd", "United States District Court, Northern District of Mississippi",
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

# THE WORD THIS COURT QUALIFIES ITS JUDGMENT WITH. The shared vocabulary
# knows 'JUDGMENT' and not 'FINAL JUDGMENT', so on msnd/52361.17.0 — a
# one-page judgment whose whole text is three sentences — no row could close
# the caption band: it ran to the band's ceiling and swallowed the title, the
# body AND the signature into the caption (the user, 2026-08-23: 'this one
# parses headmatter badly'). 'final' names no case and no party; like
# 'amended' and 'corrected' it only ever qualifies the court's own paper.
PAPER = EcfPaper(title_words=TITLE_WORDS + ("final",),
                 title_openers=TITLE_OPENERS + ("final",))


@decider("headmatter.read", court="msnd")
def read_headmatter_msnd(model, geom, **kw):
    """Read msnd's ECF pleading order, or NOTHING."""
    return read_ecf(model, geom, PAPER, **kw)
