"""
Вкладки для додатку керування ролями в клані.
"""

import sqlite3
from typing import List, Dict, Tuple

import easyocr
from PySide6 import QtGui
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel, QHeaderView, QInputDialog,
    QMenu, QApplication, QProgressBar
)
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt, QThread, Signal

from services.player_service import PlayerService
from services.role_service import RoleService
from ui.dialogs import PlayerDialog, RoleAssignDialog, RoleSelectDialog
from ui.widgets import DraggableTableWidget


class PlayersTab(QWidget):
    """Вкладка для керування гравцями."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._init_ui()

    def _init_ui(self):
        """Ініціалізація інтерфейсу."""
        v = QVBoxLayout()

        # Таблиця гравців
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Ім'я", "Обрані ролі"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Автоматичне підлаштування ширини колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # Контекстне меню
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_players_context_menu)

        v.addWidget(self.table)

        # Кнопки CRUD
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

        add_role_assignment_p = QPushButton("Додати призначення")
        add_role_assignment_p.clicked.connect(self.add_role_assignment_ui)
        hb.addWidget(add_role_assignment_p)

        clear_all_p = QPushButton("Очистити всі ролі")
        clear_all_p.clicked.connect(self.clear_all_preferences_ui)
        hb.addWidget(clear_all_p)

        hb.addStretch()
        v.addLayout(hb)
        self.setLayout(v)

    def format_preferences_with_counts(self, preferences: List[str], role_assignments: Dict[str, Tuple[int, str]]) -> str:
        """Форматує обрані ролі з кількістю призначень у дужках."""
        formatted = []
        for role in preferences:
            count = role_assignments.get(role, [0, ""])[0]
            date = role_assignments.get(role, [0, ""])[1]
            formatted.append(f"{role} ({count}{f' - {date}'if date!=''else '' })")
        return ', '.join(formatted)

    def refresh(self):
        """Оновлення таблиці гравців."""
        self.table.setRowCount(0)
        players = PlayerService.list_players()
        for p in players:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(p.nickname))

            # Форматуємо обрані ролі з кількістю призначень
            formatted_prefs = self.format_preferences_with_counts(
                p.preferences, p.role_assignments
            )
            self.table.setItem(r, 1, QTableWidgetItem(formatted_prefs))

    def add_player_ui(self):
        """Додавання нового гравця через UI."""
        dlg = PlayerDialog(self, existing_roles=RoleService.list_roles())
        if dlg.exec() == QDialog.Accepted:
            nick, prefs = dlg.get_data()
            if not nick:
                QMessageBox.warning(self, "Помилка", "Нік обов'язкове поле.")
                return
            try:
                PlayerService.add_player(nick, prefs)
                self.refresh()
                # Оновлення вкладки ролей
                if hasattr(self.parent_window, 'roles_tab'):
                    self.parent_window.roles_tab.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Помилка", str(e))

    def edit_player_ui(self):
        """Редагування існуючого гравця через UI."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Помилка", "Виберіть рядок.")
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
                    QMessageBox.warning(self, "Помилка", "Нік обов'язкове поле.")
                    return
                PlayerService.update_player(nickname, newnick, prefs)
                self.refresh()
                if hasattr(self.parent_window, 'roles_tab'):
                    self.parent_window.roles_tab.refresh()
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def delete_player_ui(self):
        """Видалення гравця через UI."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Помилка", "Виберіть рядок.")
            return
        nickname = sel[0].text()
        if QMessageBox.question(self, "Підтвердження", f"Видалити {nickname}?") == QMessageBox.Yes:
            PlayerService.delete_player(nickname)
            self.refresh()
            if hasattr(self.parent_window, 'roles_tab'):
                self.parent_window.roles_tab.refresh()

    def add_role_assignment_ui(self):
        """Видалення гравця через UI."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Помилка", "Виберіть рядок.")
            return
        nickname = sel[0].text()
        try:
            player = PlayerService.get_player(nickname)
            dlg = RoleSelectDialog(
                self,
                preselected=player.preferences
            )
            if dlg.exec() == QDialog.Accepted:
                selected = dlg.get_selected_roles()
                for role in selected:
                    PlayerService.increment_role_assignment(player.nickname, role)
                self.refresh()
                if hasattr(self.parent_window, 'roles_tab'):
                    self.parent_window.roles_tab.refresh()
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def clear_all_preferences_ui(self):
        """Очистити всі обрані ролі у всіх гравців."""
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
            if hasattr(self.parent_window, 'roles_tab'):
                self.parent_window.roles_tab.refresh()
            QMessageBox.information(self, "Успіх", "Всі обрані ролі було очищено у всіх гравців")

    def show_players_context_menu(self, position):
        """Контекстне меню для таблиці гравців."""
        menu = QMenu(self)

        # Додати гравця
        add_action = menu.addAction("Додати гравця")
        add_action.triggered.connect(self.add_player_ui)

        if self.table.itemAt(position):
            edit_action = menu.addAction("Редагувати гравця")
            edit_action.triggered.connect(self.edit_player_ui)

            delete_action = menu.addAction("Видалити гравця")
            delete_action.triggered.connect(self.delete_player_ui)

            delete_action = menu.addAction("Додати призначення")
            delete_action.triggered.connect(self.add_role_assignment_ui)


        menu.addSeparator()

        clear_action = menu.addAction("Очистити всі ролі")
        clear_action.triggered.connect(self.clear_all_preferences_ui)

        menu.exec_(self.table.mapToGlobal(position))


