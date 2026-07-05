import unittest

from medcombo.benchmarks import load_normalization_cases, run_normalization_benchmark


class NormalizationBenchmarkTest(unittest.TestCase):
    def test_normalization_benchmark_fixture_has_expected_shape(self):
        benchmark = load_normalization_cases()

        self.assertEqual(benchmark["benchmark_id"], "normalization-demo-2026-05-01")
        self.assertEqual(benchmark["data_version"], "demo-2026-05-01")
        self.assertGreaterEqual(len(benchmark["cases"]), 8)
        for case in benchmark["cases"]:
            self.assertIn("case_id", case)
            self.assertIn("raw_text", case)
            self.assertIn("expected_match_status", case)

    def test_normalization_benchmark_cases_pass_against_demo_data(self):
        report = run_normalization_benchmark()

        failures = [
            (result["case_id"], result["failures"])
            for result in report["results"]
            if result["failures"]
        ]
        self.assertEqual(failures, [])
        self.assertEqual(report["case_count"], 8)
        self.assertEqual(report["pass_count"], 8)
        self.assertEqual(report["fail_count"], 0)


if __name__ == "__main__":
    unittest.main()
