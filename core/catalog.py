from core.profile import CharacterProfile


def _key(name):
    # Ключ для пошуку: без урахування регістру й зайвих пробілів
    return " ".join(name.split()).casefold()


def default_profiles():
    # Початкові персонажі (заглушки), поки віддалений сервер недоступний.
    # Посилання ведуть на сервіс із картинками; без нього вони не відкриються.
    base = "https://genshin.jmp.blue/characters"
    return [
        CharacterProfile("Amber", "Outrider", "Pyro", "Bow", "Mondstadt", f"{base}/amber/card"),
        CharacterProfile("Diluc", "Dark Side of Dawn", "Pyro", "Claymore", "Mondstadt", f"{base}/diluc/card"),
        CharacterProfile("Keqing", "Yuheng of the Liyue Qixing", "Electro", "Sword", "Liyue", f"{base}/keqing/card"),
        CharacterProfile("Arlecchino", "Dire Balemoon", "Pyro", "Polearm", "Snezhnaya", f"{base}/arlecchino/card"),
    ]


# Каталог персонажів: список карток, пошук і додавання.
# Нічого не знає ні про консоль, ні про файли (це шар бізнес-логіки).
class CharacterCatalog:

    def __init__(self, profiles=()):
        self._profiles = list(profiles)
        # Чи є зміни, яких ще немає у файлі
        self.dirty = False

    def __len__(self):
        return len(self._profiles)

    def all(self):
        return list(self._profiles)

    def find(self, name):
        key = _key(name)
        for profile in self._profiles:
            if _key(profile.name) == key:
                return profile
        return None

    def get_by_number(self, number):
        # Нумерація з 1, як у таблиці на екрані
        if 1 <= number <= len(self._profiles):
            return self._profiles[number - 1]
        return None

    def add(self, profile):
        if self.find(profile.name) is not None:
            raise ValueError(f"персонаж «{profile.name}» уже є в каталозі")
        self._profiles.append(profile)
        self.dirty = True

    # Ті самі назви методів, що й у CharacterManager з першого модуля
    def get_all_data(self):
        return [profile.to_dict() for profile in self._profiles]

    def load_from_data(self, data_list):
        # Спершу збираємо новий список і лише потім підміняємо старий,
        # тому при помилці каталог лишається таким, яким був
        profiles = []
        seen = set()
        for item in data_list:
            profile = CharacterProfile.from_dict(item)
            if _key(profile.name) in seen:
                raise ValueError(f"персонаж «{profile.name}» повторюється")
            seen.add(_key(profile.name))
            profiles.append(profile)
        self._profiles = profiles
        self.dirty = False

    def mark_saved(self):
        self.dirty = False
