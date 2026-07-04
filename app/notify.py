"""Outbound SMS alerts to registered citizens.

When a new project/bill is published for a sub-county, every citizen registered
in that sub-county gets the AI-simplified SMS alert in THEIR language. This is
the payoff of signup: the phone number retained at registration is used here,
solely to deliver the alert.
"""

from __future__ import annotations

import logging

from . import store
from .hashing import hash_phone

log = logging.getLogger("sikika.sms")


def send_sms(to: str, message: str) -> None:
    """Deliver one SMS. Stub — wire to Africa's Talking SMS API for real sends."""
    log.info("SMS -> %s | %s", to, message)


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
    recipients = store.registrations_in(sub)
    sent = []
    for r in recipients:
        tr = store.get_translation(project_id, r["lang"] or "sw")
        message = tr["sms_alert"] if tr else f"Sikika: {project['name_en']} - dial *384#."
        deliver(r["phone_number"], message)
        sent.append({"lang": r["lang"], "ward": r["ward"]})

    return {
        "project": project["name_en"],
        "sub_county": sub,
        "recipients": len(sent),
        "sent": sent,
    }
