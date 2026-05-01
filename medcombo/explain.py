"""Consumer explanation helpers."""

from __future__ import annotations

from medcombo.models import DrugClass, Ingredient, NormalizedMedication
from medcombo.safety_language import require_consumer_safe_text


def names(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def medication_names(medications: tuple[NormalizedMedication, ...]) -> tuple[str, ...]:
    return tuple(medication.display_name for medication in medications)


def duplicate_ingredient_explanation(
    ingredient: Ingredient,
    medications: tuple[NormalizedMedication, ...],
) -> str:
    text = (
        f"{names(medication_names(medications))} may contain the same active "
        f"ingredient: {ingredient.name}. A pharmacist or clinician should review "
        "whether this overlap matters for the person's full medication list."
    )
    return require_consumer_safe_text(text)


def duplicate_ingredient_question(
    ingredient: Ingredient,
    medications: tuple[NormalizedMedication, ...],
) -> str:
    text = (
        f"Do these products both contain {ingredient.name}, and should I avoid "
        "doubling this ingredient without professional guidance?"
    )
    return require_consumer_safe_text(text)


def class_overlap_explanation(
    drug_class: DrugClass,
    medications: tuple[NormalizedMedication, ...],
) -> str:
    text = (
        f"{names(medication_names(medications))} are both listed in the "
        f"{drug_class.name} category in the demo knowledge base. This may be "
        "worth reviewing so the user understands why both products are present."
    )
    return require_consumer_safe_text(text)


def class_overlap_question(
    drug_class: DrugClass,
    medications: tuple[NormalizedMedication, ...],
) -> str:
    text = (
        f"Are these {drug_class.name} products intended to be used together for "
        "my situation?"
    )
    return require_consumer_safe_text(text)


def unknown_product_explanation(medication: NormalizedMedication) -> str:
    text = (
        f"MedCombo could not confidently match \"{medication.input_text}\" in the "
        "demo medication dataset. Verify the product label or ask a pharmacist "
        "to identify the active ingredients."
    )
    return require_consumer_safe_text(text)


def unknown_product_question(medication: NormalizedMedication) -> str:
    text = (
        f"Can you help identify the active ingredients in \"{medication.input_text}\" "
        "and check whether it overlaps with my other medications?"
    )
    return require_consumer_safe_text(text)


def ambiguous_product_explanation(medication: NormalizedMedication) -> str:
    candidates = names(medication.candidate_names)
    text = (
        f"MedCombo found more than one possible match for \"{medication.input_text}\": "
        f"{candidates}. Confirm the exact product name, formulation, or label "
        "before relying on the match."
    )
    return require_consumer_safe_text(text)


def ambiguous_product_question(medication: NormalizedMedication) -> str:
    text = (
        f"Can you confirm which product \"{medication.input_text}\" refers to and "
        "whether the formulation matters for my medication review?"
    )
    return require_consumer_safe_text(text)
