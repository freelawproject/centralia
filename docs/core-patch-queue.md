# Core patch queue

Diagnosed and proved by the port agents, NOT yet applied. Each was reported
with evidence; none is speculative. Apply serially, `guard` behind each.

## Two sentinels are pinned on a KNOWN-DEFECTIVE reading

These were pinned on 2026-08-19 to lock their courts, but their current
signature is the bug, not the truth. **Re-bless them (`guard --add <stem>`)
when patch 1 lands — do not treat a diff there as a regression.**

- `alaska/alaska_democratic_party_and_anita_thorne_v._director_carol_beecher_in_her`
  pinned `['majority','dissent','dissent']`; the majority is EMPTY and pages
  2-22 of its body are filed under the dissent.
- `alaskactapp/brett_talmadge_v._state_of_alaska` pinned
  `['order','concurrence','concurrence']`; the first byline of an announced
  run is one core cannot parse (patch 2), so it comes back as a one-row order.

## 1. An announced writing takes the majority's body — `resolve/assemble.py`

A court may print a RUN of byline rows under its roster: the first is the
majority's, the rest announce separate writings that begin many pages later.
Assembly opens a writing at each, so the majority comes back empty and its
body is filed under the announced writing.

    p2 top 167  'PATE, Justice.'
    p2 top 183  'CARNEY, Justice, dissenting.'   <- announcement
    p23 top 85  'CARNEY, Justice, dissenting.'   <- the dissent itself

The rule: **a byline immediately followed by another byline with no prose
between them announces a writing that has not begun; only the first of the
run opens one.** v1 solved this in `BaseAlaskaExtractor.find_authors` by
collapsing consecutive byline segments to the first. Affects alaska (1
record), alaskactapp (6).

## 2. `_reversed` does not know 'writing for the Court' — `resolve/bylines.py`

~line 726 tests the majority markers `("for the court", "opinion of the
court")` with `low.startswith(mk)`, but alaskactapp writes `Judge HARBISON,
writing for the Court.` — no marker matches, `verb = "writing"` is not in
`_DELIVER_VERBS`, and the byline returns None. Add `"writing for the court"`,
and let the marker's tail carry a kind clause (`Judge WOLLENBERG, writing for
the Court and concurring separately.` currently types as a concurrence when it
is the majority). 4-6 alaskactapp records.

## 3. Missouri signs at the END of every writing — `resolve/assemble.py`

`terminal_author` (~line 566) demotes a trailing byline to a signature only
when `len(starts) == 1`. mo signs every writing at its end, so on a
majority+dissent record the first signature OPENS a writing and the majority's
body is stranded — and each real author is credited with the writing BELOW his
signature:

    treasurer_of_the_state_of_missouri…:
      [majority '' 37 blocks] [majority 'ROBIN RANSOM' 54] [majority 'W. Brent Powell' 0]
      truth: Ransom wrote the first, Powell the second.

Not a two-line patch: where EVERY start is a short signature segment (<=2
lines, <=40 chars) standing after body prose, each byline CLOSES the writing
above it — the writing loop needs `(start, end, author)` triples instead of
opening anchors. v1 inverted the byline pipeline in `MissouriStyle.find_authors`.
13 mo records. Payoff: mo B/0.61 -> A/0.05.

## 4. The letter-spaced byline fold is ASCII-only — `resolve/bylines.py`

Two additive widenings, sandbox-verified on arizctapp (5 unbylined majorities,
`O’ N E I L, Judge:` and `V Á S Q U E Z, Presiding Judge:`):

    # line ~224 — the fold admits only [A-Za-z], so an accented or
    # apostrophe-tracked surname never folds
    _sp = re.match(r"^((?:[^\W\d_][’']?\s){2,}[^\W\d_])(?=[,.:;]|\s|$)", text)

and `_NAME` (~line 163) must admit the apostrophe as an alternative (it uses
`[^\W\d_]`, which is letters-only). The `is_caps_name` docstring already
claims `D'AURIA` works; the prose regex does not deliver it, so this is latent
for any court with an Irish or Hispanic surname on the bench.

## 5. A space that advances nothing is not a space — `pdfio/quirks.py`

Arizona stacks up to 16 literal `' '` glyphs on one point; the one surviving
`drop_overstruck` reads as a separator, giving `No.  CV- 24-0013-PR`,
`red- light`, `§ 28- 1521`. pdftotext sets none of them because the following
glyph starts ON TOP of the space:

    ' ' x0=301.59 x1=304.59   then  '2' x0=301.59

Add `quirks.drop_dead_spaces(chars, pm.event)` after `drop_overstruck` in
`pdfio/build.py:169`: bucket non-space chars by `round(x0*2)`; drop a
whitespace char when a non-space char starts within ±0.5pt of its x0 and
within 2.0pt of its top (the vertical tolerance is needed — the stacked spaces
carry a different `top` from the glyph they sit under). ariz mean 0.34 -> 0.13.

