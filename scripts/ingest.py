"""Run the AI simplification ahead of time and store it (AI Point 1).

This is the 'when a budget is tabled' step: it turns each project's raw source
(text or PDF) into length-capped SW / KI / EN screens and writes them to the
translations table. USSD then just reads them — no LLM call inside the 90s
USSD session.

Needs ANTHROPIC_API_KEY. Run:  python scripts/ingest.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import LANGUAGES, simplify_budget, simplify_pdf
from app import store
from data.seed import seed_all


def ingest() -> None:
    seed_all()  # ensure projects exist (idempotent-ish for a fresh demo DB)

    for ward in ("Molo",):
        for project in store.list_projects(ward):
            pid, name, pdf = project["id"], project["name_en"], project["pdf_path"]
            print(f"\nProject #{pid}: {name}  ({'PDF' if pdf else 'text'} source)")
            for lang in LANGUAGES:
                try:
                    if pdf:
                        s = simplify_pdf(pdf, lang)
                    else:
                        s = simplify_budget(project["raw_text"], lang)
                    store.upsert_translation(
                        pid, lang,
                        project_name=s.project_name,
                        sms_alert=s.sms_alert,
                        civic_education=s.civic_education,
                        data_summary=s.data_summary,
                    )
                    print(f"  {lang}: {s.sms_alert[:70]}...")
                except Exception as e:  # keep going; one language failing is not fatal
                    print(f"  {lang}: SKIPPED ({type(e).__name__}: {e})")

    print("\nIngest complete. USSD now serves AI-simplified content.")


if __name__ == "__main__":
    ingest()
