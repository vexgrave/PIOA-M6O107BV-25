from .database import Database
from .table import Table
from .errors import TableNotFoundError

class MemoryDatabase(Database):
    def __init__(self):
        self._tables = {}

    def create_table(self, name, columns):
        if name in self._tables:
            raise ValueError(f"Таблица '{name}' уже существует")
        self._tables[name] = Table(name, columns)

    def get_table(self, name):
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return self._tables[name]

    def list_tables(self):
        return list(self._tables.keys())

    def save(self):
        pass

    def load(self):
        pass