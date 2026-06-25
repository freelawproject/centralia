"""Supreme Court of Alabama.

The Alabama appellate template (caption parser, doc-type classifier, docket
matcher) lives on the shared ``AlabamaAppellate`` base. The Supreme Court
differs only in its docket prefix (``SC``), author title (``Justice``), and
the ``<court>`` label.

Layout cheatsheet:
  - Footnote separator: hairline rect at exactly x0=72, x1=216.
  - Page 1: 'Rel: <date>' -> notice advisory -> centered bold court banner ->
    'OCTOBER TERM, YYYY-YYYY' -> ____ -> <docket> -> ____ -> <case name> ->
    <motion / 'Appeal from'> -> <lower court>.
  - Body opens with an author line: 'LASTNAME, Justice[ (kind)].'.
  - Document styles: OPINIONS and NO-OPINION decisions are parsed as
    opinions; a CERTIFICATE OF JUDGMENT is classified but not parsed.
"""

from __future__ import annotations

from ._alabama import AlabamaAppellate


class AlabamaSupreme(AlabamaAppellate):
    court_id = "ala"
    court_label = "Supreme Court of Alabama."
    docket_prefix = "SC"  # 'SC-YYYY-NNNN'
    author_titles = ("Justice",)
