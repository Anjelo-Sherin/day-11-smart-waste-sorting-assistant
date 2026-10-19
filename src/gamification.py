"""
Gamification and Green Score Engine
Handles point attribution, streak mechanics, dynamic badge unlocks,
user profiles, and the competitive sustainability leaderboard.
"""

from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
from src.database import get_connection
from src.disposal_guide import get_disposal_guide

ALL_BADGES: Dict[str, Dict[str, str]] = {
    "eco_novice": {
        "name": "Eco Novice",
        "icon": "🌱",
        "desc": "Sorted your first waste item properly.",
    },
    "plastic_pioneer": {
        "name": "Plastic Pioneer",
        "icon": "🧴",
        "desc": "Correctly segregated 3+ plastic containers.",
    },
    "ewaste_guardian": {
        "name": "E-Waste Guardian",
        "icon": "🔋",
        "desc": "Safely routed hazardous electronic waste.",
    },
    "streak_master": {
        "name": "Streak Master",
        "icon": "🔥",
        "desc": "Maintained a 3-day consecutive waste sorting streak.",
    },
    "century_sorter": {
        "name": "Green Champion",
        "icon": "🏆",
        "desc": "Surpassed 100 total Green Score points.",
    },
    "zero_waste_hero": {
        "name": "Planet Savior",
        "icon": "🌍",
        "desc": "Diverted over 1 kg of material from landfills.",
    },
}


