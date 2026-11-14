import pytest

from infra.json_source import JsonFileSource


def test_read_returns_decoded_json(tmp_path):
    file = tmp_path / "data.json"
    file.write_text('[{"name": "Аліса"}]', encoding="utf-8")

    assert JsonFileSource().read(str(file)) == [{"name": "Аліса"}]


def test_read_missing_file_raises_os_error(tmp_path):
    with pytest.raises(OSError):
        JsonFileSource().read(str(tmp_path / "немає.json"))


def test_read_broken_json_raises_value_error(tmp_path):
    file = tmp_path / "data.json"
    file.write_text("{ зламано", encoding="utf-8")

    with pytest.raises(ValueError):
        JsonFileSource().read(str(file))


def test_read_non_utf8_file_raises_value_error(tmp_path):
    file = tmp_path / "data.json"
    file.write_bytes(b"\xff\xfe\x00\x80")

    with pytest.raises(ValueError):
        JsonFileSource().read(str(file))