## 6. A running head below core's repeat floor — `resolve/furniture.py`

`_band_keys` needs `n >= 0.4 * n_pages`. Two distinct failures:
- **arizctapp/cervantes_v._state**: 32 pages, three writings, so `Opinion of
  the Court` prints on only 5 and is never learned — it leaks into the body on
  pages 2,3,4,7,9. Suggested rule: in the TOP band, a row repeated on >=2
  pages NONE of which is page 1 is a head regardless of type size.
- **alacrimapp/william_chad_randolph** (2pp): a running head never prints on
  page 1, so on an n-page document its maximum count is n-1 and the floor is
  unreachable BY CONSTRUCTION. `floor = min(floor, max(1.0, n_pages - 1))` for
  the top band — but dropping to 1 risks eating a page-2 opening line, so the
  safer variant admits a count-1 top-band key only when it is docket-shaped
  AND equals a docket the document prints on page 1.

## 7. A reader's declared `doc_type_final` is thrown away — `pipeline.py`

~line 472 tests `meta.doc_type`, still UNKNOWN at that point, so core WITHDRAWS
a reader's claim on a document with no writings (ark's clerk hand-down sheet:
`court.reader_withdrawn: claim cost the document its writings`).

    -    _body_expected = meta.doc_type not in m.NO_BODY_EXPECTED
    +    _declared_type = _court_hm.get("doc_type_final") if _court_hm else None
    +    _body_expected = (_declared_type or meta.doc_type) not in m.NO_BODY_EXPECTED

and the matching line in the warning filter (~511). Only courts declaring a
`NO_BODY_EXPECTED` type are affected. NOTE the companion harness change: after
this, the notice loses its opinions section and picks up `no-opinions` (+8,
grade D) — `harness/quality.py` must not score a notice's empty body as a
defect. Also `mo/john_doe_v._eric_t._olson` types `order` instead of
`majority` for the same reason at a different call site (assemble runs at
pipeline:458, `doc_type_final` is applied at 1674).

## 8. A heading does not open in lower case — `resolve/assemble.py`

The `_titled` doc-type-heading scan (~line 938) takes any line under 80 chars
on pages 1-2, and `heading_doc_type` matches on the first word — so a
PARAGRAPH'S LAST LINE qualifies: `'order and judgment and remands the case.'`
-> ORDER, `'judgment in all respects.'` -> JUDGMENT. Harmless until a court
reader claims page 1; then the false heading is the first one left, `_named`
anchors there, and the majority is BISECTED at the page turn (mo/vernell_beach,
mo/millstone). Fix: `if _t[:1].islower(): continue` inside the line loop.

## 9. The page-1 masthead seal renders as opinion content — `pipeline.py`

`_is_figure`: mo's court seal is 91x90pt at y=72-162, ABOVE the banner, and
`_im.top > pm.height * 0.08` is 72 > 63.4, so it passes as a figure — **45 of
50 mo opinions now open with the seal.** v1 put it at the head of the
headmatter. Either exclude an image standing above the page-1 caption band (it
is stationery) or give a reader a seam to claim it: today `consumed` is line
ids only and an image cannot be claimed at all.

## 10. Publication status read out of a footnote's own citation — `pipeline.py`

