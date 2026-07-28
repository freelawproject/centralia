"""Michigan Court of Appeals.

Intermediate appellate court. Each opinion opens with a panel roster
('Before: GADOLA, C.J., and MURRAY and M. J. KELLY, JJ.') followed by the author
byline — 'NAME, J.' / 'NAME, P.J.' / 'PER CURIAM.' — then the body. A publication
notice sits at the very top of page 1.

Two court-specific fixes over the shared appellate base:

  * A half-width rule divides the caption from the panel/opinion. It sits in the
    bottom half of the page and is left-aligned, so the default footnote-separator
    finder mistakes it for a footnote rule and drops the byline + body beneath it
    (worst on a long multi-party caption that pushes the divider low). It is
    instead found by footnote-sized text directly under the rule — a real
    footnote sits in smaller type flush below, a caption divider has body-size
    text below — so the divider no longer chops the opinion.

  * The author must be a member of the 'Before:' panel. A parenthetical citation
    to another court's opinion ('... (ALITO, J., concurring), quoting ...') can
    wrap so a byline-shaped clause starts a line; restricting authors to the
    panel (or PER CURIAM) rejects those non-panel names.
"""

from __future__ import annotations

from typing import Optional

from ._appellate import StateAppellate

# Panel-roster title abbreviations, never a surname.
_TITLE_ABBR = {"JJ", "CJ", "PJ", "J", "P"}


class MichiganCourtOfAppeals(StateAppellate):
    court_id = "michctapp"
    court_label = "Michigan Court of Appeals."
    blockquote_by_indent = True
    # The caption is a measured multi-column layout (party names at left,
    # docket/publication data at right). The shared facsimile builder uses each
    # document's extracted runs and coordinates; there are no case coordinates
    # encoded here.
    facsimile_headmatter = True

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Route the italic page-top publication advisory to Removed."""
        kept = []
        notice = []
        for seg in headmatter_segs:
            remaining = []
            for line in seg:
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number")
                    if chars
                    else line.get("page_number")
                ) or 1
                _size, font, _bold = self.line_meta(line)
                if pno == 1 and line["top"] < 100 and "Italic" in font:
                    notice.append(self.line_plain_text(line).strip())
                else:
                    remaining.append(line)
            if remaining:
                kept.append(remaining)
        result = super().extract_headmatter(kept, page1_rules)
        if notice:
            result.setdefault("dropped", []).append(" ".join(notice))
        return result

    def _deep_indent_flags(self, lines) -> list:
        """Sustained inset, excluding an ordinary first-line indent."""
        deep = self.body_baseline_x0 + self.para_indent_min
        raw = [
            line["x0"] >= deep and not self._begins_paragraph_block([line])
            for line in lines
        ]
        return [
            flag
            and (
                (
                    i > 0
                    and raw[i - 1]
                    and lines[i]["top"] - lines[i - 1]["top"]
                    <= self.gap_tight_max
                )
                or (
                    i + 1 < len(raw)
                    and raw[i + 1]
                    and lines[i + 1]["top"] - lines[i]["top"]
                    <= self.gap_tight_max
                )
            )
            for i, flag in enumerate(raw)
        ]

    def _is_indented_blockquote(self, seg) -> bool:
        if len(seg) < 2:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        left = self.body_baseline_x0 + self.para_indent_min
        right = pw - self.body_baseline_x0
        return (
            min(line["x0"] for line in seg) >= left
            and min(line["x0"] for line in seg) <= pw * 0.4
            and max(line["x1"] for line in seg) <= right - 24
        )

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        if kind == "blockquote" and not self._is_indented_blockquote(seg):
            return "body"
        return kind

    def split_body_paragraphs(self, seg) -> list:
        """Michigan prose is flush after its first line and gap-paragraphed."""
        if not seg:
            return []
        out = [[seg[0]]]
        for line in seg[1:]:
            if line["top"] - out[-1][-1]["top"] > self.gap_single_max:
                out.append([line])
            else:
                out[-1].append(line)
        return out

    def classify_paragraph(self, lines) -> str:
        if lines and all(
            self.line_alignment(line, getattr(self, "_page1_width", 612.0)) == "C"
            and line["x0"] > self.body_baseline_x0 + 72
            for line in lines
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def _begins_paragraph_block(self, lines) -> bool:
        return self.classify_paragraph(lines) == "heading" if lines else False

    def build_opinion(self, op_start, op_end, **kwargs):
        opinion = super().build_opinion(op_start, op_end, **kwargs)
        merged = []
        for block in opinion.blocks:
            if (
                merged
                and block.kind == "blockquote"
                and merged[-1].kind == "blockquote"
                and block.page != merged[-1].page
            ):
                merged[-1].text += (
                    f' <pagenumber value="{block.page}"/> ' + block.text.lstrip()
                )
            else:
                merged.append(block)
        opinion.blocks = merged
        return opinion

    def find_footnote_separator(self, page) -> Optional[float]:
        # Footnotes use a left-anchored rule about 144pt wide.  Their text can
        # be body-sized, so font-size detection alone misses them; the wider
        # caption/panel shelves (~260pt) remain excluded by this signature.
        return self.footnote_sep_fixed_left_rule(page)

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        panel = self._panel_surnames(all_segments)
        if not panel:
            return starts
        return [
            i
            for i in starts
            if self._byline_surname(self.line_plain_text(all_segments[i][1][0]))
            in (None, *panel)
        ]

    @staticmethod
    def _norm(tok: str) -> str:
        return tok.replace(".", "").replace("'", "").replace("’", "").upper()

    def _panel_surnames(self, all_segments) -> set:
        """Surnames from the 'Before: ...' panel roster (the only judges who can
        author here). Title abbreviations (C.J./JJ.) and bare initials (M. J.)
        are excluded; apostrophes/periods are normalized so 'O'BRIEN' matches."""
        for _p, seg, _k in all_segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                if not t.lower().startswith("before"):
                    continue
                rest = t.split(":", 1)[1] if ":" in t else t[len("before"):]
                names = set()
                for tok in rest.replace(",", " ").split():
                    if not tok.strip(".").isupper():
                        continue
                    n = self._norm(tok)
                    if len(n) >= 2 and n.isalpha() and n not in _TITLE_ABBR:
                        names.add(n)
                return names
        return set()

    def _byline_surname(self, text: str):
        """Normalized surname of a byline ('M. J. KELLY, J.' -> 'KELLY'), or None
        for PER CURIAM (which any panel writes)."""
        t = (text or "").strip()
        if "per curiam" in t.lower():
            return None
        toks = t.split(",")[0].split()
        return self._norm(toks[-1]) if toks else None
