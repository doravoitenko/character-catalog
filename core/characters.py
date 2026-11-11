class Character:

    def __init__(self, name, hp, power):
        self.name = name
        self.hp = hp
        self.power = power
        self.weapon = None  # спочатку зброї немає

    def equip(self, weapon):
        # Екіпірує зброю на персонажа.
        self.weapon = weapon

    def to_dict(self):
        return {"name": self.name, "hp": self.hp, "power": self.power}


class CharacterManager:

    def __init__(self, displayer):
        self.displayer = displayer
        self.characters = []

    def create_character(self, name, hp=100, power=25):
        char = Character(name, hp, power)
        self.characters.append(char)
        self.displayer.display(f"Створено персонажа: {name} (HP: {hp})")

    def show_all_characters(self):
        # Виводить список усіх створених персонажів
        if not self.characters:
            self.displayer.display("Список персонажів порожній!")
        else:
            self.displayer.display("\n--- СПИСОК ПЕРСОНАЖІВ ---")
            for idx, char in enumerate(self.characters, 1):
                self.displayer.display(
                    f"{idx}. {char.name} (HP: {char.hp}, Power: {char.power})"
                )

    def get_all_data(self):
        return [c.to_dict() for c in self.characters]

    def load_from_data(self, data_list):
        self.characters = []
        for item in data_list:
            char = Character(item["name"], item["hp"], item["power"])
            self.characters.append(char)