class GamificationEngine:
    """Calculates green scores, evaluates streak continuations, and unlocks awards."""

    @staticmethod
    def get_or_create_user(user_id: str = "user_current", username: str = "Eco Explorer (You)") -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            today_str = str(date.today())
            cursor.execute(
                """
                INSERT INTO users (id, username, green_score, current_streak, max_streak, items_sorted, last_activity_date, created_at)
                VALUES (?, ?, 0, 0, 0, 0, NULL, ?)
                """,
                (user_id, username, today_str),
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()

        user = dict(row)
        conn.close()
        return user

    @staticmethod
    def record_disposal(
        user_id: str,
        waste_class: str,
        confidence: float,
        photo_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        guide = get_disposal_guide(waste_class)
        impact = guide["environmental_impact"]
        base_points = guide.get("points_reward", 15)

        conn = get_connection()
        cursor = conn.cursor()

        # Fetch or create user
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            today_str = str(date.today())
            cursor.execute(
                """
                INSERT INTO users (id, username, green_score, current_streak, max_streak, items_sorted, last_activity_date, created_at)
                VALUES (?, ?, 0, 0, 0, 0, NULL, ?)
                """,
                (user_id, f"Recycler {user_id[-4:]}", today_str),
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
        user = dict(row)

        today = date.today()
        today_str = str(today)
        last_date_str = user.get("last_activity_date")

        current_streak = user.get("current_streak", 0)
        max_streak = user.get("max_streak", 0)

        if not last_date_str:
            current_streak = 1
        else:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            if today == last_date:
                # Already active today, streak stays intact
                pass
            elif today == last_date + timedelta(days=1):
                # Consecutive day streak increment!
                current_streak += 1
            else:
                # Streak reset after lapse
                current_streak = 1

        if current_streak > max_streak:
            max_streak = current_streak

        # Streak bonus
        streak_bonus = (current_streak - 1) * 2
        total_points_earned = base_points + streak_bonus

        new_green_score = user.get("green_score", 0) + total_points_earned
        new_items_sorted = user.get("items_sorted", 0) + 1

        # Update user record
        cursor.execute(
            """
            UPDATE users
            SET green_score = ?, current_streak = ?, max_streak = ?, items_sorted = ?, last_activity_date = ?
            WHERE id = ?
            """,
            (new_green_score, current_streak, max_streak, new_items_sorted, today_str, user_id),
        )

        # Insert disposal log
        now_ts = datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT INTO disposal_logs (
                user_id, waste_class, confidence, bin_name, points_earned,
                co2_saved_kg, water_saved_liters, landfill_diverted_grams, photo_notes, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                waste_class,
                confidence,
                guide["bin_name"],
                total_points_earned,
                impact["co2_saved_kg"],
                impact["water_saved_liters"],
                impact["landfill_diverted_grams"],
                photo_notes,
                now_ts,
            ),
        )

        conn.commit()

        # Check badges
        new_badges = GamificationEngine._evaluate_badges(user_id, cursor, conn)
        conn.close()

        return {
            "user_id": user_id,
            "waste_class": waste_class,
            "points_earned": total_points_earned,
            "base_points": base_points,
            "streak_bonus": streak_bonus,
            "total_green_score": new_green_score,
            "current_streak": current_streak,
            "items_sorted": new_items_sorted,
            "impact_added": impact,
            "new_badges_unlocked": new_badges,
        }

    @staticmethod
    def _evaluate_badges(user_id: str, cursor: Any, conn: Any) -> List[Dict[str, str]]:
        cursor.execute("SELECT badge_key FROM badges WHERE user_id = ?", (user_id,))
        existing_keys = {row["badge_key"] for row in cursor.fetchall()}

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = dict(cursor.fetchone())

        cursor.execute(
            "SELECT waste_class, COUNT(*) as cnt FROM disposal_logs WHERE user_id = ? GROUP BY waste_class",
            (user_id,),
        )
        class_counts = {r["waste_class"]: r["cnt"] for r in cursor.fetchall()}

        cursor.execute(
            "SELECT SUM(landfill_diverted_grams) as total_grams FROM disposal_logs WHERE user_id = ?",
            (user_id,),
        )
        landfill_row = cursor.fetchone()
        total_grams = landfill_row["total_grams"] or 0

        unlocked = []

        def award(b_key: str):
            if b_key not in existing_keys:
                b_info = ALL_BADGES[b_key]
                now_str = datetime.utcnow().strftime("%b %d, %Y")
                cursor.execute(
                    """
                    INSERT INTO badges (user_id, badge_key, badge_name, badge_icon, description, awarded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, b_key, b_info["name"], b_info["icon"], b_info["desc"], now_str),
                )
                conn.commit()
                existing_keys.add(b_key)
                unlocked.append({"key": b_key, **b_info, "awarded_at": now_str})

        # 1st item
        if user["items_sorted"] >= 1:
            award("eco_novice")
        # 3 plastics
        if class_counts.get("plastic", 0) >= 3:
            award("plastic_pioneer")
        # 1 e-waste
        if class_counts.get("e-waste", 0) >= 1:
            award("ewaste_guardian")
        # 3 day streak
        if user["current_streak"] >= 3:
            award("streak_master")
        # 100 points
        if user["green_score"] >= 100:
            award("century_sorter")
        # 1 kg landfill diverted (1000g)
        if total_grams >= 1000:
            award("zero_waste_hero")

        return unlocked

    @staticmethod
    def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, green_score, current_streak, items_sorted
            FROM users
            ORDER BY green_score DESC, items_sorted DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        leaderboard = []
        for idx, row in enumerate(rows, 1):
            leaderboard.append({
                "rank": idx,
                "user_id": row["id"],
                "username": row["username"],
                "green_score": row["green_score"],
                "streak": row["current_streak"],
                "items_sorted": row["items_sorted"],
            })
        conn.close()
        return leaderboard

    @staticmethod
    def get_user_profile(user_id: str = "user_current") -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        user = GamificationEngine.get_or_create_user(user_id)

        # Get badges
        cursor.execute(
            "SELECT badge_key, badge_name, badge_icon, description, awarded_at FROM badges WHERE user_id = ?",
            (user_id,),
        )
        badges = [dict(r) for r in cursor.fetchall()]

        # Get totals
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_disposals,
                COALESCE(SUM(co2_saved_kg), 0) as total_co2,
                COALESCE(SUM(water_saved_liters), 0) as total_water,
                COALESCE(SUM(landfill_diverted_grams), 0) as total_landfill_g
            FROM disposal_logs
            WHERE user_id = ?
            """,
            (user_id,),
        )
        totals = dict(cursor.fetchone())

        # Category breakdown
        cursor.execute(
            """
            SELECT waste_class, COUNT(*) as count
            FROM disposal_logs
            WHERE user_id = ?
            GROUP BY waste_class
            """,
            (user_id,),
        )
        categories = {r["waste_class"]: r["count"] for r in cursor.fetchall()}

        # Recent activities
        cursor.execute(
            """
            SELECT waste_class, bin_name, points_earned, co2_saved_kg, timestamp
            FROM disposal_logs
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (user_id,),
        )
        recent = [dict(r) for r in cursor.fetchall()]

        conn.close()

        return {
            "user": user,
            "badges": badges,
            "cumulative_impact": {
                "total_co2_kg": round(totals["total_co2"], 2),
                "total_water_liters": round(totals["total_water"], 2),
                "total_landfill_kg": round(totals["total_landfill_g"] / 1000.0, 3),
            },
            "category_breakdown": categories,
            "recent_activity": recent,
        }
