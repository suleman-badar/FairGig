import random


def seed_grievances(conn):
    categories = [
        'commission_rate_change',
        'account_deactivation',
        'payment_delay',
        'incorrect_calculation',
        'unsafe_working_condition',
        'no_transparency',
        'other',
    ]
    platforms = ['Careem', 'Bykea', 'Foodpanda', 'inDrive', 'Freelance_Upwork']

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM auth.users WHERE role='worker' LIMIT 120;")
        worker_ids = [r[0] for r in cur.fetchall()]

        cur.execute('DELETE FROM grievance.complaints;')
        cur.execute('DELETE FROM grievance.clusters;')

        for i, worker_id in enumerate(worker_ids):
            category = random.choice(categories)
            platform = random.choice(platforms)
            category_label = category.replace('_', ' ')
            cur.execute(
                """
                INSERT INTO grievance.complaints (
                    worker_id, platform, category, title, description,
                    status, is_public, anonymous_display_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    worker_id,
                    platform,
                    category,
                    f"Complaint {i+1}: {category_label}",
                    f"Worker reported {category_label} issue on {platform}.",
                    'open',
                    True,
                    f'WKR-{1000+i}',
                ),
            )

    conn.commit()
