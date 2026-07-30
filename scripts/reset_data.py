"""Clear citizen-generated data to simulate everything from the start.

Wipes: registrations, votes, feedback, sms threads, browse profiles.
Keeps:  projects, bills, and AI-generated translations (no re-ingest needed).

Run:  python scripts/reset_data.py
(Full wipe instead? Delete sikika.db and run scripts/init_db.py + ingest.py.)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import store

USER_TABLES = ("sms", "feedback", "votes", "registrations", "profiles")

if __name__ == "__main__":
    store.init_db()
    with store._conn() as c:
        for t in USER_TABLES:
            c.execute(f"DELETE FROM {t}")
    print("Cleared:", ", ".join(USER_TABLES))
    print("Kept:   projects + translations")
    print("Fresh start ready — every phone is now an unregistered new user.")
