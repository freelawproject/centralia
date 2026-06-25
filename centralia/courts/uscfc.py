"""United States Court of Federal Claims (incl. Office of Special Masters).

Vaccine-program decisions carry the deciding officer in the CAPTION's
right column ('Chief Special Master Corcoran' opposite the petitioner);
the ruling opens at a centered 'DECISION …' / 'OPINION' / 'ORDER …'
heading and is single-spaced (tight segments stay in the body). Ordinary
CFC cases use a 'Judge NAME' caption line instead.
"""

from __future__ import annotations

from ._district import DistrictBase


class CourtOfFederalClaims(DistrictBase):
    court_id = "uscfc"
    court_label = "United States Court of Federal Claims."

    _START = ("DECISION", "OPINION", "RULING", "ORDER", "MEMORANDUM")

    def find_authors(self, all_segments) -> list:
        # author: 'Chief Special Master Corcoran' / 'Special Master X' /
        # 'Judge NAME' from the caption lines
        self._district_author = None
        for _p, seg, _k in all_segments[:14]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                for key in ("Chief Special Master ", "Special Master ", "Judge "):
                    ki = t.find(key)
                    if ki >= 0:
                        cand = t[ki + len(key) :].strip().rstrip(".,")
                        if cand and 1 <= len(cand.split()) <= 4 and all(
                            w[:1].isupper() for w in cand.split()
                        ):
                            self._district_author = (key + cand).strip()
                            break
                if self._district_author:
                    break
            if self._district_author:
                break
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip().upper()
            if any(t.startswith(s) for s in self._START) and len(t) < 70:
                start = i
                break
        if start is not None:
            return [start]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        if getattr(self, "_district_author", None):
            return self._district_author, [line]
        return super().split_author_line(line)