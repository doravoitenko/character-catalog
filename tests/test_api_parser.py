import pytest

from core.api_parser import CharacterApiParser, ParseError, ParseResult, slugify

FULL = {
    "name": "Hu Tao",
    "title": "Fragrance in Thaw",
    "vision": "Pyro",
    "weapon": "Polearm",
    "nation": "Liyue",
    "rarity": 5,
    "description": "зайве поле, яке ігнорується",
}


# slugify 


def test_slugify_builds_api_style_id():
    assert slugify("Hu Tao") == "hu-tao"
    assert slugify("Kaedehara  Kazuha") == "kaedehara-kazuha"
    assert slugify("Amber") == "amber"


def test_slugify_non_latin_name_gives_empty_slug():
    assert slugify("Аліса") == ""


# parse_character 


def test_parse_character_maps_all_fields():
    profile = CharacterApiParser().parse_character(FULL)

    assert profile.name == "Hu Tao"
    assert profile.title == "Fragrance in Thaw"
    assert profile.vision == "Pyro"
    assert profile.weapon == "Polearm"
    assert profile.nation == "Liyue"


def test_parse_character_builds_image_link_from_name():
    profile = CharacterApiParser().parse_character(FULL)

    assert profile.image_url == "https://genshin.jmp.blue/characters/hu-tao/card"


def test_parse_character_uses_custom_image_base():
    parser = CharacterApiParser(image_base="https://example.com/img")

    assert parser.parse_character(FULL).image_url == "https://example.com/img/hu-tao/card"


def test_parse_character_without_latin_name_has_no_image_link():
    assert CharacterApiParser().parse_character({"name": "Аліса"}).image_url == ""


def test_parse_character_only_name_is_enough():
    profile = CharacterApiParser().parse_character({"name": "Traveler"})

    assert profile.title == ""
    assert profile.vision == ""


def test_parse_character_ignores_unknown_fields():
    profile = CharacterApiParser().parse_character({"name": "A", "skillTalents": [1, 2, 3]})

    assert profile.name == "A"


def test_parse_character_trims_values():
    profile = CharacterApiParser().parse_character({"name": "  Amber ", "vision": " Pyro "})

    assert profile.name == "Amber"
    assert profile.vision == "Pyro"


def test_parse_character_converts_numbers_and_ignores_odd_types():
    profile = CharacterApiParser().parse_character({
        "name": "A", "title": 7, "vision": None, "weapon": ["Bow"], "nation": {"x": 1},
    })

    assert profile.title == "7"
    assert profile.vision == ""
    assert profile.weapon == ""
    assert profile.nation == ""


def test_parse_character_rejects_missing_or_blank_name():
    parser = CharacterApiParser()

    for data in ({}, {"name": ""}, {"name": "   "}, {"name": None}, {"name": True}):
        with pytest.raises(ParseError):
            parser.parse_character(data)


def test_parse_character_rejects_non_object():
    with pytest.raises(ParseError):
        CharacterApiParser().parse_character("Amber")


def test_parse_error_is_a_value_error():
    assert issubclass(ParseError, ValueError)


# parse 


def test_parse_list_of_objects():
    result = CharacterApiParser().parse([{"name": "A"}, {"name": "B"}])

    assert [p.name for p in result.profiles] == ["A", "B"]
    assert result.errors == []


def test_parse_single_object_is_treated_as_one_item_list():
    result = CharacterApiParser().parse(FULL)

    assert [p.name for p in result.profiles] == ["Hu Tao"]


def test_parse_empty_list():
    assert CharacterApiParser().parse([]) == ParseResult([], [])


def test_parse_collects_errors_and_keeps_good_items():
    result = CharacterApiParser().parse([{"name": "A"}, {"title": "без імені"}, 5, {"name": "B"}])

    assert [p.name for p in result.profiles] == ["A", "B"]
    assert len(result.errors) == 2
    assert result.errors[0].startswith("елемент 2:")
    assert result.errors[1].startswith("елемент 3:")


def test_parse_skips_duplicates_inside_the_list():
    result = CharacterApiParser().parse([{"name": "Amber"}, {"name": "amber "}])

    assert len(result.profiles) == 1
    assert "повторюється" in result.errors[0]


def test_parse_rejects_wrong_top_level_type():
    for data in ("text", 42, None, True):
        with pytest.raises(ParseError):
            CharacterApiParser().parse(data)


# parse_text 


def test_parse_text_reads_json_text():
    result = CharacterApiParser().parse_text('[{"name": "Amber", "vision": "Pyro"}]')

    assert result.profiles[0].vision == "Pyro"


def test_parse_text_rejects_broken_json():
    with pytest.raises(ParseError):
        CharacterApiParser().parse_text("{ це не json")


def test_parse_text_keeps_ukrainian_letters():
    result = CharacterApiParser().parse_text('{"name": "Аліса", "title": "Героїня"}')

    assert result.profiles[0].title == "Героїня"
