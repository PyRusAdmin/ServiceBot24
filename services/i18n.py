# -*- coding: utf-8 -*-
from functools import lru_cache
from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader


@lru_cache(maxsize=None)
def get_l10n() -> FluentLocalization:
    """
    Получить объект локализации.
    Кэшируется для производительности.
    """
    locales_dir = Path(__file__).parent.parent / "locales"
    loader = FluentResourceLoader(str(locales_dir))
    return FluentLocalization(["ru"], ["ru.ftl"], loader)


def t(key: str, **kwargs) -> str:
    """
    Получить перевод по ключу.

    :param key: Ключ сообщения (например, 'registered-message')
    :param kwargs: Переменные для подстановки (например, name='Иван')
    :return: Переведённая строка
    """
    l10n = get_l10n()
    return l10n.format_value(key, kwargs)
