"""The resolver-with-evidence-chain pattern.

Every hard decision is a named DECISION POINT owned by exactly one core
resolver. Core evidence steps run in a fixed order; court-registered
PROVIDERS may contribute candidates/vetoes/support into the chain — they can
never decide, and in particular can never decide "there is none" (absence of
evidence is not a decision). Every Decision records WHICH step fired and the
full chain, so `harness trace` can show why a page did what it did.

Invariants (see notes/lessons/measured-geometry.md):
- thresholds come from measured DocGeometry; profile constants only clamp;
- no evidence -> the floor, unchanged;
- vetoes are core-owned and apply to every candidate regardless of source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Literal

from ..model import Prov


@dataclass(frozen=True)
class Evidence:
    step: str                                   # "typed-underscore-rule", …
    kind: Literal["candidate", "veto", "support"]
    value: Any = None
    score: float = 1.0
    why: str = ""
    prov: Prov | None = None


@dataclass(frozen=True)
class Decision:
    point: str                                  # "footnote.separator@p7"
    value: Any                                  # the decided value (or None)
    fired: str                                  # step that decided — "" if none
    chain: tuple[Evidence, ...] = ()
    floor_used: bool = False


# --------------------------------------------------------------------------
# provider registry — the ONLY way court code plugs into a resolver
# --------------------------------------------------------------------------

Provider = Callable[..., Iterable[Evidence]]
_PROVIDERS: dict[tuple[str, str], list[Provider]] = {}


def provider(point: str, court: str):
    """Register an evidence provider for one decision point of one court.

        @provider("footnote.separator", court="akd")
        def high_rule(ctx) -> Iterable[Evidence]: ...

    Discipline: a provider yields candidates/vetoes/support only. Each one
    needs a fixture pair (a file it must fire on, a near-miss it must not);
    the census reports provider counts per court (soft cap 3)."""
    def wrap(fn: Provider) -> Provider:
        _PROVIDERS.setdefault((point, court), []).append(fn)
        return fn
    return wrap


def providers_for(point: str, court: str) -> list[Provider]:
    return _PROVIDERS.get((point, court), [])


# --------------------------------------------------------------------------
# decider registry — a court may OWN a named decision point outright
# --------------------------------------------------------------------------
# A provider contributes evidence; a DECIDER answers. The distinction matters
# because some facts are the court's own typesetting, not evidence about it:
# scotus names the section in every page's running head ('Syllabus' /
# 'Opinion of the Court'), so syllabus extent there is READ, not inferred, and
# no accumulation of core evidence should be able to outvote the page.
#
# Discipline, so 238 court files stay flat:
#   - a decider is registered for ONE named point of ONE court; it can never
#     see, wrap, or override another court's handlers — there is no chain and
#     no inheritance, so "who decided this" is (point, court) and nothing else;
#   - NOTHING means "I have no answer here" — absence is not a decision, and
#     the point falls through to core exactly as if the court file did not
#     exist;
#   - core-owned vetoes still apply: a court may decide, but not decide
#     something core has ruled impossible;
#   - the decision is recorded as fired="court:<id>:<fn>", so `harness trace`
#     names the file that answered.

NOTHING = object()          # "this decider has nothing to say"

# A DECIDER IS NOT A PROVIDER, and typing it as one made every `@decider` in
# all 241 court files a red squiggle. A provider yields `Evidence`; a decider
# returns the ANSWER for its point — a set of line ids, a {"starts", "drop"}
# map, a list of rows — or `NOTHING`, which is a bare `object()`. None of
# those are `Iterable[Evidence]`, so a checker was right to object and the
# annotation was what was wrong. Nothing here is enforced at runtime: `wrap`
# appends the function and returns it.
Decider = Callable[..., Any]
_DECIDERS: dict[tuple[str, str], list[Decider]] = {}


def decider(point: str, court: str):
    """Register the court's own answer for one decision point.

        @decider("syllabus.pages", court="scotus")
        def syllabus_pages(model, geom, **_): ...
    """
    def wrap(fn: Decider) -> Decider:
        _DECIDERS.setdefault((point, court), []).append(fn)
        return fn
    return wrap


def deciders_for(point: str, court: str) -> list[Decider]:
    return _DECIDERS.get((point, court), [])


def court_decides(point: str, court: str, trace: "Trace", **ctx) -> Any:
    """The court's answer for ``point``, or NOTHING. First non-NOTHING wins;
    the chain is one level deep by construction."""
    for fn in deciders_for(point, court):
        value = fn(**ctx)
        if value is NOTHING:
            continue
        trace.decide(Decision(point, value, f"court:{court}:{fn.__name__}"))
        return value
    return NOTHING


def decider_counts() -> dict[str, int]:
    """court -> registered decider count (the sprawl monitor's other half)."""
    out: dict[str, int] = {}
    for (_point, court), fns in _DECIDERS.items():
        out[court] = out.get(court, 0) + len(fns)
    return out


def provider_counts() -> dict[str, int]:
    """court -> registered provider count (the sprawl monitor)."""
    out: dict[str, int] = {}
    for (_point, court), fns in _PROVIDERS.items():
        out[court] = out.get(court, 0) + len(fns)
    return out


# --------------------------------------------------------------------------
# trace — every decision in one extraction, introspectable
# --------------------------------------------------------------------------

@dataclass
class Trace:
    decisions: list[Decision] = field(default_factory=list)
    events: list[tuple[str, str]] = field(default_factory=list)

    def decide(self, decision: Decision) -> Decision:
        self.decisions.append(decision)
        return decision

    def event(self, name: str, detail: str) -> None:
        self.events.append((name, detail))

    def for_point(self, prefix: str) -> list[Decision]:
        return [d for d in self.decisions if d.point.startswith(prefix)]
