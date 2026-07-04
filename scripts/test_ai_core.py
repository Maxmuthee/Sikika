"""Smoke-test the Sikika AI core end to end.

Run:  python scripts/test_ai_core.py
Needs ANTHROPIC_API_KEY in .env (copy .env.example -> .env first).

Exercises all four AI points on the real Molo-ward fertilizer example:
  1. simplify a raw English budget excerpt into SW / KI / EN
  2. translate + PII-scrub citizen feedback (given in Kiswahili & English)
  4. aggregate that feedback into a county-facing brief
"""

import sys
from pathlib import Path

# Allow running from repo root without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import LANGUAGES, aggregate_feedback, simplify_budget, translate_feedback

# A realistic raw excerpt — the kind of line buried in a 200-page county PDF.
RAW_BUDGET = """
Programme: Agriculture, Livestock & Fisheries — Crop Development Sub-programme.
Proposed allocation FY2025/26: Fertilizer subsidy for smallholder farmers, Molo Ward,
Nakuru County: KSh 5,000,000. Source of funds: Nakuru County Agricultural Development
Fund. Estimated beneficiaries: 2,000 subsidised bags of NPK fertilizer at reduced cost.
Status: Proposed for approval, pending public participation forum on 10 July at Molo Hall.
""".strip()

# Raw citizen feedback as it would arrive over USSD/SMS (name included on purpose,
# to prove PII scrubbing works before anything is stored).
RAW_FEEDBACK = [
    ("sw", "Mimi Kamau Njoroge nasema pesa ni nzuri lakini mbolea huwa inachelewa kufika msimu wa kupanda."),
    ("sw", "Naunga mkono. Mbolea ya bei nafuu itasaidia wakulima wadogo kama mimi."),
    ("en", "I support it but last year only people who knew the chief got the coupons. Fix the list."),
    ("sw", "Mifuko 2000 haitoshi Molo yote. Ongezeni pesa."),
]


def rule(title: str) -> None:
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def main() -> None:
    # --- AI Point 1: simplification in every supported language --------------
    rule("AI POINT 1 - Budget simplification (SMS/USSD, mother tongue)")
    print("RAW INPUT (English, PDF-style):\n" + RAW_BUDGET + "\n")
    for lang in LANGUAGES:
        s = simplify_budget(RAW_BUDGET, lang)
        print(f"--- {LANGUAGES[lang]['english_name']} ({lang}) ---")
        print(f"  project        : {s.project_name}")
        print(f"  SMS alert [{len(s.sms_alert):>3}]: {s.sms_alert}")
        print(f"  civic ed  [{len(s.civic_education):>3}]: {s.civic_education}")
        print(f"  data      [{len(s.data_summary):>3}]: {s.data_summary}\n")

    # --- AI Point 2: translate + scrub each feedback item -------------------
    rule("AI POINT 2 - Feedback translation + PII scrub (citizen -> county)")
    analysed = []
    for lang, text in RAW_FEEDBACK:
        a = translate_feedback(text, lang)
        analysed.append(a)
        print(f"[{lang}] IN : {text}")
        print(f"     EN : {a.english}")
        print(f"     tag: {a.sentiment} / {a.theme}\n")

    # --- AI Point 4: aggregate into the county brief -----------------------
    rule("AI POINT 4 - County brief (makes participation visible)")
    brief = aggregate_feedback(analysed)
    print(f"  {brief.headline}")
    print(f"  totals : {brief.support} support / {brief.oppose} oppose "
          f"(of {brief.total})")
    print("  top concerns:")
    for i, c in enumerate(brief.top_concerns, 1):
        print(f"    {i}. {c}")

    print("\nOK - AI core working end to end.")


if __name__ == "__main__":
    main()
