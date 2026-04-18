from typing import List, Literal

from pydantic import BaseModel


class ShiftRecord(BaseModel):
    date: str
    platform: str
    hours_worked: float
    gross_earned: float
    platform_deductions: float
    net_received: float


class AnomalyRequest(BaseModel):
    worker_id: str
    shifts: List[ShiftRecord]


class AnomalyFlag(BaseModel):
    shift_date: str
    platform: str
    anomaly_type: Literal[
        "commission_rate_spike",
        "income_drop",
        "zero_earnings",
        "deduction_spike",
    ]
    severity: Literal["low", "medium", "high"]
    confidence: float
    worker_value: float
    expected_range: dict
    explanation: str


class AnomalyResponse(BaseModel):
    worker_id: str
    shifts_analysed: int
    anomalies_found: int
    anomalies: List[AnomalyFlag]
    summary: str
