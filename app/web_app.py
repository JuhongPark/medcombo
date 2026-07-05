"""Dependency-free MedCombo web demo."""

from __future__ import annotations

import argparse
import html
import uuid
from dataclasses import dataclass, replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from medcombo.agent import answer_agent_question, start_intake_agent_session
from medcombo.disclaimers import PRODUCT_STATUS_NOTICE, SENSITIVE_DATA_NOTICE
from medcombo.rules import review_consumer_intake
from medcombo.summary import build_consumer_summary


DEFAULT_MEDICATIONS = "Tylenol\nNyQuil\nZoloft"
NO_INFORMATION_LABELS = {
    "supplements": "No supplement information",
    "demographics": "No demographic information",
    "body_info": "No body information",
    "conditions": "No chronic condition or history information",
    "symptoms": "No current symptom information",
}
SESSION_STORE = {}


@dataclass(frozen=True)
class WebSessionState:
    agent_session: object
    medications_text: str
    supplements_text: str
    demographics_text: str
    body_info_text: str
    conditions_text: str
    symptoms_text: str
    no_information: tuple[str, ...]
    source_type: str


class MedComboHandler(BaseHTTPRequestHandler):
    server_version = "MedComboDemo/0.1"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_text("ok\n")
            return
        self._send_html(
            render_page(
                medications_text=DEFAULT_MEDICATIONS,
                supplements_text="",
                demographics_text="",
                body_info_text="",
                conditions_text="",
                symptoms_text="",
                no_information=(),
                source_type="manual",
                error_message="",
                result=None,
                intake_items=(),
                conversation_questions=(),
                agent_session=None,
                web_session_id="",
            )
        )

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)
        action = _form_value(form, "action") or "review"
        if action == "reset":
            self._send_html(
                render_page(
                    medications_text=DEFAULT_MEDICATIONS,
                    supplements_text="",
                    demographics_text="",
                    body_info_text="",
                    conditions_text="",
                    symptoms_text="",
                    no_information=(),
                    source_type="manual",
                    error_message="",
                    result=None,
                    intake_items=(),
                    conversation_questions=(),
                    agent_session=None,
                    web_session_id="",
                )
            )
            return

        medications_text = _form_value(form, "medications")
        supplements_text = _form_value(form, "supplements")
        demographics_text = _form_value(form, "demographics")
        body_info_text = _form_value(form, "body_info")
        conditions_text = _form_value(form, "conditions")
        symptoms_text = _form_value(form, "symptoms")
        source_type = _form_value(form, "source_type") or "manual"
        no_information = _no_information_values(form)
        if "supplements" in no_information:
            supplements_text = ""
        if "demographics" in no_information:
            demographics_text = ""
        if "body_info" in no_information:
            body_info_text = ""
        if "conditions" in no_information:
            conditions_text = ""
        if "symptoms" in no_information:
            symptoms_text = ""
        medication_lines = [
            line.strip()
            for line in medications_text.splitlines()
            if line.strip()
        ]
        error_message = ""
        result = None
        intake_items = ()
        conversation_questions = ()
        agent_session = None
        web_session_id = _form_value(form, "web_session_id")
        if action == "answer_question":
            state = SESSION_STORE.get(web_session_id)
            if state is None:
                error_message = "The development intake session was not found. Run the review again."
            else:
                medications_text = state.medications_text
                supplements_text = state.supplements_text
                demographics_text = state.demographics_text
                body_info_text = state.body_info_text
                conditions_text = state.conditions_text
                symptoms_text = state.symptoms_text
                no_information = state.no_information
                source_type = state.source_type
                question_id = _form_value(form, "question_id")
                answer_text = _form_value(form, "answer_text")
                agent_session = state.agent_session
                if answer_text.strip():
                    try:
                        agent_session = answer_agent_question(
                            agent_session,
                            question_id,
                            answer_text,
                            max_questions=8,
                        )
                    except ValueError as exc:
                        error_message = str(exc)
                else:
                    error_message = "Enter an answer, or type I don't know if you are unsure."
                state = replace(state, agent_session=agent_session)
                SESSION_STORE[web_session_id] = state
                intake_items = agent_session.intake_items
                conversation_questions = agent_session.active_questions
                result = review_from_session_state(state)
        elif medication_lines:
            agent_session = start_intake_agent_session(
                medication_lines,
                source_type=source_type,
                max_questions=8,
            )
            web_session_id = f"web_{uuid.uuid4().hex[:12]}"
            state = WebSessionState(
                agent_session=agent_session,
                medications_text=medications_text,
                supplements_text=supplements_text,
                demographics_text=demographics_text,
                body_info_text=body_info_text,
                conditions_text=conditions_text,
                symptoms_text=symptoms_text,
                no_information=no_information,
                source_type=source_type,
            )
            SESSION_STORE[web_session_id] = state
            intake_items = agent_session.intake_items
            conversation_questions = agent_session.active_questions
            result = review_from_session_state(state)
        else:
            error_message = "Medication information is required. Enter at least one prescription, OTC product, or medication name."
        self._send_html(
            render_page(
                medications_text=medications_text,
                supplements_text=supplements_text,
                demographics_text=demographics_text,
                body_info_text=body_info_text,
                conditions_text=conditions_text,
                symptoms_text=symptoms_text,
                no_information=no_information,
                source_type=source_type,
                error_message=error_message,
                result=result,
                intake_items=intake_items,
                conversation_questions=conversation_questions,
                agent_session=agent_session,
                web_session_id=web_session_id,
            )
        )

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_html(self, content: str) -> None:
        encoded = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_text(self, content: str) -> None:
        encoded = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def _form_value(form: dict[str, list[str]], key: str) -> str:
    return "\n".join(form.get(key, [""]))


