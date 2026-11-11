class Weapon:
    # Зброя, яку можна екіпірувати на персонажа.

    def __init__(self, name, weapon_type, rarity, base_attack):
        self.name = name
        self.weapon_type = weapon_type
        self.rarity = rarity
        self.base_attack = base_attack

    def to_dict(self):
        return {
            "name": self.name,
            "weapon_type": self.weapon_type,
            "rarity": self.rarity,
            "base_attack": self.base_attack,
        }


def weapon_from_api(api_data):
    # Перетворює дані зброї з API на Weapon.
    return Weapon(
        api_data["name"],
        api_data["type"],
        api_data["rarity"],
        api_data["baseAttack"],
    )