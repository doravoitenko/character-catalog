import pytest
from unittest.mock import MagicMock

from core.characters import Character, CharacterManager
from core.text import Paragraph, DocumentManager


# Fixtures (підготовка для тестів) 

@pytest.fixture
def char_manager():
    displayer = MagicMock()
    return CharacterManager(displayer)


@pytest.fixture
def doc_manager():
    displayer = MagicMock()
    return DocumentManager(displayer)


# Тести Character 

def test_character_to_dict():
    # Arrange
    char = Character("Аліса", 80, 10)

    # Act
    result = char.to_dict()

    # Assert: словник має містити всі три поля
    assert result == {"name": "Аліса", "hp": 80, "power": 10}


# Тести CharacterManager 

def test_create_character_default_values(char_manager):
    # Act: створюємо персонажа тільки з ім'ям
    char_manager.create_character("Аліса")

    # Assert: має бути 1 персонаж зі стандартними hp=100 і power=25
    assert len(char_manager.characters) == 1
    assert char_manager.characters[0].name == "Аліса"
    assert char_manager.characters[0].hp == 100
    assert char_manager.characters[0].power == 25


def test_create_character_custom_values(char_manager):
    char_manager.create_character("Боб", hp=50, power=5)

    assert char_manager.characters[0].hp == 50
    assert char_manager.characters[0].power == 5


def test_create_character_shows_message(char_manager):
    char_manager.create_character("Аліса")

    char_manager.displayer.display.assert_called_once_with(
        "Створено персонажа: Аліса (HP: 100)"
    )


def test_show_all_characters_empty(char_manager):
    char_manager.show_all_characters()

    char_manager.displayer.display.assert_called_once_with(
        "Список персонажів порожній!"
    )


def test_show_all_characters_with_data(char_manager):
    # Arrange: створюємо двох персонажів
    char_manager.create_character("Аліса")
    char_manager.create_character("Боб", hp=50, power=5)
    char_manager.displayer.reset_mock()  # очищаємо історію викликів

    # Act
    char_manager.show_all_characters()

    # Assert: заголовок + 2 рядки = 3 виклики
    assert char_manager.displayer.display.call_count == 3
    char_manager.displayer.display.assert_any_call("1. Аліса (HP: 100, Power: 25)")
    char_manager.displayer.display.assert_any_call("2. Боб (HP: 50, Power: 5)")


def test_get_all_data(char_manager):
    char_manager.create_character("Аліса")

    result = char_manager.get_all_data()

    assert result == [{"name": "Аліса", "hp": 100, "power": 25}]


def test_get_all_data_empty(char_manager):
    assert char_manager.get_all_data() == []


def test_load_from_data(char_manager):
    data = [
        {"name": "Аліса", "hp": 100, "power": 25},
        {"name": "Боб", "hp": 50, "power": 5},
    ]

    char_manager.load_from_data(data)

    assert len(char_manager.characters) == 2
    assert char_manager.characters[1].name == "Боб"
    assert char_manager.characters[1].hp == 50


def test_load_from_data_replaces_old_characters(char_manager):
    # Arrange: спочатку вже є один персонаж
    char_manager.create_character("Старий")

    # Act: завантажуємо інші дані
    char_manager.load_from_data([{"name": "Новий", "hp": 1, "power": 1}])

    # Assert: старий персонаж зник, залишився тільки новий
    assert len(char_manager.characters) == 1
    assert char_manager.characters[0].name == "Новий"


def test_characters_save_and_load_roundtrip(char_manager):
    # Перевіряємо, що "зберегти -> завантажити" нічого не губить
    char_manager.create_character("Аліса", hp=70, power=12)
    saved = char_manager.get_all_data()

    other_manager = CharacterManager(MagicMock())
    other_manager.load_from_data(saved)

    assert other_manager.get_all_data() == saved


# Тести Paragraph 

def test_paragraph_render():
    p = Paragraph("Привіт")

    assert p.render() == "Параграф: Привіт"


#  Тести DocumentManager 

def test_add_paragraph(doc_manager):
    doc_manager.add_paragraph("Жили-були...")

    assert len(doc_manager.paragraphs) == 1
    assert doc_manager.paragraphs[0].content == "Жили-були..."
    doc_manager.displayer.display.assert_called_once_with(
        "Додано параграф: 'Жили-були...'"
    )


def test_show_all_texts_empty(doc_manager):
    doc_manager.show_all_texts()

    doc_manager.displayer.display.assert_called_once_with(
        "Список параграфів порожній!"
    )


def test_show_all_texts_with_data(doc_manager):
    doc_manager.add_paragraph("Перший")
    doc_manager.add_paragraph("Другий")
    doc_manager.displayer.reset_mock()

    doc_manager.show_all_texts()

    assert doc_manager.displayer.display.call_count == 3  # заголовок + 2 рядки
    doc_manager.displayer.display.assert_any_call("1. Перший")
    doc_manager.displayer.display.assert_any_call("2. Другий")


def test_doc_get_all_data(doc_manager):
    doc_manager.add_paragraph("Перший")
    doc_manager.add_paragraph("Другий")

    assert doc_manager.get_all_data() == ["Перший", "Другий"]


def test_doc_load_from_data(doc_manager):
    doc_manager.load_from_data(["А", "Б"])

    assert len(doc_manager.paragraphs) == 2
    assert doc_manager.paragraphs[0].content == "А"


def test_doc_load_from_data_replaces_old_paragraphs(doc_manager):
    doc_manager.add_paragraph("Старий")

    doc_manager.load_from_data(["Новий"])

    assert doc_manager.get_all_data() == ["Новий"]