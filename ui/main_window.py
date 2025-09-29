"""
Main window for the clan role manager application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QTabWidget
)
from PySide6.QtWidgets import QDialog
from services.player_service import PlayerService
from services.role_service import RoleService
from services.assignment_service import AssignmentService
from ui.dialogs import AssignDialog
from ui.tabs import PlayersTab, RolesTab
from utils.data_manager import DataManager


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clan Role Manager")
        self.resize(800, 600)
        self._init_ui()
        self.refresh_all()

    def _init_ui(self):
        """Initialize the user interface."""
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()

        # Top buttons row
        top_buttons = self._create_top_buttons()
        layout.addLayout(top_buttons)

        # Tab widget
        self.tabs = QTabWidget()

        # Players tab
        self.players_tab = PlayersTab(self)
        self.tabs.addTab(self.players_tab, "Керування людьми")

        # Roles tab
        self.roles_tab = RolesTab(self)
        self.tabs.addTab(self.roles_tab, "Керування ролями")

        layout.addWidget(self.tabs)
        main_widget.setLayout(layout)

    def _create_top_buttons(self):
        """Create the top row of buttons."""
        top_buttons = QHBoxLayout()

        # Assignment button
        assign_btn = QPushButton("Назначити людей (Ctrl+R)")
        assign_btn.clicked.connect(self.open_assign_dialog)
        assign_btn.setShortcut("Ctrl+R")
        top_buttons.addWidget(assign_btn)

        top_buttons.addStretch()

        # Import/Export buttons
        export_btn = QPushButton("Експортувати дані")
        export_btn.clicked.connect(self.export_data)
        top_buttons.addWidget(export_btn)

        import_btn = QPushButton("Імпортувати дані")
        import_btn.clicked.connect(self.import_data)
        top_buttons.addWidget(import_btn)

        return top_buttons

    def refresh_all(self):
        """Refresh both tabs."""
        self.players_tab.refresh()
        self.roles_tab.refresh()

    def open_assign_dialog(self):
        """Open the role assignment dialog."""
        roles = RoleService.list_roles()
        players_data = PlayerService.list_players()
        player_nicknames = [p.nickname for p in players_data]

        if not roles:
            QMessageBox.warning(self, "Error", "No roles defined")
            return
        if not player_nicknames:
            QMessageBox.warning(self, "Error", "No players defined")
            return

        dlg = AssignDialog(self, roles=roles, players=player_nicknames)
        if dlg.exec() == QDialog.Accepted:
            selected_data = dlg.get_selected_data()
            selected_roles = selected_data["roles"]
            role_counts = selected_data["role_counts"]
            selected_players = selected_data["players"]

            if not selected_roles:
                QMessageBox.warning(self, "Error", "Оберіть хоча б одну роль")
                return
            if not selected_players:
                QMessageBox.warning(self, "Error", "Оберіть хоча б одного гравця")
                return

            result = AssignmentService.assign_roles(role_counts, selected_players)

            # Show result
            txt = "Результати призначення:\n\n"
            for role, players in result.items():
                if players:
                    txt += f"✅ {role}: {', '.join(players)}\n"
                else:
                    txt += f"❌ {role}: немає підходящого кандидата\n"
            txt += f"\nПризначено ролей: {len(result)}"

            QMessageBox.information(self, "Результат призначення", txt)
            self.refresh_all()

    def export_data(self):
        """Export data to JSON file."""
        try:
            DataManager.export_data()
            QMessageBox.information(self, "Export", "Експортовано людей та ролі")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Помилка експорту: {str(e)}")

    def import_data(self):
        """Import data from JSON file."""
        try:
            players_count, roles_count = DataManager.import_data()
            QMessageBox.information(self, "Import",
                                  f"Імпортовано {players_count} людей та {roles_count} ролей")
            self.refresh_all()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Помилка імпорту: {str(e)}")
