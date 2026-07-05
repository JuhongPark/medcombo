import json
import unittest
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "demo"


def load_json(name):
    with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class DemoDataIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.medication_data = load_json("medications.json")
        cls.interaction_data = load_json("interactions.json")
        cls.source_data = load_json("sources.json")

    def test_data_versions_match(self):
        versions = {
            self.medication_data["data_version"],
            self.interaction_data["data_version"],
            self.source_data["data_version"],
        }

        self.assertEqual(versions, {"demo-2026-05-01"})

    def test_primary_ids_are_unique(self):
        self.assert_unique("ingredient_id", self.medication_data["ingredients"])
        self.assert_unique("class_id", self.medication_data["drug_classes"])
        self.assert_unique("medication_id", self.medication_data["medications"])
        self.assert_unique("interaction_id", self.interaction_data["interactions"])
        self.assert_unique("source_id", self.source_data["sources"])

    def test_medication_references_exist(self):
        ingredient_ids = self.ids("ingredient_id", self.medication_data["ingredients"])
        class_ids = self.ids("class_id", self.medication_data["drug_classes"])
        source_ids = self.ids("source_id", self.source_data["sources"])

        for medication in self.medication_data["medications"]:
            self.assert_reference_subset(medication["active_ingredients"], ingredient_ids, medication["medication_id"])
            self.assert_reference_subset(medication["drug_classes"], class_ids, medication["medication_id"])
            self.assert_reference_subset(medication["source_ids"], source_ids, medication["medication_id"])

    def test_interaction_references_exist(self):
        ingredient_ids = self.ids("ingredient_id", self.medication_data["ingredients"])
        source_ids = self.ids("source_id", self.source_data["sources"])

        for interaction in self.interaction_data["interactions"]:
            self.assertGreaterEqual(len(interaction["ingredient_ids"]), 2)
            self.assert_reference_subset(interaction["ingredient_ids"], ingredient_ids, interaction["interaction_id"])
            self.assert_reference_subset(interaction["source_ids"], source_ids, interaction["interaction_id"])

    def test_interactions_include_evidence_metadata(self):
        for interaction in self.interaction_data["interactions"]:
            self.assertEqual(interaction["evidence_type"], "prototype_curated_label_reference")
            self.assertTrue(interaction["clinical_concern"], interaction["interaction_id"])
            self.assertTrue(interaction["evidence_summary"], interaction["interaction_id"])
            self.assertGreaterEqual(
                len(interaction["patient_specific_modifiers"]),
                1,
                interaction["interaction_id"],
            )

    def test_ingredient_and_class_sources_exist(self):
        source_ids = self.ids("source_id", self.source_data["sources"])

        for ingredient in self.medication_data["ingredients"]:
            self.assert_reference_subset(ingredient["source_ids"], source_ids, ingredient["ingredient_id"])
        for drug_class in self.medication_data["drug_classes"]:
            self.assert_reference_subset(drug_class["source_ids"], source_ids, drug_class["class_id"])

    def assert_unique(self, key, rows):
        values = [row[key] for row in rows]
        self.assertEqual(len(values), len(set(values)), key)

    def ids(self, key, rows):
        return {row[key] for row in rows}

    def assert_reference_subset(self, references, known_values, owner_id):
        missing = sorted(set(references) - known_values)
        self.assertEqual(missing, [], owner_id)


if __name__ == "__main__":
    unittest.main()
