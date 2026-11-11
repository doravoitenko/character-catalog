from abc import ABC, abstractmethod

from cli.graphic import CLIGraphic


# Патерн STRATEGY (Стратегія): спосіб, у який об'єкт перетворюється на текст.
# CLI не знає, як виглядає персонаж чи список: він просто просить рендерер.
# Новий вигляд (наприклад, JSON) - це новий клас, а CLI не змінюється.
class Renderer(ABC):

    @abstractmethod
    def render(self, obj):
        # Повертає текст для виведення в консоль
        pass


# Картка одного персонажа
class ProfileRenderer(Renderer):

    def render(self, profile):
        rows = [
            ("Ім'я", profile.name),
            ("Титул", profile.title or "—"),
            ("Стихія", profile.vision or "—"),
            ("Зброя", profile.weapon or "—"),
            ("Країна", profile.nation or "—"),
            ("Картинка", profile.image_url or "—"),
        ]
        return CLIGraphic.box(profile.name, rows)


# Таблиця зі списком усіх персонажів
class ProfileListRenderer(Renderer):

    def render(self, profiles):
        if not profiles:
            return "Каталог порожній."
        rows = [
            (str(number), p.name, p.vision or "—", p.weapon or "—", p.nation or "—")
            for number, p in enumerate(profiles, 1)
        ]
        return CLIGraphic.table(["№", "Ім'я", "Стихія", "Зброя", "Країна"], rows)


# Таблиця доступних команд (для help); приймає трійки (команда, використання, опис)
class CommandListRenderer(Renderer):

    def render(self, commands):
        return CLIGraphic.table(["Команда", "Використання", "Опис"], commands)
