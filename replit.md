# IncidentIQ backend

## Run

```bash
PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

The API is backend-only. Configure `HINDSIGHT_API_URL`, `HINDSIGHT_BANK_ID`,
`HINDSIGHT_API_KEY` when required by the Hindsight deployment, and
`GROQ_API_KEY` in environment secrets. See `.env.example` and `README.md`.

## Verification

```bash
PYTHONPATH=. pytest -q backend/tests
```