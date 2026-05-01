"""Consumer and professional-review summaries."""

from __future__ import annotations

from medcombo.disclaimers import PRODUCT_STATUS_NOTICE, SENSITIVE_DATA_NOTICE
from medcombo.explain import names
from medcombo.models import ReviewResult
from medcombo.safety_language import require_consumer_safe_text


def build_consumer_summary(result: ReviewResult) -> str:
    lines = [
        "MedCombo consumer health review summary",
        "",
        f"Product status: {PRODUCT_STATUS_NOTICE}",
        f"Sensitive data notice: {SENSITIVE_DATA_NOTICE}",
        "Use this summary to prepare a conversation with a pharmacist or clinician before medication changes.",
        "",
        "Medications entered:",
    ]

    for medication in result.medications:
        if medication.match_status == "matched":
            ingredient_names = names(tuple(ingredient.name for ingredient in medication.active_ingredients))
            lines.append(f"- {medication.input_text} -> {medication.display_name} ({ingredient_names})")
        elif medication.match_status == "ambiguous":
            lines.append(
                f"- {medication.input_text} -> ambiguous match: {names(medication.candidate_names)}"
            )
        else:
            lines.append(f"- {medication.input_text} -> not matched in the demo dataset")

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

    lines.extend([
        "",
        "Source references:",
    ])
    for source in result.sources:
        lines.append(f"- {source.source_id}: {source.title} ({source.publisher}) {source.url}")

    summary = "\n".join(lines)
    return require_consumer_safe_text(summary)


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
