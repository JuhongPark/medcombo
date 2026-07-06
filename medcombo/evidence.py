"""Evidence records used by traceable medication review rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


EVIDENCE_STATUSES = ("imported", "curated", "expert_reviewed", "deprecated")
SIGNAL_ELIGIBLE_EVIDENCE_STATUSES = ("curated", "expert_reviewed")


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
    review_status: str = "curated"
    source_freshness_date: str = ""
    reviewer_note: str = ""

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
        review_status = row.get("review_status", "curated")
        if review_status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Interaction evidence {row['interaction_id']} has unsupported review status: {review_status}"
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
            review_status=review_status,
            source_freshness_date=row.get("source_freshness_date", ""),
            reviewer_note=row.get("reviewer_note", ""),
        )


@dataclass(frozen=True)
class EvidenceRecord:
    record_id: str
    evidence_kind: str
    status: str
    source_ids: tuple[str, ...]
    source_freshness_date: str = ""
    reviewer_note: str = ""
    interaction: InteractionEvidence | None = None

    @property
    def is_signal_eligible(self) -> bool:
        return self.status in SIGNAL_ELIGIBLE_EVIDENCE_STATUSES

    @classmethod
    def from_interaction(cls, interaction: InteractionEvidence) -> "EvidenceRecord":
        return cls(
            record_id=f"interaction.{interaction.interaction_id}",
            evidence_kind="interaction",
            status=interaction.review_status,
            source_ids=interaction.source_ids,
            source_freshness_date=interaction.source_freshness_date,
            reviewer_note=interaction.reviewer_note,
            interaction=interaction,
        )


@dataclass(frozen=True)
class EvidenceRegistry:
    records: tuple[EvidenceRecord, ...]

    @classmethod
    def from_interactions(
        cls,
        interactions: tuple[InteractionEvidence, ...],
    ) -> "EvidenceRegistry":
        return cls(tuple(EvidenceRecord.from_interaction(interaction) for interaction in interactions))

    def record_for_interaction(self, interaction_id: str) -> EvidenceRecord | None:
        record_id = f"interaction.{interaction_id}"
        for record in self.records:
            if record.record_id == record_id:
                return record
        return None

    def is_interaction_signal_eligible(self, interaction_id: str) -> bool:
        record = self.record_for_interaction(interaction_id)
        return bool(record and record.is_signal_eligible)

    def eligible_interactions(self) -> tuple[InteractionEvidence, ...]:
        return tuple(
            record.interaction
            for record in self.records
            if record.evidence_kind == "interaction"
            and record.is_signal_eligible
            and record.interaction is not None
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
