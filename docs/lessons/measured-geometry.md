# Measured geometry, not constants

Every threshold is measured from the document itself (`body_x0`, `right_x1`,
`lead`, body size). Profile constants are **floors/caps only**; a measured
value may only pull *tighter*, never looser.

**No evidence → return the floor unchanged.** Never derive a fallback from the
same signal being disambiguated.

Two bugs that wrote this rule:

- `page.height * 0.5` as a footnote fence killed footnotes in 10+ courts, all
  the same way: a footnote long enough to fill a page pushes its own rule above
  mid-page (`ortc` y=85, `utah` y=99, `neb` y=175, `scotus` y=291…).
- `_inferred_space_gap`'s fallback inferred tracking from the modal inter-char
  gap on lines *without* space glyphs; on an ornamental `* * *` break it read
  word spacing as tracking, collapsed the rule to `***`, and deleted a
  majority's final "We will affirm."

A third rule ("each half is a word the document uses") measured ~50/50 on the
corpus and was **rejected, not tuned**. If a discriminator doesn't separate the
cases, it isn't one.
