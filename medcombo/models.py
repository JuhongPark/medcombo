"""Core data models for MedCombo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MedicationInput:
    raw_text: str
    input_source: str = "manual"
    user_notes: str = ""
    created_at: str = ""


@dataclass(frozen=True)
class Ingredient:
    ingredient_id: str
    name: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class DrugClass:
    class_id: str
    name: str
    class_source: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class MedicationRecord:
    medication_id: str
    display_name: str
    normalized_name: str
    rxcui: str
    aliases: tuple[str, ...]
    active_ingredients: tuple[str, ...]
    drug_classes: tuple[str, ...]
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class NormalizedMedication:
    input_text: str
    medication_id: str | None
    display_name: str
    normalized_name: str
    rxcui: str
    match_status: str
    match_confidence: float
    active_ingredients: tuple[Ingredient, ...]
    drug_classes: tuple[DrugClass, ...]
    source_ids: tuple[str, ...]
    candidate_ids: tuple[str, ...] = ()
    candidate_names: tuple[str, ...] = ()

    @property
    def is_matched(self) -> bool:
        return self.match_status == "matched" and self.medication_id is not None


@dataclass(frozen=True)
class SafetySignal:
    signal_id: str
    signal_type: str
    review_priority: str
    medication_ids: tuple[str, ...]
    ingredient_ids: tuple[str, ...]
    plain_language_explanation: str
    professional_question: str
    source_ids: tuple[str, ...]
    rule_id: str
    data_version: str
    confidence: float


@dataclass(frozen=True)
class SourceReference:
    source_id: str
    title: str
    publisher: str
    url: str
    retrieved_or_version_date: str
    source_type: str


@dataclass(frozen=True)
class ReviewResult:
    data_version: str
    medications: tuple[NormalizedMedication, ...]
    signals: tuple[SafetySignal, ...]
    sources: tuple[SourceReference, ...]


def to_plain_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, tuple):
        return [to_plain_dict(item) for item in value]
    if isinstance(value, list):
        return [to_plain_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain_dict(item) for key, item in value.items()}
    return value
