import json
import re
from dataclasses import dataclass, field

from core.profile import CharacterProfile, name_key


# Помилка розбору відповіді сервера. Нащадок ValueError, тому її легко ловити разом
# з іншими помилками даних.
class ParseError(ValueError):
    pass


# Результат розбору списку: що вдалося прочитати й що саме пішло не так.
# Одна зіпсована картка не псує решту, тому помилки збираються, а не кидаються.
@dataclass(frozen=True)
class ParseResult:
    profiles: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def slugify(name):
    # "Hu Tao" -> "hu-tao": так виглядає id персонажа в адресах API
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# Перетворює JSON, який віддає API, на картки персонажів (CharacterProfile).
# Це патерн MAPPER (адаптер між зовнішнім форматом і моделлю програми):
# уся обізнаність про формат сервера зібрана тут, а решта програми працює
# лише з CharacterProfile. Якщо формат зміниться, правити треба тільки цей клас.
#
# Парсер нічого не знає ні про мережу, ні про файли: він отримує вже готовий текст
# або дані. Звідки вони прийшли (сервер, файл, тест), йому байдуже.
class CharacterApiParser:

    def __init__(self, image_base="https://genshin.jmp.blue/characters"):
        self.image_base = image_base

    def parse_text(self, text):
        # Розбирає текст відповіді сервера
        try:
            data = json.loads(text)
        except ValueError:
            raise ParseError("некоректний JSON")
        return self.parse(data)

    def parse(self, data):
        # Приймає один об'єкт або список об'єктів (уже розібраний JSON)
        if isinstance(data, dict):
            items = [data]
        elif isinstance(data, list):
            items = data
        else:
            raise ParseError("очікувався об'єкт або список об'єктів")
        profiles, errors, seen = [], [], set()
        for number, item in enumerate(items, 1):
            try:
                profile = self.parse_character(item)
            except ValueError as error:
                errors.append(f"елемент {number}: {error}")
                continue
            key = name_key(profile.name)
            if key in seen:
                errors.append(f"елемент {number}: «{profile.name}» повторюється")
                continue
            seen.add(key)
            profiles.append(profile)
        return ParseResult(profiles, errors)

    def parse_character(self, data):
        # Один об'єкт -> одна картка. Обов'язкове лише ім'я, решта необов'язкова,
        # зайві поля сервера просто ігноруються.
        if not isinstance(data, dict):
            raise ParseError("очікувався об'єкт JSON")
        name = self._text(data.get("name"))
        if not name:
            raise ParseError("немає поля name")
        slug = slugify(name)
        return CharacterProfile(
            name=name,
            title=self._text(data.get("title")),
            vision=self._text(data.get("vision")),
            weapon=self._text(data.get("weapon")),
            nation=self._text(data.get("nation")),
            # API не віддає посилання на картинку, але будує його за id персонажа
            image_url=f"{self.image_base}/{slug}/card" if slug else "",
        )

    @staticmethod
    def _text(value):
        # Приймаємо рядки й числа; null, списки, словники та булеві значення дають ""
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            return str(value).strip()
        return ""
