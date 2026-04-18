# FairGig Grievance Service

Node.js/Express service for complaint intake, advocate clustering, and public anonymized community board.

## Setup

1. Copy `.env.example` to `.env`
2. Install dependencies: `npm install`
3. Ensure `database/init.sql` has been applied.

## Run

- Development: `npm run dev`
- Production-like: `npm start`

## Routes

- `POST /complaints`
- `GET /complaints`
- `GET /complaints/:id`
- `PATCH /complaints/:id/status`
- `POST /complaints/:id/tags`
- `POST /complaints/:id/cluster`
- `GET /complaints/:id/similar`
- `POST /clusters`
- `GET /clusters`
- `GET /clusters/:id`
- `PATCH /clusters/:id/status`
- `GET /community`
- `GET /health`

## Notes

- JWT is validated locally using shared `JWT_SECRET`.
- `anonymous_display_id` is generated for public-safe complaint display.
- Global API rate limiting is enabled through `express-rate-limit`.
