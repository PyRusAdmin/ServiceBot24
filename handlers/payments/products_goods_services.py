# -*- coding: utf-8 -*-

password_TelegramMaster = 300.00  # Сумма товара пароль TelegramMaster-PRO
password_TelegramMaster_Commentator = 300.00  # Сумма товара пароль TelegramMaster_Commentator

TelegramMaster = 1600.00  # Стоимость товара TelegramMaster-PRO
TelegramMaster_Commentator = 1300.00  # Сумма товара "TelegramMaster_Commentator"

payment_installation = 800.00  # Сумма товара "Установка ПО"

TelegramMaster_Search_GPT = 1000.00  # Стоимость товара "TelegramMaster_Search_GPT"

# ============================================================================
# Новые продукты: MaxMaster и Аренда сервера
# ============================================================================

MaxMaster = 500.00  # Стоимость программы MaxMaster (перебор номеров в Max)

SERVER_RENT_PRICE = 250.00  # Стоимость аренды сервера в месяц (руб)

# Курс Telegram Stars (рублей за 1 звезду)
# Обновите это значение при изменении курса Telegram
# Актуальный курс на 2026 год: ~1.5 рубля за звезду
STARS_TO_RUB_RATE = 200


def get_stars_amount(rub_amount: float) -> int:
    """
    Конвертирует сумму из рублей в звезды Telegram
    :param rub_amount: сумма в рублях
    :return: количество звезд (целое число)
    """
    stars = int(rub_amount / STARS_TO_RUB_RATE)
    # Округляем до ближайшего значения, которое принимает Telegram (минимум 50 звезд)
    stars = max(1, stars)
    return stars
