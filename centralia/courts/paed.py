"""United States District Court, Eastern District of Pennsylvania ('paed').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads 60% of a five-record sample with
the default facts. The rest are UNREAD and this file is not finished:
what they are has not been measured yet.

WHAT THIS COURT DOES THAT THE SHARED PAPER DOES NOT — THE JUDGE-AND-DATE
ROW. Between the caption box and the first words of the opinion, this
court's chambers set one typed row that says who wrote the paper and when it
was filed: the judge ranged left at the body rail, the date ranged right,
and nothing between them.

    UNITED STATES OF AMERICA        :
    v.                              :   Crim. No. 15-599-02
    MOHAMED KHELIL-CHERFI           :

    Diamond, J.                                       August 12, 2026

                             MEMORANDUM

    Having pled guilty in 2016 to committing a series of robberies, …

The row belongs to neither of the blocks it stands between, and the shared
reader — which knows only a caption and a body — put it in whichever one it
touched. Where it stands ABOVE the paper's name it was pulled into the
caption's tail and split down the rail, so the judge joined the last party
('MOHAMED KHELIL-CHERFI Diamond, J.' — the parties of …512266.154.0) and the
date was read as a cell of the box's right column. Where it stands BELOW the
paper's name it fell into the writing and opened it as a heading ('McHUGH,
J. August 17, 2026' — …634924.37.0) or, with the office row fused onto it, as
a paragraph ('Joseph F. Leeson, Jr. July 14, 2026 United States District
Judge' — …643057.84.0). Either way the filing date was lost: 1 of the 33
records that print the row came back with one.

MEASURED on the 56-record corpus: 33 records set the row, in two placements
(19 above the paper's name, 14 below it) and two forms —

  * the SHORT FORM, the judge's surname and office abbreviated on the row
    itself ('Diamond, J.', 'KEARNEY, J.', 'Judge Juan R. Sánchez'); and
  * the REVERSED FORM, the name on one row and the office on another, the
    way this court's judges sign. The date rides on the OFFICE row where the
    name comes first (…634700.19.0: 'KATAYOUN M. COPELAND' over 'UNITED
    STATES MAGISTRATE JUDGE            August 14, 2026') and on the NAME row
    where the office comes second (…643057.84.0).

The row is read here, claimed whole, and reported as what it is: the judge on
`judges` and in the block as an `author` row, the date on `decision_date` and
in the block as a `date` row.

Facts this court measures differently from the shared defaults are declared
below. Nothing is inherited: this file imports core and never another court
file, and no other court file imports it.
"""

from __future__ import annotations

import re

from .. import model as m
from ..districts import EcfPaper, read_ecf
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from . import register

PAED = register(CourtProfile(
    "paed", "United States District Court, Eastern District of Pennsylvania",
    # ONE PAPER, ONE WRITING: a district court is a single judge ruling,
    # so there is no second writing to concur in or dissent from.
    single_writing=True,
    # A district judge signs in the reversed form — the name over the office
    # ('EMILY C. MARKS' / 'UNITED STATES DISTRICT JUDGE').
    byline=BylineGrammar(style="reversed",
                         rev_titles=("United States District Judge",
                                     "United States Magistrate Judge",
                                     "Senior United States District Judge",
                                     "Chief United States District Judge")),
))

PAPER = EcfPaper()


# --------------------------------------------------------------------------
# THE JUDGE-AND-DATE ROW
# --------------------------------------------------------------------------
# THE DATE, AS THIS COURT PRINTS IT. Every one of the 33 records spells the
# month out in full and prints nothing else on the piece — no 'Dated:', no
# 'Filed'. A labeled cell is therefore not this row, which is what keeps a
# caption's own date cell out of the reading.
# …AND IT MAY BE SET IN THE COURT'S OWN CAPITALS. The measurement of 33
# records read only chambers that set the month in title case;
# paed/…635664.13.0 prints 'FEBRUARY 26, 2026' beside 'PEREZ, J.' and the
# row was not found at all, so both pieces fell through to the body and
# rendered welded into one heading — 'PEREZ, J. FEBRUARY 26, 2026' (the
# user, 2026-08-25: 'shouldnt be next ot each other it should also be in
# the headmatter'). The pattern is anchored at both ends and admits nothing
# but a bare date, so case cannot widen what it takes.
_DATE_PIECE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+\d{1,2},\s+(?:19|20)\d{2}\.?$", re.I)

