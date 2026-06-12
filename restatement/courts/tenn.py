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
from ._tennessee import (
    TennesseeBlockquotes,
    TennesseeFurnitureDrop,
    TennesseeHeadmatter,
    _strip_inline,
)


class TennesseeSupreme(
    TennesseeHeadmatter, TennesseeBlockquotes, TennesseeFurnitureDrop, AbbrevTitleSupreme
):
    court_id = "tenn"
    court_label = "Supreme Court of Tennessee."
    accept_delivered = True

    def build_opinion(self, op_start, op_end, **kw):
        op = super().build_opinion(op_start, op_end, **kw)
        # A byline that wraps ('HOLLY KIRBY, J., with whom ..., joins,
        # concurring in part and / dissenting in part.') strands its tail as
        # the first body paragraph — a short lowercase kind fragment. Fold it
        # back into the byline and let the opinion type see the full clause.
        if op.blocks and op.blocks[0].kind == "p":
            t = _strip_inline(op.blocks[0].text).strip()
            low = t.lower()
            if (
                t[:1].islower()
                and len(t) <= 60
                and any(k in low for k in ("concur", "dissent", "join"))
            ):
                op.author = op.author.rstrip() + " " + t
                op.blocks.pop(0)
                op.type = self.normalize_opinion_type(op.author)
        return op
