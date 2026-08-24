# Footnote zones: one subsystem, evidence-chained

Footnote-zone detection consumed ~25% of the old repo's commit history as
scattered per-court fixes rediscovering the same root causes. The variants that
must be first-class evidence steps (not court overrides):

- learned separators clustered across pages (x0 / width / y-band, document-wide);
- structural thin-rule detection clear of text bands;
- typed rules (underscore runs) — one `is_typed_rule` definition;
- body-size footnotes where only the label digit is raised;
- courts that draw **no rule at all** (pasuperct draws none; olc's is 72pt wide);
- page-ownership vs `<footnotemark>`-based attribution of notes to writings;
- PUA/Symbol-font star canonicalization.

Core-owned vetoes, applied to every candidate regardless of source:
- an underline is not a separator;
- a footnote-looking line **above** the page's own separator is quoted body
  matter (block-quoted opinions carry the quoted court's apparatus);
- the caption's closing shelf rule is not a footnote separator (the robust
  discriminator: footnote-sized text directly below the rule).

**Nothing may guess a zone without a separator.** "No zone on this page" is a
recorded decision, not a fall-through. Truth set: 2,124 hand-labeled files in
the old repo's `output/notes/_footnotes_truth.json`.
