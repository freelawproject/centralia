"""Renderers that consume an ``ExtractedDocument``."""

from .casebody import render_casebody
from .html import fingerprint, render_html, render_index

__all__ = ["fingerprint", "render_casebody", "render_html", "render_index"]
