# The district lane: what was refusing, and why (2026-08-20, evening)

Written after the user asked to "truly solve the district court ones" and then
fed me real records from the viewer. Every number here was measured on the
rendered corpus, not sampled by eye.

## The shape of the deficit

The lane had 90 courts, 2,556 pdfs, all rendered, and **97.0% of headmatter
rows claimed** (43,410 of 44,747). That average hid the actual problem, which
was not partial reading at all:

    records reading <60% of their block     75
    records with NO headmatter block        80
    per-court claim rate                    binary — 0% or 100%

**Every deficient record was a record the shared reader REFUSED outright.**
There was almost nothing in between. So the work was not "read more of the
block", it was "find the five layouts that make `read_ecf` return NOTHING".

To find them, each `return NOTHING` now names the gate it failed
(`ecf.LAST_REFUSAL`, diagnostic only — the return value is unchanged). The
dominant gate was `no-masthead-anchor`: the court never named itself in a
form the reader would accept.

## The five families that were missing

### 1. The DRAWN box (`STYLE_DRAWN_BOX`)

nynd, nysd and nyed rule the caption box instead of typing it: two horizontal
strokes at the body rail, stopping well short of the measure, one directly
under the masthead and one under the last party. Nothing is drawn between the
columns and nothing typed marks the band, so the strokes answer the same three
questions the typed `-----X` fence does — where the masthead ends, where the
band begins, what closes it.

Only the typed test existed. A drawn-box court sets its masthead flush left,
which the centring gate refuses, and the typed fallback found no rule, so the
record was refused for never naming its court.

    nynd    26.7%  ->  99.0%   (16 of 24 records were unread)
    nysd    54.0%  ->  90.5%
    nyed    67.5%  ->  90.3%

Told from every other drawn horizontal by three measurements: starts at the
body rail, stops short of the measure (`fence_max_reach` 0.90 — a rule running
the whole column is a header or a footer), and is long enough not to be an
underline (`fence_min_w` 120pt; nynd's strokes are 247-288pt).

### 2. One edge, drawn twice (`fence_join`)

dcd rules all four sides and its box's TOP arrives as two rects 2.9pt apart.
Read as top AND foot, the band closed 2.9pt below where it opened, came back
empty, and `united_states_v._li` was refused — a regression the 2pt join I
first wrote introduced. 7pt is over half a body line and far under any
caption's depth (dcd's own top and foot stand 111pt apart). `dboxed` also now
requires the band to be at least one line of type deep, so the failure mode
cannot recur through some other route.

### 3. Every dash the word processor might have used

nyed types its `-----X` with **U+2011 NON-BREAKING HYPHENS**. Tested against
four codepoints, the entire fence read as ordinary text: 29 unread rows on
nyed/532720 alone. `_is_typed_rule` now accepts U+2010, U+2011, U+2012,
U+2013, U+2014, U+2015 and the ASCII hyphen and underscore.

    nyed    90.3%  ->  97.9%

### 4. The measure, where core could not take it

`geometry.measure` returns None on a short pleading-paper record — cacd/980704
is two pages and most of what is on them is the line-number rail — and the
fallbacks then put the body rail at 72 and the axis at the PAGE's centre, 306
on a 612pt sheet. But pleading paper moves the whole text column right to
leave the rail its margin: that record's column is centred on **340**. The
masthead stood 34pt off an axis it was never set to.

The rail is already known at that point in the walk, so the column is
measurable without core: modal left edge of what remains, out to the widest
right edge.

### 5. Nothing drawn, nothing typed (`open_left`)

Some nysd/nyed chambers set the masthead at the body rail and mark the caption
with neither a rule nor a fence nor a rail. What stands in for the fence there
is POSITION: the row names the court, it stands at the rail, and nothing but
the clerk's stamp is above it. Where that is the evidence, the masthead's run
must end on the court's own name too (`_names_court`) — otherwise, with no
rule to break on, the run swallows the caption.

## Four defects the user found by reading records

### arwd — the paper's name read as the bench

