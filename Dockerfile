FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY scripts ./scripts
RUN mkdir -p data

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./data/incidentiq.db
EXPOSE 8000
# Seed synthetic history (idempotent) then serve on the host-provided port.
CMD ["sh", "-c", "python -m scripts.seed_database && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
