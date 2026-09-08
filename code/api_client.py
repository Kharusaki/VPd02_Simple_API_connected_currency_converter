"""Модуль работы с API обмена валют.

Отвечает только за сетевые запросы к сервису open.er-api.com.
"""

import requests


API_URL = "https://open.er-api.com/v6/latest/{base}"


class ApiError(Exception):
    """Ошибка при обращении к API."""


def get_currency_rates(base: str) -> dict:
    """Возвращает объект ответа от API для базовой валюты base."""
    url = API_URL.format(base=base)

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        raise ApiError(f"Не удалось связаться с сервисом: {e}")

    if response.status_code != 200:
        raise ApiError(f"Сервис вернул ошибку. HTTP-код: {response.status_code}")

    data = response.json()
    if data.get("result") != "success":
        raise ApiError(_describe_api_error(data))

    # Сейчас сервис отдаёт курсы в поле "rates", в документации
    # модуля используется "conversion_rates". Приводим к единому ключу.
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
