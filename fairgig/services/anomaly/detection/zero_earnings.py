from schemas.anomaly import AnomalyFlag, ShiftRecord


def detect_zero_earnings(shifts: list[ShiftRecord]) -> list[AnomalyFlag]:
    flags: list[AnomalyFlag] = []
    for shift in shifts:
        if shift.hours_worked > 0 and shift.net_received == 0:
            flags.append(
                AnomalyFlag(
                    shift_date=shift.date,
                    platform=shift.platform,
                    anomaly_type="zero_earnings",
                    severity="high",
                    confidence=1.0,
                    worker_value=0.0,
                    expected_range={"min": 1, "max": None, "mean": None},
                    explanation=(
                        f"On {shift.date}, you worked {shift.hours_worked} hours on {shift.platform} "
                        "but received Rs. 0. This should be investigated."
                    ),
                )
            )
    return flags
