class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.rows = []
        self.next_id = 1

    def add(self, data):
        for col in self.columns:
            if col not in data:
                raise ValueError(f"Отсутствует поле: {col}")
        data["id"] = self.next_id
        self.rows.append(data)
        self.next_id += 1
        return data["id"]

    def read(self, filters=None):
        if not filters:
            return self.rows
        result = []
        for row in self.rows:
            match = True
            for key, value in filters.items():
                if key not in self.columns and key != "id":
                    raise ValueError(f"Поле '{key}' не найдено в таблице")
                if str(row.get(key)) != str(value):
                    match = False
                    break
            if match:
                result.append(row)
        return result

    def update(self, row_id, new_data):
        for row in self.rows:
            if row["id"] == row_id:
                for k, v in new_data.items():
                    if k in self.columns:
                        row[k] = v
                return True
        return False

    def delete(self, row_id):
        for i, row in enumerate(self.rows):
            if row["id"] == row_id:
                self.rows.pop(i)
                return True
        return False


class InMemoryDB:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns):
        if name in self.tables:
            raise ValueError(f"Таблица '{name}' уже существует")
        self.tables[name] = Table(name, columns)

    def get_table(self, name):
        if name not in self.tables:
            raise KeyError(f"Таблица '{name}' не найдена")
        return self.tables[name]

    def list_tables(self):
        return list(self.tables.keys())

