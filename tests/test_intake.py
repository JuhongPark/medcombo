import unittest

from medcombo.intake import build_medication_intake, generate_conversation_questions
from medcombo.rules import review_medication_list
from medcombo.summary import build_consumer_summary


class MedicationIntakeTest(unittest.TestCase):
    def test_matched_medication_keeps_intake_state(self):
        items = build_medication_intake(["Tylenol 500 mg 2 tablets daily"], source_type="label")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].match_status, "matched")
        self.assertEqual(items[0].verification_status, "matched_by_name")
        self.assertEqual(items[0].source_confidence, "label_verified")
        self.assertEqual(items[0].strength, "500 mg")
        self.assertEqual(items[0].dose, "2 tablets")
        self.assertEqual(items[0].frequency, "daily")

    def test_unknown_product_creates_identity_question(self):
        items = build_medication_intake(["Mystery capsule"], source_type="memory")
        questions = generate_conversation_questions(items)

        self.assertEqual(items[0].verification_status, "unknown_product")
        self.assertIn("identity", items[0].missing_fields)
        self.assertIn("information_source", items[0].missing_fields)
        self.assertEqual(questions[0].question_type, "identify_unknown_product")
        self.assertIn("exact product name", questions[0].question_text)

    def test_ambiguous_product_creates_selection_question(self):
        items = build_medication_intake(["metoprolol"], source_type="manual")
        questions = generate_conversation_questions(items)

        self.assertEqual(items[0].verification_status, "ambiguous_needs_selection")
        self.assertIn("Metoprolol Succinate", items[0].candidate_medications)
        self.assertEqual(questions[0].question_type, "select_ambiguous_product")

    def test_missing_details_generate_targeted_questions(self):
        items = build_medication_intake(["Tylenol"], source_type="manual")
        questions = generate_conversation_questions(items)
        question_types = {question.question_type for question in questions}

        self.assertIn("confirm_information_source", question_types)
        self.assertIn("confirm_strength", question_types)
        self.assertIn("confirm_dose", question_types)
        self.assertIn("confirm_frequency", question_types)
        self.assertIn("confirm_formulation", question_types)

    def test_summary_can_include_intake_quality_and_prompts(self):
        items = build_medication_intake(["Tylenol"], source_type="manual")
        questions = generate_conversation_questions(items, max_questions=2)
        result = review_medication_list(["Tylenol"])

        summary = build_consumer_summary(result, intake_items=items, conversation_questions=questions)

        self.assertIn("Medication list readiness:", summary)
        self.assertIn("Pharmacist Questions:", summary)
        self.assertIn("matched_by_name", summary)


if __name__ == "__main__":
    unittest.main()
