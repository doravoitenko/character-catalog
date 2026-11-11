from abc import ABC, abstractmethod


class Displayer(ABC):
    # Патерн STRATEGY (Стратегія): інтерфейс "способу виведення".
    #
    # Ролі:
    #     Strategy         - Displayer (цей клас): оголошує спільний інтерфейс.
    #     ConcreteStrategy - ConsoleDisplayer: виводить у консоль. Інші
    #                        реалізації (файл, GUI, веб) можна додати, не чіпаючи
    #                        жодного менеджера. У тестах роль такої стратегії
    #                        грає MagicMock.
    #     Context          - CharacterManager, DocumentManager, Presenter. Вони
    #                        отримують стратегію в конструкторі й зберігають як
    #                        поле self.displayer (агрегація, як на діаграмі).
    #
    # Завдяки цьому логіка (core) не залежить від того, КУДИ виводиться текст.

    @abstractmethod
    def display(self, message):
        # Виводить звичайний рядок.
        pass

    def display_object(self, obj):
        # Якщо об'єкт має метод render(), виводить його результат.
        text = obj.render() if hasattr(obj, "render") else str(obj)
        self.display(text)


class ConsoleDisplayer(Displayer):
    # Конкретна стратегія: вивід у консоль.

    def display(self, message):
        # Виводить звичайний рядок у консоль
        print(message)
