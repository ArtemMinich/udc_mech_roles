"""
Dialog windows for the clan role manager application.
"""

from typing import List, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QAbstractItemView, QSplitter
)
from PySide6.QtCore import Qt


class PlayerDialog(QDialog):
    """Dialog for adding/editing players."""

    def __init__(self, parent=None, nickname: str = "", preferences: List[str] = None, existing_roles: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Player")
        self.resize(400, 300)
        self.nickname = nickname
        self.preferences = preferences or []
        self.existing_roles = existing_roles or []
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        v = QVBoxLayout()
        v.addWidget(QLabel("Nickname:"))
        self.nick_edit = QLineEdit(self.nickname)
        v.addWidget(self.nick_edit)

        v.addWidget(QLabel("Preferences (select multiple):"))
        self.roles_list = QListWidget()
        self.roles_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for r in self.existing_roles:
            it = QListWidgetItem(r)
            # Pre-select roles that player already has
            it.setSelected(r in self.preferences)
            self.roles_list.addItem(it)
        v.addWidget(self.roles_list)

        h = QHBoxLayout()
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        h.addWidget(ok)
        h.addWidget(cancel)
        v.addLayout(h)
        self.setLayout(v)

    def get_data(self) -> Tuple[str, List[str]]:
        """Get dialog data."""
        nick = self.nick_edit.text().strip()
        prefs = [w.text() for w in self.roles_list.selectedItems()]
        return nick, prefs


class RoleAssignDialog(QDialog):
    """Dialog to assign a role to specific players."""

    def __init__(self, parent=None, role_name: str = "", players: List[str] = None, current_assignments: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle(f"Призначити роль: {role_name}")
        self.resize(400, 300)
        self.role_name = role_name
        self.players = players or []
        self.current_assignments = current_assignments or []
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        v = QVBoxLayout()
        v.addWidget(QLabel(f"Оберіть гравців для ролі '{self.role_name}':"))

        self.players_list = QListWidget()
        self.players_list.setSelectionMode(QAbstractItemView.MultiSelection)

        for player in self.players:
            it = QListWidgetItem(player)
            # Pre-select players who already have this role
            it.setSelected(player in self.current_assignments)
            self.players_list.addItem(it)

        v.addWidget(self.players_list)

        h = QHBoxLayout()
        ok = QPushButton("Зберегти")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Скасувати")
        cancel.clicked.connect(self.reject)
        h.addWidget(ok)
        h.addWidget(cancel)
        v.addLayout(h)
        self.setLayout(v)

    def get_selected_players(self) -> List[str]:
        """Returns list of selected player nicknames."""
        return [w.text() for w in self.players_list.selectedItems()]


class AssignDialog(QDialog):
    """Dialog to select both roles and players."""

    def __init__(self, parent=None, roles: List[str] = None, players: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Assign Roles")
        self.resize(600, 400)
        self.roles = roles or []
        self.players = players or []
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        v = QVBoxLayout()

        # Create splitter for side-by-side layout
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Roles
        roles_widget = self._create_roles_widget()
        # Right side - Players
        players_widget = self._create_players_widget()

        # Add widgets to splitter
        splitter.addWidget(roles_widget)
        splitter.addWidget(players_widget)
        splitter.setSizes([300, 300])  # Equal sizes

        v.addWidget(splitter)

        # Buttons
        h = QHBoxLayout()
        ok = QPushButton("Призначити")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Скасувати")
        cancel.clicked.connect(self.reject)
        h.addWidget(ok)
        h.addWidget(cancel)
        v.addLayout(h)
        self.setLayout(v)

    def _create_roles_widget(self):
        """Create the roles selection widget."""
        from PySide6.QtWidgets import QWidget
        roles_widget = QWidget()
        roles_layout = QVBoxLayout()
        roles_layout.addWidget(QLabel("Оберіть ролі для призначення:"))
        self.roles_list = QListWidget()
        self.roles_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for r in self.roles:
            it = QListWidgetItem(r)
            self.roles_list.addItem(it)
        roles_layout.addWidget(self.roles_list)
        roles_widget.setLayout(roles_layout)
        return roles_widget

    def _create_players_widget(self):
        """Create the players selection widget."""
        from PySide6.QtWidgets import QWidget
        players_widget = QWidget()
        players_layout = QVBoxLayout()
        players_layout.addWidget(QLabel("Оберіть гравців для участі:"))
        self.players_list = QListWidget()
        self.players_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for p in self.players:
            it = QListWidgetItem(p)
            self.players_list.addItem(it)
        players_layout.addWidget(self.players_list)
        players_widget.setLayout(players_layout)
        return players_widget

    def get_selected_data(self) -> Tuple[List[str], List[str]]:
        """Returns (selected_roles, selected_players)."""
        selected_roles = [w.text() for w in self.roles_list.selectedItems()]
        selected_players = [w.text() for w in self.players_list.selectedItems()]
        return selected_roles, selected_players
