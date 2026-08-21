# Suspected stale rows in `_footnotes_truth.json`

Cases where the new system's output disagrees with the truth set and the PDF
itself sides with the new system. Each was hand-checked against the page.
These stay "misses" in the truth score until you relabel (your call — the
truth file lives in the old repo and is not touched by this repo).

## Old system missed a whole writing's notes (truth is short)

- **ca9/dickinson_v._trump** — truth has 8 labels; the PDF has 15: majority
  notes 1–7 (pp. 13–28) + dissent notes 1–8 (pp. 37–57). All verified real
  ('1 The government contends…' etc.).
- **ca9/reach_community_development_v._united_states…** — truth has 9; the
  PDF has 12: first writing's notes 1–3 (pp. 13–15, text literally answers
  "the dissent") + dissent 1–9.
- **ca9/doe_1_v._meta_platforms_inc.** — truth 10; PDF has 12 (a middle
  writing's notes 1–2 missing from truth).
- **ca9/arizona_alliance_for_retired_americans_v._kr…** — truth ends '…3, 1';
  PDF has one more writing's note 1.

## Note text absent from the PDF (truth label can't exist)

- **ca2/farrington_v._poole** and **…_cl10940800** — truth ends with '*';
  no star-note text exists anywhere in either PDF (the only stars are the
  '* * *' dinkus on p. 28).
- **scotus/barrett_v._united_states_revisions_11426** — truth is ['*', 1–11];
  the PDF has notes 1–14 and no star line. Likely labeled from a different
  edition of this "revisions" file.
- **scotus/hencely_v._fluor_corp.** — truth ['…6, *, 7, 8']; PDF's numbered
  sequence runs to 9 with no mid-sequence star. Same edition-mismatch shape.

## Attribution judgment calls (not relabels; Phase 6 splits these)

- ca9/forward_inc._v._macomber, ca3/jameson-class caption stars: real notes
  printed on caption/syllabus pages that truth attributes to headmatter
  rather than opinion footnotes. The new system will attach them to
  headmatter once the writing-split attribution lands; the labels
  themselves are correct.

## Note text not extractable (verified in the PDF 2026-08-14)

- **ca11/roger_tejon_v._zeus_networks_llc** — truth wants notes 1–6; note 5
  lives on p17, which is a FULL-PAGE SCREENSHOT IMAGE (0 text chars). The
  label exists only as pixels; no text extraction can satisfy this row.

## Real notes the old system missed entirely (verified in the PDF 2026-08-14)

- **conn/state_v._anthony_v.** (×2 incl. `_1`) — p2 prints
  '* In accordance with our policy of protecting the privacy interests of
  the victims of family violence, we decline to use the defendant's full
  name…' under a rule. Truth rows lack the '*'. Same class as newton's
  'A pseudonym.'
- **conn/state_v._lawrence_m.** — identical anonymization star note
  (sexual-abuse victim privacy). Truth lacks the '*'.
- **utah/maxfield_v._cox** — p1 prints BOTH '* Additional Petitioners: …'
  and '** The petition for extraordinary relief was referred to the full
  court… Having recused himself…'. Truth has '*' but not '**'.
- **ca3/s.a.s.b._corp_v._johnson__johnson…** — p2 prints '*The Honorable
  Anthony J. Scirica was unavailable to participate…' under a rule. Truth
  has only 1–3.
- **coloctapp/castillo_v._stem** and **coloctapp/eaves_v._cdoc** — caption
  pages print '*Sitting by assignment of the Chief Justice under provisions
  of Colo. Const….' ruleless at the page foot. Truth lacks the '*'.
- **cadc/climate_united_fund_v._citibank_n.a.** — p1 prints '* Circuit
  Judge Henderson did not participate in this matter.' Truth is [].
- **ca2/in_re_payment_card_interchange_fee…** — p1 prints '*The Clerk of
  Court is respectfully directed to amend the caption accordingly.'
  ruleless at the page foot. Truth has only 1–6.
- **utah/utah_state_legislature_v._league_of_women** — same pair, stars set
  in SymbolMT PUA (): '* Additional Respondents…', '* Additional
  attorneys…' (p2), '** The petition… Having recused themselves…'. Truth
  lacks the '**'.
