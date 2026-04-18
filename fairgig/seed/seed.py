import os

import psycopg2

from seed_grievances import seed_grievances
from seed_shifts import seed_shifts
from seed_users import seed_users


def main():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'fairgig'),
        user=os.getenv('POSTGRES_USER', 'fairgig_admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'your_strong_password_here'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )

    print('Seeding users...')
    seed_users(conn)
    print('Seeding shifts...')
    seed_shifts(conn)
    print('Seeding grievances...')
    seed_grievances(conn)

    conn.close()
    print('Seed complete.')


if __name__ == '__main__':
    main()
