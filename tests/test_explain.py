import unittest

from medcombo.agent import answer_agent_question, start_intake_agent_session
from medcombo.rules import review_consumer_intake, review_medication_list
from medcombo.summary import build_consumer_summary


class ExplainTest(unittest.TestCase):
    def test_summary_includes_questions_and_sources(self):
        result = review_medication_list(["Warfarin", "Advil"])
        summary = build_consumer_summary(result)

        self.assertIn("MedCombo consumer health review summary", summary)
        self.assertIn("Question:", summary)
        self.assertIn("src_dailymed", summary)
        self.assertIn("not clinically validated", summary)
        self.assertIn("Sensitive personal information requires separate", summary)
        self.assertIn("Evidence concern: Bleeding-related review concern", summary)
        self.assertIn("Context to review:", summary)

    def test_every_signal_has_explanation_and_question(self):
        result = review_medication_list(["Tylenol", "NyQuil", "Zoloft"])

        self.assertGreaterEqual(len(result.signals), 1)
        for signal in result.signals:
            self.assertTrue(signal.plain_language_explanation)
            self.assertTrue(signal.professional_question)
            self.assertTrue(signal.source_ids)
            self.assertTrue(signal.rule_id)

    def test_summary_includes_supplements_and_health_context(self):
        result = review_consumer_intake(
            ["Tylenol"],
            supplements=["Vitamin D", "Fish oil"],
            demographics="Adult, age 45",
            body_info="Kidney function concern",
            conditions=["high blood pressure"],
            symptoms=["cough"],
        )
        summary = build_consumer_summary(result)

        self.assertIn("Supplements entered:", summary)
        self.assertIn("Vitamin D", summary)
        self.assertIn("Demographics: Adult, age 45", summary)
        self.assertIn("Body information: Kidney function concern", summary)
        self.assertIn("Chronic conditions or history: high blood pressure", summary)
        self.assertIn("Current symptoms: cough", summary)

    def test_summary_includes_explicit_no_information_choices(self):
        result = review_consumer_intake(
            ["Tylenol"],
            no_information=[
                "supplements",
                "demographics",
                "body_info",
                "conditions",
                "symptoms",
            ],
        )
        summary = build_consumer_summary(result)

        self.assertIn("User selected no supplement information", summary)
        self.assertIn("Demographics: user selected no information", summary)
        self.assertIn("Body information: user selected no information", summary)
        self.assertIn("Chronic conditions or history: user selected no information", summary)
        self.assertIn("Current symptoms: user selected no information", summary)

    def test_summary_separates_review_packet_sections(self):
        session = start_intake_agent_session(["metoprolol"], source_type="manual")
        updated = answer_agent_question(
            session,
            session.active_questions[0].question_id,
            "succinate",
        )
        result = review_medication_list(["Metoprolol Succinate"])

        summary = build_consumer_summary(
            result,
            intake_items=updated.intake_items,
            conversation_questions=updated.active_questions,
            agent_turns=updated.turns,
        )

        self.assertIn("Verified medications:", summary)
        self.assertIn("Uncertain or unresolved medications:", summary)
        self.assertIn("Missing intake details:", summary)
        self.assertIn("User answer history:", summary)
        self.assertIn("Pharmacist or clinician review checklist:", summary)
        self.assertIn("Answer: succinate", summary)
        self.assertIn("Metoprolol Succinate", summary)

    def test_no_signal_summary_preserves_coverage_boundary(self):
        result = review_medication_list(["Metformin", "Prilosec"])
        summary = build_consumer_summary(result)

        self.assertIn("Signal coverage note:", summary)
        self.assertIn("not a complete medication safety screen", summary)
        self.assertIn("No demo-dataset safety signals were generated", summary)
        self.assertNotIn("no risk", summary.lower())
        self.assertNotIn("all clear", summary.lower())


if __name__ == "__main__":
    unittest.main()
