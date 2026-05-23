import json
import os
from .database import Database
from .table import Table
from .errors import TableNotFoundError, FileStorageError

class FileDatabase(Database):
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self._tables = {}
        os.makedirs(data_dir, exist_ok=True)

    def _get_table_path(self, name):
        return os.path.join(self.data_dir, f"{name}.json")

    def create_table(self, name, columns):
        if name in self._tables or os.path.exists(self._get_table_path(name)):
            raise ValueError(f"Таблица '{name}' уже существует")
        table = Table(name, columns)
        self._tables[name] = table
        self._save_table(name)

    def get_table(self, name):
        if name not in self._tables:
            if os.path.exists(self._get_table_path(name)):
                self._load_table(name)
            else:
                raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return self._tables[name]

    def list_tables(self):
        self._scan_tables()
        return list(self._tables.keys())

    def _scan_tables(self):
        if not os.path.exists(self.data_dir):
            return
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                name = filename[:-5]
                if name not in self._tables:
                    self._load_table(name)

    def _save_table(self, name):
        if name not in self._tables:
            return
        path = self._get_table_path(name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._tables[name].to_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise FileStorageError(f"Ошибка записи файла: {e}")

    def _load_table(self, name):
        path = self._get_table_path(name)
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._tables[name] = Table.from_dict(data)
        except (IOError, json.JSONDecodeError) as e:
            raise FileStorageError(f"Ошибка чтения файла: {e}")

    def save(self):
        for name in self._tables:
            self._save_table(name)

    def load(self):
        self._scan_tables()