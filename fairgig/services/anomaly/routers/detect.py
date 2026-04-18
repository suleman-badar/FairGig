from fastapi import APIRouter

from detection.engine import run_all_detectors
from schemas.anomaly import AnomalyRequest, AnomalyResponse

router = APIRouter(tags=["anomaly"])


@router.post("/detect", response_model=AnomalyResponse)
def detect(payload: AnomalyRequest):
    if len(payload.shifts) < 3:
        return AnomalyResponse(
            worker_id=payload.worker_id,
            shifts_analysed=len(payload.shifts),
            anomalies_found=0,
            anomalies=[],
            summary="Not enough data to detect patterns. Log at least 7 shifts for anomaly detection.",
        )

    flags = run_all_detectors(payload.shifts)
    summary = "No major anomalies found in recent shift data."
    if flags:
        summary = f"Detected {len(flags)} anomaly flag(s) that may require your attention."

    return AnomalyResponse(
        worker_id=payload.worker_id,
        shifts_analysed=len(payload.shifts),
        anomalies_found=len(flags),
        anomalies=flags,
        summary=summary,
    )


@router.get("/health")
def health():
    return {"status": "ok", "service": "anomaly-detection"}


@router.get("/sample-payload")
def sample_payload():
    return {
        "worker_id": "worker-demo-001",
        "shifts": [
            {
                "date": "2026-03-01",
                "platform": "Careem",
                "hours_worked": 8,
                "gross_earned": 1500,
                "platform_deductions": 300,
                "net_received": 1200,
            },
            {
                "date": "2026-03-02",
                "platform": "Careem",
                "hours_worked": 7,
                "gross_earned": 1400,
                "platform_deductions": 280,
                "net_received": 1120,
            },
        ],
    }
