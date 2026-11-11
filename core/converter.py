import random

from core.characters import Character


def character_from_api(api_data, hp_range=(1000, 15000), power_range=(500, 2000)):
    # Перетворює дані з API на Character.
    #
    # hp і power в API немає, тому генеруємо їх випадково.
    name = api_data["name"]
    hp = random.randint(*hp_range)
    power = random.randint(*power_range)
    return Character(name, hp, power)