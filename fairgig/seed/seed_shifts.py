import random
from datetime import date, timedelta


def _platform_for_category(category):
    if category == 'ride_hailing':
        return random.choice(['Careem', 'Bykea', 'inDrive'])
    if category == 'food_delivery':
        return random.choice(['Foodpanda', 'Cheetay'])
    if category == 'freelance':
        return random.choice(['Freelance_Upwork', 'Freelance_Fiverr', 'Freelance_Other'])
    return random.choice(['Domestic', 'Other'])


def _earnings(platform):
    if platform == 'Careem':
        gross = random.uniform(800, 1800)
        commission = random.uniform(0.20, 0.30)
    elif platform == 'Bykea':
        gross = random.uniform(600, 1400)
        commission = random.uniform(0.18, 0.28)
    elif platform == 'Foodpanda':
        gross = random.uniform(700, 1600)
        commission = random.uniform(0.25, 0.35)
    elif platform.startswith('Freelance'):
        gross = random.uniform(3000, 15000)
        commission = random.uniform(0.05, 0.25)
    else:
        gross = random.uniform(500, 2500)
        commission = random.uniform(0.00, 0.15)

    deductions = gross * commission
    net = gross - deductions
    return round(gross, 2), round(deductions, 2), round(net, 2)


def seed_shifts(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, worker_category FROM auth.users WHERE role='worker' ORDER BY created_at ASC;")
        workers = cur.fetchall()

        cur.execute('DELETE FROM earnings.shifts;')

        start = date.today() - timedelta(days=180)
        statuses = ['verified'] * 60 + ['pending'] * 20 + ['discrepancy'] * 10 + ['unsubmitted'] * 10

        shift_rows = []
        for worker_id, worker_category in workers:
            for m in range(6):
                for _ in range(20):
                    shift_date = start + timedelta(days=(m * 30) + random.randint(0, 29))
                    platform = _platform_for_category(worker_category)
                    gross, deductions, net = _earnings(platform)
                    hours = round(random.uniform(4, 10), 2)
                    status = random.choice(statuses)
                    shift_rows.append((worker_id, platform, shift_date, hours, gross, deductions, net, status))

        # Inject 18 deliberate anomalies.
        for i in range(min(18, len(shift_rows))):
            row = list(shift_rows[i])
            if i % 3 == 0:
                row[5] = round(row[4] * random.uniform(0.55, 0.75), 2)
                row[6] = round(row[4] - row[5], 2)
            elif i % 3 == 1:
                row[6] = 0.0
            else:
                row[4] = round(row[4] * 0.3, 2)
                row[5] = round(row[5] * 0.3, 2)
                row[6] = round(row[6] * 0.3, 2)
            shift_rows[i] = tuple(row)

        for row in shift_rows:
            cur.execute(
                """
                INSERT INTO earnings.shifts (
                    worker_id, platform, shift_date, hours_worked,
                    gross_earned, platform_deductions, net_received,
                    verification_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                row,
            )

    conn.commit()
