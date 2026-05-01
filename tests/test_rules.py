import unittest

from medcombo.rules import review_medication_list


class ReviewRulesTest(unittest.TestCase):
    def test_duplicate_active_ingredient_signal(self):
        result = review_medication_list(["Tylenol", "acetaminophen"])

        duplicate_signals = [
            signal
            for signal in result.signals
            if signal.signal_type == "duplicate_active_ingredient"
        ]
        self.assertEqual(len(duplicate_signals), 1)
        self.assertEqual(duplicate_signals[0].ingredient_ids, ("ing_acetaminophen",))
        self.assertEqual(duplicate_signals[0].rule_id, "rule.duplicate_active_ingredient")
        self.assertIn("src_demo_curated", duplicate_signals[0].source_ids)

    def test_therapeutic_class_overlap_signal(self):
        result = review_medication_list(["Advil", "Aleve"])

        class_signals = [
            signal
            for signal in result.signals
            if signal.signal_type == "therapeutic_class_overlap"
        ]
        self.assertEqual(len(class_signals), 1)
        self.assertEqual(class_signals[0].review_priority, "routine_review")

    def test_curated_interaction_signal(self):
        result = review_medication_list(["Warfarin", "Advil"])

        interaction_signals = [
            signal for signal in result.signals if signal.signal_type == "possible_interaction"
        ]
        self.assertEqual(len(interaction_signals), 1)
        self.assertEqual(interaction_signals[0].review_priority, "prompt_review")
        self.assertIn("src_dailymed", interaction_signals[0].source_ids)

    def test_unknown_product_generates_review_item(self):
        result = review_medication_list(["Tylenol", "Mystery capsule"])

        unknown_signals = [
            signal for signal in result.signals if signal.signal_type == "unknown_product"
        ]
        self.assertEqual(len(unknown_signals), 1)
        self.assertEqual(unknown_signals[0].review_priority, "unknown")


if __name__ == "__main__":
    unittest.main()
