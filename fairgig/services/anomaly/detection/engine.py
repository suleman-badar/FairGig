from detection.commission_rate import detect_commission_spikes
from detection.deduction_spike import detect_deduction_spikes
from detection.income_drop import detect_income_drops
from detection.zero_earnings import detect_zero_earnings
from schemas.anomaly import AnomalyFlag, ShiftRecord


def run_all_detectors(shifts: list[ShiftRecord]) -> list[AnomalyFlag]:
    flags: list[AnomalyFlag] = []
    flags.extend(detect_commission_spikes(shifts))
    flags.extend(detect_income_drops(shifts))
    flags.extend(detect_zero_earnings(shifts))
    flags.extend(detect_deduction_spikes(shifts))
    return sorted(flags, key=lambda f: f.confidence, reverse=True)
