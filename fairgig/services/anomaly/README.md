# FairGig Anomaly Detection Service

This service exposes the judged endpoint for statistical anomaly detection.

## Stack

- Python 3.11
- FastAPI
- Standard library statistics (no numpy/pandas)

## Run

1. `pip install -r requirements.txt`
2. `uvicorn main:app --port 8003 --reload`

## Endpoints

- `POST /detect`
- `GET /health`
- `GET /sample-payload`

## Detectors

- `commission_rate_spike`: flags shifts where deduction rate is above `mean + 2*stdev`
- `income_drop`: flags month-on-month net income drop over 20%
- `zero_earnings`: flags any shift with positive hours and zero net pay
- `deduction_spike`: flags shifts where deduction is over 3x platform median

## POST /detect Request Example

```json
{
  "worker_id": "worker-spike-001",
  "shifts": [
    {
      "date": "2026-02-01",
      "platform": "Careem",
      "hours_worked": 8,
      "gross_earned": 1500,
      "platform_deductions": 300,
      "net_received": 1200
    }
  ]
}
```

## POST /detect Response Example

```json
{
  "worker_id": "worker-spike-001",
  "shifts_analysed": 4,
  "anomalies_found": 1,
  "anomalies": [
    {
      "shift_date": "2026-02-04",
      "platform": "Careem",
      "anomaly_type": "commission_rate_spike",
      "severity": "high",
      "confidence": 0.95,
      "worker_value": 56.25,
      "expected_range": { "min": 16, "max": 30, "mean": 22 },
      "explanation": "On 2026-02-04, Careem deducted 56% of your gross earnings. Your usual deduction is 22%. This is 95% likely to be unusual."
    }
  ],
  "summary": "Detected 1 anomaly flag(s) that may require your attention."
}
```

## Local Test Commands

```bash
curl -X GET http://localhost:8003/health
curl -X GET http://localhost:8003/sample-payload
curl -X POST http://localhost:8003/detect \
  -H "Content-Type: application/json" \
  -d @tests/sample_payloads/commission_spike.json
```

## Notes

- If fewer than 3 shifts are provided, service returns a clear summary with no anomalies.
- Explanations are plain English and user-friendly for live demos.
