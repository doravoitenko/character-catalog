import pytest

import catalog_app
from cli.args import ArgParser, Args
from cli.facade import CLI
from cli.graphic import CLIGraphic
from cli.renderers import CommandListRenderer, ProfileListRenderer, ProfileRenderer, Renderer
from cli.strategies import CatalogStrategy, CommandStrategy
from core.catalog import CharacterCatalog
from core.profile import CharacterProfile
from infra.catalog_storage import CatalogStorage
from tests.fakes import ScriptedPresenter


def make_cli(tmp_path, inputs=()):
    # Збирає застосунок так само, як catalog_app, але з підробленою консоллю
    presenter = ScriptedPresenter(inputs)
    cli = catalog_app.build_cli(presenter, str(tmp_path / "catalog.json"))
    return cli, presenter


def run(tmp_path, inputs):
    cli, presenter = make_cli(tmp_path, inputs)
    cli.run()
    return cli, presenter


# ---------- ArgParser ----------

def test_parser_splits_command_and_rest():
    assert ArgParser().parse_args("show Hu Tao") == Args("show", "Hu Tao")


def test_parser_lowercases_command_only():
    assert ArgParser().parse_args("  SHOW   Hu Tao  ") == Args("show", "Hu Tao")


def test_parser_without_arguments():
    assert ArgParser().parse_args("list") == Args("list", "")


def test_parser_empty_line():
    assert ArgParser().parse_args("   ") == Args("", "")


# ---------- CLIGraphic ----------

def test_graphic_messages():
    assert CLIGraphic.success("ок") == "[Успіх] ок"
    assert CLIGraphic.error("збій") == "[Помилка] збій"


def test_graphic_box_has_equal_line_widths():
    box = CLIGraphic.box("Назва", [("Поле", "значення"), ("Довге поле", "x")])

    assert len({len(line) for line in box.splitlines()}) == 1
    assert box.splitlines()[0].startswith("┌─ Назва ")
    assert "Довге поле : x" in box


def test_graphic_box_wider_for_long_title():
    box = CLIGraphic.box("Дуже-дуже довга назва", [("a", "b")])

    assert "Дуже-дуже довга назва" in box.splitlines()[0]
    assert len({len(line) for line in box.splitlines()}) == 1


def test_graphic_box_without_rows():
    assert len(CLIGraphic.box("Порожньо", []).splitlines()) == 2


def test_graphic_table_aligns_columns():
    table = CLIGraphic.table(["№", "Ім'я"], [("1", "Амбер"), ("10", "Ян")])
    lines = table.splitlines()

    assert lines[0] == "№  │ Ім'я"
    assert lines[1] == "───┼──────"
    assert lines[2] == "1  │ Амбер"
    assert lines[3] == "10 │ Ян"


def test_graphic_table_without_rows():
    assert len(CLIGraphic.table(["А", "Б"], []).splitlines()) == 2


# ---------- Renderers ----------

def test_renderer_is_abstract():
    with pytest.raises(TypeError):
        Renderer()


def test_profile_renderer_shows_all_fields_and_link():
    profile = CharacterProfile("Amber", "Outrider", "Pyro", "Bow", "Mondstadt", "https://x/a.png")

    text = ProfileRenderer().render(profile)

    for part in ("Amber", "Outrider", "Pyro", "Bow", "Mondstadt", "https://x/a.png"):
        assert part in text


def test_profile_renderer_marks_empty_fields():
    assert "Титул    : —" in ProfileRenderer().render(CharacterProfile("Amber"))


def test_profile_list_renderer_numbers_rows():
    text = ProfileListRenderer().render([CharacterProfile("Amber"), CharacterProfile("Diluc")])

    assert "1 │ Amber" in text
    assert "2 │ Diluc" in text


def test_profile_list_renderer_empty():
    assert ProfileListRenderer().render([]) == "Каталог порожній."


