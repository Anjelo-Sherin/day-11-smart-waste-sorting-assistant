"""
Comprehensive Live End-to-End Test Suite for Smart Waste Sorting Assistant.
Exercises every layer: Vision inference, Disposal matrix, OpenStreetMap GIS, and Gamification.
"""

import sys
import os
import json
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def print_section(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def test_e2e():
    print_section("1. HEALTH & METADATA VERIFICATION")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    health_data = res.json()
    print(f"✓ Service Status: {health_data['status']}")
    print(f"✓ Project Day: {health_data['day']}")
    print(f"✓ Supported Waste Classes: {health_data['classes']}")
    print(f"✓ Inference Engine: {health_data['device']}")

    print_section("2. CLASSIFYING ALL 6 BENCHMARK SAMPLES")
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_images")
    test_files = [
        ("plastic_bottle.jpg", "plastic", "Blue / Yellow Recycling Bin"),
        ("cardboard_box.jpg", "paper", "Blue Paper Bin"),
        ("aluminum_can.jpg", "metal", "Yellow / Gray Metal Bin"),
        ("glass_bottle.jpg", "glass", "Green / Brown Glass Bank"),
        ("organic_food.jpg", "organic", "Brown / Green Compost Bin"),
        ("electronic_device.jpg", "e-waste", "Special E-Waste Collection Center"),
    ]

    for fname, expected_category, expected_bin in test_files:
        path = os.path.join(sample_dir, fname)
        assert os.path.exists(path), f"Sample file not found: {path}"

        start_time = time.time()
        with open(path, "rb") as f:
            res = client.post(
                "/api/classify",
                files={"file": (fname, f, "image/jpeg")},
                data={"lat": 12.9716, "lon": 77.5946},
            )
        elapsed_ms = (time.time() - start_time) * 1000
        assert res.status_code == 200, f"Failed for {fname}: {res.text}"

        data = res.json()
        pred = data["prediction"]
        guide = data["disposal_guide"]
        gis = data.get("recycling_map")

        print(f"\n[Test Image: {fname}]")
        print(f"  → Predicted Category: {pred['predicted_class'].upper()} (Confidence: {pred['confidence_percentage']}%)")
        print(f"  → Assigned Target Bin: {guide['bin_name']}")
        print(f"  → CO2 Avoided: {guide['environmental_impact']['co2_saved_kg']} kg | Water Saved: {guide['environmental_impact']['water_saved_liters']} L")
        print(f"  → Prep Step 1: {guide['preparation_steps'][0]}")
        print(f"  → Contamination Risk: {guide['contamination_warnings'][0][:75]}...")
        if gis and gis.get("closest_facility"):
            cf = gis["closest_facility"]
            print(f"  → Closest Recycler: {cf['name']} ({cf['distance_km']} km away, {cf['walking_time_mins']} min walk)")
        print(f"  → Inference + GIS Latency: {elapsed_ms:.1f} ms")

        assert pred["predicted_class"] == expected_category, f"Expected {expected_category}, got {pred['predicted_class']}"

    print_section("3. MULTI-VIEW AMBIGUITY FUSION TEST")
    path1 = os.path.join(sample_dir, "plastic_bottle.jpg")
    path2 = os.path.join(sample_dir, "plastic_bottle.jpg")
    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        res = client.post(
            "/api/classify-multiview",
            files={
                "file1": ("view1.jpg", f1, "image/jpeg"),
                "file2": ("view2.jpg", f2, "image/jpeg"),
            },
        )
    assert res.status_code == 200
    mv_data = res.json()
    print(f"✓ Fused Prediction: {mv_data['fused_prediction']['predicted_class']}")
    print(f"✓ Fused Confidence: {mv_data['fused_prediction']['confidence_percentage']}%")
    print(f"✓ Multi-Angle Fusion Applied: {mv_data['fused_prediction']['fused_from_photos']} photos combined")

    print_section("4. OPENSTREETMAP GIS RECYCLING SEARCH & ROUTING")
    res = client.get("/api/recycling-map?lat=37.7749&lon=-122.4194&limit=3")
    assert res.status_code == 200
    map_data = res.json()
    print(f"✓ Location Queried: San Francisco ({map_data['user_coordinates']['lat']}, {map_data['user_coordinates']['lon']})")
    print(f"✓ Total Facilities Found: {map_data['total_found']}")
    for idx, fac in enumerate(map_data["facilities"], 1):
        print(f"   [{idx}] {fac['name']} — {fac['distance_km']} km away ({fac['walking_time_mins']}m walk)")
    print(f"✓ Route Waypoints Generated: {len(map_data['route_waypoints'])} navigation steps")

    print_section("5. GAMIFICATION: SCORING, STREAKS & BADGE UNLOCKS")
    user_id = f"tester_{int(time.time())}"
    # Log 3 plastics and 1 e-waste to trigger badges
    actions = ["plastic", "plastic", "plastic", "e-waste"]
    for act in actions:
        res = client.post(
            "/api/record-action",
            json={"user_id": user_id, "waste_class": act, "confidence": 0.95},
        )
        assert res.status_code == 200
        rec = res.json()
        print(f"  → Logged '{act}': Earned +{rec['points_earned']} pts (Total: {rec['total_green_score']} pts, Streak: {rec['current_streak']}d)")
        if rec["new_badges_unlocked"]:
            for b in rec["new_badges_unlocked"]:
                print(f"     🏆 BADGE UNLOCKED: {b['icon']} {b['name']} — {b['desc']}")

    print_section("6. LEADERBOARD & USER PROFILE VERIFICATION")
    res_prof = client.get(f"/api/user/profile?user_id={user_id}")
    assert res_prof.status_code == 200
    profile = res_prof.json()
    print(f"✓ User: {profile['user']['username']}")
    print(f"✓ Final Green Score: {profile['user']['green_score']} pts")
    print(f"✓ Items Sorted: {profile['user']['items_sorted']}")
    print(f"✓ Badges Earned: {[b['badge_name'] for b in profile['badges']]}")
    print(f"✓ Carbon Diverted: {profile['cumulative_impact']['total_co2_kg']} kg CO2")

    res_lead = client.get("/api/leaderboard?limit=5")
    assert res_lead.status_code == 200
    leaders = res_lead.json()["leaderboard"]
    print(f"\nTop 3 Community Leaderboard:")
    for l in leaders[:3]:
        print(f"  Rank #{l['rank']}: {l['username']} — {l['green_score']} pts (Streak: {l['streak']})")

    print_section("ALL 6 TEST SUITE PHASES COMPLETED WITH 100% SUCCESS!")


if __name__ == "__main__":
    test_e2e()
