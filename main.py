from cli.commands import CommandHandler
from cli.presenter import Presenter
from core.characters import CharacterManager
from core.text import DocumentManager
from infra.data import DataStorage
from infra.display import ConsoleDisplayer
from infra.webapi import WebApiClient


def main():
    # 1. Ініціалізуємо шар Infra
    displayer = ConsoleDisplayer()
    storage = DataStorage()

    # 2. Ініціалізуємо шар Core (передаємо displayer)
    char_mgr = CharacterManager(displayer)
    doc_mgr = DocumentManager(displayer)

    # 3. Ініціалізуємо шар CLI
    presenter = Presenter(displayer)
    web_client = WebApiClient()
    cmd_handler = CommandHandler(char_mgr, doc_mgr, storage, presenter, web_client)

    # 4. Головний цикл програми
    running = True
    while running:
        presenter.show_menu()
        choice = presenter.get_input("Оберіть дію: ")
        running = cmd_handler.handle_command(choice)


if __name__ == "__main__":
    main()
