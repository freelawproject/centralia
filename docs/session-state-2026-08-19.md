# Session state — 2026-08-19 (paused mid-session)

## Where things stand

**38 courts complete.** Newly marked this session: fladistctapp, michctapp,
moctapp, ohio, nd (you had already marked all of these in the viewer; the
script only wrote court_status.json).

Full list: ala alacivapp alacrimapp alaska alaskactapp ark arkctapp bap1
bap10 bap6 bap8 bap9 ca1 ca10 ca11 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 cadc
cafc cal fla fladistctapp idaho iowa kyed mass massappct michctapp moctapp
nd ohio scotus

`ind` left at **started** — you said "mostly good a few stragglers"
(41 yay / 9 nay).

## BACKUP — done

- Tarball: `~/Code/rewrite-backups/rewrite-src-20260819-124408.tgz`
  (3.3M, 281 files, all 61 court files, marks.json + marks.log +
  court_status.json).
- **The repo is now under git** (local only, no remote). `output/*` is
  ignored except `output/notes/`, which holds your marks. 183 files
  tracked, `.git` is 23M.
- Two commits so far this session. Re-run `git add -A && git commit` after
  any further work.

## Core patches LANDED this session

1. **Panel-roster unweld** (`resolve/assemble.py`) — a run of >=3 short
   lines at one left edge is a stack the page newlined, re-emitted one
   paragraph per printed line. nd went 49/50 mangled -> 0/50. moctapp's
   phantom trailing writing also disappeared.
   Constants `_STACK_INK=0.45 _STACK_ROWS=3 _STACK_EDGE_TOL=2.0
   _STACK_STEP=(30.0,42.0)`.
   **The cap stays at 0.45.** Measured: raising it to 0.60 newly catches 20
   same-edge runs in a 10-court sample, all real prose that must stay
   joined (counsel-list wraps, caption wraps, footnote runs). Double
   leading also fails as a discriminator — nd's own rosters are 1.00x the
   body lead.

2. **Signature block takes the whole `/s/` run** (`resolve/assemble.py`) —
   the loop scanned back only 5 blocks and broke at the FIRST `/s/` from
   the end, so `cut` landed on the last signer only. haw left 34 of its 51
   conformed names in the body as dangling left-aligned prose. Now walks up
   the contiguous run; window widened 5 -> 12. **haw: 51/51 right-aligned.**
   Guard went UP, 313 -> 317 of 348.

