"""Shared base for state intermediate appellate courts.

These parse much like the state supreme courts — an author byline opens each
opinion — but with two differences this base handles:

  * the title is usually a *Judge* ('STROUD, Judge.' / 'NAME, P.J.' / 'NAME,
    J.') rather than a Justice, so the abbreviated-title parser is reused and
    the spelled-out 'Judge' titles are added to ``author_titles`` for the
    base byline grammar; and
  * the caption is thick with non-author byline-shaped lines — the trial judge
    appealed from ('The Honorable NAME, Judge' / 'Hon. NAME, District Judge')
    and the panel that heard the case ('Before NAME, P.J., ... JJ.' / 'Present:
    NAME, ... JJ.'). The state-supreme base already drops the 'the honorable' /
    'hon.' / 'before' / 'appeal from' families and any 'District/Circuit/
    Superior Court Judge'; this base adds 'present' to that list.

Per-court subclasses set the court label and, where a court's byline differs
(reversed 'JUSTICE X delivered ...', 'Opinion by NAME, J.', a signature block),
use the matching base instead. No regex beyond the shared byline grammar.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class StateAppellate(AbbrevTitleSupreme):
    # Judge titles first (most appellate authors are Judges); Justice kept for
    # the courts that style their members Justices.
    author_titles = (
        "Chief Judge",
        "Presiding Judge",
        "Associate Judge",
        "Senior Judge",
        "Chief Justice",
        "Presiding Justice",
        "Associate Justice",
        "Senior Justice",
        "Judge",
        "Justice",
    )
