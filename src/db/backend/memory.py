from .database import Database
from .table import Table
from .errors import TableAlreadyExistsError, TableNotFoundError, InvalidAgeError, DuplicateIDError

class MemoryDatabase(Database):
    def __init__(self) -> None:
        self._tables: dict[str, Table] = {}

    def create_table(self, name: str, columns: list[str]) -> Table:
        if name in self._tables:
            raise TableAlreadyExistsError(f"Таблица '{name}' уже существует")
        table = Table(name, columns)
        self._tables[name] = table
        return table

    def get_table(self, name: str) -> Table | None:
        return self._tables.get(name)

    def insert_record(self, table_name: str, record: tuple) -> None:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        if "age" in table.columns:
            age_index = table.columns.index("age")
            if record[age_index] < 0:
                raise InvalidAgeError("Возраст не может быть отрицательным")
        if "student_id" in table.columns:
            id_index = table.columns.index("student_id")
            record_id = record[id_index]
            for existing in table.get_records():
                if existing[id_index] == record_id:
                    raise DuplicateIDError(f"Запись с id={record_id} уже существует")
        table.add_record(record)
        for column in table._indexes:
            table.update_index(column, record, "add")

    def select_records(
        self,
        table_name: str,
        filters: dict[str, any] | None = None,
        order_by: str | None = None,
        reverse: bool = False,
    ) -> list[tuple]:
        table = self._tables.get(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.select(filters, order_by, reverse)

    def save(self) -> None:
        pass

    def load(self) -> None:
        pass