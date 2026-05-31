from .backend.memory import InMemoryDB
from .backend.file import JSONDatabase, CSVDatabase


class DatabaseTUI:
    def __init__(self, db_type="memory"):
        if db_type == "json":
            self.db = JSONDatabase()
        elif db_type == "csv":
            self.db = CSVDatabase()
        else:
            self.db = InMemoryDB()
        self.db_type = db_type

    def print_table(self, table):
        if not table.rows:
            print("Записей пока нет.")
            return
        headers = ["id"] + table.columns
        header_line = "".join(f"{h:<15}" for h in headers)
        print(f"\n{header_line}")
        print("-" * len(header_line))
        for row in table.rows:
            line = "".join(f"{str(row.get(h, '')):<15}" for h in headers)
            print(line)

    def run(self):
        print(f"База данных ({self._get_db_type_name()})")
        while True:
            print("\n[MENU]")
            print("1. Создать таблицу")
            print("2. Добавить запись")
            print("3. Прочитать записи")
            print("4. Обновить запись")
            print("5. Удалить запись")
            print("6. Сортировать записи")
            print("7. Создать индекс")
            print("8. Выход")
            choice = input("Введите действие: ").strip()
            try:
                if choice == "1":
                    self.create_table_menu()
                elif choice == "2":
                    self.add_record_menu()
                elif choice == "3":
                    self.read_records_menu()
                elif choice == "4":
                    self.update_record_menu()
                elif choice == "5":
                    self.delete_record_menu()
                elif choice == "6":
                    self.sort_records_menu()
                elif choice == "7":
                    self.create_index_menu()
                elif choice == "8":
                    self.db.save()
                    print("Выход из программы...")
                    break
                else:
                    print("Неверный пункт меню.")
            except Exception as e:
                print(f"Ошибка: {e}")

    def _get_db_type_name(self):
        if self.db_type == "json":
            return "файловая JSON"
        elif self.db_type == "csv":
            return "файловая CSV"
        else:
            return "оперативная память"

    def create_table_menu(self):
        name = input("Введите название таблицы: ").strip()
        cols_str = input("Введите поля через запятую: ").strip()
        cols = [c.strip() for c in cols_str.split(",") if c.strip()]
        if not cols:
            print("Ошибка: введите хотя бы одно поле.")
            return
        self.db.create_table(name, cols)
        print(f"Таблица '{name}' успешно создана.")

    def add_record_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Доступные таблицы: {tables}")
        tbl_name = input("Введите название таблицы: ").strip()
        table = self.db.get_table(tbl_name)
        data = {}
        print(f"Введите данные для полей: {table.columns}")
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
        new_id = table.add(data)
        print(f"Запись добавлена. ID: {new_id}")
        self.db.save()

    def read_records_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Доступные таблицы: {tables}")
        tbl_name = input("Введите название таблицы: ").strip()
        table = self.db.get_table(tbl_name)
        print(f"Доступные поля для фильтрации: {table.columns + ['id']}")
        print("Пример: name=Иван age=20")
        filt_str = input("Введите условия фильтрации (или нажмите Enter для показа всех записей): ").strip()
        filters = {}
        if filt_str:
            for part in filt_str.split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    filters[k.strip()] = v.strip()
        results = table.read(filters)
        if results:
            print(f"Найдено записей: {len(results)}")
            temp_table = table.__class__(table.name, table.columns)
            temp_table.rows = results
            self.print_table(temp_table)
        else:
            print("Записи не найдены.")

    def update_record_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Доступные таблицы: {tables}")
        tbl_name = input("Введите название таблицы: ").strip()
        table = self.db.get_table(tbl_name)
        try:
            rec_id = int(input("Введите ID записи: "))
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        new_data = {}
        for col in table.columns:
            val = input(f"Новое значение для {col} (Enter - пропуск): ").strip()
            if val:
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                new_data[col] = val
        if table.update(rec_id, new_data):
            print("Запись успешно обновлена.")
            self.db.save()
        else:
            print("Запись с таким ID не найдена.")

    def delete_record_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Доступные таблицы: {tables}")
        tbl_name = input("Введите название таблицы: ").strip()
        table = self.db.get_table(tbl_name)
        try:
            rec_id = int(input("Введите ID записи для удаления: "))
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        if table.delete(rec_id):
            print("Запись успешно удалена.")
            self.db.save()
        else:
            print("Запись с таким ID не найдена.")

    def sort_records_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Доступные таблицы: {tables}")
        tbl_name = input("Введите название таблицы: ").strip()
        table = self.db.get_table(tbl_name)
        print(f"Доступные поля для сортировки: {table.columns + ['id']}")
        field = input("Введите поле для сортировки: ").strip()
        print("\nВыберите порядок сортировки:")
        print("1. По возрастанию")
        print("2. По убыванию")
        order_choice = input("Введите номер: ").strip()
        reverse = order_choice == "2"
        try:
            table.sort(field, reverse)
            print(f"Записи отсортированы по полю '{field}'.")
            self.print_table(table)
        except Exception as e:
            print(f"Ошибка: {e}")

    def create_index_menu(self):
        tables = self.db.list_tables()
        if not tables:
            print("Нет доступных таблиц.")
            return
        print(f"Доступные таблицы: {tables}")
        tbl_name = input("Введите название таблицы: ").strip()
        table = self.db.get_table(tbl_name)
        print(f"Доступные поля для индексации: {table.columns}")
        field = input("Введите поле для создания индекса: ").strip()
        try:
            table.create_index(field)
            print(f"Индекс создан для поля '{field}'.")
            self.db.save()
        except Exception as e:
            print(f"Ошибка: {e}")