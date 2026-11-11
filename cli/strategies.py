from abc import ABC, abstractmethod

from cli.catalog_commands import (
    CreateCommand,
    ExitCommand,
    HelpCommand,
    ListCommand,
    SaveCommand,
    ShowCommand,
    UpdateCommand,
)


# Патерн STRATEGY: набір команд, який підключається до CLI (cli.use_strategy).
# Базовий клас реєструє команди й виконує їх за назвою, а як саме створити
# команду (які їй потрібні залежності), вирішує конкретний набір.
# Це водночас TEMPLATE METHOD: exec_command має фіксований порядок кроків,
# а create_command реалізують нащадки.
class CommandStrategy(ABC):

    def __init__(self):
        self._commands = {}

    def register_command(self, name, command_class):
        self._commands[name] = command_class

    def get_command_selectors(self):
        # Назви всіх зареєстрованих команд
        return list(self._commands)

    def describe(self):
        # Трійки (назва, використання, опис) для help
        return [(name, cls.usage, cls.description) for name, cls in self._commands.items()]

    def exec_command(self, cli, args):
        # Повертає False, якщо такої команди немає
        command_class = self._commands.get(args.command)
        if command_class is None:
            return False
        self.create_command(command_class, cli, args).execute()
        return True

    @abstractmethod
    def create_command(self, command_class, cli, args):
        # Створює об'єкт команди з усім, що їй потрібно
        pass


# Команди каталогу персонажів
class CatalogStrategy(CommandStrategy):

    def __init__(self, catalog, storage):
        super().__init__()
        self.catalog = catalog
        self.storage = storage
        self.register_command("list", ListCommand)
        self.register_command("show", ShowCommand)
        self.register_command("create", CreateCommand)
        self.register_command("update", UpdateCommand)
        self.register_command("save", SaveCommand)
        self.register_command("help", HelpCommand)
        self.register_command("exit", ExitCommand)

    def create_command(self, command_class, cli, args):
        return command_class(cli, self.catalog, self.storage, args)
