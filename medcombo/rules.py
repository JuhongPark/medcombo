"""Traceable medication safety review rules."""

from __future__ import annotations

from collections import defaultdict

from medcombo.explain import (
    ambiguous_product_explanation,
    ambiguous_product_question,
    class_overlap_explanation,
    class_overlap_question,
    duplicate_ingredient_explanation,
    duplicate_ingredient_question,
    unknown_product_explanation,
    unknown_product_question,
)
from medcombo.knowledge import KnowledgeBase
from medcombo.models import ConsumerHealthContext, NormalizedMedication, ReviewResult, SafetySignal
from medcombo.normalize import normalize_medication_list
from medcombo.safety_language import require_consumer_safe_text
from medcombo.text import stable_id_part


PRIORITY_ORDER = {
    "urgent_review": 0,
    "prompt_review": 1,
    "routine_review": 2,
    "information": 3,
    "unknown": 4,
}


def review_medication_list(
    raw_inputs: list[str] | tuple[str, ...],
    kb: KnowledgeBase | None = None,
) -> ReviewResult:
    return review_consumer_intake(raw_inputs, kb=kb)


def review_consumer_intake(
    raw_inputs: list[str] | tuple[str, ...],
    supplements: str | list[str] | tuple[str, ...] = (),
    demographics: str = "",
    body_info: str = "",
    conditions: str | list[str] | tuple[str, ...] = (),
    symptoms: str | list[str] | tuple[str, ...] = (),
    no_information: str | list[str] | tuple[str, ...] = (),
    require_medications: bool = True,
    kb: KnowledgeBase | None = None,
) -> ReviewResult:
    kb = kb or KnowledgeBase.load_demo()
    medication_inputs = _clean_text_lines(raw_inputs)
    if require_medications and not medication_inputs:
        raise ValueError("At least one medication or product is required for review.")
    no_information_values = _clean_text_lines(no_information)
    context = ConsumerHealthContext(
        supplements=() if "supplements" in no_information_values else _clean_text_lines(supplements),
        demographics="" if "demographics" in no_information_values else demographics.strip(),
        body_info="" if "body_info" in no_information_values else body_info.strip(),
        conditions=() if "conditions" in no_information_values else _clean_text_lines(conditions),
        symptoms=() if "symptoms" in no_information_values else _clean_text_lines(symptoms),
        no_information=no_information_values,
    )
    medications = normalize_medication_list(medication_inputs, kb)
    signals = []
    signals.extend(_unresolved_signals(medications, kb))

    matched = tuple(medication for medication in medications if medication.is_matched)
    signals.extend(_duplicate_ingredient_signals(matched, kb))
    signals.extend(_class_overlap_signals(matched, kb))
    signals.extend(_interaction_signals(matched, kb))
    signals.extend(_context_signals(context, kb))

    ordered_signals = tuple(sorted(signals, key=_signal_sort_key))
    source_ids = _collect_source_ids(medications, ordered_signals)
    if context.has_any_data:
        source_ids.add("src_demo_curated")
    return ReviewResult(
        data_version=kb.data_version,
        medications=medications,
        signals=ordered_signals,
        sources=kb.source_list(tuple(sorted(source_ids))),
        context=context,
    )


