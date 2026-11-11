class Paragraph:

    def __init__(self, content):
        self.content = content

    def render(self):
        return f"Параграф: {self.content}"


class DocumentManager:

    def __init__(self, displayer):
        self.displayer = displayer
        self.paragraphs = []

    def add_paragraph(self, text):
        p = Paragraph(text)
        self.paragraphs.append(p)
        self.displayer.display(f"Додано параграф: '{text}'")

    def show_all_texts(self):
        # Виводить список усіх створених параграфів
        if not self.paragraphs:
            self.displayer.display("Список параграфів порожній!")
        else:
            self.displayer.display("\n--- СПИСОК ПАРАГРАФІВ ---")
            for idx, p in enumerate(self.paragraphs, 1):
                self.displayer.display(f"{idx}. {p.content}")

    def get_all_data(self):
        return [p.content for p in self.paragraphs]

    def load_from_data(self, data_list):
        self.paragraphs = [Paragraph(text) for text in data_list]