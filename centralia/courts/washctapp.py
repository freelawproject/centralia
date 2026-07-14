"""Washington Court of Appeals.

Same slip-print anatomy as the Washington Supreme Court (wash.py): the
em-dash byline ('BIRK, J. — The Washington State Health Care Authority …'),
two page-1 filing stamps above the banner, a ')'-rail caption whose closing
shelf must not be taken for a footnote separator (the real one is a typed
underscore run or a thin rule with footnote-sized text below), running
heads, and bottom page numbers that restart per writing. Inherits all of
it; only the identity differs. Division-specific quirks land here.
"""

from __future__ import annotations

import re

from .wash import WashingtonSupreme

_TAG = re.compile(r"<[^>]+>")


class WashingtonCourtOfAppeals(WashingtonSupreme):
    court_id = "washctapp"
    court_label = "Washington Court of Appeals."

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        # A publish-order + opinion stapled in one PDF reads as two
        # back-to-back writings by the same judge (the phantom first one is
        # the order's signature image + the opinion's own second caption).
        # Consecutive same-author same-type writings are ONE writing — the
        # oregon 'signed twice' merge.
        merged = []
        for op in doc.opinions:
            if (
                merged
                and merged[-1].author == op.author
                and merged[-1].type == op.type
            ):
                merged[-1].blocks.extend(op.blocks)
                merged[-1].footnotes.extend(op.footnotes)
            else:
                merged.append(op)
        doc.opinions = merged
        self._harvest_panel_signature(doc)
        return doc

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Only boyce-style captions carry the ')' rail (folded by the wash
        base); the other Division slips set an 'Open Range' caption — two
        columns held by whitespace alone — which pdfplumber merges onto
        single lines ('PERSON and ESTATE OF MILO No. 87593-1-I'). When no
        rail caption emerged, rebuild the two columns from the line runs."""
        d = super().extract_headmatter(headmatter_segs, page1_rules)
        if not any(
            isinstance(r, dict) and r.get("__caption__") for r in d["summary"]
        ):
            d["summary"] = self._fold_open_caption(d["summary"], headmatter_segs)
        return d

    @staticmethod
    def _is_sig_line(text: str) -> bool:
        """A panel sign-off line: the authoring judge's conformed signature
        ('MAXA, J.'), the 'We concur:' lead, or a concurring judge's line
        ('VELJACIC, A.C.J.' / 'PRICE, J.')."""
        t = _TAG.sub("", text).strip()
        low = t.lower()
        if "we concur" in low:
            return True
        if len(t) > 30 or "," not in t:
            return False
        name, title = t.split(",", 1)
        core = title.strip().rstrip(".").replace(".", "").replace(" ", "")
        return bool(name.strip()) and core.isupper() and 1 <= len(core) <= 5

    # Division slip opinions set footnotes at BODY size (12pt, only the label
    # digit is superscript), so the Supreme Court's 'smaller type below' test
    # never fires — use the structural separator test (the court also
    # UNDERLINES case names; a rule inside a text line's band is excluded).
    footnote_sep_structural = True

    def _harvest_panel_signature(self, doc) -> None:
        """Lift the three-judge sign-off panel ('MAXA, J. / We concur: /
        VELJACIC, A.C.J. / PRICE, J.', with conformed-signature images between)
        off the end of the last opinion into ``doc.signature``."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        i = len(blocks)
        while i > 0 and (
            blocks[i - 1].kind == "image"
            or self._is_sig_line(str(blocks[i - 1].text or ""))
        ):
            i -= 1
        # Require the run to actually contain the 'We concur' panel lead, so an
        # ordinary opinion ending on a short line isn't swept up.
        run = blocks[i:]
        if not any("we concur" in _TAG.sub("", str(b.text or "")).lower() for b in run):
            return
        op.blocks = blocks[:i]
        doc.signature = [
            {"__image__": True, **(b.payload or {})}
            if b.kind == "image"
            else _TAG.sub("", str(b.text or "")).strip()
            for b in run
        ]
