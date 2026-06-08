"""Supreme Court of Vermont.

Byline opens the first numbered paragraph: '¶ 1. EATON, J. Seventeen Burlington
...' / '¶ 1. REIBER, C.J. This appeal ...', with the opinion text inline after
the abbreviated title. Separate writings are numbered likewise ('¶ 50.
ROBINSON, J., concurring.'). The shared abbreviated-title base handles the
'NAME, J.' grammar once the leading '¶ N.' paragraph marker is stripped (kept
in the byline text). A trial-judge line ('Robert R. Bent, J. (Ret.)') is
title-case and a 'PRESENT: Reiber, C.J., ...' panel roster is not a clean
surname — neither is an opinion start.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class VermontSupreme(AbbrevTitleSupreme):
    court_id = "vt"
    court_label = "Supreme Court of Vermont."
    strip_para_marker = True
