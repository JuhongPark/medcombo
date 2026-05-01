"""Text normalization helpers."""

from __future__ import annotations

import re


_NON_WORD = re.compile(r"[^a-z0-9]+")


def clean_key(value: str) -> str:
    lowered = value.casefold().strip()
    compact = _NON_WORD.sub(" ", lowered)
    return " ".join(compact.split())


def stable_id_part(value: str) -> str:
    cleaned = clean_key(value)
    return cleaned.replace(" ", "_") or "unknown"
