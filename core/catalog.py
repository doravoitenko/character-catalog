from dataclasses import dataclass

from core.profile import CharacterProfile, name_key

# За якими полями можна фільтрувати
FILTER_FIELDS = ("vision", "weapon", "nation")

# Способи сортування: назва -> функція ключа (патерн Strategy у найпростішому вигляді).
# Новий спосіб сортування - це один новий рядок у цьому словнику.
SORT_KEYS = {
    "name": lambda p: name_key(p.name),
    "vision": lambda p: (p.vision.casefold(), name_key(p.name)),
    "weapon": lambda p: (p.weapon.casefold(), name_key(p.name)),
    "nation": lambda p: (p.nation.casefold(), name_key(p.name)),
}


# Умови вибірки з каталогу. Порожнє поле означає "будь-яке значення".
@dataclass(frozen=True)
class CatalogFilter:
    text: str = ""       # шукаємо в імені, титулі, стихії, зброї та країні
    vision: str = ""
    weapon: str = ""
    nation: str = ""
    sort_by: str = "name"


def _matches(wanted, actual):
    wanted = wanted.strip()
    return not wanted or wanted.casefold() == actual.casefold()


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
        key = name_key(name)
        for profile in self._profiles:
            if name_key(profile.name) == key:
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

    def query(self, criteria=None):
        # Повертає персонажів, що відповідають умовам, у вказаному порядку.
        # Це єдина точка, через яку інтерфейс (консольний чи графічний)
        # просить "знайди й відсортуй", не знаючи, як це робиться.
        criteria = criteria or CatalogFilter()
        if criteria.sort_by not in SORT_KEYS:
            raise ValueError("сортувати можна за: " + ", ".join(SORT_KEYS))
        text = " ".join(criteria.text.split()).casefold()
        found = []
        for profile in self._profiles:
            if text and not any(text in value.casefold() for value in self._searchable(profile)):
                continue
            if not all(_matches(getattr(criteria, field), getattr(profile, field)) for field in FILTER_FIELDS):
                continue
            found.append(profile)
        return sorted(found, key=SORT_KEYS[criteria.sort_by])

    @staticmethod
    def _searchable(profile):
        # Поля, у яких шукає вільний текст
        return (profile.name, profile.title, profile.vision, profile.weapon, profile.nation)

    def values_of(self, field):
        # Які значення є в каталозі (наприклад, для випадного списку фільтра)
        if field not in FILTER_FIELDS:
            raise ValueError("доступні поля: " + ", ".join(FILTER_FIELDS))
        values = {getattr(p, field) for p in self._profiles if getattr(p, field)}
        return sorted(values, key=str.casefold)

    def merge(self, profiles):
        # Додає лише нових персонажів; тих, чиє ім'я вже є, не змінює.
        # Повертає пару (додані, пропущені).
        added, skipped = [], []
        for profile in profiles:
            if self.find(profile.name) is None:
                self._profiles.append(profile)
                added.append(profile)
            else:
                skipped.append(profile)
        if added:
            self.dirty = True
        return added, skipped

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
            if name_key(profile.name) in seen:
                raise ValueError(f"персонаж «{profile.name}» повторюється")
            seen.add(name_key(profile.name))
            profiles.append(profile)
        self._profiles = profiles
        self.dirty = False

    def mark_saved(self):
        self.dirty = False
