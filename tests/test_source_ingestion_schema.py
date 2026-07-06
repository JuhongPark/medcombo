import unittest

from source_ingestion.schema import (
    ImportedMedicationRecord,
    SourceMetadata,
    validate_imported_medication_record,
)


class SourceIngestionSchemaTest(unittest.TestCase):
    def test_valid_imported_medication_record_passes_validation(self):
        record = ImportedMedicationRecord(
            source=SourceMetadata(
                source_name="RxNorm",
                source_url="https://www.nlm.nih.gov/research/umls/rxnorm/",
                retrieved_or_version_date="2026-07-06",
                license_note="Official public documentation and source terms apply.",
            ),
            source_record_id="demo-rxcui-123",
            display_name="Example Medication",
            normalized_name="example medication oral product",
            rxcui="demo-rxcui-123",
            active_ingredients=("example ingredient",),
            mapping_confidence="exact",
            review_status="imported",
        )

        self.assertEqual(validate_imported_medication_record(record), ())

    def test_out_of_scope_record_requires_reason(self):
        record = ImportedMedicationRecord(
            source=SourceMetadata(
                source_name="RxNorm",
                source_url="https://www.nlm.nih.gov/research/umls/rxnorm/",
                retrieved_or_version_date="2026-07-06",
                license_note="Official public documentation and source terms apply.",
            ),
            source_record_id="supplement-example",
            display_name="Vitamin D",
            mapping_confidence="out_of_scope",
        )

        self.assertIn(
            "out_of_scope_reason is required when mapping_confidence is out_of_scope",
            validate_imported_medication_record(record),
        )

    def test_missing_source_metadata_fails_validation(self):
        record = ImportedMedicationRecord(
            source=SourceMetadata(
                source_name="",
                source_url="",
                retrieved_or_version_date="",
                license_note="",
            ),
            source_record_id="",
            display_name="",
        )

        errors = validate_imported_medication_record(record)

        self.assertIn("source.source_name is required", errors)
        self.assertIn("source.source_url is required", errors)
        self.assertIn("source.retrieved_or_version_date is required", errors)
        self.assertIn("source.license_note is required", errors)
        self.assertIn("source_record_id is required", errors)
        self.assertIn("display_name or out_of_scope_reason is required", errors)


if __name__ == "__main__":
    unittest.main()
