import csv
import io
from datetime import date

from schemas.shift import ShiftCreate


def parse_shift_csv(content: bytes) -> tuple[list[ShiftCreate], list[dict]]:
    records: list[ShiftCreate] = []
    errors: list[dict] = []

    required = {
        "platform",
        "shift_date",
        "hours_worked",
        "gross_earned",
        "platform_deductions",
        "net_received",
    }

    stream = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(stream)
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        return [], [{"row": 0, "reason": "missing required columns"}]

    for row_num, row in enumerate(reader, start=2):
        try:
            payload = ShiftCreate(
                platform=row.get("platform", "").strip(),
                shift_date=date.fromisoformat((row.get("shift_date") or "").strip()),
                hours_worked=float(row.get("hours_worked", 0)),
                gross_earned=float(row.get("gross_earned", 0)),
                platform_deductions=float(row.get("platform_deductions", 0)),
                net_received=float(row.get("net_received", 0)),
                notes=(row.get("notes") or "").strip() or None,
            )
            records.append(payload)
        except Exception as exc:
            errors.append({"row": row_num, "reason": str(exc)})

    return records, errors
