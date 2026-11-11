# Тести для поведінкових патернів, доданих під час рефакторингу.
import pytest
from unittest.mock import MagicMock

from cli.commands import CommandHandler
from cli.menu_commands import Command, ExitCommand, WebCharacterCommand
from core.snapshot import GameSnapshot
from infra.display import ConsoleDisplayer, Displayer


# Memento

def test_snapshot_to_dict():
    snapshot = GameSnapshot(characters=["а"], texts=["б"])

    assert snapshot.to_dict() == {"characters": ["а"], "texts": ["б"]}


def test_snapshot_roundtrip():
    snapshot = GameSnapshot(characters=[{"name": "Аліса"}], texts=["Привіт"])

    assert GameSnapshot.from_dict(snapshot.to_dict()) == snapshot


def test_snapshot_from_partial_data_uses_empty_lists():
    snapshot = GameSnapshot.from_dict({})

    assert snapshot.characters == []
    assert snapshot.texts == []


# Command

def test_command_is_abstract():
    with pytest.raises(TypeError):
        Command()


def test_exit_command_stops_app():
    assert ExitCommand().stops_app is True


def test_handler_registers_all_menu_items():
    handler = CommandHandler(
        MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
    )

    assert set(handler._commands) == {str(i) for i in range(11)}


# Template Method

class FakeWebCommand(WebCharacterCommand):
    # Підклас, що записує порядок викликів примітивних операцій.

    error_message = "помилка"

    def __init__(self, presenter, fail=False):
        super().__init__(MagicMock(), presenter, None)
        self.calls = []
        self.fail = fail

    def read_input(self):
        self.calls.append("read_input")
        return "id"

    def fetch(self, user_input):
        self.calls.append("fetch")
        if self.fail:
            raise RuntimeError("API недоступне")
        return {"title": "t", "vision": "v", "weapon": "w", "nation": "n"}

    def build_character(self, fetched):
        self.calls.append("build_character")
        character = MagicMock(hp=1, power=2, weapon=None)
        character.name = "Тест"
        return character, fetched


def test_template_method_runs_steps_in_order():
    command = FakeWebCommand(MagicMock())

    command.execute()

    assert command.calls == ["read_input", "fetch", "build_character"]
    command.char_mgr.characters.append.assert_called_once()


def test_template_method_stops_on_fetch_error():
    presenter = MagicMock()
    command = FakeWebCommand(presenter, fail=True)

    command.execute()

    assert command.calls == ["read_input", "fetch"]  # build_character не викликано
    presenter.displayer.display.assert_called_once_with("помилка")


def test_template_method_is_abstract():
    with pytest.raises(TypeError):
        WebCharacterCommand(MagicMock(), MagicMock(), None)


# Strategy

def test_displayer_is_abstract():
    with pytest.raises(TypeError):
        Displayer()


def test_console_displayer_is_a_displayer():
    assert isinstance(ConsoleDisplayer(), Displayer)


def test_custom_strategy_can_replace_console():
    class ListDisplayer(Displayer):
        def __init__(self):
            self.messages = []

        def display(self, message):
            self.messages.append(message)

    displayer = ListDisplayer()
    displayer.display_object(42)

    assert displayer.messages == ["42"]
