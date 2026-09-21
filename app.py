import os

from flask import Flask, jsonify, render_template, request
from openai import OpenAI


app = Flask(__name__)


def is_demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "true").lower() in {"1", "true", "yes"}


@app.get("/")
def index():
    return render_template(
        "index.html",
        demo_mode=is_demo_mode(),
        platform=os.getenv("PLATFORM", "Docker"),
    )


@app.get("/health")
def health():
    return jsonify(status="ok", mode="demo" if is_demo_mode() else "openai")


@app.post("/api/chat")
def chat():
    message = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not message:
        return jsonify(error="Skriv en fråga först."), 400

    if is_demo_mode():
        return jsonify(
            answer=(
                "Demo-svar: Appen tog emot din fråga: "
                f"\u201d{message}\u201d. Lägg till OPENAI_API_KEY och stäng av "
                "DEMO_MODE för att få svar från OpenAI API."
            )
        )

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify(error="OPENAI_API_KEY saknas i containerns miljö."), 503

    try:
        base_url = os.getenv("OPENAI_BASE_URL", "").strip()
        client = OpenAI(**({"base_url": base_url} if base_url else {}))
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions="Svara kort, tydligt och på svenska.",
            input=message,
        )
        return jsonify(answer=response.output_text)
    except Exception as exc:
        app.logger.exception("OpenAI-anropet misslyckades")
        return jsonify(error=f"API-anropet misslyckades: {exc}"), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
