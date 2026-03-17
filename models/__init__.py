import sqlite3
from contextlib import contextmanager
from config import Config


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def initialize(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    jersey_number INTEGER,
                    age INTEGER,
                    nationality TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
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
            """)

            cursor.execute("""
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
            """)

            cursor.execute("""
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
            """)

            conn.commit()


db = Database()
