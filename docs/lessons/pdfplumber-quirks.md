# pdfplumber quirks — all repaired in pdfio, nowhere else

Every repair is a named rule that fires a trace event.

- **Stamps merge onto banner baselines** ("UNITED STATES DISTRICT COURT April
  10, 2026") — split chars at x-gaps; never filter whole lines.
- **Two visual columns merge onto one line** (same top) — split at the x-gap.
- **Italic runs split onto offset baselines** — re-merge by baseline proximity.
- **Broken glyph bboxes**: the Hawaiian ʻokina draws from a substituted face
  whose bbox sits ~4.5pt above its row (laed ~22pt). Snap to the page's
  majority row constant **only when the corrected top lands on a row that
  already has text** — that landing is what proves it's a boxing error.
- **Ligatures and nbsp** break naive matching — normalize `ﬀ`→`ff`, `\xa0`→space.
- **Rules drawn in pieces**: collect thin segments small, merge by y, THEN
  size-filter — a full-width rule drawn as short strips otherwise reads as two
  halves. Pleading rails can be triple-stroke (collapse strokes ~1–2pt apart).
- **Symbol-font asterisks** arrive as Private Use codepoints (U+F000–F0FF).