`_JUDGE_CELL`'s office words plus `judges?\b` matched
`MAGISTRATE JUDGE'S REPORT AND RECOMMENDATION` whole: the row was tinted
`panel`, the court's own paper name was listed as a member of the bench, and
because it had been put in the caption's narrow right column it wrapped to two
lines ("the panel is not panel its title").

A judge cell says WHO — `Magistrate Judge Daniel J. Stewart`. The apostrophe
says WHOSE, and what follows it is the thing owned. `judges?(?![’']s)\b`.
`magistrate` was then added to `TITLE_OPENERS` (it was already in
`TITLE_WORDS` but could not OPEN a title), and `_is_title_head` now refuses a
named judge — the same veto `_is_title_tail` already kept.

### arwd — a title split across a caption row

arwd sets `REPORT AND RECOMMENDATION` on the same typed row as the last party
and its status, and wraps `OF THE UNITED STATES MAGISTRATE JUDGE` onto the row
below. The head was lifted out of the row; the wrap, alone on its own row,
stayed in the band and was tinted `case info` beside an empty party cell. A
lifted title now carries its wrap, recognised the way the closer's is: alone
on its row, at the paper's pitch, in the court's emphasis, continuing a title.

### arwd — a title set letter by letter

One chambers stretches the paper's name across the measure, and the gaps
arrive as spaces: `R   E  P   O   R   T    A  N   D  …`. `_letter_spaced`
measures the proportion of single-character tokens (so an ordinary title
carrying an initial is untouched) and the row is respelled from the court's
own closed vocabulary.

### arwd — one document rendered as two writings

Every page of a federal district filing carries the same stamp, and it opens
on the word a cover stamp opens on: `Filed 07/06/26     Page 4 of 5 PageID #:
926`. Counted as a filing stamp it made `_attached_documents`' strict test
true on EVERY page, which widened the banner window from four rows to eight —
and eight rows down an opinion, some sentence carries two court words. So
arwd/75862 was cut in two at page 4 and rendered as two writings.

What tells the overlay from a cover is that **the overlay names its own page**.
`_is_page_overlay`. Verified that the four real staples still cut:
calctapp/bates (1,28), calctapp/in_re_mccowen (16,20),
calctapp/citizens_against_marketplace (3,22), washctapp/asbach (2,21).

### cand — the sidebar bleeding into the body

cand rules pleading paper AND runs the court's own name sideways down the left
margin. The watermark arrives as 3-6pt fragments (`i`, `tr`, `uoC rof`) and,
where one shares a numeral's row, FUSES to it: `a 12`, `uoC rof 13`,
`iDtc 15`. No digit test can see either, and the mid-page fragments stand
clear of the form band — so on cand/431521 fifteen of them opened the writing
as its first paragraph and cut four body sentences in half.

The proof is the gutter the numerals already established
(`FurnitureFinder.doc_gutter_x1`): a row whose WHOLE ink stands inside that
column is the stationery, whatever it happens to spell. 23 rows now recorded
as `gutter`; the opinion opens on its real first sentence.

### wyd — the headmatter stopping short of the title

wyd closes its box with a row of em dashes **0.03pt** below the drawn rail's
own foot, so the floor left it standing. Neither bold nor centred, it broke
the title scan on its very first candidate and the paper's three-row name —
`ORDER AFFIRMING AND ADOPTING THE MAGISTRATE JUDGE'S REPORT AND …` — opened
the writing as three paragraphs instead.

A typed rule is now stepped over and recorded, never a reason to stop looking.
And a typed rule is never the court's name: wyd centres its box's top edge
(`_____` at x 204-408 of a 612pt sheet), so the centring test had been reading
it as a third masthead row. The masthead walk breaks on a typed rule, never
walks BACK over one (cacd rules the sheet ABOVE its own name, and walking into
the run then ended that run at its first row), and a single opening rule still
sets `band_lo`.

    wyd     86.7%  ->  100.0%

### nysd — the court's own underline

nysd sets its paper's name in the caption's right column in plain roman and
underlines it (`MEMORANDUM &` over a rule at 414.0-517.0 against the row's own
414.0-516.9). A test for bold or centring could not see it, so the record had
no closer at all. `_underlined` reads a drawn horizontal that begins and ends
with the row's own ink, struck through its descender band, as the chambers'
emphasis — the same statement bold makes.

