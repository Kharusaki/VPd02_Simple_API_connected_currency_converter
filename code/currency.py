"""Исправленный и дополненный скрипт из урока.

Базовая программа: получение курсов валют от open.er-api.com,
кэширование результата в currency_rate.json и вывод курсов
RUB, EUR, GBP для выбранной базовой валюты.
"""

import json
import os
import time

import requests


API_URL = "https://open.er-api.com/v6/latest/{base}"
DEFAULT_PATH = "currency_rate.json"
CACHE_MAX_AGE = 24 * 60 * 60  # 24 часа


def get_currency_rates(base: str) -> dict:
    """Делает GET-запрос к API и возвращает данные курсов."""
    url = API_URL.format(base=base)

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        raise RuntimeError(f"Не удалось связаться с сервисом: {e}")

    if response.status_code != 200:
        raise RuntimeError(f"Сервис вернул ошибку. HTTP-код: {response.status_code}")

    data = response.json()
    if data.get("result") != "success":
        raise RuntimeError(_describe_api_error(data))

    # Сейчас сервис отдаёт курсы в поле "rates", в документации урока –
    # "conversion_rates". Приводим к единому ключу.
    if "conversion_rates" not in data and "rates" in data:
        data["conversion_rates"] = data["rates"]

    return data


def _describe_api_error(data: dict) -> str:
    """Переводит код ошибки API в понятное сообщение с подсказкой."""
    error_type = data.get("error-type", "unknown-error")

    messages = {
        "unsupported-code": (
            "Код валюты не поддерживается сервисом. "
            "Проверьте правильность кода, например USD, EUR, RUB."
        ),
        "malformed-request": (
            "Сервис не смог разобрать запрос. Проверьте, что код валюты "
            "написан без лишних символов и пробелов."
        ),
        "invalid-key": "Указан неверный ключ доступа к сервису.",
        "inactive-account": "Аккаунт для доступа к сервису не активирован.",
        "quota-reached": "Достигнут лимит запросов к сервису на сегодня.",
    }

    return messages.get(
        error_type,
        f"Сервис сообщил об ошибке: {error_type}. "
        "Проверьте запрос и попробуйте ещё раз.",
    )


def save_to_file(data: dict, path: str = DEFAULT_PATH) -> None:
    """Сохраняет данные в JSON-файл в читаемом виде."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_from_file(path: str = DEFAULT_PATH) -> dict:
    """Читает данные из JSON-файла."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def is_fresh(path: str = DEFAULT_PATH) -> bool:
    """Проверяет, что файл существует и моложе 24 часов."""
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < CACHE_MAX_AGE


def main() -> None:
    print("Программа работы с курсами валют.")

    while True:
        print("\nВведите базовую валюту (например USD),")
        print("или просто нажмите Enter, чтобы выйти.")
        try:
            base = input("Валюта: ").strip().upper()
        except EOFError:
            print("Ввод прерван. Выход из программы.")
            return

        if not base:
            print("Выход из программы. До свидания!")
            return

        try:
            if is_fresh():
                cached = read_from_file()
                if cached.get("base_code") == base:
                    print("Использую данные из кэша (currency_rate.json).")
                    rates = cached["conversion_rates"]
                else:
                    data = get_currency_rates(base)
                    save_to_file(data)
                    rates = data["conversion_rates"]
                    print("Данные обновлены и сохранены в currency_rate.json.")
            else:
                data = get_currency_rates(base)
                save_to_file(data)
                rates = data["conversion_rates"]
                print("Данные обновлены и сохранены в currency_rate.json.")
        except RuntimeError as e:
            print(f"Ошибка: {e}")
            print("Исправить проблему и попробовать снова можно, введя другую валюту.")
            continue
        except (OSError, ValueError) as e:
            print(f"Ошибка при работе с файлом: {e}")
            print("Проверьте доступ к папке с файлом currency_rate.json и попробуйте снова.")
            continue

        print(f"\nКурсы к базовой валюте {base}:")
        for code in ("RUB", "EUR", "GBP"):
            if code in rates:
                print(f"  {code}: {rates[code]:.4f}")
            else:
                print(f"  {code}: нет данных")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        print("Перезапустите программу и попробуйте ещё раз.")
