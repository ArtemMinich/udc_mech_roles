"""
Dialog windows for the clan role manager application.
"""

from typing import List, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QAbstractItemView, QSplitter, QWidget, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt

from services.role_service import RoleService


class PlayerDialog(QDialog):
    """Dialog for adding/editing players."""

    def __init__(self, parent=None, nickname: str = "", preferences: List[str] = None, existing_roles: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Гравець")
        self.resize(400, 300)
        self.nickname = nickname
        self.preferences = preferences or []
        self.existing_roles = existing_roles or []
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        v = QVBoxLayout()
        v.addWidget(QLabel("Нікнейм:"))
        self.nick_edit = QLineEdit(self.nickname)
        v.addWidget(self.nick_edit)

        v.addWidget(QLabel("Уподобання (виберіть кілька):"))
        self.roles_list = QListWidget()
        self.roles_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for r in self.existing_roles:
            it = QListWidgetItem(r)
            # Pre-select roles that player already has
            self.roles_list.addItem(it)
            it.setSelected(r in self.preferences)
        v.addWidget(self.roles_list)

        h = QHBoxLayout()
        ok = QPushButton("Готово")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Скасувати")
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
            self.players_list.addItem(it)
            it.setSelected(player in self.current_assignments)

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


class RoleSelectorWidget(QWidget):
    def __init__(self, role_name):
        super().__init__()
        self.role_name = role_name
        layout = QHBoxLayout()
        self.checkbox = QCheckBox(role_name)
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(99)
        self.spinbox.setEnabled(False)
        self.checkbox.stateChanged.connect(self.spinbox.setEnabled)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

    def is_selected(self):
        return self.checkbox.isChecked()

    def count(self):
        return self.spinbox.value()

class AssignDialog(QDialog):
    """Dialog to select both roles and players."""

    def __init__(self, parent=None, roles: List[str] = None, players: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Призначення ролей")
        self.resize(600, 400)
        self.roles = roles or []
        self.players = players or []
        self._init_ui()

    def _init_ui(self):
        v = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Roles with checkboxes and counters
        roles_widget = QWidget()
        roles_layout = QVBoxLayout()
        self.role_selectors = []
        for role in self.roles:
            selector = RoleSelectorWidget(role)
            self.role_selectors.append(selector)
            roles_layout.addWidget(selector)
        roles_widget.setLayout(roles_layout)

        # Right side - Players (залишити як було)
        players_widget = self._create_base_multi_selection_widget("Оберіть гравців для участі:", self.players)
        self.players_list = players_widget.list_widget

        splitter.addWidget(roles_widget)
        splitter.addWidget(players_widget)
        splitter.setSizes([300, 300])
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

    def _create_base_multi_selection_widget(self, label, list):
        from PySide6.QtWidgets import QWidget, QCheckBox
        from PySide6.QtCore import Qt

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))

        # Чекбокс для вибору всіх елементів
        select_all_checkbox = QCheckBox("Обрати всіх")
        layout.addWidget(select_all_checkbox)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        for p in list:
            it = QListWidgetItem(p)
            list_widget.addItem(it)

        # Використовуємо lambda для прив'язки до конкретного віджета
        select_all_checkbox.stateChanged.connect(
            lambda state, lw=list_widget: self._on_select_all_changed(lw, state)
        )

        list_widget.itemSelectionChanged.connect(
            lambda lw=list_widget, cb=select_all_checkbox: self._update_select_all_checkbox(lw, cb)
        )

        layout.addWidget(list_widget)
        widget.setLayout(layout)

        # Зберігаємо посилання на віджети для подальшого використання
        widget.list_widget = list_widget
        widget.select_all_checkbox = select_all_checkbox

        return widget

    def _on_select_all_changed(self,list_widget, state):
        """Обирає або знімає вибір з усіх елементів"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(state == 2)  # 2 = Qt.Checked

    def _update_select_all_checkbox(self,list_widget, checkbox):
        """Оновлює стан чекбоксу в залежності від вибраних елементів"""
        from PySide6.QtCore import Qt

        total = list_widget.count()
        selected = len(list_widget.selectedItems())

        # Блокуємо сигнал, щоб не викликати _on_select_all_changed
        checkbox.blockSignals(True)

        if selected == 0:
            checkbox.setCheckState(Qt.Unchecked)
        elif selected == total:
            checkbox.setCheckState(Qt.Checked)
        else:
            checkbox.setCheckState(Qt.PartiallyChecked)

        checkbox.blockSignals(False)

    def get_selected_data(self):
        selected_roles = {
            selector.role_name: selector.count()
            for selector in self.role_selectors if selector.is_selected()
        }
        selected_players = [w.text() for w in self.players_list.selectedItems()]
        return {
            "roles": list(selected_roles.keys()),
            "role_counts": selected_roles,
            "players": selected_players
        }
class RoleSelectDialog(QDialog):
    """Dialog to select roles only."""

    def __init__(self, parent=None,preselected: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Вибір ролей")
        self.resize(400, 300)
        self.roles = RoleService.list_roles()
        self.preselected = preselected or []
        self._init_ui()

    def _init_ui(self):
        v = QVBoxLayout()
        v.addWidget(QLabel("Оберіть ролі:"))

        self.checkboxes = []
        for role in self.roles:
            cb = QCheckBox(role)
            if role in self.preselected:
                cb.setChecked(True)
            self.checkboxes.append(cb)
            v.addWidget(cb)

        # Кнопки
        h = QHBoxLayout()
        ok = QPushButton("Готово")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Скасувати")
        cancel.clicked.connect(self.reject)
        h.addWidget(ok)
        h.addWidget(cancel)
        v.addLayout(h)

        self.setLayout(v)

    def get_selected_roles(self) -> List[str]:
        """Return list of selected roles."""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
