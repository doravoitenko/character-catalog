import json


# Шар постійності: читає JSON-файл і повертає розібрані дані.
# Нічого не знає про персонажів: що з цими даними робити, вирішує ядро.
class JsonFileSource:

    def read(self, path):
        # Може кинути OSError (немає файлу, немає доступу) або ValueError (не JSON)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("файл не є коректним JSON")
        except UnicodeDecodeError:
            raise ValueError("файл має бути в кодуванні UTF-8")
