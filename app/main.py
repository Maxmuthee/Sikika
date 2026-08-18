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
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from ai import aggregate_feedback, answer_sms, translate_feedback
from ai.core import FeedbackAnalysis

from . import store
from . import ussd as ussd_flow  # aliased: the /ussd route function must not shadow the module
from .anon import anon_name
from .hashing import hash_phone
from .notify import bill_link, deliver, notify_new_project, send_sms

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sikika")

app = FastAPI(title="Sikika", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    store.init_db()


_STATIC = Path(__file__).resolve().parent / "static"
# The single dashboard is the React app (dashboard/sikika-app). In production we
# serve its built output; in dev the app runs on Vite (port 5173) and proxies /api here.
_DIST = Path(__file__).resolve().parents[1] / "dashboard" / "sikika-app" / "dist"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "sikika"}


@app.get("/")
def home() -> FileResponse:
    """Serve the React single-page app (landing + county dashboard)."""
    return FileResponse(_DIST / "index.html")


@app.get("/simulator")
def simulator() -> FileResponse:
    """Feature-phone USSD simulator — drives /ussd offline for live demos."""
    return FileResponse(_STATIC / "simulator.html")


@app.get("/bill/{project_id}", response_class=HTMLResponse)
def bill_page(project_id: int) -> str:
    """Mobile-friendly bill/project page — where an SMS link lands a smartphone user."""
    p = store.get_project(project_id)
    if p is None:
        return "<h1>Not found</h1>"

    def esc(s: str) -> str:
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    langs = [("Kiswahili", "sw"), ("Gikuyu", "ki"), ("English", "en")]
    blocks = ""
    for label, code in langs:
        tr = store.get_translation(project_id, code)
        if tr:
            blocks += (
                f"<div class='lang'><h3>{label}</h3>"
                f"<p><b>{esc(tr['civic_education'])}</b></p>"
                f"<p class='muted'>{esc(tr['data_summary'])}</p></div>"
            )
    src = p["source_url"]
    src_btn = (f"<a class='btn' href='{esc(src)}' target='_blank' rel='noopener'>"
               f"Read the full official document &rarr;</a>") if src else ""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(p['name_en'])} — Sikika</title>
