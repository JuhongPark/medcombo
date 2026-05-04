"""Medication intake state and deterministic clarification prompts."""

from __future__ import annotations

import re
from dataclasses import replace

from medcombo.explain import names
from medcombo.knowledge import KnowledgeBase
from medcombo.models import ConversationQuestion, MedicationIntakeItem, NormalizedMedication
from medcombo.normalize import normalize_medication_name
from medcombo.safety_language import require_consumer_safe_text
from medcombo.text import stable_id_part


STRENGTH_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|g|gram|grams|ml|mL|units?|iu|%)\b",
    re.IGNORECASE,
)
DOSE_RE = re.compile(
    r"\b(?:\d+(?:\.\d+)?|one|two|three|half)\s?"
    r"(?:tablet|tablets|tab|tabs|capsule|capsules|cap|caps|pill|pills|"
    r"puff|puffs|drop|drops|spray|sprays|teaspoon|teaspoons|ml|mL)\b",
    re.IGNORECASE,
)

FORMULATION_TERMS = (
    "extended release",
    "delayed release",
    "immediate release",
    "tablet",
    "capsule",
    "liquid",
    "syrup",
    "inhaler",
    "cream",
    "ointment",
    "patch",
    "drops",
    "spray",
    "er",
    "xr",
    "xl",
    "cd",
)
FREQUENCY_TERMS = (
    "once daily",
    "twice daily",
    "three times daily",
    "four times daily",
    "daily",
    "nightly",
    "weekly",
    "morning",
    "evening",
    "bedtime",
    "as needed",
    "prn",
    "every ",
    "per day",
    "a day",
    "bid",
    "tid",
    "qid",
)
ROUTE_TERMS = (
    "by mouth",
    "oral",
    "inhaled",
    "inhalation",
    "topical",
    "under the tongue",
    "sublingual",
    "eye",
    "ear",
    "nasal",
)

SOURCE_CONFIDENCE = {
    "label": "label_verified",
    "pharmacy_list": "pharmacy_list_verified",
    "medical_summary": "document_based",
    "photo": "needs_visual_verification",
    "caregiver_memory": "memory_entered",
    "memory": "memory_entered",
    "confirmed_caregiver_memory": "memory_entered",
    "confirmed_memory": "memory_entered",
    "manual": "unverified_manual",
}

DETAIL_FIELDS = ("strength", "dose", "route", "frequency", "formulation")


def build_medication_intake(
    raw_inputs: list[str] | tuple[str, ...],
    source_type: str = "manual",
    kb: KnowledgeBase | None = None,
) -> tuple[MedicationIntakeItem, ...]:
    kb = kb or KnowledgeBase.load_demo()
    cleaned_inputs = tuple(item.strip() for item in raw_inputs if item and item.strip())
    normalized_medications = tuple(
        _normalize_intake_line(item, kb)
        for item in cleaned_inputs
    )
    return tuple(
        _build_intake_item(medication, source_type)
        for medication in normalized_medications
    )


def generate_conversation_questions(
    items: tuple[MedicationIntakeItem, ...],
    max_questions: int | None = None,
) -> tuple[ConversationQuestion, ...]:
    questions: list[ConversationQuestion] = []
    for index, item in enumerate(items):
        questions.extend(_questions_for_item(index, item))
    ordered_questions = tuple(sorted(questions, key=lambda question: (question.priority, question.item_index, question.question_id)))
    if max_questions is None:
        return ordered_questions
    return ordered_questions[:max_questions]


