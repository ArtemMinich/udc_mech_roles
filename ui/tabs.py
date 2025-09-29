"""
Tab widgets for the clan role manager application.
"""

import sqlite3
from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel, QHeaderView, QInputDialog,
    QMenu
)
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt

from services.player_service import PlayerService
from services.role_service import RoleService
from ui.dialogs import PlayerDialog, RoleAssignDialog
from ui.widgets import DraggableTableWidget


class PlayersTab(QWidget):
    """Tab for managing players."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        v = QVBoxLayout()

        # Player table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Ім'я", "Обрані ролі"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Auto-resize columns to content
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # Enable context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_players_context_menu)

        v.addWidget(self.table)

        # CRUD buttons
        hb = QHBoxLayout()
        add_p = QPushButton("Додати гравця")
        add_p.clicked.connect(self.add_player_ui)
        hb.addWidget(add_p)

        edit_p = QPushButton("Редагувати гравця")
        edit_p.clicked.connect(self.edit_player_ui)
        hb.addWidget(edit_p)

        del_p = QPushButton("Видалити гравця")
        del_p.clicked.connect(self.delete_player_ui)
        hb.addWidget(del_p)

        clear_all_p = QPushButton("Очистити всі ролі")
        clear_all_p.clicked.connect(self.clear_all_preferences_ui)
        hb.addWidget(clear_all_p)

        hb.addStretch()
        v.addLayout(hb)
        self.setLayout(v)

    def format_preferences_with_counts(self, preferences: List[str], role_assignments: Dict[str, int]) -> str:
        """Format preferences with role assignment counts in parentheses."""
        formatted = []
        for role in preferences:
            count = role_assignments.get(role, 0)
            formatted.append(f"{role} ({count})")
        return ', '.join(formatted)

    def refresh(self):
        """Refresh the players table."""
        self.table.setRowCount(0)
        players = PlayerService.list_players()
        for p in players:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(p.nickname))

            # Format preferences with counts
            formatted_prefs = self.format_preferences_with_counts(
                p.preferences, p.role_assignments
            )
            self.table.setItem(r, 1, QTableWidgetItem(formatted_prefs))

    def add_player_ui(self):
        """UI for adding a new player."""
        dlg = PlayerDialog(self, existing_roles=RoleService.list_roles())
        if dlg.exec() == QDialog.Accepted:
            nick, prefs = dlg.get_data()
            if not nick:
                QMessageBox.warning(self, "Error", "Nickname required")
                return
            try:
                PlayerService.add_player(nick, prefs)
                self.refresh()
                # Refresh roles tab to update player counts
                if hasattr(self.parent_window, 'roles_tab'):
                    self.parent_window.roles_tab.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def edit_player_ui(self):
        """UI for editing an existing player."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Error", "Select a row")
            return
        nickname = sel[0].text()

        try:
            player = PlayerService.get_player(nickname)
            dlg = PlayerDialog(
                self, 
                nickname=player.nickname, 
                preferences=player.preferences, 
                existing_roles=RoleService.list_roles()
            )
            if dlg.exec() == QDialog.Accepted:
                newnick, prefs = dlg.get_data()
                if not newnick:
                    QMessageBox.warning(self, "Error", "Nickname required")
                    return
                PlayerService.update_player(nickname, newnick, prefs)
                self.refresh()
                # Refresh roles tab to update player counts
                if hasattr(self.parent_window, 'roles_tab'):
                    self.parent_window.roles_tab.refresh()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def delete_player_ui(self):
        """UI for deleting a player."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Error", "Select a row")
            return
        nickname = sel[0].text()
        if QMessageBox.question(self, "Confirm", f"Delete {nickname}?") == QMessageBox.Yes:
            PlayerService.delete_player(nickname)
            self.refresh()
            # Refresh roles tab to update player counts
            if hasattr(self.parent_window, 'roles_tab'):
                self.parent_window.roles_tab.refresh()

    def clear_all_preferences_ui(self):
        """UI for clearing all role preferences from all players."""
        reply = QMessageBox.question(
            self, 
            "Підтвердження", 
            "Ви впевнені, що хочете очистити всі обрані ролі у всіх гравців?\n"
            "Цю дію неможливо скасувати.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            PlayerService.clear_all_preferences()
            self.refresh()
            # Refresh roles tab to update player counts
            if hasattr(self.parent_window, 'roles_tab'):
                self.parent_window.roles_tab.refresh()
            QMessageBox.information(self, "Успіх", "Всі обрані ролі було очищено у всіх гравців")

    def show_players_context_menu(self, position):
        """Show context menu for players table."""
        menu = QMenu(self)

        # Add player action
        add_action = menu.addAction("Додати гравця")
        add_action.triggered.connect(self.add_player_ui)

        # Edit and delete actions only if row is selected
        if self.table.itemAt(position):
            edit_action = menu.addAction("Редагувати гравця")
            edit_action.triggered.connect(self.edit_player_ui)

            delete_action = menu.addAction("Видалити гравця")
            delete_action.triggered.connect(self.delete_player_ui)

        menu.addSeparator()

        # Clear all preferences action
        clear_action = menu.addAction("Очистити всі ролі")
        clear_action.triggered.connect(self.clear_all_preferences_ui)

        menu.exec_(self.table.mapToGlobal(position))


class RolesTab(QWidget):
    """Tab for managing roles with priority."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        v = QVBoxLayout()

        # Instructions
        instructions = QLabel("Перетягніть ролі для зміни пріоритетності (вище = вищий пріоритет)")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        v.addWidget(instructions)

        # Role table with drag & drop
        self.table = DraggableTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Назва ролі", "Пріоритет", "Кількість гравців"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Auto-resize all columns to content
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # Enable context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_roles_context_menu)

        v.addWidget(self.table)

        # CRUD buttons
        hb = QHBoxLayout()
        add_r = QPushButton("Додати роль")
        add_r.clicked.connect(self.add_role_ui)
        hb.addWidget(add_r)

        assign_r = QPushButton("Призначити роль людям")
        assign_r.clicked.connect(self.assign_role_to_players_ui)
        hb.addWidget(assign_r)

        del_r = QPushButton("Видалити роль")
        del_r.clicked.connect(self.delete_role_ui)
        hb.addWidget(del_r)
        hb.addStretch()

        v.addLayout(hb)
        self.setLayout(v)

    def refresh(self):
        """Refresh the roles table."""
        self.table.setRowCount(0)
        roles = RoleService.list_roles_with_priority()
        role_player_counts = RoleService.get_role_player_counts()

        for r in roles:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(r.priority)))

            # Add player count for this role
            player_count = role_player_counts.get(r.name, 0)
            self.table.setItem(row, 2, QTableWidgetItem(str(player_count)))

    def on_roles_reordered(self):
        """Called when roles are reordered via drag & drop."""
        role_names = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                role_names.append(item.text())

        if role_names:
            RoleService.reorder_roles(role_names)
            self.refresh()  # Refresh to show updated priorities

    def assign_role_to_players_ui(self):
        """UI for assigning a role to specific players."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Error", "Оберіть роль")
            return

        role_name = sel[0].text()  # Get role name from first column
        all_players = [p.nickname for p in PlayerService.list_players()]
        current_assignments = PlayerService.get_players_with_role(role_name)

        if not all_players:
            QMessageBox.warning(self, "Error", "Немає гравців для призначення")
            return

        dlg = RoleAssignDialog(self, role_name, all_players, current_assignments)

        if dlg.exec() == QDialog.Accepted:
            selected_players = dlg.get_selected_players()
            PlayerService.set_players_for_role(role_name, selected_players)

            # Show result
            if selected_players:
                players_str = ", ".join(selected_players)
                QMessageBox.information(self, "Успіх",
                    f"Роль '{role_name}' призначена гравцям:\n{players_str}")
            else:
                QMessageBox.information(self, "Успіх",
                    f"Роль '{role_name}' видалена у всіх гравців")

            # Refresh both tabs
            if hasattr(self.parent_window, 'players_tab'):
                self.parent_window.players_tab.refresh()
            # Also refresh roles tab to update player counts
            self.refresh()

    def add_role_ui(self):
        """UI for adding a new role."""
        text, ok = QInputDialog.getText(self, "Add role", "Role name:")
        if ok and text.strip():
            # Add at the end (highest priority number)
            max_priority = len(RoleService.list_roles_with_priority())
            RoleService.add_role(text.strip(), max_priority)
            QMessageBox.information(self, "OK", f"Role '{text}' added")
            self.refresh()

    def delete_role_ui(self):
        """UI for deleting a role."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Error", "Select a role")
            return
        role_name = sel[0].text()
        if QMessageBox.question(self, "Confirm", f"Delete role '{role_name}'?") == QMessageBox.Yes:
            RoleService.delete_role(role_name)
            self.refresh()
            # Refresh players tab if it exists
            if hasattr(self.parent_window, 'players_tab'):
                self.parent_window.players_tab.refresh()

    def show_roles_context_menu(self, position):
        """Show context menu for roles table."""
        menu = QMenu(self)

        # Add role action
        add_action = menu.addAction("Додати роль")
        add_action.triggered.connect(self.add_role_ui)

        # Assign and delete actions only if row is selected
        if self.table.itemAt(position):
            assign_action = menu.addAction("Призначити роль людям")
            assign_action.triggered.connect(self.assign_role_to_players_ui)

            delete_action = menu.addAction("Видалити роль")
            delete_action.triggered.connect(self.delete_role_ui)

        menu.exec_(self.table.mapToGlobal(position))
