# Character Catalog

A console application for keeping a catalog of game characters, built as a learning
project for an Object-Oriented Programming course.

## Features

- `list`: show all characters
- `show <name or number>`: show a character card with a link to its image
- `create`: add a character through a dialog
- `update`: reload the catalog from the file
- `save`: write the catalog to `catalog.json`
- `help`, `exit`

## Requirements

Python 3.9 or newer. Tests need `pytest`.

## Run

```bash
python3 catalog_app.py
```

On the first run `catalog.json` is created with a starter set of characters.

## Tests

```bash
pip install -r requirements.txt
python3 -m pytest
```

## Project structure

```
catalog_app.py          entry point of the character catalog
main.py                 menu application from earlier practicals
cli/                    presentation layer: CLI facade, commands, renderers
core/                   business logic: CharacterProfile, CharacterCatalog and earlier models
infra/                  persistence and console output
tests/                  automated tests
docs/DESIGN.md          design document
```

## Documentation

See the [design document](docs/DESIGN.md) for architecture, class diagram and the
description of the command line interface.

## Note about the remote API

Earlier practicals loaded characters from `genshin.jmp.blue`. The service was
unavailable (HTTP 521) when this project was finished, so the catalog uses local data.
