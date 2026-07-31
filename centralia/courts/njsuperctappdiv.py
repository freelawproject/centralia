"""New Jersey Superior Court, Appellate Division.

The opinion is introduced by 'The opinion of the court was delivered by' and the
author follows as 'FIRKO, J.A.D.' / 'SUMNERS, JR., C.J.A.D.' — a surname (with
an optional 'JR.') and an Appellate-Division title. A 'PER CURIAM' opinion is
handled by the base.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# Longest first so 'C.J.A.D.'/'P.J.A.D.' win over the bare 'J.A.D.'.
_TITLES = (", C.J.A.D.", ", P.J.A.D.", ", J.A.D.")
# The byline is introduced by this fixed phrase on the line ABOVE the name
# ('The opinion of the court was delivered by' / 'FIRKO, J.A.D.'). It is part
# of the opinion, not the headmatter, so the two lines are joined (page_lines,
# or across a page break in extract) and the phrase is stripped before the name
# is parsed. Matched by its 'The opinion ... delivered by' shape so a dropped
# 'of' in the source ('The opinion the court was delivered by') still matches.


def _is_intro(text: str) -> bool:
    low = text.strip().lower()
    return low.startswith("the opinion") and low.endswith("delivered by")


class NewJerseySuperiorCourtAppellateDivision(StateSupreme):
    court_id = "njsuperctappdiv"
    court_label = "New Jersey Superior Court, Appellate Division."

    def page_lines(self, page):
        """Join the wrapped byline: 'The opinion of the court was delivered by'
        on one line, 'NAME, J.A.D.' on the next — so the introduction stays with
        the opinion (as its byline) instead of orphaning into the headmatter."""
        lines = super().page_lines(page)
        out, i = [], 0
        while i < len(lines):
            l = lines[i]
            if (
                i + 1 < len(lines)
                and _is_intro(self.line_plain_text(l))
                and self.parse_author_line(self.line_plain_text(lines[i + 1]).strip())
            ):
                merged = dict(l)
                merged["chars"] = (l.get("chars") or []) + (
                    lines[i + 1].get("chars") or []
                )
                merged["text"] = (
                    self.line_plain_text(l).strip()
                    + " "
                    + self.line_plain_text(lines[i + 1]).strip()
                )
                out.append(merged)
                i += 2
                continue
            out.append(l)
            i += 1
        return out

    # The court banner opens the caption proper; the publication advisory is
    # whatever sits ABOVE it.
    _BANNER = "SUPERIOR COURT OF NEW JERSEY"

    # The clerk's publication stamp: 10pt bold against the caption's 14pt, the
    # only sub-12pt text on page 1 anywhere in the corpus.
    _STAMP_MAX_SIZE = 10.5

    def extract(self, pdf_path):
        self._nj_stamp = []
        return super().extract(pdf_path)

    def correct_page_geometry(self, page) -> None:
        """Lift the clerk's publication stamp off the page before ANY line
        clustering, and record it.

        Removing it later by size does not work. The stamp's date row is
        printed between the party rows and overlaps the caption's 'v.'
        baseline, so the two merge into one line whose dominant size is the
        stamp's 10pt — routing that line to ``dropped`` took the caption's
        'v.' with it ('APPROVED FOR PUBLICATION v.July 13, 2026'). Deleting the
        stamp's own glyphs first leaves 'v.' a line of its own.

        The completeness audit reads through this same hook, so its ground
        truth and the extractor agree on what the page says."""
        super().correct_page_geometry(page)
        if getattr(self, "_nj_stamp", None) is None:
            self._nj_stamp = []
        chars = page.chars
        stamp = [
            i
            for i, c in enumerate(chars)
            if (c.get("text") or "").strip()
            and (c.get("size") or 99) <= self._STAMP_MAX_SIZE
            and "Bold" in (c.get("fontname") or "")
        ]
        if not stamp:
            return
        rows: list = []
        for i in stamp:
            c = chars[i]
            if rows and abs(c["top"] - rows[-1][0]) < 4:
                rows[-1][1].append(c)
            else:
                rows.append((c["top"], [c]))
        for _top, cs in rows:
            t = " ".join(
                self.line_plain_text({"chars": sorted(cs, key=lambda c: c["x0"])}).split()
            )
            if t:
                self._nj_stamp.append(t)
        for i in sorted(stamp, reverse=True):
            del chars[i]

    def _sweep_residual(self, doc, source_pages) -> None:
        """Surface the stamp BEFORE the completeness sweep, so it is matched
        against ``doc.dropped`` rather than reported as unplaced."""
        extra = list(dict.fromkeys(getattr(self, "_nj_stamp", None) or []))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Route both pieces of publication furniture out of the caption.

        Two stamps, neither of them case content, and neither removable the
        same way:

        * the advisory ('NOT FOR PUBLICATION WITHOUT THE / APPROVAL OF THE
          APPELLATE DIVISION') is set at the caption's own 14pt, so size cannot
          tell it apart — but it always sits ABOVE the court banner, which no
          caption content does. Position identifies it;
        * the clerk's stamp ('APPROVED FOR PUBLICATION / <date> / APPELLATE
          DIVISION') is 10pt bold, pinned right of centre and interleaved
          between the party rows. ``notice_max_size`` lifts it out by size.

        Keyed on structure, not the phrases: one file in the corpus prints
        'APPROVD FOR PUBLICATION', and a phrase test would keep that one stamp
        while dropping the other nineteen.
        """
        banner_top = None
        for seg in headmatter_segs:
            for line in seg:
                if self._BANNER in self.line_plain_text(line):
                    banner_top = line["top"]
                    break
            if banner_top is not None:
                break

        advisory: list = []
        if banner_top is not None:
            kept = []
            for seg in headmatter_segs:
                keep_seg = []
                for line in seg:
                    chars = line.get("chars") or []
                    pno = (
                        chars[0].get("page_number", 1)
                        if chars
                        else line.get("page_number", 1)
                    ) or 1
                    if pno == 1 and line["top"] < banner_top - 1:
                        t = self.line_plain_text(line).strip()
                        if t:
                            advisory.append(t)
                        continue
                    keep_seg.append(line)
                if keep_seg:
                    kept.append(keep_seg)
            headmatter_segs = kept

        d = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        if advisory:
            d["dropped"] = list(d.get("dropped") or []) + [" ".join(advisory)]
        return d

    def find_footnote_separator(self, page):
        """This court's separator is the 2-inch (144pt) rule at the left body
        margin — 108 of them across the corpus, against a scatter of other
        widths (103, 112, 118, 324, 468 ...) that are underlines and shelves.

        Keyed on that width alone. The inherited finder takes any thin rule
        >=100pt in the bottom half that is neither a caption PAIR nor an
        underline, which on page 1 matches the 216pt shelf closing the caption
        box — sweeping the argued/decided line and the panel roster beneath it
        into the footnote zone. Width is what separates the two here: the shelf
        is 216pt, the separator always 144pt. Keying on the court's own rule
        also drops the bottom-half fence, so a long footnote that pushes its
        separator high up the page is still found."""
        return self.footnote_sep_fixed_left_rule(page, width=144.0)

    def extract(self, pdf_path):
        """Bridge the page-break case the per-page join can't: the introduction
        is the last line of one page and the byline the first line of the next,
        so it lands as the final headmatter row while the byline starts the
        opinion. Move it onto the opinion's author line."""
        doc = super().extract(pdf_path)
        if not doc.opinions:
            return doc
        op = doc.opinions[0]
        if _is_intro(op.author or ""):
            return doc
        summary = doc.summary or []
        for i in range(len(summary) - 1, -1, -1):
            row = summary[i]
            txt = row.get("html", "") if isinstance(row, dict) else str(row)
            if not str(txt).strip():
                continue
            if _is_intro(txt):
                op.author = str(txt).strip() + " " + (op.author or "")
                doc.summary = summary[:i] + summary[i + 1 :]
            break
        return doc

    def parse_author_line(self, text):
        t = text.strip()
        # Peel the 'delivered by' introduction (present on the joined byline).
        if _is_intro(t):
            return None
        low = t.lower()
        if low.startswith("the opinion") and "delivered by" in low:
            t = t[low.index("delivered by") + len("delivered by"):].strip()
        for ti in _TITLES:
            idx = t.find(ti)
            if idx != -1 and idx > 0:
                name = t[:idx].strip()
                # Allow a hyphenated surname ('BISHOP-THOMPSON') and an
                # apostrophe ("O'CONNOR"); an 'SR.'/'JR.' suffix keeps a period.
                core = (
                    name.replace(",", "")
                    .replace(".", "")
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("’", "")
                    .replace("'", "")
                )
                if core and core.isalpha():
                    return name, "Judge", None
        return super().parse_author_line(text)
