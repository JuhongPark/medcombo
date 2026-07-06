import json
import unittest
from pathlib import Path

from medcombo.rules import review_medication_list


BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "data" / "benchmarks" / "interaction_cases.json"


def load_interaction_cases():
    with BENCHMARK_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class InteractionBenchmarkTest(unittest.TestCase):
    def test_interaction_benchmark_fixture_has_expected_shape(self):
        benchmark = load_interaction_cases()

        self.assertEqual(benchmark["benchmark_id"], "interaction-demo-2026-05-01")
        self.assertEqual(benchmark["data_version"], "demo-2026-05-01")
        self.assertGreaterEqual(len(benchmark["cases"]), 10)
        for case in benchmark["cases"]:
            self.assertIn("case_id", case)
            self.assertIn("raw_inputs", case)
            self.assertIn("expected_signal_ids", case)

    def test_interaction_benchmark_cases_match_rule_outputs(self):
        benchmark = load_interaction_cases()

        failures = []
        for case in benchmark["cases"]:
            result = review_medication_list(case["raw_inputs"])
            signals_by_id = {signal.signal_id: signal for signal in result.signals}
            signal_types = {signal.signal_type for signal in result.signals}

            for signal_id in case["expected_signal_ids"]:
                if signal_id not in signals_by_id:
                    failures.append((case["case_id"], f"missing {signal_id}"))
                    continue
                signal = signals_by_id[signal_id]
                self.assertTrue(signal.evidence_type, signal_id)
                self.assertTrue(signal.clinical_concern, signal_id)
                self.assertTrue(signal.evidence_summary, signal_id)
                self.assertTrue(signal.patient_specific_modifiers, signal_id)

            for signal_id, metadata in case.get("expected_signal_metadata", {}).items():
                if signal_id not in signals_by_id:
                    continue
                signal = signals_by_id[signal_id]
                for field_name, expected_value in metadata.items():
                    actual_value = getattr(signal, field_name)
                    if actual_value != expected_value:
                        failures.append(
                            (
                                case["case_id"],
                                f"{signal_id}.{field_name} expected {expected_value}, got {actual_value}",
                            )
                        )

            for signal_type in case.get("expected_absent_signal_types", ()):
                if signal_type in signal_types:
                    failures.append((case["case_id"], f"unexpected {signal_type}"))

        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
