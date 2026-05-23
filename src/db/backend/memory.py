from .errors import InvalidAgeError, DuplicateIDError


class StudentTable:
    def __init__(self):
        self._records = {}
        self._next_id = 1

    def create_record(self, first_name, second_name, age, sex):
        if age < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        
        record_id = self._next_id
        record = (record_id, first_name, second_name, age, sex)
        self._records[record_id] = record
        self._next_id += 1
        return record_id

    def select_record(self, record_id):
        if record_id not in self._records:
            raise KeyError(f"Запись с ID {record_id} не найдена")
        return self._records[record_id]

    def select_all(self):
        return list(self._records.values())

    def select_by_filter(self, field_name, value):
        fields = ["id", "first_name", "second_name", "age", "sex"]
        if field_name not in fields:
            raise ValueError(f"Поле '{field_name}' не найдено")
        
        field_index = fields.index(field_name)
        result = []
        for record in self._records.values():
            if str(record[field_index]) == str(value):
                result.append(record)
        return result

    def update_record(self, record_id, first_name=None, second_name=None, age=None, sex=None):
        if record_id not in self._records:
            raise KeyError(f"Запись с ID {record_id} не найдена")
        
        old_record = self._records[record_id]
        new_record = (
            record_id,
            first_name if first_name is not None else old_record[1],
            second_name if second_name is not None else old_record[2],
            age if age is not None else old_record[3],
            sex if sex is not None else old_record[4]
        )
        
        if new_record[3] < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        
        self._records[record_id] = new_record
        return True

    def delete_record(self, record_id):
        if record_id not in self._records:
            raise KeyError(f"Запись с ID {record_id} не найдена")
        del self._records[record_id]
        return True

    def sort_records(self, field_name, ascending=True):
        fields = ["id", "first_name", "second_name", "age", "sex"]
        if field_name not in fields:
            raise ValueError(f"Поле '{field_name}' не найдено")
        
        field_index = fields.index(field_name)
        records = list(self._records.values())
        records.sort(key=lambda x: x[field_index], reverse=not ascending)
        return records