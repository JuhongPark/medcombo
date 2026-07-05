"""Core data models for MedCombo."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class MedicationInput:
    raw_text: str
    input_source: str = "manual"
    user_notes: str = ""
    created_at: str = ""


@dataclass(frozen=True)
class ConsumerHealthContext:
    supplements: tuple[str, ...] = ()
    demographics: str = ""
    body_info: str = ""
    conditions: tuple[str, ...] = ()
    symptoms: tuple[str, ...] = ()
    no_information: tuple[str, ...] = ()

    @property
    def has_any_data(self) -> bool:
        return any(
            (
                self.supplements,
                self.demographics,
                self.body_info,
                self.conditions,
                self.symptoms,
                self.no_information,
            )
        )


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
class MedicationIntakeItem:
    raw_text: str
    source_type: str
    source_confidence: str
    normalized_medication: NormalizedMedication
    candidate_medications: tuple[str, ...]
    selected_medication_id: str | None
    match_status: str
    verification_status: str
    strength: str = ""
    dose: str = ""
    route: str = ""
    frequency: str = ""
    formulation: str = ""
    last_dose_taken: str = ""
    actual_use_notes: str = ""
    missing_fields: tuple[str, ...] = ()
    professional_review_questions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConversationQuestion:
    question_id: str
    item_index: int
    raw_text: str
    question_type: str
    field_name: str
    question_text: str
    rationale: str
    priority: int


@dataclass(frozen=True)
class AgentTurn:
    turn_id: str
    question_id: str
    item_index: int
    question_type: str
    question_text: str
    user_answer: str
    extracted_field: str
    extracted_value: str
    status: str


@dataclass(frozen=True)
class MedicationAgentSession:
    session_id: str
    intake_items: tuple[MedicationIntakeItem, ...]
    active_questions: tuple[ConversationQuestion, ...]
    answered_question_ids: tuple[str, ...] = ()
    turns: tuple[AgentTurn, ...] = ()
    completed: bool = False


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
    evidence_type: str = ""
    clinical_concern: str = ""
    evidence_summary: str = ""
    patient_specific_modifiers: tuple[str, ...] = ()


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
    context: ConsumerHealthContext = field(default_factory=ConsumerHealthContext)


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