## The second wave — what the first pass exposed

The first full re-render took the lane from 97.0% to 99.1% of rows claimed and
cut the sub-60% records from 75 to 27. Classifying those 27 by refusal gate
turned up four more things, three of them fixable.

### The box ruled at the FULL measure (mnd, wiwd — 6 records)

`_drawn_fence` required the stroke to stop short of the measure, because a
rule running the whole column is normally a header or a footer. mnd and wiwd
rule the box at the full measure: 72.0 to 526.0 of a column that ends at 526.
Held to 0.90 their edges were not a box, no closer was found, and the records
were refused.

What actually keeps a header rule out is not width — it is that the box's TOP
stands directly under the masthead. So the reach test was dropped
(`fence_max_reach` 1.02) and the box is now chosen from the strokes at or
below `mast[-1].top` (`_box` in the walk), with the band still required to be
at least one line of type deep. The search band for the FOOT also had to widen
from `closer_band` (0.55) to `box_band` (0.90): mnd/202185 names enough
parties to push its foot past 55% of the sheet, so only its top was visible.

    mnd     76.0%  ->  100.0%
    wiwd    95.9%  ->  100.0%

### The last status row is the caption's foot (ord — 4 records)

ord draws nothing, types nothing, sets the paper's name in the caption's RIGHT
COLUMN halfway down the block — so the title test cannot take it as the closer
without cutting off the defendants printed below it — and prints no
full-measure row on page 1 at all, because its counsel roster is a column of
short lines. Every closer the reader had came up empty.

But a caption ends by saying what its last party IS. `_is_status_row` is a
closed vocabulary that demands EVERY word be a status word, and nothing below
a caption satisfies it — ord's own roster ends 'Attorneys for Plaintiff',
which does not. Tried last of all the closers, so no court that closes any
other way is affected.

    ord     83.5%  ->  100.0%     flnd, ncmd also to 100.0%

### The box's own edges were stepped over, not CLAIMED (ctd — 11 records)

Invisible to the row-claim metric, which only counts `hmrow`s. The reader
steps over the fence rows — they are neither the court's name nor a caption
cell — but stepping over is not claiming. Unconsumed, ctd's '------------'
closer came back as CONTENT residual on 11 of its 31 records, which put every
one of them on the review worklist **with nothing whatever to fix**.

    ctd     20 valid / 11 review  ->  31 valid / 0 review

The lesson generalises: a court can sit at 100% claimed rows and still be
wrong, because `hmrow` counting cannot see what fell out of the block
entirely. Check `status` counts as well as claim rates.

### The stamp split at its column gaps (waed x3, ohnd x1)

The arwd cover-stamp fix was not enough. pdfio splits the ECF stamp at its
column gaps, and HALF A STAMP DOES NOT LOOK LIKE ONE: waed's pieces are
'Case 2:26-cv-00160-TOR', 'ECF No. 7', 'filed 07/06/26',
'PageID.29     Page 9 of 9'. Piece by piece the THIRD is a filing stamp in
exactly the strict form, and the page number lives in the FOURTH — so the
overlay test could not see it, the strict test opened the eight-row banner
window on every page, and waed/114266 was cut at page 19. Its own signature
block and two body paragraphs were rendered INSIDE the caption.

Two changes: the tests now read the whole visual ROW (`_stamp_row`, the same
device `furniture.py::_row_text` already uses), and 'of M' became optional in
`_PAGE_OF` — waed wraps its own total onto the next line ('… Page 19' / '19'),
so the row never says 'of 19' at all. What identifies the overlay is the page
it NAMES, not the total.

Verified both ways, which is the only way to change this function: the four
false splits are gone (waed/114266, waed/116383, waed/115610, ohnd/317063 —
arwd/75862 was the fifth) and all four genuine staples still cut —
calctapp/bates (1,28), calctapp/in_re_mccowen (16,20),
calctapp/citizens_against_marketplace (3,22), washctapp/asbach (2,21).

**This is why waed read as 93% with the reader returning a dict.** The
headmatter reader was working; `_attached_documents` was handing it a second
document to read. A court can look like a reader problem and be a pipeline
problem — check `_attached_documents` before touching a court file.

