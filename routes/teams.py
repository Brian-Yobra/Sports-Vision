from flask import Blueprint, render_template, flash, redirect, url_for
from core.db import get_db_connection
from services.stats_service import get_team_stats

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/team')
def team_analytics():
    """Display team analytics and performance metrics."""
    team_stats = get_team_stats()
    
    if not team_stats:
        flash('No match data available. Add matches to see analytics.', 'warning')
        return render_template('team.html', team_stats=None)
    
    # Get match history for charts
    conn = get_db_connection()
    matches = conn.execute('''
        SELECT * FROM matches 
        ORDER BY match_date ASC
    ''').fetchall()
    conn.close()
    
    # Prepare data for Chart.js
    match_dates = [m['match_date'] for m in matches]
    goals_scored = [m['team_goals'] for m in matches]
    goals_conceded = [m['opponent_goals'] for m in matches]
    possession = [m['possession'] for m in matches]
    
    return render_template('team.html',
                         team_stats=team_stats,
                         match_dates=match_dates,
                         goals_scored=goals_scored,
                         goals_conceded=goals_conceded,
                         possession=possession)

@teams_bp.route('/teams')
def teams():
    """Display all teams in the league."""
    conn = get_db_connection()
    all_teams = conn.execute('SELECT * FROM teams ORDER BY name').fetchall()
    conn.close()
    
    return render_template('teams.html', teams=all_teams)

@teams_bp.route('/team/<int:team_id>')
def team_detail(team_id):
    """Display detailed view for a specific team and its rosters."""
    conn = get_db_connection()
    team = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
    
    if not team:
        conn.close()
        flash('Team not found!', 'error')
        return redirect(url_for('teams.teams'))
        
    # Get players associated with this team
    players_data = conn.execute('''
        SELECT p.*, pt.is_current, pt.start_date, pt.end_date 
        FROM player_teams pt
        JOIN players p ON pt.player_id = p.id
        WHERE pt.team_id = ?
        ORDER BY pt.is_current DESC, p.name
    ''', (team_id,)).fetchall()
    
    conn.close()
    
    return render_template('team_detail.html', team=team, players=players_data)
