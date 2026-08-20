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

## 20. Footnote zones are measured BEFORE the court reader's claim

Reported by ri's porter, 2026-08-19.

`pipeline.py:449-464` measures the footnote zones, and only afterwards does
`court_decides("headmatter.read")` run (:485); the reader's claim is then
subtracted from `segments_by_page` alone (:495-502). So a drawn rule the court
uses for something else has already been read as a footnote separator by the
time the court file says what it is, and the reader has no way to withdraw it.

Rhode Island closes every record with the Clerk's cover sheet, a label/value
grid fenced by drawn rules. On 7 records its FIRST fence reads as a footnote
separator, so the grid's bands land in the last writing's last footnote —
`american_express_national_bank_v._anna_perretta_1` has footnote 5 =
'No. 2024-396-Appeal. Case Number (KC 21-1031) Date Opinion Filed ...'. The
bands therefore render TWICE: once as the endmatter the reader claimed, once
inside the footnote. Identical with the ri decider popped, so it is core's.

The fix is an ordering one and its blast radius is every court with footnotes,
so it is queued rather than attempted: either the zones are re-measured after
the claim is known, or the claim also subtracts from the zone lines.

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

## 18. A letter-spaced 'Chief Judge' concurrence is swallowed by the majority — `resolve/bylines.py` or `resolve/assemble.py`

Found 2026-08-20 by guard, NOT by eye: `arizctapp/cervantes_v._state` was
pinned `['majority','concurrence','dissent']` on 08-19 and now returns
`['majority','dissent']`. This is a REGRESSION against a pin that recorded
the correct reading, so something between 08-19 and 08-20 caused it.

The paper prints three bylines, all letter-spaced:

    T H U M M A, Judge:                          <- majority, parsed
    H O W E, Chief Judge, specially concurring:  <- LOST
    J A C O B S, Judge, dissenting:              <- dissent, parsed

No text is lost — the BOUNDARY is. op0 (the majority) now contains
`H O W E`, `specially concurring`, `My concurrence` and `translated to
English`, i.e. Howe's whole writing is appended to Thumma's.

Letter-spacing is NOT the cause: `J A C O B S, Judge, dissenting:` parses
from the same font treatment. `arizctapp.py:185-186` already lists
`titles=("Judge","Presiding Judge","Chief Judge","Vice Chief Judge")`, so
the title is not the cause either. What distinguishes Howe's row is the kind
clause **'specially concurring'** and the two-word title in combination.
Prime suspects, all landed after the pin: b114ccf 'signature blocks are not
writings', 28c2f7d 'Signature block takes the whole /s/ run', c96b0d7
'Conformed signature runs unweld' — a byline mis-read as a signature would
be dropped as an opener and its prose welded to the preceding writing,
which is exactly the observed shape.

**The pin is deliberately left FAILING** as a standing alarm; do not
re-bless `arizctapp/cervantes_v._state` until the concurrence returns.
arizctapp is for the same reason NOT marked complete.

Related but separate, and already verified benign: ariz's 6 pins and 4 more
arizctapp pins failed only on `opN_blocks` roughly halving (129->67,
281->149, 220->109, 169->93, 136->87, 89->50, 71->45). ops/hm/criteria/
attorneys/summary/syllabus/residual/status all held, so that is paragraph
re-uniting (representation-only) and those 12 pins were re-signed on 08-20.

## 19. A GUESSED caption band eats body mass and blocks signature demotion — `resolve/assemble.py`

Diagnosed and measured by the dc agent on 2026-08-20, with a corpus-wide
blast radius. NOT applied: four porters held the tree.

Core's two signature demotions (`terminal_author`, ~763-793, and the
end-signature cluster, ~798-812) each require `body_before >= 10` lines, and
each discounts page-1 segments falling inside `caption_band`. Where a court
draws no caption rules to measure, `captions.py:79` FALLS BACK TO A GUESS —
`band = (60.0, page_height * 0.55)` = (60.0, 435.6) — and on a short order
that guess reaches into the body: `dc/in_re_correa` opens its first body
paragraph at top 388.07. Ten of its 18 body lines are discounted,
`body_before = 8 < 10`, the demotion never fires, and the trailing
`PER CURIAM` opens a SECOND writing with ZERO blocks.

The patch, gated so it can only affect documents whose headmatter a court
reader actually claimed:

    # ~line 763, above `terminal_author = None`
    # A CLAIMED HEADMATTER LEAVES NO CAPTION APPARATUS BELOW IT. The band is
    # a GUESS where the court draws no caption rules — captions.py falls back
    # to (60.0, 55% of the page) — and on a short order that guess reaches
    # into the body: dc's one-page bar order opens its first paragraph at top
    # 388.1 of a 792pt page.
    _cap_disc = None if headmatter_claimed else caption_band

then substitute `_cap_disc` for `caption_band` AT THE TWO BODY-MASS COUNTS
ONLY — `body_before` (~775-778) and `_body_before` (~800-803). Nothing else.

**Measured over all 4,972 PDFs of the 84 reader courts:** the band
mis-excludes body mass across the `>= 10` floor on 26 files; the
`headmatter_claimed` gate reduces that to 9; of those only 4 change their
writing signature, and all 4 become CORRECT:

    dc/in_re_correa        order ''+per-curiam(0 blocks) -> per-curiam 4 blocks
    dc/in_re_kester        order ''+per-curiam(0)         -> per-curiam 3
    dc/in_re_tucker_jr.    order ''+per-curiam(0)         -> per-curiam 4
    cadc/in_re_donald_trump_1  order ''+per-curiam(2)     -> per-curiam 8

The cadc change AGREES WITH ITS v1 ORACLE, which reads that record as one
writing. Five more files flip a count without changing their signature
(cadc/joe_neguse, fla/equal_ground, nh/atl._anesthesia,
sc/state_v._john_joseph_erb, wis/planned_parenthood). Nothing is lost in any
of the four: the `PER CURIAM` row stays as the writing's last block and
still supplies the author. Proof driver and flip scan:
`scratchpad/dc-fixes/patched.py`, `flipscan.py`, `flips.jsonl`. Caveat
recorded by the agent: `wis` was held by another porter, so its baseline may
shift — re-verify that one row.

**Do not pin `dc/in_re_kester` until this lands** — its signature today is
the bug. After the patch, pin these three (one per dc format):
`dc/allen_v._united_states` (axis slip, announced concurrence-in-part),
`dc/in_re_kester` (rail bar order, head-margin stamp, page-crossing
sentence), `dc/in_re_meta_platforms_inc.` (an `in re` slip whose docket is
CENTRED, so wording would misroute it where geometry does not). Same three
stems for a new `"dc"` key in `tests/criteria_manifest.py`.

Note `dc/in_re_kester` becomes over-split only AFTER the margin-stamp fix
landed: dropping the 1-line stamp segment took its `body_before` from 10 to
9, across the same floor. Same defect, same patch.

## 20. The folio top-band threshold disagrees with the key-learning band by 0.01 — `resolve/furniture.py`

Diagnosed by the conn agent on 2026-08-20, verified at runtime by
monkeypatching rather than editing core. NOT applied.

