from .errors import InvalidAgeError, RecordNotFoundError

class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self._records = {}
        self._next_id = 1

    def create_record(self, data):
        for col in self.columns:
            if col not in data:
                raise ValueError(f"Отсутствует поле: {col}")
        if "age" in data and data["age"] < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        record_id = self._next_id
        data["id"] = record_id
        self._records[record_id] = data
        self._next_id += 1
        return record_id

    def select_record(self, record_id):
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с ID {record_id} не найдена")
        return self._records[record_id]

    def select_all(self):
        return list(self._records.values())

    def select_by_filter(self, field_name, value):
        if field_name not in self.columns and field_name != "id":
            raise ValueError(f"Поле '{field_name}' не найдено")
        result = []
        for record in self._records.values():
            if str(record.get(field_name)) == str(value):
                result.append(record)
        return result

    def update_record(self, record_id, new_data):
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с ID {record_id} не найдена")
        if "age" in new_data and new_data["age"] < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        for k, v in new_data.items():
            if k in self.columns or k == "id":
                self._records[record_id][k] = v
        return True

    def delete_record(self, record_id):
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с ID {record_id} не найдена")
        del self._records[record_id]
        return True

    def sort_records(self, field_name, ascending=True):
        if field_name not in self.columns and field_name != "id":
            raise ValueError(f"Поле '{field_name}' не найдено")
        records = list(self._records.values())
        records.sort(key=lambda x: x.get(field_name, ""), reverse=not ascending)
        return records

    def to_dict(self):
        return {
            "name": self.name,
            "columns": self.columns,
            "next_id": self._next_id,
            "records": self._records
        }

    @classmethod
    def from_dict(cls, data):
        table = cls(data["name"], data["columns"])
        table._records = data["records"]
        table._next_id = data["next_id"]
        return table