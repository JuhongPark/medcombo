"""Consumer and professional-review summaries."""

from __future__ import annotations

from medcombo.explain import names
from medcombo.models import ReviewResult
from medcombo.safety_language import require_consumer_safe_text


def build_consumer_summary(result: ReviewResult) -> str:
    lines = [
        "MedCombo medication review summary",
        "",
        "Product status: This system is in development and is not clinically validated or FDA-cleared for real-world medication decisions.",
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
