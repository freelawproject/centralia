# Porting a court from its family — the fast path

`notes/lessons/porting-court-headmatter.md` covers a COLD port: a court whose
paper nobody has read yet. This covers the other 159 — a court whose family
already has a finished reader. Different job, different first move, and an
order of magnitude cheaper when you do it in the right order.

Written 2026-08-19, after kanctapp went from **0% to 81% of its headmatter
rows tagged** on a copy of kan.py plus a four-line change to one gate.

## Step 0 — DIFF THE PAGES BEFORE YOU DIFF THE CODE

This is the whole trick and it takes thirty seconds. Dump the first dozen
lines of page 1 for the parent and the child, side by side, with geometry:

```python
from centralia.pdfio import build_pdf
import glob
for c in ('kan', 'kanctapp'):
    p = sorted(glob.glob(f'/Users/Palin/Code/centralia/assets/{c}/*.pdf'))[0]
    m = build_pdf(p)
    print(f"=== {c} ===")
    for l in sorted(m.pages[0].lines, key=lambda l: l.top)[:12]:
        print(f"  top={l.top:6.1f} x0={l.x0:6.1f} sz={l.size or 0:4.1f} "
              f"{l.plain.strip()[:58]!r}")
```

For kan/kanctapp that dump showed one single difference:

```
kan       row 0  'IN THE SUPREME COURT OF THE STATE OF KANSAS'   row 1  'No. 127,093'
kanctapp  row 0  'No. 129,334'                                    row 1  'IN THE COURT OF APPEALS OF THE STATE OF KANSAS'
```

**The docket and the masthead are swapped.** Everything below — caption,
`SYLLABUS BY THE COURT`, the numbered points, the Reporter's apparatus a
type step down, the byline forms — was identical. That one fact predicted
the entire port: copy the file, rebind the id, widen the masthead gate to
look in the first two rows, done.

Do this BEFORE reading either court file. It tells you whether you are
doing a copy (minutes), an adaptation (an hour), or a cold port (a day).

## Step 1 — copy, do not import

Court files may not import each other. A family is ported by COPYING the
reader and rebinding the decider:

```bash
# rewrite the docstring, then:
#   @decider("headmatter.read", court="kan")  ->  court="kanctapp"
#   def read_headmatter_kan(  ->  def read_headmatter_kanctapp(
```

Say so in the new file's docstring, explicitly, with the reason — otherwise
the next reader assumes the duplication is an accident and "fixes" it:

> A COPY OF kan.py, not an import of it: court files may not import each
> other, so a family that prints the same paper is ported by copying the
> reader and rebinding the id. If the two courts ever diverge, THIS file
> changes and kan.py does not.

## Step 2 — WIRE IT, then measure

`centralia/courts/__init__.py` needs `from . import <court>`. Three courts
this session had complete, working reader files that were doing nothing
because nobody added the import — md sat at 37KB and 0% coverage until it
was wired, then jumped straight to **952/952 rows tagged**.

A reader that is not imported is not a port. Measure coverage through
`harness/cli.py render`, never through a hand-rolled driver, because a
driver that imports the module by hand will show you numbers the harness
cannot reproduce.

```python
import re, glob, collections
tot = un = 0; r = collections.Counter()
for p in glob.glob('output/<court>/*.html'):
    s = open(p).read()
    rows = re.findall(r'<div class="hmrow[^"]*"([^>]*)>', s)
    tot += len(rows); un += sum(1 for x in rows if 'data-role=' not in x)
    for m in re.findall(r'<div class="hmrow[^"]*"[^>]*data-role="([^"]+)"', s):
        r[m] += 1
print(f"{tot-un}/{tot} tagged ({(tot-un)/tot*100:.0f}%)", dict(r))
```

**Count roles off `<div class="hmrow" ... data-role=`, not off bare
`data-role=`.** The legend at the top of the render also carries one
`data-role` per role, so the loose pattern reports 42 of every role on a
42-file court and looks like a perfect port when coverage is zero.

## The traps that cost the most, in order

### 1. Never index a role from a fixed row

kan's classifier opened with `kinds[0] = "court"`. On kanctapp, where row 0
is the docket, that one line produced THREE wrong roles at once — the
docket tagged `court`, the masthead tagged `caption`, and everything after
shifted. The reviewer caught all three in one glance.

Anchor roles to the LANDMARK you dispatched on, not to an ordinal:

