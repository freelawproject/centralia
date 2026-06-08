"""Map each registered court to its extractor *style family* — the base class
that governs how its headmatter and byline are parsed — and, from that, the
other courts that share the same style. Used by the per-court view to show
'this court is parsed like X' and link to its stylistic siblings.

The family is read from the extractor's class hierarchy (MRO): the first base
whose name is a known family base wins, so a mixin (ArizonaStyle) or a
specialized supreme base (ReversedJusticeSupreme) is reported in preference to
the generic StateSupreme it extends.
"""

from __future__ import annotations

from collections import defaultdict

from restatement.registry import EXTRACTORS

# Most-specific intent first; the description is what the per-court view shows.
_FAMILY_NAMES = {
    "ArizonaStyle": "Arizona style (¶-numbered body, header-transition opinions)",
    "ConnecticutStyle": "Connecticut style (bracketed-asterisk notice, paged headmatter)",
    "ReversedJusticeSupreme": "Reversed-justice byline (“JUSTICE X delivered the opinion…”)",
    "AbbrevTitleSupreme": "Abbreviated-title byline (“X, J.” / “PER CURIAM”)",
    "StateAppellate": "State appellate (publication banner, P.J./JJ. titles)",
    "StateSupreme": "State supreme (name-first byline at the body)",
    "FederalCircuitBase": "Federal circuit",
    "DistrictBase": "Federal district (CM/ECF stamp, signature-block author)",
    "GenericExtractor": "Generic (no dedicated tuning)",
}


def _family_of_class(cls) -> str | None:
    for base in cls.__mro__:
        if base.__name__ in _FAMILY_NAMES:
            return _FAMILY_NAMES[base.__name__]
    return None


# court_id -> family label (computed once at import).
COURT_FAMILY: dict[str, str] = {
    cid: _family_of_class(cls)
    for cid, cls in EXTRACTORS.items()
    if _family_of_class(cls)
}

# family label -> sorted court ids sharing it.
FAMILY_MEMBERS: dict[str, list] = defaultdict(list)
for _cid, _fam in COURT_FAMILY.items():
    FAMILY_MEMBERS[_fam].append(_cid)
for _fam in FAMILY_MEMBERS:
    FAMILY_MEMBERS[_fam].sort()


def family_of(court_id: str) -> str | None:
    return COURT_FAMILY.get(court_id)


def similar_courts(court_id: str) -> list:
    """Other registered courts parsed by the same style family."""
    fam = COURT_FAMILY.get(court_id)
    if not fam:
        return []
    return [c for c in FAMILY_MEMBERS.get(fam, []) if c != court_id]