# HOW FAR DOWN THE SHEET the row may stand. The deepest measured is 365 of a
# 792pt page (…643387.28.0, 46%); the shared paper's own closer band is 55%
# and this stays with it, because below that a bare date on a row of its own
# is as likely to be a signature block as this.
_ROW_BAND = 0.55
# THE LEFT PIECE BEGINS AT THE BODY RAIL. Measured: every one of the 33 rows
# starts within a tenth of a point of the column's own left edge (72.0
# against 72.0; 69.7 against 70.0). 8pt is far inside the narrowest indent
# this court sets (36pt, a first-line indent) and clears the rounding.
_RAIL_SLACK = 8.0
# …AND THE DATE IS SET OUT ALONG THE ROW, never butted against it. Measured:
# the leftmost date begins at x288 of a 468pt measure — 46% across it, and a
# quarter of the measure is well under that and well over any gap a broken
# line leaves behind.
_DATE_REACH = 0.25
# HOW FAR A NEIGHBORING ROW OF THE REVERSED FORM MAY STAND, in body line
# pitches. Measured on the five records that set it: 13.8pt between the name
# and the office against a 12pt body — 1.15 pitches. Held to 1.8 so a row
# one blank line away is not reached.
_NEIGHBOR_PITCH = 1.8


def _flat(text: str) -> str:
    return " ".join(text.split())


def _letters(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalpha())


_OFFICES = frozenset(_letters(t) for t in PAED.byline.rev_titles)


def _is_office(text: str) -> bool:
    """Is the row this court's own name for the office, and nothing else?"""
    return _letters(text) in _OFFICES


def _is_caps_name(text: str) -> bool:
    """A judge's name, set the way this court sets it above its office.

    ALL CAPS on every one of the measured records ('KATAYOUN M. COPELAND',
    'CAROL SANDRA MOORE WELLS', 'LYNNE A. SITARSKI'), which is what keeps a
    sentence of the opinion out: prose is not."""
    flat = _flat(text)
    if not (2 < len(flat) <= 60) or any(c.isdigit() for c in flat):
        return False
    if flat != flat.upper():
        return False
    words = flat.split()
    return 1 < len(words) <= 6 and all(
        w.strip(".,'’-").isalpha() for w in words)


def _row_mates(live: list, line) -> list:
    """Everything the page set on the same typed row as ``line``."""
    return [o for o in live if o is not line
            and abs(o.top - line.top) <= 2.5]


def _find_row(live: list, pm, body_x0: float, measure: float,
              body_size: float):
    """The judge-and-date row: (judge lines, date line), or None.

    The date names the row — a piece that is a date and NOTHING else, alone
    on its own line — and the body rail confirms it: this court sets no other
    row with a bare date set out to the right of something ranged at the
    column's left edge."""
    for date in live:
        if date.top > pm.height * _ROW_BAND:
            break
        if not _DATE_PIECE.match(_flat(date.plain)):
            continue
        if date.x0 < body_x0 + _DATE_REACH * measure:
            continue
        mates = _row_mates(live, date)
        # A RAIL GLYPH ON THE ROW MAKES IT A CAPTION CELL, whatever else it
        # says — the box is still open, and nothing in it is this row.
        if any(_flat(o.plain) in PAPER.rail_chars for o in mates):
            continue
        left = [o for o in mates if abs(o.x0 - body_x0) <= _RAIL_SLACK
                and o.x1 <= date.x0 + 2]
        if len(left) != 1:
            continue
        judge = left[0]
        if _DATE_PIECE.match(_flat(judge.plain)):
            continue
        return [judge], date
    return None


def _reversed_neighbor(live: list, judge, date, body_x0: float,
                        body_size: float):
    """The other half of the reversed form, above the row or below it.

    Where the row's own left piece is the OFFICE the name stands above it;
    where the left piece is the name the office stands below. Either way the
    neighbor is alone on its row and ranged at the same rail."""
    pitch = _NEIGHBOR_PITCH * (body_size or 12.0)
    above = [o for o in live
             if o.bottom <= judge.top + 1
             and judge.top - o.top <= pitch
             and abs(o.x0 - body_x0) <= _RAIL_SLACK
             and not _row_mates(live, o)]
    below = [o for o in live
             if o.top >= judge.bottom - 1
             and o.top - judge.top <= pitch
             and abs(o.x0 - body_x0) <= _RAIL_SLACK
             and not _row_mates(live, o)]
    if _is_office(judge.plain):
        for o in sorted(above, key=lambda l: -l.top)[:1]:
            if _is_caps_name(o.plain):
                return o, "above"
    else:
        for o in sorted(below, key=lambda l: l.top)[:1]:
            if _is_office(o.plain):
                return o, "below"
    return None, ""


