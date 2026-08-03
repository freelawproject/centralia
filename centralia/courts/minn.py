"""Supreme Court of Minnesota.

Standard bold all-caps byline ('THISSEN, Justice.' / 'MOORE III, Justice.' /
'MCKEIG, Justice (concurring).'); the shared state-supreme base handles it.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class MinnesotaSupreme(StateSupreme):
    court_id = "minn"
    court_label = "Supreme Court of Minnesota."

    def parse_author_line(self, text):
        """Parse Minnesota's accented and generational-suffix bylines.

        The shared name grammar is intentionally conservative ASCII and does
        not accept ``GAÏTAS, Justice.`` or ``MOORE, III, Justice.``.  Minnesota
        prints this exact title-last form at the opinion boundary.
        """
        original = text.strip().rstrip(".")
        kind = None
        if original.endswith(")") and "(" in original:
            original, _, tail = original.rpartition("(")
            kind = tail.rstrip(") ").strip() or None
            original = original.rstrip()
        parts = [part.strip() for part in original.split(",")]
        titles = {
            "justice": "Justice",
            "chief justice": "Chief Justice",
            "j": "Justice",
            "j.": "Justice",
            "c.j": "Chief Justice",
            "c.j.": "Chief Justice",
        }
        title_key = parts[-1].lower() if parts else ""
        if len(parts) >= 2 and title_key in titles:
            name = ", ".join(parts[:-1]).strip()
            letters = "".join(char for char in name if char.isalpha())
            caps_name = letters.isupper() or (
                letters.startswith("Mc") and letters[2:].isupper()
            ) or (
                letters.startswith("Mac") and letters[3:].isupper()
            )
            if letters and caps_name:
                return name, titles[title_key], kind
        return super().parse_author_line(text)
