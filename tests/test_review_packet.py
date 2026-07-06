import unittest

from medcombo.intake import build_medication_intake
from medcombo.review_packet import build_review_packet, render_review_packet_text
from medcombo.rules import review_consumer_intake, review_medication_list
from medcombo.safety_language import is_consumer_safe_text


class ReviewPacketTest(unittest.TestCase):
    def test_packet_contains_target_sections(self):
        result = review_medication_list(["Warfarin", "Advil"])

        packet = build_review_packet(result)
        section_ids = {section.section_id for section in packet.sections}
        text = render_review_packet_text(packet)

        self.assertIn("review_snapshot", section_ids)
        self.assertIn("verified_medications", section_ids)
        self.assertIn("identity_confirmation", section_ids)
        self.assertIn("missing_details", section_ids)
        self.assertIn("duplicate_active_ingredient_signals", section_ids)
        self.assertIn("curated_interaction_review_signals", section_ids)
        self.assertIn("supplements_and_out_of_scope_items", section_ids)
        self.assertIn("context_to_ask_about", section_ids)
        self.assertIn("pharmacist_questions", section_ids)
        self.assertIn("evidence_appendix", section_ids)
        self.assertIn("Curated Interaction Review Signals:", text)
        self.assertIn("Evidence concern: Bleeding-related review concern", text)
        self.assertTrue(is_consumer_safe_text(text))

    def test_readiness_preserves_missing_details_without_scores(self):
        intake_items = build_medication_intake(["Tylenol"], source_type="manual")
        result = review_medication_list(["Tylenol"])

        packet = build_review_packet(result, intake_items=intake_items)
        text = render_review_packet_text(packet)

        self.assertIn("missing_details", packet.readiness.labels)
        self.assertIn("needs_source_confirmation", packet.readiness.labels)
        self.assertGreaterEqual(packet.readiness.missing_field_count, 4)
        self.assertIn("Missing Dose, Frequency, Route, Or Formulation:", text)
        self.assertNotIn("safety score", text.lower())
        self.assertNotIn("risk score", text.lower())
        self.assertNotIn("all clear", text.lower())
        self.assertNotIn("no risk", text.lower())

    def test_unknown_and_supplement_items_stay_visible(self):
        result = review_consumer_intake(
            ["Mystery capsule"],
            supplements="Fish oil",
            conditions="high blood pressure",
        )

        packet = build_review_packet(result)
        text = render_review_packet_text(packet)

        self.assertIn("needs_identity_review", packet.readiness.labels)
        self.assertIn("includes_out_of_scope_items", packet.readiness.labels)
        self.assertIn("Mystery capsule", text)
        self.assertIn("Fish oil", text)
        self.assertIn("Context To Ask About:", text)


if __name__ == "__main__":
    unittest.main()
