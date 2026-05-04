import unittest

from medcombo.agent import answer_agent_question, start_intake_agent_session


class IntakeAgentTest(unittest.TestCase):
    def test_agent_starts_with_active_questions(self):
        session = start_intake_agent_session(["metoprolol"], source_type="manual")

        self.assertFalse(session.completed)
        self.assertGreaterEqual(len(session.active_questions), 1)
        self.assertEqual(session.active_questions[0].question_type, "select_ambiguous_product")

    def test_agent_answer_selects_ambiguous_candidate(self):
        session = start_intake_agent_session(["metoprolol"], source_type="manual")
        question = session.active_questions[0]

        updated = answer_agent_question(session, question.question_id, "succinate")

        self.assertEqual(updated.turns[-1].status, "captured")
        self.assertEqual(updated.intake_items[0].verification_status, "matched_by_name")
        self.assertEqual(updated.intake_items[0].normalized_medication.display_name, "Metoprolol Succinate")
        self.assertNotIn("identity", updated.intake_items[0].missing_fields)

    def test_agent_answer_identifies_unknown_product(self):
        session = start_intake_agent_session(["Mystery capsule"], source_type="manual")
        question = session.active_questions[0]

        updated = answer_agent_question(session, question.question_id, "Tylenol")

        self.assertEqual(updated.turns[-1].status, "captured")
        self.assertEqual(updated.intake_items[0].normalized_medication.display_name, "Tylenol")
        self.assertEqual(updated.intake_items[0].raw_text, "Mystery capsule")

    def test_agent_captures_information_source(self):
        session = start_intake_agent_session(["Tylenol"], source_type="manual")
        question = next(
            question
            for question in session.active_questions
            if question.question_type == "confirm_information_source"
        )

        updated = answer_agent_question(session, question.question_id, "from the bottle label")

        self.assertEqual(updated.intake_items[0].source_type, "label")
        self.assertEqual(updated.intake_items[0].source_confidence, "label_verified")
        self.assertNotIn("information_source", updated.intake_items[0].missing_fields)

    def test_agent_captures_strength_and_skips_answered_question(self):
        session = start_intake_agent_session(["Tylenol"], source_type="label")
        question = next(
            question
            for question in session.active_questions
            if question.question_type == "confirm_strength"
        )

        updated = answer_agent_question(session, question.question_id, "500 mg")

        self.assertEqual(updated.intake_items[0].strength, "500 mg")
        self.assertNotIn(question.question_id, [item.question_id for item in updated.active_questions])
        self.assertIn(question.question_id, updated.answered_question_ids)

    def test_agent_records_unsure_answer_without_reasking_same_question(self):
        session = start_intake_agent_session(["Mystery capsule"], source_type="manual")
        question = session.active_questions[0]

        updated = answer_agent_question(session, question.question_id, "I do not know")

        self.assertEqual(updated.turns[-1].status, "needs_review")
        self.assertIn("identity", updated.intake_items[0].missing_fields)
        self.assertNotIn(question.question_id, [item.question_id for item in updated.active_questions])


if __name__ == "__main__":
    unittest.main()
