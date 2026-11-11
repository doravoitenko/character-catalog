import json


# Шар постійності: читає й записує каталог у JSON-файл.
# Працює зі списком словників і нічого не знає про класи логіки.
class CatalogStorage:

    def __init__(self, filename="catalog.json"):
        self.filename = filename

    def save(self, data_list):
        # Може кинути OSError, якщо файл не можна записати
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({"characters": data_list}, f, ensure_ascii=False, indent=4)

    def load(self):
        # Повертає список словників або None, якщо файлу ще немає.
        # Пошкоджений файл дає ValueError, недоступний - OSError.
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                content = json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            raise ValueError("файл не є коректним JSON")
        if not isinstance(content, dict) or not isinstance(content.get("characters"), list):
            raise ValueError("у файлі немає списку characters")
        return content["characters"]
