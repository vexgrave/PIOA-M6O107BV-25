import json
import csv
from pathlib import Path
from .database import Database
from .table import Table
from .errors import TableNotFoundError, TableAlreadyExistsError, FileDatabaseError


class JSONDatabase(Database):
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tables = {}
        self.load()

    def create_table(self, name, columns):
        if name in self.tables:
            raise TableAlreadyExistsError(f"Таблица '{name}' уже существует")
        self.tables[name] = Table(name, columns)
        self.save()

    def get_table(self, name):
        if name not in self.tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return self.tables[name]

    def list_tables(self):
        return list(self.tables.keys())

    def save(self):
        for table_name, table in self.tables.items():
            file_path = self.data_dir / f"{table_name}.json"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(table.to_dict(), f, ensure_ascii=False, indent=2)
            except IOError as e:
                raise FileDatabaseError(f"Ошибка записи файла {file_path}: {e}")

    def load(self):
        self.tables = {}
        if not self.data_dir.exists():
            return
        
        for file_path in self.data_dir.glob("*.json"):
            try:
                if file_path.stat().st_size == 0:
                    raise FileDatabaseError(f"Пустой файл: {file_path}")
                    
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    table = Table.from_dict(data)
                    self.tables[table.name] = table
            except json.JSONDecodeError as e:
                raise FileDatabaseError(f"Ошибка парсинга JSON в файле {file_path}: {e}")
            except (KeyError, TypeError) as e:
                raise FileDatabaseError(f"Ошибка в структуре файла {file_path}: {e}")
            except IOError as e:
                raise FileDatabaseError(f"Ошибка чтения файла {file_path}: {e}")

    def close(self):
        self.save()


class CSVDatabase(Database):
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tables = {}
        self.meta_file = self.data_dir / "metadata.json"
        self.load()

    def create_table(self, name, columns):
        if name in self.tables:
            raise TableAlreadyExistsError(f"Таблица '{name}' уже существует")
        self.tables[name] = Table(name, columns)
        self._save_table(name)
        self._save_metadata()

    def get_table(self, name):
        if name not in self.tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        return self.tables[name]

    def list_tables(self):
        return list(self.tables.keys())

    def save(self):
        for table_name in self.tables:
            self._save_table(table_name)
        self._save_metadata()

    def load(self):
        self.tables = {}
        if not self.meta_file.exists():
            return
        
        try:
            if self.meta_file.stat().st_size == 0:
                return
                
            with open(self.meta_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            for table_name, table_meta in metadata.items():
                table = Table(table_name, table_meta["columns"])
                table.next_id = table_meta["next_id"]
                self.tables[table_name] = table
                self._load_table(table_name)
                
                if "indexes" in table_meta:
                    table.indexes = table_meta["indexes"]
        except json.JSONDecodeError as e:
            raise FileDatabaseError(f"Ошибка парсинга метаданных: {e}")
        except (KeyError, TypeError) as e:
            raise FileDatabaseError(f"Ошибка в метаданных: {e}")
        except IOError as e:
            raise FileDatabaseError(f"Ошибка чтения метаданных: {e}")

    def _save_table(self, table_name):
        table = self.tables[table_name]
        csv_file = self.data_dir / f"{table_name}.csv"
        
        try:
            with open(csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["id"] + table.columns)
                writer.writeheader()
                for row in table.rows:
                    writer.writerow(row)
        except IOError as e:
            raise FileDatabaseError(f"Ошибка записи файла {csv_file}: {e}")

    def _load_table(self, table_name):
        table = self.tables[table_name]
        csv_file = self.data_dir / f"{table_name}.csv"
        
        if csv_file.exists():
            try:
                with open(csv_file, "r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        parsed_row = {}
                        for key, value in row.items():
                            if key == "id":
                                parsed_row[key] = int(value)
                            else:
                                try:
                                    parsed_row[key] = int(value)
                                except ValueError:
                                    try:
                                        parsed_row[key] = float(value)
                                    except ValueError:
                                        parsed_row[key] = value
                        table.rows.append(parsed_row)
            except IOError as e:
                raise FileDatabaseError(f"Ошибка чтения файла {csv_file}: {e}")

    def _save_metadata(self):
        metadata = {}
        for table_name, table in self.tables.items():
            metadata[table_name] = {
                "columns": table.columns,
                "next_id": table.next_id,
                "indexes": table.indexes
            }
        
        try:
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise FileDatabaseError(f"Ошибка записи метаданных: {e}")

    def close(self):
        self.save()