def test_command_list_renderer():
    text = CommandListRenderer().render([("list", "list", "показати")])

    assert "Команда" in text and "показати" in text


# ---------- CLI facade ----------

def test_cli_without_strategy_reports_error():
    presenter = ScriptedPresenter()
    cli = CLI(presenter)

    cli.exec_command("list")

    assert "Набір команд не підключено" in presenter.output


def test_cli_ignores_empty_line(tmp_path):
    cli, presenter = make_cli(tmp_path)

    cli.exec_command("   ")

    assert presenter.output == ""


def test_cli_unknown_command(tmp_path):
    cli, presenter = make_cli(tmp_path)

    cli.exec_command("abracadabra")

    assert "Невідома команда: abracadabra" in presenter.output


def test_cli_display_uses_given_renderer(tmp_path):
    cli, presenter = make_cli(tmp_path)

    class Shout(Renderer):
        def render(self, obj):
            return obj.upper()

    cli.display("привіт", Shout())

    assert presenter.output == "ПРИВІТ"


def test_cli_accepts_custom_parser():
    class DashParser:
        def parse_args(self, raw):
            return Args(raw.replace("-", ""), "")

    presenter = ScriptedPresenter()
    cli = CLI(presenter, DashParser())
    cli.use_strategy(CatalogStrategy(CharacterCatalog(), CatalogStorage("x")))

    cli.exec_command("li-st")

    assert "Каталог порожній." in presenter.output


def test_cli_run_stops_when_input_ends(tmp_path):
    cli, _ = run(tmp_path, ["list"])

    assert cli.running is True  # завершилось через кінець вводу, а не через exit


def test_cli_run_stops_on_ctrl_c(tmp_path):
    cli, presenter = make_cli(tmp_path)

    def interrupt(prompt):
        raise KeyboardInterrupt

    presenter.get_input = interrupt
    cli.run()  # не має впасти


# ---------- Strategy ----------

def test_strategy_is_abstract():
    with pytest.raises(TypeError):
        CommandStrategy()


def test_strategy_lists_registered_commands():
    strategy = CatalogStrategy(CharacterCatalog(), CatalogStorage("x"))

    assert strategy.get_command_selectors() == [
        "list", "show", "create", "update", "save", "help", "exit"
    ]


def test_strategy_can_register_new_command():
    strategy = CatalogStrategy(CharacterCatalog(), CatalogStorage("x"))
    calls = []

    class Ping:
        usage = "ping"
        description = "тест"

        def __init__(self, cli, catalog, storage, args):
            calls.append(args.command)

        def execute(self):
            calls.append("executed")

    strategy.register_command("ping", Ping)

    assert strategy.exec_command(None, Args("ping")) is True
    assert calls == ["ping", "executed"]
    assert ("ping", "ping", "тест") in strategy.describe()


def test_strategy_returns_false_for_unknown_command():
    strategy = CatalogStrategy(CharacterCatalog(), CatalogStorage("x"))

    assert strategy.exec_command(None, Args("nope")) is False


# ---------- Команди каталогу ----------

def test_help_lists_all_commands(tmp_path):
    _, presenter = run(tmp_path, ["help"])

    for name in ("list", "show", "create", "update", "save", "help", "exit"):
        assert name in presenter.output


def test_list_shows_default_characters(tmp_path):
    _, presenter = run(tmp_path, ["list"])

    assert "Amber" in presenter.output
    assert "Arlecchino" in presenter.output


def test_show_by_name_prints_card_with_image_link(tmp_path):
    _, presenter = run(tmp_path, ["show amber"])

    assert "Outrider" in presenter.output
    assert "https://genshin.jmp.blue/characters/amber/card" in presenter.output


def test_show_by_number(tmp_path):
    _, presenter = run(tmp_path, ["show 2"])

    assert "Dark Side of Dawn" in presenter.output


