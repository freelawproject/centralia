# v1 lessons — the old repo's per-court knowledge, audited against the new engine

Source: full read of `/Users/Palin/Code/centralia/centralia/courts/` (25 family
modules + ~235 court files, 2026-08-17) compared against
`centralia/pipeline.py`, `resolve/{headmatter,assemble,footnotes,bylines}.py`,
`courts/__init__.py`, and `notes/review-backlog.md`.

Format per entry: **lesson** | v1's approach | new-engine status
(covered / partial / missing) | the portable signal.

Statuses were judged against the code, not hope: the footnote chain (PUA
glyph folding, typed rules, learned signatures, flush-label sequence
bookkeeping, caption-shelf/box-edge/underline vetoes) and the byline grammar
(prose/abbrev/reversed, opinion-by headings, strip_by_the_court,
also_reversed, ¶-marker strip) ported far more of v1 than the per-court files
suggest. What follows is ordered worst-gap-first.

---

## Courts with a missing OPINION MODEL (worst gaps)

### mo / moctapp — Missouri (signature-at-END model)
- **Signatures CLOSE opinions; nothing opens them** | v1 inverted the
  pipeline: each centered end-signature ('Zel M. Fischer, Judge' /
  'KELLY C. BRONIEC, JUDGE', case-insensitive title match) closes a writing;
  the majority runs from the first body segment to the first signature; a
  later writing opens at its centered 'DISSENTING OPINION' /
  'CONCURRING OPINION' / 'CONCURRING IN PART AND DISSENTING IN PART OPINION'
  heading | **missing** (backlog: "mo Supreme chips 'order' + duplicated
  end-signature byline"; the end-signature model exists only for calctapp) |
  signal: centered `NAME, Judge` at end + centered `<KIND> OPINION` headings;
  a line naming TWO judges is the panel roster, never a signature.
- **Vote-line dash roles** | 'GARY W. LYNCH, Senior Judge. – OPINION AUTHOR' /
  'DON E. BURRELL, Judge – CONCURS' — strip the en/em-dash annotation, read
  the role from it | **partial** (engine's `votes` regex sees `– CONCURS`
  to prove a writing, but doesn't use `OPINION AUTHOR` to NAME the author) |
  signal: en/em dash (never plain hyphen) + `OPINION AUTHOR|CONCURS|DISSENTS`.
- **Front matter ends at the trial-judge line** | 'The Honorable Kristine
  Kerr, Judge' is the caption's last row; body starts right after | partial
  (generic prose-anchor) | signal: `the honorable … judge` row inside caption.

### cal — Supreme Court of California (running-header-driven sectioning)
- **The running header IS the opinion map** | every body page carries
  'Opinion of the Court by <author>' / 'Concurring Opinion by Justice <name>'
  / 'Dissenting Opinion by …' at ~11pt vs 13.4pt body; consecutive same-id
  pages form one opinion; page numbers restart per writing | **missing**
  (profile has a reversed grammar only; header text is dropped as furniture,
  never read) | signal: top-band sub-body-size line starting with one of four
  fixed prefixes; id CHANGE = new writing, id text = author + type.
- **Each writing opens with its own centered title block** (case name /
  S-docket / writing id at body size, top<200) | lifted as headings, not
  body prose | missing | signal: centered rows above y≈200 on a writing's
  first page.
- **Trailer: 'Addresses and telephone numbers for counsel …' /
  'Counsel who argued in Supreme Court'** | routed to ending matter |
  missing (no trailer routing at all in the new engine) | signal: those two
  literal openers.

### ca11 — Eleventh Circuit (running head as opinion map)
- **Alternating head '24-13309 Opinion of the Court 3' /
  '3 Opinion of the Court 24-13309' / '25-14065 LAGOA, J., Dissenting 1'** |
  v1 parsed the head: page number one end, docket run the other, the NAME in
  the middle says which writing owns the page; a name change = a new opinion
  (ca11 bylines are non-bold and wrap, so the head is the reliable signal) |
  **missing** (heads are dropped by position; boundaries rely on byline
  grammar alone) | signal: strict form — bare folio one end + docket token
  run (`;`-joined when consolidated) the other, flanking
  `Opinion of the Court` or `<SURNAME>, J., Concurring|Dissenting`.
- **Narrow column** | body x0≈126 (DanteMTPro 14pt), single-spaced ~19pt |
  covered (geometry is measured) | —.

### ariz / arizctapp — Arizona
- **Separate writings located by running-header transitions** | ariz's head
  switches from 'Opinion of the Court' to 'JUSTICE BOLICK, Concurring'; the
  writing starts on that page even though the in-body byline
  ('BOLICK, J., dissenting.') supplies the author | **missing** (same
  header-map gap as cal/ca11; backlog: "ariz split authorship line" open) |
  signal: top-band id starting `JUSTICE|CHIEF JUSTICE|VICE CHIEF JUSTICE`
  or `opinion of the court`.
- **Letter-spaced bylines: 'M O R S E, Judge:'** | fold runs of 3+ single
  capitals into one word before the grammar; O’ N E I L keeps its apostrophe
  token | **missing** (see the cross-court letter-spacing entry below) |
  signal: ≥3 consecutive single-letter tokens.
- **Division Two raster ¶-markers** | tiny images in the marker column beside
  each indented first line were converted to synthetic bold '¶N' text |
  missing (niche) | signal: ≤24×16pt image in the left marker slot aligned
  with an indented line.

### prsupreme / prapp — Puerto Rico (Spanish grammar)
- **Spanish bylines** | 'La Jueza Presidenta ORONOZ RODRÍGUEZ emitió una
  Opinión de conformidad', 'Voto Particular Disidente emitido por el Juez
  Asociado señor COLÓN PÉREZ', prapp's ponente line 'Cintrón Cintrón, Jueza
  Ponente'; kind from `disidente`→dissent,
  `conformidad|concurrente`→concurrence; the certification paragraph that
  ANNOUNCES writings uses the same verbs in present tense ('emite') with
  TITLE-CASE names — only an ALL-CAPS (accented) surname run is a byline |
  **missing** (profiles are style="none"; backlog: votos swallowed) |
  signal: `El Juez|La Jueza … emitió|emite … Opinión|Voto|Sentencia` +
  caps-run (Á-Ú allowed); centered `RESOLUCIÓN|SENTENCIA|OPINIÓN|PER CURIAM`
  headings open writings (letter-spaced variants included); an unauthored
  lead RESOLUCIÓN types the document ORDER.
- **Repeated caption page per writing** | after the first writing has begun,
  a later page's banner+parties+docket above a writing-start line is
  furniture (dropped, surfaced) | missing | signal: banner page mid-document
  followed by a byline/heading start.
- **Cover 'Este documento está sujeto a los cambios y correcciones…'** |
  dropped notice | missing (Spanish cue not in `_NOTICE_CUES`) | signal:
  that opener, to end of page 1.
- **PR running head 'CC-2025-0671 2'** | `LL-YYYY-N` token ± page number |
  partial | signal as stated.

### ky / kyctapp — Kentucky
- **Flush-right-status caption (nothing drawn)** | party at left margin,
  status label pinned at the RIGHT margin, docket floating on the 'V.' row —
  v1 rebuilt three-zone rows keyed to the page's own margins | **missing**
  (backlog open: "ky/kyctapp two-column caption order") | signal: a row whose
  last run ENDS at the right margin while its first starts at the left;
  render as l/c/r zones, never one string.
- **ALL-CAPS inline byline with kind: 'NICKELL, J., DISSENTING:' /
  'MCNEILL, JUDGE: This case…'** | caps surname distinguishes the byline from
  the lowercase announcement 'Nickell, J., dissents by separate opinion' |
  partial (ky profile is abbrev + opinion_by_headings; the CAPS-KIND-COLON
  form and the caps-vs-lowercase announcement rule are not explicit) |
  signal: caps surname + title + CAPS kind + colon, body inline.
- **Unsigned panel memoranda** | no byline anywhere; body opens right below
  'BEFORE: KAREM, MCNEILL, AND TAYLOR, JUDGES.' and closes 'ALL CONCUR.' |
  partial (roster-cut exists; PER CURIAM fallback below roster does not) |
  signal: roster line + no byline in document → per curiam start after roster.
- **Ending matter 'BRIEF FOR APPELLANT:' / 'BRIEFS FOR…'** | trailer split;
  singular AND plural | missing (trailer routing) | signal: those label rows.
- **Kentucky seal watermark image on every page** | drop all images (text is
  drawn over the raster; cropping re-rasterizes body text) | partial (images
  become dropped notes generally) | signal: same image object repeated every
  page under body text.

### neb / nebctapp — Nebraska Advance Sheets (narrow reporter sheet)
- **396×612 sheet with an indent LADDER** | 54 body margin / 66 ¶ first line /
  78 quote / 90 quote first line / ≥96 right-pushed disposition; centering
  measured on the sheet's own axis (exact-center ±3pt); a byline is only a
  byline at the ¶ indent (66) — the wrapped history line 'Ricky A. /
  Schreiner, Judge, on appeal thereto' opens a continuation at 54 and must
  not parse | **partial** (geometry measured, but the ladder-driven paragraph
  grouping, right-margin dispositions and byline-at-indent gate are not) |
  signal: the five measured x-rungs; disposition = right-justified line past
  the quote rung.
- **Numbered syllabus with hanging indent** | point number outdented (58.5),
  wraps at 72; group by "line left of the deepest recurring x0 opens a
  point"; bold topic heading joins its prose | **missing** (backlog:
  neb headnote parser open) | signal: hanging-number geometry.
- **Title-case 'Per Curiam.' byline** | caps-only PER CURIAM tests miss it |
  partial (assemble matches `PER CURIAM` name from parser; grammar
  case-sensitivity should be checked) | signal: `Per Curiam.` standalone at
  the ¶ indent.

### md / mdctspecapp — Maryland
- **Reporter headnote page(s) BEFORE the caption page** | everything before
  the page carrying 'IN THE SUPREME COURT / OF MARYLAND' is headnotes
  (bold topic heads 'LANDLORD-TENANT LAW – …' over summary prose, grouped by
  weight runs) → `headnotes` section | **missing** (backlog: md headnotes
  similar to kan) | signal: the banner page; all-caps banner phrase never
  appears in headnote prose.
- **Only 'Opinion by NAME, J.' is a byline** | a bare 'Fader, C.J.' coram row
  or 'Killough' signature is NOT; joinder tails tolerated ('…which Biran, J.,
  joins.'); inverted names ('Opinion by Eyler, Deborah S., J.') | partial
  (opinion_by_headings=True, but v1 deliberately DISABLED the bare abbrev
  fallback — the new abbrev grammar may still fire on coram rows) | signal:
  require the `Opinion by` prefix on this court; drop the bare-abbrev path.
- **Asterisk-rail ORDER captions + '/s/ Name' + title author; letter-spaced
  'O R D E R' heading; caption centered on a right-half axis (~x413)** |
  fold rows at the rail's measured x; axis from the caption's own underscore
  rule or agreeing midpoints | missing (md short orders open in backlog) |
  signals: '*' column; `/s/` + `Chief Justice|Justice|Senior Justice`;
  despaced `ORDER`.
- **Word's invisible ghost anchors ('650.7F8')** | strip chars with
  size ≤1.5pt from the page object cache (also sd, va, delsuperct, dcd) |
  **missing** (no mention anywhere in the new repo) | signal: sub-visible
  (<1.5–4pt) glyphs beside a real superscript; text like `.0F1` mid-word.

### coloctapp — Colorado Court of Appeals
- **Front-matter pages BEFORE the banner page** | page(s) ahead of the first
  page whose opening line is 'COLORADO COURT OF APPEALS' hold the publication
  notice (→dropped) and the official SUMMARY (announcement number '2025COA88',
  right-aligned 'SUMMARY' label + date, bold docket/case/subject head, prose)
  → `syllabus` | **partial** (new syllabus routing keys on the literal word
  SYLLABUS; Colorado says SUMMARY) | signal: caption page = first page
  opening with the court banner; everything before it is front matter.
- **Author announced, body starts at ¶ 1** | 'Opinion by JUDGE SCHUTZ' with
  'Grove and Bernard, JJ., concur' beneath; body = first '¶ 1' paragraph;
  separate writings open 'JUDGE BERGER, concurring in part and dissenting in
  part.' — comma + lowercase participle vs the roster's finite verb
  ('JUDGE GROVE and JUDGE BERNARD concur.') | partial (opinion_by_headings
  set; the ¶-anchor and participle-vs-roster discriminator are not) |
  signals: `Opinion by JUDGE X`; `¶ 1`; `TITLE NAME, <participle>` vs
  `… concur.`.
- **Caption page never has a footnote separator** | its four full-measure
  rules + body-size text mimic one; v1 returned "no zone" on that page as a
  FINAL decision | partial (caption-shelf veto exists; multi-rule caption
  pages worth checking) | signal: caption page + full-measure rules.

### va / vactapp — Virginia
- **Author announced in the caption's right column, merged into the record
  row** | 'v. Record No. 250365 JUSTICE JUNIUS P. FULTON, III' under an
  'OPINION BY' row; body opens after the centered ALL-CAPS
  'FROM THE COURT OF APPEALS OF VIRGINIA' / 'UPON AN APPEAL FROM A JUDGMENT
  RENDERED BY…' line | **partial** (opinion_by_headings + order cues landed;
  the caps FROM/UPON caption-closer as body anchor is not explicit) |
  signal: caps `FROM THE …|UPON A[N] …` row closes the caption.
- **VA order convening recital carries the date** | 'VIRGINIA: In the Supreme
  Court of Virginia held at the Supreme Court Building in the City of
  Richmond on Thursday, the 11th day of December, 2025.' | **missing** —
  new `recital_date` only fires on 'at a stated term' + spelled-out year;
  VA's year is numeric | signal: `held at … on <weekday>, the Nth day of
  <Month>, <year>` (numeric year variant of the ca2 recital).
- **vactapp short in-body byline 'Causey, J., dissenting.'** | title-case
  surname + abbrev title + participle — admitted ONLY as a separate writing
  (trial judges 'Cheryl V. Higgins, Judge' otherwise rejected) | partial
  (backlog: nmariana analog open) | signal: 3-comma shape ending on
  participle.
- **Rehearing staples: several announcements in one filing** (opinion on
  rehearing + rehearing order + withdrawn original) | each 'PUBLISHED
  OPINION BY / JUDGE NAME' announcement opens a writing | partial
  (stapled-document splitter keys on Filed+banner; VA style differs) |
  signal: repeated announcement rows.

### wash / washctapp — Washington
- **Two page-1 filing stamps sharing lines with each other and the caption** |
  split each line at wide x-gaps; everything above the banner is stamp |
  partial (stamp groups exist; the split-at-gap of MERGED stamp/caption rows
  is the open two-column epic) | signal: `IN THE SUPREME COURT`/`IN THE COURT
  OF APPEALS` banner top bounds the stamp zone.
- **Running-head kinds type dashless second bylines** | '(Madsen, J.P.T.,
  dissenting)' head names the writing whose pages these are; a bare
  'MADSEN, J.P.T.—' byline with no parenthetical takes its type from the
  head | missing (header-map gap again) | signal: parenthesized head with
  concur/dissent.
- **The em-dash is the byline clincher** | every wash writing byline ends
  '…—' with body inline; signature sign-offs are dashless title-case |
  covered (abbrev grammar + `strip_by_the_court`; washctapp's dash-required
  gate worth keeping in mind) | signal: em/en dash after the title.
- **Signature-roster rules come in PAIRS (left + right column)** | a left
  rule with a same-baseline companion in the right half is never a footnote
  separator | covered (`_shares_row` box-edge veto) | —.
- **Stapled publish-order + opinion** | mid-document banner splits; the
  phantom same-author twin merges (Oregon's 'signed twice' merge) | partial
  (`_attached_documents` + announcement dedup should catch most; verify on
  wash/washctapp corpus) | signal: interior banner page; consecutive
  same-author same-type writings are one.

---

## Cross-court structural lessons (apply to many files at once)

### Letter-spacing fold — MISSING, broad
v1 folded `O R D E R`, `B e f o r e:`, `S E N T E N C I A`,
`J U D G M E N T`, `M O R S E, Judge:`, `PER CURIAM O R D E R`,
`ATTORNEY FOR A PP E L L AN T` before every heading/byline/roster/counsel
test (md, dc, ca7, cadc, prapp, arizctapp, bap6, ind). New engine: only the
`_syl` check and heading tests use squeezed compare in places; backlog lists
ind letterspaced counsel as open. Portable signal: a run of ≥3 single-letter
tokens collapses to one word; apply at classify time, keep printed text.

### Running-head reading (not just dropping) — MISSING, broad
Repetition-learned heads (same text tops ≥2 pages: ca2, armfor, nmcca, nc,
prsupreme variant heads) plus head-as-opinion-map (cal, ca11, ariz, wash,
scotus section labels, vi 'Opinion of the Court' row). The new engine drops
by position and dedups by digitless key; it never LEARNS head text (variant
heads leak — backlog prsupreme) and never READS it. Two ports: (1) learn
top-band texts recurring on 2+ pages → furniture whatever their size;
(2) expose the head's parsed (docket, label, folio) to assembly for
boundaries/types and to criteria for the docket (a ca2 summary order's head
is its ONLY full docket statement).

### Footnote reattribution by mark — MISSING (acknowledged in assemble.py)
v1's `_footnoteattr` ran corpus-wide: a writing holding a note it never
calls, when exactly ONE other writing calls that label and doesn't hold it,
hands it over; unlabelled leading tails travel with it and splice onto the
recipient's last note. Root cause: page-ownership splits (pacommwct's order
opens on the majority's last page and steals its final note; ark's dissent
starts mid-page and steals the concurrence's notes 1–2). Signal: the
`<footnotemark>` labels already in block text vs `Footnote.label` — no
geometry needed.

### Footnote continuation across pages — PARTIAL (open epic)
v1 lessons the epic needs: sd's carried-over zone opens with a typed
underscore row + '(. . . continued)'; pacommwct prints '(Footnote continued
on next page…)'; district carry matched the PRIOR page's trailing inset +
leading geometry (`_remember_footnote_carry`), incl. the one-line-zone case
(remember x0 alone); a labelless zone that runs to the page foot is a carry.
Signals: `(continued` markers; geometry carry (x0 + lead) from a zone whose
last line reached the page bottom.

### Headmatter caption footnotes — MISSING refinement
A superscript on a caption row ('TASHA MILLMAN,¹', tenn 'AT JACKSON¹', ca2's
'* amend the caption' note, calag's acting-title note) sends that LABEL's
note to `headmatter_footnotes` even though the opinion owns the page.
Signal: sub-0.8×-dominant-size digit runs inside pre-opinion lines = the
set of hm labels.

### Trailer / ending-matter routing — MISSING category
v1 routed: illappct's drawn case-information table (label column | content,
detected by rules sharing one seam-x), kyctapp 'BRIEF(S) FOR …', fla
'A TRUE COPY' certification + panel-participation rows, flnd/ncwd magistrate
'NOTICE TO THE PARTIES'/'Time for Objections' advisories, ca1 clerk 'By the
Court: / …, Clerk / cc: <list>', cal counsel addresses, calctapp
'Trial Court:' block, texbizct's appended e-filing certificate-of-service
sheet, hid end-caption footer. New engine: `doc.trailer` exists but nothing
routes to it (ca1 clerk fusions and cc-guard exist as small fixes). Signals
as quoted — all fixed openers or drawn structure.

### Ink color + font-family furniture — MISSING
waed: clerk stamp pure red (1,0,0), CM/ECF band pure blue (0,0,1) — colour is
the only separator when stamp glyphs share baselines with form text.
delaware/haw: red e-file stamps. ca8: WHITE-filled letters used as spacing
(`non_stroking_color == (1,1,1)`) arrive mid-caption. Font-family stamps:
ca5 (Arial stamp vs OldEnglish banner, stamp runs DEEPER than the banner),
txsd (unsubsetted base-14 Helvetica vs subsetted serif body), bap9/bap10
(Arial in a Palatino doc; strip at CHAR level because rows share baselines),
alnd/ilcd/tenn (stamp = only sans on the sheet), wva (Arial rows interleaved
INTO caption rows — flush-right + foreign family). Signals: non-grayscale
ink; a glyph family the document uses nowhere else, top corner, flush right.

### Sub-visible ghost glyphs — MISSING
Word writes 1pt '0F'/'12F' anchor pairs next to real footnote marks (sd, va,
md, dcd, delsuperct); they weld into body rows ('Act.0F1'). Signal: drop
chars with size < ~1.5pt (nothing readable is set below 4pt) at the geometry
hook so extractor and coverage agree.

### Per-page / per-template leading — PARTIAL
En banc staples set writings at DIFFERENT leadings (ca2 order single vs
writings double; ca3 majority 15pt vs dissent 13pt — whole writings became
blockquotes); ga has 16pt and 36pt templates; nm has Times-32pt and
Arial-13.8pt layouts. v1 measured leading per page (rail-returning lines,
largest recurring gap) and judged 'tighter than body' against the PAGE.
New engine measures one document geometry. Signal: page-local lead from
lines sharing the leftmost recurring rail.

### Two-column BODY reflow — MISSING
ncmd magistrate R&Rs set the RULING itself in two columns; v1 found the
gutter as a per-x coverage valley (full-width banner rows tolerated), read
left column then right, re-based paragraph indents per column. Signal:
central x-band crossed by ≤2 rows.

### Tables — MISSING (known)
Guards that matter even without a table model: a JUSTIFIED block quote reads
as a 34–47-column pseudo-table (nd, vtsuperct word-background boxes tiling
every word) — cap plausible column counts / drop one-line-tall abutting cell
rects; nd's header band (two long rules with sub-body text between, grid on
the next page); ncctapp continuation pages proved by rails + adjacency.

### Neutral citation as criteria — MISSING field
nd '2026 ND 70', ohio 'SLIP OPINION NO. 2026-OHIO-…', vi 'Cite as: 2026 VI
3', wis '2026 WI App 23', guam 'Cite as: 2025 Guam 14', texbizct '2026 Tex.
Bus. 23', ncbizct 'Brock v. Kyryk, 2026 NCBC 62.' — `_is_citation_row`
already recognizes the shape but only to EXCLUDE it from parties. Signal:
capture it into a `criteria.citation` field.

---

## Remaining per-court lessons (condensed)

### ca2 — Second Circuit (beyond the ported recital)
- **PRESENT: roster (letter-spaced 'B e f o r e:' too), closing on the
  ITALIC bench-title row without a trailing comma** ('Chief Judge,' mid-list
  keeps it open) | style-specific state walk | partial (engine roster prose
  covers 'Before'; 'PRESENT:' listed in old panel_openers only) | signal:
  `PRESENT:` opener; italic `… Judges.` closes.
- **Caption between typed underscore rules; parties on the caption's own
  rail, statuses INDENTED + ITALIC, versus row centered carrying the docket
  ('v. 25-1830-cv'); consolidated dockets flush-right tagged
  '(L)/(CON)/(XAP)'** | column reading by rail/italic/center | partial
  (caption blocks exist; italic-status vs caps-name and (L)/(CON) tag capture
  are not) | signals as stated; `- against -` and '— v. —' are hinges.
- **En banc signer bylines: caps names + PLURAL title + colon** ('JOSÉ A.
  CABRANES AND GUIDO CALABRESI, Circuit Judges:'), wrapped up to 3 lines;
  enumeration sentences end in a PERIOD and are not starts | colon-terminal
  discriminator | partial (`_joined_byline` handles wraps; plural-title
  signer form is outside the prose grammar) | signal: caps head + bench title
  + terminating colon; kind 'statement' when no concur/dissent word.
- **Two-column counsel gutter** ('For Debtor-Appellant Julia F. | Jeffrey L.
  Herzberg,…' label column beside attorney column) | measured gutter (leaps +
  rows that BEGIN at the far side; ≥¼ rows agree), cut every row, read each
  column down | missing (guam column fix is address-roster-shaped, not
  label|attorney) | signal: recurring mid-block x where rows jump or start.
- **BIA origin stack above the banner** ('BIA' / 'Straus, IJ' /
  'A209 866 562/563') | the only origin statement on those orders | missing |
  signal: those three short-row shapes above the banner.

### scotus
- Centered outline labels 'I' / 'A' / '1' stacked on consecutive rows must
  each stay a row (backlog: centered headings epic) | partial | signal:
  ≤2-char centered token, width ≤40pt.
- Hanging bullets (SymbolMT ) at the hanging indent — take the line's x0
  from its TEXT, mark the bullet as an item opener | missing | signal:
  non-alnum first glyph a full space left of the text column.
- Orders bylines: 'Statement of JUSTICE SOTOMAYOR respecting the denial of
  certiorari.' and kind clauses that close the sentence ('…dissenting from
  the denial of motion for leave to file complaint.') | partial (reversed
  grammar; 'Statement of' prefix and open-ended kind vocab uncertain) |
  signal: `Statement of` prefix; kind clause must CLOSE the sentence.
- Printed slip page numbers restart per writing; blocks should carry the
  printed folio | missing (cosmetic/provenance).

### ca1
- **Byline = the leading BOLD run** ('**BARRON, Chief Judge.** This appeal…';
  regular-weight comma inside it) — rejects the regular-weight roster row
  and accepts kind suffixes | partial (`require_bold` exists on the grammar;
  the run-boundary use of bold is not) | signal: bold run with byline form.
- Clerk sign-off 'By the Court: / <name>, Clerk / cc:' is indented into the
  signature column (x0 > rail+72) — never a byline | covered-ish (recent
  ca1 clerk fusion fixes) | signal: x-position of `By the Court`.

### ca4 / ca6 / cadc / ca7 / ca10 / cafc / ca5 / ca8 (criteria/pattern notes)
- ca4: band-per-section headmatter; ONE origin/dates/roster for all
  consolidated cases (shared tail); 'ARGUED:'/'ON BRIEF:' fences counsel to
  the next rule; designated-judge bylines print the name in full with only
  the surname capitalized ('Patricia Tolliver GILES, … sitting by
  designation:') | mostly covered (dispositions, rosters, notices); shared
  consolidated tail missing | signal: origin stated once below the LAST
  caption governs every case.
- ca6: '>' box-rail caption (docket loss is an open backlog item); 'Case No.'
  docket opener; disposition row 'CLAY, J., delivered…' covered | partial |
  signal: box-drawing glyphs ┐│┘ and the escaped `&gt;` rail.
- cadc: order form parties in TITLE CASE — caption is BOUNDED (between
  'Filed On:' row and 'BEFORE:'), never recognized; 'DOD-03/03/2026 Order' =
  order under review; trial docket '1:25-cv-03581-UNA' under the appeal
  docket opens NO new case; sealed-opinion placeholder (28pt 'OPINION UNDER
  SEAL' banner ends the doc) is a NOTICE with zero opinions | missing
  (bounded-caption + sealed placeholder) | signals as quoted.
- ca7: order-form roster one judge PER ROW (rows unterminated; a terminated
  row is a byline) — ported as the kindless-roster rule; measured whitespace
  gutter caption (parties | origin) | covered / partial | signal: gutter =
  empty column intersected across rows, wider than any caption indent.
- ca10: 'Entered for the Court / <name> / Circuit Judge' names the author of
  an unsigned order-and-judgment | missing | signal: that literal opener at
  the end.
- cafc: small-caps counsel rows report the size of their FULL-SIZE glyphs
  (small caps ≠ size change) | partial (cadc snap handles collisions; size
  reporting rule is separate) | signal: smaller glyphs all-uppercase on a row
  that also has the larger size.
- ca5: stamp font vs banner font (see font-family entry); typed footnote
  rule; titlecase bylines (profile covered).
- ca8: white-ink filler letters (see ink entry); filled-path (curves)
  separator population 143.9–144.0 exactly.

### Families already largely ported (verify, don't re-port)
- **conn/connappct**: reporter labels 'Syllabus'/'Procedural History'/
  'Opinion'; ligature-overprinted space (backlog open, cosmetic); head band =
  everything above y≈185 on Reports pages; leading-based paragraphing
  (12.3 vs 18pt); law-journal vs bound-reports style detection ('Page N
  CONNECTICUT LAW JOURNAL' head). Engine covers most; the LEADING-based
  paragraph split and the two-printing style label are not.
- **tenn family**: delivered bylines, OPINION banner anchor, byline row-walk
  by fills-measure, positional criteria (SECOND 'No.' row is the caption
  floor; centered run below = disposition; 'February 12, 2025 Session' =
  argued vs 'Assigned on Briefs' = submitted), missing-space byline repair
  ('KYLE A.HIXSON, J.' → insert spaces after ./, before letters). Mostly
  covered (accept_delivered, banner heading, tenn syllabus); session-date
  forms and the space-repair are cheap misses.
- **mass/massappct**: rescripts ('So ordered.') ported; advisory opinions
  ('To the Honorable…' → 'BY THE JUSTICES') missing; Rule 23.0 summary
  decisions: the underlined centered 'MEMORANDUM AND ORDER PURSUANT TO RULE
  23.0' title is the caption/body boundary and the writing's heading —
  missing | signal: centered + ruled across its own measure + that stem.
- **haw/hawapp**: OPINION-BY headings, e-file stamps, publication banner all
  ported. Underlined ALL-CAPS order titles as writing anchors when the title
  is qualified ('AMENDED¹ ORDER…') — missing | signal: drawn rule inside the
  row's own band + caps row + '(By: …)' roster below.
- **kan**: SYLLABUS BY THE COURT block (centered title after the italic
  caption-status row; body-size until the type drops) — backlog open |
  signal: centered all-caps title following the last ITALIC centered caption
  line; syllabus ends at the size drop.
- **nm**: brace pinpoints, flush glued labels admitted by sequence — ported
  (admit_flush_labels is v1's count lesson); WE CONCUR signature pages open
  in backlog.
- **sd**: '[¶N.]' markers ported; '#30782-aff in pt & rev in pt-JMK' cover
  header carries the AUTHOR'S INITIALS (trailing token) — unused, niche;
  typed continuation separator (see continuation epic).
- **ohio/ohioctapp**: flush 'N.' labels at the rail (no hanging indent) —
  check `flush_label_shape` handles the dot form; italic-only catchline →
  headnotes (missing); clerk orders start at '{¶ 1}' with no byline (missing;
  general marker-anchored order start); small-caps rows should report MAX
  glyph size (partial).
- **alaska**: right-column caption fields ('Supreme Court No.' / 'O P I N I
  O N' / 'No. 7802 – Feb 20, 2026' carries the decision date) — date capture
  from the right column is worth checking; adjacent announcement rows
  (backlog open: majority under dissent chip); caption divider must DIVIDE
  (text on both sides) — ported ideas in captions.py presumably.
- **mich**: masthead right column (x>300, top<210) + rotated margin tabs;
  roster loss open in backlog | signal: x/y band + rotated text (rotated_text
  already dropped).
- **nd**: rehoming ported; bold name-first byline vs non-bold announcement |
  signal: bold as the tell (require_bold available, unset in profile).
- **la**: page-1 clerk NEWS RELEASE cover ('FOR IMMEDIATE NEWS RELEASE',
  'BY McCallum, J.:' announcement, separate-writing list) — cover is
  headmatter, real byline on p2 is caps; title-case cover byline must only
  admit the exact announced surname | missing | signal: that cover opener.
- **nev/nevapp**: 'By the Court,' tag ported; missing-comma byline
  ('PICKERING J.:') tolerated; sub-9pt left-margin seal/speckle band; 'Judge'
  is TRIAL-court-only in nevapp (a 'Bill / Henderson, Judge.' wrap opened a
  phantom) — profile uses abbrev so mostly safe | signals: seal band
  geometry; drop 'Judge' from nevapp titles.
- **wva/wvactapp**: profile covers both byline forms; FILED stamp interleaved
  into caption rows needs the font-family removal (see above); short-rule-
  on-rail separator censuses ported in spirit (learned signatures).
- **idaho/illinois/mississippi/kansas/iowa/nh/ri/sc/mont/wyo/minn/nc/guam/
  nmariana/vt/wis**: byline grammars all in profiles; residual items are in
  the backlog (ri reversed titlecase ported; sc roster-window kinds partial;
  nmariana 'MANGLOÑA, J., concurring:' accent + title-first 'C.J. CASTRO:'
  form — title-FIRST abbrev is missing from the abbrev grammar).

### Federal specialty courts — NO PROFILES YET (data-only adds)
armfor (title-first 'Chief Judge OHLSON delivered…', 2–3-line wrapped
bylines healing mid-word 'con-/curring', cover announcement roster, 2–3-line
running head at sub-body size), BAPs (bap1/6/8/9/10: 'U.S. Bankruptcy
Appellate Panel Judge' — the longest title in the corpus; 'Bankruptcy Judge';
unsigned NOT-FOR-PUBLICATION memoranda opening at 'INTRODUCTION'; body-size
footnotes under exact 144pt rules; two-axis centered cover, bap8), military
CCAs (spelled title + colon; ')'-rail orders; acca is OCR with label-at-rail
footnotes), tax ('KERRIGAN, Judge:' colon form; '[*14]' star pages), cit
('Barnett, Chief Judge:'), bia ('HUNSUCKER, Appellate Immigration Judge:' —
colon form; BEFORE-roster ends in period), ttab ('Opinion by Cohen,
Administrative Trademark Judge:'; interlocutory-attorney signers), olc
(423pt sheet: SHEET-RELATIVE separator width floor — flat 100pt floors lose
everything; signature '… Assistant Attorney General' author), mspb
('FOR THE BOARD:' + Clerk = signature, author THE BOARD), cavc (footnote
labels at the rail are NOT a pleading gutter; 'JAQUITH, Judge, concurring:'
appended writings), uscfc ('Chief Special Master Corcoran' in the caption's
right column; stapled proffers restart footnote labels — repeated labels are
real), nyslipop courts (cover-sheet 'Judge:' line = author; body starts
page 2; NYSCEF edge stamps split at x-runs; 'Cases posted with a "30000"
identifier…' notice; nycivct 7pt checkbox disposition form).

### District family — future scope, but the lessons are systemic
- **Pleading gutter vs footnote-label column**: a real 1–28 rail is DENSE
  (≥14 numbers), SPANS most of the sheet, STARTS at 1; footnote labels sit in
  the bottom fifth (lamd/lawd/gand/nhd/sdd/utd/txwd/laed/cavc/texbizct all
  re-learned this one lesson) | signal: extent + density + start value.
- **CM/ECF band harvest**: the header strip is the one place EVERY filing
  prints its docket ('3:25-cv-00691-wmc' self-identifying cv/cr token) and
  'Filed mm/dd/yy' — read before dropping | signal: digit-cv/cr-digit token.
- **Signature block anatomy**: title-line anchor ('UNITED STATES DISTRICT
  JUDGE' family), image signatures with 'Signed:/ENTER:' date stamps (stamp
  placed ABOVE the decretal line by absolute positioning — lift by FONT),
  AcroForm widget signatures (kywd), 'Present: The Honorable NAME' minute
  orders, NY-district bylines ('ERIC KOMITEE, United States District
  Judge:'), letters ('The Honorable' + 'Dear Judge X:' = FILING not ruling),
  cacd ruling-vs-attorney-filing (minute header or judge signature required).
- **Caption facsimiles**: ')'/']'/'}'/'§'/':' rails, Old Faithful/Double Box
  drawn shapes, flush-right status; the new caption fingerprints cover state
  variants — district shapes will map onto the same machinery.

---

## TOP 15 PORTS by expected impact

1. **Running-head learning + reading** (repetition-learned top-band text →
   furniture; parsed head → writing boundaries/types + docket). Unlocks: cal,
   ca11, ariz/arizctapp, wash/washctapp kinds, prsupreme variant heads, nc,
   nmcca, armfor, vi, ohio terms, ca2 head-docket. Signal: same squeezed text
   atop ≥2 pages; `<docket run> <label> <folio>` triples; label vocabulary
   `Opinion of the Court|<NAME, J., Concurring/Dissenting>`.
2. **Missouri signature-at-end model** (generalize calctapp's end-signature:
   signatures close writings; centered `<KIND> OPINION` headings open later
   ones; dash-role votes name authors). Unlocks mo, moctapp; hardens
   pacommwct/or 'signed twice' handling. Signal: end signature + kind-OPINION
   headings.
3. **Letter-spacing fold before all classification** (headings, bylines,
   rosters, counsel labels). Unlocks md/dc orders, ca7/cadc order titles,
   prapp dispositions, arizctapp bylines, ind counsel, bap6 'O R D E R'.
   Signal: ≥3 single-letter tokens.
4. **Footnote reattribution by mark** (+ hm-superscript caption footnotes).
   Fixes silent wrong-writing notes corpus-wide (pacommwct, ark, tenn caption
   notes, calag, delaware caption footnotes). Signal: label called in exactly
   one other writing and unheld there.
5. **Spanish grammar for PR** (emitió/emite + caps-run; ponente; RESOLUCIÓN/
   SENTENCIA headings; Spanish cover notice cue; repeated per-writing caption
   pages). Unlocks prsupreme + prapp entirely (currently among the worst
   outputs).
6. **Trailer/ending-matter routing** (fixed openers: BRIEF(S) FOR, A TRUE
   COPY, NOTICE TO THE PARTIES / Time for Objections, cc: lists, Trial
   Court:, counsel-address blocks; illappct's seam-ruled case-info table).
   Unlocks fla, kyctapp, illappct, cal, ncwd, flnd, hid, ca1, texbizct.
7. **Ink-color + font-family furniture identification** (non-grayscale
   glyphs; a family the document never uses elsewhere, char-level removal on
   shared baselines; white-ink filler dropped). Unlocks waed, wva/wvactapp,
   ca5, txsd, bap9/bap10, alnd, ilcd, delaware, haw red stamps, ca8.
8. **Ky flush-right-status caption + the caps-kind-colon byline family**
   (three-zone rows; `NAME, J., DISSENTING:`). Unlocks ky, kyctapp (backlog
   open) and the same 3-zone renderer helps mspb/nev open-range captions.
9. **Sub-visible ghost glyph strip** (size <1.5pt at the geometry hook).
   Unlocks sd, va, md, dcd, delsuperct — removes a text-corruption class that
   defeats coverage matching ('Act.0F1').
10. **Per-page leading for stapled/multi-template docs** (page-local lead
    from rail-returning lines; blockquote judged per page). Unlocks ca2/ca3
    en banc staples, ga disciplinary template, nm Arial/Times duality —
    prevents whole-writing-as-blockquote failures.
11. **Announced-author + marker-anchored body start** (coloctapp 'Opinion by
    JUDGE X' → body at ¶1; ohio clerk orders at '{¶ 1}'; illappct/ill at ¶1
    after OPINION divider; va after the caps FROM/UPON row). One mechanism:
    when the byline is an announcement, anchor the body at the court's own
    printed marker/banner, not at the announcement. Unlocks coloctapp, ohio
    orders, illappct, va, vactapp.
12. **Md/coloctapp front-matter page split by banner page** (headnote/summary
    pages before the first page opening with the court banner → headnotes/
    syllabus; extend the SYLLABUS trigger to SUMMARY and to md's topic-head
    form). Unlocks md, mdctspecapp, coloctapp, and neb's headnote parser
    shares the hanging-number grouping.
13. **VA-style numeric-year convening recital** (extend `recital_date` to
    'held at … on <weekday>, the Nth day of <Month>, <YYYY>'). Unlocks va
    order dates; same pattern covers other 'held at' recitals.
14. **Neutral-citation criteria field** (capture what `_is_citation_row`
    already matches, plus 'Cite as: …' and 'SLIP OPINION NO.' forms).
    Unlocks nd, ohio, wis/wisctapp, guam, vi, texbizct, ncbizct metadata.
15. **Specialty-court profiles (data-only)**: BAP long titles, military
    spelled-title-colon, tax/cit/bia/ttab colon forms, armfor title-first +
    rev_titles, olc/mspb/cavc/uscfc author rules, nyslipop cover model.
    Cheap (BylineGrammar facts) and unlocks ~15 courts at once.

---

## 12-line summary of the biggest missing lessons

1. Running heads are read in v1, not just dropped: they are the opinion map
   (cal, ca11, ariz, wash) and sometimes the only docket (ca2). Engine only drops.
2. Missouri's whole model is inverted (signatures close writings) — unported.
3. Letter-spaced text ('O R D E R', 'M O R S E, Judge:') defeats every
   heading/byline test; v1 folded it everywhere, engine doesn't.
4. Footnote mark-based reattribution between writings is acknowledged in
   assemble.py but unbuilt; page ownership still mis-homes notes.
5. Puerto Rico's Spanish byline/heading grammar is entirely missing.
6. Trailer/ending-matter routing (certifications, brief-for blocks, cc:
   lists, case-info tables) has a field but no logic.
7. Ink-color and font-family stamp identification (red/blue/white ink,
   foreign-family Arial stamps interleaved into captions) is missing.
8. Word's invisible 1pt '0F' anchor ghosts corrupt body text in 5+ courts.
9. Per-page leading for en banc staples (ca2/ca3) and dual-template courts
   (ga, nm) — one document-wide lead turns whole writings into blockquotes.
10. Announced-author courts need body anchored at the court's own marker
    (¶1 / {¶1} / caps FROM-row), not at the announcement (coloctapp, ohio, va).
11. md/coloctapp front-matter pages before the banner page (headnotes,
    official summaries) and kan/neb syllabus parsing are still unrouted.
12. ~15 specialty federal courts (BAPs, military, tax, cit, ttab, olc, mspb,
    cavc, armfor, NY slip-op) need only data profiles + 3 small grammar forms.
