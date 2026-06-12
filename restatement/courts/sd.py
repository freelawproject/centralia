"""Supreme Court of South Dakota.

Byline is a plain (non-bold) ALL-CAPS surname over the full title word —
'KERN, Retired Justice' / 'SALTER, Justice' / 'JENSEN, Chief Justice' — at
the top of the opinion, above '[¶1.]'-numbered paragraphs. The cover page
carries the docket-and-disposition header ('#30782-aff in pt & rev in
pt-JMK', the authoring justice's initials trailing), the 'IN THE SUPREME
COURT / OF THE / STATE OF SOUTH DAKOTA' banner, '* * * *' rails, the parties,
the 'APPEAL FROM …' history, the trial judge, and counsel — all headmatter.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class SouthDakotaSupreme(StateSupreme):
    court_id = "sd"
    court_label = "Supreme Court of South Dakota."
