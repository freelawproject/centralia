"""CourtProfile: data-only court FACTS. Frozen — unknown fields are a
construction error, so the old 111-knob / 25-declaration-site sprawl cannot
recur. Courts contribute a profile, a list of published document styles, and
(rarely) registered evidence providers. Never code, never a pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .resolve.bylines import BylineGrammar
from .resolve.footnotes import FootnoteConfig


@dataclass(frozen=True)
class CourtProfile:
    court_id: str
    court_label: str
    styles: tuple[str, ...] = ("generic",)
    byline: BylineGrammar = field(default_factory=BylineGrammar)
    footnotes: FootnoteConfig = field(default_factory=FootnoteConfig)
    fold_page_numbers: bool = False
    # What the court prints BEFORE the opinion, declared — not inferred.
    # 'syllabus': a formal, court-published syllabus (scotus, conn, nj,
    # mich). 'summary': a staff summary that is not part of the opinion
    # (ca9). 'none' (default): the court prints neither, so front prose is
    # the body and any section built from it would be invented.
    front_matter: tuple[str, ...] = ()
    # PARAGRAPH INDENT: how far a first line must leave its flow's runover
    # edge to open a paragraph. A fact of the court's typesetting, not a
    # threshold to tune — half-inch reporters indent ~28pt, scotus 8-11pt,
    # conn ~10pt. Twice this is the BLOCK-QUOTATION fence: a run set out
    # that far is a quotation, and its first line is not a new paragraph.
    para_indent_min: float = 12.0
    # CAPTION WRAPS: does this court set caption statements that RUN ON to
    # the next line? Where it does, a row is joined to the one above it by
    # GEOMETRY alone — same type size, leading tighter than 1.5x that size.
    # scotus wraps at 1.22-1.23x and stands its next element off at 1.9x, so
    # the page separates the two without a single word being read. Declared
    # per court because a label GRID ('Argued:' over 'Decided:') sets rows
    # at the same size and leading and means something else entirely.
    caption_wraps: bool = False
    # COUNSEL AFTER THE WRITINGS: does this court print its appearance
    # roster BELOW the opinions (ca3's order form) rather than in the
    # headmatter? Default False, and the default is load-bearing: it is the
    # only condition under which any pass may take content back OUT of an
    # assembled writing. Everywhere else, text inside an opinion stays in
    # that opinion — a roster heuristic reaching into a writing deleted a
    # paragraph of a scotus concurrence that merely CITED 'Brief for
    # Respondent 26.'
    counsel_after_writings: bool = False
    # ONE PAPER, ONE WRITING. A federal district court is a single judge
    # ruling: there is no panel, so there is nothing to concur in or dissent
    # from, and a district record that comes back with two writings has been
    # SPLIT, not read. Measured on gamd, where 10 of 31 records came back as
    # two writings by the same judge, broken at the court's own 'ANALYSIS'
    # heading. Default False and the default is load-bearing — every
    # appellate court in this corpus genuinely prints several writings, and
    # folding theirs together would destroy the separate opinions.
    single_writing: bool = False
    # Rollout state: pending | migrated | blocked (the census reports it).
    rollout: str = "pending"
