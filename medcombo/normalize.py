"""Medication-name normalization against the curated knowledge base."""

from __future__ import annotations

from difflib import get_close_matches

from medcombo.knowledge import KnowledgeBase
from medcombo.models import NormalizedMedication
from medcombo.text import clean_key


def normalize_medication_name(raw_text: str, kb: KnowledgeBase | None = None) -> NormalizedMedication:
    kb = kb or KnowledgeBase.load_demo()
    key = clean_key(raw_text)
    candidate_ids = kb.alias_index.get(key, ())

    if len(candidate_ids) == 1:
        return _matched(raw_text, candidate_ids[0], kb, confidence=1.0)

    if len(candidate_ids) > 1:
        return _ambiguous(raw_text, candidate_ids, kb, confidence=0.5)

    close_aliases = get_close_matches(key, kb.alias_index.keys(), n=3, cutoff=0.88)
    close_ids: list[str] = []
    for alias in close_aliases:
        for medication_id in kb.alias_index[alias]:
            if medication_id not in close_ids:
                close_ids.append(medication_id)

    if len(close_ids) == 1:
        return _matched(raw_text, close_ids[0], kb, confidence=0.86)

    if len(close_ids) > 1:
        return _ambiguous(raw_text, tuple(close_ids), kb, confidence=0.4)

    return NormalizedMedication(
        input_text=raw_text,
        medication_id=None,
        display_name=raw_text.strip() or "Unknown medication",
        normalized_name="",
        rxcui="",
        match_status="unknown",
        match_confidence=0.0,
        active_ingredients=(),
        drug_classes=(),
        source_ids=(),
    )


def normalize_medication_list(raw_inputs: list[str] | tuple[str, ...], kb: KnowledgeBase | None = None) -> tuple[NormalizedMedication, ...]:
    kb = kb or KnowledgeBase.load_demo()
    return tuple(
        normalize_medication_name(item, kb)
        for item in raw_inputs
        if item and item.strip()
    )


def _matched(
    raw_text: str,
    medication_id: str,
    kb: KnowledgeBase,
    confidence: float,
) -> NormalizedMedication:
    record = kb.medication(medication_id)
    return NormalizedMedication(
        input_text=raw_text,
        medication_id=record.medication_id,
        display_name=record.display_name,
        normalized_name=record.normalized_name,
        rxcui=record.rxcui,
        match_status="matched",
        match_confidence=confidence,
        active_ingredients=tuple(kb.ingredient(ingredient_id) for ingredient_id in record.active_ingredients),
        drug_classes=tuple(kb.drug_class(class_id) for class_id in record.drug_classes),
        source_ids=record.source_ids,
    )


def _ambiguous(
    raw_text: str,
    candidate_ids: tuple[str, ...] | list[str],
    kb: KnowledgeBase,
    confidence: float,
) -> NormalizedMedication:
    ordered_ids = tuple(candidate_ids)
    candidate_names = tuple(kb.medication(candidate_id).display_name for candidate_id in ordered_ids)
    return NormalizedMedication(
        input_text=raw_text,
        medication_id=None,
        display_name=raw_text.strip() or "Ambiguous medication",
        normalized_name="",
        rxcui="",
        match_status="ambiguous",
        match_confidence=confidence,
        active_ingredients=(),
        drug_classes=(),
        source_ids=("src_demo_curated",),
        candidate_ids=ordered_ids,
        candidate_names=candidate_names,
    )
