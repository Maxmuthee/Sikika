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

from ai import aggregate_feedback, answer_sms, translate_feedback
from ai.core import FeedbackAnalysis

from . import store
from . import ussd as ussd_flow  # aliased: the /ussd route function must not shadow the module
from .hashing import hash_phone
from .notify import deliver, notify_new_project, send_sms

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
    """A two-way SMS assistant for offline citizens.

    Default: the message is a QUESTION -> Claude answers, grounded in the
    current projects/bills, in the citizen's language, with conversation memory.
    Commands: SIKIZA <id> (listen by voice), MAONI <text> (submit feedback),
    MSAADA/HELP (help).
    """
    body = text.strip()
    phone_hash = hash_phone(from_)
    reg = store.get_registration(phone_hash)
    lang_hint = reg["lang"] if reg else None

    # History BEFORE storing the current inbound message.
    history = store.sms_history_for_ai(phone_hash)
    store.add_sms(phone_hash, from_, "in", body)

    reply = _handle_sms(body, phone_hash, from_, reg, lang_hint, history)
    reply = reply[:480]  # keep to a few SMS segments
    store.add_sms(phone_hash, from_, "out", reply)
    send_sms(from_, reply)
    return {"reply": reply}


@app.get("/api/sms")
def api_sms(phone: str) -> dict:
    """The SMS thread for a phone (used by the simulator)."""
    rows = store.sms_thread(hash_phone(phone))
    return {"messages": [
        {"direction": r["direction"], "body": r["body"], "at": r["created_at"]}
        for r in rows
    ]}


@app.post("/api/demo/notify")
def demo_notify(phone: str, project_id: int = 1) -> dict:
    """Demo helper: push a project's SMS alert straight to one phone's thread."""
    project = store.get_project(project_id)
    if project is None:
        return {"error": "unknown project"}
    reg = store.get_registration(hash_phone(phone))
    lang = reg["lang"] if reg else "sw"
    tr = store.get_translation(project_id, lang)
    msg = tr["sms_alert"] if tr else f"Sikika: {project['name_en']} - dial *384#."
    deliver(phone, msg)
    return {"sent": msg}


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


# --- SMS routing -------------------------------------------------------------
def _handle_sms(body, phone_hash, phone, reg, lang_hint, history) -> str:
    up = body.upper()

    # HELP / MSAADA
    if up in ("HELP", "MSAADA", "SIKIKA"):
        return ("Sikika: Uliza swali lolote kuhusu bajeti au miswada ya Nakuru. "
                "Tuma 'SIKIZA <namba>' kusikia kwa sauti. Piga *384#.")

    # SIKIZA <project_id> -> voice/IVR callback (simulated)
    if up.startswith(("SIKIZA", "SIKILIZA", "LISTEN")):
        parts = body.split()
        pid = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        project = store.get_project(pid) if pid else None
        if project is None:
            return "Sikika: Tuma 'SIKIZA <namba ya mradi>'. / Send 'SIKIZA <project number>'."
        return (f"Sikika: Tunakupigia simu kusoma '{project['name_en']}' kwa sauti. "
                f"/ We will call you to read '{project['name_en']}' aloud.")

    # MAONI <text> / FEEDBACK <text> -> capture feedback
    if up.startswith(("MAONI", "FEEDBACK")):
        fb = body.split(" ", 1)[1].strip() if " " in body else ""
        if not fb:
            return "Sikika: Andika 'MAONI' kisha maoni yako. / Write 'MAONI' then your feedback."
        sub = reg["sub_county"] if reg else None
        project = (store.latest_project_in(sub) if sub else None) or (
            store.all_projects()[-1] if store.all_projects() else None)
        if project is None:
            return "Sikika: Hakuna mradi kwa sasa. / No project available now."
        try:
            a = translate_feedback(fb, lang_hint or "sw")
            store.record_feedback(project["id"], phone_hash, lang_hint or "sw",
                                  a.english, a.sentiment, a.theme)
            return ("Sikika: Maoni yako kuhusu '" + project["name_en"] +
                    "' yamepokelewa. Asante!")
        except Exception:  # AI unavailable — still acknowledge
            return "Sikika: Maoni yako yamepokelewa. Asante!"

    # Default: an open question -> AI answers, grounded in project facts.
    try:
        return answer_sms(body, history, _projects_context(), lang_hint)
    except Exception as e:  # e.g. no API key / network — fail gracefully
        log.warning("SMS AI answer failed: %s", e)
        return ("Sikika: Samahani, siwezi kujibu sasa. Piga *384# au uliza tena baadaye. "
                "/ Sorry, I can't answer right now. Dial *384# or try again later.")


def _projects_context() -> str:
    """Compact fact sheet of all current projects/bills for the SMS assistant."""
    lines = []
    for p in store.all_projects():
        tr = store.get_translation(p["id"], "en")
        if tr:
            lines.append(f"- #{p['id']} {tr['project_name']} ({p['ward']}): "
                         f"{tr['civic_education']} {tr['data_summary']}")
        else:
            lines.append(f"- #{p['id']} {p['name_en']} ({p['ward']})")
    return "\n".join(lines)
