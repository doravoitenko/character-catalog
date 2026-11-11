# Команди меню.
#
# Тут реалізовано два патерни:
#
# 1. COMMAND (Команда) - кожен пункт меню є окремим об'єктом з методом execute().
#        Command         - абстрактний клас Command
#        ConcreteCommand - CreateCharacterCommand, SaveStateCommand, ...
#        Receiver        - менеджери (CharacterManager, DocumentManager), сховище,
#                          веб-клієнт: вони знають, ЯК виконати дію
#        Invoker         - CommandHandler (cli/commands.py): зберігає команди й
#                          викликає їх за номером пункту меню
#        Раніше CommandHandler був одним довгим if/elif. Тепер новий пункт меню
#        це новий клас + один рядок у реєстрі, а існуючий код не змінюється
#        (принцип open-closed).
#
# 2. TEMPLATE METHOD (Шаблонний метод) - WebCharacterCommand. Команди "завантажити
#        персонажа" і "екіпірувати зброю" мали однаковий алгоритм (ввести id ->
#        завантажити -> обробити помилку -> створити персонажа -> додати -> показати)
#        і відрізнялись лише деталями. Загальний алгоритм тепер записаний один раз.

from abc import ABC, abstractmethod

from core.converter import character_from_api
from core.presentation import build_presentation
from core.snapshot import GameSnapshot
from core.weapons import weapon_from_api


def _normalize_id(raw):
    # id з API: без пробілів і малими літерами.
    return raw.strip().lower()


# --- COMMAND: базовий інтерфейс ---

class Command(ABC):
    # Інтерфейс команди меню.

    # Чи завершує команда роботу програми (потрібно лише для "Вихід").
    stops_app = False

    @abstractmethod
    def execute(self):
        # Виконує дію команди.
        pass


# --- COMMAND: прості команди ---

class CreateCharacterCommand(Command):
    def __init__(self, char_mgr, presenter):
        self.char_mgr = char_mgr
        self.presenter = presenter

    def execute(self):
        name = self.presenter.get_input("Введіть ім'я персонажа: ")
        self.char_mgr.create_character(name)


class AddParagraphCommand(Command):
    def __init__(self, doc_mgr, presenter):
        self.doc_mgr = doc_mgr
        self.presenter = presenter

    def execute(self):
        text = self.presenter.get_input("Введіть текст параграфа: ")
        self.doc_mgr.add_paragraph(text)


class ShowCharactersCommand(Command):
    def __init__(self, char_mgr):
        self.char_mgr = char_mgr

    def execute(self):
        self.char_mgr.show_all_characters()


class ShowTextsCommand(Command):
    def __init__(self, doc_mgr):
        self.doc_mgr = doc_mgr

    def execute(self):
        self.doc_mgr.show_all_texts()


class SaveStateCommand(Command):
    # Зберігає стан гри (використовує Memento: GameSnapshot).

    def __init__(self, char_mgr, doc_mgr, storage):
        self.char_mgr = char_mgr
        self.doc_mgr = doc_mgr
        self.storage = storage

    def execute(self):
        snapshot = GameSnapshot(
            characters=self.char_mgr.get_all_data(),
            texts=self.doc_mgr.get_all_data(),
        )
        self.storage.save_data(snapshot.to_dict())


class LoadStateCommand(Command):
    # Відновлює стан гри зі знімка (Memento: GameSnapshot).

    def __init__(self, char_mgr, doc_mgr, storage, presenter):
        self.char_mgr = char_mgr
        self.doc_mgr = doc_mgr
        self.storage = storage
        self.presenter = presenter

    def execute(self):
        data = self.storage.load_data()
        if data:
            snapshot = GameSnapshot.from_dict(data)
            self.char_mgr.load_from_data(snapshot.characters)
            self.doc_mgr.load_from_data(snapshot.texts)
            self.presenter.displayer.display("[Успіх] Дані завантажено!")


class ShowApiListCommand(Command):
    # Показує список id з API (персонажів або зброї).
    #
    # getter - функція, яка отримує веб-клієнт і повертає список. Клієнт
    # передається в момент виконання, а не створення команди.

    def __init__(self, presenter, web_client, title, getter):
        self.presenter = presenter
        self.web_client = web_client
        self.title = title
        self.getter = getter

    def execute(self):
        try:
            names = self.getter(self.web_client)
        except Exception:
            self.presenter.displayer.display("[Помилка] Не вдалося отримати список!")
            return
        self.presenter.displayer.display(f"\n--- СПИСОК {self.title.upper()} З API ---")
        for idx, name in enumerate(names, 1):
            self.presenter.displayer.display(f"{idx}. {name}")


class ExitCommand(Command):
    stops_app = True

    def execute(self):
        pass  # нічого робити не треба, CommandHandler зупинить цикл


# --- TEMPLATE METHOD ---

class WebCharacterCommand(Command, ABC):
    # Шаблон алгоритму "завантажити персонажа з API та показати його".
    #
    # execute() - ШАБЛОННИЙ МЕТОД: задає незмінний порядок кроків.
    # read_input / fetch / build_character - ПРИМІТИВНІ ОПЕРАЦІЇ: підкласи
    # реалізують їх по-своєму. error_message теж задає підклас.

    error_message = ""

    def __init__(self, char_mgr, presenter, web_client):
        self.char_mgr = char_mgr
        self.presenter = presenter
        self.web_client = web_client

    def execute(self):
        user_input = self.read_input()                      # крок 1 (примітив)
        try:
            fetched = self.fetch(user_input)                # крок 2 (примітив)
        except Exception:
            self.presenter.displayer.display(self.error_message)
            return
        character, api_data = self.build_character(fetched)  # крок 3 (примітив)
        self.char_mgr.characters.append(character)          # крок 4 (спільний)
        self.presenter.displayer.display(                   # крок 5 (спільний)
            build_presentation(character, api_data)
        )

    @abstractmethod
    def read_input(self):
        # Запитує в користувача все потрібне (id).
        pass

    @abstractmethod
    def fetch(self, user_input):
        # Завантажує дані з API. Може кинути виняток.
        pass

    @abstractmethod
    def build_character(self, fetched):
        # Повертає пару (character, api_data) для показу представлення.
        pass


class LoadCharacterFromWebCommand(WebCharacterCommand):
    error_message = "[Помилка] Не вдалося завантажити персонажа!"

    def read_input(self):
        return self.presenter.get_input("Введіть id персонажа (напр. arlecchino): ")

    def fetch(self, char_id):
        return self.web_client.get_character(_normalize_id(char_id))

    def build_character(self, api_data):
        return character_from_api(api_data), api_data


class EquipWeaponFromWebCommand(WebCharacterCommand):
    error_message = "[Помилка] Не вдалося завантажити дані!"

    def read_input(self):
        char_id = self.presenter.get_input("Введіть id персонажа: ")
        weapon_id = self.presenter.get_input("Введіть id зброї: ")
        return char_id, weapon_id

    def fetch(self, user_input):
        char_id, weapon_id = user_input
        api_data = self.web_client.get_character(_normalize_id(char_id))
        weapon_data = self.web_client.get_weapon(_normalize_id(weapon_id))
        return api_data, weapon_data

    def build_character(self, fetched):
        api_data, weapon_data = fetched
        character = character_from_api(api_data)
        character.equip(weapon_from_api(weapon_data))
        return character, api_data
