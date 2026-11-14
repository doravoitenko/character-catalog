from cli.menu_commands import Command
from cli.renderers import CommandListRenderer, ProfileListRenderer, ProfileRenderer
from core.api_parser import CharacterApiParser
from core.catalog import FILTER_FIELDS, CatalogFilter
from core.profile import CharacterProfile
from infra.json_source import JsonFileSource

YES = ("y", "yes", "т", "так")
NO = ("n", "no", "н", "ні")


# Патерн COMMAND. Базовий інтерфейс Command (метод execute) узято з
# cli/menu_commands.py, тобто з попередніх практичних. Кожна команда каталогу -
# окремий клас, який отримує все потрібне в конструкторі.
class CatalogCommand(Command):

    # Рядки для help
    usage = ""
    description = ""

    def __init__(self, cli, catalog, storage, args):
        self.cli = cli
        self.catalog = catalog
        self.storage = storage
        self.args = args

    def save_catalog(self):
        # Спільна дія для save і exit. Повертає True, якщо збережено.
        try:
            self.storage.save(self.catalog.get_all_data())
        except OSError as error:
            self.cli.error(f"Не вдалося зберегти: {error.strerror or error}")
            return False
        self.catalog.mark_saved()
        return True


class ListCommand(CatalogCommand):
    usage = "list"
    description = "показати всіх персонажів"

    def execute(self):
        self.cli.display(self.catalog.all(), ProfileListRenderer())


class UpdateCommand(CatalogCommand):
    usage = "update"
    description = "перечитати каталог із файлу й показати список"

    def execute(self):
        if self.catalog.dirty:
            answer = self.cli.ask("Незбережені зміни буде втрачено. Продовжити? (y/n): ")
            if answer.strip().lower() not in YES:
                self.cli.show("Оновлення скасовано.")
                return
        try:
            data = self.storage.load()
            if data is None:
                self.cli.error("Файл каталогу не знайдено, список не змінено.")
                return
            self.catalog.load_from_data(data)
        except (OSError, ValueError) as error:
            self.cli.error(f"Не вдалося оновити каталог: {error}")
            return
        self.cli.success(f"Каталог оновлено, персонажів: {len(self.catalog)}.")
        self.cli.display(self.catalog.all(), ProfileListRenderer())


class ShowCommand(CatalogCommand):
    usage = "show <ім'я або №>"
    description = "показати картку персонажа з посиланням на картинку"

    def execute(self):
        query = self.args.rest
        if not query:
            self.cli.error("Вкажіть ім'я або номер: show <ім'я або №>")
            return
        if query.isdigit():
            profile = self.catalog.get_by_number(int(query))
        else:
            profile = self.catalog.find(query)
        if profile is None:
            self.cli.error(f"Персонажа «{query}» не знайдено. Введіть list.")
            return
        self.cli.display(profile, ProfileRenderer())


class SearchCommand(CatalogCommand):
    usage = "search <текст> [vision=..] [weapon=..] [nation=..] [sort=..]"
    description = "пошук за будь-яким полем, фільтри й сортування"

    def execute(self):
        words, criteria = [], {}
        for word in self.args.rest.split():
            key, separator, value = word.partition("=")
            if separator:
                criteria[key.lower()] = value
            else:
                words.append(word)
        if not words and not criteria:
            self.cli.error("Вкажіть текст або умови: search amber, search vision=pyro sort=nation")
            return
        unknown = [key for key in criteria if key not in (*FILTER_FIELDS, "sort")]
        if unknown:
            self.cli.error(f"Невідома умова: {unknown[0]}. Доступні: {', '.join(FILTER_FIELDS)}, sort")
            return
        try:
            found = self.catalog.query(CatalogFilter(
                text=" ".join(words),
                vision=criteria.get("vision", ""),
                weapon=criteria.get("weapon", ""),
                nation=criteria.get("nation", ""),
                sort_by=criteria.get("sort", "name"),
            ))
        except ValueError as error:
            self.cli.error(str(error))
            return
        if not found:
            self.cli.show("Нічого не знайдено.")
            return
        self.cli.show(f"Знайдено: {len(found)}")
        self.cli.display(found, ProfileListRenderer(numbered=False))


