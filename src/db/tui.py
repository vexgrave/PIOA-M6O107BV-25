from .backend.memory import MemoryDatabase
from .backend.file import FileDatabase
from .backend.file_csv import CsvDatabase
from .backend.errors import DatabaseError, InvalidAgeError, DuplicateIDError

class TUI:
    def __init__(self, db_type: str = "memory", data_dir: str = "data"):
        if db_type == "memory":
            self.db = MemoryDatabase()
        elif db_type == "file":
            self.db = FileDatabase(data_dir)
        elif db_type == "csv":
            self.db = CsvDatabase(data_dir)
        else:
            self.db = MemoryDatabase()
        self.current_table = None

    def run(self):
        print("Добро пожаловать в СУБД")
        while True:
            print("\nГлавное меню:")
            print("1. Создать таблицу")
            print("2. Выбрать таблицу")
            print("3. Добавить запись")
            print("4. Поиск записей")
            print("5. Сортировать записи")
            print("6. Создать индекс")
            print("7. Сохранить данные")
            print("8. Загрузить данные")
            print("9. Выход")
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                self._create_table()
            elif choice == "2":
                self._select_table()
            elif choice == "3":
                self._add_record()
            elif choice == "4":
                self._search_records()
            elif choice == "5":
                self._sort_records()
            elif choice == "6":
                self._create_index()
            elif choice == "7":
                self.db.save()
                print("Данные сохранены")
            elif choice == "8":
                self.db.load()
                print("Данные загружены")
            elif choice == "9":
                break
            else:
                print("Неверный выбор")

    def _create_table(self):
        name = input("Имя таблицы: ").strip()
        columns_input = input("Колонки (через запятую): ").strip()
        columns = [c.strip() for c in columns_input.split(",") if c.strip()]
        try:
            self.db.create_table(name, columns)
            print(f"Таблица '{name}' создана")
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _select_table(self):
        name = input("Имя таблицы: ").strip()
        table = self.db.get_table(name)
        if table:
            self.current_table = name
            print(f"Выбрана таблица '{name}'")
        else:
            print(f"Таблица '{name}' не найдена")

    def _add_record(self):
        if not self.current_table:
            print("Сначала выберите таблицу")
            return
        table = self.db.get_table(self.current_table)
        if not table:
            print("Таблица не найдена")
            return
        print(f"Введите значения для колонок: {', '.join(table.columns)}")
        values = []
        for col in table.columns:
            val = input(f"{col}: ").strip()
            if col in ["student_id", "age"]:
                try:
                    values.append(int(val))
                except ValueError:
                    values.append(val)
            else:
                values.append(val)
        try:
            self.db.insert_record(self.current_table, tuple(values))
            print("Запись добавлена")
        except InvalidAgeError as e:
            print(f"Ошибка: {e}")
        except DuplicateIDError as e:
            print(f"Ошибка: {e}")
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _search_records(self):
        if not self.current_table:
            print("Сначала выберите таблицу")
            return
        print("Фильтры (оставьте пустым для пропуска):")
        table = self.db.get_table(self.current_table)
        if not table:
            return
        filters = {}
        for col in table.columns:
            val = input(f"{col}: ").strip()
            if val:
                if col in ["student_id", "age"]:
                    try:
                        filters[col] = int(val)
                    except ValueError:
                        filters[col] = val
                else:
                    filters[col] = val
        try:
            results = self.db.select_records(self.current_table, filters)
            if results:
                print(f"\nНайдено записей: {len(results)}")
                for rec in results:
                    print(rec)
            else:
                print("Записи не найдены")
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _sort_records(self):
        if not self.current_table:
            print("Сначала выберите таблицу")
            return
        table = self.db.get_table(self.current_table)
        if not table:
            return
        field = input(f"Поле для сортировки ({', '.join(table.columns)}): ").strip()
        order = input("Порядок (asc/desc): ").strip().lower()
        reverse = order == "desc"
        try:
            results = self.db.select_records(self.current_table, order_by=field, reverse=reverse)
            for rec in results:
                print(rec)
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _create_index(self):
        if not self.current_table:
            print("Сначала выберите таблицу")
            return
        table = self.db.get_table(self.current_table)
        if not table:
            return
        field = input(f"Поле для индекса ({', '.join(table.columns)}): ").strip()
        try:
            table.create_index(field)
            print(f"Индекс создан для поля '{field}'")
        except DatabaseError as e:
            print(f"Ошибка: {e}")