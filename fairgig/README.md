# FairGig — Gig Worker Income & Rights Platform

SOFTEC 2026 Web Dev Competition

## Quick Start (Start All Services)

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### 1. Database Setup

createdb fairgig
psql fairgig < database/init.sql
cp .env.example .env

# Edit .env with your PostgreSQL credentials and JWT secret

### 2. Seed Data

cd seed && python seed.py

### 3. Start All Services (open 7 terminals or use tmux)

cd services/auth && uvicorn main:app --port 8001 --reload
cd services/earnings && uvicorn main:app --port 8002 --reload
cd services/anomaly && uvicorn main:app --port 8003 --reload
cd services/grievance && npm start
cd services/analytics && uvicorn main:app --port 8005 --reload
cd services/certificate && uvicorn main:app --port 8006 --reload
cd frontend && npm run dev

### 4. Access

Frontend: http://localhost:5173
Auth API docs: http://localhost:8001/docs
Earnings API docs: http://localhost:8002/docs
Anomaly API docs: http://localhost:8003/docs
Grievance API: http://localhost:8004 (see docs/FairGig_API.postman_collection.json)
Analytics API docs: http://localhost:8005/docs
Certificate API docs: http://localhost:8006/docs

### Demo Accounts (created by seed script)

Worker: 03001234567 / demo1234
Verifier: 03007654321 / demo1234
Advocate: 03009999999 / demo1234
