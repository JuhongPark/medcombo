"""Structured pharmacist review packet generation."""

from __future__ import annotations

from dataclasses import dataclass

from medcombo.disclaimers import PRODUCT_STATUS_NOTICE, SENSITIVE_DATA_NOTICE
from medcombo.explain import names
from medcombo.models import ConversationQuestion, MedicationIntakeItem, ReviewResult, SafetySignal
from medcombo.safety_language import require_consumer_safe_text


LOW_CONFIDENCE_SOURCE_STATUSES = {
    "memory_entered",
    "needs_visual_verification",
    "unverified_manual",
}
DETAIL_FIELDS = ("strength", "dose", "route", "frequency", "formulation")


@dataclass(frozen=True)
class MedicationListReadiness:
    verified_count: int
    ambiguous_count: int
    unknown_count: int
    out_of_scope_count: int
    missing_field_count: int
    low_confidence_source_count: int
    labels: tuple[str, ...]


@dataclass(frozen=True)
class ReviewPacketSection:
    section_id: str
    title: str
    items: tuple[str, ...]


@dataclass(frozen=True)
class ReviewPacket:
    title: str
    readiness: MedicationListReadiness
    notices: tuple[str, ...]
    sections: tuple[ReviewPacketSection, ...]


def build_review_packet(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...] = (),
    conversation_questions: tuple[ConversationQuestion, ...] = (),
    agent_turns: tuple = (),
) -> ReviewPacket:
    readiness = build_medication_list_readiness(result, intake_items)
    sections = (
        _review_snapshot_section(result, readiness),
        _verified_medication_section(result, intake_items),
        _identity_confirmation_section(result, intake_items),
        _missing_details_section(intake_items),
        _duplicate_signals_section(result),
        _interaction_signals_section(result),
        _other_signals_section(result),
        _supplements_section(result),
        _context_section(result),
        _answer_history_section(agent_turns),
        _pharmacist_questions_section(result, intake_items, conversation_questions),
        _evidence_appendix_section(result),
    )
    return ReviewPacket(
        title="MedCombo pharmacist-ready review packet",
        readiness=readiness,
        notices=(
            f"Product status: {PRODUCT_STATUS_NOTICE}",
            f"Sensitive data notice: {SENSITIVE_DATA_NOTICE}",
            "Use this packet to prepare a conversation with a pharmacist or clinician before medication changes.",
        ),
        sections=sections,
    )


def build_medication_list_readiness(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...] = (),
) -> MedicationListReadiness:
    if intake_items:
        verified_count = sum(1 for item in intake_items if item.normalized_medication.is_matched)
        ambiguous_count = sum(1 for item in intake_items if item.match_status == "ambiguous")
        unknown_count = sum(1 for item in intake_items if item.match_status == "unknown")
        missing_field_count = sum(len(item.missing_fields) for item in intake_items)
        low_confidence_source_count = sum(
            1
            for item in intake_items
            if item.source_confidence in LOW_CONFIDENCE_SOURCE_STATUSES
        )
    else:
        verified_count = sum(1 for medication in result.medications if medication.is_matched)
        ambiguous_count = sum(1 for medication in result.medications if medication.match_status == "ambiguous")
        unknown_count = sum(1 for medication in result.medications if medication.match_status == "unknown")
        missing_field_count = 0
        low_confidence_source_count = 0

    out_of_scope_count = len(result.context.supplements)
    labels: list[str] = []
    if ambiguous_count or unknown_count:
        labels.append("needs_identity_review")
    if missing_field_count:
        labels.append("missing_details")
    if low_confidence_source_count:
        labels.append("needs_source_confirmation")
    if out_of_scope_count:
        labels.append("includes_out_of_scope_items")
    if not labels:
        labels.append("ready_for_professional_review")

    return MedicationListReadiness(
        verified_count=verified_count,
        ambiguous_count=ambiguous_count,
        unknown_count=unknown_count,
        out_of_scope_count=out_of_scope_count,
        missing_field_count=missing_field_count,
        low_confidence_source_count=low_confidence_source_count,
        labels=tuple(labels),
    )


def render_review_packet_text(packet: ReviewPacket) -> str:
    lines = [packet.title, ""]
    lines.extend(packet.notices)
    lines.extend(["", "Medication list readiness:"])
    lines.extend(_readiness_lines(packet.readiness))
    for section in packet.sections:
        lines.extend(["", f"{section.title}:"])
        for item in section.items:
            lines.append(f"- {item}")
    return require_consumer_safe_text("\n".join(lines))


