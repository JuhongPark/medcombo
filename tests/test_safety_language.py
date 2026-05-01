import unittest

from medcombo.safety_language import find_prohibited_phrases, is_consumer_safe_text


class SafetyLanguageTest(unittest.TestCase):
    def test_detects_direct_medication_commands(self):
        text = "You should stop taking this medication today."

        self.assertFalse(is_consumer_safe_text(text))
        self.assertIn("stop taking", find_prohibited_phrases(text))

    def test_allows_review_signal_language(self):
        text = "This combination may need pharmacist review before medication changes."

        self.assertTrue(is_consumer_safe_text(text))


if __name__ == "__main__":
    unittest.main()
