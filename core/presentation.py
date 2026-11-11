from core.text import Paragraph


def build_presentation(character, api_data):
    # Збирає представлення персонажа з параграфів.
    paragraphs = [
        Paragraph(f"{character.name}, {api_data['title']}"),
        Paragraph(f"Стихія: {api_data['vision']}"),
        Paragraph(f"Зброя: {api_data['weapon']}"),
        Paragraph(f"Країна: {api_data['nation']}"),
        Paragraph(f"HP: {character.hp}, Power: {character.power}"),
    ]
    if character.weapon is not None:
        paragraphs.append(
            Paragraph(
                f"Екіпіровано: {character.weapon.name} "
                f"(атака {character.weapon.base_attack})"
            )
        )
    return "\n".join(p.render() for p in paragraphs)