def _review_snapshot_section(
    result: ReviewResult,
    readiness: MedicationListReadiness,
) -> ReviewPacketSection:
    items = [
        f"Data version: {result.data_version}",
        f"Recognized medication identities: {readiness.verified_count}",
        f"Ambiguous medication identities: {readiness.ambiguous_count}",
        f"Unknown medication identities: {readiness.unknown_count}",
        f"Review signals in packet: {len(result.signals)}",
        "Signal coverage note: MedCombo only checks the curated demo dataset and review rules. This is not a complete medication safety screen.",
    ]
    if not result.signals:
        items.append(
            "No demo-dataset safety signals were generated. A pharmacist or clinician should still review unresolved products, missing details, and medication questions."
        )
    return ReviewPacketSection("review_snapshot", "Review Snapshot", tuple(items))


def _verified_medication_section(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...],
) -> ReviewPacketSection:
    items: list[str] = []
    if intake_items:
        for item in intake_items:
            medication = item.normalized_medication
            if not medication.is_matched:
                continue
            ingredient_names = names(tuple(ingredient.name for ingredient in medication.active_ingredients))
            detail_summary = _detail_summary(item)
            items.append(
                f"{item.raw_text} -> {medication.display_name} ({ingredient_names}). "
                f"Verification: {item.verification_status}. Source: {item.source_confidence}. "
                f"Captured details: {detail_summary}"
            )
    else:
        for medication in result.medications:
            if medication.match_status != "matched":
                continue
            ingredient_names = names(tuple(ingredient.name for ingredient in medication.active_ingredients))
            items.append(f"{medication.input_text} -> {medication.display_name} ({ingredient_names})")
    return ReviewPacketSection(
        "verified_medications",
        "Verified Medication Items",
        tuple(items) or ("None verified in the demo dataset",),
    )


def _identity_confirmation_section(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...],
) -> ReviewPacketSection:
    items: list[str] = []
    if intake_items:
        for item in intake_items:
            medication = item.normalized_medication
            if medication.is_matched:
                continue
            if medication.match_status == "ambiguous":
                items.append(
                    f"{item.raw_text}: ambiguous match candidates are {names(medication.candidate_names)}"
                )
            else:
                items.append(f"{item.raw_text}: not matched in the demo dataset")
    else:
        for medication in result.medications:
            if medication.match_status == "ambiguous":
                items.append(
                    f"{medication.input_text}: ambiguous match candidates are {names(medication.candidate_names)}"
                )
            elif medication.match_status == "unknown":
                items.append(f"{medication.input_text}: not matched in the demo dataset")
    return ReviewPacketSection(
        "identity_confirmation",
        "Needs Identity Confirmation",
        tuple(items) or ("No unresolved medication identities flagged",),
    )


def _missing_details_section(
    intake_items: tuple[MedicationIntakeItem, ...],
) -> ReviewPacketSection:
    if not intake_items:
        return ReviewPacketSection(
            "missing_details",
            "Missing Dose, Frequency, Route, Or Formulation",
            ("No intake detail state was available",),
        )
    items = []
    for item in intake_items:
        missing_details = tuple(field for field in item.missing_fields if field in DETAIL_FIELDS)
        if missing_details:
            items.append(f"{item.raw_text}: missing {names(missing_details)}")
    return ReviewPacketSection(
        "missing_details",
        "Missing Dose, Frequency, Route, Or Formulation",
        tuple(items) or ("No missing dose, frequency, route, or formulation details flagged",),
    )


def _duplicate_signals_section(result: ReviewResult) -> ReviewPacketSection:
    return ReviewPacketSection(
        "duplicate_active_ingredient_signals",
        "Duplicate Active Ingredient Signals",
        _signal_items(result, ("duplicate_active_ingredient",))
        or ("No duplicate active ingredient signals generated from the demo dataset",),
    )


def _interaction_signals_section(result: ReviewResult) -> ReviewPacketSection:
    return ReviewPacketSection(
        "curated_interaction_review_signals",
        "Curated Interaction Review Signals",
        _signal_items(result, ("possible_interaction",))
        or ("No curated interaction review signals generated from the demo dataset",),
    )


def _other_signals_section(result: ReviewResult) -> ReviewPacketSection:
    target_types = {"duplicate_active_ingredient", "possible_interaction"}
    items = tuple(
        _signal_item(signal)
        for signal in result.signals
        if signal.signal_type not in target_types
    )
    return ReviewPacketSection(
        "other_review_signals",
        "Other Review Signals",
        items or ("No other review signals generated",),
    )


