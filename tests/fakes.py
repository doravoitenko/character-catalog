from cli.presenter import Presenter
from infra.display import Displayer


# Дисплеєр для тестів: нічого не друкує, а запам'ятовує повідомлення
class RecordingDisplayer(Displayer):

    def __init__(self):
        self.messages = []

    def display(self, message):
        self.messages.append(message)


# Презентер для тестів: замість клавіатури бере заздалегідь задані відповіді.
# Коли відповіді закінчуються, поводиться як кінець вводу (Ctrl+D).
class ScriptedPresenter(Presenter):

    def __init__(self, inputs=()):
        super().__init__(RecordingDisplayer())
        self.inputs = list(inputs)
        self.prompts = []

    def get_input(self, prompt):
        self.prompts.append(prompt)
        if not self.inputs:
            raise EOFError
        return self.inputs.pop(0)

    @property
    def output(self):
        return "\n".join(self.displayer.messages)