def _no_information_values(form: dict[str, list[str]]) -> tuple[str, ...]:
    values = []
    for key in NO_INFORMATION_LABELS:
        if f"no_{key}" in form:
            values.append(key)
    return tuple(values)


def review_from_session_state(state: WebSessionState):
    review_lines = [
        item.normalized_medication.display_name
        if item.normalized_medication.is_matched
        else item.raw_text
        for item in state.agent_session.intake_items
    ]
    return review_consumer_intake(
        review_lines,
        supplements=state.supplements_text,
        demographics=state.demographics_text,
        body_info=state.body_info_text,
        conditions=state.conditions_text,
        symptoms=state.symptoms_text,
        no_information=state.no_information,
    )


def render_page(
    medications_text: str,
    supplements_text: str,
    demographics_text: str,
    body_info_text: str,
    conditions_text: str,
    symptoms_text: str,
    no_information: tuple[str, ...],
    source_type: str,
    error_message: str,
    result,
    intake_items: tuple = (),
    conversation_questions: tuple = (),
    agent_session=None,
    web_session_id: str = "",
) -> str:
    escaped_medications = html.escape(medications_text)
    escaped_supplements = html.escape(supplements_text)
    escaped_demographics = html.escape(demographics_text)
    escaped_body_info = html.escape(body_info_text)
    escaped_conditions = html.escape(conditions_text)
    escaped_symptoms = html.escape(symptoms_text)
    result_html = (
        render_result(
            result,
            intake_items,
            conversation_questions,
            agent_session=agent_session,
            web_session_id=web_session_id,
        )
        if result
        else render_empty_state(error_message)
    )
    no_supplements_checked = checked_attr("supplements", no_information)
    no_demographics_checked = checked_attr("demographics", no_information)
    no_body_info_checked = checked_attr("body_info", no_information)
    no_conditions_checked = checked_attr("conditions", no_information)
    no_symptoms_checked = checked_attr("symptoms", no_information)
    source_type_options = render_source_type_options(source_type)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MedCombo</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #19202a;
      --muted: #5b6573;
      --line: #d9dee7;
      --accent: #0f6b63;
      --accent-strong: #0b4f49;
      --warn: #8a5a00;
      --unknown: #5e6470;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    .wrap {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }}
    .topbar {{
      min-height: 72px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}
    h1 {{
      margin: 0;
      font-size: 26px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .status {{
      max-width: 560px;
      color: var(--muted);
      font-size: 14px;
      text-align: right;
    }}
    main {{
      padding: 28px 0 42px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(300px, 430px) 1fr;
      gap: 20px;
      align-items: start;
    }}
    .review-form, .section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    label {{
      display: block;
      margin-bottom: 10px;
      font-weight: 700;
      font-size: 15px;
    }}
    textarea, input, select {{
      width: 100%;
      border: 1px solid #c9d0da;
      border-radius: 6px;
      padding: 12px;
      font: 15px/1.45 Arial, Helvetica, sans-serif;
      color: var(--text);
      background: #fff;
    }}
    textarea {{ resize: vertical; }}
    textarea {{
      min-height: 108px;
    }}
    .medications-input {{
      min-height: 170px;
    }}
    .form-section {{
      margin-bottom: 16px;
    }}
    .form-section:last-of-type {{
      margin-bottom: 0;
    }}
    .required {{
      color: var(--warn);
      font-size: 13px;
      font-weight: 700;
      margin-left: 4px;
    }}
    .checkbox-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    .checkbox-row input {{
      width: 16px;
      height: 16px;
      padding: 0;
      flex: 0 0 auto;
    }}
    .error {{
      border-left: 4px solid #b42318;
      background: #fff1f0;
      color: #5b130f;
      padding: 10px 12px;
      font-size: 13px;
      margin-bottom: 14px;
    }}
    button {{
      width: 100%;
      min-height: 44px;
      margin-top: 12px;
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: #fff;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
    }}
    button:hover {{ background: var(--accent-strong); }}
    button.secondary {{
      background: #e8edf1;
      color: #26313f;
    }}
    button.secondary:hover {{ background: #dbe2e8; }}
    .answer-form {{
      margin-top: 12px;
      display: grid;
      gap: 10px;
    }}
    .answer-actions {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }}
    .answer-actions button {{
      width: auto;
      min-width: 132px;
      margin-top: 0;
      padding: 0 16px;
    }}
    .turn-list {{
      display: grid;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .turn {{
      padding: 8px 10px;
      border-left: 3px solid var(--line);
      background: #f8fafb;
      font-size: 13px;
    }}
    .fineprint {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    .notice {{
      border-left: 4px solid var(--warn);
      background: #fff8e8;
      padding: 10px 12px;
      color: #3a2a00;
      font-size: 13px;
      margin-bottom: 14px;
    }}
    .section h2 {{
      margin: 0 0 14px;
      font-size: 19px;
      letter-spacing: 0;
    }}
    .med-list, .signal-list, .source-list, .chat-list {{
      display: grid;
      gap: 10px;
    }}
    .chat-message {{
      border-left: 4px solid var(--accent);
    }}
    .speaker {{
      color: var(--accent-strong);
      font-weight: 700;
      font-size: 13px;
      margin-bottom: 4px;
    }}
    .field-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }}
    .field-chip {{
      border-radius: 999px;
      background: #eef4f3;
      color: #174f49;
      padding: 3px 8px;
      font-size: 12px;
    }}
    .item {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
    }}
    .item-title {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 6px;
      font-weight: 700;
    }}
    .tag {{
      flex: 0 0 auto;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 12px;
      color: #fff;
      background: var(--accent);
      white-space: nowrap;
    }}
    .tag.prompt_review {{ background: var(--warn); }}
    .tag.routine_review {{ background: var(--accent); }}
    .tag.unknown {{ background: var(--unknown); }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
    }}
    .question {{
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
      color: #26313f;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      margin: 0;
      font: 13px/1.45 Arial, Helvetica, sans-serif;
      color: #273142;
    }}
    .stack {{
      display: grid;
      gap: 16px;
    }}
    @media (max-width: 860px) {{
      .topbar {{
        align-items: flex-start;
        flex-direction: column;
        padding: 18px 0;
      }}
      .status {{ text-align: left; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <h1>MedCombo</h1>
      <div class="status">Consumer-first healthcare AI system. {html.escape(PRODUCT_STATUS_NOTICE)}</div>
    </div>
  </header>
  <main class="wrap">
    <div class="grid">
      <form class="review-form" method="post">
        {render_error(error_message)}
        <div class="notice">{html.escape(SENSITIVE_DATA_NOTICE)}</div>
        <div class="form-section">
          <label for="medications">Medication list<span class="required">required</span></label>
          <textarea class="medications-input" id="medications" name="medications" spellcheck="false" required placeholder="One prescription or OTC medicine per line">{escaped_medications}</textarea>
        </div>
        <div class="form-section">
          <label for="source_type">How this medication list was entered</label>
          <select id="source_type" name="source_type">{source_type_options}</select>
        </div>
        <div class="form-section">
          <label for="supplements">Supplements</label>
          <textarea id="supplements" name="supplements" spellcheck="false" placeholder="Vitamin D&#10;Fish oil&#10;Magnesium">{escaped_supplements}</textarea>
          <label class="checkbox-row"><input type="checkbox" name="no_supplements" value="1"{no_supplements_checked}> No supplement information</label>
        </div>
        <div class="form-section">
          <label for="demographics">Demographic information</label>
          <textarea id="demographics" name="demographics" spellcheck="false" placeholder="Age range, sex, pregnancy status, or other context the user chooses to provide">{escaped_demographics}</textarea>
          <label class="checkbox-row"><input type="checkbox" name="no_demographics" value="1"{no_demographics_checked}> No demographic information</label>
        </div>
        <div class="form-section">
          <label for="body_info">Body information</label>
          <textarea id="body_info" name="body_info" spellcheck="false" placeholder="Height, weight, kidney or liver notes, blood pressure context, or other relevant body information">{escaped_body_info}</textarea>
          <label class="checkbox-row"><input type="checkbox" name="no_body_info" value="1"{no_body_info_checked}> No body information</label>
        </div>
        <div class="form-section">
          <label for="conditions">Chronic conditions or history</label>
          <textarea id="conditions" name="conditions" spellcheck="false" placeholder="One condition or history item per line">{escaped_conditions}</textarea>
          <label class="checkbox-row"><input type="checkbox" name="no_conditions" value="1"{no_conditions_checked}> No chronic condition or history information</label>
        </div>
        <div class="form-section">
          <label for="symptoms">Current symptoms</label>
          <textarea id="symptoms" name="symptoms" spellcheck="false" placeholder="One symptom or concern per line">{escaped_symptoms}</textarea>
          <label class="checkbox-row"><input type="checkbox" name="no_symptoms" value="1"{no_symptoms_checked}> No current symptom information</label>
        </div>
        <button type="submit" name="action" value="review">Review list</button>
        <button class="secondary" type="submit" name="action" value="reset" formnovalidate>Start over</button>
        <div class="fineprint">Use pharmacist or clinician review before medication changes.</div>
      </form>
      <div class="stack">
        {result_html}
      </div>
    </div>
  </main>
</body>
</html>"""


def checked_attr(key: str, no_information: tuple[str, ...]) -> str:
    return " checked" if key in no_information else ""


def selected_attr(value: str, selected_value: str) -> str:
    return " selected" if value == selected_value else ""


def render_source_type_options(selected_value: str) -> str:
    options = (
        ("manual", "Typed manually or mixed source"),
        ("label", "Copied from bottle or product label"),
        ("pharmacy_list", "Copied from pharmacy medication list"),
        ("medical_summary", "Copied from visit summary or medical record"),
        ("photo", "Read from a photo"),
        ("memory", "Entered from memory"),
        ("caregiver_memory", "Entered from caregiver memory"),
    )
    return "".join(
        f"""<option value="{html.escape(value)}"{selected_attr(value, selected_value)}>{html.escape(label)}</option>"""
        for value, label in options
    )


def render_error(error_message: str) -> str:
    if not error_message:
        return ""
    return f"""<div class="error">{html.escape(error_message)}</div>"""


def render_empty_state(error_message: str = "") -> str:
    detail = (
        html.escape(error_message)
        if error_message
        else "Enter at least one medication. Optional health details can be entered or marked as no information."
    )
    return """
    <section class="section">
      <h2>Review</h2>
      <div class="item">
        <div class="item-title">Ready</div>
        <div class="meta">""" + detail + """</div>
      </div>
    </section>
    """


def render_result(
    result,
    intake_items: tuple = (),
    conversation_questions: tuple = (),
    agent_session=None,
    web_session_id: str = "",
) -> str:
    medications = "".join(render_medication(medication) for medication in result.medications)
    if not medications:
        medications = """
        <div class="item">
          <div class="item-title">No medications entered</div>
          <div class="meta">The current review includes only additional health context.</div>
        </div>
        """
    signals = "".join(render_signal(signal) for signal in result.signals)
    if not signals:
        signals = """
        <div class="item">
          <div class="item-title">No demo signals</div>
          <div class="meta">No demo-dataset safety signals were generated. This does not mean the medication list has no risk.</div>
        </div>
        """
    intake_quality = render_intake_quality(intake_items)
    conversation = render_conversation_questions(
        conversation_questions,
        agent_session=agent_session,
        web_session_id=web_session_id,
    )
    summary = html.escape(
        build_consumer_summary(
            result,
            intake_items=intake_items,
            conversation_questions=conversation_questions,
            agent_turns=agent_session.turns if agent_session else (),
        )
    )
    context = render_context(result.context)
    sources = "".join(render_source(source) for source in result.sources)
    return f"""
    <section class="section">
      <h2>Normalized medications</h2>
      <div class="med-list">{medications}</div>
    </section>
    <section class="section">
      <h2>Intake quality</h2>
      <div class="med-list">{intake_quality}</div>
    </section>
    <section class="section">
      <h2>Guided clarification chat</h2>
      <div class="chat-list">{conversation}</div>
    </section>
    <section class="section">
      <h2>Additional health context</h2>
      <div class="med-list">{context}</div>
    </section>
    <section class="section">
      <h2>Review-worthy signals</h2>
      <div class="signal-list">{signals}</div>
    </section>
    <section class="section">
      <h2>Pharmacist or clinician summary</h2>
      <div class="item"><pre>{summary}</pre></div>
    </section>
    <section class="section">
      <h2>Sources</h2>
      <div class="source-list">{sources}</div>
    </section>
    """


def render_intake_quality(intake_items: tuple) -> str:
    if not intake_items:
        return """
        <div class="item">
          <div class="item-title">No intake state</div>
          <div class="meta">Medication intake state appears after a review is run.</div>
        </div>
        """
    return "".join(render_intake_item(item) for item in intake_items)


def render_intake_item(item) -> str:
    title = html.escape(item.raw_text)
    status = html.escape(item.verification_status)
    source = html.escape(item.source_confidence)
    normalized = html.escape(item.normalized_medication.display_name)
    tag = html.escape(item.match_status)
    if item.missing_fields:
        chips = "".join(
            f"""<span class="field-chip">{html.escape(field.replace("_", " "))}</span>"""
            for field in item.missing_fields
        )
    else:
        chips = """<span class="field-chip">no missing fields flagged</span>"""
    questions = "".join(
        f"""<div class="question"><strong>Review question:</strong> {html.escape(question)}</div>"""
        for question in item.professional_review_questions
    )
    return f"""
    <div class="item">
      <div class="item-title"><span>{title}</span><span class="tag {tag}">{status}</span></div>
      <div class="meta">Candidate: {normalized}</div>
      <div class="meta">Source confidence: {source}</div>
      <div class="field-list">{chips}</div>
      {questions}
    </div>
    """


def render_conversation_questions(
    conversation_questions: tuple,
    agent_session=None,
    web_session_id: str = "",
) -> str:
    turns = render_agent_turns(agent_session.turns if agent_session else ())
    if not conversation_questions:
        return """
        <div class="item chat-message">
          <div class="speaker">Assistant</div>
          <div>No first-pass clarification questions were generated. Keep the label or pharmacy list available for professional review.</div>
        </div>
        """ + turns
    intro = """
    <div class="item chat-message">
      <div class="speaker">Assistant</div>
      <div>I will ask for facts that help prepare a pharmacist or clinician review. Unknown answers can stay marked for review.</div>
    </div>
    """
    active_form = render_active_question_form(conversation_questions[0], web_session_id)
    queued_questions = "".join(
        render_conversation_question(question)
        for question in conversation_questions[1:]
    )
    return turns + intro + active_form + queued_questions


def render_agent_turns(turns: tuple) -> str:
    if not turns:
        return ""
    entries = "".join(
        f"""
        <div class="turn">
          <div><strong>Question:</strong> {html.escape(turn.question_text)}</div>
          <div><strong>Answer:</strong> {html.escape(turn.user_answer or "No answer captured")}</div>
          <div class="meta">Captured field: {html.escape(turn.extracted_field)} | Status: {html.escape(turn.status)}</div>
        </div>
        """
        for turn in turns
    )
    return f"""
    <div class="item chat-message">
      <div class="speaker">Conversation history</div>
      <div class="turn-list">{entries}</div>
    </div>
    """


def render_active_question_form(question, web_session_id: str) -> str:
    return f"""
    <div class="item chat-message">
      <div class="speaker">Assistant</div>
      <div>{html.escape(question.question_text)}</div>
      <div class="meta">{html.escape(question.rationale)}</div>
      <form class="answer-form" method="post">
        <input type="hidden" name="action" value="answer_question">
        <input type="hidden" name="web_session_id" value="{html.escape(web_session_id)}">
        <input type="hidden" name="question_id" value="{html.escape(question.question_id)}">
        <label for="answer_text_{html.escape(question.question_id)}">Your answer</label>
        <div class="answer-actions">
          <input id="answer_text_{html.escape(question.question_id)}" name="answer_text" autocomplete="off" placeholder="Type an answer or I don't know">
          <button type="submit">Send answer</button>
        </div>
      </form>
    </div>
    """


def render_conversation_question(question) -> str:
    return f"""
    <div class="item chat-message">
      <div class="speaker">Assistant</div>
      <div>{html.escape(question.question_text)}</div>
      <div class="meta">{html.escape(question.rationale)}</div>
    </div>
    """


def render_context(context) -> str:
    items = []
    if context.supplements:
        items.append(("Supplements", ", ".join(context.supplements)))
    elif "supplements" in context.no_information:
        items.append(("Supplements", "User selected no supplement information"))
    if context.demographics:
        items.append(("Demographics", context.demographics))
    elif "demographics" in context.no_information:
        items.append(("Demographics", "User selected no demographic information"))
    if context.body_info:
        items.append(("Body information", context.body_info))
    elif "body_info" in context.no_information:
        items.append(("Body information", "User selected no body information"))
    if context.conditions:
        items.append(("Chronic conditions or history", ", ".join(context.conditions)))
    elif "conditions" in context.no_information:
        items.append(("Chronic conditions or history", "User selected no condition or history information"))
    if context.symptoms:
        items.append(("Current symptoms", ", ".join(context.symptoms)))
    elif "symptoms" in context.no_information:
        items.append(("Current symptoms", "User selected no symptom information"))
    if not items:
        return """
        <div class="item">
          <div class="item-title">No additional context entered</div>
          <div class="meta">The current review only uses the medication list.</div>
        </div>
        """
    return "".join(
        f"""
        <div class="item">
          <div class="item-title">{html.escape(title)}</div>
          <div class="meta">{html.escape(value)}</div>
        </div>
        """
        for title, value in items
    )


def render_medication(medication) -> str:
    title = html.escape(medication.display_name)
    input_text = html.escape(medication.input_text)
    tag = html.escape(medication.match_status)
    if medication.match_status == "matched":
        ingredients = ", ".join(ingredient.name for ingredient in medication.active_ingredients)
        classes = ", ".join(drug_class.name for drug_class in medication.drug_classes)
        body = f"""
          <div class="meta">Input: {input_text}</div>
          <div class="meta">Ingredients: {html.escape(ingredients)}</div>
          <div class="meta">Classes: {html.escape(classes)}</div>
        """
    elif medication.match_status == "ambiguous":
        candidates = ", ".join(medication.candidate_names)
        body = f"""
          <div class="meta">Input: {input_text}</div>
          <div class="meta">Possible matches: {html.escape(candidates)}</div>
        """
    else:
        body = f"""
          <div class="meta">Input: {input_text}</div>
          <div class="meta">No match in the demo dataset.</div>
        """
    return f"""
    <div class="item">
      <div class="item-title"><span>{title}</span><span class="tag {tag}">{tag}</span></div>
      {body}
    </div>
    """


def render_signal(signal) -> str:
    priority = html.escape(signal.review_priority)
    explanation = html.escape(signal.plain_language_explanation)
    question = html.escape(signal.professional_question)
    rule = html.escape(signal.rule_id)
    sources = html.escape(", ".join(signal.source_ids))
    signal_type = html.escape(signal.signal_type.replace("_", " "))
    evidence = render_signal_evidence(signal)
    return f"""
    <div class="item">
      <div class="item-title"><span>{signal_type}</span><span class="tag {priority}">{priority}</span></div>
      <div>{explanation}</div>
      <div class="question"><strong>Question:</strong> {question}</div>
      {evidence}
      <div class="meta">Rule/source: {rule} | {sources}</div>
    </div>
    """


def render_signal_evidence(signal) -> str:
    if not (signal.clinical_concern or signal.evidence_summary or signal.patient_specific_modifiers):
        return ""
    lines = []
    if signal.clinical_concern:
        lines.append(f"""<div class="meta">Evidence concern: {html.escape(signal.clinical_concern)}</div>""")
    if signal.evidence_summary:
        lines.append(f"""<div class="meta">Evidence note: {html.escape(signal.evidence_summary)}</div>""")
    if signal.patient_specific_modifiers:
        modifiers = html.escape(", ".join(signal.patient_specific_modifiers))
        lines.append(f"""<div class="meta">Context to review: {modifiers}</div>""")
    return "".join(lines)


def render_source(source) -> str:
    title = html.escape(source.title)
    publisher = html.escape(source.publisher)
    url = html.escape(source.url)
    source_id = html.escape(source.source_id)
    return f"""
    <div class="item">
      <div class="item-title">{title}</div>
      <div class="meta">{source_id} | {publisher}</div>
      <div class="meta">{url}</div>
    </div>
    """


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8010, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MedComboHandler)
    print(f"MedCombo demo running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
