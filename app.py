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
        return jsonify(error="Enter a question first."), 400

    if is_demo_mode():
        return jsonify(
            answer=(
                f'Demo response: The app received your question: "{message}". '
                "Add OPENAI_API_KEY and disable DEMO_MODE to receive answers "
                "from the OpenAI API."
            )
        )

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify(error="OPENAI_API_KEY is missing from the container environment."), 503

    try:
        base_url = os.getenv("OPENAI_BASE_URL", "").strip()
        client = OpenAI(**({"base_url": base_url} if base_url else {}))
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions="Answer briefly and clearly in English.",
            input=message,
        )
        return jsonify(answer=response.output_text)
    except Exception as exc:
        app.logger.exception("OpenAI request failed")
        return jsonify(error=f"API request failed: {exc}"), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