def refresh_medication_intake_item(
    item: MedicationIntakeItem,
    normalized_medication: NormalizedMedication | None = None,
    source_type: str | None = None,
    strength: str | None = None,
    dose: str | None = None,
    route: str | None = None,
    frequency: str | None = None,
    formulation: str | None = None,
    last_dose_taken: str | None = None,
    actual_use_notes: str | None = None,
) -> MedicationIntakeItem:
    medication = normalized_medication or item.normalized_medication
    selected_source_type = source_type or item.source_type
    details = {
        "strength": item.strength,
        "dose": item.dose,
        "route": item.route,
        "frequency": item.frequency,
        "formulation": item.formulation,
    }
    overrides = {
        "strength": strength,
        "dose": dose,
        "route": route,
        "frequency": frequency,
        "formulation": formulation,
    }
    for field_name, value in overrides.items():
        if value is not None:
            details[field_name] = value.strip()
    missing_fields = _missing_fields(medication, details, selected_source_type)
    review_questions = _professional_review_questions(medication, missing_fields)
    return MedicationIntakeItem(
        raw_text=item.raw_text,
        source_type=selected_source_type,
        source_confidence=SOURCE_CONFIDENCE.get(selected_source_type, "unverified_manual"),
        normalized_medication=medication,
        candidate_medications=medication.candidate_names,
        selected_medication_id=medication.medication_id,
        match_status=medication.match_status,
        verification_status=_verification_status(medication),
        strength=details["strength"],
        dose=details["dose"],
        route=details["route"],
        frequency=details["frequency"],
        formulation=details["formulation"],
        last_dose_taken=last_dose_taken if last_dose_taken is not None else item.last_dose_taken,
        actual_use_notes=actual_use_notes if actual_use_notes is not None else item.actual_use_notes,
        missing_fields=missing_fields,
        professional_review_questions=review_questions,
    )


def _normalize_intake_line(raw_text: str, kb: KnowledgeBase) -> NormalizedMedication:
    medication = normalize_medication_name(raw_text, kb)
    if medication.match_status != "unknown":
        return medication

    candidate_text = _candidate_identity_text(raw_text)
    if candidate_text == raw_text:
        return medication

    retry = normalize_medication_name(candidate_text, kb)
    if retry.match_status == "unknown":
        return medication
    return replace(retry, input_text=raw_text)


def _candidate_identity_text(raw_text: str) -> str:
    candidate = STRENGTH_RE.sub(" ", raw_text)
    candidate = DOSE_RE.sub(" ", candidate)
    for terms in (FREQUENCY_TERMS, ROUTE_TERMS):
        for term in terms:
            cleaned_term = term.strip()
            if not cleaned_term:
                continue
            candidate = re.sub(
                rf"\b{re.escape(cleaned_term)}\b",
                " ",
                candidate,
                flags=re.IGNORECASE,
            )
    candidate = re.sub(r"\s+", " ", candidate).strip(" ,;-")
    return candidate or raw_text


def _build_intake_item(
    medication: NormalizedMedication,
    source_type: str,
) -> MedicationIntakeItem:
    details = _extract_details(medication.input_text)
    verification_status = _verification_status(medication)
    source_confidence = SOURCE_CONFIDENCE.get(source_type, "unverified_manual")
    missing_fields = _missing_fields(medication, details, source_type)
    review_questions = _professional_review_questions(medication, missing_fields)
    return MedicationIntakeItem(
        raw_text=medication.input_text,
        source_type=source_type,
        source_confidence=source_confidence,
        normalized_medication=medication,
        candidate_medications=medication.candidate_names,
        selected_medication_id=medication.medication_id,
        match_status=medication.match_status,
        verification_status=verification_status,
        strength=details["strength"],
        dose=details["dose"],
        route=details["route"],
        frequency=details["frequency"],
        formulation=details["formulation"],
        missing_fields=missing_fields,
        professional_review_questions=review_questions,
    )


def _extract_details(raw_text: str) -> dict[str, str]:
    text = raw_text.strip()
    text_lower = f" {text.lower()} "
    return {
        "strength": _first_regex_match(STRENGTH_RE, text),
        "dose": _first_regex_match(DOSE_RE, text),
        "route": _first_term_match(ROUTE_TERMS, text_lower),
        "frequency": _first_term_match(FREQUENCY_TERMS, text_lower),
        "formulation": _first_term_match(FORMULATION_TERMS, text_lower),
    }


def _first_regex_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(0) if match else ""


def _first_term_match(terms: tuple[str, ...], text_lower: str) -> str:
    for term in terms:
        normalized_term = f" {term.lower()} "
        if normalized_term in text_lower:
            return term
    return ""


def _verification_status(medication: NormalizedMedication) -> str:
    if medication.match_status == "matched":
        return "matched_by_name"
    if medication.match_status == "ambiguous":
        return "ambiguous_needs_selection"
    return "unknown_product"


def _missing_fields(
    medication: NormalizedMedication,
    details: dict[str, str],
    source_type: str,
) -> tuple[str, ...]:
    fields: list[str] = []
    if medication.match_status in {"unknown", "ambiguous"}:
        fields.append("identity")
    if source_type in {"manual", "memory", "caregiver_memory"}:
        fields.append("information_source")
    if medication.match_status == "matched":
        for field_name in ("strength", "dose", "frequency", "formulation"):
            if not details[field_name]:
                fields.append(field_name)
    return tuple(fields)


