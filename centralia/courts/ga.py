"""Supreme Court of Georgia."""

from __future__ import annotations

from ._statesupreme import StateSupreme


class GeorgiaSupreme(StateSupreme):
    court_id = "ga"
    court_label = "Supreme Court of Georgia."
    author_titles = ("Justice", "Chief Justice", "Presiding Justice")
    # Page numbers print as bare numbers between paragraphs — fold them into
    # page-break markers so the wrapped paragraphs rejoin.
    fold_page_numbers = True
    # Georgia's body is single-spaced (~16pt line gap) with a wide left margin
    # (baseline x0≈126, paragraphs indented to ≈162). The default thresholds
    # (tuned for double-spaced, baseline-72 courts) misread the ~16pt gap as a
    # 'notice' and split every line. Retune so the body reads as 'body' and is
    # split on the paragraph indent.
    gap_tight_max = 11
    gap_single_max = 14
    gap_double_max = 27
    body_baseline_x0 = 126.0  # base splits paragraphs at body_baseline_x0+28
    # Georgia prints a small publication advisory at the top. It is removed by
    # extract_headmatter as a contiguous NOTICE:-led block, not by font size:
    # later provenance rows ("On Appeal from", lower-court number, "Decided")
    # are also small print and must remain.
    notice_max_size = None
    # The footnote separator is a right-shifted ~324pt rule at x0≈162 (aligned
    # with the indented body column, not the page's left quarter).
    footnote_sep_x0_max = 170.0

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        ordered = sorted(
            (
                line
                for seg in headmatter_segs
                for line in seg
                if (line.get("text") or "").strip()
            ),
            key=lambda line: (
                (line.get("chars") or [{}])[0].get("page_number", 1),
                line["top"],
                line["x0"],
            ),
        )
        notice_ids = set()
        start = next(
            (
                i
                for i, line in enumerate(ordered)
                if (line.get("text") or "").strip().startswith("NOTICE:")
            ),
            None,
        )
        if start is not None:
            notice_ids.add(id(ordered[start]))
            previous = ordered[start]
            for line in ordered[start + 1 :]:
                # The advisory is one tightly-led block. A large vertical gap
                # ends it even if the next caption row happens to use small
                # type too.
                if line["top"] - previous["top"] > 22:
                    break
                notice_ids.add(id(line))
                previous = line

        notice = [
            (line.get("text") or "").strip()
            for line in ordered
            if id(line) in notice_ids
        ]
        kept = [
            [line for line in seg if id(line) not in notice_ids]
            for seg in headmatter_segs
        ]
        kept = [seg for seg in kept if seg]

        result = super().extract_headmatter(kept, page1_rules)
        if notice:
            result.setdefault("dropped", []).append(" ".join(notice))

        # Pull the retained provenance rows into the document metadata as well
        # as leaving them in the styled headmatter.
        seen_appeal_source = False
        for seg in kept:
            for line in seg:
                text = (line.get("text") or "").strip()
                if not text:
                    continue
                if text.startswith("On Appeal from "):
                    result["history"] = text
                    result["lowercourt"] = text.removeprefix("On Appeal from ")
                    seen_appeal_source = True
                elif text.startswith("Decided:"):
                    result["decisiondate"] = text.removeprefix("Decided:").strip()
                elif text.startswith("No. "):
                    number = text.removeprefix("No. ").strip()
                    if seen_appeal_source:
                        result["otherdocket"] = number
                    elif "docketnumber" not in result:
                        result["docketnumber"] = number
        return result
