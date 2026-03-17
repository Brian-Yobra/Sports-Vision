import os
import re
from functools import wraps
from flask import session, redirect, url_for, flash
from models import db


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        from config import Config

        allowed_extensions = Config.ALLOWED_EXTENSIONS

    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def calculate_pass_accuracy(attempted, completed):
    if attempted == 0:
        return 0.0
    return round((completed / attempted) * 100, 2)


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_username(username):
    return len(username) >= 3 and bool(re.match(r"^[a-zA-Z0-9_]+$", username))


def validate_password(password):
    return len(password) >= 6


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("Admin access required", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def get_team_stats():
    with db.get_connection() as conn:
        matches = conn.execute(
            "SELECT * FROM matches ORDER BY match_date DESC"
        ).fetchall()

        if not matches:
            return None

        total = len(matches)
        wins = sum(1 for m in matches if m["result"] == "Win")
        losses = sum(1 for m in matches if m["result"] == "Loss")
        draws = sum(1 for m in matches if m["result"] == "Draw")

        return {
            "total_matches": total,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": round((wins / total) * 100, 2),
            "goals_scored": sum(m["team_goals"] for m in matches),
            "goals_conceded": sum(m["opponent_goals"] for m in matches),
            "goal_difference": sum(m["team_goals"] for m in matches)
            - sum(m["opponent_goals"] for m in matches),
            "avg_goals_per_match": round(
                sum(m["team_goals"] for m in matches) / total, 2
            ),
            "avg_possession": round(sum(m["possession"] for m in matches) / total, 2),
            "last_5_results": [m["result"] for m in reversed(matches[:5])],
        }


def get_player_full_stats(player_id):
    from models import db

    with db.get_connection() as conn:
        player = conn.execute(
            "SELECT * FROM players WHERE id = ?", (player_id,)
        ).fetchone()

        if not player:
            return None

        stats = conn.execute(
            """
            SELECT * FROM player_stats 
            WHERE player_id = ? 
            ORDER BY season DESC
        """,
            (player_id,),
        ).fetchall()

        total_matches = sum(s["matches_played"] for s in stats) if stats else 0
        total_goals = sum(s["goals"] for s in stats) if stats else 0
        total_assists = sum(s["assists"] for s in stats) if stats else 0
        total_passes_attempted = (
            sum(s["passes_attempted"] for s in stats) if stats else 0
        )
        total_passes_completed = (
            sum(s["passes_completed"] for s in stats) if stats else 0
        )

        performances = conn.execute(
            """
            SELECT mp.*, m.match_date 
            FROM match_performance mp
            JOIN matches m ON mp.match_id = m.id
            WHERE mp.player_id = ?
            ORDER BY m.match_date DESC
            LIMIT 10
        """,
            (player_id,),
        ).fetchall()

        return {
            "player": player,
            "stats": stats,
            "total_matches": total_matches,
            "total_goals": total_goals,
            "total_assists": total_assists,
            "pass_accuracy": calculate_pass_accuracy(
                total_passes_attempted, total_passes_completed
            ),
            "performances": performances,
        }
