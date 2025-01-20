from pathlib import Path
import os


class PopulateMixin:
    BASE_DIR = Path(__file__).resolve().parent.parent

    def __init__(self, excel_name=None):
        self.db_name = os.getenv("db_name")
        self.db_user = os.getenv("db_user_name")
        self.db_password = os.getenv("db_psw")
        self.db_host = os.getenv("db_host")
        self.db_port = os.getenv("db_port")

        if excel_name is not None:
            self.df_path = self.BASE_DIR / "movies" / "data" / f"{excel_name}.xlsx"
