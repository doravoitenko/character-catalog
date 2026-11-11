# Елементи, специфічні для консолі: повідомлення, рамки, таблиці.
# Усі методи лише повертають готовий текст, нічого не виводячи.
class CLIGraphic:

    @staticmethod
    def success(text):
        return f"[Успіх] {text}"

    @staticmethod
    def error(text):
        return f"[Помилка] {text}"

    @staticmethod
    def box(title, rows):
        # Рамка із заголовком; rows - пари (назва поля, значення)
        label_width = max((len(label) for label, _ in rows), default=0)
        lines = [f"{label.ljust(label_width)} : {value}" for label, value in rows]
        inner = max(max((len(line) for line in lines), default=0), len(title) + 2)
        top = "┌─ " + title + " " + "─" * (inner - len(title) - 1) + "┐"
        body = ["│ " + line.ljust(inner) + " │" for line in lines]
        bottom = "└" + "─" * (inner + 2) + "┘"
        return "\n".join([top, *body, bottom])

    @staticmethod
    def table(headers, rows):
        # Таблиця, де ширина кожного стовпця підлаштовується під вміст
        widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *rows)]

        def line(cells):
            return " │ ".join(str(cell).ljust(width) for cell, width in zip(cells, widths)).rstrip()

        separator = "─┼─".join("─" * width for width in widths)
        return "\n".join([line(headers), separator, *[line(row) for row in rows]])