def _professional_review_questions(
    medication: NormalizedMedication,
    missing_fields: tuple[str, ...],
) -> tuple[str, ...]:
    questions: list[str] = []
    if "identity" in missing_fields:
        if medication.match_status == "ambiguous":
            question = (
                f"Can you confirm which product \"{medication.input_text}\" refers to "
                "before reviewing the rest of my medication list?"
            )
        else:
            question = (
                f"Can you help identify \"{medication.input_text}\" and check its active "
                "ingredients against my other medications?"
            )
        questions.append(require_consumer_safe_text(question))
    missing_detail_fields = tuple(
        field_name
        for field_name in ("strength", "dose", "frequency", "formulation")
        if field_name in missing_fields
    )
    if missing_detail_fields:
        question = (
            f"Can you verify the {names(missing_detail_fields)} for "
            f"\"{medication.input_text}\"?"
        )
        questions.append(require_consumer_safe_text(question))
    if "information_source" in missing_fields:
        question = (
            f"Can you confirm \"{medication.input_text}\" against a bottle label, "
            "pharmacy list, or medication record?"
        )
        questions.append(require_consumer_safe_text(question))
    return tuple(questions)


def _questions_for_item(
    item_index: int,
    item: MedicationIntakeItem,
) -> tuple[ConversationQuestion, ...]:
    questions = []
    for field_name in item.missing_fields:
        question_type = _question_type(field_name, item)
        question_text = _question_text(field_name, item)
        rationale = _question_rationale(field_name, item)
        questions.append(
            ConversationQuestion(
                question_id=f"q_{item_index}_{field_name}_{stable_id_part(item.raw_text)}",
                item_index=item_index,
                raw_text=item.raw_text,
                question_type=question_type,
                field_name=field_name,
                question_text=require_consumer_safe_text(question_text),
                rationale=require_consumer_safe_text(rationale),
                priority=_question_priority(field_name),
            )
        )
    return tuple(questions)


def _question_type(field_name: str, item: MedicationIntakeItem) -> str:
    if field_name == "identity" and item.match_status == "unknown":
        return "identify_unknown_product"
    if field_name == "identity":
        return "select_ambiguous_product"
    if field_name == "information_source":
        return "confirm_information_source"
    return f"confirm_{field_name}"


def _question_text(field_name: str, item: MedicationIntakeItem) -> str:
    if field_name == "identity" and item.match_status == "unknown":
        return (
            f"I could not match \"{item.raw_text}\" in the demo dataset. What exact "
            "product name or active ingredients are listed on the label?"
        )
    if field_name == "identity":
        candidates = names(item.candidate_medications)
        return (
            f"I found more than one possible match for \"{item.raw_text}\": "
            f"{candidates}. Which one matches the label?"
        )
    if field_name == "information_source":
        return (
            f"Did you copy \"{item.raw_text}\" from a bottle label, a pharmacy list, "
            "a medical visit summary, a photo, or memory?"
        )
    if field_name == "strength":
        return f"What strength is listed for \"{item.raw_text}\" such as 500 mg or 10 mg?"
    if field_name == "dose":
        return f"How much of \"{item.raw_text}\" do you take at one time?"
    if field_name == "frequency":
        return f"How often do you take \"{item.raw_text}\"?"
    if field_name == "formulation":
        return (
            f"Does the label for \"{item.raw_text}\" say tablet, capsule, liquid, "
            "inhaler, patch, ER, XR, XL, or another formulation?"
        )
    return f"What information is listed for \"{item.raw_text}\"?"


def _question_rationale(field_name: str, item: MedicationIntakeItem) -> str:
    if field_name == "identity":
        return "Medication identity must be clarified before first-pass screening can be interpreted."
    if field_name == "information_source":
        return "The review packet should show whether this entry came from a label, record, photo, or memory."
    return f"The review packet is missing the {field_name} for this medication entry."


def _question_priority(field_name: str) -> int:
    order = {
        "identity": 0,
        "information_source": 1,
        "strength": 2,
        "dose": 3,
        "frequency": 4,
        "formulation": 5,
    }
    return order.get(field_name, 99)
