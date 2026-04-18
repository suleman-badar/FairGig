from collections import defaultdict
from statistics import median

from schemas.anomaly import AnomalyFlag, ShiftRecord


def detect_deduction_spikes(shifts: list[ShiftRecord]) -> list[AnomalyFlag]:
    per_platform = defaultdict(list)
    for shift in shifts:
        per_platform[shift.platform].append(shift.platform_deductions)

    medians = {platform: median(values) for platform, values in per_platform.items() if values}

    flags: list[AnomalyFlag] = []
    for shift in shifts:
        med = medians.get(shift.platform)
        if med is None or med == 0:
            continue
        if shift.platform_deductions <= (3 * med):
            continue

        flags.append(
            AnomalyFlag(
                shift_date=shift.date,
                platform=shift.platform,
                anomaly_type="deduction_spike",
                severity="medium",
                confidence=0.8,
                worker_value=round(shift.platform_deductions, 2),
                expected_range={"min": 0, "max": round(3 * med, 2), "mean": round(med, 2)},
                explanation=(
                    f"On {shift.date}, {shift.platform} deducted Rs. {shift.platform_deductions:,.0f}. "
                    f"Your usual {shift.platform} deduction is around Rs. {med:,.0f}."
                ),
            )
        )
    return flags
