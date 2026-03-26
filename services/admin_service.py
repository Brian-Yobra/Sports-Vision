from datetime import datetime
from core.db import get_db_connection

def add_player(name, position, jersey_number, age, nationality):
    """Add a new player to the database."""
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO players (name, position, jersey_number, age, nationality)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, position, jersey_number, age, nationality))
    
    player_id = cursor.lastrowid
    
    # Initialize player stats for current season
    current_season = datetime.now().year
    conn.execute('''
        INSERT INTO player_stats (player_id, season)
        VALUES (?, ?)
    ''', (player_id, str(current_season)))
    
    conn.commit()
    conn.close()
    return player_id

def add_match(match_date, opponent, venue, team_goals, opponent_goals, possession, shots, shots_on_target, corners, fouls):
    """Add a new match to the database."""
    # Determine result
    if team_goals > opponent_goals:
        result = 'Win'
    elif team_goals < opponent_goals:
        result = 'Loss'
    else:
        result = 'Draw'
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO matches (match_date, opponent, venue, team_goals, 
                           opponent_goals, possession, shots, shots_on_target, 
                           corners, fouls, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (match_date, opponent, venue, team_goals, opponent_goals, 
          possession, shots, shots_on_target, corners, fouls, result))
    
    conn.commit()
    conn.close()

def edit_player(player_id, name, position, jersey_number, age, nationality):
    """Edit player information."""
    conn = get_db_connection()
    conn.execute('''
        UPDATE players 
        SET name = ?, position = ?, jersey_number = ?, age = ?, nationality = ?
        WHERE id = ?
    ''', (name, position, jersey_number, age, nationality, player_id))
    conn.commit()
    conn.close()

def edit_player_stats(player_id, season, matches_played, goals, assists, passes_attempted, passes_completed, minutes_played, yellow_cards, red_cards, rating):
    """Edit player statistics."""
    conn = get_db_connection()
    
    # Check if stats exist for this season
    existing = conn.execute('''
        SELECT id FROM player_stats WHERE player_id = ? AND season = ?
    ''', (player_id, season)).fetchone()
    
    if existing:
        conn.execute('''
            UPDATE player_stats 
            SET matches_played = ?, goals = ?, assists = ?, 
                passes_attempted = ?, passes_completed = ?, minutes_played = ?,
                yellow_cards = ?, red_cards = ?, rating = ?
            WHERE player_id = ? AND season = ?
        ''', (matches_played, goals, assists, passes_attempted, passes_completed,
              minutes_played, yellow_cards, red_cards, rating, player_id, season))
    else:
        conn.execute('''
            INSERT INTO player_stats (player_id, season, matches_played, goals, assists,
                                    passes_attempted, passes_completed, minutes_played,
                                    yellow_cards, red_cards, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, season, matches_played, goals, assists, passes_attempted,
              passes_completed, minutes_played, yellow_cards, red_cards, rating))
    
    conn.commit()
    conn.close()

def delete_player(player_id):
    """Delete a player and all associated data."""
    conn = get_db_connection()
    conn.execute('DELETE FROM players WHERE id = ?', (player_id,))
    conn.commit()
    conn.close()

def delete_match(match_id):
    """Delete a match and all associated performance data."""
    conn = get_db_connection()
    conn.execute('DELETE FROM matches WHERE id = ?', (match_id,))
    conn.commit()
    conn.close()
