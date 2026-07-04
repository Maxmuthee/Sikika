"""Create the SQLite DB and seed demo projects (no API key needed).

Run:  python scripts/init_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.seed import seed_all

if __name__ == "__main__":
    seed_all()
    print("DB ready. USSD will serve hand-written fallback text until you run ingest.py.")
