"""Evidence records used by traceable medication review rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InteractionEvidence:
    interaction_id: str
    ingredient_ids: tuple[str, ...]
    review_priority: str
    evidence_type: str
    clinical_concern: str
    evidence_summary: str
    patient_specific_modifiers: tuple[str, ...]
    plain_language_explanation: str
    professional_question: str
    source_ids: tuple[str, ...]

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "InteractionEvidence":
        missing_fields = [
            field_name
            for field_name in REQUIRED_INTERACTION_FIELDS
            if not row.get(field_name)
        ]
        if missing_fields:
            joined = ", ".join(missing_fields)
            interaction_id = row.get("interaction_id", "unknown")
            raise ValueError(f"Interaction evidence {interaction_id} is missing required fields: {joined}")

        ingredient_ids = tuple(row["ingredient_ids"])
        source_ids = tuple(row["source_ids"])
        patient_specific_modifiers = tuple(row["patient_specific_modifiers"])
        if len(ingredient_ids) < 2:
            raise ValueError(f"Interaction evidence {row['interaction_id']} needs at least two ingredients")
        if not source_ids:
            raise ValueError(f"Interaction evidence {row['interaction_id']} needs at least one source")
        if not patient_specific_modifiers:
            raise ValueError(
                f"Interaction evidence {row['interaction_id']} needs patient-specific modifiers"
            )

        return cls(
            interaction_id=row["interaction_id"],
            ingredient_ids=ingredient_ids,
            review_priority=row["review_priority"],
            evidence_type=row["evidence_type"],
            clinical_concern=row["clinical_concern"],
            evidence_summary=row["evidence_summary"],
            patient_specific_modifiers=patient_specific_modifiers,
            plain_language_explanation=row["plain_language_explanation"],
            professional_question=row["professional_question"],
            source_ids=source_ids,
        )


REQUIRED_INTERACTION_FIELDS = (
    "interaction_id",
    "ingredient_ids",
    "review_priority",
    "evidence_type",
    "clinical_concern",
    "evidence_summary",
    "patient_specific_modifiers",
    "plain_language_explanation",
    "professional_question",
    "source_ids",
)
