import json
import random
from pathlib import Path

import psycopg2
from passlib.context import CryptContext

ROOT = Path(__file__).resolve().parent
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__rounds=12)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_phone(i: int) -> str:
    return f"03{(100000000 + i):09d}"[:11]


def build_users():
    names = load_json(ROOT / 'data' / 'faker_names_pk.json')
    city_zones = load_json(ROOT / 'data' / 'city_zones.json')

    workers = []
    verifiers = []
    advocates = []

    categories = (['ride_hailing'] * 60) + (['food_delivery'] * 50) + (['freelance'] * 30) + (['domestic'] * 10)
    worker_zones = (['Lahore-North'] * 60) + (['Karachi-Central'] * 50) + (['Islamabad-West'] * 40)

    for i in range(150):
        workers.append({
            'phone': generate_phone(i),
            'full_name': random.choice(names),
            'role': 'worker',
            'city_zone': worker_zones[i],
            'worker_category': categories[i],
            'password_hash': pwd_context.hash('demo1234')
        })

    for i in range(150, 180):
        verifiers.append({
            'phone': generate_phone(i),
            'full_name': random.choice(names),
            'role': 'verifier',
            'city_zone': random.choice(city_zones),
            'worker_category': None,
            'password_hash': pwd_context.hash('demo1234')
        })

    for i in range(180, 200):
        advocates.append({
            'phone': generate_phone(i),
            'full_name': random.choice(names),
            'role': 'advocate',
            'city_zone': random.choice(city_zones),
            'worker_category': None,
            'password_hash': pwd_context.hash('demo1234')
        })

    return workers + verifiers + advocates


def seed_users(conn):
    users = build_users()
    with conn.cursor() as cur:
        cur.execute('DELETE FROM auth.refresh_tokens;')
        cur.execute('DELETE FROM auth.users;')
        for u in users:
            cur.execute(
                """
                INSERT INTO auth.users (phone, password_hash, full_name, role, city_zone, worker_category)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (u['phone'], u['password_hash'], u['full_name'], u['role'], u['city_zone'], u['worker_category']),
            )
    conn.commit()


if __name__ == '__main__':
    conn = psycopg2.connect('dbname=fairgig user=fairgig_admin password=your_strong_password_here host=localhost port=5432')
    seed_users(conn)
    conn.close()
