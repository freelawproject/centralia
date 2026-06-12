"""United States District Court, Western District of North Carolina.

ncwd's segmentation lives here (not in the shared district base) — tuning
another district can't regress it. Two house styles, both identified by the
page-1 caption fingerprint:

  * 9/10: a Parenthetical Box / Banded Bracket — a stacked ')' rail down the
    middle of the caption (sometimes inside a drawn Word-table box), with the
    document title set INSIDE the caption's right column ('  )  MEMORANDUM /
    OF DECISION AND ORDER'). There is no heading line at all; the opinion
    opens directly below the rail with a bold-lead 'THIS MATTER is before
    the Court…' paragraph. The rail's y-extent (``rail_band`` from the
    fingerprint) marks where the caption — and the headmatter — ends.
  * 1/10: a bare whitespace two-column caption (parties left, docket right,
    nothing drawn), followed by a centered bold ALL-CAPS heading
    ('MEMORANDUM OPINION AND ORDER') — the generic heading scan handles it.

Rulings end 'Signed:' / 'ENTER:' + date and a signature IMAGE (the judge's
name and title are pixels inside the graphic, so there is no text to anchor
on) — the shared base harvests that pattern into the Signature section.

Section heads in the body ('I. BACKGROUND', 'C. Deliberate Indifference…')
are fully-bold standalone lines — flipped to heading blocks for rendering.
"""

from __future__ import annotations

from ._district import DistrictBase


def _is_section_heading(text: str) -> bool:
    """A short fully-bold standalone section head: ALL-CAPS ('ORDER',
    'I. BACKGROUND'), or an enumerated title-case head ('C. Deliberate
    Indifference to a Serious Medical Need')."""
    t = text.strip()
    if not t or len(t) > 90:
        return False
    letters = [c for c in t if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        return True
    head, _, rest = t.partition(" ")
    if not rest or not head.endswith("."):
        return False
    num = head.rstrip(".")
    return bool(num) and (
        all(c in "IVX" for c in num)
        or (len(num) == 1 and num.isalpha() and num.isupper())
    )


class WesternDistrictOfNorthCarolina(DistrictBase):
    court_id = "ncwd"
    court_label = (
        "United States District Court, Western District of North Carolina."
    )

    # ------------------------------------------------------------ opinion start
    def find_authors(self, all_segments) -> list:
        """Opinion start from the caption geometry: the first page-1 segment
        BELOW the ')' rail (the fingerprint's ``rail_band``). The title sits
        inside the caption column here, so the generic heading scan would
        run pages ahead to the decretal 'ORDER' section. Falls back to the
        generic path when there is no rail (the whitespace style opens with
        a real centered heading)."""
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        cap_bottom = None
        if sig and sig.get("rail_band"):
            cap_bottom = sig["rail_band"][1]
        if cap_bottom is not None:
            self._district_author = (
                self._signature_author(all_segments)
                or self._present_author(all_segments)
                or self._byline_author(all_segments)
                or self._caption_judge(all_segments)
            )
            for i, (pno, seg, _k) in enumerate(all_segments):
                if pno != 1:
                    break
                if seg and seg[0].get("top", 0) > cap_bottom + 4:
                    return [i]
        return super().find_authors(all_segments)

    # ------------------------------------------------------- section headings
    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            for b in op.blocks:
                if b.kind != "p":
                    continue
                t = str(b.text)
                if "<strong>" not in t:
                    continue
                inner = self._untag(t).strip()
                # fully bold: no printable text outside the <strong> spans
                outside, s = [], t
                while True:
                    i = s.find("<strong>")
                    if i < 0:
                        outside.append(s)
                        break
                    outside.append(s[:i])
                    j = s.find("</strong>", i)
                    if j < 0:
                        break
                    s = s[j + len("</strong>"):]
                bold_only = not any(
                    c.isalnum() for c in self._untag("".join(outside))
                )
                if bold_only and _is_section_heading(inner):
                    b.kind = "heading"
        return doc
