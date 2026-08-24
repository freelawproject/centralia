"""The federal district lane's shared reading.

89 district corpora are not 89 papers: they are ONE paper — the CM/ECF
pleading order — with a handful of dividers. This package holds that paper.
It is CORE, not a court file: a district court file may import it (the
per-court-file rule forbids importing another COURT file, never core), and
nothing outside `centralia/courts/<district>.py` reaches it.

See `notes/district-rollout.md`.
"""

from .ecf import (STYLE_DRAWN_RAIL, STYLE_FLUSH_STATUS, STYLE_GLYPH_RAIL,
                  EcfPaper, read_ecf)

__all__ = ["EcfPaper", "read_ecf", "STYLE_GLYPH_RAIL", "STYLE_DRAWN_RAIL",
           "STYLE_FLUSH_STATUS"]
