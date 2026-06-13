"""
SQLite database for configuration and logging
"""

import logging
import sqlite3
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Manage bot configuration and data persistence"""
    
    def __init__(self, db_path: str = "data/infobot.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Room configurations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY,
                    jid TEXT UNIQUE NOT NULL,
                    nickname TEXT,
                    config JSON,
                    enabled BOOLEAN DEFAULT 1,
                    joined_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Admin JIDs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY,
                    jid TEXT UNIQUE NOT NULL,
                    added_at TIMESTAMP
                )
            ''')
            
            # Message logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    room_jid TEXT,
                    sender_jid TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Earthquake alerts sent
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS earthquake_alerts (
                    id INTEGER PRIMARY KEY,
                    location TEXT,
                    magnitude REAL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("✅ Database initialized")
    
    def add_room(self, jid: str, nickname: str, config: dict):
        """Add/update room configuration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO rooms 
                (jid, nickname, config, updated_at) 
                VALUES (?, ?, ?, ?)
            ''', (jid, nickname, json.dumps(config), datetime.now()))
            conn.commit()
            logger.info(f"✅ Room saved: {jid}")
    
    def get_room(self, jid: str) -> dict:
        """Get room configuration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT config FROM rooms WHERE jid = ?', (jid,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
    
    def add_admin(self, jid: str):
        """Add admin JID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO admins (jid, added_at) VALUES (?, ?)',
                (jid, datetime.now())
            )
            conn.commit()
    
    def log_message(self, room_jid: str, sender_jid: str, message: str):
        """Log message for audit"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO messages (room_jid, sender_jid, message) VALUES (?, ?, ?)',
                (room_jid, sender_jid, message)
            )
            conn.commit()
