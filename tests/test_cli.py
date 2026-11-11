import pytest
from unittest.mock import MagicMock

from cli.commands import CommandHandler
from cli.presenter import Presenter


# Підготовка (fixture) 
# Fixture - це функція, яка готує дані для тестів.

@pytest.fixture
def handler():
    char_mgr = MagicMock()   # фейковий менеджер персонажів
    doc_mgr = MagicMock()    # фейковий менеджер текстів
    storage = MagicMock()    # фейкове сховище
    presenter = MagicMock()  # фейковий презентер
    return CommandHandler(char_mgr, doc_mgr, storage, presenter)


# Тести CommandHandler

def test_create_character(handler):
    # Arrange: кажемо, що користувач "ввів" ім'я Аліса
    handler.presenter.get_input.return_value = "Аліса"

    # Act: виконуємо команду "1"
    result = handler.handle_command("1")

    # Assert: перевіряємо, що персонажа створили з правильним ім'ям
    handler.char_mgr.create_character.assert_called_once_with("Аліса")
    assert result is True


def test_add_paragraph(handler):
    handler.presenter.get_input.return_value = "Жили-були..."

    result = handler.handle_command("2")

    handler.doc_mgr.add_paragraph.assert_called_once_with("Жили-були...")
    assert result is True


def test_show_characters(handler):
    result = handler.handle_command("3")

    handler.char_mgr.show_all_characters.assert_called_once()
    assert result is True


def test_show_texts(handler):
    result = handler.handle_command("4")

    handler.doc_mgr.show_all_texts.assert_called_once()
    assert result is True


def test_save_data(handler):
    # Arrange: задаємо, що повертають менеджери
    handler.char_mgr.get_all_data.return_value = ["персонаж"]
    handler.doc_mgr.get_all_data.return_value = ["текст"]

    # Act
    handler.handle_command("5")

    # Assert: у сховище мав піти словник з обома списками
    handler.storage.save_data.assert_called_once_with(
        {"characters": ["персонаж"], "texts": ["текст"]}
    )


def test_load_data_success(handler):
    handler.storage.load_data.return_value = {
        "characters": ["персонаж"],
        "texts": ["текст"],
    }

    handler.handle_command("6")

    handler.char_mgr.load_from_data.assert_called_once_with(["персонаж"])
    handler.doc_mgr.load_from_data.assert_called_once_with(["текст"])
    handler.presenter.displayer.display.assert_called_once_with(
        "[Успіх] Дані завантажено!"
    )


def test_load_data_when_nothing_loaded(handler):
    # Якщо файл порожній/відсутній, load_data повертає None
    handler.storage.load_data.return_value = None

    handler.handle_command("6")

    # Нічого не мало завантажитись і повідомлення про успіх не мало з'явитись
    handler.char_mgr.load_from_data.assert_not_called()
    handler.doc_mgr.load_from_data.assert_not_called()
    handler.presenter.displayer.display.assert_not_called()


def test_exit_returns_false(handler):
    # "0" - вихід, тому handle_command має повернути False
    assert handler.handle_command("0") is False


def test_unknown_command(handler):
    result = handler.handle_command("99")

    handler.presenter.displayer.display.assert_called_once_with("Невідома команда!")
    assert result is True  # програма продовжує працювати


# Тести Presenter

def test_show_menu_prints_all_lines():
    # Arrange
    displayer = MagicMock()
    presenter = Presenter(displayer)

    # Act
    presenter.show_menu()

    # Assert: у меню 8 рядків, і серед них є пункт виходу
    assert displayer.display.call_count == 12
    displayer.display.assert_any_call("0. Вихід")


def test_get_input_returns_user_text(monkeypatch):
    # monkeypatch тимчасово підміняє input(), щоб тест не чекав клавіатуру
    monkeypatch.setattr("builtins.input", lambda prompt: "Привіт")
    presenter = Presenter(MagicMock())

    result = presenter.get_input("Введіть: ")

    assert result == "Привіт"