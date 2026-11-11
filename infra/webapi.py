import json
import urllib.request


class WebApiClient:
    # Клієнт, який бере дані персонажів з інтернету.

    def __init__(self, base_url="https://genshin.jmp.blue"):
        self.base_url = base_url

    def get_json(self, path):
        # Робить запит і повертає відповідь як словник/список Python.
        url = f"{self.base_url}/{path}"
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_character_names(self):
        # Повертає список імен персонажів.
        return self.get_json("characters")

    def get_character(self, name):
        # Повертає дані одного персонажа.
        return self.get_json(f"characters/{name}")
    def get_weapon(self, weapon_id):
        # Повертає дані однієї зброї.
        return self.get_json(f"weapons/{weapon_id}")
    def get_weapon_names(self):
        # Повертає список id зброї.
        return self.get_json("weapons")