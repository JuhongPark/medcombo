import unittest

from medcombo.knowledge import KnowledgeBase
from medcombo.normalize import normalize_medication_name


class NormalizeMedicationTest(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase.load_demo()

    def test_brand_name_matches_curated_medication(self):
        medication = normalize_medication_name("Tylenol", self.kb)

        self.assertEqual(medication.match_status, "matched")
        self.assertEqual(medication.display_name, "Tylenol")
        self.assertEqual(
            [ingredient.name for ingredient in medication.active_ingredients],
            ["acetaminophen"],
        )

    def test_combination_product_resolves_multiple_ingredients(self):
        medication = normalize_medication_name("NyQuil", self.kb)

        self.assertEqual(medication.match_status, "matched")
        self.assertEqual(
            [ingredient.name for ingredient in medication.active_ingredients],
            ["acetaminophen", "dextromethorphan", "doxylamine"],
        )

    def test_generic_ingredient_name_matches_generic_record(self):
        medication = normalize_medication_name("acetaminophen", self.kb)

        self.assertEqual(medication.match_status, "matched")
        self.assertEqual(medication.display_name, "Generic Acetaminophen")

    def test_unknown_product_stays_unresolved(self):
        medication = normalize_medication_name("Mystery capsule", self.kb)

        self.assertEqual(medication.match_status, "unknown")
        self.assertEqual(medication.active_ingredients, ())

    def test_ambiguous_short_name_keeps_candidates_visible(self):
        medication = normalize_medication_name("metoprolol", self.kb)

        self.assertEqual(medication.match_status, "ambiguous")
        self.assertEqual(
            set(medication.candidate_names),
            {"Metoprolol Tartrate", "Metoprolol Succinate"},
        )


if __name__ == "__main__":
    unittest.main()
