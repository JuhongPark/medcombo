import unittest

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


if __name__ == "__main__":
    unittest.main()
