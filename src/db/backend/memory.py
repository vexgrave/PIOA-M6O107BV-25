from .database import Database
from .table import Table
from .errors import TableNotFoundError, TableAlreadyExistsError


class InMemoryDB(Database):
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns):
        if name in self.tables:
            raise TableAlreadyExistsError(f"Таблица '{name}' уже существует")
        self.tables[name] = Table(name, columns)

    def get_table(self, name):
        if name not in self.tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return self.tables[name]

    def list_tables(self):
        return list(self.tables.keys())

    def save(self):
        pass

    def load(self):
        pass