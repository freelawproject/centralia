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
        self._harvest_panel_signature(doc)
        return doc

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

    # -------------------------------------------------- footnote separator
    def find_footnote_separator(self, page):
        """Division slip opinions set footnotes at BODY size (12pt, only the
        label digit is superscript), so the Supreme Court's 'smaller type
        below' test never fires and the footnotes fall into the body.

        The court's real cues are structural: the separator is a thin rule at
        the body's left margin, standing clear of any text line (the court
        also UNDERLINES case names — a rule inside a text line's band is an
        underline, not a separator), with footnote matter below it — either a
        raised label digit, or single-spaced continuation text (the body is
        double-spaced, so leading is the discriminator). Caption shelves and
        conformed-signature rules carry double-spaced text below and drop
        out."""
        from collections import Counter

        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        if not chars:
            return None
        body = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        pw, cutoff = page.width, page.height * 0.45
        text_lines = page.extract_text_lines()

        cands = []
        for r in page.rects:
            if (
                r["bottom"] - r["top"] < 2.5
                and (r["x1"] - r["x0"]) >= 60
                and r["x0"] < pw * 0.35
                and r["top"] > cutoff
            ):
                cands.append((r["top"], r["x0"], r["x1"]))
        for ln in page.lines:
            if (
                abs(ln["bottom"] - ln["top"]) < 2.5
                and abs(ln["x1"] - ln["x0"]) >= 60
                and min(ln["x0"], ln["x1"]) < pw * 0.35
                and ln["top"] > cutoff
            ):
                cands.append(
                    (ln["top"], min(ln["x0"], ln["x1"]), max(ln["x0"], ln["x1"]))
                )

        good = []
        for top, rx0, rx1 in cands:
            # An underline sits INSIDE the band of the text line it decorates.
            if any(
                tl["top"] - 1 <= top <= tl["bottom"] + 2
                and tl["x0"] < rx1
                and tl["x1"] > rx0
                for tl in text_lines
            ):
                continue
            below = sorted(
                (tl for tl in text_lines if tl["top"] > top + 1),
                key=lambda tl: tl["top"],
            )[:4]
            if not below:
                continue
            first_chars = below[0].get("chars") or []
            label = first_chars and round(first_chars[0].get("size", 0)) <= body - 3
            gaps = [b["top"] - a["top"] for a, b in zip(below, below[1:])]
            single = gaps and gaps[0] < body * 1.4  # ~13.8 vs the 27.6 body
            if label or single:
                good.append(top)
        return min(good) if good else None

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
