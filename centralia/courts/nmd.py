"""United States District Court, District of New Mexico ('nmd').

THE CONTRACT — the ECF pleading order, `centralia.districts.ecf`, the paper
this court shares with the other federal district corpora. The paper, the
walk and the vocabularies are documented there.

MEASURED: the shared reader reads 80% of a five-record sample with
the default facts. The rest are UNREAD and this file is not finished:
what they are has not been measured yet.

Facts this court measures differently from the shared defaults are declared
below. Nothing is inherited: this file imports core and never another court
file, and no other court file imports it.
"""

from __future__ import annotations

import re as _re

from .. import model as m
from ..districts import EcfPaper, read_ecf
from ..geometry import line_alignment
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import NOTHING, decider
from ..resolve.footnotes import line_markup
from ..resolve.furniture import FurnitureFinder
from . import register

NMD = register(CourtProfile(
    "nmd", "United States District Court, District of New Mexico",
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
# THE APPEARANCES, PRINTED AFTER THE WRITING
# --------------------------------------------------------------------------
# This court sets its appearances at the FOOT of the opinion, not on the
# cover. The judge signs, and under the signature the roster runs to the last
# line of the last page — each party's counsel with their firm and their
# city, co-counsel divided by '-- and --', and every group closed by the line
# that says whom they appeared for:
#
#     UNITED STATES DISTRICT JUDGE
#
#     Counsel:
#
#     Jacob Payne
#     Jesse Gallegos
#     Singleton Schreiber
#     Albuquerque, New Mexico
#
#             Attorneys for Plaintiffs
#
# The shared paper looks for appearances beside the caption, which is where
# every other district prints them, so it found none here and the roster
# stayed in the writing: `endmatter` came back 0 on all 17 records that print
# one, while the names sat in the opinion's text as prose. The page sets one
# name per line and the assembler joins short adjacent lines, so five
# attorneys arrived welded into a sentence — 'Jacob Payne Jesse Gallegos
# Alexander Flores Robert Sanchez Brian Colon' (…502829.63.0) — which is not
# a thing anyone can look a lawyer up in.
#
# MEASURED on all 55 records: 17 print the roster and 38 do not, and every
# one of the 17 opens it with a label of its own and runs it to the end of
# the document. Two spellings, both read letters-only: 'Counsel:' (16) and
# 'Parties and counsel:' (…502936.24.0).

# WHAT OPENS THE ROSTER, letters-only so the colon and the case cannot
# matter.
_ROSTER_LABELS = frozenset({"counsel", "partiesandcounsel"})
# …AND WHAT PROVES IT IS ONE. Every measured roster closes each group on the
# line naming whom counsel appeared for. A body row reading 'Counsel:' alone
# would open nothing and close on nothing, and this is what tells them apart.
_APPEARED_FOR = _re.compile(r"^attorneys?\s+for\b", _re.I)
# THE LABEL STANDS AT THE BODY RAIL, like the names under it. 8pt clears the
# rounding and stays far inside this court's own indent (36pt).
_ROSTER_RAIL = 8.0


def _letters(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalpha())


def _roster_opens(model, body_x0: float):
    """The row this court's appearances open on, or None.

    The LAST such label in the document, because the roster runs from it to
    the end and a paper prints only one — taking the last is what keeps a
    quoted one in the body from opening a roster that never closes."""
    found = None
    for pm in model.pages:
        for line in pm.lines:
            flat = " ".join(line.plain.split())
            if _letters(flat) in _ROSTER_LABELS and flat.endswith(":") \
                    and abs(line.x0 - body_x0) <= _ROSTER_RAIL:
                found = (pm.number, line)
    return found


@decider("headmatter.read", court="nmd")
def read_headmatter_nmd(model, geom, **kw):
    """Read nmd's ECF pleading order and its closing appearances, or NOTHING.

    The cover is the shared paper's. The roster under the signature is this
    court's own, and it is handed back on `attorneys` — the endmatter — one
    row per line the page printed, so a name stays a name."""
    out = read_ecf(model, geom, PAPER, **kw)
    if out is NOTHING or not isinstance(out, dict) or not model.pages:
        return out

    body_x0 = geom.body_x0 if geom else 72.0
    body_size = geom.body_size if geom else 12.0
    opened = _roster_opens(model, body_x0)
    if opened is None:
        return out
    page_no, label = opened

    # EVERYTHING FROM THE LABEL TO THE LAST LINE OF THE PAPER, in the order
    # the pages print it — the roster spans sheets (…352853.498.0 opens it on
    # page 2 of 4 and closes it on page 4).
    finder = FurnitureFinder(model, body_x0, body_size)
    rows: list = []
    for pm in model.pages:
        if pm.number < page_no:
            continue
        for line in sorted((l for l in pm.lines if l.plain.strip()),
                           key=lambda l: (l.top, l.x0)):
            if pm.number == page_no and line.top < label.top - 1:
                continue
            # THE PAGE'S OWN FURNITURE IS NOT COUNSEL. The roster crosses a
            # sheet boundary, so the e-filing stamp at the head of the next
            # page and the folio at the foot of this one stand inside the run
            # (…517883.791.0 spans three sheets). Left in, '- 14 -' is
            # reported as an appearance.
            if finder.kind(pm, line) is not None:
                continue
            rows.append((pm, line))

    # A ROSTER CLOSES ITS GROUPS. See `_APPEARED_FOR` — without one this is
    # not the appearances and nothing is claimed.
    if not any(_APPEARED_FOR.match(" ".join(l.plain.split()))
               for _pm, l in rows):
        return out

    for pm, line in rows:
        out["attorneys"].append(m.HmLine(
            text=line_markup(line), prov=m.Prov(pm.number, (line.id,)),
            align=m.Align(line_alignment(line, pm.width, geom)),
            x0=line.x0, size=line.size or 0.0,
            bold=bool(line.all_bold), role="counsel"))
        out["consumed"].add(line.id)
    return out
