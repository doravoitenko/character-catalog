import pytest

from core.catalog import CatalogFilter, CharacterCatalog
from core.profile import CharacterProfile


def make_catalog():
    return CharacterCatalog([
        CharacterProfile("Amber", "Outrider", "Pyro", "Bow", "Mondstadt"),
        CharacterProfile("Venti", "Windborne Bard", "Anemo", "Bow", "Mondstadt"),
        CharacterProfile("Hu Tao", "Fragrance in Thaw", "Pyro", "Polearm", "Liyue"),
        CharacterProfile("Xiao", "Vigilant Yaksha", "Anemo", "Polearm", "Liyue"),
        CharacterProfile("Traveler"),
    ])


def names(profiles):
    return [p.name for p in profiles]


#  query: пошук 

def test_query_without_criteria_returns_everyone_sorted_by_name():
    assert names(make_catalog().query()) == ["Amber", "Hu Tao", "Traveler", "Venti", "Xiao"]


def test_query_text_searches_name():
    assert names(make_catalog().query(CatalogFilter(text="hu"))) == ["Hu Tao"]


def test_query_text_searches_title():
    assert names(make_catalog().query(CatalogFilter(text="bard"))) == ["Venti"]


def test_query_text_searches_vision_weapon_and_nation():
    catalog = make_catalog()

    assert names(catalog.query(CatalogFilter(text="pyro"))) == ["Amber", "Hu Tao"]
    assert names(catalog.query(CatalogFilter(text="polearm"))) == ["Hu Tao", "Xiao"]
    assert names(catalog.query(CatalogFilter(text="mondstadt"))) == ["Amber", "Venti"]


def test_query_text_ignores_case_and_extra_spaces():
    assert names(make_catalog().query(CatalogFilter(text="  HU   tao "))) == ["Hu Tao"]


def test_query_no_matches_returns_empty_list():
    assert make_catalog().query(CatalogFilter(text="нічого")) == []


#  query: фільтри 

def test_query_filters_by_each_field():
    catalog = make_catalog()

    assert names(catalog.query(CatalogFilter(vision="Pyro"))) == ["Amber", "Hu Tao"]
    assert names(catalog.query(CatalogFilter(weapon="bow"))) == ["Amber", "Venti"]
    assert names(catalog.query(CatalogFilter(nation="LIYUE"))) == ["Hu Tao", "Xiao"]


def test_query_filters_require_exact_value():
    assert make_catalog().query(CatalogFilter(vision="Pyr")) == []


def test_query_combines_text_and_filters():
    found = make_catalog().query(CatalogFilter(text="tao", vision="pyro", nation="liyue"))

    assert names(found) == ["Hu Tao"]


def test_query_empty_filter_values_mean_any():
    assert len(make_catalog().query(CatalogFilter(vision="  ", weapon=""))) == 5


#  query: сортування 

def test_query_sorts_by_other_fields_then_by_name():
    catalog = make_catalog()

    assert names(catalog.query(CatalogFilter(sort_by="nation"))) == [
        "Traveler", "Hu Tao", "Xiao", "Amber", "Venti"
    ]
    assert names(catalog.query(CatalogFilter(sort_by="vision"))) == [
        "Traveler", "Venti", "Xiao", "Amber", "Hu Tao"
    ]
    assert names(catalog.query(CatalogFilter(sort_by="weapon"))) == [
        "Traveler", "Amber", "Venti", "Hu Tao", "Xiao"
    ]


def test_query_rejects_unknown_sort_key():
    with pytest.raises(ValueError):
        make_catalog().query(CatalogFilter(sort_by="rarity"))


def test_query_does_not_change_catalog_order():
    catalog = make_catalog()

    catalog.query(CatalogFilter(sort_by="nation"))

    assert names(catalog.all()) == ["Amber", "Venti", "Hu Tao", "Xiao", "Traveler"]


#  values_of 

def test_values_of_returns_sorted_distinct_non_empty_values():
    catalog = make_catalog()

    assert catalog.values_of("vision") == ["Anemo", "Pyro"]
    assert catalog.values_of("weapon") == ["Bow", "Polearm"]
    assert catalog.values_of("nation") == ["Liyue", "Mondstadt"]


def test_values_of_empty_catalog():
    assert CharacterCatalog().values_of("vision") == []


def test_values_of_rejects_unknown_field():
    with pytest.raises(ValueError):
        make_catalog().values_of("title")


#  merge 

def test_merge_adds_new_and_skips_existing():
    catalog = make_catalog()

    added, skipped = catalog.merge([CharacterProfile("Ganyu"), CharacterProfile("amber", title="інший")])

    assert names(added) == ["Ganyu"]
    assert names(skipped) == ["amber"]
    assert catalog.find("Amber").title == "Outrider"  # існуючий не перезаписано
    assert len(catalog) == 6


def test_merge_marks_dirty_only_when_something_added():
    catalog = make_catalog()

    catalog.merge([CharacterProfile("Amber")])
    assert catalog.dirty is False

    catalog.merge([CharacterProfile("Ganyu")])
    assert catalog.dirty is True


def test_merge_handles_duplicates_inside_the_batch():
    catalog = CharacterCatalog()

    added, skipped = catalog.merge([CharacterProfile("A"), CharacterProfile("a")])

    assert len(added) == 1 and len(skipped) == 1
