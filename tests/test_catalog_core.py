import pytest

from core.catalog import CharacterCatalog, default_profiles
from core.profile import CharacterProfile


# ---------- CharacterProfile ----------

def test_profile_trims_and_normalizes_name():
    profile = CharacterProfile("  Hu   Tao ", title=" Boss ")

    assert profile.name == "Hu Tao"
    assert profile.title == "Boss"


def test_profile_requires_name():
    with pytest.raises(ValueError):
        CharacterProfile("   ")


def test_profile_rejects_bad_image_url():
    with pytest.raises(ValueError):
        CharacterProfile("Amber", image_url="ftp://amber.png")


def test_profile_accepts_empty_and_http_urls():
    assert CharacterProfile("A").image_url == ""
    assert CharacterProfile("A", image_url="http://x/a.png").image_url == "http://x/a.png"
    assert CharacterProfile("A", image_url="https://x/a.png").image_url == "https://x/a.png"


def test_profile_dict_roundtrip():
    profile = CharacterProfile("Amber", "Outrider", "Pyro", "Bow", "Mondstadt", "https://x/a.png")

    assert CharacterProfile.from_dict(profile.to_dict()) == profile


def test_profile_from_dict_fills_missing_fields():
    profile = CharacterProfile.from_dict({"name": "Amber"})

    assert profile.title == ""
    assert profile.vision == ""


def test_profile_from_dict_handles_null_values():
    assert CharacterProfile.from_dict({"name": "Amber", "title": None}).title == ""


def test_profile_from_dict_rejects_broken_records():
    with pytest.raises(ValueError):
        CharacterProfile.from_dict({"title": "без імені"})
    with pytest.raises(ValueError):
        CharacterProfile.from_dict("не словник")


# ---------- CharacterCatalog ----------

def make_catalog():
    return CharacterCatalog([CharacterProfile("Amber"), CharacterProfile("Diluc")])


def test_catalog_all_returns_copy():
    catalog = make_catalog()

    catalog.all().clear()

    assert len(catalog) == 2


def test_catalog_find_ignores_case_and_spaces():
    catalog = CharacterCatalog([CharacterProfile("Hu Tao")])

    assert catalog.find("hu   TAO").name == "Hu Tao"
    assert catalog.find("нема") is None


def test_catalog_get_by_number_is_one_based():
    catalog = make_catalog()

    assert catalog.get_by_number(1).name == "Amber"
    assert catalog.get_by_number(2).name == "Diluc"
    assert catalog.get_by_number(0) is None
    assert catalog.get_by_number(3) is None


def test_catalog_add_marks_dirty():
    catalog = make_catalog()
    assert catalog.dirty is False

    catalog.add(CharacterProfile("Keqing"))

    assert len(catalog) == 3
    assert catalog.dirty is True


def test_catalog_rejects_duplicate_names():
    catalog = make_catalog()

    with pytest.raises(ValueError):
        catalog.add(CharacterProfile("amber"))

    assert len(catalog) == 2
    assert catalog.dirty is False


def test_catalog_data_roundtrip():
    catalog = make_catalog()
    other = CharacterCatalog()

    other.load_from_data(catalog.get_all_data())

    assert other.get_all_data() == catalog.get_all_data()
    assert other.dirty is False


def test_catalog_load_replaces_old_profiles_and_clears_dirty():
    catalog = make_catalog()
    catalog.add(CharacterProfile("Keqing"))

    catalog.load_from_data([{"name": "Новий"}])

    assert [p.name for p in catalog.all()] == ["Новий"]
    assert catalog.dirty is False


def test_catalog_load_keeps_old_data_on_error():
    catalog = make_catalog()

    with pytest.raises(ValueError):
        catalog.load_from_data([{"name": "Добрий"}, {"немає": "імені"}])

    assert [p.name for p in catalog.all()] == ["Amber", "Diluc"]


def test_catalog_load_rejects_duplicates():
    catalog = CharacterCatalog()

    with pytest.raises(ValueError):
        catalog.load_from_data([{"name": "Amber"}, {"name": "AMBER"}])


def test_catalog_mark_saved():
    catalog = make_catalog()
    catalog.add(CharacterProfile("Keqing"))

    catalog.mark_saved()

    assert catalog.dirty is False


def test_default_profiles_are_valid_and_unique():
    catalog = CharacterCatalog()

    catalog.load_from_data([p.to_dict() for p in default_profiles()])

    assert len(catalog) >= 3
    assert all(p.image_url.startswith("https://") for p in catalog.all())
