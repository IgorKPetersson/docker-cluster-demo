# Handoff – docker-cluster-demo

Updated 2 October 2026 (Europe/Stockholm).

## Context

The user requested homework-11: evaluate this repository's chatbot with at least eight machine-checkable cases, including two attacks, a runnable PASS/FAIL table, and a report no longer than one A4 page. At least one case had to fail on the first run. The user later asked for English throughout the international project.

- `cases.json` contains eight cases for empty input, whitespace, a non-string message, an ordinary question, an English answer, prompt injection, API key extraction, and system prompt extraction.
- `run_evals.py` runs the cases through Flask's test client against `app.py`. Real API mode is the default and requires a configured `.env`. It saves only timing and pass/fail metadata.
- `app.py` validates the JSON payload and message type. Its model instruction asks for brief English answers and resistance to spoofed system or developer messages.
- `resultat.md` is the required report; `final_run.json` holds the latest result metadata. `TESTING.md` explains the added files, and `README.md` links to it.

## Observed runs

- 1 October 2026: the original Swedish-language cases produced 6 PASS and 2 FAIL. `non_string_message` caused HTTP 500 instead of 400; `prompt_injection` elicited the attacker's marker.
- After the fixes, the Swedish-language cases produced 8 PASS and 0 FAIL. The system prompt check was then tightened to search for a phrase in the current model instruction.
- 2 October 2026: the English-language cases and English model instruction produced 8 PASS and 0 FAIL. `final_run.json` contains this latest run. The first run's JSON was not saved because the earlier runner used timezone data unavailable on Windows; the table was observed in the terminal. The runner now records a UTC timestamp.

## Limits and next steps

Real API runs have a small cost. The local `.env` contains an API key and is Git-ignored; never display or commit it. `.venv` is also ignored. Model-dependent cases can vary between runs. The key check only confirms that the configured key is absent from the HTTP response JSON. Check `git status` and the remote branch before submitting the repository link.