### A URL is not a missing space (harness)

`joins` flagged 'cdcrNu' inside
'https://ciris.mt.cdcr.ca.gov/details?cdcrNumber=AS1891' (cand) and graded the
record C. The allowlist cannot learn the web's query-parameter names, and no
opinion prose is set inside an unbroken run carrying '://' or a query, so
`quality._in_url` now excludes them. cand/431521 C -> A, arwd/75862 B -> A.
The remaining arwd flag is 'PrimeCare', a real clinic name, and stuffing the
allowlist is a losing game — left alone.

## The third wave — nynd, and what the claim rate could not see

The user, looking at the rendered output rather than the metric: "feel free to
look at nynd that isnt good at headmatter parsing" — with nynd sitting at
99.0% claimed and zero bad files. They were right. **Three whole blocks were
opening the opinion instead of standing in the headmatter**, and the row-claim
metric cannot see that: what falls out of the block is not an `hmrow` to
count. This is the ctd lesson again, and it is the most important thing in
this document.

Four causes on one court:

1. **The roster's end could not be recognised.** nynd closes its appearances
   block with the officer signing over his office on TWO rows — 'DANIEL J.
   STEWART' / 'United States Magistrate Judge' — and `_BYLINE_HEAD` wants
   'STEWART, Magistrate Judge' on one. Neither row could end the roster, so
   the roster was never closed and its whole tail — roster, announcement AND
   title — became the writing's first three paragraphs. `_OFFICE_ROW` plus
   `_is_name_row` now read that pair, and it is emitted as `author`.

2. **`counsel_max_rows` counted line PIECES.** A two-column roster is split at
   its column gap, so nynd's nine typed rows arrive as eighteen line objects
   and the 16-piece cap cut the roster in half — before the byline that
   actually ends it. The cap now counts distinct typed rows.

3. **`_APPEARANCE_END` demanded a full stop.** nynd closes each side with
   'Attorneys for Plaintiffs' / 'Attorney for Defendants' and sets no period
   on either, so the run was trimmed away to nothing. The period is now
   optional, and a run that states its party's own status
   ('Plaintiff, Pro Se') is accepted as having said who it appeared for.

4. **The title stands BELOW the roster.** The title scan ran from the box's
   foot and broke on 'APPEARANCES:' — bold, and no paper's name — so the
   title was never read on any of the court's 24 records. The scan now runs
   AFTER the roster, from below whatever it claimed. The roster walk had to
   learn to stop at a title in return, because for the far commoner order
   (box, title, body) the title stands first in that run.

Plus the docket: nynd and nysd bracket the judges' initials
('1:23-cv-01599 (AMN/PJE)', '25-CV-9876 (LTS)') and `_CASE_NUMBER` spelled
only the hyphenated and spaced forms, so those rows were tinted 'case info'
with no docket criterion read at all.

    nynd    415 rows claimed  ->  597      (24 records)

### A regression the walk caught: the stroke ABOVE the masthead

Allowing full-measure strokes for mnd and wiwd meant `_drawn_fence` began
returning page-border rules — it cannot judge which strokes are the box,
because it runs before the masthead is found. txed rules its sheet at 71.9 AND
114.7, both 72.0-539.9, with the masthead at 91.2 BETWEEN them: the masthead
walk broke on the first of them and the record was refused for having no
masthead at all. The walk now breaks on the first stroke strictly BELOW the
court's own name (`dbelow`).

    txed    96.1%  ->  100.0%

## What is NOT solved, and must not be counted as solved

**68 records lane-wide (2.7%) have an image-only page 1** carrying nothing but
the ECF stamp. There is nothing there for any reader to read.

    mtd  13/29   ded  11/25   cacd 10/22   vtd  5/33   nywd 4/26
    lamd  3/33   msnd  3/28   pawd  3/22   +11 courts with 1-2 each

Verified by splitting them on the whole document's text, not page 1's:

    59  are FULL SCANS end to end. `triage()` already calls these and flags
        'scan with OCR text layer; extracted, geometry untrusted'. ded/67860
        is 8 pages carrying 272 letters in total. Correctly handled today.
     9  are HYBRIDS: an image page 1 over a born-digital body — six cacd
        form orders (846 letters, 2pp, identical text), cacd/996274,
        mtd/83033, nysd/609828. They carry the 'N image-only page(s), no
        text layer' warning already.

