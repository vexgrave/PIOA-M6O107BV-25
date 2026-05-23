from .backend.memory import StudentTable
from .backend.errors import StudentTableError, InvalidAgeError, DuplicateIDError

class TUI:
    def __init__(self, table: StudentTable):
        self.table = table

    def run(self):
        while True:
            print("\nМеню:")
            print("1. Добавить запись")
            print("2. Поиск записей")
            print("3. Сортировать записи")
            print("4. Выход")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self._add_record()
            elif choice == "2":
                self._search_records()
            elif choice == "3":
                self._sort_records()
            elif choice == "4":
                break
            else:
                print("Неверный выбор")

    def _add_record(self):
        try:
            student_id = int(input("ID: ").strip())
            first_name = input("Имя: ").strip()
            second_name = input("Фамилия: ").strip()
            age = int(input("Возраст: ").strip())
            sex = input("Пол (M/F): ").strip()

            record = self.table.create_record(
                student_id, first_name, second_name, age, sex
            )
            print(f"Запись создана: {record}")
        except InvalidAgeError as e:
            print(f"Ошибка: {e}")
        except DuplicateIDError as e:
            print(f"Ошибка: {e}")
        except ValueError:
            print("Ошибка: некорректный ввод данных")

    def _search_records(self):
        print("\nФильтры (оставьте пустым для пропуска):")
        student_id = input("ID: ").strip()
        first_name = input("Имя: ").strip()
        second_name = input("Фамилия: ").strip()
        age = input("Возраст: ").strip()
        sex = input("Пол: ").strip()

        filters = {}
        if student_id:
            filters["student_id"] = int(student_id)
        if first_name:
            filters["first_name"] = first_name
        if second_name:
            filters["second_name"] = second_name
        if age:
            filters["age"] = int(age)
        if sex:
            filters["sex"] = sex

        results = self.table.select_record(**filters)
        if results:
            print("\nНайдено записей:", len(results))
            for record in results:
                print(record)
        else:
            print("Записи не найдены")

    def _sort_records(self):
        field = input("Поле для сортировки (student_id/first_name/second_name/age/sex): ").strip()
        order = input("Порядок (asc/desc): ").strip().lower()
        reverse = order == "desc"

        try:
            results = self.table.sort_records(field, reverse)
            for record in results:
                print(record)
        except ValueError as e:
            print(f"Ошибка: {e}")

    def display_records(self, records: list):
        if not records:
            print("Нет данных для отображения")
            return
        for record in records:
            print(f"ID: {record[0]}, Имя: {record[1]}, Фамилия: {record[2]}, Возраст: {record[3]}, Пол: {record[4]}")