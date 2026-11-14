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


# Таблиця зі списком персонажів. Номери показуємо лише для повного списку:
# для результатів пошуку вони були б оманливими (show працює з номерами каталогу).
class ProfileListRenderer(Renderer):

    def __init__(self, numbered=True):
        self.numbered = numbered

    def render(self, profiles):
        if not profiles:
            return "Каталог порожній."
        headers = ["Ім'я", "Стихія", "Зброя", "Країна"]
        rows = [(p.name, p.vision or "—", p.weapon or "—", p.nation or "—") for p in profiles]
        if self.numbered:
            headers.insert(0, "№")
            rows = [(str(number), *row) for number, row in enumerate(rows, 1)]
        return CLIGraphic.table(headers, rows)


# Таблиця доступних команд (для help); приймає трійки (команда, використання, опис)
class CommandListRenderer(Renderer):

    def render(self, commands):
        return CLIGraphic.table(["Команда", "Використання", "Опис"], commands)
