"""The date parser: it must read what courts print and REFUSE the rest.

No corpus needed. The cases are taken from the corpus census (8,392 values,
1,338 distinct) so the table is evidence rather than imagination.
"""

from __future__ import annotations

import pytest

from centralia.dates import all_iso, to_iso

# (value as printed, expected ISO) — the forms the census found, by frequency.
READS = [
    ("January 22, 2026", "2026-01-22"),        # 59% of the corpus
    ("January 2, 2026", "2026-01-02"),         # a further 24%
    ("01/22/2026", "2026-01-22"),
    ("22 January 2026", "2026-01-22"),
    ("01/22/26", "2026-01-22"),                # two-digit year, stated century
    ("Filed: January 22, 2026", "2026-01-22"),  # label leaked into the value
    ("JANUARY 22, 2026", "2026-01-22"),        # all caps
    ("Sept. 9, 2025", "2025-09-09"),           # 4-letter abbreviation
    ("Dec 23 2025", "2025-12-23"),             # no comma
    ("Decided December 23, 2025", "2025-12-23"),
    ("Oral argument held January 22, 2026", "2026-01-22"),
    ("June25, 2025", "2025-06-25"),            # the welded text layer
]

# Values that must NOT parse. Each is either not a date at all or a reading
# bug upstream; a parser that guessed one would be silently wrong forever.
REFUSES = [
    None, "", "   ",
    "Submitted without oral argument",
    "Considered without oral argument",
    "Argued at Richmond, Virginia",
    "October Term, 2024",
    "2025 MP 14",              # a citation, not a date
    "January January, 2026",   # a misread
    "February 30, 2026",       # a day that does not exist
    "January 20",              # truncated: no year
    "13/22/2026",              # month 13
]


@pytest.mark.parametrize("text,want", READS)
def test_reads_the_forms_courts_print(text, want):
    assert to_iso(text) == want


@pytest.mark.parametrize("text", REFUSES)
def test_refuses_rather_than_guesses(text):
    assert to_iso(text) is None


def test_all_iso_returns_every_date_in_order():
    got = all_iso("Oral argument held July 8, 2025. "
                  "Supplemental briefing filed July 31, 2025")
    assert got == ["2025-07-08", "2025-07-31"]


def test_all_iso_deduplicates():
    assert all_iso("May 1, 2026 and again May 1, 2026") == ["2026-05-01"]


def test_all_iso_is_empty_for_a_non_date():
    assert all_iso("Submitted without oral argument") == []
