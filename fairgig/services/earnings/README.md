# FairGig Earnings Service

FastAPI microservice for worker shift logs, CSV bulk imports, screenshot uploads, and verifier review workflow.

## Setup

1. Copy `.env.example` to `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure `database/init.sql` has been applied.

## Run

`uvicorn main:app --port 8002 --reload`

## Endpoints

- `POST /shifts`
- `GET /shifts`
- `GET /shifts/{id}`
- `PATCH /shifts/{id}`
- `DELETE /shifts/{id}`
- `POST /shifts/bulk`
- `POST /shifts/{id}/screenshot`
- `GET /shifts/{id}/screenshot`
- `GET /verification/queue`
- `POST /verification/{shift_id}/review`
- `GET /health`

## Notes

- CSV imports are partial-success by design and return row-level errors.
- Screenshot MIME type validation is enforced.
- Workers can edit/delete only their own unverified records.
