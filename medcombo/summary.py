"""Consumer and professional-review summaries."""

from __future__ import annotations

from medcombo.disclaimers import PRODUCT_STATUS_NOTICE, SENSITIVE_DATA_NOTICE
from medcombo.explain import names
from medcombo.models import ConversationQuestion, MedicationIntakeItem, ReviewResult
from medcombo.safety_language import require_consumer_safe_text


def build_consumer_summary(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...] = (),
    conversation_questions: tuple[ConversationQuestion, ...] = (),
    agent_turns: tuple = (),
) -> str:
    lines = [
        "MedCombo consumer health review summary",
        "",
        f"Product status: {PRODUCT_STATUS_NOTICE}",
        f"Sensitive data notice: {SENSITIVE_DATA_NOTICE}",
        "Use this summary to prepare a conversation with a pharmacist or clinician before medication changes.",
        "",
        "Intake quality and missing information:",
        "",
        "Verified medications:",
    ]

    lines.extend(_verified_medication_lines(result, intake_items))
    lines.extend(["", "Uncertain or unresolved medications:"])
    lines.extend(_uncertain_medication_lines(result, intake_items))
    lines.extend(["", "Missing intake details:"])
    lines.extend(_missing_detail_lines(intake_items))

    lines.extend(["", "User answer history:"])
    lines.extend(_agent_turn_lines(agent_turns))

    if conversation_questions:
        lines.extend(["", "Conversation follow-up prompts:"])
        for question in conversation_questions:
            lines.append(f"- {question.question_text}")
            lines.append(f"  Why this matters: {question.rationale}")

    lines.extend(["", "Supplements entered:"])
    if result.context.supplements:
        for supplement in result.context.supplements:
            lines.append(f"- {supplement}")
    elif "supplements" in result.context.no_information:
        lines.append("- User selected no supplement information")
    else:
        lines.append("- None entered")

    lines.extend(["", "Health context entered:"])
    context_lines = _context_summary_lines(result)
    if context_lines:
        lines.extend(context_lines)
    else:
        lines.append("- None entered")

    if result.signals:
        lines.extend(["", "Review-worthy signals:"])
        for signal in result.signals:
            lines.append(f"- [{signal.review_priority}] {signal.plain_language_explanation}")
            lines.append(f"  Question: {signal.professional_question}")
            lines.append(f"  Rule/source: {signal.rule_id} | {', '.join(signal.source_ids)}")
    else:
        lines.extend([
            "",
            "Review-worthy signals:",
            "- No demo-dataset safety signals were generated. This does not mean the medication list has no risk.",
        ])

    lines.extend(["", "Pharmacist or clinician review checklist:"])
    lines.extend(_professional_checklist_lines(result, intake_items, conversation_questions))

    lines.extend([
        "",
        "Source references:",
    ])
    for source in result.sources:
        lines.append(f"- {source.source_id}: {source.title} ({source.publisher}) {source.url}")

    summary = "\n".join(lines)
    return require_consumer_safe_text(summary)


def _verified_medication_lines(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...],
) -> list[str]:
    lines = []
    if intake_items:
        for item in intake_items:
            medication = item.normalized_medication
            if not medication.is_matched:
                continue
            ingredient_names = names(tuple(ingredient.name for ingredient in medication.active_ingredients))
            detail_summary = _detail_summary(item)
            lines.append(
                f"- {item.raw_text} -> {medication.display_name} ({ingredient_names}); "
                f"verification={item.verification_status}; source={item.source_confidence}; details={detail_summary}"
            )
    else:
        for medication in result.medications:
            if medication.match_status != "matched":
                continue
            ingredient_names = names(tuple(ingredient.name for ingredient in medication.active_ingredients))
            lines.append(f"- {medication.input_text} -> {medication.display_name} ({ingredient_names})")
    return lines or ["- None verified in the demo dataset"]


def _uncertain_medication_lines(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...],
) -> list[str]:
    lines = []
    if intake_items:
        for item in intake_items:
            medication = item.normalized_medication
            if medication.is_matched:
                continue
            if medication.match_status == "ambiguous":
                candidate_text = names(medication.candidate_names)
                lines.append(f"- {item.raw_text}: ambiguous match candidates are {candidate_text}")
            else:
                lines.append(f"- {item.raw_text}: not matched in the demo dataset")
    else:
        for medication in result.medications:
            if medication.match_status == "ambiguous":
                lines.append(
                    f"- {medication.input_text}: ambiguous match candidates are {names(medication.candidate_names)}"
                )
            elif medication.match_status == "unknown":
                lines.append(f"- {medication.input_text}: not matched in the demo dataset")
    return lines or ["- No uncertain medication identities flagged"]


def _missing_detail_lines(intake_items: tuple[MedicationIntakeItem, ...]) -> list[str]:
    if not intake_items:
        return ["- No intake detail state was available"]
    lines = []
    for item in intake_items:
        if item.missing_fields:
            lines.append(f"- {item.raw_text}: missing {names(item.missing_fields)}")
    return lines or ["- No missing details flagged by the MVP intake rules"]


def _agent_turn_lines(agent_turns: tuple) -> list[str]:
    if not agent_turns:
        return ["- No follow-up answers recorded in this summary"]
    lines = []
    for turn in agent_turns:
        answer = turn.user_answer or "No answer captured"
        value = f"; captured={turn.extracted_value}" if turn.extracted_value else ""
        lines.append(
            f"- {turn.question_text} Answer: {answer}. Field={turn.extracted_field}; status={turn.status}{value}"
        )
    return lines


def _professional_checklist_lines(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...],
    conversation_questions: tuple[ConversationQuestion, ...],
) -> list[str]:
    checklist = []
    for item in intake_items:
        checklist.extend(item.professional_review_questions)
    for question in conversation_questions:
        checklist.append(question.question_text)
    for signal in result.signals:
        checklist.append(signal.professional_question)

    ordered = []
    seen = set()
    for item in checklist:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(f"- {item}")
    return ordered or ["- Bring the medication list to a pharmacist or clinician for review if questions remain"]


def _detail_summary(item: MedicationIntakeItem) -> str:
    details = []
    for field_name in ("strength", "dose", "route", "frequency", "formulation"):
        value = getattr(item, field_name)
        if value:
            details.append(f"{field_name}={value}")
    return ", ".join(details) if details else "details not fully captured"


def _context_summary_lines(result: ReviewResult) -> list[str]:
    context = result.context
    lines = []
    if context.demographics:
        lines.append(f"- Demographics: {context.demographics}")
    elif "demographics" in context.no_information:
        lines.append("- Demographics: user selected no information")
    if context.body_info:
        lines.append(f"- Body information: {context.body_info}")
    elif "body_info" in context.no_information:
        lines.append("- Body information: user selected no information")
    if context.conditions:
        lines.append(f"- Chronic conditions or history: {names(context.conditions)}")
    elif "conditions" in context.no_information:
        lines.append("- Chronic conditions or history: user selected no information")
    if context.symptoms:
        lines.append(f"- Current symptoms: {names(context.symptoms)}")
    elif "symptoms" in context.no_information:
        lines.append("- Current symptoms: user selected no information")
    return lines
