"""Court date strings -> ISO ``YYYY-MM-DD``, or nothing at all.

The criteria keep a date AS THE COURT PRINTED IT, because that is what the
page says and no two courts say it the same way. A consumer wants a date it
can compare, so this module offers the ISO twin — and REFUSES rather than
guesses, because a wrong date that parses is worse than a missing one that
does not.

MEASURED over the 8,392 date values the corpus renders (1,338 distinct):

    4949  'January 22, 2026'          59%  ┐ two forms are 83% of everything
    2033  'January 2, 2026'           24%  ┘
     189  '01/22/2026'
      88  '22 January 2026'
      78  '01/22/26'
      58  'Filed: January 22, 2026'        the label leaked into the value
      47  'Submitted without oral argument'   not a date at all
      45  'JANUARY 22, 2026'              all caps
      41  'January January, 2026'         a misread
      38  'Oral argument held January 22, 2026'

So: month-name-first, day-first, and numeric — with a leading label tolerated
and a trailing remark ignored. Everything else returns None, which is a
REPORT: `diagnostics` shows which dates did not parse, and the ones that never
will are reading bugs upstream ('Filed:' claimed with its value, prose in a
date field) rather than grammar this module should grow to cover.

TWO-DIGIT YEARS are read in the corpus's own century. These are contemporary
filings — the corpus runs 2025-2026 — so '26' is 2026. A pivot is a guess
whatever it is; this one is stated rather than hidden.
"""

from __future__ import annotations

import re

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
    # The abbreviations the reporters set, with or without the point.
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH_RE = "|".join(sorted(_MONTHS, key=len, reverse=True))

# 'January 22, 2026' — the comma is optional, the day may be 1 or 2 digits.
_MDY = re.compile(rf"\b(?P<m>{_MONTH_RE})\.?\s+(?P<d>\d{{1,2}})(?:st|nd|rd|th)?"
                  rf"\s*,?\s*(?P<y>\d{{4}})\b", re.I)
# '22 January 2026' — the day-first form.
_DMY = re.compile(rf"\b(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\s+(?P<m>{_MONTH_RE})\.?"
                  rf"\s*,?\s*(?P<y>\d{{4}})\b", re.I)
# '01/22/2026' and '1/22/26'. MONTH FIRST: every numeric date in this corpus
# is a US filing stamp, and the two forms cannot be told apart from one value.
_SLASH = re.compile(r"\b(?P<m>\d{1,2})/(?P<d>\d{1,2})/(?P<y>\d{2,4})\b")
# The corpus's century, for a two-digit year. See the note above.
_CENTURY = 2000

_DAYS = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _build(y: int, mth: int, d: int) -> str | None:
    if y < _CENTURY:                       # a two-digit year
        y += _CENTURY
    if not (1 <= mth <= 12) or not (1 <= d <= _DAYS[mth - 1]):
        return None
    if not (1700 <= y <= 2200):
        return None
    return f"{y:04d}-{mth:02d}-{d:02d}"


def to_iso(text: str | None) -> str | None:
    """``YYYY-MM-DD`` for the FIRST date in ``text``, or None.

    The first, because a court that prints two in one field prints the one the
    field is named for first ('Oral argument held July 8, 2025. Supplemental
    briefing filed July 31, …'). One value in 8,392 does that, so this is a
    tie-break rather than a feature.
    """
    if not text:
        return None
    s = " ".join(str(text).split())
    for pat in (_MDY, _DMY):
        got = pat.search(s)
        if got:
            iso = _build(int(got.group("y")),
                         _MONTHS[got.group("m").lower().rstrip(".")],
                         int(got.group("d")))
            if iso:
                return iso
    got = _SLASH.search(s)
    if got:
        return _build(int(got.group("y")), int(got.group("m")),
                      int(got.group("d")))
    return None


def all_iso(text: str | None) -> list[str]:
    """Every date in ``text``, in the order printed — for a field that carries
    more than one and a caller that wants both."""
    if not text:
        return []
    s = " ".join(str(text).split())
    found: list[tuple[int, str]] = []
    for pat in (_MDY, _DMY):
        for got in pat.finditer(s):
            iso = _build(int(got.group("y")),
                         _MONTHS[got.group("m").lower().rstrip(".")],
                         int(got.group("d")))
            if iso:
                found.append((got.start(), iso))
    for got in _SLASH.finditer(s):
        iso = _build(int(got.group("y")), int(got.group("m")),
                     int(got.group("d")))
        if iso and not any(abs(p - got.start()) < 4 for p, _ in found):
            found.append((got.start(), iso))
    out: list[str] = []
    for _, iso in sorted(found):
        if iso not in out:
            out.append(iso)
    return out
