import os
import sqlite3
from core.db import get_db_connection

def calculate_pass_accuracy(attempted, completed):
    """Calculate pass accuracy percentage."""
    if attempted == 0:
        return 0.0
    return round((completed / attempted) * 100, 2)

def get_team_stats():
    """Calculate comprehensive team statistics."""
    conn = get_db_connection()
    
    # Get all matches
    matches = conn.execute('SELECT * FROM matches ORDER BY match_date DESC').fetchall()
    
    if not matches:
        conn.close()
        return None
    
    total_matches = len(matches)
    wins = sum(1 for m in matches if m['result'] == 'Win')
    losses = sum(1 for m in matches if m['result'] == 'Loss')
    draws = sum(1 for m in matches if m['result'] == 'Draw')
    
    total_goals_scored = sum(m['team_goals'] for m in matches)
    total_goals_conceded = sum(m['opponent_goals'] for m in matches)
    avg_possession = round(sum(m['possession'] for m in matches) / total_matches, 2)
    
    # Last 5 matches for trend
    last_5 = matches[:5] if len(matches) >= 5 else matches
    last_5_results = [m['result'] for m in reversed(last_5)]
    
    conn.close()
    
    return {
        'total_matches': total_matches,
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': round((wins / total_matches) * 100, 2),
        'goals_scored': total_goals_scored,
        'goals_conceded': total_goals_conceded,
        'goal_difference': total_goals_scored - total_goals_conceded,
        'avg_goals_per_match': round(total_goals_scored / total_matches, 2),
        'avg_possession': avg_possession,
        'last_5_results': last_5_results
    }

def get_player_full_stats(player_id):
    """Get comprehensive statistics for a specific player."""
    conn = get_db_connection()
    
    player = conn.execute('SELECT * FROM players WHERE id = ?', (player_id,)).fetchone()
    
    if not player:
        conn.close()
        return None
    
    stats = conn.execute('''
        SELECT * FROM player_stats 
        WHERE player_id = ? 
        ORDER BY season DESC
    ''', (player_id,)).fetchall()
    
    # Aggregate stats across all seasons
    total_matches = sum(s['matches_played'] for s in stats) if stats else 0
    total_goals = sum(s['goals'] for s in stats) if stats else 0
    total_assists = sum(s['assists'] for s in stats) if stats else 0
    total_passes_attempted = sum(s['passes_attempted'] for s in stats) if stats else 0
    total_passes_completed = sum(s['passes_completed'] for s in stats) if stats else 0
    
    pass_accuracy = calculate_pass_accuracy(total_passes_attempted, total_passes_completed)
    
    # Get match performances for trend analysis
    performances = conn.execute('''
        SELECT mp.*, m.match_date 
        FROM match_performance mp
        JOIN matches m ON mp.match_id = m.id
        WHERE mp.player_id = ?
        ORDER BY m.match_date DESC
        LIMIT 10
    ''', (player_id,)).fetchall()
    
    # Get history of teams
    teams_history = conn.execute('''
        SELECT t.*, pt.is_current, pt.start_date, pt.end_date
        FROM player_teams pt
        JOIN teams t ON pt.team_id = t.id
        WHERE pt.player_id = ?
        ORDER BY pt.is_current DESC, pt.start_date DESC
    ''', (player_id,)).fetchall()
    
    conn.close()
    
    return {
        'player': player,
        'stats': stats,
        'total_matches': total_matches,
        'total_goals': total_goals,
        'total_assists': total_assists,
        'pass_accuracy': pass_accuracy,
        'performances': performances,
        'teams_history': teams_history
    }
