"""Persistence for Sikika — dual backend.

Uses PostgreSQL (e.g. Neon) when DATABASE_URL is set, otherwise a local SQLite
file. All application queries are written with '?' placeholders and are
translated to '%s' for PostgreSQL, so the rest of the app is backend-agnostic.

Tables:
  projects       -- a tabled budget item / bill (raw English source); carries a
                    `sector` label and a `county_wide` flag (see TRACKED_SECTORS)
  translations   -- AI-simplified content per project x language
  profiles       -- hashed phone -> ward/language (no personal data)
  registrations  -- one-time citizen signup (hashed ID, phone for delivery)
  votes          -- one support/oppose per person per project (vote nullifier)
  feedback       -- citizen feedback: English + PII-scrubbed + tagged
  sms            -- two-way SMS thread (notifications + AI Q&A)

Sector policy: Sikika monitors ONLY Agriculture & Livestock bills. Every public
query (dashboard, USSD, SMS routing, notifications, stats, AI context) filters
on TRACKED_SECTORS, so bills in other sectors (development, health,
infrastructure, explosives, finance, ...) are neither tracked nor shown.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

from dotenv import load_dotenv

load_dotenv()  # ensure DATABASE_URL from .env is honoured regardless of import order

DATABASE_URL = os.getenv("DATABASE_URL")          # set → PostgreSQL (Neon)
IS_PG = bool(DATABASE_URL)
DB_PATH = os.getenv("SIKIKA_DB", "sikika.db")     # used only when SQLite

if IS_PG:
    import psycopg  # noqa: F401
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool

    # A pool reuses connections — essential over a remote DB, where opening a
    # fresh TLS connection per query is far too slow. prepare_threshold=None
    # keeps us compatible with Neon's transaction pooler (PgBouncer).
    def _configure(conn):
        conn.autocommit = True  # avoid a separate COMMIT round-trip per query

    # check: validate (and transparently reconnect) each connection on checkout —
    # Neon closes idle connections, so a pooled one can be dead between requests
    # ("SSL connection has been closed unexpectedly"). max_lifetime recycles
    # connections proactively before Neon drops them.
    _pool = ConnectionPool(
        DATABASE_URL, min_size=1, max_size=5, open=False, configure=_configure,
        kwargs={"row_factory": dict_row, "prepare_threshold": None},
        check=ConnectionPool.check_connection,
        max_lifetime=300,
    )
    _pool.open()


class _DB:
    """Thin wrapper so the same '?'-style SQL runs on SQLite and PostgreSQL."""

    def __init__(self, raw):
        self._raw = raw

    def execute(self, sql: str, params=()):
        if IS_PG:
            sql = sql.replace("?", "%s")
        return self._raw.execute(sql, params)


@contextmanager
def _conn() -> Iterator[_DB]:
    if IS_PG:
        with _pool.connection() as raw:  # autocommit is on (see _configure)
            yield _DB(raw)
    else:
        raw = sqlite3.connect(DB_PATH)
        raw.row_factory = sqlite3.Row
        raw.execute("PRAGMA foreign_keys = ON")
        try:
            yield _DB(raw)
            raw.commit()
        finally:
            raw.close()


# --- Sector policy ----------------------------------------------------------
# Sikika tracks ONLY Agriculture & Livestock bills. Bills in any other sector
# (development, health, infrastructure, explosives, finance, constitutional
# affairs, water, ...) are excluded from every public query below.
TRACKED_SECTORS = ("Agriculture & Livestock",)

# Display label for bills that apply to Nakuru County as a whole.
COUNTY_WIDE_WARD = "Nakuru County"


def is_county_wide(project) -> bool:
    """True when a bill cuts across all sub-counties (Nakuru as a whole), so it
    must be visible/actionable in every sub-county's menu."""
    return "county_wide" in project.keys() and bool(project["county_wide"])


def display_ward(project) -> str:
    """Sub-county label shown to citizens; county-wide bills show the county."""
    return COUNTY_WIDE_WARD if is_county_wide(project) else project["ward"]


def is_tracked(project) -> bool:
    """True when a project belongs to a sector Sikika monitors."""
    sector = project["sector"] if "sector" in project.keys() else None
    return sector in TRACKED_SECTORS


def _tracked_placeholders() -> str:
    """'?' placeholders for the TRACKED_SECTORS IN-clause (backend-agnostic)."""
    return ", ".join("?" for _ in TRACKED_SECTORS)


