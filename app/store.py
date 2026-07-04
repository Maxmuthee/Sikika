"""SQLite persistence for Sikika.

Tables:
  projects       -- a tabled budget item / bill (raw English source)
  translations   -- AI-simplified content per project x language
  profiles       -- hashed phone -> ward/language (no personal data)
  votes          -- one support/oppose per hashed phone per project
  feedback       -- citizen feedback: raw + English + PII-scrubbed + tagged

The USSD path only READS translations (AI runs ahead of time, at ingest — a
USSD session is too short to call an LLM). See scripts/ingest.py.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

DB_PATH = os.getenv("SIKIKA_DB", "sikika.db")


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ward        TEXT NOT NULL,
                name_en     TEXT NOT NULL,
                raw_text    TEXT NOT NULL,
                pdf_path    TEXT,
                status      TEXT DEFAULT 'Proposed'
            );
            CREATE TABLE IF NOT EXISTS translations (
                project_id      INTEGER NOT NULL REFERENCES projects(id),
                lang            TEXT NOT NULL,
                project_name    TEXT NOT NULL,
                sms_alert       TEXT NOT NULL,
                civic_education TEXT NOT NULL,
                data_summary    TEXT NOT NULL,
                PRIMARY KEY (project_id, lang)
            );
            CREATE TABLE IF NOT EXISTS profiles (
                phone_hash  TEXT PRIMARY KEY,
                lang        TEXT,
                sub_county  TEXT,
                ward        TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );
            -- One-time citizen registration. phone_number is retained ONLY to
            -- deliver SMS alerts; id_hash (never the raw ID) is UNIQUE so a
            -- person can register once even from a different phone.
            CREATE TABLE IF NOT EXISTS registrations (
                phone_hash   TEXT PRIMARY KEY,
                phone_number TEXT NOT NULL,
                id_hash      TEXT NOT NULL UNIQUE,
                lang         TEXT,
                sub_county   TEXT,
                ward         TEXT,
                created_at   TEXT DEFAULT (datetime('now'))
            );
            -- One vote per person per project. voter_hash is a vote-scoped hash
            -- of the national ID (see hashing.vote_nullifier) — never the ID,
            -- never the phone. A person can vote once even across phones.
            CREATE TABLE IF NOT EXISTS votes (
                project_id  INTEGER NOT NULL REFERENCES projects(id),
                voter_hash  TEXT NOT NULL,
                choice      TEXT NOT NULL CHECK (choice IN ('support','oppose')),
                created_at  TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (project_id, voter_hash)
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id),
                phone_hash  TEXT NOT NULL,
                lang        TEXT,
                english     TEXT,
                sentiment   TEXT,
                theme       TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );
            """
        )


# --- projects & translations -------------------------------------------------
def upsert_project(ward: str, name_en: str, raw_text: str,
                   pdf_path: Optional[str] = None, status: str = "Proposed") -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO projects (ward, name_en, raw_text, pdf_path, status) "
            "VALUES (?,?,?,?,?)",
            (ward, name_en, raw_text, pdf_path, status),
        )
        return int(cur.lastrowid)


def get_or_create_project(ward: str, name_en: str, raw_text: str,
                          pdf_path: Optional[str] = None, status: str = "Proposed") -> int:
    """Return the id of an existing (ward, name) project, or create it.

    Makes seeding idempotent — re-running init_db does not duplicate rows or
    disturb votes/feedback already recorded against a project.
    """
    with _conn() as c:
        row = c.execute(
            "SELECT id FROM projects WHERE ward = ? AND name_en = ?", (ward, name_en)
        ).fetchone()
        if row:
            return int(row["id"])
        cur = c.execute(
            "INSERT INTO projects (ward, name_en, raw_text, pdf_path, status) "
            "VALUES (?,?,?,?,?)",
            (ward, name_en, raw_text, pdf_path, status),
        )
        return int(cur.lastrowid)


def upsert_translation(project_id: int, lang: str, project_name: str,
                       sms_alert: str, civic_education: str, data_summary: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO translations "
            "(project_id, lang, project_name, sms_alert, civic_education, data_summary) "
            "VALUES (?,?,?,?,?,?) "
            "ON CONFLICT(project_id, lang) DO UPDATE SET "
            "project_name=excluded.project_name, sms_alert=excluded.sms_alert, "
            "civic_education=excluded.civic_education, data_summary=excluded.data_summary",
            (project_id, lang, project_name, sms_alert, civic_education, data_summary),
        )


