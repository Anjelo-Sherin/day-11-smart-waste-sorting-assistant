"""
Tests for GIS and Overpass Service
"""

from src.gis_service import (
    haversine_distance_km,
    generate_route_waypoints,
    GISRecyclingService,
)


def test_haversine_distance():
    # Distance between London and Paris is roughly 344 km
    london_lat, london_lon = 51.5074, -0.1278
    paris_lat, paris_lon = 48.8566, 2.3522
    dist = haversine_distance_km(london_lat, london_lon, paris_lat, paris_lon)
    assert 330 < dist < 360


def test_route_waypoints_generation():
    start_lat, start_lon = 12.9716, 77.5946
    end_lat, end_lon = 12.9815, 77.6045
    waypoints = generate_route_waypoints(start_lat, start_lon, end_lat, end_lon, steps=5)
    assert len(waypoints) == 6
    assert waypoints[0] == [round(start_lat, 6), round(start_lon, 6)]


def test_get_nearby_recyclers():
    service = GISRecyclingService()
    res = service.get_nearby_recyclers(user_lat=12.9716, user_lon=77.5946, limit=4)
    assert "facilities" in res
    assert len(res["facilities"]) > 0
    assert "closest_facility" in res
    assert res["closest_facility"]["distance_km"] >= 0
    assert len(res["route_waypoints"]) > 0
