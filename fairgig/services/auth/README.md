# FairGig Auth Service

FastAPI microservice for registration, login, token refresh, and profile management.

## Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- JWT (python-jose)

## Setup

1. Copy `.env.example` to `.env`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Ensure `database/init.sql` has been applied.

## Run

`uvicorn main:app --port 8001 --reload`

## Endpoints

- `POST /register`
- `POST /login` (rate-limited 10/min per IP)
- `POST /refresh`
- `GET /me`
- `PATCH /me`
- `GET /health`

## Example Login Request

```json
{
  "phone": "03001234567",
  "password": "demo1234"
}
```

## Example Login Response

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "phone": "03001234567",
    "role": "worker",
    "is_active": true
  }
}
```
