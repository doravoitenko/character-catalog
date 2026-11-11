class Presenter:

    def __init__(self, displayer):
        self.displayer = displayer

    def show_menu(self):
        self.displayer.display("\n- МЕНЮ УПРАВЛІННЯ -")
        self.displayer.display("1. Створити персонажа")
        self.displayer.display("2. Додати параграф тексту")
        self.displayer.display("3. Переглянути персонажів")
        self.displayer.display("4. Переглянути параграфи")
        self.displayer.display("5. Зберегти стан у файл")
        self.displayer.display("6. Завантажити стан з файлу")
        self.displayer.display("7. Завантажити персонажа з інтернету")
        self.displayer.display("8. Список персонажів з API")
        self.displayer.display("9. Список зброї з API")
        self.displayer.display("10. Екіпірувати зброю на персонажа")
        self.displayer.display("0. Вихід")

    def get_input(self, prompt):
        return input(prompt)