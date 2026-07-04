"""Sikika FastAPI app — Africa's Talking (sandbox) webhooks + county API.

Endpoints:
  POST /ussd            -> USSD state machine (plain-text CON/END replies)
  POST /sms             -> inbound SMS treated as citizen feedback (AI-processed)
  GET  /county/{id}/brief -> aggregated county brief (feeds the dashboard)
  GET  /health          -> liveness

Run:  uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging

from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, PlainTextResponse

from ai import aggregate_feedback, translate_feedback
from ai.core import FeedbackAnalysis

from . import store
from . import ussd as ussd_flow  # aliased: the /ussd route function must not shadow the module
from .hashing import hash_phone
from .notify import notify_new_project, send_sms

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sikika")

app = FastAPI(title="Sikika", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    store.init_db()


_STATIC = Path(__file__).resolve().parent / "static"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "sikika"}


@app.get("/")
def dashboard() -> FileResponse:
    """County-official participation dashboard (static, self-contained)."""
    return FileResponse(_STATIC / "dashboard.html")


@app.get("/simulator")
def simulator() -> FileResponse:
    """Feature-phone USSD simulator — drives /ussd offline for live demos."""
    return FileResponse(_STATIC / "simulator.html")


@app.get("/api/projects")
def api_projects() -> dict:
    """All projects with live vote tallies + feedback counts (for the dashboard)."""
    out = []
    for ward in ussd_flow.WARDS:
        for p in store.list_projects(ward):
            out.append({
                "id": p["id"],
                "name": p["name_en"],
                "ward": p["ward"],
                "status": p["status"],
                "votes": store.vote_tally(p["id"]),
                "feedback_count": len(store.list_feedback(p["id"])),
            })
    return {"projects": out}


# --- USSD --------------------------------------------------------------------
@app.post("/ussd", response_class=PlainTextResponse)
def ussd(
    phoneNumber: str = Form(...),
    text: str = Form(default=""),
    sessionId: str = Form(default=""),
    serviceCode: str = Form(default=""),
) -> str:
    reply = ussd_flow.handle(phoneNumber, text)
    log.info("USSD %s text=%r -> %s", sessionId, text, reply.split(chr(10))[0])
    return reply


# --- Notifications: alert registered citizens about a new item ---------------
@app.post("/admin/notify/{project_id}")
def admin_notify(project_id: int) -> dict:
    """Send the project's SMS alert to every registered citizen in its sub-county."""
    return notify_new_project(project_id)


@app.get("/api/stats")
def api_stats() -> dict:
    return {"registrations": store.count_registrations()}


# --- Inbound SMS as feedback -------------------------------------------------
@app.post("/sms")
def inbound_sms(
    from_: str = Form(..., alias="from"),
    text: str = Form(...),
    to: str = Form(default=""),
) -> dict:
    """Treat an inbound SMS as feedback.

    Format:  "<project_id> <message>"  (project id optional; defaults to latest).
    The message is translated to English, PII-scrubbed, tagged, and stored
    against the SHA-256 hash of the sender — never the number.
    """
    project_id, message = _parse_sms(text)
    if project_id is None:
        send_sms(from_, "Sikika: tuma 'namba_ya_mradi ujumbe'. / send 'project_id message'.")
        return {"status": "no_project"}

    phone_hash = hash_phone(from_)
    profile = None
    # Use the citizen's known language as a translation hint if we have it.
    src_lang = _profile_lang(phone_hash) or "sw"

    analysis = translate_feedback(message, src_lang)  # AI Point 2
    store.record_feedback(
        project_id, phone_hash, src_lang,
        analysis.english, analysis.sentiment, analysis.theme,
    )
    send_sms(from_, "Sikika: Maoni yako yamepokelewa. Asante! / Your feedback was received. Thank you!")
    return {"status": "recorded", "sentiment": analysis.sentiment, "theme": analysis.theme}


# --- County-facing brief (feeds the dashboard) -------------------------------
@app.get("/county/{project_id}/brief")
def county_brief(project_id: int) -> dict:
    """Aggregate stored feedback + votes into a brief officials can't ignore."""
    project = store.get_project(project_id)
    if project is None:
        return {"error": "unknown project"}

    rows = store.list_feedback(project_id)
    tally = store.vote_tally(project_id)
    result: dict = {
        "project": project["name_en"],
        "ward": project["ward"],
        "votes": tally,
        "feedback_count": len(rows),
    }
    if rows:
        items = [
            FeedbackAnalysis(english=r["english"], sentiment=r["sentiment"], theme=r["theme"])
            for r in rows
        ]
        brief = aggregate_feedback(items)  # AI Point 4
        result["brief"] = brief.model_dump()
    return result


# --- helpers -----------------------------------------------------------------
def _parse_sms(text: str) -> tuple[int | None, str]:
    text = text.strip()
    head, _, rest = text.partition(" ")
    if head.isdigit() and rest:
        return int(head), rest.strip()
    # No leading project id: attach to the most recent project, if any.
    for ward in ussd_flow.WARDS:
        projects = store.list_projects(ward)
        if projects:
            return int(projects[-1]["id"]), text
    return None, text


def _profile_lang(phone_hash: str) -> str | None:
    with store._conn() as c:  # small read; fine for the demo
        row = c.execute(
            "SELECT lang FROM profiles WHERE phone_hash = ?", (phone_hash,)
        ).fetchone()
    return row["lang"] if row else None
