"""pdfio — the ONE pass over the PDF. The only pdfplumber import site.

Everything downstream (classification, caption fingerprint, footnotes,
segmentation, rendering, audit) reads the PageModel/PdfModel built here.
There is no second parse of any page, ever.
"""

from .build import build_pdf
from .model import DrawnRule, Line, PageModel, PdfModel, VRule

__all__ = ["build_pdf", "DrawnRule", "Line", "PageModel", "PdfModel", "VRule"]
