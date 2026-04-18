from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "anomaly-detection"


def test_detect_insufficient_data():
    payload = {
        "worker_id": "w1",
        "shifts": [
            {
                "date": "2026-01-01",
                "platform": "Careem",
                "hours_worked": 8,
                "gross_earned": 1000,
                "platform_deductions": 200,
                "net_received": 800,
            }
        ],
    }
    response = client.post("/detect", json=payload)
    assert response.status_code == 200
    assert response.json()["anomalies_found"] == 0
