from dataclasses import dataclass


# Розібраний рядок користувача: "show Hu Tao" -> command="show", rest="Hu Tao"
@dataclass(frozen=True)
class Args:
    command: str = ""
    rest: str = ""


# Розбирає введений рядок на назву команди й аргументи.
# Назва команди не залежить від регістру, аргументи лишаються як є.
class ArgParser:

    def parse_args(self, raw):
        command, _, rest = raw.strip().partition(" ")
        return Args(command.lower(), rest.strip())
