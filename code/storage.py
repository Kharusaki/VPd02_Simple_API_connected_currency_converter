"""Модуль работы с файлом кэша.

Отвечает только за чтение и запись данных в JSON-файл.
"""

import json
import os
import time


DEFAULT_PATH = "currency_rate.json"
CACHE_MAX_AGE = 24 * 60 * 60  # 24 часа в секундах


class StorageError(Exception):
    """Ошибка при работе с файлом кэша."""


def save_to_file(data: dict, path: str = DEFAULT_PATH) -> None:
    """Сохраняет данные в JSON-файл в читаемом виде."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except OSError as e:
        raise StorageError(f"Не удалось сохранить файл {path}: {e}")


def read_from_file(path: str = DEFAULT_PATH) -> dict:
    """Читает данные из JSON-файла."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError) as e:
        raise StorageError(f"Не удалось прочитать файл {path}: {e}")


def is_fresh(path: str = DEFAULT_PATH, max_age: int = CACHE_MAX_AGE) -> bool:
    """Возвращает True, если файл существует и моложе max_age секунд."""
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < max_age
