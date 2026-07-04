"""Sikika AI core — LLM calls behind the outbound/inbound AI tasks.

Uses the OpenAI SDK pointed at DeepSeek's OpenAI-compatible API
(base_url = https://api.deepseek.com). Structured outputs use DeepSeek's JSON
mode, validated into the same Pydantic schemas the rest of the app expects, so
callers get validated objects and function signatures are unchanged.

Config (from .env):
  SIKIKA_API_KEY   - the DeepSeek API key
  SIKIKA_BASE_URL  - default https://api.deepseek.com
  SIKIKA_MODEL     - default deepseek-chat
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from .prompts import (
    AGGREGATE_SYSTEM,
    FEEDBACK_TRANSLATE_SYSTEM,
    is_supported,
    simplify_system,
    sms_assistant_system,
)

load_dotenv()

MODEL = os.getenv("SIKIKA_MODEL", "deepseek-chat")
BASE_URL = os.getenv("SIKIKA_BASE_URL", "https://api.deepseek.com")


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("SIKIKA_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
        base_url=BASE_URL,
    )


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

    total: int = Field(description="integer: number of feedback items considered")
    support: int = Field(description="integer: count supporting")
    oppose: int = Field(description="integer: count opposing")
    headline: str = Field(description="One-sentence summary for officials")
    top_concerns: list[str] = Field(description="JSON array of strings, most-common first")


# --- structured-output helper (DeepSeek JSON mode) --------------------------
def _json_instruction(model_cls: type[BaseModel]) -> str:
    lines = []
    for name, f in model_cls.model_fields.items():
        t = getattr(f.annotation, "__name__", None) or str(f.annotation)
        lines.append(f'  "{name}": ({t}) {f.description or ""}')
    return (
        "Respond ONLY with a single valid JSON object (no markdown, no code fences) "
        "with exactly these keys:\n{\n" + ",\n".join(lines) + "\n}"
    )


def _structured(system: str, user: str, model_cls, max_tokens: int = 1024,
                temperature: float = 0.3):
    resp = _client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system + "\n\n" + _json_instruction(model_cls)},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return model_cls.model_validate_json(resp.choices[0].message.content)


# --- AI Point 1: simplification ---------------------------------------------
def simplify_budget(raw_text: str, lang: str = "sw") -> BudgetSummary:
    """Turn a raw English budget excerpt into mother-tongue, feature-phone-ready text."""
    if not is_supported(lang):
        raise ValueError(f"Unsupported language: {lang!r}")
    return _structured(simplify_system(lang), raw_text, BudgetSummary)


def _pdf_text(pdf_path: str, max_chars: int = 20000) -> str:
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return text[:max_chars]


def simplify_pdf(pdf_path: str, lang: str = "sw", instruction: str | None = None) -> BudgetSummary:
    """Simplify a real PDF (e.g. a tabled bill). Text is extracted locally with
    pypdf (DeepSeek has no PDF input), then simplified like any budget text."""
    if not is_supported(lang):
        raise ValueError(f"Unsupported language: {lang!r}")
    text = _pdf_text(pdf_path)
    if not text.strip():
        raise ValueError("No extractable text in PDF (it may be a scanned image).")
    return simplify_budget(text, lang)


# --- SMS assistant: conversational civic Q&A over SMS -----------------------
def answer_sms(question: str, history: list[tuple[str, str]], context: str,
               lang_hint: str | None = None) -> str:
    """Answer one citizen SMS question, grounded in the projects `context`."""
    messages = [{"role": "system", "content": sms_assistant_system(context, lang_hint)}]
    for d, b in history:
        messages.append({"role": "user" if d == "in" else "assistant", "content": b})
    messages.append({"role": "user", "content": question})

    resp = _client().chat.completions.create(
        model=MODEL, messages=messages, max_tokens=320, temperature=0.4,
    )
    return (resp.choices[0].message.content or "").strip()


# --- AI Point 2: feedback translation ---------------------------------------
def translate_feedback(text: str, source_lang: str = "sw") -> FeedbackAnalysis:
    """Translate one citizen's feedback to English, scrub PII, tag it."""
    return _structured(
        FEEDBACK_TRANSLATE_SYSTEM,
        f"Source language: {source_lang}\nFeedback:\n{text}",
        FeedbackAnalysis,
        max_tokens=512,
    )


# --- AI Point 4: aggregation ------------------------------------------------
def aggregate_feedback(items: list[FeedbackAnalysis]) -> CountyBrief:
    """Roll many analysed feedback items into one county-facing brief."""
    if not items:
        raise ValueError("No feedback to aggregate")
    payload = "Citizen feedback on this budget item:\n" + "\n".join(
        f"- [{it.sentiment}] ({it.theme}) {it.english}" for it in items
    )
    return _structured(AGGREGATE_SYSTEM, payload, CountyBrief)
