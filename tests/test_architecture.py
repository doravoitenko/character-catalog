import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def imported_modules(folder):
    # Повертає пари (файл, модуль) для всіх імпортів у .py-файлах папки
    result = []
    for path in sorted((ROOT / folder).glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                result += [(path.name, alias.name) for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                result.append((path.name, node.module))
    return result


def violations(folder, forbidden):
    return [
        f"{folder}/{file} імпортує {module}"
        for file, module in imported_modules(folder)
        if module.split(".")[0] in forbidden
    ]


# Правило багатошарової архітектури: ядро (бізнес-логіка) не залежить від
# інтерфейсу й від шару даних, тому його можна використати і в консолі, і в GUI.
def test_core_does_not_depend_on_cli_or_infra():
    assert violations("core", {"cli", "infra"}) == []


def test_infra_does_not_depend_on_cli_or_core():
    assert violations("infra", {"cli", "core"}) == []


def test_architecture_check_really_sees_imports():
    # Захист від пустої перевірки: у cli/ імпорти ядра точно є
    assert any(module.startswith("core") for _, module in imported_modules("cli"))
