from flask import Blueprint, render_template
from core.db import get_db_connection
from services.stats_service import get_team_stats

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Main dashboard showing overview of team and player stats."""
    conn = get_db_connection()
    
    # Get summary statistics
    players_count = conn.execute('SELECT COUNT(*) as count FROM players').fetchone()['count']
    matches_count = conn.execute('SELECT COUNT(*) as count FROM matches').fetchone()['count']
    
    # Get top scorers
    top_scorers = conn.execute('''
        SELECT p.name, p.position, SUM(ps.goals) as total_goals
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY p.id
        ORDER BY total_goals DESC
        LIMIT 5
    ''').fetchall()
    
    # Get recent matches
    recent_matches = conn.execute('''
        SELECT * FROM matches 
        ORDER BY match_date DESC 
        LIMIT 5
    ''').fetchall()
    
    # Get team stats
    team_stats = get_team_stats()
    
    conn.close()
    
    return render_template('dashboard.html',
                         players_count=players_count,
                         matches_count=matches_count,
                         top_scorers=top_scorers,
                         recent_matches=recent_matches,
                         team_stats=team_stats)
