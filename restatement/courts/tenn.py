"""Supreme Court of Tennessee.

The opinion byline is the prose authorship line, not bold:
  'DWIGHT E. TARWATER, J., delivered the opinion of the Court, in which
   JEFFREY S. BIVINS, C.J., ... joined.'
There is no separate short byline, so ``accept_delivered`` turns this
'NAME, J., delivered ...' form into the opinion start (the all-caps name leads,
the abbreviated title and an opinion verb follow). A bold 'No. 20C2503 Thomas
W. Brothers, Judge' line is the trial-court judge from the case history (its
name is title-case), and the end-of-opinion signature 'DWIGHT E. TARWATER,
JUSTICE' is a sign-off with no body after it — neither is an opinion start.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class TennesseeSupreme(AbbrevTitleSupreme):
    court_id = "tenn"
    court_label = "Supreme Court of Tennessee."
    accept_delivered = True
