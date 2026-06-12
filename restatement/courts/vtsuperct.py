"""Vermont Superior Court.

Intermediate appellate court. Single ruling by one judge; the author comes from the signature block and the whole ruling is one opinion (district-court model).
"""

from __future__ import annotations

from ._district import DistrictBase


class VermontSuperiorCourt(DistrictBase):
    court_id = "vtsuperct"
    court_label = "Vermont Superior Court."

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        # a furniture line ('Superior Court Judge') is not a name
        au = getattr(self, "_district_author", None)
        if au and any(w in au.lower().split() for w in ("court", "division", "superior")):
            self._district_author = None
        if out and getattr(self, "_district_author", None):
            return out
        # Environmental Division decisions have no heading after the
        # masthead — the ruling starts at the first body paragraph and is
        # signed 'Electronically signed … / Thomas G. Walsh, Judge /
        # Superior Court, Environmental Division' (name + title one line).
        if not getattr(self, "_district_author", None):
            lines = [
                self.line_plain_text(l).strip()
                for _p, seg, _k in all_segments
                for l in seg
            ]
            for t in reversed(lines):
                if t.lower().rstrip(".").endswith(", judge") or t.lower().rstrip(
                    "."
                ).endswith(" judge"):
                    head = t.rsplit(",", 1)[0].strip()
                    toks = head.split()
                    if (
                        2 <= len(toks) <= 4
                        and all(w[:1].isupper() for w in toks)
                        and not any(
                            w.lower() in ("court", "superior", "division", "judge")
                            for w in toks
                        )
                    ):
                        self._district_author = head
                        break
        if out:
            return out
        # single-spaced decisions read as 'notice' to the classifier — the
        # ruling starts at the first multi-line prose segment
        for i, (_p, seg, kind) in enumerate(all_segments):
            if kind == "body" or (
                kind in ("notice", "blockquote") and len(seg) >= 3
            ):
                return [i]
        return []
