"""Shared base for the New York trial courts published as 'NY Slip Op' (U)
decisions — Supreme Court, Civil Court, Family Court, Surrogate's Court. They all
carry the same machine-generated cover page and e-filed decision:

  * Page 1 is a cover sheet: the case name, the slip-opinion number ('2026 NY
    Slip Op 31149(U)'), the date, the court + county, the docket, and 'Judge:
    <name>' — followed by a fixed republication notice ('Cases posted with a
    "30000" identifier ... not selected for official publication.') and a
    'file:///...' path footer.
  * Page 2 onward is the decision itself, stamped with NYSCEF e-filing furniture
    ('INDEX NO. ...', 'NYSCEF DOC. NO. ... RECEIVED NYSCEF: ...') at the page
    edges, a 'STATE OF NEW YORK / ... COURT' caption, a 'DECISION AND ORDER'
    heading, and the body.

The author is taken from the cover's 'Judge:' line; the opinion is everything
from page 2 on; the republication notice, the file path, and the NYSCEF stamps
are dropped as furniture.
"""

from __future__ import annotations

from ..models import DocType
from .generic import GenericExtractor


def _is_nyscef(low: str) -> bool:
    return (
        low.startswith("nyscef doc")
        or low.startswith("index no.")
        or "received nyscef" in low
        or low.startswith("file://")
        or low.startswith("filed:")
    )


class NewYorkSlipOp(GenericExtractor):
    # The scanned decisions' OCR layers have tight line gaps that classify
    # as 'notice' — never drop them from the body.
    drop_notice_in_body = False
    # The cover's bold case-name title sits at top~38; keep it (default 39 clips
    # it).
    margin_top = 30.0

    def extract(self, pdf_path):
        self._ny_author = ""
        self._ny_dropped = []
        doc = super().extract(pdf_path)
        doc.doc_type = DocType.OPINION
        seen, uniq = set(), []
        for t in self._ny_dropped:
            if t and t not in seen:
                seen.add(t)
                uniq.append(t)
        if uniq:
            doc.dropped = list(doc.dropped) + uniq
        return doc

    @staticmethod
    def _x_runs(line):
        chars = line.get("chars") or []
        runs, cur = [], []
        for c in chars:
            if cur and c["x0"] - cur[-1]["x1"] > 8:
                runs.append(cur)
                cur = [c]
            else:
                cur.append(c)
        if cur:
            runs.append(cur)
        return runs

    def page_lines(self, page):
        out, in_notice = [], False
        for l in super().page_lines(page):
            t = self.line_plain_text(l).strip()
            low = t.lower()
            if low.startswith("cases posted with"):
                in_notice = True
            if in_notice:
                self._ny_dropped.append(t)
                if low.endswith("publication.") or low == "publication":
                    in_notice = False
                continue
            if _is_nyscef(low):
                # An edge stamp can merge with a caption row — drop only the
                # stamp runs, keep the content runs.
                keep = []
                for r in self._x_runs(l):
                    rt = self.line_plain_text({"chars": r}).strip()
                    if _is_nyscef(rt.lower()):
                        self._ny_dropped.append(rt)
                    else:
                        keep.append(r)
                if keep:
                    chars = [c for r in keep for c in r]
                    l = dict(l)
                    l["chars"] = chars
                    l["x0"] = min(c["x0"] for c in chars)
                    l["x1"] = max(c["x1"] for c in chars)
                    out.append(l)
                continue
            out.append(l)
        return out

    def find_authors(self, all_segments) -> list:
        # Author off the cover's 'Judge:' line.
        self._ny_author = ""
        for _p, seg, _k in all_segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                if t.startswith("Judge:"):
                    self._ny_author = t[len("Judge:"):].strip()
                    break
            if self._ny_author:
                break
        # The decision is everything from page 2 on (page 1 is the cover sheet).
        for i, (pno, _seg, _k) in enumerate(all_segments):
            if pno >= 2:
                return [i]
        return []

    def split_author_line(self, line):
        # The decision opens on the page-2 caption/body, not a byline.
        return "", [line]

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        op.author = self._ny_author or "PER CURIAM"
        return op