For the hybrids I checked whether the caption survives anywhere else: it does
not. cacd/1024889 page 2 is pure continuation prose ('In responding to this
Order to Show Cause, Plaintiff shall identify…') with no masthead, no parties
and no docket. **The headmatter of these nine is only on the image.** No
reader can recover it; OCR is the only route. Do not chase them, and do not
count them against the lane.

**nysd/665741** has a judge's memo-endorsement typed across the caption at
8.5pt, interleaved BY TOP POSITION with the caption's own rows. It now gets
past the anchor gate and refuses at `band-empty-after-closer`. Deliberately
left failing rather than made to pass.

**vawd/136577 is a pdfio defect, not a reader defect, and is REPORTED not
patched.** Its clerk's stamp stands in the right margin on the SAME ROWS as
the masthead, and the column-gap splitter did not fire on the first of them:
the row arrives fused as

    'IN THE UNITED STATES DISTRICT COURT CLERKS OFFICE US DISTRICT COURT'
    x 178.4-564.1 on a 612pt sheet

Its midpoint is 371 against an axis of 306 — 65pt off, so no centring test can
accept it — and it does not start at the body rail either, so the flush-left
fallback cannot take it. The row below it splits correctly ('FOR THE WESTERN
DISTRICT OF VIRGINIA' at 174.0-437.9 beside 'AT HARRISONBURG, VA' at
467.1-544.8), which is what makes this a splitter miss rather than a layout.

The fix belongs in `pdfio/build.py`'s row splitting. That file was being
rewritten by another session throughout, so per the standing parallel-porting
rule it is diagnosed here and left alone. Do NOT work around it in `ecf.py` by
guessing where the masthead ends inside a fused row.

### Reported, not patched: the signature block (7 records, 3 courts)

Swept for exhaustively — every district record whose status is `review` with
NO source warning, i.e. a parse complaint and nothing else. Seven, and all one
defect class: the signature block's own rows left as CONTENT residual.

    wiwd  44170, 53741, 55031, 56711   'BY THE COURT:'  '/s/'
    vawd  131341, 138836               '/s/ Robert S. Ballou'  'Robert S. Ballou'
    vtd   32844                        'DATED at Burlington, in the District of…'

Headmatter is 100% claimed on all seven. This is core's signature assembly,
and `resolve/assemble.py` was being rewritten by another session throughout,
so per the standing parallel-porting rule it is diagnosed here and left alone.

**That sweep is the useful part, not the seven files.** `status == 'review'
and not warnings` isolates parse defects from PDF properties in one pass, and
it is the check the row-claim census cannot do.

## Where the lane finished

Measured on the final render of all 90 courts, 2,217 records, 0 errors.

    headmatter rows claimed     38,314 / 38,375   99.8%   (was 97.0%)
    courts at exactly 100%          84 / 90
    records reading <60%             5              (was 75)
    valid                        2,119
    scanned                         38
    review                          59   — 52 source complaints, 7 signature
    failed                           1   — one CID-damaged PDF

The five records still reading under 60% are named above: three are image-only
page 1s (ohsd/287991 — the record this session opened on, txnd/408989,
vtd/40027), one is nysd/665741's memo endorsement, one is vawd/136577's fused
masthead row (a pdfio defect, reported).

## Process notes

- `pdfio/build.py`, `courts/__init__.py`, `pipeline.py`, `resolve/assemble.py`
  and `resolve/segments.py` were being edited by ANOTHER SESSION throughout.
  A transient `NameError: find_grids` came from reading build.py mid-write.
  Re-run rather than diagnose when an import breaks for one call.
- 10 cores here, and the other session held an 8-worker pool: a serial
  `harness/cli.py render` over the lane was starved to ~1 court per 6 minutes.
  `scratchpad/prender.py` renders in a 4-worker pool instead.
- Do NOT `render $(ls output)`. That is all 238 courts, and it re-renders
  state courts the other session is mid-edit on.
