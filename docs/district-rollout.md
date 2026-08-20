# The federal district lane — plan

Written 2026-08-20, before any code. Measured, not assumed: every number below
comes from a census run today over the real corpus at
`/Users/Palin/Code/centralia/assets`.

## What is out there

    district corpora            89      (~2,185 pdfs)
    already ported               1      kyed, 25 pdfs
    remaining                   88      ~2,160 pdfs

`nhd` is the one mixed dir (34 pdfs, 24 of them CM/ECF, 10 something else) —
treat it as a district with a tail, not as a clean district.

## The finding that makes this lane cheap

**These 89 courts are not 89 papers. They are one paper with five dividers.**

A sampled census of 445 page-1s (5 per court) classifies the caption band's
divider mechanically. Dominant family per court:

    glyph rail   ')' stacked between the columns      33 courts
    flush        nothing drawn; status set flush right 32 courts
    drawn rail   a drawn vertical stroke              14 courts
    drawn + pleading-paper line numbers                6 courts   azd caed casd nvd waed wawd
    glyph + typed rule                                 2 courts   gamd mad
    typed rule   '-------X' or '_______'               1 court    nyed
    drawn + pleading + rotated watermark               1 court    cand

Two caveats on those numbers, so nobody reads them as gospel: `drawn` is
detected as any drawn vertical ≥25pt in the middle half of the page, so a
stamp box or a table border can raise it falsely; and `flush` is the residual
bucket — "nothing else fired", not a positive reading.

**kyed already reads three of those five.** Its 710 lines are named for
Kentucky and are almost entirely not about Kentucky: the CM/ECF overlay, the
centred masthead, the two-column caption band, the closer, and dispatch on
GLYPH RAIL / DRAWN RAIL / FLUSH-RIGHT STATUS. What is missing is the typed
rule, the pleading-paper line-number rail, and the scanned clerk stamps.

**v1 solved it the same way and its numbers say the tail is short.** The old
engine has `courts/_district.py` at 1,939 lines plus a per-court file for all
89. Of those 89 files:

    56  are ≤20 lines — a court_id and a label, nothing else
     7  21-60 lines
    14  61-150 lines
    12  >150 lines   ncwd 522 · cacd 271 · caed 257 · kywd 227 · cand 209
                     ncmd 195 · waed 190 · txwd 188 · txsd 179 · wiwd 177
                     akd 172 · wvnd 164

So the expected shape of the work is: one shared reader, ~56 courts that need
only a registration, ~20 that need a measured fact or two, and ~12 that need
real reading. That is the lane, and it is why it can go faster than the state
lane — where every court was its own publisher.

## Design: promote, don't repeat

New core module, `centralia/districts/` (`ecf.py` + whatever it grows), holding
the ECF paper: overlay, masthead, caption band, divider dispatch, closer,
signature block. It is core, so a court file may import it — the per-court-file
rule forbids importing another COURT file, not core.

Each district court file then reads:

```python
DISTRICT = register(CourtProfile(id="almd", ...))

@decider("headmatter.read", court="almd")
def read_headmatter_almd(model, geom, **kw):
    return districts.read_ecf(model, geom, facts=_FACTS, **kw)
```

with `_FACTS` carrying only what was MEASURED for that court: which dividers
its chambers draw, its overlay grammar, its stamp geometry. A court that needs
more writes it in its own file; nothing is inherited, and no district file
imports another.

The overlay grammar is itself shared work: kyed's stamp reads
`Case: 2:25-cv-00171-DLB-CJS  Doc #: 8  Filed: 05/20/26  Page: 1 of 19`, cand's
reads `Case 5:19-cv-04392-BLF   Document 148   Filed 01/23/26   Page 1 of 3`,
txsd's adds `in TXSD`. Same stamp, three punctuations. (A first census pass
scored 132 of 445 page-1s as having NO overlay; that was the regex missing the
colon form, not an absence. The variants belong in one place.)

## Why this cannot break the state courts

This is the constraint the whole plan is built around.

1. **Nothing existing is edited.** `centralia/districts/*` is new code reached
   only from district court files, which are also new. No seam in
   `pipeline.py`, `resolve/*`, `pdfio/*`, `render/*` changes shape. A state
   court never routes through a line of it.