def _hmline(line, pm, geom, role: str, align: str) -> m.HmLine:
    return m.HmLine(text=line_markup(line), prov=m.Prov(1, (line.id,)),
                    align=m.Align(align), x0=line.x0, size=line.size or 0.0,
                    bold=bool(line.all_bold), role=role)


@decider("headmatter.read", court="paed")
def read_headmatter_paed(model, geom, **kw):
    """Read paed's ECF pleading order, or NOTHING.

    The judge-and-date row is found FIRST and held back from the shared
    reader, so the caption it stands under is read as the box the page drew
    and nothing is pulled out of it afterwards. It is put back as its own
    two rows once the paper has been read."""
    if not model.pages:
        return read_ecf(model, geom, PAPER, **kw)
    pm = model.pages[0]
    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    measure = (getattr(geom, "column", None) if geom else None) \
        or (pm.width - 2 * body_x0)
    live = sorted((l for l in pm.lines if l.plain.strip()),
                  key=lambda l: (l.top, l.x0))

    found = _find_row(live, pm, body_x0, measure, body_size)
    if found is None:
        return read_ecf(model, geom, PAPER, **kw)
    judges, date = found
    mate, _where = _reversed_neighbor(live, judges[0], date,
                                       body_x0, body_size)
    if mate is not None:
        judges = sorted(judges + [mate], key=lambda l: l.top)

    held = {l.id for l in judges} | {date.id}
    kept = pm.lines
    pm.lines = [l for l in kept if l.id not in held]
    try:
        out = read_ecf(model, geom, PAPER, **kw)
    finally:
        pm.lines = kept
    if out is NOTHING or not isinstance(out, dict):
        # THE ROW WAS NOT WHAT HELD THE READING UP. Give the shared reader
        # its page back rather than refuse a record it could have read.
        return read_ecf(model, geom, PAPER, **kw)

    # THE ROW IS ONLY THE COVER'S IF THE COVER REACHES IT. Where the shared
    # reader leaves a row above this one unclaimed — …636167.47.0 reads the
    # last party cell as its title and never claims the underlined
    # 'MEMORANDUM' over the judge — the writing opens on that row, and
    # everything below it stands INSIDE the writing. Core's own invariant
    # then reunites what a later rule cut out of the middle of an opinion
    # (pipeline.py, '9b A WRITING IS NEVER BISECTED'), so a claim made here
    # is undone there and the row comes back as two paragraphs instead of
    # the one row the page set. The criteria the row states are still read;
    # only the CLAIM is withheld, and the row renders where it did before.
    _above = any(l.top < judges[0].top and l.id not in out["consumed"]
                 and l.id not in held for l in live)
    if _above:
        _record(out, judges, date)
        return out

    def _align(line) -> str:
        return line_alignment(line, pm.width, geom,
                              banner_center_min_size=(body_size or 12.0) + 2.0)

    rows = [(l, "author", _align(l)) for l in judges]
    # THE DATE IS RANGED RIGHT, and it is the page that ranged it — the row
    # is one typed line and the block renders row by row, so the only way to
    # keep the date where the court put it is to say so.
    rows.append((date, "date", "R"))
    out["items"].extend(_hmline(l, pm, geom, role, al) for l, role, al in rows)
    out["consumed"].update(held)

    _record(out, judges, date)
    return out


def _record(out, judges: list, date) -> None:
    """What the row SAYS, whether or not the block could keep it."""
    crit = out["criteria"]
    # ONE JUDGE, HOWEVER MANY ROWS THE COURT SET THE NAME ON. The reversed
    # form prints the name and the office on two rows and they are the same
    # person, so they are joined the way a byline reads and not listed as a
    # bench of two. The row is reported AS PRINTED — 'Diamond, J.' keeps its
    # period, because in the short form the period is the abbreviation's and
    # not the row's.
    crit.setdefault("judges", ", ".join(_flat(l.plain) for l in judges))
    crit.setdefault("decision_date", _flat(date.plain).rstrip("."))
