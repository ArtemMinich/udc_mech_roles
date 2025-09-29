import os
import sys
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def resource_path(relative_path: str) -> str:
    try:
        # PyInstaller створює тимчасову папку _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- CONFIG ----------------
SPREADSHEET_ID = "1vjwB8_4nWp-7BTqo8hBTYuXvPXmRT6MBXQGvsDY8jT0"
SHEET_RANGE = "Відповіді форми (1)"
SERVICE_KEY_FILE = resource_path("resources/service_account.json")
# ----------------------------------------

class FormService:

    @staticmethod
    def _get_service():
        creds = Credentials.from_service_account_file(
            SERVICE_KEY_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        return build("sheets", "v4", credentials=creds)

    @staticmethod
    def fetch_responses():
        """Зчитує відповіді з Google Sheets і показує їх у таблиці"""

        service = FormService._get_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()
        values = result.get("values", [])
        if not values:
            return {}

        data_dict = {}  # ключ: nickname, значення: масив з 3-го стовпця
        for row in values[1:]:  # пропускаємо заголовок
            if len(row) < 3:
                continue  # пропускаємо неповні рядки

            date_str = row[0]  # 1-й стовпець — дата
            nickname = row[1]  # 2-й стовпець — нікнейм
            third_column = [item.strip() for item in row[2].split(",")]  # 3-й стовпець → масив

            # Перетворимо дату у datetime для порівняння
            try:
                row_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                row_date = datetime.min  # якщо невірний формат, вважаємо дуже старою

            # Якщо нікнейм вже є, залишаємо рядок з новішою датою
            if nickname in data_dict:
                existing_date = data_dict[nickname]["date"]
                if row_date > existing_date:
                    data_dict[nickname] = {"date": row_date, "values": third_column}
            else:
                data_dict[nickname] = {"date": row_date, "values": third_column}

        # Повертаємо лише масиви, без дати
        final_dict = {k: v["values"] for k, v in data_dict.items()}
        return final_dict
