from .backend.memory import StudentTable

class DatabaseTUI:
    def __init__(self):
        self.table = StudentTable()

    def print_records(self, records):
        if not records:
            print("Записей не найдено.")
            return
        headers = ["ID", "Имя", "Фамилия", "Возраст", "Пол"]
        header_line = "".join(f"{h:<15}" for h in headers)
        print(f"\n{header_line}")
        print("-" * len(header_line))
        for rec in records:
            line = "".join(f"{str(v):<15}" for v in rec)
            print(line)

    def run(self):
        print("Система управления данными студентов")
        while True:
            print("\n[MENU]")
            print("1. Добавить запись")
            print("2. Показать все записи")
            print("3. Найти запись по ID")
            print("4. Найти по фильтру")
            print("5. Обновить запись")
            print("6. Удалить запись")
            print("7. Сортировать записи")
            print("8. Выход")
            choice = input("Введите действие: ").strip()
            try:
                if choice == "1":
                    self.add_record_menu()
                elif choice == "2":
                    self.show_all_menu()
                elif choice == "3":
                    self.find_by_id_menu()
                elif choice == "4":
                    self.find_by_filter_menu()
                elif choice == "5":
                    self.update_record_menu()
                elif choice == "6":
                    self.delete_record_menu()
                elif choice == "7":
                    self.sort_records_menu()
                elif choice == "8":
                    print("Выход из программы...")
                    break
                else:
                    print("Неверный пункт меню.")
            except Exception as e:
                print(f"Ошибка: {e}")

    def add_record_menu(self):
        first_name = input("Имя: ").strip()
        second_name = input("Фамилия: ").strip()
        age_str = input("Возраст: ").strip()
        sex = input("Пол (М/Ж): ").strip()
        try:
            age = int(age_str)
        except ValueError:
            print("Ошибка: возраст должен быть числом.")
            return
        record_id = self.table.create_record(first_name, second_name, age, sex)
        print(f"Запись добавлена. ID: {record_id}")

    def show_all_menu(self):
        records = self.table.select_all()
        self.print_records(records)

    def find_by_id_menu(self):
        try:
            record_id = int(input("Введите ID записи: ").strip())
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        try:
            record = self.table.select_record(record_id)
            self.print_records([record])
        except KeyError as e:
            print(f"Ошибка: {e}")

    def find_by_filter_menu(self):
        field = input("Поле для фильтра (id/first_name/second_name/age/sex): ").strip()
        value = input("Значение: ").strip()
        try:
            results = self.table.select_by_filter(field, value)
            self.print_records(results)
        except ValueError as e:
            print(f"Ошибка: {e}")

    def update_record_menu(self):
        try:
            record_id = int(input("Введите ID записи: ").strip())
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        first_name = input("Новое имя (Enter - без изменений): ").strip()
        second_name = input("Новая фамилия (Enter - без изменений): ").strip()
        age_str = input("Новый возраст (Enter - без изменений): ").strip()
        sex = input("Новый пол (Enter - без изменений): ").strip()
        
        age = int(age_str) if age_str else None
        
        try:
            self.table.update_record(
                record_id,
                first_name if first_name else None,
                second_name if second_name else None,
                age,
                sex if sex else None
            )
            print("Запись обновлена.")
        except (KeyError, ValueError) as e:
            print(f"Ошибка: {e}")

    def delete_record_menu(self):
        try:
            record_id = int(input("Введите ID записи для удаления: ").strip())
        except ValueError:
            print("Ошибка: ID должен быть числом.")
            return
        try:
            self.table.delete_record(record_id)
            print("Запись удалена.")
        except KeyError as e:
            print(f"Ошибка: {e}")

    def sort_records_menu(self):
        field = input("Поле для сортировки (id/first_name/second_name/age/sex): ").strip()
        order = input("Порядок (asc - по возрастанию, desc - по убыванию): ").strip().lower()
        ascending = order != "desc"
        try:
            sorted_records = self.table.sort_records(field, ascending)
            self.print_records(sorted_records)
        except ValueError as e:
            print(f"Ошибка: {e}")