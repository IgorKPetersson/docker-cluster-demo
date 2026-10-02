# Chatbot testing

This repository began as a demonstration of one chatbot running in Docker, Docker Compose, and Kubernetes. The files below were added for **homework-11**, which evaluates the chatbot as a product. They do not change how the Docker variants start.

| File | Purpose |
|---|---|
| `cases.json` | Eight test cases with assertions checked by code, including two attack cases. |
| `run_evals.py` | Sends each question to `/api/chat` through Flask and prints a PASS/FAIL table. |
| `resultat.md` | Required submission report with dates, initial failures, changes, and final results. |
| `final_run.json` | Saved timing and PASS/FAIL results from the latest run; no answers or keys. |
| `AGENTS.md`, `HANDOFF.md` | Project notes for continuing the work; they are not evaluation results. |

The first run found two problems: a non-text message caused HTTP 500, and a prompt injection affected the reply. `app.py` was updated with type validation and clearer model instructions. The current English-language evaluation passed all eight cases on 2 October 2026. Details and limitations are in [resultat.md](resultat.md).

To rerun the evaluation, install `requirements.txt` and configure your **own** API key in the local, Git-ignored `.env` file with `DEMO_MODE=false`. Then run `python run_evals.py --output final_run.json` in the project directory. The script uses Flask's local test client, so Docker does not need to be running. Never submit `.env` or the API key.
