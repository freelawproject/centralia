"""United States District Court, District of Massachusetts ('mad').

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

from ..districts import EcfPaper, read_ecf
from ..profile import CourtProfile
from ..resolve.bylines import BylineGrammar
from ..resolve.evidence import decider
from . import register

MAD = register(CourtProfile(
    "mad", "United States District Court, District of Massachusetts",
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

_TAGS = _re.compile(r"<[^>]+>")

PAPER = EcfPaper()


# THE DATE THIS COURT PRINTS UNDER ITS TITLE. mad centres the paper's name
# and then the date beneath it — 'OPINION AND ORDER' over 'August 11, 2026' —
# and a centred row below the caption is what the shared reader's title scan
# is looking for, so the date joined the paper's NAME on 5 of this court's 27
# records ('OPINION AND ORDER AUGUST 11, 2026') and no record had a decision
# date at all (the user, 2026-08-24: 'gotta fix tese MAD ones').
#
# Declared here rather than in the shared reader because it is this court's
# habit: the reader is right that a centred row under the caption is the
# title, and only mad puts a bare date in that position. What the row IS is
# unambiguous — nothing but a month, a day and a year — so the title it was
# glued to is given back its own name and the date is published as one.
_DATE_ROW = _re.compile(
    r"^(?:dated?\s*:?\s*)?"
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
    r"\s+\d{1,2},?\s+\d{4})\.?$", _re.I)


@decider("headmatter.read", court="mad")
def read_headmatter_mad(model, geom, **kw):
    """Read mad's ECF pleading order, or NOTHING."""
    out = read_ecf(model, geom, PAPER, **kw)
    if not isinstance(out, dict):
        return out
    crit = out.get("criteria") or {}
    for item in out.get("items") or []:
        if getattr(item, "role", "") != "title":
            continue
        flat = " ".join(_TAGS.sub("", getattr(item, "text", "") or "").split())
        hit = _DATE_ROW.match(flat)
        if not hit:
            continue
        item.role = "date"
        if not crit.get("decision_date"):
            crit["decision_date"] = hit.group(1)
        # …and the paper's name is what is left of it.
        title = crit.get("title")
        if title:
            cut = _re.sub(_re.escape(hit.group(1)) + r"\.?\s*$", "",
                          title, flags=_re.I).strip(" ,.;:")
            crit["title"] = cut or title
    return out
