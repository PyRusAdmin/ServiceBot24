# -*- coding: utf-8 -*-
"""
Цены на продукты
"""
# password_TelegramMaster_PRO = 300.00  # Сумма товара пароль TelegramMaster-PRO
# password_TelegramMaster_Commentator = 300.00  # Сумма товара пароль TelegramMaster_Commentator
# TelegramMaster_Commentator = 1300.00  # Сумма товара "TelegramMaster_Commentator"

TelegramMaster_PRO = {
    "name": "TelegramMaster-PRO",  # Название товара
    "price": 1600.00,  # Стоимость товара TelegramMaster-PRO
    "name_password": "TelegramMaster-PRO",
    "price_password": 300.00  # Стоимость товара "TelegramMaster_Commentator"
}

TelegramMaster_Commentator = {
    "name": "TelegramMaster-Commentator",  # Название товара
    "price": 1300.00,  # Стоимость товара TelegramMaster_Commentator
    "name_password": "TelegramMaster-Commentator",
    "price_password": 300.00  # Стоимость товара "TelegramMaster_Commentator"
}

payment_installation = 800.00  # Сумма товара "Установка ПО"
TelegramMaster_Search_GPT = 1000.00  # Стоимость товара "TelegramMaster_Search_GPT"
MaxMaster = 500.00  # Стоимость программы MaxMaster
SERVER_RENT_PRICE = 250.00  # Стоимость аренды сервера в месяц (руб)

# ============================================================================
# Курс Telegram Stars (рублей за 1 звезду)
# Измените это значение, чтобы обновить курс во всем проекте
# ============================================================================
STARS_TO_RUB_RATE = 1.5  # 1 звезда = 1.5 рубля


def get_stars_amount(rub_amount: float) -> int:
    """
    Конвертирует сумму из рублей в звезды Telegram

    :param rub_amount: сумма в рублях
    :return: количество звезд (целое число)
    """
    stars = int(rub_amount / STARS_TO_RUB_RATE)
    # Минимум 1 звезда
    stars = max(1, stars)
    return stars