def test_show_without_argument(tmp_path):
    _, presenter = run(tmp_path, ["show"])

    assert "Вкажіть ім'я або номер" in presenter.output


def test_show_unknown_name_and_number(tmp_path):
    _, presenter = run(tmp_path, ["show нема", "show 99"])

    assert "Персонажа «нема» не знайдено" in presenter.output
    assert "Персонажа «99» не знайдено" in presenter.output


def test_create_adds_character(tmp_path):
    cli, presenter = run(tmp_path, [
        "create", "Hu Tao", "Butterfly Cleanser", "Pyro", "Polearm", "Liyue",
        "https://example.com/hutao.png", "list",
    ])

    assert "Персонажа «Hu Tao» створено" in presenter.output
    assert "5 │ Hu Tao" in presenter.output
    assert cli.strategy.catalog.dirty is True


def test_create_asks_questions_in_order(tmp_path):
    _, presenter = run(tmp_path, ["create", "Новий", "", "", "", "", ""])

    assert presenter.prompts[1:4] == ["Ім'я: ", "Титул: ", "Стихія: "]


def test_interrupted_dialog_cancels_only_that_command(tmp_path):
    cli, presenter = run(tmp_path, ["create", "Хтось"])  # ввід обривається посеред діалогу

    assert "Команду перервано." in presenter.output
    assert len(cli.strategy.catalog) == 4
    assert cli.strategy.catalog.dirty is False


def test_create_rejects_empty_name_without_more_questions(tmp_path):
    cli, presenter = run(tmp_path, ["create", "   "])

    assert "ім'я не може бути порожнім" in presenter.output
    assert len(presenter.prompts) == 3  # catalog>, Ім'я, catalog>


def test_create_rejects_existing_name_without_more_questions(tmp_path):
    cli, presenter = run(tmp_path, ["create", "amber"])

    assert "уже є в каталозі" in presenter.output
    assert len(cli.strategy.catalog) == 4


def test_create_rejects_bad_link(tmp_path):
    cli, presenter = run(tmp_path, [
        "create", "Хтось", "", "", "", "", "не-посилання",
    ])

    assert "посилання має починатися" in presenter.output
    assert len(cli.strategy.catalog) == 4


def test_create_allows_empty_optional_fields(tmp_path):
    cli, _ = run(tmp_path, ["create", "Хтось", "", "", "", "", ""])

    assert cli.strategy.catalog.find("Хтось") is not None


def test_save_writes_file_and_clears_dirty(tmp_path):
    cli, presenter = run(tmp_path, [
        "create", "Хтось", "", "", "", "", "", "save",
    ])

    assert "Збережено персонажів: 5" in presenter.output
    assert cli.strategy.catalog.dirty is False
    assert "Хтось" in (tmp_path / "catalog.json").read_text(encoding="utf-8")


def test_save_reports_write_error(tmp_path):
    cli, presenter = make_cli(tmp_path, ["save"])
    cli.strategy.storage = CatalogStorage(str(tmp_path / "немає_папки" / "c.json"))

    cli.run()

    assert "Не вдалося зберегти" in presenter.output


def test_update_reloads_file_and_shows_list(tmp_path):
    cli, presenter = make_cli(tmp_path, ["update"])
    CatalogStorage(str(tmp_path / "catalog.json")).save([{"name": "Зі файлу"}])

    cli.run()

    assert "Каталог оновлено, персонажів: 1" in presenter.output
    assert "1 │ Зі файлу" in presenter.output


def test_update_when_file_is_missing(tmp_path):
    cli, presenter = make_cli(tmp_path, ["update"])
    (tmp_path / "catalog.json").unlink()

    cli.run()

    assert "Файл каталогу не знайдено" in presenter.output
    assert len(cli.strategy.catalog) == 4


def test_update_with_broken_file_keeps_catalog(tmp_path):
    cli, presenter = make_cli(tmp_path, ["update"])
    (tmp_path / "catalog.json").write_text("{ зламано", encoding="utf-8")

    cli.run()

    assert "Не вдалося оновити каталог" in presenter.output
    assert len(cli.strategy.catalog) == 4