3. **New `syllabus` headmatter role** (`render/html.py` + `courts/kan.py`) —
   Kansas prints numbered points of law BY THE COURT; headnotes are the
   REPORTER's subject list. 852 kan rows retagged off `headnotes`; the 50
   real reporter headnotes keep theirs. Own tint (#f2f4f6).

4. **Legend fix** (`render/html.py`) — `docket/date` was one key, so a
   document with dates and no dockets showed no date in the legend. Split
   into `docket` and `date`; added `title`.

## Courts wired / ported this session

- **gactapp** — wired (its agent left it unimported by design). 192/192
  rows tagged, 42/42 valid, quality A.
- **md** — its file existed at 37KB but was never imported. Now wired:
  **952/952 rows tagged (100%)**.
- **kanctapp** — NEW, copied from kan.py (court files may not import each
  other). The two papers differ in exactly one thing: kan sets
  masthead-then-docket, kanctapp sets **docket-then-masthead**. Gate
  widened to find the banner in the first two rows. **0% -> 81% tagged**,
  42/42 valid. 28 of 42 dispatch; the other 14 print a different paper.

## YOUR OPEN ITEMS — not yet fixed

### kanctapp — the panel row (edit was rejected, NOT applied)
"this is not an opinion `Before CLINE, P.J., BOLTON FLEMING, J., and
JEFFREY GETTLER, District Judge, assigned.` this is panel right?"

Yes. Measured: it sits in the **opinion body on 28 of 42** kanctapp records
and untagged in the headmatter on 15. kan has no counterpart (the Supreme
Court sits en banc; the Court of Appeals sits in panels), so this is
genuinely kanctapp's own.

The prepared fix (not applied): after the `_DELIVERED` recital check at the
end of `read_headmatter_kanctapp`, claim a row matching
`^Before\s+.*?(?:JJ?\.|Judges?)\b` as `panel` and set `crit["panel_line"]`.

### mo — the dissent boundary
`mo/d.j._by_and_through_his_next_friend_r.j._v._first_student_inc.`
Three defects, one cause. Writing 2 is typed `majority` but is Wilson's
DISSENT, and it opens with:
  1. the vote line `Russell, C.J., Ransom, Broniec, and Gooch, JJ., concur;
     Wilson, J., dissents in separate opinion filed; Powell, J., concurs in
     opinion of Wilson, J.` — which belongs at the END of the majority
  2. the reprinted caption `NEXT FRIEND, R.J., ) )` / `Respondent, ) ) v. )
     No. SC100702` / `)` — the cover the court prints atop the separately
     paginated dissent
  3. a THIRD writing with 0 paragraphs (phantom)

This is core-queue item 15 (reprinted covers, also mich/scotus/nj/wash).

### md — headnote/summary alternation
"instead of headnote summary headnote summary just make it all one headnote
section". md now tags `headnotes: 32` and `summary: 54`. Maryland prints
each headnote as a SUBJECT line (caps, en-dashes) followed by its
explanatory paragraph; the pair is one headnote, not a headnote plus a
summary.

### gactapp — two items
1. "we should in gactapp drop the seal and signature stuff in it" — 37 of
   42 files carry an image; the block is the clerk's certificate: two
   blockquotes (`Court of Appeals of the State of Georgia` / `Clerk's
   Office, Atlanta, 07/27/2026`) plus a PNG seal, sitting in sec-opinions.
2. "gets footnotes wrong weirdly" — **content loss across a page break.**
   In `in_re_estate_of_tien_thi_davis`, footnote 1 runs from page 1
   (`time for seeking an appeal. While OCGA 9-11-60(f) provides that a
   "judgment void`) onto page 2 (`time," the Supreme Court has
   explained...`), and the page-2 continuation lands in the BODY instead of
   rejoining its note. NOT a duplication — the note is filed correctly, the
   continuation is orphaned. Corpus scale UNMEASURED (my first proxy caught
   ordinary untagged page-turn continuations too and is not a valid count).

### haw — one row
`haw/lewis_v._department_of_hawaiian_homelands`: `ORDER DENYING PETITIONS
FOR WRIT OF MANDAMUS (By: Devens, C.J., McKenna, Eddins, and Ginoza, JJ.,
and Circuit Judge Wong, assigned by reason of vacancy)` should be part of
the headmatter.

### nj — NOTHING TO FIX
Your two nays (`state_v._darryl_nieves_state_v._michael_cifelli` and
`..._1`) are a duplicate in the SOURCE corpus: two PDFs of the same
consolidated case (748591 vs 753629 bytes), both 157pp. The only difference
in the rendered output is the source filename in the provenance line. Both
extract identically and correctly.

## Agents

**All 13 died in a network outage** (ENOTFOUND / connection lost / timeout)
partway through. Landed before dying: gactapp, fladistctapp (both reported
in full). Wrote files but never reported: md, kan, haw, iowa, michctapp,
moctapp, njsuperctappdiv, texcrimapp. Never wrote: nc, ind, tennctapp.

Two messages were queued to agents that then died and were never acted on —
the moctapp roster task and the kan syllabus task. The kan syllabus item I
then did myself. The moctapp roster item is still open:

### moctapp — the roster still welds
`JEFFREY W. BATES, J. – OPINION AUTHOR DON E. BURRELL, J. – CONCUR MATTHEW
P. HAMNER, J. – CONCUR` renders as one line. The page sets three rows at
x0=72.0, tops 434.0/463.9/493.7, ink 55%/40%/47%. Core's stack rule needs
every line <=45%, and moctapp's rows carry a name AND a role so two exceed
it. Must be fixed in `courts/moctapp.py` keyed on the court's own role
vocabulary (OPINION AUTHOR / CONCUR / ...), NOT by widening the core cap.

## Guard

317/348. The standing failures include courts whose readers moved this
session (cal, ariz, arizctapp, haw, michctapp) and virginislands/guam/idaho,
whose `op0_blocks` DROPPED — that was the blockquote-merging structure-wave
agent, not the roster patch (verified: `stack_events=0` on all three).

**25+ complete courts still have no role fingerprinting in their pins.**
Re-blessing all ~348 sentinels is still outstanding.
