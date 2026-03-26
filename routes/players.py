from flask import Blueprint, render_template, flash, redirect, url_for
from core.db import get_db_connection
from services.stats_service import get_player_full_stats

players_bp = Blueprint('players', __name__)

@players_bp.route('/players')
def players():
    """Display all players with their statistics."""
    conn = get_db_connection()
    
    players = conn.execute('''
        SELECT p.*, 
               COALESCE(SUM(ps.goals), 0) as total_goals,
               COALESCE(SUM(ps.assists), 0) as total_assists,
               COALESCE(SUM(ps.matches_played), 0) as total_matches
        FROM players p
        LEFT JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY p.id
        ORDER BY p.name
    ''').fetchall()
    
    conn.close()
    
    return render_template('players.html', players=players)

@players_bp.route('/player/<int:player_id>')
def player_detail(player_id):
    """Display detailed statistics for a specific player."""
    stats = get_player_full_stats(player_id)
    
    if not stats:
        flash('Player not found!', 'error')
        return redirect(url_for('players.players'))
    
    return render_template('player_detail.html', **stats)
