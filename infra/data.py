import json


class DataStorage:

    def __init__(self, filename="game_save.json"):
        self.filename = filename

    def save_data(self, data_dict):
        # Зберігає словник у файл JSON
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)
        print(f"[Успіх] Дані збережено у {self.filename}")

    def load_data(self):
        # Завантажує дані з файлу JSON
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("[Помилка] Файл збереження не знайдено!")
            return {}