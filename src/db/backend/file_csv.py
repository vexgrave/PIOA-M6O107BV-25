import csv
import os
from pathlib import Path
from .database import Database
from .table import Table
from .errors import (
    TableAlreadyExistsError, TableNotFoundError,
    InvalidStorageDataError, InvalidAgeError, DuplicateIDError
)

class CsvDatabase(Database):
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._tables: dict[str, Table] = {}

    def _get_file_path(self, table_name: str) -> Path:
        return self.data_dir / f"{table_name}.csv"

    def _get_meta_path(self, table_name: str) -> Path:
        return self.data_dir / f"{table_name}.meta"

    def create_table(self, name: str, columns: list[str]) -> Table:
        if name in self._tables:
            raise TableAlreadyExistsError(f"Таблица '{name}' уже существует")
        file_path = self._get_file_path(name)
        if file_path.exists():
            raise TableAlreadyExistsError(f"Файл таблицы '{name}' уже существует")
        table = Table(name, columns)
        self._tables[name] = table
        self._save_meta(name)
        self._save_table(name)
        return table

    def get_table(self, name: str) -> Table | None:
        if name not in self._tables:
            meta_path = self._get_meta_path(name)
            if meta_path.exists():
                self._load_table(name)
        return self._tables.get(name)

    def _save_meta(self, table_name: str) -> None:
        table = self._tables.get(table_name)
        if not table:
            return
        meta_path = self._get_meta_path(table_name)
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(",".join(table.columns))

    def _load_meta(self, table_name: str) -> list[str]:
        meta_path = self._get_meta_path(table_name)
        if not meta_path.exists():
            raise TableNotFoundError(f"Метаданные таблицы '{table_name}' не найдены")
        with open(meta_path, "r", encoding="utf-8") as f:
            columns = f.read().strip().split(",")
        return columns

    def _save_table(self, table_name: str) -> None:
        table = self._tables.get(table_name)
        if not table:
            return
        file_path = self._get_file_path(table_name)
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for record in table.get_records():
                writer.writerow(record)

    def _load_table(self, table_name: str) -> None:
        columns = self._load_meta(table_name)
        table = Table(table_name, columns)
        file_path = self._get_file_path(table_name)
        if not file_path.exists():
            self._tables[table_name] = table
            return
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                record = tuple(row)
                if len(record) == len(columns):
                    converted = []
                    for i, val in enumerate(record):
                        if columns[i] in ["student_id", "age"]:
                            try:
                                converted.append(int(val))
                            except ValueError:
                                converted.append(val)
                        else:
                            converted.append(val)
                    table.add_record(tuple(converted))
        self._tables[table_name] = table

    def insert_record(self, table_name: str, record: tuple) -> None:
        table = self.get_table(table_name)
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
        self._save_table(table_name)

    def select_records(
        self,
        table_name: str,
        filters: dict[str, any] | None = None,
        order_by: str | None = None,
        reverse: bool = False,
    ) -> list[tuple]:
        table = self.get_table(table_name)
        if not table:
            raise TableNotFoundError(f"Таблица '{table_name}' не найдена")
        return table.select(filters, order_by, reverse)

    def save(self) -> None:
        for name in self._tables:
            self._save_meta(name)
            self._save_table(name)

    def load(self) -> None:
        for meta_path in self.data_dir.glob("*.meta"):
            table_name = meta_path.stem
            if table_name not in self._tables:
                self._load_table(table_name)