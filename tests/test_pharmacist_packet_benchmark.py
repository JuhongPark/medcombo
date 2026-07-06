import unittest

from medcombo.benchmarks import load_pharmacist_packet_cases, run_pharmacist_packet_benchmark


class PharmacistPacketBenchmarkTest(unittest.TestCase):
    def test_packet_fixture_has_expected_shape(self):
        benchmark = load_pharmacist_packet_cases()

        self.assertEqual(benchmark["benchmark_id"], "pharmacist-packet-demo-2026-05-01")
        self.assertEqual(benchmark["data_version"], "demo-2026-05-01")
        self.assertGreaterEqual(len(benchmark["cases"]), 3)
        for case in benchmark["cases"]:
            self.assertIn("case_id", case)
            self.assertIn("raw_inputs", case)
            self.assertIn("expected_section_ids", case)
            self.assertIn("expected_readiness_labels", case)
            self.assertIn("expected_text_contains", case)
            self.assertIn("expected_question_contains", case)
            self.assertIn("prohibited_text", case)

    def test_packet_fixture_cases_pass(self):
        report = run_pharmacist_packet_benchmark()

        self.assertEqual(report["benchmark_id"], "pharmacist-packet-demo-2026-05-01")
        self.assertEqual(report["case_count"], 3)
        self.assertEqual(report["fail_count"], 0, report["results"])


if __name__ == "__main__":
    unittest.main()
