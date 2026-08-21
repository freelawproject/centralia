"""Named layout contracts (document styles) — the CA2 lesson generalized.

A DocStyle is a landmark-driven contract for one printed format a court
publishes ("stated-term order", "engraved ladder", "pleading-paper"). It
carries DATA (landmark declarations, expectations) and one matcher over the
PdfModel — never arbitrary pipeline code. Courts LIST the styles they
publish in their profile; the classifier picks the best-matching declared
style per document. Styles fill in as courts roll out; "generic" always
matches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .pdfio.model import PdfModel


@dataclass(frozen=True)
class DocStyle:
    id: str
    name: str
    match: Callable[[PdfModel, dict], float]   # (model, caption_sig) -> score 0..1
    # Expectations resolvers may consult (all optional):
    expects: dict = field(default_factory=dict)
    # e.g. {"caption": "parenthetical-box", "rules_trustworthy": False,
    #       "masthead_by_size": True, "no_footnote_rule": True}


_REGISTRY: dict[str, DocStyle] = {}


def register(style: DocStyle) -> DocStyle:
    if style.id in _REGISTRY:
        raise ValueError(f"duplicate style id {style.id!r}")
    _REGISTRY[style.id] = style
    return style


def get(style_id: str) -> DocStyle:
    return _REGISTRY[style_id]


def pick(model: PdfModel, caption_sig: dict, declared: tuple[str, ...]) -> str:
    """Best-matching declared style for THIS document."""
    best, best_score = "generic", -1.0
    for sid in declared:
        style = _REGISTRY[sid]
        score = style.match(model, caption_sig)
        if score > best_score:
            best, best_score = sid, score
    return best


register(DocStyle("generic", "Generic", lambda m, sig: 0.1))
