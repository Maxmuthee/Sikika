"""Copy data from the local SQLite DB into the PostgreSQL (Neon) database.

By default it copies only the *content* — projects and their AI translations —
which is what production needs (real citizen activity is collected live via
USSD/SMS). Pass --with-activity to also copy the demo citizen rows
(registrations, profiles, votes, feedback, sms) for a populated demo.

Usage:
  # DATABASE_URL (Neon) must be set in .env or the environment.
  python -m scripts.migrate_to_neon                 # projects + translations
  python -m scripts.migrate_to_neon --with-activity # + demo citizen data
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = os.getenv("SIKIKA_DB", "sikika.db")

CONTENT_TABLES = ["projects", "translations"]
ACTIVITY_TABLES = ["registrations", "profiles", "votes", "feedback", "sms"]


def _columns(sq: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in sq.execute(f"PRAGMA table_info({table})")]


def _copy_table(sq: sqlite3.Connection, pg, table: str) -> int:
    cols = _columns(sq, table)
    rows = sq.execute(f"SELECT {', '.join(cols)} FROM {table}").fetchall()
    if not rows:
        return 0
    placeholders = ", ".join(["%s"] * len(cols))
    collist = ", ".join(cols)
    sql = f"INSERT INTO {table} ({collist}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    with pg.cursor() as cur:
        cur.executemany(sql, [tuple(r) for r in rows])
        # Keep SERIAL sequences ahead of the copied ids.
        if "id" in cols:
            cur.execute(
                "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                "COALESCE((SELECT MAX(id) FROM " + table + "), 1))",
                (table,),
            )
    return len(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-activity", action="store_true",
                    help="also copy demo citizen data (registrations, votes, feedback, sms)")
    args = ap.parse_args()

    if not DATABASE_URL:
        sys.exit("DATABASE_URL is not set. Uncomment it in .env (Neon) first.")

    import psycopg  # imported here so SQLite-only runs don't need it

    tables = CONTENT_TABLES + (ACTIVITY_TABLES if args.with_activity else [])

    sq = sqlite3.connect(SQLITE_PATH)
    # Ensure the target schema exists before copying.
    from app import store
    store.init_db()

    with psycopg.connect(DATABASE_URL, autocommit=False) as pg:
        for table in tables:
            n = _copy_table(sq, pg, table)
            print(f"  {table:15} copied {n} rows")
        pg.commit()
    sq.close()
    print("Done. Neon now holds the migrated data.")


if __name__ == "__main__":
    main()
