"""
Tests for Gamification, Green Score, and Badges
"""

import os
from src.database import init_db
from src.gamification import GamificationEngine


def setup_module():
    init_db()


def test_user_creation_and_disposal():
    user = GamificationEngine.get_or_create_user("test_user_99", "Test Recycler")
    assert user["id"] == "test_user_99"

    # Record disposal of plastic
    res = GamificationEngine.record_disposal(
        user_id="test_user_99",
        waste_class="plastic",
        confidence=0.92,
        photo_notes="Test plastic bottle",
    )
    assert res["points_earned"] >= 15
    assert res["items_sorted"] >= 1
    assert res["total_green_score"] >= 15


def test_leaderboard():
    leaderboard = GamificationEngine.get_leaderboard(limit=5)
    assert isinstance(leaderboard, list)
    assert len(leaderboard) > 0
    assert "green_score" in leaderboard[0]
    assert "rank" in leaderboard[0]
