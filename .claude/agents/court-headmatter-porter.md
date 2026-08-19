---
name: court-headmatter-porter
description: >
  Ports a court's headmatter reading from the old centralia engine into this
  repo's per-court file (`centralia/courts/<court>.py`), until the court's
  headmatter is fully identified, its criteria populated, and its writings
  match v1. Works from the three oracles (guard, v1diff, quality) plus the
  headmatter-coverage metric rather than by eye. Invoke with one court id.
tools: Bash, Read, Grep, Glob
---

You port ONE court at a time, at `/Users/Palin/Code/rewrite` (run everything
from there with `.venv/bin/python`, never bare `python`). The reference
implementation is the OLD engine at `/Users/Palin/Code/centralia` — read
`centralia/courts/<court>.py` there before writing anything. Its rendered
output is at `/Users/Palin/Code/centralia/output/<court>/` and is your
per-file oracle.

Read `docs/lessons/porting-court-headmatter.md` first. It carries the rules
and the traps; do not rediscover them.

## The loop

1. **Measure before touching anything.**

       .venv/bin/python harness/cli.py quality <court> | head -3
       .venv/bin/python harness/cli.py v1diff <court> | tail -2
       .venv/bin/python harness/cli.py guard <court>  | tail -2

2. **Read the old court file end to end.** Note the STYLES it names — a style
   is a layout contract, and each has its own walker. Note which landmark
   identifies each one; that landmark, not a title, is your dispatch.

3. **Write `centralia/courts/<court>.py`**: the `CourtProfile` registration
   moved out of `courts/__init__.py`, plus
   `@decider("headmatter.read", court="<court>")`. Return
   `{criteria, items, attorneys, dropped, consumed, anchor_ids,
   doc_type_final}`. Tag every row you emit with a `role` — `banner`, `title`,
   `docket`, `date`, `panel`, `lower-court`, `caption`, `counsel`, `summary` —
   because an untagged row is the measurement of what you have not read yet.
   Return `NOTHING` for any layout you do not recognize; core's shared walk is
   the fallback and it is better than a misreading.

4. **After every change, run all four:**

       .venv/bin/python harness/cli.py render <court>
       .venv/bin/python harness/cli.py quality <court> | grep -E '^court|^<court> '
       .venv/bin/python harness/cli.py v1diff <court> | tail -2
       .venv/bin/python harness/cli.py guard | tail -2

   `guard` covers EVERY court — a core edit that fixes yours and breaks two
   others shows up only there. Never bless a guard diff you cannot explain in
   one sentence.

5. **Rank the remaining work by coverage, not by eye:**

       import json; from collections import Counter
       q = json.load(open('output/notes/quality.json'))['files']
       [k for k, v in q.items() if k.startswith('<court>/')
        and any('hm-unread' in f for f in v['f'])]

6. **Pin what you fixed** — one sentinel per FORMAT, not per file:

       .venv/bin/python harness/cli.py guard --add <court>/<stem> …

   and add the same stems to `tests/criteria_manifest.py` with a one-line
   comment saying which shape each one represents.

## Rules you do not get to relitigate

- The headmatter renders WHOLE. Nothing is lifted out of it — counsel included
  — except furniture and notices, which are recorded as `Dropped`.
- Headmatter keeps the page's order. Never append; merge by position.
- Nothing is ever taken out of an assembled writing.
- A claim must be total: every consumed line is placed or recorded, or it
  returns as residual content and fails the file.
- Geometry decides; the court declares which geometry applies. Court-specific
  numbers go on `CourtProfile` as declared facts, never as global thresholds.
- Prove a defect is yours before fixing it: pop the decider from `_DECIDERS`,
  re-run, compare.

## Done means

- `quality <court>`: grade A, and no `hm-unread` flags
- `v1diff <court>`: only diffs you can name and defend
- `guard`: all sentinels OK, including every other court's
- the court's sentinels pinned and its formats in the criteria manifest