def _clean_text_lines(values: str | list[str] | tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(values, str):
        raw_values = values.splitlines()
    else:
        raw_values = values
    return tuple(value.strip() for value in raw_values if value and value.strip())


def _unresolved_signals(
    medications: tuple[NormalizedMedication, ...],
    kb: KnowledgeBase,
) -> tuple[SafetySignal, ...]:
    signals = []
    for medication in medications:
        if medication.match_status == "unknown":
            signals.append(
                SafetySignal(
                    signal_id=f"sig_unknown_{stable_id_part(medication.input_text)}",
                    signal_type="unknown_product",
                    review_priority="unknown",
                    medication_ids=(),
                    ingredient_ids=(),
                    plain_language_explanation=unknown_product_explanation(medication),
                    professional_question=unknown_product_question(medication),
                    source_ids=("src_demo_curated",),
                    rule_id="normalization.unknown_product",
                    data_version=kb.data_version,
                    confidence=0.0,
                )
            )
        elif medication.match_status == "ambiguous":
            signals.append(
                SafetySignal(
                    signal_id=f"sig_ambiguous_{stable_id_part(medication.input_text)}",
                    signal_type="ambiguous_product",
                    review_priority="unknown",
                    medication_ids=medication.candidate_ids,
                    ingredient_ids=(),
                    plain_language_explanation=ambiguous_product_explanation(medication),
                    professional_question=ambiguous_product_question(medication),
                    source_ids=("src_demo_curated",),
                    rule_id="normalization.ambiguous_product",
                    data_version=kb.data_version,
                    confidence=medication.match_confidence,
                )
            )
    return tuple(signals)


def _duplicate_ingredient_signals(
    medications: tuple[NormalizedMedication, ...],
    kb: KnowledgeBase,
) -> tuple[SafetySignal, ...]:
    ingredient_to_meds: dict[str, list[NormalizedMedication]] = defaultdict(list)
    for medication in medications:
        for ingredient in medication.active_ingredients:
            ingredient_to_meds[ingredient.ingredient_id].append(medication)

    signals = []
    for ingredient_id, medication_group in sorted(ingredient_to_meds.items()):
        unique_medications = _unique_medications(medication_group)
        if len(unique_medications) < 2:
            continue

        ingredient = kb.ingredient(ingredient_id)
        source_ids = _ordered_unique(
            ("src_demo_curated",)
            + ingredient.source_ids
            + tuple(source_id for medication in unique_medications for source_id in medication.source_ids)
        )
        signals.append(
            SafetySignal(
                signal_id=f"sig_duplicate_{ingredient_id}",
                signal_type="duplicate_active_ingredient",
                review_priority="prompt_review",
                medication_ids=tuple(medication.medication_id or "" for medication in unique_medications),
                ingredient_ids=(ingredient_id,),
                plain_language_explanation=duplicate_ingredient_explanation(ingredient, unique_medications),
                professional_question=duplicate_ingredient_question(ingredient, unique_medications),
                source_ids=source_ids,
                rule_id="rule.duplicate_active_ingredient",
                data_version=kb.data_version,
                confidence=0.95,
            )
        )
    return tuple(signals)


def _class_overlap_signals(
    medications: tuple[NormalizedMedication, ...],
    kb: KnowledgeBase,
) -> tuple[SafetySignal, ...]:
    class_to_meds: dict[str, list[NormalizedMedication]] = defaultdict(list)
    for medication in medications:
        for drug_class in medication.drug_classes:
            class_to_meds[drug_class.class_id].append(medication)

    signals = []
    for class_id, medication_group in sorted(class_to_meds.items()):
        unique_medications = _unique_medications(medication_group)
        if len(unique_medications) < 2:
            continue
        ingredient_sets = {
            tuple(ingredient.ingredient_id for ingredient in medication.active_ingredients)
            for medication in unique_medications
        }
        if len(ingredient_sets) == 1:
            continue

        drug_class = kb.drug_class(class_id)
        source_ids = _ordered_unique(
            ("src_demo_curated",)
            + drug_class.source_ids
            + tuple(source_id for medication in unique_medications for source_id in medication.source_ids)
        )
        ingredient_ids = _ordered_unique(
            tuple(
                ingredient.ingredient_id
                for medication in unique_medications
                for ingredient in medication.active_ingredients
            )
        )
        signals.append(
            SafetySignal(
                signal_id=f"sig_class_overlap_{class_id}",
                signal_type="therapeutic_class_overlap",
                review_priority="routine_review",
                medication_ids=tuple(medication.medication_id or "" for medication in unique_medications),
                ingredient_ids=ingredient_ids,
                plain_language_explanation=class_overlap_explanation(drug_class, unique_medications),
                professional_question=class_overlap_question(drug_class, unique_medications),
                source_ids=source_ids,
                rule_id="rule.therapeutic_class_overlap",
                data_version=kb.data_version,
                confidence=0.8,
            )
        )
    return tuple(signals)


def _interaction_signals(
    medications: tuple[NormalizedMedication, ...],
    kb: KnowledgeBase,
) -> tuple[SafetySignal, ...]:
    ingredient_to_medications: dict[str, list[NormalizedMedication]] = defaultdict(list)
    for medication in medications:
        for ingredient in medication.active_ingredients:
            ingredient_to_medications[ingredient.ingredient_id].append(medication)

    signals = []
    for interaction in kb.interactions:
        ingredient_ids = tuple(interaction["ingredient_ids"])
        if not all(ingredient_id in ingredient_to_medications for ingredient_id in ingredient_ids):
            continue

        medication_ids = _ordered_unique(
            tuple(
                medication.medication_id or ""
                for ingredient_id in ingredient_ids
                for medication in ingredient_to_medications[ingredient_id]
            )
        )
        explanation = require_consumer_safe_text(interaction["plain_language_explanation"])
        question = require_consumer_safe_text(interaction["professional_question"])
        patient_specific_modifiers = tuple(
            require_consumer_safe_text(modifier)
            for modifier in interaction.get("patient_specific_modifiers", ())
        )
        signals.append(
            SafetySignal(
                signal_id=f"sig_{interaction['interaction_id']}",
                signal_type="possible_interaction",
                review_priority=interaction["review_priority"],
                medication_ids=medication_ids,
                ingredient_ids=ingredient_ids,
                plain_language_explanation=explanation,
                professional_question=question,
                source_ids=tuple(interaction["source_ids"]),
                rule_id=f"interaction.{interaction['interaction_id']}",
                data_version=kb.data_version,
                confidence=0.85,
                evidence_type=require_consumer_safe_text(interaction.get("evidence_type", "")),
                clinical_concern=require_consumer_safe_text(interaction.get("clinical_concern", "")),
                evidence_summary=require_consumer_safe_text(interaction.get("evidence_summary", "")),
                patient_specific_modifiers=patient_specific_modifiers,
            )
        )
    return tuple(signals)


def _context_signals(
    context: ConsumerHealthContext,
    kb: KnowledgeBase,
) -> tuple[SafetySignal, ...]:
    signals = []
    if context.supplements:
        supplement_names = _sentence_list(context.supplements)
        explanation = require_consumer_safe_text(
            f"MedCombo recorded supplement products for review: {supplement_names}. "
            "This MVP does not validate supplement-drug interactions yet, so a "
            "pharmacist or clinician should review them with the medication list."
        )
        question = require_consumer_safe_text(
            "Can you review these supplements with my prescription and "
            "over-the-counter products for overlap or interaction concerns?"
        )
        signals.append(
            SafetySignal(
                signal_id="sig_context_supplements",
                signal_type="supplement_context",
                review_priority="routine_review",
                medication_ids=(),
                ingredient_ids=(),
                plain_language_explanation=explanation,
                professional_question=question,
                source_ids=("src_demo_curated",),
                rule_id="context.supplements_recorded",
                data_version=kb.data_version,
                confidence=1.0,
            )
        )

    if context.demographics or context.body_info or context.conditions or context.symptoms:
        explanation = require_consumer_safe_text(
            "MedCombo recorded demographic, body, condition, or symptom context "
            "for review. This MVP includes that context in the review summary but "
            "does not use it for personalized clinical risk scoring yet."
        )
        question = require_consumer_safe_text(
            "Which of these health details matter for medication safety, and "
            "should any medication review account for them?"
        )
        signals.append(
            SafetySignal(
                signal_id="sig_context_health_profile",
                signal_type="health_context_recorded",
                review_priority="information",
                medication_ids=(),
                ingredient_ids=(),
                plain_language_explanation=explanation,
                professional_question=question,
                source_ids=("src_demo_curated",),
                rule_id="context.health_profile_recorded",
                data_version=kb.data_version,
                confidence=1.0,
            )
        )
    return tuple(signals)


def _unique_medications(
    medications: list[NormalizedMedication] | tuple[NormalizedMedication, ...],
) -> tuple[NormalizedMedication, ...]:
    seen: set[str] = set()
    unique = []
    for medication in medications:
        key = medication.medication_id or medication.input_text
        if key in seen:
            continue
        seen.add(key)
        unique.append(medication)
    return tuple(unique)


def _ordered_unique(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)


def _sentence_list(values: tuple[str, ...]) -> str:
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def _collect_source_ids(
    medications: tuple[NormalizedMedication, ...],
    signals: tuple[SafetySignal, ...],
) -> set[str]:
    source_ids = set()
    for medication in medications:
        source_ids.update(medication.source_ids)
        for ingredient in medication.active_ingredients:
            source_ids.update(ingredient.source_ids)
        for drug_class in medication.drug_classes:
            source_ids.update(drug_class.source_ids)
    for signal in signals:
        source_ids.update(signal.source_ids)
    return source_ids


def _signal_sort_key(signal: SafetySignal) -> tuple[int, str, str]:
    return (
        PRIORITY_ORDER.get(signal.review_priority, 99),
        signal.signal_type,
        signal.signal_id,
    )
