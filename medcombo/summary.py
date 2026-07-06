"""Compatibility wrapper for review packet summaries."""

from __future__ import annotations

from medcombo.models import ConversationQuestion, MedicationIntakeItem, ReviewResult
from medcombo.review_packet import build_review_packet, render_review_packet_text


def build_consumer_summary(
    result: ReviewResult,
    intake_items: tuple[MedicationIntakeItem, ...] = (),
    conversation_questions: tuple[ConversationQuestion, ...] = (),
    agent_turns: tuple = (),
) -> str:
    packet = build_review_packet(
        result,
        intake_items=intake_items,
        conversation_questions=conversation_questions,
        agent_turns=agent_turns,
    )
    return render_review_packet_text(packet)
