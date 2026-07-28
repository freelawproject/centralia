"""Arizona Court of Appeals.

Shares the Arizona page mechanics (running-header drop, ¶-marker body grouping,
centered headings, page-aware headmatter) with the Supreme Court via
``ArizonaStyle``. What is specific here:

  * the byline is name-first and letter-spaced: 'M O R S E, Judge:' /
    'J A C O B S, Judge, dissenting:' / 'C A T T A N I, Judge, dissenting in
    part.'. The spaced capitals are collapsed to a surname ('MORSE');
  * the trial-court judge in the caption ('The Honorable ... , Judge') is not
    an author and is excluded;
  * unlike the Supreme Court, the running header stays 'Opinion of the Court'
    even on a separate writing's pages, so opinion boundaries come from these
    body bylines (handled by the shared base's byline scan), not header
    transitions.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._arizona import ArizonaStyle
from ._statesupreme import is_caps_name


class ArizonaCourtOfAppeals(ArizonaStyle, StateAppellate):
    court_id = "arizctapp"
    court_label = "Arizona Court of Appeals."

    def extract(self, pdf_path: str):
        # Division Two prints paragraph numbers as small raster glyphs.  Their
        # pixels carry the number, but their geometry carries the useful
        # structure: one glyph in the left paragraph-marker column, aligned
        # with each indented first line.  Number them in document order.
        self._image_paragraph_number = 1
        self._paragraph_marker_images = {}
        return super().extract(pdf_path)

    @staticmethod
    def _marker_image(image, line) -> bool:
        """Whether a tiny image occupies the marker slot beside ``line``."""
        return (
            8 <= image["width"] <= 20
            and 8 <= image["height"] <= 18
            and abs(image["top"] - line["top"]) <= 2.5
            and line["x0"] >= image["x1"] + 20
        )

    def page_lines(self, page):
        lines = super().page_lines(page)
        marker_keys = set()
        for image in sorted(page.images, key=lambda item: item["top"]):
            aligned = [
                line for line in lines if self._marker_image(image, line)
            ]
            if not aligned:
                continue
            line = min(aligned, key=lambda item: abs(item["top"] - image["top"]))
            chars = line.get("chars") or []
            if not chars:
                continue

            number = self._image_paragraph_number
            self._image_paragraph_number += 1
            marker = dict(chars[0])
            marker.update(
                {
                    "text": f"¶{number}",
                    "x0": image["x0"],
                    "x1": image["x1"],
                    # The printed marker is bold.  Give the synthetic character
                    # the same semantic style so the shared Arizona grouper
                    # recognizes it exactly like Division One's text markers.
                    "fontname": "Centralia-Bold",
                }
            )
            line["chars"] = [marker, *chars]
            line["text"] = f"¶{number} {line['text']}"
            # Keep the line's original x0: it describes the indented prose
            # column and is what the generic paragraph splitter uses.  The
            # marker's own x0 remains on its synthetic character.
            marker_keys.add(
                (
                    round(image["top"], 2),
                    round(image["x0"], 2),
                    round(image["width"], 2),
                    round(image["height"], 2),
                )
            )
        self._paragraph_marker_images[page.page_number] = marker_keys
        return lines

    def extract_page_images(self, page) -> list:
        # Paragraph glyphs have already become semantic text in page_lines().
        # Keep every other embedded image as ordinary document content.
        marker_keys = self._paragraph_marker_images.get(page.page_number, set())
        return [
            image
            for image in super().extract_page_images(page)
            if (
                round(image["top"], 2),
                round(image["x0"], 2),
                round(image["width"], 2),
                round(image["height"], 2),
            )
            not in marker_keys
        ]

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        t = text.strip()
        if t.lower().startswith("the honorable"):  # trial-court judge
            return None
        name, sep, after = t.partition(",")
        if not sep:
            return None
        rest = after.strip()
        # Title-led: 'Judge' / 'Presiding Judge' / 'Chief Judge' /
        # 'Vice Chief Judge', optionally followed by a kind ('dissenting').
        title = None
        for cand in ("Vice Chief Judge", "Chief Judge", "Presiding Judge", "Judge"):
            if rest.lower().startswith(cand.lower()):
                title = cand
                rest = rest[len(cand) :]
                break
        if title is None:
            return None
        # Collapse letter-spaced capitals: 'M O R S E' -> 'MORSE'.
        toks = name.split()
        if toks and all(len(tk) == 1 for tk in toks):
            name = "".join(toks)
        else:
            name = name.strip()
        if not is_caps_name(name):
            return None
        kind = rest.strip(" ,.:").strip() or None
        return name, title, kind