class RolesTab(QWidget):
    """Вкладка для керування ролями з пріоритетом."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._init_ui()

    def _init_ui(self):
        """Ініціалізація інтерфейсу."""
        v = QVBoxLayout()

        # Інструкції
        instructions = QLabel("Перетягніть ролі для зміни пріоритетності (вище = вищий пріоритет)")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        v.addWidget(instructions)

        # Таблиця ролей з drag & drop
        self.table = DraggableTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Назва ролі", "Пріоритет", "Кількість гравців"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_roles_context_menu)

        v.addWidget(self.table)

        # Кнопки CRUD
        hb = QHBoxLayout()
        add_r = QPushButton("Додати роль")
        add_r.clicked.connect(self.add_role_ui)
        hb.addWidget(add_r)

        assign_r = QPushButton("Призначити роль гравцям")
        assign_r.clicked.connect(self.assign_role_to_players_ui)
        hb.addWidget(assign_r)

        del_r = QPushButton("Видалити роль")
        del_r.clicked.connect(self.delete_role_ui)
        hb.addWidget(del_r)
        hb.addStretch()

        v.addLayout(hb)
        self.setLayout(v)

    def refresh(self):
        """Оновлення таблиці ролей."""
        self.table.setRowCount(0)
        roles = RoleService.list_roles_with_priority()
        role_player_counts = RoleService.get_role_player_counts()

        for r in roles:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(r.priority)))

            player_count = role_player_counts.get(r.name, 0)
            self.table.setItem(row, 2, QTableWidgetItem(str(player_count)))

    def on_roles_reordered(self):
        """При зміні порядку ролей через drag & drop."""
        role_names = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                role_names.append(item.text())

        if role_names:
            RoleService.reorder_roles(role_names)
            self.refresh()

    def assign_role_to_players_ui(self):
        """Призначення ролі конкретним гравцям."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Помилка", "Оберіть роль")
            return

        role_name = sel[0].text()
        all_players = [p.nickname for p in PlayerService.list_players()]
        current_assignments = PlayerService.get_players_with_role(role_name)

        if not all_players:
            QMessageBox.warning(self, "Помилка", "Немає гравців для призначення")
            return

        dlg = RoleAssignDialog(self, role_name, all_players, current_assignments)

        if dlg.exec() == QDialog.Accepted:
            selected_players = dlg.get_selected_players()
            PlayerService.set_players_for_role(role_name, selected_players)

            if selected_players:
                players_str = ", ".join(selected_players)
                QMessageBox.information(self, "Успіх",
                    f"Роль '{role_name}' призначена гравцям:\n{players_str}")
            else:
                QMessageBox.information(self, "Успіх",
                    f"Роль '{role_name}' видалена у всіх гравців")

            if hasattr(self.parent_window, 'players_tab'):
                self.parent_window.players_tab.refresh()
            self.refresh()

    def add_role_ui(self):
        """Додавання нової ролі."""
        text, ok = QInputDialog.getText(self, "Додати роль", "Назва ролі:")
        if ok and text.strip():
            max_priority = len(RoleService.list_roles_with_priority())
            RoleService.add_role(text.strip(), max_priority)
            QMessageBox.information(self, "Успіх", f"Роль '{text}' додана")
            self.refresh()

    def delete_role_ui(self):
        """Видалення ролі."""
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Помилка", "Виберіть роль")
            return
        role_name = sel[0].text()
        if QMessageBox.question(self, "Підтвердження", f"Видалити роль '{role_name}'?") == QMessageBox.Yes:
            RoleService.delete_role(role_name)
            self.refresh()
            if hasattr(self.parent_window, 'players_tab'):
                self.parent_window.players_tab.refresh()

    def show_roles_context_menu(self, position):
        """Контекстне меню для таблиці ролей."""
        menu = QMenu(self)

        add_action = menu.addAction("Додати роль")
        add_action.triggered.connect(self.add_role_ui)

        if self.table.itemAt(position):
            assign_action = menu.addAction("Призначити роль гравцям")
            assign_action.triggered.connect(self.assign_role_to_players_ui)

            delete_action = menu.addAction("Видалити роль")
            delete_action.triggered.connect(self.delete_role_ui)

        menu.exec_(self.table.mapToGlobal(position))


