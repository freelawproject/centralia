# Porting a court's headmatter reader

Written after porting ca2 (the `stated-term order` and `ladder` families) and
scotus. ca2 went from **A 0.47 / 92% A/B with 20 of 73 files marked failing by
a human** to **A 0.18 / 100% A/B, 73 valid, 0 errors, 4 v1 diffs**. These are
the rules that got it there, and the traps that cost the most time.

The old engine reads some courts with a court-owned walker. The new engine
exposes one seam — `headmatter.read` — where a court file may do the same. It
runs after segmentation and before assembly; a court that answers claims its
headmatter lines and they are subtracted from the stream.

## The method

**1. Use the oracles, not your eyes.** Three exist, and they disagree with
each other in useful ways:

| oracle | answers | command |
|---|---|---|
| `guard` | is this document still put together the same way | `cli.py guard [court]` |
| `v1diff` | do we find the writings v1 found | `cli.py v1diff <court>` |
| `quality` | does the render carry visible defects | `cli.py quality <court>` |

None of them saw the headmatter until this port added the `hm-unread` metric
(a row a reader did not identify). `v1diff` reported **2 diffs while a human
marked 20 files failing** — an oracle that cannot see the thing you are
working on will report green all day.

**2. Get the human's marks early and correlate.** One review pass over 73
files produced the signal that found everything else:

| | files marked failing | files marked good |
|---|---|---|
| headmatter left unread | **62%** | **10%** |
| counsel rows found | 2.5 | 9.7 |
| style | 18 of 24 stated-term | 37 of 46 ladder |

That told us which *component* was broken, not which files.

**3. Diff against the old engine's rendered output**, at
`/Users/Palin/Code/centralia/output/<court>/`. Its headmatter rows are under
`<section class="block headmatter">`. Expect intentional differences
(we drop the running head and the convening recital; it keeps them).

**4. Prove a defect is yours before fixing it.** Pop the decider and re-run:

    from centralia.resolve.evidence import _DECIDERS
    saved = _DECIDERS.pop(("headmatter.read", "<court>"))

If the file fails the same way without your reader, it is a core gap.

## The rules

**Port the style DISPATCH, not just the reader.** The old
`headmatter_style()` looks trivial because the real decision happens upstream.
Substituting a text test for it misrouted every en banc denial. A style is a
LAYOUT CONTRACT named for a landmark it always prints — for ca2, the recital
(`At a stated term of the United States Court of Appeals…`), not the title.

**A claim must be total: consumed ⇒ placed or recorded.** Every line a reader
removes from the stream must end in an item, a block, or a `Dropped`. Three
separate bugs were this one bug (running heads read but not recorded; counsel
continuations merged into an entry's text while their line ids were dropped
from its `prov`; counsel labels passed over). Unaccounted lines resurface as
residual content and put the file in `review`.

**Provenance survives a merge.** Merging a continuation merges the text; the
line ids have to merge too.

**Bound every state — the original does not have to.** The old readers walk a
headmatter span the extractor already delimited, so `state == "counsel":
append` to the end is safe there. A reader walking raw pages has no such
bound, and each state needs its own end:

