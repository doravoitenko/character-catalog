# Патерн MEMENTO (Memento / Знімок стану).
#
# Ролі в проєкті:
#     Originator  - CharacterManager і DocumentManager. Тільки вони знають, як
#                   перетворити свій внутрішній стан на дані (get_all_data) і
#                   відновити його назад (load_from_data).
#     Memento     - GameSnapshot (цей клас). Незмінний "знімок" стану всієї гри.
#                   Команди нічого не знають про поля Character чи Paragraph,
#                   вони працюють лише зі знімком.
#     Caretaker   - DataStorage. Зберігає знімок (як словник у JSON) і віддає
#                   його назад, не заглядаючи всередину.
#
# Навіщо: раніше формат файлу збереження ("characters", "texts") був
# розмазаний усередині CommandHandler. Тепер він описаний в одному місці,
# і додати нову частину стану (наприклад, зброю) можна, змінивши лише цей клас.

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GameSnapshot:
    # Незмінний знімок стану гри.

    characters: list = field(default_factory=list)
    texts: list = field(default_factory=list)

    def to_dict(self):
        # Формат, у якому знімок зберігається у файл.
        return {"characters": self.characters, "texts": self.texts}

    @classmethod
    def from_dict(cls, data):
        # Відновлює знімок із даних файлу (відсутні розділи стають порожніми).
        return cls(data.get("characters", []), data.get("texts", []))
