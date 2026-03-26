import sqlite3
import os

DATABASE = 'data/sportvision.db'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

def get_db_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            jersey_number INTEGER,
            age INTEGER,
            nationality TEXT,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Safely add image column to existing players table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN image TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
    
    # Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            logo TEXT,
            country TEXT,
            league TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Player Teams relationship table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            is_current BOOLEAN DEFAULT 1,
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
        )
    ''')
    
    # Player statistics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            season TEXT NOT NULL,
            matches_played INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            passes_attempted INTEGER DEFAULT 0,
            passes_completed INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        )
    ''')
    
    # Matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_date DATE NOT NULL,
            opponent TEXT NOT NULL,
            venue TEXT NOT NULL,
            team_goals INTEGER DEFAULT 0,
            opponent_goals INTEGER DEFAULT 0,
            possession REAL DEFAULT 50.0,
            shots INTEGER DEFAULT 0,
            shots_on_target INTEGER DEFAULT 0,
            corners INTEGER DEFAULT 0,
            fouls INTEGER DEFAULT 0,
            result TEXT DEFAULT 'Draw',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Match player performance (linking players to matches)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")
