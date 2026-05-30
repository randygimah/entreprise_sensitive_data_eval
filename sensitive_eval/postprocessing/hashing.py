"""SHA-256 hashing for deduplication reporting"""

import hashlib


def hash_value(raw_value: str) -> str:
    """Return a deterministic SHA-256 hash for a raw sensitive value."""
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()
