from collections import defaultdict
from datetime import datetime

from schemas.anomaly import AnomalyFlag, ShiftRecord


def detect_income_drops(shifts: list[ShiftRecord]) -> list[AnomalyFlag]:
    monthly = defaultdict(float)
    month_platform = {}

    for shift in shifts:
        month = datetime.strptime(shift.date, "%Y-%m-%d").strftime("%Y-%m")
        monthly[month] += shift.net_received
        month_platform.setdefault(month, shift.platform)

    ordered_months = sorted(monthly.keys())
    if len(ordered_months) < 2:
        return []

    flags: list[AnomalyFlag] = []
    for idx in range(1, len(ordered_months)):
        prev_m = ordered_months[idx - 1]
        cur_m = ordered_months[idx]
        prev_v = monthly[prev_m]
        cur_v = monthly[cur_m]

        if prev_v <= 0:
            continue
        if cur_v >= prev_v * 0.80:
            continue

        drop = (prev_v - cur_v) / prev_v
        confidence = 0.5
        severity = "low"
        if drop > 0.5:
            confidence = 0.95
            severity = "high"
        elif drop > 0.3:
            confidence = 0.75
            severity = "medium"

        flags.append(
            AnomalyFlag(
                shift_date=f"{cur_m}-01",
                platform=month_platform.get(cur_m, "Mixed"),
                anomaly_type="income_drop",
                severity=severity,
                confidence=confidence,
                worker_value=round(cur_v, 2),
                expected_range={
                    "min": round(prev_v * 0.8, 2),
                    "max": round(prev_v * 1.2, 2),
                    "mean": round(prev_v, 2),
                },
                explanation=(
                    f"Your income in {cur_m} was {drop:.0%} lower than in {prev_m}. "
                    "This may indicate fewer shifts, a rate cut, or an account issue."
                ),
            )
        )

    return flags
