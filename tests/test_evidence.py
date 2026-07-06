import unittest

from medcombo.evidence import InteractionEvidence
from medcombo.knowledge import KnowledgeBase


VALID_INTERACTION_ROW = {
    "interaction_id": "int_test",
    "ingredient_ids": ["ing_a", "ing_b"],
    "review_priority": "prompt_review",
    "evidence_type": "prototype_curated_label_reference",
    "clinical_concern": "Test review concern",
    "evidence_summary": "A test evidence note.",
    "patient_specific_modifiers": ["test context"],
    "plain_language_explanation": "This test pair may need professional review.",
    "professional_question": "Can you review this test pair?",
    "source_ids": ["src_demo_curated"],
}


class InteractionEvidenceTest(unittest.TestCase):
    def test_interaction_evidence_from_row_preserves_metadata(self):
        evidence = InteractionEvidence.from_row(VALID_INTERACTION_ROW)

        self.assertEqual(evidence.interaction_id, "int_test")
        self.assertEqual(evidence.ingredient_ids, ("ing_a", "ing_b"))
        self.assertEqual(evidence.patient_specific_modifiers, ("test context",))
        self.assertEqual(evidence.source_ids, ("src_demo_curated",))

    def test_interaction_evidence_requires_metadata(self):
        row = dict(VALID_INTERACTION_ROW)
        row.pop("clinical_concern")

        with self.assertRaisesRegex(ValueError, "clinical_concern"):
            InteractionEvidence.from_row(row)

    def test_demo_knowledge_base_loads_interaction_evidence_records(self):
        kb = KnowledgeBase.load_demo()

        self.assertIsInstance(kb.interactions[0], InteractionEvidence)
        self.assertTrue(kb.interactions[0].clinical_concern)


if __name__ == "__main__":
    unittest.main()
