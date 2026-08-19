# Circuit-family knowledge harvested from old centralia (2026-08-14)

Mined from the old repo's ca1–ca11/cadc/cafc/scotus court files, `_circuit.py`,
and review notes. ✅ = implemented in the rewrite; ☐ = still open. File:line
references are to the OLD repo's `centralia/courts/`.

## Implemented

- ✅ Running heads by repetition + measured band (≤0.19 height, ≥40%-of-pages
  floor), recorded to Removed. Covers ca6 (two heights), ca7 (docket+folio
  form), ca11 (~102pt, name changes per writing), ca2 (learned), scotus
  (label band).
- ✅ Footnote separators: evidence chain (typed rules, curves, rail-relative,
  no height floors, label corroboration). 98.3% truth.
- ✅ White-filled invisible glyphs dropped by measured fill (ca8).
- ✅ Small caps report full size — cafc counsel no longer splits mid-word.
- ✅ Superscript marker no longer raises line top (ca3 paragraph splits).
- ✅ Per-page leading on the page's leftmost rail, largest recurring gap
  (ca9 memos 10–17 blocks/page → ~3.5; the ca2/waldman shape).
- ✅ Wrapped bylines (join 2 lines, dehyphenate), letter-spaced headings
  ('O R D E R', 'J U D G M E N T', 'MEMORANDUM*'), colon terminators,
  Jr./Sr. suffixes, titlecase Per Curiam (ca5), designated-judge mixed-case
  names (ca4 'Patricia Tolliver GILES' — via titlecase profile for ca5;
  ca4 works via caps-last-token acceptance… VERIFY).
- ✅ Roster runs (adjacent kindless bylines = panel, ca7), joinder vs
  'with whom', en banc announcement terminator rules (partially — see open).
- ✅ Terminal Per Curiam = signature (cadc judgments), heading anchors
  inside caption bands deflect below the caption.
- ✅ Caption shapes: box-glyph + ')' rails (ca6), measured whitespace gutter
  (ca7 via pdfio col-split), stacked boxes split at shelf rules (akd),
  paired L/R cells, rail glyphs excluded from cells, typed-sandwich stays
  centered (ca8), glyph-rail band from rail extent (ca6).
- ✅ Disposition row → criteria.disposition ('delivered the opinion…',
  'Opinion for the Court filed by…').
- ✅ scotus: em-dash typed rules, star-note solid form ('*JUSTICE JACKSON'),
  'with whom … joins, dissenting from…' kind clauses, underscore FRAME pair
  vs separator (partially — verify hamm_v._smith).

## Still open (ordered by value)

1. ☐ ca2 document styles (stated-term order / engraved+plain ladder /
   numbered paper): landmark readers, recital date ('two thousand
   twenty-six' spelled year), two-column counsel with voted gutter,
   consolidated docket tags (CON)/(L)/(XAP), line-number gutter mode <65,
   en banc enumeration vs byline (terminator ':' vs '.'), body openers for
   summary orders. OLD: ca2.py:264,638,1010,2120,1666.
2. ☐ scotus syllabus routing: pages whose running label is 'Syllabus' →
   doc.syllabus; later writings' cover pages dropped as notice; printed
   slip page numbers replace PDF index (restart per writing);
   'No. …. Argued …—Decided …' syllabus date line → argued date.
   OLD: scotus.py:920,938,370,325.
3. ☐ ca9 published SUMMARY → syllabus, COUNSEL → attorneys (heading
   inclusive); ca9 abbreviated bench titles ('R. Nelson, J., concurring:')
   need abbrev titles in a PROSE court (currently prose grammar only).
   OLD: ca9.py:437,278.
4. ☐ ca3 counsel ADDENDUM after the opinion (between writings) → trailer;
   ca1 clerk sign-off + cc: list → trailer. OLD: ca3.py:688, ca1.py:29.
5. ☐ ca1 bold-run byline form (byline IS the leading bold run; regular
   roster rejected); ca10 bold-caps byline; clerk attestation
   ('BY THE COURT' right of center) is a signature not byline (ca1/ca3).
   OLD: ca1.py:225, ca10.py:139, ca3.py:362.
6. ☐ Consolidated shared-tail origin (ca4/ca5/ca8: origin/dates/roster
   stated once for all cases — 15 of 16 petitions showed no origin).
   OLD: _circuit.py:2030, ca8.py:14.
7. ☐ Publication flag → criteria (PUBLISHED/UNPUBLISHED/PUBLISH stems,
   incl. sharing the banner row); ca6/ca9/cafc skip-segment notices
   ('NOT RECOMMENDED FOR PUBLICATION', 'FILE NAME:', nonprecedential NOTE
   rows → dropped). OLD: _circuit.py:861,821.
8. ☐ cadc sealed-opinion sheet → DocType.NOTICE (ends in ≥2× body-size
   banner, no author); cadc bounded caption for TITLE-CASE order-form
   parties (between 'Filed On:' row and 'BEFORE:' row); trial docket rows
   ('1:25-cv-03581-UNA') excluded from captions. OLD: cadc.py:68,322,139.
9. ☐ ca10 'Entered for the Court / <Name> / <title>' signer replaces
   PER CURIAM; running head '<docket>, <name>' before follow-on writings.
   OLD: ca10.py:183,33.
10. ☐ ca11 header-derived writing starts (byline wraps + not bold; the
    running head names the current writing and its changes mark new
    writings); folio at either header end. OLD: ca11.py:140,58,81.
11. ☐ scotus criteria: order-form docket-last ('No. 25–248. Decided …'),
    pending-buffer caption attach, consolidated inline docket tags
    ('25–406 v.'), origin openers ×12. OLD: scotus.py:136,299,308.
12. ☐ Headmatter row-grouping niceties: face-change = boundary; L↔R flip
    never joins; L→C joins; typed rule excluded from leading measurement;
    cross-page join blocked after '. : ;'. OLD: _circuit.py:405,358.
13. ☐ cadc dense-footnote table false positive (reject ≤3 rows × ≥8 cols)
    — when tables land. OLD: cadc.py:305.
14. ☐ Writing-banner rehoming (centered OPINION/DISSENT banner belongs to
    the writing it introduces; a banner with nothing after it STAYS —
    cafc's closing 'AFFIRMED'). OLD: _circuit.py:267,279-293.

## Cross-cutting invariants (from the old notes, verbatim-worthy)

1. A constant standing in for a measurement is the corpus's #1 bug class.
   "Measure BOTH populations corpus-wide and show they do not overlap
   before choosing any threshold."
2. Identified furniture must be RECORDED, never merely deleted — and
   recorded before the completeness sweep, or it reads as unplaced.
