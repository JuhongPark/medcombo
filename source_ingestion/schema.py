"""Shared schemas for offline source-ingestion experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceMetadata:
    source_name: str
    source_url: str
    retrieved_or_version_date: str
    license_note: str
    use_restrictions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImportedMedicationRecord:
    source: SourceMetadata
    source_record_id: str
    display_name: str
    normalized_name: str = ""
    rxcui: str = ""
    active_ingredients: tuple[str, ...] = ()
    mapping_confidence: str = "unmapped"
    out_of_scope_reason: str = ""
    review_status: str = "imported"


ALLOWED_MAPPING_CONFIDENCE = {
    "exact",
    "probable",
    "ambiguous",
    "unmapped",
    "out_of_scope",
}

ALLOWED_REVIEW_STATUS = {
    "imported",
    "curated",
    "expert_reviewed",
    "deprecated",
}


def validate_imported_medication_record(record: ImportedMedicationRecord) -> tuple[str, ...]:
    errors = []
    if not record.source.source_name:
        errors.append("source.source_name is required")
    if not record.source.source_url:
        errors.append("source.source_url is required")
    if not record.source.retrieved_or_version_date:
        errors.append("source.retrieved_or_version_date is required")
    if not record.source.license_note:
        errors.append("source.license_note is required")
    if not record.source_record_id:
        errors.append("source_record_id is required")
    if not record.display_name and not record.out_of_scope_reason:
        errors.append("display_name or out_of_scope_reason is required")
    if record.mapping_confidence not in ALLOWED_MAPPING_CONFIDENCE:
        errors.append(f"mapping_confidence is not allowed: {record.mapping_confidence}")
    if record.review_status not in ALLOWED_REVIEW_STATUS:
        errors.append(f"review_status is not allowed: {record.review_status}")
    if record.mapping_confidence == "out_of_scope" and not record.out_of_scope_reason:
        errors.append("out_of_scope_reason is required when mapping_confidence is out_of_scope")
    return tuple(errors)
