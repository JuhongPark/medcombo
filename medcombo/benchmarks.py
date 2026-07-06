"""Benchmark fixtures for deterministic MedCombo development checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from medcombo.intake import build_medication_intake
from medcombo.knowledge import KnowledgeBase
from medcombo.review_packet import build_review_packet, render_review_packet_text
from medcombo.rules import review_consumer_intake
from medcombo.safety_language import find_prohibited_phrases


def default_normalization_benchmark_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "data" / "benchmarks" / "normalization_cases.json"


def default_pharmacist_packet_benchmark_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "data" / "benchmarks" / "pharmacist_packet_cases.json"


def load_normalization_cases(path: Path | None = None) -> dict[str, Any]:
    selected_path = path or default_normalization_benchmark_path()
    with selected_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_pharmacist_packet_cases(path: Path | None = None) -> dict[str, Any]:
    selected_path = path or default_pharmacist_packet_benchmark_path()
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


def run_pharmacist_packet_benchmark(
    path: Path | None = None,
    kb: KnowledgeBase | None = None,
) -> dict[str, Any]:
    benchmark = load_pharmacist_packet_cases(path)
    kb = kb or KnowledgeBase.load_demo()
    results = [
        _evaluate_packet_case(case, kb)
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


def _evaluate_packet_case(case: dict[str, Any], kb: KnowledgeBase) -> dict[str, Any]:
    result = review_consumer_intake(
        case["raw_inputs"],
        supplements=case.get("supplements", ""),
        demographics=case.get("demographics", ""),
        body_info=case.get("body_info", ""),
        conditions=case.get("conditions", ""),
        symptoms=case.get("symptoms", ""),
        no_information=case.get("no_information", ()),
        kb=kb,
    )
    intake_items = build_medication_intake(
        case["raw_inputs"],
        source_type=case.get("source_type", "manual"),
        kb=kb,
    )
    packet = build_review_packet(result, intake_items=intake_items)
    text = render_review_packet_text(packet)
    section_ids = {section.section_id for section in packet.sections}
    questions = tuple(
        item
        for section in packet.sections
        if section.section_id == "pharmacist_questions"
        for item in section.items
    )
    failures = []

    for section_id in case.get("expected_section_ids", ()):
        if section_id not in section_ids:
            failures.append(f"missing section {section_id}")

    for label in case.get("expected_readiness_labels", ()):
        if label not in packet.readiness.labels:
            failures.append(f"missing readiness label {label}")

    for expected_text in case.get("expected_text_contains", ()):
        if expected_text not in text:
            failures.append(f"missing text {expected_text}")

    for expected_question in case.get("expected_question_contains", ()):
        if not any(expected_question in question for question in questions):
            failures.append(f"missing question {expected_question}")

    lower_text = text.lower()
    for phrase in case.get("prohibited_text", ()):
        if phrase.lower() in lower_text:
            failures.append(f"prohibited text {phrase}")

    prohibited_matches = find_prohibited_phrases(text)
    if prohibited_matches:
        failures.append(f"consumer language guardrail matched {prohibited_matches}")

    return {
        "case_id": case["case_id"],
        "raw_inputs": case["raw_inputs"],
        "readiness_labels": packet.readiness.labels,
        "section_ids": tuple(sorted(section_ids)),
        "failures": tuple(failures),
    }


def main() -> None:
    reports = (
        run_normalization_benchmark(),
        run_pharmacist_packet_benchmark(),
    )
    for report in reports:
        print(
            f"{report['benchmark_id']}: "
            f"{report['pass_count']}/{report['case_count']} cases passed"
        )
        for result in report["results"]:
            if result["failures"]:
                print(f"- {result['case_id']}: {'; '.join(result['failures'])}")
    raise SystemExit(1 if any(report["fail_count"] for report in reports) else 0)


if __name__ == "__main__":
    main()