def _ddl() -> list[str]:
    # Dialect-specific bits; the rest of the SQL is identical across backends.
    pk = "SERIAL PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ts = "TIMESTAMPTZ DEFAULT now()" if IS_PG else "TEXT DEFAULT (datetime('now'))"
    return [
        f"""CREATE TABLE IF NOT EXISTS projects (
                id {pk}, ward TEXT NOT NULL, name_en TEXT NOT NULL,
                raw_text TEXT NOT NULL, pdf_path TEXT, source_url TEXT,
                sector TEXT, county_wide INTEGER NOT NULL DEFAULT 0,
                status TEXT DEFAULT 'Proposed')""",
        """CREATE TABLE IF NOT EXISTS translations (
                project_id INTEGER NOT NULL, lang TEXT NOT NULL,
                project_name TEXT NOT NULL, sms_alert TEXT NOT NULL,
                civic_education TEXT NOT NULL, data_summary TEXT NOT NULL,
                PRIMARY KEY (project_id, lang))""",
        f"""CREATE TABLE IF NOT EXISTS profiles (
                phone_hash TEXT PRIMARY KEY, lang TEXT, sub_county TEXT,
                ward TEXT, created_at {ts})""",
        f"""CREATE TABLE IF NOT EXISTS registrations (
                phone_hash TEXT PRIMARY KEY, phone_number TEXT NOT NULL,
                id_hash TEXT NOT NULL UNIQUE, lang TEXT, sub_county TEXT,
                ward TEXT, created_at {ts})""",
        f"""CREATE TABLE IF NOT EXISTS votes (
                project_id INTEGER NOT NULL, voter_hash TEXT NOT NULL,
                choice TEXT NOT NULL CHECK (choice IN ('support','oppose')),
                created_at {ts}, PRIMARY KEY (project_id, voter_hash))""",
        f"""CREATE TABLE IF NOT EXISTS sms (
                id {pk}, phone_hash TEXT NOT NULL, phone_number TEXT,
                direction TEXT NOT NULL CHECK (direction IN ('in','out')),
                body TEXT NOT NULL, created_at {ts})""",
        f"""CREATE TABLE IF NOT EXISTS feedback (
                id {pk}, project_id INTEGER NOT NULL, phone_hash TEXT NOT NULL,
                lang TEXT, english TEXT, sentiment TEXT, theme TEXT,
                created_at {ts})""",
    ]


def init_db() -> None:
    with _conn() as c:
        for stmt in _ddl():
            c.execute(stmt)
        # Migration: add columns to older databases without dropping data.
        if IS_PG:
            c.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS source_url TEXT")
            c.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS sector TEXT")
            c.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS county_wide INTEGER NOT NULL DEFAULT 0")
        else:
            cols = [r["name"] for r in c.execute("PRAGMA table_info(projects)")]
            if "source_url" not in cols:
                c.execute("ALTER TABLE projects ADD COLUMN source_url TEXT")
            if "sector" not in cols:
                c.execute("ALTER TABLE projects ADD COLUMN sector TEXT")
            if "county_wide" not in cols:
                c.execute("ALTER TABLE projects ADD COLUMN county_wide INTEGER NOT NULL DEFAULT 0")
        # Backfill sector/county_wide for rows created before this migration, so
        # a deployed DB that only runs init_db() on startup is classified
        # correctly without a manual re-seed. Mirrors the entries in data/seed.py.
        _SECTOR_BY_NAME = {
            "Molo fertilizer subsidy": "Agriculture & Livestock",
            "Njoro water rehabilitation": "Water",
            "Naivasha roads upgrade": "Infrastructure",
            "Health facilities upgrade": "Health",
            "Rongai ward infrastructure": "Infrastructure",
            "The Explosives Bill 2026": "Mining & Explosives",
            "The Finance Bill 2026": "Finance",
            "Constitution (Amendment) Bill 2026": "Constitutional Affairs",
            "County Wards (Equitable Development) Bill 2024": "Development",
            "Digital Agricultural Information Bill 2026": "Agriculture & Livestock",
            "Livestock Protection & Sustainability Bill 2024": "Agriculture & Livestock",
            "Agriculture Produce (Minimum Returns) Bill 2025": "Agriculture & Livestock",
        }
        _COUNTY_WIDE_BY_NAME = {
            "The Explosives Bill 2026", "The Finance Bill 2026",
            "Constitution (Amendment) Bill 2026",
            "County Wards (Equitable Development) Bill 2024",
            "Digital Agricultural Information Bill 2026",
            "Livestock Protection & Sustainability Bill 2024",
            "Agriculture Produce (Minimum Returns) Bill 2025",
        }
        for name, sector in _SECTOR_BY_NAME.items():
            c.execute("UPDATE projects SET sector = ? WHERE name_en = ? AND sector IS NULL",
                      (sector, name))
        for name in _COUNTY_WIDE_BY_NAME:
            c.execute("UPDATE projects SET county_wide = 1 WHERE name_en = ? AND county_wide = 0",
                      (name,))