The `_UNPUB` scan (`low.startswith(u) or u in low[:60]`) matches inside a
footnote: *"…providing text of unpublished order in Artemie v. State, No.
S-12026 (Alaska…"* stamps the order `unpublished`. A publication flag is a row
the court sets ALONE. Suggested: `if len(low) <= 80 and any(low.startswith(u)
for u in _UNPUB)`. Confirmed on alaska/steve_pete and 5 alaskactapp records.
Needs guard — it will move other courts.

## 11. A submission statement is not counsel — `pipeline.py`

`CONSIDERED ON BRIEFS FEBRUARY 9, 2026 OPINION FILED 02/18/26` published as
`attorneys`. 13 files are purely this (mont 7, sd 3, wisctapp 2); another 7
(ca10, ortc, njsuperctappdiv) are a submission LABEL followed by real counsel
and are arguably correct. A rule refusing a counsel criterion that carries no
name, no firm and no representation clause fixes the 13.

## 12. The disposition row is pulled into `parties` — `resolve/headmatter.py`

`nd/adams_v._state`: `parties` = `Jarrod Jashawn Adams, v. State of North
Dakota, AFFIRMED.` — `AFFIRMED.` stands 130pt below the caption, past the
docket and the origin. Core's shared party reader over-reaching on an unported
court; a port fixes it, so this is only worth patching if nd stays unported.

## 13. `¶N` renders as a heading, not inline — `resolve/assemble.py` / render

Every `¶N` on both Arizona courts renders as `<h3 class="bhead"><strong>¶1
</strong></h3>` followed by a separate `<p>`, instead of `¶1 ` inline at the
head of its paragraph. v1 renders it correctly. Corpus-wide on that family;
`quality` does not score it and `v1diff` cannot see it.

## 14. `geom.body_size` mis-measures on short slips — `geometry.py`

On a 2-page Alabama cover the 9-10pt reporter-notice band outvotes the 14pt
body, so `body_size` comes back 9.0-10.0 and core's own corner-stamp test
fails on `Rel:`. All three Alabama readers route around it by reading that
band by POSITION rather than size. Changing it moves every court's
measurements, so it wants its own pass.

## 15. A separate writing's REPRINTED COVER lands in the writing before it

**RE-SCOPED 2026-08-19 — this is NOT core's, and mich is now fixed in its own
court file.** The item's premise was that "a headmatter reader may not reach
into an assembled writing". That premise is wrong: a reader's `consumed` set
is subtracted from the segment stream at `pipeline.py:474-484`, *before*
assembly, so a court file can claim a reprinted cover today and those rows
never enter a writing at all. No `cover.reprint` decision point is needed.

Done for mich in `courts/mich.py` (`_reprint_block` / `_drop_reprints`,
called from `_read_slip` once the lead walk closes on its byline). The
candidate is identified by GEOMETRY alone — the page's first content row is
centred within 12pt AND matches the row this document's own lead cover
printed as the court naming itself, so there is no wording list — and the run
ends at the next byline, the same landmark that ends the lead walk. Recorded
as `Dropped(kind="superfluous")`, which core still mines for criteria. A run
that reaches 14 pages without meeting a byline is not this shape and nothing
is claimed.

Measured over all 50 mich records: **52 reprinted covers on 30 records, all
52 closing on a byline, and not one containing a full-measure lower-case row**
— no prose is ever inside one. `pinebrook_warren_llc_v._city_of_warren_1`
went from 359 writing blocks to 228 (131 caption blocks lifted out of the
majority); 63 pages dropped; writing counts unchanged on all 50 records.

**scotus / nj / wash can be fixed the same way, in their court files.** What
IS genuinely blocked in core is a different seam: `_syl_drop`
(`syllabus.trim`) is consulted only at `pipeline.py:923`, nested inside
`if seg.page in _syl_pages or id(seg) in _syl_pull:` (line 922), and `_msegs`
holds only `assembled.headmatter_segments` (line 723).

Still open here: pin a guard sentinel for the reprinted-cover format —
`cli.py guard --add mich/pinebrook_warren_llc_v._city_of_warren_1`. mich's
only sentinel today (`darnell_hairston_v._josh_lku`) has no reprint, so the
format is unguarded.

### The original report


**The user's call, 2026-08-19:** "when a new opinion starts [it] has the big
old case caption — that should be, if it's the same, not repeated, or placed
in the end of the previous opinion." I.e. a caption identical to the
document's own must not be reprinted, and must certainly not be filed as the
tail of the preceding opinion, which is where it lands today.

Measured over the current renders, counting body paragraphs whose text
matches one of the document's own `role="caption"` rows:

    mich        30 of  50 files · 155 rows
    scotus      25 of 100 files ·  53 rows
    nj           2 of  48 files ·   9 rows
    michctapp    unported, so not yet visible — it prints mich's paper

`mich/philip_m_ohalloran_md_v._secretary_of_state`, writing 2's last
paragraphs, interleaved with its own footnote text:

    'RICHARD DEVISSER, MICHIGAN REPUBLICAN PARTY, and REPUBLICAN NATIONAL COMMITTEE'
    'v'
    'No. 166425'
    'SECRETARY OF STATE and DIRECTOR OF THE BUREAU OF ELECTIONS,'
    'Emphasis added.'

Michigan repeats the whole caption — centred `STATE OF MICHIGAN`, the party
block, the shelf rule — on each separate writing's own cover page, and
assembly anchors the writing at the byline BELOW that cover, so the cover
falls into the preceding writing's blocks. New Jersey and scotus print the
same shape.

**Why it is core's.** A headmatter reader stops at the first byline and may
not reach into an assembled writing (mich's porter: "`syllabus.trim` cannot
reach it — it is consulted only inside the `seg.page in _syl_pages` branch,
and `_msegs` holds only pre-first-opinion segments"). Both mich's and nj's
porters diagnosed it and both declined to patch it, which was right.

**The two honest shapes**, from mich's porter:
1. let assembly open a writing at its PRINTED COVER and put those rows in
   the `Opinion.caption` field the model already has; or
2. a pre-assembly decision point (`cover.reprint`) a court answers with line
   ids to subtract, recorded as `Dropped(kind="superfluous")`.

Given the user's instruction, (2) is the closer fit for a caption that merely
repeats — nothing court-written is lost, because the rows are a verbatim
repeat of the block that already renders whole at the head of the document,
and `Dropped` keeps them attested. (1) is better if the reprinted cover ever
differs from the document's caption; check before choosing.

**Blocked on:** `resolve/assemble.py`, held by the mass agent while it lands
patch 1 (the standalone disposition). Start this the moment that reports.

## 16. A stacked panel roster at the foot of a writing is mangled 3 ways

Found by nd's porter, 2026-08-19, then re-measured after I pushed back on its
first estimate — it had under-counted. **49 of nd's 50 records**, in three
modes on the same printed object:

    welded into one paragraph   37   '[¶4] Lisa Fair McEvers, C.J. Jerod E. Tufte Jon J. Jensen …'
    read as a BLOCKQUOTE         8   the stack is indented on both margins (pederson, medina)
    torn in two                  4   half paragraph, half blockquote (volker_v._nygaard)
    clean                        1

nd signs at the END, one name per line at x0=108.0, each line 15.3-36.9% of
the measure, where body prose in the same writing runs 93-100% on every line
but its last. The page's own geometry separates them; nothing joins them but
paragraph assembly's default "consecutive lines are runover". Core's only
signature lift (`assemble.py` ~1640) triggers on `/s/`, which nd never prints.

**The fix, written and verified but NOT shipped** (the porter did not own the
file): inside one writing, a run of >=3 consecutive lines whose every line's
ink is <=45% of the measure, at a SINGLE left edge, is a stack the page
newlined — re-emitted one Paragraph per printed line, IN PLACE, so the
writing keeps every line and the page keeps its order.

The subtlety that took it two passes: the stack must be built from the
INNERMOST left edge plus at most ONE opening row a single 36pt step out (the
row carrying the pilcrow). Without that bound, `state_v._reese`'s short
closing sentence `[¶13] We affirm the judgment.` (38.5% of measure, at the
body rail) is swallowed into the roster.

Verified by wrapping `assemble()` rather than editing core: 0 of 50 still
mangled, quality unchanged at A/0.01/100%, residual 0, and the awkward cases
right — pederson's blockquote, volker's torn roster reunited, haskell's
concurrence roster, and `eggleston`/`adoption` where a REAL paragraph follows
the roster (`[¶4] The Honorable Donovan J. Foughty, Surrogate Judge, sitting
in place of Crothers, J., disqualified.`) stays a paragraph.

Patch text with its four declared constants: `/private/tmp/nd-port/patch.py`
(insert above the `# Signature lift:` comment). Proof render:
`/private/tmp/nd-port/patched/`.

**Expect one guard diff:** `nd/interest_of_w.j.` goes `op0_blocks: 3 -> 6` —
four welded names becoming four blocks. Re-bless it together with the `hm`
13 -> 16 from the port itself.

**Almost certainly not nd-only.** Any court closing a writing with a stacked
panel hits the same three modes, and the test names no court. Needs a corpus
guard run behind it. Mode 2 (blockquote misclassification) may be fixed or
changed by the `_page_bands` work in item 13's wave — land that first and
re-measure before applying this.

**Blocked on:** `resolve/assemble.py` (mass agent) and `resolve/segments.py`
(segmentation wave). Apply when both land.

## 18. Doc-type heading below a claimed headmatter — drop the dispo conjunct
`centralia/resolve/assemble.py` ~879. TWO agents converged independently (mass,
gactapp). A paragraph's own last line is naturally short, so it clears the
0.8-of-measure guard and is read as a doc-type HEADING; under a claimed
headmatter that anchor cuts one writing in two at a page break. mass fixed it
narrowly with `and _is_dispo_line(head)`; gactapp proves the conjunct should go
entirely — `landren_gipson` 2 writings -> 1, no other gactapp record changes.
Core's own comment says dropping such an anchor "can only ever merge the two
starts back into one". NOT APPLIED: corpus-wide impact unmeasured. Measure the
writings-count delta across all ported courts before landing.

## 19. Panel-roster stack — LANDED 2026-08-19
`_STACK_INK/_STACK_ROWS/_STACK_EDGE_TOL/_STACK_STEP` + the unweld block above
the signature lift. nd 49/50 mangled -> 0/50. moctapp's phantom trailing
writing also gone. Cap stays at 0.45: measured 0.45->0.60 newly catches 20
same-edge runs in a 10-court sample, all real prose (counsel wraps, caption
wraps, footnote runs). Double-leading fails as a discriminator (nd's own
rosters are 1.00x the body lead). Courts whose roster rows carry a name AND a
role exceed the cap and must handle it in their own file — routed to moctapp.
