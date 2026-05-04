"""Development-stage medication intake agent."""

from __future__ import annotations

import re
from dataclasses import replace

from medcombo.intake import (
    DOSE_RE,
    FORMULATION_TERMS,
    FREQUENCY_TERMS,
    SOURCE_CONFIDENCE,
    STRENGTH_RE,
    build_medication_intake,
    generate_conversation_questions,
    refresh_medication_intake_item,
)
from medcombo.knowledge import KnowledgeBase
from medcombo.models import (
    AgentTurn,
    ConversationQuestion,
    MedicationAgentSession,
    MedicationIntakeItem,
    NormalizedMedication,
)
from medcombo.normalize import normalize_medication_name
from medcombo.text import clean_key, stable_id_part


UNKNOWN_ANSWERS = {
    "i don't know",
    "i do not know",
    "dont know",
    "don't know",
    "do not know",
    "not sure",
    "unsure",
    "unknown",
    "no idea",
    "idk",
}


def start_intake_agent_session(
    raw_inputs: list[str] | tuple[str, ...],
    source_type: str = "manual",
    kb: KnowledgeBase | None = None,
    max_questions: int | None = None,
) -> MedicationAgentSession:
    kb = kb or KnowledgeBase.load_demo()
    intake_items = build_medication_intake(raw_inputs, source_type=source_type, kb=kb)
    active_questions = generate_conversation_questions(intake_items, max_questions=max_questions)
    return MedicationAgentSession(
        session_id=f"agent_{stable_id_part('|'.join(item.raw_text for item in intake_items))}",
        intake_items=intake_items,
        active_questions=active_questions,
        completed=not active_questions,
    )


def answer_agent_question(
    session: MedicationAgentSession,
    question_id: str,
    answer_text: str,
    kb: KnowledgeBase | None = None,
    max_questions: int | None = None,
) -> MedicationAgentSession:
    kb = kb or KnowledgeBase.load_demo()
    question = _find_question(session.active_questions, question_id)
    item = session.intake_items[question.item_index]
    updated_item, extracted_value, status = _apply_answer(item, question, answer_text, kb)
    updated_items = _replace_item(session.intake_items, question.item_index, updated_item)
    answered_question_ids = _ordered_unique(session.answered_question_ids + (question_id,))
    active_questions = _filter_answered_questions(
        generate_conversation_questions(updated_items, max_questions=None),
        answered_question_ids,
    )
    if max_questions is not None:
        active_questions = active_questions[:max_questions]
    turn = AgentTurn(
        turn_id=f"turn_{len(session.turns) + 1}_{stable_id_part(question_id + answer_text)}",
        question_id=question.question_id,
        item_index=question.item_index,
        question_type=question.question_type,
        question_text=question.question_text,
        user_answer=answer_text.strip(),
        extracted_field=question.field_name,
        extracted_value=extracted_value,
        status=status,
    )
    return replace(
        session,
        intake_items=updated_items,
        active_questions=active_questions,
        answered_question_ids=answered_question_ids,
        turns=session.turns + (turn,),
        completed=not active_questions,
    )


def _find_question(
    questions: tuple[ConversationQuestion, ...],
    question_id: str,
) -> ConversationQuestion:
    for question in questions:
        if question.question_id == question_id:
            return question
    raise ValueError(f"Unknown active question: {question_id}")


def _apply_answer(
    item: MedicationIntakeItem,
    question: ConversationQuestion,
    answer_text: str,
    kb: KnowledgeBase,
) -> tuple[MedicationIntakeItem, str, str]:
    answer = answer_text.strip()
    if not answer or _is_unknown_answer(answer):
        return item, "", "needs_review"

    if question.field_name == "identity":
        return _apply_identity_answer(item, answer, kb)
    if question.field_name == "information_source":
        source_type = _parse_source_type(answer)
        return (
            refresh_medication_intake_item(item, source_type=source_type),
            SOURCE_CONFIDENCE.get(source_type, "unverified_manual"),
            "captured",
        )
    if question.field_name == "strength":
        value = _regex_or_answer(STRENGTH_RE, answer)
        return refresh_medication_intake_item(item, strength=value), value, "captured"
    if question.field_name == "dose":
        value = _regex_or_answer(DOSE_RE, answer)
        return refresh_medication_intake_item(item, dose=value), value, "captured"
    if question.field_name == "frequency":
        value = _term_or_answer(FREQUENCY_TERMS, answer)
        return refresh_medication_intake_item(item, frequency=value), value, "captured"
    if question.field_name == "formulation":
        value = _term_or_answer(FORMULATION_TERMS, answer)
        return refresh_medication_intake_item(item, formulation=value), value, "captured"

    return item, "", "needs_review"


def _apply_identity_answer(
    item: MedicationIntakeItem,
    answer: str,
    kb: KnowledgeBase,
) -> tuple[MedicationIntakeItem, str, str]:
    medication = _candidate_answer_match(item, answer, kb)
    if medication is None:
        medication = normalize_medication_name(answer, kb)
    if medication.match_status == "unknown":
        return item, "", "needs_review"
    medication = replace(medication, input_text=item.raw_text)
    return (
        refresh_medication_intake_item(item, normalized_medication=medication),
        medication.display_name,
        "captured",
    )


def _candidate_answer_match(
    item: MedicationIntakeItem,
    answer: str,
    kb: KnowledgeBase,
) -> NormalizedMedication | None:
    answer_key = clean_key(answer)
    for candidate_id, candidate_name in zip(
        item.normalized_medication.candidate_ids,
        item.normalized_medication.candidate_names,
    ):
        candidate_key = clean_key(candidate_name)
        if answer_key in candidate_key or candidate_key in answer_key:
            return normalize_medication_name(kb.medication(candidate_id).display_name, kb)
    return None


def _parse_source_type(answer: str) -> str:
    key = clean_key(answer)
    if "pharmacy" in key:
        return "pharmacy_list"
    if "visit" in key or "summary" in key or "record" in key:
        return "medical_summary"
    if "photo" in key or "picture" in key or "image" in key:
        return "photo"
    if "caregiver" in key:
        return "confirmed_caregiver_memory"
    if "memory" in key or "remember" in key:
        return "confirmed_memory"
    if "label" in key or "bottle" in key or "package" in key:
        return "label"
    return "manual"


def _regex_or_answer(pattern: re.Pattern[str], answer: str) -> str:
    match = pattern.search(answer)
    return match.group(0) if match else answer


def _term_or_answer(terms: tuple[str, ...], answer: str) -> str:
    answer_key = clean_key(answer)
    for term in terms:
        term_key = clean_key(term)
        if term_key and term_key in answer_key:
            return term
    return answer


def _is_unknown_answer(answer: str) -> bool:
    return clean_key(answer) in {clean_key(value) for value in UNKNOWN_ANSWERS}


def _replace_item(
    items: tuple[MedicationIntakeItem, ...],
    index: int,
    updated_item: MedicationIntakeItem,
) -> tuple[MedicationIntakeItem, ...]:
    return tuple(
        updated_item if item_index == index else item
        for item_index, item in enumerate(items)
    )


def _filter_answered_questions(
    questions: tuple[ConversationQuestion, ...],
    answered_question_ids: tuple[str, ...],
) -> tuple[ConversationQuestion, ...]:
    answered = set(answered_question_ids)
    return tuple(question for question in questions if question.question_id not in answered)


def _ordered_unique(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)
