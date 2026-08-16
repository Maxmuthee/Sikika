"""Outbound SMS alerts to registered citizens.

When a new project/bill is published for a sub-county, every citizen registered
in that sub-county gets the AI-simplified SMS alert in THEIR language. This is
the payoff of signup: the phone number retained at registration is used here,
solely to deliver the alert.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

from . import store
from .hashing import hash_phone

log = logging.getLogger("sikika.sms")

# Africa's Talking config. If unset, SMS is logged only (local simulator still
# works). Set AT_USERNAME=sandbox + AT_API_KEY=<sandbox key> to send for real.
AT_USERNAME = os.getenv("AT_USERNAME")
AT_API_KEY = os.getenv("AT_API_KEY")
AT_SENDER = os.getenv("AT_SENDER")  # optional short code / sender id (not in sandbox)

# Public base URL used to build clickable bill links in SMS (smartphone users
# can tap through to read the full bill). Set to your domain in production.
PUBLIC_URL = os.getenv("SIKIKA_PUBLIC_URL", "http://localhost:8000").rstrip("/")


def bill_link(project) -> str:
    """Link to the official source document directly; fall back to Sikika's own
    bill page only when a project has no source URL."""
    src = project["source_url"] if "source_url" in project.keys() else None
    return src or f"{PUBLIC_URL}/bill/{project['id']}"


@lru_cache(maxsize=1)
def _at_sms():
    import africastalking

    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    return africastalking.SMS


def send_sms(to: str, message: str) -> None:
    """Deliver one SMS via Africa's Talking when configured, else log (local demo)."""
    if AT_USERNAME and AT_API_KEY:
        try:
            kwargs = {"sender_id": AT_SENDER} if AT_SENDER else {}
            _at_sms().send(message, [to], **kwargs)
            log.info("AT SMS -> %s | %s", to, message)
            return
        except Exception as e:  # network/creds/package issue — don't break the flow
            log.warning("AT SMS send failed (%s); logging instead", e)
    log.info("SMS(stub) -> %s | %s", to, message)


def deliver(phone_number: str, message: str) -> None:
    """Send an SMS and record it in the citizen's Sikika thread."""
    send_sms(phone_number, message)
    store.add_sms(hash_phone(phone_number), phone_number, "out", message)


def notify_new_project(project_id: int) -> dict:
    """Alert every registered citizen in the project's sub-county, in their language."""
    project = store.get_project(project_id)
    if project is None:
        return {"error": "unknown project"}

    sub = project["ward"]
    link = bill_link(project)
    recipients = store.registrations_in(sub)
    sent = []
    for r in recipients:
        tr = store.get_translation(project_id, r["lang"] or "sw")
        base = tr["sms_alert"] if tr else f"Sikika: {project['name_en']} - dial *384*7030#."
        message = f"{base}\nSoma: {link}"
        deliver(r["phone_number"], message)
        sent.append({"lang": r["lang"], "ward": r["ward"]})

    return {
        "project": project["name_en"],
        "sub_county": sub,
        "recipients": len(sent),
        "sent": sent,
    }
