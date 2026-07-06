import unittest
from dataclasses import replace

from medcombo.evidence import EvidenceRegistry, InteractionEvidence
from medcombo.knowledge import KnowledgeBase
from medcombo.rules import review_medication_list


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
        self.assertEqual(evidence.review_status, "curated")

    def test_interaction_evidence_requires_metadata(self):
        row = dict(VALID_INTERACTION_ROW)
        row.pop("clinical_concern")

        with self.assertRaisesRegex(ValueError, "clinical_concern"):
            InteractionEvidence.from_row(row)

    def test_interaction_evidence_rejects_unknown_review_status(self):
        row = dict(VALID_INTERACTION_ROW)
        row["review_status"] = "unreviewed"

        with self.assertRaisesRegex(ValueError, "unsupported review status"):
            InteractionEvidence.from_row(row)

    def test_evidence_registry_marks_curated_and_expert_reviewed_eligible(self):
        curated = InteractionEvidence.from_row(VALID_INTERACTION_ROW)
        expert_reviewed = replace(curated, interaction_id="int_expert", review_status="expert_reviewed")
        registry = EvidenceRegistry.from_interactions((curated, expert_reviewed))

        self.assertTrue(registry.is_interaction_signal_eligible("int_test"))
        self.assertTrue(registry.is_interaction_signal_eligible("int_expert"))
        self.assertEqual(len(registry.eligible_interactions()), 2)

    def test_evidence_registry_blocks_imported_and_deprecated_records(self):
        imported = replace(
            InteractionEvidence.from_row(VALID_INTERACTION_ROW),
            interaction_id="int_imported",
            review_status="imported",
        )
        deprecated = replace(imported, interaction_id="int_deprecated", review_status="deprecated")
        registry = EvidenceRegistry.from_interactions((imported, deprecated))

        self.assertFalse(registry.is_interaction_signal_eligible("int_imported"))
        self.assertFalse(registry.is_interaction_signal_eligible("int_deprecated"))
        self.assertEqual(registry.eligible_interactions(), ())

    def test_demo_knowledge_base_loads_interaction_evidence_records(self):
        kb = KnowledgeBase.load_demo()

        self.assertIsInstance(kb.interactions[0], InteractionEvidence)
        self.assertTrue(kb.interactions[0].clinical_concern)
        self.assertTrue(kb.evidence_registry.is_interaction_signal_eligible(kb.interactions[0].interaction_id))

    def test_deprecated_interaction_evidence_does_not_emit_signal(self):
        kb = KnowledgeBase.load_demo()
        interactions = tuple(
            replace(interaction, review_status="deprecated")
            if interaction.interaction_id == "int_warfarin_nsaid"
            else interaction
            for interaction in kb.interactions
        )
        updated_kb = KnowledgeBase(
            data_version=kb.data_version,
            medications=kb.medications,
            ingredients=kb.ingredients,
            drug_classes=kb.drug_classes,
            interactions=interactions,
            sources=kb.sources,
        )

        result = review_medication_list(["Warfarin", "Advil"], kb=updated_kb)

        self.assertNotIn("sig_int_warfarin_nsaid", [signal.signal_id for signal in result.signals])


if __name__ == "__main__":
    unittest.main()
