"""
Data manager for import/export operations.
"""

import json
from typing import Tuple
from PySide6.QtWidgets import QFileDialog, QWidget

from services.player_service import PlayerService
from services.role_service import RoleService


class DataManager:
    """Manages data import/export operations."""

    @staticmethod
    def export_data(parent: QWidget = None) -> None:
        """Export both players and roles to single JSON file."""
        path, _ = QFileDialog.getSaveFileName(
            parent, "Export data", filter="Clan Role Manager Files (*.crm)"
        )

        if not path.endswith('.crm'):
            path += '.crm'

        if not path:
            return

        data = {
            'players': [p.to_dict() for p in PlayerService.list_players()],
            'roles': [r.to_dict() for r in RoleService.list_roles_with_priority()],
            'version': '1.0'
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def import_data(parent: QWidget = None) -> Tuple[int, int]:
        """
        Import both players and roles from single JSON file.
        Returns tuple of (players_imported, roles_imported).
        """
        path, _ = QFileDialog.getOpenFileName(
            parent, "Import data", filter="Clan Role Manager Files (*.crm)"
        )


        if not path:
            return 0, 0

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different formats
        if isinstance(data, list):
            # Old format - just players
            players_data = data
            roles_data = []
        else:
            # New format - players and roles
            players_data = data.get('players', [])
            roles_data = data.get('roles', [])

        # Import roles first
        roles_count = 0
        for r in roles_data:
            try:
                RoleService.add_role(r['name'], r.get('priority', 0))
                roles_count += 1
            except Exception:
                # skip duplicates or errors
                pass

        # Import players
        players_count = 0
        for p in players_data:
            try:
                PlayerService.add_player(p['nickname'], p.get('preferences', []))
                players_count += 1
            except Exception:
                # skip duplicates or errors
                pass

        return players_count, roles_count