# --- projects & translations -------------------------------------------------
def upsert_project(ward: str, name_en: str, raw_text: str,
                   pdf_path: Optional[str] = None, status: str = "Proposed",
                   sector: Optional[str] = None, county_wide: int = 0) -> int:
    with _conn() as c:
        row = c.execute(
            "INSERT INTO projects (ward, name_en, raw_text, pdf_path, status, "
            "sector, county_wide) VALUES (?,?,?,?,?,?,?) RETURNING id",
            (ward, name_en, raw_text, pdf_path, status, sector, int(county_wide)),
        ).fetchone()
        return int(row["id"])


def get_or_create_project(ward: str, name_en: str, raw_text: str,
                          pdf_path: Optional[str] = None, status: str = "Proposed",
                          sector: Optional[str] = None, county_wide: int = 0) -> int:
    """Return the id of an existing (ward, name) project, or create it.

    Makes seeding idempotent — re-running init_db does not duplicate rows or
    disturb votes/feedback already recorded against a project. On an existing
    row we still refresh sector/county_wide so re-seeding migrates old data.
    """
    with _conn() as c:
        row = c.execute(
            "SELECT id FROM projects WHERE ward = ? AND name_en = ?", (ward, name_en)
        ).fetchone()
        if row:
            pid = int(row["id"])
            c.execute("UPDATE projects SET sector = ?, county_wide = ? WHERE id = ?",
                      (sector, int(county_wide), pid))
            return pid
        row = c.execute(
            "INSERT INTO projects (ward, name_en, raw_text, pdf_path, status, "
            "sector, county_wide) VALUES (?,?,?,?,?,?,?) RETURNING id",
            (ward, name_en, raw_text, pdf_path, status, sector, int(county_wide)),
        ).fetchone()
        return int(row["id"])


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


def set_source_url(project_id: int, source_url: Optional[str]) -> None:
    with _conn() as c:
        c.execute("UPDATE projects SET source_url = ? WHERE id = ?", (source_url, project_id))


def translation_exists(project_id: int, lang: str) -> bool:
    with _conn() as c:
        return c.execute(
            "SELECT 1 FROM translations WHERE project_id = ? AND lang = ?",
            (project_id, lang),
        ).fetchone() is not None