class ImportCommand(CatalogCommand):
    usage = "import <файл>"
    description = "додати персонажів із JSON-файлу у форматі API"

    # Скільки помилок показувати, щоб не засмітити екран
    MAX_ERRORS_SHOWN = 5

    def __init__(self, cli, catalog, storage, args):
        super().__init__(cli, catalog, storage, args)
        self.source = JsonFileSource()
        self.parser = CharacterApiParser()

    def execute(self):
        path = self.args.rest
        if not path:
            self.cli.error("Вкажіть файл: import <файл>")
            return
        try:
            result = self.parser.parse(self.source.read(path))
        except FileNotFoundError:
            self.cli.error(f"Файл не знайдено: {path}")
            return
        except (OSError, ValueError) as error:
            self.cli.error(f"Не вдалося імпортувати: {getattr(error, 'strerror', None) or error}")
            return
        added, skipped = self.catalog.merge(result.profiles)
        self.cli.success(
            f"Додано: {len(added)}, уже були в каталозі: {len(skipped)}, "
            f"з помилками: {len(result.errors)}."
        )
        for message in result.errors[:self.MAX_ERRORS_SHOWN]:
            self.cli.show(f"  - {message}")
        if added:
            self.cli.display(added, ProfileListRenderer(numbered=False))
            self.cli.show("Щоб запам'ятати, введіть save.")


class CreateCommand(CatalogCommand):
    usage = "create"
    description = "створити персонажа через діалог"

    # Питання діалогу після імені: (поле, текст запитання)
    QUESTIONS = (
        ("title", "Титул: "),
        ("vision", "Стихія: "),
        ("weapon", "Зброя: "),
        ("nation", "Країна: "),
        ("image_url", "Посилання на картинку (можна пропустити): "),
    )

    def execute(self):
        name = self.cli.ask("Ім'я: ")
        if not name.strip():
            self.cli.error("Не вдалося створити персонажа: ім'я не може бути порожнім")
            return
        if self.catalog.find(name) is not None:
            self.cli.error(f"Персонаж «{name.strip()}» уже є в каталозі.")
            return
        values = {"name": name}
        for field, question in self.QUESTIONS:
            values[field] = self.cli.ask(question)
        try:
            profile = CharacterProfile(**values)
            self.catalog.add(profile)
        except ValueError as error:
            self.cli.error(f"Не вдалося створити персонажа: {error}")
            return
        self.cli.success(f"Персонажа «{profile.name}» створено. Щоб запам'ятати, введіть save.")
        self.cli.display(profile, ProfileRenderer())


class SaveCommand(CatalogCommand):
    usage = "save"
    description = "зберегти каталог у файл"

    def execute(self):
        if self.save_catalog():
            self.cli.success(f"Збережено персонажів: {len(self.catalog)} ({self.storage.filename}).")


class HelpCommand(CatalogCommand):
    usage = "help"
    description = "показати список команд"

    def execute(self):
        self.cli.display(self.cli.strategy.describe(), CommandListRenderer())


class ExitCommand(CatalogCommand):
    usage = "exit"
    description = "вийти (запропонує зберегти зміни)"

    def execute(self):
        if self.catalog.dirty:
            answer = self.cli.ask("Є незбережені зміни. Зберегти? (y - так, n - ні, інше - лишитись): ")
            answer = answer.strip().lower()
            if answer in YES:
                if not self.save_catalog():
                    return  # не вийшло зберегти, тому не виходимо
            elif answer not in NO:
                self.cli.show("Вихід скасовано.")
                return
        self.cli.show("До побачення!")
        self.cli.stop()