<style>
 body{{margin:0;background:#f6f7f9;color:#1a1d21;font:16px/1.6 system-ui,sans-serif}}
 .wrap{{max-width:680px;margin:0 auto;padding:20px}}
 header{{background:#0f766e;color:#fff;padding:20px}}
 header .w{{max-width:680px;margin:0 auto}} h1{{margin:.2em 0;font-size:22px}}
 .badge{{display:inline-block;background:rgba(255,255,255,.2);padding:2px 10px;border-radius:999px;font-size:13px}}
 .lang{{background:#fff;border:1px solid #e4e7eb;border-radius:12px;padding:14px 16px;margin:14px 0}}
 .lang h3{{margin:.1em 0;color:#0b5a54;font-size:15px}} .muted{{color:#5b6470}}
 .btn{{display:inline-block;background:#0f766e;color:#fff;text-decoration:none;padding:12px 18px;border-radius:10px;margin:8px 0;font-weight:600}}
 details{{background:#fff;border:1px solid #e4e7eb;border-radius:12px;padding:12px 16px;margin:14px 0}}
 summary{{cursor:pointer;font-weight:600}} .src{{color:#5b6470;font-size:14px;white-space:pre-wrap}}
 footer{{color:#5b6470;font-size:13px;text-align:center;padding:20px}}
</style></head><body>
<header><div class="w"><span class="badge">{esc(p['ward'])} &middot; {esc(p['status'])}</span>
<h1>{esc(p['name_en'])}</h1></div></header>
<div class="wrap">
 {blocks}
 {src_btn}
 <details><summary>Official source text</summary><p class="src">{esc(p['raw_text'])}</p></details>
</div>
<footer>Sikika &middot; dial *384*7030# on any phone &middot; <a href="/">county dashboard</a></footer>
</body></html>"""


@app.get("/api/projects")
def api_projects() -> dict:
    """Tracked (Agriculture & Livestock) bills with live vote tallies + feedback
    counts. County-wide bills appear once (they surface in every sub-county)."""
    out = []
    seen: set[int] = set()
    for ward in ussd_flow.WARDS:
        for p in store.list_projects(ward):
            if p["id"] in seen:
                continue
            seen.add(p["id"])
            out.append({
                "id": p["id"],
                "name": p["name_en"],
                "ward": store.display_ward(p),
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


@app.get("/api/subcounties")
def api_subcounties() -> dict:
    """All Nakuru County sub-counties (canonical list) for dashboard filters."""
    from .wards import WARDS_BY_SUBCOUNTY
    return {"subcounties": list(WARDS_BY_SUBCOUNTY)}


def _ago(ts) -> str:
    """Human 'x ago' from a stored UTC timestamp (SQLite text or PG datetime)."""
    if not ts:
        return ""
    if isinstance(ts, str):
        try:
            dt = datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return ""
    else:
        dt = ts if getattr(ts, "tzinfo", None) else ts.replace(tzinfo=timezone.utc)
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


@app.get("/api/activity")
def api_activity() -> dict:
    """Live recent citizen activity for the landing-page status panel."""
    return {
        "activity": [
            {"kind": r["kind"], "area": r["area"], "ago": _ago(r["at"])}
            for r in store.recent_activity(4)
        ]
    }


def _to_date(ts):
    """Date part of a stored UTC timestamp (SQLite text or PG datetime)."""
    if not ts:
        return None
    if isinstance(ts, str):
        try:
            return datetime.strptime(ts[:10], "%Y-%m-%d").date()
        except ValueError:
            return None
    return ts.date() if hasattr(ts, "date") else None


def _engagement(days: int = 7) -> list[dict]:
    """Real daily citizen-activity counts for the last `days` days."""
    today = datetime.now(timezone.utc).date()
    buckets = {today - timedelta(days=i): 0 for i in range(days)}
    for ts in store.activity_timestamps():
        d = _to_date(ts)
        if d in buckets:
            buckets[d] += 1
    return [
        {"label": d.strftime("%a"), "value": buckets[d]}
        for d in sorted(buckets)  # oldest -> newest
    ]


# Fixed civic pipeline; the *current* stage is derived from a bill's real status.
_STATUS_STAGE = {"Proposed": 1, "Bill": 2, "Ongoing": 4}


def _featured_bill(ward: str | None = None) -> dict | None:
    """The most-engaged tracked bill (votes + feedback) for a sub-county (or
    county-wide when `ward` is None), with live tallies and AI brief."""
    projects = store.all_projects() if ward is None else store.list_projects(ward)
    if not projects:
        return None

    def engagement(p) -> int:
        t = store.vote_tally(p["id"])
        return t["support"] + t["oppose"] + len(store.list_feedback(p["id"]))

    p = max(projects, key=engagement)
    tally = store.vote_tally(p["id"])
    total = tally["support"] + tally["oppose"]
    fb = len(store.list_feedback(p["id"]))
    tr = store.get_translation(p["id"], "en")
    insight = ((tr["data_summary"] or tr["civic_education"]) if tr else "") or ""
    return {
        "id": p["id"],
        "title": (tr["project_name"] if tr and tr["project_name"] else p["name_en"]),
        "ward": store.display_ward(p),
        "status": p["status"],
        "support_pct": round(tally["support"] / total * 100) if total else 0,
        "oppose_pct": round(tally["oppose"] / total * 100) if total else 0,
        "votes_total": total,
        "participants": total + fb,
        "ai_insight": insight[:240],
        # Which pipeline stage is live, so the timeline reflects the real bill.
        "stage": _STATUS_STAGE.get(p["status"], 1),
    }


@app.get("/api/dashboard-stats")
def api_dashboard_stats(ward: str | None = None) -> dict:
    """Live figures + latest anonymised feedback for the React dashboard.

    Pass ?ward=<sub-county> to scope the bill list and featured bill to that
    area (county-wide bills are included in every area); untracked sectors are
    never shown. SMS/registration counts stay global.
    """
    votes = store.total_votes()
    regs = store.count_registrations()
    projects = store.all_projects() if ward is None else store.list_projects(ward)
    bills = []
    for p in projects:
        t = store.vote_tally(p["id"])
        bills.append({
            "id": p["id"],
            "name": p["name_en"],
            "ward": store.display_ward(p),
            "status": p["status"],
            "support": t["support"],
            "oppose": t["oppose"],
            "votes_total": t["support"] + t["oppose"],
            "feedback_count": len(store.list_feedback(p["id"])),
        })
    return {
        "sms_total": store.sms_count(),
        "votes_total": votes,
        "bills_tracked": len(projects),
        "registrations": regs,
        "participation_pct": round(min(100.0, votes / regs * 100), 1) if regs else 0.0,
        "featured": _featured_bill(ward),
        "bills": bills,
        "engagement": _engagement(7),
        "feedback": [
            {
                "name": anon_name(r["phone_hash"]),
                "sentiment": r["sentiment"],
                "theme": r["theme"],
                "text": r["english"],
            }
            for r in store.recent_feedback(6)
        ],
    }


# --- Inbound SMS as feedback -------------------------------------------------
# Shared Africa's Talking gateway (shortcode 20880). Messages that reach us are
# prefixed with the gateway keyword and our project tag, e.g. "kamilimu sikika
# <the citizen's actual message>". We strip that prefix before processing.
SMS_KEYWORD = "kamilimu"
SMS_PROJECT_TAG = "sikika"


def _strip_keyword(text: str) -> str:
    """Remove a leading 'kamilimu' (+ optional 'sikika') routing prefix."""
    t = (text or "").strip()
    for tag in (SMS_KEYWORD, SMS_PROJECT_TAG):
        if t.lower().startswith(tag):
            t = t[len(tag):].strip()
    return t


def _process_inbound(sender: str, body: str) -> str:
    """Core two-way SMS pipeline: store, answer via AI/commands, reply, store.

    Default: the message is a QUESTION -> the AI answers, grounded in the current
    projects/bills, in the citizen's language, with conversation memory.
    Commands: MAONI <text> (submit feedback), MSAADA/HELP (help).
    """
    body = (body or "").strip()
    phone_hash = hash_phone(sender)
    reg = store.get_registration(phone_hash)
    lang_hint = reg["lang"] if reg else None

    # History BEFORE storing the current inbound message.
    history = store.sms_history_for_ai(phone_hash)
    store.add_sms(phone_hash, sender, "in", body)

    reply = _handle_sms(body, phone_hash, sender, reg, lang_hint, history)
    reply = reply[:480]  # keep to a few SMS segments
    store.add_sms(phone_hash, sender, "out", reply)
    send_sms(sender, reply)
    return reply


@app.post("/sms")
def inbound_sms(
    from_: str = Form(..., alias="from"),
    text: str = Form(...),
    to: str = Form(default=""),
) -> dict:
    """Direct Africa's Talking inbound-SMS callback (dedicated shortcode / sandbox)."""
    return {"reply": _process_inbound(from_, _strip_keyword(text))}


@app.post("/sms/kamilimu")
async def inbound_sms_kamilimu(request: Request) -> dict:
    """Production callback for the SHARED KamiLimu gateway (shortcode 20880).

    Tolerant of payload shape: accepts form-encoded (Africa's Talking default) or
    JSON, and pulls the sender/text from the common field names. The full raw
    payload is logged so the exact gateway format is visible during live testing.
    Register this URL with the gateway operator:  https://<host>/sms/kamilimu
    """
    ctype = request.headers.get("content-type", "")
    if "application/json" in ctype:
        data = dict(await request.json())
    else:
        data = dict(await request.form())
    log.info("KamiLimu inbound payload: %s", data)

    sender = str(
        data.get("from") or data.get("msisdn") or data.get("phoneNumber")
        or data.get("sender") or ""
    ).strip()
    raw = str(
        data.get("text") or data.get("message") or data.get("content") or ""
    ).strip()
    if not sender or not raw:
        return {"error": "missing sender or text", "received": data}

    reply = _process_inbound(sender, _strip_keyword(raw))
    # Return the reply too, in case the gateway relays HTTP responses back to the sender.
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
    base = tr["sms_alert"] if tr else f"Sikika: {project['name_en']} - dial *384*7030#."
    msg = f"{base}\nSoma: {bill_link(project)}"
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
        # Individual feedback shown under an anonymous, stable display name —
        # never the hash. Same citizen -> same name (grouped), unlinkable to ID.
        "feedback": [
            {
                "name": anon_name(r["phone_hash"]),
                "sentiment": r["sentiment"],
                "theme": r["theme"],
                "text": r["english"],
            }
            for r in rows
        ],
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
                "Tuma 'MAONI <ujumbe>' kutoa maoni. Piga *384*7030#.")

    # MAONI <text> / FEEDBACK <text> -> capture feedback
    if up.startswith(("MAONI", "FEEDBACK")):
        fb = body.split(" ", 1)[1].strip() if " " in body else ""
        if not fb:
            return "Sikika: Andika 'MAONI' kisha maoni yako. / Write 'MAONI' then your feedback."
        sub = reg["sub_county"] if reg else None
        project = (store.latest_project_in(sub) if sub else None) or (
            store.all_projects()[-1] if store.all_projects() else None)
        if project is None:
            return ("Sikika: Hakuna miswada inayofanya kazi kwa sasa. "
                    "/ There are no active bills right now.")
        if not ussd_flow.participation_open(project["status"]):
            return ("Sikika: Ushiriki kwa mswada huu umefungwa. "
                    "/ Participation for this bill is closed.")
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
        return ("Sikika: Samahani, siwezi kujibu sasa. Piga *384*7030# au uliza tena baadaye. "
                "/ Sorry, I can't answer right now. Dial *384*7030# or try again later.")


def _projects_context() -> str:
    """Compact fact sheet of all tracked bills for the SMS assistant."""
    lines = []
    for p in store.all_projects():
        tr = store.get_translation(p["id"], "en")
        loc = store.display_ward(p)
        if tr:
            lines.append(f"- #{p['id']} {tr['project_name']} ({loc}): "
                         f"{tr['civic_education']} {tr['data_summary']}")
        else:
            lines.append(f"- #{p['id']} {p['name_en']} ({loc})")
    return "\n".join(lines)


# --- Serve the built React SPA (must stay LAST so it can't shadow API routes) -
if (_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str) -> FileResponse:
    """Serve real dist files (images, favicon) or fall back to the SPA shell.

    Registered last, GET-only, so it never intercepts the API or POST webhooks;
    client-side routes like /dashboard resolve to index.html and let React route.
    """
    candidate = (_DIST / full_path).resolve()
    if candidate.is_file() and _DIST.resolve() in candidate.parents:
        return FileResponse(candidate)
    return FileResponse(_DIST / "index.html")
