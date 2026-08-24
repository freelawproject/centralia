# Session state — 2026-08-20 (supersedes the mid-session restart point)

Written at the user's request, agents stopped to conserve usage. Resume here.

## Where the corpus stands

    courts with a corpus   238   (9,377 pdfs)
    with a reader           92   (5,310 pdfs)     <- was 84 this morning
    marked complete         47
    no reader              146
    guard pins             408   across 59 courts
    core-patch-queue items  55 headings (~46 defects, 2 applied)

## What landed today (40 commits)

**The state supremes are CLOSED.** utah (1271/1271) and wis (647/647) were the
last two with a corpus. **colo, ny and okla have NO CORPUS AT ALL** — Colorado
ships only coloctapp, New York only nyed/nysd/nysupct/nycivct/nyfamct/nysurct,
Oklahoma nothing. Stop looking for them.

**Two courts were live but inert, for two different reasons** — the durable
lesson is in the `inert-reader-failure-modes` memory:
- `vt` was written but never imported: inert outside its author's driver. 867/867 once wired.
- `wyo` gated on `crit['docket_number']` one line ABOVE the `walk.finish()`
  that fills it, so a correct 592-line reader refused all 50 of its own
  records. 0/1232 -> 1204/1232.

**Fixed and shipped:** ill's public-domain cite (`2025 IL 130862` wore the
`docket` role; now `citation`, docket `130862`) · va's caption into two columns
over an undrawn gutter (41/50) · dc's head-margin docket stamp out of the
court's own sentence · conn's second paper (the CONNECTICUT LAW JOURNAL
extract, 92.35% -> 100%) · ri's OPINION COVER SHEET into endmatter on 50/50 ·
haw's order title and bench line into headmatter, plus the FIRST EVER writer
for `Document.signature` · wash's reprinted covers (121 misfiled blocks across
38 of 50 files -> 0).

**Ported from scratch today (8 courts, 5,948 rows that were unread this
morning):**

    utah       1271/1271    wis         647/647
    pasuperct   686/686     illappct   1005/1005
    ohioctapp  1323/1323    connappct  1905/1905
    calctapp   1029/1029
    + pacommwct 610/610, ncctapp 431/431, nebctapp 2889/2889 (reports not collected)

**Marked complete:** ariz, ill, kan.

## Three deliberate holds — do not mistake these for oversights

1. **`arizctapp` is NOT complete.** Its `cervantes_v._state` pin is left
   FAILING on purpose as a standing alarm for queue item 18: Howe's
   letter-spaced `H O W E, Chief Judge, specially concurring:` is swallowed by
   Thumma's majority.
2. **`ohioctapp/bath_v._rudisill` and `calctapp/in_re_mccowen` are UNPINNED**
   because their current signatures ARE known bugs (items 40 and 42). Pinning
   them would make guard pass and hide the defect — the 08-19 alaska mistake.
3. **`calctapp/citizens_against_marketplace` IS pinned** but its op typing is
   still wrong; its `ops` will change when item 44 lands. That is the fix, not
   a regression.

## The core queue — stashed for tomorrow at the user's instruction

~46 diagnosed defects with exact patches. Two applied today (item 29, the
`Document.signature` seam; and the panel-roster stack from 08-19). **The queue
has DUPLICATE NUMBERING** from multiple sessions — two 18s, two 19s, two 20s.
Renumber before working through it, or "apply item 19" stays ambiguous.

Land first, in this order:
- **item 21** — `bylines.py:667` searches for the abbreviated title from index
  0, so `JILL J. KAROFSKY, J., concurring.` matches the `J.` inside *JILL J.*
  and the CONCURRENCE types as a MAJORITY. One line.
- **item 19** — staged and anchor-verified at `scratchpad/apply_item19.py`
  (`--check` re-verifies). Blast radius measured across all 4,972 PDFs of the
  84 reader courts: 4 files change signature, all 4 become correct.
- **item 42** — the queue's only CONTENT LOSS: `_announces` deletes a stapled
  order's writing, 135 words gone with no residual, because its veto compares
  the literal `IT IS ORDERED` while California writes `IT IS THEREFORE ORDERED`.
- **items 41 + 30 together** — `criteria.attorneys` comes back empty two
  different ways. Verified on a shipped court: **conn populates it on 0 of 8
  sampled records and 0 of 50 renders carry the chip.**
- **item 34** — `triage()`'s CID test is document-wide, so one unreadable PAGE
  always passes. Took pasuperct from **F/193.5 to A/0.23**.

Corpus-wide and expensive, each wanting its own guard run: items 22, 23, 28,
40, 43.

Also owed: the `harness/quality.py` `_CITE_AFTER` fix (the `joins` false
positive the user saw on va), **item 36** (illappct's profile needs
`strip_para_marker=True` and `also_abbrev=True` or every announced separate
writing in that corpus is lost — MINE to apply, safe now the tree is quiet),
and criteria-manifest entries for va, conn, dc, utah, ri, haw, pasuperct,
illappct, ohioctapp, connappct, calctapp.

## The appellate lane — 44 of 67 remain (1,489 pdfs)

Next batch, siblings already COMPLETE: calag, idahoctapp, iowactapp, ncbizct,
nmariana, nmcca, nmctapp, ohioctcl.

**Sequence AFTER their siblings settle** (they pair to courts rewritten
today): utahctapp, wisctapp, vactapp, washctapp, hawapp.

**Cannot inherit at all** — no `ny` reader exists: nycivct, nyfamct, nysupct,
nysurct.

Beyond this lane: **89 federal district courts** (2,192 pdfs), a different
problem — they do not descend from a state supreme, and `kyed` was picked as
the district exemplar but its census of the other 89 was never run. Plus 10
military/agency, 4 territory, 4 other.

Practical ceiling: guard's 8-worker pool died at eleven concurrent agents.
Batch 3-6.

## Oracles: what NOT to trust

Every mechanical oracle here has a measured blind spot — the user's marks are
the gold standard. Today added three:
- **dc** scored grade A / 0 v1 diffs with a docket welded into a sentence and
  an empty trailing writing. v1 welds the same stamp, so agreeing with v1
  CONFIRMED the bug.
- **wash** had 121 misfiled blocks and a phantom writing at A / mean 0.31,
  with per-file rows BYTE-IDENTICAL before and after the fix.
- **`v1diff` returns 0 diffs VACUOUSLY where no baseline exists** — calctapp
  hit this. Check for `baseline/<court>.json` before believing a zero.

Measuring claimed rows correctly (a grep requiring adjacency showed ri at 63%
and tenn at 6% when both were above 99%): strip the `hm-legend` block first,
and allow a `style` attribute between `class="hmrow …"` and `data-role=`.

    rows = re.findall(r'<div class="hmrow\b[^>]*>', html_without_legend)
    claimed = [r for r in rows if 'data-role=' in r]

## Two process rules paid for today

1. **Commit a new court's module WITH its registry line.** Staging
   `courts/__init__.py` alone swept in another agent's untracked module and
   left HEAD unable to import the courts package. Verify with a clean
   checkout, not by eye:
   `T=$(mktemp -d); git archive HEAD | tar -x -C "$T"` then import.
2. **A probe built from a few eyeballed files understates a class by an order
   of magnitude.** My wash brief named 4 files; the real defect was 38, and
   two of my four were false positives. Hand agents the probe AND tell them to
   re-derive the scope.
