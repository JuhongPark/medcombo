import unittest
from pathlib import Path

from app.web_app import (
    WebSessionState,
    render_page,
    render_result,
    render_sample_only_page,
    review_from_session_state,
)
from medcombo.agent import answer_agent_question, start_intake_agent_session


class WebAppWorkflowTest(unittest.TestCase):
    def test_public_copy_uses_review_packet_positioning(self):
        page = render_page(
            medications_text="Tylenol",
            supplements_text="",
            demographics_text="",
            body_info_text="",
            conditions_text="",
            symptoms_text="",
            no_information=(),
            source_type="manual",
            error_message="",
            result=None,
        )
        readme = Path("README.md").read_text(encoding="utf-8")
        public_copy = f"{page}\n{readme}"

        self.assertIn("pharmacist-ready review packet", public_copy)
        self.assertIn("Build review packet", page)
        self.assertNotIn("Consumer-first healthcare AI system", public_copy)
        self.assertNotIn("medication-combination safety review", public_copy)
        self.assertNotIn("Review list", page)
        self.assertNotIn("all clear", public_copy.lower())
        self.assertNotIn("safe combination", public_copy.lower())

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

    def test_sample_only_page_disables_real_input_collection(self):
        rendered = render_sample_only_page()

        self.assertIn("Synthetic sample mode is on", rendered)
        self.assertIn("Build sample packet", rendered)
        self.assertIn("readonly aria-readonly", rendered)
        self.assertIn("<select id=\"source_type\" name=\"source_type\" disabled>", rendered)
        self.assertIn("MedCombo pharmacist-ready review packet", rendered)
        self.assertNotIn('name="answer_text"', rendered)

    def test_render_page_sample_only_copy_uses_synthetic_boundary(self):
        rendered = render_page(
            medications_text="Tylenol",
            supplements_text="",
            demographics_text="",
            body_info_text="",
            conditions_text="",
            symptoms_text="",
            no_information=(),
            source_type="manual",
            error_message="",
            result=None,
            sample_only=True,
        )

        self.assertIn("Synthetic sample mode is on", rendered)
        self.assertIn("Do not enter real medication or health information", rendered)
        self.assertIn("Build sample packet", rendered)
        self.assertNotIn("Build review packet", rendered)

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

    def test_render_result_keeps_no_signal_boundary_near_results(self):
        agent_session = start_intake_agent_session(["Metformin", "Prilosec"], source_type="label")
        state = WebSessionState(
            agent_session=agent_session,
            medications_text="Metformin\nPrilosec",
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

        self.assertIn("Signal coverage note", rendered)
        self.assertIn("not a complete medication safety screen", rendered)
        self.assertIn("No demo-dataset safety signals were generated", rendered)
        self.assertNotIn("no risk", rendered.lower())
        self.assertNotIn("all clear", rendered.lower())

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
