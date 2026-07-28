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
    blockquote_by_indent = True

    def _byline_at(self, line) -> bool:
        """An opinion-opening byline always carries the inline dash.

        Publication orders end in a centered ``MAXA, J.``-style signature.
        The broader Washington parser intentionally accepts a dashless clause
        after a byline has already been isolated, but it must not promote that
        order signature to the start of a phantom opinion.
        """
        text = self.line_plain_text(line).strip()
        return any(mark in text for mark in ("—", "–")) and self._abbrev_parse(text) is not None

    def find_authors(self, all_segments) -> list:
        # Apply the same dash gate to the final candidate list: the shared
        # StateSupreme finder also has a direct parse path used by several
        # dashless courts, so overriding only ``_byline_at`` is not enough.
        return [
            i
            for i in super().find_authors(all_segments)
            if any(
                mark in self.line_plain_text(all_segments[i][1][0])
                for mark in ("—", "–")
            )
        ]

    def _is_running_head(self, text: str) -> bool:
        if super()._is_running_head(text):
            return True
        # Division One commonly omits the "No." prefix:
        # ``87958-8-I/4``.  It remains a compact docket/page token in the
        # page-top band, with no spaces and both digits and hyphens.
        return (
            len(text) <= 28
            and " " not in text
            and "/" in text
            and "-" in text
            and any(c.isdigit() for c in text)
        )

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        # The dash is the byline/body delimiter, not part of the prose.  The
        # shared character split deliberately errs toward retaining boundary
        # glyphs; trim only those leading delimiter characters from block one.
        if op.blocks and op.blocks[0].kind in ("p", "blockquote"):
            op.blocks[0].text = str(op.blocks[0].text or "").lstrip(" —–")
        return op

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        # Some filed PDFs staple an order granting publication ahead of the
        # previously unpublished opinion. Keep only the second, actual-opinion
        # caption as headmatter; surface the wrapper order in Removed instead
        # of presenting it as another opinion or as part of the case caption.
        banners = [
            i
            for i, row in enumerate(doc.summary)
            if "IN THE COURT OF APPEALS OF THE STATE OF WASHINGTON"
            in _TAG.sub("", str(row)).upper()
        ]
        if len(banners) >= 2:
            wrapper = doc.summary[: banners[1]]

            def row_text(row):
                if isinstance(row, str):
                    return "" if row.startswith("__") else row
                if not isinstance(row, dict):
                    return ""
                if row.get("__hm__"):
                    return _TAG.sub("", str(row.get("html") or ""))
                if row.get("__caption__"):
                    values = []
                    for side in ("left", "right"):
                        for item in row.get(side, []):
                            if isinstance(item, str):
                                values.append(item)
                            elif isinstance(item, dict) and item.get("h"):
                                values.append(str(item["h"]))
                    return " ".join(values)
                return ""

            order_text = " ".join(
                text for text in (row_text(row).strip() for row in wrapper) if text
            )
            if order_text:
                doc.dropped = list(doc.dropped) + [
                    "Publication order wrapper: " + order_text
                ]
            doc.summary = doc.summary[banners[1] :]
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
        lines = [line for seg in headmatter_segs for line in seg]
        banners = [
            i
            for i, line in enumerate(lines)
            if "court of appeals of the state of washington"
            in self.line_plain_text(line).strip().lower()
        ]
        if len(banners) >= 2:
            # A publication order and the opinion each carry their own caption.
            # Fold them independently; folding the combined stream claims only
            # the first caption and leaves the second one's columns interleaved.
            first_lines = lines[: banners[1]]
            second_lines = lines[banners[1] :]
            first = super().extract_headmatter([first_lines], page1_rules)
            second = super().extract_headmatter([second_lines], None)
            if not any(
                isinstance(row, dict) and row.get("__caption__")
                for row in first["summary"]
            ):
                first["summary"] = self._fold_open_caption(
                    first["summary"], [first_lines]
                )
            if not any(
                isinstance(row, dict) and row.get("__caption__")
                for row in second["summary"]
            ):
                # _fold_open_caption normally operates on the document's
                # page-1 caption. Here the opinion's own caption begins on a
                # later stapled page, so present a geometry-only copy rebased
                # to page 1 for the fold; the rendered rows retain their text
                # and spacing, and no source object is mutated.
                fold_lines = []
                for line in second_lines:
                    copied = dict(line)
                    copied["page_number"] = 1
                    copied["chars"] = [
                        {**char, "page_number": 1}
                        for char in (line.get("chars") or [])
                    ]
                    fold_lines.append(copied)
                second["summary"] = self._fold_open_caption(
                    second["summary"], [fold_lines]
                )
            first["summary"] = first["summary"] + [""] + second["summary"]
            first["dropped"] = list(first.get("dropped") or []) + list(
                second.get("dropped") or []
            )
            return first

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