def list_projects(ward: str) -> list[sqlite3.Row]:
    """Tracked bills visible to a sub-county: its own bills plus every
    county-wide bill (a bill for Nakuru as a whole is actionable everywhere)."""
    with _conn() as c:
        return c.execute(
            f"SELECT * FROM projects WHERE sector IN ({_tracked_placeholders()}) "
            "AND (ward = ? OR county_wide = 1) ORDER BY id",
            (*TRACKED_SECTORS, ward),
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


def update_registration(phone_hash: str, lang: Optional[str] = None,
                        sub_county: Optional[str] = None, ward: Optional[str] = None) -> None:
    """Update a citizen's profile (language and/or home area)."""
    sets, vals = [], []
    if lang is not None:
        sets.append("lang = ?"); vals.append(lang)
    if sub_county is not None:
        sets.append("sub_county = ?"); vals.append(sub_county)
    if ward is not None:
        sets.append("ward = ?"); vals.append(ward)
    if not sets:
        return
    vals.append(phone_hash)
    with _conn() as c:
        c.execute(f"UPDATE registrations SET {', '.join(sets)} WHERE phone_hash = ?", vals)


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


# --- SMS thread --------------------------------------------------------------
def add_sms(phone_hash: str, phone_number: str, direction: str, body: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO sms (phone_hash, phone_number, direction, body) VALUES (?,?,?,?)",
            (phone_hash, phone_number, direction, body),
        )


def sms_thread(phone_hash: str, limit: int = 60) -> list[sqlite3.Row]:
    with _conn() as c:
        rows = c.execute(
            "SELECT direction, body, created_at FROM sms WHERE phone_hash = ? "
            "ORDER BY id DESC LIMIT ?", (phone_hash, limit),
        ).fetchall()
    return list(reversed(rows))


def sms_history_for_ai(phone_hash: str, limit: int = 6) -> list[tuple[str, str]]:
    """Recent (direction, body) pairs to give the AI conversation memory."""
    with _conn() as c:
        rows = c.execute(
            "SELECT direction, body FROM sms WHERE phone_hash = ? "
            "ORDER BY id DESC LIMIT ?", (phone_hash, limit),
        ).fetchall()
    return [(r["direction"], r["body"]) for r in reversed(rows)]


def all_projects() -> list[sqlite3.Row]:
    """Every tracked (Agriculture & Livestock) bill, oldest first. Untracked
    sectors never surface anywhere on the platform."""
    with _conn() as c:
        return c.execute(
            f"SELECT * FROM projects WHERE sector IN ({_tracked_placeholders()}) "
            "ORDER BY id",
            (*TRACKED_SECTORS,),
        ).fetchall()


def total_votes() -> int:
    """Votes cast on tracked bills only (untracked sectors aren't monitored)."""
    with _conn() as c:
        return int(c.execute(
            f"SELECT COUNT(*) n FROM votes v JOIN projects p ON p.id = v.project_id "
            f"WHERE p.sector IN ({_tracked_placeholders()})",
            (*TRACKED_SECTORS,),
        ).fetchone()["n"])


def sms_count() -> int:
    with _conn() as c:
        return int(c.execute("SELECT COUNT(*) n FROM sms").fetchone()["n"])


def recent_feedback(limit: int = 6) -> list[sqlite3.Row]:
    with _conn() as c:
        return c.execute(
            f"SELECT f.phone_hash, f.english, f.sentiment, f.theme "
            f"FROM feedback f JOIN projects p ON p.id = f.project_id "
            f"WHERE p.sector IN ({_tracked_placeholders()}) "
            f"ORDER BY f.id DESC LIMIT ?",
            (*TRACKED_SECTORS, limit),
        ).fetchall()


def recent_activity(limit: int = 5) -> list[sqlite3.Row]:
    """Newest citizen events — feedback & votes on tracked bills, registrations."""
    with _conn() as c:
        return c.execute(
            f"SELECT kind, area, at FROM ("
            f"  SELECT 'feedback' AS kind, r.sub_county AS area, f.created_at AS at "
            f"    FROM feedback f JOIN projects p ON p.id = f.project_id "
            f"    LEFT JOIN registrations r ON r.phone_hash = f.phone_hash "
            f"    WHERE p.sector IN ({_tracked_placeholders()}) "
            f"  UNION ALL "
            f"  SELECT 'registration' AS kind, sub_county AS area, created_at AS at FROM registrations "
            f"  UNION ALL "
            f"  SELECT 'vote' AS kind, CAST(NULL AS TEXT) AS area, v.created_at AS at "
            f"    FROM votes v JOIN projects p ON p.id = v.project_id "
            f"    WHERE p.sector IN ({_tracked_placeholders()}) "
            f") ORDER BY at DESC LIMIT ?",
            (*TRACKED_SECTORS, *TRACKED_SECTORS, limit),
        ).fetchall()


def activity_timestamps() -> list:
    """Citizen-event timestamps (feedback & votes on tracked bills, plus
    registrations) for the dashboard trend chart."""
    with _conn() as c:
        rows = c.execute(
            f"SELECT at FROM ("
            f"  SELECT v.created_at AS at FROM votes v "
            f"    JOIN projects p ON p.id = v.project_id "
            f"    WHERE p.sector IN ({_tracked_placeholders()}) "
            f"  UNION ALL SELECT f.created_at AS at FROM feedback f "
            f"    JOIN projects p ON p.id = f.project_id "
            f"    WHERE p.sector IN ({_tracked_placeholders()}) "
            f"  UNION ALL SELECT created_at AS at FROM registrations "
            f")",
            (*TRACKED_SECTORS, *TRACKED_SECTORS),
        ).fetchall()
    return [r["at"] for r in rows]


def latest_project_in(sub_county: str) -> Optional[sqlite3.Row]:
    """Newest tracked bill open to a sub-county (county-wide bills included)."""
    with _conn() as c:
        return c.execute(
            f"SELECT * FROM projects WHERE sector IN ({_tracked_placeholders()}) "
            "AND (ward = ? OR county_wide = 1) ORDER BY id DESC LIMIT 1",
            (*TRACKED_SECTORS, sub_county),
        ).fetchone()


def all_registrations() -> list[sqlite3.Row]:
    """Every registered citizen, used to alert about county-wide bills."""
    with _conn() as c:
        return c.execute(
            "SELECT phone_number, lang, ward FROM registrations ORDER BY ward"
        ).fetchall()
