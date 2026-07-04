"""Phone-number anonymisation.

Sikika never stores a phone number. On first contact the number is hashed with
SHA-256 (plus a deployment secret so hashes are not reversible via a rainbow
table of all Kenyan MSISDNs) and only the hash is persisted. Same number ->
same hash, so a citizen keeps one ward profile without being identifiable.
"""

import hashlib
import os

# Set SIKIKA_HASH_SALT in the environment for production. The default is only
# for local demos — a shared salt across deployments weakens the guarantee.
_SALT = os.getenv("SIKIKA_HASH_SALT", "sikika-local-dev-salt")


def hash_phone(phone_number: str) -> str:
    """Return a stable, non-reversible hash of a phone number."""
    normalised = phone_number.strip().replace(" ", "")
    digest = hashlib.sha256((_SALT + normalised).encode("utf-8")).hexdigest()
    return digest


def hash_id(id_number: str) -> str:
    """Non-reversible hash of a national ID number.

    Stored (never the raw ID) to enforce one registration per person — the ID
    is only ever compared as a hash, never displayed or reversed.
    """
    normalised = id_number.strip().replace(" ", "")
    return hashlib.sha256((_SALT + "id:" + normalised).encode("utf-8")).hexdigest()


def vote_nullifier(id_number: str) -> str:
    """A vote-scoped, non-reversible hash of a national ID.

    Distinct from hash_id() (different domain prefix), so the value stored with
    a vote cannot be directly joined back to the registration's id_hash — a
    vote is not linkable to the registered phone by a plain DB query. Used to
    enforce one vote per person per project.
    """
    normalised = id_number.strip().replace(" ", "")
    return hashlib.sha256((_SALT + "vote:" + normalised).encode("utf-8")).hexdigest()
