"""Benchmark fixtures for deterministic MedCombo development checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from medcombo.intake import build_medication_intake
from medcombo.knowledge import KnowledgeBase


def default_normalization_benchmark_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "data" / "benchmarks" / "normalization_cases.json"


def load_normalization_cases(path: Path | None = None) -> dict[str, Any]:
    selected_path = path or default_normalization_benchmark_path()
    with selected_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_normalization_benchmark(
    path: Path | None = None,
    kb: KnowledgeBase | None = None,
) -> dict[str, Any]:
    benchmark = load_normalization_cases(path)
    kb = kb or KnowledgeBase.load_demo()
    results = [
        _evaluate_case(case, kb)
        for case in benchmark["cases"]
    ]
    failures = [
        result
        for result in results
        if result["failures"]
    ]
    return {
        "benchmark_id": benchmark["benchmark_id"],
        "data_version": benchmark["data_version"],
        "case_count": len(results),
        "pass_count": len(results) - len(failures),
        "fail_count": len(failures),
        "results": results,
    }


def _evaluate_case(case: dict[str, Any], kb: KnowledgeBase) -> dict[str, Any]:
    item = build_medication_intake(
        [case["raw_text"]],
        source_type=case.get("source_type", "manual"),
        kb=kb,
    )[0]
    medication = item.normalized_medication
    failures = []

    expected_status = case["expected_match_status"]
    if medication.match_status != expected_status:
        failures.append(
            f"match_status expected {expected_status}, got {medication.match_status}"
        )

    expected_medication_id = case.get("expected_medication_id")
    if expected_medication_id and medication.medication_id != expected_medication_id:
        failures.append(
            f"medication_id expected {expected_medication_id}, got {medication.medication_id}"
        )

    expected_candidate_ids = case.get("expected_candidate_ids")
    if expected_candidate_ids and set(medication.candidate_ids) != set(expected_candidate_ids):
        failures.append(
            "candidate_ids expected "
            f"{sorted(expected_candidate_ids)}, got {sorted(medication.candidate_ids)}"
        )

    for field_name in ("strength", "dose", "frequency", "formulation"):
        expected_value = case.get(f"expected_{field_name}")
        actual_value = getattr(item, field_name)
        if expected_value and actual_value != expected_value:
            failures.append(f"{field_name} expected {expected_value}, got {actual_value}")

    return {
        "case_id": case["case_id"],
        "raw_text": case["raw_text"],
        "match_status": medication.match_status,
        "medication_id": medication.medication_id,
        "candidate_ids": medication.candidate_ids,
        "failures": tuple(failures),
    }