2. **Core defects are REPORTED, not patched** — the standing parallel-porting
   rule. A district porter that finds an `assemble.py` bug writes the diagnosis
   and the exact patch into the core queue; the orchestrator applies it
   serially, with guard, when the tree is quiet.
3. **Guard is the tripwire, not a hope.** 408 pins across 59 courts. Run the
   full guard before the lane opens (the green baseline), and after every
   batch merges. Any state-court pin that moves stops the lane.
4. **One file per agent, and a list of files no agent may touch**:
   `tests/fixtures/guard.json` (never `guard --add`), `output/notes/quality.json`
   (read-modify-write; concurrent runs drop rows), `tests/criteria_manifest.py`,
   `centralia/courts/__init__.py`, and every core module — including
   `centralia/districts/` once Phase A freezes it.
5. **`courts/__init__.py` is the one unavoidable shared edit** (each new module
   must be imported or the reader is inert — the `vt` lesson). The orchestrator
   makes that edit, serially, after a batch lands. Never an agent.
6. **Per-agent scratch directories.** Shared scratch cost three porters real
   time on 08-18.

## Sequencing

**Phase A — promotion (serial, one worker, no fan-out).**
Lift kyed's reading into `centralia/districts/ecf.py`; kyed's own file shrinks
to facts + a call. *The acceptance test is that kyed's guard pins stay green
and its renders are byte-identical* — that is the proof the promotion changed
no behaviour. Nothing else runs during Phase A.

**Phase B — five second witnesses, one per family, still serial-ish.**
A shared reader written from one court is a guess about the other 88. Pick one
court per family and make the shared module read it without a court-specific
hack:

    glyph            almd   (33 courts behind it)
    flush            nysd   (32) — also the '-----X' dashed rail and '-against-'
    drawn            akd    (14)
    pleading         caed   (6)  — line-number rail
    typed rule       wyd    (1)  — typed underscore box, single column
    watermark        cand   (1)  — rotated marginal watermark, worst case

Each new family that the module absorbs is a fact added to `districts/`, not a
branch added to a court file. When these six read clean, the module is real.

**Phase C — fan-out, batched by family, 4-6 agents.**
Guard's 8-worker pool died at eleven concurrent agents; 4-6 is the measured
ceiling. Batch by family so agents hit the same failure at the same time and
one core fix serves the batch. Take the ≤20-line-in-v1 courts first — those are
the ones where "register and measure" should be the whole job — and leave the
twelve real deltas (ncwd, cacd, caed, kywd, cand, ncmd, waed, txwd, txsd, wiwd,
akd, wvnd) for last, one agent each.

## Hazards already visible

- **Image-only page 1s.** 15 of 445 sampled pages are >50% image with almost no
  text (mtd 3, cacd 2, ded 2, and singles in idd lamd msnd nysd nywd oked txsd
  vtd). txsd's first page is nothing but an `ENTERED / Nathan Ochsner, Clerk`
  stamp. This is core-queue **item 34** — `triage()`'s CID test is
  document-wide, so one unreadable page always passes. Land item 34 before
  Phase C or these read as empty.
- **Scanned clerk stamps that OCR into garbage.** vtd's page 1 carries
  `01S; RIC! lir VU~MONT` and `2026 APR 23 PM t1: SO` interleaved BY TOP
  POSITION with the real masthead rows. A masthead walk that trusts row order
  will eat them.
- **Rotated watermarks.** cand prints its court name sideways down the left
  margin; it arrives as 3-6pt fragments (`a`, `i`, `tr`, `n`, `uoC rof`).
- **Pleading-paper line numbers** (the 9th Circuit tradition, 7 courts) are a
  left rail of bare numerals that will otherwise read as caption rows.
- **The oracles are thinner here than in the state lane.** `baseline/` holds 18
  courts, so v1diff is dark for nearly every district. v1's rendered output at
  `/Users/Palin/Code/centralia/output/<court>/` is the per-file reference —
  and per [[v1-is-reference-not-standard]], it is a reference, not a standard.

## The agent

`.claude/agents/district-court-porter.md` — written alongside this plan. It
differs from `court-headmatter-porter` in three ways: it starts from the shared
`centralia/districts/` contract rather than from a v1 court class; its default
answer is "register and measure, add nothing"; and it must report, in writing,
every fact it could not measure rather than guessing one.
