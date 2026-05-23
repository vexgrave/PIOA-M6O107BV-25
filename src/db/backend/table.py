from .errors import MissingFieldError, FieldNotFoundError


class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.rows = []
        self.next_id = 1
        self.indexes = {}

    def add(self, data):
        for col in self.columns:
            if col not in data:
                raise MissingFieldError(f"Отсутствует поле: {col}")
        data["id"] = self.next_id
        self.rows.append(data)
        self._update_indexes(data, "add")
        self.next_id += 1
        return data["id"]

    def read(self, filters=None):
        if filters is None:
            return self.rows[:]
        
        if filters and self.indexes:
            for key, value in filters.items():
                if key in self.indexes:
                    index = self.indexes[key]
                    if str(value) in index:
                        return [self.rows[i] for i in index[str(value)]]
        
        result = []
        for row in self.rows:
            match = True
            for key, value in filters.items():
                if key not in self.columns and key != "id":
                    raise FieldNotFoundError(f"Поле '{key}' не найдено в таблице")
                if str(row.get(key)) != str(value):
                    match = False
                    break
            if match:
                result.append(row)
        return result

    def update(self, row_id, new_data):
        for row in self.rows:
            if row["id"] == row_id:
                old_data = row.copy()
                for k, v in new_data.items():
                    if k in self.columns:
                        row[k] = v
                self._update_indexes_after_update(old_data, row)
                return True
        return False

    def delete(self, row_id):
        for i, row in enumerate(self.rows):
            if row["id"] == row_id:
                self._update_indexes(row, "delete")
                self.rows.pop(i)
                return True
        return False

    def sort(self, field, reverse=False):
        if field not in self.columns and field != "id":
            raise FieldNotFoundError(f"Поле '{field}' не найдено в таблице")
        self.rows = sorted(
            self.rows,
            key=lambda row: row.get(field, ""),
            reverse=reverse
        )
        return self.rows[:]

    def create_index(self, field):
        if field not in self.columns:
            raise FieldNotFoundError(f"Поле '{field}' не найдено в таблице")
        
        self.indexes[field] = {}
        for i, row in enumerate(self.rows):
            value = str(row.get(field, ""))
            if value not in self.indexes[field]:
                self.indexes[field][value] = []
            self.indexes[field][value].append(i)

    def drop_index(self, field):
        if field in self.indexes:
            del self.indexes[field]

    def _update_indexes(self, data, operation):
        for field, index in self.indexes.items():
            if field in data:
                value = str(data[field])
                if operation == "add":
                    if value not in index:
                        index[value] = []
                    index[value].append(len(self.rows) - 1)
                elif operation == "delete":
                    if value in index:
                        idx_to_remove = None
                        for i, row_idx in enumerate(index[value]):
                            if self.rows[row_idx]["id"] == data["id"]:
                                idx_to_remove = i
                                break
                        if idx_to_remove is not None:
                            index[value].pop(idx_to_remove)
                        if not index[value]:
                            del index[value]

    def _update_indexes_after_update(self, old_data, new_data):
        for field in self.indexes:
            if field in old_data and field in new_data:
                old_value = str(old_data[field])
                new_value = str(new_data[field])
                
                if old_value != new_value:
                    if old_value in self.indexes[field]:
                        for i, row_idx in enumerate(self.indexes[field][old_value]):
                            if self.rows[row_idx]["id"] == new_data["id"]:
                                self.indexes[field][old_value].pop(i)
                                break
                        if not self.indexes[field][old_value]:
                            del self.indexes[field][old_value]
                    
                    if new_value not in self.indexes[field]:
                        self.indexes[field][new_value] = []
                    self.indexes[field][new_value].append(
                        next(i for i, row in enumerate(self.rows) if row["id"] == new_data["id"])
                    )

    def to_dict(self):
        return {
            "name": self.name,
            "columns": self.columns,
            "rows": self.rows,
            "next_id": self.next_id,
            "indexes": self.indexes
        }

    @classmethod
    def from_dict(cls, data):
        table = cls(data["name"], data["columns"])
        table.rows = data["rows"]
        table.next_id = data["next_id"]
        table.indexes = data.get("indexes", {})
        return table