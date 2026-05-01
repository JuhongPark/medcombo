"""Dependency-free MedCombo web demo."""

from __future__ import annotations

import argparse
import html
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from medcombo.rules import review_medication_list
from medcombo.summary import build_consumer_summary


DEFAULT_MEDICATIONS = "Tylenol\nNyQuil\nZoloft"


class MedComboHandler(BaseHTTPRequestHandler):
    server_version = "MedComboDemo/0.1"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_text("ok\n")
            return
        self._send_html(render_page(DEFAULT_MEDICATIONS, None))

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)
        medications_text = "\n".join(form.get("medications", [""]))
        medication_lines = [
            line.strip()
            for line in medications_text.splitlines()
            if line.strip()
        ]
        result = review_medication_list(medication_lines) if medication_lines else None
        self._send_html(render_page(medications_text, result))

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


def render_page(medications_text: str, result) -> str:
    escaped_text = html.escape(medications_text)
    result_html = render_result(result) if result else render_empty_state()
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
      grid-template-columns: minmax(280px, 390px) 1fr;
      gap: 20px;
      align-items: start;
    }}
    form, .section {{
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
    textarea {{
      width: 100%;
      min-height: 220px;
      resize: vertical;
      border: 1px solid #c9d0da;
      border-radius: 6px;
      padding: 12px;
      font: 15px/1.45 Arial, Helvetica, sans-serif;
      color: var(--text);
      background: #fff;
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
    .fineprint {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    .section h2 {{
      margin: 0 0 14px;
      font-size: 19px;
      letter-spacing: 0;
    }}
    .med-list, .signal-list, .source-list {{
      display: grid;
      gap: 10px;
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
      <div class="status">Consumer-first healthcare AI system in development. Not clinically validated or FDA-cleared for real-world medication decisions.</div>
    </div>
  </header>
  <main class="wrap">
    <div class="grid">
      <form method="post">
        <label for="medications">Medication list</label>
        <textarea id="medications" name="medications" spellcheck="false">{escaped_text}</textarea>
        <button type="submit">Review list</button>
        <div class="fineprint">Use pharmacist or clinician review before medication changes.</div>
      </form>
      <div class="stack">
        {result_html}
      </div>
    </div>
  </main>
</body>
</html>"""


def render_empty_state() -> str:
    return """
    <section class="section">
      <h2>Review</h2>
      <div class="item">
        <div class="item-title">Ready</div>
        <div class="meta">Enter one medication or product per line.</div>
      </div>
    </section>
    """


def render_result(result) -> str:
    medications = "".join(render_medication(medication) for medication in result.medications)
    signals = "".join(render_signal(signal) for signal in result.signals)
    if not signals:
        signals = """
        <div class="item">
          <div class="item-title">No demo signals</div>
          <div class="meta">No demo-dataset safety signals were generated. This does not mean the medication list has no risk.</div>
        </div>
        """
    summary = html.escape(build_consumer_summary(result))
    sources = "".join(render_source(source) for source in result.sources)
    return f"""
    <section class="section">
      <h2>Normalized medications</h2>
      <div class="med-list">{medications}</div>
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
    return f"""
    <div class="item">
      <div class="item-title"><span>{signal_type}</span><span class="tag {priority}">{priority}</span></div>
      <div>{explanation}</div>
      <div class="question"><strong>Question:</strong> {question}</div>
      <div class="meta">Rule/source: {rule} | {sources}</div>
    </div>
    """


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
