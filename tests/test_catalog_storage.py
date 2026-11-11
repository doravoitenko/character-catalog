import pytest

from infra.catalog_storage import CatalogStorage


def test_default_filename():
    assert CatalogStorage().filename == "catalog.json"


def test_save_and_load_roundtrip(tmp_path):
    storage = CatalogStorage(str(tmp_path / "c.json"))
    data = [{"name": "Аліса", "title": "Тест"}]

    storage.save(data)

    assert storage.load() == data


def test_save_keeps_ukrainian_letters(tmp_path):
    file = tmp_path / "c.json"

    CatalogStorage(str(file)).save([{"name": "Аліса"}])

    assert "Аліса" in file.read_text(encoding="utf-8")


def test_load_missing_file_returns_none(tmp_path):
    assert CatalogStorage(str(tmp_path / "немає.json")).load() is None


def test_load_broken_json_raises_value_error(tmp_path):
    file = tmp_path / "c.json"
    file.write_text("{ це не json", encoding="utf-8")

    with pytest.raises(ValueError):
        CatalogStorage(str(file)).load()


def test_load_wrong_structure_raises_value_error(tmp_path):
    file = tmp_path / "c.json"
    file.write_text('{"something": []}', encoding="utf-8")

    with pytest.raises(ValueError):
        CatalogStorage(str(file)).load()


def test_load_list_instead_of_object_raises_value_error(tmp_path):
    file = tmp_path / "c.json"
    file.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(ValueError):
        CatalogStorage(str(file)).load()


def test_save_to_unwritable_path_raises_os_error(tmp_path):
    storage = CatalogStorage(str(tmp_path / "немає_папки" / "c.json"))

    with pytest.raises(OSError):
        storage.save([])