Connecticut's Law Journal prints its volume folio at top **150.5 of a 792pt
page = 0.1900252**, two hundredths of a point ABOVE a `0.19` cut.
`furniture.py:137` already documents this exact number ("Connecticut's
reporter row sits at exactly 0.1900 of a Law Journal page") and the
key-LEARNING band was already widened to **0.22** for this same row — but the
folio DECISION at lines ~378/384 still tests `0.19`. The two bands disagree
by a hair, so the bare folio falls through as content.

    -        if is_folio_text(text) and (frac <= 0.19 or frac >= 0.82):
    +        # Top band 0.20, not 0.19: Connecticut's Law Journal folio stands
    +        # at 150.5 of 792 = 0.190025 — two hundredths of a point below a
    +        # 0.19 cut. The key-learning band above was already widened to
    +        # 0.22 for this same row; the two must agree.
    +        if is_folio_text(text) and (frac <= 0.20 or frac >= 0.82):
    -            if frac <= 0.19:
    +            if frac <= 0.20:
                     return "folio"

0.20 is the narrowest value that clears 0.1900252. Consequence today, on
pages 7+ where a headmatter reader cannot reach (inside an assembled
writing): stray numeric blocks and paragraphs split mid-sentence —
`state_v._matheney_1` leaks `['216','219','222','223','226','229','230',
'235','238']`, `state_v._johnson_2` leaks `['99','100','101','104','107',
'108','114','122','127']` and `['141']`.

Verified effect (scratchpad/conn-lawjournal/stray20.py): every stray numeral
disappears and paragraphs rejoin across pages — matheney majority 87 -> 62
blocks, johnson_2 80 -> 51 and 67 -> 44, walton 4 -> 3. `residual` stays 0
and the 38 advance-release records are unaffected.

**Blast radius is wider than conn**: any court printing a bare numeral or
`Page N` between 19% and 20% of page height. This one wants a full `guard`
run behind it, unlike item 19 whose radius was already measured at 4 files.

## Pending sentinel work once the tree is quiet

- `conn/amadasun_v._armstrong_town_clerk_of_south_windsor` was **already
  regressed before any work today** (`syllabus 8->0`, `hm 12->80`, `parties`
  added): the fixture predates conn's existing format-A branch. Investigate
  whether the pin or the reading is wrong BEFORE blessing — do not bless it
  blind.
- Pin, one per conn format: `conn/del_rio_v._amazon.com_services_inc._1`
  (Law Journal extract), `conn/walton_v._walton_1` (extract with NO syllabus
  band, 3pp, body_size 8.0 — the finder's blind spot),
  `conn/state_v._johnson_1` (slip separate opinion: notice only, no caption).
- Pin dc's three AFTER item 19 lands (see item 19).
- Apply the drafted `harness/quality.py` `_CITE_AFTER` fix (va's `joins`
  false positive) and the va + conn + dc `tests/criteria_manifest.py` entries.
- Item 19 is STAGED and anchor-verified at
  `scratchpad/apply_item19.py` (`--check` to re-verify, no args to apply).

## 21. `_abbrev` finds the abbreviated title INSIDE the given name — `resolve/bylines.py`

From the wis port, 2026-08-20. Verified in isolation. **The cleanest patch in
this queue — one line, and it changes a writing's TYPE, not just its label.**

`bylines.py:667` is `end = text.find(ab) + len(ab)`, searching from index 0.
On `JILL J. KAROFSKY, J., concurring.` the first `J.` is the one inside
*JILL J.*, so `end=7`, the tail becomes `KAROFSKY, J., concurring.`, and the
kind clause is never reached: the printed byline truncates to **`JILL J.`**
and the CONCURRENCE types as a **majority**. Hits `state_v._jobert_l._molde`
and its duplicate.

`after` is always a suffix of `text` at that point, so:

    -            end = text.find(ab) + len(ab)
    +            # THE TITLE IS FOUND AFTER THE NAME, not from the head of the
    +            # row. A given name may itself end in an initial ('JILL J.
    +            # KAROFSKY, J., concurring.' — wis), and searching from index 0
    +            # found the 'J.' inside the NAME.
    +            end = (len(text) - len(after)) + len(ab)

Checked: the wis case goes `end 7 -> 20` (tail `', concurring.'`), while
`HAGEDORN, J. …`, `JILL J. KAROFSKY, C.J. …`, `JANET C. PROTASIEWICZ, J. …`
and `REBECCA GRASSL BRADLEY, J., delivered …` all keep an identical offset.
Any court whose justices carry a middle initial before the title is exposed,
so this is worth a guard run even though the change is tiny.

## 22. A masthead below the first text row is planted in the writing as a figure — `pipeline.py`

From the wis port. Affects **49 of 49** wis records.

`pipeline.py:384` requires `_im.top <= _first_text` for a masthead. wis prints
its public-domain cite (`2025 WI 23`, top 105.2) ABOVE the letterhead, so both
the masthead (top 129) and the seal (top 170) fall below the first text row.
The seal then passes `_is_figure` (74x72, top>8%, bottom<92%) and is planted
inside the first writing as `<img alt="figure">`, while the masthead fails it
(h=34 < 40) and is dropped as `graphic 364x34pt`.

                _is_masthead = (pm.number == 1
                                and (_im.top <= _first_text
    +                                or _im.bottom <= pm.height * 0.35)
                                and _w <= pm.width * 0.55

wis's seal bottom is 242 of 792 = 0.306. This widens a corpus-wide test —
full `guard` run before blessing.

## 23. A two-row running head loses its second row — `resolve/furniture.py`

From the wis port. **12 of 49** wis records.

wis heads every continuation page with the case short name over the WRITING's
name (`Opinion of the Court`, `Order of the Court`, `JUSTICE ZIEGLER,
dissenting`), both at body size 12.0. `_band_keys`
(`furniture.py:168-170`) admits a per-writing head only through the
sub-body-size exemption, and on a record with several writings that head
repeats on fewer than 40% of pages — so it is not furniture and welds onto
the page's first paragraph (`…to receive these filings.` / `Order of the
Court pursuant to WIS. STAT. § 801.50(4m)…`). The 37 records that work are
the ones whose lead writing covers >=40% of the sheet.

Proposed rule, same place: a top-band key sharing a baseline with a key
already proven furniture, on 2+ pages, is the other row of the same head.
Changes furniture for every court — wants its own corpus run. Note this is
the same FAMILY as item 20 (folio bands) but a different mechanism.

## 24. `publication_status` read off a body citation — `pipeline.py`

From the wis port. 2 of 49 wis records, confirmed pre-existing (identical
with the reader popped).

`pipeline.py:725` guards with `_STATUS_CITES_ANOTHER`, which fails to match
`unpublished, unauthored summary affirmance of the court of appeals, state`
(`state_v._kordell_l._grady` para 1) and `unpublished slip op. (wis. ct. app.
may 14, 2024) (per curiam) (reversing the`
(`wisconsin_department_of_corrections…`). Both records come back
`unpublished` when they are published slips. The pipeline's own comment
already anticipates this family ("wis cites an 'unpublished order at 5-10'");
the guard needs the court-abbreviation form (`ct. app.`) and the
reporter-less `slip op.` as additional cues.

## wis sentinels to pin (one per band composition, all reading correctly)

    wis/josh_kaul_v._wisconsin_state_legislature          5 fences, REVIEW origin on two rows, 2-row announcement
    wis/office_of_lawyer_regulation_v._bryant_h._klos     4 fences, matter title over caption, no announcement
    wis/elizabeth_bothfeld_v._wisconsin_elections_commission  3 fences, intervening party group, recital left to the order
    wis/scot_van_oudenhoven_v._wisconsin_department_of_justice 4 fences, origin, no announcement
    wis/state_v._andreas_w._rauch_sharak                  APPEAL origin, route + court below in one statement
    wis/state_v._michael_joseph_gasper                    10-row announcement, en-dash docket, Reserve J.

`wis/planned_parenthood_of_wisconsin_v._joel_urmanski` is already pinned and
passes (its page 5 is a genuine image-only page — the 1 `scanned` status).

## 25. A reversed byline accepts an UNTERMINATED verb clause — `resolve/bylines.py`

From the utah port, 2026-08-20. This is why 48 of 50 utah records carried the
cover's authorship summary inside the majority before that port.

    BylineParser(get_profile('utah').byline).parse(
        'JUSTICE HAGEN authored the opinion of the Court, in which')
      -> Byline(name='HAGEN', title='Justice', kind=None, end=57)

That row is NOT a byline — it is the cover's authorship summary, and the
writing signs itself `JUSTICE HAGEN, opinion of the Court:` twenty rows later.

v1 encoded this deliberately: `_reversedjustice.py` comments that `'authored'`
is *absent* from `_OPINION_VERBS` because "treating 'authored' as a verb would
double-count the two", and its comma-form branch required the row to END at
its kind (`_KIND_ENDINGS`). The new parser has NEITHER guard.

The rule: **a reversed byline must terminate at its kind or a colon, and
`authored` is not an opinion verb.** Blast radius is every `also_reversed`
court, so measure before tightening. utah is immune court-locally today
(`_is_writing_byline()` refuses any row containing `authored`, and the summary
is claimed as `panel` so it is subtracted from the stream).

## 26. A court claim is never subtracted from the FOOTNOTE ZONES — `pipeline.py`

From the ri port. **8 of 50** ri records, and pre-existing (identical with
ri's decider popped).

Zones are measured in step 6, the reader runs in step 8, and `_claimed` is
subtracted only from `segments_by_page` — never from the zone lines. On those
8 records the cover sheet's first fence reads as a note separator, so every
band below it is ALSO published as a block of the last writing's last
footnote. On `american_express_national_bank_v._anna_perretta_1` that is 19 of
the 27 lines the reader claims on page 10, reproduced verbatim inside
footnote 5.

Patch, beside the existing subtraction at `pipeline.py:495-501`:

    for _pg, _ls in list(zone_lines_by_page.items()):
        _keep = [l for l in _ls if l.id not in _claimed]
        if _keep:
            zone_lines_by_page[_pg] = _keep
        else:
            zone_lines_by_page.pop(_pg)
            zone_tops.pop(_pg, None)

`zone_tops` is only read after this point by `assemble` and the residual
sweep, both of which want the claimed page gone; segmentation already
happened at line 473. Affected ri stems: american_express, asa_s._davis,
estate_of_louis_campagnone, in_re_e.g.s, jay_patel_v._mancini,
robert_schmidt, the_providence_community_health_centers, william_fairhurst.

## 27. `render/casebody.py` hard-codes the hm section's element — `render/casebody.py:100`

From the ri port. `_hm_xml(value, "summary", out)` ignores `spec.casebody`, so
the endmatter exports as `<summary>` rows rather than `<attorneys>`. The fix
is literally `_hm_xml(value, spec.casebody, out)` — but that changes the
HEADMATTER's element too, so it is a casebody-compatibility call for the core
owner, not a local fix. Flagged, not decided.

## 28. A drawn fence is read as an UNDERLINE — `pdfio/quirks.py:tag_underlined_chars`

From the ri port. **229 spurious `<u>` runs across all 50 ri files**,
pre-existing and untouched by that port.

The rule requires only horizontal OVERLAP plus a -2.5…+5.0pt vertical window,
so ri's 470pt band fence tags the band's last value row: `<u>(KC 21-1031)</u>`,
`<u>Long, JJ.</u>`, `<u>Matthew Casey, Esq.</u>`.

An underline is the width of what it underlines; a hairline overhanging both
ends of the row by more than a couple of ems is a rule the page set as
structure. Suggested guard in the `line_rects` comprehension:

    and (r["x1"] - r["x0"]) <= (chars[-1]["x1"] - chars[0]["x0"]) \
                               + 4 * (chars[0].get("size") or 12)

Corpus-wide by nature — any court drawing a fence at a row's baseline.

## 29. APPLIED 2026-08-20 — `Document.signature` had no writer (`pipeline.py`)

Landed with `_EMIT_SIGNATURE_SECTION = True` in `centralia/courts/haw.py`; the
two are one change, and either alone is wrong (consuming into a key core
ignores DELETES the court's signature, returning without consuming prints it
TWICE beside core's own `Opinion.signature` lift).

    doc.summary.extend(_court_hm.get("summary") or [])
    + doc.signature.extend(_court_hm.get("signature") or [])

Declared on `model.py:324` and in `sections.py` since the section list
existed, written by nobody: `sig_blocks=0` corpus-wide, so every court's
`/s/` run was opinion body prose.

Safe to land with a porter still holding the tree because **haw.py is the only
court emitting a `signature` key**, so the blast radius outside haw is nil —
verified after the fact: `guard utah wis va ill kan ri` = **37/37**.

Measured on haw: **37 of 50 files gain a `sec-signature` of 219 rows**, zero
duplication (`DATED: Honolulu` no longer appears inside `sec-opinions` on any
file), 50/50 valid, residual 0, headmatter still 825/825 = 100%, ʻokina
intact. Exactly what the agent's in-memory proof predicted.

**This is the pattern for `md` (32 of 50 files) and `del` (42 of 50)**, which
lose judges AND date to the same gap — see the signature-band epic in
`docs/review-backlog.md`.

## 30. `criteria.attorneys` cannot see a `CaptionBlock` — `pipeline.py:1859`

From haw. `" ".join(… getattr(b, "text", "") for b in doc.attorneys)` — a
`CaptionBlock` has no `.text`, so any court emitting counsel as TWO COLUMNS
publishes no `attorneys` criterion at all, and a single loose row beside the
block captures the field instead (haw's filled with the DATE until the court
set the criterion itself). Walk `left`/`right`, or reuse `sections.iter_text`.
Affects every two-column endmatter court — ri and va both emit CaptionBlocks
now.

## 31. `Criteria` has no place field — `model.py`

From haw. The attestation states WHERE the court signed (`DATED: Honolulu,
Hawaiʻi, May 20, 2026.`) and there is nowhere declared to put it, so it
survives only as printed text. `place: str | None = None` on `model.Criteria`
if wanted — `setattr` would otherwise attach it silently and never serialize.

## 32. Three more ʻokina shapes defeat the glyph quirk — `pdfio/quirks.py`

From haw, pre-existing. `february_2026` renders `Hawai#i`; `kenny_v._lange`,
`kenny_v._roberts` and `west_physicians_associates_llc_v._quiane` render
`Hawaii` (private-use glyph); several render `Hawai'i` (U+2018). The
glyph-bbox rule handles the common case — `fung_v._hoi` is correct U+02BB —
but not these three shapes.

## 33. `haw/m.s._v._l.s._1`'s dissent types `majority` — `resolve/bylines.py`

From haw. `DISSENT BY GINOZA, J.` parses as a byline but the writing comes
back `type='majority'`. Its signature was also welded (`'/s/ Lisa M. Ginoza
/s/ Kauanoe A.D. Jackson'` as one paragraph) because `_unweld_conformed`
splits on the glyph only when the paragraph has >= 2 source lines and pdfio
gave both names on one visual row — the item 29 seam fixed the welding as a
side effect, but the TYPE is still wrong.

## Item 6 — SHARPENED by wash, 2026-08-20, with a count-independent rule

wash's port found the per-writing running head is a much bigger defect than
item 6 records, and supplied the general rule item 6 was missing.

Washington prints a head UNIQUE TO EACH WRITING, so its repeat count can never
reach `_band_keys`' `0.4 * n_pages` floor and `FurnitureFinder.kind()` returns
None on every page:

    scott_v._amazon.com_inc.        'Ruth Scott et al. v. Amazon.com, Inc., No. 103730-9'
                                    stands as a PARAGRAPH inside its majority on
                                    pages 3,4,8,11,12,14,15,17,20 — 9 copies, and
                                    only ONE Dropped(running-head) record exists
                                    for all of them
    luv_v._w._coast_servicing_inc.  'No. 103031-2' over '(Madsen, J., concurring)'
                                    at the left margin, pages 14-19
    a_better_richland_v._chilton    '… No. 103715-5 (González, J., concurring in
                                    part)' WELDED to the head of a paragraph,
                                    pages 19, 22, 23

**The proposed rule, which is count-independent:** in the TOP band, a row is a
running head when its docket-shaped tail equals a docket the document prints
on page 1, regardless of repeat count. That catches a count-1 first-page head
AND item 6's `alacrimapp` "unreachable by construction" case, and it is the
same identity test wash's reader had to implement locally (`_docket_key`,
which compares the NUMBER not the setting — the court prints `No. 202,258-8`
in the caption and `No. 202258-8` at the head, `No.104342-2` tight and loose).

**Not fixable from a court file in general**: claiming those rows in a reader
would double-claim against core's own sweep on the pages where it DOES fire.

## Item 15 — DONE for wash; scotus and nj remain

Its re-scoped premise held exactly: a court claim is subtractive and
pre-assembly (`pipeline.py:474-484`), so no `cover.reprint` seam was needed.
A reader can only SUBTRACT a reprinted cover, never attach it to the writing
it introduces, because `Opinion.caption` is filled by assembly, which runs
AFTER `headmatter.read`.

**One correction to item 15's text:** wash's reprint is NOT byte-identical to
page 1 — `NO. 103715-5`/`No. 103715-5`, `EN BANC`/`En Banc`, `acting in her
capacity as the Benton County Auditor`/`…as Benton County Auditor`, and a
different rail x (321.1 vs 305.5). So identity must never be tested on the
caption TEXT; the banner row is the only row stable enough to compare.

## 34. `triage()`'s CID test is DOCUMENT-wide, so one unreadable PAGE always passes — `pipeline.py`

Found by the pasuperct port, 2026-08-20. NOT previously in this queue. This is
the highest-impact quality defect measured so far: it takes a court from
**F, mean 193.512 to A, mean 0.226**.

`classify.py:41` compares `cid / ink` summed over the WHOLE document against
`CID_MAX_FRAC = 0.2`. On **21 of the 42 pasuperct records the LAST page** is
set in a subset font with no usable encoding: pdfplumber returns it as
`(cid:N)` runs with the surviving letters shifted three places (`WKUHFRG` for
`therecord`) and advance widths collapsed to zero, so even the row order is
meaningless. That page is emitted as body prose — mojibake inside the writing.

Measured separation is clean: those 21 pages run **0.220-0.818** CID per ink
char while their DOCUMENTS run **0.001-0.016**, so the same constant applied
PER PAGE separates them exactly. Over 2,323 pages of pa, pacommwct, ca6, wyo,
ohioctapp and mass it catches NONE.

Patch goes in `pipeline.py` immediately after the existing `_img_only` block
(~line 248), before `if verdict == "unreadable":`, mirroring that block's
idiom — full text with its comment is in the agent's report; the shape is:

    from .classify import CID_MAX_FRAC
    _cid_bad = [pm for pm in model.pages
                if pm.ink_chars and pm.cid_chars >= 10
                and pm.cid_chars / pm.ink_chars > CID_MAX_FRAC]
    if _cid_bad and verdict != "unreadable" and len(_cid_bad) < model.n_pages:
        for pm in _cid_bad:
            doc.dropped.append(m.Dropped(..., kind="unreadable-page"))
            pm.event("cid-page", f"{pm.cid_chars}/{pm.ink_chars} CID")
            pm.lines = []

Validated in-process (monkeypatched, no core file edited): pasuperct F/193.512
-> A/0.226, all 42 stay `valid`, headmatter stays 686/686, both pasuperct pins
still compare OK.

**Deliberate design choice to preserve when landing:** record the page as a
`Dropped(kind="unreadable-page")`, NOT as a `doc.warnings` entry. A warning
containing "unreadable text layer" added to `SOURCE_WARNINGS` would flip those
21 records from `valid` to `scanned` and move the `status` field of every pin
the test catches — a corpus-wide decision for the owner, not a side effect of
a page fix. Whoever lands it should run the FULL guard; only six other courts
were sampled.

Related but distinct: item 5 (`a space that advances nothing is not a space`)
and the wash `(cid:NN)` clerk-signature glyphs are both about unmapped fonts,
but neither removes an unreadable PAGE.

## 35. `_reversed` does not survive a FOOTNOTE MARK on the author's name — `resolve/bylines.py`

From the illappct port, 2026-08-20. The Fifth District hangs a footnote on
the byline to explain a panel substitution:

    people_v._lee p1 top 377.6:
      'JUSTICE CLARKE* delivered the judgment of the court, with opinion.'

`BylineParser.parse` returns None, so the record assembles as ONE UNBYLINED
majority. Same shape on `people_v._spears`, whose roster reads
`Justices Hackett* and Clarke** concurred …`.

    # near the top of _reversed(), before the title match
    _FN_MARKS = "*∗†‡§"
    text = text.translate({ord(c): None for c in _FN_MARKS})

Also wanted in `is_caps_name`'s tokenizer. Sandbox-verified: with the marks
removed the string parses to `Byline(name='CLARKE', title='Justice')`. Scope:
2 illappct records, plus any court that footnotes a byline — and utah's port
noted its own footnote stars come in three interchangeable forms (`*`,
`∗` and the PRIVATE-USE ``), so the mark set should include PUA
variants where a court is known to use them.

## 36. HOLD — the illappct CourtProfile needs two byline flags (`courts/__init__.py:221-225`)

**This one is MINE to apply, not core's, and it is deliberately not applied
yet:** three porters were appending their own import lines to
`courts/__init__.py` at the time, and a read-modify-write on that file could
drop one of them — which is precisely the "a port is not real until it is
wired in" failure that hid six ports on 2026-08-19. Apply when the tree is
quiet, then verify every expected import is still present.

illappct numbers its paragraphs with a hanging pilcrow AND numbers its
separate-writing bylines, exactly as ill does, and signs some abbreviated:

    people_v._salinas p21:  '¶ 59 JUSTICE BIRKETT, concurring in part and dissenting in part:'
    in_re_a.b.       p15:  '¶ 57 Ellis, J., dissenting.'

Without `strip_para_marker=True` and `also_abbrev=True` every announced
separate writing in the corpus is LOST and the document assembles as one
majority.

    register(CourtProfile(
        "illappct", "Illinois Appellate Court",
        byline=BylineGrammar(style="reversed", allow_titlecase_name=True,
                             strip_para_marker=True, also_abbrev=True,
                             rev_titles=("JUSTICE", "PRESIDING JUSTICE",
                                         "Justice", "Presiding Justice"))))

Sandbox-verified: with both flags the strings above parse and the majority
byline and concurrence-roster rows behave exactly as before. It WILL change
the `ops` signature of `people_v._salinas` and `in_re_a.b.` — bless those
deliberately. Neither is pinned yet, on purpose.

## 37. A parsable dissent byline is dropped by assembly — `resolve/assemble.py`

From illappct. `people_v._reyes` p15 top 478.9 prints
`PRESIDING JUSTICE NAVARRO, dissenting:`, which `BylineParser` DOES parse
(`Byline(name='NAVARRO', title='Presiding Justice', kind='dissenting:')`) —
yet the document assembles with a single writing
(`ops [('majority','OCASIO',72)]`). Not the byline grammar, and not the
court's claim. **v1 also loses it, so v1diff is blind here** — another entry
for the oracle blind spots.

## 38. The criteria box hides seven populated fields — `render/html.py:305-318`

From illappct. `panel`, `panel_line`, `court`, `case_name`, `motion`,
`lower_court_judge` and `headmatter_style` are populated on 41-42 of 42
illappct records and are INVISIBLE in review — the agent had to write a
scratch script to see them. `criteria · N` therefore undercounts what a
reader actually read, which is the same class of blindness `hm-unread` was
added to fix. Additive patch: extend the `crit_rows` tuple.

## 39. There is no `endmatter.read` seam — every illappct record loses its counsel

From illappct, and this is a SEAM GAP rather than a bug. All 42 records end
with a drawn two-column CASE-INFORMATION page carrying counsel, and it stays
in the writing as body prose: `criteria.attorneys` is empty on 42/42 while
the page prints e.g. `Attorneys for Appellant: Adam Goodman, of Goodman
Tovrov Hardy & Johnson LLC, of Chicago, for appellant.`

v1 lifted it into `doc.trailer` via `page_lines`
(`illappct.py::_case_info_table`), detected from the drawn seam where each row
rule is laid as TWO SEGMENTS MEETING AT A SHARED COLUMN X — geometry, not
wording. A court file cannot do this today: `headmatter.read` is the only
reader seam, and it cannot reach the last page's grid.

Relates to item 30 (`criteria.attorneys` cannot see a `CaptionBlock`) and to
ri's cover sheet, which only reached the endmatter because ri could return it
under the `attorneys` key from `headmatter.read`. A general `endmatter.read`
seam would serve illappct, ri, haw and the whole two-column endmatter family.

## 40. A title-case byline is only a byline when it is a BARE SURNAME on its whole line — `resolve/bylines.py`

From the ohioctapp port, 2026-08-20, with the tradeoff MEASURED both ways
(reader popped, so only the grammar varied). Six of Ohio's eight appellate
districts sign in title case (`Baldwin, J.`, `Hess, J.`, `King, P.J.`), so
`allow_titlecase_name` looks obviously right — and as the flag stands it is a
NET LOSS:

    allow_titlecase_name=False -> 45 writings,  9 records unauthored, typed 'order'
    allow_titlecase_name=True  -> 72 writings,  those 9 authored, +27 PHANTOM writings

The 27 phantoms are the conformed roster every district prints at the FOOT of
its opinion — `Thomas J. Osowik, P.J.`, `Gene A. Zmuda, J.` — plus inline
concur lines: `Hoffman, P.J. and`, `Gormley, J. concur.`, `Abele, J. &
Wilkin, J.: Concur in Judgment and Opinion.`

v1 solved this with two guards in `_appellate`/`ohioctapp`: `_name_ok` required
a title-case name to be a SINGLE TOKEN, and `_byline_split` declined any split
that left text over. `titlecase_kind_only` does NOT substitute — it rejects
`Baldwin, J.` (no kind clause) and admits `Gormley, J. concur.`

A NEW declared flag, so no existing court moves:

    # in BylineGrammar, beside allow_titlecase_name
    titlecase_bare_surname: bool = False

    # ~line 547, at the two points that consult allow_titlecase_name
    if not self.g.allow_titlecase_name and not self.g.titlecase_bare_surname \
            and not is_caps_name(name):
        return None
    if self.g.titlecase_bare_surname and not is_caps_name(name) \
            and (len(name.split()) != 1 or (rest or "").strip(" ,.;:—–")):
        return None

then `byline=BylineGrammar(style="abbrev", titlecase_bare_surname=True)` in
`courts/ohioctapp.py`. Expected: 9 records gain their real author (bath, hsbc,
eldridge, gates, krichbaum, m.m.a., mayle, kent, klingensmith), 0 phantoms.

**Needs a corpus guard run: `neb` declares `allow_titlecase_name` today and
must not move.** Separately, `cme_fed` carries a pre-existing ALL-CAPS phantom
(`BOGGS, P.J.` out of its concur roster) that is present with the flag off and
is untouched by this patch — it wants its own look.

**Sentinel note:** `ohioctapp/bath_v._rudisill` was pinned and then UNPINNED
on 2026-08-20, because its current `['order']` signature IS this bug — an
unauthored majority typed as an order. Pin it only after this lands, when it
should read as a bylined majority. `hsbc_bank_usa_v._pryor` is the same shape
and is likewise unpinned. This is the 08-19 alaska mistake avoided rather than
repeated.

## Housekeeping lesson, 2026-08-20 — staging `courts/__init__.py` sweeps in other agents' work

My illappct commit (`e357eec`) staged `centralia/courts/__init__.py`, which
picked up the `from . import ohioctapp` line a concurrent porter had appended
while `ohioctapp.py` itself was still untracked. **HEAD could not import the
courts package at all** until that agent committed its own module
(`3413854`), which it correctly did.

Rule: when several porters are appending imports, either commit the module
file together with the registry line, or do not stage `courts/__init__.py`.
Verify with a clean checkout, not by eye:

    T=$(mktemp -d); git archive HEAD | tar -x -C "$T"
    (cd "$T" && .venv/bin/python -c "import centralia.courts as C; print(len(C.PROFILES))")

## 41. `criteria.attorneys` is UNREACHABLE for a reader that keeps counsel in the headmatter — `pipeline.py:1862-1870`

From the connappct port, 2026-08-20. **Verified against an already-shipped
court: conn populates `criteria.attorneys` on 0 of 8 sampled records, and 0 of
its 50 renders carry the `attorneys` chip.** This patch fixes conn for free.

The stated invariant is "counsel printed inside the headmatter STAYS there,
its text copied into `criteria.attorneys`". The copy has only two sources:
`_counsel_texts` (blocks core MOVED) and `doc.attorneys` (the separate section
a `counsel_after_writings` court builds). **A reader that obeys the invariant
hits neither** — so the appearances are read perfectly, render in place, and
are stated nowhere machine-readable. `harness/quality.py`'s `no_atty`
consequently fires on 8 of 44 connappct records and on ALL 50 conn records.

Insert after line 1870:

    if doc.criteria.attorneys is None:
        # A COURT THAT READS ITS OWN BLOCK KEEPS COUNSEL IN IT. Neither
        # source above can see those appearances: `_counsel_texts` holds
        # blocks core MOVED and `doc.attorneys` is the separate section a
        # `counsel_after_writings` court builds. So a reader obeying the
        # invariant gets its first half and never its second.
        from .audit import strip_tags as _stc, unescape_xml as _uxc
        _hm_counsel = [_uxc(_stc(getattr(it, "text", "") or ""))
                       for it in doc.headmatter
                       if getattr(it, "role", None) == "counsel"]
        if _hm_counsel:
            doc.criteria.attorneys = " ".join(
                t for t in _hm_counsel if t.strip())[:2000]

connappct closed it inside its own court file (mean 0.602/B -> 0.057/A) with
the rows still rendering in place, so the court is not waiting on this — but
conn and every future reader that keeps counsel in the block are.

Blast radius: only courts whose reader emits `role="counsel"` rows and set no
attorneys section. It ADDS a criteria key, which is exactly the shape of diff
several pins record, so it needs a guard run.

Relates to item 30 (`criteria.attorneys` cannot see a `CaptionBlock`) — same
field, different reason it comes back empty. Both should land together.

## Item 20 does NOT manifest in connappct — recorded so nobody re-derives it

Item 20 is Connecticut's **Law Journal** folio at 150.5/792 = 0.1900252.
connappct's corpus contains NO Journal extract, so no connappct record leaks a
bare numeral and `folio-leak` is absent from all 44. The defect stays latent
for its extract branch.

## 42. CONTENT LOSS — `_announces` deletes a stapled order's writing — `resolve/assemble.py:1720`

From the calctapp port, 2026-08-20. **The only content loss in that corpus,
and the most serious class of defect in this queue: 135 words vanish with NO
residual to show for it.** `calctapp/in_re_mccowen` loses its whole
modification order (pages 17-18) because `_announces` marks it dead and
`result.consumed_ids.update(...)` swallows its blocks.

The chain, proved: core splits the stapled paper
(`pipeline.py::_attached_documents` -> `[(0,16),(16,20)]`); part 2's cover is
read, so its writing measures under the 900-char bar; `_announces` then returns
True because the order names a LATER writing's author — which an order
attaching a concurrence necessarily does (`add and incorporate the concurring
opinion of RAPHAEL, J.`) — and `_DELIVER_VERBS` matches on the incidental
`filed`. The veto that should have saved it tests the LITERAL string
`"IT IS ORDERED"`, and California writes `IT IS THEREFORE ORDERED` /
`IT IS FURTHER ORDERED`. Verified: veto cues present = `[]`.

    _joined = " ".join(_sta(getattr(b, "text", "") or "") for b in op.blocks)
    # A RULING THAT PRONOUNCES ITSELF IS A WRITING, whatever else it
    # mentions — and an order ATTACHING a concurrence necessarily names
    # that concurrence's author. The formula takes an adverb
    # ('IT IS THEREFORE ORDERED', 'IT IS FURTHER ORDERED'), so it is
    # MATCHED, not compared.
    if any(cue in _joined for cue in ("is denied", "are denied", "is granted",
                                      "is DENIED", "are DENIED",
                                      "is dismissed", "is affirmed")) \
            or _rex.search(r"(?i)\bit is (?:\w+ )?ordered\b", _joined):
        return False

`import re as _rex` already sits four lines below — hoist it above this block.
**Do not pin `calctapp/in_re_mccowen` until this lands.**

## 43. `_shift_pages` double-counts a stapled part's pages — `pipeline.py:130-150`

From calctapp. `extract` renumbers a part's `PageModel.number` to 1..n but
**`Line.page` stays ABSOLUTE** — verified: `pm.number == 1` while
`pm.lines[0].page == 17`. Every `Prov` is built from `line.page`, so it is
already absolute when `_shift_pages(doc, a)` adds the offset again:
`in_re_mccowen` (20 pages) emits `data-pg="33"`, `35`, `36`. Affects every
stapled record — 8 in calctapp alone.

Two fixes: renumber `Line.page` alongside `PageModel.number`, or drop
`_shift_pages` entirely and let the absolute `line.page` stand. The second is
smaller and needs a check that no reader uses `pm.number` for provenance.

## 44. Item 7 UPDATED — `doc_type_final` has an OPINION mirror but no ORDER one

Supersedes part of queued item 7, which said the reader's declared
`doc_type_final` is thrown away. It is NOT: it reaches op typing through the
mirror at `pipeline.py:1880-1885`. Declaring `DocType.OPINION` retyped **9**
calctapp records from `order` to `majority` — all the unpublished ones, because
`classify_doc_type` has no cue for `NOT TO BE PUBLISHED IN [THE] OFFICIAL
REPORTS`, so they classify UNKNOWN and `assemble.py:1554` types their only
writing `order`.

What is missing is the mirror's other half, so an unsigned lead writing typed
`majority` stays wrong where the court NAMES the paper an order (`citizens`
part 1, `bates` part 1, `kumar` part 2):

    if (meta.doc_type is m.DocType.ORDER and doc.opinions
            and doc.opinions[0].type == "majority"
            and not doc.opinions[0].author_name):
        doc.opinions[0].type = "order"

`calctapp/citizens_against_marketplace` is already pinned and reads its
headmatter correctly, but its op typing is still wrong (part 1 is an order
typed `majority`) — **expect its `ops` to change when this lands; that is the
fix, not a regression.**

## 45. `_render_endmatter` hard-codes `data-role="counsel"` — `render/html.py:233`

From calctapp. Every endmatter row renders as `counsel` regardless of
`HmLine.role`, so cal's careful docket-sheet roles (`title`, `docket`, `date`,
`lower-court`, `case-info`) are all discarded, along with calctapp's 121 sheet
rows. Cosmetic, but **it makes the role histogram lie about what a reader
actually read** — which is the metric this project steers by.

    role = getattr(b, "role", "") or "counsel"
    out.append(f'<div class="hmrow al" data-role="{role}"{attr}>'

## 46. A line a court reader claims can still carry a `Dropped` — `pipeline.py:330-345` vs `:485`

From calctapp. The furniture sweep records `Dropped(kind=...)` ~150 lines
BEFORE the `headmatter.read` seam, and `_court_hm["consumed"]` is never
reconciled against `doc.dropped`. calctapp claims its filing stamp — the only
date the court prints anywhere, and v1's first headmatter row — so on **34
records the stamp appears both in the headmatter and under "removed"**.
Over-accounting rather than loss, and the cure is three lines at the seam:

    if _court_hm:
        _claimed = set(_court_hm.get("consumed") or ())
        # A LINE A READER CLAIMS IS NOT ALSO REMOVED. The furniture sweep
        # runs 150 lines above this seam, so a row the court reader goes on
        # to place was already recorded as junk.
        doc.dropped = [d for d in doc.dropped
                       if not (d.prov.line_ids
                               and set(d.prov.line_ids) <= _claimed)]

## Items 36 and 37 — RESOLVED 2026-08-20, and item 37 was MISDIAGNOSED

Item 36 (illappct's profile needs `strip_para_marker=True` and
`also_abbrev=True`) is APPLIED. illappct stays at 1005/1005 rows, 42/42 valid,
and `guard illappct ill` is 11/11.

**Item 37 was not an assembly defect at all.** It reported that
`people_v._reyes` printed `PRESIDING JUSTICE NAVARRO, dissenting:`, which
`BylineParser` parsed, yet assembly returned one writing — and concluded the
loss was in `resolve/assemble.py`. It was the same missing profile flags. All
three records recovered together:

    people_v._salinas  [('majority','SCHOSTOK'), ('concurring-in-part-and-dissenting-in-part','BIRKETT')]
    in_re_a.b.         [('majority','MIKVA'),    ('dissent','Ellis')]
    people_v._reyes    [('majority','OCASIO'),   ('dissent','NAVARRO')]

**Item 37 is CLOSED — do not go looking for an assemble.py bug.** The lesson:
a byline that parses in isolation can still be invisible to assembly because
the COURT'S OWN GRAMMAR never offered it, and that reads exactly like an
assembly defect from the outside. Check the profile before the pipeline.

The three stems are now pinned, since their readings are correct.

## calctapp notice fix, and one more stale pin removed — 2026-08-20

**User-reported:** the California Rules of Court rule 8.1115(a) notice was not
being removed on `calctapp/bates_v._city_of_temecula_ca41` — its three 8.0pt
rows came back tagged `date`.

Cause was in the court file, not core. `_read_stamp` deliberately reads off the
PAGE rather than the filtered rows (that is what lets it claim the clerk's
stamp at all, since core's furniture finder takes the stamp out of `above` on
28 of 42 records) — but it applied only the UPPER size bound
`<= body_size - _STAMP_STEP` (<= 11.0). The notice at 8.0pt passed a test meant
for the 10.0pt stamp, and `_read_masthead` never saw those rows to drop them
because the furniture filter had already removed them from `above`.

The file's own comment (~line 186) already documented the two-threshold design
— "the body is 13.0pt, the clerk's stamp 10.0-10.1pt, and the
uncertified-opinion notice 8.0pt. Two steps, so two thresholds, and the window
between them (9.0-11.0) is empty across the corpus" — the stamp reader just
never applied the second one. Now:

    body_size - _NOTICE_STEP < (l.size or body_size) <= body_size - _STAMP_STEP

Verified: rule 8.1115 no longer lands in ANY content section on any of the 42
records; calctapp holds at 1026/1026 rows (100%), 42/42 valid, 0 unread. The
row total fell 1029 -> 1026, which is exactly the three notice rows now dropped.

**Also removed a stale pin:**
`calctapp/citizens_against_marketplace_etc._v._city_of_san_ramon` recorded
`hm: 513` — the whole document sitting in the headmatter, which was the
pre-port bug. It now reads 14 hm rows, `valid`, residual 0. But its op typing
is STILL wrong (`ops` is two unauthored majorities where part 1 is an order),
which is queue item 44. A stale pin whose stored state is the old bug produces
noise rather than signal, and re-blessing it would lock the wrong op typing —
so it is unpinned, like `bath_v._rudisill` and `in_re_mccowen`. **Re-pin all
three after items 40, 42 and 44 land.**

## 47. A ONE-GLYPH row is accepted as a displaced substitute-font run — `pdfio/quirks.py:snap_displaced_fragments`

From the idahoctapp port, 2026-08-20. **A strict REGRESSION against v1, which
reads the line correctly.**

`quirks.py:260` tests `if not (1 <= len(frag) <= 40): continue` — so a
one-glyph row qualifies as displaced. A typed caption rail is exactly that: a
stack of one-glyph rows at one x, in the face the caption is set in, and every
one of them looks displaced against the roman prose below.

On `idahoctapp/in_the_interest_of_john_doe` the raw page has 14 bold `)` at
x0=302.21 on a 13.8pt grid, tops 128.97 -> 295.08. The last one is alone on its
row, bold where the row 28pt below is roman, and 4pt wide — exactly the
whitespace between `of` and `the` — so it snaps down and the origin prints
**`Appeal from the Magistrate Division of) t he District Court`**. The rail
also loses its bottom glyph.

The principled test: **a glyph standing in a COLUMN is structure, not
displacement**, and the rail's own same-x siblings are the evidence. Insert
after the `f_fonts`/`fx0`/`fx1` measurement (~line 263), before the `near`
block:

    # A GLYPH THAT STANDS IN A COLUMN IS STRUCTURE, NOT DISPLACEMENT.
    if len(frag) <= 2 and any(
            (c.get("text") or "") == (fc.get("text") or "")
            and abs(c["x0"] - fc["x0"]) <= 1.0
            and 4.0 < abs(c["top"] - top) <= 60.0
            for fc in frag for c in printable if c is not fc):
        continue

Validated in-process (monkeypatched, no core file edited): the line reads
correctly, no other idahoctapp record moves, and **68 guard sentinels across
the nine courts the quirk was written for — arizctapp, me, ca5, cadc, ariz,
mont, ca9, conn, idaho — are byte-identical before and after.** Note the
SECOND pass of the same function already requires `len(frag) >= 4`; the first
pass having no floor at all is the asymmetry. Run the full 410-sentinel guard
before landing.

**Do not pin `idahoctapp/in_the_interest_of_john_doe` until this lands** — its
`lower_court` currently carries `of) t he`.

## Item 46 — a SECOND manifestation, from idahoctapp

Item 46 (a line a court reader claims can still carry a `Dropped`) also occurs
in the opposite direction: idahoctapp's page foot is dropped as `folio` by
core's own furniture pass AND was being recorded again by the reader, so on the
one record whose page 1 the reader owns end to end the same line appeared
twice. Worked around in the court file by leaving the foot unclaimed. The
reconciliation in item 46 fixes both directions.

## nmctapp note — `Opinion Number: __________` is a BLANK PLACEHOLDER

Observed while checking nmctapp's citation coverage: **20 of its 21 records are
UNPUBLISHED** ("not selected for publication in the New Mexico Appellate
Reports. Refer to Rule 12-405 NMRA"), so they print the citation FIELD with no
value — `Opinion Number: __________`, and one bare `Opinion Number:`. The row
is correctly tagged `citation` and `Criteria.citation` is correctly EMPTY; only
`apache_corp._v._n.m._tax__rev._dept` carries a real cite (`2024-NMCA-080`).
Not a defect. Whether a blank placeholder row is worth rendering at all is a
judgement call for review, not a bug.

## 48. `heading_doc_type` reads an announced-AUTHOR row as a doc-type heading — `classify.py:158`

From the iowactapp port, 2026-08-20. Not previously in this queue, and it will
bite any of the ~150 unported courts that announce authorship in front matter.

`_matches("OPINION BY GREER, P.J.", "OPINION")` returns True through the
prefix-phrase arm that exists for `ORDER GRANTING…`:

    >>> heading_doc_type('Opinion by Greer, P.J.')   -> opinion
    >>> heading_doc_type('Opinion by Sandy, J.')     -> opinion

`assemble.py:1153-1163` uses it to set `_titled`, and `:1293-1305` then CLOSES
THE HEADMATTER at that segment (`trace: body.doc-type-heading — "heading
closes headmatter @seg19"`). So `Opinion by Greer, P.J.` rendered as an
`<h3 class="bhead">` inside the majority — whose real byline
(`GREER, Presiding Judge.`) is on page 2.

**It is INTERMITTENT, which is why it survived this long.** `:1293` requires
`not _rostered`, so it fires only where the segmenter puts the roster row in a
different segment. In iowactapp that is exactly 1 of 30 records — the one
whose roster row is wide enough (390pt) to be split off, because it carries an
appended recusal clause.

    def _matches(cand: str, key: str) -> bool:
        c = _strip_modifiers(cand)
        if c == key or c.startswith(key + " ") or c.startswith(key + ":"):
            # 'OPINION BY GREER, P.J.' names the AUTHOR, not the paper.
            if re.match(rf"^{re.escape(key)}\s+BY\s+\S", c):
                return False
            return True
        return key in _SUFFIX_KEYS and c.endswith(" " + key) and len(c) <= 40

**Caveat from the agent, and the reason it did not apply this: `va` prints a
bare `OPINION BY` on its own line** over `JUSTICE …`, and `classify_doc_type`
also feeds two-line joins (`OPINION BY  JUSTICE …`) into `_matches`. The
`\s+BY\s+\S` guard deliberately keeps the bare form matching, but the
joined-wrap path needs a full guard run. Moot for iowactapp itself, whose
reader now claims the row.

## Two iowactapp modelling choices — ACCEPTED 2026-08-20

The agent flagged both rather than burying them, and both are right:

1. **An in-rem caption sets `parties = [the matter title]` alone**, with the
   appealing party recoverable from `criteria.caption` (verbatim rows). The
   alternative `[title, appellant]` renders as
   `"In the Interest of F.M., Minor Child v. T.M., Mother"`, which states a
   relationship the page does not.
2. **`history` keeps the origin band AS PRINTED**, duplicating the parsed
   `lower_court`/`lower_court_judge`, because it is the only field that records
   the ROUTE — and `Certiorari from` is not `Appeal from`. Affects all 30.

Its six sentinels are pinned on that basis.

## Items 34, 40, 41 — manifestation log

Recorded so nobody re-derives them per court:
- **item 41** (`criteria.attorneys` unreachable) HIT on idahoctapp and
  iowactapp as diagnosed; both closed it inside their own court file, as
  connappct did. Confirmed on conn, connappct, idahoctapp, iowactapp — the
  patch is wanted regardless.
- **item 34** (document-wide CID test) does NOT manifest on idahoctapp or
  iowactapp: `cid_chars == 0` on every page of all 60 records.
- **item 40** (title-case bylines) does NOT manifest on either: both sign in
  full caps and all 60 lead writings come back authored.

## 49. A byline BELOW the attestation is a signature too — `resolve/assemble.py:717`

From the nmctapp port, 2026-08-20. **22 phantom empty writings across 11 of
13 records**, and the best-evidenced patch in this queue — its author measured
the counterfactual.

`_signs_off` (~703) catches the AUTHOR's conformed name, which stands ABOVE
`WE CONCUR:`. The judges who JOINED sign BELOW it, one name per row — and
nmctapp types a rule over each name, so those names are NOT ADJACENT segments
and the panel-roster fold at line 731 (`b - a == 1`) cannot see them:

    state_v._klumb p16:  349.1  '      ______________________________'
                         365.1  '      KRISTOPHER N. HOUGHTON, Judge'   <- author, caught
                         397.3  'WE CONCUR:'
                         445.6  '___________________________'
                         461.7  'ZACHARY A. IVES, Judge'                <- opens a writing
                         509.9  '___________________________'
                         526.1  'JANE B. YOHALEM, Judge'                <- opens a writing

That is exactly the slip/memorandum split: the 7 memorandum records print no
rules, their names ARE adjacent, and they fold correctly.

Patch goes immediately before the `# A TERMINAL byline is a SIGNATURE` comment
(~line 758), where `_kindless_pure` is in scope — full text in the agent's
report; the shape is a `_under_attest(i)` predicate walking back to an
`_ATTEST` row on the same page, bailing on any line over 60 chars, then
`starts = [i for i in starts if not _under_attest(i)]`.

**THE `_kindless_pure` GATE IS LOAD-BEARING, AND THERE IS A MEASUREMENT
PROVING IT.** Without it, nmctapp goes 22/22 clean but **`nm` LOSES TWO REAL
DISSENTS** — `nm/state_v._cardenas_1` (`dissent THOMSON 15`) and
`nm/state_v._vasquez_1` (`dissent ZAMORA 16`) fold into their majorities. With
the gate, across **273 files of nm / calctapp / ca7 / wis / nmcca only 2
change, both `nm`, both strict improvements** (each loses a phantom
`[…,'FULL NAME',0]` and returns its rows to the writing above).

nmctapp then goes 21 of 22. The one remaining is `silva`'s
`J. MILES HANISEE, Judge, specially concurring` under `WE CONCUR:` — that row
carries a KIND, so it ANNOUNCES a writing beginning on the next page, which is
**queue item 1**, not this. Needs a full guard run when landed.

## 50. `sitting by designation` is only recognized at the START of the kind clause — `resolve/bylines.py:531`

From nmctapp. `BUSTAMANTE, Judge, retired, sitting by designation.` yields
`kind='retired, sitting by designation'`, and `normalize_opinion_type` turns
that into the opinion TYPE **`retired,-sitting-by-designation`**. apache's only
writing is typed that way, and `nm` already carries a
`['retired', 'RICHARD C. BOSSON', 5]` from the same shape.

    sitting = bool(kind) and "sitting by designation" in \
        " ".join(kind.lower().split()) \
        and not any(w in kind.lower() for w in _KIND_WORDS)

A/B'd against a grammar carrying `Circuit Judge` / `United States District
Judge`: only the target changes — `David J. NOVAK, …, sitting by designation:`,
`Tolliver, …, sitting by designation.` and `GRASZ, Circuit Judge, dissenting,
sitting by designation.` all behave identically.

## 51. HOLD (MINE) — nmctapp's CourtProfile is missing two measured facts (`courts/__init__.py:374`)

Not core's, and not applied yet because two porters were appending to that file.
`register` refuses a duplicate id, so the agent could not move the profile into
its own module. `centralia/courts/nmctapp.py:146` records what belongs on it:

- **`titles=(… "Justice", "Chief Justice")`** — retired Supreme Court justices
  sit here by designation and sign as such. `BOSSON, Justice, retired, sitting
  by designation.` fails to parse, which is why
  **`komis_v._farmers_ins._co.` is the one authorless record** and its byline
  renders as a body block. (Authorless is not a defect per the 2026-08-19
  ruling — but here the page DOES print an author.)
- **`para_indent_min=24.0`** — `state_v._romanis-beltran` body pages: 649 rows
  at x0 72 (rail), 139 at 108 (paragraph opener), 12 at 144 and 56 at 180
  (quotations). At the 12.0 default the quotation fence sits at 24pt and every
  ordinary paragraph opener falls inside it.

## nmctapp: the signing stamp is an ANNOTATION with no characters

Worth recording because I briefed the agent to fear it. The
`Office of the Director / New Mexico Compilation Commission / 2024.12.17`
block is a `/Widget` SIGNATURE ANNOTATION on exactly ONE of the 21 records
(`apache_corp` — the only paper the Commission has signed). **pdfminer returns
zero characters for it**: `[c for c in pg.chars if c['top'] < 75] == []`, and
page 1's first text row is the masthead at top 75.8. So there was never a row
to drop and its timestamp could not have reached `decision_date` (which comes
from `Filing Date: June 17, 2024`). The reader still claims that region as
`kind="stamp"` so a future extractor that DOES render annotations lands
somewhere already accounted for.

Also confirmed here: **item 38** (the criteria box hides populated fields) —
`title`, `court`, `case_name` and `headmatter_style` are populated on all 21
records and displayed on none. **Items 34 and 5 do NOT manifest** (worst
per-page cid/ink is 0 across all 21; dockets come out clean).

## 52. `conformed_signature_author` cannot read a bare judicial title, and its tail window is 14 lines — `resolve/bylines.py:910-930`

From the ohioctcl port, 2026-08-20. **23 of 30 records come back authorless
while the page prints the author.**

The Court of Claims signs `LISA L. SADLER` over `Judge` (or `SARAH PIERCE`
over `Special Master`) at the foot of the last page. The `_OFFICES` arm catches
`special master` but has no bare `judge`/`magistrate`/`justice`, and its window
is `lines_text[-14:]`.

Measured with a monkeypatch (no core file edited): an added arm requiring the
FOLLOWING line to be **exactly** one of
`Judge|Magistrate|Justice|Chief Justice|Special Master|Magistrate Judge` — an
exact match, not the substring test the existing arm uses, so `Judge` inside
prose cannot pose as one — over a **40-line** tail takes ohioctcl to **28 of 30
authored, every name matching the caption's bench row exactly**, which is
independent confirmation from the other end of the paper. The 2 that still miss
(`kanter`, `kolkowski`) print appendices after the signature.

The arm is deliberately tail-limited today, so widening the window has blast
radius — **full guard run required.** Related to item 39 (no `endmatter.read`
seam): with that seam a court could claim its own signature block instead.

**EXPECTED DIFF WHEN THIS LANDS, DO NOT READ IT AS A REGRESSION:**
`lead_bylined` flips false -> true on **23 ohioctcl records**, including 4 of
its 5 pinned sentinels. Re-bless deliberately.

## 53. `op_type` has no `report-and-recommendation` mirror — `resolve/assemble.py:1550-1554`

From ohioctcl. All **10** of its reports-and-recommendations are typed `order`.
A report is not an order; it recommends.

    if dt is None and doc_type == DocType.OPINION:
        dt = DocType.OPINION
    op_type = "order" if dt in (DocType.ORDER, None) else "majority"

An unbylined writing in an `RR` document falls through `dt is None` to
`"order"`. Same shape as item 44 (`doc_type_final` has an OPINION mirror but no
ORDER one) — extend the inheritance,
`if dt is None and doc_type in (DocType.OPINION, DocType.RR): dt = doc_type`,
or mirror it at `pipeline.py:1882` where `doc_type_final` already promotes an
unauthored `order` to `majority` for OPINION. Blast radius: any court whose
documents classify RR — uscfc's special masters.

**`ohioctcl/brown-austin_v._s._ohio_corr._facility` is deliberately UNPINNED**
because of this: its headmatter reading is correct but its `ops` is `['order']`.
All 10 R&R records share the shape, so there is no clean alternative sentinel
for it. Pin it when this lands.

## Oracle blind spot #4, measured on ohioctcl — a mis-read cover graded IDENTICALLY

The sharpest instance yet. Before this port, core published **the entire cover**
— cite line, banner, both caption columns, the paper's own name — as opinion
body prose, and left a one-row headmatter holding `Respondent` under a phantom
`upside-down-t` caption.

**Quality graded that A, mean 0.183 — exactly what it grades the correct
reading now.** `hm-unread` could not see it because the mis-read left FEWER
than the 6 hmrows its gate requires (`harness/quality.py:234`), and
`_court_has_reader` was false.

Two ideas, offered not patched: keep the existing gate but ALSO flag a
claimed-headmatter court whose block is implausibly SMALL against its page-1
ink; and note `v1diff` was dark here for the ordinary reason (no frozen
baseline). **A court with no reader cannot fail the headmatter metric, so the
metric cannot find an unported court's worst mis-reads** — which is the whole
reason headmatter COVERAGE, not grade, is the number this project steers by.

## Item 6 — third manifestation, and a structural fix worth generalising

ohioctcl's running head is ONE visual row of three pieces (`Case No. …` /
`-2-` / `JUDGMENT ENTRY`). Core learns a head by repetition, so on a TWO-PAGE
record each piece prints once and the third — the only one that is not a
number — survives as a doctype heading in the court's own words. With page 1's
title claimed it became the document's FIRST one and assembly opened a phantom
writing: **5 records bisected.** Measured split: core names all three pieces on
the 23 records of >=3 pages and only the first two on the 7 records of 2 pages.

Fixed in-court by a structural test that reads no wording — **a piece of a
head-band row whose siblings core already calls furniture is the same
furniture.** Fires on 9 rows corpus-wide, every one genuinely a running head,
and never where core's pass already succeeded (so no double `Dropped`, item
46). Worth lifting into item 6's proposed rule alongside wash's
count-independent docket test.

## 54. The court's own CITATION is dropped as a publication `status` stamp — `resolve/furniture.py`

From the scctapp port, 2026-08-20. **Found only because the reader was popped
to look** — any court reader that claims the row masks it, which is why it went
unseen.

With the decider popped, `furniture.py` classifies
`Unpublished Opinion No. 2026-UP-388` as furniture kind `status` and files it in
the removed box on **5 of the 7 unpublished records** (akpa, daisy_crump,
blakeney, kelly, altamont). `altamont` additionally loses
`Heard June 10, 2026 – Filed July 22, 2026` — its whole date band.

The publication WORD in the row is being read as a publication STAMP, but the
row is the court's own citation. Fix: require a stamp row to be the flag
**alone** — refuse any candidate whose text carries a citation or docket form,
concretely `r"\bNo\.\s*\S"` after the publication word.

**Check `sc` when this lands** — same publisher, same numbering, and its
reader may be masking the same drop.

## 55. A counsel block below a page break becomes a writing — `resolve/assemble.py`

From scctapp. On `in_the_matter_of_the_estate_of_paul_brandon_barringer_ii_3`
core opens an `order` writing on the page-2 counsel rows (`Desa Ballard, of
Ballard & Watson …`), giving the record two writings where the paper has one.

Those rows stand at the CAPTION rail (144.0), 72pt inside the body rail, and
are separated from the real byline by a drawn fence. Proposed rule: an unsigned
writing whose every block stands at or right of `caption_rail`, and which is
closed by a drawn rule before the first body-rail row, is not a writing — fold
it back into the headmatter span.

Same symptom family as item 49 (phantom writings) but a different cause: 49 is
a signature below an attestation, this is counsel below a page break.

## scctapp's shape — a new branch of the divider taxonomy

Worth recording, because six ports have now each had to name their shape and
this one is genuinely new: **the DRAWN-MARK family but HORIZONTAL, with no
second column.** Measured over all 28 records x 6 pages, the only rules these
pages draw are a 97.2pt band fence on the page axis (140 of them), the
footnote separator (74, and 162pt off axis), and ONE 216.2pt underline whose
ends coincide with the heading 11pt above it. **Vertical rules corpus-wide: 0**
(counted). So the page draws its structure horizontally and there is no caption
column at all — no `CaptionBlock` is emitted. The fence gate tests the AXIS
first and the measure second, which is what excludes that single underline.

## v1 loses 34 rows where we do not — scctapp/barringer

Recorded as evidence for the "v1 is a reference, not a standard" rule. On
`barringer`, v1 TRUNCATED the cover at page 1's eighth caption row and lost the
second consolidated caption, the docket, the origin, the citation, both dates,
the disposition and both counsel entries — 34 rows. We read them. Three other
records differ only because we re-emit drawn fences v1 omitted.

**Do NOT pin barringer yet.** Its rows, roles, fences and cross-page order are
all correct, but `case_name` and `parties[0]` fold its style row into the first
party: `"In the Matter of the Estate of Paul Brandon Barringer, II Hampton
Barringer Luzak"`. Inherited from `sc.py`'s `_trim`/`_case_name`. The structural
cue that would fix it — a caption row with no terminal punctuation followed by
another caption row — appears on exactly one record, so the agent correctly
declined to encode it from a single witness. Pin once that style-row rule is
settled; it is the only consolidated caption AND the only two-row disposition.

## 56. A short LOWER-CASE prose line is accepted as a doc-type heading — `resolve/assemble.py` (~line 1004)

From the ncbizct port, 2026-08-20.

`hart_v._dwm_advisors_llc` page 2 opens with the TAIL of paragraph 3 —
`judgment are deemed admitted.").`, 32 chars, 189pt wide — which
`heading_doc_type` types `JUDGMENT`. The `headmatter_claimed` rule at ~1105
then prepends `_body0` and keeps that anchor, **splitting one order at the page
break**.

Core alone never reaches the line, because the first heading it finds is the
caption's own `ORDER AND OPINION GRANTING` and the caption-band rule sends the
body below it — a row a reader has now claimed. So this only surfaces once a
court reads its own cover, which is why it is appearing now.

The existing `_wide` guard catches a full-measure prose line but NOT a
paragraph's LAST line, which is short by definition. One line:

    _wide = _col > 100 and (line.x1 - line.x0) >= 0.8 * _col
    # A HEADING DOES NOT OPEN IN LOWER CASE.
    dt = (None if _wide or len(head) >= 80 or head[:1].islower()
          else heading_doc_type(head))

Measured over the corpus, `hart` is the ONLY record with such a line, so the
patch moves this court by exactly one file. Same neighbourhood as item 48
(`heading_doc_type` reading `Opinion by <name>` as a heading) — both are
`heading_doc_type` being asked a question about a row that is not a heading.

**Do not pin `ncbizct/hart_v._dwm_advisors_llc` until this lands** — it comes
back with two orders where the paper has one.

## Item 10 — confirmed a second time, and closed locally by ncbizct

`publication_status` read out of a body parenthetical: core had
`ncbizct/fs_med._supplies_llc_v._tannergap_inc.` as **unpublished** off a
page-2 citation to ANOTHER decision, `*3-4 (2019) (unpublished)`. ncbizct now
declares status from the printed opinion number instead — this court numbers
`YYYY NCBC NN` only what it publishes and cites its unpublished work as
`YYYY NCBC LEXIS NN`.

## Two ncbizct judgement calls worth a human eye before more pinning

1. **The same-baseline join `v. Plaintiffs,`** — 13 rows across ~11 files,
   including two pinned sentinels. The court sets the pivot on the SAME
   baseline as the status above it; we reproduce the line as printed, v1 split
   them (which prints the status *under* the pivot it stands beside). If v1's
   reading is preferred, sentinels 1 and 3 change.
2. **`olds_v._olds` is deliberately unpinned**: its `IN RE: CUSTODIAL ACCOUNT
   OF …` recital and the plaintiff `DAVIS AUSTIN OLDS` merge into one party
   group, because the court separates them with a BLANK LINE and no status
   label — and a blank line is not a landmark the reader treats as structure.
   Reasonable, but not pinnable as correct.

Also from ncbizct, informational: core types 32 of these 42 papers `order` and
10 `majority` from an IDENTICAL masthead, which is why `doc_type_final` is now
stated by the reader rather than inferred. And `disposition` is set to a bare
`DENIED.` from body prose on two records — core's, not the reader's; thin but
not false.
