from cli.menu_commands import (
    AddParagraphCommand,
    CreateCharacterCommand,
    EquipWeaponFromWebCommand,
    ExitCommand,
    LoadCharacterFromWebCommand,
    LoadStateCommand,
    SaveStateCommand,
    ShowApiListCommand,
    ShowCharactersCommand,
    ShowTextsCommand,
)


class CommandHandler:
    # INVOKER з патерну Command.
    #
    # Не знає, що саме робить кожна команда: лише шукає її за номером пункту
    # меню в реєстрі й викликає execute().

    def __init__(self, char_manager, doc_manager, storage, presenter, web_client=None):
        self.char_mgr = char_manager
        self.doc_mgr = doc_manager
        self.storage = storage
        self.presenter = presenter
        self.web_client = web_client
        self._commands = self._build_registry()

    def _build_registry(self):
        # Реєстр "номер пункту меню -> команда".
        return {
            "1": CreateCharacterCommand(self.char_mgr, self.presenter),
            "2": AddParagraphCommand(self.doc_mgr, self.presenter),
            "3": ShowCharactersCommand(self.char_mgr),
            "4": ShowTextsCommand(self.doc_mgr),
            "5": SaveStateCommand(self.char_mgr, self.doc_mgr, self.storage),
            "6": LoadStateCommand(
                self.char_mgr, self.doc_mgr, self.storage, self.presenter
            ),
            "7": LoadCharacterFromWebCommand(
                self.char_mgr, self.presenter, self.web_client
            ),
            "8": ShowApiListCommand(
                self.presenter, self.web_client, "персонажів",
                lambda client: client.get_character_names(),
            ),
            "9": ShowApiListCommand(
                self.presenter, self.web_client, "зброї",
                lambda client: client.get_weapon_names(),
            ),
            "10": EquipWeaponFromWebCommand(
                self.char_mgr, self.presenter, self.web_client
            ),
            "0": ExitCommand(),
        }

    def handle_command(self, choice):
        # Виконує команду. Повертає False, якщо програму треба завершити.
        command = self._commands.get(choice)
        if command is None:
            self.presenter.displayer.display("Невідома команда!")
            return True
        command.execute()
        return not command.stops_app
