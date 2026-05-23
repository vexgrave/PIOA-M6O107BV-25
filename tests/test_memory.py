import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.student_table = StudentTable()

    def test_student_table_allocation(self):
        self.assertIsInstance(self.student_table, StudentTable)

    def test_create_record(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
            (11, "Jack", "Thomas", 18, "M"),
            (12, "Kathy", "Jackson", 23, "F"),
        ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.student_table.create_record(*test_data)
                self.assertEqual(record, test_data)

    def test_create_record_negative_age(self):
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
            (3, "Alice", "Johnson", -10, "F"),
        ]
        error_message = "Поле age не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidAgeError) as context:
                    self.student_table.create_record(*test_data)
                self.assertEqual(str(context.exception), error_message)

    def test_create_record_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.student_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

    def test_select_record(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        cases = [
            {
                "name": "Выбор без фильтров",
                "filters": {},
                "expected": test_datas,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"student_id": 1},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по имени",
                "filters": {"first_name": "Jane"},
                "expected": [test_datas[1]],
            },
            {
                "name": "Фильтр по фамилии",
                "filters": {"second_name": "Johnson"},
                "expected": [test_datas[2]],
            },
            {
                "name": "Фильтр по возрасту",
                "filters": {"age": 20},
                "expected": [test_datas[0], test_datas[6]],
            },
            {
                "name": "Фильтр по полу",
                "filters": {"sex": "F"},
                "expected": [
                    test_datas[1],
                    test_datas[2],
                    test_datas[5],
                    test_datas[7],
                    test_datas[9],
                ],
            },
        ]

        for case in cases:
            with self.subTest(
                case=case["name"], filters=case["filters"], expected=case["expected"]
            ):
                records = self.student_table.select_record(**case["filters"])
                self.assertEqual(records, case["expected"])

    def test_sort_records_by_field(self):
        test_datas = [
            (3, "Alice", "Johnson", 19, "F"),
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        sorted_by_id = self.student_table.sort_records("student_id")
        self.assertEqual(sorted_by_id[0][0], 1)
        self.assertEqual(sorted_by_id[1][0], 2)
        self.assertEqual(sorted_by_id[2][0], 3)

        sorted_by_age_desc = self.student_table.sort_records("age", reverse=True)
        self.assertEqual(sorted_by_age_desc[0][3], 22)
        self.assertEqual(sorted_by_age_desc[1][3], 20)
        self.assertEqual(sorted_by_age_desc[2][3], 19)

        sorted_by_name = self.student_table.sort_records("first_name")
        self.assertEqual(sorted_by_name[0][1], "Alice")
        self.assertEqual(sorted_by_name[1][1], "Jane")
        self.assertEqual(sorted_by_name[2][1], "John")

    def test_sort_records_invalid_field(self):
        with self.assertRaises(ValueError):
            self.student_table.sort_records("invalid_field")

    def test_create_record_strips_whitespace(self):
        record = self.student_table.create_record(1, "  John  ", "  Doe  ", 20, "  M  ")
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))

    def test_select_record_returns_copy(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        result1 = self.student_table.select_record()
        result2 = self.student_table.select_record()
        self.assertIsNot(result1, result2)
        self.assertEqual(result1, result2)