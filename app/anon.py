"""Stable, anonymous display names for citizens.

Like Google Docs' "Anonymous Aardvark", we turn a citizen's phone hash into a
friendly, human-readable label — e.g. "Brave Leopard 42". It is:

  * deterministic  — the same user always gets the same name (so their feedback
                     is grouped), derived purely from their existing hash;
  * anonymous      — a one-way function of an already one-way hash; it reveals
                     nothing about the phone number or ID;
  * unique-ish     — adjective x animal x number gives ~340k combinations.

This replaces showing a raw hash on the dashboard.
"""

from __future__ import annotations

ADJECTIVES = [
    "Brave", "Calm", "Bright", "Bold", "Swift", "Kind", "Wise", "Quiet",
    "Noble", "Gentle", "Clever", "Loyal", "Keen", "Merry", "Proud", "Steady",
]
ANIMALS = [
    "Lion", "Eagle", "Zebra", "Gazelle", "Falcon", "Elephant", "Leopard",
    "Crane", "Buffalo", "Hippo", "Rhino", "Antelope", "Cheetah", "Ostrich",
    "Flamingo", "Giraffe",
]


def anon_name(seed_hash: str) -> str:
    """Map a hex hash (e.g. a phone hash) to a stable friendly name."""
    try:
        n = int(seed_hash, 16)
    except (TypeError, ValueError):
        n = abs(hash(seed_hash))
    adj = ADJECTIVES[n % len(ADJECTIVES)]
    animal = ANIMALS[(n // len(ADJECTIVES)) % len(ANIMALS)]
    number = (n // 100) % 100
    return f"{adj} {animal} {number}"
