from cli.args import ArgParser
from cli.graphic import CLIGraphic


# Патерн FACADE (Фасад). Єдина "точка входу" до консольного інтерфейсу:
# зовнішній код викликає лише три методи (use_strategy, exec_command, display),
# а розбір рядків, пошук команд і форматування лишаються всередині.
#
# Патерн STRATEGY: набір команд (CommandStrategy) і спосіб виведення (Renderer)
# підключаються ззовні, тож CLI можна переналаштувати, не змінюючи його код.
#
# Ввід і вивід іде через Presenter з попередніх практичних, тому в тестах
# консоль легко підмінити.
class CLI:

    def __init__(self, presenter, parser=None):
        self.presenter = presenter
        self.parser = parser or ArgParser()
        self.strategy = None
        self.running = True

    def use_strategy(self, strategy):
        # Підключає набір команд
        self.strategy = strategy

    def exec_command(self, raw):
        # Виконує рядок, введений користувачем
        args = self.parser.parse_args(raw)
        if not args.command:
            return
        if self.strategy is None:
            self.error("Набір команд не підключено (use_strategy).")
        elif not self.strategy.exec_command(self, args):
            self.error(f"Невідома команда: {args.command}. Введіть help.")

    def display(self, obj, renderer):
        # Виводить об'єкт у тому вигляді, який задає рендерер
        self.show(renderer.render(obj))

    def show(self, text):
        self.presenter.displayer.display(text)

    def success(self, text):
        self.show(CLIGraphic.success(text))

    def error(self, text):
        self.show(CLIGraphic.error(text))

    def ask(self, prompt):
        return self.presenter.get_input(prompt)

    def stop(self):
        self.running = False

    def run(self, prompt="catalog> "):
        # Головний цикл: читаємо рядок, виконуємо, повторюємо
        while self.running:
            try:
                raw = self.ask(prompt)
            except (EOFError, KeyboardInterrupt):
                break
            try:
                self.exec_command(raw)
            except (EOFError, KeyboardInterrupt):
                # Ввід перервано посеред команди (наприклад, діалогу create):
                # скасовуємо лише її, а програма продовжує працювати
                self.show("Команду перервано.")
