# Per-court files: one file per court, flat wiring

Status: proposed 2026-08-18. Pilot court: `scotus` (headmatter + syllabus).

## The distinction this rests on

The old repo's sprawl was **inheritance**, not per-court code: `_AlaFamily`
overrode `_StateSupreme` overrode base, so "who decided this line" needed a
debugger, and 111 profile knobs were read at 25 declaration sites.

What this plan builds instead: 238 **flat** files, each registering at named
seams, none overriding another. "Who decided this" is answered by one lookup —
point name + court — and by `harness trace`.

Kept from today: court FACTS stay declared data (`CourtProfile`), and rules that
generalize stay in core with the court as a named witness. A court file is for
what is genuinely that court's own.

## Shape

### 1. `centralia/courts/<court_id>.py`

Each file holds, for exactly one court:

- its `register(CourtProfile(...))` call (moved out of `courts/__init__.py`)
- its `@provider` / `@decider` registrations — the only place court *code* lives

Rules, enforced mechanically:

- a court file may import from `centralia.*` core, and **never** from another
  court file (an import-graph test asserts this — this is what makes
  "no this-overrides-that" a guarantee rather than a habit)
- one court per file, one file per court; no families, no mixins, no subclassing

`courts/__init__.py` shrinks to `PROFILES` / `register` / `get_profile` plus a
deterministic import of every court module. Shared byline grammars that several
courts *genuinely* print identically (`_TENN_GRAMMAR` today) move to
`courts/_grammars.py` and are referenced explicitly by each court file — shared
data by reference, never behavior by inheritance.

### 2. Two handler kinds, one level deep

`resolve/evidence.py` already has half of this. Add the second kind:

- `@provider(point, court)` — yields candidate / veto / support evidence.
  Cannot decide. Exists today.
- `@decider(point, court)` — returns `value` or `NOTHING`. A returned value IS
  the decision, recorded as `fired="court:<id>:<fn>"`.

Order at every point, identical everywhere:

1. court **decider** — first, short-circuiting. Reading the court file therefore
   tells you the whole answer for that point without knowing core's step order.
2. core-owned **vetoes** still apply to a court decision (evidence.py's
   invariant: vetoes are core-owned and apply to every candidate regardless of
   source). A vetoed court decision is recorded and falls through to core.
3. core evidence steps, in their fixed order
4. court **providers** feeding candidates into those steps
5. the floor, unchanged, when there is no evidence

No court can observe or affect another court's handlers. There is no second
level to reason about.

### 3. Decision points for the pilot

`read_headmatter` currently emits trace **events**, not `Decision`s, so there is
nothing to hook. The pilot names five seams — the ones scotus actually needs:

| point | today |
| --- | --- |
| `headmatter.docket` | `looks_like_docket` — `resolve/headmatter.py:126` |
| `headmatter.decision_date` | `date_row_value` — `resolve/headmatter.py:192` |
| `headmatter.parties` | `read_parties` — `resolve/headmatter.py:273` |
| `headmatter.row_kind` | per-row routing emitting `criteria.*` — ~`:590-710` |
| `syllabus.open` | the `front_matter` gate — `pipeline.py:742` |

Each becomes a real `trace.decide(Decision(point, ...))`, so `harness trace`
explains headmatter the way it already explains `footnote.separator`.

## Guardrails against re-sprawl

- one file per court; no court-to-court imports (import-graph test)
- every handler needs a **fixture pair**: a file it must fire on, a near-miss it
  must not — already the provider discipline
- census reports handler counts per court; soft cap 3 per point
- **promotion detector**: when >= 3 courts register semantically identical
  deciders at one point, the census flags it as a global-rule candidate
- the trace names the deciding court file

### The cost, stated plainly

A court that decides stops sharing its fix. `Decided`-beats-`Argued` lives in
`headmatter.py:204` with scotus as witness, so every court printing that row
gets it free today. Moved into `scotus.py`, the next court printing it breaks
again. That is duplication, not sprawl — the promotion detector is how it gets
caught in the census instead of a year later.

## Migration order

Nothing big-bang; each step is separately verifiable.

1. **Split** `courts/__init__.py` into per-court files, mechanically. Behavior
   identical: re-render the corpus and diff output byte-for-byte. Reversible.
2. **Add** `@decider` + trace plumbing to `evidence.py`. No court uses it yet.
3. **Name** the five headmatter/syllabus decision points. Core behavior
   unchanged; those decisions are now traced.
4. **Pilot**: move scotus's own headmatter/syllabus behaviors into
   `courts/scotus.py` as deciders. Only genuinely scotus-shaped things move;
   general rules other courts share stay in core.
5. **Verify**: re-render scotus against its baseline (grade B, mean 1.28,
   74% A/B, 100/100 valid as of 2026-08-18) and diff every other court's output
   to prove nothing else moved.

## Open input needed

Step 4 cannot be specified until the scotus headmatter/syllabus behaviors to
change are named — what it does now vs. what it should do. Steps 1-3 are
independent of that and can start immediately.

## Sequencing note

Do not start step 1 while a corpus re-render sweep is in flight: engine changes
landing mid-sweep make the output a mix of two engines and destroy the baseline
step 1 is diffed against.
