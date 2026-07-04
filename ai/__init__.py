"""Sikika AI core — the four AI touch-points for civic budget accountability.

1. simplify_budget()    : 200-page English PDF text -> 140-char mother-tongue SMS
2. translate_feedback() : citizen feedback (any language) -> English + PII-scrubbed
3. aggregate_feedback() : many citizen votes/comments -> one county-facing brief

All calls go through the Claude API. Language is a single `lang` code threaded
everywhere: "sw" (Kiswahili), "ki" (Gikuyu), "en" (English).
"""

from .core import simplify_budget, simplify_pdf, translate_feedback, aggregate_feedback
from .prompts import LANGUAGES, is_supported

__all__ = [
    "simplify_budget",
    "simplify_pdf",
    "translate_feedback",
    "aggregate_feedback",
    "LANGUAGES",
    "is_supported",
]
