"""
Role service for managing role operations.
"""

import sqlite3
from typing import List
from models.role import Role
from database.db_manager import db_manager


class RoleService:
    """Service for managing role operations."""

    @staticmethod
    def add_role(name: str, priority: int = 0) -> None:
        """Add a new role to the database."""
        try:
            db_manager.execute_query(
                "INSERT INTO roles (name, priority) VALUES (?,?)",
                (name, priority)
            )
        except sqlite3.IntegrityError:
            # Role already exists, ignore
            pass

    @staticmethod
    def update_role_priority(name: str, priority: int) -> None:
        """Update role priority."""
        db_manager.execute_query(
            "UPDATE roles SET priority=? WHERE name=?",
            (priority, name)
        )

    @staticmethod
    def delete_role(name: str) -> None:
        """Delete a role from the database."""
        db_manager.execute_query(
            "DELETE FROM roles WHERE name=?",
            (name,)
        )

    @staticmethod
    def list_roles() -> List[str]:
        """Return role names only (for backwards compatibility)."""
        rows = db_manager.execute_query(
            "SELECT name FROM roles ORDER BY priority ASC, name ASC",
            fetch_all=True
        )
        return [row['name'] for row in rows]

    @staticmethod
    def list_roles_with_priority() -> List[Role]:
        """Return roles with priority information."""
        rows = db_manager.execute_query(
            "SELECT name, priority FROM roles ORDER BY priority ASC, name ASC",
            fetch_all=True
        )
        return [Role(name=row['name'], priority=row['priority']) for row in rows]

    @staticmethod
    def reorder_roles(role_names: List[str]) -> None:
        """Update priority based on new order."""
        for i, name in enumerate(role_names):
            db_manager.execute_query(
                "UPDATE roles SET priority=? WHERE name=?",
                (i, name)
            )
