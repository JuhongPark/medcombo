"""Safety-language checks for consumer-facing medication text."""

from __future__ import annotations

import re


PROHIBITED_PATTERNS = (
    re.compile(r"\bstop taking\b", re.IGNORECASE),
    re.compile(r"\bstart taking\b", re.IGNORECASE),
    re.compile(r"\bchange how you take\b(?!.*pharmacist|.*clinician|.*doctor)", re.IGNORECASE),
    re.compile(r"\bsafe to take\b", re.IGNORECASE),
    re.compile(r"\bunsafe\b", re.IGNORECASE),
    re.compile(r"\bdo not take\b", re.IGNORECASE),
    re.compile(r"\byou should take\b", re.IGNORECASE),
)


def find_prohibited_phrases(text: str) -> tuple[str, ...]:
    matches: list[str] = []
    for pattern in PROHIBITED_PATTERNS:
        match = pattern.search(text)
        if match:
            matches.append(match.group(0))
    return tuple(matches)


def is_consumer_safe_text(text: str) -> bool:
    return not find_prohibited_phrases(text)


def require_consumer_safe_text(text: str) -> str:
    matches = find_prohibited_phrases(text)
    if matches:
        joined = ", ".join(sorted(set(matches)))
        raise ValueError(f"Consumer-facing text contains prohibited medication language: {joined}")
    return text
