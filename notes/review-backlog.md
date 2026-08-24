# Review-sweep backlog (headmatter-style-reviewer findings)

Fixed already (2026-08-16):
- ✅ Column-split rows losing their text piece (`single` used lines[0] only)
  — ill ¶-paragraphs, idahoctapp/del headings, and kin.
- ✅ Paragraphs split at page breaks (`_flush_merge`: unterminated tail +
  lowercase head joins, including blockquote-misclassified continuations).

Fixed in the same pass (shard 1 + follow-ups):
- ✅ conn/connappct running heads injected at page breaks (top band → 0.22;
  heads sat at 0.214 on 792pt sheets).
- ✅ calctapp end-signature collapse (signature-cluster demotion; body was
  landing in headmatter with signature-only writings).
- ✅ Trailing counsel after the last writing → attorneys (fla/ind/ark class).
- ✅ Announcement-dup dedup made case-insensitive (MCCONNELL/McCONNELL).

Fixed from the attorneys-reviewer batch 1 (2026-08-16):
- ✅ Strong/weak counsel marks (nj syllabus prose no longer classifies as
  counsel via 'for the defendant').
- ✅ Window-based trailing-roster harvest (ind/ohio/fla/mass end rosters
  with interleaved address blocks now reach attorneys).
- ✅ Line-level panel/disposition peel inside counsel segments (dc 'Before
  MCLEESE…', conn 'Affirmed.').
- ✅ Leading appeal-from/history peel (njsuperctappdiv example case).

Fixed from headmatter-style shard 3 (2026-08-16):
- ✅ kan counsel/blockquote continuations dropped as positional running
  heads (head positions now require SHORT lines, ≤0.55 width).
- ✅ me official citations ('2026 ME 14' / 'Som-25-258') eaten as corner
  stamps (neutral-citation/docket guard).

Open from headmatter-style shard 3:
- **me overstruck-italic char interleaving** (450 corruptions/file: the
  '(Benson, J.)' parenthetical interleaves char-by-char into body text) —
  pdfio quirk work, HIGH priority for Maine quality.
- **ky/kyctapp two-column caption order** (banner/docket flattened after
  parties; consolidated captions interleaved; counsel footers scrambled) —
  same family as guam counsel columns.
- **ind marginal [N] paragraph numbers** (dropped as stamps or injected
  mid-sentence) — needs the ill-¶-style same-row treatment for the
  bracketed-margin variant.
- **md short orders: body as headmatter, opinion = signature only.**
- **la trailing dissents not segmented** ('WEIMER, C.J., dissenting.'
  inside the majority block).
- **lactapp counsel names divorced from role labels.**
- **kan 'SYLLABUS BY THE COURT' stays in headmatter** (syllabus field
  empty); md headnotes similar.
- **iowa/mass counsel left in headmatter** (front-matter counsel blocks not
  hitting the marks — check mark coverage for 'attorneys for appellee.'
  tails split across lines).

Fixed from headmatter-style shard 4 (2026-08-16):
- ✅ OCR-layered scans now EXTRACTED with review status (nev/nevapp/tenn
  wigdor/lactapp writ — wholesale-loss class dead).
- ✅ michctapp caption-divider phantom zone (a rule with 'Before:' roster
  below it is a caption shelf, never a separator) — schubiner recovered
  with byline + 15 footnotes.

Open from headmatter-style shard 4:
- **mont missing-space line joins** ('granting defendantsDennis E. Lind')
  — inline_text loses the inter-line space at bold/italic/small-caps
  boundaries; worst live text-corruption class. pdfio work.
- **Section-router decapitation**: first line(s) of caption-page paragraphs
  stay in headmatter as hmrows, rest flows onward mid-sentence (mich syllabus,
  minn, mo/moctapp bodies, nh counsel). One root: headmatter routing is
  segment-scoped; needs paragraph-scoped continuation.
- **miss/missctapp label:value caption tables shredded** (labels divorced
  from values; fused rows in attorneys).
- **neb advance-sheet headnotes** need a numbered-headnote parser (hyphen
  stubs, fused items).
- **mich caption right-column roster loss** ('Brian K. Zahra' at 456.5R
  vanishes — grid pairing drop, not in dropped).
- **Signature stacks fuse or become headings** (/s/ rows, small-caps
  justices).
- **Heading classifier instability** (same doc: sibling headings as
  h3 / blockquote / p).
- **mont concurrence fn attached to dissent list** (all_families fn4).
- **mo Supreme chips 'order' + duplicated end-signature byline.**

Fixed from headmatter-style shard 5 (2026-08-16):
- ✅ nm/ind/ill paragraph markers ('{4}', '[3]', '¶ 12') exempted from ALL
  furniture rules.
- ✅ or margin folios on shared rows dropped by position.
- ✅ pa 'JUSTICE MUNDY DECIDED:' byline mangling (date-label stops the
  name walk and the clause).
- ✅ pasuperct 'OPINION/MEMORANDUM BY BENDER, P.J.E.:' headings (grammar +
  spread-safe abbrev matching).

Open from headmatter-style shard 5:
- **CRITERIA EPIC**: parties fused with dockets/banners/boilerplate (12/14
  courts), decision_date = argued date (nj) or missing (pa, ohio, nmctapp),
  docket_number takes cite fragments ('2026-Ohio-1230.]'). Needs a
  systematic read_headmatter/criteria pass.
- **or folio INSIDE the text line** ('728 form of workers…' — pdfio merges
  the margin folio into the line; needs char-level margin split).
- **Footnote text hoisted to body** (or/allen fn1 blockquote; pasuperct
  fn continuations; '(Footnote Continued Next Page)' handling).
- **nm WE-CONCUR signature pages** parsed as phantom footnotes with
  justice-name labels + gutter digits as body paragraphs.
- **nc byrd majority split at mid-citation into phantom per-curiam** +
  unsegmented 'Justice EARLS dissenting.'
- **nysupct OCR running feet as headings** ('Page 1 of 9').
- **pasuperct CID garbage folio** ('(cid:0)(cid:16)…' kept as paragraph).
- **or de-hyphenation intermittent** ('back- ground' family).
- **njsuperctappdiv SABATINO 'P.J.A.D.' title split** ('A.D.' glued to
  body).

Fixed from headmatter-style shard 6 (2026-08-16):
- ✅ sd '[¶N.]' paragraph markers exempted from furniture.
- ✅ OPINION/O P I N I O N banners now render as the writing's heading
  instead of being consumed (tennctapp/tenncrimapp/texcrimapp).
- ✅ Delivered-announcement bylines no longer severed mid-name (longest
  full-line kindless parse wins — 'in which J. STEVEN STAFFORD…joined.').

Open from headmatter-style shard 6:
- **prapp footnote/caption docket drops** (fns 3-11 dropped as running
  feet or vanished; p1 caption docket eaten by the p2+ running-head key).
- **Footnote continuations spliced into body** (sd/advisory, utah/armenta
  '(continued …)' markers) — cross-page fn continuation epic with the
  or/pasuperct cases from shard 5.
- **RI orders swallow the first paragraph into headmatter** (md/mo class).
- **prsupreme variant running heads leak as h3** (~24×/80pp; dedup fails
  when the head's text varies) + bold body lines rendered as headings.
- **sc/amazon counsel severed mid-sentence across sections** (page-break
  counsel continuation class).
- **texapp Sitting/Delivered/disposition rows fused into body.**
- **tenn filed stamps ('07/15/2026') dropped** — the only filed date in
  that format; should reach criteria.decision_date.
- **utah panel-attribution block emits phantom first majority.**

Fixed from headmatter-style shard 7 (2026-08-16):
- ✅ Duplicated first line in ¶-byline courts (vt/wis/wisctapp) — byline
  row-mates claimed across segments; paragraph re-united by flush-merge.

Open from headmatter-style shard 7 (mostly reinforcing existing epics):
- **Two-column interleaving epic** grows: wva/guam counsel columns, vt
  caption+notice grid, wash re-captions, va order pages (12+ majors).
- **Byline-less openings absorbed into headmatter** (va OPINION-BY style,
  wvactapp memoranda, wis/wash per curiams, ri orders, md orders — one
  epic: headmatter/body boundary fallback when no byline exists on p1).
- **Docket numbers dropped as stamps** ('Record No. 240830', '2025AP825',
  vi caption rows) — retain anything matching the case's own docket.
- **texapp Q:/A: testimony labels mis-paired**; guam '[N]' markers as
  centered h3 (marker-piece binding, ind class).
- **wash '(cid:NN)' signature glyphs** (unmapped font in signature).
- **vactapp counsel pairs fused into one attorneys block** (needs
  paragraph-gap splitting — multi-appearance epic).
- **nmariana concurrence 'MANGLOÑA, J., concurring:' not segmented.**
- **vactapp literal fn marks in headings ('BACKGROUND2').**

Fixed from headmatter-style shard 8 (2026-08-16, federal):
- ✅ Top-band folios cut even beside row-mates (ca6 'Page 2' fusion, ca11/
  cafc/cadc standalone folio paragraphs).
- ✅ Unterminated 'Before …' roster wraps suppressed as writing boundaries
  (ca4 gietz phantom).
- ✅ ca2 stationery numbers welded into the text line split at pdfio
  (margin-fragment split, citation-safe).

Open from headmatter-style shard 8:
- **Foot folios fused INTO the line** remain where pdfio merges them
  (ca11 '4 about' bottom variants, or '728 form…') — needs the margin
  split generalized to trailing/foot fragments.
- **ca6 bracket-rail caption loses the docket** ('No. 25-1802' beside the
  '>' glyph never lands).
- **scotus/ca9/ca2 syllabus first page as headmatter rows** (the
  byline-less-openings epic — biggest remaining class).
- **ca9 clerk FILED date dropped to removed** (date loss).
- **Hyphen retention at row joins** (ca5/ca7/ca11/cafc/scotus 'pro-posed'
  family — vocabulary can't prove all words; consider welding without
  space when unproven instead of keeping 'pro- posed').
- **cafc counsel torn across three fields** (page-break counsel epic).
- **ca10 Before-line in body; ca4 'I. A.' heading fusion; ca1 clerk
  signature/cc fusions** (minor).

Open from attorneys-reviewer batch 1:
- **guam two-column counsel scrambling** (row-wise reading misattributes
  lawyers to the wrong party) — same class as the back-page interleave.
- **Counsel page-break fragmentation** (njsuperctappdiv dcpp justified
  lines shredded into headmatter fragments; tenn amicus stranded).
- **Multi-appearance fusion** (several counsel paragraphs in one block —
  needs paragraph-gap splitting inside counsel segments).
- **ind letterspaced counsel headers** ('ATTORNEY FOR A PP E L L AN T' —
  needs the letterspace fold applied to counsel text).
- **nj criteria.decision_date takes the ARGUED date** (all nj samples).
- **tenn OCR-layer scans yield empty docs** (design decision — triage
  calls OCR scans scans; revisit whether counsel should be salvaged).
- **ark dodson: dissent with stripped byline classified as attorneys.**

Open, by priority:
- **alaska announcement pairs** ('PATE, Justice.' + 'CARNEY, Justice,
  dissenting.' adjacent announcement rows) — majority text lands under a
  dissent chip.
- **ark/illappct caption grid interleave** (disposition column interleaved
  with parties; sidebar shredded).
- **Centered section headings never promoted** ('I. Facts', 'Standard of
  Review' render as p/blockquote; h3.bhead unused) — style-level, broad.
- **Footnote continuation on disposition pages** routed to body as
  blockquote (ala/alaskactapp fn tails).
- **ariz split authorship line** ('…in which' second majority stub).
1. **Two-column back-page counsel/signature interleaving** — guam (counsel
   columns row-interleaved and mispaired), haw/hawapp (counsel × /s/
   signatures interleaved). Needs column-aware reading of trailing blocks.
2. **End-of-opinion counsel not routed to `attorneys`** — fla,
   fladistctapp, ind leave counsel in the writing body (the counsel-marks
   routing only runs on headmatter segments; trailing counsel needs the
   same test).
3. **'?' mega-notes** — fla/brito fns 8–31 merged into one unlabeled note;
   ind/nemeth headmatter items fused into a '?' footnote. Zone label
   detection failing mid-doc on these layouts.
4. **Spurious bylines from signature blocks** — haw/hawapp/del orders mint
   an author from '/s/ NAME' + title lines near the end.
5. **Caption rail glyph leaks** — idaho ')' pieces, gactapp underscore
   fill-ins ('ATLANTA,__Ju_l_y…'), illappct caption grid interleaving
   parties with the right column.
6. **Clerk-certificate removal without a `dropped` entry** — gactapp
   (consumed_ids silences residual but breaks the audit trail; should be
   surfaced as dropped kind='attestation').
7. **ga notice tail eaten as corner stamp** — 'official text of the
   opinion.' (short line, top band) hits the corner-stamp rule.
8. **dc/barlow literal footnote marker** ('taxes.5' not superscripted) and
   ind letterspaced heading garble ('ATTORNEY   FOR  A PP E L L AN T').
9. **hawapp table flattened** (fn7 — no table model yet; known limitation).

## Session 2026-08-16 — sweep-driven fixes (whitespace + notice/stamp reports)

Fixed this session (all courts re-rendered after):
- **Caption cell loss** (`_paired_caption_block` kept only the first cell
  per side) — me's 'Docket: PUC-25-60'/dates vanished silently; cells now
  JOIN. Same fix restored every label+value caption corpus-wide.
- **me corner-stamp overdrop** — all-caps dockets ('PUC-25-60') and caption
  labels ('Docket:') exempted from the corner-stamp rule.
- **Notice-boilerplate dropper generalized** (was conn-only): reporter
  cues (subject to formal revision / reporter of decisions / advance
  sheet / typographical / formal errors / Detroit Timber / readers are
  requested / before publication in / superseded / bound volume / further
  editing) + line-level peel with band-adjacency reunification for
  split notices. Verified: ala, scotus (both blocks), ohio, ga, mich,
  mass, ri, dc, alaskactapp, wisctapp.
- **Stamp-group peel**: haw/hawapp 'Electronically Filed' blocks, ca10
  right-margin FILED/Clerk box (center-axis grouping).
- **(cid:N) decode quirk** — +29 offset per font, plausibility-gated;
  (cid:0) notdef dropped. wash fully decoded ('Johnson, J.', 'WE
  CONCUR'); pasuperct brown 1013→403 (rest is a corrupt font, refused);
  tenncrimapp kelley refused (junk mapping) — OCR candidates.
- **Footnote first-line dehyphenation** ('Ex- change' class: scotus 1178,
  ca7 442, cafc 321…) — vocab-proof weld in _group_footnotes.
- **Empty <strong> </strong> debris** stripped at inline_text.
- **Byline grammar**: joint caps names ('MILLETT and GARCIA, Circuit
  Judges:'), inline joint + plural titles, ca5 en banc 'joined by …,
  Circuit Judges:' (colon-terminal exemption from roster-tail guard),
  ri 'Chief Justice Suttell, for the Court.' inline majority marker,
  me panel-list byline ('DOW, J., MURRAY, J., and STOKES, A.R.J.').
  cadc national_trust 0→2 opinions (1041→23 hmrows); ca5 nathan →7
  opinions; ri carreiro 400→26 hmrows.
- **Criteria**: submitted (argued date) split from decision_date (label
  row-mate awareness), judges/panel from rosters, lower_court from origin
  rows, scotus '—Decided <date>' harvested, docket truncated before
  apparatus, banner two-court-word rule, apparatus rows out of parties.
  Criteria now rendered as a collapsed box in review HTML.
- **Quality grades**: harness/quality.py + `quality` CLI → per-file A–F +
  court rollup in output/notes/quality.json; viewer shows grades
  (court list, file list, title flags) via /api/quality.
- **Viewer**: refresh keeps current file (URL hash + localStorage).
- **Scan-stub staleness**: virginislands/nysupct extract fine now (OCR
  salvage postdated their last render) — fixed by re-render.

Open (new, from the sweeps):
- **prsupreme/prapp votos segmentation** — Spanish constituent writings
  swallowed into headmatter (mcg_therapy 121pp hm; redmane 965 frags).
- **tenncrimapp/pasuperct corrupt-font pages** — cid decode refused
  (non-+29 orderings); needs OCR or per-font maps.
- **wyo notice printed as a headmatter FOOTNOTE** — notice peel doesn't
  see hm footnotes.
- **neb/nebctapp p1 'Advance Sheets' banner** (p2+ dropped as running
  head; page-1 exemption gap).
- **ca5 'not designated for publication' one-liner** renders in opinions;
  headmatter-worthy.
- **wash dissent running-heads kind-labeled 'stamp'** (cosmetic).
- **scotus parties** from syllabus-format caption still garbage.
- **me displaced-italic pass** — snap_displaced_fragments generalized
  (interlock test: collision-free x-fit within a host row 4–32pt away,
  fonts disjoint; self-row host bug fixed). me coverage worst 0.945→0.977.
  Residual tail (~2% on 4 files: sean_eori, mccoy, ballot_challenge,
  h.a.t.) is a further variant — investigate post-corpus-coverage.
- **coverage harness** — harness/coverage.py (`coverage` CLI): pdftotext
  oracle vs rendered+dropped words; output/notes/coverage.json.
- NOTE: re-render batches aa/ab ran WITHOUT the displaced-italic interlock
  fix (launched earlier); corpus coverage pass will flag any court that
  needs a re-render under the newer quirk.

### Coverage-driven wave 2 (same session, post-corpus-render)
- **mich 'BEFORE THE ENTIRE BENCH' bylines** — midsentence Before-guard
  now accepts ')'/':' terminals and the bare 'bench' idiom (17 mich files
  0→1 opinions; latent since 08-14, surfaced by re-render). ca4 verified.
- **lactapp writ scans stubbed empty** — OCR-salvage ink floor 500→250
  (a 1-page writ disposition is ~350 chars; stamp overlays still stub).
- **wis 'Statement of NAME, J.' orders** — name-led Statement-of branch
  (was reversed-grammar-only); planned_parenthood statement recovered.
- **Hybrid image-only pages** — warning '<n> image-only page(s), no text
  layer' + review status (wis reprint appendix).
- **va unsigned full-court orders** — classify cues 'this matter comes
  before the court' / 'upon a petition for review' → ORDER (koski 0→1).
- **utah 'PER CURIAM**:' with footnote stars** — star/PUA glyphs allowed
  between name and colon (league_of_women 0→1).
- **gactapp clerk certificate** — now surfaced as dropped kind=attestation
  (was silent consumed_ids; Assembled.dropped added).
- **coverage accounting** — furniture drops weighted by PDF page count;
  dropped-text cap 400→1200; UELMA signature-annotation boilerplate
  (invisible to pdfminer) discounted. md 32→2 flagged (at-floor noise).

### Reviewer verdicts + wave 3 (2026-08-17)
30 worst files reviewed vs PDFs (0 pass / 3 minor / 27 major). One defect
explained 26/30: me's displaced-italic interleave. Fixes landed:
- **Displaced-run second pass** (quirks.snap_displaced_fragments): orphan
  interleaved runs (no host hole — italic HEADINGS whose true band is
  empty) move by the page's median measured snap-delta, or the host-row
  pitch when no snap measured; band-clear guarded. me coverage flags
  41→19, davis/mick_land case names + headings restored inline.
- **'ST. EVE, Circuit Judge.'** — saint-prefix (S[Tt]\.) added to the
  prose name grammar; ca7/khouri 0→1 opinions, ca7 100/100 valid.
- **nd counsel loss** — announcement-dedup now REHOMES a doomed twin's
  blocks to the survivor (never consumes); leading-counsel harvest routes
  'on brief' head blocks to attorneys. nd 15 flagged→0 (worst 0.996).
- **Coverage oracle discounts**: pdftotext dehyphenation variants
  (threejudge = three-judge), UELMA annotation boilerplate, furniture ×
  PDF-page-count. Corpus flags 1454→136 (src≥50: me 19, md 27 at-floor
  annotation noise, pasuperct/tenncrimapp 18 corrupt-font).
Catalogued (reviewer, still open): me fns 2–3 rendered inline in body
(davis); me counsel-section routing inconsistent across files; conn
ligature+space split ('fi rst', ~150 words/file, cosmetic); mont
run-boundary space fusion ('neglectand'); texapp corpus contains two
non-opinion filings (one rot+3 corrupt text layer — OCR only); me
residual interleave (~1-2 lines in worst files, e.g. fifth_generation).

### Visual-reviewer pilot + fixes (2026-08-17, session 2)
New agent: .claude/agents/visual-reviewer.md — rasterizes pages, LOOKS at
them (Read on PNGs), compares against rendered HTML. Pilot on michctapp/
ahmed, pasuperct/adoption (verify), calctapp/aqualliance (verify) found:
- FIXED **calctapp fabricated byline** — 'ROBIE, Acting P. J.' now parses
  (Acting/Presiding/Associate prefix before abbrev titles); the author is
  ROBIE, not the 'We concur:' signer KRAUSE. Type now 'majority' (prose
  head inherits the DOCUMENT's OPINION classification).
- FIXED **blockquote-cast headings** — centered caps headings that segment
  as blockquotes now get the same heading test as 'single' (michctapp
  'II. STANDARD OF REVIEW' etc.; all 7 headings consistent).
- FIXED **banner inside caption grid** — leading band rows spanning both
  columns render as full-width hmrows, not cap-left cells (michctapp
  'STATE OF MICHIGAN'; also cleans criteria.parties).
- FIXED **stacked /s/ signatures joined** — render keeps one signer per
  line (<br> before each '/s/').
- FIXED **'FILED: <date>' body leak** — harvested to criteria.decision_
  date + dropped as stamp (pasuperct adoption now has its decided chip).
- Earlier same session: pa doubled colon rail (leading rail glyph strip),
  pasuperct consolidated multi-docket rail boxes rebuilt as caption grids
  (rail-column evidence, cell-never-crosses-rail), signature graphic
  stash (kind=signature, dims + date), mitchell OPINION BY + FILED row-
  mate, J-session-number never a docket, rail-glyph strip in docket
  detector, date-rows never dockets, calctapp cover-banner prose anchor,
  2-weak-marks counsel, compact docket C102382, appeal-from initial-wrap
  peel, quality flags hm-overrun + authorless, ShotSpotter-class repeat-
  join discount.
Open (visual pilot, minor): michctapp fn italic loss (Hoyt v Hoyt);
pasuperct 'I.' enumerator promoted to bhead; p2 paragraph split mid-
sentence ('removed from|Mother's care'); merged adjacent blockquotes;
bold-italic 'See' loses marks in fns; publication-notice row alignment;
Kohler/Prothonotary typed lines near signature graphic not quoted in
removed box; calctapp signature names as bheads; criteria disposition/
history/lower_court duplication + truncation.
- **REGRESSION caught & fixed same session**: the displaced-run gate used
  SPAN overlap, so ca5's interlocking italic panel names (small baseline
  offset, correctly positioned) were thrown one pitch away — 36 ca5 files
  lost their opinions. Gate now requires GLYPH-BOX COLLISIONS (true
  displacement lands ON foreign text; correct interlock touches nothing).
  me davis verified still clean. hm-overrun threshold 80→220 (mich/nj
  letterheads legitimately run ~100–190). Full corpus re-rendered.

### guam "lines in headmatter" + cadc roster interleave (2026-08-17, session 2)
- **guam gutierrez**: the headmatter "lines" were the counsel column-header
  UNDERLINES rendered as full-width rules — the underline exclusion now
  tests the PAGE's lines (the decorated rows had routed to attorneys) with
  4pt tolerance (also kills the p2 running-head underline). The markless
  right-column tail ('111 Chalan…') now MERGES into the counsel segment
  (column-edge continuation) — no more hm leak; two-column counsel renders
  line-per-line (address roster), gated on _column_order actually firing.
- **cadc accuracy_in_media** ('CJir Ucu Dit JGu dMge Es' garble): the snap
  interlock now tests the host's whole LINE BAND (small-caps rosters split
  across two baselines and read falsely sparse), requires the frag's ink
  to fit real WHITESPACE (not kerning gaps — 'JUDGMENT' dodged the dense
  roster collision-free), and requires ENGAGEMENT not containment (a run
  may own the host line's tail — mick_land 'cf. Dionne v.').
  Verified simultaneously: cadc roster clean, ca5 roster clean, me davis
  0 interleaves, mick_land Dionne inline.
- Corpus re-rendering with final quirk logic (lanes restarted).

### Syllabus extraction restored + cadc caption fidelity (2026-08-17, session 2 cont.)
- **Syllabus-page routing** (user: 'like we did in centralia'): a page
  OPENING with a standalone SYLLABUS heading (first three rows, or a
  ≥3×body watermark — mich) starts a syllabus block; following pages
  continue until a court-banner page (the real caption). All hm segments
  on those pages route to doc.syllabus as flow. nj caneiro 120 hmrows→14
  with a proper 17-block syllabus; mich hairston syl=18; scotus syl=15;
  conn unaffected (interior 'Syllabus' heading excluded).
- **nj clerk-note cues** ('prepared by the office of the clerk' / 'may
  not summarize all portions') → dropped as notice.
- **Syllabus criteria backfill**: docket ((A-1-25) paren form + generic),
  decided (date_row_value incl. long-paragraph 'officially released'),
  argued — for pages that bypass read_headmatter.
- **Label-GRID dates**: 'Argued | Decided' label row above a values row
  pairs by COLUMN, not reading order (nj crosswired decided=argued).
- **find_date**: footnote marks on the year ('2026*' — conn) stripped.
- **conn docket**: '(SC 21196)' accepted from the post-cover caption page.
- **cadc headmatter**: short centered separator dashes (36pt '────')
  render as span-center rules (width<60 floor exempted, in-band allowed);
  hanging-indent status labels ('APPELLEES' at +108pt) reproduce via
  HmLine.rel on plain rows (never caption cells).
- Corpus lanes restarted with the complete set.
- **nh torn counsel wrap** — a counsel segment opening lowercase under an
  unterminated neighbor pulls the torn first line(s) in (backward merge;
  the marks live on continuations). nh doe: both counsel paragraphs whole.
- **nh underlines invisible** — tag_underlined_chars offset window now
  starts at −2.5pt (char-box bottom includes descender space; nh draws at
  −1.3; strike-throughs at −4 stay out). nh doe: 85 <u> runs (case names,
  counsel, 'See' signals).

## THE GUARD (2026-08-17) — how fixes stop breaking other things

`uv run python harness/cli.py guard` — 56 pinned sentinel files, ~14s.

Every defect fixed in this project came from a real file; each of those
files is now PINNED with its structural signature (status, opinion kinds,
whether the lead writing is bylined, headmatter size, section sizes,
residual count, which criteria were found). A diff in any of those means
a regression, and the guard prints exactly which field moved.

RULE: run the guard after EVERY engine change, before moving on. It is
fast enough that there is no excuse. Only `--bless` after confirming a
diff is an intended improvement (it re-pins every sentinel).

    guard                 check all
    guard ca9 ca10        check some courts
    guard --add c/stem    pin a new case (do this for every new fix)
    guard --bless         re-pin (state verified good)

Why this exists: during the 2026-08-17 federal review, five separate
fixes silently broke other courts (the displaced-run gate cost ca5 36
opinions; a front-matter change cost ca9 its summaries twice; a COUNSEL
heading left ariz files in residual; a summary section flipped scotus to
review). Each was found by the USER, not by me. The guard closes that.

It caught its first defect the moment it was written: ca5/nathan's en
banc majority was typed as the raw joiner clause
('joined-by-elrod,-chief-judge,-and-jones,…') instead of 'majority' —
normalize_opinion_type now maps a joiner list with no participle to
majority.

## The v1 oracle (2026-08-17) — `uv run python harness/cli.py v1diff`

v1's frozen output (baseline/, 18 courts) is a correctness oracle: v1 parsed
most courts right, one court at a time. `v1diff` diffs v2 against it and
writes notes/v1-diff.md, ranked worst-first. Use it instead of eyeballing.

FIRST FULL RUN: 271 diffs / 18 courts.
- **scotus, conn, ca4: ZERO diffs** — those courts have reached v1 parity.
- `doc-type` 229, of which 114+ are `opinion -> order`. v1's own lessons doc
  admits it called 88% of the corpus 'opinion'; v2 classifies precisely.
  NOT defects.
- `opinion-count` 39: 29 where v2 finds MORE (several verified v2 wins —
  ca10/garrett's concurrence, calctapp's rehearing denial, wis's dismissal
  order, all of which v1 missed) and 10 where v2 found FEWER.

The 10 "v2 missing" cases, resolved:
- FIXED ca2/carroll, ca2/havlish (partial), ca10/watkins, ca9/vericool,
  ca5/busby (partial) — see the rules below.
- v2 IS RIGHT, v1 over-counted: mont/roaring_lion + mont/state_v._a._emmings
  (v1 counted the '/S/ …' concurrence signature block as a second writing);
  cadc/adsync + cadc/john_doe (one-page sealed-opinion PLACEHOLDERS — caption
  + roster + 'OPINION UNDER SEAL / NOT AVAILABLE TO THE PUBLIC', no body at
  all; v1 manufactured a majority from the placeholder).
- open: ca10/national_association (4pp, single Per Curiam — v1 likely
  double-counted), ca2/havlish's 5th 'statement'.

Rules added from this pass (all general, all guard-pinned):
- **A court pronouncing its own disposition anchors a writing** ('the
  petitions for rehearing en banc are hereby DENIED') even with no heading
  and no byline — recovered ca2/carroll, ca2/havlish, calctapp, wis.
- **A measured caption band may run to the page foot**: prose inside it is
  not automatically caption matter — step past the band and look again.
- **An order that announces its separate writings inside its own body is
  still the order** (ca10/watkins says 'Judge Hartz has filed a separate
  opinion…' then denies the petition) — the court's own disposition
  pronouncement is what separates an order from an announcement.
- **A body-size line below the footnote separator that PARSES AS A BYLINE
  opens the next writing** (ca9 sets 'BUMATAY, Circuit Judge, dissenting:'
  between the rule and the notes). Gated on the byline grammar because ca3
  sets its footnotes at body size.
- **An unsigned writing that pronounces a disposition types as `order`**,
  never inheriting the document's `majority`.
- Unicode asterisk variants (∗ ⁎ ﹡ ＊) are footnote marks everywhere ASCII
  '*' is (ca10 stars its panel roster with U+2217).

## Pass: status honesty + the last crashes (2026-08-17)

Two crashes and a mislabelled status class were hiding the real worklist.

**Crashes (both fatal, both mine):**
- `NameError: substantive` — a word-floor guard left behind in the
  terminal-author loop when it was hoisted into the shared `_prose_anchor`.
  Every file reaching that loop died (ca8, cadc).
- `IndexError` in the writing loop — the caption run-on rebuild shrinks
  `split_stream` *after* `starts` was computed against the old list, so the
  later bounds ran off the end (ca11). `starts` is now remapped by segment
  identity, and a run that absorbs every start keeps both halves of the
  headmatter instead of dropping the moved segments.

With these two fixed the corpus has **zero extraction errors** (calctapp
alone went 33 valid/9 error → 42/0).

**`scanned` is now its own status.** 'review' has to mean *something to
fix*. Roughly 100 files carry only a source complaint — the PDF is a scan
with an OCR text layer, or has image-only pages — which no amount of better
parsing can repair. Lumping them in with real defects buried the work:
Nevada looked like the worst court in the corpus (17 valid / 33 review) and
is in fact **100% correctly handled, source-limited**. Same for nevapp,
nysupct, and virginislands. `quality.py` no longer scores a scan against a
court's grade; it flags `scanned-source` instead.

Rules added this pass (all general, all guard-pinned):
- **A page that prints a byline has started its writing**, however much
  caption spilled onto it — ca11 runs a two-page caption and then sets
  `PER CURIAM:` plus the whole opinion on page 2. The court's own signal
  outranks caption-shape evidence.
- **A bench roster closes the headmatter even with no doc-type heading
  above it** (lactapp: caption / `BEFORE: WOLFE, STROMBERG, AND BALFOUR,
  JJ.` / `WRIT DENIED.`). Allowed only where nothing else found a writing,
  so it rescues a total miss but never moves a working boundary.
- **A standalone disposition can BE the writing**, not just terminate one:
  `WRIT DENIED.` is the entire body of a supervisory writ ruling. Together
  with the roster rule this took lactapp from 11 review to 1.
- **A line of pure rail glyphs is furniture** — no alnum character, no
  content. pasuperct sets `:` down the middle of its caption and was
  failing on punctuation alone (7 review → 0).
- **A caption row is claimed whole**: where the left cell hugs the rail
  (`COMMONWEALTH OF PENNSYLVANIA :`) the band could admit the right cell
  and leave its twin unowned — captured as a party, but reported as lost.
- **A clerk's cover sheet names itself** (`OPINION COVER SHEET`) — ri sets
  one on a trailing page as a label/value metadata grid. It is apparatus:
  routed to headmatter, kept out of assembly, no longer a phantom tail.
- **A trailing notice is publisher apparatus wherever it prints.** The
  headmatter sweep never reached fla's finality notice on the last page.
  The run is exactly the trailing blocks that each carry a cue — so it
  stops at the counsel entry above it — and must clear the two-cue bar.
- **A counsel entry closes on the party it represents** (`…, for Appellant.`).
  The role must sit in the entry's closing span: matching it mid-sentence
  swept ca6's conclusion paragraph and a me footnote into the attorney list.
  The roster also ends at its last marked entry plus short continuation
  rows, rather than running to the end of the document.
- **An adverb may precede the participle** — `specially concurring`,
  `respectfully dissenting` are ordinary opinion grammar, not a court's
  local dialect. This recovered fladistctapp's missed concurrence while
  leaving the third-person announcement (`PRATT, J., specially concurs,
  with opinion.`) correctly *not* a byline.

`render` now takes multiple courts in one invocation.

## Discovered, characterized, NOT yet fixed (2026-08-17)

**1. The corpus is 238 courts, not 117.** The extra ~121 are federal
district courts and specialty tribunals (tax courts, AG opinion
collections, bankruptcy appellate panels, TTAB, military appeals). **None
of them has a CourtProfile** — they have been running on the default
grammar the whole time, and that is where essentially all remaining
`review` flags live. Every one diagnosed so far reports the same single
warning, `no opinion start found`, because the default byline grammar does
not match the court's dialect.

Proven cheap to fix — one DATA declaration each, zero engine code:

| court | before | after |
|---|---|---|
| indtc | 5 valid / 36 review | 36 / 5 |
| mdag | 9 / 33 | 40 / 2 |
| uscfc | 23 / 9 | 32 / 0 |
| vtsuperct | 21 / 19 | 33 / 7 |
| minnag | 15 / 16 | 27 / 4 |

Still unprofiled, worst first — each needs its dialect read off the page:
- `bap1` 3/29, `bap8` 3/24 — bankruptcy appellate panels
- `njtaxct` 18/24 — `:`-rail tax caption, body opens on `I. Findings of Fact`
- `ortc` 24/18 — Oregon Tax Court
- `afcca` 21/11, `uscgcoca` 22/10 — military; cover page of counsel, then
  the writing; closes `For the Court,` / clerk (NOT the author)
- `ttab` 24/8 — signs `By the Board:` under an
  `Administrative Trademark Judge` roster
- `mtd` 19/10 — all ten are scans whose OCR also defeats the body anchor

**2. `(cid:N)` font-encoding corruption — 75 files across 25 courts**
(pasuperct 21, cit 16, vawd 5, ga 4, ilsd 4, tenncrimapp 4, … including
ca7 1). These files pass the accounting check and report `valid`, so only
`quality.py` sees them — pasuperct is 42 valid / 0 review and still grades
**F (193.75)** on this alone. This is the clearest evidence that status and
quality measure different things and both are needed.

Diagnosis is complete. The font is a subset with no ToUnicode map, using
the standard Mac glyph order, so **glyph id = ascii − 29**: `(cid:3)` is a
space, `(cid:15)` a comma, and literal `2Q` is `On`. Decoding with that
offset (self-calibrating: the most frequent cid in a run IS the space, so
`off = 32 − most_common_cid`) yields real English.

**But decoding alone is not enough** — the character ORDER is also wrong:
the decode of pasuperct/brown_p._v._brown_s. p16 gives `On is threcod, we
cdonluthat  hisCot ur` where the page reads `On this record, we conclude
that this Court…`. Every letter is present and interleaved. The font
carries no metrics, so per-glyph x-positions are wrong and the draw passes
get shuffled by x-sorting. The real fix is in `pdfio`: for a font with no
usable metrics, order characters by the text-showing operator sequence
rather than by computed x. Not attempted — it is a pdfio change that would
touch every court's line assembly and needs its own guarded pass.

### Coverage oracle agrees (2026-08-17)

`coverage` (pdftotext word-set vs rendered+dropped) scored 9,293 files:
**174 below 0.95 — 98.1% of the corpus at ≥95% word coverage.**

The flagged files concentrate in exactly the same unprofiled courts named
above: bap1 23, armfor 16, bap8 16, njtaxct 13, ortc 12, ttab 8, delch 5,
mdag 5, indtc 4. Three independent measures — extraction status, the
quality grader, and the coverage oracle — now point at the same ~10 courts.
That convergence is the argument for doing the profile work as one pass:
it is the last concentrated block of missing content in the corpus.

(delch is the exception worth a separate look: it is profiled and mostly
valid, but its worst files miss `see×103`, `trial×148`, `dkt×46` — the
shape of Chancery's heavy footnote apparatus, not a byline problem.)

## Pass: where the headmatter ends (2026-08-17, user-directed del + azd)

The user pointed at `del/cannon_v._state`, `del/ferrer-vasquez_v._state`
and three `azd` orders with one complaint — "looks like you aren't starting
opinions properly". All five were the same root cause, and it is the thing
the user has said matters most: **nothing was telling the engine where the
headmatter ends.**

- del/cannon prints `ORDER` under its caption and then the whole narrative.
  That narrative stayed in headmatter (hm 14) and only the closing
  `NOW, THEREFORE, IT IS ORDERED` paragraph became the body.
- del/best and del/boulden parsed correctly **by luck**: they print a
  `Before …` roster, which was the only thing closing the headmatter.
- azd was worse — the entire page-1 body sat in headmatter and the writing
  opened mid-sentence (`judgment is void; (5) the judgment has been
  satisfied…`). 1420543 went from 18 headmatter rows to 5, and from a
  broken start to 127 blocks opening on `ORDER`.

**A DOC-TYPE HEADING CLOSES THE HEADMATTER**, exactly as a bench roster
does. Three guarded conditions, each learned from a sentinel it broke:
1. Only when the found writing did NOT open on a printed byline. A byline
   outranks a heading above it — that is the title case the title-skip
   already handles. (First attempt split ca2/ca6/pa majorities in two.)
2. Only when no caption, roster, or counsel apparatus FOLLOWS the heading.
   ca2 sets `SUMMARY ORDER` above its caption and counsel; anchoring there
   swallowed the whole headmatter and lost perez_v._porter's 11 attorneys.
   Tested by what comes after, NOT by the measured caption band — del's
   band runs past its own heading, so a band test blocks the del fix.
3. Later starts survive only if the page prints a byline there; otherwise
   they were heuristic anchors that found this same writing from its tail.
   (Inside an open order, `NOW, THEREFORE` is the conclusion, not a second
   writing — without this cannon came out as two orders.)

Also found while checking del — invisible to the status check, since all
50 files were already `valid`:
- **38 of 50 del opinions ended their body on `BY THE COURT:`**. The
  attestation that OPENS the signature block was left dangling as the
  opinion's last paragraph. It now joins the `/s/` block, like the `DATED`
  line already did.
- **Pleading-paper `/ / /` filler is furniture.** Numbered paper fills
  unused lines to keep the numbering continuous; merged into the prose it
  swallowed azd's `Accordingly,` into a blockquote, away from the
  `IT IS ORDERED` sentence it introduces. (This was the user's "missing a
  line".)

Known and NOT fixed here: azd leaves the judge's signature graphic as an
empty trailing `ImageBlock` instead of stashing it in the signature, and
calctapp's rehearing order picks up a few caption cells from its
two-column page — though it also gained the ruling text it was previously
missing, so that file is net better.

## Session 2026-08-18 (BAP finishing pass) — core fixes

All four were found from ONE user-marked nay (`bap1/banco_popular`) plus the
BAP quality flags, and all four are CORE, not court code. `guard` 197/197
after each.

- ✅ **Page-turn marker welded to the next word.** `assemble.py`'s
  cross-page paragraph merge wrote `joined + " " + _mk + b.text`, so the
  `<pagenumber/>` marker took a space on its left only: the corpus printed
  `respective plans 5of reorganization` ~62,000 times across 7,792 files,
  every court affected. v1 sets `… plans 5 of …`. The hyphen-weld branch
  still takes no spaces, which is right.
- ✅ **Footnote marks fused into headings.** `_segment_blocks` built
  `m.Heading(text=plain)` from PLAIN text while paragraphs used the markup
  rebuild, so a reference on a heading printed as a bare digit —
  `BACKGROUND2`, 403 headings across mspb/uscfc/bap9/utah/ca3/…. Headings
  now carry the same inline markup; `_mend_seams` re-forms the adjacent
  emphasis runs a column-split label row otherwise leaves doubled
  (`<strong>III. </strong> <strong>The Appeal</strong>`).
- ✅ **Vertical rules drawn as filled PATHS were invisible.** `collect_rules`
  read `page.curves` for horizontals only. bap10/james_perry draws its
  caption divider as a path, so bap10's reader found no rail and returned
  NOTHING for a cover it owns (its docstring had recorded this as a known
  loss). Criteria 4 → 7; parties, docket and counsel now read.
- ✅ **A headmatter fence read as a footnote separator.** bap10 sets its
  headmatter as a ladder of fences; the fence above the panel roster has
  note 1 two lines below it, which satisfied the late-label test, while the
  shape the document proves on twenty pages (its 144pt rule at the body
  rail) stands 95pt further down the same page. `_outranked_by_signature`
  now loses an unproven rule to a proven one lower on the page, in the
  relaxed steps (3, 3.5, 4, 6) only — step 2's size-drop evidence is
  untouched. Two `?` notes gone (roster and byline had been inside a
  "zone").
- ✅ **A carried tail may turn its own paragraph.** `_labelled_note_after_carry`
  required the whole tail to be single-spaced, so bap10/irene_moden p11 lost
  notes 28 and 29 to the body for want of 0.1pt (pitch 14.9, the note's own
  paragraph break 20.9, the flat gate `body_size × 1.6` = 20.8). The run's
  MEASURED pitch now sets the gate — but only when `prev_had_zone`, the same
  carry gate steps 8 and 9 keep. Without that gate ca5's caption fence read
  the roster, the byline and the opening paragraphs as one tail and swallowed
  six sentinels' bylines.

Harness, same session:
- ✅ **The join oracle stopped counting party names.** `[a-z]{3,}[A-Z][a-z]`
  flagged every camel-case corporate name in a citation — CitiMortgage,
  VeroBlue, TrafficSchool.com, ExecuCorp, MusclePharm, PennyMac. A hand-kept
  prefix allowlist can never track the corporate register, so CONTEXT decides
  instead: a citation signal before the name (`v.`, `In re`, `quoting`,
  `citing`, `see`) or a corporate designator after it (`, Inc`, `, LLC`,
  `Corp`, …), each allowed a name-head's distance from the capital. bap9 was
  a B on 14 such hits and is an A with 3 (all genuine brands in prose:
  CourtSolutions, PureChoice, GoFundMe, GlenFed).
  NOTE: stored `joins` counts for every court NOT re-measured since predate
  this and are inflated.

Status: bap1 and bap6 marked complete by the user. bap8/bap9/bap10 still need
guard sentinels (only bap8 has any) and criteria_manifest entries.

## Session 2026-08-19 — marks, staleness, and two live defects

**The nay list was almost entirely historical.** Of 73 nays, only TWO were
judgements of the current rendering: `nd/adams_v._state` and
`sd/advisory_opinion`. Every other file had been re-rendered since it was
marked — ca9 alone carried 45 nays whose files had all been rewritten, 35 of
them mechanically clean by the time anyone looked, which is why nothing
structural separated ca9's nays from its yays.

- ✅ **The viewer now says so.** `/api/stale` reports, per mark, whether the
  rendering has moved under it, and the file list shows a glyph: `◆ changed`
  (proven by digest), `◇ re-rendered` (rewritten, may or may not differ),
  `· unknown` (marked before the journal existed). Marks written from now on
  carry a `sha` of the rendering they judged, so staleness is a byte
  comparison rather than a timestamp guess.
- ✅ **Counsel published in lower case.** `pipeline.py` appended `lw` — the
  lowercased working copy the counsel MARKS are matched against — to
  `_counsel_texts` instead of the block's own text, so every appearance
  lifted from above the body was published lowercased: `kiara c. kraus-parr,
  grand forks, nd, for petitioner and appellant`. 22 files across nd, indtc,
  ca1, sd, tnwd. Now publishes as printed.

Still open, both from the two live nays and both core's SHARED walk (i.e.
they are what a port fixes, and both courts are unported):
- **nd**: the disposition row is pulled into `parties` — `Jarrod Jashawn
  Adams, v. State of North Dakota, AFFIRMED.` `AFFIRMED.` stands 130pt below
  the caption, past the docket and the origin.
- **A submission statement read as counsel**: `CONSIDERED ON BRIEFS FEBRUARY
  9, 2026 OPINION FILED 02/18/26` published as `attorneys`. 13 files are
  purely this (mont 7, sd 3, wisctapp 2); another 7 (ca10, ortc,
  njsuperctappdiv) are a submission LABEL followed by real counsel and are
  arguably right. A rule that refuses a counsel criterion carrying no name,
  no firm and no representation clause would fix the 13 — it touches counsel
  harvesting for every court, so it wants a guard run behind it.

## Signature-band epic, ranked PER COURT (swept 2026-08-20)

Found by generalising the user's haw finding into a class and sweeping every
rendered court, then asking the only question that matters: does the court
LOSE the data, or merely print it in the wrong place? `Document.signature` is
used by NO court in the corpus (`sig_blocks=0` everywhere), so every `/s/`
run currently lives inside `sec-opinions` as body prose.

REAL DATA LOSS — the band is the only place the names/date appear, and both
criteria fields come back empty. Fix these first:

    md         32 of 50 files   judges=None  date=None   (bar applications, attorney grievance)
    del        42 of 50 files   judges=None  date sometimes present
    me          2 of 50 files   judges=None  date=None   — and ONE of the two is a
               FALSE POSITIVE: opinion_of_the_justices_ranked-choice_voting matches on
               'SPONSORED BY: _______/s/____' inside a QUOTED legislative joint order
               (Senator RENY), not a judicial signature. Real scope for me is ONE file.

    Counting note: the first pass reported 32/16/42 as OCCURRENCE counts, which
    overstated me by 8x — one file can carry a dozen '/s/' rows. Per-FILE counts are
    the ones above, and they are what ranks the work.

COSMETIC ONLY — the band is body prose but the court already captures both
fields from its headmatter, so nothing is lost and these are low priority:

    michctapp     119 sig-runs   judges + date populated
    cadc           38 sig-runs   judges + date populated
    virginislands  26 + 18 dated judges + date populated

Under active fix on 2026-08-20: haw (183 + 38, the user's exemplar) and ri
(5, plus its 36-file OPINION COVER SHEET). Small tails not yet triaged:
tennctapp 8, wyo 7, nev 2, wash 2, bap1 1, ca11 1, ca6 1, wva 1.

Companion negative result worth keeping: the ill defect (a public-domain
citation wearing the `docket` role) was swept across all 82 readers and
occurs NOWHERE else — it was genuinely isolated, and is fixed.

## nh, from the three viewer 'nay' marks (checked 2026-08-21)

The three marks are `contoocook_valley_sch._dist._v._state`, `state_v._dunbar`
and `state_v._miller`. All three shas are STALE — the output has been
re-rendered since they were set — so each was re-checked against its PDF
rather than taken at face value.

CLEARED, nothing left to do:

    state_v._dunbar    8pp   every PDF line present bar the nine-line notice
                             (correctly dropped); headmatter routes tribunal,
                             docket, citation, caption and both dates; 20/20
                             `[¶N]` open a paragraph; the PDF has no footnotes
    state_v._miller   13pp   same, 47/47 paragraphs

STILL OPEN:

- **contoocook_valley: two separate writings buried in the lead opinion.**
  A 48-page case with three writings; we render one, so pages 29–48 are
  welded onto Bassett's lead opinion and credited to him. The court opens
  each separate writing at the HEAD of a page on the paragraph indent
  (x0 108.0 against a 72.0 rail), runs it on at the rail, and closes it on a
  full stop whose last clause names the kind:

      p29  COUNTWAY and DONOVAN, JJ., jointly concurring in Part II(B)
           but otherwise dissenting.                        (2 rows)
      p34  NADEAU, J., retired superior court chief justice, and ABRAMSON,
           J., retired superior court justice, both specially assigned
           under RSA 490:3, jointly concurring in part and dissenting in
           part.                                            (3 rows)

  `BylineGrammar(style="abbrev")` parses `BASSETT, J.` and returns None for
  both of these — plural `JJ.`, two named judges, and a kind clause that
  wraps across rows. A sweep of all 50 nh PDFs found these two page-heads
  and no others, so this is ONE fact about how this court opens a separate
  writing, and it belongs in a `writing.covers` provider in `nh.py`
  (lactapp.py and mo.py are the models) — never as a relaxation of the
  byline rule in core. Note the lead byline `BASSETT, J.` also stands at
  108.0 but does NOT open its page (p3, top 285.3, under the appearances),
  and the prose openers `[¶N]` hang at 103.6/103.7, not 108.0.

- **`criteria.parties` carries the printed pivot — 32 of nh's 50 files.**
  `nh.py:307` sets `parties` to the raw caption rows, `v.` row included, and
  `render/html.py:353` joins that list with `" v. "`:

      THE STATE OF NEW HAMPSHIRE v. v. v. JALEN MILLER
      ROBERT MORRIS & a. v. v. v. COMMISSIONER, NEW HAMPSHIRE
        DEPARTMENT OF REVENUE v. ADMINISTRATION

  The second shows the other half of it: a party name that WRAPS becomes two
  list entries and gets a pivot inserted between them. The fix is wyo's
  `_party_names` — split the caption on its printed pivot rows and join each
  run — and it must be a run-join, not a row-per-party. `case_name` is built
  by a different path and reads correctly; leave it alone.

## pacommwct, from the five viewer 'nay' marks (fixed 2026-08-21)

THE FINDING THAT COVERED FOUR OF THE FIVE: **this court files its order as a
separate paper, and gives every paper its own cover.** Swept over all 42
records — each one ENDS with a fresh page carrying the masthead, the caption
box and (on 41) the bench roster, then a centred bold order title ('O R D E R'
letter-spaced on 35, 'ORDER' solid on 7), the 'AND NOW, …' decree and the
signing judge. Four records staple further writings behind that, each on its
own cover: abdulhay p27, giant_eagle p15, js_technology p51, passhe p19 and
p24.

Before this the order was never a writing on ANY of the 42 — it fell into the
last paragraph of whatever came before it — and the repeated cover went with
it, so the caption, the docket and the whole bench roster were published a
second time inside the body of the opinion.

Fixed in `courts/pacommwct.py` (`writing.covers`):
- ✅ The cover is found by its own ink — masthead, then the box's rows (every
  one carrying a glyph in the rail's own column, which `_rail`/`_is_rail`
  already measure for page 1), then the roster. The paper begins at the first
  row that is none of those; everything above it is dropped, RECORDED as
  `kind="cover"`. Page 1 is exempt: its cover is the headmatter the reader
  above has already claimed.
- ✅ The order title is declared as a writing start. The title is
  letter-spaced, which is a fact about glyphs and not words: 'O R D E R'
  collapses to 'ORDER' once its spaces are shed.
- ✅ `_ANN_HEAD` now admits a solidus in the kind. passhe files both forms —
  'CONCURRING AND DISSENTING OPINION BY' (p24) and 'CONCURRING/DISSENTING
  OPINION' (p19) — and a kind class of letters and spaces alone matched the
  first and missed the second, so Judge Covey's writing was swallowed whole.

Two core fixes fell out of it, both scoped to `headmatter_claimed`:
- ✅ `assemble.py` — a doc-type anchor on page 1 is no longer pushed below the
  caption band when a reader has claimed that band. The two cases the push
  was written for (akd's 'ORDER OF DISMISSAL', ca9's 'MEMORANDUM*') are
  caption CELLS of a caption still standing in the stream; where a reader took
  those rows, a heading that survives inside the band's coordinates is the
  writing's own title. pacommwct measures its band down to the announcement,
  so 'MEMORANDUM OPINION BY' read as a cell and the anchor moved to page 2 —
  city_of_lancaster came back as a 3-block 'majority' plus an 82-block
  'order' opening on 'I. BACKGROUND'.
- ✅ `assemble.py` — a `writing.covers` declaration AT the first writing (not
  before it) is now honoured, and index 0 counts as the first writing when the
  headmatter is claimed. The boundary does not move; the court is naming the
  kind of the paper that already opens there. passhe's announcement is
  'OPINION1' (this court hangs a footnote mark on the paper's own name), so
  `heading_doc_type` did not recognise it, the head went unsigned, and an
  unsigned head types `order` — the lead opinion of a 31-page en banc case
  came back an order.

Result: all 42 records now read `['majority', 'order']`, except the five that
genuinely carry more — abdulhay (+concurrence), giant_eagle (+dissent),
js_technology (+dissent), passhe (majority/order/dissent/dissent), and
g._wilkins, whose order this court signs PER CURIAM.

STILL OPEN, small:
- **g._wilkins types its order `per-curiam`, not `order`.** Its cover is the
  corpus's only per curiam one, and the row under it is 'PER CURIAM' rather
  than the order title. That row names the order's author, so the paper opens
  there — but core consults a declared kind ONLY in its unsigned branch, and
  a parsed byline wins. Nothing is lost or misplaced; only the type is the
  narrower fact. Fixing it means letting a declared kind outrank a parsed
  byline's, which is a corpus-wide question about `assemble.py` and wants its
  own sweep.
- **js_technology's majority and order have an empty `author`.** The
  announcement is 'OPINION BY' / 'PRESIDENT JUDGE COHN JUBELIRER' over two
  rows and neither parses alone; the writing is typed right and placed right,
  but the name never reaches `Opinion.author`. Same family as the note in the
  `writing.covers` comment about 12 of 13 announcements not parsing.

## cadc, from the three viewer 'nay' marks (2026-08-21)

TWO OF THE THREE WERE ONE DEFECT: **the clerk's attestation was opening a
writing.** This court closes every paper the way a federal appellate clerk
does — the text, a centred `Per Curiam`, then

    Per Curiam
                                  FOR THE COURT:
                                  Clifton B. Cislak, Clerk
                                  BY: /s/  Daniel J. Reidy, Deputy Clerk

That trailing `Per Curiam` is the paper's attribution; core read it as a
byline opening a new writing, so the record grew a phantom per-curiam holding
nothing but the signature block. 7 of cadc's 100 records: in_re_donald_trump_1
('not tow opinions'), joe_neguse ('too many opinions'), alexander_kursar,
heritage_foundation, jorge_lujan, national_trust…v._nps, new_york_times.

- ✅ `assemble.py` — `_ATTEST` now admits the clerk's form. Core already had
  the concept (a byline followed by an attestation is a signature, not a
  start); its vocabulary was `WE CONCUR:` / `I DISSENT:` only. `FOR THE
  COURT:` is anchored WHOLE, exactly as the others are, because the narrow
  anchoring is what an earlier regression bought (idahoctapp/state_v._reyes).
  The row occurs in 11 courts — vt 42, cadc 37, nmcca 36, afcca 32, cafc 29,
  acca 13, ca2 8, lactapp 5, ilcd 2, washctapp 2, nj 1.
  After: trump is one `order`, neguse is `order` + `concurrence`, and both
  retain 100% of their PDF text.

STILL OPEN — **vermont_information_processing…_adopted_proposed_judgment**,
and deliberately not fixed, because every rule it wants would be built from
ONE record:

  It is an OCR SCAN (the only one in cadc) and it is not this court's paper at
  all — it is an NLRB adopted-proposed-judgment packet of four stapled papers:

      p1-2  JUDGMENT       masthead, caption, 'JUDGMENT', 'Before: Millett,
                           Walker, and Pan, Circuit Judges', the THIS CAUSE
                           recital, 'ORDERED AND ADJUDGED…', the judges'
                           hand signatures (OCR renders them as garbage —
                           `-=::1:c~:....t,•"'`), 'ENTERED:'
      p3-5  ORDER          the Board's cease-and-desist terms, 'Mandate
                           shall issue forthwith.', 'ENTERED:'
      p6-7  APPENDIX       'NOTICE TO EMPLOYEES'
      p8    CERTIFICATE OF SERVICE, over a repeat of the caption

  All eight pages come back as ONE writing typed `order`, authored **'Ruth E.
  Burdick'** — the NLRB Deputy Associate General Counsel who signed the
  certificate of service on page 8. The court's own judges never reach the
  record.

  Why nothing was built for it, measured:
  - its caption is a `)` rail, not the `_` fence the cadc reader is built on.
    `parenthetical-box` is 1 of cadc's 100 records, and it is the ONLY cadc
    record whose headmatter renders entirely unclaimed (the note's 'no
    headmatter': the rows are all there, none carries a role). Teaching cadc
    the `)` rail off one record is the mistake `[[misc-lane-2026-08-20]]`
    already names — the `)` rail is per-court, never inherited.
  - the packet shape is 1 of the whole corpus: only 10 rendered records
    anywhere carry a 'CERTIFICATE OF SERVICE' (uscfc 3, mied 3, cadc 1,
    texapp 1, nvd 1, ned 1, nev 1) and only this one is the NLRB packet.

  What IS generalizable, and wants its own pass: **a `s/ <name>` standing
  under a CERTIFICATE OF SERVICE is the filer's signature, never the
  writing's author.** Of the 10 records above, mied's 'Judith E. Levy' and
  uscfc's 'Brian H. Corcoran' are genuinely the judge and the special master,
  but cadc's 'Ruth E. Burdick', ned's 'F. Beau Howard', nvd's 'Gina G.
  Zayat', texapp's 'Kristian McCray Stewart' and nev's 'Kathryn Reynolds'
  all look like counsel or clerks credited as authors. Confirming each
  against its PDF is the work; the rule is one line in
  `conformed_signature_author` once they are confirmed.

## paed/658030 — the centred fence, and one accepted loss (2026-08-21)

`paed/gov.uscourts.paed.658030.12.0` was marked 'fix headmatter': its whole
caption sat in the opinion body and it read NO criteria at all.

THE CAUSE: `read_ecf` anchors on the masthead — a row where the court names
itself — and this paper's masthead is not text (see the accepted loss below).
With no anchor it refused, honestly, and everything fell through to the body.

What the page DOES put in its text layer is a caption fenced by three short
strokes on the page axis:

        ───────      drawn rule, x 288.0-324.0
    No. 1:26-cv-01525
        ───────      drawn rule, x 288.0-324.0
       Rothwell,
       Plaintiff,
           v.
    Anthony & Sylvan Corp.,
       Defendant.
        ───────      drawn rule, x 288.0-324.0

Swept over ALL 2,217 district records: 8 pages carry short centred strokes
and exactly 3 are this fence — paed/658030, txed/243348, txed/245820 — two
courts sharing one chambers template (the paed record is a transferred order
signed by a Texas judge). Every stroke of all three is x 288.0-324.0 on a
612pt sheet. The other 5 hits are 2.5pt marks that fail the equal-width test.

Fixed in `districts/ecf.py`:
- ✅ `_centre_fence` + `EcfPaper.centre_fence_*` — the fence is recognised
  when no masthead anchor is found. `_drawn_fence` cannot see these strokes:
  it wants a rule that STARTS at the body rail, and these start halfway
  across the sheet.
- ✅ The band is split by the MIDDLE stroke, top from bottom — docket above,
  parties below — not by a left/right gutter. This caption has no columns.
- ✅ The items are emitted in the PAGE'S OWN ORDER: three centred `Rule`s
  with the docket and the party stack between them. Published as a
  `CaptionBlock` it came out as two columns either side of a rail the page
  never draws, with the docket rendered BELOW the parties (a right column
  renders after a left one) and the three strokes appearing nowhere at all
  (the user, 2026-08-21: 'the format isnt matching the pdf'). The columns
  still do the READING; only the emission changed. `[[reproduce-dont-restructure]]`
- ✅ `_norm` now folds U+FB00-FB06. This chambers ships 'Plaintiﬀ,' as one
  ligature glyph, so the ASCII status vocabulary missed it and the party came
  back as 'Rothwell, Plaintiﬀ' with its status glued on. Only 7 district
  records contain a ligature at all; the fold changed one other
  (ncmd/103164) and improved it the same way.

All three records now read docket, caption, parties and case_name, and the
two txed ones their `ORDER` title.

### THE ACCEPTED LOSS — drawn lettering, no text

The user's call, 2026-08-21: *'ill deal with that loss'*. Recorded so it is
not rediscovered as a bug.

This paper draws its small-caps headings as VECTOR OUTLINES, not text. On
paed/658030 page 1, pdfplumber reports 212 curve objects and ZERO chars in
two bands:

    y  90-126   138 curves, 0 chars   UNITED STATES DISTRICT COURT /
                                      WESTERN DISTRICT OF TEXAS /
                                      AUSTIN DIVISION
    y 276-282    68 curves, 0 chars   MEMORANDUM OPINION AND ORDER

txed/243348 has the same disease, milder: its masthead is 114 curves in
y 90-108, while its 'OR D ER' title happens to be real letter-spaced text,
which is why that one renders.

So the masthead and the title are not dropped — they were never extracted,
by us or by pdfplumber. There is no OCR engine in this repo (only
`classify.ocr_text_layer`, which DETECTS an existing OCR layer), so
recovering them means a new dependency.

TWO LESSONS WORTH MORE THAN THE RECORD:
- **An audit built on the text layer inherits the extractor's blind spot.**
  The line-accounting audit compared `pm.lines` against the render and
  reported '10 unaccounted, all ECF stamps' — true of TEXT, and silent about
  206 curves of drawn lettering. The page IMAGE is what settled it.
  `[[oracle-blind-spots]]`
- **The ECF stamp accounting is separately broken** and is NOT this loss:
  core removes the repeated stamp on pages 2+ without a `Dropped` record,
  while the shared reader records page 1's. Measured: paed/658030 10
  unaccounted, paed/596645 23 (all 23 stamps), txed/243348 2 — against wyo,
  cadc, pacommwct and nh at 0. Still open.
