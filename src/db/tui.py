from .backend.memory import MemoryDatabase
from .backend.file import FileDatabase

class DatabaseTUI:
    def __init__(self, storage_type="memory", data_dir="data"):
        if storage_type == "file":
            self.db = FileDatabase(data_dir)
        else:
            self.db = MemoryDatabase()
        self.storage_type = storage_type

    def print_records(self, records):
        if not records:
            print("Записей не найдено.")
            return
        headers = list(records[0].keys())
        header_line = "".join(f"{h:<15}" for h in headers)
        print(f"\n{header_line}")
        print("-" * len(header_line))
        for rec in records:
            line = "".join(f"{str(rec.get(h, '')):<15}" for h in headers)
            print(line)

    def run(self):
        print(f"Система управления данными ({self.storage_type})")
        while True:
            print("\n[MENU]")
            print("1. Создать таблицу")
            print("2. Добавить запись")
            print("3. Показать все записи")
            print("4. Найти запись по ID")
            print("5. Найти по фильтру")
            print("6. Обновить запись")
            print("7. Удалить запись")
            print("8. Сортировать записи")
            print("9. Сохранить данные")
            print("10. Выход")
            choice = input("Введите действие: ").strip()
            try:
                if choice == "1":
                    self.create_table_menu()
                elif choice == "2":
                    self.add_record_menu()
                elif choice == "3":
                    self.show_all_menu()
                elif choice == "4":
                    self.find_by_id_menu()
                elif choice == "5":
                    self.find_by_filter_menu()
                elif choice == "6":
                    self.update_record_menu()
                elif choice == "7":
                    self.delete_record_menu()
                elif choice == "8":
                    self.sort_records_menu()
                elif choice == "9":
                    self.db.save()
                    print("Данные сохранены.")
                elif choice == "10":
                    if self.storage_type == "file":
                        self.db.save()
                    print("Выход из программы...")
                    break
                else:
                    print("Неверный пункт меню.")
            except Exception as e:
                print(f"Ошибка: {e}")

    def create_table_menu(self):
        name = input("Название таблицы: ").strip()
        cols_str = input("Поля через запятую: ").strip()
        cols = [c.strip() for c in cols_str.split(",") if c.strip()]
        if not cols:
            print("Ошибка: введите хотя бы одно поле.")
            return
        self.db.create_table(name, cols)
        print(f"Таблица '{name}' создана.")

    def add_record_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        data = {}
        print(f"Введите данные для: {table.columns}")
        for col in table.columns:
            val = input(f"  {col}: ").strip()
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    pass
            data[col] = val
        record_id = table.create_record(data)
        print(f"Запись добавлена. ID: {record_id}")

    def show_all_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        records = table.select_all()
        self.print_records(records)

    def find_by_id_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        try:
            record_id = int(input("ID записи: ").strip())
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        try:
            record = table.select_record(record_id)
            self.print_records([record])
        except Exception as e:
            print(f"Ошибка: {e}")

    def find_by_filter_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        field = input("Поле для фильтра: ").strip()
        value = input("Значение: ").strip()
        try:
            results = table.select_by_filter(field, value)
            self.print_records(results)
        except Exception as e:
            print(f"Ошибка: {e}")

    def update_record_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        try:
            record_id = int(input("ID записи: ").strip())
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        new_data = {}
        for col in table.columns:
            val = input(f"Новое {col} (Enter - пропуск): ").strip()
            if val:
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                new_data[col] = val
        if not new_data:
            print("Нет данных для обновления.")
            return
        try:
            table.update_record(record_id, new_data)
            print("Запись обновлена.")
        except Exception as e:
            print(f"Ошибка: {e}")

    def delete_record_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        try:
            record_id = int(input("ID записи: ").strip())
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        try:
            table.delete_record(record_id)
            print("Запись удалена.")
        except Exception as e:
            print(f"Ошибка: {e}")

    def sort_records_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Таблицы: {tables}")
        tbl_name = input("Выберите таблицу: ").strip()
        table = self.db.get_table(tbl_name)
        field = input("Поле для сортировки: ").strip()
        order = input("Порядок (asc/desc): ").strip().lower()
        ascending = order != "desc"
        try:
            sorted_records = table.sort_records(field, ascending)
            self.print_records(sorted_records)
        except Exception as e:
            print(f"Ошибка: {e}")