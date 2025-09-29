"""
Player service for managing player operations.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict
from models.player import Player
from database.db_manager import db_manager


class PlayerService:
    """Service for managing player operations."""

    @staticmethod
    def add_player(nickname: str, preferences: List[str]) -> None:
        """Add a new player to the database."""
        prefs_json = json.dumps(preferences)
        role_assignments_json = json.dumps({})

        try:
            db_manager.execute_query(
                "INSERT INTO players (nickname, preferences, role_assignments) VALUES (?,?,?)",
                (nickname, prefs_json, role_assignments_json)
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Player with nickname '{nickname}' already exists")

    @staticmethod
    def update_player(nickname: str, new_nickname: str, preferences: List[str]) -> None:
        """Update an existing player."""
        prefs_json = json.dumps(preferences)
        db_manager.execute_query(
            "UPDATE players SET nickname=?, preferences=? WHERE nickname=?",
            (new_nickname, prefs_json, nickname)
        )

    @staticmethod
    def delete_player(nickname: str) -> None:
        """Delete a player from the database."""
        db_manager.execute_query(
            "DELETE FROM players WHERE nickname=?",
            (nickname,)
        )

    @staticmethod
    def list_players() -> List[Player]:
        """Get all players from the database."""
        rows = db_manager.execute_query(
            "SELECT nickname, preferences, role_assignments FROM players",
            fetch_all=True
        )

        players = []
        for row in rows:
            role_assignments = row['role_assignments']
            if role_assignments:
                try:
                    role_assignments_dict = json.loads(role_assignments)
                except (json.JSONDecodeError, TypeError):
                    role_assignments_dict = {}
            else:
                role_assignments_dict = {}

            player = Player(
                nickname=row['nickname'],
                preferences=json.loads(row['preferences']),
                role_assignments=role_assignments_dict
            )
            players.append(player)

        return players

    @staticmethod
    def get_player(nickname: str) -> Player:
        """Get a specific player by nickname."""
        players = PlayerService.list_players()
        player = next((p for p in players if p.nickname == nickname), None)
        if not player:
            raise ValueError(f"Player '{nickname}' not found")
        return player

    @staticmethod
    def get_players_with_role(role_name: str) -> List[str]:
        """Get list of player nicknames who have this role in their preferences."""
        players = PlayerService.list_players()
        return [p.nickname for p in players if p.has_role_preference(role_name)]

    @staticmethod
    def set_players_for_role(role_name: str, player_nicknames: List[str]) -> None:
        """Set which players have this role in their preferences."""
        all_players = PlayerService.list_players()

        for player in all_players:
            current_prefs = player.preferences.copy()
            if player.nickname in player_nicknames:
                # Add role if not present
                if role_name not in current_prefs:
                    current_prefs.append(role_name)
                    PlayerService.update_player(player.nickname, player.nickname, current_prefs)
            else:
                # Remove role if present
                if role_name in current_prefs:
                    current_prefs.remove(role_name)
                    PlayerService.update_player(player.nickname, player.nickname, current_prefs)

    @staticmethod
    def increment_role_assignment(nickname: str, role: str) -> None:
        """Increment assignment counter for specific role."""
        # Get current role assignments
        row = db_manager.execute_query(
            "SELECT role_assignments FROM players WHERE nickname=?",
            (nickname,), fetch_one=True
        )

        if not row:
            return

        role_assignments = row['role_assignments']
        if role_assignments:
            try:
                assignments_dict = json.loads(role_assignments)
            except (json.JSONDecodeError, TypeError):
                assignments_dict = {}
        else:
            assignments_dict = {}

        # Increment counter for this role
        today = datetime.now().strftime("%d.%m.%y")

        count, _ = assignments_dict.get(role, (0, ""))  # отримуємо старе значення або (0,"")
        assignments_dict[role] = (count + 1, today)

        # Save back to database
        db_manager.execute_query(
            "UPDATE players SET role_assignments=? WHERE nickname=?",
            (json.dumps(assignments_dict), nickname)
        )

    @staticmethod
    def get_role_assignment_count(nickname: str, role: str) -> int:
        """Get assignment count for specific player and role."""
        try:
            player = PlayerService.get_player(nickname)
            return player.get_role_assignment_count(role)
        except ValueError:
            return 0

    @staticmethod
    def clear_all_preferences() -> None:
        """Clear all role preferences for all players."""
        db_manager.execute_query(
            "UPDATE players SET preferences = '[]'",
            ()
        )