def list_projects(ward: str) -> list[sqlite3.Row]:
    with _conn() as c:
        return c.execute(
            "SELECT * FROM projects WHERE ward = ? ORDER BY id", (ward,)
        ).fetchall()


def get_project(project_id: int) -> Optional[sqlite3.Row]:
    with _conn() as c:
        return c.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()


def get_translation(project_id: int, lang: str) -> Optional[sqlite3.Row]:
    """Return the translation for lang, falling back to English then any row."""
    with _conn() as c:
        for candidate in (lang, "en"):
            row = c.execute(
                "SELECT * FROM translations WHERE project_id = ? AND lang = ?",
                (project_id, candidate),
            ).fetchone()
            if row:
                return row
        return c.execute(
            "SELECT * FROM translations WHERE project_id = ? LIMIT 1", (project_id,)
        ).fetchone()


# --- profiles, votes, feedback ----------------------------------------------
def upsert_profile(phone_hash: str, lang: str, sub_county: str, ward: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO profiles (phone_hash, lang, sub_county, ward) VALUES (?,?,?,?) "
            "ON CONFLICT(phone_hash) DO UPDATE SET "
            "lang=excluded.lang, sub_county=excluded.sub_county, ward=excluded.ward",
            (phone_hash, lang, sub_county, ward),
        )


def get_registration(phone_hash: str) -> Optional[sqlite3.Row]:
    with _conn() as c:
        return c.execute(
            "SELECT * FROM registrations WHERE phone_hash = ?", (phone_hash,)
        ).fetchone()


def register(phone_hash: str, phone_number: str, id_hash: str,
             lang: str, sub_county: str, ward: str) -> str:
    """Create a one-time registration. Returns 'ok', 'id_taken', or 'phone_taken'."""
    with _conn() as c:
        if c.execute("SELECT 1 FROM registrations WHERE phone_hash = ?",
                     (phone_hash,)).fetchone():
            return "phone_taken"
        if c.execute("SELECT 1 FROM registrations WHERE id_hash = ?",
                     (id_hash,)).fetchone():
            return "id_taken"
        c.execute(
            "INSERT INTO registrations "
            "(phone_hash, phone_number, id_hash, lang, sub_county, ward) "
            "VALUES (?,?,?,?,?,?)",
            (phone_hash, phone_number, id_hash, lang, sub_county, ward),
        )
        return "ok"


def registrations_in(sub_county: str, ward: Optional[str] = None) -> list[sqlite3.Row]:
    """Registered citizens in a sub-county (optionally a specific ward)."""
    with _conn() as c:
        if ward:
            return c.execute(
                "SELECT phone_number, lang, ward FROM registrations "
                "WHERE sub_county = ? AND ward = ?", (sub_county, ward)
            ).fetchall()
        return c.execute(
            "SELECT phone_number, lang, ward FROM registrations WHERE sub_county = ?",
            (sub_county,),
        ).fetchall()


def count_registrations() -> int:
    with _conn() as c:
        return int(c.execute("SELECT COUNT(*) n FROM registrations").fetchone()["n"])


def has_voted(project_id: int, voter_hash: str) -> bool:
    with _conn() as c:
        return c.execute(
            "SELECT 1 FROM votes WHERE project_id = ? AND voter_hash = ?",
            (project_id, voter_hash),
        ).fetchone() is not None


def record_vote(project_id: int, voter_hash: str, choice: str) -> None:
    """Record a vote. Once cast, a person's vote is final (no overwrite)."""
    with _conn() as c:
        c.execute(
            "INSERT INTO votes (project_id, voter_hash, choice) VALUES (?,?,?) "
            "ON CONFLICT(project_id, voter_hash) DO NOTHING",
            (project_id, voter_hash, choice),
        )


def vote_tally(project_id: int) -> dict[str, int]:
    with _conn() as c:
        rows = c.execute(
            "SELECT choice, COUNT(*) n FROM votes WHERE project_id = ? GROUP BY choice",
            (project_id,),
        ).fetchall()
    tally = {"support": 0, "oppose": 0}
    for r in rows:
        tally[r["choice"]] = r["n"]
    return tally


def record_feedback(project_id: int, phone_hash: str, lang: str,
                    english: str, sentiment: str, theme: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO feedback (project_id, phone_hash, lang, english, sentiment, theme) "
            "VALUES (?,?,?,?,?,?)",
            (project_id, phone_hash, lang, english, sentiment, theme),
        )


def list_feedback(project_id: int) -> list[sqlite3.Row]:
    with _conn() as c:
        return c.execute(
            "SELECT * FROM feedback WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()
