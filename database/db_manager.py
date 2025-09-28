"""
Database manager for clan role manager application.
Handles all database operations and connections.
"""

import sqlite3
import json
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, db_path: str = "clan.db"):
        self.db_path = db_path
        self.init_db()

    def get_conn(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables and perform migrations."""
        conn = self.get_conn()
        c = conn.cursor()

        # Create tables
        c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            preferences TEXT NOT NULL, -- json list
            role_assignments TEXT DEFAULT '{}' -- json dict {role_name: count}
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            priority INTEGER DEFAULT 0 -- lower number = higher priority
        )
        """)

        # Migration: remove total_assignments column if it exists
        try:
            c.execute("ALTER TABLE players DROP COLUMN total_assignments")
            conn.commit()
        except sqlite3.OperationalError:
            # Column doesn't exist or already removed
            pass

        # Migration: add priority column if it doesn't exist
        try:
            c.execute("ALTER TABLE roles ADD COLUMN priority INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False):
        """Execute a database query with proper error handling."""
        conn = self.get_conn()
        try:
            c = conn.cursor()
            c.execute(query, params)

            if fetch_one:
                result = c.fetchone()
            elif fetch_all:
                result = c.fetchall()
            else:
                result = None

            conn.commit()
            return result
        finally:
            conn.close()


# Global database manager instance
db_manager = DatabaseManager()
