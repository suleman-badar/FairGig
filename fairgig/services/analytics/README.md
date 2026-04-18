# FairGig Analytics Service

Read-only FastAPI service that exposes privacy-safe aggregate analytics.

## Setup

1. Copy `.env.example` to `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure `analytics_reader` DB role is created and granted view access only.

## Run

`uvicorn main:app --port 8005 --reload`

## Endpoints

- `GET /analytics/commission-trends`
- `GET /analytics/worker-median`
- `GET /analytics/income-distribution`
- `GET /analytics/vulnerability-flags` (advocate/admin)
- `GET /analytics/top-complaints`
- `GET /health`

## Privacy Model

- Service uses restricted DB credentials (`ANALYTICS_DB_USER` / `ANALYTICS_DB_PASSWORD`).
- Core metrics come from `analytics.*` views with minimum-group-size protections.