class OCRThread(QThread):
    progress = Signal(int)       # сигнал прогресу (0-100)
    finished = Signal(list)      # сигнал результатів

    def __init__(self, reader, img_path):
        super().__init__()
        self.reader = reader
        self.img_path = img_path

    def run(self):
        results = self.reader.readtext(self.img_path)
        total = len(results)
        for i, r in enumerate(results):
            percent = int((i + 1) / total * 100)
            self.progress.emit(percent)
        self.finished.emit(results)

class DetectionNicksTab(QWidget):
    """Вкладка для детекції нікнеймів зі скріншота Discord."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.reader = easyocr.Reader(['en', 'uk'])

    def _init_ui(self):
        v = QVBoxLayout()

        self.info_label = QLabel("Вставте скріншот (Ctrl+V)")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #555; font-style: italic;")
        v.addWidget(self.info_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #aaa; min-height: 200px;")
        v.addWidget(self.image_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        v.addWidget(self.progress_bar)

        self.results_table = QTableWidget(0, 2)
        self.results_table.setHorizontalHeaderLabels(["Нік", "Ймовірність"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        v.addWidget(self.results_table)

        self.setLayout(v)

        # Глобальний Ctrl+V
        paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        paste_shortcut.activated.connect(self.paste_image)

    def paste_image(self):
        """Вставка з буфера та запуск OCR."""
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaledToWidth(400, Qt.SmoothTransformation))
            tmp_path = "clipboard.png"
            pixmap.save(tmp_path, "PNG")
            self.run_ocr(tmp_path)

    def run_ocr(self, img_path: str):
        """Запуск OCR у окремому потоці з прогрес-баром."""
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.ocr_thread = OCRThread(self.reader, img_path)
        self.ocr_thread.progress.connect(self.progress_bar.setValue)
        self.ocr_thread.finished.connect(self.show_results)
        self.ocr_thread.start()

    def show_results(self, results):
        """Вивід результатів OCR у таблицю з перевіркою [UKR]."""
        self.progress_bar.setVisible(False)
        self.results_table.setRowCount(0)
        for box, text, prob in results:
            if text.startswith("[UKR]"):
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(text))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"{prob:.2f}"))
