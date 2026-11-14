from dataclasses import asdict, dataclass

# Поля картки персонажа в тому порядку, у якому їх показує каталог
FIELDS = ("name", "title", "vision", "weapon", "nation", "image_url")


def name_key(name):
    # Ключ для порівняння імен: без урахування регістру й зайвих пробілів
    return " ".join(name.split()).casefold()


# Картка одного персонажа каталогу (модель шару бізнес-логіки).
# Усі перевірки даних зібрані саме тут, тому створити некоректну картку неможливо.
@dataclass
class CharacterProfile:
    name: str
    title: str = ""
    vision: str = ""
    weapon: str = ""
    nation: str = ""
    image_url: str = ""

    def __post_init__(self):
        # Прибираємо зайві пробіли (в імені ще й подвійні всередині)
        self.name = " ".join(self.name.split())
        self.title = self.title.strip()
        self.vision = self.vision.strip()
        self.weapon = self.weapon.strip()
        self.nation = self.nation.strip()
        self.image_url = self.image_url.strip()
        if not self.name:
            raise ValueError("ім'я не може бути порожнім")
        if self.image_url and not self.image_url.startswith(("http://", "https://")):
            raise ValueError("посилання має починатися з http:// або https://")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        # Може кинути ValueError, якщо запис пошкоджений
        if not isinstance(data, dict) or "name" not in data:
            raise ValueError("некоректний запис персонажа")
        values = {}
        for field in FIELDS:
            value = data.get(field)
            values[field] = "" if value is None else str(value)
        return cls(**values)