def _supplements_section(result: ReviewResult) -> ReviewPacketSection:
    context = result.context
    if context.supplements:
        items = (
            f"Supplements recorded for professional review: {names(context.supplements)}",
            "This MVP records supplements but does not validate supplement-drug interactions yet.",
        )
    elif "supplements" in context.no_information:
        items = ("User selected no supplement information",)
    else:
        items = ("No supplements entered",)
    return ReviewPacketSection(
        "supplements_and_out_of_scope_items",
        "Supplements And Out-Of-Scope Items",
        items,
    )


def _context_section(result: ReviewResult) -> ReviewPacketSection:
    context = result.context
    items: list[str] = []
    if context.demographics:
        items.append(f"Demographics: {context.demographics}")
    elif "demographics" in context.no_information:
        items.append("Demographics: user selected no information")
    if context.body_info:
        items.append(f"Body information: {context.body_info}")
    elif "body_info" in context.no_information:
        items.append("Body information: user selected no information")
    if context.conditions:
        items.append(f"Chronic conditions or history: {names(context.conditions)}")
    elif "conditions" in context.no_information:
        items.append("Chronic conditions or history: user selected no information")
    if context.symptoms:
        items.append(f"Current symptoms: {names(context.symptoms)}")
    elif "symptoms" in context.no_information:
        items.append("Current symptoms: user selected no information")
    return ReviewPacketSection(
        "context_to_ask_about",
        "Context To Ask About",
        tuple(items) or ("No additional health context entered",),
    )


def _answer_history_section(agent_turns: tuple) -> ReviewPacketSection:
    if not agent_turns:
        return ReviewPacketSection(
            "user_answer_history",
            "User Answer History",
            ("No follow-up answers recorded in this packet",),
        )
    items = []
    for turn in agent_turns:
        answer = turn.user_answer or "No answer captured"
        value = f". Captured value: {turn.extracted_value}" if turn.extracted_value else ""
        items.append(
            f"{turn.question_text} Answer: {answer}. Field: {turn.extracted_field}. "
            f"Status: {turn.status}{value}"
        )
    return ReviewPacketSection("user_answer_history", "User Answer History", tuple(items))


def _pharmacist_questions_section(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...],
    conversation_questions: tuple[ConversationQuestion, ...],
) -> ReviewPacketSection:
    questions: list[str] = []
    for item in intake_items:
        questions.extend(item.professional_review_questions)
    for question in conversation_questions:
        questions.append(question.question_text)
    for signal in result.signals:
        questions.append(signal.professional_question)
    return ReviewPacketSection(
        "pharmacist_questions",
        "Pharmacist Questions",
        _ordered_unique(questions)
        or ("Bring the medication list to a pharmacist or clinician for review if questions remain",),
    )


def _evidence_appendix_section(result: ReviewResult) -> ReviewPacketSection:
    items = [
        f"{source.source_id}: {source.title} ({source.publisher}) {source.url}"
        for source in result.sources
    ]
    return ReviewPacketSection(
        "evidence_appendix",
        "Evidence Appendix",
        tuple(items) or ("No source references attached to this packet",),
    )


def _signal_items(result: ReviewResult, signal_types: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        _signal_item(signal)
        for signal in result.signals
        if signal.signal_type in signal_types
    )


def _signal_item(signal: SafetySignal) -> str:
    lines = [
        f"[{signal.review_priority}] {signal.plain_language_explanation}",
        f"Question: {signal.professional_question}",
        f"Rule/source: {signal.rule_id} | {', '.join(signal.source_ids)}",
    ]
    if signal.clinical_concern:
        lines.append(f"Evidence concern: {signal.clinical_concern}")
    if signal.evidence_summary:
        lines.append(f"Evidence note: {signal.evidence_summary}")
    if signal.patient_specific_modifiers:
        lines.append(f"Context to review: {names(signal.patient_specific_modifiers)}")
    return "\n  ".join(lines)


def _readiness_lines(readiness: MedicationListReadiness) -> tuple[str, ...]:
    return (
        f"- Labels: {names(readiness.labels)}",
        f"- Verified identities: {readiness.verified_count}",
        f"- Ambiguous identities: {readiness.ambiguous_count}",
        f"- Unknown identities: {readiness.unknown_count}",
        f"- Out-of-scope items recorded: {readiness.out_of_scope_count}",
        f"- Missing intake fields: {readiness.missing_field_count}",
        f"- Low-confidence sources: {readiness.low_confidence_source_count}",
    )


def _detail_summary(item: MedicationIntakeItem) -> str:
    details = []
    for field_name in DETAIL_FIELDS:
        value = getattr(item, field_name)
        if value:
            details.append(f"{field_name}={value}")
    return ", ".join(details) if details else "details not fully captured"


def _ordered_unique(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    ordered = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)
