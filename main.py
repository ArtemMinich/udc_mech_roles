import sys

from PySide6.QtWidgets import QApplication

from database.db_manager import db_manager
from ui.main_window import MainWindow

if __name__ == '__main__':
    db_manager.init_db()
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())