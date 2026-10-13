FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY app.py engine.py ./
COPY web ./web
COPY data ./data
ENV HOST=0.0.0.0 PORT=8080
USER 65534:65534
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 90 app:app"]
