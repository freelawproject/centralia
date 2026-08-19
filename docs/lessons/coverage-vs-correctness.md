# Coverage is not correctness

The old system reached **100.00% line coverage over 3,000,400 lines** while 225
of 238 courts still needed review. Connecticut lost 341k body words to misfiled
sections and the audit stayed clean the whole time — every line was *placed*,
just in the wrong section. 128 of 195 damaged documents had *gained* footnotes.

Gates that catch what coverage can't:
- compare **opinion counts** and **per-section normalized word mass**, not line
  placement (mass moving BETWEEN sections is the signal);
- keep **coverage and furniture as two counters** — a filter that gets too
  conservative reads 0-missing while dumping furniture into the body;
- substantive content may never be reclassified as furniture to improve a
  metric.

Prefer a guard that asks the structural question directly ("how many non-gutter
words would this cut sacrifice?") over a proxy (page modal x0) that inverts on
exactly the sparse pages that matter.
