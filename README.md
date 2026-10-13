# ShiftProof — AI Builder Cup 2026 prototype

Evidence-backed maintenance handovers using synthetic records. Fresh project begun 7 October 2026.

## Run

Use Python 3.12. Create a virtual environment and install requirements.lock.txt.
Run `python app.py` and open http://127.0.0.1:8096.
Run `python -m unittest discover -s tests -v` for the 17 checks.
Run `python evaluation/run.py --out evaluation/runs/baseline.json` for the development benchmark.

## Status and limitations

The local keyword baseline, editable sources, quote validation, human review and JSON export work.
The optional Google Gen AI adapter is implemented but live inference and Cloud Run deployment remain unverified.
To configure live mode, use Google's Application Default Credentials and set GOOGLE_CLOUD_PROJECT,
GOOGLE_CLOUD_LOCATION, GEMINI_MODEL and ENABLE_GEMINI=1. Never commit credentials.
The Dockerfile serves Flask through Gunicorn. Start deployments with authenticated access.
Public model calls require cost and abuse controls before release.

Twenty synthetic development cases have draft labels: the keyword baseline matched 8 expected findings,
missed 10, and produced 2 extra predictions. These are category/source-set proxies, not model accuracy.
Exact source quotes do not prove an interpretation is correct. Human acknowledgements are unauthenticated.
No business impact or practitioner validation has been measured. This app does not certify equipment safety.
