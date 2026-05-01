import unittest

from medcombo.rules import review_consumer_intake, review_medication_list


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

    def test_supplement_and_health_context_generate_review_items(self):
        result = review_consumer_intake(
            ["Tylenol"],
            supplements="Vitamin D\nFish oil",
            demographics="Adult",
            body_info="Weight provided",
            conditions="high blood pressure",
            symptoms="cough",
        )

        signal_types = {signal.signal_type for signal in result.signals}
        self.assertIn("supplement_context", signal_types)
        self.assertIn("health_context_recorded", signal_types)
        self.assertEqual(result.context.supplements, ("Vitamin D", "Fish oil"))
        self.assertEqual(result.context.conditions, ("high blood pressure",))
        self.assertEqual(result.context.symptoms, ("cough",))

    def test_medication_is_required_for_consumer_intake(self):
        with self.assertRaises(ValueError):
            review_consumer_intake(
                [],
                supplements="Vitamin D",
                no_information=["demographics", "body_info", "conditions", "symptoms"],
            )

    def test_no_information_selection_clears_optional_context(self):
        result = review_consumer_intake(
            ["Tylenol"],
            supplements="Vitamin D",
            demographics="Adult",
            body_info="Weight provided",
            conditions="high blood pressure",
            symptoms="cough",
            no_information=[
                "supplements",
                "demographics",
                "body_info",
                "conditions",
                "symptoms",
            ],
        )

        self.assertEqual(result.context.supplements, ())
        self.assertEqual(result.context.demographics, "")
        self.assertEqual(result.context.body_info, "")
        self.assertEqual(result.context.conditions, ())
        self.assertEqual(result.context.symptoms, ())
        self.assertEqual(
            result.context.no_information,
            ("supplements", "demographics", "body_info", "conditions", "symptoms"),
        )


if __name__ == "__main__":
    unittest.main()