```python
kinds[_head] = "court"          # _head is where the banner actually is
for i in range(0, len(block)):
    if i == _head:
        continue
```

### 2. Check the role vocabulary BEFORE you tag

There was no `syllabus` role, so Kansas's syllabus — 852 rows of numbered
points of law BY THE COURT — was tagged `headnotes` and the port shipped
that way. Headnotes are the REPORTER's subject list
(`Attorneys—Misconduct—…`); a syllabus is the court's own writing. Same
band of the page, different authorship, different role.

The vocabulary lives in `centralia/model.py` on `HmLine.role`, and every
role needs three things to exist: the docstring entry, a tint in
`render/html.py`, and a legend entry. If the row you are looking at has no
honest role, ADD ONE — do not park it on the nearest neighbour. A
mis-tagged row is worse than an untagged one: untagged says "nobody read
this", which is true and measurable.

### 3. A heading that names a SECTION is not a `title`

`title` is what the paper calls ITSELF (`OPINION`, `SUMMARY ORDER`).
`SYLLABUS BY THE COURT` names the block beneath it and belongs to that
block. Same for `SYLLABUS`, `HEADNOTES`, `ORDER` when it heads a region
rather than the document.

### 4. Reuse falls with each extra PAPER, not with layout difference

Measured across the family ports:

| child | parent | reuse | why |
|---|---|---:|---|
| alacivapp | ala | 70% | same paper, zero debugging iterations |
| alacrimapp | ala | 74% | same paper |
| arkctapp | ark | 63% | same paper |
| gactapp | ga | 54% | two papers, both the parent's shapes |
| massappct | mass | 52% file / 65% statements | same paper, different bench titles |
| fladistctapp | fla | 58% (19% verbatim + 39% adapted) | **child prints a second paper** |

fladistctapp is the shape of the exception: fla lets core harvest its
roster, while fladistctapp prints a whole ENDMATTER block — roster plus a
four-way finality stamp plus its own fences — that had to be claimed as a
second region. That block alone is ~35% of the file. Strip it and the
headmatter proper is back at ~70%.

**So estimate a family port by counting the child's PAPERS, not by eyeing
its captions.** Step 0's page dump tells you this too.

### 5. Do not widen a core constant on one court's evidence

moctapp's closing roster (`JEFFREY W. BATES, J. – OPINION AUTHOR` …) welds
into one line because core's stack rule needs every line at most 45% of the
measure and moctapp's rows carry a name AND a role, so they run 40–55%.
The obvious fix is to raise the cap. It is wrong: raising 0.45 → 0.60
newly catches 20 same-edge runs in a 10-court sample, and they are real
prose that must stay joined — counsel-list wraps, caption wraps, footnote
runs. Double leading fails as a discriminator too, because nd's own rosters
are single-leaded.

Before touching a core constant, measure the BAND you are about to open:

```python
# every 3+ run of same-edge lines, bucketed by max ink, across 10 courts
```

If the band contains anything that is not the thing you are chasing, the
rule belongs in the court file.

### 6. Check for a new court file before blaming core

kyed lost its roles and core got the blame; the cause was an unwired
`kyed.py` a scout had written. `ls -la centralia/courts/<court>.py` and
`grep "from . import <court>" centralia/courts/__init__.py` first, every
time.

### 7. The grade is not the port

`quality` grades A on a court with 0% headmatter coverage — it grades the
render, not the reading. `v1diff` is structurally blind on 221 of 239
courts (only 18 carry `baseline/*.json`), so **0 diffs is not a pass**;
where a court has no baseline, diff against
`/Users/Palin/Code/centralia/output/<court>/` by hand and expect v1 to be
WORSE in places (it truncates multi-row captions, leaves finality stamps in
the body, and identifies no rows at all).

**Headmatter coverage is the metric.** Report it as `n/total (pct)`.

## Definition of done for a family port

1. Page-1 dump of parent and child diffed, and the difference named in the
   new file's docstring.
2. `from . import <court>` present in `centralia/courts/__init__.py`.
3. `harness/cli.py render <court>` — all valid, 0 residual.
4. Coverage measured off `hmrow` rows, reported as a fraction.
5. Every emitted role read end to end for mis-tags — a confident wrong role
   is invisible to every oracle.
6. One sentinel pinned per FORMAT (not per record) via `cli.py guard --add`.
7. Core defects REPORTED to the coordinator, never patched by the porter.
