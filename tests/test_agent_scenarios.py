import unittest

from medcombo.agent import answer_agent_question, start_intake_agent_session


def answer_field(session, field_name, answer):
    question = next(
        question
        for question in session.active_questions
        if question.field_name == field_name
    )
    return answer_agent_question(session, question.question_id, answer)


class IntakeAgentScenarioTest(unittest.TestCase):
    def test_ambiguous_metoprolol_conversation_resolves_identity(self):
        session = start_intake_agent_session(["metoprolol"], source_type="manual")

        self.assertEqual(session.active_questions[0].question_type, "select_ambiguous_product")

        updated = answer_field(session, "identity", "succinate")

        self.assertEqual(updated.turns[-1].status, "captured")
        self.assertEqual(updated.intake_items[0].verification_status, "matched_by_name")
        self.assertEqual(updated.intake_items[0].normalized_medication.display_name, "Metoprolol Succinate")
        self.assertNotIn("identity", updated.intake_items[0].missing_fields)
        self.assertNotIn(
            session.active_questions[0].question_id,
            [question.question_id for question in updated.active_questions],
        )

    def test_unknown_product_can_be_corrected_to_known_product(self):
        session = start_intake_agent_session(["Mystery capsule"], source_type="manual")

        updated = answer_field(session, "identity", "Tylenol")

        self.assertEqual(updated.turns[-1].status, "captured")
        self.assertEqual(updated.intake_items[0].raw_text, "Mystery capsule")
        self.assertEqual(updated.intake_items[0].normalized_medication.display_name, "Tylenol")
        self.assertEqual(updated.intake_items[0].verification_status, "matched_by_name")

    def test_unsure_answer_preserves_missing_need_without_reasking_question(self):
        session = start_intake_agent_session(["Mystery capsule"], source_type="manual")
        question = session.active_questions[0]

        updated = answer_agent_question(session, question.question_id, "I don't know")

        self.assertEqual(updated.turns[-1].status, "needs_review")
        self.assertIn("identity", updated.intake_items[0].missing_fields)
        self.assertNotIn(
            question.question_id,
            [active_question.question_id for active_question in updated.active_questions],
        )

    def test_slot_capture_updates_all_targeted_intake_details(self):
        session = start_intake_agent_session(["Tylenol"], source_type="label")

        session = answer_field(session, "strength", "500 mg")
        session = answer_field(session, "dose", "2 tablets")
        session = answer_field(session, "frequency", "daily")
        session = answer_field(session, "formulation", "tablet")

        item = session.intake_items[0]
        self.assertEqual(item.strength, "500 mg")
        self.assertEqual(item.dose, "2 tablets")
        self.assertEqual(item.frequency, "daily")
        self.assertEqual(item.formulation, "tablet")
        self.assertEqual(item.missing_fields, ())
        self.assertTrue(session.completed)

    def test_information_source_answer_updates_source_confidence(self):
        session = start_intake_agent_session(["Tylenol"], source_type="manual")

        updated = answer_field(session, "information_source", "from the pharmacy medication list")

        self.assertEqual(updated.intake_items[0].source_type, "pharmacy_list")
        self.assertEqual(updated.intake_items[0].source_confidence, "pharmacy_list_verified")
        self.assertNotIn("information_source", updated.intake_items[0].missing_fields)


if __name__ == "__main__":
    unittest.main()
