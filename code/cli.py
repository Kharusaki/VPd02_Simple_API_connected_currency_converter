"""Модуль интерфейса (CLI) для работы с курсами валют.

Позволяет:
- выбрать базовую валюту и посмотреть курсы RUB, EUR, GBP;
- конвертировать сумму между двумя валютами;
- проверяет, что коды валют существуют.
"""

import sys

import api_client
import storage


def load_rates(base: str) -> dict:
    """Возвращает данные курсов, используя кэш, если он свежий и подходит."""
    if storage.is_fresh():
        try:
            data = storage.read_from_file()
        except storage.StorageError as e:
            print(f"Ошибка чтения кэша: {e}")
            data = None

        if data and data.get("base_code") == base:
            print("Использую данные из кэша (file: currency_rate.json).")
            return data
        print("Кэш не подходит под базовую валюту, обновляю.")
    else:
        print("Кэш устарел или отсутствует, запрашиваю свежие данные.")

    data = api_client.get_currency_rates(base)
    storage.save_to_file(data)
    print("Данные обновлены и сохранены в currency_rate.json.")
    return data


def show_rates(data: dict) -> None:
    """Показывает курсы для RUB, EUR, GBP относительно базовой валюты."""
    base = data.get("base_code", "?")
    rates = data.get("conversion_rates", {})
    print(f"\nКурсы к базовой валюте {base}:")
    for code in ("RUB", "EUR", "GBP"):
        if code in rates:
            print(f"  {code}: {rates[code]:.4f}")
        else:
            print(f"  {code}: нет данных")


def validate_code(code: str, rates: dict) -> bool:
    """Проверяет, что код валюты есть в списке доступных."""
    if code not in rates:
        print(f"Ошибка: валюта '{code}' не найдена в списке доступных.")
        print("Проверьте правильность кода или посмотрите полный список в файле currency_rate.json.")
        return False
    return True


def convert(data: dict) -> None:
    """Конвертирует сумму из одной валюты в другую через базовую валюту."""
    rates = data.get("conversion_rates", {})

    from_code = input("Из какой валюты (например USD): ").strip().upper()
    if not validate_code(from_code, rates):
        return

    to_code = input("В какую валюту (например RUB): ").strip().upper()
    if not validate_code(to_code, rates):
        return

    try:
        amount = float(input("Сумма: ").strip())
    except ValueError:
        print("Ошибка: сумма должна быть числом (например 100 или 12.5).")
        return

    if from_code == to_code:
        result = amount
    else:
        value_in_base = amount / rates[from_code]
        result = value_in_base * rates[to_code]

    print(f"{amount:.4f} {from_code} = {result:.4f} {to_code}")


def main() -> int:
    print("Программа работы с курсами валют.")

    while True:
        print("\nВведите базовую валюту (например USD),")
        print("или просто нажмите Enter, чтобы выйти.")
        try:
            base = input("Валюта: ").strip().upper()
        except EOFError:
            print("Ввод прерван. Выход из программы.")
            return 1

        if not base:
            print("Выход из программы. До свидания!")
            return 0

        try:
            data = load_rates(base)
        except api_client.ApiError as e:
            print(f"Ошибка: {e}")
            print("Исправить проблему и попробовать снова можно, введя другую валюту.")
            continue
        except storage.StorageError as e:
            print(f"Ошибка при работе с файлом: {e}")
            print("Проверьте доступ к папке с файлом currency_rate.json и попробуйте снова.")
            continue

        show_rates(data)

        print("\n-- Конвертер --")
        while True:
            try:
                choice = input("Хотите конвертировать сумму? (y/n): ").strip().lower()
            except EOFError:
                break
            if choice in ("n", "no", ""):
                break
            if choice in ("y", "yes"):
                convert(data)
            else:
                print("Пожалуйста, введите y или n.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
