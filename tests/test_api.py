"""
Integration Tests for FastAPI Endpoints
"""

import os
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["day"] == 11
    assert len(data["classes"]) == 6


def test_disposal_guides_endpoint():
    res = client.get("/api/disposal-guides")
    assert res.status_code == 200
    data = res.json()
    assert "plastic" in data
    assert "e-waste" in data


def test_recycling_map_endpoint():
    res = client.get("/api/recycling-map?lat=12.9716&lon=77.5946&limit=3")
    assert res.status_code == 200
    data = res.json()
    assert "facilities" in data
    assert len(data["facilities"]) <= 3


def test_classify_endpoint_sample_image():
    sample_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_images", "plastic_bottle.jpg"
    )
    if os.path.exists(sample_file):
        with open(sample_file, "rb") as f:
            res = client.post(
                "/api/classify",
                files={"file": ("plastic_bottle.jpg", f, "image/jpeg")},
                data={"lat": 12.9716, "lon": 77.5946},
            )
        assert res.status_code == 200
        data = res.json()
        assert "prediction" in data
        assert "disposal_guide" in data
        assert "recycling_map" in data


def test_record_action_endpoint():
    payload = {
        "user_id": "api_test_user",
        "waste_class": "aluminum_can",
        "confidence": 0.88,
        "photo_notes": "API test submission",
    }
    # Using metal or aluminum
    payload["waste_class"] = "metal"
    res = client.post("/api/record-action", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["points_earned"] >= 20
    assert data["total_green_score"] >= 20


def test_leaderboard_endpoint():
    res = client.get("/api/leaderboard?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "leaderboard" in data
    assert len(data["leaderboard"]) > 0
