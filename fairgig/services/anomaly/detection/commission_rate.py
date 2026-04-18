from statistics import mean, stdev

from schemas.anomaly import AnomalyFlag, ShiftRecord


def detect_commission_spikes(shifts: list[ShiftRecord]) -> list[AnomalyFlag]:
    rates = [
        s.platform_deductions / s.gross_earned
        for s in shifts
        if s.gross_earned > 0 and s.platform_deductions > 0
    ]
    if len(rates) < 3:
        return []

    mu = mean(rates)
    sigma = stdev(rates)
    if sigma == 0:
        return []

    flags: list[AnomalyFlag] = []
    threshold = mu + (2 * sigma)

    for shift in shifts:
        if shift.gross_earned <= 0:
            continue
        rate = shift.platform_deductions / shift.gross_earned
        if rate <= threshold:
            continue

        z_score = (rate - mu) / sigma
        confidence = min(max(z_score / 4, 0.0), 1.0)

        severity = "low"
        if z_score >= 3.5:
            severity = "high"
        elif z_score >= 2.5:
            severity = "medium"

        flags.append(
            AnomalyFlag(
                shift_date=shift.date,
                platform=shift.platform,
                anomaly_type="commission_rate_spike",
                severity=severity,
                confidence=round(confidence, 2),
                worker_value=round(rate * 100, 2),
                expected_range={
                    "min": round(max((mu - sigma) * 100, 0), 2),
                    "max": round((mu + (2 * sigma)) * 100, 2),
                    "mean": round(mu * 100, 2),
                },
                explanation=(
                    f"On {shift.date}, {shift.platform} deducted {rate:.0%} of your gross earnings. "
                    f"Your usual deduction is {mu:.0%}. This is {confidence:.0%} likely to be unusual."
                ),
            )
        )

    return flags
