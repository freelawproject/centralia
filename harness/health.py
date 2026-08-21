"""The per-file health vector and the corpus census.

Seven integers tell you at a glance whether a document parsed sanely:
(pages, opinions, body_words, footnotes, residual_content, dropped, warnings).
The census rolls them up per court and adds the sprawl monitor: how many
evidence providers each court registers (soft cap 3).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Health:
    pages: int
    opinions: int
    body_words: int
    footnotes: int
    residual_content: int
    dropped: int
    warnings: int

    def row(self) -> tuple[int, ...]:
        return (self.pages, self.opinions, self.body_words, self.footnotes,
                self.residual_content, self.dropped, self.warnings)


COLUMNS = ("pages", "opinions", "body_words", "footnotes",
           "residual_content", "dropped", "warnings")
