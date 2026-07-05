import unittest

from app.web_app import WebSessionState, render_result, review_from_session_state
from medcombo.agent import answer_agent_question, start_intake_agent_session


class WebAppWorkflowTest(unittest.TestCase):
    def test_render_result_includes_active_question_answer_form(self):
        agent_session = start_intake_agent_session(["metoprolol"], source_type="manual")
        state = WebSessionState(
            agent_session=agent_session,
            medications_text="metoprolol",
            supplements_text="",
            demographics_text="",
            body_info_text="",
            conditions_text="",
            symptoms_text="",
            no_information=(),
            source_type="manual",
        )
        result = review_from_session_state(state)

        rendered = render_result(
            result,
            intake_items=agent_session.intake_items,
            conversation_questions=agent_session.active_questions,
            agent_session=agent_session,
            web_session_id="web_test",
        )

        self.assertIn('name="action" value="answer_question"', rendered)
        self.assertIn('name="web_session_id" value="web_test"', rendered)
        self.assertIn(agent_session.active_questions[0].question_id, rendered)

    def test_render_result_includes_interaction_evidence_metadata(self):
        agent_session = start_intake_agent_session(["Warfarin", "Advil"], source_type="label")
        state = WebSessionState(
            agent_session=agent_session,
            medications_text="Warfarin\nAdvil",
            supplements_text="",
            demographics_text="",
            body_info_text="",
            conditions_text="",
            symptoms_text="",
            no_information=(),
            source_type="label",
        )
        result = review_from_session_state(state)

        rendered = render_result(
            result,
            intake_items=agent_session.intake_items,
            conversation_questions=agent_session.active_questions,
            agent_session=agent_session,
            web_session_id="web_test",
        )

        self.assertIn("Evidence concern: Bleeding-related review concern", rendered)
        self.assertIn("Context to review:", rendered)

    def test_review_from_session_state_uses_updated_agent_identity(self):
        agent_session = start_intake_agent_session(["metoprolol"], source_type="manual")
        updated_session = answer_agent_question(
            agent_session,
            agent_session.active_questions[0].question_id,
            "succinate",
        )
        state = WebSessionState(
            agent_session=updated_session,
            medications_text="metoprolol",
            supplements_text="",
            demographics_text="",
            body_info_text="",
            conditions_text="",
            symptoms_text="",
            no_information=(),
            source_type="manual",
        )

        result = review_from_session_state(state)

        self.assertEqual(result.medications[0].display_name, "Metoprolol Succinate")
        self.assertEqual(result.medications[0].match_status, "matched")
        self.assertNotIn("ambiguous_product", [signal.signal_type for signal in result.signals])


if __name__ == "__main__":
    unittest.main()
