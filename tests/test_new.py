import pytest
from unittest.mock import MagicMock, patch

from cli.commands import CommandHandler
from core.characters import Character
from core.converter import character_from_api
from core.presentation import build_presentation
from core.weapons import Weapon, weapon_from_api
from infra.webapi import WebApiClient


# Фейкові дані (схожі на відповідь API, але без інтернету) 

FAKE_CHARACTER = {
    "name": "Arlecchino",
    "title": "Dire Balemoon",
    "vision": "Pyro",
    "weapon": "Polearm",
    "nation": "Snezhnaya",
}

FAKE_WEAPON = {
    "name": "Crimson Moon's Semblance",
    "type": "Polearm",
    "rarity": 5,
    "baseAttack": 48,
}


@pytest.fixture
def handler():
    web_client = MagicMock()
    web_client.get_character.return_value = FAKE_CHARACTER
    web_client.get_weapon.return_value = FAKE_WEAPON
    return CommandHandler(
        MagicMock(), MagicMock(), MagicMock(), MagicMock(), web_client
    )


# Тести core/converter.py 

def test_character_from_api_takes_name():
    character = character_from_api(FAKE_CHARACTER)

    assert character.name == "Arlecchino"


def test_character_from_api_hp_and_power_in_range():
    # Числа випадкові, тому перевіряємо не значення, а діапазон
    character = character_from_api(
        FAKE_CHARACTER, hp_range=(1000, 15000), power_range=(500, 2000)
    )

    assert 1000 <= character.hp <= 15000
    assert 500 <= character.power <= 2000


def test_character_from_api_custom_range():
    # Якщо діапазон з одного числа, результат завжди однаковий
    character = character_from_api(FAKE_CHARACTER, (7, 7), (3, 3))

    assert character.hp == 7
    assert character.power == 3


#  Тести core/weapons.py 

def test_weapon_from_api():
    weapon = weapon_from_api(FAKE_WEAPON)

    assert weapon.name == "Crimson Moon's Semblance"
    assert weapon.weapon_type == "Polearm"
    assert weapon.rarity == 5
    assert weapon.base_attack == 48


def test_weapon_to_dict():
    weapon = Weapon("Меч", "Sword", 3, 20)

    assert weapon.to_dict() == {
        "name": "Меч",
        "weapon_type": "Sword",
        "rarity": 3,
        "base_attack": 20,
    }


#  Тести equip (core/characters.py) 

def test_character_has_no_weapon_by_default():
    character = Character("Аліса", 100, 25)

    assert character.weapon is None


def test_character_equip():
    character = Character("Аліса", 100, 25)
    weapon = Weapon("Меч", "Sword", 3, 20)

    character.equip(weapon)

    assert character.weapon is weapon


# Тести core/presentation.py 

def test_presentation_without_weapon():
    character = Character("Arlecchino", 5000, 1000)

    result = build_presentation(character, FAKE_CHARACTER)

    assert "Параграф: Arlecchino, Dire Balemoon" in result
    assert "Параграф: Стихія: Pyro" in result
    assert "Параграф: HP: 5000, Power: 1000" in result
    assert "Екіпіровано" not in result


def test_presentation_with_weapon():
    character = Character("Arlecchino", 5000, 1000)
    character.equip(weapon_from_api(FAKE_WEAPON))

    result = build_presentation(character, FAKE_CHARACTER)

    assert "Параграф: Екіпіровано: Crimson Moon's Semblance (атака 48)" in result


#  Тести infra/webapi.py 
# patch тимчасово підміняє urlopen, тож інтернет не потрібен.

def test_webapi_get_json_parses_response():
    fake_response = MagicMock()
    fake_response.read.return_value = '{"name": "Amber"}'.encode("utf-8")
    fake_response.__enter__.return_value = fake_response

    with patch("urllib.request.urlopen", return_value=fake_response):
        result = WebApiClient().get_json("characters/amber")

    assert result == {"name": "Amber"}


def test_webapi_get_character_uses_correct_path():
    client = WebApiClient()
    client.get_json = MagicMock(return_value={})

    client.get_character("amber")

    client.get_json.assert_called_once_with("characters/amber")


def test_webapi_get_weapon_uses_correct_path():
    client = WebApiClient()
    client.get_json = MagicMock(return_value={})

    client.get_weapon("staff-of-homa")

    client.get_json.assert_called_once_with("weapons/staff-of-homa")


def test_webapi_lists_use_correct_paths():
    client = WebApiClient()
    client.get_json = MagicMock(return_value=[])

    client.get_character_names()
    client.get_weapon_names()

    client.get_json.assert_any_call("characters")
    client.get_json.assert_any_call("weapons")


#  Тести cli/commands.py (нові пункти меню) 

def test_command_7_loads_character(handler):
    handler.presenter.get_input.return_value = " Arlecchino "

    result = handler.handle_command("7")

    # пробіли прибрані, літери малі
    handler.web_client.get_character.assert_called_once_with("arlecchino")
    handler.char_mgr.characters.append.assert_called_once()
    assert result is True


def test_command_7_shows_error_when_api_fails(handler):
    handler.presenter.get_input.return_value = "nobody"
    handler.web_client.get_character.side_effect = Exception("нема інтернету")

    handler.handle_command("7")

    handler.presenter.displayer.display.assert_called_once_with(
        "[Помилка] Не вдалося завантажити персонажа!"
    )
    handler.char_mgr.characters.append.assert_not_called()


def test_command_8_shows_character_list(handler):
    handler.web_client.get_character_names.return_value = ["amber", "diluc"]

    handler.handle_command("8")

    handler.presenter.displayer.display.assert_any_call("1. amber")
    handler.presenter.displayer.display.assert_any_call("2. diluc")


def test_command_9_shows_weapon_list(handler):
    handler.web_client.get_weapon_names.return_value = ["rust", "quartz"]

    handler.handle_command("9")

    handler.presenter.displayer.display.assert_any_call("1. rust")
    handler.presenter.displayer.display.assert_any_call("2. quartz")


def test_command_8_shows_error_when_api_fails(handler):
    handler.web_client.get_character_names.side_effect = Exception("помилка")

    handler.handle_command("8")

    handler.presenter.displayer.display.assert_called_once_with(
        "[Помилка] Не вдалося отримати список!"
    )


def test_command_10_equips_weapon(handler):
    handler.presenter.get_input.side_effect = ["arlecchino", "rust"]

    handler.handle_command("10")

    # беремо персонажа, якого додали в список, і дивимось, чи є в нього зброя
    added_character = handler.char_mgr.characters.append.call_args[0][0]
    assert added_character.weapon is not None
    assert added_character.weapon.name == "Crimson Moon's Semblance"


def test_command_10_shows_error_when_api_fails(handler):
    handler.presenter.get_input.side_effect = ["arlecchino", "rust"]
    handler.web_client.get_weapon.side_effect = Exception("помилка")

    handler.handle_command("10")

    handler.presenter.displayer.display.assert_called_once_with(
        "[Помилка] Не вдалося завантажити дані!"
    )
    handler.char_mgr.characters.append.assert_not_called()