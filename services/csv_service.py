import pandas as pd
from core.db import get_db_connection

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_players_csv(filepath):
    """Process uploaded players CSV file."""
    try:
        df = pd.read_csv(filepath)
        conn = get_db_connection()
        
        required_cols = ['name', 'position']
        if not all(col in df.columns for col in required_cols):
            return False, "CSV must contain 'name' and 'position' columns"
        
        added_count = 0
        for _, row in df.iterrows():
            conn.execute('''
                INSERT INTO players (name, position, jersey_number, age, nationality)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['name'],
                row['position'],
                row.get('jersey_number', None),
                row.get('age', None),
                row.get('nationality', 'Unknown')
            ))
            added_count += 1
        
        conn.commit()
        conn.close()
        return True, f"Successfully added {added_count} players"
    
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"

def process_matches_csv(filepath):
    """Process uploaded matches CSV file."""
    try:
        df = pd.read_csv(filepath)
        conn = get_db_connection()
        
        required_cols = ['match_date', 'opponent', 'venue']
        if not all(col in df.columns for col in required_cols):
            return False, "CSV must contain 'match_date', 'opponent', and 'venue' columns"
        
        added_count = 0
        for _, row in df.iterrows():
            # Determine result
            team_goals = int(row.get('team_goals') or 0)
            opponent_goals = int(row.get('opponent_goals') or 0)
            
            if team_goals > opponent_goals:
                result = 'Win'
            elif team_goals < opponent_goals:
                result = 'Loss'
            else:
                result = 'Draw'
            
            conn.execute('''
                INSERT INTO matches (match_date, opponent, venue, team_goals, 
                                   opponent_goals, possession, shots, shots_on_target, 
                                   corners, fouls, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['match_date'],
                row['opponent'],
                row['venue'],
                team_goals,
                opponent_goals,
                row.get('possession', 50.0),
                row.get('shots', 0),
                row.get('shots_on_target', 0),
                row.get('corners', 0),
                row.get('fouls', 0),
                result
            ))
            added_count += 1
        
        conn.commit()
        conn.close()
        return True, f"Successfully added {added_count} matches"
    
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"
