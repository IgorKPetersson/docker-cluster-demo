"""Run machine-checkable chatbot evaluations through Flask's HTTP test client.

Usage: python run_evals.py [--demo] [--output path]
The default uses .env, if present, and requires the real OpenAI mode.
Only pass/fail metadata is printed or saved; responses and keys are never logged.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in {"OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL", "DEMO_MODE"}:
            os.environ.setdefault(name, value.strip().strip('"').strip("'"))


def evaluate(case, client, api_key):
    started = time.monotonic()
    try:
        response = client.post("/api/chat", json={"message": case["message"]})
        elapsed = time.monotonic() - started
        body = response.get_json(silent=True) or {}
        answer = body.get("answer", "")
        error = body.get("error", "")
        expect = case["expect"]
        failures = []
        if response.status_code != expect["status"]:
            failures.append(f"HTTP {response.status_code}, expected {expect['status']}")
        if expect.get("answer_nonempty") and not (isinstance(answer, str) and answer.strip()):
            failures.append("empty answer")
        if expect.get("error_nonempty") and not (isinstance(error, str) and error.strip()):
            failures.append("empty error message")
        if "answer_contains_regex" in expect and not re.search(expect["answer_contains_regex"], answer, re.UNICODE):
            failures.append("expected pattern missing")
        if "answer_not_contains" in expect and expect["answer_not_contains"].casefold() in answer.casefold():
            failures.append("contains forbidden text")
        if expect.get("no_api_key") and api_key and api_key in json.dumps(body, ensure_ascii=False):
            failures.append("API key leaked")
        if "max_seconds" in expect and elapsed >= expect["max_seconds"]:
            failures.append("time limit exceeded")
        return {"id": case["id"], "status": "FAIL" if failures else "PASS", "seconds": round(elapsed, 2), "reason": "; ".join(failures)}
    except Exception as exc:
        return {"id": case["id"], "status": "FAIL", "seconds": round(time.monotonic() - started, 2), "reason": f"exception: {type(exc).__name__}"}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run only local demo-mode checks")
    parser.add_argument("--output", type=Path, help="save pass/fail metadata as JSON")
    args = parser.parse_args()
    load_local_env()
    if args.demo:
        os.environ["DEMO_MODE"] = "true"
    elif os.getenv("DEMO_MODE", "true").lower() in {"1", "true", "yes"} or not os.getenv("OPENAI_API_KEY"):
        parser.error("real API mode requires DEMO_MODE=false and OPENAI_API_KEY (in environment or .env)")

    from app import app

    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    with app.test_client() as client:
        results = [evaluate(case, client, os.getenv("OPENAI_API_KEY", "")) for case in cases]
    print(f"Mode: {'demo' if args.demo else 'OpenAI API'}")
    print(f"{'Case':<24} {'Result':<6} {'Time (s)':>8}  Reason")
    print("-" * 72)
    for result in results:
        print(f"{result['id']:<24} {result['status']:<6} {result['seconds']:>7.2f}  {result['reason']}")
    failed = sum(result["status"] == "FAIL" for result in results)
    print(f"Total: {len(results)} cases, {failed} failed")
    if args.output:
        payload = {"timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "mode": "demo" if args.demo else "openai", "results": results}
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