- the caption ends at BODY PROSE — full measure, lower-case, **at the rail**
  (a caption's own wraps are indented from it), and only where no rule will
  close it;
- the counsel block ends at a row outside every column the block itself uses;
- the whole reader ends at the first byline.

**Geometry decides; the court declares which geometry applies.** Wrap vs. new
element is measurable (scotus: 1.22× the type size vs 1.9×). Party vs. status
vs. pivot is a COLUMN question. But a label grid has a wrap's geometry and
means something else, so the behaviour is a declared fact (`caption_wraps`,
`para_indent_min`), never a global rule. Measure the caption rail INSIDE the
caption band, never across the headmatter.

**Closed vocabularies are legitimate; open ones are not.** Never read a party
or court NAME by wording. Party STATUS, BENCH words and generational SUFFIXES
are finite role vocabularies. Without them a roster yields a judge called
`Circuit`, one called `and`, and `RAYMOND J. LOHIER, JR.` as two people.
Statuses are italic on one style and roman on another.

**Keep the printed form beside the parsed form.** `panel_line` and `panel`;
`caption` and `case_name`. Build the name from the party names either side of
the pivot — joining caption rows wholesale yields `AMANDA BROOKS,
Plaintiff-Appellant, BRIGHT HORIZONS …`.

**A reader that claims a region inherits its furniture.** Running heads, the
citation notice, the convening recital, line-number gutters. Reuse core's
measurements (`repeated_top_keys`, `gutter_column_ids`) rather than matching
wording — a running head takes every form (`23-258 (L); 23-354 (L) Havlish v.
Taliban; Aliganga v. Taliban`).

**A notice is a RUN, and it closes on its own sentence.** Two cues identify
it; its middle and closing lines carry one or none (`REPRESENTED BY
COUNSEL.`). Follow the type SIZE, but end at the first line that ends in a
period — size alone runs away when the notice shares the banner's size.

**New criteria keys must be DECLARED.** `setattr` accepts any name, so an
invented key attaches silently and never serializes.

**Never reach into a writing.** The reader stops at the first byline, and no
later pass may take content out of an assembled opinion.

## Layout contracts found so far

| court | contract | what marks the zones |
|---|---|---|
| ca2 | `stated-term order` | typed underscore rules; caption read by column |
| ca2 | `ladder` (engraved / plain / numbered paper) | landmarks in fixed order, not the rules |
| ca1 | `whitespace-zoned` | NO rules at all — a 27pt stand-off against a 13.6pt leading |
| ca4 | `ruled bands` | a DRAWN 108pt rect centred on the page axis, between rows |
| scotus | per-writing covers | the section name printed in every page's running head |
| ca6 | `rail and fence` | the caption's own COLUMN DIVIDER — a box rail or a stacked `)` |
| ca9 | `ruled caption box` | the caption's DRAWN divider — a vertical rule with a horizontal across its head and another across its foot; the head and foot rules END at the divider, so the column is readable even where pdfio drops the vertical |
| ca8 | `engraved ladder` | a BLACKLETTER masthead over zones each fenced by a TYPED underscore rule on the page axis; the zone holding an ITALIC row is the caption, the zone at the BODY RAIL is the roster, the origin is what is left |
| ca5 | `typed sandwich` | a rule PAIR centred on the page axis in two invariant measures — SHORT 90–106pt around the docket, LONG 234–252pt around the origin; the MEASURE names the section |

Three notes from ca5 that generalize to any ruled court:

- **The same measure OFF the axis means something else entirely.** ca5
  types its footnote separator at 165pt and its consolidation divider at
  the LONG measure, both ~80pt off the axis. Width alone takes both; the
  axis takes neither. Test the axis first, the measure second.
- **A drawn rule whose ends coincide with the row above is an UNDERLINE,
  not a fence.** Same test ca1 needed for its counsel underlines,
  arrived at independently — it is the general way to tell a rule the
  court set as structure from one it set as emphasis.
- **A caption row that leaves the body rail is flush right to the
  CAPTION'S OWN rail** — measured inside the band, never across the
  headmatter. A status label long enough to start left of the page's 0.6
  mark still reads as left-aligned to a shared test, and renders as an
  indent instead (ca5/mcnutt).

### Two-column captions: read the divider, not the text (ca6 is the reference)

**ca6 is the standard to hold every two-column court to.** It is the first
port where the caption's own geometry did all of the work and nothing was
inferred from wording. When we reach another court that sets its caption in
two columns, this is the shape to reproduce:

- **The divider IS the parser.** ca6 draws a rail between the two columns,
  and the glyph it draws it with names the paper: box-drawing characters
  (`┐ │ ┘`) on the 65 published slips, a stacked `)` on the 38 unpublished
  ones. Nothing is matched against text to decide which layout this is.
- **The divider defines the zones, so the columns are never guessed.** What
  stands ABOVE the rail is the masthead; INSIDE it, left of the rail, the
  parties; right of the rail, the origin and the `OPINION` label; the single
  row BELOW it is the panel. Column membership is decided by which side of a
  drawn line a row sits on — never by what the row says.
- **Dispatch on the rail, not on the flag beside it.** The court prints
  `RECOMMENDED FOR PUBLICATION`, and it would be the obvious thing to key
  on. ca6 keys on the rail instead and treats the flag as a payload. Over
  the corpus the box rail and the 110pt drawn rule co-occur on all 65
  published records and on none of the 38 unpublished ones — the geometry
  is the more reliable signal, and it is the one that survives a court
  changing its wording.
- **No rail, no claim.** A record that draws neither divider is not this
  contract and the reader returns `NOTHING`. Better to leave a record for
  core than to force it through the wrong contract.

This is exactly the rule we already committed to — split by geometry, not by
searching and regex — and ca6 is the file that shows what it looks like when
followed all the way down. Result: **A, mean 0.19, 99% A/B**, headmatter
fully read.


ca4 is worth studying as the clean case: every one of its 103 records fences
every section, page-1 fence counts run 2–9, the rule is 108.0pt wide and
invariant, normally `x0=252` on a 612pt page and 18pt left of that on an
off-axis caption. Two consequences generalize:

- **The band is the unit of meaning, not the row.** Ask once per band what
  section it is. That is what keeps a roster row that parses as a byline
  ('GILES, United States District Judge for the Eastern District of
  Virginia, sitting by') from ending the reader — it is inside a fenced
  roster band, so it belongs to that band whatever it looks like alone. Run
  the byline test only in the trailing UNFENCED region.
- **A reader that claims the block must re-emit the fences.** Core draws
  them in `read_headmatter`, and that pass only runs on rows the reader left
  behind; a total claim silences it.

## Core invariants this port established

These live in `pipeline.py` / `assemble.py` and apply to every court:

- **a writing is never bisected** — a row filed elsewhere that lies inside a
  writing's span is put back into it;
- **counsel printed inside the headmatter stays there**, its text copied into
  `criteria.attorneys`; only a court declaring `counsel_after_writings` (ca3)
  gets a separate section;
- **the headmatter keeps the page's order** — a reader's rows and core's
  leftovers are merged by position, never appended;
- **an empty writing is not a writing** — it is dropped and any footnote it
  held goes to the headmatter;
- **a court reader may improve the headmatter but never cost the document its
  writings** — if a claim leaves no writing, release the anchor heading, and
  failing that withdraw the claim entirely;
- where a reader claimed the headmatter, **an unread row below it belongs to
  the writing**, and core's appeal-from veto and caption-cell/run-on lifts are
  suspended (they assume an unclaimed front matter).

## Traps that cost the most time

- `_named = _titled if _titled else None` — **index 0 is falsy**, so the
  rescue anchor was discarded and unsigned orders came back with no writing.
- `§` is not a footnote mark (`§ 1983. This claim arose…` opened a note and
  swallowed the summary).
- A footnote mark ALONE on its row opens a note whose first word is
  capitalised — the "continue while lower-case" rule ends it immediately.
- Same-row pieces: a justified line split at wide gaps looks like rows outside
  the gutter and ends the counsel block mid-entry.
- A folio may be dressed (`- 4 -`), and a docket-shaped row is a running head
  only in the TOP BAND — mid-page it is the caption's own docket.
- A bare `v.` row is the ordinary multi-row caption; joining it into a
  pivot-wrap rule destroyed `parties` **corpus-wide** and was caught only by
  the guard.

## Open items

- `ala/790_montclair_llc_v…` lost its `disposition` criterion during this
  work; the guard is blessed to the new behaviour, so this is recorded here
  rather than hidden.
- `hm-unread` catches 10 of 24 human-marked failures with 2 false alarms. It
  sees rows nobody claimed, never rows claimed WRONGLY, so it needs a
  companion metric before it can be trusted alone.
