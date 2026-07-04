"""Sikika AI core — Claude API calls behind the three outbound/inbound AI tasks.

Uses client.messages.parse() with Pydantic schemas so callers get validated
objects, never fragile hand-parsed JSON. Model defaults to claude-opus-4-8
(override with SIKIKA_MODEL, e.g. claude-haiku-4-5 for cheap high-volume SMS).
"""

from __future__ import annotations

import base64
import os
from functools import lru_cache
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .prompts import (
    AGGREGATE_SYSTEM,
    FEEDBACK_TRANSLATE_SYSTEM,
    is_supported,
    simplify_system,
)

load_dotenv()

MODEL = os.getenv("SIKIKA_MODEL", "claude-opus-4-8")


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    # Resolves ANTHROPIC_API_KEY from env (loaded from .env above).
    return anthropic.Anthropic()


# --- Schemas -----------------------------------------------------------------
class BudgetSummary(BaseModel):
    """AI Point 1 output — feeds the SMS alert and the USSD menu tree."""

    project_name: str = Field(description="Short project name in the target language")
    sms_alert: str = Field(description="<=160 char SMS alert in the target language")
    civic_education: str = Field(description="<=130 char 'what is this project' explainer")
    data_summary: str = Field(description="<=130 char raw facts: amount, source, status")


class FeedbackAnalysis(BaseModel):
    """AI Point 2 output — one citizen's feedback, translated and scrubbed."""

    english: str = Field(description="Faithful English translation, PII redacted")
    sentiment: Literal["support", "oppose", "mixed", "unclear"]
    theme: str = Field(description="Main concern in 1-4 English words")


class CountyBrief(BaseModel):
    """AI Point 4 output — the artifact that makes participation visible."""

    total: int = Field(description="Number of feedback items considered")
    support: int
    oppose: int
    headline: str = Field(description="One-sentence summary for officials")
    top_concerns: list[str] = Field(description="Concerns ranked most-common first")


# --- AI Point 1: simplification ---------------------------------------------
def simplify_budget(raw_text: str, lang: str = "sw") -> BudgetSummary:
    """Turn a raw English budget excerpt into mother-tongue, feature-phone-ready text."""
    if not is_supported(lang):
        raise ValueError(f"Unsupported language: {lang!r}")

    resp = _client().messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=simplify_system(lang),
        messages=[{"role": "user", "content": raw_text}],
        output_format=BudgetSummary,
    )
    return resp.parsed_output


def simplify_pdf(pdf_path: str, lang: str = "sw", instruction: str | None = None) -> BudgetSummary:
    """Same as simplify_budget() but reads a real PDF (e.g. a tabled bill or budget).

    Sends the PDF to Claude via a native document block — no local PDF tooling
    needed. This is the true 'a 200-page PDF nobody can read -> one SMS' path.
    """
    if not is_supported(lang):
        raise ValueError(f"Unsupported language: {lang!r}")

    with open(pdf_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    task = instruction or (
        "Summarise the parts of this document that affect an ordinary citizen — "
        "licences, permits, fees, penalties, deadlines, and who is affected."
    )
    resp = _client().messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=simplify_system(lang),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": data,
                        },
                    },
                    {"type": "text", "text": task},
                ],
            }
        ],
        output_format=BudgetSummary,
    )
    return resp.parsed_output


# --- AI Point 2: feedback translation ---------------------------------------
def translate_feedback(text: str, source_lang: str = "sw") -> FeedbackAnalysis:
    """Translate one citizen's feedback to English, scrub PII, tag it."""
    resp = _client().messages.parse(
        model=MODEL,
        max_tokens=512,
        system=FEEDBACK_TRANSLATE_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Source language: {source_lang}\nFeedback:\n{text}",
            }
        ],
        output_format=FeedbackAnalysis,
    )
    return resp.parsed_output


# --- AI Point 4: aggregation ------------------------------------------------
def aggregate_feedback(items: list[FeedbackAnalysis]) -> CountyBrief:
    """Roll many analysed feedback items into one county-facing brief."""
    if not items:
        raise ValueError("No feedback to aggregate")

    lines = [
        f"- [{it.sentiment}] ({it.theme}) {it.english}" for it in items
    ]
    payload = "Citizen feedback on this budget item:\n" + "\n".join(lines)

    resp = _client().messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=AGGREGATE_SYSTEM,
        messages=[{"role": "user", "content": payload}],
        output_format=CountyBrief,
    )
    return resp.parsed_output
