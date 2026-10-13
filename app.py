"""Local and Cloud Run API; keep cloud service authenticated for initial deployment."""
import json
import os
from pathlib import Path
from threading import BoundedSemaphore
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException
from engine import analyze, ModelResponseError

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder='web', static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 64000
model_slots = BoundedSemaphore(2)


def live_enabled():
    return os.getenv('ENABLE_GEMINI') == '1' and bool(os.getenv('GOOGLE_CLOUD_PROJECT') and os.getenv('GEMINI_MODEL'))


@app.after_request
def response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    return response


@app.get('/')
def index():
    return send_from_directory(ROOT / 'web', 'index.html')


@app.get('/api/scenarios')
def scenarios():
    return jsonify(json.loads((ROOT / 'data/scenarios.json').read_text()))


@app.get('/api/config')
def config():
    return jsonify(gemini_enabled=live_enabled(), model=os.getenv('GEMINI_MODEL') if live_enabled() else None)


@app.get('/health')
def health():
    return jsonify(status='ok')


@app.post('/api/analyze')
def analyze_request():
    if not request.is_json:
        return jsonify(error='Send a JSON request.'), 415
    payload = request.get_json()
    if not isinstance(payload, dict):
        return jsonify(error='Request must be an object.'), 400
    mode = payload.get('mode', 'replay')
    if mode == 'gemini' and not live_enabled():
        return jsonify(error='Live Gemini is not configured. Use the clearly labelled local baseline.'), 503
    if not model_slots.acquire(blocking=False):
        return jsonify(error='Analysis is busy. Please try again shortly.'), 429
    try:
        return jsonify(analyze(payload.get('sources'), mode))
    except ModelResponseError:
        return jsonify(error='Gemini returned an unsupported draft. No findings were accepted. Please retry or review the source records.'), 502
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except Exception:
        app.logger.warning('Model request failed; source text and credentials omitted.')
        return jsonify(error='Gemini request failed. No baseline fallback was used. Check model access and server credentials.'), 502
    finally:
        model_slots.release()


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code


if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '8096')), debug=False)
