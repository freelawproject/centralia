---
name: legal-pdf-fidelity-auditor
description: Find, diagnose, repair, regenerate, and validate legal court-PDF extraction failures in Centralia. Use when auditing or fixing unplaced content, missing opinions, malformed headmatter, notices, footnotes, blockquotes, tables, signatures, multi-opinion boundaries, end matter, font artifacts, or court-specific parsing regressions.
---

# Legal PDF Fidelity Auditor

Use this skill to move through Centralia’s audit queue as an evidence-backed repair loop. Preserve authored content and legal structure while routing removable court furniture to the Removed area.

## Workflow

1. Establish scope. Inspect the worktree, identify the court and document, and preserve unrelated user changes.
2. Reproduce the failure. Run the court extractor directly and inspect `Opinion`, `Footnote`, `Block`, `trailer`, `signature`, `dropped`, and `residual`. Compare the source PDF with rendered HTML.
3. Classify the failure:
   - authored text with no home: parser or segmentation issue;
   - court furniture: notice, filing stamp, page furniture, publication boilerplate, signature, or counsel tail;
   - structural loss: paragraph, blockquote, statute subdivision, transcript turn, table, footnote, or multi-opinion boundary;
   - text-layer corruption: duplicated glyphs, `(cid:N)` placeholders, or missing mappings.
4. Choose the narrowest durable fix. Prefer shared geometry/model/rendering logic for general patterns. Add court-specific logic only for genuinely distinctive PDF conventions. Prefer geometry, font runs, indentation, and boundaries over raw text-pattern matching.
5. Preserve structure. Keep ordinary wrapped prose grouped; split transcripts at speaker or timestamp turns; preserve statute/rule subdivisions and nested indentation; keep each opinion’s caption, body, footnotes, and signatures together; route notices and end matter to their proper sections.
6. Validate before broad regeneration. Run compilation, `git diff --check`, direct extraction, and the relevant coverage audit. Confirm substantive residuals are gone and legitimate text was not moved to Removed.
7. Regenerate affected HTML/XML/JSON only after the extractor is correct. Re-run representative court regressions and report remaining issues honestly.

## Centralia Guidance

- Use `rg` for source and output searches.
- Use `centralia.registry.get_extractor(court_id).extract(pdf_path)` for focused diagnostics.
- Use `centralia.audit.audit_coverage(doc, pdf_path, extractor)` to verify source coverage.
- Run `.venv/bin/python -m compileall -q centralia` and `git diff --check` after edits.
- Regenerate with `PYTHONPATH=. .venv/bin/python -m centralia.cli <court> assets/<court> --html --output output` when a court-wide refresh is warranted.
- Distinguish furniture residuals from substantive content. Do not leave substantive content unplaced or hide it merely to improve audit counts.
- Check both the structured model and HTML. A technically covered line can still be visually or semantically misplaced.

## Common Repair Patterns

- Blockquotes: preserve internal paragraph, transcript, subdivision, and horizontal-indent structure without splitting every physical wrapped line.
- Footnotes: apply the same structural logic to quoted statutes and rules inside notes.
- Notices: remove only a recognizable contiguous boilerplate unit; preserve nearby provenance, docket, and authored text.
- End matter: detect counsel/signature rosters by structural headings and move the complete tail to `doc.trailer` or `doc.signature`.
- Multi-opinion PDFs: recognize repeated captions and separate writings; never merge opinions merely because author and type match.
- Font artifacts: de-duplicate overlapping glyphs for coverage; remove standalone CID-only furniture; preserve real text containing suspicious tokens for review.
