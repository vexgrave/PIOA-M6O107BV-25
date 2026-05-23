from .errors import DuplicateIDError, InvalidAgeError

type StudentRecord = tuple[int, str, str, int, str]

class StudentTable:
    def __init__(self) -> None:
        self._student: list[StudentRecord] = []

    def create_record(
        self,
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
    ) -> StudentRecord:
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")

        if any(record[0] == student_id for record in self._student):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._student.append(new_record)
        return new_record

    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:
        if all(
            param is None
            for param in [student_id, first_name, second_name, age, sex]
        ):
            return self._student.copy()

        result: list[StudentRecord] = []

        for record in self._student:
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1] != first_name:
                continue
            if second_name is not None and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and record[4] != sex:
                continue
            result.append(record)

        return result

    def sort_records(
        self,
        field: str,
        reverse: bool = False,
    ) -> list[StudentRecord]:
        field_index = {
            "student_id": 0,
            "first_name": 1,
            "second_name": 2,
            "age": 3,
            "sex": 4,
        }

        if field not in field_index:
            raise ValueError(f"Недопустимое поле для сортировки: {field}")

        index = field_index[field]
        return sorted(self._student, key=lambda x: x[index], reverse=reverse)