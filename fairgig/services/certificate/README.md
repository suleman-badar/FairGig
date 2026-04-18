# FairGig Certificate Service

FastAPI service that generates printable income certificates from verified shift data.

## Setup

1. Copy `.env.example` to `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure earnings service is running.

## Run

`uvicorn main:app --port 8006 --reload`

## Endpoints

- `POST /certificate`
- `GET /certificate/preview/{worker_id}`
- `GET /health`

## Request Body

```json
{
  "worker_id": "uuid",
  "from_date": "2026-01-01",
  "to_date": "2026-01-31"
}
```

## Notes

- Validates authenticated user matches `worker_id` (unless admin).
- Renders HTML with print-friendly CSS for landlord/bank sharing.
