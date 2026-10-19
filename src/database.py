"""
SQLite Database Layer for Smart Waste Sorting Assistant
Stores users, sorting activities, streaks, environmental impact logs, and leaderboard.
"""

import os
import sqlite3
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional

DB_FILE = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "waste_assistant.db"))


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(DB_FILE)), exist_ok=True)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            green_score INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            items_sorted INTEGER DEFAULT 0,
            last_activity_date TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS disposal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            waste_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            bin_name TEXT NOT NULL,
            points_earned INTEGER NOT NULL,
            co2_saved_kg REAL NOT NULL,
            water_saved_liters REAL NOT NULL,
            landfill_diverted_grams REAL NOT NULL,
            photo_notes TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            badge_key TEXT NOT NULL,
            badge_name TEXT NOT NULL,
            badge_icon TEXT NOT NULL,
            description TEXT NOT NULL,
            awarded_at TEXT NOT NULL,
            UNIQUE(user_id, badge_key),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    conn.commit()

    # Seed default community demo users if leaderboard is empty
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]
    if count == 0:
        seed_users = [
            ("user_maya", "Maya Lin (EcoHero)", 320, 5, 8, 24, "2026-10-19", "2026-10-01"),
            ("user_alex", "Alex Rivera (GreenOps)", 285, 4, 6, 21, "2026-10-19", "2026-10-02"),
            ("user_sam", "Samira Khan (ZeroWaste)", 210, 3, 5, 16, "2026-10-18", "2026-10-05"),
            ("user_current", "Eco Explorer (You)", 50, 1, 1, 3, "2026-10-19", "2026-10-19"),
        ]
        for uid, name, score, c_strk, m_strk, items, last_act, created in seed_users:
            cursor.execute(
                """
                INSERT INTO users (id, username, green_score, current_streak, max_streak, items_sorted, last_activity_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (uid, name, score, c_strk, m_strk, items, last_act, created),
            )
        conn.commit()

    conn.close()
