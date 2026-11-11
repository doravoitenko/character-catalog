import json

from core.text import Paragraph
from infra.data import DataStorage
from infra.display import ConsoleDisplayer


#  Тести DataStorage 
# tmp_path - це тимчасова папка

def test_default_filename():
    storage = DataStorage()

    assert storage.filename == "game_save.json"


def test_save_data_creates_file(tmp_path):
    # Arrange: шлях до файлу в тимчасовій папці
    file = tmp_path / "save.json"
    storage = DataStorage(str(file))

    # Act
    storage.save_data({"characters": [], "texts": []})

    # Assert: файл з'явився
    assert file.exists()


def test_save_data_writes_correct_json(tmp_path):
    file = tmp_path / "save.json"
    storage = DataStorage(str(file))
    data = {"characters": [{"name": "Аліса", "hp": 100, "power": 25}], "texts": ["Привіт"]}

    storage.save_data(data)

    # Читаємо файл самостійно й порівнюємо з тим, що зберігали
    with open(file, "r", encoding="utf-8") as f:
        assert json.load(f) == data


def test_save_data_keeps_ukrainian_letters(tmp_path):
    file = tmp_path / "save.json"
    storage = DataStorage(str(file))

    storage.save_data({"texts": ["Привіт"]})

    # ensure_ascii=False означає, що літери записані як є, а не як \u041f...
    content = file.read_text(encoding="utf-8")
    assert "Привіт" in content


def test_save_data_prints_success_message(tmp_path, capsys):
    storage = DataStorage(str(tmp_path / "save.json"))

    storage.save_data({})

    output = capsys.readouterr().out
    assert "[Успіх] Дані збережено" in output


def test_load_data_returns_saved_data(tmp_path):
    # Arrange: спочатку зберігаємо
    storage = DataStorage(str(tmp_path / "save.json"))
    data = {"characters": [{"name": "Боб", "hp": 50, "power": 5}], "texts": ["А", "Б"]}
    storage.save_data(data)

    # Act: потім завантажуємо
    result = storage.load_data()

    # Assert: отримали те саме
    assert result == data


def test_load_data_missing_file_returns_empty_dict(tmp_path):
    # Файлу, якого не існує
    storage = DataStorage(str(tmp_path / "no_such_file.json"))

    result = storage.load_data()

    assert result == {}


def test_load_data_missing_file_prints_error(tmp_path, capsys):
    storage = DataStorage(str(tmp_path / "no_such_file.json"))

    storage.load_data()

    output = capsys.readouterr().out
    assert "[Помилка] Файл збереження не знайдено!" in output


# Тести ConsoleDisplayer

def test_display_prints_message(capsys):
    displayer = ConsoleDisplayer()

    displayer.display("Привіт")

    # print додає в кінці символ нового рядка "\n"
    assert capsys.readouterr().out == "Привіт\n"


def test_display_object_with_render(capsys):
    # Невеликий власний клас із методом render()
    class WithRender:
        def render(self):
            return "відрендерено"

    displayer = ConsoleDisplayer()

    displayer.display_object(WithRender())

    assert capsys.readouterr().out == "відрендерено\n"


def test_display_object_without_render(capsys):
    # У звичайного числа немає методу render(), тому виводиться str(obj)
    displayer = ConsoleDisplayer()

    displayer.display_object(42)

    assert capsys.readouterr().out == "42\n"


def test_display_object_with_real_paragraph(capsys):
    # Перевіряємо разом з реальним класом із core
    displayer = ConsoleDisplayer()

    displayer.display_object(Paragraph("Текст"))

    assert capsys.readouterr().out == "Параграф: Текст\n"