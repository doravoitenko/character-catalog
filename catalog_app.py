from cli.facade import CLI
from cli.presenter import Presenter
from cli.strategies import CatalogStrategy
from core.catalog import CharacterCatalog, default_profiles
from infra.catalog_storage import CatalogStorage
from infra.display import ConsoleDisplayer


def load_catalog(storage):
    # Повертає пару (каталог, попередження або None)
    warning = None
    try:
        data = storage.load()
        if data is not None:
            catalog = CharacterCatalog()
            catalog.load_from_data(data)
            return catalog, None
    except (OSError, ValueError) as error:
        warning = f"Не вдалося прочитати файл каталогу ({error}). Завантажено стандартний набір."
    catalog = CharacterCatalog(default_profiles())
    if warning is None:
        # Перший запуск: створюємо файл зі стандартним набором
        try:
            storage.save(catalog.get_all_data())
        except OSError:
            pass
    return catalog, warning


def build_cli(presenter, storage_path="catalog.json"):
    # Збирає всі шари разом: дані -> логіка -> консольний інтерфейс
    storage = CatalogStorage(storage_path)
    catalog, warning = load_catalog(storage)
    cli = CLI(presenter)
    cli.use_strategy(CatalogStrategy(catalog, storage))
    if warning:
        cli.error(warning)
    return cli


def main(storage_path="catalog.json"):
    cli = build_cli(Presenter(ConsoleDisplayer()), storage_path)
    cli.show("Каталог персонажів. Введіть help, щоб побачити команди.")
    cli.run()


if __name__ == "__main__":
    main()
