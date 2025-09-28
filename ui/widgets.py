"""
Custom widgets for the clan role manager application.
"""

from PySide6.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem
from PySide6.QtCore import Qt


class DraggableTableWidget(QTableWidget):
    """Table widget that supports drag and drop reordering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def dropEvent(self, event):
        """Handle drop events for reordering."""
        if event.source() == self:
            rows = set()
            for index in self.selectedIndexes():
                rows.add(index.row())

            if len(rows) != 1:
                return

            drag_row = list(rows)[0]
            drop_row = self.rowAt(event.pos().y())

            if drop_row == -1:
                drop_row = self.rowCount() - 1

            if drag_row != drop_row:
                self.move_row(drag_row, drop_row)
                if hasattr(self.parent(), 'on_roles_reordered'):
                    self.parent().on_roles_reordered()

        event.accept()

    def move_row(self, from_row, to_row):
        """Move a row from one position to another."""
        # Store the data
        column_count = self.columnCount()
        from_data = []
        for col in range(column_count):
            item = self.item(from_row, col)
            from_data.append(item.text() if item else "")

        # Remove the row
        self.removeRow(from_row)

        # Adjust target row if necessary
        if to_row > from_row:
            to_row -= 1

        # Insert at new position
        self.insertRow(to_row)
        for col, text in enumerate(from_data):
            self.setItem(to_row, col, QTableWidgetItem(text))

        # Select the moved row
        self.selectRow(to_row)