def test_update_asks_confirmation_when_there_are_unsaved_changes(tmp_path):
    cli, presenter = run(tmp_path, [
        "create", "Хтось", "", "", "", "", "", "update", "n",
    ])

    assert "Оновлення скасовано" in presenter.output
    assert cli.strategy.catalog.find("Хтось") is not None


def test_update_after_confirmation_discards_unsaved_changes(tmp_path):
    cli, _ = run(tmp_path, [
        "create", "Хтось", "", "", "", "", "", "update", "y",
    ])

    assert cli.strategy.catalog.find("Хтось") is None
    assert cli.strategy.catalog.dirty is False


# ---------- Вихід ----------

def test_exit_without_changes_stops_immediately(tmp_path):
    cli, presenter = run(tmp_path, ["exit"])

    assert cli.running is False
    assert "До побачення!" in presenter.output
    assert len(presenter.prompts) == 1


def test_exit_with_unsaved_changes_and_save(tmp_path):
    cli, _ = run(tmp_path, ["create", "Хтось", "", "", "", "", "", "exit", "y"])

    assert cli.running is False
    assert "Хтось" in (tmp_path / "catalog.json").read_text(encoding="utf-8")


def test_exit_with_unsaved_changes_and_discard(tmp_path):
    cli, _ = run(tmp_path, ["create", "Хтось", "", "", "", "", "", "exit", "n"])

    assert cli.running is False
    assert "Хтось" not in (tmp_path / "catalog.json").read_text(encoding="utf-8")


def test_exit_can_be_cancelled(tmp_path):
    cli, presenter = run(tmp_path, ["create", "Хтось", "", "", "", "", "", "exit", ""])

    assert cli.running is True
    assert "Вихід скасовано" in presenter.output


def test_exit_stays_if_saving_fails(tmp_path):
    cli, presenter = make_cli(tmp_path, [
        "create", "Хтось", "", "", "", "", "", "exit", "y",
    ])
    cli.strategy.storage = CatalogStorage(str(tmp_path / "немає_папки" / "c.json"))

    cli.run()

    assert cli.running is True
    assert "Не вдалося зберегти" in presenter.output


# ---------- Збирання застосунку (catalog_app) ----------

def test_first_run_creates_file_with_defaults(tmp_path):
    make_cli(tmp_path)

    assert (tmp_path / "catalog.json").exists()
    assert len(CatalogStorage(str(tmp_path / "catalog.json")).load()) == 4


def test_data_survives_restart(tmp_path):
    run(tmp_path, ["create", "Хтось", "", "", "", "", "", "save", "exit"])

    _, presenter = run(tmp_path, ["list"])  # "новий запуск"

    assert "5 │ Хтось" in presenter.output


def test_broken_file_gives_warning_and_defaults(tmp_path):
    (tmp_path / "catalog.json").write_text("{ зламано", encoding="utf-8")

    cli, presenter = make_cli(tmp_path)

    assert "Не вдалося прочитати файл каталогу" in presenter.output
    assert len(cli.strategy.catalog) == 4
    # пошкоджений файл не перезаписується
    assert (tmp_path / "catalog.json").read_text(encoding="utf-8") == "{ зламано"


def test_unwritable_location_does_not_crash(tmp_path):
    presenter = ScriptedPresenter()

    cli = catalog_app.build_cli(presenter, str(tmp_path / "немає_папки" / "c.json"))

    assert len(cli.strategy.catalog) == 4


def test_main_runs_and_exits(tmp_path, monkeypatch, capsys):
    answers = iter(["help", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    catalog_app.main(str(tmp_path / "catalog.json"))

    output = capsys.readouterr().out
    assert "Каталог персонажів" in output
    assert "До побачення!" in output
