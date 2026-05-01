import unittest

from medcombo.rules import review_medication_list
from medcombo.summary import build_consumer_summary


class ExplainTest(unittest.TestCase):
    def test_summary_includes_questions_and_sources(self):
        result = review_medication_list(["Warfarin", "Advil"])
        summary = build_consumer_summary(result)

        self.assertIn("MedCombo medication review summary", summary)
        self.assertIn("Question:", summary)
        self.assertIn("src_dailymed", summary)
        self.assertIn("not clinically validated", summary)

    def test_every_signal_has_explanation_and_question(self):
        result = review_medication_list(["Tylenol", "NyQuil", "Zoloft"])

        self.assertGreaterEqual(len(result.signals), 1)
        for signal in result.signals:
            self.assertTrue(signal.plain_language_explanation)
            self.assertTrue(signal.professional_question)
            self.assertTrue(signal.source_ids)
            self.assertTrue(signal.rule_id)


if __name__ == "__main__":
    unittest.main()
