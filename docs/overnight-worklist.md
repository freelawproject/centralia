# Overnight worklist — remaining state courts

Generated 2026-08-20. **Tick a court off by deleting its line** once its
reader is committed. This file is the source of truth for the overnight
batches; the cron job reads it, not the conversation.

Batch protocol is in `docs/session-state-2026-08-20.md`. Non-negotiables:
one court file per agent, own scratch dir, no core edits (report with an
exact patch), never `guard --add`/`--bless`, never the `quality`
subcommand, and **commit the module WITH its `courts/__init__.py` import
line** — staging that file alone broke HEAD once today.

41 courts remaining, 1363 pdfs.


## sibling COMPLETE — safest inheritance

| court | pdfs | inherit from |
|---|---|---|
| `calag` | 42 | `cal.py` |
| `ncbizct` | 42 | `nc.py` |
| `nmariana` | 32 | `nm.py` |
| `nmcca` | 32 | `nm.py` |
| `idahoctapp` | 30 | `idaho.py` |
| `iowactapp` | 30 | `iowa.py` |
| `ohioctcl` | 30 | `ohio.py` |
| `nmctapp` | 21 | `nm.py` |

## sibling has a reader, not yet marked

| court | pdfs | inherit from |
|---|---|---|
| `delch` | 42 | `del.py` |
| `delctcompl` | 42 | `del.py` |
| `delsuperct` | 42 | `del.py` |
| `indctapp` | 42 | `ind.py` |
| `kyctapp` | 42 | `ky.py` |
| `lactapp` | 42 | `la.py` |
| `mdag` | 42 | `md.py` |
| `njtaxct` | 42 | `nj.py` |
| `orctapp` | 42 | `or.py` |
| `ortc` | 42 | `or.py` |
| `tenncrimapp` | 42 | `tenn.py` |
| `texag` | 42 | `tex.py` |
| `texbizct` | 42 | `tex.py` |
| `vtsuperct` | 42 | `vt.py` |
| `washctapp` | 42 | `wash.py` |
| `wvactapp` | 42 | `wva.py` |
| `indtc` | 41 | `ind.py` |
| `minnag` | 41 | `minn.py` |
| `nevapp` | 31 | `nev.py` |
| `hawapp` | 30 | `haw.py` |
| `mdctspecapp` | 30 | `md.py` |
| `minnctapp` | 30 | `minn.py` |
| `missctapp` | 30 | `miss.py` |
| `texapp` | 30 | `tex.py` |
| `utahctapp` | 30 | `utah.py` |
| `vactapp` | 30 | `va.py` |
| `wisctapp` | 30 | `wis.py` |
| `scctapp` | 28 | `sc.py` |
| `mesuperct` | 20 | `me.py` |

## NO sibling reader — needs its own contract

| court | pdfs | inherit from |
|---|---|---|
| `nysupct` | 21 | — |
| `nysurct` | 5 | — |
| `nycivct` | 4 | — |
| `nyfamct` | 1 | — |
